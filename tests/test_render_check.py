"""render_check must never close a PowerPoint the consultant has open.

PowerPoint is a single-instance COM server: `New-Object -ComObject PowerPoint.Application`
attaches to a running instance rather than starting a private one, so an unconditional
`$app.Quit()` in the teardown closes the consultant's windows and discards unsaved work.
A clean COM quit also deletes the AutoRecover files, so nothing is recoverable afterwards.
These tests pin the two guards that prevent it.

The busy guard asks what is open, not whether a POWERPNT process exists: PowerPoint lingers
as a process with no document window and consultants leave it running all day, so a process
check refuses every render and asks them to kill the program. It refuses only on work that
could actually be lost -- an unsaved presentation, or the target deck itself, which Open()
would hand back as the consultant's own window.
"""
import re
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent / ".claude" / "skills" / "deck-qc" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import render_check  # noqa: E402


def rendered_script() -> str:
    return render_check.PS_TEMPLATE.format(slides="", scale=1200, all="$false")


def test_busy_guard_precedes_any_slide_export():
    """The busy check must come before anything is opened or exported, or it is useless."""
    script = rendered_script()
    guard = script.find("PPTBUSY")
    opened = script.find("$app.Presentations.Open(")
    assert guard != -1, "no busy guard in the PowerShell template"
    assert opened != -1, "template no longer opens the deck; update this test"
    assert guard < opened, "the busy guard must run before the deck is opened"


def test_busy_guard_attaches_before_it_decides():
    """Attach first, then ask what is open -- the same question the cleanup asks."""
    script = rendered_script()
    attach = script.find('GetActiveObject("PowerPoint.Application")')
    decide = script.find("PPTBUSY")
    assert attach != -1, "the guard must attach with GetActiveObject, not start a new instance"
    assert attach < decide, "the busy decision must follow the attach, not precede it"


def test_busy_guard_does_not_test_for_a_process():
    """A POWERPNT process with no open document is not a reason to refuse."""
    script = rendered_script()
    assert "POWERPNT" not in script, (
        "the guard is back to testing for a process; PowerPoint lingers with no document window"
    )
    assert "Get-Process" not in script


def test_busy_guard_refuses_only_on_unsaved_work_or_the_target():
    script = rendered_script()
    assert "$op.Saved -eq $false" in script, "nothing checks for unsaved changes"
    assert "$op.FullName" in script, "nothing checks whether the target deck is the open one"


def test_new_com_object_only_when_nothing_was_attached():
    """New-Object must sit in the else branch: attaching first is what makes Quit() safe."""
    script = rendered_script()
    com = script.find("New-Object -ComObject PowerPoint.Application")
    assert com != -1, "template no longer creates the COM object; update this test"
    assert script.find("} else {", script.find("PPTBUSY")) < com, (
        "New-Object must run only when GetActiveObject found no running instance"
    )


def test_busy_guard_exits_without_rendering():
    script = rendered_script()
    line = next(ln for ln in script.splitlines() if "PPTBUSY" in ln)
    assert "exit 2" in line, "a busy skip must exit 2, the gate's non-blocking skip code"


def test_quit_is_conditional_on_an_empty_instance():
    """Quit only when no presentation is left open: the consultant may have launched
    PowerPoint into our instance while the export was running."""
    script = rendered_script()
    assert "$app.Quit()" in script
    quit_line = next(ln for ln in script.splitlines() if "$app.Quit()" in ln)
    assert "$others -eq 0" in quit_line, "Quit() must be guarded by an empty-instance check"
    assert "Presentations.Count" in script, "nothing establishes how many decks are open"


def test_an_attached_instance_is_never_quit():
    """If PowerPoint was already running, the instance is the consultant's; leave it running."""
    script = rendered_script()
    quit_line = next(ln for ln in script.splitlines() if "$app.Quit()" in ln)
    assert "-not $attached" in quit_line, (
        "Quit() must also be guarded on having started the instance ourselves"
    )


def test_no_unconditional_quit_anywhere():
    script = rendered_script()
    for ln in script.splitlines():
        if "$app.Quit()" not in ln:
            continue
        assert re.search(r"if\s*\(", ln), "found an unguarded $app.Quit(): %r" % ln


@pytest.mark.skipif(sys.platform != "win32", reason="the busy path is Windows-only")
def test_busy_skip_returns_two(monkeypatch, tmp_path):
    """When the shell reports PPTBUSY, main() reports a skip rather than a pass or a block."""
    class FakeProc:
        returncode = 2
        stdout = "PPTBUSY\n"
        stderr = ""

    monkeypatch.setattr(render_check.subprocess, "run", lambda *a, **k: FakeProc())
    deck = tmp_path / "deck.pptx"
    deck.write_bytes(b"not a real pptx; the shell call is stubbed")
    rc = render_check.main([str(deck), "--out", str(tmp_path / "out"), "--no-sheet"])
    assert rc == 2, "a busy skip must not read as a clean render (0) or an overflow block (1)"

#!/usr/bin/env python3
"""render_check.py: the render step, on Windows through PowerPoint itself.

Usage:
    python render_check.py DECK.pptx [--out DIR] [--slides 1-9] [--scale 1600]

Exports each requested slide to PNG (so the builder can look at the page) and reports every text frame whose
laid-out text is taller than its box, measured by PowerPoint, not estimated. Exit 0 when nothing overflows,
1 when something does, 2 when PowerPoint is not available. On a machine without PowerPoint, use the soffice
and pdftoppm route described in the deck-qc skill instead.

Appendix pages (after a slide titled Appendix, Crosstabs or Backup) are skipped unless --all is given: they are
data pages the consultant leaves as they are.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

PS_TEMPLATE = r'''
$ErrorActionPreference = "Stop"
$p = "{deck}"
$out = "{out}"
New-Item -ItemType Directory -Force $out | Out-Null
try {{ $app = New-Object -ComObject PowerPoint.Application }} catch {{ Write-Output "NOPPT"; exit 2 }}
$pres = $app.Presentations.Open($p, $true, $false, $false)
$n = $pres.Slides.Count
Write-Output ("SLIDES {{0}}" -f $n)
$stop = $n
if (-not {all}) {{
  for ($i = 1; $i -le $n; $i++) {{
    $s = $pres.Slides.Item($i)
    foreach ($sh in $s.Shapes) {{
      if ($sh.HasTextFrame -and ($sh.Name -like "Title*")) {{
        $t = $sh.TextFrame.TextRange.Text.Trim()
        if ($t -match "^(Appendix|Crosstabs?|Backup)") {{ $stop = $i - 1; break }}
      }}
    }}
    if ($stop -lt $n) {{ break }}
  }}
}}
$wanted = @({slides})
if ($wanted.Count -eq 0) {{ $wanted = 1..$stop }}
$over = 0
foreach ($i in $wanted) {{
  if ($i -gt $stop) {{ continue }}
  $s = $pres.Slides.Item($i)
  $s.Export("$out\slide$i.png", "PNG", {scale}, [int]({scale} * 9 / 16))
  foreach ($sh in $s.Shapes) {{
    if ($sh.HasTextFrame) {{
      $tr = $sh.TextFrame.TextRange
      if ($tr.Text.Length -gt 0 -and $sh.TextFrame.WordWrap -and ($tr.BoundHeight -gt ($sh.Height + 6))) {{
        $over++
        $txt = $tr.Text; if ($txt.Length -gt 60) {{ $txt = $txt.Substring(0, 60) }}
        Write-Output ("OVERFLOW slide={{0}} shape={{1}} text={{2}}pt box={{3}}pt '{{4}}'" -f $i, $sh.Name, [int]$tr.BoundHeight, [int]$sh.Height, $txt)
      }}
    }}
  }}
}}
$pres.Close(); $app.Quit()
Write-Output ("OVERFLOWS {{0}}" -f $over)
'''


def parse_slides(spec: str | None) -> list[int]:
    if not spec:
        return []
    out: list[int] = []
    for part in spec.split(","):
        part = part.strip()
        if "-" in part:
            a, b = part.split("-")
            out.extend(range(int(a), int(b) + 1))
        elif part:
            out.append(int(part))
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("deck")
    ap.add_argument("--out", default=None)
    ap.add_argument("--slides", default=None, help="e.g. 1-9 or 1,3,5; default: every page before the appendix")
    ap.add_argument("--scale", type=int, default=1600)
    ap.add_argument("--all", action="store_true", help="include appendix pages")
    args = ap.parse_args(argv)
    deck = Path(args.deck).resolve()
    out = Path(args.out).resolve() if args.out else deck.parent / ("render_" + deck.stem)
    slides = ",".join(str(i) for i in parse_slides(args.slides))
    script = PS_TEMPLATE.format(deck=str(deck), out=str(out), slides=slides, scale=args.scale,
                                all="$true" if args.all else "$false")
    if sys.platform != "win32":
        print("render_check needs PowerPoint on Windows; use soffice + pdftoppm here")
        return 2
    proc = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", script], capture_output=True, text=True)
    text = proc.stdout.strip()
    print(text)
    if proc.returncode != 0 and proc.stderr.strip():
        print(proc.stderr.strip()[:800])
    if proc.returncode == 2 or "NOPPT" in text:
        return 2
    for line in text.splitlines():
        if line.startswith("OVERFLOWS"):
            return 0 if line.split()[1] == "0" else 1
    return 2


if __name__ == "__main__":
    sys.exit(main())

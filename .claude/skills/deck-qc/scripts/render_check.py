#!/usr/bin/env python3
"""render_check.py: the render step, on Windows through PowerPoint itself.

Usage:
    python render_check.py DECK.pptx [--out DIR] [--slides 1-9] [--scale 1200] [--no-sheet]

Exports each requested slide to PNG (so the builder can look at the page) and reports every text frame whose
laid-out text is taller than its box, measured by PowerPoint, not estimated. Exit 0 when nothing overflows,
1 when something does, 2 when PowerPoint is not available. On a machine without PowerPoint, use the soffice
and pdftoppm route described in the deck-qc skill instead.

After exporting, the pages are tiled into contact sheets (sheet_1.png, sheet_2.png, ...; nine pages per sheet, three
across) so the builder reads one image per nine pages instead of one per page. Reading a page image costs roughly the
same number of tokens whatever its size, so the sheet is the cheap way to look at a whole deck; open a single
slideN.png only when a sheet shows something that needs a closer look. Use --slides to render only the pages an
iteration changed.

Appendix pages (after a slide titled Appendix, Crosstabs or Backup) are skipped unless --all is given: they are
data pages the consultant leaves as they are.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

# Paths reach PowerShell through environment variables, never by string interpolation: a deck named
# "Q4 $ale$.pptx" or one with a quote in it must not break or run as code.
PS_TEMPLATE = r'''
$ErrorActionPreference = "Stop"
$p = $env:QC_RENDER_DECK
$out = $env:QC_RENDER_OUT
New-Item -ItemType Directory -Force $out | Out-Null
try {{ $app = New-Object -ComObject PowerPoint.Application }} catch {{ Write-Output "NOPPT"; exit 2 }}
$pres = $null
try {{
$pres = $app.Presentations.Open($p, $true, $false, $false)
$n = $pres.Slides.Count
$w = [int]{scale}
$h = [int]([double]$w * $pres.PageSetup.SlideHeight / $pres.PageSetup.SlideWidth)
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
  $s.Export("$out\slide$i.png", "PNG", $w, $h)
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
Write-Output ("OVERFLOWS {{0}}" -f $over)
}} finally {{
  if ($pres -ne $null) {{ try {{ $pres.Close() }} catch {{}} }}
  try {{ $app.Quit() }} catch {{}}
}}
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
    ap.add_argument("--scale", type=int, default=1200)
    ap.add_argument("--no-sheet", action="store_true", help="skip the contact sheets")
    ap.add_argument("--per-sheet", type=int, default=9)
    ap.add_argument("--all", action="store_true", help="include appendix pages")
    args = ap.parse_args(argv)
    deck = Path(args.deck).resolve()
    out = Path(args.out).resolve() if args.out else deck.parent / ("render_" + deck.stem)
    slides = ",".join(str(i) for i in parse_slides(args.slides))
    script = PS_TEMPLATE.format(slides=slides, scale=int(args.scale), all="$true" if args.all else "$false")
    if sys.platform != "win32":
        print("render_check needs PowerPoint on Windows; use soffice + pdftoppm here")
        return 2
    env = dict(os.environ, QC_RENDER_DECK=str(deck), QC_RENDER_OUT=str(out))
    proc = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", script],
                          capture_output=True, text=True, env=env, timeout=600)
    text = proc.stdout.strip()
    print(text)
    if proc.returncode != 0 and proc.stderr.strip():
        print(proc.stderr.strip()[:800])
    if proc.returncode == 2 or "NOPPT" in text:
        return 2
    if not args.no_sheet:
        for sheet in contact_sheets(out, per_sheet=args.per_sheet):
            print("SHEET", sheet)
    for line in text.splitlines():
        if line.startswith("OVERFLOWS"):
            return 0 if line.split()[1] == "0" else 1
    return 2


def contact_sheets(out: Path, per_sheet: int = 9, cols: int = 3, cell_w: int = 640) -> list:
    """Tile slideN.png files into numbered sheets, three across, page number stamped in the corner."""
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        return []
    pngs = sorted(out.glob("slide*.png"), key=lambda q: int(q.stem[5:]))
    sheets = []
    for k in range(0, len(pngs), per_sheet):
        batch = pngs[k:k + per_sheet]
        first = Image.open(batch[0])
        cell_h = int(first.height * cell_w / first.width)
        rows = (len(batch) + cols - 1) // cols
        gap = 12
        sheet = Image.new("RGB", (cols * cell_w + (cols + 1) * gap, rows * cell_h + (rows + 1) * gap), "#666666")
        draw = ImageDraw.Draw(sheet)
        for i, png in enumerate(batch):
            im = Image.open(png).convert("RGB").resize((cell_w, cell_h))
            x = gap + (i % cols) * (cell_w + gap)
            y = gap + (i // cols) * (cell_h + gap)
            sheet.paste(im, (x, y))
            label = png.stem[5:]
            draw.rectangle([x, y, x + 14 + 9 * len(label), y + 18], fill="#000000")
            draw.text((x + 6, y + 3), label, fill="#FFFFFF")
        dest = out / ("sheet_%d.png" % (k // per_sheet + 1))
        sheet.save(dest, optimize=True)
        sheets.append(dest)
    return sheets


if __name__ == "__main__":
    sys.exit(main())

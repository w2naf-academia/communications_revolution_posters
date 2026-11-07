#!/usr/bin/env python3
"""Check that every line of each transcription appears verbatim on its poster.

Strips only transcriber markup (the same markup build_posters.py removes), then looks for
each line of panel text, every heading and every header card in the poster's text.
Exits non-zero if anything is missing.
"""
import re
import sys
from pathlib import Path

from pptx import Presentation

sys.path.insert(0, str(Path(__file__).parent))
from build_posters import BOARDS, REPO, parse_board, plain  # noqa: E402


def poster_text(path):
    out = []
    for sh in Presentation(str(path)).slides[0].shapes:
        if sh.has_text_frame:
            out.extend(p.text for p in sh.text_frame.paragraphs)
    return out


bad = 0
for b in BOARDS:
    paras = poster_text(REPO / 'posters' / f"{b['out']}.pptx")
    columns = parse_board(REPO / 'transcription' / b['md'])
    headers = [line for col in columns for line in (col.header or [])]
    body = []
    for col in columns:
        for p in col.panels:
            if p.title:
                body.append(plain(p.title))
            body += [plain(blk.runs) for blk in p.blocks]
    missing = [e for e in headers + body if e not in paras]
    # Count content lines in the Markdown directly, to catch any line the parser dropped.
    md = (REPO / 'transcription' / b['md']).read_text().split('## Transcriber notes')[0]
    raw = [l for l in md.split('\n') if l.strip()
           and not l.startswith(('# ', '## Column', 'Source photo:', 'Author of original', '<!--', '[image:'))
           and not re.match(r'^\((Title|Printed)\b.*\)$', l)
           and not re.fullmatch(r'### \((.*\b)?untitled\)', l)]
    dropped = len(raw) - len(body)
    print(f"{b['out']}: {len(body)} text lines + {len(headers)} header lines on the poster; "
          f"{len(raw)} lines in the transcription; {len(missing)} missing, {dropped} dropped")
    for m in missing:
        print('   MISSING:', m[:100])
    bad += len(missing) + abs(dropped)
sys.exit(1 if bad else 0)

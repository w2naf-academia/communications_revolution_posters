#!/usr/bin/env python3
"""Build the three Communications Revolution posters from the verbatim transcriptions.

Reads transcription/board_*.md, lays each board out on the HamSCI 48 x 36 in PowerPoint poster
template (one rounded column box per board column, the board's panels stacked inside), picks
the largest body font size at which every column fits, and writes posters/*.pptx.

The text is taken from the transcription verbatim. Only transcriber markup is removed:
annotations such as "(Title printed in bold.)", [image: ...] notes, [red]...[/red] markers, and
[?x?] uncertainty brackets (the best reading x is used). Nothing after "## Transcriber notes"
is used.

Usage:
    .venv/bin/python posters/build_posters.py [--template PATH]

Text is measured with Carlito, which has the same metrics as Calibri (the template's font).
Render to PDF with LibreOffice to check (see posters/README.md).
"""
import argparse
import copy
import io
import os
import re
from dataclasses import dataclass, field
from pathlib import Path

from PIL import ImageFont
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Pt

REPO = Path(__file__).resolve().parent.parent
DEFAULT_TEMPLATE = Path.home() / 'hamsci/presentation_templates/poster/pptx/hamsci_poster_template.pptx'
FONT_DIR = Path('/usr/share/fonts/truetype/crosextra')
ACCENT = RGBColor(0x25, 0x41, 0x60)   # the template's HamSCI blue
EMU = 914400                          # EMU per inch

# Poster geometry (inches), from the template's three column boxes.
AREA_LEFT, AREA_RIGHT = 0.59, 47.41
AREA_TOP, AREA_BOTTOM = 7.15, 34.32
GUTTER = 0.42
PAD_X, PAD_TOP, PAD_BOTTOM = 0.45, 0.35, 0.45
SUB_GUTTER = 0.5                      # between sub-columns inside one column box
HEADER_PT = 54
LINE = 1.2207                         # Calibri line height, in em
MIN_PANEL_GAP = 0.45                  # inches between panels in a column
MAX_WIDTH_RATIO = 1.2                 # widest column vs. the mean column width

# Per-board layout. "split" lists, per column, how many panels go in each sub-column.
# "scale" enlarges the body text of panels whose title matches (the board-1 intro and closing
# statement were printed in large type on the original board).
BOARDS = [
    dict(md='board_1_1775-1848.md', out='poster_1_1775-1848',
         title='The Communications Revolution, 1775–1848',
         part='Part 1 of 3',
         split={1: [3, 3]},
         scale={'THE COMMUNICATIONS REVOLUTION': 1.45, None: 1.45}),
    dict(md='board_2_1850-1940.md', out='poster_2_1850-1940',
         title='The Communications Revolution, 1850–1940',
         part='Part 2 of 3', split={}, scale={}),
    dict(md='board_3_1940-2020.md', out='poster_3_1940-2020',
         title='The Communications Revolution, 1940–2020',
         part='Part 3 of 3', split={}, scale={}),
]


# --------------------------------------------------------------------------- parsing

@dataclass
class Run:
    text: str
    bold: bool = False
    italic: bool = False
    sup: bool = False
    underline: bool = False


@dataclass
class Block:
    kind: str            # 'bullet', 'sub', 'para', 'subhead'
    runs: list


@dataclass
class Panel:
    title: list | None   # runs, or None for an untitled panel
    title_key: str | None
    blocks: list = field(default_factory=list)


@dataclass
class Column:
    header: list | None  # lines of the header card, or None
    panels: list = field(default_factory=list)


TOKEN = re.compile(r'(\*\*|\*|</?sup>|</?u>|\[/?red\])')


def parse_runs(text):
    """Split inline Markdown (bold, italic, <sup>, <u>) into styled runs; drop [red] markers."""
    text = re.sub(r'\[\?(.*?)\?\]', r'\1', text)      # [?x?] -> x (best reading)
    runs, state = [], dict(bold=False, italic=False, sup=False, underline=False)
    for piece in TOKEN.split(text):
        if piece == '**':
            state['bold'] = not state['bold']
        elif piece == '*':
            state['italic'] = not state['italic']
        elif piece in ('<sup>', '</sup>'):
            state['sup'] = piece == '<sup>'
        elif piece in ('<u>', '</u>'):
            state['underline'] = piece == '<u>'
        elif piece in ('[red]', '[/red]'):
            continue
        elif piece:
            runs.append(Run(piece, **state))
    return runs


def plain(runs):
    return ''.join(r.text for r in runs)


def parse_board(path):
    columns = []
    for line in path.read_text().split('\n'):
        if line.startswith('## Transcriber notes'):
            break
        s = line.rstrip()
        if (not s or s.startswith(('# ', 'Source photo:', 'Author of original exhibit:', '<!--',
                                   '[image:'))
                or re.match(r'^\((Title|Printed)\b.*\)$', s)):
            continue
        if s.startswith('## Column: '):
            h = s[len('## Column: '):]
            columns.append(Column(None if h.startswith('Left (') else h.split(' / ')))
        elif s.startswith('### '):
            t = s[4:]
            if re.fullmatch(r'\((.*\b)?untitled\)', t):
                columns[-1].panels.append(Panel(None, None))
            else:
                runs = parse_runs(t)
                columns[-1].panels.append(Panel(runs, plain(runs)))
        elif s.startswith('  - '):
            columns[-1].panels[-1].blocks.append(Block('sub', parse_runs(s[4:])))
        elif s.startswith('  '):           # continuation line of a sub-item
            columns[-1].panels[-1].blocks.append(Block('subpara', parse_runs(s.strip())))
        elif s.startswith('- '):
            columns[-1].panels[-1].blocks.append(Block('bullet', parse_runs(s[2:])))
        elif re.fullmatch(r'\*\*[^*]+\*\*:?', s):
            columns[-1].panels[-1].blocks.append(Block('subhead', parse_runs(s)))
        else:
            columns[-1].panels[-1].blocks.append(Block('para', parse_runs(s)))
    return columns


# --------------------------------------------------------------------------- measuring

_fonts = {}


def font(bold, italic):
    key = (bold, italic)
    if key not in _fonts:
        name = 'Carlito-' + {(0, 0): 'Regular', (1, 0): 'Bold', (0, 1): 'Italic',
                             (1, 1): 'BoldItalic'}[(int(bold), int(italic))] + '.ttf'
        _fonts[key] = ImageFont.truetype(str(FONT_DIR / name), 1000)
    return _fonts[key]


def text_width_pt(text, size, bold=False, italic=False):
    return font(bold, italic).getlength(text) * size / 1000


def wrap_lines(runs, size, width_pt, force_bold=False):
    """Greedy word wrap, as PowerPoint does; returns the number of lines."""
    words = []                      # (text, width) pieces including their trailing space
    for r in runs:
        rsize = size * (0.65 if r.sup else 1)
        for w in re.findall(r'\S+\s*|\s+', r.text):
            words.append(text_width_pt(w, rsize, r.bold or force_bold, r.italic))
    lines, cur = 1, 0.0
    for w in words:
        if cur and cur + w > width_pt + 0.5:
            lines += 1
            cur = w
        else:
            cur += w
    return lines


@dataclass
class Style:
    body: float          # body size, pt
    @property
    def title(self): return round(self.body * 1.22)
    @property
    def gap(self): return self.body * 0.30      # space before each bullet, pt
    @property
    def indent(self): return self.body * 0.95   # bullet indent, pt
    @property
    def sub_indent(self): return self.body * 1.9


def block_metrics(block, st, scale):
    """(left margin pt, font size pt, space-before pt, bullet char) for one block."""
    b = st.body * scale
    return {
        'bullet': (st.indent * scale, b, st.gap * scale, '•'),
        'sub': (st.sub_indent * scale, b, st.gap * 0.6 * scale, '–'),
        'subpara': (st.sub_indent * scale, b, st.gap * 0.3 * scale, None),
        'para': (0, b, st.gap * 1.6 * scale, None),
        'subhead': (0, b, st.gap * 2.2 * scale, None),
    }[block.kind]


def panel_height_pt(panel, st, width_pt, scale):
    h = 0.0
    if panel.title:
        ts = st.title * scale
        h += wrap_lines(panel.title, ts, width_pt, force_bold=True) * ts * LINE
    for i, blk in enumerate(panel.blocks):
        marl, size, before, _ = block_metrics(blk, st, scale)
        if i or panel.title:
            h += before
        h += wrap_lines(blk.runs, size, width_pt - marl, force_bold=blk.kind == 'subhead') * size * LINE
    return h


def header_height_in(col, width_in):
    if not col.header:
        return 0.0
    n = sum(wrap_lines([Run(l, bold=True)], HEADER_PT, width_in * 72) for l in col.header)
    return n * HEADER_PT * LINE / 72 + 0.35


def subcolumns(col, split):
    if not split:
        return [col.panels]
    out, i = [], 0
    for n in split:
        out.append(col.panels[i:i + n])
        i += n
    return out


def scale_for(panel, board):
    return board['scale'].get(panel.title_key, 1.0)


def column_fits(col, ci, board, st, width_in):
    subs = subcolumns(col, board['split'].get(ci))
    inner_w = width_in - 2 * PAD_X
    sub_w = (inner_w - SUB_GUTTER * (len(subs) - 1)) / len(subs)
    avail = (AREA_BOTTOM - AREA_TOP) - PAD_TOP - PAD_BOTTOM - header_height_in(col, inner_w)
    for panels in subs:
        need = sum(panel_height_pt(p, st, sub_w * 72, scale_for(p, board)) for p in panels) / 72
        need += MIN_PANEL_GAP * (len(panels) - 1)
        if need > avail:
            return False
    return True


def min_width(col, ci, board, st):
    lo, hi = 3.0, AREA_RIGHT - AREA_LEFT
    if not column_fits(col, ci, board, st, hi):
        return None
    for _ in range(30):
        mid = (lo + hi) / 2
        lo, hi = (lo, mid) if column_fits(col, ci, board, st, mid) else (mid, hi)
    return hi


def layout(columns, board, start=44.0):
    """Largest body size (0.5 pt steps, at most `start`) at which all columns fit; widths shared out."""
    total = AREA_RIGHT - AREA_LEFT - GUTTER * (len(columns) - 1)
    best = None
    size = start
    while size >= 16:
        st = Style(size)
        widths = [min_width(c, i, board, st) for i, c in enumerate(columns)]
        # Columns may differ in width, but none wider than MAX_WIDTH_RATIO x the mean (weighted
        # by sub-columns), so the poster keeps an even rhythm like the original boards.
        nsub = [len(board['split'].get(i, [1])) for i in range(len(columns))]
        unit = total / sum(nsub)
        if all(widths) and all(w <= MAX_WIDTH_RATIO * unit * k for w, k in zip(widths, nsub)) \
                and sum(widths) <= total:
            # Share out the spare width so columns are as even as possible (water-filling).
            lo, hi = 0.0, max(widths) / min(nsub)
            for _ in range(50):
                level = (lo + hi) / 2
                if sum(max(w, level * k) for w, k in zip(widths, nsub)) > total:
                    hi = level
                else:
                    lo = level
            out = [max(w, lo * k) for w, k in zip(widths, nsub)]
            spare = (total - sum(out)) / len(out)
            best = (st, [w + spare for w in out])
            break
        size -= 0.5
    if best is None:
        raise SystemExit(f"{board['md']}: text does not fit even at 16 pt")
    return best


# --------------------------------------------------------------------------- writing

def set_runs(paragraph, runs, size, bold=None, color=None):
    for r in runs:
        run = paragraph.add_run()
        run.text = r.text
        f = run.font
        f.size = Pt(size)
        f.bold = r.bold if bold is None else (bold or r.bold)
        f.italic = r.italic
        if r.underline:
            f.underline = True
        if r.sup:
            run._r.get_or_add_rPr().set('baseline', '30000')
        if color is not None:
            f.color.rgb = color


def para_format(p, marl_pt=0, indent_pt=0, before_pt=0, bullet=None):
    pPr = p._p.get_or_add_pPr()
    pPr.set('marL', str(int(marl_pt * 12700)))
    pPr.set('indent', str(int(-indent_pt * 12700)))
    lnSpc = pPr.makeelement(qn('a:lnSpc'), {})
    pct = lnSpc.makeelement(qn('a:spcPct'), {'val': '100000'})
    lnSpc.append(pct)
    spcBef = pPr.makeelement(qn('a:spcBef'), {})
    spcBef.append(spcBef.makeelement(qn('a:spcPts'), {'val': str(int(before_pt * 100))}))
    spcAft = pPr.makeelement(qn('a:spcAft'), {})
    spcAft.append(spcAft.makeelement(qn('a:spcPts'), {'val': '0'}))
    for el in (lnSpc, spcBef, spcAft):
        pPr.append(el)
    if bullet:
        pPr.append(pPr.makeelement(qn('a:buFont'), {'typeface': 'Arial'}))
        pPr.append(pPr.makeelement(qn('a:buChar'), {'char': bullet}))
    else:
        pPr.append(pPr.makeelement(qn('a:buNone'), {}))


def textbox(slide, x, y, w, h):
    tb = slide.shapes.add_textbox(Emu(int(x * EMU)), Emu(int(y * EMU)), Emu(int(w * EMU)), Emu(int(h * EMU)))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.auto_size = None
    for side in ('margin_left', 'margin_right', 'margin_top', 'margin_bottom'):
        setattr(tf, side, 0)
    tf.vertical_anchor = MSO_ANCHOR.TOP
    return tb, tf


def write_panel(slide, panel, st, scale, x, y, w, h):
    tb, tf = textbox(slide, x, y, w, h)
    first = True

    def new_para():
        nonlocal first
        if first:
            first = False
            return tf.paragraphs[0]
        return tf.add_paragraph()

    if panel.title:
        p = new_para()
        para_format(p)
        set_runs(p, panel.title, st.title * scale, bold=True, color=ACCENT)
    for i, blk in enumerate(panel.blocks):
        marl, size, before, bullet = block_metrics(blk, st, scale)
        p = new_para()
        para_format(p, marl, (st.indent * 0.95 * scale) if bullet else 0,
                    before if (i or panel.title) else 0, bullet)
        set_runs(p, blk.runs, size, bold=True if blk.kind == 'subhead' else None)
    return tb


def replace_text(shape, lines):
    """Replace a template text shape's text, keeping the first run's formatting per paragraph."""
    tf = shape.text_frame
    paras = tf.paragraphs
    for i, line_runs in enumerate(lines):
        p = paras[min(i, len(paras) - 1)]
        if i >= len(paras):
            new = copy.deepcopy(paras[-1]._p)
            tf._txBody.append(new)
            p = tf.paragraphs[-1]
        rs = p.runs
        proto = rs[0]._r if rs else None
        for r in rs:
            p._p.remove(r._r)
        for text, kw in line_runs:
            el = copy.deepcopy(proto)
            el.find(qn('a:t')).text = text
            rPr = el.find(qn('a:rPr'))
            rPr.attrib.pop('baseline', None)
            for k, v in kw.items():
                rPr.set(k, v)
            end = p._p.find(qn('a:endParaRPr'))
            if end is not None:
                end.addprevious(el)
            else:
                p._p.append(el)
    for extra in tf.paragraphs[len(lines):]:
        tf._txBody.remove(extra._p)


HAMSCI_LOGO_PX = (779, 167)  # pixel size of the HamSCI logo inside the template's logo group


def hamsci_logo_only(slide, group, slide_width):
    """Replace the footer's partner-logo group with the HamSCI logo alone, centered.

    The template's footer group holds five logos (Scranton, HamSCI, NSF, NASA Partner, ARDC).
    These outreach posters are not sponsored work, so only HamSCI is kept, at its printed size.
    """
    xfrm = group._element.find(qn('p:grpSpPr')).find(qn('a:xfrm'))
    off, ext = xfrm.find(qn('a:off')), xfrm.find(qn('a:ext'))
    choff, chext = xfrm.find(qn('a:chOff')), xfrm.find(qn('a:chExt'))
    sx = int(ext.get('cx')) / int(chext.get('cx'))
    sy = int(ext.get('cy')) / int(chext.get('cy'))
    logo = next(sh for sh in group.shapes
                if sh.shape_type == 13 and sh.image.size == HAMSCI_LOGO_PX)
    w, h = logo.width * sx, logo.height * sy
    top = int(off.get('y')) + (logo.top - int(choff.get('y'))) * sy
    blob = io.BytesIO(logo.image.blob)
    group._element.getparent().remove(group._element)
    slide.shapes.add_picture(blob, Emu(int((slide_width - w) / 2)), Emu(int(top)),
                             Emu(int(w)), Emu(int(h)))


def build(board, template, outdir, size):
    columns = parse_board(REPO / 'transcription' / board['md'])
    st, widths = layout(columns, board, size)

    prs = Presentation(str(template))
    slide = prs.slides[0]
    by_name = {sh.name: sh for sh in slide.shapes}
    for name in ('Rounded Rectangle 25', 'Rounded Rectangle 56', 'Rounded Rectangle 57'):
        el = by_name[name]._element
        el.getparent().remove(el)
    replace_text(by_name['TextBox 12'], [[(board['title'], {})]])
    replace_text(by_name['Rectangle 3'], [
        [('Charlie Cebula, AC2ZU', {'b': '1'})],
        [(f"From his tri-fold exhibit “The Communications Revolution” · {board['part']}", {})],
    ])
    replace_text(by_name['TextBox 66'], [[('hamsci.org', {})]])
    replace_text(by_name['TextBox 36'], [[(board['part'], {})]])
    hamsci_logo_only(slide, by_name['Group 1'], prs.slide_width)

    x = AREA_LEFT
    for ci, (col, w) in enumerate(zip(columns, widths)):
        box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Emu(int(x * EMU)),
                                     Emu(int(AREA_TOP * EMU)), Emu(int(w * EMU)),
                                     Emu(int((AREA_BOTTOM - AREA_TOP) * EMU)))
        box.adjustments[0] = 0.04 * 15.33 / w if w > 15.33 else 0.04
        box.fill.background()
        box.line.color.rgb = ACCENT
        box.line.width = Pt(2)
        box.shadow.inherit = False

        inner_x, inner_w = x + PAD_X, w - 2 * PAD_X
        y = AREA_TOP + PAD_TOP
        if col.header:
            hh = header_height_in(col, inner_w)
            tb, tf = textbox(slide, inner_x, y, inner_w, hh)
            for i, line in enumerate(col.header):
                p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
                para_format(p)
                p.alignment = PP_ALIGN.CENTER
                set_runs(p, [Run(line, bold=True)], HEADER_PT, color=ACCENT)
            y += hh

        subs = subcolumns(col, board['split'].get(ci))
        sub_w = (inner_w - SUB_GUTTER * (len(subs) - 1)) / len(subs)
        avail = AREA_BOTTOM - PAD_BOTTOM - y
        for si, panels in enumerate(subs):
            sx = inner_x + si * (sub_w + SUB_GUTTER)
            hs = [panel_height_pt(p, st, sub_w * 72, scale_for(p, board)) / 72 for p in panels]
            gap = (avail - sum(hs)) / max(len(panels) - 1, 1)
            gap = min(gap, 1.6)  # don't spread panels absurdly far apart
            py = y
            for p, ph in zip(panels, hs):
                write_panel(slide, p, st, scale_for(p, board), sx, py, sub_w, ph)
                py += ph + gap
        x += w + GUTTER

    out = outdir / f"{board['out']}.pptx"
    prs.save(str(out))
    print(f"{out.relative_to(REPO)}: body {st.body} pt, column widths "
          + ', '.join(f'{w:.1f}' for w in widths) + ' in')


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--template', type=Path,
                    default=Path(os.environ.get('HAMSCI_POSTER_TEMPLATE', DEFAULT_TEMPLATE)))
    args = ap.parse_args()
    outdir = REPO / 'posters'
    # One body size for the whole set: the largest at which every poster fits.
    size = min(layout(parse_board(REPO / 'transcription' / b['md']), b)[0].body for b in BOARDS)
    for board in BOARDS:
        build(board, args.template, outdir, size)


if __name__ == '__main__':
    main()

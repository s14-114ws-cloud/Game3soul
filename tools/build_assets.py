#!/usr/bin/env python3
"""Slice the source sheets in assets/src into individual WebP sprites and
embed them into the game HTML.

Usage: python3 tools/build_assets.py soul_tether_v51_title_ui.html

The script is idempotent: it rewrites only
  * the `keyVisual` / `portraitSheet` entries of ART.paths
  * the single line that starts with `const UI_SPRITES=`
Every embedded WebP is decoded again after encoding and compared against its
source so that a corrupted asset (like the v50 sheets) can never be shipped.
"""
import base64
import io
import json
import re
import sys
from pathlib import Path

import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'assets' / 'src'


def load(name):
    return Image.open(SRC / f'{name}.png').convert('RGBA')


def trim(im, pad=4, thr=8):
    a = np.asarray(im)[:, :, 3]
    ys, xs = np.where(a > thr)
    if not len(xs):
        return im
    x0, x1 = max(0, xs.min() - pad), min(im.width, xs.max() + 1 + pad)
    y0, y1 = max(0, ys.min() - pad), min(im.height, ys.max() + 1 + pad)
    return im.crop((x0, y0, x1, y1))


def isolate(im, keep_ratio=.15):
    """Drop fragments of neighbouring sprites: small pieces touching the crop edge."""
    from scipy import ndimage
    a = np.asarray(im).copy()
    lab, n = ndimage.label(ndimage.binary_dilation(a[:, :, 3] > 8, iterations=2))
    if n < 2:
        return im
    sizes = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))
    big = sizes.max()
    h, w = lab.shape
    edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    for i in range(1, n + 1):
        if i in edge and sizes[i - 1] < big * keep_ratio:
            a[lab == i, 3] = 0
    return Image.fromarray(a, 'RGBA')


def cell(im, x0, y0, x1, y1, max_w=None):
    c = trim(isolate(im.crop((x0, y0, x1, y1))))
    if max_w and c.width > max_w:
        c = c.resize((max_w, round(c.height * max_w / c.width)), Image.LANCZOS)
    return c


def white_to_alpha(im, tol=34):
    """Flood-fill the white sheet background (from every border pixel) to transparent."""
    rgb = im.convert('RGB')
    w, h = rgb.size
    marker = (255, 0, 255)
    seeds = [(x, 0) for x in range(0, w, 7)] + [(x, h - 1) for x in range(0, w, 7)]
    seeds += [(0, y) for y in range(0, h, 7)] + [(w - 1, y) for y in range(0, h, 7)]
    for s in seeds:
        p = rgb.getpixel(s)
        if min(p) > 255 - tol and p != marker:
            ImageDraw.floodfill(rgb, s, marker, thresh=tol)
    a = np.asarray(rgb).copy()
    mask = (a[:, :, 0] == 255) & (a[:, :, 1] == 0) & (a[:, :, 2] == 255)
    out = np.dstack([np.asarray(im.convert('RGB')), np.where(mask, 0, 255).astype(np.uint8)])
    # soften the 1px fringe left by anti-aliased white edges
    img = Image.fromarray(out, 'RGBA')
    return img


def hue_to_spirit(im):
    """Fallback spirit-theme frame: shift warm gold/orange hues toward cold blue."""
    rgba = np.asarray(im).astype(np.float32)
    hsv = np.asarray(im.convert('RGB').convert('HSV')).astype(np.float32)
    h = hsv[:, :, 0]
    warm = (h < 45) | (h > 235)
    h = np.where(warm, (h + 150) % 256, h)
    s = np.where(warm, hsv[:, :, 1] * .85, hsv[:, :, 1])
    out = Image.fromarray(np.dstack([h, s, hsv[:, :, 2]]).astype(np.uint8), 'HSV').convert('RGB')
    return Image.fromarray(np.dstack([np.asarray(out), rgba[:, :, 3].astype(np.uint8)]), 'RGBA')


def encode(im, quality=93):
    try:
        return _encode(im, quality)
    except AssertionError:
        try:
            return _encode(im, 96)   # tiny frames with soft glow need a finer quantiser
        except AssertionError:
            buf = io.BytesIO()
            im.save(buf, 'WEBP', lossless=True, method=6)
            raw = buf.getvalue()
            return 'data:image/webp;base64,' + base64.b64encode(raw).decode(), len(raw)


def _encode(im, quality=86):
    buf = io.BytesIO()
    if im.mode == 'RGBA' and np.asarray(im)[:, :, 3].min() == 255:
        im = im.convert('RGB')
    im.save(buf, 'WEBP', quality=quality, method=6, alpha_quality=100)
    raw = buf.getvalue()
    # verification: decode again and compare
    back = Image.open(io.BytesIO(raw))
    back.load()
    assert back.size == im.size, 'size mismatch after re-decode'
    a = np.asarray(back.convert('RGBA')).astype(np.int16)
    b = np.asarray(im.convert('RGBA')).astype(np.int16)
    err = np.abs(a - b)[:, :, :3][np.asarray(im.convert('RGBA'))[:, :, 3] > 128].mean() if (b[:, :, 3] > 128).any() else 0
    assert err < 12, f'WebP re-decode error too large ({err:.1f})'
    return 'data:image/webp;base64,' + base64.b64encode(raw).decode(), len(raw)


# Labeled character sheet (2172x724, 11 cards per row with captions below).
# Order, top row: ST7 inspector, ST1 nurse, ST2 lamp spirit, ST3 librarian, ST4 armor,
# ST6 raven, ST9 inverted researcher, Shiki, K-04, ST12 weaver, EX zero observer.
# Bottom row: Mashiro, Haru, Towa, Shigure, Mio, Ren, N-03, library-committee ghost,
# child ghost, factory-worker ghost, grave monk.
LABELED_CARDS = [
    [(5, 211), (224, 425), (433, 644), (652, 854), (863, 1060), (1068, 1261), (1271, 1450),
     (1458, 1632), (1640, 1809), (1818, 1992), (2000, 2166)],
    [(6, 189), (197, 381), (389, 563), (572, 812), (821, 1015), (1024, 1219), (1228, 1409),
     (1417, 1598), (1606, 1786), (1795, 1975), (1983, 2164)],
]
LABELED_ROWS = [(3, 325), (372, 665)]


def labeled_sheet(cell=(200, 316)):
    src = white_to_alpha(load('labeledSheet'))
    out = Image.new('RGBA', (cell[0] * 11, cell[1] * 2), (0, 0, 0, 0))
    for r, (cols, (y0, y1)) in enumerate(zip(LABELED_CARDS, LABELED_ROWS)):
        for c, (x0, x1) in enumerate(cols):
            card = trim(src.crop((x0, y0, x1, y1)), pad=0)
            # cover-fit: centre-crop overly wide cards (Shigure) to the cell aspect
            want = card.height * cell[0] / cell[1]
            if card.width > want:
                cut = (card.width - want) / 2
                card = card.crop((round(cut), 0, round(card.width - cut), card.height))
            card = card.resize(cell, Image.LANCZOS)
            out.alpha_composite(card, (c * cell[0], r * cell[1]))
    return out


# Boss face sheet (2172x724): 12 cards per row, top row = normal, bottom row = angry.
# Column order by character: nurse, lantern spirit, librarian, armor, golem, raven,
# inverted researcher (ST9), soul-core master (ST8), K-04 (ST11), Shiki (ST10),
# weaver mother (ST12), zero observer (EX). (The sheet's ST7-ST11 captions are shifted.)
BOSS_FACE_COLS = [(5, 170), (177, 348), (353, 522), (533, 694), (706, 864), (871, 1039), (1045, 1209),
                  (1221, 1390), (1396, 1562), (1567, 1738), (1744, 1951), (1958, 2166)]
BOSS_FACE_ROWS = [(100, 399), (410, 711)]


def boss_face_sheet(cell=(200, 316)):
    src = load('bossFaces')
    out = Image.new('RGBA', (cell[0] * 12, cell[1] * 2), (0, 0, 0, 0))
    for r, (y0, y1) in enumerate(BOSS_FACE_ROWS):
        for c, (x0, x1) in enumerate(BOSS_FACE_COLS):
            card = src.crop((x0, y0, x1, y1))
            want = card.height * cell[0] / cell[1]
            if card.width > want:
                cut = (card.width - want) / 2
                card = card.crop((round(cut), 0, round(card.width - cut), card.height))
            out.alpha_composite(card.resize(cell, Image.LANCZOS), (c * cell[0], r * cell[1]))
    return out

def build():
    sprites = {}

    # ---- title / menu buttons (7 rows: new, continue, stage, options, credits, back, quit) ----
    names = ['new', 'continue', 'stage', 'options', 'credits', 'back', 'quit']
    bm = load('bodyMenu')
    rows = [(0, 172), (168, 338), (335, 502), (500, 665), (662, 826), (822, 962), (955, 1086)]
    for n, (y0, y1) in zip(names, rows):
        sprites[f'menu.body.{n}'] = cell(bm, 50, y0, 735, y1, 520)
        sprites[f'menu.body.{n}.on'] = cell(bm, 730, y0, 1410, y1, 520)
    sm = load('spiritMenu')
    rows = [(0, 192), (186, 355), (350, 512), (508, 672), (668, 830), (822, 955), (950, 1086)]
    for n, (y0, y1) in zip(names, rows):
        sprites[f'menu.spirit.{n}'] = cell(sm, 5, y0, 726, y1, 520)
        sprites[f'menu.spirit.{n}.on'] = cell(sm, 728, y0, 1446, y1, 520)

    # ---- touch controls ----
    bc = load('bodyControl')
    six = [(30, 262), (262, 496), (498, 726), (726, 952), (958, 1186), (1186, 1418)]
    for i, n in enumerate(['jump', 'act', 'attack']):
        sprites[f'ctl.body.{n}'] = cell(bc, *(six[i * 2][0], 0, six[i * 2][1], 256), 200)
        sprites[f'ctl.body.{n}.on'] = cell(bc, *(six[i * 2 + 1][0], 0, six[i * 2 + 1][1], 256), 200)
    for i, n in enumerate(['soul', 'hint', 'pause']):
        sprites[f'ctl.body.{n}'] = cell(bc, six[i * 2][0], 254, six[i * 2][1], 506, 200)
        sprites[f'ctl.body.{n}.on'] = cell(bc, six[i * 2 + 1][0], 254, six[i * 2 + 1][1], 506, 200)
    cw = (1418 - 28) / 8
    for i, n in enumerate(['resume', 'restart', 'title', 'next']):
        sprites[f'ctl.body.{n}'] = cell(bc, round(28 + cw * i * 2), 504, round(28 + cw * (i * 2 + 1)), 702, 180)
        sprites[f'ctl.body.{n}.on'] = cell(bc, round(28 + cw * (i * 2 + 1)), 504, round(28 + cw * (i * 2 + 2)), 702, 180)
    sprites['ctl.body.up'] = cell(bc, 38, 700, 198, 880, 140)
    sprites['ctl.body.up.on'] = cell(bc, 196, 700, 356, 880, 140)
    sprites['ctl.body.down'] = cell(bc, 394, 700, 551, 882, 140)
    sprites['ctl.body.down.on'] = cell(bc, 549, 700, 706, 882, 140)
    sprites['ctl.body.left'] = cell(bc, 38, 876, 198, 1060, 140)
    sprites['ctl.body.right'] = cell(bc, 394, 876, 553, 1060, 140)
    sprites['ctl.body.right.on'] = cell(bc, 549, 876, 706, 1060, 140)
    # the body sheet has no lit "left" arrow: mirror the lit "right" arrow
    sprites['ctl.body.left.on'] = sprites['ctl.body.right.on'].transpose(Image.FLIP_LEFT_RIGHT)

    sc = load('spiritControl')
    six = [(25, 268), (268, 505), (505, 728), (728, 958), (958, 1205), (1205, 1442)]
    for i, n in enumerate(['jump', 'act', 'attack']):
        sprites[f'ctl.spirit.{n}'] = cell(sc, six[i * 2][0], 10, six[i * 2][1], 272, 200)
        sprites[f'ctl.spirit.{n}.on'] = cell(sc, six[i * 2 + 1][0], 10, six[i * 2 + 1][1], 272, 200)
    six = [(30, 265), (265, 500), (500, 730), (730, 962), (962, 1200), (1200, 1442)]
    for i, n in enumerate(['soul', 'hint', 'pause']):
        sprites[f'ctl.spirit.{n}'] = cell(sc, six[i * 2][0], 270, six[i * 2][1], 512, 200)
        sprites[f'ctl.spirit.{n}.on'] = cell(sc, six[i * 2 + 1][0], 270, six[i * 2 + 1][1], 512, 200)
    mid = [(30, 246), (246, 448), (448, 648), (648, 815), (815, 1002), (1002, 1205), (1205, 1432)]
    for i, n in enumerate(['resume', 'resume.on', 'restart', 'restart.on', 'title', 'title.on', 'next']):
        sprites[f'ctl.spirit.{n}'] = cell(sc, mid[i][0], 510, mid[i][1], 724, 180)
    sprites['ctl.spirit.next.on'] = sprites['ctl.spirit.next']
    arrows = [(22, 198), (198, 382), (382, 562), (562, 742)]
    for i, n in enumerate(['up', 'up.on', 'down', 'down.on']):
        sprites[f'ctl.spirit.{n}'] = cell(sc, arrows[i][0], 716, arrows[i][1], 890, 140)
    for i, n in enumerate(['left', 'left.on', 'right', 'right.on']):
        sprites[f'ctl.spirit.{n}'] = cell(sc, arrows[i][0], 884, arrows[i][1], 1070, 140)
    # newer crescent-moon spirit set replaces the above; JUMP becomes DASH in spirit mode
    from spirit_ctl import controls as spirit_controls
    for k, im in spirit_controls(SRC, {'up': 140, 'down': 140, 'left': 140, 'right': 140}).items():
        sprites[f'ctl.spirit.{k}'] = im
    sprites['ctl.spirit.jump'] = sprites['ctl.spirit.dash']
    sprites['ctl.spirit.jump.on'] = sprites['ctl.spirit.dash.on']

    # ---- frame kit (body), spirit variant derived by hue shift until a real one exists ----
    fk = load('frameKit')
    frames = {
        'panel': (8, 4, 862, 400),
        'bar': (866, 34, 1434, 252),
        'plate': (824, 230, 1438, 470),
        'square': (24, 374, 562, 876),
        'hp': (572, 426, 1434, 586),
        'sp': (572, 584, 1434, 734),
        'tether': (572, 732, 1434, 884),
        'nameplate': (20, 868, 580, 1074),
        'small': (600, 878, 1056, 1074),
        'corner': (1072, 866, 1262, 1056),
        'star': (1290, 884, 1432, 1040),
    }
    for n, box in frames.items():
        im = cell(fk, *box, 640)
        sprites[f'frame.body.{n}'] = im
        sprites[f'frame.spirit.{n}'] = hue_to_spirit(im)

    # ---- icon sheet (from the combo sheet) ----
    ic = load('iconCombo')
    icons = {
        'heart': (14, 700, 162, 846), 'spirit': (172, 690, 330, 852), 'thread': (338, 680, 500, 872),
        'shard': (500, 676, 656, 870), 'book': (654, 680, 820, 878), 'shrine': (818, 672, 1012, 878),
        'flame': (1012, 676, 1140, 868), 'key': (1138, 680, 1286, 868), 'gear': (1282, 692, 1438, 856),
        'bell': (14, 852, 186, 1078), 'radio': (180, 852, 316, 1052), 'phone': (312, 868, 432, 1056),
        'anchor': (424, 850, 606, 1072), 'rat': (596, 880, 768, 1070), 'crow': (754, 880, 1014, 1078),
        'warning': (966, 898, 1144, 1070), 'skull': (1132, 856, 1314, 1078), 'crystal': (1310, 862, 1430, 1060),
    }
    for n, box in icons.items():
        sprites[f'icon.{n}'] = cell(ic, *box, 96)

    # ---- ST7 boss battle frames (source faces RIGHT) ----
    from inspector_frames import frames as inspector_frames
    for k, im in inspector_frames(SRC / 'inspectorSheet.png').items():
        sprites[f'insp.{k}'] = im

    # ---- ST1/4/6/9/11/EX boss battle frames (source faces RIGHT) ----
    from boss_frames import frames as boss_frames
    for k, im in boss_frames(SRC / 'bossSheetA.png').items():
        sprites[f'boss.{k}'] = im

    # ---- ST2/3/5/8/10/12 boss battle frames (transparent sheets, source faces RIGHT) ----
    from boss_frames2 import frames as boss_frames2
    for k, im in boss_frames2(SRC).items():
        sprites[f'boss.{k}'] = im

    # ---- Ren (player) and Mio (companion), with body-centre anchors ----
    from hero_frames import frames as hero_frames
    for k, v in hero_frames(SRC).items():
        sprites[f'hero.{k}'] = v
    from spirit_dash import frames as dash_frames
    for k, v in dash_frames(SRC).items():
        sprites[f'hero.{k}'] = v
    from hero_frames import npc_frames
    for k, v in npc_frames(SRC).items():
        sprites[f'hero.{k}'] = v

    # ---- stage backgrounds (216px tall) and title logo ----
    from stage_bgs import stage_backgrounds, title_logo
    for n, im in stage_backgrounds(SRC).items():
        sprites[f'bg.{n}'] = im
    sprites['title.logo'] = title_logo(SRC)

    # ---- regular enemies (per-stage sets) ----
    from enemy_frames import frames as enemy_frames
    for k, im in enemy_frames(SRC).items():
        sprites[f'en.{k}'] = im

    # ---- possessable animals/machines and gimmicks ----
    from prop_frames import frames as prop_frames
    for k, im in prop_frames(SRC).items():
        sprites[f'prop.{k}'] = im

    # ---- stage devices and boss-arena set pieces ----
    from device_frames import frames as device_frames
    for k, im in device_frames(SRC).items():
        sprites[f'prop.{k}'] = im

    # ---- combat / soul effects ----
    from fx_frames import frames as fx_frames
    for k, im in fx_frames(SRC).items():
        sprites[f'prop.{k}'] = im

    # ---- screen atmosphere (rain, petals, embers, fog, spirit haze) ----
    from atmo_frames import frames as atmo_frames
    for k, im in atmo_frames(SRC).items():
        sprites[f'prop.{k}'] = im

    # ---- story CG stills (full screen, drawn at 384x216 logical) ----
    for k in ['cgOpen', 'cgBlade', 'cgM10', 'cgDrag', 'cgMorning', 'cgWake', 'cgSunrise',
              'cgCrow', 'cgTrain', 'cgZeroRoom', 'cgObserver']:
        sprites[f'prop.cg.{k}'] = load(k).convert('RGB')

    # ---- stage-select thumbnails (480x270) ----
    from stage_thumbs import thumbs
    for n, im in thumbs(SRC).items():
        sprites[f'thumb.{n}'] = im

    # ---- whole images (keep their own keys in ART.paths) ----
    art = {
        'keyVisual': load('keyVisual').convert('RGB'),
        'portraitSheet': white_to_alpha(load('portraitSheet')),
        'portraitSheet2': white_to_alpha(load('portraitSheet2')),
        'allySheet': white_to_alpha(load('allySheet')),
        'portraitSheet3': labeled_sheet(),
        'bossFaceSheet': boss_face_sheet(),
    }
    return sprites, art


def main():
    target = Path(sys.argv[1])
    sprites, art = build()
    total = 0
    enc = {}
    anchors = {}
    for k, im in list(sprites.items()):
        if isinstance(im, tuple):
            im, anchors[k] = im[0], im[1:]
            sprites[k] = im
    for k, im in sprites.items():
        uri, n = encode(im)
        enc[k] = {'src': uri, 'w': im.width, 'h': im.height}
        if k.startswith(('boss.', 'insp.', 'en.', 'prop.')) and k != 'insp.ticket':
            enc[k]['s'] = 2
        if k.startswith('prop.cg.'):
            enc[k]['s'] = round(im.width / 384, 4)
        if k.startswith('bg.'):
            enc[k]['s'] = round(im.height / 216, 4)
        if k == 'insp.ticket':
            enc[k]['s'] = 2
        if k in anchors:
            enc[k]['ax'] = anchors[k][0]
            if len(anchors[k]) > 1:
                enc[k]['s'] = anchors[k][1]
        total += n
    art_enc = {}
    for k, im in art.items():
        uri, n = encode(im, 84)
        art_enc[k] = uri
        total += n
        print(f'  {k:16s} {im.size} {n // 1024} KB')
    print(f'{len(sprites)} sprites, total embedded {total // 1024} KB')

    html = target.read_text(encoding='utf-8')
    lines = html.split('\n')
    for k, uri in art_enc.items():
        pat = re.compile(r"^(\s*)" + k + r":'data:image/webp;base64,[^']*'(,?)$")
        hit = [i for i, l in enumerate(lines) if pat.match(l)]
        if hit:
            i = hit[0]
            m = pat.match(lines[i])
            lines[i] = f"{m.group(1)}{k}:'{uri}'{m.group(2)}"
        else:
            # new sheet: insert after keyVisual
            i = [i for i, l in enumerate(lines) if re.match(r"^\s*keyVisual:'data:image/webp", l)][0]
            lines.insert(i + 1, f"  {k}:'{uri}',")
    js = 'const UI_SPRITES=' + json.dumps(enc, separators=(',', ':')) + ';'
    hit = [i for i, l in enumerate(lines) if l.startswith('const UI_SPRITES=')]
    if hit:
        lines[hit[0]] = js
    else:
        i = [i for i, l in enumerate(lines) if l.startswith('const EXTRA_ART=')][0]
        lines.insert(i, js)
    target.write_text('\n'.join(lines), encoding='utf-8')

    # contact sheet for visual QA
    qa = Image.new('RGBA', (1600, 2400), (40, 40, 48, 255))
    x = y = rowh = 0
    for k, im in sprites.items():
        t = im.convert("RGBA")
        t.thumbnail((150, 120))
        if x + t.width > 1600:
            x, y, rowh = 0, y + rowh + 6, 0
        qa.alpha_composite(t, (x, y))
        x += t.width + 6
        rowh = max(rowh, t.height)
    qa = qa.crop((0, 0, 1600, y + rowh + 4))
    out = ROOT / 'assets' / 'qa_sprites.png'
    qa.save(out)
    print('QA sheet:', out)


if __name__ == '__main__':
    main()

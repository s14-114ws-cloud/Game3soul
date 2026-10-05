"""Regular enemy frames from assets/src/enemySheet.png (transparent, 4x3 stage
panels + an EX strip; each panel has 3 sprite rows; figures face RIGHT).

Frames inside a row are found by splitting on columns where the opaque body
(alpha > 170) has a gap; soft glow is kept but cut at the split lines.
"""
import numpy as np
from PIL import Image
from boss_frames import shrink, RES

PANEL_X = [(5, 365), (368, 727), (728, 1088), (1090, 1446)]
PANEL_ROWS = [[(54, 130), (132, 208), (209, 282)],
              [(333, 409), (411, 491), (493, 569)],
              [(624, 694), (697, 779), (781, 861)]]
EX_ROW = (918, 1042)
EX_SPLIT = [(10, 360), (380, 880), (885, 1440)]
# sheet panel label -> game stage (the sheet follows the boss-face numbering:
# its ST7 is the inverted researcher (game ST9), ST9 is K-04 (game ST11),
# ST11/ST12 are both the weaver (game ST12)). Game ST7 has no set.
PANEL_STAGE = {(0, 0): 1, (0, 1): 2, (0, 2): 3, (0, 3): 4,
               (1, 0): 5, (1, 1): 6, (1, 2): 9, (1, 3): 8,
               (2, 0): 11, (2, 1): 10, (2, 2): 12, (2, 3): 12}
# row target heights in the 384x216 game (source rows are ~70px)
# ST7 subway sheet: ticket drone, subway ghost, tether-biter
ST7_ROWS = [(140, 390), (460, 765), (838, 1020)]
ST7_EW = (175, 205, 195)
ST7_H = (24, 36, 22)
ROW_H = {
    1: (36, 26, 22), 2: (30, 26, 22), 3: (22, 20, 36), 4: (38, 36, 28),
    5: (38, 34, 30), 6: (26, 24, 22), 9: (36, 30, 22), 8: (28, 22, 26),
    11: (36, 36, 34), 10: (22, 24, 30), 12: (30, 36, 34), 13: (26, 32, 36),
}


def split_cols(a, min_w=10, gap=2):
    core = (a[:, :, 3] > 170).sum(0)
    cols, s, run = [], None, 0
    for x, v in enumerate(core):
        if v > 1:
            if s is None:
                s = x
            run = 0
        elif s is not None:
            run += 1
            if run > gap:
                if x - run - s >= min_w:
                    cols.append((s, x - run + 1))
                s, run = None, 0
    if s is not None and len(core) - s >= min_w:
        cols.append((s, len(core)))
    return cols


def row_frames(sheet, x0, x1, y0, y1, height, ew=None):
    a = sheet[y0:y1, x0:x1]
    cols = split_cols(a)
    # split segments where touching sprites merged: cut at the thinnest columns
    core = (a[:, :, 3] > 170).sum(0).astype(float)
    ew = ew or max(30, (y1 - y0) * .75)
    fixed = []
    for c0, c1 in cols:
        k = int(round((c1 - c0) / ew))
        if (c1 - c0) > 1.6 * ew and k >= 2:
            cuts = [c0]
            for j in range(1, k):
                g = c0 + (c1 - c0) * j / k
                lo, hi = int(g - ew / 3), int(g + ew / 3)
                cuts.append(lo + int(np.argmin(core[lo:hi])))
            cuts.append(c1)
            fixed += [(cuts[j], cuts[j + 1]) for j in range(k)]
        else:
            fixed.append((c0, c1))
    cols = fixed
    out = []
    for i, (c0, c1) in enumerate(cols):
        # include glow up to half-way to the neighbouring frames
        l = c0 - (c0 - cols[i - 1][1]) // 2 if i else max(0, c0 - 6)
        r = c1 + (cols[i + 1][0] - c1) // 2 if i + 1 < len(cols) else min(a.shape[1], c1 + 6)
        seg = a[:, l:r].copy()
        # drop thin horizontal rule fragments (panel/label lines) caught in the band
        from scipy import ndimage
        lab, n = ndimage.label(seg[:, :, 3] > 40)
        for j, sl in enumerate(ndimage.find_objects(lab)):
            if sl and (sl[0].stop - sl[0].start) <= 3 and (sl[1].stop - sl[1].start) >= 10:
                seg[:, :, 3][lab == j + 1] = 0
        im = Image.fromarray(seg, 'RGBA')
        bb = Image.fromarray((np.asarray(im)[:, :, 3] > 40).astype(np.uint8) * 255).getbbox()
        if not bb:
            continue
        im = im.crop(bb)
        core_h = Image.fromarray((np.asarray(im)[:, :, 3] > 170).astype(np.uint8) * 255).getbbox()
        ch = (core_h[3] - core_h[1]) if core_h else im.height
        out.append(shrink(im, height * RES / max(ch, 1)))
    return out


def frames(src_dir):
    sheet = np.asarray(Image.open(src_dir / 'enemySheet.png').convert('RGBA'))
    out = {}
    for (pr, pc), stage in PANEL_STAGE.items():
        x0, x1 = PANEL_X[pc]
        sub = 'b' if (pr, pc) == (2, 3) else 'a'
        for r, (y0, y1) in enumerate(PANEL_ROWS[pr]):
            for i, im in enumerate(row_frames(sheet, x0, x1, y0, y1, ROW_H[stage][r])):
                out[f'e{stage}{sub}{r}.{i}'] = im
    st7 = np.asarray(Image.open(src_dir / 'enemySheet7.png').convert('RGBA'))
    for r, ((y0, y1), h, ew) in enumerate(zip(ST7_ROWS, ST7_H, ST7_EW)):
        for i, im in enumerate(row_frames(st7, 20, 1440, y0, y1, h, ew=ew)):
            out[f'e7a{r}.{i}'] = im
    for r, (x0, x1) in enumerate(EX_SPLIT):
        for i, im in enumerate(row_frames(sheet, x0, x1, *EX_ROW, ROW_H[13][r])):
            out[f'e13a{r}.{i}'] = im
    return out

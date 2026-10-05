"""Battle frames for ST2/3/5/8/10/12 bosses from the transparent 5-column sheets
assets/src/bossSheetB.png (ST8..EX) and bossSheetC.png (ST1..ST7). Figures face RIGHT.
Neighbouring glows overlap, so each cell keeps only the opaque body whose centre lies
in that cell, plus a soft halo around it.
"""
import numpy as np
from PIL import Image
from scipy import ndimage
from boss_frames import shrink

COLS_B = [(140, 348), (348, 596), (596, 832), (832, 1132), (1132, 1448)]
COLS_C = [(150, 330), (330, 584), (584, 806), (806, 1124), (1124, 1448)]
ROWS_B = {'soulCore': (0, 198), 'shiki': (380, 572), 'weaver': (730, 908)}
ROWS_C = {'lantern': (148, 308), 'scribe': (300, 462), 'golem': (610, 772)}
# frame names per column; scale -> standing pose about the boss hitbox height
NAMES = {
    'soulCore': (['idle1', 'idle2', 'atk1', 'atk2', 'burst'], 60 / 150),
    'shiki': (['idle1', 'atk1', 'atk2', 'barrage', 'final'], 58 / 140),
    'weaver': (['idle1', 'idle2', 'atk1', 'p2', 'p3'], 66 / 150),
    'lantern': (['idle1', 'idle2', 'idle3', 'atk1', 'burst'], 54 / 130),
    'scribe': (['idle1', 'idle2', 'idle3', 'atk1', 'final'], 54 / 130),
    'golem': (['idle1', 'walk', 'idle2', 'slam', 'core'], 58 / 125),
}


def cut(sheet, x0, y0, x1, y1, pad=40):
    H, W = sheet.shape[:2]
    X0, Y0, X1, Y1 = max(0, x0 - pad), max(0, y0 - 2), min(W, x1 + pad), min(H, y1 + 2)
    a = sheet[Y0:Y1, X0:X1].copy()
    core = a[:, :, 3] > 170
    lab, n = ndimage.label(ndimage.binary_dilation(core, iterations=2))
    if n:
        keep = []
        cxlo, cxhi = x0 - X0, x1 - X0
        for i, s in enumerate(ndimage.find_objects(lab)):
            cx = (s[1].start + s[1].stop) / 2
            cy = (s[0].start + s[0].stop) / 2 + Y0
            size = (lab[s] == i + 1).sum()
            tall = s[0].stop - s[0].start
            if cxlo <= cx < cxhi and y0 <= cy < y1 and size > 60 and tall > 8:
                keep.append(i + 1)
        body = np.isin(lab, keep)
        halo = ndimage.binary_dilation(body, iterations=7)
        a[:, :, 3] = np.where(halo, a[:, :, 3], 0)
    im = Image.fromarray(a, 'RGBA')
    bb = Image.fromarray(np.where(a[:, :, 3] > 24, 255, 0).astype(np.uint8)).getbbox()
    return im.crop(bb)


def frames(src_dir):
    out = {}
    for fname, rows, cols in [('bossSheetB.png', ROWS_B, COLS_B), ('bossSheetC.png', ROWS_C, COLS_C)]:
        sheet = np.asarray(Image.open(src_dir / fname).convert('RGBA'))
        for boss, (y0, y1) in rows.items():
            names, scale = NAMES[boss]
            for (x0, x1), n in zip(cols, names):
                out[f'{boss}.{n}'] = shrink(cut(sheet, x0, y0, x1, y1), scale)
    return out

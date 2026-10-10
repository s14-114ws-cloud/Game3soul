"""Large gimmicks + extra tile sets from gimmickSheet (flat grey, labelled cells).

Gimmicks: 3 states each (idle / active / done-or-gone), stored at 2x, face RIGHT.
Tiles: ST4 weapons facility, ST10 M-10 memory, EX zero room -> tile.<theme>.{l,m1,m2,r}
using the same band/surface convention as floor_tiles.
"""
import numpy as np
from PIL import Image
from boss_frames import shrink, RES
from prop_frames import key_grey
from floor_tiles import keyed, THICK

# (name, y0, y1, [(x0, x1) x3], logical height of the idle frame, solid keying?)
GIMMICKS = [
    ('rift', 45, 275, [(14, 147), (148, 362), (362, 475)], 60, False),
    ('console', 55, 275, [(500, 652), (652, 818), (818, 980)], 44, True),
    ('lens', 45, 275, [(998, 1172), (1175, 1356), (1358, 1525)], 40, True),
    ('pylon', 362, 548, [(15, 140), (145, 280), (282, 410)], 46, False),
    ('page', 375, 532, [(428, 535), (538, 676), (680, 775)], 18, False),
    ('turret', 362, 535, [(790, 900), (900, 998), (1005, 1172)], 30, True),
    ('perch', 362, 545, [(1184, 1286), (1290, 1398), (1402, 1520)], 30, False),
]
TILESETS = [('weapons', 755, 820, [(18, 146), (172, 339), (365, 483)], 859, 965, (18, 161)),
            ('memory', 755, 820, [(546, 667), (694, 860), (885, 995)], 859, 965, (559, 668)),
            ('zero', 755, 820, [(1042, 1168), (1190, 1360), (1382, 1495)], 859, 965, (1042, 1182))]


def bbox(im, th=24):
    return im.getchannel('A').point(lambda v: 255 if v > th else 0).getbbox()


def frames(src):
    rgb = np.asarray(Image.open(src / 'gimmickSheet.png').convert('RGB'))
    bg = tuple(int(v) for v in rgb[3, 3])
    out = {}
    for name, y0, y1, cols, h, solid in GIMMICKS:
        ims = [(keyed if solid else key_grey)(rgb[y0:y1, x0:x1], bg) for x0, x1 in cols]
        b0 = bbox(ims[0], 90)
        sc = h * RES / (b0[3] - b0[1])
        for i, im in enumerate(ims):
            out[f'gim.{name}{i}'] = shrink(im.crop(bbox(im)), sc)
    for theme, y0, y1, cols, uy0, uy1, ucol in TILESETS:
        ims = [keyed(rgb[y0:y1, x0:x1], bg) for x0, x1 in cols]
        tops = [np.nonzero(np.asarray(im)[:, :, 3] > 24)[0] for im in ims]
        surf = tops[1].min()
        mid_h = tops[1].max() + 1 - surf
        top = min(t.min() for t in tops)
        bot = max(t.max() + 1 for t in tops)
        sc = THICK * RES / mid_h
        for nm, (x0, x1), im in zip(['l', 'm1', 'r'], cols, ims):
            xs = np.nonzero(np.asarray(im)[:, :, 3].max(0) > 24)[0]
            out[f'tile.{theme}.{nm}'] = (shrink(im.crop((xs[0], top, xs[-1] + 1, bot)), sc), round((surf - top) * sc), RES)
        out[f'tile.{theme}.m2'] = out[f'tile.{theme}.m1']
        under = keyed(rgb[uy0:uy1, ucol[0]:ucol[1]], bg)
        out[f'tile.{theme}.under'] = shrink(under.crop(bbox(under)), sc)
    return out

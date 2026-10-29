"""Second asset batch: ST2 grudge memory (3 states), spirit-flame trap (4 states),
platform underside tiles for the 9 base themes, and the ACT prompt plates (body / spirit / lit).
All on flat grey sheets.
"""
import numpy as np
from PIL import Image
from boss_frames import shrink, RES
from prop_frames import key_grey
from floor_tiles import keyed

GRUDGE = [(99, 422), (512, 913), (994, 1388)]
FLAME = [(15, 334), (375, 695), (737, 1057), (1099, 1418)]
UNDER = [(36, 153), (184, 300), (327, 436), (471, 587), (620, 746), (773, 899), (933, 1068), (1099, 1215), (1241, 1415)]
UNDER_THEMES = ['hosp', 'street', 'school', 'factory', 'grave', 'subway', 'tower', 'bound', 'cath']
PLATES = [(45, 477), (511, 931), (957, 1412)]


def crop(im):
    bb = im.getchannel('A').point(lambda v: 255 if v > 24 else 0).getbbox()
    return im.crop(bb)


def load(src, name):
    a = np.asarray(Image.open(src / f'{name}.png').convert('RGB'))
    return a, tuple(int(v) for v in a[4, 4])


def frames(src):
    out = {}
    a, bg = load(src, 'grudgeSheet')
    ims = [crop(key_grey(a[:, x0:x1], bg)) for x0, x1 in GRUDGE]
    sc = 24 * RES / ims[0].height
    for i, im in enumerate(ims):
        out[f'grudge{i}'] = shrink(im, sc)
    a, bg = load(src, 'spiritFlameSheet')
    ims = [key_grey(a[:, x0:x1], bg) for x0, x1 in FLAME]
    ims = [crop(im) for im in ims]
    base = ims[0]   # the floor seal: ~32px wide in game
    sc = 32 * RES / base.width
    for i, im in enumerate(ims):
        out[f'sflame{i}'] = shrink(im, sc)
    a, bg = load(src, 'underTiles')
    for t, (y0, y1) in zip(UNDER_THEMES, UNDER):
        im = crop(keyed(a[y0:y1, 30:1060], bg))
        # the strip already repeats 4x: keep one quarter so it tiles at a sensible size
        q = im.crop((0, 0, im.width // 4, im.height))
        out[f'tile.{t}.under'] = shrink(q, 26 * RES / q.height)
    a, bg = load(src, 'promptPlates')
    for i, (x0, x1) in enumerate(PLATES):
        im = crop(key_grey(a[300:640, x0:x1], bg) if i == 2 else keyed(a[300:640, x0:x1], bg))
        out[f'plate{i}'] = shrink(im, 15 * RES / im.height)
    return out

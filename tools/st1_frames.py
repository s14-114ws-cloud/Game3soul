"""ST1 opening: Ren asleep in the hospital bed (renBed, 3x4) and the evil spirit
pinning him down (evilSpirit: rows idle, idle, lash-out, dissolve). Flat grey sheets.

Bed rows: 0 = asleep (breathing), 1 = restless (twitching), 2 = waking up.
Spirit rows: 0+1 = idle loop, 2 = lash out (used as hit reaction), 3 = dissolve.
Both face RIGHT as drawn; stored at 2x.
"""
import numpy as np
from PIL import Image
from boss_frames import shrink, RES
from prop_frames import key_grey
from spirit_ctl import key_flood

BED_ROWS = [(80, 340), (395, 655), (712, 975)]
BED_COLS = [(8, 354), (368, 716), (730, 1078), (1092, 1440)]
BED_W = 74          # logical width of the bed in the 384x216 game
SPIRIT_ROWS = [((18, 290), [(14, 344), (365, 689), (710, 1053), (1085, 1401)]),
               ((300, 541), [(14, 342), (360, 701), (709, 1072), (1085, 1431)]),
               ((557, 782), [(15, 336), (345, 784), (784, 1435)]),
               ((803, 1053), [(23, 357), (381, 729), (739, 1090), (1100, 1420)])]
SPIRIT_SCALE = 54 / 230   # idle frames are ~230px tall in the sheet -> ~54px in game


def crop_key(arr, bg, box, solid=False):
    x0, y0, x1, y1 = box
    if solid:   # opaque prop: flood the grey from the border so dark hair/shadows stay opaque
        return key_flood(arr[y0:y1, x0:x1], bg)
    im = key_grey(arr[y0:y1, x0:x1], bg)
    bb = Image.fromarray((np.asarray(im)[:, :, 3] > 24).astype(np.uint8) * 255).getbbox()
    return im.crop(bb) if bb else im


def frames(src):
    out = {}
    bed = np.asarray(Image.open(src / 'renBed.png').convert('RGB'))
    bg = tuple(int(v) for v in bed[3, 3])
    for r, (y0, y1) in enumerate(BED_ROWS):
        for c, (x0, x1) in enumerate(BED_COLS):
            im = crop_key(bed, bg, (x0, y0, x1, y1), solid=True)
            out[f'renbed.{r * 4 + c}'] = shrink(im, BED_W * RES / im.width)
    ev = np.asarray(Image.open(src / 'evilSpirit.png').convert('RGB'))
    bg = tuple(int(v) for v in ev[3, 3])
    n = 0
    for r, ((y0, y1), cols) in enumerate(SPIRIT_ROWS):
        for i, (x0, x1) in enumerate(cols):
            im = crop_key(ev, bg, (x0, y0, x1, y1))
            out[f'evil.{["idle", "idle", "lash", "die"][r]}{(i + 4) if r == 1 else i}'] = shrink(im, SPIRIT_SCALE * RES)
    return out

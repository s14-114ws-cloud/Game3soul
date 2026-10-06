"""Spirit dash frames (spiritDash: 4 rows on a flat dark sheet, figure faces RIGHT).

Rows: 0 = rising dash (used for up / up-diagonal), 1 = low dash (down / down-diagonal),
2 = forward lunge (spare), 3 = horizontal dash. Frames in a row are split at the
thinnest column near equal spacing (smoke trails join neighbouring frames).
"""
import numpy as np
from PIL import Image
from scipy import ndimage
from hero_frames import key_dark, RES
from boss_frames import shrink

BG = (37, 40, 42)
ROWS = [(22, 272, 6, 'up'), (298, 482, 6, 'down'), (496, 724, 6, 'lunge'), (744, 920, 5, 'h')]
SCALE = .16


def split(m, k):
    cols = m.sum(0).astype(float)
    xs = np.nonzero(cols)[0]
    x0, x1 = xs[0], xs[-1] + 1
    cuts = [x0]
    for j in range(1, k):
        g = x0 + (x1 - x0) * j / k
        lo, hi = int(g - (x1 - x0) / k / 3), int(g + (x1 - x0) / k / 3)
        cuts.append(lo + int(np.argmin(cols[lo:hi])))
    cuts.append(x1)
    return list(zip(cuts, cuts[1:]))


def frames(src):
    rgb = np.asarray(Image.open(src / 'spiritDash.png').convert('RGB'))
    dev = np.abs(rgb.astype(np.float32) - np.array(BG, np.float32)).max(2)
    out = {}
    for y0, y1, k, name in ROWS:
        for i, (c0, c1) in enumerate(split(dev[y0:y1] > 40, k)):
            im = key_dark(rgb[y0:y1, c0:c1], BG)
            a = np.asarray(im)[:, :, 3]
            bb = Image.fromarray((a > 30).astype(np.uint8) * 255).getbbox()
            im = im.crop(bb)
            a = np.asarray(im)[:, :, 3].astype(float)
            # anchor on the body: strong pixels in the upper 70% (skip smoke and blade tip)
            core = a[: int(a.shape[0] * .7)] > 200
            ys, xs = np.nonzero(core)
            cx = float(np.median(xs)) if len(xs) else im.width / 2
            small = shrink(im, SCALE * RES)
            out[f'ren.dash.{name}{i + 1}'] = (small, round(cx * small.width / im.width), RES)
    return out

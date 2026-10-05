"""Stage devices (grey-background sheets) and boss-arena set pieces (transparent sheets).

Devices: (key, sheet, (x0, y0, x1, y1), logical height). Stored at 2x.
Set pieces: one landmark per stage drawn behind the boss arena.
"""
import numpy as np
from PIL import Image
from scipy import ndimage
from boss_frames import shrink, RES
from prop_frames import key_grey

D = []


def row(sheet, y0, y1, xs, names, h):
    for (x0, x1), n in zip(zip(xs, xs[1:]), names):
        D.append((n, sheet, (x0, y0, x1, y1), h))


# radio / bell / phone: idle, active, resonance, broken
q = [0, 362, 724, 1086, 1448]
row('devSheet1', 0, 345, q, ['radio.0', 'radio.1', 'radio.2', 'radio.3'], 22)
row('devSheet1', 335, 715, q, ['bell.0', 'bell.1', 'bell.2', 'bell.3'], 30)
row('devSheet1', 705, 1086, q, ['phone.0', 'phone.1', 'phone.2', 'phone.3'], 22)
# floor plate / socket pedestal / crystal: idle, variant, active, broken
row('devSheet2', 0, 345, q, ['plate.0', 'plate.1', 'plate.2', 'plate.3'], 14)
row('devSheet2', 340, 690, q, ['socket.0', 'socket.1', 'socket.2', 'socket.3'], 30)
row('devSheet2', 670, 1086, q, ['crystal.0', 'crystal.1', 'crystal.2', 'crystal.3'], 42)
# capsule (empty, Mio, open) + restraint bed (normal, cursed, spirit leaving)
row('devSheet3', 0, 345, [0, 250, 495, 740], ['pod.0', 'pod.1', 'pod.2'], 58)
row('devSheet3', 0, 345, [740, 958, 1190, 1448], ['bed.0', 'bed.1', 'bed.2'], 26)
row('devSheet3', 340, 665, [0, 280, 505, 820], ['pole.0', 'pole.1', 'pole.2'], 34)
row('devSheet3', 655, 1086, [0, 262, 512, 780], ['archive.0', 'archive.1', 'archive.2'], 44)
row('devSheet3', 590, 1086, [778, 985, 1192, 1448], ['tank.0', 'tank.1', 'tank.2'], 46)
# shrine statue, ticket gate, crystal tank / armillary, loom throne, womb pod
row('devSheet4', 0, 500, [0, 300, 575], ['statue.0', 'statue.1'], 46)
row('devSheet4', 0, 500, [570, 820, 1045], ['turnstile.0', 'turnstile.1'], 46)
row('devSheet4', 0, 500, [1040, 1238, 1448], ['ctank.0', 'ctank.1'], 50)
row('devSheet4', 470, 1086, [0, 268, 565], ['armil.0', 'armil.1'], 44)
row('devSheet4', 470, 1086, [560, 818, 1072], ['loom.0', 'loom.1'], 54)
row('devSheet4', 470, 1086, [1068, 1255, 1448], ['womb.0', 'womb.1'], 30)

# set pieces: (key, sheet, quadrant box) -> logical height
SETS = [
    ('set.1', 'setSheet1', (0, 0, 800, 505)), ('set.2', 'setSheet1', (800, 0, 1448, 505)),
    ('set.3', 'setSheet1', (0, 450, 720, 1086)), ('set.4', 'setSheet1', (720, 500, 1448, 1086)),
    ('set.5', 'setSheet2', (0, 0, 764, 545)), ('set.6', 'setSheet2', (764, 0, 1448, 545)),
    ('set.7', 'setSheet2', (0, 540, 764, 1086)), ('set.8', 'setSheet2', (764, 540, 1448, 1086)),
    ('set.9', 'setSheet3', (0, 0, 724, 513)), ('set.10', 'setSheet3', (724, 0, 1448, 513)),
    ('set.11', 'setSheet3', (0, 513, 724, 1086)), ('set.12', 'setSheet3', (724, 513, 1448, 1086)),
    ('set.13', 'setSheet4', (0, 525, 724, 1086)), ('set.13pod', 'setSheet4', (0, 0, 724, 540)),
    ('set.13origin', 'setSheet4', (724, 0, 1448, 540)), ('set.true', 'setSheet4', (724, 525, 1448, 1086)),
]
SET_H = 128


def cut_quadrant(a, x0, y0, x1, y1, pad=60):
    """Keep opaque parts whose centre lies inside the quadrant (neighbours overlap at edges)."""
    H, W = a.shape[:2]
    X0, Y0, X1, Y1 = max(0, x0 - pad), max(0, y0 - pad), min(W, x1 + pad), min(H, y1 + pad)
    s = a[Y0:Y1, X0:X1].copy()
    lab, n = ndimage.label(ndimage.binary_dilation(s[:, :, 3] > 150, iterations=3))
    keep = []
    sizes = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1)) if n else [1]
    big = max(sizes)
    for i, sl in enumerate(ndimage.find_objects(lab)):
        if sizes[i] < big * .06:
            continue
        if not sl:
            continue
        cy, cx = (sl[0].start + sl[0].stop) / 2 + Y0, (sl[1].start + sl[1].stop) / 2 + X0
        if x0 <= cx < x1 and y0 <= cy < y1 and (lab[sl] == i + 1).sum() > 200:
            keep.append(i + 1)
    s[:, :, 3] = np.where(ndimage.binary_dilation(np.isin(lab, keep), iterations=10), s[:, :, 3], 0)
    im = Image.fromarray(s, 'RGBA')
    return im.crop(Image.fromarray((s[:, :, 3] > 20).astype(np.uint8) * 255).getbbox())


def frames(src):
    out, sheets = {}, {}
    for key, sheet, (x0, y0, x1, y1), h in D:
        if sheet not in sheets:
            arr = np.asarray(Image.open(src / f'{sheet}.png').convert('RGB'))
            sheets[sheet] = (arr, tuple(int(v) for v in arr[5, 5]))
        arr, bg = sheets[sheet]
        im = key_grey(arr[y0:y1, x0:x1], bg)
        bb = Image.fromarray((np.asarray(im)[:, :, 3] > 30).astype(np.uint8) * 255).getbbox()
        im = im.crop(bb)
        out['dev.' + key] = shrink(im, h * RES / im.height)
    for key, sheet, box in SETS:
        a = np.asarray(Image.open(src / f'{sheet}.png').convert('RGBA'))
        im = cut_quadrant(a, *box, pad=0 if sheet == 'setSheet3' else 60)
        out[key] = shrink(im, SET_H * RES / im.height)
    return out

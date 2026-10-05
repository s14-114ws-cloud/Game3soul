"""Possessable animals/machines and stage gimmicks from flat grey-background sheets.

Each item: (key, sheet, box(x0,y0,x1,y1), target logical height, flip).
'flip' marks source frames that face LEFT so every stored frame faces RIGHT.
Stored at 2x (RES) like the other sprites.
"""
import numpy as np
from PIL import Image
from scipy import ndimage
from boss_frames import shrink, RES

ITEMS = [
    # rat (faces right)
    ('rat.idle1', 'ratSheet', (330, 150, 605, 365), 15, 0), ('rat.idle2', 'ratSheet', (618, 140, 875, 365), 16, 0),
    ('rat.run1', 'ratSheet', (12, 500, 294, 716), 14, 0), ('rat.run2', 'ratSheet', (293, 502, 602, 716), 14, 0),
    ('rat.run3', 'ratSheet', (590, 520, 928, 716), 13, 0), ('rat.run4', 'ratSheet', (895, 536, 1246, 716), 12, 0),
    ('rat.act1', 'ratSheet', (283, 815, 576, 1124), 20, 0), ('rat.act2', 'ratSheet', (587, 912, 943, 1126), 13, 0),
    # crow (perched frames face left; flying frames face right)
    ('crow.perch1', 'crowSheet', (37, 318, 273, 647), 26, 1), ('crow.perch2', 'crowSheet', (297, 318, 534, 647), 26, 1),
    ('crow.fly1', 'crowSheet', (554, 222, 870, 642), 22, 0), ('crow.fly2', 'crowSheet', (885, 273, 1240, 633), 19, 0),
    ('crow.fly3', 'crowSheet', (7, 683, 328, 1042), 19, 0), ('crow.fly4', 'crowSheet', (328, 688, 656, 1044), 19, 0),
    ('crow.dive', 'crowSheet', (665, 692, 914, 1056), 20, 0), ('crow.grab', 'crowSheet', (910, 691, 1238, 1051), 20, 0),
    # factory robot (idle frames face left)
    ('robot.idle1', 'robotSheet', (348, 18, 598, 396), 30, 1), ('robot.idle2', 'robotSheet', (633, 22, 894, 395), 30, 1),
    ('robot.walk1', 'robotSheet', (50, 438, 321, 784), 28, 0), ('robot.walk2', 'robotSheet', (368, 431, 634, 786), 28, 0),
    ('robot.walk3', 'robotSheet', (658, 434, 913, 784), 28, 0), ('robot.walk4', 'robotSheet', (957, 430, 1216, 784), 28, 0),
    ('robot.arm', 'robotSheet', (59, 832, 592, 1179), 28, 0), ('robot.crank', 'robotSheet', (680, 821, 1205, 1182), 28, 0),
    # purple spirit barrier (narrow loop) — stretched to the wall rectangle at draw time
    ('wall.a1', 'wallSheet', (13, 616, 110, 797), 60, 0), ('wall.a2', 'wallSheet', (108, 616, 205, 798), 60, 0),
    ('wall.a3', 'wallSheet', (204, 616, 305, 797), 60, 0), ('wall.a4', 'wallSheet', (303, 621, 406, 797), 60, 0),
    # exit door: sealed / opening / open
    ('exit.sealed', 'exitSheet', (13, 240, 424, 984), 70, 0), ('exit.opening', 'exitSheet', (423, 240, 833, 991), 70, 0),
    ('exit.open', 'exitSheet', (831, 240, 1242, 995), 70, 0),
    # checkpoint shrine: dormant / lit / activating
    ('cp.off', 'cpSheet', (31, 79, 406, 540), 44, 0), ('cp.on', 'cpSheet', (430, 79, 820, 540), 44, 0),
    ('cp.burst', 'cpSheet', (821, 40, 1244, 548), 48, 0),
    # gate: closed / opening / open / sealed
    ('gate.closed', 'gateSheet', (28, 314, 326, 909), 100, 0), ('gate.opening', 'gateSheet', (322, 314, 628, 909), 100, 0),
    ('gate.open', 'gateSheet', (622, 314, 935, 909), 100, 0), ('gate.sealed', 'gateSheet', (931, 314, 1240, 909), 100, 0),
    # lever switch: off / moving / on
    ('lever.off', 'switchSheet', (13, 298, 311, 956), 26, 0), ('lever.mid', 'switchSheet', (314, 305, 635, 930), 26, 0),
    ('lever.on', 'switchSheet', (617, 296, 1019, 942), 26, 0),
]


def key_grey(rgb, bg):
    a = rgb.astype(np.float32)
    dev = np.abs(a - np.array(bg, np.float32)).max(2)
    al = np.clip((dev - 8) / 42, 0, 1)
    lab, n = ndimage.label(ndimage.binary_dilation(al > .5, iterations=3))
    if n:
        sizes = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))
        keep = [i + 1 for i, s in enumerate(sizes) if s > sizes.max() * .03]
        al = al * ndimage.binary_dilation(np.isin(lab, keep), iterations=4)
    col = np.clip(np.array(bg) + (a - np.array(bg)) / np.maximum(al[:, :, None], 1e-3), 0, 255)
    col = np.where(al[:, :, None] > 0, col, 0)
    return Image.fromarray(np.dstack([col, al * 255]).astype(np.uint8), 'RGBA')


def frames(src_dir):
    sheets, out = {}, {}
    for key, sheet, (x0, y0, x1, y1), h, flip in ITEMS:
        if sheet not in sheets:
            arr = np.asarray(Image.open(src_dir / f'{sheet}.png').convert('RGB'))
            sheets[sheet] = (arr, tuple(int(v) for v in arr[5, 5]))
        arr, bg = sheets[sheet]
        im = key_grey(arr[y0:y1, x0:x1], bg)
        bb = Image.fromarray((np.asarray(im)[:, :, 3] > 30).astype(np.uint8) * 255).getbbox()
        im = im.crop(bb)
        if flip:
            im = im.transpose(Image.FLIP_LEFT_RIGHT)
        out[key] = shrink(im, h * RES / im.height)
    return out

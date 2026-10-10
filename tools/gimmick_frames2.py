"""ST1/2/4/5/6/7/11/12 gimmicks from gimmickSheet2/3 (dark flat sheets, hand-set boxes).

Each entry: key -> (sheet, (x0, y0, x1, y1), logical height, solid). 'solid' flood-keys the
background from the box border (opaque props); otherwise colour-distance keying keeps glows soft.
Stored at 2x like the other props.
"""
import numpy as np
from PIL import Image
from boss_frames import shrink, RES
from prop_frames import key_grey
from floor_tiles import keyed

S2, S3 = 'gimmickSheet2', 'gimmickSheet3'
ITEMS = {
    'ticket0': (S2, (35, 111, 152, 332), 16, True), 'ticket1': (S2, (164, 91, 308, 362), 16, False),
    'ticket2': (S2, (321, 106, 493, 368), 16, False),
    'rail0': (S2, (553, 82, 963, 178), 12, True), 'rail1': (S2, (553, 186, 963, 290), 12, False),
    'rail2': (S2, (553, 300, 963, 400), 12, False),
    'whistle0': (S2, (1020, 75, 1139, 365), 22, True), 'whistle1': (S2, (1158, 75, 1281, 365), 22, False),
    'whistle2': (S2, (1300, 75, 1419, 364), 22, False),
    'k04e0': (S2, (27, 589, 198, 900), 30, False), 'k04e1': (S2, (180, 589, 345, 900), 30, False),
    'k04e2': (S2, (345, 589, 500, 900), 30, False), 'k04e3': (S2, (500, 589, 652, 900), 30, False),
    'pod0': (S2, (691, 580, 942, 925), 50, True), 'pod1': (S2, (942, 580, 1192, 925), 50, True),
    'pod2': (S2, (1192, 580, 1437, 925), 50, True),
    'lily0': (S2, (1045, 961, 1102, 1037), 8, False), 'lily1': (S2, (1138, 965, 1192, 1034), 8, False),
    'bed1': (S3, (23, 35, 440, 350), 30, True), 'bed0': (S3, (425, 35, 705, 192), 24, True),
    'mirror0': (S3, (764, 43, 960, 345), 44, True), 'mirror1': (S3, (977, 49, 1115, 345), 44, True),
    'mirror3': (S3, (1233, 47, 1407, 333), 42, True),
    'siphon0': (S3, (32, 395, 318, 709), 58, True), 'siphon1': (S3, (318, 395, 482, 709), 46, True),
    'haru0': (S3, (675, 425, 962, 702), 40, True), 'haru1': (S3, (1082, 455, 1226, 682), 38, True),
    'fuse0': (S3, (1273, 412, 1338, 560), 14, True), 'fuse1': (S3, (1342, 412, 1410, 560), 14, True),
    'seal0': (S3, (28, 762, 220, 1045), 38, True), 'seal1': (S3, (225, 762, 475, 1045), 38, False),
    'sealf0': (S3, (850, 850, 1120, 935), 8, True), 'sealf1': (S3, (1150, 790, 1440, 995), 8, False),
}


def frames(src):
    sheets, out = {}, {}
    for key, (sh, (x0, y0, x1, y1), h, solid) in ITEMS.items():
        if sh not in sheets:
            arr = np.asarray(Image.open(src / f'{sh}.png').convert('RGB'))
            sheets[sh] = (arr, tuple(int(v) for v in arr[5, 5]))
        arr, bg = sheets[sh]
        band = arr[y0:y1, x0:x1]
        im = keyed(band, bg) if solid else key_grey(band, bg)
        bb = im.getchannel('A').point(lambda v: 255 if v > 24 else 0).getbbox()
        im = im.crop(bb)
        out[f'gim2.{key}'] = shrink(im, h * RES / im.height)
    return out

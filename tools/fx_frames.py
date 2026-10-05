"""Priority-A effects from fxSheetA/B (dark grey background). Stored at 2x, facing RIGHT."""
import numpy as np
from PIL import Image
from boss_frames import shrink, RES
from prop_frames import key_grey

ROWS = [  # (prefix, sheet, y0, y1, x cuts, logical height)
    ('slashB', 'fxSheetB', 88, 215, [10, 270, 520, 815, 1100], 26),
    ('slashS', 'fxSheetB', 240, 445, [10, 265, 525, 810, 1110], 30),
    ('slashX', 'fxSheetB', 445, 700, [10, 200, 410, 660, 880, 1110], 36),
    ('hitB', 'fxSheetB', 700, 912, [20, 265, 575, 840, 1100], 24),
    ('hitS', 'fxSheetB', 920, 1125, [20, 270, 560, 850, 1100], 24),
    ('hurt', 'fxSheetB', 1130, 1360, [80, 340, 700, 1020], 34),
    ('vanB', 'fxSheetA', 110, 430, [12, 140, 265, 385, 500, 615, 715], 36),
    ('vanS', 'fxSheetA', 110, 430, [725, 880, 990, 1100, 1230, 1440], 36),
    ('rel', 'fxSheetA', 470, 770, [8, 225, 455, 720, 960, 1210, 1440], 52),
]
# fixed-scale rows (frames keep their relative size: growing pillars / rings, shrinking sigils)
FIXED = [  # (prefix, sheet, y0, y1, x cuts, logical height of the whole band)
    ('die', 'fxSheetC', 0, 378, [10, 200, 385, 590, 860, 1050, 1235, 1440], 112),
    ('core', 'fxSheetC', 405, 625, [20, 360, 700, 1070, 1430], 48),
    ('soul', 'fxSheetC', 640, 865, [30, 340, 600, 880, 1110, 1400], 42),
    ('wave', 'fxSheetC', 890, 1052, [15, 235, 520, 850, 1140, 1440], 26),
    ('sigB', 'fxSheetD', 12, 245, [40, 400, 740, 1060, 1320], 26),
    ('sigS', 'fxSheetD', 249, 494, [40, 400, 740, 1060, 1320], 26),
    ('sigD', 'fxSheetD', 494, 744, [40, 400, 740, 1060, 1320], 26),
    ('chain', 'fxSheetD', 755, 868, [5, 330, 620, 925, 1435], 9),
    ('chainBrk', 'fxSheetD', 885, 1062, [20, 400, 715, 1070, 1420], 15),
    ('erase', 'fxSheetE', 25, 290, [25, 300, 665, 1100, 1660], 70),
    ('sever', 'fxSheetE', 325, 540, [30, 230, 610, 1100, 1660], 48),
    ('cpRing', 'fxSheetE', 545, 800, [40, 250, 550, 955, 1660], 40),
    ('trail', 'fxSheetE', 808, 915, [25, 230, 500, 740, 1040, 1300, 1640], 12),
    ('shard', 'fxSheetF', 22, 175, [50, 215, 405, 600, 780, 975], 20),
    ('shardGet', 'fxSheetF', 22, 175, [975, 1150, 1330], 20),
    ('poss', 'fxSheetF', 192, 392, [30, 255, 460, 645, 895], 36),
    ('lamp', 'fxSheetF', 408, 568, [30, 195, 380], 22),
    ('train', 'fxSheetF', 408, 568, [385, 1000, 1645], 28),
    ('steam', 'fxSheetF', 572, 767, [35, 225, 460, 700, 940], 30),
    ('ifield', 'fxSheetF', 775, 922, [25, 430, 830, 1230, 1645], 26),
]
SINGLE = [  # (key, sheet, box, logical height)
    ('linkG', 'fxSheetA', (76, 860, 146, 980), 7), ('linkR', 'fxSheetA', (800, 862, 866, 982), 7),
    ('ringG', 'fxSheetA', (505, 845, 612, 985), 12), ('ringR', 'fxSheetA', (1195, 845, 1315, 975), 12),
]


def frames(src):
    sheets, out = {}, {}

    def get(name):
        if name not in sheets:
            arr = np.asarray(Image.open(src / f'{name}.png').convert('RGB'))
            sheets[name] = (arr, tuple(int(v) for v in arr[5, 5]))
        return sheets[name]

    def cut(name, x0, y0, x1, y1, h):
        arr, bg = get(name)
        im = key_grey(arr[y0:y1, x0:x1], bg)
        bb = Image.fromarray((np.asarray(im)[:, :, 3] > 25).astype(np.uint8) * 255).getbbox()
        return shrink(im.crop(bb), h * RES / (bb[3] - bb[1])) if bb else None

    for pre, name, y0, y1, xs, h in ROWS:
        for i, (x0, x1) in enumerate(zip(xs, xs[1:])):
            im = cut(name, x0, y0, x1, y1, h)
            if im:
                out[f'fx.{pre}.{i}'] = im
    for pre, name, y0, y1, xs, h in FIXED:
        arr, bg = get(name)
        for i, (x0, x1) in enumerate(zip(xs, xs[1:])):
            im = key_grey(arr[y0:y1, x0:x1], bg)
            bb = Image.fromarray((np.asarray(im)[:, :, 3] > 25).astype(np.uint8) * 255).getbbox()
            if bb:
                out[f'fx.{pre}.{i}'] = shrink(im.crop(bb), h * RES / (y1 - y0))
    for key, name, (x0, y0, x1, y1), h in SINGLE:
        out[f'fx.{key}'] = cut(name, x0, y0, x1, y1, h)
    return out

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
    for key, name, (x0, y0, x1, y1), h in SINGLE:
        out[f'fx.{key}'] = cut(name, x0, y0, x1, y1, h)
    return out

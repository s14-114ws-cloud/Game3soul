"""Priority-D screen atmosphere textures from fxSheetG (dark background).
rain: 8 animation tiles; petals / embers: one long drifting strip each;
fog: two horizontal bands; haze: two spirit-realm bands. Stored at 2x."""
import numpy as np
from PIL import Image
from boss_frames import shrink, RES
from prop_frames import key_grey

TILES = [('rain', 31, 196, [20, 200, 395, 590, 760, 940, 1095, 1255, 1430], 110)]
STRIPS = [  # key, box, logical height
    ('petal', (15, 255, 1435, 385), 46), ('ember', (20, 425, 1435, 560), 46),
    ('fogA', (15, 590, 1435, 690), 44), ('fogB', (15, 670, 1435, 780), 46),
    ('hazeA', (15, 810, 1435, 930), 48), ('hazeB', (15, 925, 1435, 1050), 48),
]


def frames(src):
    arr = np.asarray(Image.open(src / 'fxSheetG.png').convert('RGB'))
    bg = tuple(int(v) for v in arr[5, 5])
    out = {}

    def keyed(x0, y0, x1, y1):
        a = arr[y0:y1, x0:x1].astype(np.float32)
        dev = np.abs(a - np.array(bg, np.float32)).max(2)
        al = np.clip((dev - 6) / 60, 0, 1)
        col = np.clip(np.array(bg) + (a - np.array(bg)) / np.maximum(al[:, :, None], 1e-3), 0, 255)
        col = np.where(al[:, :, None] > 0, col, 0)
        return Image.fromarray(np.dstack([col, al * 255]).astype(np.uint8), 'RGBA')

    for key, y0, y1, xs, h in TILES:
        for i, (x0, x1) in enumerate(zip(xs, xs[1:])):
            out[f'atmo.{key}.{i}'] = shrink(keyed(x0, y0, x1, y1), h * RES / (y1 - y0))
    for key, (x0, y0, x1, y1), h in STRIPS:
        out[f'atmo.{key}'] = shrink(keyed(x0, y0, x1, y1), h * RES / (y1 - y0))
    return out

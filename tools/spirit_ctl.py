"""Spirit-mode touch controls (spiritControl2: crescent-moon badges on a flat grey sheet).

The background is removed by flood-filling the grey from the crop border, so the dark
navy badge interiors stay opaque. The sheet has no pressed states: '.on' frames are a
brightened copy.
"""
import numpy as np
from PIL import Image, ImageEnhance
from scipy import ndimage

BOXES = {
    'dash': (30, 15, 315, 340), 'attack': (325, 15, 605, 340), 'act': (610, 15, 900, 340),
    'hint': (900, 15, 1190, 340), 'pause': (1195, 15, 1515, 340),
    'soul': (15, 330, 272, 620), 'restart': (268, 330, 520, 620), 'resume': (512, 330, 768, 620),
    'next': (758, 330, 1012, 620), 'options': (1008, 330, 1265, 620), 'title': (1262, 330, 1525, 620),
    'up': (40, 655, 228, 1005), 'down': (220, 655, 410, 1005), 'left': (400, 655, 592, 1005),
    'right': (588, 655, 778, 1005),
}


def key_flood(rgb, bg):
    a = rgb.astype(np.float32)
    dev = np.abs(a - np.array(bg, np.float32)).max(2)
    near = dev < 14
    lab, _ = ndimage.label(near)
    border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    bgm = np.isin(lab, list(border))
    al = np.where(bgm, 0.0, 1.0)
    # soften the rim: pixels touching the background fade by how far they are from grey
    rim = ndimage.binary_dilation(bgm, iterations=2) & ~bgm
    al = np.where(rim, np.clip((dev - 4) / 30, 0, 1), al)
    # keep only the main badge (drop bits of neighbours caught in the crop)
    lab2, n = ndimage.label(ndimage.binary_dilation(al > .3, iterations=2))
    if n > 1:
        sizes = ndimage.sum(np.ones_like(lab2), lab2, range(1, n + 1))
        keep = [i + 1 for i, s in enumerate(sizes) if s > sizes.max() * .08]
        al = al * np.isin(lab2, keep)
    col = np.clip(np.array(bg) + (a - np.array(bg)) / np.maximum(al[:, :, None], 1e-3), 0, 255)
    col = np.where(al[:, :, None] > 0, col, 0)
    im = Image.fromarray(np.dstack([col, al * 255]).astype(np.uint8), 'RGBA')
    return im.crop(im.getchannel('A').point(lambda v: 255 if v > 20 else 0).getbbox())


def lit(im):
    rgb = ImageEnhance.Brightness(im.convert('RGB')).enhance(1.3)
    rgb = ImageEnhance.Color(rgb).enhance(1.15)
    return Image.merge('RGBA', (*rgb.split(), im.getchannel('A')))


def controls(src, sizes):
    sheet = Image.open(src / 'spiritControl2.png').convert('RGB')
    arr = np.asarray(sheet)
    bg = tuple(int(v) for v in arr[5, 5])
    out = {}
    for k, (x0, y0, x1, y1) in BOXES.items():
        im = key_flood(arr[y0:y1, x0:x1], bg)
        mw = sizes.get(k, 200)
        if im.width > mw:
            im = im.resize((mw, round(im.height * mw / im.width)), Image.LANCZOS)
        out[k] = im
        out[k + '.on'] = lit(im)
    return out

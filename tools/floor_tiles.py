"""Platform tiles (floorTiles: 9 theme rows x [left cap, mid A, mid B, right cap], grey sheet).

The four pieces of a row are cut to a common vertical band so they line up; every tile's
stored 'ax' field carries the walkable-surface offset from the top of that band (stored px).
Caps are cut down to their decorated outer end so short platforms still read mostly as mid.
"""
import numpy as np
from PIL import Image
from scipy import ndimage
from boss_frames import shrink, RES

THEMES = ['hosp', 'street', 'school', 'factory', 'grave', 'subway', 'tower', 'bound', 'cath']
ROWS = [(26, 117), (120, 224), (231, 335), (339, 451), (447, 573), (578, 684), (688, 795), (800, 924), (924, 1050)]
COLS = [(165, 462), (468, 754), (762, 1069), (1074, 1400)]
THICK = 13          # logical thickness of a mid tile (platform collision boxes are 8px)
CAP_KEEP = .42      # fraction of a cap kept (its outer end)


def keyed(band, bg):
    """Flood the flat grey from the band border to transparent; same size as the band."""
    a = band.astype(np.float32)
    dev = np.abs(a - np.array(bg, np.float32)).max(2)
    lab, _ = ndimage.label(dev < 14)
    border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    bgm = np.isin(lab, list(border))
    al = np.where(bgm, 0.0, 1.0)
    rim = ndimage.binary_dilation(bgm, iterations=2) & ~bgm
    al = np.where(rim, np.clip((dev - 4) / 30, 0, 1), al)
    col = np.clip(np.array(bg) + (a - np.array(bg)) / np.maximum(al[:, :, None], 1e-3), 0, 255)
    col = np.where(al[:, :, None] > 0, col, 0)
    return Image.fromarray(np.dstack([col, al * 255]).astype(np.uint8), 'RGBA')


def frames(src):
    rgb = np.asarray(Image.open(src / 'floorTiles.png').convert('RGB'))
    bg = tuple(int(v) for v in rgb[3, 3])
    out = {}
    for theme, (y0, y1) in zip(THEMES, ROWS):
        pieces = []
        for x0, x1 in COLS:
            im = keyed(rgb[y0:y1, x0:x1], bg)
            ys, xs = np.nonzero(np.asarray(im)[:, :, 3] > 24)
            pieces.append((im, ys.min(), ys.max() + 1, xs.min(), xs.max() + 1))
        surf = min(pieces[1][1], pieces[2][1])                 # top of the mid tiles
        mid_h = max(pieces[1][2], pieces[2][2]) - surf
        top = min(p[1] for p in pieces)
        bot = max(p[2] for p in pieces)
        scale = THICK * RES / mid_h
        for name, (im, _, _, l, r) in zip(['l', 'm1', 'm2', 'r'], pieces):
            im = im.crop((l, top, r, bot))
            if name == 'l':
                im = im.crop((0, 0, round(im.width * CAP_KEEP), im.height))
            elif name == 'r':
                im = im.crop((im.width - round(im.width * CAP_KEEP), 0, im.width, im.height))
            out[f'tile.{theme}.{name}'] = (shrink(im, scale), round((surf - top) * scale), RES)
    return out

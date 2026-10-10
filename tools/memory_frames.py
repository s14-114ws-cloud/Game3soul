"""Memory shard / lore stone / echo node (memorySheet: 3x3 on flat grey, 3 states per row:
idle, active, dissolving). Glow rows are keyed by colour distance (soft alpha); the stone
row is flood-keyed from the border so its grey rock stays opaque.
"""
import numpy as np
from PIL import Image
from boss_frames import shrink, RES
from prop_frames import key_grey
from floor_tiles import keyed

COLS = [(0, 512), (512, 1024), (1024, 1536)]
ROWS = [('shard', (0, 300), 22), ('lore', (300, 640), 34), ('echo', (640, 1024), 36)]


def frames(src):
    rgb = np.asarray(Image.open(src / 'memorySheet.png').convert('RGB'))
    bg = tuple(int(v) for v in rgb[3, 3])
    out = {}
    for name, (y0, y1), h in ROWS:
        ims = []
        for ci, (x0, x1) in enumerate(COLS):
            if name == 'echo' and ci == 1:
                x1 = 950          # a stray petal at the cell edge
            band = rgb[y0:y1, x0:x1]
            im = keyed(band, bg) if name == 'lore' else key_grey(band, bg)
            ims.append(im)
        # scale every state of a row by the idle frame's height so they stay consistent
        bb0 = ims[0].getchannel('A').point(lambda v: 255 if v > 60 else 0).getbbox()
        sc = h * RES / (bb0[3] - bb0[1])
        for i, im in enumerate(ims):
            bb = im.getchannel('A').point(lambda v: 255 if v > 20 else 0).getbbox()
            out[f'mem.{name}{i}'] = shrink(im.crop(bb), sc)
    return out

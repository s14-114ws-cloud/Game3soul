"""ST7 boss (無貌の検札官) battle frames, cut from assets/src/inspectorSheet.png.

The source sheet is drawn facing RIGHT on a flat navy background; frames are
keyed out by colour, cut per group and scaled per group so that the normal
standing pose is ~60 px tall in the 384x216 game canvas.
"""
import numpy as np
from PIL import Image
from scipy import ndimage

# (name, x0, y0, x1, y1)
GROUPS = {
    # basic motion row, source idle height ~140 px
    'motion': (60 * 1.25 / 140, [
        ('idle1', 468, 62, 570, 210), ('idle2', 572, 62, 682, 210), ('idle3', 688, 62, 796, 210),
        ('walk1', 805, 62, 884, 210), ('walk2', 898, 62, 982, 210), ('walk3', 994, 62, 1072, 210),
        ('back', 1084, 62, 1174, 210), ('guard', 1184, 62, 1300, 210), ('lantern', 1300, 58, 1396, 210),
        ('vanish', 1410, 58, 1520, 210),
    ]),
    # a single flying ticket (projectile), source ~44 px wide -> 12 px
    'ticket': (12 / 44, [('ticket', 1398, 330, 1470, 382)]),
    # hit / damage row, source height ~87 px
    'hit': (60 * 1.25 / 87, [
        ('hit1', 22, 740, 112, 824), ('hit2', 124, 740, 214, 824), ('hitBig', 228, 740, 326, 824),
        ('dissolve', 338, 738, 444, 824),
    ]),
    # final phase (large form), source height ~232 px -> 86 px in game
    'final': (86 * 1.25 / 232, [
        ('final1', 484, 772, 694, 984), ('final2', 708, 772, 992, 984), ('final3', 998, 772, 1226, 984),
        ('final4', 1230, 772, 1528, 984),
    ]),
}


def key_out(rgb):
    a = rgb.astype(int)
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    # background candidates: flat navy plus the blue-grey panel borders / floor strips
    cand = ((r <= 12) & (b - r >= 10) & (g - r >= 5) & (b < 52)) | ((b >= r + 8) & (b >= g + 2) & (r < 110))
    # only remove candidate regions connected to the crop edge, so dark navy cloth inside the figure stays
    lab, n = ndimage.label(cand)
    edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    bg = np.isin(lab, list(edge))
    fg = ~bg
    lab, n = ndimage.label(ndimage.binary_dilation(fg, iterations=1))
    if n:
        sizes = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))
        keep = np.isin(lab, [i + 1 for i, s in enumerate(sizes) if s >= max(40, sizes.max() * .02)])
        fg &= keep
    alpha = np.where(fg, 255, 0).astype(np.uint8)
    return Image.fromarray(np.dstack([rgb, alpha]), 'RGBA')


def frames(src_path):
    sheet = np.asarray(Image.open(src_path).convert('RGB'))
    out = {}
    for group, (scale, items) in GROUPS.items():
        for name, x0, y0, x1, y1 in items:
            im = key_out(sheet[y0:y1, x0:x1])
            bb = im.getbbox()
            im = im.crop(bb)
            w, h = max(1, round(im.width * scale)), max(1, round(im.height * scale))
            # downscale colour with LANCZOS on premultiplied data, then hard-threshold alpha for crisp pixels
            arr = np.asarray(im).astype(np.float32)
            arr[:, :, :3] *= arr[:, :, 3:4] / 255
            small = np.stack([np.asarray(Image.fromarray(arr[:, :, c].astype(np.uint8)).resize((w, h), Image.LANCZOS)).astype(np.float32)
                              for c in range(4)], 2)
            al = small[:, :, 3]
            rgb = np.where(al[:, :, None] > 0, small[:, :, :3] * 255 / np.maximum(al[:, :, None], 1), 0)
            alpha = np.where(al > 110, 255, 0)
            out[name] = Image.fromarray(np.dstack([np.clip(rgb, 0, 255), alpha]).astype(np.uint8), 'RGBA')
    return out

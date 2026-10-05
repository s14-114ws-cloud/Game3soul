"""Ren (player) and Mio (companion) frames from assets/src/renSheet.png and
mioSheet.png (dark navy backgrounds, figures face RIGHT).

Each entry: (name, x0, y0, x1, y1, body_center_x) in source pixels. The body
centre is stored as an anchor so wide slash frames stay aligned with the hitbox.
"""
import numpy as np
from PIL import Image
from scipy import ndimage
from boss_frames import shrink

REN_BG = (10, 15, 28)
MIO_BG = (6, 12, 30)
REN = {
    'body': (38 / 200, [
        ('idle1', 20, 55, 155, 262, 85), ('idle2', 155, 55, 305, 262, 228), ('idle3', 305, 55, 456, 262, 378),
        ('walk1', 462, 55, 606, 262, 535), ('walk2', 606, 55, 748, 262, 676), ('walk3', 748, 55, 892, 262, 818),
        ('walk4', 894, 55, 1044, 262, 966),
        ('jump1', 1058, 55, 1240, 258, 1150), ('jump2', 1240, 55, 1432, 258, 1336),
        ('atk1', 14, 300, 278, 496, 140), ('atk2', 280, 300, 646, 496, 452), ('atk3', 640, 300, 964, 496, 768),
        ('hurt1', 988, 318, 1210, 496, 1100), ('hurt2', 1212, 340, 1432, 496, 1322),
        ('blade1', 14, 800, 378, 1042, 196), ('blade2', 380, 800, 906, 1042, 640), ('blade3', 906, 800, 1432, 1042, 1130),
    ]),
    'spirit': (31 / 210, [
        ('float1', 16, 545, 210, 762, 122), ('float2', 222, 545, 416, 762, 322), ('float3', 418, 545, 702, 762, 560),
        ('atk1', 702, 545, 1096, 762, 905), ('atk2', 1064, 545, 1436, 762, 1205),
    ]),
}
MIO = (22 / 290, [
    ('idle1', 28, 128, 472, 442, 250), ('idle2', 478, 128, 890, 442, 690), ('idle3', 926, 128, 1372, 442, 1150),
    ('float1', 18, 468, 442, 718, 250), ('float2', 472, 468, 914, 718, 720), ('float3', 916, 468, 1432, 718, 1180),
    ('cast1', 78, 752, 662, 1082, 330), ('cast2', 690, 752, 1360, 1082, 1010),
])


def key_dark(rgb, bg):
    a = rgb.astype(np.float32)
    dev = np.abs(a - np.array(bg, np.float32)).max(2)
    al = np.clip((dev - 10) / 55, 0, 1)
    # drop pieces of neighbouring frames that touch the crop edge
    lab, n = ndimage.label(ndimage.binary_dilation(al > .5, iterations=2))
    if n > 1:
        sizes = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))
        edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
        drop = [i + 1 for i, s in enumerate(sizes) if i + 1 in edge and s < sizes.max() * .08]
        al = np.where(ndimage.binary_dilation(np.isin(lab, drop), iterations=3), 0, al)
    col = np.clip(np.array(bg) + (a - np.array(bg)) / np.maximum(al[:, :, None], 1e-3), 0, 255)
    col = np.where(al[:, :, None] > 0, col, 0)
    return Image.fromarray(np.dstack([col, al * 255]).astype(np.uint8), 'RGBA')


def cut(sheet, bg, scale, items, prefix):
    out = {}
    for name, x0, y0, x1, y1, cxs in items:
        im = key_dark(sheet[y0:y1, x0:x1], bg)
        bb = Image.fromarray((np.asarray(im)[:, :, 3] > 30).astype(np.uint8) * 255).getbbox()
        im = im.crop(bb)
        small = shrink(im, scale)
        ax = round((cxs - x0 - bb[0]) * small.width / im.width)
        out[f'{prefix}.{name}'] = (small, ax)
    return out


def frames(src_dir):
    ren = np.asarray(Image.open(src_dir / 'renSheet.png').convert('RGB'))
    mio = np.asarray(Image.open(src_dir / 'mioSheet.png').convert('RGB'))
    out = {}
    for kind, (scale, items) in REN.items():
        out.update(cut(ren, REN_BG, scale, items, 'ren.' + kind))
    out.update(cut(mio, MIO_BG, MIO[0], MIO[1], 'mio'))
    return out

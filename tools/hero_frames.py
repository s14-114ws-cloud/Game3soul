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


RES = 2   # heroes are stored at 2x and drawn at half size on the 2x canvas


def finish(im, x0, bbx, cxs, scale):
    small = shrink(im, scale * RES)
    ax = round((cxs - x0 - bbx) * small.width / im.width)
    return (small, ax, RES)


def cut(sheet, bg, scale, items, prefix):
    out = {}
    for name, x0, y0, x1, y1, cxs in items:
        im = key_dark(sheet[y0:y1, x0:x1], bg)
        bb = Image.fromarray((np.asarray(im)[:, :, 3] > 30).astype(np.uint8) * 255).getbbox()
        out[f'{prefix}.{name}'] = finish(im.crop(bb), x0, bb[0], cxs, scale)
    return out


# second sheets (transparent): soul release, left-behind body, ACT, spirit hurt, death; Mio expressions
REN2 = 38 / 270
REN2_ITEMS = [
    ('rel1', 206, 40, 352, 300, 275), ('rel2', 372, 30, 562, 300, 462), ('rel3', 576, 20, 782, 318, 690),
    ('limp1', 60, 298, 190, 548, 126), ('limp2', 252, 302, 384, 548, 318), ('limp3', 448, 302, 582, 548, 515),
    ('sit1', 652, 386, 866, 548, 740), ('sit2', 870, 386, 1084, 548, 960), ('sit3', 1090, 404, 1372, 548, 1190),
    ('act1', 14, 546, 196, 750, 105), ('act2', 268, 576, 446, 748, 360), ('act3', 515, 576, 674, 748, 600),
    ('act4', 744, 580, 893, 748, 810), ('act5', 989, 572, 1140, 748, 1070), ('act6', 1214, 570, 1370, 748, 1290),
    ('shurt1', 40, 746, 270, 936, 150), ('shurt2', 316, 750, 572, 956, 440), ('shurt3', 620, 758, 882, 944, 750),
    ('shurt4', 886, 766, 1125, 962, 1005),
    ('die1', 22, 902, 172, 1080, 95), ('die2', 177, 922, 321, 1080, 250), ('die3', 326, 954, 487, 1080, 405),
    ('die4', 492, 968, 683, 1080, 590), ('die5', 676, 988, 925, 1080, 800), ('die6', 924, 992, 1183, 1080, 1055),
    ('die7', 1185, 1000, 1440, 1080, 1310),
]
MIO2 = 25 / 330
MIO2_ITEMS = [
    ('reach', 27, 56, 370, 416, 200), ('surprised', 373, 70, 716, 410, 545), ('hurt', 730, 66, 1116, 406, 920),
    ('worry', 1094, 62, 1410, 413, 1250), ('pray1', 29, 450, 365, 766, 197), ('pray2', 385, 450, 699, 766, 542),
    ('shiver', 740, 455, 1041, 779, 890), ('pray3', 1096, 451, 1405, 780, 1250),
    ('reach2', 250, 786, 708, 1068, 470), ('calm', 644, 787, 1192, 1072, 900),
]


def cut_alpha(sheet, items, scale, prefix):
    """Keep opaque bodies whose centre lies in the cell (+ soft halo); anchor = given body x."""
    out = {}
    for name, x0, y0, x1, y1, cxs in items:
        a = sheet[y0:y1, x0:x1].copy()
        lab, n = ndimage.label(ndimage.binary_dilation(a[:, :, 3] > 170, iterations=2))
        keep = [i + 1 for i, sl in enumerate(ndimage.find_objects(lab))
                if sl and (lab[sl] == i + 1).sum() > 60]
        halo = ndimage.binary_dilation(np.isin(lab, keep), iterations=7)
        a[:, :, 3] = np.where(halo, a[:, :, 3], 0)
        im = Image.fromarray(a, 'RGBA')
        bb = Image.fromarray((a[:, :, 3] > 24).astype(np.uint8) * 255).getbbox()
        out[f'{prefix}.{name}'] = finish(im.crop(bb), x0, bb[0], cxs, scale)
    return out


def frames(src_dir):
    ren = np.asarray(Image.open(src_dir / 'renSheet.png').convert('RGB'))
    mio = np.asarray(Image.open(src_dir / 'mioSheet.png').convert('RGB'))
    out = {}
    for kind, (scale, items) in REN.items():
        out.update(cut(ren, REN_BG, scale, items, 'ren.' + kind))
    out.update(cut(mio, MIO_BG, MIO[0], MIO[1], 'mio'))
    ren2 = np.asarray(Image.open(src_dir / 'renSheet2.png').convert('RGBA'))
    mio2 = np.asarray(Image.open(src_dir / 'mioSheet2.png').convert('RGBA'))
    out.update(cut_alpha(ren2, REN2_ITEMS, REN2, 'ren.x'))
    out.update(cut_alpha(mio2, MIO2_ITEMS, MIO2, 'mio.x'))
    return out

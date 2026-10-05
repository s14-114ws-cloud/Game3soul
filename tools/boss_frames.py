"""Battle frames for ST1 / ST4 / ST6 / ST9 / ST11 / EX bosses, cut from
assets/src/bossSheetA.png (grey background, every figure drawn facing RIGHT).

Each boss row uses ONE scale factor so the relative size of its frames is
kept (e.g. the collapsed K-04 or the ORIGIN form stay bigger than the base
form). Scales are chosen so the standing pose roughly matches the boss
hitbox height in the 384x216 game canvas.
"""
import numpy as np
from PIL import Image
from scipy import ndimage

# boss -> (scale, [(frame, x0, y0, x1, y1), ...])
BOSSES = {
    'nurse': (62 * 1.25 / 95, [
        ('idle1', 8, 34, 98, 131), ('walk1', 100, 34, 173, 131), ('walk2', 182, 34, 264, 131),
        ('walk3', 271, 34, 358, 131), ('idle2', 364, 34, 462, 131),
        ('atk1', 466, 34, 590, 131), ('atk2', 590, 34, 708, 131), ('dash', 711, 34, 868, 131),
        ('rage', 928, 34, 1024, 131), ('stagger', 1026, 34, 1106, 131), ('cast', 1110, 34, 1276, 131),
        ('spirit1', 1282, 34, 1500, 131), ('spirit2', 1500, 34, 1768, 131),
    ]),
    'armor': (64 * 1.25 / 110, [
        ('idle1', 8, 168, 100, 276), ('idle2', 100, 168, 200, 276), ('idle3', 200, 168, 296, 276),
        ('guard1', 298, 168, 408, 276), ('guard2', 410, 168, 508, 276),
        ('thrust', 512, 168, 642, 276), ('bash', 644, 160, 768, 276), ('spin', 768, 160, 902, 276),
        ('core1', 904, 160, 1002, 278), ('core2', 1002, 160, 1102, 278), ('coreThrust', 1104, 160, 1268, 278),
        ('coreLunge', 1266, 160, 1372, 278), ('coreBurst', 1374, 160, 1496, 282), ('coreNova', 1588, 158, 1764, 296),
    ]),
    'raven': (56 * 1.25 / 105, [
        ('idle1', 8, 314, 168, 420), ('idle2', 170, 314, 298, 420), ('sword', 298, 312, 418, 420),
        ('idle3', 418, 312, 540, 420), ('flap', 536, 304, 686, 420), ('flame', 766, 304, 906, 420),
        ('rear', 906, 300, 1068, 420),
        ('calm1', 1070, 300, 1244, 420), ('calm2', 1246, 300, 1404, 420), ('calm3', 1404, 300, 1576, 420),
        ('rest', 1576, 300, 1766, 420),
    ]),
    'boundary': (60 * 1.25 / 88, [
        ('b_idle1', 8, 484, 102, 570), ('b_idle2', 102, 478, 204, 570), ('b_atk1', 204, 484, 304, 570),
        ('b_idle3', 310, 484, 390, 570), ('b_atk2', 392, 478, 502, 570), ('b_atk3', 504, 484, 632, 570),
        ('b_crouch', 636, 484, 746, 570),
        ('s_idle1', 884, 484, 978, 572), ('s_idle2', 980, 476, 1062, 572), ('s_idle3', 1110, 474, 1202, 572),
        ('s_atk1', 1200, 470, 1298, 572), ('s_idle4', 1298, 474, 1398, 572), ('s_final', 1506, 468, 1766, 574),
    ]),
    'k04': (54 * 1.25 / 75, [
        ('a_idle1', 8, 628, 108, 695), ('a_idle2', 124, 618, 212, 695), ('a_idle3', 214, 618, 302, 695),
        ('a_idle4', 300, 618, 386, 695), ('a_lunge', 554, 612, 626, 695), ('a_slash', 624, 612, 790, 695),
        ('b_idle1', 812, 628, 942, 696), ('b_idle2', 944, 612, 1032, 696), ('b_rise', 1034, 612, 1196, 696),
        ('b_crawl', 1180, 640, 1262, 696), ('b_ring', 1252, 612, 1372, 696), ('b_roar', 1394, 612, 1566, 696),
        ('b_burst', 1566, 612, 1766, 696),
    ]),
    'zero': (64 * 1.25 / 105, [
        ('p1_idle1', 8, 760, 100, 878), ('p1_idle2', 100, 760, 166, 878), ('p1_halo', 166, 752, 216, 878),
        ('p1_idle3', 216, 760, 282, 878), ('p1_cast', 342, 760, 404, 878),
        ('p2_idle', 468, 760, 546, 878), ('p2_open', 546, 752, 722, 878), ('p2_idle2', 734, 752, 852, 878),
        ('p3_form', 902, 752, 1104, 878), ('p3_pillar', 1192, 752, 1272, 878),
        ('origin', 1490, 752, 1700, 878),
    ]),
}


RES = 2   # stored at 2x, drawn at half size on the 2x canvas


def key_out(rgb):
    a = rgb.astype(int)
    grey = (np.abs(a - 83).max(2) <= 14) & (np.ptp(a, axis=2) <= 8)
    # remove only grey regions connected to the crop edge (keeps grey inside the figures)
    lab, n = ndimage.label(grey)
    edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    sizes = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1)) if n else []
    # also enclosed background (inside crescents / tentacle loops); tiny grey specks inside figures stay
    enclosed = [i + 1 for i, s in enumerate(sizes) if s >= 24]
    fg = ~np.isin(lab, list(edge) + enclosed)
    # drop specks and neighbours' fragments touching the crop edge
    lab, n = ndimage.label(ndimage.binary_dilation(fg, iterations=1))
    if n:
        sizes = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))
        big = sizes.max()
        border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
        keep = [i + 1 for i, s in enumerate(sizes)
                if s >= max(30, big * .015) and not (i + 1 in border and s < big * .12)]
        fg &= np.isin(lab, keep)
    # glows were painted semi-transparently over the grey: recover their alpha from the distance
    # to the background grey and un-mix the grey out of the colour
    dev = np.abs(a - 83).max(2).astype(np.float32)
    al = np.clip(dev / 48, 0, 1) * fg
    col = np.clip(83 + (a - 83) / np.maximum(al[:, :, None], 1e-3), 0, 255)
    col = np.where(al[:, :, None] > 0, col, 0).astype(np.uint8)
    return Image.fromarray(np.dstack([col, (al * 255).astype(np.uint8)]), 'RGBA')


def shrink(im, scale):
    w, h = max(1, round(im.width * scale)), max(1, round(im.height * scale))
    arr = np.asarray(im).astype(np.float32)
    arr[:, :, :3] *= arr[:, :, 3:4] / 255
    small = np.stack([np.asarray(Image.fromarray(arr[:, :, c].astype(np.uint8)).resize((w, h), Image.LANCZOS)).astype(np.float32)
                      for c in range(4)], 2)
    al = small[:, :, 3]
    rgb = np.where(al[:, :, None] > 0, small[:, :, :3] * 255 / np.maximum(al[:, :, None], 1), 0)
    return Image.fromarray(np.dstack([np.clip(rgb, 0, 255), np.where(al > 110, 255, 0)]).astype(np.uint8), 'RGBA')


def frames(src_path):
    sheet = np.asarray(Image.open(src_path).convert('RGB'))
    out = {}
    for boss, (scale, items) in BOSSES.items():
        for name, x0, y0, x1, y1 in items:
            im = key_out(sheet[y0:y1, x0:x1])
            im = im.crop(im.getbbox())
            out[f'{boss}.{name}'] = shrink(im, scale * RES)
    return out

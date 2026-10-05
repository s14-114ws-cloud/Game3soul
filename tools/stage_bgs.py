"""Stage backgrounds and title logo.

Background sheets (1448x1086) hold four horizontal strips each:
  bgSheet1: ST1 hospital, ST2 rainy street, ST3 school, ST4 weapons facility
  bgSheet5: ST5 husk factory, ST6 eclipse cemetery, ST7 ghost subway, ST8 soul-core tower
  bgSheet9: ST9 boundary lab, ST10 M-10 memory, ST11 boundary keep, ST12 cathedral
  bgEX:     EX zero room (single framed picture; a wide band is cropped from it)
Every strip is scaled to the 216px game canvas height.
"""
import numpy as np
from PIL import Image, ImageFilter

GAME_H = 216
STRIPS = {
    'bgSheet1': [(8, 1440, 6, 248), (8, 1440, 262, 530), (8, 1440, 540, 778), (8, 1440, 789, 1078)],
    'bgSheet5': [(4, 1444, 2, 250), (4, 1444, 263, 538), (4, 1444, 551, 792), (4, 1444, 803, 1084)],
    'bgSheet9': [(2, 1446, 2, 266), (2, 1446, 274, 537), (2, 1446, 546, 810), (2, 1446, 816, 1084)],
}
ORDER = [('bgSheet1', 0), ('bgSheet1', 1), ('bgSheet1', 2), ('bgSheet1', 3),
         ('bgSheet5', 0), ('bgSheet5', 1), ('bgSheet5', 2), ('bgSheet5', 3),
         ('bgSheet9', 0), ('bgSheet9', 1), ('bgSheet9', 2), ('bgSheet9', 3)]


def stage_backgrounds(src):
    out = {}
    for i, (sheet, k) in enumerate(ORDER):
        x0, x1, y0, y1 = STRIPS[sheet][k]
        im = Image.open(src / f'{sheet}.png').convert('RGB').crop((x0, y0, x1, y1))
        out[i + 1] = im.resize((round(im.width * GAME_H / im.height), GAME_H), Image.LANCZOS)
    ex = Image.open(src / 'bgEX.png').convert('RGB').crop((22, 380, 1426, 1050))
    out[13] = ex.resize((round(ex.width * GAME_H / ex.height), GAME_H), Image.LANCZOS)
    return out


def title_logo(src, width=1100):
    """Lift the lettering, chain and gold frame off the logo picture's background."""
    im = Image.open(src / 'titleLogo.png').convert('RGB').crop((80, 270, 1650, 790))
    a = np.asarray(im).astype(np.float32)
    lum = a.max(2)
    sat = a.max(2) - a.min(2)
    gold = (a[:, :, 0] > 150) & (a[:, :, 1] > 110) & (a[:, :, 2] < a[:, :, 0] * .8)
    alpha = np.clip((lum - 92) / 70, 0, 1)
    alpha = np.maximum(alpha, gold.astype(np.float32))
    # soften: keep a little dark outline around bright strokes
    al = Image.fromarray((alpha * 255).astype(np.uint8))
    halo = np.asarray(al.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(2))).astype(np.float32) / 255
    alpha = np.maximum(alpha, halo * .72)
    # fade the outer edge so no rectangular crop shows
    h, w = alpha.shape
    yy, xx = np.mgrid[0:h, 0:w]
    edge = np.minimum.reduce([xx / 40, (w - 1 - xx) / 40, yy / 30, (h - 1 - yy) / 30, np.ones_like(alpha)])
    alpha = alpha * np.clip(edge, 0, 1)
    out = Image.fromarray(np.dstack([a, alpha * 255]).astype(np.uint8), 'RGBA')
    return out.resize((width, round(out.height * width / out.width)), Image.LANCZOS)

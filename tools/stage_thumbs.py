"""Stage-select thumbnails (16:9 crops, caption bands left out).

thumbSheetA/B/C are 2x2 grids of framed cards (ST1-4, ST5-8, ST9-12);
each crop takes the top 16:9 band inside a card's frame. ST2 uses its own
picture (thumbST2, the lantern boss) and EX a band from its framed card.
"""
from PIL import Image

TW, TH = 480, 270
CELLS = [(16, 16, 712), (744, 16, 1432), (16, 556, 712), (744, 556, 1432)]  # x0, y0, x1
SHEETS = ['thumbSheetA', 'thumbSheetB', 'thumbSheetC']


def fit(im):
    w, h = im.size
    if w * 9 > h * 16:
        nw = h * 16 // 9
        im = im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
    else:
        im = im.crop((0, 0, w, w * 9 // 16))
    return im.resize((TW, TH), Image.LANCZOS)


def thumbs(src):
    out = {}
    for s, sheet in enumerate(SHEETS):
        im = Image.open(src / f'{sheet}.png').convert('RGB')
        for c, (x0, y0, x1) in enumerate(CELLS):
            out[s * 4 + c + 1] = fit(im.crop((x0, y0, x1, y0 + (x1 - x0) * 9 // 16)))
    out[2] = fit(Image.open(src / 'thumbST2.png').convert('RGB'))
    out[13] = fit(Image.open(src / 'thumbEX.png').convert('RGB').crop((60, 100, 1390, 848)))
    return out

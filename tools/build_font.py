"""Re-subset DotGothic16 to exactly the characters the game uses and embed it (woff2, base64).

    python3 tools/build_font.py soul_tether.html

Run after any text change so new kanji never fall back to a system font.
Font: assets/src/fonts/DotGothic16-Regular.ttf (SIL OFL 1.1, see OFL.txt).
"""
import base64, io, re, sys
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools import subset

ROOT = Path(__file__).resolve().parent.parent
FONT = ROOT / 'assets' / 'src' / 'fonts' / 'DotGothic16-Regular.ttf'


def main():
    target = Path(sys.argv[1])
    s = target.read_text(encoding='utf-8')
    text = re.sub(r'data:[a-z/+\-0-9]+;base64,[A-Za-z0-9+/=]+', '', s)
    chars = {c for c in text if ord(c) >= 32}
    chars |= {chr(c) for c in range(0x20, 0x7f)} | {chr(c) for c in range(0x3041, 0x3097)} | {chr(c) for c in range(0x30a1, 0x30fb)}
    f = TTFont(FONT)
    cmap = f.getBestCmap()
    missing = sorted(c for c in chars if ord(c) not in cmap and ord(c) > 0x3000)
    opt = subset.Options()
    opt.flavor = 'woff2'
    opt.layout_features = ['*']
    sub = subset.Subsetter(opt)
    sub.populate(unicodes=[ord(c) for c in chars])
    sub.subset(f)
    f.flavor = 'woff2'
    buf = io.BytesIO()
    f.save(buf)
    b64 = base64.b64encode(buf.getvalue()).decode()
    s2, n = re.subn(r"(font-family:'DotGothic16';src:url\(data:font/woff2;base64,)[A-Za-z0-9+/=]+", lambda m: m.group(1) + b64, s)
    assert n == 1, 'font-face not found'
    target.write_text(s2, encoding='utf-8')
    print(f'font {len(buf.getvalue()) // 1024} KB; glyphs not in DotGothic16: {"".join(missing) or "none"}')


if __name__ == '__main__':
    main()

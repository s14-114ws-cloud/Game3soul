"""Embed BGM/SE into the HTML as `const AUDIO_DATA={...};` (idempotent, one line).

Music: only tracks referenced by MUSIC_FILE (see audio_sources.py), re-encoded to MP3 64 kbps joint stereo with ffmpeg (MP3 decodes in every browser; AAC is missing from some Chromium builds) to keep the single
HTML under the 64 MB budget. SE: assets/src/audio/se/*.mp3 embedded as is (short, mono).
Source pack: README_audio_pack.txt (original synthesized music rendered from MIDI + synthesized SE).
"""
import base64, json, subprocess, sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

ROOT = Path(__file__).resolve().parent.parent
# superseded by the Suno ending songs (kept in the repo, not embedded, to stay under 64 MB)
EXCLUDE = {'bgm_ending', 'bgm_true_end', 'bgm_credits'}
SRC = ROOT / 'assets' / 'src' / 'audio'


def main():
    target = Path(sys.argv[1])
    data, total = {}, 0
    from audio_sources import used_music, encode
    html = target.read_text(encoding='utf-8')
    with tempfile.TemporaryDirectory() as td:
        for name in used_music(html):
            b = encode(name, Path(td) / (name + '.mp3'), '64k').read_bytes()
            data[name] = 'data:audio/mpeg;base64,' + base64.b64encode(b).decode()
            total += len(b)
    for f in sorted((SRC / 'se').glob('*.mp3')):
        b = f.read_bytes()
        data[f.stem] = 'data:audio/mpeg;base64,' + base64.b64encode(b).decode()
        total += len(b)
    js = 'const AUDIO_DATA=' + json.dumps(data, separators=(',', ':')) + ';'
    lines = target.read_text(encoding='utf-8').split('\n')
    hit = [i for i, l in enumerate(lines) if l.startswith('const AUDIO_DATA=')]
    if hit:
        lines[hit[0]] = js
    else:
        i = [i for i, l in enumerate(lines) if l.startswith('const UI_SPRITES=')][0]
        lines.insert(i + 1, js)
    target.write_text('\n'.join(lines), encoding='utf-8')
    print(f'{len(data)} audio files, {total // 1024} KB')


if __name__ == '__main__':
    main()

"""Shared audio source lookup for build_audio.py (single file) and build_web.py (web).

Only music referenced by MUSIC_FILE in the game is shipped. Sources, first match wins:
  assets/src/audio/suno/<name>.mp3   Suno tracks; trimmed to the loop window in suno/loops.json
                                     (drops the fade-out tail so the loop restarts cleanly)
  assets/src/audio/songs/<name>.m4a  Suno ending songs (play once)
  assets/src/audio/bgm/<name>.mp3    older synthesized pack (still used where nothing replaced it)
"""
import json, re, subprocess
from pathlib import Path

AUD = Path(__file__).resolve().parent.parent / 'assets' / 'src' / 'audio'
LOOPS = json.loads((AUD / 'suno' / 'loops.json').read_text()) if (AUD / 'suno' / 'loops.json').exists() else {}


def used_music(html):
    m = re.search(r'const MUSIC_FILE=\{(.*?)\};', html, re.S)
    return sorted(set(re.findall(r":'([a-zA-Z0-9_]+)'", m.group(1))))


def source(name):
    for p in (AUD / 'suno' / f'{name}.mp3', AUD / 'songs' / f'{name}.m4a', AUD / 'bgm' / f'{name}.mp3'):
        if p.exists():
            return p
    raise FileNotFoundError(name)


def encode(name, out, bitrate):
    """Write `name` as MP3 at `bitrate` to `out`, trimmed/faded to its loop window when it has one."""
    src = source(name)
    cmd = ['ffmpeg', '-loglevel', 'error', '-y', '-i', str(src)]
    lp = LOOPS.get(name)
    if lp:
        st, en = lp['start'], lp['end']
        fade = min(1.2, max(.3, (en - st) * .01))
        cmd += ['-ss', str(st), '-t', str(en - st), '-af', f'afade=t=in:d=0.04,afade=t=out:st={en - st - fade:.2f}:d={fade:.2f}']
    cmd += ['-c:a', 'libmp3lame', '-b:a', bitrate, str(out)]
    subprocess.run(cmd, check=True)
    return out


def se_files():
    return sorted((AUD / 'se').glob('*.mp3'))

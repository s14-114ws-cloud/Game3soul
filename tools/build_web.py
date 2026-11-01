"""Web (PWA) build: split the single-file game into cacheable files under dist/.

    python3 tools/build_web.py [soul_tether.html]

- Every inline data: URI (images, stills, sheets) is written out as dist/a/<hash>.<ext> with the
  exact same bytes (no re-encoding) and the HTML points at it. Content-hashed names never change for
  unchanged art, so browsers / the service worker / Git keep them forever.
- Music and SE use the ORIGINAL files from assets/src/audio (128 kbps MP3, Suno AAC + MP3 fallback),
  not the 64 kbps copies the single-file build needs to stay under its size budget.
- A service worker (sw.js) serves everything cache-first and quietly downloads the rest of the game in
  the background after the first launch, so later launches start instantly and work offline.
- manifest.webmanifest + icons: "Add to Home Screen" on iPhone launches full screen (no Safari bars).
- _headers works on both Netlify and Cloudflare Pages (long cache for /a/*, no-cache for the shell).
"""
import base64, hashlib, json, re, shutil, subprocess, sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / 'dist'
AUD = ROOT / 'assets' / 'src' / 'audio'
EXT = {'image/webp': 'webp', 'image/png': 'png', 'image/jpeg': 'jpg', 'audio/mpeg': 'mp3', 'audio/mp4': 'm4a'}
SKIP_EMBED = {'bgm_ending', 'bgm_true_end', 'bgm_credits'}   # superseded by the Suno songs


def put(data, ext, assets):
    h = hashlib.sha1(data).hexdigest()[:12]
    rel = f'a/{h}.{ext}'
    if rel not in assets:
        (DIST / rel).write_bytes(data)
        assets[rel] = len(data)
    return rel


def main():
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'soul_tether.html'
    html = src.read_text(encoding='utf-8')
    if DIST.exists():
        shutil.rmtree(DIST)
    (DIST / 'a').mkdir(parents=True)
    assets = {}

    # 1. audio: original files instead of the embedded 64 kbps copies
    audio = {}
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from audio_sources import used_music, encode, source, se_files
    for name in used_music(html):
        src = source(name)
        if src.suffix == '.m4a':   # ending songs: original AAC first, MP3 fallback
            mp3 = encode(name, DIST / 'tmp.mp3', '192k')
            audio[name] = [put(src.read_bytes(), 'm4a', assets), put(mp3.read_bytes(), 'mp3', assets)]
        elif src.parent.name == 'suno':
            audio[name] = put(encode(name, DIST / 'tmp.mp3', '192k').read_bytes(), 'mp3', assets)
        else:
            audio[name] = put(src.read_bytes(), 'mp3', assets)
    (DIST / 'tmp.mp3').unlink(missing_ok=True)
    for f in se_files():
        audio[f.stem] = put(f.read_bytes(), 'mp3', assets)
    lines = html.split('\n')
    i = [k for k, l in enumerate(lines) if l.startswith('const AUDIO_DATA=')][0]
    lines[i] = 'const AUDIO_DATA=' + json.dumps(audio, separators=(',', ':')) + ';'
    html = '\n'.join(lines)

    # 2. every other data: URI (except the small embedded font) -> file
    pat = re.compile(r'data:(image/webp|image/png|image/jpeg|audio/mpeg|audio/mp4);base64,([A-Za-z0-9+/=]+)')
    html = pat.sub(lambda m: put(base64.b64decode(m.group(2)), EXT[m.group(1)], assets), html)

    # 3. icons from the key visual
    kv = Image.open(ROOT / 'assets' / 'src' / 'keyVisual.png').convert('RGB')
    w, h = kv.size
    side = min(w, h)
    sq = kv.crop(((w - side) // 2 - int(w * .12), 0, (w - side) // 2 - int(w * .12) + side, side))
    for n in (180, 192, 512):
        sq.resize((n, n), Image.LANCZOS).save(DIST / f'icon-{n}.png')
    (DIST / 'manifest.webmanifest').write_text(json.dumps({
        'name': 'SOUL TETHER', 'short_name': 'SOUL TETHER', 'start_url': './', 'scope': './',
        'display': 'fullscreen', 'orientation': 'landscape', 'background_color': '#04060d', 'theme_color': '#04060d',
        'icons': [{'src': 'icon-192.png', 'sizes': '192x192', 'type': 'image/png'},
                  {'src': 'icon-512.png', 'sizes': '512x512', 'type': 'image/png', 'purpose': 'any maskable'}]},
        ensure_ascii=False, indent=1), encoding='utf-8')

    # 4. head tags + service worker registration
    head = ('<link rel="manifest" href="manifest.webmanifest"><link rel="apple-touch-icon" href="icon-180.png">'
            '<meta name="apple-mobile-web-app-capable" content="yes"><meta name="mobile-web-app-capable" content="yes">'
            '<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">'
            '<meta name="apple-mobile-web-app-title" content="SOUL TETHER"><meta name="theme-color" content="#04060d">'
            "<script>if('serviceWorker' in navigator&&location.protocol==='https:'){navigator.serviceWorker.register('sw.js').then(r=>{"
            "const warm=()=>{const w=r.active||navigator.serviceWorker.controller;w&&w.postMessage('warm')};"
            "addEventListener('load',()=>setTimeout(warm,4000))}).catch(()=>{});"
            "navigator.serviceWorker.addEventListener('message',e=>{const m=e.data||{};let el=document.getElementById('offlineTag');"
            "if(!el){el=document.createElement('div');el.id='offlineTag';el.style.cssText='position:fixed;left:50%;top:8px;transform:translateX(-50%);z-index:96;padding:3px 12px;border-radius:12px;background:rgba(6,8,16,.78);border:1px solid rgba(230,180,95,.45);color:#ffe6bd;font:11px DotGothic16,sans-serif;pointer-events:none;transition:opacity .6s';document.body.appendChild(el)}"
            "if(m.t==='prog'){el.textContent='オフライン用に保存中… '+m.p+'%';el.style.opacity=document.getElementById('menu')&&getComputedStyle(document.getElementById('menu')).display!=='none'?1:0}"
            "else if(m.t==='ready'&&m.fresh){el.textContent='保存完了：次からはオフラインでも遊べます';el.style.opacity=1;setTimeout(()=>el.style.opacity=0,4000)}})}</script>")
    k = html.index('</head>')
    html = html[:k] + head + html[k:]
    (DIST / 'index.html').write_text(html, encoding='utf-8')

    # 5. service worker
    ver = hashlib.sha1(html.encode()).hexdigest()[:10]
    sw = """const V='st-%s',SHELL=['./','index.html','manifest.webmanifest','icon-192.png','icon-180.png'],ASSETS=%s;
self.addEventListener('install',e=>{e.waitUntil(caches.open(V).then(c=>c.addAll(SHELL)).then(()=>self.skipWaiting()))});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==V&&k!=='st-assets').map(k=>caches.delete(k)))).then(()=>self.clients.claim()))});
// /a/* files are content-hashed: cache-first forever. The shell (index.html) is network-first so updates arrive.
self.addEventListener('fetch',e=>{const u=new URL(e.request.url);if(e.request.method!=='GET'||u.origin!==location.origin)return;
 if(u.pathname.includes('/a/')){e.respondWith(caches.open('st-assets').then(c=>c.match(e.request).then(r=>r||fetch(e.request).then(n=>{if(n.ok)c.put(e.request,n.clone());return n}))));return}
 e.respondWith(fetch(e.request).then(n=>{if(n.ok)caches.open(V).then(c=>c.put(e.request,n.clone()));return n}).catch(()=>caches.match(e.request).then(r=>r||caches.match('index.html'))))});
// after the first launch, fetch the rest of the game quietly so later launches are instant and offline-ready
self.addEventListener('message',e=>{if(e.data!=='warm')return;e.waitUntil(caches.open('st-assets').then(async c=>{const have=new Set((await c.keys()).map(r=>new URL(r.url).pathname.split('/').pop()));
 const keep=new Set(ASSETS.map(a=>a.split('/').pop()));for(const r of await c.keys())if(!keep.has(new URL(r.url).pathname.split('/').pop()))await c.delete(r);
 const say=async m=>{for(const cl of await self.clients.matchAll())cl.postMessage(m)};let done=0,miss=ASSETS.filter(a=>!have.has(a.split('/').pop()));
 if(!miss.length){await say({t:'ready',fresh:false});return}
 for(const a of miss){try{const n=await fetch(a);if(n.ok)await c.put(a,n)}catch(_){}if(++done%%20===0)await say({t:'prog',p:Math.round(done*100/miss.length)})}await say({t:'ready',fresh:true})}))});
""" % (ver, json.dumps(sorted(assets)))
    (DIST / 'sw.js').write_text(sw, encoding='utf-8')

    # 6. cache headers (Netlify / Cloudflare Pages)
    (DIST / '_headers').write_text("/a/*\n  Cache-Control: public, max-age=31536000, immutable\n"
                                   "/index.html\n  Cache-Control: no-cache\n/\n  Cache-Control: no-cache\n"
                                   "/sw.js\n  Cache-Control: no-cache\n", encoding='utf-8')
    tot = sum(assets.values())
    print(f'dist/index.html {len(html.encode()) // 1024} KB, {len(assets)} asset files {tot // 1048576} MB, version {ver}')


if __name__ == '__main__':
    main()

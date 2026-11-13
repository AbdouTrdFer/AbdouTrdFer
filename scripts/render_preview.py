"""Render original SVG motion to GIF and a local README preview.

Optional authoring dependencies: pip install pillow playwright markdown
Then: python -m playwright install chromium
These are NOT required by the daily GitHub Action.
"""
import argparse
import io
from pathlib import Path
import re
from PIL import Image
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]

def make_gif(page, name, width, height, duration, frames):
    source=(ROOT/f'assets/{name}.svg').read_text(encoding='utf-8')
    page.set_viewport_size({'width':width,'height':height})
    page.set_content('<html><body style="margin:0;background:#0b1514">'+source+'</body></html>')
    page.evaluate('document.getAnimations().forEach(a=>a.pause())')
    rendered=[]
    for frame in range(frames):
        page.evaluate('(time)=>document.getAnimations().forEach(a=>a.currentTime=time)',frame*duration/frames)
        rendered.append(Image.open(io.BytesIO(page.screenshot())).convert('RGB'))
    # One palette for every frame prevents color flicker around static text.
    palette=rendered[0].quantize(colors=128)
    rendered=[im.quantize(palette=palette,dither=Image.Dither.NONE) for im in rendered]
    rendered[0].save(ROOT/f'assets/{name}.gif',save_all=True,append_images=rendered[1:],duration=round(duration/frames/10)*10,loop=0,optimize=True,disposal=1)
    print(f'{name}.gif: {frames} frames, {(ROOT/f"assets/{name}.gif").stat().st_size//1024} KB')

def preview_html():
    import markdown
    source=(ROOT/'README.md').read_text(encoding='utf-8')
    body=markdown.markdown(source,extensions=['tables','md_in_html'])
    css='''*{box-sizing:border-box}body{margin:0;background:#0d1117;color:#e6edf3;font:15px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif}main{max-width:1040px;margin:38px auto;padding:32px;border:1px solid #30363d;border-radius:8px}img{max-width:100%;height:auto;vertical-align:middle}p{margin:16px 0}h3{font-size:20px;margin:34px 0 18px;padding-bottom:12px;border-bottom:1px solid #30363d}a{color:#8bd8bf;text-decoration:none}code{background:#202b29;padding:3px 6px;border-radius:5px;font-size:12px}table{width:100%;border-collapse:collapse;margin:16px 0}td,th{border:1px solid #30363d;padding:16px;text-align:left}th{background:#151e1c}summary{cursor:pointer;color:#a3b8ac}details{font-size:13px}.preview-note{font-size:12px;color:#8b949e;margin:0 0 18px}.light{background:#fff;color:#1f2328}.light main,.light td,.light th,.light h3{border-color:#d0d7de}.light a{color:#09654e}.light code,.light th{background:#eff5f0}@media(max-width:600px){main{margin:0;padding:16px;border:0}td,th{padding:9px;font-size:12px}h3{font-size:18px}p[align=center] a img[height]{max-width:30%;height:auto}}'''
    html='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Abdelali Ferhan · GitHub profile preview</title><style>'+css+'</style><body><main><p class="preview-note">LOCAL README PREVIEW · GitHub controls final fonts and spacing</p>'+body+'</main></body></html>'
    (ROOT/'preview.html').write_text(html,encoding='utf-8')

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--skip-gifs',action='store_true')
    args=parser.parse_args()
    preview_html()
    out=ROOT/'.preview'
    out.mkdir(exist_ok=True)
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        page=browser.new_page(device_scale_factor=1)
        if not args.skip_gifs:
            make_gif(page,'hero',1000,430,24000,192)
            make_gif(page,'process',1000,152,8000,64)
        # Keep validation local; don't artificially increment the public view counter.
        def cached_badge(route):
            name='views.svg' if 'komarev.com' in route.request.url else 'followers.svg'
            cached=out/name
            if cached.exists():
                route.fulfill(path=str(cached),content_type='image/svg+xml')
            else:
                route.abort()
        page.route(re.compile(r'^https?://'),cached_badge)
        page.set_viewport_size({'width':1120,'height':900})
        page.goto((ROOT/'preview.html').as_uri())
        page.wait_for_timeout(500)
        page.screenshot(path=str(out/'desktop.png'),full_page=True)
        page.evaluate("document.body.classList.add('light')")
        page.screenshot(path=str(out/'light.png'),full_page=True)
        page.evaluate("document.body.classList.remove('light')")
        page.set_viewport_size({'width':390,'height':844})
        page.screenshot(path=str(out/'mobile.png'),full_page=True)
        overflow=page.evaluate('document.documentElement.scrollWidth > window.innerWidth')
        print('Mobile horizontal overflow:',overflow)
        if overflow:
            raise RuntimeError('Mobile preview overflows the viewport')
        missing=page.evaluate("Array.from(document.images).filter(i=>!i.src.startsWith('http') && (!i.complete || i.naturalWidth===0)).map(i=>i.src)")
        print('Missing local images:',missing)
        if missing:
            raise RuntimeError('Missing local images')
        page.emulate_media(reduced_motion='reduce')
        page.wait_for_function("Array.from(document.querySelectorAll('picture img')).every(i=>i.complete && i.naturalWidth>0)")
        selected=page.locator('picture img[src$=".gif"]').evaluate_all('(imgs)=>imgs.map(i=>i.currentSrc)')
        assert all('static.svg' in src for src in selected),selected
        print('Reduced-motion images verified.')
        browser.close()

if __name__=='__main__':
    main()

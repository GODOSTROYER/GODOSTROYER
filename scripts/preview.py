"""Build an honest local preview of the actual README, then optionally serve it."""
from __future__ import annotations
import argparse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]

BODY_CSS = """
:root{color-scheme:dark;--bg:#0d1117;--fg:#f0f6fc;--muted:#9198a1;--line:#3d444d;--link:#92bdff;--code:#656c7633}
:root[data-theme=light]{color-scheme:light;--bg:#fff;--fg:#1f2328;--muted:#59636e;--line:#d1d9e0;--link:#0969da;--code:#818b981f}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
::selection{background:#729c37;color:#fff}a{color:var(--link);text-decoration:none;text-underline-offset:.2em}a:hover{text-decoration:underline}a:focus-visible,summary:focus-visible{outline:2px solid var(--link);outline-offset:5px}
article{max-width:1012px;margin:0 auto;padding:32px 40px}img{max-width:100%;height:auto;vertical-align:middle;border-radius:5px}picture{display:block}h2{font-size:24px;line-height:1.25;margin:32px 0 18px;padding-bottom:10px;border-bottom:1px solid var(--line)}h3{font-size:20px;margin:26px 0 16px;line-height:1.4}p{margin:0 0 16px}picture+p{margin-top:24px}code{font:85%/1.7 ui-monospace,SFMono-Regular,Consolas,monospace;padding:.2em .4em;border-radius:6px;background:var(--code)}ul{padding-left:2em;margin:0 0 16px}li+li{margin-top:6px}sub{font-size:12px;color:var(--muted);vertical-align:baseline}hr{height:1px;padding:0;margin:24px 0;border:0;background:var(--line)}details{margin-top:24px}summary{cursor:pointer;color:var(--fg)}details[open] summary{margin-bottom:12px}
@media(max-width:600px){body{font-size:15px}article{padding:20px 16px}h2{font-size:23px}h3{font-size:18px}code{display:inline-block;margin-bottom:3px}p{line-height:1.65}}@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
"""

SHELL = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Arnav Bule &middot; GitHub profile preview</title>
<style>
:root{color-scheme:dark;--bg:#10191b;--panel:#162225;--fg:#edf2e8;--muted:#a6b5ad;--accent:#bce16b;--line:#34423f}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:14px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}::selection{background:var(--accent);color:var(--bg)}header{max-width:1080px;margin:0 auto;padding:24px 24px 18px;display:flex;gap:20px;align-items:center;justify-content:space-between}h1{font-size:18px;margin:0;letter-spacing:-.02em}header p{margin:3px 0 0;color:var(--muted);font-size:12px}nav{display:flex;flex-wrap:wrap;gap:8px;align-items:center}.group{display:flex;gap:2px;background:var(--panel);padding:3px;border-radius:8px}button,a.download{font:inherit;border:0;padding:7px 11px;border-radius:5px;color:var(--muted);background:transparent;cursor:pointer;text-decoration:none}button[aria-pressed=true]{background:var(--accent);color:var(--bg)}button:hover,a.download:hover{color:var(--fg);background:#31443a}button[aria-pressed=true]:hover{background:#c9ed82;color:var(--bg)}button:focus-visible,a:focus-visible{outline:2px solid var(--accent);outline-offset:3px}main{max-width:1040px;margin:0 auto 40px;padding:0 16px}.frame{width:100%;margin:auto;border:1px solid var(--line);border-radius:12px;overflow:hidden;background:#0d1117}.frame.mobile{max-width:390px}iframe{display:block;width:100%;height:2600px;border:0}footer{max-width:1040px;margin:auto;padding:0 24px 30px;color:var(--muted);font-size:12px}@media(max-width:700px){header{align-items:flex-start;flex-direction:column;padding:18px 16px}nav{gap:4px}main{padding:0 8px}button,a.download{padding:7px 9px}h1{font-size:17px}}@media(prefers-reduced-motion:reduce){.frame{transition:none}}
</style></head><body>
<header><div><h1>Arnav Bule / README.md</h1><p>Local preview &middot; the actual README, with GitHub-style typography</p></div><nav aria-label="Preview controls"><div class="group" role="group" aria-label="Width"><button data-width="desktop" aria-pressed="true">Desktop</button><button data-width="mobile" aria-pressed="false">Mobile</button></div><div class="group" role="group" aria-label="Theme"><button data-theme="dark" aria-pressed="true">Dark</button><button data-theme="light" aria-pressed="false">Light</button></div><a class="download" href="../README.md" download>Download README &darr;</a></nav></header>
<main><div class="frame"><iframe title="GitHub profile README" src="readme.html?theme=dark"></iframe></div></main><footer>The artwork and content are ready for GitHub. This local preview does not change your public profile.</footer>
<script>
const frame=document.querySelector('iframe'),wrap=document.querySelector('.frame');let theme='dark';
function fit(){if(frame.contentDocument)frame.style.height=(frame.contentDocument.documentElement.scrollHeight+2)+'px'}
frame.addEventListener('load',()=>{fit();new ResizeObserver(fit).observe(frame.contentDocument.body)});
document.querySelectorAll('[data-width]').forEach(b=>b.addEventListener('click',()=>{wrap.classList.toggle('mobile',b.dataset.width==='mobile');document.querySelectorAll('[data-width]').forEach(x=>x.setAttribute('aria-pressed',String(x===b)));setTimeout(fit,300)}));
document.querySelectorAll('button[data-theme]').forEach(b=>b.addEventListener('click',()=>{theme=b.dataset.theme;frame.src='readme.html?theme='+theme;document.querySelectorAll('button[data-theme]').forEach(x=>x.setAttribute('aria-pressed',String(x===b)))}));
</script></body></html>"""


def build():
    readme = (ROOT/'README.md').read_text(encoding='utf-8')
    readme = readme.replace('src="assets/', 'src="../assets/').replace('srcset="assets/', 'srcset="../assets/')
    readme = readme.replace('<h2>Selected work</h2>', '<h2 id="selected-work">Selected work</h2>')
    theme_script = """const t=new URLSearchParams(location.search).get('theme')==='light'?'light':'dark';document.documentElement.dataset.theme=t;document.querySelectorAll('source').forEach(s=>{if(s.media.includes('prefers-color-scheme: dark'))s.media=t==='dark'?s.media.replace('(prefers-color-scheme: dark)','(min-width: 0px)'):'not all'});document.querySelectorAll('a[href^="https:"]').forEach(a=>{a.target='_blank';a.rel='noopener noreferrer'});"""
    page = '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Arnav Bule &mdash; README</title><style>'+BODY_CSS+'</style></head><body><article>'+readme+'</article><script>'+theme_script+'</script></body></html>'
    preview = ROOT/'preview'
    preview.mkdir(exist_ok=True)
    (preview/'index.html').write_text(SHELL,encoding='utf-8')
    (preview/'readme.html').write_text(page,encoding='utf-8')
    print('Built preview/index.html from README.md.')


class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,directory=str(ROOT),**kwargs)

    def do_GET(self):
        path = unquote(urlsplit(self.path).path)
        if any(part.startswith('.') or part == '..' for part in Path(path).parts):
            self.send_error(403)
            return
        super().do_GET()

    def list_directory(self,path):
        self.send_error(403)
        return None


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--serve',action='store_true')
    parser.add_argument('--port',type=int,default=8765)
    args=parser.parse_args()
    build()
    if args.serve:
        print(f'Preview: http://127.0.0.1:{args.port}/preview/',flush=True)
        ThreadingHTTPServer(('127.0.0.1',args.port),Handler).serve_forever()

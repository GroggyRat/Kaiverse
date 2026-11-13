#!/usr/bin/env python3
"""Builds the static site. Run: python3 build.py
src/kaitech.html      -> index.html   (the one-screen site)
src/pages/<name>.html -> <name>.html  (About, Privacy, Terms)"""
import re, pathlib
root = pathlib.Path(__file__).parent
FONTS = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter+Tight:wght@400;500&family=JetBrains+Mono:wght@400;500&family=Michroma&display=swap">'
HEAD = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="description" content="{desc}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta name="theme-color" content="#030712">
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
'''
src = (root / 'src/kaitech.html').read_text()
(root / 'index.html').write_text(
    HEAD.format(title='KaiTech', desc='Software that keeps Fiji business moving. KaiWorkforce, BillZilla, KaiInspect and Drivo.')
    + '<style>body{margin:0}[hidden]{display:none!important}</style>\n</head>\n<body>\n' + src + '</body>\n</html>\n')

PAGE_CSS = '''<style>
:root{--bg0:#030712;--bg1:#14295A;--fg:#F5F6F9;--dim:#A3ACC0;--line:#243049;--accent:#4C8DF5;color-scheme:dark;
  --display:'Michroma','Eurostile','Arial Black',sans-serif;--text:'Inter Tight',system-ui,-apple-system,'Segoe UI',sans-serif;--mono:'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace}
*{box-sizing:border-box}
body{margin:0;background:var(--bg0) radial-gradient(90% 60% at 80% 0%,var(--bg1) 0%,var(--bg0) 70%) no-repeat;color:var(--fg);font:17px/1.6 var(--text);-webkit-font-smoothing:antialiased;min-height:100vh}
.w{max-width:44rem;margin:0 auto;padding-block:22px 80px;padding-left:max(22px,env(safe-area-inset-left,0px));padding-right:max(22px,env(safe-area-inset-right,0px))}
a{color:inherit;text-underline-offset:3px}
a:focus-visible{outline:1px solid var(--fg);outline-offset:4px}
header{display:flex;justify-content:space-between;align-items:center;gap:16px;margin-bottom:clamp(48px,10vh,110px)}
.mark{display:flex;align-items:center;gap:12px;font:400 14px/1 var(--display);letter-spacing:.42em;text-decoration:none}
.mark svg{width:26px;height:26px}
.back,.tag,footer{font:400 11px/1.4 var(--mono);text-transform:uppercase;letter-spacing:.14em;color:var(--dim)}
.tag{margin:0 0 18px}
h1{margin:0 0 24px;font:400 clamp(28px,5vw,48px)/1.12 var(--display);letter-spacing:.01em;text-transform:uppercase;text-wrap:balance}
h2{margin:44px 0 10px;font:400 12px/1.4 var(--mono);text-transform:uppercase;letter-spacing:.14em;color:var(--accent)}
p,li{color:var(--dim);margin:0 0 14px;text-wrap:pretty}
.lead{font-size:clamp(19px,2.2vw,23px);line-height:1.45;color:var(--fg)}
strong{color:var(--fg);font-weight:500}
ul{padding-left:1.1em;margin:0 0 14px}
.cta{display:inline-flex;margin-top:14px;padding:13px 22px;border-radius:999px;background:var(--accent);color:var(--bg0);text-decoration:none;font:500 12px/1 var(--mono);text-transform:uppercase;letter-spacing:.12em}
.cta:hover{background:var(--fg)}
footer{margin-top:72px;padding-top:18px;border-top:1px solid var(--line);display:flex;gap:8px 22px;flex-wrap:wrap}
</style>'''
MARK = '<svg viewBox="0 0 26 26" aria-hidden="true"><rect x="0" y="1" width="26" height="6" rx="3" fill="#F5F6F9"/><rect x="6.5" y="10" width="13" height="6" rx="3" fill="#4C8DF5"/><rect x="0" y="19" width="26" height="6" rx="3" fill="#F5F6F9"/></svg>'
for f in sorted((root / 'src/pages').glob('*.html')):
    body = f.read_text()
    m = re.match(r'<!-- title: (.*?) \| description: (.*?) -->\n', body)
    title, desc = m.group(1), m.group(2)
    (root / f.name).write_text(
        HEAD.format(title=title, desc=desc) + f'<title>{title}</title>\n{FONTS}\n{PAGE_CSS}\n</head>\n<body>\n<div class="w">\n'
        f'<header><a class="mark" href="index.html" aria-label="KaiTech home">{MARK}KAITECH</a><a class="back" href="index.html">Back to site</a></header>\n<main>\n'
        + body[m.end():] +
        '</main>\n<footer><a href="index.html">Home</a><a href="about.html">About</a><a href="privacy.html">Privacy</a><a href="terms.html">Terms</a><span>kaitechfj@gmail.com</span></footer>\n</div>\n</body>\n</html>\n')
print('built')

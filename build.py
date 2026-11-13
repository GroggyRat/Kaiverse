#!/usr/bin/env python3
"""Builds the static site from src/. Run: python3 build.py

src/content.json      the words: every section and product, used everywhere below
src/kaitech.html      -> index.html          the one-screen site (its content block is refreshed from content.json)
src/content.json      -> <product>.html      one plain page per product, for search engines and sharing
src/pages/<name>.html -> <name>.html         About, Privacy, Terms
                      -> sitemap.xml, robots.txt

Set SITE_URL to the site's address when it changes, for example SITE_URL=https://kaitech.com.fj python3 build.py
Put a square photo at assets/founder.jpg and it appears on the About page."""
import html, json, os, pathlib, re
root = pathlib.Path(__file__).parent
SITE = os.environ.get('SITE_URL', 'https://kaitechfj.vercel.app').rstrip('/')
C = json.loads((root / 'src/content.json').read_text())
site, sections = C['site'], C['sections']
products = [s for s in sections if s.get('product')]
e = lambda t: html.escape(str(t), quote=True)

def head(title, desc, path, extra=''):
    url = SITE + ('/' + path if path else '/')
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{e(url)}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="KaiTech">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{e(url)}">
<meta property="og:image" content="{SITE}/assets/og.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#030712">
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
{extra}'''

# ── 1. the one-screen site: refresh its content block, then wrap it ──
JS = ("// <content> written by build.py from src/content.json; edit that file, not this block\n"
      f"const MAIL = {json.dumps(site['email'])};\n"
      f"const MODES = {json.dumps(sections, ensure_ascii=False, indent=1)};\n"
      "// </content>\n")
srcp = root / 'src/kaitech.html'
src = srcp.read_text()
src = re.sub(r'// <content>.*?// </content>\n', lambda m: JS, src, count=1, flags=re.S)
srcp.write_text(src)
src = re.sub(r'<title>.*?</title>\n', '', src, count=1)
org = json.dumps({"@context": "https://schema.org", "@type": "Organization", "name": "KaiTech", "url": SITE + "/",
    "logo": SITE + "/assets/og.jpg", "email": site['email'], "telephone": site['phones'][0][1],
    "founder": {"@type": "Person", "name": site['founder']}, "areaServed": "Fiji",
    "makesOffer": [{"@type": "Offer", "itemOffered": {"@type": "SoftwareApplication", "name": p['product'],
        "applicationCategory": "BusinessApplication", "description": p['seo'], "url": f"{SITE}/{p['id']}"}} for p in products]})
(root / 'index.html').write_text(
    head('KaiTech · ' + site['tagline'], sections[0]['body'], '',
         f'<script type="application/ld+json">{org}</script>\n<style>body{{margin:0}}[hidden]{{display:none!important}}</style>\n')
    + '</head>\n<body>\n'
    + src + '</body>\n</html>\n')

# ── 2. shared look for the plain pages ──
FONTS = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter+Tight:wght@400;500&family=JetBrains+Mono:wght@400;500&family=Michroma&display=swap">'
PAGE_CSS = '''<style>
:root{--bg0:#030712;--bg1:#14295A;--fg:#F5F6F9;--dim:#A3ACC0;--line:#243049;--accent:#4C8DF5;color-scheme:dark;
  --display:'Michroma','Eurostile','Arial Black',sans-serif;--text:'Inter Tight',system-ui,-apple-system,'Segoe UI',sans-serif;--mono:'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace}
*{box-sizing:border-box}
body{margin:0;background:var(--bg0) radial-gradient(90% 60% at 80% 0%,var(--bg1) 0%,var(--bg0) 70%) no-repeat;color:var(--fg);font:17px/1.6 var(--text);-webkit-font-smoothing:antialiased;min-height:100vh}
.w{max-width:46rem;margin:0 auto;padding-block:22px 80px;padding-left:max(22px,env(safe-area-inset-left,0px));padding-right:max(22px,env(safe-area-inset-right,0px))}
a{color:inherit;text-underline-offset:3px}
a:focus-visible{outline:1px solid var(--fg);outline-offset:4px}
header{display:flex;justify-content:space-between;align-items:center;gap:16px;margin-bottom:clamp(48px,10vh,110px)}
.mark{display:flex;align-items:center;gap:12px;font:400 14px/1 var(--display);letter-spacing:.42em;text-decoration:none}
.mark svg{width:26px;height:26px}
.back,.tag,footer{font:400 11px/1.4 var(--mono);text-transform:uppercase;letter-spacing:.14em;color:var(--dim)}
.tag{margin:0 0 18px}
h1{margin:0 0 24px;font:400 clamp(28px,5vw,48px)/1.12 var(--display);letter-spacing:.01em;text-transform:uppercase;text-wrap:balance}
h2{margin:44px 0 10px;font:400 12px/1.4 var(--mono);text-transform:uppercase;letter-spacing:.14em;color:var(--accent)}
h3{margin:28px 0 6px;font:500 19px/1.3 var(--text);color:var(--fg)}
p,li{color:var(--dim);margin:0 0 14px;text-wrap:pretty}
.lead{font-size:clamp(19px,2.2vw,23px);line-height:1.45;color:var(--fg)}
strong{color:var(--fg);font-weight:500}
ul{padding-left:1.1em;margin:0 0 14px}
.acts{display:flex;gap:10px;flex-wrap:wrap;margin:22px 0 8px}
.cta{display:inline-flex;margin-top:14px;padding:13px 22px;border-radius:999px;background:var(--accent);color:var(--bg0);border:1px solid var(--accent);text-decoration:none;font:500 12px/1 var(--mono);text-transform:uppercase;letter-spacing:.12em}
.acts .cta{margin-top:0}
.cta:hover{background:var(--fg);border-color:var(--fg)}
.cta.ghost{background:transparent;color:var(--fg);border-color:var(--line)}
.cta.ghost:hover{border-color:var(--fg)}
dl{margin:28px 0 0;display:grid;grid-template-columns:auto minmax(0,1fr);font:400 12px/1.4 var(--mono);text-transform:uppercase;letter-spacing:.06em}
dt,dd{margin:0;padding:11px 0;border-top:1px solid var(--line)}
dt{padding-right:20px;color:var(--fg)} dd{text-align:right;color:var(--dim)}
.shots{display:grid;gap:18px;margin:36px 0 0}
.shots.phone{grid-template-columns:repeat(auto-fit,minmax(min(220px,100%),1fr))}
.shots figure{margin:0;background:var(--bg1);border-radius:14px;padding:12px}
.shots img{display:block;width:100%;height:auto;border-radius:8px}
.shots figcaption{margin-top:10px;font-size:14px;color:var(--dim)}
.more{list-style:none;padding:0;display:grid;grid-template-columns:repeat(auto-fit,minmax(min(170px,100%),1fr));gap:10px}
.more a{display:block;padding:16px;border:1px solid var(--line);border-radius:14px;text-decoration:none}
.more a:hover{border-color:var(--fg)}
.more b{display:block;font-weight:500;color:var(--fg)} .more span{font-size:14px;color:var(--dim)}
.founder{display:flex;align-items:center;gap:18px;margin:0 0 26px}
.founder img,.founder .ph{width:84px;height:84px;border-radius:50%;object-fit:cover;flex:none;background:var(--bg1);border:1px solid var(--line)}
.founder .ph{display:grid;place-items:center;font:400 22px/1 var(--display);letter-spacing:.06em}
.founder span{font:400 11px/1.5 var(--mono);text-transform:uppercase;letter-spacing:.14em;color:var(--dim)}
.founder b{display:block;font:500 18px/1.3 var(--text);text-transform:none;letter-spacing:0;color:var(--fg)}
.clients{display:flex;gap:28px;align-items:center;flex-wrap:wrap;margin:18px 0 6px}
.clients img{height:22px;width:auto}
.clients .tp{display:inline-flex;align-items:center;gap:10px;font:400 13px/1 var(--display);letter-spacing:.14em}
.clients .tp svg{width:20px;height:20px}
footer{margin-top:72px;padding-top:18px;border-top:1px solid var(--line);display:flex;gap:8px 22px;flex-wrap:wrap}
</style>'''
MARK = '<svg viewBox="0 0 26 26" aria-hidden="true"><rect x="0" y="1" width="26" height="6" rx="3" fill="#F5F6F9"/><rect x="6.5" y="10" width="13" height="6" rx="3" fill="#4C8DF5"/><rect x="0" y="19" width="26" height="6" rx="3" fill="#F5F6F9"/></svg>'
FOOT = ('<footer><a href="index.html">Home</a>' + ''.join(f'<a href="{p["id"]}.html">{e(p["product"])}</a>' for p in products)
        + '<a href="about.html">About</a><a href="privacy.html">Privacy</a><a href="terms.html">Terms</a></footer>')
CLIENTS = ('<div class="clients"><img src="assets/clients/nafco.png" alt="NAFCO" width="75" height="22">'
           '<span class="tp"><svg viewBox="0 0 24 24" aria-hidden="true"><rect x=".75" y=".75" width="22.5" height="22.5" fill="none" stroke="currentColor" stroke-width="1.5"/>'
           '<path d="M4 4l8 8-8 8zM20 4l-8 8 8 8z" fill="currentColor"/><path d="M12 7l2.2 5L12 17l-2.2-5z" fill="none" stroke="currentColor" stroke-width="1.1"/></svg>Totoka Pacific</span></div>')
photo = root / 'assets/founder.jpg'
FOUNDER = ('<div class="founder">' + (f'<img src="assets/founder.jpg" alt="{e(site["founder"])}" width="84" height="84">' if photo.exists()
           else '<div class="ph" aria-hidden="true">' + ''.join(w[0] for w in site['founder'].split()) + '</div>')
           + f'<span><b>{e(site["founder"])}</b>Founder, KaiTech</span></div>')

def page(name, title, desc, body):
    (root / f'{name}.html').write_text(
        head(title, desc, name) + f'{FONTS}\n{PAGE_CSS}\n</head>\n<body>\n<div class="w">\n'
        f'<header><a class="mark" href="index.html" aria-label="KaiTech home">{MARK}KAITECH</a><a class="back" href="index.html">Back to site</a></header>\n<main>\n'
        + body + f'</main>\n{FOOT}\n</div>\n</body>\n</html>\n')

# ── 3. one page per product ──
for p in products:
    shots = p.get('screens') or []
    phone = shots and all(s.get('phone') for s in shots)
    body = (f'<p class="tag">{e(p["kind"])} · live</p>\n<h1>{e(p["product"])}</h1>\n<p class="lead">{e(p["body"])}</p>\n'
            f'<div class="acts"><a class="cta" href="index.html#demo-{p["id"]}">Book a demo</a><a class="cta ghost" href="index.html#{p["id"]}">See it on the site</a></div>\n'
            '<dl>' + ''.join(f'<dt>{e(a)}</dt><dd>{e(b)}</dd>' for a, b in p['slots']) + '</dl>\n')
    if shots:
        body += f'<div class="shots{" phone" if phone else ""}">' + ''.join(
            f'<figure><img src="{e(s["src"])}" alt="{e(s["caption"])}" width="{s["w"]}" height="{s["h"]}" loading="lazy"><figcaption>{e(s["caption"])}</figcaption></figure>'
            for s in shots) + '</div>\n<p class="tag" style="margin-top:12px">Shown with sample data</p>\n'
    body += '<h2>What it does</h2>\n' + ''.join(f'<h3>{e(h)}</h3>\n<p>{e(t)}</p>\n' for h, t in p['points'])
    body += ('<h2>See it for your business</h2>\n<p>We will show you ' + e(p['product']) + ' with your own kind of work, and answer anything you want to know.</p>\n'
             f'<div class="acts"><a class="cta" href="index.html#demo-{p["id"]}">Book a demo</a></div>\n'
             '<h2>More from KaiTech</h2>\n<ul class="more">' + ''.join(
                 f'<li><a href="{q["id"]}.html"><b>{e(q["product"])}</b><span>{e(q["kind"])}</span></a></li>' for q in products if q is not p) + '</ul>\n')
    page(p['id'], f'{p["product"]} · {p["kind"]} software for Fiji · KaiTech', p['seo'], body)

# ── 4. About, Privacy, Terms ──
for f in sorted((root / 'src/pages').glob('*.html')):
    body = f.read_text()
    m = re.match(r'<!-- title: (.*?) \| description: (.*?) -->\n', body)
    body = body[m.end():].replace('<!--founder-->', FOUNDER).replace('<!--clients-->', CLIENTS)
    page(f.stem, m.group(1), m.group(2), body)

# ── 5. for search engines ──
paths = [''] + [p['id'] for p in products] + ['about', 'privacy', 'terms']
(root / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + ''.join(f'  <url><loc>{SITE}/{p}</loc></url>\n' for p in paths) + '</urlset>\n')
(root / 'robots.txt').write_text(f'User-agent: *\nAllow: /\nDisallow: /api/\n\nSitemap: {SITE}/sitemap.xml\n')
print('built', ', '.join(['index'] + [p['id'] for p in products] + [f.stem for f in sorted((root / "src/pages").glob("*.html"))]), '+ sitemap.xml, robots.txt for', SITE)

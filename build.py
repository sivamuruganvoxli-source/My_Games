# -*- coding: utf-8 -*-
"""Builds the static My Games Bay site into ./dist  (run: python3 build.py)"""
import os, json, shutil, html, datetime
from games_data import GAMES, CATEGORIES, COLORS

# ------------------------------------------------------------------ CONFIG
SITE = "https://my-games-bay.vercel.app"
SITE_NAME = "My Games Bay"
# !! No contact address exists anywhere in the original project. Put your REAL
# !! address here before deploying. The build prints a warning until you do.
CONTACT_EMAIL = os.environ.get("CONTACT_EMAIL", "sivamurugan0412@gmail.com").strip()

# ---- AdSense (all OFF until you fill these in) -------------------------------
# ADSENSE_PUBLISHER_ID: your own ID from AdSense (looks like "pub-" + 16 digits, or "ca-pub-..."). Leave empty = no AdSense script, no ads.txt.
ADSENSE_PUBLISHER_ID = os.environ.get("ADSENSE_PUBLISHER_ID", "").strip()
# Optional ad-unit (slot) IDs created in AdSense -> Ads -> By ad unit. An empty slot = no ad shown at that location.
ADSENSE_SLOTS = {"home": "", "category": "", "game": ""}
# Set True ONLY after you have published a Google-certified message in AdSense -> Privacy & messaging (see ADSENSE_CONSENT_SETUP.md).
CONSENT_CONFIGURED = False
TODAY = "2026-09-19"
UPDATED_HUMAN = "September 19, 2026"
DIST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dist")

esc = html.escape
def slug_cat(c): return c.lower()
CATS = list(CATEGORIES.keys())
BY_SLUG = {g["slug"]: g for g in GAMES}
def indexable(g): return g.get("verified", True) and not g.get("dup")

def contact_html():
    if CONTACT_EMAIL:
        return f'<a href="mailto:{esc(CONTACT_EMAIL)}">{esc(CONTACT_EMAIL)}</a>'
    return '<strong>[add your contact email in build.py before publishing]</strong>'

# ------------------------------------------------------------------ CSS / JS
CSS = r"""
:root{--bg:#070b14;--bg-alt:#0b1120;--grid-line:rgba(255,255,255,.035);--surface:rgba(255,255,255,.05);--surface-hover:rgba(255,255,255,.09);--border:rgba(255,255,255,.1);--border-strong:rgba(255,255,255,.2);--text:#eaf2ff;--muted:#9aabc7;--muted-dim:#7d8ca8;--cyan:#00f0ff;--magenta:#ff2ee6;--radius-lg:20px;--radius-md:14px;--radius-sm:9px;--font-body:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;--font-mono:Consolas,'Courier New',monospace}
*{margin:0;padding:0;box-sizing:border-box}
html{scroll-behavior:smooth}
body{background:radial-gradient(ellipse 900px 500px at 15% -5%,rgba(0,240,255,.08),transparent 60%),radial-gradient(ellipse 900px 500px at 85% 0%,rgba(255,46,230,.07),transparent 60%),repeating-linear-gradient(0deg,var(--grid-line) 0,var(--grid-line) 1px,transparent 1px,transparent 42px),repeating-linear-gradient(90deg,var(--grid-line) 0,var(--grid-line) 1px,transparent 1px,transparent 42px),var(--bg);color:var(--text);font-family:var(--font-body);min-height:100vh;line-height:1.6;-webkit-font-smoothing:antialiased;overflow-x:hidden;display:flex;flex-direction:column}
main{flex:1}
a{color:inherit;text-decoration:none}
img{max-width:100%;display:block}
ul{list-style:none}
button{font-family:inherit;border:none;background:none;cursor:pointer;color:inherit}
input{font-family:inherit}
:focus-visible{outline:2px solid var(--cyan);outline-offset:3px;border-radius:4px}
.wrap{max-width:1200px;margin:0 auto;padding:0 24px}
.skip{position:absolute;left:-999px;top:8px;background:var(--cyan);color:#04070d;padding:8px 14px;border-radius:6px;z-index:100}
.skip:focus{left:8px}
/* header */
.site-header{position:sticky;top:0;z-index:50;backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);background:rgba(7,11,20,.85);border-bottom:1px solid var(--border)}
.site-header .wrap{display:flex;align-items:center;justify-content:space-between;min-height:74px;gap:20px;flex-wrap:wrap}
.logo{font-size:19px;font-weight:800;letter-spacing:1px;display:flex;align-items:center;gap:10px;flex-shrink:0}
.logo .dot{width:9px;height:9px;border-radius:50%;background:var(--cyan);box-shadow:0 0 10px 2px var(--cyan)}
.logo .bay{color:var(--cyan)}
.nav-links{display:flex;gap:6px 22px;font-family:var(--font-mono);font-size:12.5px;letter-spacing:1px;text-transform:uppercase;flex-wrap:wrap}
.nav-links a{color:var(--muted);padding:10px 2px;transition:color .2s}
.nav-links a:hover,.nav-links a[aria-current=page]{color:var(--text)}
/* hero */
.hero{padding:64px 0 36px;border-bottom:1px solid var(--border)}
.eyebrow{font-family:var(--font-mono);font-size:12.5px;letter-spacing:3px;text-transform:uppercase;color:var(--cyan);margin-bottom:14px}
.hero h1,.page-title{font-size:clamp(28px,5vw,48px);font-weight:800;line-height:1.12;background:linear-gradient(90deg,#fff 25%,var(--cyan) 65%,var(--magenta) 100%);-webkit-background-clip:text;background-clip:text;color:transparent;max-width:780px;margin-bottom:16px}
.hero p.sub{color:var(--muted);font-size:16.5px;max-width:600px;margin-bottom:28px}
.controls{display:flex;flex-direction:column;gap:18px}
.search-box{position:relative;max-width:440px}
.search-box input{width:100%;padding:14px 18px 14px 46px;background:var(--surface);border:1px solid var(--border);border-radius:100px;color:var(--text);font-size:16px}
.search-box input::placeholder{color:var(--muted-dim)}
.search-box input:focus{border-color:var(--cyan);outline:none}
.search-box .icon{position:absolute;left:18px;top:50%;transform:translateY(-50%);pointer-events:none}
.filters{display:flex;gap:10px;flex-wrap:wrap}
.chip{font-family:var(--font-mono);font-size:12px;letter-spacing:.8px;text-transform:uppercase;padding:10px 18px;border-radius:100px;border:1px solid var(--border-strong);color:var(--muted);transition:all .2s}
.chip:hover{color:var(--text);background:var(--surface)}
.chip.active{color:#04070d;font-weight:700;background:linear-gradient(90deg,var(--cyan),var(--magenta));border-color:transparent}
/* sections */
.section-head{margin:52px 0 24px}
.section-head h2{font-size:clamp(20px,3vw,27px);font-weight:800}
.section-head p{color:var(--muted);margin-top:6px;max-width:680px}
.result-count{font-family:var(--font-mono);font-size:12px;color:var(--muted-dim);margin-top:4px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,270px),1fr));gap:22px;padding-bottom:56px}
.card{position:relative;background:var(--surface);border:1px solid var(--border);border-radius:var(--radius-lg);padding:2px;transition:transform .3s ease,box-shadow .3s ease}
.card::before{content:"";position:absolute;inset:0;border-radius:var(--radius-lg);padding:1px;background:linear-gradient(135deg,var(--c1,var(--cyan)),var(--c2,var(--magenta)));opacity:0;transition:opacity .3s;-webkit-mask:linear-gradient(#fff 0 0) content-box,linear-gradient(#fff 0 0);-webkit-mask-composite:xor;mask-composite:exclude;pointer-events:none}
.card:hover,.card:focus-within{transform:translateY(-5px);box-shadow:0 20px 45px -20px rgba(0,0,0,.6),0 0 30px -8px var(--c1,var(--cyan))}
.card:hover::before,.card:focus-within::before{opacity:1}
.card-inner{background:var(--bg-alt);border-radius:calc(var(--radius-lg) - 2px);padding:24px;height:100%;display:flex;flex-direction:column}
.card-top{display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:14px}
.card-icon{font-size:34px}
.badge{font-family:var(--font-mono);font-size:10.5px;letter-spacing:1px;text-transform:uppercase;padding:5px 11px;border-radius:100px;border:1px solid var(--border-strong);color:var(--muted);white-space:nowrap}
.card h3{font-size:19px;font-weight:800;margin-bottom:8px}
.card p{color:var(--muted);font-size:14px;margin-bottom:20px;flex-grow:1}
.card .stretch::after{content:"";position:absolute;inset:0;border-radius:var(--radius-lg)}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;font-weight:700;font-size:14px;padding:13px 22px;border-radius:var(--radius-sm);border:1px solid transparent;min-height:44px;transition:transform .2s,box-shadow .2s}
.btn-primary{background:linear-gradient(90deg,var(--c1,var(--cyan)),var(--c2,var(--magenta)));color:#04070d}
.btn-primary:hover{transform:translateY(-2px);box-shadow:0 10px 25px -8px var(--c1,var(--cyan))}
.btn-ghost{border-color:var(--border-strong);color:var(--text)}
.btn-ghost:hover{background:var(--surface-hover)}
.btn-block{width:100%}
.no-results{text-align:center;padding:50px 20px;color:var(--muted)}
[hidden]{display:none!important}
.cat-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,210px),1fr));gap:16px;padding-bottom:20px}
.cat-tile{display:block;border:1px solid var(--border);background:var(--surface);border-radius:var(--radius-md);padding:18px;border-top:3px solid var(--c1)}
.cat-tile:hover{background:var(--surface-hover)}
.cat-tile h3{font-size:17px;margin-bottom:4px}
.cat-tile p{font-size:13px;color:var(--muted)}
/* breadcrumb */
.breadcrumb{padding:22px 0 0;font-family:var(--font-mono);font-size:12.5px;color:var(--muted-dim)}
.breadcrumb a{color:var(--muted);padding:6px 0;display:inline-block}
.breadcrumb a:hover{color:var(--cyan)}
.breadcrumb .sep{margin:0 6px}
/* game page */
.game-head{padding:28px 0 20px}
.game-head h1{font-size:clamp(28px,5vw,42px);font-weight:800;line-height:1.1;margin:8px 0 12px;background:linear-gradient(90deg,#fff 20%,var(--c1,var(--cyan)) 100%);-webkit-background-clip:text;background-clip:text;color:transparent}
.game-head .lead{color:var(--muted);font-size:16px;max-width:760px}
.pills{display:flex;gap:10px;flex-wrap:wrap;margin-top:16px}
.pill{font-family:var(--font-mono);font-size:12px;padding:6px 12px;border:1px solid var(--border-strong);border-radius:100px;color:var(--muted)}
.play-panel{margin:8px 0 12px;border:1px solid var(--border-strong);border-radius:var(--radius-lg);background:var(--bg-alt);box-shadow:0 30px 60px -30px rgba(0,0,0,.7),0 0 40px -14px var(--c1,var(--cyan));overflow:hidden}
.play-frame{position:relative;width:100%;aspect-ratio:16/10;max-height:80vh;background:#03050a;display:flex;align-items:center;justify-content:center;flex-direction:column;gap:14px;text-align:center;padding:20px}
.play-frame iframe{position:absolute;inset:0;width:100%;height:100%;border:0}
.play-frame .big-icon{font-size:56px}
.play-bar{display:flex;gap:10px;flex-wrap:wrap;align-items:center;justify-content:space-between;padding:12px 16px;border-top:1px solid var(--border);font-size:13px;color:var(--muted)}
.play-bar .actions{display:flex;gap:10px;flex-wrap:wrap}
.play-bar .btn{padding:9px 16px;font-size:13px;min-height:40px}
.notice{border-left:3px solid var(--c1,var(--cyan));background:var(--surface);padding:12px 16px;border-radius:0 var(--radius-sm) var(--radius-sm) 0;color:var(--muted);font-size:14px;margin:14px 0}
.info-grid{display:grid;grid-template-columns:1.3fr 1fr;gap:40px;padding:24px 0 10px}
@media(max-width:860px){.info-grid{grid-template-columns:1fr;gap:8px}}
.info h2,.prose h2{font-size:21px;margin:26px 0 10px}
.info h2:first-child{margin-top:0}
.info p,.info li,.prose p,.prose li{color:var(--muted);font-size:15.5px}
.info ol{padding-left:22px;display:grid;gap:8px}
.info ul.bul,.prose ul{padding-left:20px;list-style:disc;display:grid;gap:6px}
.prose ol{padding-left:22px;display:grid;gap:6px}
.info li::marker,.prose li::marker{color:var(--cyan)}
table.ctl{width:100%;border-collapse:collapse;font-size:14.5px}
table.ctl th,table.ctl td{text-align:left;padding:10px 12px;border-bottom:1px solid var(--border);vertical-align:top}
table.ctl th{color:var(--text);font-weight:600;width:34%}
table.ctl td{color:var(--muted)}
.prose{max-width:780px;padding:12px 0 60px}
.prose h3{font-size:17px;margin:18px 0 6px}
.prose p{margin-bottom:12px}
.prose a,.info a{color:var(--cyan);text-decoration:underline;text-underline-offset:3px}
.prose .updated{font-family:var(--font-mono);font-size:12px;color:var(--muted-dim);margin-bottom:18px}
.spacer{height:56px}
.ad-slot{margin:36px 0;min-height:120px;text-align:center;overflow:hidden}
.ad-label{display:block;font-family:var(--font-mono);font-size:11px;color:var(--muted-dim);margin-bottom:6px}
/* footer */
.site-footer{border-top:1px solid var(--border);padding:44px 0 28px;margin-top:20px;background:rgba(3,5,10,.5)}
.foot-grid{display:grid;grid-template-columns:1.4fr 1fr 1fr 1fr;gap:32px}
@media(max-width:760px){.foot-grid{grid-template-columns:1fr 1fr}}
@media(max-width:460px){.foot-grid{grid-template-columns:1fr}}
.foot-grid h2{font-family:var(--font-mono);font-size:12px;letter-spacing:1.5px;text-transform:uppercase;color:var(--text);margin-bottom:12px}
.foot-grid li a{display:inline-block;padding:5px 0;color:var(--muted);font-size:14px}
.foot-grid li a:hover{color:var(--cyan)}
.foot-about p{color:var(--muted);font-size:14px;max-width:320px;margin-top:10px}
.foot-bottom{margin-top:30px;padding-top:20px;border-top:1px solid var(--border);font-family:var(--font-mono);font-size:12px;color:var(--muted-dim);display:flex;justify-content:space-between;flex-wrap:wrap;gap:10px}
#back-to-top{position:fixed;right:20px;bottom:20px;z-index:60;width:46px;height:46px;border-radius:50%;background:linear-gradient(135deg,var(--cyan),var(--magenta));color:#04070d;font-size:18px;font-weight:800;opacity:0;visibility:hidden;transition:opacity .3s,visibility .3s}
#back-to-top.show{opacity:1;visibility:visible}
@media(max-width:640px){.hero{padding:44px 0 28px}.wrap{padding:0 18px}.site-header .wrap{padding-top:8px;padding-bottom:4px}.nav-links{width:100%;justify-content:space-between;gap:0 6px;font-size:11px;letter-spacing:.3px}.play-frame{aspect-ratio:4/3}}
@media(prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important;scroll-behavior:auto!important}}
"""

JS = r"""
(function(){
  // back to top
  var b=document.getElementById('back-to-top');
  if(b){window.addEventListener('scroll',function(){b.classList.toggle('show',window.scrollY>420)},{passive:true});
    b.addEventListener('click',function(){window.scrollTo({top:0,behavior:'smooth'})});}
  // search + category filter (progressive enhancement: all cards are already in the HTML)
  var grid=document.getElementById('game-grid');
  if(grid){
    var input=document.getElementById('search-input'),chips=document.querySelectorAll('.chip[data-cat]'),
        count=document.getElementById('result-count'),none=document.getElementById('no-results'),
        cards=Array.prototype.slice.call(grid.querySelectorAll('.card')),cat='All';
    function apply(){
      var q=(input.value||'').trim().toLowerCase(),n=0;
      cards.forEach(function(c){
        var ok=(cat==='All'||c.dataset.cat===cat)&&(!q||c.dataset.search.indexOf(q)!==-1);
        c.hidden=!ok; if(ok)n++;
      });
      count.textContent=n+' game'+(n===1?'':'s')+' found';
      none.hidden=n!==0;
    }
    input.addEventListener('input',apply);
    chips.forEach(function(ch){ch.addEventListener('click',function(){
      cat=ch.dataset.cat;chips.forEach(function(c){c.classList.remove('active');c.setAttribute('aria-pressed','false')});
      ch.classList.add('active');ch.setAttribute('aria-pressed','true');apply();});});
    var p=new URLSearchParams(location.search);
    if(p.get('search')){input.value=p.get('search');}
    if(p.get('category')){chips.forEach(function(c){if(c.dataset.cat.toLowerCase()===p.get('category').toLowerCase())c.click();});}
    apply();
  }
  // click-to-load game frame
  var btn=document.getElementById('load-game'),frame=document.getElementById('play-frame');
  if(btn&&frame){
    btn.addEventListener('click',function(){
      var f=document.createElement('iframe');
      f.src=frame.dataset.src;
      f.title=frame.dataset.title;
      f.setAttribute('allow','fullscreen; autoplay; gamepad');
      f.setAttribute('sandbox','allow-scripts allow-same-origin allow-pointer-lock allow-popups allow-forms');
      f.setAttribute('referrerpolicy','strict-origin-when-cross-origin');
      frame.innerHTML='';frame.appendChild(f);f.focus();
    });
  }
  var fs=document.getElementById('fs-btn');
  if(fs&&frame){fs.addEventListener('click',function(){
    var el=frame.requestFullscreen?frame:null; if(el){el.requestFullscreen().catch(function(){});}
  });if(!frame.requestFullscreen){fs.hidden=true;}}
})();
"""

# ------------------------------------------------------------------ ADSENSE (config-driven, off by default)
import re as _re
def _pub_id():
    v = ADSENSE_PUBLISHER_ID.lower().replace("ca-", "")
    if not v: return ""
    if not _re.fullmatch(r"pub-\d{16}", v):
        raise SystemExit("ADSENSE_PUBLISHER_ID must look like pub-1234567890123456 (or ca-pub-...). Got: " + ADSENSE_PUBLISHER_ID)
    return v
PUB = _pub_id()
ADS_ON = bool(PUB)

def adsense_head():
    if not ADS_ON: return ""
    return f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-{PUB}" crossorigin="anonymous"></script>'

def ad_slot(kind):
    """One responsive display unit, only when the publisher ID and this location's slot ID are both set."""
    slot = ADSENSE_SLOTS.get(kind, "")
    if not (ADS_ON and slot): return ""
    return (f'<aside class="ad-slot" aria-label="Advertisement"><span class="ad-label">Advertisement</span>'
            f'<ins class="adsbygoogle" style="display:block" data-ad-client="ca-{PUB}" data-ad-slot="{esc(slot)}" '
            f'data-ad-format="auto" data-full-width-responsive="true"></ins>'
            f'<script>(adsbygoogle = window.adsbygoogle || []).push({{}});</script></aside>')

# ------------------------------------------------------------------ TEMPLATE
def ld(obj): return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False) + '</script>'

def breadcrumb_ld(crumbs):
    return ld({"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":i+1,"name":n,"item":SITE+p} for i,(n,p) in enumerate(crumbs)]})

def crumbs_html(crumbs):
    parts=[]
    for i,(n,p) in enumerate(crumbs):
        if i==len(crumbs)-1: parts.append(f'<span aria-current="page">{esc(n)}</span>')
        else: parts.append(f'<a href="{p}">{esc(n)}</a>')
    return '<nav class="wrap breadcrumb" aria-label="Breadcrumb">' + '<span class="sep">/</span>'.join(parts) + '</nav>'

def page(title, desc, path, body, extra_ld="", noindex=False, current="", og_type="website"):
    url = SITE + path
    robots = "noindex, follow" if noindex else "index, follow, max-image-preview:large"
    nav = [("Home","/","home"),("All Games","/games/","games"),("Categories","/#categories","cats"),("About","/about/","about"),("Contact","/contact/","contact")]
    nav_html = "".join(f'<a href="{h}"' + (' aria-current="page"' if k==current else '') + f'>{n}</a>' for n,h,k in nav)
    cats_f = "".join(f'<li><a href="/category/{slug_cat(c)}/">{c} Games</a></li>' for c in CATS)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="{robots}">
<meta name="theme-color" content="#070b14">
<link rel="canonical" href="{url}">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Ccircle cx='32' cy='32' r='16' fill='%2300f0ff'/%3E%3C/svg%3E">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="{SITE_NAME}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/og-cover.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="My Games Bay: free browser games">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(desc)}">
<meta name="twitter:image" content="{SITE}/og-cover.png">
<link rel="stylesheet" href="/assets/style.css">
{extra_ld}
{adsense_head()}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
  <div class="wrap">
    <a class="logo" href="/"><span class="dot" aria-hidden="true"></span>MY GAMES <span class="bay">BAY</span></a>
    <nav class="nav-links" aria-label="Main">{nav_html}</nav>
  </div>
</header>
<main id="main">
{body}
</main>
<footer class="site-footer">
  <div class="wrap">
    <div class="foot-grid">
      <div class="foot-about"><a class="logo" href="/"><span class="dot" aria-hidden="true"></span>MY GAMES <span class="bay">BAY</span></a>
        <p>A collection of free browser games. No downloads and no accounts.</p></div>
      <div><h2>Games</h2><ul><li><a href="/games/">All Games</a></li>{cats_f}</ul></div>
      <div><h2>Site</h2><ul><li><a href="/">Home</a></li><li><a href="/about/">About Us</a></li><li><a href="/contact/">Contact Us</a></li></ul></div>
      <div><h2>Legal</h2><ul><li><a href="/privacy-policy/">Privacy Policy</a></li><li><a href="/terms/">Terms &amp; Conditions</a></li><li><a href="/disclaimer/">Disclaimer</a></li><li><a href="/cookie-policy/">Cookie Policy</a></li></ul></div>
    </div>
    <div class="foot-bottom"><span>© 2026 {SITE_NAME}</span><span>Free browser games</span></div>
  </div>
</footer>
<button id="back-to-top" aria-label="Back to top">↑</button>
<script src="/assets/app.js" defer></script>
</body>
</html>
"""

def style_vars(cat):
    c1,c2 = COLORS[cat]; return f'--c1:{c1};--c2:{c2};'

def card(g):
    search = (g["title"]+" "+g["short"]+" "+g["cat"]+" "+g.get("ingame","")).lower()
    return f"""<article class="card" data-cat="{g['cat']}" data-search="{esc(search)}" style="{style_vars(g['cat'])}">
  <div class="card-inner">
    <div class="card-top"><div class="card-icon" aria-hidden="true">{g['icon']}</div><span class="badge">{g['cat']}</span></div>
    <h3>{esc(g['title'])}</h3>
    <p>{esc(g['short'])}</p>
    <a class="btn btn-primary btn-block stretch" href="/games/{g['slug']}/">Play {esc(g['title'])}</a>
  </div>
</article>"""

# ------------------------------------------------------------------ PAGES
def write(path, content, binary=False):
    full = os.path.join(DIST, path.lstrip("/"))
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "wb" if binary else "w", **({} if binary else {"encoding":"utf-8"})) as f: f.write(content)

def listing_controls():
    chips = '<button class="chip active" data-cat="All" aria-pressed="true">All</button>' + "".join(
        f'<button class="chip" data-cat="{c}" aria-pressed="false">{c}</button>' for c in CATS)
    return f"""<div class="controls">
  <div class="search-box"><span class="icon" aria-hidden="true">🔍</span>
    <input type="search" id="search-input" placeholder="Search games" aria-label="Search games" autocomplete="off"></div>
  <div class="filters" role="group" aria-label="Filter by category">{chips}</div>
</div>"""

def build_home():
    cards = "".join(card(g) for g in GAMES)
    tiles = "".join(f'<a class="cat-tile" href="/category/{slug_cat(c)}/" style="{style_vars(c)}"><h3>{c}</h3><p>{esc(CATEGORIES[c])}</p></a>' for c in CATS)
    body = f"""<section class="hero"><div class="wrap">
  <p class="eyebrow">Free browser games</p>
  <h1>Pick a game and play in your browser. No downloads, no accounts.</h1>
  <p class="sub">My Games Bay is a collection of {len(GAMES)} free browser games. Every game page explains how to play and lists the controls, so you can start straight away on a computer or a phone.</p>
  {listing_controls()}
</div></section>
<div class="wrap">
  <div class="section-head"><h2>Game library</h2><p class="result-count" id="result-count" aria-live="polite">{len(GAMES)} games found</p></div>
  <div class="grid" id="game-grid">{cards}</div>
  <p class="no-results" id="no-results" hidden>No games match your search. Try a different word or category.</p>

  <div class="section-head" id="categories"><h2>Browse by category</h2></div>
  <div class="cat-grid">{tiles}</div>

  {ad_slot("home")}
  <div class="section-head" id="about-section"><h2>About My Games Bay</h2>
    <p>My Games Bay is a small collection of free, browser-based games. Every title opens in your browser tab, with nothing to install and no account required. Each game has its own page with a short description, how to play, controls and whether it works on mobile. <a href="/about/" style="color:var(--cyan);text-decoration:underline">Read more about the site</a>.</p></div>
  <div class="spacer"></div>
</div>"""
    site_ld = ld({"@context":"https://schema.org","@type":"WebSite","name":SITE_NAME,"url":SITE+"/","description":"Free browser games you can play instantly, with no downloads or sign-up."})
    write("index.html", page(f"{SITE_NAME}: Free Browser Games, No Download",
        "Play free browser games instantly: action, arcade, puzzle, multiplayer and strategy. Each game has a guide with controls and mobile support. No downloads or sign-up.",
        "/", body, site_ld, current="home"))

def build_games_index():
    cards = "".join(card(g) for g in GAMES)
    crumbs=[("Home","/"),("All Games","/games/")]
    body = crumbs_html(crumbs)+f"""<section class="wrap" style="padding:26px 0 0">
  <h1 class="page-title">All free browser games</h1>
  <p class="sub" style="color:var(--muted);max-width:640px;margin-bottom:24px">Browse all {len(GAMES)} games. Search by name or filter by category, then open a game page to read how to play and start the game.</p>
  {listing_controls()}
  <div class="section-head" style="margin-top:36px"><p class="result-count" id="result-count" aria-live="polite">{len(GAMES)} games found</p></div>
  <div class="grid" id="game-grid">{cards}</div>
  <p class="no-results" id="no-results" hidden>No games match your search. Try a different word or category.</p>
</section>"""
    items = ld({"@context":"https://schema.org","@type":"ItemList","itemListElement":[
        {"@type":"ListItem","position":i+1,"url":f"{SITE}/games/{g['slug']}/","name":g["title"]} for i,g in enumerate([x for x in GAMES if indexable(x)])]})
    write("games/index.html", page(f"All Free Browser Games | {SITE_NAME}",
        f"Browse all {len(GAMES)} free browser games on My Games Bay. Filter by action, arcade, puzzle, multiplayer or strategy and start playing in your browser.",
        "/games/", body, breadcrumb_ld(crumbs)+items, current="games"))

def build_categories():
    for c in CATS:
        gl = [g for g in GAMES if g["cat"]==c]
        crumbs=[("Home","/"),("All Games","/games/"),(f"{c} Games",f"/category/{slug_cat(c)}/")]
        body = crumbs_html(crumbs)+f"""<section class="wrap" style="padding:26px 0 0">
  <h1 class="page-title">Free {c.lower()} games</h1>
  <p class="sub" style="color:var(--muted);max-width:640px">{esc(CATEGORIES[c])} There {'is' if len(gl)==1 else 'are'} {len(gl)} {c.lower()} game{'' if len(gl)==1 else 's'} on My Games Bay.</p>
  <div class="grid" style="margin-top:32px">{"".join(card(g) for g in gl)}</div>
  {ad_slot("category")}
</section>"""
        write(f"category/{slug_cat(c)}/index.html", page(f"Free {c} Games to Play Online | {SITE_NAME}",
            f"Play free {c.lower()} browser games. Browse {len(gl)} {c.lower()} game{'' if len(gl)==1 else 's'} with how-to-play guides, controls and mobile info. No download needed.",
            f"/category/{slug_cat(c)}/", body, breadcrumb_ld(crumbs), current="cats"))

def mob_pill(g):
    m=g['mobile']
    if m.startswith('Yes'): return 'Mobile friendly'
    if m.startswith('Touch'): return 'Touch controls'
    if m.startswith('Works'): return 'Mobile: harder'
    return 'Mobile: see below'

def related(g):
    same=[x for x in GAMES if x["slug"]!=g["slug"] and x["cat"]==g["cat"] and indexable(x)]
    other=[x for x in GAMES if x["slug"]!=g["slug"] and x["cat"]!=g["cat"] and indexable(x)]
    return (same+other)[:3]

def build_game(g):
    path=f"/games/{g['slug']}/"
    crumbs=[("Home","/"),("All Games","/games/"),(f"{g['cat']} Games",f"/category/{slug_cat(g['cat'])}/"),(g["title"],path)]
    ctrl = "".join(f"<tr><th scope='row'>{esc(a)}</th><td>{esc(b)}</td></tr>" for a,b in g["controls"])
    how = "".join(f"<li>{esc(s)}</li>" for s in g["how"])
    feats = "".join(f"<li>{esc(s)}</li>" for s in g["features"])
    ingame = f'<p style="margin-top:6px">Title shown inside the game: <em>{esc(g["ingame"])}</em></p>' if g.get("ingame") and g["ingame"]!=g["title"] else ""
    note = f'<div class="notice">{esc(g["note"])}</div>' if g.get("note") else ""
    rel = "".join(card(x) for x in related(g))
    host = g["url"].split("/")[2]
    body = crumbs_html(crumbs)+f"""<div class="wrap" style="{style_vars(g['cat'])}">
<header class="game-head">
  <div style="font-size:40px" aria-hidden="true">{g['icon']}</div>
  <h1>{esc(g['title'])}</h1>
  <p class="lead">{esc(g['short'])}</p>
  <div class="pills"><a class="pill" href="/category/{slug_cat(g['cat'])}/">{g['cat']}</a><span class="pill">Free</span><span class="pill">Plays in browser</span><span class="pill">{esc(mob_pill(g))}</span></div>
</header>

<section class="play-panel" aria-label="Play {esc(g['title'])}">
  <div class="play-frame" id="play-frame" data-src="{esc(g['url'])}" data-title="{esc(g['title'])}">
    <div class="big-icon" aria-hidden="true">{g['icon']}</div>
    <button class="btn btn-primary" id="load-game" type="button">▶ Play {esc(g['title'])}</button>
    <noscript><a class="btn btn-primary" href="{esc(g['url'])}" rel="noopener" target="_blank">Play {esc(g['title'])} (opens in a new tab)</a></noscript>
  </div>
  <div class="play-bar">
    <span>The game loads from {esc(host)} when you press Play. If it does not appear here, open it in a new tab.</span>
    <span class="actions"><button class="btn btn-ghost" id="fs-btn" type="button">Full screen</button><a class="btn btn-ghost" href="{esc(g['url'])}" target="_blank" rel="noopener">Open in new tab</a></span>
  </div>
</section>
{note}

<div class="info-grid">
  <div class="info">
    <h2>About {esc(g['title'])}</h2>
    <p>{esc(g['about'])}</p>{ingame}
    <h2>How to play</h2>
    <ol>{how}</ol>
    <h2>Objective</h2>
    <p>{esc(g['objective'])}</p>
  </div>
  <div class="info">
    <h2>Controls</h2>
    <table class="ctl"><tbody>{ctrl}</tbody></table>
    <h2>Features</h2>
    <ul class="bul">{feats}</ul>
    <h2>Mobile</h2>
    <p>{esc(g['mobile'])}</p>
  </div>
</div>

{ad_slot("game")}
<div class="section-head" style="margin-top:30px"><h2>More games you might like</h2></div>
<div class="grid">{rel}</div>
</div>"""
    game_ld = ld({"@context":"https://schema.org","@type":"VideoGame","name":g["title"],"url":SITE+path,"description":g["short"],
        "genre":g["cat"],"applicationCategory":"Game","gamePlatform":"Web Browser","inLanguage":"en",
        "offers":{"@type":"Offer","price":"0","priceCurrency":"USD","availability":"https://schema.org/InStock"}})
    write(f"games/{g['slug']}/index.html", page(f"{g['title']}: Play Free Online | {SITE_NAME}",
        f"{g['short']} How to play, controls and mobile support. Free, no download.", path, body,
        game_ld+breadcrumb_ld(crumbs), noindex=not indexable(g), current="games", og_type="article"))

def consent_sentence():
    if CONSENT_CONFIGURED:
        return "Where the law requires consent for cookies or similar technologies (for example in the European Economic Area, the United Kingdom and Switzerland), a Google-certified consent message asks for it before personalized ads are shown."
    return "Where the law requires consent for cookies or similar technologies (for example in the European Economic Area, the United Kingdom and Switzerland), personalized ads will only be shown once a Google-certified consent message is in place."

def static_page(slug, title, desc, inner, current=""):
    path=f"/{slug}/"; crumbs=[("Home","/"),(title,path)]
    body = crumbs_html(crumbs)+f'<article class="wrap prose"><h1 class="page-title" style="margin-top:26px">{esc(title)}</h1>{inner}</article>'
    write(f"{slug}/index.html", page(f"{title} | {SITE_NAME}", desc, path, body, breadcrumb_ld(crumbs), current=current))

def build_static():
    static_page("about","About Us","Learn what My Games Bay is: a collection of free browser games with clear guides, no downloads and no accounts.",
    f"""<p>My Games Bay is a collection of free games that you play in your web browser. There is nothing to download or install and no account to create. Open a game page, press Play and start.</p>
<h2>What you will find here</h2>
<ul><li>{len(GAMES)} games across five categories: action, arcade, puzzle, multiplayer and strategy.</li>
<li>A page for every game with a short description, step-by-step instructions, the controls for keyboard and touch screens, and whether it works on mobile.</li>
<li>Search and category pages to help you find something to play quickly.</li></ul>
<h2>How the games work</h2>
<p>Each game runs from its own web address. When you press Play on a game page, that game is loaded into the page, and you can also open it in its own tab or in full screen. We describe each game from what its own start screen and instructions show. If something on a game page is wrong or out of date, please tell us.</p>
<h2>Advertising</h2>
<p>My Games Bay is free to use. To cover running costs we may show ads from Google AdSense. Ads are kept away from the game area and the play buttons. See our <a href="/privacy-policy/">Privacy Policy</a> and <a href="/cookie-policy/">Cookie Policy</a> for details.</p>
<h2>Contact</h2>
<p>Questions, bug reports and feedback are welcome. See the <a href="/contact/">Contact page</a>.</p>""", "about")

    static_page("contact","Contact Us","Contact My Games Bay to report a bug, ask a question, send feedback or raise a rights or privacy concern.",
    f"""<p>You can reach My Games Bay by email at {contact_html()}.</p>
<h2>What to write to us about</h2>
<ul><li><strong>A game does not load or has a bug.</strong> Tell us the game name, your device and browser, and what happened.</li>
<li><strong>Feedback or suggestions</strong> for games or for the site.</li>
<li><strong>Copyright or rights concerns.</strong> If you own content that appears on this site and want it reviewed or removed, include the page address and a description of your rights.</li>
<li><strong>Privacy requests.</strong> See the <a href="/privacy-policy/">Privacy Policy</a>.</li></ul>
<p>Please do not send passwords or payment details by email.</p>""", "contact")

    ads_ppl = f"""<h2>Advertising and cookies</h2>
<p>We may show ads served by Google AdSense. Third-party vendors, including Google, use cookies to serve ads based on a user's previous visits to this website or other websites.</p>
<p>Google's use of advertising cookies enables it and its partners to serve ads to you based on your visit to this site and/or other sites on the Internet.</p>
<p>You can opt out of personalized advertising by visiting <a href="https://adssettings.google.com" rel="noopener">Google Ads Settings</a>. You can also opt out of some third-party vendors' use of cookies for personalized advertising at <a href="https://www.aboutads.info" rel="noopener">aboutads.info</a>. To learn how Google uses data from sites that use its services, see <a href="https://policies.google.com/technologies/partner-sites" rel="noopener">How Google uses information from sites or apps that use our services</a>.</p>
<p>{consent_sentence()}</p>"""
    static_page("privacy-policy","Privacy Policy","How My Games Bay handles information, cookies and advertising, including Google AdSense.",
    f"""<p class="updated">Last updated: {UPDATED_HUMAN}</p>
<p>This policy explains what information is handled when you visit My Games Bay ({SITE}). We aim to collect as little as possible.</p>
<h2>Information we collect</h2>
<p>My Games Bay has no accounts, no sign-up and no forms that collect personal details. We do not ask for your name, email address or payment information.</p>
<p>Like most websites, our hosting provider (Vercel) processes technical data such as IP address, browser type and pages requested in server logs, in order to deliver the site and keep it secure. This site does not currently use an analytics tool. If we add one, we will update this policy.</p>
<h2>Games and third-party addresses</h2>
<p>Each game runs from its own web address. When you load a game, your browser connects to that address, and the game may store data in your browser (for example a best score) using local storage or similar technology. That data stays on your device unless the game says otherwise. Multiplayer games that connect players directly (peer-to-peer) may share connection details such as an IP address with the other player.</p>
{ads_ppl}
<h2>Children</h2>
<p>My Games Bay is a general-audience website and is not directed to children under 13. We do not knowingly collect personal information from children.</p>
<h2>Your choices</h2>
<ul><li>You can block or delete cookies and site data in your browser settings.</li><li>You can manage personalized advertising with the links above.</li><li>You can email us to ask a question about this policy.</li></ul>
<h2>Changes to this policy</h2>
<p>We may update this policy. The date at the top shows when it was last changed.</p>
<h2>Contact</h2>
<p>Privacy questions: {contact_html()}. See also the <a href="/contact/">Contact page</a>.</p>""")

    static_page("terms","Terms & Conditions","The terms for using My Games Bay, including use of games, third-party content, advertising and limits of liability.",
    f"""<p class="updated">Last updated: {UPDATED_HUMAN}</p>
<p>By using My Games Bay you agree to these terms. If you do not agree, please do not use the site.</p>
<h2>Use of the site</h2>
<p>The site and its games are free to use for personal, non-commercial entertainment. Please do not misuse the site: do not try to disrupt it, attack it, scrape it at a harmful rate, or use it to break the law.</p>
<h2>Games and content</h2>
<p>Games are loaded from their own web addresses and are provided as they are. We may add, change or remove games at any time. Names, logos and other content belong to their respective owners. If you believe something on this site infringes your rights, please contact us so we can review it.</p>
<h2>Advertising</h2>
<p>We may display ads, including Google AdSense ads. Advertisers are responsible for their own ads and websites. Please do not click ads for any reason other than genuine interest.</p>
<h2>No warranty</h2>
<p>We do our best to keep the site running but we do not promise that it or any game will always be available, error-free or suitable for your device. Use of the site is at your own risk.</p>
<h2>Limitation of liability</h2>
<p>To the extent allowed by law, My Games Bay is not liable for any loss or damage arising from your use of the site or its games, or from third-party sites linked or loaded from it.</p>
<h2>Changes</h2>
<p>We may update these terms. Continuing to use the site after a change means you accept the updated terms.</p>
<h2>Contact</h2>
<p>Questions about these terms: {contact_html()}.</p>""")

    static_page("disclaimer","Disclaimer","Disclaimer for My Games Bay: games are provided as-is, third-party content, advertising and external links.",
    f"""<p class="updated">Last updated: {UPDATED_HUMAN}</p>
<h2>General</h2>
<p>The information and games on My Games Bay are provided for entertainment. We try to keep game descriptions accurate, but games can change without notice, so a description may occasionally differ from what you see in the game.</p>
<h2>Games and external addresses</h2>
<p>Each game loads from its own web address. We are not responsible for changes to, or the availability of, those addresses. Prediction and strategy games on this site use points or lives only. None of them involves real money, betting or financial advice.</p>
<h2>Advertising</h2>
<p>Ads shown on the site are provided by third parties such as Google AdSense. We do not control which ads are shown and an ad is not an endorsement of the advertised product.</p>
<h2>Health note</h2>
<p>Some games have fast-moving or flashing visuals. Take regular breaks, and stop playing if you feel unwell.</p>
<h2>Contact</h2>
<p>If you spot a problem, please <a href="/contact/">contact us</a> or email {contact_html()}.</p>""")

    static_page("cookie-policy","Cookie Policy","How My Games Bay and its advertising partners use cookies and similar technologies, and how to control them.",
    f"""<p class="updated">Last updated: {UPDATED_HUMAN}</p>
<h2>What are cookies?</h2>
<p>Cookies are small files stored on your device by a website. Similar technologies, such as local storage, work in a comparable way.</p>
<h2>How My Games Bay uses them</h2>
<ul><li><strong>Our own pages</strong> do not set cookies or use analytics.</li>
<li><strong>Games</strong> may keep small pieces of data in your browser, such as a best score or saved progress.</li>
<li><strong>Advertising.</strong> If ads are shown, Google and its partners may set or read cookies to show and measure ads, and to personalize them if you allow it.</li></ul>
<p>{consent_sentence()}</p>
<h2>Controlling cookies</h2>
<ul><li>Use your browser settings to block or delete cookies and site data.</li>
<li>Manage personalized ads at <a href="https://adssettings.google.com" rel="noopener">Google Ads Settings</a> or <a href="https://www.aboutads.info" rel="noopener">aboutads.info</a>.</li>
<li>Read <a href="https://policies.google.com/technologies/cookies" rel="noopener">how Google uses cookies</a>.</li></ul>
<p>Blocking some cookies can affect features such as saved scores. For more, see our <a href="/privacy-policy/">Privacy Policy</a>.</p>""")

def build_404():
    body = """<section class="wrap" style="padding:80px 0;text-align:center">
<h1 class="page-title" style="margin:0 auto 14px">Page not found</h1>
<p style="color:var(--muted);margin-bottom:26px">That page does not exist or has moved. Try the game library or go home.</p>
<p style="display:flex;gap:12px;justify-content:center;flex-wrap:wrap"><a class="btn btn-primary" href="/games/">Browse all games</a> <a class="btn btn-ghost" href="/">Home</a></p>
<h2 style="font-size:18px;margin:34px 0 12px">Categories</h2>
<p style="display:flex;gap:10px;justify-content:center;flex-wrap:wrap">"""+"".join(f'<a class="chip" href="/category/{slug_cat(c)}/">{c}</a>' for c in CATS)+"""</p></section>"""
    write("404.html", page(f"Page Not Found | {SITE_NAME}","The page you are looking for could not be found.","/404.html",body,noindex=True).replace(f'<link rel="canonical" href="{SITE}/404.html">',''))

def build_root_files():
    urls = ["/","/games/"]+[f"/category/{slug_cat(c)}/" for c in CATS]+["/about/","/contact/","/privacy-policy/","/terms/","/disclaimer/","/cookie-policy/"]+[f"/games/{g['slug']}/" for g in GAMES if indexable(g)]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"  <url><loc>{SITE}{u}</loc><lastmod>{TODAY}</lastmod></url>\n" for u in urls) + "</urlset>\n"
    write("sitemap.xml", sm)
    write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")
    if ADS_ON:
        write("ads.txt", f"google.com, {PUB}, DIRECT, f08c47fec0942fa0\n")
    write("assets/style.css", CSS); write("assets/app.js", JS)
    vj = {"cleanUrls":True,"trailingSlash":True,
      "redirects":[{"source":"/index.html","destination":"/","permanent":True}],
      "headers":[
        {"source":"/(.*)","headers":[
          {"key":"X-Content-Type-Options","value":"nosniff"},
          {"key":"Referrer-Policy","value":"strict-origin-when-cross-origin"},
          {"key":"X-Frame-Options","value":"SAMEORIGIN"},
          {"key":"Permissions-Policy","value":"camera=(), microphone=(), geolocation=(), payment=()"}]},
        {"source":"/assets/(.*)","headers":[{"key":"Cache-Control","value":"public, max-age=86400, stale-while-revalidate=604800"}]}]}
    write("vercel.json", json.dumps(vj, indent=2))
    # social image
    from PIL import Image, ImageDraw, ImageFont
    im = Image.new("RGB",(1200,630),(7,11,20)); d = ImageDraw.Draw(im)
    for x in range(0,1200,42): d.line([(x,0),(x,630)],fill=(16,21,32))
    for y in range(0,630,42): d.line([(0,y),(1200,y)],fill=(16,21,32))
    def font(sz):
        for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf","/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"]:
            if os.path.exists(p): return ImageFont.truetype(p,sz)
        return ImageFont.load_default()
    d.ellipse([90,150,120,180],fill=(0,240,255))
    d.text((140,120),"MY GAMES",font=font(96),fill=(234,242,255)); 
    d.text((140,230),"BAY",font=font(96),fill=(0,240,255))
    d.text((140,380),"Free browser games. No download. No sign-up.",font=font(40),fill=(154,171,199))
    d.rectangle([140,470,560,478],fill=(255,46,230))
    im.save(os.path.join(DIST,"og-cover.png"),optimize=True)

def main():
    if os.path.exists(DIST): shutil.rmtree(DIST)
    os.makedirs(DIST)
    build_home(); build_games_index(); build_categories()
    for g in GAMES: build_game(g)
    build_static(); build_404(); build_root_files()
    n = sum(len(f) for _,_,f in os.walk(DIST))
    print(f"Built {n} files into {DIST}")
    print("AdSense:", "ENABLED (" + PUB + ")" if ADS_ON else "disabled (no ADSENSE_PUBLISHER_ID)", "| ads.txt:", "written" if ADS_ON else "not written", "| slots set:", [k for k,v in ADSENSE_SLOTS.items() if v] or "none")
    if ADS_ON and not CONSENT_CONFIGURED:
        print("WARNING: AdSense is enabled but CONSENT_CONFIGURED is False. Publish a Privacy & messaging message before ads serve to EEA/UK visitors.")
    if not CONTACT_EMAIL:
        print("WARNING: CONTACT_EMAIL is empty. Set it in build.py before deploying (Contact/Privacy pages show a placeholder).")

if __name__=="__main__": main()

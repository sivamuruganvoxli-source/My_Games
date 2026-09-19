"""Validation for dist/. Exit code 1 on any error."""
import os,re,sys,json,collections
from html.parser import HTMLParser
sys.path.insert(0,'.')
from games_data import GAMES, CATEGORIES
import build
D='dist'; SITE=build.SITE; errs=[]; warns=[]
class P(HTMLParser):
    def __init__(s):
        super().__init__(); s.links=[]; s.h1=0; s.title=''; s._t=False; s.desc=None; s.canon=None; s.robots=None
        s.ld=[]; s._ld=False; s._buf=''; s.headings=[]; s.text=[]; s.scripts=[]; s.iframes=0; s.ids=set()
    def handle_starttag(s,t,a):
        a=dict(a)
        if 'id' in a: s.ids.add(a['id'])
        if t=='a' and 'href' in a: s.links.append(a['href'])
        if t=='h1': s.h1+=1
        if t in('h1','h2'): s.headings.append(t)
        if t=='title': s._t=True
        if t=='iframe': s.iframes+=1
        if t=='script':
            s.scripts.append(a.get('src','inline'))
            s._ld = a.get('type')=='application/ld+json'; s._buf=''
        if t=='meta' and a.get('name')=='description': s.desc=a.get('content')
        if t=='meta' and a.get('name')=='robots': s.robots=a.get('content')
        if t=='link' and a.get('rel')=='canonical': s.canon=a.get('href')
    def handle_data(s,d):
        if s._t: s.title+=d
        if s._ld: s._buf+=d
        s.text.append(d)
    def handle_endtag(s,t):
        if t=='title': s._t=False
        if t=='script' and s._ld:
            s.ld.append(s._buf); s._ld=False
pages={}; raw={}
for r,_,fs in os.walk(D):
    for f in fs:
        if f.endswith('.html'):
            p=os.path.join(r,f); u='/'+os.path.relpath(p,D).replace('\\','/')
            u=u[:-10] if u.endswith('/index.html') else u
            if u=='': u='/'
            if u.endswith('index.html'): u='/'
            x=P(); src=open(p,encoding='utf-8').read(); x.feed(src); pages[u]=x; raw[u]=src
if '/' not in pages: pages['/']=pages.get('')
def is_idx(u): return u!='/404.html' and 'noindex' not in (pages[u].robots or '')
expected_noindex={'/404.html'}|{f'/games/{g["slug"]}/' for g in GAMES if not build.indexable(g)}
# ---- per page
for u,x in pages.items():
    src=raw[u]
    for bad in ('monetag','quge5','popunder'):
        if bad in src.lower(): errs.append(('forbidden script',u,bad))
    if not build.ADS_ON and ('adsbygoogle' in src or 'googlesyndication' in src): errs.append(('AdSense present while disabled',u))
    if x.h1!=1: errs.append(('H1 count',u,x.h1))
    if not x.title.strip(): errs.append(('no title',u))
    if not x.desc: errs.append(('no description',u))
    elif not 50<=len(x.desc)<=170: warns.append(('description length',u,len(x.desc)))
    if u!='/404.html':
        exp=SITE+u
        if x.canon!=exp: errs.append(('canonical',u,x.canon))
    noidx=not is_idx(u)
    if noidx and u not in expected_noindex: errs.append(('ACCIDENTAL noindex',u))
    if not noidx and u in expected_noindex: errs.append(('expected noindex missing',u))
    for j in x.ld:
        try: json.loads(j)
        except Exception as e: errs.append(('bad JSON-LD',u,str(e)))
    # footer trust links on every page
    need=['/about/','/contact/','/privacy-policy/','/terms/','/disclaimer/','/cookie-policy/','/games/','/']
    for n in need:
        if n not in x.links: errs.append(('missing footer/nav link',u,n))
def exists(l):
    l=l.split('#')[0].split('?')[0]
    if not l: return True
    fp=os.path.join(D,l.lstrip('/'))
    return os.path.isfile(fp) or os.path.isfile(os.path.join(fp,'index.html'))
for u,x in pages.items():
    for l in x.links:
        if l.startswith(('http','mailto:')): continue
        if not exists(l): errs.append(('broken link',u,l))
        lp=l.split('#')[0]
        if l.startswith('/') and lp not in ('','/') and not lp.endswith('/') and '.' not in lp.split('/')[-1]: errs.append(('no trailing slash',u,l))
        if l.split('#')[0]!='' and l.split('#')[0] not in pages and not l.startswith('/assets'): warns.append(('link target not a page',u,l))
# dup titles/descs among indexable pages
for name,attr in (('title','title'),('description','desc')):
    c=collections.Counter((getattr(x,attr) or '').strip() for u,x in pages.items() if u!='/404.html')
    errs+=[('duplicate '+name,v[:60]) for v,n in c.items() if n>1]
# removed game
if os.path.exists(D+'/games/prediction-gray'): errs.append(('prediction-gray page still exists',))
for u,x in pages.items():
    if 'prediction-gray' in raw[u]: errs.append(('prediction-gray referenced',u))
# ---- game pages
abouts=collections.Counter()
for g in GAMES:
    u=f'/games/{g["slug"]}/'; x=pages.get(u)
    if not x: errs.append(('game page missing',u)); continue
    t=' '.join(x.text)
    for sec in ('About ','How to play','Objective','Controls','Features','Mobile','More games you might like'):
        if sec not in t: errs.append(('game section missing',u,sec))
    if g['title'] not in t: errs.append(('title missing',u))
    if x.iframes: errs.append(('iframe present before click',u))
    if 'id="load-game"' not in raw[u] or 'Open in new tab' not in raw[u] or 'id="fs-btn"' not in raw[u]: errs.append(('game controls missing',u))
    if f'data-src="{g["url"]}"' not in raw[u]: errs.append(('game url mismatch',u))
    if 'rel="noopener"' not in raw[u]: errs.append(('new-tab link missing noopener',u))
    if len(t.split())<230: warns.append(('short game page',u,len(t.split())))
    abouts[g['about']]+=1
    if build.indexable(g):
        rel=[l for l in x.links if l.startswith('/games/') and l not in(u,'/games/')]
        if len(rel)<3: errs.append(('too few related links',u,len(rel)))
        for l in rel:
            s=l.strip('/').split('/')[-1]
            gg=next((q for q in GAMES if q['slug']==s),None)
            if gg is None or not build.indexable(gg): errs.append(('related link to non-indexable game',u,l))
errs+=[('duplicate about text',a[:50]) for a,n in abouts.items() if n>1]
# ---- robots / sitemap
rb=open(D+'/robots.txt').read()
if rb!=f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n": errs.append(('robots.txt content',rb))
sm=open(D+'/sitemap.xml').read(); locs=re.findall(r'<loc>(.*?)</loc>',sm)
if len(locs)!=len(set(locs)): errs.append(('duplicate sitemap urls',))
idx={SITE+u for u in pages if is_idx(u)}
if set(locs)!=idx: errs.append(('sitemap != indexable pages',sorted(set(locs)^idx)))
for l in locs:
    if not l.startswith(SITE+'/') or not l.endswith('/'): errs.append(('bad sitemap url',l))
# ---- 404
n=raw['/404.html']
for need in ('href="/"','href="/games/"'):
    if need not in n: errs.append(('404 missing link',need))
for c in CATEGORIES:
    if f'/category/{c.lower()}/' not in n: errs.append(('404 missing category',c))
# ---- contact email
mail=[u for u in ('/contact/','/privacy-policy/','/terms/','/disclaimer/') if 'mailto:' not in raw[u]]
if mail: warns.append(('CONTACT EMAIL NOT CONFIGURED: no mailto link on',mail))
print('pages',len(pages),'| indexable (sitemap)',len(locs),'| noindex',sorted(expected_noindex))
print('WARNINGS',warns or 'none'); print('ERRORS',errs or 'none')
sys.exit(1 if errs else 0)

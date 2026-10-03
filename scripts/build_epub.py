#!/usr/bin/env python3
"""Build CORVUS.epub (EPUB 3 + NCX) from source/chapters/*.md with the chosen cover."""
import glob, re, os, uuid, zipfile, datetime, html, sys
from xml.etree import ElementTree as ET

ROOT='source'; OUT=sys.argv[1] if len(sys.argv)>1 else 'source/CORVUS_Book_One.epub'
COVER=sys.argv[2] if len(sys.argv)>2 else 'source/cover/var_01_michroma.png'
TITLE='CORVUS'; AUTHOR='Pseudonim'; SERIES='Corvus Saga'; SUBTITLE='A Sci-Fi Progression Novel'
BOOK_ID='urn:uuid:'+str(uuid.uuid5(uuid.NAMESPACE_URL,'corvus-saga-book-one'))
MOD=datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

def smart(s):
    out=[]; prev=' '
    for ch in s:
        if ch=='"':
            out.append('“' if prev in ' \n(‘[—' else '”')
        elif ch=="'":
            out.append('‘' if prev in ' \n(“[' else '’')
        else: out.append(ch)
        prev=ch
    return ''.join(out)

def esc(s): return html.escape(smart(s), quote=False)

def block_html(block):
    lines=block.split('\n')
    if lines[0].startswith('>'):
        paras=[]; cur=[]
        for l in lines:
            t=re.sub(r'^>\s?','',l)
            if t.strip()=='' :
                if cur: paras.append(cur); cur=[]
            else: cur.append(t)
        if cur: paras.append(cur)
        inner=''.join('<p>'+'<br/>'.join(esc(x) for x in p)+'</p>' for p in paras)
        return f'<blockquote class="letter">{inner}</blockquote>'
    if re.fullmatch(r'-{3,}', lines[0].strip()):
        return '<hr class="scene"/>'
    letters=[c for c in block if c.isalpha()]
    up=sum(c.isupper() for c in letters)/max(1,len(letters))
    if len(lines)==1:
        return f'<p>{esc(lines[0])}</p>'
    # multi-line: a line opening with a quote starts a new paragraph; otherwise keep the line breaks
    paras=[]; cur=[]
    for l in lines:
        if l.startswith('"') and cur: paras.append(cur); cur=[l]
        else: cur.append(l)
    paras.append(cur)
    cls=' class="log"' if up>0.6 else ' class="lines"'
    return ''.join(f'<p{cls}>'+'<br/>'.join(esc(x) for x in p)+'</p>' if len(p)>1 else f'<p>{esc(p[0])}</p>' for p in paras)

def chapter_xhtml(num, heading, body_blocks):
    m=re.match(r'^(Chapter \d+|Interlude [IVX]+|Epilogue)\s*[—-]\s*(.+)$', heading)
    label,title=(m.group(1),m.group(2)) if m else ('',heading)
    body=''.join(block_html(b) for b in body_blocks)
    return label,title,f'''<?xml version="1.0" encoding="utf-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="en" lang="en">
<head><meta charset="utf-8"/><title>{esc(heading)}</title><link rel="stylesheet" type="text/css" href="style.css"/></head>
<body><section epub:type="chapter" id="ch{num:02d}">
<header class="chap"><p class="label">{esc(label)}</p><h1>{esc(title)}</h1><p class="mark">&#9670;</p></header>
{body}
</section></body></html>'''

# ---- read chapters ----
files=sorted(glob.glob(f'{ROOT}/chapters/ch*.md'), key=lambda f:int(re.search(r'ch(\d+)',f).group(1)))
chapters=[]
for f in files:
    n=int(re.search(r'ch(\d+)',f).group(1))
    text=open(f).read().strip()
    blocks=[b.strip() for b in text.split('\n\n') if b.strip()]
    heading=blocks[0].lstrip('#').strip() if blocks[0].startswith('#') else f'Chapter {n}'
    body=[b for b in blocks[1:] if b!='END OF BOOK ONE']
    if 'END OF BOOK ONE' in text: body.append('END OF BOOK ONE')
    label,title,xhtml=chapter_xhtml(n,heading,body)
    chapters.append(dict(n=n,label=label,title=title,xhtml=xhtml,file=f'ch{n:02d}.xhtml'))

# acts
acts=[('Act I','The Reading',1,10),('Act II','The Bidding',11,33),('Act III','Saturnalia',34,44)]

css='''
@page { margin: 1em; }
body { font-family: Georgia, "Times New Roman", serif; line-height: 1.5; margin: 0; padding: 0 0.6em; }
p { margin: 0; text-indent: 1.3em; text-align: justify; }
header.chap + p, hr.scene + p, blockquote + p, p.log + p, p.lines + p { text-indent: 0; }
header.chap { text-align: center; margin: 3em 0 2.2em 0; }
header.chap .label { text-indent: 0; text-align: center; font-size: 0.8em; letter-spacing: 0.35em; text-transform: uppercase; color: #8a6a1f; margin-bottom: 0.4em; }
header.chap h1 { font-size: 1.7em; font-weight: normal; letter-spacing: 0.08em; margin: 0; }
header.chap .mark { text-indent: 0; text-align: center; color: #b8902a; font-size: 0.7em; margin-top: 0.8em; }
hr.scene { border: 0; text-align: center; margin: 1.6em auto; width: 30%; height: 1px; background: #b8902a; }
p.log { font-family: "Courier New", Courier, monospace; font-size: 0.82em; line-height: 1.45; text-indent: 0; text-align: left; margin: 1em 0 1em 1.3em; letter-spacing: 0.02em; }
p.lines { text-indent: 0; margin: 0.6em 0; }
blockquote.letter { margin: 1.2em 1.6em; font-style: italic; }
blockquote.letter p { text-indent: 0; margin-bottom: 0.7em; }
p.end { text-indent: 0; text-align: center; letter-spacing: 0.35em; margin-top: 3em; color: #8a6a1f; font-size: 0.85em; }
.titlepage { text-align: center; margin-top: 18%; }
.titlepage .series { letter-spacing: 0.4em; font-size: 0.8em; text-transform: uppercase; color: #8a6a1f; }
.titlepage h1 { font-size: 3em; letter-spacing: 0.3em; font-weight: normal; margin: 0.4em 0 0.2em 0; }
.titlepage .sub { letter-spacing: 0.3em; font-size: 0.85em; text-transform: uppercase; margin-bottom: 3em; }
.titlepage .author { letter-spacing: 0.35em; font-size: 1.1em; text-transform: uppercase; }
.titlepage svg { width: 60%; max-width: 420px; height: auto; margin: 1.5em auto; display: block; }
.part { text-align: center; margin-top: 35%; }
.part .label { letter-spacing: 0.4em; text-transform: uppercase; color: #8a6a1f; font-size: 0.9em; }
.part h1 { font-size: 2em; font-weight: normal; letter-spacing: 0.15em; margin: 0.4em 0; }
.cover { text-align: center; margin: 0; padding: 0; }
.cover img { max-width: 100%; max-height: 100%; }
.colophon { font-size: 0.85em; margin-top: 30%; text-align: center; }
.colophon p { text-indent: 0; margin-bottom: 0.6em; }
nav ol { list-style: none; padding-left: 0; } nav li { margin: 0.35em 0; } nav ol ol { padding-left: 1.4em; }
'''

# the ten-stroke mark as static SVG (gold, no filters) for the title page
mark_svg='''<svg xmlns="http://www.w3.org/2000/svg" viewBox="120 500 1360 960"><g fill="none" stroke="#b8902a" stroke-linecap="square" stroke-linejoin="miter">
<polygon points="758,834 800,780 860,786 950,844 860,880 788,886" stroke-width="12"/><polyline points="800,886 800,998" stroke-width="12"/>
<polyline points="844,1000 1440,556" stroke-width="14"/><polyline points="756,1000 160,556" stroke-width="14"/>
<polyline points="912,1092 1304,800" stroke-width="9"/><polyline points="688,1092 296,800" stroke-width="9"/>
<polyline points="758,1004 800,1300" stroke-width="12"/><polyline points="842,1004 800,1300" stroke-width="12"/>
<polyline points="800,1300 736,1396" stroke-width="12"/><polyline points="800,1300 864,1396" stroke-width="12"/></g></svg>'''

def page(title, body, extra_head=''):
    return f'''<?xml version="1.0" encoding="utf-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="en" lang="en">
<head><meta charset="utf-8"/><title>{esc(title)}</title><link rel="stylesheet" type="text/css" href="style.css"/>{extra_head}</head>
<body>{body}</body></html>'''

cover_x=page('Cover','<section epub:type="cover" class="cover"><img src="images/cover.png" alt="CORVUS"/></section>')
title_x=page('Title page',f'<section epub:type="titlepage" class="titlepage"><p class="series">{SERIES} · Book One</p>{mark_svg}<h1>{TITLE}</h1><p class="sub">{SUBTITLE}</p><p class="author">{AUTHOR}</p></section>')
colophon_x=page('Copyright',f'<section epub:type="copyright-page" class="colophon"><p>{TITLE}<br/>{SERIES}, Book One</p><p>Copyright © {datetime.date.today().year} {AUTHOR}. All rights reserved.</p><p>This is a work of fiction. Names, characters, places and incidents are products of the author’s imagination or are used fictitiously.</p><p>First edition.</p></section>')
parts=[]
for i,(lab,name,a,b) in enumerate(acts,1):
    parts.append(dict(file=f'part{i}.xhtml',xhtml=page(lab,f'<section epub:type="part" class="part"><p class="label">{lab}</p><h1>{name}</h1></section>'),label=lab,name=name,a=a,b=b))

# nav
def chap_entry(c):
    t=(c['label']+'. ' if c['label'] else '')+c['title']
    return f'<li><a href="{c["file"]}">{esc(t)}</a></li>'
nav_items=''
for p in parts:
    inner=''.join(chap_entry(c) for c in chapters if p['a']<=c['n']<=p['b'])
    nav_items+=f'<li><a href="{p["file"]}">{p["label"]} · {p["name"]}</a><ol>{inner}</ol></li>'
nav_x=f'''<?xml version="1.0" encoding="utf-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="en" lang="en">
<head><meta charset="utf-8"/><title>Contents</title><link rel="stylesheet" type="text/css" href="style.css"/></head>
<body><nav epub:type="toc" id="toc"><h1>Contents</h1><ol>
<li><a href="title.xhtml">Title page</a></li>{nav_items}</ol></nav>
<nav epub:type="landmarks" hidden="hidden"><ol><li><a epub:type="cover" href="cover.xhtml">Cover</a></li><li><a epub:type="toc" href="nav.xhtml">Table of contents</a></li><li><a epub:type="bodymatter" href="part1.xhtml">Start of content</a></li></ol></nav>
</body></html>'''

# NCX (EPUB 2 readers)
def ncx_point(id_,label,src,order,children=''):
    return f'<navPoint id="{id_}" playOrder="{order}"><navLabel><text>{esc(label)}</text></navLabel><content src="{src}"/>{children}</navPoint>'
order=[1]; pts=''
def nxt(): order[0]+=1; return order[0]
pts+=ncx_point('np-title','Title page','title.xhtml',1)
for p in parts:
    o=nxt(); kids=''
    for c in chapters:
        if p['a']<=c['n']<=p['b']:
            kids+=ncx_point(f'np-{c["file"]}',(c['label']+'. ' if c['label'] else '')+c['title'],c['file'],nxt())
    pts+=ncx_point(f'np-{p["file"]}',p['label']+' · '+p['name'],p['file'],o,kids)
ncx=f'''<?xml version="1.0" encoding="utf-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1"><head><meta name="dtb:uid" content="{BOOK_ID}"/><meta name="dtb:depth" content="2"/><meta name="dtb:totalPageCount" content="0"/><meta name="dtb:maxPageNumber" content="0"/></head>
<docTitle><text>{TITLE}</text></docTitle><navMap>{pts}</navMap></ncx>'''

# OPF
manifest=['<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>',
          '<item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>',
          '<item id="css" href="style.css" media-type="text/css"/>',
          '<item id="cover-image" href="images/cover.png" media-type="image/png" properties="cover-image"/>',
          '<item id="cover" href="cover.xhtml" media-type="application/xhtml+xml"/>',
          '<item id="title" href="title.xhtml" media-type="application/xhtml+xml" properties="svg"/>',
          '<item id="colophon" href="colophon.xhtml" media-type="application/xhtml+xml"/>']
spine=['<itemref idref="cover" linear="no"/>','<itemref idref="title"/>','<itemref idref="colophon"/>','<itemref idref="nav"/>']
for p in parts:
    pid=p['file'].replace('.xhtml','')
    manifest.append(f'<item id="{pid}" href="{p["file"]}" media-type="application/xhtml+xml"/>')
    spine.append(f'<itemref idref="{pid}"/>')
    for c in chapters:
        if p['a']<=c['n']<=p['b']:
            cid=c['file'].replace('.xhtml','')
            manifest.append(f'<item id="{cid}" href="{c["file"]}" media-type="application/xhtml+xml"/>')
            spine.append(f'<itemref idref="{cid}"/>')
opf=f'''<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookid" xml:lang="en">
<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
<dc:identifier id="bookid">{BOOK_ID}</dc:identifier>
<dc:title id="t1">{TITLE}</dc:title><meta refines="#t1" property="title-type">main</meta>
<dc:title id="t2">{SUBTITLE}</dc:title><meta refines="#t2" property="title-type">subtitle</meta>
<dc:creator id="creator">{AUTHOR}</dc:creator><meta refines="#creator" property="role" scheme="marc:relators">aut</meta>
<dc:language>en</dc:language>
<dc:description>{SERIES}, Book One. An interplanetary Rome that never fell; a baker’s son from Ceres rated Null by the census; a bracelet that lies low.</dc:description>
<meta property="belongs-to-collection" id="series">{SERIES}</meta><meta refines="#series" property="collection-type">series</meta><meta refines="#series" property="group-position">1</meta>
<meta name="cover" content="cover-image"/>
<meta property="dcterms:modified">{MOD}</meta>
</metadata>
<manifest>{''.join(manifest)}</manifest>
<spine toc="ncx">{''.join(spine)}</spine>
</package>'''
container='''<?xml version="1.0" encoding="utf-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles></container>'''

# ---- write ----
files_out={'OEBPS/content.opf':opf,'OEBPS/nav.xhtml':nav_x,'OEBPS/toc.ncx':ncx,'OEBPS/style.css':css,'OEBPS/cover.xhtml':cover_x,'OEBPS/title.xhtml':title_x,'OEBPS/colophon.xhtml':colophon_x}
for p in parts: files_out['OEBPS/'+p['file']]=p['xhtml']
for c in chapters: files_out['OEBPS/'+c['file']]=c['xhtml']
# well-formedness check
bad=[]
for k,v in files_out.items():
    if k.endswith(('.xhtml','.opf','.ncx')):
        try: ET.fromstring(v.encode('utf-8'))
        except ET.ParseError as e: bad.append((k,str(e)))
if bad: print('XML ERRORS', bad); sys.exit(1)
with zipfile.ZipFile(OUT,'w') as z:
    z.writestr(zipfile.ZipInfo('mimetype'),'application/epub+zip',compress_type=zipfile.ZIP_STORED)
    z.writestr('META-INF/container.xml',container,compress_type=zipfile.ZIP_DEFLATED)
    for k,v in files_out.items(): z.writestr(k,v,compress_type=zipfile.ZIP_DEFLATED)
    z.write(COVER,'OEBPS/images/cover.png',compress_type=zipfile.ZIP_STORED)
words=sum(len(re.sub(r'<[^>]+>',' ',c['xhtml']).split()) for c in chapters)
print('wrote',OUT,'chapters',len(chapters),'approx words',words,'size',os.path.getsize(OUT))

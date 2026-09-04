#!/usr/bin/env python3
"""Build an EPUB 3 of the novel from source/chapter_NN.md. Usage: _build_epub.py OUT.epub"""
import glob, html, re, sys, uuid, zipfile, datetime

TITLE = "Damnatio"
SUBTITLE = "Sertorius, Book One"
AUTHOR = "Carlos Montojo"
LANG = "en"
PARTS = [(1, "Part I", "The Fang"), (9, "Part II", "The Forms"),
         (25, "Part III", "The Trimmer"), (35, "Part IV", "The Name")]

CSS = """
body { font-family: Georgia, "Times New Roman", serif; line-height: 1.5; margin: 0 4%; }
h1 { font-size: 1.5em; text-align: center; margin: 2.5em 0 1.5em; font-weight: normal; }
h1 .num { display: block; font-size: 0.7em; letter-spacing: 0.15em; text-transform: uppercase; color: #666; margin-bottom: 0.6em; }
h2.part { font-size: 2em; text-align: center; margin-top: 35%; font-weight: normal; }
h2.part .num { display: block; font-size: 0.5em; letter-spacing: 0.2em; text-transform: uppercase; color: #666; margin-bottom: 1em; }
p { margin: 0; text-indent: 1.4em; text-align: justify; }
p.first, h1 + p, hr + p, pre + p { text-indent: 0; }
hr.scene { border: 0; text-align: center; margin: 1.6em 0; }
hr.scene:after { content: "\\2022  \\2022  \\2022"; color: #666; letter-spacing: 0.3em; }
pre.reading { font-family: "Courier New", monospace; font-size: 0.85em; margin: 1.2em 1.5em; white-space: pre-wrap; }
.titlepage { text-align: center; margin-top: 30%; }
.titlepage h1 { font-size: 2.6em; margin: 0; }
.titlepage p { text-indent: 0; text-align: center; color: #444; }
p.end { text-align: center; text-indent: 0; margin-top: 3em; letter-spacing: 0.2em; }
"""

def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", s)
    return s

def md_to_xhtml(text):
    lines = text.split("\n")
    out = []
    title = ""
    i = 0
    para = []
    def flush():
        nonlocal para
        if para:
            out.append("<p>%s</p>" % inline(" ".join(para)))
            para = []
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("# "):
            flush(); title = ln[2:].strip(); i += 1; continue
        if ln.strip() == "---":
            flush(); out.append('<hr class="scene"/>'); i += 1; continue
        if ln.startswith("    ") and ln.strip():
            flush(); block = []
            while i < len(lines) and (lines[i].startswith("    ") or (lines[i].strip() == "" and i + 1 < len(lines) and lines[i + 1].startswith("    "))):
                block.append(lines[i][4:] if lines[i].startswith("    ") else ""); i += 1
            out.append('<pre class="reading">%s</pre>' % html.escape("\n".join(block)))
            continue
        if ln.strip() == "":
            flush(); i += 1; continue
        if ln.strip() == "END OF BOOK ONE":
            flush(); out.append('<p class="end">END OF BOOK ONE</p>'); i += 1; continue
        para.append(ln.strip()); i += 1
    flush()
    return title, "\n".join(out)

def xhtml(body, head_title):
    return ('<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE html>\n'
            '<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="%s">\n'
            '<head><meta charset="utf-8"/><title>%s</title><link rel="stylesheet" type="text/css" href="style.css"/></head>\n'
            '<body>\n%s\n</body>\n</html>\n' % (LANG, html.escape(head_title), body))

def main(out):
    files = sorted(glob.glob("source/chapter_*.md"))
    chapters = []
    for f in files:
        n = int(re.search(r"chapter_(\d+)", f).group(1))
        t, body = md_to_xhtml(open(f, encoding="utf-8").read())
        m = re.match(r"Chapter (\d+): (.*)", t)
        ctitle = m.group(2) if m else t
        chapters.append((n, ctitle, body))
    uid = "urn:uuid:" + str(uuid.uuid5(uuid.NAMESPACE_URL, "supernarrative/damnatio/book1"))
    now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    manifest, spine, navpoints, toc_nav = [], [], [], []
    docs = {}
    # title page
    docs["title.xhtml"] = xhtml('<div class="titlepage"><h1>%s</h1><p>%s</p><p>%s</p></div>' % (TITLE, SUBTITLE, AUTHOR), TITLE)
    manifest.append('<item id="title" href="title.xhtml" media-type="application/xhtml+xml"/>'); spine.append('<itemref idref="title"/>')
    parts = {p[0]: p for p in PARTS}
    play = 1
    for n, ctitle, body in chapters:
        if n in parts:
            _, pnum, pname = parts[n]
            pid = "part%d" % n
            docs[pid + ".xhtml"] = xhtml('<h2 class="part"><span class="num">%s</span>%s</h2>' % (pnum, pname), pname)
            manifest.append('<item id="%s" href="%s.xhtml" media-type="application/xhtml+xml"/>' % (pid, pid)); spine.append('<itemref idref="%s"/>' % pid)
            toc_nav.append('<li><a href="%s.xhtml">%s: %s</a><ol>' % (pid, pnum, html.escape(pname)))
            navpoints.append('<navPoint id="np%d" playOrder="%d"><navLabel><text>%s: %s</text></navLabel><content src="%s.xhtml"/>' % (play, play, pnum, html.escape(pname), pid)); play += 1
        cid = "ch%02d" % n
        head = '<h1><span class="num">Chapter %d</span>%s</h1>' % (n, inline(ctitle))
        docs[cid + ".xhtml"] = xhtml(head + "\n" + body, "Chapter %d: %s" % (n, ctitle))
        manifest.append('<item id="%s" href="%s.xhtml" media-type="application/xhtml+xml"/>' % (cid, cid)); spine.append('<itemref idref="%s"/>' % cid)
        toc_nav.append('<li><a href="%s.xhtml">%d. %s</a></li>' % (cid, n, html.escape(ctitle)))
        navpoints.append('<navPoint id="np%d" playOrder="%d"><navLabel><text>%d. %s</text></navLabel><content src="%s.xhtml"/></navPoint>' % (play, play, n, html.escape(ctitle), cid)); play += 1
        nxt = [p for p in PARTS if p[0] > n]
        if (nxt and nxt[0][0] == n + 1) or n == chapters[-1][0]:
            toc_nav.append("</ol></li>"); navpoints.append("</navPoint>")
    nav = ('<nav epub:type="toc" id="toc"><h1>Contents</h1><ol>%s</ol></nav>' % "\n".join(toc_nav))
    docs["nav.xhtml"] = xhtml(nav, "Contents")
    manifest.append('<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>')
    manifest.append('<item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>')
    manifest.append('<item id="css" href="style.css" media-type="text/css"/>')
    opf = ('<?xml version="1.0" encoding="utf-8"?>\n<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid">\n'
           '<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">\n<dc:identifier id="uid">%s</dc:identifier>\n<dc:title>%s</dc:title>\n'
           '<dc:creator>%s</dc:creator>\n<dc:language>%s</dc:language>\n<meta property="dcterms:modified">%s</meta>\n</metadata>\n'
           '<manifest>\n%s\n</manifest>\n<spine toc="ncx">\n%s\n</spine>\n</package>\n' % (uid, TITLE, AUTHOR, LANG, now, "\n".join(manifest), "\n".join(spine)))
    ncx = ('<?xml version="1.0" encoding="utf-8"?>\n<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">\n'
           '<head><meta name="dtb:uid" content="%s"/></head>\n<docTitle><text>%s</text></docTitle>\n<navMap>\n%s\n</navMap>\n</ncx>\n' % (uid, TITLE, "\n".join(navpoints)))
    container = ('<?xml version="1.0" encoding="utf-8"?>\n<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">\n'
                 '<rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles>\n</container>\n')
    with zipfile.ZipFile(out, "w") as z:
        z.writestr(zipfile.ZipInfo("mimetype"), "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        z.writestr("META-INF/container.xml", container, compress_type=zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/content.opf", opf, compress_type=zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/toc.ncx", ncx, compress_type=zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/style.css", CSS, compress_type=zipfile.ZIP_DEFLATED)
        for name, content in docs.items():
            z.writestr("OEBPS/" + name, content, compress_type=zipfile.ZIP_DEFLATED)
    print("wrote", out, "chapters:", len(chapters))

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "source/Damnatio_Book1.epub")

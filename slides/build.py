#!/usr/bin/env python3 -B
# vim: set et sw=2 ts=2 sts=2 :
# build.py: slides/*.html -> slides/out/*.html, ready to screenshot.
#   <pre class="awk" data-src="bundle/gawk/nb.awk" [data-lines="1-23"]></pre>
#     inlines that file, syntax-coloured, so a slide cannot drift from the
#     code it shows.  class is awk|make|out|txt.
#   <tag data-raw="slides/fig/x.svg"></tag> inlines a file verbatim.
# Also adds prev/next nav (parked below the 1080px fold, so the screenshot
# clips it) and writes an index page.
# usage: python3 slides/build.py   (or: make slides)
import html, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT, OUT = os.path.dirname(HERE), HERE + "/out"
EG = r"slide[0-9][a-z]?\.html"
COLS = ["", "a", "b", "b", "d", "d", "d", "b", "pd", ""]   # `make nb` columns
KW = ("BEGIN|END|function|if|else|while|for|do|return|next|nextfile|break|"
      "continue|delete|exit|print|printf|getline|split|length|log|exp|int|"
      "sqrt|rand|srand|tolower|toupper|gsub|gensub|sub|match|sprintf|substr|"
      "index|close|system")

AWK = re.compile(r"(?P<com>#[^\n]*)|(?P<str>\"(?:[^\"\\\n]|\\.)*\")"
                 r"|(?P<re>(?<=[~(,])\s*/(?:[^/\n\\]|\\.)*/)"
                 r"|(?P<kw>\b(?:" + KW + r")\b)"
                 r"|(?P<num>\b\d+(?:\.\d+)?(?:[eE][-+]?\d+)?\b)")
MAKE = re.compile(r"(?P<doc>##[^\n]*)|(?P<com>#[^\n]*)"
                  r"|(?P<str>'(?:[^'\n]|\\.)*'|\"(?:[^\"\n]|\\.)*\")"
                  r"|(?P<var>^[A-Za-z_]\w*(?=\s*[:?+]?=))"
                  r"|(?P<tgt>^[a-z][\w-]*(?=:))"
                  r"|(?P<call>\$\$?[({][^(){}\n]*[)}]|\$\$[A-Za-z_]\w*)"
                  r"|(?P<kw>\b(?:case|esac|in|then|else|fi|do|done)\b)"
                  r"|(?P<num>\b\d+(?:\.\d+)?\b)", re.M)
PY = re.compile(r"(?P<com>#[^\n]*)"
                r"|(?P<str>\"\"\"(?:[^\"]|\"(?!\"\"))*\"\"\""
                r"|\"(?:[^\"\\\n]|\\.)*\"|'(?:[^'\\\n]|\\.)*')"
                r"|(?P<kw>\b(?:def|return|for|in|if|elif|else|while|not|and"
                r"|or|lambda|import|from|with|as|yield|break|continue|None"
                r"|True|False|class|global|try|except|is|pass)\b)"
                r"|(?P<num>\b\d+(?:\.\d+)?(?:[eE][-+]?\d+)?\b)")
PRE = re.compile(r"<pre([^>]*)></pre>")
RAW = re.compile(r'<(\w+)([^>]*\bdata-raw="([^"]*)"[^>]*)></\1>')
OUTB = re.compile(r'(<pre class="out">)(.*?)(</pre>)', re.S)
ATTR = re.compile(r'(\w[\w-]*)="([^"]*)"')
TITLE = re.compile(r"<title>(.*?)</title>", re.S)

def esc(s): return html.escape(s)

def paint(pat, s):  # wrap every token in a span, escape everything else
  out, at = [], 0
  for m in pat.finditer(s):
    out += [esc(s[at:m.start()]), f'<span class="{m.lastgroup}">{esc(m[0])}</span>']
    at = m.end()
  return "".join(out) + esc(s[at:])

def cols(s):  # colour a comma-separated report, one colour per column
  out = []
  for line in s.split("\n"):
    at, buf = 0, []
    for cell in re.split(r"(,)", line):
      if cell == ",": buf, at = buf + [","], at + 1
      else:
        k = COLS[at] if at < len(COLS) else ""
        buf += [f'<span class="{k}">{esc(cell)}</span>' if k else esc(cell)]
    out += ["".join(buf)]
  return "\n".join(out)

PAINT = dict(awk=lambda s: paint(AWK, s), make=lambda s: paint(MAKE, s),
             py=lambda s: paint(PY, s), out=cols, txt=esc)

def src(a):  # the data-src file, sliced by an optional data-lines="a-b"
  s = open(f"{ROOT}/{a['data-src']}").read().rstrip("\n")
  if "data-lines" in a:
    i, _, j = a["data-lines"].partition("-")
    s = "\n".join(s.split("\n")[int(i) - 1:int(j)])
  return s

def fill(p):
  def pre(m):
    a = dict(ATTR.findall(m[1]))
    if "data-src" not in a: return m[0]
    return f"<pre{m[1]}>{PAINT[a.get('class','txt').split()[0]](src(a))}</pre>"
  p = OUTB.sub(lambda m: m[1] + cols(html.unescape(m[2])) + m[3], p)
  return RAW.sub(lambda m: f"<{m[1]}{m[2]}>{open(ROOT+'/'+m[3]).read()}</{m[1]}>",
                 PRE.sub(pre, p))

NAV = """
<nav class="nav">
  <a href="{prev}" title="previous">&larr;</a>
  <a href="index.html" title="all slides">{at} / {of}</a>
  <a href="{next}" title="next">&rarr;</a>
  <span>&larr; &rarr; keys work too</span>
</nav>
<script>
document.addEventListener("keydown", function (e) {{
  if (e.key === "ArrowLeft")  location.href = "{prev}";
  if (e.key === "ArrowRight") location.href = "{next}";
  if (e.key === "Escape")     location.href = "index.html";
}});
</script>
"""
CARD = ('  <a href="{0}.html"><img src="../../{0}.png" alt="{1}">'
        '<b>{1}</b><span>{0}</span></a>')
INDEX = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>tinyai slides</title>
<link rel="stylesheet" href="../style.css">
<style>
  body {{ width: auto; height: auto; padding: 40px 56px 60px; }}
  .deck {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 26px; }}
  .deck a {{ text-decoration: none; color: inherit; display: block; }}
  .deck img {{ width: 100%; border: 1px solid var(--rule); border-radius: 8px;
               display: block; background: #fff; }}
  .deck b {{ display: block; font-size: 17px; margin-top: 9px; }}
  .deck span {{ font-size: 15px; color: var(--muted); }}
</style></head>
<body>
<h1>tinyai slides</h1>
<p class="sub">{n} slides &middot; edit slides/*.html, then <code>make slides</code></p>
<div class="deck">
{cards}
</div>
</body></html>
"""

def main():
  os.makedirs(OUT, exist_ok=True)
  eg = sorted(f for f in os.listdir(HERE) if re.fullmatch(EG, f))
  if not eg: sys.exit("no slide*.html in " + HERE)
  for f in sorted(set(os.listdir(OUT)) - set(eg) - {"index.html"}):
    if f.endswith(".html"): os.remove(f"{OUT}/{f}"); print("dropped out/" + f)
  cards, n = [], len(eg)
  for i, f in enumerate(eg):
    p = fill(open(f"{HERE}/{f}").read())
    p = p.replace("</body>", NAV.format(prev=eg[i - 1], next=eg[(i + 1) % n],
                                        at=i + 1, of=n) + "</body>")
    open(f"{OUT}/{f}", "w").write(p)
    m = TITLE.search(p)
    cards += [CARD.format(f[:-5], m[1].strip() if m else f[:-5])]
    print("out/" + f)
  open(f"{OUT}/index.html", "w").write(INDEX.format(n=n, cards="\n".join(cards)))
  print("out/index.html")

main()

local l={}
l.head=[[
<a href="http://not2much.github.io/se4ai">
  <img alt="🗂️ home" src="https://img.shields.io/badge/home-eeeeee?style=flat"></a>
<a href="/src/">
  <img alt="🗂️ src" src="https://img.shields.io/badge/src-bbbbbb?style=flat"></a>
<a href="https://github.com/not2much/se4ai/fork">
  <img alt="🔱 fork" src="https://img.shields.io/badge/fork-888888?style=flat&amp;logo=github&amp;logoColor=white"></a>
<a href="#">
  <img alt="© 2025" src="https://img.shields.io/badge/© 2025-666666?style=flat"></a><br>

<a href="/docs/rules.md">
  <img alt="🧭 rules" src="https://img.shields.io/badge/guide-ff6f6f?style=flat"></a>
<a href="/docs/egs.md">
  <img alt="📂 egs" src="https://img.shields.io/badge/egs-ff9999?style=flat"></a>
<a href="/docs/motives.md">
  <img alt="💡 why" src="https://img.shields.io/badge/motivation-ffcccc?style=flat"></a>&nbsp;&nbsp;
<a href="/docs/sh.md">
  <img alt="🐚 sh" src="https://img.shields.io/badge/sh-f1c40f?style=flat"></a>
<a href="/docs/python.md">
  <img alt="🐍 python" src="https://img.shields.io/badge/python-f39c12?style=flat"></a>
<a href="/docs/se.md">
  <img alt="🛠 se" src="https://img.shields.io/badge/se-e67e22?style=flat"></a>&nbsp;&nbsp;
<a href="/docs/maths.md">
  <img alt="📐 math" src="https://img.shields.io/badge/maths-7fdb7f?style=flat"></a>
<a href="/docs/a.md">
  <img alt="🧠 ai" src="https://img.shields.io/badge/ai-2ecc71?style=flat"></a>
<a href="/docs/apps.md">
  <img alt="📦 apps" src="https://img.shields.io/badge/apps-27ae60?style=flat"></a>&nbsp;&nbsp;
]]

l.fmt = string.format
function l.tag(t,s) return l.fmt("<%s>%s</%s>",t,s,t) end
function l.slurp(x) local f=assert(io.open(x,"rb"));local s=f:read"*a";f:close();return s end

-- 256-code → hex (same hues you picked)
l.hex = { [75]="#268bd2",[140]="#af87d7",[174]="#ff6e64",
              [180]="#b58900",[81]="#2aa198",[108]="#859900" }

l.R,l.k = "",{               -- no ANSI now
  def=75,class=75,lambda=75,
  ["if"]=140,["elif"]=140,["else"]=140,["for"]=140,["while"]=140,
  ["break"]=140,continue=140,["return"]=140,pass=140,
  try=174,except=174,finally=174,raise=174,assert=174,
  True=180,False=180,None=180,
  ["and"]=81,["or"]=81,["not"]=81,is=81,["in"]=81,
  import=108,from=108,with=108,yield=108,
  global=108,nonlocal=108,del=108 }

function l.esc(s)  -- & < >
  return (s:gsub("&","&amp;"):gsub("<","&lt;"):gsub(">","&gt;")) end

function l.pylite(src)     -- HTML highlighter
  src=l.esc(src)
  return src:gsub("(%f[%w_][%a_][%w_]*)%f[%W_]",function(w)
    local c=l.k[w];return c and
      ('<span style="color:'..l.hex[c]..'">'..w..'</span>') or w end) end

function l.code(path)      -- emit <pre> block
  print( l.tag("tiny",l.tag("pre", l.pylite( l.slurp(path))))) end

function l.p(s)  print("<p>"  .. s .. "</p>") end
function l.h1(s) print("<h1>" .. s .. "</h1>") end
function l.h2(s) print("<h2>" .. s .. "</h2>") end
-- demo
--code("../src/adds.py")

return l

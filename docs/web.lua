local l={}

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

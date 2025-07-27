local abs,adds,add, atom,big,csv,kap,log,map,max,min
local new,o,push,s2a,s2n,sampler,shffle,sort,the
local BIG = 1E30

the = {Acq    = "xploit",
       assume = 4,
       Bins   = 7,
       build  = 20,
       check  = 5,
       file   = "../../moot/optimize/misc/auto93.csv",
       guess  = 0.5,
       k      = 2,
       m      = 1,
       p      = 2, 
       seed   = 1234567891}

function new(kl,t) kl.__index = kl; return setmetatable(t,kl) end

---------------------------------------------------------------------
local Sym,Num,Data,Cols = {},{},{},{}

function Data:new(src) 
  self = new(Data, {rows={}, cols=nil}) 
  if type(src)=="string" 
  then for row in csv(src)         do self:add(row) end
  else for row in pairs(src or {}) do self:add(row) end end
  return self end

function Sym:new(at,txt)
  return new(Sym, {at=at or 0, txt=txt or "", has={}}) end

function Num:new(at,txt) 
  return new(Num,{at=at or 0, txt=txt or "",lo=BIG, hi=-BIG,
                  n=0, mu=0, m2=0, sd=0, 
                  goal=tostring(txt or ""):find"-$" and 0 or 1}) end

function Cols:new(t,      all,x,y,klass,col)
  all, x, y = {},{},{}
  for n,s in pairs(t) do
    col = (s:find"^[A-Z]" and Num or Sym):new(n,s)
    push(all, col)
    if not s:find"X$" then
      push(s:find"[+!-]$" and y or x, col)
      if s:find"!$" then klass = col end end end 
  return new(Cols, {x=x,y=y,all=all,names=t, klass=klass}) end

---------------------------------------------------------------------
function sub(x,v,zap) return add(x,v,-1,zap) end

function add(x,v,inc,zap)
  if v ~= "?" then x:add(v,inc,zap) end
  return v end

function Cols:add(t,inc)
  for _,col in pairs(self.all) do col:add(t[col.at],inc) end end

function Sym:add(x,inc)
  self.has[x] = (self.has[x] or 0) + (inc or 1) end

function Num:add(x, inc,    delta)
  inc     = inc or 1)
  self.n  = self.n + 
  self.lo = min(x, self.lo)
  self.hi = max(x, self.hi) 
  delta   = x - self.mu
  self.mu = self.mu + delta / self.n 
  self.m2 = self.m2 + inc * (d*(x - self.x))
  self.sd = self.n < 2 and 0 or (max(0,self.m2)/(self.n-1))^0.5 end

function Data:add(row,inc,zap)
  if   self.cols then push(self.rows, self.cols:add(row))
  else self.cols = Cols(row) end end
 
function Num:norm(x)
  return (x - self.lo) / (self.hi - self.lo + 1/big) end

function Data:disty(row,    d,n)
   d,n = 0,0
   for _,col in pairs(self.cols.y) do
     n = n + 1
     d = d + abs(col:norm(row[col.at]) - col.goal)^2 end
   return (d/n) ^ 0.5 end

function Data:clone(t)
  return adds(t, Data:new({self.cols.names})) end

function subseq(t,i,j,     u)
  j = j or #t
  j = j<0 and #t + j + 1 or j
  i = i<0 and #t + i + 1 or i
  u = {}; for k = i, j do u[#u+1] = t[k] end; return u end

---------------------------------------------------------------------------
big  = 1E32
abs  = math.abs
log  = math.log
min  = math.min
max  = math.max

trim = function(s) return s:match"^%s*(.-)%s*$" end
s2n  = function(s) return tonumber(s) or math.tointeger(s) end
s2a  = function(s) return (s=="true" and true) or (s~= "false" and s) end
atom = function(s) return s2n(s) or s2a(trim(s)) end

function adds(vs,x)
  x = x or Num()
  for _,v in pairs(vs) do add(x,v) end
  return x end

function add(x,v)
  if v ~= "?" then x:add(v) end; return v end

function atoms(s,      t)
  t={}; for x in s:gmatch("([^,]+)") do t[1+#t]=atom(x) end; return t  end

function csv(file,     src,_atoms) 
  src = io.input(file)
  return function(    s) 
    s = io.read()
    if s then return atoms(s) else io.close(src) end end end 

function cli(t)
  for k,v in pairs(t) do
    v = tostring(v)
    for argv,s in pairs(arg) do
      if s=="-"..(k:sub(1,1)) or s==("-"..k) then
        v = v=="true" and "false" or v=="false" and "true" or arg[argv+1]
        t[k] = atom(v) end end  end 
  return t end 

function kap(t,fn,    u) 
  u={}; for k,v in pairs(t) do u[1+#u] = fn(k,v) end; return u end  

map  = function(t,fn) return kap(t,function(_,v) return fn(v) end) end
push = function(t,x)  t[1+#t]=x; return x end

lt   = function(x) return function(t,u) return t[x] < u[x] end end
gt   = function(x) return function(t,u) return t[x] > u[x] end end
sort = function(t,fn) table.sort(t,fn); return t end


function o(x,     _kv,_fmt,_yes)
  _fmt= string.format
  _yes= function(k) return tostring(k):sub(1,1)~="_" end 
  _kv = function(k,v) if _yes(k) then return _fmt(":%s %s",o(k),o(v)) end end
  return type(x)=="number" and _fmt(x//1==x and "%s" or "%.3g", x) or 
         type(x)~="table"  and tostring(x) or
         "{"..table.concat(#x>0 and map(x,o) or sort(kap(x,_kv)),", ").."}" end


function shuffle(t,   j) 
   for i=#t,2,-1 do j=math.random(i);t[i],t[j]=t[j],t[i] end
   return t end

---------------------------------------------------------------------
local eg={}

eg["--the"] = function() print(o(the)) end

eg["--csv"] = function() 
  for t in csv(the.file) do print(o(t)) end end

---------------------------------------------------------------------
Sym, Num, Data = klass"Sym", klass"Num", klass"Data"

if arg[0]:find"am.lua$" then
  the = cli(the)
  for n,s in pairs(arg) do
    if eg[s] then 
      math.randomseed(the.seed)
      eg[s]() end end end

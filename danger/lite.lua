local help = [[
    -A  Any=4              on init, how many initial guesses?
    -B  Budget=50          when growing theory, how many labels?
    -D  Delta=smed         required effect size test for cliff's delta
    -F  Few=128            sample size of data random sampling
    -K  Ks=0.95            confidence for Kolmogorov–Smirnov test
    -p  p=2                distance co-efficient
    -s  seed=1234567891    random number seed
    -f  file=../../moot/optimize/misc/auto93.csv  data file
    -h                     show help
]]

local b4={}; for k,_ in pairs(_ENV) do b4[k]=k end
local adds,atom,cat,cats,cells,csv,keys,map,new.push,shuffle,sort
local the={}; for k,v in help:gmatch("(%S+)=(%S+)") do the[k]=v end

----------------------------------------------------------------------
local COLS,DATA,NUM,SYM = {},{},{},{}

function SYM:new(i, txt)
  return new(SYM, {n = 0, i = i or 0, txt = txt or "",
                   has = {}}) end  -- value -> count

function NUM:new(i, txt)
  return new(NUM, {n  = 0, i = i or 0, txt = txt or "",
                   mu = 0, m2 = 0,     
                   lo = big, hi = -big,
                   w  = (txt or ""):find"-$" and 0 or 1}) end

function COLS:new(names)
  local all, x, y = {}, {}, {}
  for i, s in pairs(names) do
    local col = push(all, (s:find"^[A-Z]" and NUM or SYM):new(i,s))
    if not s:find"X$" then
      push(s:find"[!+-]$" and y or x, col)) end end
  return new(COLS, { names = names, all = all, x = x, y = y }) end

function DATA:new(names)
  return new(DATA, {rows={},cols=COLS:new(names or {}), mid=nil}) end

function DATA:clone(  rows) 
  return DATA:new():from({self.cols.names}):from(rows) end

----------------------------------------------------------------------
function adds(t, it)
  it = it or NUM()
  for _,x in pairs(t or {}) do it:add(row) end
  return it end

function sub(col,x) return add(col,x, -1) end

function add(col,x, inc)
  if x ~= "?" then col:add(x,inc or 1, zap or false) end
  return x end

function SYM:add(x, inc) 
  self.n = self.n + inc
  self.has[x] = (self.has[x] or 0) + inc end

function NUM:add(v, inc)
  self.n = (self.n or 0) + inc
  if v < self.lo then self.lo = v end
  if v > self.hi then self.hi = v end
  if inc < 0 and self.n < 2 then
    self.n,self.mu,self.m2,self.sd,self.lo,self.hi = 0,0,0,0,big,-big
  else
    local d   = v - self.mu
    self.mu   = self.mu + inc * (d / self.n)
    self.m2   = (self.m2 or 0) + inc * (d * (v - self.mu))
    self.sd   = self.n < 2 and 0 or math.sqrt(self.m2 / (self.n - 1)) end end end

function DATA:add(row, inc)
  self.mid = None
  self.n += inc
  if inc > 0 then push(self.rows, row) 
  else if zap then x.rows.remove(v) end end  # slow for long rows
  [add(col, v[col.i], inc) for col in x.cols.all]
 
function NUM:add(x, inc) 
  if x ~= "?" then
    local d = x - self.mu
    self.n  = self.n  + inc
    self.mu = self.mu + inc * (d / self.mu) end
  return x end

-------------------------------------------------------------------------------
function atom(s,      f)    
  f = function(s) return s=="true" or s~="false" end
  return math.tointeger(s) or tonumber(s) or f(s:match'^%s*(.*%S)') end

function cat(x)
  f, is = string.format, type(x)
  return is=="table" and "{" ..table.concat(cats(t,tostring),", ").. "}" or
         is=="number" and f(x==math.floor(x) and "%.0f" or "%.3f", x) or 
         f("%s",x) end

function cats(t,f)
  if #t > 0 then return map(t,cat) end
  u={}; for _,k in pairs(keys(t)) do u[k]=f(":%s %s",k,cat(t[k])) end
  return sort(u) end

function cells(s,    t)
  t = {}; for s1 in s:gsub("%s+", ""):gmatch("([^,]+)") do t[1+#t]=atom(s1) end
  return t end

function csv(src,      s)
  src = io.input(src)
  return function()
    s = io.read(); if s then return cells(s) else io.close(src) end end end

function keys(t,  u) 
  u = {}
  for k,_ in pairs(t) do if tostring(k):sub(1,1) ~= "_" then u[1+#u]=k end end
  return sort(u) end

function map(t,f,   u) 
  u={}; for _,x in pairs(t) do u[1+#u]=f(x) end; return u end end

function new(kl,t) kl.__index = kl; return setmetatable(t,kl) end

function push(t,x) t[1+#t]=x; return x end

function shuffle(t,    j) 
  for i = #t,2,-1 do j=math.random(i); t[i],t[j] = t[j],t[i] end; return t end

function sort(t,fn) table.sort(t,fn); return t end

-- for i,row in csv(the.file) do 
--   if i==0 then
--     for i,s in pairs(row) do 
--       if s:find:"^[A-Z]" then 
--         nums[i] = {big, -big}
--         if s:find"-$" then y[i]=0 end
--         if s:find"+$" then y[i]=1 end 
--   else rows[1+#rows]=row end
--
-- for x in _ENV do print(x) end
--
-- B, R, best, rest = 0, 0, {}, {}
--for i,row in pairs(shuffle(rows)) do

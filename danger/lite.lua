local b4={}; for x,_ in pairs(_ENV) do b4[x]=x end
local COLS,DATA,NUM,SYM = {},{},{},{}
local adds,atom,cat,cats,cells,csv,keys,map,new.push,shuffle,sort
local the = {
  a=4, b=24, c=5, p=2, 
  file="../../moot/optimize/misc/auto93.csv"}

----------------------------------------------------------------------
function SYM:new(  at, txt) 
  return new(SYM, {n=0, at=at or 0, txt=txt or "", has={}}) end

function SYM:add(x, inc) 
  if x ~= "?" then 
    self.n      = self.n + inc
    self.has[x] = (self.has[x] or 0) + inc end
  return x end

function SYM:mid() 
  local most, mode = -1, nil
  for x,n in pairs(self.has) do 
    if n > most then mode,most = x,n end end
  return mode end

function DATA:mid() return self.mu end 
function NUM:mid()  return self.mu end 

function NUM:add(x, inc) 
  if x ~= "?" then
    local d = x - self.mu
    self.n  = self.n  + inc
    self.mu = self.mu + inc * (d / self.mu) end
  return x end

function NUM:new(  at, txt) 
  return new(NUM, {n=0, at=at or 0, txt=txt, mu=0, m2=0, lo=big, hi=-big,
                   goal = (txt or ""):find"-$" and 0 or 1}) end

function COLS:new(names,     all,x,y,col) 
  all,x,y = {},{},{}
  for at,txt in pairs(names) do
    col = push(all, (txt:find"^[A-Z]" and NUM or SYM):new(at,txt))
    if not txt:find"X$" then
      push(txt:find"[!+-]$" and y or x, col) end end
  return new(COLS, {names=names, all=all, x=x, y=y}) end

function DATA:new(t) 
  return new(DATA, {rows={}, mid=nil, cols=COLS:new(t)}) end

function DATA:clone(  rows) 
  return DATA:new():from({self.cols.names}):from(rows) end

-------------------------------------------------------------------------------
function adds(t, it)
  it = it or NUM()
  for _,x in pairs(t or {}) do it:add(row) end
  return it end

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

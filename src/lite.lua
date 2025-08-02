local the = {a=4, b=24, c=5, p=2, file="../../moot/optimize/misc/auto93.csv"}

local COLS,DATA,NUM,SYM = {},{},{},{}

local adds, cells, new,atom,map,cat,shuffle,csv,push

----------------------------------------------------------------------
function SYM:new(  at, txt) 
  return l.new(SYM, {n=0, at=at or 0, txt=txt or "", has={}}) end

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

function Data:mid() return self.mu end 
function Num:mid() return self.mu end 

function NUM:add(x, inc) 
  if x ~= "?" then
    local d = x - self.mu
    self.n  = self.n  + inc
    self.mu = self.mu + inc * (d / self.mu) 
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
  return l.new(DATA, {rows={}, mid=nil, cols=COLS:new(t)}) end

function DATA:clone(  rows) 
  return DATA:new():from({self.cols.names}):from(rows) end

function adds(t, it)
  it = it or NUM()
  for _,x in pairs(t or {}) do self:add(row) end
  return it end

function cells(s,    t)
  t={}; for s1 in s:gsub("%s+", ""):gmatch("([^,]+)") do t[1+#t]=atom(s1) end
  return t end

function new(kl,t)  kl.__index = kl; return setmetatable(t,kl) end
function atom(s)    return math.tointeger(s) or tonumber(s) or s:match'^%s*(.*%S)' end
function map(t,fn)  local u={}; for _,x in ipairs(t) do u[1+#u]=fn(x) end; return u end
function cat(t)     return "{" .. table.concat(map(t,tostring),", ") .. "}" end

function shuffle(t,    j) 
  for i = #t,2,-1 do j=math.random(i); t[i],t[j] = t[j],t[i] end; return t end

function csv(src,      s,i)
  i, src = -1, io.input(src)
  return function()
    s = io.read(); if s then i=i+1; return i,cells(s) else io.close(src) end end end

function push(t,x) t[1+#t]=x; return x end


for i,row in csv(the.file) do 
  if i==0 then
    for i,s in pairs(row) do 
      if s:find:"^[A-Z]" then 
        nums[i] = {big, -big}
        if s:find"-$" then y[i]=0 end
        if s:find"+$" then y[i]=1 end 
  else rows[1+#rows]=row end

B, R, best, rest = 0, 0, {}, {}
for i,row in pairs(shuffle(rows)) do

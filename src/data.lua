local l=require"lib"
local maths=require"maths"
local the,help=l.settings[[
rulr2.lua : a small range learner
(c) 2024, Tim Menzies, timm@ieee.org, BSD-2 license

Options:
  -r --ranges  max nu,ber of bins = 7
  -b --big     a big number       = 1E30
  -d --dull    too smal to be interesting = 0.05
  -s --seed    random number seed = 1234567891
  -t --train   train data         = auto83.csv ]]

local NUM  = {} -- info on numeric columns
local SYM  = {} -- info on symbolic columns
local DATA = {} -- place to store all the columns 
local COLS = {} -- factory to make NUMs and SYMs
local RANGE= {} -- stores ranges

-----------------------------------------------------------------------------------------
function RANGE.new(col,r)
  return l.is(RANGE, { _col=col, has=r,  _score=0}) end

function RANGE:__tostring() return self._col.name .. l.o(self) end

function RANGE:add(x,d)
  self._score = self._score + d  end

function RANGE:score(      s)
  s= self._score/self._col.n; return s < 0 and 0 or s end

-----------------------------------------------------------------------------------------
function NUM.new(name,pos)
  return l.is(NUM, {name=name, pos=pos, n=0,
                   mu=0, m2=0, sd=0, lo=1E30, hi= -1E30,
                   best = (name or ""):find"-$" and 0 or 1}) end

function NUM:norm(x)
  return x=="?" and x or (x - self.lo) / (self.hi - self.lo + 1/the.big) end

function NUM:add(x,     d)
  if x ~= "?" then
    self.n  = 1 + self.n
    self.lo = math.min(x, self.lo)
    self.hi = math.max(x, self.hi)
    self.mu, self.m2, self.sd = maths.welford(self.n, self.mu, self.m2)
  return x end

function NUM:range(x,     area,tmp)
  area = maths.auc(x, self.mu, self/sd)
  tmp = 1 + (area * the.ranges // 1) -- maps x to 0.. the.range+1
  return  math.max(1, math.min(the.ranges, tmp)) end -- keep in bounds

-----------------------------------------------------------------------------------------
function SYM.new(name,pos)
  return l.is(SYM, {name=name, pos=pos, n=0,
                   seen={}, mode=nil, most=0}) end

function SYM:range(x) return x end

function SYM:add(x)
  if x ~= "?" then
    self.n = 1 + self.n
    self.seen[x] = 1 + (self.seen[x] or 0)
    if self.seen[x] > self.most then
      self.most, self.mode = self.seen[x], x end end end

-----------------------------------------------------------------------------------------
function COLS.new(names,     self,col)
  self = l.is(COLS, { all={}, x={}, y={}, names=names })
  for n,s in pairs(names) do self:newColumn(n,s) end
return self end

function COLS:newColumn(n,s,    col)
  col = (s:find"^[A-Z]" and NUM or SYM).new(s,n)
  l.push(self.all,col)
  if not s:find"X$" then
    l.push(s:find"[-+!]$" and self.y or self.x, col) end end

function COLS:add(row,        x)
  for _,cols in pairs{self.x, self.y} do
    for _,col in pairs(cols) do
       x = row[col.pos]
       if x ~= "?" then col:add(row[col.pos]) end end end
  return row end

function COLS:arrange(x,col,d,       r)
  if x ~= "?" then
    r = col:range(x)
    col.ranges    = col.ranges or {}
    col.ranges[r] = col.ranges[r] or RANGE.new(col,r,x)
    col.ranges[r]:add(x,d) end end

-----------------------------------------------------------------------------------------
function DATA.new(src,  names,      cols)
  cols = names and COLS.new(names) or nil
  return l.is(DATA,{rows={},  cols=cols}) end

function DATA:read(file) for   row in l.csv(file) do self:add(row) end; return self end
function DATA:load(lst)  for _,row in pairs(lst)  do self:add(row) end; return self end

function DATA:add(row)
  if   self.cols
  then l.push(self.rows, self.cols:add(row))
  else self.cols = COLS.new(row) end 
  return self end

function DATA:sort(     fun)
  fun = function(row) return chebyshev(row,self.cols.y) end
  self.rows = l.sort(self.rows, function(a,b) return fun(a) < fun(b) end)
  return self end


function DATA:arrages(row,   d)
  d= chebyshev(row,self.cols.y)
  for _,col in pairs(self.cols.x) do self:arrange(row[col.pos],col,d) end end
    
function DATA:ranges(     fun,out)
  out = {}
  fun = function(r) return r:score() end
  for _,col in pairs(self.cols.x) do
    for _,r in pairs(DATA:merge(col.ranges, #(self.rows)/the.ranges, the.dull)) do
       l.push(out,r) end end
  return out end

-----------------------------------------------------------------------------------------
function SYM:mid() return self.mode end
function NUM:mid() return self.mu end

function SYM:div() return l.entropy(self.has) end
function NUM:div() return self.sd end

function DATA:mids(cols)
  return l.map(cols or self.cols.y, function(col) return l.rnd(col:mid()) end) end

-----------------------------------------------------------------------------------------
local l ={}
function l.is(class, object)  -- how we create instances
  class.__index=class; setmetatable(object, class); return object end

l.cat = table.concat
l.fmt = string.format

function l.sort(t,fun,     u) -- return a copy of `t`, sorted using `fun`,
  u={}; for _,v in pairs(t) do u[1+#u]=v end; table.sort(u,fun); return u end

function l.by(x) return function(a,b) return a[x] < b[x] end end

function l.on(fun) return function(a,b) return fun(a) < fun(b) end end

function l.push(t,x) t[1+#t]=x; return x end

function l.map(t,f,     u) u={}; for k,v in pairs(t) do u[1+#u]= f(v)   end; return u end
function l.kap(t,f,     u) u={}; for k,v in pairs(t) do u[1+#u]= f(k,v) end; return u end

function l.csv(src)
  src = src=="-" and io.stdin or io.input(src)
  return function(      s)
    s = io.read()
    if s then return l.cells(s) else io.close(src) end end end

function l.cells(s,    t)
  t={}; for s1 in s:gsub("%s+", ""):gmatch("([^,]+)") do t[1+#t]=l.coerce(s1) end
  return t end

function l.coerce(s,     _other)
  _other = function(s) if s=="nil" then return nil  end
                       return s=="true" or s ~="false" and s or false end
  return math.tointeger(s) or tonumber(s) or _other(s:match'^%s*(.*%S)') end

function l.oo(t) print(l.o(t)); return t end

function l.o(t,    _list,_dict,u)
  if type(t) == "number" then return tostring(l.rnd(t)) end
  if type(t) ~= "table" then return tostring(t) end
  _list = function(_,v) return l.o(v) end
  _dict = function(k,v) if not tostring(k):find"^_" then return l.fmt(":%s %s",k,l.o(v)) end end
  u = l.kap(t, #t==0 and _dict or _list)
  return "{" .. l.cat(#t==0 and l.sort(u) or u ," ") .. "}" end

function l.rnd(n, ndecs)
  if type(n) ~= "number" then return n end
  if math.floor(n) == n  then return math.floor(n) end
  local mult = 10^(ndecs or 2)
  return math.floor(n * mult + 0.5) / mult end

function l.rogues()
  for k,v in pairs(_ENV) do if not b4[k] then print("Rogue?",k,type(v)) end end end



math.randomseed(the.seed)
return {the=the, lib=l,DATA=DATA,SYM=SYM,NUM=NUM,COLS=COLS}

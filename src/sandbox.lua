local l, the, help == {},{}, [[
local help =[[rulr2.lua : a small range learner
(c) 2024, Tim Menzies, timm@ieee.org, BSD-2 license

Options:
  -b --big     a big number                    = 1E30
  -F --far     how far to search for 'far'     = 0.9
  -k --k       low class frequency kludge      = 1
  -m --m       low attribute frequency kludge  = 2
  -s --seed    random number seed              = 1234567891
  -t --train   train data                      = ../data/misc/auto93.csv ]]

local function new(class, object)  -- how we create instances
  class.__index=class; setmetatable(object, class); return object end

function l.as(s,     _other)
  function _other(s) 
    if s=="nil" then return nil  else return s=="true" or s ~="false" and s or false end
  return math.tointeger(s) or tonumber(s) or _other(s:match'^%s*(.*%S)') end

for k,s in help:gmatch("[-][-]([%S]+)[^=]+=[%s]*([%S]+)") do the[k] = l.as(s) end

function lib.csv(src)
  src = src=="-" and io.stdin or io.input(src)
  return function(      s,t)
    x = io.read()
    if x 
    then t={};for x in s:gsub("%s+", ""):gmatch("([^,]+)") do t[1+#t]=l.as(x) end; return t 
    else io.close(src) end end end

function push(t,x) t[1+#t]=x; return x end

local NUM,SYM,DATA={}

local function _col(name,pos) return {name=name,pos=pos,has={}} end
function SYM.new(name,pos)    return isa(SYM, _col(name,pos)) end
function NUM.new(name,pos)    return isa(NUM, _col(name,pos)) end
function COL(name,pos)        return (name:find"^[A-Z]" and NUM or SYM)(name,pos) end 

function NUM:stats(     n) a=self.has; n=#a//10; return a[5*n], (a[9*n] - a[n])/2.56 end
function NUM:lo()          return self.has[1] end
function NUM:hi()          return self.has[#self.has] end

function NUM:sort()     table.sort(self.has) end
function SUM:sort()     end

function SYM:range(x,_,) return x end
function NUM:ranges(x,ranges,   area,cdf,tmp,mu,sd,z)
  cdf   = function(z) return 1 - 0.5*2.718^(-0.717*z - 0.416*z*z) end
  mu,sd = self:stats()
  z     = (x - mu) / sd
  area  = z >= 0 and cdf(z) or 1 - cdf(-z) end
  return  math.max(1, math.min(ranges, 1 + (area * ranges // 1))) end 

function DATA.new()   return new(DATA, {rows={}, cols={names={},x={},y={}}}) end
function DATA:read(f) for   row in csv(f)           do self:add(row) end; return self end
function DATA:load(t) for _,row in pairs(t)         do self:add(row) end; return self end
function DATA:sort()  for _,col in pairs(self.cols) do col:sort() end;    return self end

function DATA:add(row)
  if   #self.cols.names > 0 
  then for i,x in pairs(push(self.rows,row)) do if x ~= "?" then push(cols[i],x) end end 
  else self.cols.names = row
       for pos,name in pairs(names) do 
         col = COL(name,pos)
         push(name:find"[!+-]$" and self.cols.y or self.cols.x, col) end end end
        
function RANGE.new(col,r) return new(RANGE, { _col=col, has={r},  n=0, score=0}) end
function RANGE:add(x,d)  self.n = self.n + 1; self.score = self.score + d  end

-----------------------------------------------------------------------------------------
local function COL(name,pos) 
  name, pos = name or "", pos or 0
  return ((name or ""):find"^[A-Z]" and NUM or SYM).new(name,pos) end

function NUM.new(name,pos)
  return l.is(NUM, {name=name or "", pos=pos or 0, n=0,
                   mu=0, m2=0, sd=0, lo=1E30, hi= -1E30,
                   best = (name or ""):find"-$" and 0 or 1}) end

function SYM.new(name,pos)
  return l.is(SYM, {name=name or "", pos=pos or 0, n=0,
                   seen={}, mode=nil, most=0}) end

-----------------------------------------------------------------------------------------
function NUM:add(x,     d)
  if x ~= "?" then
    self.n  = 1 + self.n
    self.lo = math.min(x, self.lo)
    self.hi = math.max(x, self.hi)
    self.mu, self.m2, self.sd = calc.welford(x, self.n, self.mu, self.m2) end
  return x end

function SYM:add(x)
  if x ~= "?" then
    self.n = 1 + self.n
    self.seen[x] = 1 + (self.seen[x] or 0)
    if self.seen[x] > self.most then
      self.most, self.mode = self.seen[x], x end end end

-----------------------------------------------------------------------------------------
function SYM:mid() return self.mode end
function NUM:mid() return self.mu end

function SYM:div() return calc.entropy(self.seen) end
function NUM:div() return self.sd end

function NUM:norm(x)
  if x=="?" then return x end
  return (x - self.lo) / (self.hi - self.lo + 1E-30) end


local NUM  = ns.NUM  -- info on numeric columns
local SYM  = ns.SYM  -- info on symbolic columns
local DATA = {} -- place to store all the columns 
local COLS = {} -- factory to make NUMs and SYMs

-----------------------------------------------------------------------------------------
function DATA.new(  names,      cols)
  cols = names and COLS.new(names) or nil
  return l.is(DATA,{rows={},  cols=cols}) end

function DATA:read(file) for   row in l.csv(file) do self:add(row) end; return self end
function DATA:load(lst)  for _,row in pairs(lst)  do self:add(row) end; return self end

function DATA:add(row)
  if   self.cols
  then l.push(self.rows, self.cols:add(row))
  else self.cols = COLS.new(row) end 
  return self end

function DATA:mids(cols)
  return l.map(cols or self.cols.y, function(col) return l.rnd(col:mid()) end) end

----------------------------------------------------------------------------------------
function COLS.new(names,     self,col)
  self = l.is(COLS, { all={}, x={}, y={}, names=names })
  for pos,name in pairs(names) do self:newColumn(name,pos) end
return self end

function COLS:newColumn(name,pos,    col)
  col = ns.COL(name,pos)
  l.push(self.all,col)
  if not name:find"X$" then
    l.push(name:find"[-+!]$" and self.y or self.x, col) end end

function COLS:add(row,        x)
  for _,cols in pairs{self.x, self.y} do
    for _,col in pairs(cols) do
       x = row[col.pos]
       if x ~= "?" then col:add(row[col.pos]) end end end
  return row end

-----------------------------------------------------------------------------------------
-- Once we have rows, we can talk likelihood of rows

function DATA:like(row,nall,nh,    prior,x,like,out)
  out, prior = 0, (#self.rows + the.k) / (nall + the.k*nh)
  for _,col in pairs(self.cols.x) do
    x = row[col.pos]
    if x ~= "?" then
      like = col:like(x,prior)
      if like > 0 then out = out + math.log(like) end end end
  return out + math.log(prior) end 

function SYM:like(x, prior)
  return ((self.has[x] or 0) + the.m*prior)/(self.n +the.m) end

function NUM:like(x,_,      nom,denom)
  local mu, sd =  self:mid(), (self:div() + 1E-30)
  nom   = 2.718^(-.5*(x - mu)^2/(sd^2))
  denom = (sd*2.5 + 1E-30)
  return  nom/denom end

-----------------------------------------------------------------------------------------
-- Once we have rows, we can talk distance between rows or rows

function DATA:dist(row1,row2,  cols)
  return calc.minkowski(row1,row2,the.p, cols or self.cols.x) end

function SYM:dist(x,y)
  return  (x=="?" and y=="?" and 1) or (x==y and 0 or 1) end

function NUM:dist(x,y)
  if x=="?" and y=="?" then return 1 end
  x,y = self:norm(x), self:norm(y)
  if x=="?" then x=y<.5 and 1 or 0 end
  if y=="?" then y=x<.5 and 1 or 0 end
  return math.abs(x-y) end

function DATA:neighbors(rowx,  rows, cols,     d)
  d = function(row) return self:dist(row,rowx,cols) end
  return l.sort(rows or self.rows, function(row2,row3) return d(row2) < d(row3) end) end

--------------------------------------------------------------------------------
math.randomseed(the.seed)
return {the=the, lib=l,DATA=DATA,SYM=SYM,NUM=NUM,COLS=COLS}

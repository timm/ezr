#!/usr/bin/env lua
-- <!-- vim:set filetype=lua et : -->
-- See README.md for the  data formats, type hints, and coding conventions used in this code.

local the = require"config"
the.bins=7

-- ## Lib
local abs,log, max, min = math.abs, math.log, math.max, math.min
local l = {}

function l.push(t,x)  --> x
  t[1+#t]=x; return x end

function l.ocat(a,    u) --> array[str]
  u={}; for _,v in pairs(a) do l.push(u,tostring(v)) end; return u end

function l.okat(d,    u) --> array[str]
  u={}
  for k,v in pairs(d) do 
    if not tostring(k):find"^_" then l.push(u,string.format("%s:%s",k,v)) end end
  table.sort(u)
  return u end

function l.o(t)  --> t
  return "("..table.concat(#t==0 and l.okat(t) or l.ocat(t),", ")..")" end

function l.oo(t) --> t
  print(l.o(t)); return t end

function l.coerce(s,    fun) --> number | str | boolean
  if type(s) ~= "string" then return s end
  fun = function(s) return s=="true" or s ~="false" and s end 
  return math.tointeger(s) or tonumber(s) or fun(s:match"^%s*(.-)%s*$") end 

function l.csv(sFile,   n) --> interator
  sFile = sFile=="-" and io.stdin or io.input(sFile)
  n = -1
  return function(      s,t) --> row
    s = io.read()
    if s then 
       n = n + 1
       t={};for x in s:gsub("%s+", ""):gmatch("([^,]+)") do t[1+#t]=l.coerce(x) end
       return n,t 
    else io.close(sFile) end end end 

function l.copy(t,  u)
  if type(t) ~= "table" then return t end
  u={}; for k,v in pairs(t) do u[l.copy(k)] = l.copy(v) end
  return setmetatable(u, getmetatable(t)) end

function l.new(dmeta,d) --> instance ;(a) create 1 instance; (b) enable class polymorphism
  dmeta.__index=dmeta; setmetatable(d,dmeta); return d end

-- ## Structs for storing DATA
local SYM,NUM,COLS,DATA = {},{},{},{}

function SYM:new(s,n) --> sym
  return l.new(SYM,{name=s,pos=n,n=0,has={}}) end

function NUM:new(s,n) --> num
  return l.new(NUM,{name=s,pos=n,n=0,w=0,mu=0,m2=0, lo=the.inf, hi=-the.inf}) end

function COLS:new() --> cols
  return l.new(COLS,{all={}, x={}, y={}, names=""}) end

function DATA:new() --> data
  return l.new(DATA,{rows={}, cols=COLS:new()}) end

-- ## Create
function DATA:read(sFile) --> data
  for n,row in l.csv(sFile) do if n==0 then self:head(row) else self:add(row) end end
  return self end

function DATA:head(row,    col) --> nil
  self.cols.names = row
  for pos,name in pairs(row) do 
    if not name:find"X$" then 
      col = l.push(self.all, (name:find"^[A-Z]" and NUM or SYM):new(name,pos)) 
      if     name:find"-$" then col.w=0; l.push(self.y, col) 
      elseif name:find"+$" then col.w=1; l.push(self.y, col) 
      else   l.push(self.x, col) end end end end

function DATA:clone(  rows,    data)  --> data ; new data has same structure as self
  data = DATA:new():head(self.cols.names) 
  for _,row in pairs(rows or {}) do data:add(row) end 
  return data end

-- ## Update
function DATA:add(row) --> nil
  l.push(self.rows,row)
  for _,col in pairs(self.cols.all) do 
    if row[col.pos]~="?" then col:add(row[col.pos]) end end end 

function SYM:add(x) --> x
  if x ~="?" then self.n=self.n + 1; self.has[x]=(self.has[x] or 0)+1 end; return x end

function SYM:sub(x) --> x
  if x ~="?" then self.n=self.n - 1; self.has[x]=self.has[x] - 1 end; return x end

function NUM:add(n,      d) --> n
  if n ~= "?" then self.n  = self.n + 1
                   d       = n - self.mu
                   self.mu = self.mu + d/self.n
                   self.m2 = self.m2 + d * (n-self.mu)
                   if     n > self.hi then self.hi = n 
                   elseif n < self.lo then self.lo = n end end
  return n end

function NUM:sub(n,     d) --> n
  if n ~= "?" then self.n  = self.n - 1
                   d       = n - self.mu
                   self.mu = self.mu - d/self.n
                   self.m2 = self.m2 - d*(n - self.mu) end
  return n end

-- ## Query
function NUM:mid() --> number
  return self.mu end

function SYM:mid(     most,out) --> x
  most=0; for k,v in pairs(self.has) do if v>most then out,most=k,v end end; return out end

function NUM:div() --> number ; returns standard deviation
  return self.n < 2 and 0 or (self.m2/(self.n - 1))^0.5  end

function SYM:div(   e,N)  --> number ; returns entropy
  N=0; for _,v in pairs(self.has) do N = N + v end
  e=0; for _,v in pairs(self.has) do e = e + v/N*log(v/N,2) end
  return -e end

function NUM:norm(x) --> x | 0..1
  return x=="?" and x or (x-self.lo)/(self.hi-self.lo + 1/the.inf) end

function DATA:sort() --> data ; sorts rows by chebyshev, so left-hand-side rows  are better
  table.sort(self.rows, function(a,b) return self:chebyshev(a) < self:chebyshev(b) end)
  return self end

function DATA:chebyshev(row,     d) --> number ; max distance of any goal to best
  d=0; for _,y in pairs(self.cols.y) do d = max(d,abs(y:norm(row[y.pos]) - y.w)) end
  return d end

function DATA:chebyshevs(rows,    sum,n) --> number ; mean chebyshev
  sum,n=0,0; for _,r in pairs(rows or self.rows) do n=n+1; sum=sum+self:chebyshev(r) end
  return sum/n end
-- ## Discretization
local BIN={}

function BIN:new(s,n,  lo,hi) --> BIN
  return l.new(BIN,{name=s,pos=n, lo=lo or the.inf, hi=hi or lo or the.inf, y=NUM:new(s,n)}) end 

function BIN:add(x,y)
  if x ~= "?" then if x < self.lo then self.lo = x end
                   if x > self.hi then self.hi = x end
                   self.y:add(y) end  end
 
function BIN:sub(x,y) -- assumes removal in ascending order
  if x ~= "?" then self.y:sub(y) 
                   self.lo = x end end

function BIN:__tostring(     lo,hi,s)
  lo,hi,s = self.x.lo, self.x.hi,self.x.name
  if lo == -the.inf then return string.format("%s <= %g", s,hi) end
  if hi ==  the.inf then return string.format("%s > %g",  s,lo) end
  if lo ==  hi  then return string.format("%s == %s", s,lo) end
  return string.format("%g < %s <= %g", lo, s, hi) end

function BIN:selects(rows,     u,lo,hi,x)
  u,lo,hi = {}, self.x.lo, self.y.hi
  for _,row in pairs(rows) do 
    x = row[self.x.pos]
    if x=="?" or lo==hi and lo==x or lo < x and x <= hi then l.push(u,r) end end
  return u end

function SYM:bins(rows,y,     t,x) --> array[bin] ; proposes one split per symbol value
  t = {}
  for row in pairs(rows) do
    x = row[self.pos]
    if x ~= "?" then t[x] = t[x] or BIN:new(self.name,self.pos,x) 
                     t[x]:add(x, y(row)) end end
  return t end

function NUM:bins(rows,y) --> nil | [bin1,bin2] ; proposes a binary split of these numerics
  local left1,right1, left,right,last,y1,tmp,xpect,x,q,got
  function q(x) return x=="?" and -the.inf or x end
  table.sort(rows, function(a,b) return q(a[self.pos]) < q(b[self.pos]) end)
  left  = BIN:new(self.name,self.pos,self.lo)
  right = BIN:new(self.name,self.pos,self.lo,self.hi); right.y=l.copy(self)
  xpect = self:div()
  for i,row in pairs(rows) do
    x  = row[self.pos]
    y1 = y(row)
    if x ~= "?" then got = got or (#rows - i - 1)
                     left:add(x,y1)
                     right:sub(x,y1)
                     if last ~= x and left.n >= got^0.5 and right.n >= got^0.5 then
                       tmp = (left.n*left:div() + right.n*right:div()) / got
                       if tmp < xpect then 
                         xpect,left1,right1 = tmp, l.copy(left), l.copy(right) end end end end
    if left1 then return {left,right} end end

-- ## TREE
local TREE={}

function TREE:new(here,lvl,s,n,lo,hi,mu)
  return l.new(TREE,{lvl=lvl or 0, bin=BIN:new(s,n,lo,hi), 
                     mu=mu or 0, here=here, _kids={}})  end

function TREE:__tostring() 
  return string.format("%.2f\t%5s\t%s%s", self.mu, #self.here.rows, 
                       ("|.. "):rep(self.lvl-1), self.lvl==0 and "" or self.bin) end

function TREE:visit(fun) 
  fun = fun or print
  fun(self)
  for _,kid in pairs(self._kids) do kid:visit(fun) end end 

function DATA:tree(     _grow)
  function _grow(rows,stop,lvl,name,pos,lo,hi,     tree,sub,_grow)
    tree = TREE:new(self:clone(rows), lvl,name,pos,lo,hi,self:chebyshevs(rows))
    for _,bin in pairs(self:bins(rows):spitter().bins) do
      sub = bin:selects(rows)
      if #sub < #rows and #sub > stop then
        l.push(tree._kids, _grow(sub,stop,lvl+1,bin.name,bin.pos,bin.x.lo,bin.x.hi)) end end
    return tree 
  end
  return _grow(self.rows,(#self.rows)^0.5,0) end

function DATA:splitter(      lo,w,n,out,tmp)
  lo = the.inf
  for _,col in pairs(self.cols.x) do
    w,n,tmp,out = 0,0,{},out or col
    for _,bin in pairs(col.bins) do w=w+bin.y.n*bin.y:div(); n=n+bin.y.n; l.push(tmp,bin) end
    if w/n < lo then lo, out = w/n, col end
    table.sort(tmp, function(a,b) return a.y.mu < b.y.mu end)
    col.bins = tmp end 
  return out end  

local function _bestBins(bins,      most,best,n,xpect)
  xpect,n,best = 0,0,nil
  for _,bin in pairs(bins) do 
    best = best or bin
    n    = n   + bin.y.n
    xpect  = xpect + bin.y:div() 
    if bin.y:mid() > most then most,best = bin.y:mid(),bin end end
  best.best=true
  return bins, xpect/n end

-- ## eg
local eg={}
eg["-h"] = function(_) print("lua x2.lua --[aa|bb] [FILE.csv]") end

eg["--train"] = function(train,     d) 
  d=DATA:new():read(train or the.train) 
  l.oo(d.cols.x[2]) end

eg["--sort"] = function(train)
  for i,row in pairs(DATA:new():read(train or the.train):sort().rows) do 
    if i==1 or i%25==0 then print(i, l.o(row)) end end end 

eg["--bins"] = function(train,    d)
  d = DATA:new():read(train or the.train)
  l.oo(d)
  d:bins() end

-- ## Start up
if arg[1]=="x2" then eg[arg[2] or "-h"](l.coerce(arg[3])) end

return {NUM=NUM, SYM=SYM, DATA=DATA, TREE=TREE, BIN=BIN, lib=l}

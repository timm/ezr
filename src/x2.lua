#!/usr/bin/env lua
-- <!-- vim:set filetype=lua et : -->
local the = require"config"
the.bins=7

-- Structs
-- -------
local inf = 1E32
local SYM,NUM,COLS,DATA,BIN,TREE={},{},{},{},{},{}
local function new(dmeta,d) dmeta.__index=dmeta; setmetatable(d,dmeta); return d end

function SYM:new(s,n) return new(SYM,{name=s,pos=n,bins={},n=0,has={},mode=nil,most=0})end
function NUM:new(s,n) return new(NUM,{name=s,pos=n,bins={},n=0,w=0,mu=0,m2=0,sd=0,
                                                           lo=the.inf, hi=-the.inf}) end
function COLS:new()   return new(COLS,{all={}, x={}, y={}, names=""}) end
function DATA:new()   return new(DATA,{rows={}, cols=COLS:new()}) end
 
function BIN:new(name,pos,  lo,hi) 
  return new(BIN,{name=name,pos=pos, lo=lo or inf, hi=hi or lo, y=NUM:new(name,pos)}) end 

function TREE:new(here,lvl,name,pos,lo,hi,mu)
  return l.new(TREE,{lvl=lvl or 0, bin=BIN:new(name,pos,lo,hi), 
                     mu=mu or 0, here=here, _kids={}})  end

-- Lib
-- ---
local abs, max, min = math.abs, math.max, math.min
local push,oo,o,cat,kat,coerce,csv

function push(t,x)    t[1+#t]=x; return x end

function oo(t)        print(o(t)); return t end
function o(t)         return "("..table.concat(#t==0 and kat(t) or cat(t),", ")..")" end
function cat(t,    u) u={}; for _,v in pairs(t) do push(u,tostring(v)) end; return u end
function kat(t,    u)
  u={}
  for k,v in pairs(t) do 
    if not tostring(k):find"^_" then push(u,string.format("%s:%s",k,v)) end end
  table.sort(u)
  return u end

function coerce(s,    fun)
  if type(s) ~= "string" then return s end
  fun = function(s) return s=="true" or s ~="false" and s end 
  return math.tointeger(s) or tonumber(s) or fun(s:match"^%s*(.-)%s*$") end 

function csv(sFile,   n)
  sFile = sFile=="-" and io.stdin or io.input(sFile)
  n = -1
  return function(      s,t)
    s = io.read()
    if s then 
       n = n + 1
       t={};for x in s:gsub("%s+", ""):gmatch("([^,]+)") do t[1+#t]=coerce(x) end
       return n,t 
    else io.close(sFile) end end end 

-- Create
-- ------
function DATA:read(sFile)
  for n,row in csv(sFile) do if n==0 then self:head(row) else self:add(row) end end
  return self end

function DATA:head(row)
  self.cols.names = row
  for c,x in pairs(row) do if not x:find"X$" then self.cols:add(c,x) end end 
  return self end

function DATA:clone(  rows,    data) 
  data = DATA:new():head(self.cols.names) 
  for _,row in pairs(rows or {}) do data:add(row) end 
  return data end

--  Update
-- -------
function SYM:add(x) 
  self.n = self.n + 1
  self.has[x] = 1 + (self.has[x] or 0) 
  if self.has[x] > self.most then self.most,self.mode = self.has[x],x end end

function NUM:add(n,      d)
  self.n  = self.n + 1
  d       = n - self.mu
  self.mu = self.mu + d/self.n
  self.m2 = self.m2 + d * (n-self.mu)
  self.sd = self.n < 2 and 0 or (self.m2/(self.n - 1))^0.5 
  if     n > self.hi then self.hi = n 
  elseif n < self.lo then self.lo = n end end

function COLS:add(pos,name,     col)
  col = push(self.all, (name:find"^[A-Z]" and NUM or SYM):new(name,pos)) 
  col.bins[col.pos] = {}
  if name:find"-$" then col.w=0; return push(self.y, col) end
  if name:find"+$" then col.w=1; return push(self.y, col) end
  push(self.x, col) end

function DATA:add(row)
  push(self.rows,row)
  for _,c in pairs(self.cols.all) do if row[c.pos]~="?" then c:add(row[c.pos]) end end end 

function BIN:add(x,y)
  if x ~= "?" then 
    if x < self.lo then self.lo = x end
    if x > self.hi then self.hi = x end
    self.y:add(y) end end

--- Query
-- -----
function SYM:bin(x) return x end
function NUM:bin(n) return math.floor(0.5 + the.bins*self:cdf(n))  end

function NUM:norm(n) return n=="?" and n or (n-self.lo)/(self.hi-self.lo + 1/the.inf) end

function NUM:cdf(n,      fun,z)
  fun = function(z) return 1 - 0.5*2.718^(-0.717*z - 0.416*z*z) end
  z = (n - self.mu) / self.sd
  return z >= 0 and fun(z) or 1 - fun(-z) end

function BIN:__tostring(     lo,hi,s)
  lo,hi,s = self.x.lo, self.x.hi,self.x.name
  if lo == -inf then return string.format("%s <= %g", s,hi) end
  if hi ==  inf then return string.format("%s > %g",  s,lo) end
  if lo ==  hi  then return string.format("%s == %s", s,lo) end
  return string.format("%g < %s <= %g", lo, s, hi) end

function BIN:selects(rows,     u,lo,hi,x)
  u,lo,hi = {}, self.x.lo, self.y.hi
  for _,row in pairs(rows) do 
    x = row[self.x.pos]
    if x=="?" or lo==hi and lo==x or lo < x and x <= hi then push(u,r) end end
  return u end

-- Discretization
-- -------------
function DATA:sort()
  table.sort(self.rows, function(a,b) return self:chebyshev(a) < self:chebyshev(b) end)
  return self end

function DATA:chebyshevs(rows,    sum,n)
  sum,n=0,0; for _,r in pairs(rows or self.rows) do n=n+1; sum=sum+self:chebyshev(r) end
  return sum/n end

function DATA:chebyshev(row,     d) 
  d=0; for _,y in pairs(self.cols.y) do d = max(d,abs(y:norm(row[y.pos]) - y.w)) end
  return d end

function DATA:bins(rows,     x,y,b) 
  for _,row in pairs(rows or self.rows) do 
    y = self:chebyshev(row)
    print""
    for _,col in pairs(self.cols.x) do
      x = row[col.pos]
      if x ~= "?" then 
        b = col:bin(x)
        print(string.format("<%s><%s>",x,b))
        col.bins[b] = col.bins[b] or  BIN:new(col.name,col.pos,x,x) 
        print(string.format("[%s][%s]",x,b))
        if col.bins[b] and col.bins[b].add 
        then col.bins[b]:add(x,y) 
        else oo(col) ; print("---",x,b,o(cols.bins[b]) end end end end
  return self end 

function DATA:splitter(      lo,w,n,out,tmp)
  lo = inf
  for _,col in pairs(self.cols.x) do
    w,n,tmp,out = 0,0,{},out or col
    for _,bin in pairs(col.bins) do w=w+bin.y.n*bin.y.sd; n=n+bin.y.n; push(tmp,bin) end
    if w/n < lo then lo, out = w/n, col end
    table.sort(tmp, function(a,b) return a.y.mu < b.y.mu end)
    col.bins = tmp end 
  return out end  

function DATA:tree(     _grow)
  function _grow(rows,stop,lvl,name,pos,lo,hi,     tree,sub,_grow)
    tree = TREE:new(self:clone(rows), lvl,name,pos,lo,hi,self:chebyshevs(rows))
    for _,bin in pairs(self:bins(rows):spitter().bins) do
      sub = bin:selects(rows)
      if #sub < #rows and #sub > stop then
        push(tree._kids, _grow(sub,stop,lvl+1,bin.name,bin.pos,bin.x.lo,bin.x.hi)) end end
    return tree 
  end
  return _grow(self.rows,(#self.rows)^0.5,0) end

function TREE:__tostring() 
  return string.format("%.2f\t%5s\t%s%s", self.mu, #self.here.rows, 
                       ("|.. "):rep(self.lvl-1), self.lvl==0 and "" or self.bin) end

function TREE:visit(fun) 
  fun = fun or print
  fun(self)
  for _,kid in pairs(self._kids) do kid:visit(fun) end end 

-- eg
-- --
local eg={}
eg["-h"] = function(_) print("lua x2.lua --[aa|bb] [FILE.csv]") end

eg["--train"] = function(train,     d) 
  d=DATA:new():read(train or the.train) 
  oo(d.cols.x[2]) end

eg["--sort"] = function(train)
  for i,row in pairs(DATA:new():read(train or the.train):sort().rows) do 
    if i==1 or i%25==0 then print(i, o(row)) end end end 

eg["--bins"] = function(train,    d)
  d = DATA:new():read(train or the.train)
  oo(d)
  d:bins() end

eg[arg[1] or "-h"](coerce(arg[2]))

-- Notes on Type Hints in Variable Names
-- -------------------------------------
-- Holds only for function arguments.
--
-- - `t` = table
-- - `u` = table. some output generated from `t`
-- - `d` = dictionary (table with keys)
-- - `a` = array (table with numeric keys)
-- - `s` = string
-- - `n` = number
-- - `x` = any
-- - suffix s denotes arrays of certain types. e.g. ns = array of numbers.
-- - prefixes combine types and names; e.g. sFile is a string that is a file name
-- - `row` = `list[n | s | "?"]`
-- - `rows` = `list[row]`
-- - names in lower cases from UPPER CASE functions; e.g. sym made by SYM:new()

#!/usr/bin/env lua
-- <!-- vim:set filetype=lua et : -->
local the = require"config"
the.bins=7

-- Types
-- -----
-- - `t` = table
-- - `d`= dictionary (table with keys)
-- - `a` = list (table with numeric keys)
-- - `s` = string
-- - `n` = number
-- - `x` = any
-- - `row` = `list[n | s | "?"]`
-- - `rows` = `list[row]`
-- - UPPER CASE = instance

-- Structs
-- -------
local SYM,NUM,COLS,DATA,BIN={},{},{},{},{}
local function new(isa,t)   isa.__index=isa; setmetatable(t,isa); return t end

function SYM:new(s,n) return new(SYM,{name=s,pos=n,bins={},n=0,has={},mode=nil,most=0})end
function NUM:new(s,n) return new(NUM,{name=s,pos=n,bins={},n=0,w=0,mu=0,m2=0,sd=0,
                                                           lo=the.inf, hi=-the.inf}) end
function COLS:new()   return new(COLS,{all={}, x={}, y={}, names=""}) end
function DATA:new()   return new(DATA,{rows={}, cols=COLS:new(), bins={}}) end

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
  for n,row in csv(sFile) do if n==0 then self:head(row) else self:body(row) end end
  return self end

function DATA:head(row)
  self.cols.names = row
  for c,x in pairs(row) do if not x:find"X$" then self.cols:add(c,x) end end 
  return self end

function DATA:body(row) self:add(row); end --self:bins(row) end 

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
  for _,c in pairs(self.cols.all) do if row[c.pos]~="?" then c:add(row[c.pos]) end end end 

-- Query
-- -----
function SYM:bin(x) return x end
function NUM:bin(n) return the.bins*self:cdf(n) // 1 end

function NUM:norm(n) return n=="?" and n or (n-self.lo)/(self.hi-self.lo + 1/the.inf) end

function NUM:cdf(n,      fun,z)
  fun = function(z) return 1 - 0.5*2.718^(-0.717*z - 0.416*z*z) end
  z = (n - self.mu) / self.sd
  return z >= 0 and fun(z) or 1 - fun(-z) end

-- Discretization
-- -------------
function BIN:new(s,n,lo,hi) return new(BIN, {name=s,pos=n,lo=lo,hi=hi or lo}) end 

function DATA:chebyshev(row,     d) 
  d=0; for _,y in pairs(self.cols.y) do d = max(d,abs(y:norm(row[y.pos]) - y.w)) end
  return d end

function DATA:bins(row,    d,x,b)
  d = self:chebshev(row)
  for _,col in pairs(self.cols.x) do
    x = row[col.pos]
    if x ~= "?" then
      b = col:bin(x)
      col.bins[b] = (col.bins[b] or 0) + d end end end

-- eg
-- --
local eg={}
eg["-h"] = function(_) print("lua x2.lua --[aa|bb] [FILE.csv]") end

eg["--train"] = function(train,     d)
  d=DATA:new():read(train or the.train) 
  oo(d.cols.x[2])
  end


eg[arg[1] or "-h"](coerce(arg[2]))

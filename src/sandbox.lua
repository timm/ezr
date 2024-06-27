#!/usr/bin/env lua
-- sandbox.lua : multi-objective rule generation
-- (c) Tim Menzies <timm@ieee.org> MIT license

local the={bins=17, fmt="%.3g", cohen=0.35, seed=1234567891,
           train="../data/misc/auto93.csv"}

local big=1E30
local DATA,SYM,NUM,COLS,XY,ROW = {},{},{},{},{},{}
local abs, max, min = math.abs, math.max, math.min
local coerce,coerces,copy,csv,fmt,id,new,o,okey,okeys,olist,push,sort
-----------------------------------------------------------------------------------------
function NUM.new(name,pos)
  return new(NUM,{name=name, pos=pos, n=0, mu=0, m2=0, sd=0, lo=big, hi= -big,
                  goal= (name or ""):find"-$" and 0 or 1}) end

function NUM:add(x,     d)
  if x ~= "?" then
    self.n  = self.n + 1
    d       = x - self.mu
    self.mu = self.mu + d/self.n
    self.m2 = self.m2 + d*(x - self.mu)
    self.sd = self.n<2 and 0 or (self.m2/(self.n - 1))^.5 
    self.lo = min(x, self.lo)
    self.hi = max(x, self.hi)
    return x end end 

function NUM:norm(x) return x=="?" and x or (x - self.lo)/(self.hi - self.lo) end

function NUM:small(x) return x < the.cohen * self.sd end

function NUM.same(i,j,    pooled)
  pooled = (((i.n-1)*i.sd^2 + (j.n-1)*j.sd^2)/ (i.n+j.n-2))^0.5
  return abs(i.mu - j.mu) / pooled <= (the.cohen or .35) end
-----------------------------------------------------------------------------------------
function SYM.new(name,pos)
  return new(SYM,{name=name, pos=pos, n=0, has={}, most=0, mode=nil}) end

function SYM:add(x,     d)
  if x ~= "?" then
    self.n  = self.n + 1
    self.has[x] = 1 + (self.has[x] or 0)
    if self.has[x] > self.most then self.most,self.mode = self.has[x], x end 
    return x end end
-----------------------------------------------------------------------------------------
function ROW.new(t) return new(ROW,{cells=t,y=0,id=id()}) end
-----------------------------------------------------------------------------------------
function DATA.new(file,    self) 
  self = new(DATA, {rows={}, cols=nil})
  for row in csv(file) do  self:add(ROW.new(row)) end
  for n,row in pairs(self.rows) do  row.y =  1 - self:chebyshev(row) end
  return self end

function DATA:add(row)
  if self.cols then push(self.rows, self.cols:add(row)) else 
     self.cols = COLS.new(row) end end 

function DATA:chebyshev(row,     d) 
  d=0; for _,col in pairs(self.cols.y) do 
         d = max(d,abs(col:norm(row.cells[col.pos]) - col.goal)) end
  return d end
-------------------------------------------------------------------------------------
function COLS.new(row,    self,skip,col)
  self = new(COLS,{all={},x={}, y={}, klass=nil})
  skip={}
  for k,v in pairs(row.cells) do
    col = push(v:find"X$" and skip or v:find"[!+-]$" and self.y or self.x,
            push(self.all, 
              (v:find"^[A-Z]" and NUM or SYM).new(v,k))) 
    if v:find"!$" then self.klass=col end end
  return self end 

function COLS:add(row)
  for _,cols in pairs{self.x, self.y} do
    for _,col in pairs(cols) do  col:add(row.cells[col.pos]) end end 
  return row end
-----------------------------------------------------------------------------------------
function DATA:xys(rows,      xys,val,down) 
  xys = {}
  for _,col in pairs(self.cols.x) do
    val  = function(a)   return a.cells[col.pos]=="?" and -big or a.cells[col.pos] end
    down = function(a,b) return val(a) < val(b) end
    for _,xy in pairs(col:xys(sort(rows, down))) do 
      if not (xy.lo == -big and xy.hi == big) then push(xys,xy) end  end end
  return xys end 

function SYM:xys(rows,     t,x) 
  t={}
  for k,row in pairs(rows) do
    x= row.cells[self.pos] 
    if x ~= "?" then
      t[x] = t[x] or XY.new(self.name,self.pos,x)
      t[x]:add(row) end end
  return t end

function NUM:xys(rows,     t,a,b,ab,x,want)
  t = {} 
  b = XY.new(self.name, self.pos)
  ab= XY.new(self.name, self.pos)
  for k,row in pairs(rows) do
    x = row.cells[self.pos] 
    if x ~= "?" then 
      want = want or (#rows - k - 1)/the.bins
      if b.y.n >= want and #rows - k > want and not self:small(b.hi - b.lo) then
        a = t[#t]; if a and a.y:same(b.y) then t[#t]=ab else push(t,b) end
        ab= copy(t[#t])
        b = XY.new(self.name,self.pos,x) end
      b:add(row) 
      ab:add(row) 
  end end 
  a = t[#t]; if a and a.y:same(b.y) then t[#t]=ab else push(t,b) end
  t[1].lo  = -big
  t[#t].hi =  big
  for k = 2,#t do t[k].lo = t[k-1].hi end 
  return t end
-----------------------------------------------------------------------------------------
function XY.new(name,pos,lo,hi)
  return new(XY,{lo=lo or big, hi= hi or lo or -big,  _rules={}, y=NUM.new(name,pos)}) end

function XY:add(row,     x) 
  x = row.cells[self.y.pos]
  if x ~= "?" then
    if x < self.lo then self.lo = x end
    if x > self.hi then self.hi = x end
    self._rules[row.id] = row.id
    self.y:add(row.y) end end

function XY:__tostring(     lo,hi,s)
  lo,hi,s = self.lo, self.hi,self.y.name
  if lo == -math.huge then return fmt("%s < %g", s,hi) end
  if hi ==  math.huge then return fmt("%s >= %g",s,lo) end
  if lo ==  hi        then return fmt("%s == %s",s,lo) end
  return fmt("%g <= %s < %g", lo, s, hi) end
-----------------------------------------------------------------------------------------
local _id=0
function id() _id=_id+1; return _id end

fmt = string.format

function olist(t)  local u={}; for k,v in pairs(t) do push(u, fmt("%s", o(v))) end; return u end
function okeys(t)  
  local u={}; for k,v in pairs(t) do 
               if not tostring(k):find"^_" then push(u, fmt(":%s %s", k,o(v))) end end; 
  return sort(u) end

function o(x)
  if type(x)=="number" then return fmt(the.fmt or "%g",x) end
  if type(x)~="table"  then return tostring(x) end 
  return "{" .. table.concat(#x==0 and okeys(x) or olist(x),", ")  .. "}" end

function new (klass,object) 
  klass.__index=klass; setmetatable(object, klass); return object end

function coerce(s,    also)
  if s ~= nil then
    also = function(s) return s=="true" or s ~="false" and s end 
    return math.tointeger(s) or tonumber(s) or also(s:match"^%s*(.-)%s*$") end end

function coerces(s,    t)
  t={}; for s1 in s:gsub("%s+", ""):gmatch("([^,]+)") do t[1+#t]=coerce(s1) end
  return t end

function csv(src)
  src = src=="-" and io.stdin or io.input(src)
  return function(      s)
    s = io.read()
    if s then return coerces(s) else io.close(src) end end end

function push(t,x) t[1+#t]=x; return x end 
function sort(t,fun) table.sort(t,fun); return t end

function copy(t,     u)
  if type(t) ~= "table" then return t end 
  u={}; for k,v in pairs(t) do u[copy(k)] = copy(v) end 
  return setmetatable(u, getmetatable(t)) end
-----------------------------------------------------------------------------------------
local eg={}

eg["-h"] = function(_) 
  print"USAGE: lua sandbox.lua -[hkln] [ARG]" end

eg["--copy"] = function(_,     n1,n2,n3) 
  n1,n2 = NUM.new(),NUM.new()
  for i=1,100 do n2:add(n1:add(math.random()^2)) end
  n3 = copy(n2)
  for i=1,100 do n3:add(n2:add(n1:add(math.random()^2))) end
  for k,v in pairs(n3) do assert(v == n2[k] and v == n1[k]) end 
  n3:add(0.5)
  assert(n2.mu ~= n3.mu) end

eg["--cohen"] = function(_,    u,t) 
    for _,inc in pairs{1,1.05,1.1,1.15,1.2,1.25} do
      u,t = NUM.new(), NUM.new()
      for i=1,20 do u:add( inc * t:add(math.random()^.5))  end
      print(inc, u:same(t)) end end 

eg["--train"] = function(file,     d,want) 
  d= DATA.new(file or the.train) 
  want=1
  for i,row in pairs(sort(d.rows,function(a,b) return a.y > b.y end)) do
    if i == want then want=2*want; print(i, o{y=row.y,row=row.cells}) end end end

eg["--xys"] = function(file,     d,last) 
  d= DATA.new(file or the.train) 
  for _,xy in pairs(d:xys(d.rows)) do
    if xy.y.name ~= last then print""; last=xy.y.name end
     print(fmt("%5.3g\t %s", xy.y.mu, xy)) end
  end 
-----------------------------------------------------------------------------------------
if   pcall(debug.getlocal, 4, 1) 
then return {DATA=DATA,NUM=NUM,SYM=SYM,XY=XY}
else math.randomseed(the.seed or 1234567891)
     for k,v in pairs(arg) do if eg[v] then eg[v](coerce(arg[k+1])) end end end
-----------------------------------------------------------------------------------------
-- ## Details
--
-- - Download:     github.com/timm/ezr/blob/main/src/sandbox.lua
-- - Sample Data:  github.com/timm/ezr/tree/main/data/*/*.csv (ignore the "old" directory)
-- - Sample Usage: lua sandox.lua --xys data/misc/auto93.csv

-- ## MIT License
--
-- Copyright (c) 2024, Tim Menzies
--
-- Permission is hereby granted, free of charge, to any person obtaining a copy
-- of this software and associated documentation files (the "Software"), to deal
-- in the Software without restriction, including without limitation the rights
-- to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
-- copies of the Software, and to permit persons to whom the Software is
-- furnished to do so, subject to the following conditions:
--
-- The above copyright notice and this permission notice shall be included in all
-- copies or substantial portions of the Software.
--
-- THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
-- IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
-- FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
-- AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
-- LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
-- OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
-- SOFTWARE. 

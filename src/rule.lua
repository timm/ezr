#!/usr/bin/env lua
-- <!-- vim : set ts=4 sts=4 et : -->

--                      ___              
--                     /\_ \             
--      _ __   __  __  \//\ \       __   
--     /\`'__\/\ \/\ \   \ \ \    /'__`\ 
--     \ \ \/ \ \ \_\ \   \_\ \_ /\  __/ 
--      \ \_\  \ \____/   /\____\\ \____\
--       \/_/   \/___/    \/____/ \/____/

-- rulr.lua multi-objective rule generation   
-- (c) 2024 Tim Menzies <timm@ieee.org>, BSD-2 license.
local the = { bins  = 16,
              train = "../data/misc/auto93.csv"}

local l=require"lib"
local BIN,NUM,SYM,DATA={},{},{},{}
local abs,max,min = math.abs, math.max, math.min
local csv, new, o, oo, push = l.csv, l.new, l.o, l.oo, l.push
-------------------------------------------------------------------------------
local the = { train = "../data/misc/auto93.csv"}

local function is(name,x,       pat) 
  pat = {num    = "^[A-Z]", 
         goal   = "[!+-]$", 
         min    = "-$", 
         ignore = "X$"}
  return (name or ""):find(pat[x]) end
-------------------------------------------------------------------------------
function BIN.new(pos,name,lo,hi) 
  return new(BIN, {pos=pos,name=name,n=0,ds=0,rowids={},
                   lo=lo or math.huge, hi= hi or -math.huge}) end

function BIN:add(row,data,     x)
  x = row[self.pos]
  if x ~= "?" then
    self.n  = self.n + 1
    self.ds = self.ds + (1 - data:chebyshev(row))
    if x < self.lo then self.lo=x end
    if x > self.hi then self.hi=x end
    push(self.rowids, row[#row]) end end

function BIN:__tostring(     lo,hi,s)
  lo,hi,s = self.lo, self.hi,self.name
  if lo == -math.huge then return string.format("%s < %s", s,hi) end
  if hi ==  math.huge then return string.format("%s >= %s",s,lo) end
  if lo ==  hi        then return string.format("%s == %s",s,lo) end
  return string.format("%s <= %s < %s", lo, s, hi) end
-------------------------------------------------------------------------------
function SYM.new(name,pos) return new(SYM, {name=name, pos=pos, has={}}) end

function SYM:add(x) if x ~= "?" then self.has[x] = 1 + (self.has[x] or 0) end end

function SYM:bins(rows,bins,    tmp,x)
  tmp={}
  for m,row in pairs(rows) do
    x = row[self.pos]
    if x ~= "?" then
      tmp[x] = tmp[x] or push(bins, BIN.new(self.pos,self.name,x,x))
      tmp[x]:add(row,self) end end end
-------------------------------------------------------------------------------
function NUM.new(name,pos) 
  return new(NUM, 
   {name=name, pos=pos, lo=math.huge, hi=-math.huge, goal=is(name,"min") and 0 or 1}) end

function NUM:add(x) 
  if x ~= "?" then self.lo = min(x, self.lo); self.hi = max(x,self.hi)  end end

function NUM:norm(x)
  return x=="?" and x or (x - self.lo)/(self.hi - self.lo + 1E-30) end

function NUM:bins(rows,bins,    _numLast,_order,bin,x,want)
  _numLast = function(x) return x=="?" and -math.huge or x end
  _order   = function(a,b) return _numLast(a[self.pos]) < _numLast(b[self.pos]) end
  bin      = push(bins, BIN.new(self.pos,self.name, -math.huge))
  for m,row in pairs(sort(self.rows, _order)) do
    x = row[self.pos] 
    if x ~= "?" then
      want = want or (#self.rows - m) / the.bins
      if bin.n > want then
        if x ~= self.rows[m-1][c] then
          bin = push(bins, BIN.new(self.pos,self.name,bin.hi)) end  end
      bin:add(row,self) end end 
  bin.hi = math.huge end
-------------------------------------------------------------------------------
function DATA.new() return new(DATA,{rows={}, cols=nil}) end 

local _rowid=0
function DATA:read(file,     body) 
  for row in l.csv(file) do 
    if body then _rowid = 1 + _rowid push(row, _rowid) end
    body = true
    self:add(row,true) end
  return self end

function DATA:add(row)
  if self.cols then self:_body(row) else self.cols=self:_header(row) end end

function DATA:_header(row,      all,x,y)
  all,x,y = {},{},{}
  for pos,name in pairs(row) do  
    col = push(all, (is(name,"num") and NUM or SYM).new(name,pos))
    if not is(name,"ignore") then 
      push(is(name,"goal") and y or x, col) end end 
  return {names=row, all=all, x=x, y=y} end 

function DATA:_body(row)
  push(self.rows, row)  
  for _,col in pairs(self.cols.all) do col:add(row[col.pos]) end end
  
function DATA:sort(      d)
  d = function(row) return self:chebyshev(row) end
  table.sort(self.rows, function(a,b) return d(a) < d(b) end)
  return self end

function DATA:chebyshev(row,     d)
  d=0; for _,col in pairs(self.cols.y) do 
         d = max(d,abs(col:norm(row[col.pos]) - col.goal)) end
  return d end

function DATA:bins(      bins)
  bins={}; for _,col in pairs(self.cols.x) do col:bins(self.rows,bins) end
  return l.sort(bins, l.down"ds") end
-----------------------------------------------------------------------------------------
---       _    _  
--      (/_  (_| 
--            _| 
local eg={}

function eg.help(_) 
  print("./rule.lua [help|data|bins|grow] [csv]") end

function eg.data(train,     d,m) 
  d = DATA.new():read(the.train):sort()  
  m = 1
  for n,row in pairs(d.rows) do 
    if n==m then m=m*2; print(n,o(d:chebyshev(row)),o(row)) end end  end

if pcall(debug.getlocal, 4, 1)
then return {DATA=DATA}
else eg[ arg[1] or "help" ]( arg[2] or the.train )
end 

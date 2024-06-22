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
local BIN,DATA={},{}
local abs,max,min = math.abs, math.max, math.min
local csv, new, o, oo, push = l.csv, l.new, l.o, l.oo, l.push

local the = { train = "../data/misc/auto93.csv"}

local function is(name,x,       pat) 
  pat = {num = "^[A-Z]", goal = "[!+-]$", min  = "-$", ignore = "X$"}
  return name:find(pat[x]) end

function BIN.new(pos,name,lo,hi) 
  return new(BIN, {pos=pos,name=name,n=0,ds=0,rowids={},
                   lo=lo or math.huge,hi= hi or -math.huge}) end

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

function DATA.new() return new(DATA,{rows={},names=nil,goals={},nums={}}) end 

function DATA:read(it)
  for row in it do 
    if self.names then self:_body(row) else self:_header(row) end end
  return self end

function DATA:sort(      d)
  d = function(row) return self:chebyshev(row) end
  table.sort(self.rows, function(a,b) return d(a) < d(b) end)
  return self end

function DATA:_header(row,      _header)
  self.names=row 
  for c,name in pairs(self.names) do  
    if not is(name,"ignore") then 
      if is(name,"goal") then self.goals[c] = is(name,"min")  and 0 or 1 end 
      if is(name,"num")  then self.nums[c]  = {lo=math.huge, hi=-math.huge} end end end end

local _rowid=0
function DATA:_body(row)
   _rowid = _rowid + 1
   push(row, _rowid)
   push(self.rows, row) 
   for c,num in pairs(self.nums) do
     num.lo = min(row[c], num.lo)
     num.hi = max(row[c], num.hi) end end 
  
function DATA:norm(c,x,    num) 
  num=  self.nums[c]
  return x=="?" and x or (x-num.lo)/(num.hi - num.lo + 1E-30) end

function DATA:chebyshev(row,     d)
  d=0; for c,goal in pairs(self.goals) do d = max(d,abs(self:norm(c,row[c]) - goal)) end
  return d end

function DATA:bins(     bins)
  bins={}
  for c,name in pairs(self.names) do
    if not is(name,"goals") then
      if is(name,"nums") then self:nums2bins(c,name,bins) 
                         else self.syms2bins(c,name,bins) end end end 
  return l.sort(bins, l.down"ds") end

function DATA:syms2bins(c,name,bins,    tmp,x)
  tmp={}
  for m,row in pairs(self.rows) do
    x = row[c]
    if x ~= "?" then
      tmp[x] = tmp[x] or push(bins, BIN.new(c,name,x,x))
      tmp[x]:add(row,self) end end end

function DATA:nums2bins(c,name,bins,    _value,bin,x,want)
  _value = function(row) return row[c]=="?" and -math.huge or row[c] end
  bin = push(bins, BIN.new(c,name, -math.huge))
  self.rows = l.sort(self.rows, function(a,b) return _value(a) < _value(a) end)
  for m,row in pairs(self.rows) do
    x = row[c] 
    if x ~= "?" then
      want = want or (#self.rows - m) / the.bins
      if bin.n > want then
        if x ~= self.rows[m-1][c] then
          bin = push(bins, BIN.new(c,name,bin.hi)) end  end
      bin:add(row,self) end end 
  bin.hi = math.huge end
   
-----------------------------------------------------------------------------------------
---       _    _  
--      (/_  (_| 
--            _| 
local eg={}

function eg.help(_) 
  print("./rule.lua [help|data|bins|grow] [csv]") end

function eg.data(train,     d,m) 
  d = DATA.new():read(csv(train)):sort()  
  m = 1
  for n,row in pairs(d.rows) do 
    if n==m then m=m*2; print(n,o(d:chebyshev(row)),o(row)) end end  end

if   pcall(debug.getlocal, 4, 1)
then return {DATA=DATA}
else eg[ arg[1] or "help" ]( arg[2] or the.train )
end 

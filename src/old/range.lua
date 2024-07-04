#!/usr/bin/env lua
-- <!-- vim : set ts=4 sts=4 et : -->
--
--      _ __     __       ___       __        __   
--     /\`'__\ /'__`\   /' _ `\   /'_ `\    /'__`\ 
--     \ \ \/ /\ \L\.\_ /\ \/\ \ /\ \L\ \  /\  __/ 
--      \ \_\ \ \__/.\_\\ \_\ \_\\ \____ \ \ \____\
--       \/_/  \/__/\/_/ \/_/\/_/ \/___L\ \ \/____/
--                                  /\____/        
--                                  \_/__/         
--
-- rulr.lua multi-objective rule generation   
-- (c) 2024 Tim Menzies <timm@ieee.org>, BSD-2 license.
local the = { bins  = 16,
              train = "../data/misc/auto93.csv"}

local l=require"lib"
local rulr={}
local abs,max,min = math.abs, math.max, math.min
local new, o, oo, push = l.new, l.o, l.oo, l.push

local d=require"data"
local NUM, SYM, DATA = d.NUM, d.SYM, d.DATA
local RANGE={}

local id=0
function RANGE.new(name,pos,lo)
  id=id+1
  return new(RANGE, {name=name,pos=pos,lo=lo,hi=lo, n=0, id=id, ys=0}) end

function RANGE:add(x,y)
  if x == "?" then return end
  self.n  = self.n + 1
  self.lo = min(x,self.lo)
  self.hi = max(x,self.hi) 
  self.ys = self.ys + y end

function RANGE:show(     lo,hi,s)
  lo,hi,s = self.lo, self.hi,self.name
  if lo == -math.huge then return l.fmt("%s < %s", s,hi) end
  if hi ==  math.huge then return l.fmt("%s >= %s",s,lo) end
  if lo ==  hi        then return l.fmt("%s == %s",s,lo) end
  return l.fmt("%s <= %s < %s", lo, s, hi) end

function RANGE.merge(i,j,    k)
  k = RANGE.new(i.name, i.pos, min(i.lo, j.lo))
  k.hi = max(i.hi, j.hi)
  k.n  = i.n + j.n
  k.ys = (i.n*i.ys + j.n*j.ys)/k.n
  return k end

function RANGE:merged(other,tiny,pedantry,trivial)
  print("....")
  if self.n < tiny   and other.n < tiny    or
     self.ys < trivial and other.ys < trivial or
     abs(self.ys - other.ys) < pedantry 
  then return self:merge(other) end end

-----------------------------------------------------------------------------------------
function SYM:bin(x) return x end
function SYM:mergeds(ranges,...) return ranges end

function NUM:bin(x,    z,area) 
  if x=="?" then return x end
  z    = (x - self.mu) / self.sd
  area = z >= 0 and l.cdf(z) or 1 - l.cdf(-z) 
  return max(1, min(the.bins, 1 + (area * the.bins // 1))) end 

function NUM:mergeds(ranges,  tiny,pedantry,trivial,    i,a,tmp,both)
  print(100,o(ranges))
  i,tmp = 1,{}
  while i <= #ranges do
    a = ranges[i]
    print(i, o(a))
    if i < #ranges then
      both = a:merged(ranges[i+1],tiny,pedantry,trivial)
      if both then 
        a = both
        i = i+1 end end
    tmp[1+#tmp] = a
    i = i+1 end
  if #tmp < #ranges then return self:mergeds(tmp,tiny,pedantry,trivial) end
  for i = 2,#tmp do tmp[i].lo = tmp[i-1].hi end
  print(111,o(tmp[1]))
  tmp[1].lo  = -math.huge
  tmp[#tmp].hi =  math.huge
  return tmp end

function DATA:bins(     out,d,x,b, bins)
  for _,row in pairs(self.rows) do
    d = l.chebyshev(row, self.cols.y)
    for _,col in pairs(self.cols.x) do
      x = row[col.pos]
      if x ~= "?" then
        b = col:bin(x)
        col.bins[b]  = col.bins[b] or RANGE.new(col.name,col.pos,x)
        col.bins[b]:add(x, (1 - d)/#self.rows) end end end
  out = {}
  for _,col in pairs(self.cols.x) do
    bins = l.map(col.bins, function(x) return x end)
    for _,bin in pairs(col:mergeds(bins, 1/the.bins*#self.rows, 0.025, 0.025)) do
      push(out,bin) end end
  return l.sort(out,l.down"ys") end
-----------------------------------------------------------------------------------------
local _selects1,_selects,_score, _add2rule,rulr

function rulr(data,  rows)
  local now,b4,last = {},{},0
  local bins = data:bins()
  for i,bin in pairs(bins) do
    _add2rule(now, bin)
    local tmp = _score(data,now,rows)
    if tmp > last then _add2rule(b4, bin) else return b4 end 
    last = tmp end end 

function _add2rule(rule,bin,    pos) 
  pos = bin.pos
  rule[pos] = rule[pos] or {}
  push(rule[pos], bin) end

function _score(data,rule,  rows,    n,s) 
  n,s = 0,0
  for _,row in pairs(rows or data.rows) do 
    if _selects(data,rule, row) then
      n = n + 1 
      s = s + 1 - l.chebyshev(row, data.cols.y) end end 
  return s/n end

function _selects(data,rule,row,     col,x) -- true if each bin satisfied
  for pos,bins in pairs(rule) do
    col = data.cols.all[pos]
    x = row[pos] 
    if x ~= "?" then
      if not _selects1(bins, col:bin(x)) then return false end end end
  return true end

function _selects1(bins, want) -- true if any bin is satisfied
  for _,bin in pairs(bins) do if bin.bin==want then return true end end  end


-----------------------------------------------------------------------------------------
--       ._ _    _.  o  ._  
--       | | |  (_|  |  | | 

local main={}

function main.help(_) 
  print("./range.lua [help|data|bins|grow] [csv]") end

function main.data(train,     d,m) 
  d = DATA.new():read(train):sort()
  m = 1
  for n,row in pairs(d.rows) do 
    if n==m then m=m*2; print(n,o(l.chebyshev(row, d.cols.y)),o(row)) end end end

function main.bins(train)
  d = DATA.new():read(train):sort()
  for _,bin in pairs(d:bins()) do  
    print(o(bin.n), bin.bin, bin.name) end end

function main.grow(train,      rule)
  d = DATA.new():read(train):sort()
  rule = oo(rulr(d)) 
  print(rule[1].name, o(rule)) end

if   pcall(debug.getlocal, 4, 1)
then return {rulr=rulr}
else main[ arg[1] or "help" ]( arg[2] or the.train )
end

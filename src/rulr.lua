#!/usr/bin/env lua
-- <!-- vim : set ts=4 sts=4 et : -->
--
--                       ___           
--                      /\_ \           
--       _ __   __  __  \//\ \     _ __  
--      /\`'__\/\ \/\ \   \ \ \   /\`'__\ 
--      \ \ \/ \ \ \_\ \   \_\ \_ \ \ \/ 
--       \ \_\  \ \____/   /\____\ \ \_\ 
--        \/_/   \/___/    \/____/  \/_/ 
--     
-- rulr.lua multi-objective rule generation   
-- (c) 2024 Tim Menzies <timm@ieee.org>, BSD-2 license.
-- XXX help string
local the = { bins  = 5,
              fmt   = "%6.3f", 
              train = "../data/misc/auto93.csv"}

local l=require"lib"
local abs,max,min = math.abs, math.max, math.min
local coerce,    cdf,  csv,  fmt,  o,  oo,  push,  sort,  down = 
      l.coerce,l.cdf,l.csv,l.fmt,l.o,l.oo,l.push,l.sort,l.dowm

local d=require"data"
local NUM, SYM, DATA = d.NUM, d.SYM, d.DATA
-----------------------------------------------------------------------------------------

function SYM:bin(x) return x end

function NUM:bin(x,    z,area) 
  if x=="?" then return x end
  z    = (x - self.mu) / self.sd
  area = z >= 0 and cdf(z) or 1 - cdf(-z) 
  return max(1, min(the.bins, 1 + (area * the.bins // 1))) end 

function DATA:bins(     out,tmp,x,b)
  out = {}
  for _,row in pairs(self.rows) do
    d = l.chebyshev(row, self.cols.y)
    for _,col in pairs(self.cols.x) do
      x = row[col.pos]
      if x ~= "?" then
        b = col:bin(x)
        col.bins[b]   = col.bins[b] or push(out, {col=col,bin=b,n=0}) 
        col.bins[b].n = col.bins[b].n + (1 - d)/#self.rows end end end
  return out end

function DATA:growRule(bins,rows,     _add2rule,_score)
  function _add2rule(rule,bin,    pos) 
    pos = bin.col.pos
    rule[pos] = rule[pos] or {}
    push(rule[pos], bin) end

  function _score(rule,    n,s) 
    n,s = 0,0
    for _,row in pairs(rows or self.rows) do 
      if self:selects(rule, row) then
        n = n + 1 
        s = s + 1 - self:chebyshev(row, self.cols.y) end end 
    return s/n end

  local now,b4,last = {},{},0
  for _,bin in pairs(sort(bins, down"n")) do
    _add2rule(now, bin)
    local tmp = _score(now)
    if tmp > last then _add2rule(b4, bin) else return b4 end 
    last = tmp end end 

function DATA:selects(rule,row,     _selects1,col,x) -- returns true if each bin is satisfied
  function _selects1(bins, want) -- returns true if any bin is satisfied
    for _,bin in pairs(bins) do if bin.bin==want then return true end end  end

  for pos,bins in pairs(rule) do
    col = self.cols.all[pos]
    x = row[pos] 
    if x ~= "?" then
      if not _selects1(bins, col:bin(x)) then return false end end end
  return true end

-----------------------------------------------------------------------------------------
--       ._ _    _.  o  ._  
--       | | |  (_|  |  | | 

local main={}
function main.help() print("sandbox v0.1") end

function main.data(train,     d,want) 
  d = DATA.new():read(train):sort()
  m = 1
  for n,row in pairs(d.rows) do 
    if n==m then m=m*2; print(n,o(l.chebyshev(row, d.cols.y)),o(row)) end end end

function main.bins(train)
  d = DATA.new():read(train):sort()
  for _,bin in pairs(d:bins()) do  print(o(bin.n), bin.bin, bin.col.name) end end

if    pcall(debug.getlocal, 4, 1)
then  return {DATA=DATA,NUM=NUM,SYM=SYM} 
else  main[ arg[1] or "ver" ]( arg[2]  or "../data/misc/auto93.csv")  end

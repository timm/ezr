#!/usr/bin/env lua
-- <!-- vim : set ts=4 sts=4 et : -->
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
local the = { bins  = 5,
              train = "../data/misc/auto93.csv"}

local l=require"lib"
local rulr={}
local abs,max,min = math.abs, math.max, math.min
local o, oo, push = l.o, l.oo, l.push

local d=require"data"
local NUM, SYM, DATA = d.NUM, d.SYM, d.DATA
-----------------------------------------------------------------------------------------
function SYM:bin(x) return x end

function NUM:bin(x,    z,area) 
  if x=="?" then return x end
  z    = (x - self.mu) / self.sd
  area = z >= 0 and l.cdf(z) or 1 - l.cdf(-z) 
  return max(1, min(the.bins, 1 + (area * the.bins // 1))) end 

function DATA:bins(     out,tmp,x,b)
  out = {}
  for _,row in pairs(self.rows) do
    d = l.chebyshev(row, self.cols.y)
    for _,col in pairs(self.cols.x) do
      x = row[col.pos]
      if x ~= "?" then
        b = col:bin(x)
        col.bins[b]   = col.bins[b] or push(out, {_col=col,bin=b,n=0}) 
        col.bins[b].n = col.bins[b].n + (1 - d)/#self.rows end end end
  return l.sort(out,l.down"n") end
-----------------------------------------------------------------------------------------
function rulr.rulr(data,  rows)
  local now,b4,last = {},{},0
  local bins = data:bins()
  for i,bin in pairs(bins) do
    rulr.add2rule(now, bin)
    local tmp = rulr.score(data,now,rows)
    if tmp > last then rulr.add2rule(b4, bin) else return b4 end 
    last = tmp end end 

function rulr.add2rule(rule,bin,    pos) 
  pos = bin._col.pos
  rule[pos] = rule[pos] or {}
  push(rule[pos], bin) end

function rulr.score(data,rule,  rows,    n,s) 
  n,s = 0,0
  for _,row in pairs(rows or data.rows) do 
    if rulr.selects(data,rule, row) then
      n = n + 1 
      s = s + 1 - l.chebyshev(row, data.cols.y) end end 
  return s/n end

function rulr.selects(data,rule,row,     col,x) -- true if each bin satisfied
  for pos,bins in pairs(rule) do
    col = data.cols.all[pos]
    x = row[pos] 
    if x ~= "?" then
      if not rulr.selects1(bins, col:bin(x)) then return false end end end
  return true end

function rulr.selects1(bins, want) -- true if any bin is satisfied
  for _,bin in pairs(bins) do if bin.bin==want then return true end end  end
-----------------------------------------------------------------------------------------
--       ._ _    _.  o  ._  
--       | | |  (_|  |  | | 

local main={}

main["--help"] = function() 
  print("./ruler.lua --[help|data|bins] [csv]") end

main["--data"] = function(train,     d,want) 
  d = DATA.new():read(train):sort()
  m = 1
  for n,row in pairs(d.rows) do 
    if n==m then m=m*2; print(n,o(l.chebyshev(row, d.cols.y)),o(row)) end end end

main["--bins"]= function(train)
  d = DATA.new():read(train):sort()
  for _,bin in pairs(d:bins()) do  
    print(o(bin.n), bin.bin, bin._col.name) end end

main["--grow"] = function(train)
  d = DATA.new():read(train):sort()
  rulr.rulr(d) end

if   pcall(debug.getlocal, 4, 1)
then return {rulr=rulr}
else main[ arg[1] or "--help" ]( arg[2] or "../data/misc/auto93.csv")  
end

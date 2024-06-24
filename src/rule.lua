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
local the = { bins  = 10,
              cohen = .35,
              beam  = 7,
              seed  = 1234567891,
              train = "../data/misc/auto93.csv"}

local l=require"lib"
local abs,max,min = math.abs, math.max, math.min
local csv, fmt, new, o, oo, push = l.csv, l.fmt, l.new, l.o, l.oo, l.push

local data = require"data"
local DATA,NUM,SYM = data.DATA, data.NUM, data.SYM
local BIN = {}

-------------------------------------------------------------------------------
local _id,_new_id = 0,function() _id=_id+1; return _id end

--Incremetnall update  the (a) `lo` and `hi` value;
--  the (b) observed rule._id values; (c) the mean `y` value.

function BIN.new(pos,name,lo,hi) 
  return new(BIN, {pos=pos,name=name,n=0,mu=0, _rowids={},
                   lo=lo or math.huge, hi= -math.huge}) end

function BIN:add(row,y,     d,x)
  x = row[self.pos]
  if x ~= "?" then
    self.n  = self.n + 1
    d = y - self.mu
    self.mu = self.mu + d/self.n
    if x < self.lo then self.lo=x end
    if x > self.hi then self.hi=x end
    self._rowids[row._id] =  row._id end end

function BIN:__tostring(     lo,hi,s)
  lo,hi,s = self.lo, self.hi,self.name
  if lo == -math.huge then return fmt("%s <= %s", s,hi) end
  if hi ==  math.huge then return fmt("%s > %s",s,lo) end
  if lo ==  hi        then return fmt("%s == %s",s,lo) end
  return fmt("%s < %s <= %s", lo, s, hi) end

-------------------------------------------------------------------------------
-- Make one bin for every unique value in this column.
function SYM:bins(rows,yfun,bins,    tmp,x)
  tmp={}
  for m,row in pairs(rows) do
    x = row[self.pos]
    if x ~= "?" then
      tmp[x] = tmp[x] or push(bins, BIN.new(self.pos,self.name,x,x))
      tmp[x]:add(row,yfun(row)) end end end

-------------------------------------------------------------------------------
-- (a) Sort rows on this column, with all the "?" at the start of the sort.
-- (b) Run down the rows till you clear the ">" values then divide the rest into #rest/bins.
--  Don't divide if (c) the current bin has less than 1/bins of the rows; 
--  if (d) the current value is the same as the last value;
-- if (e)  the current bin's (hi-lo) is not just noise, is more than a 
--   small fraction of the standard deviation,
-- When done, then (f) fill in any gaps between the bins and (f) stretch the first/last bin
-- to negative/positive infinity.
function NUM:bins(rows,yfun,bins,    _numLast,_order,bin,x,want)
  _numLast = function(x) return x=="?" and -math.huge or x end
  _order   = function(a,b) return _numLast(a[self.pos]) < _numLast(b[self.pos]) end
  rows     = l.sort(rows, _order)
  here     = {} 
  bin      = push(here, push(bins, BIN.new(self.pos,self.name)))
  for i,row in pairs(rows) do
    x = row[self.pos] 
    if x ~= "?" then
      want = want or (#rows - i) / the.bins;
      if bin.n > want and #rows - i > want then
        if x ~= rows[i-1][self.pos] then
          if bin.hi - bin.lo > the.cohen*self.sd then
            bin = push(here, push(bins, BIN.new(self.pos,self.name))) end  end end
      bin:add(row,yfun(row)) end end
  for i = 2,#here do here[i].lo = here[i-1].hi end 
  here[1].lo  = -math.huge 
  here[#here].hi =  math.huge end

-------------------------------------------------------------------------------
function DATA:bins(      bins,indx,yfun)
  bins,indx = {},{}
  for n,row in pairs(self.rows) do row._id = n; indx[row._id] = row end
  yfun = function(row) return 1 - l.chebyshev(row,self.cols.y) end
  for _,col in pairs(self.cols.x) do col:bins(self.rows,yfun,bins) end
  return bins,indx end 

function AND(t,u,     v)
  v={}; for k,row in pairs(t) do if u[k] then v[k]=row end end
  return v end

function OR(ts,u,     v)
  v={}; for _,tmp in pairs(t,u) do
          for k,row in pairs(tmp) do v[k] = row end end 
  return v end

local function DATA:_combine(bins,      rule,tmp)
  rule,tmp={},{}
  for _,bin in pairs(bins) do tmp[bin.pos] = OR(tmp[bin.pos] or {}, bin._rowids) end
  for _,v in pairs(tmp) do rule = AND(rule,v) end
  s=0; for _,row in pairs(rule) do s = s + 1 - l.chebyshev(row, self.cols.y) end
  return s/#bins,rule end
         
function DATA:rules(      good,bins,indx)
  good={}
  bins,indx = self:bins()
  bins = l.sort(bins,l.down"mu")
  for i = 1, min(the.beam, #bins) do push(good, bins[i]) end
  for _,set in pairs(l.powerset(good)) do
    s,rule = self:_combine(set) end end

--  see
-----------------------------------------------------------------------------------------
---       _    _  
--      (/_  (_| 
--            _| 
local eg={}

function eg.help(_) 
  print("./rule.lua [help|data|bins|grow] [csv]") end

function eg.data(train,     d,m) 
  d = DATA.new():read(the.train):sort()  
  l.shuffle(d.rows)
  m = 1
  for n,row in pairs(d.rows) do 
    if n % 30 ==1 then  print(n,o(row),o(l.chebyshev(row,d.cols.y))) end end  end

function eg.bins(train,     d,last) 
  d = DATA.new():read(the.train):sort()  
  for _,bin in pairs(d:bins()) do 
    if bin.name ~= last then print"" end
    print(o{n=bin.n,mu=bin.mu},bin) 
    last = bin.name end end

function eg.rule(train,     d,last) 
  d = DATA.new():read(the.train):sort()  
  d:rules()
end

if pcall(debug.getlocal, 4, 1)
then return {DATA=DATA}
else math.randomseed(the.seed)
     eg[ arg[1] or "help" ]( arg[2] or the.train )
end 

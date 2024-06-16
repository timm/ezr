local l=require"lib"
local calc=require"calc"
local the,help=l.settings[[
rulr2.lua : a small range learner
(c) 2024, Tim Menzies, timm@ieee.org, BSD-2 license

Options:
  -b --big     a big number       = 1E30
  -s --seed    random number seed = 1234567891
  -t --train   train data         = ../data/misc/auto93.csv ]]

local NUM  = {} -- info on numeric columns
local SYM  = {} -- info on symbolic columns
local DATA = {} -- place to store all the columns 
local COLS = {} -- factory to make NUMs and SYMs

-----------------------------------------------------------------------------------------
function NUM.new(name,pos)
  return l.is(NUM, {name=name, pos=pos, n=0,
                   mu=0, m2=0, sd=0, lo=1E30, hi= -1E30,
                   best = (name or ""):find"-$" and 0 or 1}) end

-----------------------------------------------------------------------------------------
function SYM.new(name,pos)
  return l.is(SYM, {name=name, pos=pos, n=0,
                   seen={}, mode=nil, most=0}) end

function NUM:add(x,     d)
  if x ~= "?" then
    self.n  = 1 + self.n
    self.lo = math.min(x, self.lo)
    self.hi = math.max(x, self.hi)
    self.mu, self.m2, self.sd = calc.welford(x, self.n, self.mu, self.m2) end
  return x end

function SYM:add(x)
  if x ~= "?" then
    self.n = 1 + self.n
    self.seen[x] = 1 + (self.seen[x] or 0)
    if self.seen[x] > self.most then
      self.most, self.mode = self.seen[x], x end end end

-----------------------------------------------------------------------------------------
function NUM:norm(x)
  return x=="?" and x or (x - self.lo) / (self.hi - self.lo + 1/the.big) end

function SYM:mid() return self.mode end
function NUM:mid() return self.mu end

function SYM:div() return calc.entropy(self.seen) end
function NUM:div() return self.sd end

-----------------------------------------------------------------------------------------
function COLS.new(names,     self,col)
  self = l.is(COLS, { all={}, x={}, y={}, names=names })
  for n,s in pairs(names) do self:newColumn(n,s) end
return self end

function COLS:newColumn(n,s,    col)
  col = (s:find"^[A-Z]" and NUM or SYM).new(s,n)
  l.push(self.all,col)
  if not s:find"X$" then
    l.push(s:find"[-+!]$" and self.y or self.x, col) end end

function COLS:add(row,        x)
  for _,cols in pairs{self.x, self.y} do
    for _,col in pairs(cols) do
       x = row[col.pos]
       if x ~= "?" then col:add(row[col.pos]) end end end
  return row end

-----------------------------------------------------------------------------------------
function DATA.new(src,  names,      cols)
  cols = names and COLS.new(names) or nil
  return l.is(DATA,{rows={},  cols=cols}) end

function DATA:read(file) for   row in l.csv(file) do self:add(row) end; return self end
function DATA:load(lst)  for _,row in pairs(lst)  do self:add(row) end; return self end

function DATA:add(row)
  if   self.cols
  then l.push(self.rows, self.cols:add(row))
  else self.cols = COLS.new(row) end 
  return self end

function DATA:mids(cols)
  return l.map(cols or self.cols.y, function(col) return l.rnd(col:mid()) end) end

-------------------------------------------------------------------------------
math.randomseed(the.seed)
return {the=the, lib=l,DATA=DATA,SYM=SYM,NUM=NUM,COLS=COLS}

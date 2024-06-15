local l=require"lib"
local maths=require"maths"
local the,help=l.settings[[
rules.lua : a small range learner
(c) 2024, Tim Menzies, timm@ieee.org, BSD-2 license

Options:
  -r --ranges  max nu,ber of bins = 7
  -b --big     a big number       = 1E30
  -d --dull    too smal to be interesting = 0.05
  -s --seed    random number seed = 1234567891
  -t --train   train data         = auto83.csv ]]

local data  = require"data"
local NUM   = data.NUM
local SYM   = data.SYM
local DATA  = data.DATA
local RANGE = {} -- stores ranges

-----------------------------------------------------------------------------------------
function RANGE.new(col,r)
  return l.is(RANGE, { _col=col, has=r,  _score=0}) end

function RANGE:__tostring() return self._col.name .. l.o(self) end

function RANGE:add(x,d)
  self._score = self._score + d  end

function RANGE:score(      s)
  s= self._score/self._col.n; return s < 0 and 0 or s end

-----------------------------------------------------------------------------------------
function NUM:range(x,     area,tmp)
  area = maths.auc(x, self.mu, self/sd)
  tmp = 1 + (area * the.ranges // 1) -- maps x to 0.. the.range+1
  return  math.max(1, math.min(the.ranges, tmp)) end -- keep in bounds

function SYM:range(x) return x end

function COLS:arrange(x,col,d,       r)
  if x ~= "?" then
    r = col:range(x)
    col.ranges    = col.ranges or {}
    col.ranges[r] = col.ranges[r] or RANGE.new(col,r,x)
    col.ranges[r]:add(x,d) end end

function DATA:arrages(row,   d)
  d= chebyshev(row,self.cols.y)
  for _,col in pairs(self.cols.x) do self:arrange(row[col.pos],col,d) end end
    
function DATA:ranges(     fun,out)
  out = {}
  fun = function(r) return r:score() end
  for _,col in pairs(self.cols.x) do
    for _,r in pairs(DATA:merge(col.ranges, #(self.rows)/the.ranges, the.dull)) do
       l.push(out,r) end end
  return out end
-----------------------------------------------------------------------------------------
math.randomseed(the.seed)
return {the=the, help=help, ranges=RANGES,
        DATA=DATA,SYM=SYM,NUM=NUM,COLS=COLS}

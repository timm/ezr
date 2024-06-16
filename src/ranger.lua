local l    = require"lib"
local calc = require"calc"
local data = require"data"
local the,help=l.settings[[
ranger.lua : a small range learner
(c) 2024, Tim Menzies, timm@ieee.org, BSD-2 license

Options:
  -b --big     a big number         = 1E30
  -d --dul     small amount         = 0.01
  -r --ranges  max number of ranges = 7
  -s --seed    random number seed   = 1234567891
  -t --train   train data           = ../data/misc/auto93.csv ]]

local NUM, SYM, DATA = data.NUM, data.SYM, data.DATA

local RANGE= {} -- stores ranges

-----------------------------------------------------------------------------------------
function RANGE.new(col,r)
  return l.is(RANGE, { _col=col, has=r,  score=0}) end

function RANGE:__tostring() return self._col.name .. l.o(self) end

function RANGE:add(x,d) self.score = self.score + d  end

----------------------------------------------------------------------------------------
function DATA:sort(     fun)
  fun = function(row) return calc.chebyshev(row,self.cols.y) end
  self.rows = l.sort(self.rows, function(a,b) return fun(a) < fun(b) end)
  return self end

function DATA:ranges(row,d,  all) -- e.g. calc.chebyshev(row,self.cols.y)
  for _,col in pairs(self.cols.x) do 
    col.ranges = col.ranges or {}
    self:range(row[col.pos],col,d) end end
    
function DATA:range(x,col,d       r)
  if x ~= "?" then
    r = col:range(x,the.ranges)
    col.ranges[r] = all[r] or RANGE.new(col,r)
    col.ranges[r]:add(x,d) end end

function DATA:ranges(     fun,out)
  out = {}
  fun = function(r) return r:score() end
  for _,col in pairs(self.cols.x) do
    for _,r in pairs(DATA:merge(col.ranges, #(self.rows)/the.ranges, the.dull)) do
       l.push(out,r) end end
  return out end

return {the=the, DATA=DATA}

local l    = require"lib"
local calc = require"calc"
local data = require"data"
local the,help=l.settings[[
ranger.lua : a small range learner
(c) 2024, Tim Menzies, timm@ieee.org, BSD-2 license

Options:
  -b --big     a big number         = 1E30
  -r --ranges  max number of ranges = 7
  -s --seed    random number seed   = 1234567891
  -t --train   train data           = auto83.csv ]]

local DATA=data.DATA


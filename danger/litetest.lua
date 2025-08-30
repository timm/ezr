-- litetest.lua
local l = require "lite"
local r2, say

function r2(x) return math.floor(x*100+0.5)/100 end
function say(str,want,fun) print(str); assert want==fun() end

local eg = {}

function eg.Sym()
  f=function() return r2(l.like(l.adds("aaaabbc", l.Sym()), "a")) end
  say("Sym: demo of likelihood", -0.81,f) end

function eg.num(     f0,f1,f2): 
  f0 = function() return adds(random.gauss(10,2) for _ in range(1000)) end
  f1 = function() return round(f0().mu, 1.99) end
  f2 = function() return round(f0().sd, 10) end
  say("Num: check Num sample tracks gaussians", 1.99, f1)
  say("Num: check Num sample tracks variance",  10,   f2) end

def eg__checkData():
  "check we can read csv files from disk"
  try: Data(csv(the.file))
  except Exception as _ : print(the.file)

def eg__data():
  "check we can read csv files from disk"
  print(x := round(sum(y.mu for y in Data(csv(the.file)).cols.y),2))
  #assert x == 3009.84


-- runner
for name, t in pairs(eg) do
  local help, fn = t[1], t[2]
  print(("\n== %s == %s"):format(name, help))
  local ok, err = pcall(fn)
  if not ok then print("❌", err) else print("✅ ok") end end

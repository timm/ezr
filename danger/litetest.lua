-- litetest.lua
from lite import *
from stats import *

def eg__the(): 
  "show config"
  print(the)

def eg__csv():
  "read from csv files"
  [pout(x) for x in list(csv(the.file))[::30]]

-- runner
for name, t in pairs(eg) do
  local help, fn = t[1], t[2]
  print(("\n== %s == %s"):format(name, help))
  local ok, err = pcall(fn)
  if not ok then print("❌", err) else print("✅ ok") end end

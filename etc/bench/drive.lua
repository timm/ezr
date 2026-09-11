P, Few, Start, Stop, SEED = 2, 128, 4, 50, 1
dofile("slice.lua")
local function atom(s) return tonumber(s) or s end
local function split(s,    t) t={}
  for w in s:gmatch("[^,]+") do t[#t+1]=w end
  return t end
local raw = {}
for line in io.lines("data.csv") do
  if line:match("%S") then raw[#raw+1] = split((line:gsub("%s+$",""))) end end
local src = {raw[1]}
for i=2,#raw do local r={}
  for j=1,#raw[i] do r[j-1] = atom(raw[i][j]) end
  src[#src+1] = r end
local t = Tbl(src)
local R = t.rows
local xs = {}
for _,a in ipairs(t.x) do xs[#xs+1]=a end
local ys = {}
for _,aw in ipairs(t.y) do ys[#ys+1] = string.format("(%d, %d)", aw[1], aw[2]) end
print(string.format("n %d x [%s] y [%s]", #R, table.concat(xs,", "), table.concat(ys,", ")))
print(string.format("ymu %.6f", ymu(t,R)))
print(string.format("ydist0 %.6f", ydist(t,R[1])))
print(string.format("xdist01 %.6f", xdist(t,R[1],R[2])))
local dv = {}
for at=0,#t.names-1 do if t.cols[at] then dv[#dv+1]=string.format("%.6f", div(t.cols[at])) end end
print("div "..table.concat(dv," "))
local md = {}
for _,at in ipairs(t.x) do md[#md+1]=string.format("%d:%.6f", at, mids(t)[at]) end
print("mids "..table.concat(md," "))
local g = {}
for line in io.lines("gauss.txt") do
  local row={} ; for w in line:gmatch("[^,]+") do row[#row+1]=tonumber(w) end
  g[#g+1]=row end
print(string.format("same %d %d", same(g[1],g[2]) and 1 or 0, same(g[1],g[3]) and 1 or 0))
local t0 = os.clock()
local s = 0.0
for _=1,tonumber(arg[1]) do
  for i=1,120 do for j=i+1,120 do s = s + xdist(t,R[i],R[j]) end end end
print(string.format("W1 %.6f", s))
local s2 = 0.0
for _=1,tonumber(arg[2]) do s2 = s2 + ydist(t, acquire(t)[1]) end
print(string.format("W2 %.6f", s2))
print("SEED "..math.floor(SEED))
io.stderr:write(string.format("secs %.3f\n", os.clock()-t0))

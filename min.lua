#!/usr/bin/env luajit
-- min.lua: eat rows, spit guesses.
-- (c) 2026 Tim Menzies <timm@ieee.org> MIT license.
--
-- options:
--   budget=50   rows we may label, all up
--   check=5     of that budget, saved for the unseen rows
--   seed=1      random number seed
local abs,exp,max,min,sqrt = math.abs,math.exp,math.max,math.min,math.sqrt
local _ENV = setmetatable({},{__index=_G}) -- `function f` defines & exports
if setfenv then setfenv(1,_ENV) end

the = {budget=50, check=5, seed=1,
       file="../src/ezr-lua/data/auto93.csv"}

--## 1. eat: rows off disc; mu,n,m2 per num, seen[v]+1 per sym -
function Col(txt,at) -- uppercase name = NUM, else SYM; +- = a goal
  return {at=at, txt=txt, n=0, mu=0, m2=0, seen={},
          num=txt:find"^%u", y=txt:find"[-+]$",
          goal=txt:find"-$" and 0 or 1} end

function add(col,v,   d) -- show V to COL
  if v ~= "?" then col.n = col.n + 1
    if not col.num then col.seen[v] = 1 + (col.seen[v] or 0)
    else d = v - col.mu                        -- Welford
      col.mu = col.mu + d/col.n
      col.m2 = col.m2 + d*(v - col.mu) end end
  return v end

function cols(names,   all,x,y) -- sort the header into roles
  all, x, y = {}, {}, {}
  for at,s in ipairs(names) do
    all[at] = Col(s,at)
    if all[at].y then y[#y+1] = all[at]
    elseif s:sub(-1) ~= "X" then x[#x+1] = all[at] end end
  return all, x, y end

function rows(names,src,   d) -- fold rows into fresh columns
  d = {rows={}}
  d.cols, d.x, d.y = cols(names)
  for _,row in ipairs(src) do
    d.rows[#d.rows+1] = row
    for _,c in ipairs(d.cols) do add(c, row[c.at]) end end
  return d end

function eat(file,   names,src,t) -- row 1 names the cols, rest are data
  names, src = nil, {}
  for line0 in io.lines(file) do
    local line = line0:gsub("\239\187\191","")  -- drop any BOM (5.5: const)
    if line:match"%S" then
      t = {}
      for s in (line..","):gmatch"(.-)," do t[#t+1] = tonumber(s) or s end
      if names then src[#src+1] = t else names = t end end end
  return rows(names, src) end

--## distance --------------------------------------------------
function norm(col,v) -- to 0..1, by the logistic curve; syms do not scale
  if not col.num or v == "?" then return v end
  return 1/(1+exp(-1.7*max(-3,min(3,
         (v-col.mu)/(1e-32+sqrt(col.m2/max(1,col.n-1))))))) end

function gap(col,a,b) -- one column's two values; unknown = far
  if a == "?" or b == "?" then return 1 end
  if col.num then return norm(col,a) - norm(col,b) end
  return a ~= b and 1 or 0 end

function ydist(d,row,   s,g) -- goals to heaven; 0 = best
  s = 0
  for _,c in ipairs(d.y) do
    g = norm(c,row[c.at]) - c.goal; s = s + g*g end
  return sqrt(s/#d.y) end

function xdist(d,r1,r2,   s,g) -- two rows, over the x columns
  s = 0
  for _,c in ipairs(d.x) do
    g = gap(c, r1[c.at], r2[c.at]); s = s + g*g end
  return sqrt(s/#d.x) end

function mid(d,rs,   out,c,hi) -- centroid: each column's mean, or its mode
  out = {}
  for _,col in ipairs(d.cols) do
    c = Col(col.txt, col.at)
    for _,row in ipairs(rs) do add(c, row[col.at]) end
    out[col.at], hi = c.mu, -1
    for k,n in pairs(c.seen) do
      if n > hi then out[col.at], hi = k, n end end end
  return out end

--## 2. spit: budget random labels, then rank what is left -----
function shuffle(t,   u,j) -- Fisher-Yates; copies first
  u = {}
  for _,v in ipairs(t) do u[#u+1] = v end
  for i = #u,2,-1 do j = math.random(i); u[i],u[j] = u[j],u[i] end
  return u end

function keysort(t,f,   p,u) -- sort by f(v), computed once per item
  p, u = {}, {}
  for i,v in ipairs(t) do u[i], p[v] = v, f(v) end
  table.sort(u, function(a,b) return p[a] < p[b] end)
  return u end

function spit(d,   todo,lab,b,r,n,k,out) -- label, split best vs rest, rank
  math.randomseed(the.seed)
  todo = shuffle(d.rows)
  n    = the.budget - the.check              -- keep `check` in hand
  lab  = {}
  for _ = 1,n do lab[#lab+1] = table.remove(todo) end
  lab = keysort(lab, function(row) return ydist(d,row) end)
  k = math.floor(sqrt(#lab))                 -- sqrt best, rest rest
  b, r = {}, {}
  for i,row in ipairs(lab) do
    local t = i <= k and b or r; t[#t+1] = row end
  b, r = mid(d,b), mid(d,r)
  todo = keysort(todo, function(row)
           return xdist(d,row,b) - xdist(d,row,r) end)
  out = todo[1]                              -- label `check`, keep the best
  for i = 1,the.check do
    if ydist(d,todo[i]) < ydist(d,out) then out = todo[i] end end
  return out, lab[1] end

if arg and arg[0] and arg[0]:find"min%.lua$" then
  local d = eat(the.file)
  local got, seen = spit(d)
  print(("labels=%s  picked=%.3f  bestOfBudget=%.3f"):format(
        the.budget, ydist(d,got), ydist(d,seen))) end

return _ENV

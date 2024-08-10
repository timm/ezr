#!/usr/bin/env lua
-- vim : set ts=2 sw=2 sts=2 et : 
local help=[[
be.lua: stuff
(c) 2024 Tim Menzies, <timm@ieee.org>, BSD-2

USAGE:
  lua be.lua [-h] [-[bBcst] ARG] 

OPTIONS:
  -b int     max number of bins =  16
  -B float   threshold for best =  .5
  -c float   cohen small effect =  .35
  -h         show help
  -s int     random number seed =  1234567891
  -t file    csv data file      =  ../../../timm/moot/optimize/misc/auto93.csv
]]

local DATA,BIN,COLS,ROW,go = {},{},{},{},{}
local cells, coerce, csv, fmt, new, o, oo, push, sort, the

the = { cohen = .35
      , bins  = 16
			, Best  = .5
      , seed  = 1234567891
      , train = "../../moot/optimize/misc/auto93.csv"
      }

fmt = string.format

function push(t,x) t[1+#t] = x; return x end

function sort(t,fun) table.sort(t,fun); return t end

function new(klass,obj) klass.__index=klass; return setmetatable(obj,klass) end

function oo(x) print(o(x)) end

function o(x,    u)
  if type(x) == "number" then return fmt("%g",x) end
  if type(x) ~= "table"  then return tostring(x) end
  u={}; if   #x > 0 
        then for k,v in pairs(x) do u[1+#u] = o(v) end 
        else for k,v in pairs(x) do u[1+#u] = fmt("%s=%s", k, o(v)) end
             table.sort(u) end
  return "{" .. table.concat(u,", ") .. "}" end 

function coerce(s,    fun)
  function fun(s) return s=="true" and true or (s ~= "false" and s) or false end
  return math.tointeger(s) or tonumber(s) or fun(s:match"^%s*(.-)%s*$") end

function csv(sFilename,fun,      src,s,cells)
  function cells(s,    t) 
    t={}; for s1 in s:gmatch("([^,]+)") do t[1+#t]=coerce(s1) end; return t end
  src = io.input(sFilename)
  while true do
    s = io.read()
    if s then fun(cells(s)) else return io.close(src) end end end
-- ----------------------------------------------------------------------------
function ROW:new(t)
  return new(ROW,{cells=t, score=nil}) end
-- ----------------------------------------------------------------------------
function COLS.new(i,names)
  i = new(COLS,{names=names, x={}, y={}, lo={}, hi={}}) 
  for c,s in pairs(i.names) do
    if not s:find"X$" then
      if   s:find"^[A-Z].*" then i.lo[c] = 1E32; i.hi[c] = -1E32 end 
      if   s:find"-$"    then i.y[c] = 0 
      else if s:find"+$" then i.y[c] = 1 
      else i.x[c] = 1  end end end end
  return i end

function COLS.add(i,row,      z)
  for c,lo in pairs(i.lo) do
    z = row.cells[c]
    if z ~= "?" then
      i.lo[c] = math.min(lo,      z)
      i.hi[c] = math.max(i.hi[c], z) end end 
  return row end 
   
function COLS.chebyshev(i,row,    x,d)
  d=0
  for c,goal in pairs(i.y) do
    x = (row.cells[c] - i.lo[c]) / (i.hi[c] - i.lo[c])
    d = math.max(d, math.abs(x - goal)) end 
  return d end 
-- ----------------------------------------------------------------------------
function DATA:new(_) return new(DATA, {cols=nil, rows={}}) end

function DATA.load(i,lst) 
  for _,row in pairs(lst or {}) do i:add(row) end 
  return i end

function DATA.read(i,file) 
  csv(file, function(row) i:add(ROW:new(row)) end) 
  return i end

function DATA.add(i,row)
  if   i.cols
  then push(i.rows, i.cols:add(row)) 
  else i.cols = COLS:new(row.cells) end end

function DATA.sort(i,    f,n)
  f = function(row) return i.cols:chebyshev(row) end
  i.rows = sort(i.rows, function(a,b) return f(a) < f(b) end) 
  for j,row in pairs(i.rows) do
    if j % 30 == 0 then print(j, o(row),f(row)) end end 
  n = (#i.rows)^the.Best // 1 
  return f( i.rows[n] ) end 

-- function DATA.allBins(i)
--   for c,_ in pairs(i.cols.x) do
-- 		i:bins(i.rows, function(row) return row.cells[c] end)
-- end

function DATA.bins(i,rows,xfun,yfun,     my,bins)
  my, rows = i:my(i:sortedRows(rows,xfun), xfun, yfun)
  bins = { BIN:new(xfun(rows[1])) }
  for r,row in pairs(rows) do
    if r > my.skip 
    then i:theCurrentBin(my,r,xfun(row),rows,bins,xfun)
          :add( yfun(row), my.seen) end end
  return bins end

function DATA:theCurrentBin(my,r,x,rows,bins,xfun)
  if r < #rows - my.gap then
    if x ~= xfun( rows[r+1] )  then
      if bins[#bins].n >= my.gap then  
        if x - bins[#bins].lo >= my.sd*the.cohen then 
          push(bins, BIN:new(x,bins[#bins])) end end end end
  return bins[#bins] end

function DATA.sortedRows(i,rows,xfun,       q)
  q = function(row) return xfun(row)=="?" and -1E32 or xfun(row)  end
  return sort(rows, function(row1,row2) return q(row1) < q(row2) end) end

function DATA.my(i,rows,xfun,yfun,      seen,x,y,n,skip) 
  seen={}
  for r,row in pairs(rows) do
    x,y = xfun(row), yfun(row)
    if   x == "?" 
    then skip = r 
    else seen[y] = 1 + (seen[y] or 0) end end 
  n = #rows - skip + 1
  return {skip= skip, 
          seen = seen,
          gap  = (n / the.bins) //1,
          sd   = (rows[(skip+1+ .9*n)//1] - rows[(skip+1+ .1*n)//1]) /2.58
         }, rows end
-- ----------------------------------------------------------------------------
function BIN.new(i,x,b4)
  i = new(BIN,{n=0, lo=x, seen={}})
  if b4 then
    i.last = b4
    b4.next = i end
  return i end

function BIN.add(i,y,ys)
  i.seen[y] = (i.seen[y] or 0) + 1/ys[y]
  i.n = i.n + 1 end
-- ----------------------------------------------------------------------------
go.h   = function(_) print("\n" .. help) end
go.c   = function(x) the.cohen = x end
go.b   = function(x) the.bins  = x end
go.B   = function(x) the.Best  = x end
go.s   = function(x) the.seed  = x; math.randomseed(x) end
go.t   = function(x) the.train = x end
go.the = function(_) oo(the) end
go.csv = function(_) csv(the.train, oo) end
go.data= function(_) 
  d = DATA:new():read(the.train)
	oo(d:sort())
  -- for k,v in pairs(d.cols.lo) do 
  --   print(k,d.cols.names[k],v, d.cols.hi[k]) end end
	end

for j,s in pairs(arg) do
  math.randomseed(the.seed)
  if go[s:sub(2)] then go[s:sub(2)](coerce(arg[j+1] or "")) end end 

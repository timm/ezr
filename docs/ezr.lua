local b4={}; for k, _ in pairs(_ENV) do b4[k]=k end
local l,b4,help = {}, {}, [[
ezr.lua easier AI
(c) 2024, Tim Menzies, <timm@ieee.org>]]
--[[
The _difference_ between things can sometimes be _more informative_ 
than the things themelves. For example, suppose we are want to find good 
things within a 1000 examples, but there is no time to look at all that data.
Let's  start by 
   
- labelling (say) 10  examples;
- sorting them  into `best`  and `rest`;
- building a model that can guess  `b=prob(best)` and `r=prob(rest)`. 
The remaining  990 examples can be sorted by the formula `-b/r`, the 
worse can be pruned, and the top one labelled.  Repeating this  a few 
times results in  a model that knows `best` from `rest'. --]]

local options={k=1, m=2, bins=10, file="../data/auto03.csv",
                seed=1234567891,start=10, repeats=20, prunes=0.2}

--[[
## Step1: Read in some data
  
To make all this work, we need to load  some sample data from disk. In 
these csv files, the column names in row1 indicate if the columns are:
     
- numeric or symbolic (numeric columns start with upper case);
- goals we want to minimize of maximize (these end with `+` or `-`);
- things  we just want to skip over (these end with `X`). ]]--

local NUM,SYM
local is={}
function is.what(s)       return s:find"^[A-Z]" and NUM or SYM end
function is.goal(s)       return s:find"[!+-]$" end
function is.minimize(s)   return s:find"-$" end
function is.ignorable(s)  return s:find"X$" end
function is.klass(s)      return s:find"!$" end


function NUM(   s,n) 
  return {is=NUM, txt=s or " ", at=n or 0, n=0, mu=0, m2=0, hi=-1E30, lo=1E30,
          heaven = (s or ""):find"-$" and 0 or 1} end 

function SYM(  s,n)
  return {is=SYM, txt=s or " ", at=n or 0, n=0, has={}, mode=nil, most=0} end 

-- udpate NUM or SYM
local function col(col1, x)
  function num(     d)
    d      = x - col1.mu
    col1.mu = col1.mu + d/col1.n
    col1.m2 = col1.m2 + d*(x - col1.mu)
    col1.lo = math.min(x, col1.lo)
    col1.hi = math.max(x, col1.hi) end
  function sym()
    col1.has[x] = 1 + (col1.has[x] or 0)
    if col1.has[x] > col1.most then 
      col1.most, col1.mode = col1.has[x], x end end
  if x ~= "?" then 
    col1.n = col1.n + 1
    (col1.is==NUM and num or sym)() end end

-- COLS are places to store NUMs or SYMs
local COLS,cols
local function COLS(as,      cols0,col)
  cols0 = {is=COLS, all={}, x={}, y={}, klass=nil}
  for n,s in pairs(as) do
    col = l.push(cols0.all,  is.what(s)(s,n))
    if not is.ignorable(s) then
      l.push( is.goal(s) and cols0.y or cols0.x, col)
      if is.klass(s) then cols0.klass = col end end end 
  return cols0 end 

function cols(cols1,a)
  for _,cols in pairs(cols1.cols.x, cols1.cols.y) do
    for _,col1 in pairs(cols) do
      col(col1, a[col.at]) end end 
  return a end

-- update NUM or SYM


-- DATA are places to store cols and rows of data. 
local DATA,data,d2h,norm
function DATA(src,  order,    data)
  data0 = {rows={}, cols=nil}
  if   type(src)=="string"
  then for   a in l.csv(src) do data(data,a) end
  else for _,a in pairs(src) do data(data,a) end end
  if order then l.keysort(data.rows, d2h, data) end
  return data end

function data(data1, a)
  if   data1.cols
  then l.push(data1.rows, cols(data1.cols, a))
  else data1.cols = COLS(a) end end
  
-- Inside DATA, rows can be sorted by how the distance of
-- goal values to `heaven` (0 for minimize, 1 for maximize).
function d2h(a,data,     n,dist)
  n,dist = 0,0
  for _,col1 in pairs(data.cols.y) do
    n    = n+1
    dist = dist + math.abs(col1.heaven - norm(col1, a[col.at]))^2 end
  return (dist/n)^0.5 end

function norm(col1, x) return (x-col1.lo)/ (col1.hi - col1.lo + 1E-30) end


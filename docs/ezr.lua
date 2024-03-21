
local b4 = {}; for k, _ in pairs(_ENV) do b4[k]=k end
local help = [[
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

local l,the,eg = {},{},{}
local NUM,SYM,COLS,DATA,BIN = {},{}

local is={}
function is.what(s)       return s:find"^[A-Z]" and NUM or SYM end
function is.goal(s)       return s:find"[!+-]$" end
function is.minimize(s)   return s:find"-$" end
function is.ignorable(s)  return s:find"X$" end
function is.klass(s)      return s:find"!$" end

function NUM:new(   s,n) 
  return setmetatable({txt=s or " ", at=n or 0, n=0, mu=0, m2=0, hi=-1E30, lo=1E30,
          heaven = ako.minimize(s or "") and 0 or 1},NUM) end 

function SYM:new(  s,n)
  return setmetatable({txt=s or " ", at=n or 0, n=0, has={}, mode=nil, most=0},SYM) end 

function NUM:add(x,     d)
  if x ~="?" then
    self.n = self.n + 1
    d      = x - self.mu
    self.mu = col1.mu + d/self.n
    self.m2 = col1.m2 + d*(x - self.mu)
    self.lo = math.min(x, self.lo)
    self.hi = math.max(x, self.hi) end end

function SYM:add(x)  
  if x ~="?" then
    self.n = self.n + 1
    self.has[x] = 1 + (self.has[x] or 0)
    if self.has[x] > self.most then 
      self.most, self.mode = self.has[x], x end end end

-- COLS are places to store NUMs or SYMs
local COLS={}
function COLS:new(as,      col,all,x,y,klass)
  all,x,y,klass = {},{},{},{}
  for n,s in pairs(as) do
    col = l.push(all,  is.what(s)(s,n))
    if not is.ignorable(s) then
      l.push( is.goal(s) and  y or  x, col)
      if is.klass(s) then  klass = col end end end 
  return {all=all, x=x, y=y, klass=klass} end 

function COLS:add(a)
  for _,cols in pairs(self.cols.x, self.cols.y) do
    for _,col in pairs(cols) do
      col.add(a[col.at]) end end 
  return a end

 
-- DATA are places to store cols and rows of data. 
local DATA,data,d2h,norm
function DATA:new (src,  order,    rows)
  self.rows={}
  if   type(src)=="string"
  then for   a in l.csv(src) do self:add(a)  end
  else for _,a in pairs(src) do self:add(a)   end end
  if order then l.keysort(data.rows, d2h, self) end
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

function l._new(klass,...)   
  local inst=setmetatable({},klass);
  return setmetatable(klass.new(inst,...) or inst,klass) end

function l.obj(s, t) 
  t={__tostring = function(x) return s..o(x) end} 
  t.__index = t;return setmetatable(t,{__call=l._new}) end
#!/usr/bin/env lua
-- <!-- vim : set ts=2 sts=2 et : -->
--       __                __                
--      /\ \              /\ \__             
--      \_\ \      __     \ \ ,_\     __     
--      /'_` \   /'__`\    \ \ \/   /'__`\   
--     /\ \L\ \ /\ \L\.\_   \ \ \_ /\ \L\.\_ 
--     \ \___,_\\ \__/.\_\   \ \__\\ \__/.\_\
--      \/__,_ / \/__/\/_/    \/__/ \/__/\/_/
                                      
local NUM,SYM,DATA,_COLS = {},{},{},{}

local l=require"lib"
local   csv,   map,   new,   o,   oo,   push,   sort = 
      l.csv, l.map, l.new, l.o, l.oo, l.push, l.sort
local abs,log,max,min = math.abs, math.log, math.max, math.min

-----------------------------------------------------------------------------------------
--       _  ._   _    _.  _|_   _  
--      (_  |   (/_  (_|   |_  (/_ 

function SYM.new(name,pos) return new(SYM, {name=name, pos=pos, n=0, seen={}}) end

function NUM.new(name,pos)
  return new(NUM, {name=name, pos=pos, n=0, mu=0, m2=0, sd=0, lo=1E30, hi=-1E30,
                   goal = (name or ""):find"-$" and 0 or 1}) end

function _COLS.new(names,    all,x,y,col) 
  all,x,y = {},{},{}
  for i,s in pairs(names) do 
    col = push(all, (s:find"^[A-Z]" and NUM or SYM).new(s,i))
    if not s:find"X$" then push(s:find"[!+-]$" and y or x,col) end end
  return new(_COLS, {names=names, all=all, x=x, y=y}) end

function DATA.new(  names) 
  return  new(DATA, {rows={}, cols=names and _COLS.new(names) or nil}) end
-----------------------------------------------------------------------------------------
--       ._   _    _.   _| 
--       |   (/_  (_|  (_| 

function DATA:read(file) for   row in csv(file) do self:add(row) end; return self end
function DATA:load(t)    for _,row in pairs(t)  do self:add(row) end; return self end
-----------------------------------------------------------------------------------------
--            ._    _|   _.  _|_   _  
--       |_|  |_)  (_|  (_|   |_  (/_ 
--            |                       

function DATA:add(t) 
  if self.cols then push(self.rows, self.cols:add(t)) else 
     self.cols = _COLS.new(t) end end

function _COLS:add(t)
  for _,cs in pairs{self.x,self.y} do for _,c in pairs(cs) do c:add(t[c.pos]) end end 
  return t end

function SYM:add(x)
  if x ~= "?" then
    self.n  = self.n+1
    self.seen[x] = 1 + (self.seen[x] or 0) end end 

function NUM:add(x,    d)
  if x ~= "?" then
    self.n  = self.n + 1
    self.mu, self.m2, self.sd = l.welford(x, self.n, self.mu, self.m2)
    if x > self.hi then self.hi=x end
    if x < self.lo then self.lo=x end end end
-----------------------------------------------------------------------------------------
--        _.        _   ._     
--       (_|  |_|  (/_  |   \/ 
--         |                /  

function NUM:norm(x) return x=="?" and x or (x - self.lo)/(self.hi - self.lo) end
               
-----------------------------------------------------------------------------------------
--      |  o  |    _  
--      |  |  |<  (/_ 

function DATA:like(row,nall,nh,  k,m,    prior,x,like,out)
  out, prior = 0, (#self.rows + (k or 1)) / (nall + (k or 1)*nh)
  for _,col in pairs(self.cols.x) do
    x = row[col.pos]
    if x ~= "?" then
      like = col:like(x,prior,m)
      if like > 0 then out = out + math.log(like) end end end
  return out + math.log(prior) end 

function SYM:like(x, prior,  m)
  return ((self.has[x] or 0) + (m or 2)*prior)/(self.n + (m or 2)) end

function NUM:like(x,_,      nom,denom)
  local mu, sd =  self:mid(), (self:div() + 1E-30)
  nom   = math.exp(1)^(-.5*(x - mu)^2/(sd^2))
  denom = (sd*2.5 + 1E-30)
  return nom/denom end
                 
-----------------------------------------------------------------------------------------
--       _|  o   _  _|_ 
--      (_|  |  _>   |_ 

function SYM:dist(x,y)
  return  (x=="?" and y=="?" and 1) or (x==y and 0 or 1) end

function NUM:dist(x,y)
  if x=="?" and y=="?" then return 1 end
  x,y = self:norm(x), self:norm(y)
  if x=="?" then x=y<.5 and 1 or 0 end
  if y=="?" then y=x<.5 and 1 or 0 end
  return math.abs(x-y) end

function DATA:sort(      d)
  d = function(row) return  l.chebyshev(row,self.cols.y) end
  self.rows = sort(self.rows, function(a,b) return  d(a) < d(b) end) 
  return self end

function DATA:dist(row1,row2,  p,cols)
  return l.minkowski(row1,row2,(p or 2), cols or self.cols.x) end

function DATA:around(row,  rows,p,cols,d)
  d = function(other) return self:dist(row,other,p,cols) end
  return sort(rows or self.rows,function(a,b) return d(a) < d(b) end) end

-----------------------------------------------------------------------------------------
--        _    _  
--       (/_  (_| 
--             _| 

local eg={}

function eg.help(_) 
  print("lua data.lua [help|csv|cols|data] [csv]") end

function eg.csv(train,    n) 
  n=0; for row in csv(train) do 
         n=n+1; if n % 50==0 then print(n,o(row)) end end end

function eg.cols(train,     d) 
  d = DATA.new():read(train)
  for _,col in pairs(d.cols.y) do oo(col) end end

function eg.data(train,     d,m) 
  d = DATA.new():read(train):sort()
  m = 1
  for n,row in pairs(d.rows) do 
    if n==m then 
      m=m*2
      print(n,o(l.chebyshev(row,d.cols.y)),o(row)) end end end

if   pcall(debug.getlocal, 4, 1) 
then return {DATA=DATA, NUM=NUM, SYM=SYM,eg=eg} 
else eg[ arg[1]  or "help" ](arg[2] or "../data/misc/auto93.csv")
     l.rogues()
end

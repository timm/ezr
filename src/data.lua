#!/usr/bin/env lua
-- <!-- vim : set ts=4 sts=4 et : -->
-- ---------------------------------------------------------------------------------------
-- ## Data layer
local DATA,SYM,NUM,COLS = {},{},{},{}
local abs, max, min, rand = math.abs, math.max, math.min, math.random
local l = require"lib"
local the =require"config"

-- ### class NUM
-- Incremental update of summary of numbers.

-- `NUM.new(?name:str, ?pos:int) -> NUM`  
function NUM.new(  name,pos)
  return l.new(NUM,{name=name, pos=pos, n=0, mu=0, m2=0, sd=0, lo=l.inf, hi= -l.inf,
                  goal= (name or ""):find"-$" and 0 or 1}) end

-- `NUM:add(x:num) -> x`
function NUM:add(x,     d)
  if x ~= "?" then
    self.n  = self.n + 1
    d       = x - self.mu
    self.mu = self.mu + d/self.n
    self.m2 = self.m2 + d*(x - self.mu)
    self.sd = self.n<2 and 0 or (self.m2/(self.n - 1))^.5 
    self.lo = min(x, self.lo)
    self.hi = max(x, self.hi)
    return x end end 

-- `NUM:norm(x:num) -> 0..1`
function NUM:norm(x) return x=="?" and x or (x - self.lo)/(self.hi - self.lo) end

-- `NUM:small(x:num) -> bool`
function NUM:small(x) return x < the.cohen * self.sd end

-- `NUM:same(i:NUM, j:NUM) -> bool`   
-- True if statistically insignificantly different (using Cohen's rule).
-- Used to decide if two BINs should be merged.
function NUM.same(i,j,    pooled)
  pooled = (((i.n-1)*i.sd^2 + (j.n-1)*j.sd^2)/ (i.n+j.n-2))^0.5
  return abs(i.mu - j.mu) / pooled <= (the.cohen or .35) end

-- ### class SYM
-- Incremental update of summary of symbols.

-- `SYM.new(?name:str, ?pos:int) -> SYM`  
function SYM.new(  name,pos)
  return l.new(SYM,{name=name, pos=pos, n=0, has={}, most=0, mode=nil}) end

-- `SYM:add(x:any) -> x`
function SYM:add(x,     d)
  if x ~= "?" then
    self.n  = self.n + 1
    self.has[x] = 1 + (self.has[x] or 0)
    if self.has[x] > self.most then self.most,self.mode = self.has[x], x end 
    return x end end

-- ### class DATA
-- Manage rows, and their summaries in columns

-- `DATA.new() -> DATA`
function DATA.new() return l.new(DATA, {rows={}, cols=nil}) end

-- `DATA:read(file:str) -> DATA`   
-- Imports the rows from `file` contents into `self`.
function DATA:import(file) 
  for row in l.csv(file) do self:add(row) end; return self end

-- `DATA:load(t:list) -> DATA`   
-- Loads the rows from `t` `self`.
function DATA:load(t)    
  for _,row in pairs(t)  do self:add(row) end; return self end

-- `DATA:clone(?init:list) -> DATA`     
-- ①  Create a DATA with same column roles as `self`.   
-- ②  Loads rows (if any) from `init`.
function DATA:clone(  init) 
   return DATA:new():load({self.cols.names}) -- ①  
                    :load(init or {}) end    -- ② 

-- `DATA:add(row:list) -> nil`    
-- Create or update  the summaries in `self.cols`.
-- If not the first row, push this `row` onto `self.rows`.
function DATA:add(row)
  if self.cols then l.push(self.rows, self.cols:add(row)) else 
     self.cols = COLS.new(row) end end 

-- `DATA:chebyshev(row:list) -> 0..1`    
-- Report distance to best solution (and _lower_ numbers are _better_).    
function DATA:chebyshev(row,     d) 
  d=0; for _,c in pairs(self.cols.y) do d = max(d,abs(c:norm(row[c.pos]) - c.goal)) end
  return d end
  
function DATA:chebyshevs(  rows,       num)
  num = NUM.new()
  for _,r in pairs(rows or self.rows) do num:add(self:chebyshev(r)) end 
  return num end

-- `DATA:sort() -> DATA`   
-- Sort rows by `chebyshev` (so best rows appear first). 
function DATA:sort()
  table.sort(self.rows, function(a,b) return self:chebyshev(a) < self:chebyshev(b) end)
  return self end 

-- ### class COLS
-- Column creation and column updates.

-- `COLS.new(row: list[str]) -> COLS`
-- Upper case prefix means number (else you are a symbol). 
-- Suffix `X` means "ignore". Suffix "+,-,!" means maximize, minimize, or klass.
function COLS.new(row,    self,skip,col)
  self = l.new(COLS,{names=row, all={},x={}, y={}, klass=nil})
  skip={}
  for k,v in pairs(row) do
    col = l.push(v:find"X$" and skip or v:find"[!+-]$" and self.y or self.x,
                 l.push(self.all, 
                        (v:find"^[A-Z]" and NUM or SYM).new(v,k))) 
    if v:find"!$" then self.klass=col end end
  return self end 

-- `COLS:add(row:list[thing]) -> row`
function COLS:add(row)
  for _,cols in pairs{self.x, self.y} do
    for _,col in pairs(cols) do  col:add(row[col.pos]) end end 
  return row end
------------------------------------------------------------------------------
-- ## Start-up Actions
local eg={}
local copy,o,oo,push=l.copy,l.o,l.oo,l.push

eg["-h"] = function(_) print("lua data.lua --[all,copy,cohen,train,clone] [FILE]") end
eg["-t"] = function(x) the.train= x end

eg["--all"] = function(_) l.all(eg,{"--copy","--cohen","--train","--clone"}) end

eg["--copy"] = function(_,     n1,n2,n3) 
  n1,n2 = NUM.new(),NUM.new()
  for i=1,100 do n2:add(n1:add(rand()^2)) end
  n3 = copy(n2)
  for i=1,100 do n3:add(n2:add(n1:add(l.rand()^2))) end
  for k,v in pairs(n3) do if k ~="_id" then ; assert(v == n2[k] and v == n1[k]) end end
  n3:add(0.5)
  assert(n2.mu ~= n3.mu) end

eg["--cohen"] = function(_,    u,t) 
    for inc = 1,1.25,0.03 do 
      u,t = NUM.new(), NUM.new()
      for i=1,20 do u:add( inc * t:add(rand()^.5))  end
      print(inc, u:same(t)) end end 

eg["--train"] = function(file,     d) 
  d= DATA.new():import(file or the.train):sort() 
  for i,row in pairs(d.rows) do
    if i==1 or i %25 ==0 then 
      print(l.fmt("%3s\t%.2f\t%s",i, d:chebyshev(row), o(row))) end end end

eg["--clone"] = function(file,     d0,d1) 
  d0= DATA.new():import(file or the.train) 
  d1 = d0:clone(d0.rows)
  for k,col1 in pairs(d1.cols.x) do print""
     print(o(col1))
     print(o(d0.cols.x[k])) end end 
-- ---------------------------------------------------------------------------------------
-- ## Start-up
if   pcall(debug.getlocal, 4, 1) 
then return {DATA=DATA,NUM=NUM,SYM=SYM,the=the,lib=l,eg=eg}
else math.randomseed(the.seed or 1234567891)
     for k,v in pairs(arg) do if eg[v] then eg[v](l.coerce(arg[k+1])) end end end

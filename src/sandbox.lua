#!/usr/bin/env lua
-- <img src=sandbox.png align=left width=150>
-- sandbox.lua : multi-objective rule generation   
-- (c)2024 Tim Menzies <timm@ieee.org> MIT license
  
-- - Download:     `github.com/timm/ezr/blob/main/src/sandbox.lua`
-- - Sample Data:  `github.com/timm/ezr/tree/main/data/\*/\*.csv` (ignore the "old" directory)
-- - Sample Usage: `lua sandox.lua --bins data/misc/auto93.csv`

local the={bins=17, top=7, fmt="%g", cohen=0.35, seed=1234567891,
           train="../data/misc/auto93.csv"}

local big=1E30
local DATA,SYM,NUM,COLS,BIN,TREE = {},{},{},{},{},{}
local abs, max, min = math.abs, math.max, math.min
local coerce,coerces,copy,csv,fmt,list
local new,o,okey,okeys,olist,powerset,push,sort
-----------------------------------------------------------------------------------------
-- ## NUM
-- incremental update of summary of numbers
function NUM.new(name,pos)
  return new(NUM,{name=name, pos=pos, n=0, mu=0, m2=0, sd=0, lo=big, hi= -big,
                  goal= (name or ""):find"-$" and 0 or 1}) end

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

function NUM:norm(x) return x=="?" and x or (x - self.lo)/(self.hi - self.lo) end

function NUM:small(x) return x < the.cohen * self.sd end

function NUM.same(i,j,    pooled)
  pooled = (((i.n-1)*i.sd^2 + (j.n-1)*j.sd^2)/ (i.n+j.n-2))^0.5
  return abs(i.mu - j.mu) / pooled <= (the.cohen or .35) end
-----------------------------------------------------------------------------------------
-- ## SYM
-- incremental update of summary of symbols
function SYM.new(name,pos)
  return new(SYM,{name=name, pos=pos, n=0, has={}, most=0, mode=nil}) end

function SYM:add(x,     d)
  if x ~= "?" then
    self.n  = self.n + 1
    self.has[x] = 1 + (self.has[x] or 0)
    if self.has[x] > self.most then self.most,self.mode = self.has[x], x end 
    return x end end
-----------------------------------------------------------------------------------------
-- ## DATA
-- manage rows, and their summaries in columns
function DATA.new(file,    self) 
  self = new(DATA, {rows={}, cols=nil})
  for row in csv(file) do  self:add(row) end
  return self end

function DATA:add(row)
  if self.cols then push(self.rows, self.cols:add(row)) else 
     self.cols = COLS.new(row) end end 

function DATA:chebyshev(row,     d) 
  d=0; for _,col in pairs(self.cols.y) do 
         d = max(d,abs(col:norm(row[col.pos]) - col.goal)) end
  return d end
-------------------------------------------------------------------------------------
-- ## COLS
-- Manage column creation and column updates.
function COLS.new(row,    self,skip,col)
  self = new(COLS,{all={},x={}, y={}, klass=nil})
  skip={}
  for k,v in pairs(row) do
    col = push(v:find"X$" and skip or v:find"[!+-]$" and self.y or self.x,
            push(self.all, 
              (v:find"^[A-Z]" and NUM or SYM).new(v,k))) 
    if v:find"!$" then self.klass=col end end
  return self end 

function COLS:add(row)
  for _,cols in pairs{self.x, self.y} do
    for _,col in pairs(cols) do  col:add(row[col.pos]) end end 
  return row end
-- ## BIN
-- Track x.lo to x.hi values for some y values.
function BIN.new(name,pos,lo,hi)
  return new(BIN,{lo=lo or big, hi= hi or lo or -big,   y=NUM.new(name,pos)}) end

function BIN:add(row,y,     x) 
  x = row[self.y.pos]
  if x ~= "?" then
    if x < self.lo then self.lo = x end
    if x > self.hi then self.hi = x end
    self.y:add(y) end end

function BIN:__tostring(     lo,hi,s)
  lo,hi,s = self.lo, self.hi,self.y.name
  if lo == -big then return fmt("%s < %g", s,hi) end
  if hi ==  big then return fmt("%s >= %g",s,lo) end
  if lo ==  hi  then return fmt("%s == %s",s,lo) end
  return fmt("%g <= %s < %g", lo, s, hi) end

function BIN:selects(rows,     u)
  u={}; for _,r in pairs(rows) do if self:select(r) then push(u,r) end end; return u end

function BIN:select(row,     x)
  x=row[self.y.pos]
  return (x=="?") or (self.lo==self.hi and self.lo==x) or (self.lo <= x and x < self.hi) end

-- Generate the bins from all x columns.
function DATA:bins(rows,data,      tbins,val,down,yfun) 
  tbins = {}
  for _,col in pairs(self.cols.x) do
    val  = function(a)   return a[col.pos]=="?" and -big or a[col.pos] end
    down = function(a,b) return val(a) < val(b) end
		yfun = function(row) return data:chebyshev(row) end
    for _,bin in pairs(col:bins(sort(rows, down),yfun)) do 
      tbins[col.pos] = {}
      if not (bin.lo== -big and bin.hi==big) then push(tbins[col.pos],bin) end end end
  return tbins end 

-- Generate bins from SYM columns
function SYM:bins(rows,yfun,     t,x,y) 
  t={}
  for k,row in pairs(rows) do
    x= row[self.pos] 
	  y= yfun(row)
    if x ~= "?" then
      t[x] = t[x] or BIN.new(self.name,self.pos,x)
      t[x]:add(row,y) end end
  return t end

-- Generate bins from NUM columns
function NUM:bins(rows,yfun,     t,a,b,ab,x,want,y)
  t = {} 
  b = BIN.new(self.name, self.pos) 
  ab= BIN.new(self.name, self.pos)
  for k,row in pairs(rows) do
    x = row[self.pos] 
	  y = yfun(row)
    if x ~= "?" then 
      want = want or (#rows - k - 1)/the.bins
      if b.y.n >= want and #rows - k > want and not self:small(b.hi - b.lo) then
        a = t[#t]; if a and a.y:same(b.y) then t[#t]=ab else push(t,b) end
        ab= copy(t[#t])
        b = BIN.new(self.name,self.pos,x) end
      b:add(row,y) 
      ab:add(row,y) 
  end end 
  a = t[#t]; if a and a.y:same(b.y) then t[#t]=ab else push(t,b) end
  t[1].lo  = -big
  t[#t].hi =  big
  for k = 2,#t do t[k].lo = t[k-1].hi end 
  return t end
----------------------------------------------------------------------------------------
-- XXX need a clone and a data per child
function DATA:tree(rows,tbins,  stop,       node,splitter,sub)
	node = {_kids={}, here = self:clone(rows), leaf=true}
	stop = stop or 4
	if #rows > stop then 
    splitter = self:minXpected(rows,tbins) 
	  for _,bin in pairs(tbins[splitter]) do
		  sub= bin:selects(rows)
			if #sub < #rows and #rows > stop then
			  node.leaf=false
	      node.kids[bin.y.pos] = {pos=bin.y.pos, lo=bin.lo, hi=bin.hi, name=bin.name,
				                        _tree = self:tree(sub, tbins)}  end end
	return node end end 

function DATA:minXpected(rows,tbins,    lo,n,w,tmp,out)
  lo = big
  for pos,bins in pairs(tbins) do
	  tmp = self:xpected(rows,bins)
    if tmp < lo then lo,out = tmp,pos end end
	return out end

function DATA:xpected(rows,bins,    w,num)
  w = 0
  for _,bin in pairs(bins) do
    num = NUM.new()
    for _,r in pairs(rows) do if bin:select(r) then num:add(self:chebyshev(r)) end end
    w = w + num.n*num.sd end
	return w/#rows end

function TREE:visit(fun,lvl)
  lvl = lvl or 0
	fun(self,lvl)
  for _,sub in pairs(self._kids) do if sub.kids then self:visit(lvl+1) end end end
  
-- ## Lib

-- object creation
local _id = 0
local function id() _id = _id + 1; return _id end

function new (klass,t) 
  t._id=id(); klass.__index=klass; setmetatable(t,klass); return t end

-- lists
function list(t,    u)
  u={}; for _,v in pairs(t) do push(u,v) end; return u end

function push(t,x) t[1+#t]=x; return x end 

function sort(t,fun) table.sort(t,fun); return t end

function copy(t,     u)
  if type(t) ~= "table" then return t end 
  u={}; for k,v in pairs(t) do u[copy(k)] = copy(v) end 
  return setmetatable(u, getmetatable(t)) end

-- thing to string
fmt = string.format

function olist(t)  
  local u={}; for k,v in pairs(t) do push(u, fmt("%s", o(v))) end; return u end

function okeys(t)  
  local u={}; for k,v in pairs(t) do 
               if not tostring(k):find"^_" then push(u, fmt(":%s %s", k,o(v))) end end; 
  return sort(u) end

function o(x)
  if type(x)=="number" then return fmt(the.fmt or "%g",x) end
  if type(x)~="table"  then return tostring(x) end 
  return "{" .. table.concat(#x==0 and okeys(x) or olist(x),", ")  .. "}" end

-- strings to things
function coerce(s,    also)
	if type(s) ~= "string" then return s end
  also = function(s) return s=="true" or s ~="false" and s end 
  return math.tointeger(s) or tonumber(s) or also(s:match"^%s*(.-)%s*$") end 

function coerces(s,    t)
  t={}; for s1 in s:gsub("%s+", ""):gmatch("([^,]+)") do t[1+#t]=coerce(s1) end
  return t end

function csv(src)
  src = src=="-" and io.stdin or io.input(src)
  return function(      s)
    s = io.read()
    if s then return coerces(s) else io.close(src) end end end
-- ## Start-up Actions
local eg={}

eg["-h"] = function(_) 
  print"USAGE: lua sandbox.lua -[hkln] [ARG]" end

eg["--all"] = function(_)
  for _,x in pairs{"--copy","--cohen","--train","--bins"} do 
	  math.randomseed(the.seed)
	  print(x);eg[x]() end end 

eg["--copy"] = function(_,     n1,n2,n3) 
  n1,n2 = NUM.new(),NUM.new()
  for i=1,100 do n2:add(n1:add(math.random()^2)) end
  n3 = copy(n2)
  for i=1,100 do n3:add(n2:add(n1:add(math.random()^2))) end
  for k,v in pairs(n3) do if k ~="_id" then ; assert(v == n2[k] and v == n1[k]) end  end
  n3:add(0.5)
  assert(n2.mu ~= n3.mu) end

eg["--cohen"] = function(_,    u,t) 
    for _,inc in pairs{1,1.05,1.1,1.15,1.2,1.25} do
      u,t = NUM.new(), NUM.new()
      for i=1,20 do u:add( inc * t:add(math.random()^.5))  end
      print(inc, u:same(t)) end end 

eg["--train"] = function(file,     d) 
  d= DATA.new(file or the.train) 
  for i,row in pairs(sort(d.rows,function(a,b) return d:chebyshev(a) <  d:chebyshev(b) end)) do
    if i==1 or i %25 ==0 then print(i, o{y=row.y,row=row}) end end end

eg["--bins"] = function(file,     d,last,ys) 
  d= DATA.new(file or the.train) 
  for col,bins in pairs(d:bins(d.rows, d)) do
     print""
		 for _,bin in pairs(bins) do
     	 print(fmt("%5.3g\t %s", bin.y.mu, bin)) end end  end

eg["--tree"] = function(file,     d,ys) 
  d= DATA.new(file or the.train) 
  ys={}; for _,row in pairs(d.rows) do ys[row.id] = 1 - d:chebyshev(row) end 
  d:tree(d.rows, d:bins(d.rows,ys)) 
end 
-----------------------------------------------------------------------------------------
-- ## Start-up
if   pcall(debug.getlocal, 4, 1) 
then return {DATA=DATA,NUM=NUM,SYM=SYM,BIN=BIN}
else math.randomseed(the.seed or 1234567891)
     for k,v in pairs(arg) do if eg[v] then eg[v](coerce(arg[k+1])) end end end

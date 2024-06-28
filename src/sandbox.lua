#!/usr/bin/env lua
-- <img src=sandbox.png align=left width=150>
-- sandbox.lua : multi-objective rule generation   
-- (c)2024 Tim Menzies <timm@ieee.org> MIT license

local the={bins=17, top=7, fmt="%g", cohen=0.35, seed=1234567891,
           train="../data/misc/auto93.csv"}

local big=1E30
local DATA,SYM,NUM,COLS,BIN,ROW,RULE = {},{},{},{},{},{},{}
local abs, max, min = math.abs, math.max, math.min
local coerce,coerces,copy,csv,fmt,id,new,o,okey,okeys,olist,powerset,push,sort
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
-- ## ROW
-- Stores one record, with an unique id.
local _rid=0
function ROW.new(t) 
  _rid = _rid+1
  return new(ROW,{cells=t,id=_rid}) end
-----------------------------------------------------------------------------------------
-- ## DATA
-- manage rows, and their summaries in columns
function DATA.new(file,    self) 
  self = new(DATA, {rows={}, cols=nil})
  for row in csv(file) do  self:add(ROW.new(row)) end
  return self end

function DATA:add(row)
  if self.cols then push(self.rows, self.cols:add(row)) else 
     self.cols = COLS.new(row) end end 

function DATA:chebyshev(row,     d) 
  d=0; for _,col in pairs(self.cols.y) do 
         d = max(d,abs(col:norm(row.cells[col.pos]) - col.goal)) end
  return d end
-------------------------------------------------------------------------------------
-- ## COLS
-- Manage column creation and column updates.
function COLS.new(row,    self,skip,col)
  self = new(COLS,{all={},x={}, y={}, klass=nil})
  skip={}
  for k,v in pairs(row.cells) do
    col = push(v:find"X$" and skip or v:find"[!+-]$" and self.y or self.x,
            push(self.all, 
              (v:find"^[A-Z]" and NUM or SYM).new(v,k))) 
    if v:find"!$" then self.klass=col end end
  return self end 

function COLS:add(row)
  for _,cols in pairs{self.x, self.y} do
    for _,col in pairs(cols) do  col:add(row.cells[col.pos]) end end 
  return row end
-----------------------------------------------------------------------------------------
-- ## BIN
-- Track x.lo to x.hi values for some y values.
function BIN.new(name,pos,lo,hi)
  return new(BIN,{lo=lo or big, hi= hi or lo or -big,  _rules={}, y=NUM.new(name,pos)}) end

function BIN:add(row,ys,     x) 
  x = row.cells[self.y.pos]
  if x ~= "?" then
    if x < self.lo then self.lo = x end
    if x > self.hi then self.hi = x end
    self._rules[row.id] = row.id
    self.y:add(ys[row.id]) end end

function BIN:__tostring(     lo,hi,s)
  lo,hi,s = self.lo, self.hi,self.y.name
  if lo == -big then return fmt("%s < %g", s,hi) end
  if hi ==  big then return fmt("%s >= %g",s,lo) end
  if lo ==  hi  then return fmt("%s == %s",s,lo) end
  return fmt("%g <= %s < %g", lo, s, hi) end

function BIN:select(row,     x)
  x=row.cells[self.y.pos]
  return (x=="?") or (self.lo==self.hi and self.lo==x) or (self.lo <= x and x < self.hi) end

-- Generate the bins from all x columns.
function DATA:bins(rows,ys,      bins,val,down) 
  bins = {}
  for _,col in pairs(self.cols.x) do
    val  = function(a)   return a.cells[col.pos]=="?" and -big or a.cells[col.pos] end
    down = function(a,b) return val(a) < val(b) end
    for _,bin in pairs(col:bins(sort(rows, down),ys)) do 
      if not (bin.lo == -big and bin.hi == big) then push(bins,bin) end  end end
  return bins end 

-- Generate bins from SYM columns
function SYM:bins(rows,ys,     t,x) 
  t={}
  for k,row in pairs(rows) do
    x= row.cells[self.pos] 
    if x ~= "?" then
      t[x] = t[x] or BIN.new(self.name,self.pos,x)
      t[x]:add(row,ys) end end
  return t end

-- Generate bins from NUM columns
function NUM:bins(rows,ys,     t,a,b,ab,x,want)
  t = {} 
  b = BIN.new(self.name, self.pos)
  ab= BIN.new(self.name, self.pos)
  for k,row in pairs(rows) do
    x = row.cells[self.pos] 
    if x ~= "?" then 
      want = want or (#rows - k - 1)/the.bins
      if b.y.n >= want and #rows - k > want and not self:small(b.hi - b.lo) then
        a = t[#t]; if a and a.y:same(b.y) then t[#t]=ab else push(t,b) end
        ab= copy(t[#t])
        b = BIN.new(self.name,self.pos,x) end
      b:add(row,ys) 
      ab:add(row,ys) 
  end end 
  a = t[#t]; if a and a.y:same(b.y) then t[#t]=ab else push(t,b) end
  t[1].lo  = -big
  t[#t].hi =  big
  for k = 2,#t do t[k].lo = t[k-1].hi end 
  return t end
----------------------------------------------------------------------------------------
-- ## RULE

-- To generate rules, only exploring combinations of the.top scored bins
function DATA:rules(rows,     tmp,ys)
  ys,tmp = {},{}
  for _,row in pairs(rows) do ys[row.id] = 1 - self:chebyshev(row) end 
  for _,bins in pairs(powerset(self:topScoredBins(rows,ys))) do 
    if #bins > 1 -- ignore empty set
    then push(tmp, RULE.new(bins,ys,#rows)) end end
  return self:topScoredRules(tmp) end

-- Return just the.top number of bins. 
function DATA:topScoredBins(rows,ys,    out,binScoreDown)
  out,binScoreDown = {},function(a,b) return a.y.mu > b.y.mu end
  for k,bin in pairs(sort(self:bins(rows,ys), binScoreDown)) do
    if k > the.top then break else push(out,bin) end end 
  return out end

-- Return just the.top number of rukes. 
function DATA:topScoredRules(rules,   out, ruleRankDown)
  out,ruleRankDown  = {}, function(a,b) return a.rank < b.rank   end
  rules = sort(rules, ruleRankDown)
  for k,rule in pairs(rules) do
    if k > the.top then break else push(out,rule) end end
  return out end

-- Rules are  combinations of a set or rule ids, score by their mean chebyshev.
-- (a) The set  of rule ids for each attribute are OR-ed together.
-- (b) This is then AND-ed and (c) scored.
-- (d) If the rule selects for everything, it has no information. So we ignore it.
-- (e) Rule is ranked to minimize size and maximize score.
function RULE.new(bins,ys,tooMuch,    mu,n,nbins,tmp)
  mu,n,nbins,tmp = 0,0,0,{}
  for _,bin in pairs(bins) do 
    nbins = nbins + 1
    tmp[bin.y.pos] = OR(tmp[bin.y.pos] or {}, bin._rules) end -- (a)
  for k,_ in pairs( ANDS(tmp)) do n=n+1; mu = mu + (ys[k]  - mu)/n end  -- (b),(c)
  order=function(a,b) return a.y.pos==b.y.pos and (a.lo<b.lo) or (a.y.pos<b.y.pos) end
  if n < tooMuch then -- (d)
     return new(RULE,{rank= ((0 - nbins/the.top)^2 + (1 - mu)^2)^0.5, -- (e)
                      bins=sort(bins,order), score=mu, }) end end

-- To print a RULE, group its bins by position number, then sorted by `lo`.
function RULE:__tostring(     order,tmp)
  tmp ={}; for k,bin in pairs(self.bins) do tmp[k] = tostring(bin) end
  return "("..table.concat(tmp,"), (")..")" end

function RULE:selects(rows,     out)
  out={}; for _,row in pairs(rows) do if self:select(row) then push(out,row) end end
  return out end

function RULE:select(row,     tmp)
  tmp={}
  for _,bin in pairs(self.bins) do 
    tmp[bin.y.pos] = (tmp[bin.y.pos] or 0) + (bin:select(row) and 1 or 0)  end
  for _,n in pairs(tmp) do if n==0 then return false end end
  return true end

-----------------------------------------------------------------------------------------
-- ## Lib

-- object creation
function new (klass,object) 
  klass.__index=klass; setmetatable(object, klass); return object end

-- lists
function push(t,x) t[1+#t]=x; return x end 

function sort(t,fun) table.sort(t,fun); return t end

function copy(t,     u)
  if type(t) ~= "table" then return t end 
  u={}; for k,v in pairs(t) do u[copy(k)] = copy(v) end 
  return setmetatable(u, getmetatable(t)) end

function powerset(s,       t)
  t = {{}}
  for i = 1, #s do
    for j = 1, #t do
      t[#t+1] = {s[i],table.unpack(t[j])} end end
   return t end
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
  if s ~= nil then
    also = function(s) return s=="true" or s ~="false" and s end 
    return math.tointeger(s) or tonumber(s) or also(s:match"^%s*(.-)%s*$") end end

function coerces(s,    t)
  t={}; for s1 in s:gsub("%s+", ""):gmatch("([^,]+)") do t[1+#t]=coerce(s1) end
  return t end

function csv(src)
  src = src=="-" and io.stdin or io.input(src)
  return function(      s)
    s = io.read()
    if s then return coerces(s) else io.close(src) end end end

-- Sets
function ANDS(t,     out)
  for _,u in pairs(t) do if not out then out=u else out=AND(u,out) end end; return out end 

function AND(t,u,    out) 
  out={}; for k,_ in pairs(t) do if u[k] then out[k]=k end end; return out end 

function OR(t,u,     out) 
  out={}; for _,w in pairs{t,u} do for k,_ in pairs(w) do out[k]=k end end; return out end

-----------------------------------------------------------------------------------------
-- ## Start-up Actions
local eg={}

eg["-h"] = function(_) 
  print"USAGE: lua sandbox.lua -[hkln] [ARG]" end

eg["--copy"] = function(_,     n1,n2,n3) 
  n1,n2 = NUM.new(),NUM.new()
  for i=1,100 do n2:add(n1:add(math.random()^2)) end
  n3 = copy(n2)
  for i=1,100 do n3:add(n2:add(n1:add(math.random()^2))) end
  for k,v in pairs(n3) do assert(v == n2[k] and v == n1[k]) end 
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
    if i==1 or i %25 ==0 then print(i, o{y=row.y,row=row.cells}) end end end

eg["--bins"] = function(file,     d,last,ys) 
  d= DATA.new(file or the.train) 
  ys={}; for _,row in pairs(d.rows) do ys[row.id] = 1 - d:chebyshev(row) end 
  for _,bin in pairs(d:bins(d.rows, ys)) do
    if bin.y.name ~= last then print""; last=bin.y.name end
     print(fmt("%5.3g\t %s", bin.y.mu, bin)) end end 

eg["--rules"] = function(file,     d,last,ys) 
  d= DATA.new(file or the.train) 
  for _,rule in pairs(d:rules(d.rows)) do
    print(rule.rank, rule, #rule:selects(d.rows))
end end
-----------------------------------------------------------------------------------------
-- ## Start-up
if   pcall(debug.getlocal, 4, 1) 
then return {DATA=DATA,NUM=NUM,SYM=SYM,BIN=BIN}
else math.randomseed(the.seed or 1234567891)
     for k,v in pairs(arg) do if eg[v] then eg[v](coerce(arg[k+1])) end end end
-----------------------------------------------------------------------------------------
-- ## Notes
-- - Download:     `github.com/timm/ezr/blob/main/src/sandbox.lua`
-- - Sample Data:  `github.com/timm/ezr/tree/main/data/\*/\*.csv` (ignore the "old" directory)
-- - Sample Usage: `lua sandox.lua --bins data/misc/auto93.csv`

-- ### MIT License
-- Copyright (c) 2024, Tim Menzies
--
-- Permission is hereby granted, free of charge, to any person obtaining a copy
-- of this software and associated documentation files (the "Software"), to deal
-- in the Software without restriction, including without limitation the rights
-- to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
-- copies of the Software, and to permit persons to whom the Software is
-- furnished to do so, subject to the following conditions:
--
-- The above copyright notice and this permission notice shall be included in all
-- copies or substantial portions of the Software.
--
-- THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
-- IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
-- FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
-- AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
-- LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
-- OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
-- SOFTWARE. 

#!/usr/bin/env lua
-- <!-- vim : set ts=4 sts=4 et : -->

local l=require"lib"
local the =require"config"
local data=require"data"

local NUM,SYM,DATA = data.NUM, data.SYM, data.DATA
local BIN = {}

-- ### class BIN: discretization
-- BINs hold information on what happens to some `y` variable as we move from
-- `lo` to `hi` in another column. TREEs will be built by searching through the bins.

-- `BIN.new(name:str, pos:int, ?lo:atom, ?hi:atom) -> BIN`
function BIN.new(name,pos,  lo,hi)
  hi = hi or lo or -l.inf
  lo = lo or l.inf
  return l.new(BIN,{name=name, pos=pos, lo=lo, hi= hi, y=NUM.new()}) end

-- `BIN:add(row:row, y:num) -> nil`    
-- ①  Expand `lo` and `hi` to cover `x`.     
-- ②  Update `self.y` with `y`.
function BIN:add(row,y,     x) 
  x = row[self.pos]
  if x ~= "?" then
    if x < self.lo then self.lo = x end -- ①  
    if x > self.hi then self.hi = x end -- ①  
    self.y:add(y) end end -- ②  

-- `BIN:__tostring() -> str`
function BIN:__tostring(     lo,hi,s)
  lo,hi,s = self.lo, self.hi,self.name
  if lo == -l.inf then return l.fmt("%s <= %g", s,hi) end
  if hi ==  l.inf then return l.fmt("%s > %g",s,lo) end
  if lo ==  hi  then return l.fmt("%s == %s",s,lo) end
  return l.fmt("%g < %s <= %g", lo, s, hi) end

-- `BIN:selects(rows: list[row]) : list[row]`   
-- Return the subset of `rows` selected by `self`.
function BIN:selects(rows,     u)
  u={}; for _,r in pairs(rows) do if self:select(r) then l.push(u,r) end end; return u end

-- `BIN:select(row: row) : bool`
function BIN:select(row,     x)
  x=row[self.pos]
  return (x=="?") or (self.lo==self.hi and self.lo==x) or (self.lo < x and x <= self.hi) end

-- ### Bin generation
-- `DATA:bins(?rows: list[rows]) : dict[int, list[bins]] `   
-- ①  For each x-columns,    
-- ②  Return  a list of  bins ...    
-- ③  ... that separate  the Chebyshev distances ...   
-- ④  ... rejecting any bin that span from minus to plus infinity.
function DATA:bins(  rows,      tbins) 
  tbins, rows = {}, rows or self.rows
  for _,col in pairs(self.cols.x) do -- ①
    tbins[col.pos] = {}
    for _,bin in pairs(col:bins(self:dontKnowSort(col.pos,rows), -- ②  
                               function(row) return self:chebyshev(row) end)) do -- ③  
      if not (bin.lo== -l.inf and bin.hi==l.inf) then --  ④     
         l.push(tbins[col.pos],bin) end end  end
  return tbins end 

-- `DATA:dontKnowSort(pos:int, rows: list[row]) : list[row]`    
-- Sort rows on item `pos`, pushing all the "?" values to the front of the list.   
function DATA:dontKnowSort(pos,rows,     val,down)
  val  = function(a)   return a[pos]=="?" and -l.inf or a[pos] end  
  down = function(a,b) return val(a) < val(b) end  
  return l.sort(rows or self.rows, down) end  

-- `SYM:bins(rows:list[row], y:callable) -> list[BIN]`   
-- Generate one bin for each symbol seen in a  SYM column.
function SYM:bins(rows,y,     out,x) 
  out={}
  for k,row in pairs(rows) do
    x= row[self.pos]
    if x ~= "?" then
      out[x] = out[x] or BIN.new(self.name,self.pos,x)
      out[x]:add(row,y(row)) end end
  return out end

-- `NUM:bins(rows:list[row], y:callable) -> list[BIN]`   
-- Generate one bins for the numeric ranges in this column. Assumes
-- rows are sorted with all the "?" values pushed to the front. Run
-- over rows till we clear the "?" values, then set `want` the
-- remaining rows divided by `the.bins`.  Collect `x` and `y(row)`
-- values for each remaining row, saving them in `b` (the new bin)
-- and `ab` the combination of the new bin and the last thing we
-- added to `out`.
local _newBin, _fillGaps
function NUM:bins(rows,y,     out,b,ab,want,b4,x)
  out = {} 
  b = BIN.new(self.name, self.pos) 
  ab= BIN.new(self.name, self.pos)
  for k,row in pairs(rows) do
    x = row[self.pos] 
    if x ~= "?" then 
      want = want or (#rows - k - 1)/the.bins
      if x ~= b4 and                 -- if there is a break between values
         b.y.n >= want and           -- and the current bin is big enough
         #rows - k > want and        -- and after, there is space for 1 more bin 
         not self:small(b.hi - b.lo) -- the span of this bin is not trivially small
      then 
         b,ab = _newBin(b,ab,x,out)  -- ensure the `b` info is added to end of `out`
      end
      b:add(row,y(row))    -- update the current new bin
      ab:add(row,y(row))   -- update the combination of current new bin and end of `out`
      b4 = x end 
  end
  _newBin(b,ab,x,out) -- handle end of list
  return _fillGaps(out) end 

-- helper function for NUM:bins. If the new bin is the same as the last bin,
-- then replace the last bin with `ab` (which is the new bin plus the last bin).
-- Else push the new bin onto `out`.
function _newBin(b,ab,x,out,      a)
  a = out[#out]
  if   a and a.y:same(b.y)  
  then out[#out] = ab     -- replace the last bin with last plus `b`
  else l.push(out,b) end  -- add `b` to the out
  return BIN.new(b.name,b.pos,x), l.copy(out[#out]) end -- return the new b,ab

-- helper function for NUM:bins. Fill in any gaps in the bins
function _fillGaps(out)
  out[1].lo    = -l.inf  -- expand out to cover -infinity to...
  out[#out].hi =  l.inf  -- ... plus infinity
  for k = 2,#out do out[k].lo = out[k-1].hi end  -- fill in any gaps with the bins
  return out end
-----------------------------------------------------------------------------
-- ## Start-up Actions
local eg={}
local copy,o,oo,push=l.copy,l.o,l.oo,l.push

eg["-h"] = function(_) print("lua discretize.lua --[bins] [FILE]") end
eg["-t"] = function(x) the.train= x end

eg["--bins"] = function(file,     d) 
  d= DATA.new():import(file or the.train):sort()
  print(l.fmt("%.3f", d:chebyshevs().mu))
  for col,bins in pairs(d:bins(d.rows)) do
    print""
    for _,bin in pairs(bins) do
      print(l.fmt("%5.3g\t%3s\t%s", bin.y.mu, bin.y.n, bin)) end end  end

-- ---------------------------------------------------------------------------------------
-- ## Start-up
if   pcall(debug.getlocal, 4, 1) 
then return {DATA=DATA, NUM=NUM, SYM=SYM, BIN=BIN, the=the, lib=l, eg=eg}
else math.randomseed(the.seed or 1234567891)
     for k,v in pairs(arg) do if eg[v] then eg[v](l.coerce(arg[k+1])) end end end


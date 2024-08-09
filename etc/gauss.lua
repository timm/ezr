local DATA,BIN={},{}
local the,pop,nth,sort,push,new
the={cohen=.35,bins=16}

pop=table.remove
function nth(n)      return function(lst) return lst[n] end end
function sort(t,fun) table.sort(t,fun); return t end
function push(t,x)   t[1+#t] = x; return x end
function new(klass,obj) klass.__index=klass; return setmetatable(obj,klass) end

function ROW:new(t)
  return new(ROW,{cells=t,score=nil}) end

function COLS.new(i,names)
  i = new(COLS,{names=names, goals=goals, lo=lo, hi=hi}) 
  for at,s in pairs(i.names) do
    if s:find"-$"     then i.goals[at]=0 end
    if s:find"+-$"    then i.goals[at]=1 end
    if s.find"^[A-Z]" then i.lo[at]=1E32; i.hi[at]=-1E32 end  end
  return i end

function COL.add(i,row)
  for c,lo in pairs(i.lo) do
    if row[c] != "?" then
      i.lo[c] = math.min(lo,           row.cells[c])
      i.hi[c] = math.max(i.cols.hi[c], row.cells[c]) end end 
  return row end 
   
function COLS.chebyshev(i,row,    d)
  d=0
  for c,goal in pairs(i.goals) do
    x = (row.cells[c] - i.lo[c]) / (i.hi[c] - i.lo[c])
    d = math.max(d, math.abs(x - goal)) end 
  return d end 

function DATA.new(i,names)
  return new(DATA, {cols=COLS:new(names), rows={}}) end

function DATA.add(i,row)
  push(i.rows, i.cols.add(row)) end

function DATA.bins(i,rows,xfun,yfun,     my,bins)
  my, rows = i:my(i:sortedRows(rows,xfun), xfun, yfun)
  bins = { BIN:new(xfun(rows[1])) }
  for r,row in pairs(rows) do
    if r > my.skip 
    then i:theCurrentBin(my,r,xfun(row),rows,bins,xfun)
          :add( yfun(row), my.seen) end end
  return bins end

function DATA:theCurrentBin(,my,r,x,rows,bins,xfun)
  if r < #rows - my.gap then
    if x != xfun( rows[r+1] )  then
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
          gap  = (n / the.bins) //1 
          sd   = (rows[(skip+1+ .9*n)//1] - rows[(skip+1+ .1*n)//1]) /2.58
         }, rows end

function BIN.new(i,x,b4)
  i = new(BIN,{n=0, lo=x, seen={}})
  if b4 then
    i.last = b4
    b4.next = i end
  return i end

function BIN.add(i,y,ys)
  i.seen[y] = (i.seen[y] or 0) + 1/ys[y]
  i.n = i.n + 1 end


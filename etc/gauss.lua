DATA,CUT={},{}
the={cohen=.35}
pop=table.remove
function new(klass,obj) klass.__index=klass; return setmetatable(obj,klass) end

function COLS.new(i,names)
  i = new(COLS,{names=names, goals=goals, lo=lo, hi=hi}) 
  for at,s in pairs(i.names) do
    if s:find"-$"     then i.goals[at]=0 end
    if s:find"\+-$"   then i.goals[at]=1 end
    if s.find"^[A-Z]" then i.lo[at]=1E32; i.hi[at]=-1E32 end  end
  return i end

function COL.add(i,row)
  for c,lo in pairs(i.lo) do
    if row[c] != "?" then
      i.lo[c] = math.min(lo,           row[c])
      i.hi[c] = math.max(i.cols.hi[c], row[c]) end end 
  return row end 
   
function COLS.chebyshev(i,row)
  for c,goal in pairs(i.goals) do
    x = (row[c] - i.lo[x]) / (i.hi[c] - i.lo[c])
    d = math.max(d, math.abs(x - goal)) end
  return d end

function DATA.new(i,names,rows)
  return new(DATA, {cols=COLS:new(names), rows=rows or {}}) end

function DATA.add(i,row)
  push(i.rows, i.cols.add(row)) end

 function DATA.cuts(i,rows,xfun,yfun,     my,cuts)
  my, rows = i:my(i:sortedRows(rows,xfun), xfun, yfun)
  cuts = {CUT:new(xfun(rows[1]))}
  for r,row in pairs(rows) do
    if r > my.skip 
    then i:cut(my,r,xfun(row),rows,cuts,xfun)
          :add( yfun(row), my.seen) end end
  return cuts end

function DATA.cut(i,my,r,x,rows,cuts,xfun)
  if r < #rows - my.gap then
    if x != xfun( rows[r+1] )  then
      if cuts[#cuts].n >= my.gap then  
        if x - cuts[#cuts].lo >= my.sd*the.cohen then 
          push(cuts, CUT:new(x,cuts[#cuts])) end end end end
  return cuts[#cuts] end

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

function CUT.new(i,x,b4)
  i = new(CUT,{n=0, lo=x, seen={}})
  if b4 then
    i.last = b4
    b4.next = i end
  return i end

function CUT.add(i,y,ys)
  i.seen[y] = (i.seen[y] or 0) + 1/ys[y]
  i.n = i.n + 1 end

function nth(n) return function(lst) return lst[n] end end
function sort(t,fun) table.sort(t,fun); return t end

local the={bins=17, cohen=0.35}
local big=1E30

local train,head,bin,bins,numBins
-- move to "?"sort
function NUM(name,pos)
  return {name=name, pos=pos, n=0, mu=0, m2=0, sd=0} end

function add2num(num,x,     d)
  if x ~= "?" then
    num.n  = num.n + 1
    d      = x - num.mu
    num.mu = num.mu + d/num.n
    num.m2 = num.m2 + d*(x - num.mu)
    num.sd = n<2 and 0 or (num.m2/(num.n - 1))^.5 
    return num end end 

function XY(name,pos)
  return {x={lo=big, hi=-big}, y=BIN(name,pos)} end

function add2xy(xy,x,y)
  if add2num(xy.y,y) then
    xy.x.lo = math.min(x, xy.x.lo)
    xy.x.hi = math.max(x, xy.x.hi) end end

function DATA(    data) 
  data = {rows={}, cols=nil}
  for r in csv(file) do  add2data(data,r) end
  return data end

function add2data(data, row)
  if data.cols then push(data.rows, row) else data.cols = COLS(row) end end

function COLS(row,    cols)
  cols = {x={}, y={}, num={}, has={}}
  for k,v in pairs(row) do
    cols.has[k] = {}
    if v:find"^[A-Z]" then cols.num[k] = v end
    if v:find"[!+-]$" then cols.y[k]   = v:find"-$" and 0 or 1 
                      else cols.x[k]   = v end end
  return cols end 

function bins(data,rows,      bins,qval,fun)
  bins = {}
  for k,name in pairs(data.cols.x) do
    qval= function(a)   return a=="?" and -big or a end
    fun = function(a,b) return qval(a[k]) < qval(b[k]) end
    (cols.num[k] and numBins or symBins)(sort(rows,fun),k,name,bins) end 
  return bins end 

function sd(t,  lo,hi,fun)
   lo  = lo or 1
   hi  = hi or #t
   fun = fun or function(x) return x end
   n   = (hi-lo)//10
   return (fun(t[hi - n]) - fun(t[lo+n]))/2.58 end

function numBins(rows,k,name,bins,     big,dull,b,out) 
  tmp = {}
  b   = push(bins, push(tmp, BIN(name, k)))
  gap  = (#rows - start)/the.bins
  dull = the.cohen * sd(rows,start,#rows, function(r) return r[k] end)
  for k,row in pairs(rows) do
    if k=="?" then start=k+1 else 
      if b.y.n > gap and b.hi - b.lo > dull and #t -  k > gap then
        b = push(bins, push(tmp, BIN(name, k))) end
      add2bin(b,rows[r][k],row._score) end end
  tmp[1].lo = - big
  tmp[#tmp].hi = big
  for k = 2,#t do tmp[k].lo = tmp[k-1].hi end

function csv(src)
  src = src=="-" and io.stdin or io.input(src)
  return function(      s)
    s = io.read()
    if s then return cells(s) else io.close(src) end end end

function lib.cells(s,    t)
  t={}; for s1 in s:gsub("%s+", ""):gmatch("([^,]+)") do t[1+#t]=lib.coerce(s1) end
  return t end

function push(t,x) t[1+#t]=x; return x end 
function sort(t,fun)
   table.sort(t,fun)
   return t end

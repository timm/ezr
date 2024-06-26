local the={bins=17, cohen=0.35}
local big=1E30

-- move to "?"sort

function train(it,    data)
  data = {rows={}, cols=nil}
  for row in it do
    if data.cols then push(data.rows,row) else data.cols=head(row) end end 
  return data end

function head(row,    cols)
  cols = {x={}, y={}, num={}, has={}}
  for k,v in pairs(row) do
    cols.has[k] = {}
    if v:find"^[A-Z]" then cols.num[k] = true end
    if v:find"[!+-]$" then cols.y[k] = v:find"-$" and 0 or 1 
                      else cols.x[k] = true end end
  return cols end 

function bin(name,pos) return {name=name,pos=pos,lo=big,hi= -big,n=0} end

function bins(data)
  bins={}
  for k,t in pairs(data.cols.has) do
    table.sort(t)
    (cols.num[k] and numBins or symBins)(data.cols.names[k],k,t,tmp) end end 

function numBins(name,k,t,bins,     big,dull,b,out) 
  big  = #t/the.bins
  dull = (t[#t] - t[1])/2.58 * the.cohen
  tmp  = {}
  b    = push(bins, push(tmp, bin(name, k)))
  for k,v in pairs(t) do
    if b.n > big and b.hi - b.lo > dull and #t - k > big then
      b = push(bins, push(tmp, bin(name, k))) end
    b.n  = b.n + 1
    b.lo = math.min(b.lo,v)
    b.hi = math.max(b.hi,v) end
  tmp[1].lo = - big
  tmp[#tmp].hi = big
  for k = 2,#t do tmp[k].lo = tmp[k-1].hi end

function push(t,x) t[1+#t]=x; return x end 

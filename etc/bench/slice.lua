local max,min,floor,exp,sqrt,log = math.max,math.min,math.floor,math.exp,math.sqrt,math.log
function Num() return {n=0, mu=0, m2=0} end   -- all Welford keeps
function Sym() return {has={}} end            -- array of {v,c}, in order
function rnd()                                -- MINSTD, shared by all ports
  SEED = SEED * 16807 % 2147483647
  return SEED / 2147483647 end
function shuffle(a,    b,j)                   -- Fisher-Yates, shared rnd order
  b={}; for i=1,#a do b[i]=a[i] end
  for i=#b,2,-1 do j=floor(rnd()*i)+1; b[i],b[j]=b[j],b[i] end
  return b end
function sortBy(t,f,    d)                    -- decorate, sort, undecorate
  d={}; for i=1,#t do d[i]={k=f(t[i]), v=t[i]} end
  table.sort(d, function(p,q) return p.k < q.k end)
  for i=1,#d do t[i]=d[i].v end
  return t end
function sd(c) return c.n < 2 and 0 or sqrt(c.m2/(c.n-1)) end
function add(c,v,inc,    d,hit)               -- inc=-1 undoes
  inc = inc or 1
  if v == "?" then return c end
  if c.has then
    for _,kv in ipairs(c.has) do
      if kv[1] == v then kv[2] = kv[2] + inc; hit = true; break end end
    if not hit then c.has[#c.has+1] = {v, inc} end
    return c end
  c.n = c.n + inc
  d = v - c.mu
  c.mu = c.mu + inc*d/max(1,c.n)
  c.m2 = max(0, c.m2 + inc*d*(v - c.mu))
  return c end
function adds(lst,it) it = it or Num()
  for _,v in ipairs(lst) do add(it,v) end
  return it end
function size(c,    s) if not c.has then return c.n end
  s=0; for _,kv in ipairs(c.has) do s=s+kv[2] end
  return s end
function div(c,    n,s)                       -- Num: sd. Sym: entropy
  if not c.has then return sd(c) end
  n, s = size(c), 0
  for _,kv in ipairs(c.has) do
    if kv[2] > 0 then s = s + kv[2]/n*log(kv[2]/n,2) end end
  return -s end
function addRow(tbl,row,inc)                  -- inc=-1 pops the last row
  inc = inc or 1
  tbl._mids = nil
  if inc > 0 then tbl.rows[#tbl.rows+1] = row
  else row = table.remove(tbl.rows) end
  for at,c in pairs(tbl.cols) do add(c, row[at], inc) end
  return row end
function Tbl(src,    tbl,s,last)
  tbl = {rows={}, cols={}, x={}, y={}, names=src[1], klass=nil}
  for at=0,#src[1]-1 do
    s = src[1][at+1]; last = s:sub(-1)
    if last ~= "X" then
      tbl.cols[at] = s:sub(1,1):match("%u") and Num() or Sym()
      if last == "!" then tbl.klass = at
      elseif last == "+" or last == "-" then
        tbl.y[#tbl.y+1] = {at, last == "+" and 1 or 0}
      else tbl.x[#tbl.x+1] = at end end end
  for i=2,#src do addRow(tbl, src[i]) end
  return tbl end
function clone(tbl,rows,    s) s={tbl.names}
  for _,r in ipairs(rows or {}) do s[#s+1]=r end
  return Tbl(s) end
function norm(col,v,    z)
  z = max(-3, min(3, (v - col.mu)/(1e-32 + sd(col))))
  return 1/(1 + exp(-1.7*z)) end
function mid(col,    best)
  if not col.has then return col.mu end
  best = col.has[1]
  for _,kv in ipairs(col.has) do if kv[2] > best[2] then best = kv end end
  return best[1] end
function mids(tbl)                            -- x centroid; cached
  if not tbl._mids then tbl._mids = {}
    for _,at in ipairs(tbl.x) do tbl._mids[at] = mid(tbl.cols[at]) end end
  return tbl._mids end
function mink(gaps,    s) s=0
  for _,g in ipairs(gaps) do s = s + g^P end
  return (s/#gaps)^(1/P) end
function ydist(tbl,row,    g) g={}
  for _,aw in ipairs(tbl.y) do
    g[#g+1] = math.abs(norm(tbl.cols[aw[1]], row[aw[1]]) - aw[2]) end
  return mink(g) end
function dist1(col,a,b)
  if a == "?" or b == "?" then return 1 end
  if col.has then return a ~= b and 1 or 0 end
  return math.abs(norm(col,a) - norm(col,b)) end
function xdist(tbl,row,m,    g) g={}
  for _,at in ipairs(tbl.x) do
    g[#g+1] = dist1(tbl.cols[at], row[at], m[at]) end
  return mink(g) end
function ymu(tbl,rows,    s) s=0
  for _,r in ipairs(rows) do s = s + ydist(tbl,r) end
  return s/#rows end
function ymids(tbl,rows,    out,s) out={}
  for _,aw in ipairs(tbl.y) do s=0
    for _,r in ipairs(rows) do s = s + r[aw[1]] end
    out[#out+1] = s/#rows end
  return out end
function centroid(tbl,best,rest)              -- near best, far from rest
  return function(z) return xdist(tbl,z,mids(rest)) - xdist(tbl,z,mids(best)) end end
function label(tbl,best,rest,row,    b,r)     -- keep best pool near sqrt
  addRow(best,row)
  sortBy(best.rows, function(z) return ydist(tbl,z) end)
  b, r = #best.rows, #rest.rows
  if b > sqrt(1+b+r) then addRow(rest, addRow(best,nil,-1)) end end
function acquire(tbl,cap,score,    best,rest,todo,out)  -- pop the top scorer
  score = score or centroid
  best, rest, todo = clone(tbl), clone(tbl), {}
  for i,r in ipairs(shuffle(tbl.rows)) do if i <= Few then todo[i]=r end end
  for _=1,Start do label(tbl,best,rest,table.remove(todo)) end
  cap = cap or Stop
  while #todo > 0 and #best.rows + #rest.rows < cap do
    sortBy(todo, score(tbl,best,rest))
    label(tbl,best,rest,table.remove(todo)) end
  out = {}
  for _,r in ipairs(best.rows) do out[#out+1]=r end
  for _,r in ipairs(rest.rows) do out[#out+1]=r end
  return out end
function cohen(xs,ys,d,eps,    a,b,pool)      -- gap vs pooled sd, floored
  d, eps = d or 0.35, eps or 0
  a, b = adds(xs), adds(ys)
  pool = ((a.n-1)*sd(a)^2 + (b.n-1)*sd(b)^2)/(a.n+b.n-2)
  return math.abs(a.mu-b.mu) <= max(eps, d*sqrt(pool)) end
function cliffs(xs,ys,d,    gt,lt,j,k,m)      -- sorted in. rank imbalance ok?
  d = d or 0.197
  gt,lt,j,k,m = 0,0,0,0,#ys
  for _,x in ipairs(xs) do
    while j < m and ys[j+1] <  x do j=j+1; k=j end
    while k < m and ys[k+1] <= x do k=k+1 end
    gt, lt = gt+j, lt+m-k end
  return math.abs(gt-lt)/(#xs*m) <= d end
function ks(xs,ys,a,    n,m,i,j,d,v)          -- sorted in. 95% K-S
  a = a or 1.36
  n,m,i,j,d = #xs,#ys,0,0,0
  while i < n and j < m do
    v = min(xs[i+1], ys[j+1])
    while i < n and xs[i+1] <= v do i=i+1 end
    while j < m and ys[j+1] <= v do j=j+1 end
    d = max(d, math.abs(i/n - j/m)) end
  return d <= a*sqrt((n+m)/(n*m)) end
function same(xs,ys,eps,    a,b)              -- indistinguishable, all three
  a,b = {},{}
  for i,v in ipairs(xs) do a[i]=v end
  for i,v in ipairs(ys) do b[i]=v end
  table.sort(a); table.sort(b)
  return cliffs(a,b) and ks(a,b) and cohen(a,b,0.35,eps or 0) end

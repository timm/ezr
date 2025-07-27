local BINS,E=7,193/71

function Num() return {lo=1e32,hi=-1e32,mu=0,m2=0,sd=0,n=0} end

function num(n,v)
  n.n=n.n+1
  n.lo=math.min(v,n.lo)
  n.hi=math.max(v,n.hi)
  local d=v-n.mu
  n.mu=n.mu+d/n.n
  n.m2=n.m2+d*(v-n.mu)
  n.sd=n.n<2 and 0 or (n.m2/(n.n-1))^0.5 end

function cdf(n,v,     z,f)
  z=(v-n.mu)/(n.sd+1e-32)
  f=function(z) return 1-0.5*E^(-0.717*z-0.416*z*z) end
  return z>=0 and f(z) or 1-f(-z) end

function norm(n,v,      b,x)
  if v=="?" then return v end
  b=(n.hi-n.lo)/(BINS-1)
  x=math.floor(cdf(n,v)*(BINS-1)+0.5)
  return n.lo+x*b end

function header(cols,    t)
  t={nums={},rows={},names=cols}
  for c,col in ipairs(cols) do
    if col:find"^[A-Z]" and not col:find"[+-X!]$" then
      t.nums[c]=Num() end end
  return t end

function body(cells,state,       row)
  row={}
  for c,val in ipairs(cells) do
    if state.nums[c] and val~="?" then
      val=tonumber(val)
      num(state.nums[c],val) end
    row[c]=val end
  table.insert(state.rows,row) end

function splitCSV(s,      t)
  t={}; for x in s:gmatch("[^,]+") do t[#t+1]=x end; return t end

function norms(state)
  for _,row in ipairs(state.rows) do
    local out={row[1]}
    for c=2,#row do
      out[#out+1]=state.nums[c] and norm(state.nums[c],row[c]) or row[c] end
    print(table.concat(out,",")) end end

local state
for line in io.lines() do
  local cells=splitCSV(line)
  if not state then print(line); state=header(cells)
  else body(cells,state) end end

norms(state)

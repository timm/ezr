local help = [[
    -A  Any=4              on init, how many initial guesses?
    -B  Budget=50          when growing theory, how many labels?
    -D  Delta=smed         required effect size test for cliff's delta
    -F  Few=128            sample size of data random sampling
    -K  Ks=0.95            confidence for Kolmogorov–Smirnov test
    -p  p=2                distance co-efficient
    -s  seed=1234567891    random number seed
    -f  file=../../moot/optimize/misc/auto93.csv  data file
    -h                     show help
]]

local b4={}; for k,_ in pairs(_ENV) do b4[k]=k end
local adds,atom,cat,cats,cells,csv,keys,map,new.push,shuffle,sort
local sqrt = math.sqrt

local the={}; for k,v in help:gmatch("(%S+)=(%S+)") do the[k]=v end

----------------------------------------------------------------------
-- **SYM:new**: `(int=0, str="") -> tbl` <br> categorical column
function SYM:new(at, txt)
  return new(SYM, {n = 0, at = at or 0, txt = txt or "",
                   has = {}}) end  -- value -> count

-- **NUM:new**: `(int=0, str="") -> tbl` <br> numeric stats column
function NUM:new(at, txt)
  return new(NUM, {n  = 0, at = at or 0, txt = txt or "",
                   mu = 0, m2 = 0,     -- mean, sum of squares
                   lo = big, hi = -big,-- min, max
                   w  = (txt or ""):find"-$" and 0 or 1}) end -- weight

-- **COLS:new**: `(arr<str>) -> tbl` <br> build column sets.
-- Choose NUM if col name starts with uppercase, else SYM.
-- Skip cols ending in "X"; send !,+,- cols to y, else to x.
function COLS:new(names)
  local all, x, y = {}, {}, {}
  for at, s in pairs(names) do
    local col = push(all, (s:find"^[A-Z]" and NUM or SYM):new(at,s))
    if not s:find"X$" then
      push(s:find"[!+-]$" and y or x, col) end end
  return new(COLS, { names = names, all = all, x = x, y = y }) end

-- **DATA:new**: `(arr<str>|nil) -> tbl` <br> dataset container
function DATA:new(names)
  return new(DATA, {rows={},cols=COLS:new(names or {}), mid=nil}) end

-- **DATA:clone**: `(arr<tbl>|nil) -> tbl` <br> clone with names
function DATA:clone(  rows) 
  return adds(rows or {}, adds({self.cols.names}, DATA:new())) end

----------------------------------------------------------------------
-- **adds**: `(tbl|arr<any>, tbl=NUM()) -> tbl` <br> add many items
function adds(t, it)
  it = it or NUM()
  for _,x in pairs(t or {}) do add(it,x) end
  return it end

-- **add**: `(tbl, any, int=1) -> any` <br> generic add/update
function add(i,x,  inc)
  if x ~= "?" then 
    i.n = i.n + 1
    i:_add(x,inc or 1) end
  return x end

-- **sub**: `(tbl, any) -> any` <br> decrement via add
function sub(i,x) return add(i,x, -1) end

-- **SYM:_add**: `(str, int) -> nil` <br> bump symbol count
function SYM:_add(x, inc) 
  self.has[x] = (self.has[x] or 0) + inc end

-- **NUM:_add**: `(num, int) -> nil` <br> update running stats
function NUM:_add(v, inc)
  if inc < 0 and self.n < 2 then
    self.n, self.mu, self.m2, self.sd = 0, 0, 0, 0
  else
    if v < self.lo then self.lo = v end
    if v > self.hi then self.hi = v end
    local d = v - self.mu
    self.mu = self.mu + inc * (d / self.n)
    self.m2 = (self.m2 or 0) + inc * (d * (v - self.mu))
    self.sd = self.n < 2 and 0 or sqrt(self.m2 / (self.n - 1)) end end 

-- **DATA:_add**: `(tbl, int) -> nil` <br> update rows and cols
function DATA:_add(row, inc)
  self.mid = nil
  if inc > 0 then push(self.rows, row) end
  for _,col in pairs(self.cols.all) do add(col, row[col.at], inc) end end

-------------------------------------------------------------------------------
-- **atom**: `(str, fun=nil) -> int|num|bool|str` <br> parse literal or trim string
function atom(s,      f)    
  f = function(s) return s=="true" or s~="false" end
  return math.tointeger(s) or tonumber(s) or f(s:match'^%s*(.*%S)') end

-- **cat**: `(any) -> str` <br> stringify value
function cat(x)
  f, is = string.format, type(x)
  return is=="table" and "{" ..table.concat(cats(t,f),", ").. "}" or
         is=="number" and f(x==math.floor(x) and "%.0f" or "%.3f", x) or 
         f("%s",x) end

-- **cats**: `(tbl, fun) -> arr<str>` <br> stringify table
function cats(t,f)
  if #t > 0 then return map(t,cat) end
  u={}; for _,k in pairs(keys(t)) do u[1+#u]=f(":%s %s",k,cat(t[k])) end
  return sort(u) end

-- **cells**: `(str) -> arr<int|num|bool|str>` <br> split CSV row into values
function cells(s,    t)
  t = {}; for s1 in s:gsub("%s+", ""):gmatch("([^,]+)") do t[1+#t]=atom(s1) end
  return t end

-- **csv**: `(str) -> fun()->arr<int|num|bool|str>` <br> row iterator
function csv(src,      s)
  src = io.input(src)
  return function()
    s = io.read(); if s then return cells(s) else io.close(src) end end end

-- **keys**: `(tbl) -> arr<str>` <br> list of non-underscore keys
function keys(t,  u) 
  u = {}
  for k,_ in pairs(t) do if tostring(k):sub(1,1) ~= "_" then u[1+#u]=k end end
  return sort(u) end

-- **map**: `(arr<any>, fun) -> arr<any>` <br> map over array
function map(t,f,   u) 
  u={}; for _,x in pairs(t) do u[1+#u]=f(x) end; return u end

-- **new**: `(tbl, tbl) -> tbl` <br> constructor with metatable
function new(kl,t) kl.__index = kl; return setmetatable(t,kl) end

-- **push**: `(arr<any>, any) -> any` <br> append to array
function push(t,x) t[1+#t]=x; return x end

-- **shuffle**: `(arr<any>) -> arr<any>` <br> Fisher-Yates shuffle
function shuffle(t,    j) 
  for i = #t,2,-1 do j=math.random(i); t[i],t[j] = t[j],t[i] end; return t end

-- **sort**: `(arr<any>, fun|nil) -> arr<any>` <br> sort array in-place
function sort(t,fn) table.sort(t,fn); return t end


-- for i,row in csv(the.file) do 
--   if i==0 then
--     for i,s in pairs(row) do 
--       if s:find:"^[A-Z]" then 
--         nums[i] = {big, -big}
--         if s:find"-$" then y[i]=0 end
--         if s:find"+$" then y[i]=1 end 
--   else rows[1+#rows]=row end
--
-- for x in _ENV do print(x) end
--
-- B, R, best, rest = 0, 0, {}, {}
--for i,row in pairs(shuffle(rows)) do

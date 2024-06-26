local the={bins=17, cohen=0.35, fmt="%6.3f", cohen=0.35}
local big=1E30

local DATA,SYM,NUM,COLS = {},{},{},{}
local abs,max,min = math.abs,math.max, math.min
local cells,coerce,csv,fmt,new,o,okey,okeys,olist,push,sort
-----------------------------------------------------------------------------------------
function NUM.new(name,pos)
  return new(NUM,{name=name, pos=pos, n=0, mu=0, m2=0, sd=0,
                  goal= name:find"-$" and 0 or 1}) end

function NUM:add(x,     d)
  if x ~= "?" then
    self.n  = self.n + 1
    d       = x - self.mu
    self.mu = self.mu + d/self.n
    self.m2 = self.m2 + d*(x - self.mu)
    self.sd = n<2 and 0 or (self.m2/(self.n - 1))^.5 
    return self end end 

function NUM:norm(x) return x=="?" and x or (x - self.lo)/(self.hi - self.lo) end

function NUM:small(x) return x < the.cohen * self.sd end
-----------------------------------------------------------------------------------------
function SYM.new(name,pos)
  return new(NUM,{name=name, pos=pos, n=0, has={}, most=0, mode=nil}) end

function SYM:add(x,     d)
  if x ~= "?" then
    self.n  = self.n + 1
    self.has[x] = 1 + (self.has[x] or 0)
    if self.has[x] > self.most then self.most,self.mode = self.has[x], x end end end
-----------------------------------------------------------------------------------------
function DATA.new(    self) 
  self = new(DATA, {rows={}, cols=nil})
  for row in csv(file) do  self:add(row) end
  for n,row in pairs(rows) do: self:complete(n,row) end
  return self end

function DATA:add(row)
  if self.cols then push(self.rows, self.cols:add(row)) else self.cols = COLS.new(row) end end

function DATA:complete(n,row)
  row._id  = row._id or n
  row._y = 1 - self:chebyshev(row) end

function DATA:chebyshev(row,     d) 
  d=0; for _,col in pairs(self.cols.y) do d = max(d,abs(col:norm(row[col.pos]) - col.goal)) end
  return d end
-----------------------------------------------------------------------------------------
function COLS.new(row,    self,skip,col)
  self = new(COLS,{all={},x={}, y={}, klass=nil})
  skip={}
  for k,v in pairs(row) do
    col = push(k:find"X$" and skip or k:find"^[!+-]$" and self.y or self.x,
               push(all, 
                    (v:find"^[A-Z]" and NUM or SYM).new(v,k))) 
    if v:find"!$" then self.klass=col end end
  return self end 

function COLS:add(row)
  for _,cols in pairs{self.x, self.y} do
    for _,col in pairs(cols) do col:add(row[col.pos]) end end 
  return row end
-----------------------------------------------------------------------------------------
function XY.new(name,pos)
  return new(XY,{lo=big, hi= -big,  y=NUM(name,pos)}) end

function XY:add(row) 
  x = row[self.y.pos]
  if x ~= "?" then
    if x < self.lo then self.lo = x end
    if x > self.hi then self.hi = x end
    self.y:add(row._y) end end
-----------------------------------------------------------------------------------------
fmt = string.format

function okey(k,v) if not tostring(k):find"^_" then return tostring(v) end end
function okeys(t)  local u={}; for k,v in pairs(t) do push(u, okey(k,v)) end; return sort(u) end
function olist(t)  local u={}; for k,v in pairs(t) do push(u, fmt("%s", o(v))) end; return u end

function o(x)
  if type(x)=="number" then return x == floor(x) and tostring(x) or fmt(the.fmt,x) end
  if type(x)~="table"  then return tostring(x) end 
  return "(" .. table.concat(#x==0 and okeys(x) or olist(x),", ")  .. ")" end

function new (klass,object) 
  klass.__index=klass; klass.__tostring=o; setmetatable(object, klass); return object end

function bins(data,rows,      bins,qval,fun)
  bins = {}
  for _,col in pairs(data.cols.x) do
    val = function(a) return a[col.pos]=="?" and -big or a[col.pos] end
    col:bins(bins, sort(rows, function(a,b) return val(a) < val(b) end)) end
  return bins end 

-- add the stats test here using pooled cohen
function NUM:bins(rows,bins,     big,dull,b,out,start) 
  tmp = {}
  b   = push(bins, push(tmp, XY(col.name, col.pos)))
  for k,row in pairs(rows) do
    if row[cols.pos] ~= "?" then 
      want = want or (#rows - k - 1)/the.bins
      if b.y.n >= want and #rows - k > want and not col:small(b.hi - b.lo) then
        b = push(bins, push(tmp, XY(col.name, col.pos))) end
      b:add(row) end end 
  tmp[1].lo = - big
  tmp[#tmp].hi = big
  for k = 2,#t do tmp[k].lo = tmp[k-1].hi end

function coerce(s,    also)
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

function push(t,x) t[1+#t]=x; return x end 
function sort(t,fun) table.sort(t,fun); return t end

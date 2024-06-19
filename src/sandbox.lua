local NUM,SYM,DATA,COLS = {},{},{},{}
local adds, each, fmt, o, okeys, olist, push, sort
local new = function(kl,o) kl.__index=kl; setmetatable(o, kl); return o end

local the = {fmt="%6.sf"}
------------------------------------------------------------------------------------------
function DATA.new(it,  names) 
  return new(DATA, {rows={}, cols=COLS.new(names or it())}) end

function SYM.new(pos,name) 
  return new(SYM, {name=name, pos=pos, n=n, seen={}}) end

function NUM.new(pos,name)
  return new(NUM, {name=name, pos=pos, n=n, mu=0, m2=0, sd=0, lo=1E30, hi=-1E30}) end

function COLS.new(names,    all,x,y) 
  all,x,y = {},{},{}
  for i,s in pairs(names) do 
    push(all, 
        push(s:find"[!+-$]" and y or x, 
            (s:find"^[A-Z]" and NUM or SYM)(s,i))) end
  return new(COLS, {names=names, all=all, x=x, y=y}) end
------------------------------------------------------------------------------------------
function DATA.add(t) 
  push(self,rows, self.cols.add(t)) end

function COLS:add(t)
  for cs in each{self.x,self.y} do for c in each(cs) do col:add(t[c.pos]) end end end

function SYM:add(x)
  if x ~= "?" then
    self.n  = self.n+1
    self.seen[x] = 1 + (self.seen[x] or 0) end end 

function NUM:add(x,    d)
  if x ~= "?" then
    if x > self.hi then self.hi=x end
    if x < self.lo then self.lo=x end
    d       = x - self.mu
    self.n  = self.n + 1
    self.mu = self.mu + d/self.n
    self.m2 = self.m2 + d*(x - self.mu)
    self.sd = self.n<2 and 0 or (self.m2/(self.n - 1))^.5  end end
------------------------------------------------------------------------------------------
fmt = string.format
function adds(x,it)  for one in it do x:add(one) end; return x end
function each(t)     return function(lst,i) return next(lst,i) end, t, nil end
function push(t,x)   t[1+#t] = x; return x end
function sort(t,fun) table.sort(t,fun); return t end

function o(t)
  if type(n)=="number" then
    return n == math.floor(n) and tostring(n) or fmt(the.fmt,n) end
  if type(t) ~= "table" then return tostring(t) end
  return "(" .. table.concat(#t==0 and okeys(t) or olist(t))  .. ")" end

function olist(t,    u) 
  u={}; for k,v in pairs(t) do push(u, o(v)) end; return u end

function okeys(t,    u)
  u={}; for k,v in pairs(t) do push(u, fmt(":%s %s",k,o(v))) end; return sort(u) end

#!/usr/bin/env lua
local NUM,SYM,DATA,COLS = {},{},{},{}
local adds, as, cdf, cells, csv, fmt, o, oo, push, sort, welford
local abs,max,min = math.abs, math.max, math.min

local the = { bins  = 7,
              fmt   = "%6.3f", 
              train = "../data/misc/auto93.csv"}
------------------------------------------------------------------------------------------
local function new (kl,o) kl.__index=kl; setmetatable(o, kl); return o end

function SYM.new(name,pos) 
  return new(SYM, {name=name, pos=pos, n=0, seen={}}) end

function NUM.new(name,pos)
  return new(NUM, {name=name, pos=pos, n=0, mu=0, m2=0, sd=0, lo=1E30, hi=-1E30,
                   goal = (name or ""):find"-$" and 0 or 1}) end

function COLS.new(names,    all,x,y) 
  all,x,y = {},{},{}
  for i,s in pairs(names) do 
    col = push(all, (s:find"^[A-Z]" and NUM or SYM).new(s,i))
    if not s:find"X$" then push(s:find"[!+-$]" and y or x,col) end end
  return new(COLS, {names=names, all=all, x=x, y=y}) end

function DATA.new(  names) 
  return  new(DATA, {rows={}, cols=names and COLS.new(names) or nil}) end

function DATA:read(file)
  for row in csv(file) do self:add(row) end; return self end

function DATA:load(t)
  for _,row in pairs(t) do self:add(row) end; return self end
------------------------------------------------------------------------------------------
function DATA:add(t) 
  if self.cols then push(self.rows, self.cols:add(t)) else 
     self.cols = COLS.new(t) end end

function COLS:add(t)
  for _,cs in pairs{self.x,self.y} do for _,c in pairs(cs) do c:add(t[c.pos]) end end 
  return t end

function SYM:add(x)
  if x ~= "?" then
    self.n  = self.n+1
    self.seen[x] = 1 + (self.seen[x] or 0) end end 

function NUM:add(x,    d)
  if x ~= "?" then
    self.n  = self.n + 1
    self.mu, self.m2, self.sd = welford(x, self.n, self.mu, self.m2)
    if x > self.hi then self.hi=x end
    if x < self.lo then self.lo=x end end end
------------------------------------------------------------------------------------------
function NUM:norm(x)
  return x=="?" and x or (x - self.lo)/(self.hi - self.lo) end
------------------------------------------------------------------------------------------
function DATA:chebyshev(row,     d)
  d=0; for _,col in pairs(self.cols.y) do
         d = max(d, abs(col:norm(row[col.at]) - col.goal)) end
  return d end

function SYM:bin(x) return x end

function NUM:bin(x,    z,area) 
  if x=="?" then return x end
  z    = (x - i.mu) / i.sd
  area = z >= 0 and cdf(z) or 1 - cdf(-z) 
  return max(1, min(the.bins, 1 + (area * the.bins // 1))) end 
------------------------------------------------------------------------------------------
fmt = string.format
function adds(x,it)  for one in it do x:add(one) end; return x end
function cdf(z)      return 1 - 0.5*math.exp(1)^(-0.717*z - 0.416*z*z) end
function oo(x)       print(o(x)); return x end
function push(t,x)   t[1+#t] = x; return x end
function sort(t,fun) table.sort(t,fun); return t end
function welford(x,n,mu,m2,    d,sd)
  d  = x - mu
  mu = mu + d/n
  m2 = m2 + d*(x - mu)
  sd = n<2 and 0 or (m2/(n - 1))^.5  
  return mu,m2,sd end

function o(t,     list,keys)
  list= function(t,u) u={}; for k,v in pairs(t) do push(u, o(v)) end; return u end
  keys= function(t,u)
         u={}; for k,v in pairs(t) do push(u,fmt(":%s %s",k,o(v))) end; return sort(u) end
  if type(t)=="number" then
    return t == math.floor(t) and tostring(t) or fmt(the.fmt,t) end
  if type(t) ~= "table" then return tostring(t) end
  return "(" .. table.concat(#t==0 and keys(t) or list(t)," ")  .. ")" end

function as(s,    f)
  f=function(s) 
    if s=="nil" then return nil else return s=="true" or s ~="false" and s or false end end
  return math.tointeger(s) or tonumber(s) or f(s:match'^%s*(.*%S)') end

function cells(s,    t)
  t={}; for s1 in s:gsub("%s+", ""):gmatch("([^,]+)") do t[1+#t]=as(s1) end; return t end

function csv(src)
  src = src=="-" and io.stdin or io.input(src)
  return function(      s)
    s = io.read()
    if s then return cells(s) else io.close(src) end end end
------------------------------------------------------------------------------------------
local go={}
function go.ver() print("sandox v0.1") end

function go.the() oo(the) end

function go.csv(    n) 
  n=0; for row in csv(the.train) do n=n+1; if (n % 50)==0 then print(n,o(row)) end end end

function go.data(     d) 
  d = DATA.new():read(the.train)
  for _,col in pairs(d.cols.all) do oo(col) end end
  
go[ arg[1] or "ver" ]()

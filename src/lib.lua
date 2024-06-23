-- <!-- vim : set ts=2 sts=2 et : -->
--      ___              __        
--     /\_ \      __    /\ \       
--     \//\ \    /\_\   \ \ \____  
--       \ \ \   \/\ \   \ \ '__`\ 
--        \_\ \_  \ \ \   \ \ \L\ \
--        /\____\  \ \_\   \ \_,__/
--        \/____/   \/_/    \/___/ 
--
-- lib.lua: some standard Lua tricks
-- (c) 2024 Tim Menzies <timm@ieee.org>, BSD-2 license.

local lib ={}
local abs,exp,floor,log,max,min = math.abs,math.exp,math.floor, math.log, math.max, math.min

-- Cache the stuff needed  by rogue() to find var name typos
local b4={}; for k,_ in pairs(_ENV) do b4[k]=k end 

-- ### Objects
function lib.new (klass,object) 
  klass.__index=klass; setmetatable(object, klass); return object end

-- ### Meta
function lib.rogues()
  for k,v in pairs(_ENV) do if not b4[k] then print("Typo in var name? ",k,type(v)) end end end

function lib.map(t,f,     u) u={}; for k,v in pairs(t) do u[1+#u]= f(v)   end; return u end

function lib.kap(t,f,     u) u={}; for k,v in pairs(t) do u[1+#u]= f(k,v) end; return u end

--  # Shortcuts
lib.cat = table.concat
lib.fmt = string.format

-- ## Objects
function lib.is(class, object)  -- how we create instances
  class.__index=class; setmetatable(object, class); return object end

-- ## Maths
function lib.cdf(z) return 1 - 0.5*exp(1)^(-0.717*z - 0.416*z*z) end

function lib.welford(x,n,mu,m2,    d,sd)
  d  = x - mu
  mu = mu + d/n
  m2 = m2 + d*(x - mu)
  sd = n<2 and 0 or (m2/(n - 1))^.5  
  return mu,m2,sd end

function lib.minkowski(t1,t2,p,cols,           n,d)
  n,d = 0,0
  for _,col in pairs(cols) do
    n = n + 1
    d = d + col:dist(t1[col.pos],t2[col.pos]) ^ p end
  return (d/n)^(1/p) end

function lib.chebyshev(row,cols,     d)
  d=0; for _,col in pairs(cols) do d = max(d,abs(col:norm(row[col.pos]) - col.goal)) end
  return d end

-- ## Lists
function lib.push(t,x) t[1+#t]=x; return x end

function lib.shuffle(t,    u,j)
  u={}; for _,x in pairs(t) do u[1+#u]=x; end;
  for i = #u,2,-1 do j=math.random(i); u[i],u[j] = u[j],u[i] end
  return u end

function lib.powerset(s,       t)
  t = {{}}
  for i = 1, #s do
    for j = 1, #t do
      t[#t+1] = {s[i],table.unpack(t[j])} end end
   return t end

-- ### Sorting
function lib.sort(t,fun,     u) -- return a copy of `t`, sorted using `fun`,
  u={}; for _,v in pairs(t) do u[1+#u]=v end; table.sort(u,fun); return u end

-- Sort by a slot name in ascending, descending oder
function lib.up(x) return function(a,b) return a[x] < b[x] end end
function lib.down(x) return function(a,b) return a[x] > b[x] end end

-- Sort by a function applied to a table
function lib.on(fun) return function(a,b) return fun(a) < fun(b) end end

-- ## Strings to Things

-- Parse help strings
function lib.settings(s,     t)
  t={}
  for k,s1 in s:gmatch("[-][-]([%S]+)[^=]+=[%s]*([%S]+)") do t[k] = lib.coerce(s1) end
  return t,s end

-- Strings to atoms

local function _also(s)
  if s=="nil" then return nil else return s=="true" or s ~="false" and s or false end end

function lib.coerce(s,    also)
   return math.tointeger(s) or tonumber(s) or _also(s:match'^%s*(.*%S)') end

-- Iterate over rows in a table.
function lib.csv(src)
  src = src=="-" and io.stdin or io.input(src)
  return function(      s)
    s = io.read()
    if s then return lib.cells(s) else io.close(src) end end end

-- Turn a string into a list of atoms
function lib.cells(s,    t)
  t={}; for s1 in s:gsub("%s+", ""):gmatch("([^,]+)") do t[1+#t]=lib.coerce(s1) end
  return t end

-- ## Things to Strings (Pretty Print)

-- Print a pretty string
function lib.oo(t) print(lib.o(t)); return t end

-- Generate a pretty string
local function _olist(t,fmt,    u) 
  u={}; for k,v in pairs(t) do lib.push(u,lib.o(v,fmt))                 end; return u end

local function _okeys(t,fmt,    u) 
  u={}; for k,v in pairs(t) do 
          if not tostring(k):find"^_" then lib.push(u,lib.fmt(":%s %s",k,lib.o(v,fmt))) end end
  return u end

function lib.o(t,  fmt) 
  if type(t)=="number" then return t == floor(t) and tostring(t) or lib.fmt(fmt or "%6.3g",t) end
  if type(t)~="table"  then return tostring(t) end 
  return "(" .. table.concat(#t==0 and lib.sort(_okeys(t,fmt)) or _olist(t,fmt),", ")  .. ")" end

-- Simplify a number
function lib.rnd(n, ndecs)
  if type(n) ~= "number" then return n end
  if floor(n) == n  then return floor(n) end
  local mult = 10^(ndecs or 2)
  return floor(n * mult + 0.5) / mult end

return lib


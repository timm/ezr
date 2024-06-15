-- Lib.lua : misc lua tools
-- (c) 2024 Tim Menzies, timm@ieee.org, BSD-2 license

local lib ={}

local b4={}; for k,_ in pairs(_ENV) do b4[k]=k end -- used by rogue() to find var name typos

--  # Shortcuts
lib.cat = table.concat
lib.fmt = string.format

-- ## Objects
function lib.is(class, object)  -- how we create instances
  class.__index=class; setmetatable(object, class); return object end

-- ## Lists
function lib.push(t,x) t[1+#t]=x; return x end

-- ### Meta
function lib.map(t,f,     u) u={}; for k,v in pairs(t) do u[1+#u]= f(v)   end; return u end

function lib.kap(t,f,     u) u={}; for k,v in pairs(t) do u[1+#u]= f(k,v) end; return u end

function lib.rogues()
  for k,v in pairs(_ENV) do if not b4[k] then print("Typo in var name? ",k,type(v)) end end end

-- ### Sorting
function lib.sort(t,fun,     u) -- return a copy of `t`, sorted using `fun`,
  u={}; for _,v in pairs(t) do u[1+#u]=v end; table.sort(u,fun); return u end

function lib.by(x) return function(a,b) return a[x] < b[x] end end

function lib.on(fun) return function(a,b) return fun(a) < fun(b) end end

-- ## Strings to Things

function lib.settings(s,     t)
  t={}
  for k,s1 in s:gmatch("[-][-]([%S]+)[^=]+=[%s]*([%S]+)") do t[k] = lib.coerce(s1) end
  return t,s end

function lib.coerce(s,     _other)
  _other = function(s) if s=="nil" then return nil  end
                       return s=="true" or s ~="false" and s or false end
  return math.tointeger(s) or tonumber(s) or _other(s:match'^%s*(.*%S)') end

function lib.csv(src)
  src = src=="-" and io.stdin or io.input(src)
  return function(      s)
    s = io.read()
    if s then return lib.cells(s) else io.close(src) end end end

function lib.cells(s,    t)
  t={}; for s1 in s:gsub("%s+", ""):gmatch("([^,]+)") do t[1+#t]=lib.coerce(s1) end
  return t end

-- ## Things to Strings (Pretty Print)
function lib.oo(t) print(lib.o(t)); return t end

function lib.o(t,    _list,_dict,u)
  if type(t) == "number" then return tostring(lib.rnd(t)) end
  if type(t) ~= "table" then return tostring(t) end
  _list = function(_,v) return lib.o(v) end
  _dict = function(k,v) if not tostring(k):find"^_" then return lib.fmt(":%s %s",k,lib.o(v)) end end
  u = lib.kap(t, #t==0 and _dict or _list)
  return "{" .. lib.cat(#t==0 and lib.sort(u) or u ," ") .. "}" end

function lib.rnd(n, ndecs)
  if type(n) ~= "number" then return n end
  if math.floor(n) == n  then return math.floor(n) end
  local mult = 10^(ndecs or 2)
  return math.floor(n * mult + 0.5) / mult end

return lib

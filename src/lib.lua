#!/usr/bin/env lua
-- <!-- vim : set ts=4 sts=4 et : -->
local help=[[
lib.lua : misc Lua functions
(c)2024 Tim Menzies <timm@ieee.org> MIT license

## INSTALL
## INSTALL
wget https://raw.githubusercontent.com/timm/ezr/main/src/lib.lua

## USAGE 
Usually this code is `required` by other code. But if you want to test the demos:

    lua lib.lua --[XXX]

For a list of start up actions:

    lua lib.lua actions

To test all the demos

    lua lib.lua --all]]

-- ## Lib

local lib= {inf = 1E32}
local abs, max, min, rand = math.abs, math.max, math.min, math.random
local the=require"config"

-- ### Object creation
local _id = 0
local function id() _id = _id + 1; return _id end

-- `new(klass: klass, t: dict) -> dict`      
-- Add a unique `id`; connection `t` to its `klass`; ensure `klass` knows to call itself.
function lib.new (klass,t) 
  t._id=id(); klass.__index=klass; setmetatable(t,klass); return t end

-- ### Lists
-- `push(t: list, x:any) -> x`
function lib.push(t,x) t[1+#t]=x; return x end 

-- `sort(t: list, ?fun:callable) -> list`
function lib.sort(t,  fun) table.sort(t,fun); return t end

function lib.xby(x) 
  return type(x)=="function" and function(a,b) return x(a) < x(b) end 
                             or  function(a,b) print(4,x,lib.o(a)); return a[x] < b[x] end end 

-- `copy(t: any) -> any`
function lib.copy(t,     u)
  if type(t) ~= "table" then return t end 
  u={}; for k,v in pairs(t) do u[lib.copy(k)] = lib.copy(v) end 
  return setmetatable(u, getmetatable(t)) end

-- ### Thing to string
lib.fmt = string.format

-- `oo(x:any, ?fmt:str) -> x`   
-- Show `x`, then return it. Format numbers using `fmt` (defaults to "%g").
function lib.oo(x) print(lib.o(x,fmt)); return x end

-- `o(x:any,?fmt:str) -> str`   
-- Generate a show string for `x`. Format numbers using `fmt` (defaults to "%g").
function lib.o(x,   fmt)
  if type(x)=="number" then return lib.fmt(fmt or the.fmt or "%g",x) end
  if type(x)~="table"  then return tostring(x) end 
  return "{" .. table.concat(#x==0 and lib.okeys(x,fmt) or lib.olist(x,fmt),", ")  .. "}" end

-- `olist(t:list, ?fmt:str) -> str`   
-- Generate a show string for tables with numeric indexes. Format numbers using `fmt` (defaults to "%g").
function lib.olist(t,  fmt)  
  local u={}; for k,v in pairs(t) do lib.push(u, lib.fmt("%s", lib.o(v,fmt))) end; return u end

-- `okeys(t:dict,?fmt: str) -> str`   
-- Generate a show string for tables with symboloc indexes. Skip private keys; i.e.
-- those starting with "_". Format numbers using `fmt` (defaults to "%g").
function lib.okeys(t,  fmt)  
  local u={} 
  for k,v in pairs(t) do 
    if not tostring(k):find"^_" then lib.push(u, lib.fmt(":%s %s", k,lib.o(v,fmt))) end end; 
  return lib.sort(u) end

-- ### Strings to things

-- `coerce(s:str) -> thing`    
function lib.coerce(s,    also)
  if type(s) ~= "string" then return s end
  also = function(s) return s=="true" or s ~="false" and s end 
  return math.tointeger(s) or tonumber(s) or also(s:match"^%s*(.-)%s*$") end 

-- `coerces(s:str) -> list[thing]`
-- Coerce everything inside a comma-seperated string.
function lib.coerces(s,    t)
  t={}; for s1 in s:gsub("%s+", ""):gmatch("([^,]+)") do t[1+#t]=lib.coerce(s1) end
  return t end

-- Iterator `csv(file:str) -> list[thing]`
function lib.csv(file)
  file = file=="-" and io.stdin or io.input(file)
  return function(      s)
    s = io.read()
    if s then return lib.coerces(s) else io.close(file) end end end

-- `settings(s:tr) -> dict`  
-- For any line containing `--(key) ... = value`, generate `key=coerce(value)` .
function lib.settings(s,     t)
  t={}
  for k,s1 in s:gmatch("[-][-]([%S]+)[^=]+=[%s]*([%S]+)[.]*\n") do 
    t[k] = lib.coerce(s1) end
  return t end

function lib.all(eg,t,     reset,fails)
  fails,reset = 0,lib.copy(the)
  for _,x in pairs(t) do
    print(1)
    math.randomseed(the.seed) -- setup
    print(2)
    if eg[lib.oo(x)]()==false then fails=fails+1 end
    the = lib.copy(reset) -- tear down
  end 
  os.exit(fails) end 

return lib

-- My LUA library
local l={}
--[[
In my LUA code:

- In function argument lists, two spaces denote optional args while 
  four spaces denote local vars.)
- A function name that is all UPPER CASE is a constructor.
- If a constructor name is `THING`, then `thing1` is something made by THING
- The thing named in lower case, is a function to update `thing`s. 
  - So things build by `function NUM() ...` are updated by `function num() ...`.
- Usually:
  -`s`,`n`  denote strings and numbers.
  -  `d` and `a` are for arrays with symbolic or integer keys.
  - `t` is an array that could be `d` or `a` 
  - `ts,as,as` and `tn, dn,an` are  arrays of strings or numbers (respectively). 
  - `tthing, athing, dthing` denote arrays of `thing` 
  - `fun` denotes a function. ]]

-- In LUA, everything is global unless declared `local`. To catch things that might
-- better be declared local, use the function `rogue`. 
local b4={};  for k, _ in pairs(_ENV) do l.b4[k]=k end
function l.rogue()
  for k,v in pairs(_ENV) do if not b4[k] then print("W> rogue? ",k) end end end

-- ## Lists
-- Push `x` onto `a` and return `x`.
function l.push(a,x) a[#a+1]=x; return x end

-- Schwartzian transform:  decorate, sort, undecorate (so while sorting, only
-- compute the key once).
function l.keysort(a,fun,...)
  local u,v
  u={}; for _,x in pairs(a) do u[1+#u]={x=x, y=fun(x,...)} end -- decorate
  table.sort(u, function(one,two) return one.y < two.y end) -- sort
  v={}; for _,xy in pairs(u) do v[1+#v] = xy.x end -- undecoreate
  return v end
  
-- ## Coerce strings to things
-- Coerce an atomic thing.
function l.coerce(s,    fun) 
  function fun(s1)
    return s1=="true" or (s1~="false" and s1) or false end 
  return math.tointeger(s) or tonumber(s) or fun(s:match'^%s*(.*%S)') end

-- Return rows of a csv file, coerciing all the cells as we go.
function l.csv(src,    parse)
  src  = src=="-" and io.stdin or io.input(src)
  return function(      s,a)
    s=io.read()
    if s 
    then a={}; for s1 in s:gmatch("([^,]+)") do a[1+#a]=l.coerce(s1) end; return a end
    else io.close(src) end end end

return l
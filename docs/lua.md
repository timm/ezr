# Introduction to Lua for Software Engineering

## Overview
Lua is a lightweight, high-level, multi-paradigm programming language designed primarily for embedded use in applications. It's known for its simplicity and flexibility, making it a popular choice in game development, web servers, and other embedded systems.

Many of the implementation choices within Lua were made, carefully balancing  simplicity and functionality. For example,
everything in Lua is global by default unelss:

- it is declared as a extra argument in a function argument list
- it is declared using the keyword `local`.

## Basic Concepts

### Variables and Functions
In Lua, variables are dynamically typed, and functions are first-class citizens, meaning they can be stored in variables, passed as arguments, and returned from other functions.

```lua
local abs, exp, floor = math.abs, math.exp, math.floor
```
- `local` declares a variable with local scope.
- `math.abs`, `math.exp`, and `math.floor` are standard library functions for absolute value, exponentiation, and flooring a number, respectively.

### Tables
Tables are the main data structure in Lua, used to represent arrays, dictionaries, and objects.

```lua
local lib = {}
```
- `lib` is an empty table, which can be used to store functions and variables.

```lua
local the = {seed=1234567891,
             train="../data/misc/auto93.csv"}
```
- `the` is not a place to store settings; e.g. the random number seed is help in `the.seed`.

### Object-Oriented Polymorphsim
Lua supports object-oriented polyorphism through the use of tables and metatables. When `object` is sent a message
it does not understand, it asks for help from its metatable. That metatable realize there is something missing
so it asks its `__index`  what to do. If that table's `__index' points to itself then we  can store the object
data in the data and the methods for that object's class in the meta table.

```lua
function lib.new(klass, object)
  klass.__index = klass
  setmetatable(object, klass)
  return object end
```
- `lib.new` is a constructor function that sets up the polymorphism for a new obkect.
  `klass.__index = klass` and `setmetatable(object, klass)` make `object` use emthods defined in  `klass`.
  For example:

```lua
function Singer:new(name,age) return new(Singer,{name=name,age=age}) end
function Write:new(name,age) return new(Writer,{name=name,age=age}) end

function Writer:perfom() .. end -- reads poety
function Singer:perfom() .. end -- sings a cong
```


## Key Functions

### Error Detection
```lua
function lib.rogues()
  for k, v in pairs(_ENV) do
    if not b4[k] then
      print("Typo in var name?", k, type(v)) end end end
```
- `lib.rogues` detects undeclared global variables, which might indicate typos or errors in variable names.

### Functional Programming
Lua supports higher-order functions, allowing functions to be passed as arguments and returned from other functions.

```lua
function lib.map(t, f)
  local u = {}
  for k, v in pairs(t) do
    u[1 + #u] = f(v) end
  return u
end
```
- `lib.map` applies function `f` to each element in table `t` and returns a new table with the results.

## Practical Examples

### Sorting
Sorting can be customized by passing different comparison functions.

```lua
function lib.sort(t, fun)
  local u = {}
  for _, v in pairs(t) do u[1 + #u] = v end
  table.sort(u, fun)
  return u end
```
- `lib.sort` creates a sorted copy of table `t` using the comparison function `fun`.

### String Parsing
Lua excels at parsing and transforming strings. For example, suppose our code file starts with a help
string (note: multi-line strings in Lua are defined with `[[...]]`).

```lua
local lib=require"lib"
local the,help = lib.setting([[
  
xai: multi-goal semi-supervised explanation
(c) 2023 Tim Menzies <timm@ieee.org> BSD-2
  
USAGE: lua xai.lua [OPTIONS] [-g ACTIONS]
  
OPTIONS:
  -b  --bins    initial number of bins       = 16
  -f  --file    data file                    = ../etc/data/auto93.csv
  -R  --Reuse   child splits reuse a parent pole = true
  -s  --seed    random number seed           = 1234567891]])
```
The following code builds a table with  `key=value` parirs for every line containing `--`, For example,
the above string would geneerate

    {bins=16, file="../etc/data/auto93.csv", Reuse=true, seed=1234567891}

Here's that code:

```lua
function lib.settings(s)
  local t = {}
  for k, s1 in s:gmatch("[-][-]([%S]+)[^=]+=[%s]*([%S]+)") do t[k] = lib.coerce(s1) end
  return t, s end

local function _also(s)
  if s=="nil" then return nil else return s=="true" or s ~="false" and s or false end end

function lib.coerce(s,    also)
   return math.tointeger(s) or tonumber(s) or _also(s:match'^%s*(.*%S)') end
```
- `lib.settings` parses key-value pairs from a string `s`.
- `lib.coerce` converts a string to a number if possible, otherwise returns the string.

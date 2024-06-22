
#  Discretizing Data Columns using Equal Frequency Discretization in Lua

In this detailed tutorial, we'll explore the code for discretizing data columns via equal frequency discretization, implemented in Lua. This method divides the range of numerical attributes into intervals that contain approximately the same number of data points. We'll provide an in-depth explanation of the code and its components.

# 1. Prerequisites

Ensure you have the Lua programming environment set up and the required CSV data file ready.

# 2. Code Overview

The provided Lua script performs equal frequency discretization on data columns while skipping unknown entries marked with `"?"`.

# 3. Code Breakdown

## 3.1. Initial Setup

First, we set up some configurations and import necessary libraries:

```lua
#!/usr/bin/env lua
-- <!-- vim : set ts=4 sts=4 et : -->

local the = { bins  = 16,
              train = "../data/misc/auto93.csv"}

local l = require "lib"
local BIN, DATA = {}, {}
local abs, max, min = math.abs, math.max, math.min
local csv, new, o, oo, push = l.csv, l.new, l.o, l.oo, l.push

local the = { train = "../data/misc/auto93.csv"}
```

Here, we define the configuration settings for the script, such as the number of bins (`bins = 16`) and the path to the training data file (`train = "../data/misc/auto93.csv"`). We also import functions from the `lib` module.

## 3.2. Helper Functions

We define a helper function to identify column types based on naming patterns:

```lua
local function is(name, x, pat)
  pat = {num = "^[A-Z]", goal = "[!+-]$", min = "-$", ignore = "X$"}
  return name:find(pat[x])
end
```

This function checks the column name against predefined patterns to determine if it represents a numerical attribute, a goal, a minimum value, or if it should be ignored.

# 4. BIN Class

The `BIN` class represents a bin for discretization. Each bin keeps track of the range of values it contains, the number of entries, and the sum of distances for those entries.

## 4.1. Creating a New BIN

```lua
function BIN.new(pos, name, lo, hi)
  return new(BIN, {pos = pos, name = name, n = 0, ds = 0, rowids = {}, lo = lo or math.huge, hi = hi or -math.huge})
end
```

The `BIN.new` function initializes a new bin with the specified position, name, and optional lower (`lo`) and upper (`hi`) bounds.

## 4.2. Adding an Entry to a BIN

```lua
function BIN:add(row, data, x)
  x = row[self.pos]
  if x ~= "?" then
    self.n = self.n + 1
    self.ds = self.ds + (1 - data:chebyshev(row))
    if x < self.lo then self.lo = x end
    if x > self.hi then self.hi = x end
    push(self.rowids, row[#row])
  end
end
```

The `BIN:add` function adds a row to the bin if the value is not unknown (`"?"`). It updates the count (`n`), the sum of distances (`ds`), and the lower (`lo`) and upper (`hi`) bounds.

## 4.3. String Representation of a BIN

```lua
function BIN:__tostring(lo, hi, s)
  lo, hi, s = self.lo, self.hi, self.name
  if lo == -math.huge then return string.format("%s < %s", s, hi) end
  if hi == math.huge then return string.format("%s >= %s", s, lo) end
  if lo == hi then return string.format("%s == %s", s, lo) end
  return string.format("%s <= %s < %s", lo, s, hi)
end
```

The `BIN:__tostring` function provides a string representation of the bin's range and name.

# 5. DATA Class

The `DATA` class handles reading and processing the data. It stores the data rows, column names, goal columns, and numerical columns.

## 5.1. Creating a New DATA Object

```lua
function DATA.new()
  return new(DATA, {rows = {}, names = nil, goals = {}, nums = {}})
end
```

The `DATA.new` function initializes a new `DATA` object.

## 5.2. Reading Data

```lua
function DATA:read(it)
  for row in it do
    if self.names then self:_body(row) else self:_header(row) end
  end
  return self
end
```

The `DATA:read` function reads data from an iterator (`it`). It processes the header row and data rows accordingly.

## 5.3. Sorting Data

```lua
function DATA:sort(d)
  d = function(row) return self:chebyshev(row) end
  table.sort(self.rows, function(a, b) return d(a) < d(b) end)
  return self
end
```

The `DATA:sort` function sorts the data rows based on their Chebyshev distance.

## 5.4. Processing Header and Body Rows

```lua
function DATA:_header(row, _header)
  self.names = row
  for c, name in pairs(self.names) do
    if not is(name, "ignore") then
      if is(name, "goal") then self.goals[c] = is(name, "min") and 0 or 1 end
      if is(name, "num") then self.nums[c] = {lo = math.huge, hi = -math.huge} end
    end
  end
end

local _rowid = 0
function DATA:_body(row)
  _rowid = _rowid + 1
  push(row, _rowid)
  push(self.rows, row)
  for c, num in pairs(self.nums) do
    num.lo = min(row[c], num.lo)
    num.hi = max(row[c], num.hi)
  end
end
```

The `DATA:_header` function processes the header row to identify column types and initialize numerical columns. The `DATA:_body` function processes data rows and updates numerical column ranges.

## 5.5. Normalizing Data

```lua
function DATA:norm(c, x, num)
  num = self.nums[c]
  return x == "?" and x or (x - num.lo) / (num.hi - num.lo + 1E-30)
end
```

The `DATA:norm` function normalizes a value in a column based on the column's range.

## 5.6. Calculating Chebyshev Distance

```lua
function DATA:chebyshev(row, d)
  d = 0
  for c, goal in pairs(self.goals) do
    d = max(d, abs(self:norm(c, row[c]) - goal))
  end
  return d
end
```

The `DATA:chebyshev` function calculates the Chebyshev distance of a row from the goal values.

# 6. Discretizing Columns

The `DATA:bins` method performs the discretization of columns:

```lua
function DATA:bins(bins)
  bins = {}
  for c, name in pairs(self.names) do
    if not is(name, "goals") then
      if is(name, "nums") then self:nums2bins(c, name, bins)
      else self:syms2bins(c, name, bins) end
    end
  end
  return l.sort(bins, l.down "ds")
end
```

## 6.1. Discretizing Symbolic Columns

```lua
function DATA:syms2bins(c, name, bins, tmp, x)
  tmp = {}
  for m, row in pairs(self.rows) do
    x = row[c]
    if x ~= "?" then
      tmp[x] = tmp[x] or push(bins, BIN.new(c, name, x, x))
      tmp[x]:add(row, self)
    end
  end
end
```

The `DATA:syms2bins` function discretizes symbolic columns by grouping rows with the same value into bins.

## 6.2. Discretizing Numerical Columns

```lua
function DATA:nums2bins(c, name, bins, _value, bin, x, want)
  _value = function(row) return row[c] == "?" and -math.huge or row[c] end
  bin = push(bins, BIN.new(c, name, -math.huge))
  self.rows = l.sort(self.rows, function(a, b) return _value(a) < _value(b) end)
  for m, row in pairs(self.rows) do
    x = row[c]
    if x ~= "?" then
      want = want or (#self.rows - m) / the.bins
      if bin.n > want then
        if x ~= self.rows[m - 1][c] then
          bin = push(bins, BIN.new(c, name, bin.hi))
        end
```

# Core functions
This section defines basic tools used throughout the code:
- `new` for prototypal inheritance
- `isa` to test types
- `sum` as a shortcut
- `coerce` to convert strings into typed atoms

    new = (klass, t={}) ->
      klass.__index = klass
      Object.assign t, klass
      t
    
    isa = (x, klass) -> x instanceof klass
    
    sum = (lst) -> lst.reduce ((a,b) -> a + b), 0
    
    coerce = (s) ->
      s = s.trim()
      return true  if s in ['true', 'True']
      return false if s in ['false', 'False']
      parseFloat(s) if /^\d/.test s
      s

# Statistics: Sym and Num
Symbols (`Sym`) count categories. Numbers (`Num`) track
running mean, standard deviation, and range. We also define:
- `add` to update stats
- `mid` to find the central value
- `div` to measure diversity

    class Sym
      constructor: ->
    
    class Num
      constructor: ->
        @lo = 1e32
        @hi = -1e32
        @mu = @m2 = @sd = @n = 0
        @heaven = 1
    
    add = (col,v,inc=1) ->
      return v if v == "?"
      if col instanceof Sym
        col[v] ?= 0
        col[v] += inc
      else
        col.n += inc
        if inc < 0 and col.n < 2
          col.mu = col.sd = col.m2 = 0
        else
          d = v - col.mu
          col.mu += inc * d / col.n
          col.m2 += inc * d * (v - col.mu)
          col.sd = if col.n < 2 then 0 else Math.sqrt         Math.max 0, col.m2 / (col.n - 1)
        col.lo = Math.min v, col.lo
        col.hi = Math.max v, col.hi
      v
    
    mid = (col) ->
      if col instanceof Sym
        best = null
        most = -1
        for k, v of col
          [best, most] = [k,v] if v > most
        best
      else
        col.mu
    
    div = (col) ->
      if col instanceof Sym
        N = sum (v for k,v of col)
        sum (-(v/N)*Math.log(v/N)/Math.LN2 for k,v of col)
      else
        col.sd

# Data: Rows and Columns
The `Data` structure stores tabular data and summarizes
columns. It uses:
- `adds` to incrementally update statistics
- `Data()` to initialize from headers and rows
- `clone()` to duplicate structure
- `mids()` to extract central values per column

    adds = (data,row,inc=1,zap=false) ->
      if inc > 0
        data.rows.push row
      else if zap
        for i in [data.rows.length-1..0]
          if data.rows[i] is row
            data.rows.splice i,1
            break
      add col, row[i], inc for col, i in data.cols.all.entries()
      row
    
    Data = (src) ->
      _cols = (names) ->
        out = names: names, all: [], x: {}, y: {}, klass: null
        for s, i in names
          col = if /^[A-Z]/.test s then new Num else new Sym
          out.all.push col
          continue if /X$/.test s
          out.klass = i if /!$/.test s
          col.heaven = 0 if /-$/.test s
          tgt = if /[!+-]$/.test s then out.y else out.x
          tgt[i] = col
        out
    
      names = src.shift()
      data = rows: [], cols: _cols names
      adds data, row for row in src
      data
    
    clone = (data, rows=[]) ->
      out = Data [data.cols.names]
      adds out, r for r in rows
      out
    
    mids = (data) -> [mid col for col in data.cols.all]

# Distances and Normalization
We define:
- `norm` to normalize numbers
- `xdist` to compare independent columns
- `ydist` to measure distance to "heaven"
- `minkowski` for generalized distance

    norm = (col,v) ->
      return v if v == "?" or col instanceof Sym
      (v - col.lo) / (col.hi - col.lo + 1e-32)
    
    minkowski = (nums) ->
      p = the.p
      d = sum (x**p for x in nums)
      (d / nums.length) ** (1/p)
    
    xdist = (data, r1, r2) ->
      _aha = (col, a, b) ->
        return 1 if a == "?" and b == "?"
        if col instanceof Sym then return +(a != b)
        a = norm(col,a)
        b = norm(col,b)
        a = if a == "?" then (if b > 0.5 then 0 else 1) else a
        b = if b == "?" then (if a > 0.5 then 0 else 1) else b
        Math.abs a - b
    
      minkowski (_aha(col, r1[c], r2[c]) for c, col of data.cols.x)
    
    ydist = (data, row) ->
      minkowski (Math.abs(norm(col, row[c]) - col.heaven)
                 for c, col of data.cols.y)

# Bayesian Classification
We estimate class likelihoods using:
- `like()` to measure match per column
- `likes()` to compute log-likelihood of a row
- `liked()` to find the best class

    like = (col, v, prior=0) ->
      if col instanceof Sym
        (col[v] or 0 + the.m * prior) /     (sum(v for k,v of col) + the.m + 1e-32)
      else
        var = 2 * col.sd * col.sd + 1e-32
        z = (v - col.mu) ** 2 / var
        Math.exp(-z) / Math.sqrt(2 * Math.PI * var)
    
    likes = (data, row, nall=100, nh=2) ->
      prior = (data.rows.length + the.k) / (nall + the.k * nh)
      tmp = [like(col, row[c], prior)
             for c, col of data.cols.x when row[c] != "?"]
      sum Math.log(n) for n in tmp.concat(prior) when n > 0
    
    liked = (datas, row, nall=null) ->
      nall ?= sum(data.rows.length for k,data of datas)
      best = null
      best_val = -Infinity
      for k, data of datas
        val = likes(data, row, nall, Object.keys(datas).length)
        [best, best_val] = [k, val] if val > best_val
      best

# Evaluation with Confusion Matrix
To assess classification:
- `Confuse()` creates a stats holder
- `confuse()` updates matrix with a guess
- `confused()` returns summary stats like precision

    Confuse = ->
      klasses: {}, total: 0
    
    confuse = (cf, want, got) ->
      for x in [want, got]
        cf.klasses[x] ?= label: x, tn: cf.total, fn: 0, fp: 0, tp: 0
      for c in Object.values cf.klasses
        if c.label is want
          c.tp += +(got is want)
          c.fn += +(got isnt want)
        else
          c.fp += +(got is c.label)
          c.tn += +(got isnt c.label)
      cf.total += 1
      got
    
    confused = (cf, summary=false) ->
      percent = (y,z) -> Math.round 100 * y / (z or 1e-32)
      finalize = (c) ->
        c.pd = percent c.tp, c.tp + c.fn
        c.prec = percent c.tp, c.fp + c.tp
        c.pf = percent c.fp, c.fp + c.tn
        c.acc = percent c.tp + c.tn, c.tp + c.fp + c.fn + c.tn
        c
    
      if summary
        out = label: "_OVERALL", tn:0, fn:0, fp:0, tp:0
        for c in Object.values cf.klasses
          c = finalize c
          for k in ["tn","fn","fp","tp"]
            out[k] += c[k]
        return finalize out
    
      list = Object.values cf.klasses
      list.map finalize
      list.push confused(cf, true)
      list.sort (a,b) -> (a.fn + a.tp) - (b.fn + b.tp)

# CLI and I/O Utilities
Here we define:
- `csv()` to read data
- `has()` to summarize a list
- `pretty()` to format values
- `show()` to print tables

    csv = (file) ->
      require('fs').readFileSync(file, 'utf-8')
        .split('\n')
        .filter (line) -> line and not line.startsWith "%"
        .map (line) -> (coerce x.trim() for x in line.split ',')
    
    has = (src, col=null) ->
      for row in src
        col ?= if typeof row is 'number' then new Num else new Sym
        add col, row
      col
    
    pretty = (v, prec=0) ->
      return v.toFixed prec if typeof v is 'number' and v % 1
      "#{v}"
    
    show = (lst, pre="| ", prec=0) ->
      head = Object.keys lst[0]
      rows = [[pretty(r[k], prec) for k in head] for r in lst]
      table = [head].concat rows
      gaps = [Math.max ...(row[i].length for row in table) for i in [0...head.length]]
      fmt = (row) ->
        pre + row.map((r,i) -> r.padStart gaps[i]).join(" | ") + " |"
      console.log fmt head
      console.log pre + gaps.map((g) -> "-".repeat g).join(" | ") + " |"
      console.log fmt r for r in rows

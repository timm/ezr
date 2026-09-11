Num = ->{ [0, 0, 0] }                      # n, mu, m2: all Welford keeps
def rnd                                    # MINSTD, shared by all ports
  $seed = $seed * 16807 % 2147483647
  $seed / 2147483647.0
end
def shuffle(a)                             # Fisher-Yates, in shared rnd order
  a = a.dup
  (a.size - 1).downto(1) { |i| j = (rnd * (i + 1)).to_i; a[i], a[j] = a[j], a[i] }
  a
end
def sd(c) = c[0] < 2 ? 0 : sqrt(c[2] / (c[0] - 1.0))
def add(c, v, inc = 1)                     # new Num, or updated Sym
  return c if v == "?"
  return c.merge!(v => (c[v] || 0) + inc) if c.is_a?(Hash)
  n, mu, m2 = c
  n += inc
  d = v - mu
  mu += inc * d / [1, n].max.to_f
  [n, mu, [0, m2 + inc * d * (v - mu)].max]
end
def adds(lst, it = nil)                    # accumulate a list into it
  it ||= Num.()
  lst.each { |y| it = add(it, y) }
  it
end
def size(c) = c.is_a?(Hash) ? c.values.sum : c[0]
def div(c)                                 # Num: sd. Sym: entropy
  return sd(c) unless c.is_a?(Hash)
  n = c.values.sum.to_f
  -c.values.sum { |v| v > 0 ? v / n * log2(v / n) : 0 }
end
def addRow(tbl, row = nil, inc = 1)        # inc=-1 pops the last row
  tbl[:_mids] = nil
  inc > 0 ? tbl[:rows].push(row) : row = tbl[:rows].pop
  tbl[:cols].each { |at, c| tbl[:cols][at] = add(c, row[at], inc) }
  row
end
def Tbl(src)
  tbl = {rows: [], cols: {}, x: [], y: {}, names: src[0], klass: nil}
  src[0].each_with_index do |s, at|
    next if s.end_with?("X")
    tbl[:cols][at] = s[0] == s[0].upcase ? Num.() : {}
    case s[-1]
    when "!"      then tbl[:klass] = at
    when "+", "-" then tbl[:y][at] = s[-1] == "+" ? 1 : 0
    else tbl[:x].push(at)
    end
  end
  src[1..].each { |row| addRow(tbl, row) }
  tbl
end
def clone(tbl, rows = []) = Tbl([tbl[:names]] + rows)
def norm(col, v)
  z = (v - col[1]) / (1e-32 + sd(col))
  1 / (1 + exp(-1.7 * z.clamp(-3, 3)))
end
def mid(col) = col.is_a?(Hash) ? col.max_by { |_, v| v }[0] : col[1]
def mids(tbl)                              # x centroid; cached until rows change
  tbl[:_mids] ||= tbl[:x].to_h { |at| [at, mid(tbl[:cols][at])] }
end
def mink(gaps) = (gaps.sum { |g| g**$P } / gaps.size.to_f)**(1.0 / $P)
def ydist(tbl, row)
  mink(tbl[:y].map { |at, w| (norm(tbl[:cols][at], row[at]) - w).abs })
end
def _dist(col, a, b)
  return 1 if a == "?" || b == "?"
  col.is_a?(Hash) ? (a != b ? 1 : 0) : (norm(col, a) - norm(col, b)).abs
end
def xdist(tbl, row, m)
  mink(tbl[:x].map { |at| _dist(tbl[:cols][at], row[at], m[at]) })
end
def ymu(tbl, rows) = rows.sum { |r| ydist(tbl, r) } / rows.size.to_f
def ymids(tbl, rows)
  tbl[:y].keys.map { |at| rows.sum { |r| r[at] } / rows.size.to_f }
end
def centroid(tbl, best, rest)              # near best, far from rest
  ->(z) { xdist(tbl, z, mids(rest)) - xdist(tbl, z, mids(best)) }
end
def label(tbl, best, rest, row)            # keep best pool near sqrt
  addRow(best, row)
  best[:rows] = best[:rows].sort_by { |r| ydist(tbl, r) }
  b, r = best[:rows].size, rest[:rows].size
  addRow(rest, addRow(best, nil, -1)) if b > sqrt(1 + b + r)
end
def acquire(tbl, cap = nil, score = method(:centroid))  # pop the top scorer
  best, rest = clone(tbl), clone(tbl)
  todo = shuffle(tbl[:rows])[0, $Few]
  $Start.times { label(tbl, best, rest, todo.pop) }
  cap ||= $Stop
  while !todo.empty? && best[:rows].size + rest[:rows].size < cap
    f = score.(tbl, best, rest)
    todo = todo.sort_by { |r| f.(r) }
    label(tbl, best, rest, todo.pop)
  end
  best[:rows] + rest[:rows]
end
def cohen(xs, ys, d = 0.35, eps = 0)       # gap vs pooled sd, floored
  a, b = adds(xs), adds(ys)
  pool = ((a[0] - 1) * sd(a)**2 + (b[0] - 1) * sd(b)**2) / (a[0] + b[0] - 2)
  (a[1] - b[1]).abs <= [eps, d * sqrt(pool)].max
end
def cliffs(xs, ys, d = 0.197)              # sorted in. rank imbalance ok?
  gt = lt = j = k = 0
  xs.each do |x|
    (j += 1; k = j) while j < ys.size && ys[j] < x
    k += 1 while k < ys.size && ys[k] <= x
    gt += j; lt += ys.size - k
  end
  (gt - lt).abs / (xs.size * ys.size).to_f <= d
end
def ks(xs, ys, a = 1.36)                   # sorted in. 95% kolmogorov-smirnov
  n, m, i, j, d = xs.size, ys.size, 0, 0, 0
  while i < n && j < m
    v = [xs[i], ys[j]].min
    i += 1 while i < n && xs[i] <= v
    j += 1 while j < m && ys[j] <= v
    d = [d, (i.to_f / n - j.to_f / m).abs].max
  end
  d <= a * sqrt((n + m).to_f / (n * m))
end
def same(xs, ys, eps = 0)                  # indistinguishable, by all three
  xs, ys = xs.sort, ys.sort
  cliffs(xs, ys) && ks(xs, ys) && cohen(xs, ys, 0.35, eps)
end

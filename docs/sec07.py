#-- stats -------------------------------------------------
def cohen(xs, ys, d=0.35, eps=0): # gap vs pooled sd, floored
  a, b = adds(xs), adds(ys)
  pool = ((a[0]-1)*sd(a)**2 + (b[0]-1)*sd(b)**2)/(a[0]+b[0]-2)
  return abs(a[1] - b[1]) <= max(eps, d * sqrt(pool))

def cliffs(xs, ys, d=0.197): # sorted in. rank imbalance ok?
  gt = lt = j = k = 0
  for x in xs:
    while j < len(ys) and ys[j] <  x: j += 1; k = j
    while k < len(ys) and ys[k] <= x: k += 1
    gt += j; lt += len(ys) - k
  return abs(gt - lt) / (len(xs) * len(ys)) <= d

def ks(xs, ys, a=1.36): # sorted in. 95% kolmogorov-smirnov
  n, m, i, j, d = len(xs), len(ys), 0, 0, 0
  while i < n and j < m:
    v = min(xs[i], ys[j])
    while i < n and xs[i] <= v: i += 1
    while j < m and ys[j] <= v: j += 1
    d = max(d, abs(i/n - j/m))
  return d <= a * sqrt((n + m) / (n * m))

def same(xs, ys, eps=0): # indistinguishable, by all three
  xs, ys = sorted(xs), sorted(ys)
  return (cliffs(xs,ys) and ks(xs,ys) and cohen(xs,ys,eps=eps))


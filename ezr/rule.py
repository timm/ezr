#-- Rule Generation ----------------------------------------------------
# --- build 1 rile
def ruleAdd(rule, at, b):
  spans = rule.setdefault(at, [])
  for i, (a, z) in enumerate(spans):
    if a-1 <= b <= z+1:
      spans[i] = (min(a,b), max(z,b))
      return
  spans.append((b, b))

def ruleSeen(rule, at, b):
  return at in rule and any(a <= b <= z for a, z in rule[at])

# --- query rows with a rule 
def ruleSelect(data, rule, row):
  fn = lambda at, a, z: a <= bucket(data.cols.all[at], row[at]) <= z
  return all(any(fn(at, a, z) for a, z in spans)
             for at, spans in rule.items())

def ruleSelects(data, rule, rows):
  return [r for r in rows if ruleSelect(data, rule, r)]

# --- show a rule
def ruleShow1(txt, lo, hi):
  return f"{txt} == {o(lo)}" if lo == hi else f"{o(lo)} <= {txt} <= {o(hi)}"

def ruleShow(rule, data, lo, hi, rows=None):
  pre = "IF  "
  for at, spans in rule.items():
    txt = data.cols.all[at].txt
    s = " OR ".join(ruleShow1(txt,lo[at,a],hi[at,b]) for a,b in spans)
    if rows:
      rows = ruleSelects(data, {at: spans}, rows)
      s2 = adds(disty(data, r) for r in rows)
      print(f"{pre}{s:<35} THEN {o(s2.mu)} ({s2.n})")
    else:
      print(f"{pre}{s}")
    pre = "AND "
   
# --- grow rules
def ruleGrow(data):
  lo, hi = {}, {}
  def stats(rows):
    d, n = {}, len(rows)
    for r in rows:
      for c in data.cols.x:
        if (v := r[c.at]) != "?":
          k = (c.at, bucket(c, v))
          d[k] = d.get(k, 0) + 1 / n
          lo[k] = min(lo.get(k, v), v)
          hi[k] = max(hi.get(k, v), v)
    return d

  def score(b, r): return b**2 / (b + r + 1e-30)

  def grow(b, r, rule):
    if len(b) > the.leaf and r:
      bd, rd = stats(b), stats(r)
      if most:= max((k for k in bd if not ruleSeen(rule,*k)),default=None,
                      key=lambda k: score(bd[k], rd.get(k, 0))):
        at, want = most
        b1 = ruleSelects(data, {at:[(want,want)]}, b)
        r1 = ruleSelects(data, {at:[(want,want)]}, r)
        s  = adds(disty(data, row) for row in b1)
        if s.n >= the.leaf and (len(b1) < len(b) or len(r1) < len(r)):
          ruleAdd(rule, at, want)
          grow(b1, r1, rule)

  data.rows.sort(key=lambda r: disty(data, r))
  n = max(int(len(data.rows)**0.5), the.leaf + 1)
  rule = {}
  grow(data.rows[:n], data.rows[n:], rule)
  return rule, lo, hi

def eg__bore(f:filename):
  "best or rest rule generation"
  data = DATA(csv(f))
  some = clone(data, shuffle(data.rows)[:50])
  [print(row) for row in some.rows]
  rule, lo, hi = ruleGrow(some)
  n = max(int(len(some.rows)**0.5), the.leaf + 1)
  ruleShow(rule, some, lo, hi, some.rows[:n])



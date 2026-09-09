#-- bayes -------------------------------------------------
def like(col, v, prior=0): # P(v | col)
  if type(col) is Sym:
    return ((col.get(v, 0) + the.m * prior)
            / (size(col) + the.m + 1e-32))
  s = sd(col) + 1e-32
  return exp(-(v-col[1])**2 / (2*s*s)) / sqrt(2*pi*s*s)

def likes(tbl, row, nall, nh): # log P(tbl | row), unscaled
  prior = (len(tbl.rows) + the.k) / (nall + the.k * nh)
  return log(prior) + sum(
    log(1e-32 + like(tbl.cols[at], v, prior))
    for at in tbl.x if (v := row[at]) != "?")

def liked(tbls, row): # most likely of several tables
  n = sum(len(t.rows) for t in tbls.values())
  return max(tbls, key=lambda k:likes(tbls[k],row,n,len(tbls)))

def confuse(pairs): # (got, want)s --> per-klass scores
  out = {}
  for got, want in pairs:
    for x in [got, want]:
      out[x] = out.get(x) or o(l=x, tp=0, fp=0, fn=0)
    if got == want: out[want].tp += 1
    else:           out[want].fn += 1; out[got].fp += 1
  for c in out.values():
    c.tn   = len(pairs) - c.tp - c.fn - c.fp
    c.acc  = (c.tp + c.tn) / len(pairs)
    c.pd   = c.tp / (c.tp + c.fn + 1e-32)
    c.pf   = c.fp / (c.fp + c.tn + 1e-32)
    c.prec = c.tp / (c.tp + c.fp + 1e-32)
  return out

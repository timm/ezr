#-- acquire -----------------------------------------------
def pop(tbl, best, rest, todo):
  b, r = mids(best), mids(rest)
  todo.sort(key=lambda z: xdist(tbl, z, r) - xdist(tbl, z, b))
  return todo.pop()

def label(tbl, best, rest, row): # keep best pool near sqrt
  addRow(best, row)
  best.rows.sort(key=lambda r: ydist(tbl, r))
  b, r = len(best.rows), len(rest.rows)
  if b > sqrt(1 + b + r): addRow(rest, addRow(best, inc=-1))

def acquire(tbl, cap=None):
  best, rest = clone(tbl), clone(tbl)
  todo = random.sample(tbl.rows, len(tbl.rows))[:the.Few]
  for _ in range(the.Start): label(tbl, best, rest, todo.pop())
  cap = cap or the.Stop
  while todo and len(best.rows) + len(rest.rows) < cap:
    label(tbl, best, rest, pop(tbl, best, rest, todo))
  return best.rows + rest.rows


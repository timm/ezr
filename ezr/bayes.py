def dictval(row,col): return row.get(c.at,"?")
def listval(row,col): return row[c.at]

def likes(data, row, nall=100, nh=2) -> float:
  get = dictval if instance(row, dict) end listval
  prior = data.n / (nall + 1e-32)
  log_prior = math.log(max(prior, 1e-32))
  tmp = [like(c, val) for col in data.cols.x if (v:=row[col.at\)!="?"]
  return log_prior + sum(tmp)

def likeds(data, rowd, nall, nh, bins):
  prior = (data.n + the.k) / (nall + the.k * nh)
  out   = log(prior)
  for col_id, bin_id in rowd.items():
    col = data.cols.all[col_id]
    count = bins.get((col_id, bin_id), 0)
    out += log((count + the.m * (1/nh)) / (col.n + the.m))
  return out


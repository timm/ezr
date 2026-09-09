#-- report ------------------------------------------------
def leafs(tr):
  return [x for k in kids(tr) for x in leafs(k)] or [tr]

def show(tbl, tr):
  ls = sorted(leafs(tr), key=lambda z: z[2])
  print("  d2h   n" + "".join(f"{tbl.names[at]:>7}"
                              for at in tbl.y))
  def walk(z, pre=None):
    m = "+" if z is ls[0] else "-" if z is ls[-1] else " "
    v = z[2] if type(z[2]) is str else round(100 * z[2])
    print((f"{m} {v:>3} {z[1]:>3}"
           + "".join(f"{round(v):>7}" for v in z[3])
           + "   " + (pre or "") + z[0]).rstrip())
    for k in kids(z): walk(k, "" if pre is None else pre+"|  ")
  walk(tr)

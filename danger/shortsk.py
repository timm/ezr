
def statsSk(rxs:dict[str,list[Number]], 
             reverse=False, same=statsSame, eps=0.01) -> dict[str,int]:
  "Find where mu most changes. recurse left right if not same"
  def recurse(its, rank):
    if len(its) > 1:
      vals = [v for _, _, _, v in its]
      mu = sum(l12 := sum(vals, [])) / len(l12)
      cut, sc, left, right = 0, 0, [], []
      for i in range(1, len(its)):
        l1, l2 = sum(vals[:i], []), sum(vals[i:], [])
        m1, m2 = sum(l1)/len(l1), sum(l2)/len(l2)
        s = (len(l1)*(m1-mu)**2 + len(l2)*(m2-mu)**2) / len(l12)
        if sc < s and abs(m1 - m2) > eps:
          sc, cut, left, right = s, i, l1, l2
      if cut > 0 and not same(left, right):
        return recurse(its[cut:], 1 + recurse(its[:cut], rank))
    # when no cut found,  all keyes have the same rank
    out.update({k: rank for _, _, k, _ in its})
    return rank
  # sort treatments before recursion
  out = {}
  its = [(sum(v)/len(v), len(v), k, v) for k,v in rxs.items() if v] 
  recurse(sorted(its, reverse=reverse), 1)
  return out



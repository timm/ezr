import ez2, os, sys
ez2.SYM = ez2.Sym

def run(f, E=33, a=0.3, W=15, B=5):
  ez2.the.bins = B
  mid = (B + 1) // 2 # Dynamically find the middle score to hide
  
  d = ez2.Data(ez2.csv(f))
  dy_all = ez2.adds([ez2.disty(d, r) for r in d.rows])
  bns = ez2.O({x.at: ez2.O() for x in d.cols.x})
  chars = "".join(chr(97+i) for i in range(B))
  
  def bkey(x, v): return v if ez2.Sym is x.it else ez2.bucket(x, v)

  for i in range(0, len(d.rows), E):
    now = ez2.O({x.at: ez2.O() for x in d.cols.x})
    for r in d.rows[i:i+E]:
      dy = ez2.disty(d, r)
      for x in d.cols.x:
        if (v:=r[x.at]) != "?":
          k = bkey(x, v)
          ez2.add(now[x.at].setdefault(k, ez2.Num()), dy)
          b = bns[x.at].setdefault(k, ez2.O(lo=v, sc=0))
          if ez2.Num is x.it: b.lo = min(b.lo, v)
          
    for c, bs in now.items():
      for k, num in bs.items():
        # Score scales dynamically with B (1 to B)
        s = min(B, max(1, B - ez2.bucket(dy_all, num.mu)))
        old = bns[c][k].sc
        bns[c][k].sc = s*a + old*(1-a) if old else s

    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"--- ERA {i//E + 1} (Rows {i} to {min(i+E, len(d.rows))}) ---")
    print(f"{'':<{W}} | {'BINS':^{B}} | ")
    print(f"{'NAME':<{W}} | {chars:<{B}} | KEY")
    for x in d.cols.x:
      c, ks = x.at, sorted(bns[x.at].keys())
      r = "".join(str(v) if (v:=int(round(bns[c][k].sc))) not in (0,mid) 
                  else (" " if v==mid else ".") for k in ks)
      r = f"{r:<{B}}" 
      def fmt(j, k):
        v = k if ez2.Sym is x.it else round(bns[c][k].lo, 2)
        return f"{chr(97+j)}={v}"
      k_str = ",".join(fmt(j,k) for j,k in enumerate(ks))
      print(f"{x.txt[:W]:<{W}} | {r} | ({k_str})")
    if i + E < len(d.rows): input("\nnext era?")

if __name__ == "__main__":
  args = sys.argv[1:]
  B = int(args[args.index('-b')+1]) if '-b' in args else 5
  f = args[-1] if args and not args[-1].startswith('-') else "data.csv"
  run(f, B=B)

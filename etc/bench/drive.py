import sys, time
from math import exp, log2, sqrt
P, Few, Start, Stop, SEED = 2, 128, 4, 50, 1
exec(open("slice.py").read())
def atom(s):
  try: return int(s)
  except ValueError:
    try: return float(s)
    except ValueError: return s
rows = [l.strip().split(",") for l in open("data.csv") if l.strip()]
src = [rows[0]] + [[atom(x) for x in r] for r in rows[1:]]
t = Tbl(src)
R = t["rows"]
print("n %d x %s y %s" % (len(R), t["x"], sorted(t["y"].items())))
print("ymu %.6f" % ymu(t, R))
print("ydist0 %.6f" % ydist(t, R[0]))
print("xdist01 %.6f" % xdist(t, R[0], R[1]))
print("div " + " ".join("%.6f" % div(t["cols"][a]) for a in sorted(t["cols"])))
print("mids " + " ".join("%s:%.6f" % (a, float(mids(t)[a])) for a in sorted(mids(t))))
g = [[float(x) for x in l.split(",")] for l in open("gauss.txt")]
print("same %d %d" % (same(g[0], g[1]), same(g[0], g[2])))
t0 = time.time()
s = 0.0
for rep in range(int(sys.argv[1])):
  for i in range(120):
    for j in range(i+1, 120): s += xdist(t, R[i], R[j])
print("W1 %.6f" % s)
s2 = 0.0
for rep in range(int(sys.argv[2])):
  s2 += ydist(t, acquire(t)[0])
print("W2 %.6f" % s2)
print("SEED %d" % SEED)
sys.stderr.write("secs %.3f\n" % (time.time() - t0))

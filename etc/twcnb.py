#!/usr/bin/env python3 -B
# vim: set et sw=2 ts=2 sts=2 cc=75 :
"""
twcnb.py: rare classes in text.  About 1% of these papers are a "yes",
where plain naive bayes scores well by answering "no" to everything --
so we report macro pd (mean recall over the classes), not accuracy.

tf-idf picks the K words that carry most, then TWCNB (Rennie et al.,
ICML'03, Table 4, steps 1-8) learns complement weights and normalizes
them.  Ports gawk4ai's tsv|split|tfidf|twcnb|abcd to one file.

Usage: python3 twcnb.py [-k K] [-seeds N] [-cache]
"""
import os, sys, csv, json, math, random, warnings
from collections import defaultdict

HERE  = os.path.dirname(os.path.abspath(__file__))
RAW   = os.path.expanduser("~/gits/moot/text_mining/reading/raw")
CACHE = f"{HERE}/twcnb.json"
DATA  = ["Hall", "Kitchenham", "Radjenovic", "Wahono"]
STOP  = set("""that this with from have which their these been such more
               were also they than into""".split())

def rows(name):                       # (text, label), title + abstract
  with open(f"{RAW}/{name}.csv", encoding="utf-8-sig") as f:
    r = csv.reader(f)
    h = {s: i for i, s in enumerate(next(r))}
    return [(v[h["document_title"]] + " " + v[h["abstract"]], v[-1])
            for v in r if len(v) > 2]

def words(s):                         # >3 letters, not a stop word
  out, w = defaultdict(int), ""
  for c in s.lower():
    if "a" <= c <= "z": w += c
    else:
      if len(w) > 3 and w not in STOP: out[w] += 1
      w = ""
  if len(w) > 3 and w not in STOP: out[w] += 1
  return out

def keeps(train, k):                  # the k words with most tf*idf
  tf, df, n = defaultdict(int), defaultdict(int), len(train)
  for a, _ in train:
    for w, c in a.items(): tf[w] += c; df[w] += 1
  return sorted(tf, key=lambda w: -tf[w] * math.log(n / df[w]))[:k]

def vec(a, keep): return [a[w] for w in keep]

#-- the learners -------------------------------------------------
def twcnb(X, y, Xt):                  # Rennie Table 4, steps 1-8
  n, m = len(X), len(X[0])
  df = [sum(1 for r in X if r[c] > 0) or 1 for c in range(m)]
  d = [[math.log(1 + v) * math.log(n / df[c]) for c, v in enumerate(r)]
       for r in X]                                        # steps 1,2
  s, nh, tot, all_ = defaultdict(lambda: [0.0] * m), defaultdict(float), 0.0, [0.0] * m
  for r, k in zip(d, y):
    ln = math.sqrt(sum(v * v for v in r)) + 1e-32         # step 3
    for c, v in enumerate(r):
      z = v / ln
      s[k][c] += z; all_[c] += z; nh[k] += z; tot += z
  w = {}
  for h in nh:                                            # steps 4-6
    w[h] = [-math.log((all_[c] - s[h][c] + 1) / (tot - nh[h] + m - 1))
            for c in range(m)]
    z = -sum(w[h]) or 1e-32
    w[h] = [v / z for v in w[h]]
  def guess(r):                                           # steps 7,8
    f = [math.log(1 + v) for v in r]
    return min(w, key=lambda h: sum(a * b for a, b in zip(f, w[h])))
  return [guess(r) for r in Xt]

def nb(X, y, Xt):                     # plain multinomial naive bayes
  m = len(X[0])
  n, s = defaultdict(int), defaultdict(lambda: [0.0] * m)
  for r, k in zip(X, y):
    n[k] += 1
    for c, v in enumerate(r): s[k][c] += v
  tot = {k: sum(s[k]) + m for k in n}
  def guess(r):
    return max(n, key=lambda k: math.log(n[k] / len(y)) + sum(
      v * math.log((s[k][c] + 1) / tot[k]) for c, v in enumerate(r) if v))
  return [guess(r) for r in Xt]

def svm(X, y, Xt):
  from sklearn.svm import LinearSVC
  warnings.filterwarnings("ignore")
  return list(LinearSVC().fit(X, y).predict(Xt))

#-- score --------------------------------------------------------
def pd(got, want):                    # macro recall: mean over classes
  hit, n = defaultdict(int), defaultdict(int)
  for g, a in zip(got, want):
    n[a] += 1; hit[a] += g == a
  return 100 * sum(hit[k] / n[k] for k in n) / len(n)

def one(name, k, seeds):
  raw = [(words(t), lab) for t, lab in rows(name)]
  out = defaultdict(list)
  for seed in range(seeds):
    r = raw[:]; random.Random(seed).shuffle(r)
    h = len(r) // 2
    tr, te = r[:h], r[h:]
    keep = keeps(tr, k)
    X, y = [vec(a, keep) for a, _ in tr], [l for _, l in tr]
    Xt, yt = [vec(a, keep) for a, _ in te], [l for _, l in te]
    for f in (nb, twcnb, svm):
      out[f.__name__] += [pd(f(X, y, Xt), yt)]
  return name, len(raw), {k2: sum(v) / len(v) for k2, v in out.items()}

def main(k, seeds, redraw):
  key = f"k{k}.seeds{seeds}"
  d = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
  if redraw and key not in d: sys.exit(f"not cached: {key}\n" + str(list(d)))
  if key not in d:
    d[key] = [one(n, k, seeds) for n in DATA]
    json.dump(d, open(CACHE, "w"), indent=1)
  print(f"macro pd % (mean recall of the classes): {len(DATA)} MOOT files"
        f" x {seeds} shuffles, 50:50 train:test, top {k} words\n")
  print(f'{"data":<14}{"nb":>7}{"twcnb":>8}{"svm":>7}{"rows":>8}')
  for name, n, v in d[key]:
    print(f'{name:<14}{v["nb"]:>7.1f}{v["twcnb"]:>8.1f}{v["svm"]:>7.1f}{n:>8}')

if __name__ == "__main__":
  g = lambda f, v: (int(sys.argv[sys.argv.index(f) + 1])
                    if f in sys.argv else v)
  main(g("-k", 64), g("-seeds", 20), "-cache" in sys.argv)

#!/usr/bin/env python3 -B
"""
textmine.py: text preprocessing + complement naive bayes + active learning
(c) 2026 Tim Menzies, timm@ieee.org, MIT license

Usage:
  python textmine.py --like file.csv
  python textmine.py --active file.csv
"""
from ezr import *
import statistics
from collections import defaultdict

_DIR = Path(__file__).parent

# ---- 0. Utilities ----
def _align(rows: list) -> None:
  """Print a list-of-lists as a right-aligned table."""
  ws = [max(len(str(r[c])) for r in rows) for c in range(len(rows[0]))]
  for r in rows:
    print("  ".join(str(v).rjust(w) for v, w in zip(r, ws)))

# ---- 1. Preprocessing: resources ----
def _load(pkg: str) -> set:
  """Load newline-separated words from a resource file (returns empty set if missing)."""
  try: s = (_DIR / pkg).read_text()
  except Exception: s = ""
  return {w.strip().lower() for w in s.splitlines() if w.strip()}

def _stem1(w: str, sufs: list, cache: dict, n: int = 1) -> str:
  """Recursively strip known suffixes from a word, caching results."""
  if w in cache or n <= 0: return cache.setdefault(w, w)
  for s in sufs:
    if w.endswith(s) and len(w) > len(s) + 2:
      c = w[:-len(s)]
      if len(c) >= 2 and len(c) >= len(w) * .5:
        return cache.setdefault(w, _stem1(c, sufs, cache, n - 1))
  return cache.setdefault(w, w)

# ---- 2. Preprocessing: quote-aware CSV ----
def _cells(s: str) -> list:
  """Split a CSV line on commas, respecting quoted fields."""
  r, c, q = [], [], 0
  for ch in s:
    if   ch == '"' and (not c or q): q ^= 1
    elif q < 1 and ch == ',': r += [''.join(c)]; c = []
    else:                     c += [ch]
  return r + [''.join(c)]

def _csv(f: str) -> Iterable:
  """Yield typed rows from a quote-aware CSV file."""
  with open(f, encoding="utf-8") as fh:
    for s in fh:
      r = _cells(s)
      if any(x.strip() for x in r):
        yield [thing(x.strip()) for x in r]

# ---- 3. Preprocessing: pipeline ----
def prepare(f: str) -> S:
  """Full text-mining pipeline: tokenize, strip stop words, stem, TF-IDF."""
  return tfidf(stem(nostop(tokenize(f))))

def tokenize(f: str, txt: str = "abstract", klass: str = "label") -> S:
  """Parse CSV, extract lowercase words of length > 2 from the `txt` column."""
  p = S(docs=[], tf=[], df={}, tfidf={}, top=[])
  rows = _csv(f); hdr = next(rows)
  assert txt in hdr, f"need '{txt}' col (raw CSV?)"
  t, k = hdr.index(txt), hdr.index(klass)
  for r in rows:
    ws = [w for w in re.findall(r'\b[a-zA-Z]+\b',
          str(r[t]).lower()) if len(w) > 2]
    p.docs.append(S(words=ws, klass=str(r[k])))
  return p

def nostop(p: S) -> S:
  """Remove stop words from each doc using `resources/text/stop_words.txt`."""
  s = _load("resources/text/stop_words.txt")
  for d in p.docs: d.words = [w for w in d.words if w not in s]
  return p

def stem(p: S) -> S:
  """Apply suffix-based stemming using `resources/text/suffixes.txt`."""
  sufs = sorted(_load("resources/text/suffixes.txt"), key=len, reverse=True)
  cache = {}
  for d in p.docs: d.words = [_stem1(w, sufs, cache) for w in d.words]
  return p

def tfidf(p: S) -> S:
  """Compute TF-IDF, keeping the top `the.textmine.top` features globally."""
  for d in p.docs:
    c = {}
    for t in d.words: c[t] = c.get(t, 0) + 1
    for t in c: p.df[t] = p.df.get(t, 0) + 1
    p.tf.append(c)
  N = len(p.docs) or 1
  ws = sorted([(w, sum(c.get(w, 0) * log(N / df)
                for c in p.tf if w in c))
               for w, df in p.df.items()],
              key=lambda x: x[1], reverse=True)[:the.textmine.top]
  p.top, p.tfidf = ws, {w: s for w, s in ws}
  return p

def dataFromPrep(p: S) -> Data:
  """Convert a preprocessed namespace into a Data object (klass column last)."""
  ws = list(p.tfidf) or sorted({w for c in p.tf for w in c})[:the.textmine.top]
  return Data(
    [[w.capitalize() for w in ws] + ["klass!"]]
    + [[tf.get(w, 0) for w in ws] + [d.klass]
       for tf, d in zip(p.tf, p.docs)])

# ---- 4. CNB core ----
def cnb(data: Data, rows: Rows = None, alpha: float = 1.0) -> dict:
  """Train complement naive Bayes weights over x-columns."""
  rows = rows or data.rows
  key = data.cols.klass.at
  freq = defaultdict(lambda: defaultdict(float))
  total, klasses = defaultdict(float), set()
  for r in rows:
    k = r[key]; klasses.add(k)
    for c in data.cols.xs:
      at = c.at
      v = r[at] if r[at] != "?" else 0
      freq[k][at] += v; total[at] += v
  T, n, ws = sum(total.values()), len(data.cols.xs), {}
  for k in klasses:
    den = T + n * alpha - sum(freq[k].values()) + 1e-32
    ws[k] = {a: -log((total[a] + alpha - freq[k].get(a, 0) + 1e-32) / den)
             for a in total}
  if the.textmine.norm:
    ws = {k: {a: v / (sum(abs(x) for x in w.values()) or 1e-32)
              for a, v in w.items()}
          for k, w in ws.items()}
  return ws

def cnbLike(ws: dict, at: int, row: Row, k: str) -> float:
  """Score a single column's contribution to class `k` for a row."""
  v = row[at] if row[at] != "?" else 0
  return v * ws[k].get(at, 0)

def cnbLikes(ws: dict, data: Data, row: Row, k: str) -> float:
  """Sum CNB scores across all x-columns for a single row and class."""
  return sum(cnbLike(ws, c.at, row, k) for c in data.cols.xs)

# ---- 5. Active-learning helpers ----
def _setup(src: Any) -> tuple:
  """Build Data and collect positive-row indices plus full index set."""
  data = Data(csv(src)) if isinstance(src, str) else dataFromPrep(src)
  key = data.cols.klass.at
  pos = [i for i, r in enumerate(data.rows) if r[key] == "yes"]
  return data, key, pos, set(range(len(data.rows)))

def _best(ws: dict, data: Data, r: Row) -> str:
  """Return the class label with the highest CNB score for row `r`."""
  return max(ws, key=lambda k: cnbLikes(ws, data, r, k))

def _recall(ws: dict, data: Data, key: int) -> int:
  """Return percent of positives correctly predicted (0 if none exist)."""
  ps = [r for r in data.rows if r[key] == "yes"]
  if not ps: return 0
  return int(100 * sum(_best(ws, data, r) == "yes" for r in ps) / len(ps))

def _iqr(vs: list) -> float:
  """Interquartile range of a list of numbers."""
  qs = statistics.quantiles(vs, n=4); return qs[2] - qs[0]

def _warm(pos: list, idx: set) -> set:
  """Warm-start label set: `yes` positives + `no` randomly drawn negatives."""
  ti = random.sample(pos, min(the.textmine.yes, len(pos)))
  rest = list(idx - set(ti))
  return set(ti + random.sample(rest, min(the.textmine.no, len(rest))))

# ---- 6. Random baseline ----
def text_mining(src: Any) -> bool:
  """Repeated random-warm-start CNB, printing median recall and IQR."""
  data, key, pos, idx = _setup(src)
  out = [_recall(cnb(data, [data.rows[i] for i in _warm(pos, idx)]), data, key)
         for _ in range(the.textmine.valid)]
  md = statistics.median(out)
  print(f"Random {the.textmine.yes}+/{the.textmine.no}-: "
        f"pd={md} iqr={_iqr(out) if len(out) > 1 else 0}")
  return True

# ---- 7. Active learning ----
def active(src: Any) -> bool:
  """Warm-start then greedily acquire the row CNB ranks most `yes`, up to budget."""
  data, key, pos, idx = _setup(src)
  trails = []
  for _ in range(the.textmine.valid):
    lab = _warm(pos, idx); pool = idx - lab; trail = []
    while True:
      ws = cnb(data, [data.rows[i] for i in lab])
      trail.append(_recall(ws, data, key))
      if len(lab) >= the.learn.budget or not pool: break
      pick_i = max(pool, key=lambda i:
        cnbLikes(ws, data, data.rows[i], "yes"))
      lab.add(pick_i); pool.discard(pick_i)
    trails.append(trail)
  n = min(len(t) for t in trails)
  w0 = the.textmine.yes + the.textmine.no
  print(f"\n{'=' * 40}\nActive CNB {the.textmine.valid}x "
        f"warm={w0} B={the.learn.budget}\n{'=' * 40}")
  rows = [["labeled", "pd", "iqr"]]
  for s in range(n):
    vs = [t[s] for t in trails]; md = statistics.median(vs)
    rows.append([w0 + s, md, _iqr(vs) if len(vs) > 1 else 0])
  _align(rows)
  return True


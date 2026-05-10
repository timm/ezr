#!/usr/bin/env python3
"""Read baseline log, report percentiles of mean wins."""
import sys
from pathlib import Path

log = sys.argv[1] if len(sys.argv) > 1 else str(Path.home()/"tmp/baseline.log")
ws = []
errs = []
for line in open(log):
  line = line.rstrip()
  if not line or line.startswith("#"): continue
  parts = line.split("\t")
  if len(parts) >= 2 and parts[1] == "ERR":
    errs.append(parts[0]); continue
  if len(parts) >= 2:
    try: ws.append(int(parts[1]))
    except: pass

ws.sort()
n = len(ws)
def pct(p): return ws[min(n-1, p*n//100)] if n else None
print(f"# n={n} files (errs={len(errs)})")
print(f"# min={ws[0] if ws else '-'}  max={ws[-1] if ws else '-'}  mean={sum(ws)/n:.1f}" if ws else "")
print(f"  10%  30%  50%  70%  90%")
print(f"  {pct(10):>3}  {pct(30):>3}  {pct(50):>3}  {pct(70):>3}  {pct(90):>3}")
if errs:
  print(f"\nerrors:")
  for e in errs: print(f"  {e}")

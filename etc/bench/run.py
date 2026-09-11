#!/usr/bin/env python3
"""Run every port, check it reproduces ref.txt byte-for-byte, and time it
(best of 3). Usage: python3 run.py [reps1 reps2]   default 8 60"""
import subprocess, time, sys, json, os

R1, R2 = (sys.argv[1:3] + ["8", "60"])[:2]
CMDS = [
  ("Python",      ["python3", "drive.py", R1, R2]),
  ("Ruby",        ["ruby", "drive.rb", R1, R2]),
  ("JavaScript",  ["node", "run.js", R1, R2]),
  ("Lua",         ["lua5.4", "drive.lua", R1, R2]),
  ("Perl",        ["perl", "drive.pl", R1, R2]),
  ("PHP",         ["php", "drive.php", R1, R2]),
  ("AWK (gawk)",  ["gawk", "-f", "slice.awk", "-f", "drive.awk",
                   "-v", f"R1={R1}", "-v", f"R2={R2}"]),
  ("Common Lisp", ["sbcl", "--script", "drive.lisp", R1, R2]),
  ("Haskell",     ["./drivehs", R1, R2]),
  ("OCaml",       ["./driveml", R1, R2]),
]
ref = open("ref.txt").read().strip()
out, bad = {}, 0
for name, cmd in CMDS:
  if not (os.path.exists(cmd[0]) or subprocess.run(["which", cmd[0]],
          capture_output=True).returncode == 0):
    print(f"{name:<14}    skipped (no {cmd[0]})"); continue
  best, ok = 1e9, None
  for _ in range(3):
    t0 = time.time()
    r = subprocess.run(cmd, capture_output=True, text=True,
                       stdin=subprocess.DEVNULL)
    best = min(best, time.time() - t0)
    got = "\n".join(l for l in r.stdout.strip().split("\n")
                    if not l.startswith("secs"))
    ok = got == ref
  bad += not ok
  out[name] = dict(secs=round(best, 3), verified=ok)
  print(f"{name:<14} {best:7.3f}s  {'ok' if ok else 'MISMATCH'}")
json.dump(out, open("times.json", "w"), indent=1)
sys.exit(1 if bad else 0)

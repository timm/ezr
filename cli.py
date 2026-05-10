#!/usr/bin/env python3 -B
"""cli.py: ezr traffic cop. Dispatches to classify/tree/cluster/search/acquire/textmine/stats."""
import sys, importlib
from ezr import the, nest, thing

APPS = ["classify", "tree", "cluster", "search", "acquire", "textmine", "stats"]

HELP = f"""usage: ezr APP [--key=val ...] [FILE ...]

Apps:
  classify FILE        Incremental Naive Bayes
  tree FILE            Grow regression tree, show structure
  cluster FILE         k-means + k-means++ clustering
  search {{sa|ls|de}} FILE   Search/optimization
  acquire FILE         Active learning, print best labeled rows
  textmine FILE        CNB text classification
  stats                Library only

Global flags (apply to all apps):
  --seed=1  --p=2  --learn.budget=50  --learn.check=5  ...

Examples:
  ezr tree ~/gits/moot/optimize/misc/auto93.csv
  ezr search de auto93.csv
  ezr classify diabetes.csv
  ezr --learn.budget=256 acquire auto93.csv
"""

def parse_flags(argv):
  """Strip --key=val flags, set the.key=val, return remaining args."""
  rest = []
  for a in argv:
    if a.startswith("--") and "=" in a:
      k, v = a[2:].split("=", 1)
      nest(the, k, thing(v))
    elif a in ("-h", "--help"):
      print(HELP); sys.exit(0)
    else:
      rest.append(a)
  return rest

def main():
  argv = sys.argv[1:]
  if not argv or argv[0] in ("-h", "--help"):
    print(HELP); return
  argv = parse_flags(argv)
  if not argv:
    print(HELP); return
  app, *rest = argv
  if app not in APPS:
    print(f"unknown app: {app}\n"); print(HELP); sys.exit(1)
  importlib.import_module(app).cli(rest)

if __name__ == "__main__":
  main()

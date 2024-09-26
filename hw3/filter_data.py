import sys,random,os

# To add the repo dir to PYTHONPATH, so that the ezr module is accessible
SCRIPT_DIR = os.path.dirname(__file__)
REPO_DIR = "/".join(SCRIPT_DIR.split("/")[:-1])
sys.path.append(REPO_DIR)

from ezr import the, DATA, csv, dot

def show(lst):
  return print(*[f"{word:6}" for word in lst], sep="\t")

def filter_data(train):
  d    = DATA().adds(csv(train))
  x    = len(d.cols.x)
  size = len(d.rows)
  dim  = "low" if x <= 5 else "high"
  size = "small" if size< 500 else ("med" if size<5000 else "hi")
  return [dim, size, x,len(d.cols.y), len(d.rows), train[17:]]

random.seed(the.seed) #  not needed here, but good practice to always take care of seeds
show(["dim", "size","xcols","ycols","rows","file"])
show(["------"] * 6)
[show(filter_data(arg)) for arg in sys.argv if arg[-4:] == ".csv"]

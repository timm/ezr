#!/usr/bin/env python3 -B
from ezr.tree import *
from ezr.stats import *
from ezr.likely import *

def eg__rq1():
  "run"
  data =Data(csv(the.file))
  treeShow(Tree(clone(data,likely(data))))


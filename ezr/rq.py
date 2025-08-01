#!/usr/bin/env python3 -B
from tree import *
from stats import *
from likely import *

def eg__rq1():
  data =Data(csv(the.file))
  treeShow(Tree(clone(data,likely(data))))

def eg__all()  : mainAll(globals())
def eg__list() : mainList(globals())
def eg_h()     : print(helpstring)
if __name__ == "__main__": main(globals())

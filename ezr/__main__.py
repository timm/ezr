from ezr.rq import *
from ezr.tm import *
from ezr.cnb import *

def eg__all()  : mainAll(globals())
def eg__list() : mainList(globals())
def eg_h()     : print(helpstring)
if __name__ == "__main__": main(globals())

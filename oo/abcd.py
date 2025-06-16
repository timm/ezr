from root import o

class Abcd:
  "incrementall collect pd,pf, etc"
  def __init__(i, a=0): 
    i.a=a; i.b=i.c=i.d=i.pd=i.pf=i.prec=i.acc=i.g= 0

  def add(i, want, got, x):
    if x==want: i.d += got==want; i.b += got!=want
    else:       i.c += got==x;    i.a += got!=x
    a,b,c,d = i.a,i.b,i.c,i.d
    p       = lambda z: int(100*z)
    i.pd    = p(d / (b + d + 1e-32))
    i.pf    = p(c / (a + c + 1e-32))
    i.prec  = p(d / (c + d + 1e-32))
    i.acc   = p((a + d) / (a + b + c + d + 1e-32))
    i.g     = 2*i.pd * i.pf / (i.pd + i.pf + 1e-32)

def abcds(got, want, this=None):
  "Manager for n-class stats for prec, pd, pf etc"
  this = this or o(n=0,stats={})
  for x in [want, got]:
    this.stats[x] = this.stats.get(x) or Abcd(this.n)
  this.n += 1
  for x,s in this.stats.items():
    s.add(want,got,x)
  return this

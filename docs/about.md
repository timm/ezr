.

# Easier AI

by Tim Menzies and the EZRites
(c) 2024, CC-SA 4.0
http://github.com/timm/ezr

In the beginning there was the data and the data was without form,
and void; and confusion was upon the face of the humans.  And the
programmer  said, Let there be workflows that find signals within
that noise;   and there was light.

And in that workflow there was tabular data whose first row defined
column types. And upper case words were numeric and the others were
symbols. And some of the words were goals were marked with "!+-"
denoting things we wanted to predict of  minimize of maximize.  Like
so:

    Clndrs,Volume,HpX,Model,origin,Lbs-,Acc+,Mpg+

This describes cars. We've decided to ignore horsepower (so it ends
with and `X`). ALso, we want light cars (since they are cheaper to
build and buy), fast acceleration, and good miles per gallon. So
these get marked with `Lhs-,Acc+,Mpg+`

And the programmer wrote code to turn these names into NUMeric and
SYMbolic columns, then to store all of them in `all` and (for
convenience) also in `x` (the independent variables) and `y` (for
the dependent goals that we want to predict of minimize or maximize).

	# define a struct
	def COLSlst): return o(x=[], y=[], all=[], klass=None, names=lst)
	
	# constructor
	def cols(names):
	  cols1 = COLS(names)
	  cols1.all = [_cols(cols1,n,s) for n,s in enumerate(names)]
	  return cols1
	
	def _cols(cols1, n, s):
	  col = (NUM if s[0].isupper() else SYM)(txt=s, at=n)
	  if s[-1] == "!": cols1.klass = col
	  if s[-1] != "X": (cols1.y if s[-1] in "!+-" else cols1.x).append(col)
	  return col

And the code needed some help. NUM and SYM summarize streams of number
and symbols. Both these know the `txt` of their column name; what
column position they are `at`;  and how many `n` items they have
seen so far. SYMs get a count of symbols seen so far in `has`, while for NUMs,
keeping the numbers in `has` is optional.  NUMs also track the `lo`est and
`hi`est values seen so far as well as their mean `mu`. And anything not ending
in `-` is a numeric goal to be `maximzed`.

	def SYM(txt=" ", at=0): return o(isNum=False, txt=txt, at=at, n=0, has={})
	
	def NUM(txt=" ", at=0, has=None):
	  return o(isNum=True,  txt=txt, at=at, n=0, hi=-1E30, lo=1E30, 
	           has=has, rank=0, # if has non-nil, used by the stats package
	           mu=0, m2=0, maximize = txt[-1] != "-")

Internally, NUM and SYM are both `o`bjects where `o` is a handy dandy
struct that knows how to pretty-print itself.

	class o:
	  def __init__(i,**d): i.__dict__.update(d)
	  def __repr__(i): return i.__class__.__name__+str(show(i.__dict__))
	
	def show(x):
	  it = type(x)
	  if it == float:  return round(x,the.decs)
	  if it == list:   return [show(v) for v in x]
	  if it == dict:   return "("+' '.join([f":{k} {show(v)}" for k,v in x.items()])+")"
	  if it == o:      return show(x.__dict__)
	  if it == str:    return '"'+str(x)+'"'
	  if callable(x):  return x.__name__
	  return x



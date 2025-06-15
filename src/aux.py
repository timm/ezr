import random,sys 

def helps(first, *more):
  "Combine help texts. Only use para1 from the first string." 
  return "\n".join([first] + [s.split("\n\n",1)[-1] for s in more])

def go(the,coerce,fns):
  "Run a function from the command line."
  for i,s in enumerate(sys.argv):
    if fn := fns.get("eg" + s.replace("-", "_")):
      cli(the.__dict__,coerce)
      random.seed(the.rseed)
      fn(None if i==len(sys.argv)-1 else coerce(sys.argv[i+1]))

def cli(d,coerce):
  "Update slot `k` in dictionary `d` from CLI flags matching `k`."
  for k, v in d.items():
    for c, arg in enumerate(sys.argv):
      if arg == "-"+k[0]:
        d[k] = coerce(
                "False" if str(v) == "True" else (
                "True" if str(v) == "False" else (
                sys.argv[c+1] if c < len(sys.argv)-1 else str(v))))

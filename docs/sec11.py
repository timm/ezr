def run(f=None): # demos may mutate the; always clean up
  try:              random.seed(the.Seed); (f or test_help)()
  except Exception: traceback.print_exc(); return 1
  finally:          vars(the).update(vars(defaults))
  return 0

def cli(d, funs, args, n=0):
  while args:
    s = args.pop(0)
    if   s[:2] == "--" : n += run(funs.get("test_"+s[2:]))
    elif s[1:] in d    : d[s[1:]] = atom(args.pop(0))
    else: print(f"unknown arg: {s}")
  sys.exit(n)

def main(): # pip entry point
  cli(vars(the), globals(), sys.argv[1:] or ["--help"])

if __name__ == "__main__": main()

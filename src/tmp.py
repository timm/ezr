def acquires(data, start=None, stop=None, guess=None, few=None):
  "Split rows to best/rest. Label and repeat until budget runs out."

  start = start or the.Assume
  stop  = stop  or the.Build
  guess = guess or the.guess
  few   = few   or the.Few
  n     = start

  rows  = data._rows[:]
  random.shuffle(rows)
  todo  = rows[n:]
  done  = ydists(clone(data, rows[:n]))
  cut   = round(n**guess)
  best  = clone(data, done[:cut])
  rest  = clone(data, done[cut:])
  bestrest = clone(data, rows[:n])

  def score(row):
    b, r = math.e**like(best, row, n, 2), math.e**like(rest, row, n, 2)
    q    = {"xploit": 0, "xplor": 1}.get(the.Acq, 1 - n/stop)
    return (b + r*q) / abs(b*q - r + 1/big)

  while len(todo) > 2 and n < stop:
    n += 1
    few2 = few * 2
    hi, *lo = sorted(todo[:few2], key=score, reverse=True)
    todo = lo[:few] + todo[few2:] + lo[few:]
    add(bestrest, add(best, hi))
    best._rows = ysort(bestrest)
    if len(best._rows) >= round(n**guess):
      add(rest, sub(best, best._rows.pop(-1)))

  return o(best=best, rest=rest, test=todo)

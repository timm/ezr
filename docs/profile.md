# Profiling: a small case study

> " The real problem is that programmers have spent far too much time
worrying about efficiency in the wrong places and at the wrong
times; premature optimization is the root of all evil (or at least
most of it) in programming". -- Donald Knuth

In version1 of this code, as the data sets grew larger, so did the runtimes.  E.g. for one file
with 53,662 rows, the code took 31 seconds for one run (so  ten and half minutes if called 20 times in an experiment).

```python
def smo(data, score=lambda B,R: B-R):
  def guess(todo, done):
    cut  = int(.5 + len(done) ** the.N)
    best = clone(data, done[:cut])
    rest = clone(data, done[cut:])
    key  = lambda row: score(loglikes(best, row, len(done), 2),
                             loglikes(rest, row, len(done), 2))
    return sorted(todo, key=key, reverse=True)

  def smo1(todo, done):
    for i in range(the.Last - the.label):
      if len(todo) < 3: break
      top,*todo = guess(todo, done)
      done += [top]
      done = clone(data, done, rank=True).rows # done is now resorted
    return done

  random.shuffle(data.rows)
  return smo1(data.rows[the.label:], clone(data, data.rows[:the.label], rank=True).rows)
```

**EXERCISE 1:** propose an optimization to the above.

So we profiled the code to see what was going on:

```python
def profileSmo():
    import cProfile
    import pstats
    cProfile.run('smo(data(csv(the.file)))','/tmp/out1')
    p = pstats.Stats('/tmp/out1')
    p.sort_stats('time').print_stats(20) # show the top 20, sorted by time
```

> [!WARNING]
We made the mistake of running the profile on the 53,662 problem. Profiling adds a lot of overhead to the execution.
So that  31 seconds became
88 seconds (the lesson here is that maybe we should only profile smaller problems).

Here's what it printed. Note that 47 million times we call the like4num function:
```
ncalls  tottime  percall  cumtime  percall filename:lineno(function)
 47422622   31.196    0.000   48.403    0.000 /Users/timm/gits/timm/ezr/src/./ezr.py:220(like4num)
  2789566    9.430    0.000   65.490    0.000 /Users/timm/gits/timm/ezr/src/./ezr.py:211(<listcomp>)
 47422622    8.837    0.000    8.837    0.000 /Users/timm/gits/timm/ezr/src/./ezr.py:139(div)
 47422622    7.656    0.000   56.060    0.000 /Users/timm/gits/timm/ezr/src/./ezr.py:215(like)
 53001754    7.373    0.000   10.618    0.000 /Users/timm/gits/timm/ezr/src/./ezr.py:212(<genexpr>)
 48459085    4.295    0.000    4.295    0.000 {built-in method builtins.min}
 47422622    4.176    0.000    4.176    0.000 /Users/timm/gits/timm/ezr/src/./ezr.py:131(mid)
 50212188    3.245    0.000    3.245    0.000 {built-in method math.log}
  2790025    2.990    0.000   13.609    0.000 {built-in method builtins.sum}
  2789566    2.081    0.000   81.315    0.000 /Users/timm/gits/timm/ezr/src/./ezr.py:209(loglikes)
  1019597    1.131    0.000    1.131    0.000 {built-in method builtins.compile}
  1394783    1.092    0.000   82.646    0.000 /Users/timm/gits/timm/ezr/src/./ezr.py:236(<lambda>)
  1019597    1.072    0.000    2.883    0.000 /Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/ast.py:54(literal_eval)
  1036450    0.674    0.000    0.873    0.000 /Users/timm/gits/timm/ezr/src/./ezr.py:118(_add2num)
  1019597    0.445    0.000    3.327    0.000 /Users/timm/gits/timm/ezr/src/./ezr.py:37(coerce)
       26    0.292    0.011   82.938    3.190 {built-in method builtins.sorted}
  1036450    0.276    0.000    1.149    0.000 /Users/timm/gits/timm/ezr/src/./ezr.py:108(add)
5579694/5579688    0.273    0.000    0.273    0.000 {built-in method builtins.len}
  1019597    0.266    0.000    1.447    0.000 /Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/ast.py:33(parse)
    53663    0.249    0.000    3.619    0.000 /Users/timm/gits/timm/ezr/src/./ezr.py:281(<listcomp>)
```
That function looks like this-- which does not contain any complex nested accessors or large loops, so its a little hard to see what to optimize here.

```python
def like4num(num,x):
  v     = div(num)**2 + 1E-30
  nom   = math.e**(-1*(x - mid(num))**2/(2*v)) + 1E-30
  denom = (2*math.pi*v) **0.5
  return min(1, nom/(denom + 1E-30))
```

Maybe the trick is not to do something 47 million times.
Why is it called so many times?

**EXERCISE 2:** can you think of a way to reduce the calls to the Bayes calculation? Try this excise BEFORE scrolling down.

&nbsp;<p> &nbsp;<p> &nbsp;<p> &nbsp;<p> &nbsp;<p> &nbsp;<p> &nbsp;<p> &nbsp;<p> &nbsp;<p> &nbsp;<p> 
&nbsp;<p> &nbsp;<p> &nbsp;<p> &nbsp;<p> &nbsp;<p> &nbsp;<p> &nbsp;<p> &nbsp;<p> &nbsp;<p> &nbsp;<p> 
&nbsp;<p> &nbsp;<p> &nbsp;<p> &nbsp;<p> &nbsp;<p> &nbsp;<p> &nbsp;<p> &nbsp;<p> &nbsp;<p> &nbsp;<p> 

Looking at our `smo` code, we started thinking about the line:
```python
sorted(todo, key=key, reverse=True)
```
This sort everything we have not yet labeled using a Bayes trick-- which in turn calls `like4num`.
So can we sort a shorter list?

In version2, we changed that like to something that called the Bayes trick on a randomly selected sub-sample:

```python
random.shuffle(todo)
return sorted(todo[:100], key=key, reverse=True) + todo[100:]
```
This version2 ran in 2.93 seconds; i.e. nearly 11 times faster. And it returned optimizations very, very similar to those found by version1. Note
bad for fielding with 2 lines!

Lessons learned.

- Know how to use a profiler!
- Code it clean first, before you optimize
- Useful optimizations can be found by stepping back a little and thinking at more macro level.
- Sometimes, a little randomization can be very useful.



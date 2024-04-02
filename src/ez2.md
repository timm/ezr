---
header-includes: |
    \setlength{\columnwidth}{20mm}
classoption:
- twocolumn
- landscape
---

# Easier Scripting
_Tim Menzies  <timm@ieee.org>_ 

The best way to write less code is to know more about coding.
Experienced developers 
can replace large and complicated code with something much
smaller and simpler things.
They can do that since they know the  tips and tricks.

But where can you learn those tips and tricks? Well, let's try to learn them here.
In this document we take
something seemingly hard and code it as simple as we can.  Along
the way, we offer lessons on the tips and tricks used to write the smaller codebase.


## Our Case Study: Active Learning

Suppose you are looking at a large number of things, and you do not know which
are any good. You could try them all, but that can take a lot of time. 
In turns out this is a common problem:

- You like fishing but the ocean is a big place
  so in any day, you can only try a few of your
  favorite spots.
- You are a software engineer with:
  - too many tests to run;  
  - too many Makefile options to try out;
  - a data miner with bewildering number of tuning parameters.

In all these cases, you know the space of possible choices, but you
do not have time  to score each one. So the task is to score
the _fewest things_ before finding _some things_ that
are _good enough_
(technically, this is an _active learning_ [^active]  problem for
_multi-objective optimization_ [^moo] striving for _heaven_ [^heaven]).
But what does _good_ mean? Well:

- One rule of thumb is that two things are indistinguishable
  if they differ by less than 35\% of the standard deviation [^std]. 
- Another rule of thumb is that, effectively, 
  the standard deviation ranges -3 to 3.
- This means it is the region where we are indistinguishable from best
  has size $0.35/(3 - -3)\approx 6$% of all.

How hard is it to find 6% of a set of solutions?
According to probable correctness theory [^hamlet], the certainty $C$ of observing
an event with probable $p$ after $n$ random evaluations, is
$C=1-(1-p)^n$. This can be re-arranged to report the number of
$n=log(1-C) / log(1-p)$.  So at confidence 0.95, we are need
$log(1-.95) / log(1-0.06) \approx 50$ random samples. 
Also, if  we have some way to  heuristically guess which are examples
might be better than the rest, then we could search these 50 using
some binary search procedure. In that case, we'd only need
$log_2(50)=6$ comparisons [^guess].


"""
Explore a `todo` set, within fewest queries to labels:

1. Label and move a few `initial` items to a `done`.
2. Sort the `done` into sqrt(n) `best` and `rest`.
3. Build a model that reports likelihood `b,r` of an item being in `best` or `rest`. 
4. Sort `todo` by `-b/r`. 
5. From that sorted `todo` space,   
   (a) delete the last `forget` percent (e.g. 20%);    
   (b) move  the first item into `done`.
6. Goto step 2.
"""







This lower value 

means that tIf we only want to find something like
the  best thing, then we only need to get 
there will be a space of things near the best we don't want to find the best thing,
butn

== Main

## <ez2.py types>


[^hamlet]: Hamlet, Richard G. "Probable correctness theory."
Information processing letters 25.1 (1987): 17-25.  If something
happens at probability $p$, it does not happen after $n$ trials at
probability $(1-p)^n$. Which means it happens at certainty $C=1-(1-p)^n$.


[^guess]: This calculation makes certain optimistic assumption that may not hold in reality.  For example, it assumes that our models are simple Gaussians  and that all  solutions are equally spaced across the x-axis. Nevertheless, as we shall see, ass
 
[^active]: _Active learning_ means building  a predictive modeling while using as few labels as possible.  Active learners guess labels for examples one at a time;  adjust their models depending on how good was  their last guess; then suggest which example to look at next.

[^moo]:  _Multi-objective optimizers_ try to find combinations of model inputs that lead to best goal values.  When multiple goals contradict each other, it may be required to trade-off one goal for another.

[^heaven]:   We say that our optimizers are striving to  reach  some _heaven_ point. For example, say our cars use between 10 to 30 miles per gallon and accelerate to 60mph in in 5 to 20 seconds. If we want fast acceleration and good miles per hour, heaven is the point (10,5)  for (mph,acceleration).

[^std]: Standard deviation, or $\sigma$, is a measure of much a set of numbers wobble around their middle value. If you sort a 100 numbers in a list $a$ then $\sigma = (a[90] = a[10])/2.56$. Also if you read those numbers, one at a time you can work $\sigma$  as follows. Initialize  _n=0,$\mu$=0,m2=0_ then for each new number $x$ then   (a) $n = n+1$;  (b) $d = x-\mu$;  (c) $\mu = \mu + d/n$;       (d) $m2 = m2+d*(x - \mu)$;       (e)$\sigma = (m2/(n-1))^{0.5}$ .

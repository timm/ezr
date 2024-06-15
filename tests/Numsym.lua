-- # NUMbers and SYMbols
-- 
-- Symbols and numbers differ
-- by the operations they support.
-- Both can be sorted and both
-- have measures of (a) central
-- tendancies and (b) diversity around
-- tha central tendandcy. But only
-- numbers can be added, divided,
-- subtraced, multiplied, etc.
-- 
-- The central tendancy of NUM,SYMs
-- is called the mean (`mu`) and
-- `mode`, respectively. The diversity
-- measures are `entropy` and `sd`
-- (standard deviation). These
-- diversity measures are a measure of
-- confusion and when we go learning,
-- we prefer ranges where that dviersity is 
-- minimized.
-- 

l=require"lib" ; local o,oo=l.o,l.oo
d=require"data"; local NUM=d.NUM; SYM=d.SYM

f=function(n) return l.rnd(n,3) end

num1 = NUM.new()
for i = 1,1000 do num1:add(i) end
print("nums",f(num1:mid()), f(num1:div()))
assert(500.5 == f(num1:mid()) and 288.819 == f(num1:div()),"bad nums")

sym1 = SYM.new()
for c in ("aaaabbc"):gmatch"." do sym1:add(c) end
print("syms", sym1:mid(), f(sym1:div()))
assert("a"  == f(sym1:mid()) and 1.379 == f(sym1:div()),"bad syms")
-- 
-- 
-- The standard deviation is zero when the numbers are all the same.
-- Similarly, entropy is also zero when all the symbols are the same.

num2 = NUM.new()
for i = 1,1000 do num2:add(1) end
print("sames",f(num2:mid()), f(num2:div()))
assert(1 == f(num2:mid()) and 0 == f(num2:div()),"non-zero ent")

sym2 = SYM.new()
for c in ("aaaaaaa"):gmatch"." do sym2:add(c) end
print("syms", sym2:mid(), f(sym2:div()))
assert("a"  == f(sym2:mid()) and 0 == f(sym2:div()),"bad syms")
-- 
-- 
-- Standard deviations can be calculated in two passes. Once the mean ($\mu$)
-- is known (in pass1), the a second pass can be calculated
-- from the wriggle around the mean; i.e. 
-- as the mean sum of the absolute value of the differences between
-- each item and the mean:
-- 
-- $$\sqrt{\sum_i (x_i - \mu)^2/(n-1)}$$
-- 
-- But why do it it two passes when you can do it in one. Welford's
-- algorithm allows of the incremetanl updating of `sd`:
-- 

function welford(x,n,mu,m2,     d)
  d  = x  - mu
  mu = mu + d/n
  m2 = m2 + d*(x- mu)
  sd = (m2/(n-1+1E-30))^0.5
  return mu,m2,sd end

num3 = NUM.new()
for i = 1,100 do 
   num3:add(math.random())
   if i % 5 ==0 then  
      print("inc", num3.n, f(num3:mid()), f(num3:div()))  end end
-- 
-- One thing that will be important is how early `mu` and `sd` can
-- stabilitize. For example in the above code, `mu` and `sd` converge
-- to 0.55 and 0.288 pretty quickly. 
-- 
--              mu    sd
--              ----- -----
--      inc	10	0.416	0.231
--      inc	20	0.555	0.283
--      inc	30	0.59	0.281
--      inc	40	0.589	0.286
--      inc	50	0.575	0.284
--      inc	60	0.54	0.297
--      inc	70	0.54	0.284
--      inc	80	0.545	0.288
--      inc	90	0.552	0.289
--      inc	100	0.556	0.288
-- 
-- 

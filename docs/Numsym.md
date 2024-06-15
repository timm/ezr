# NUMbers and SYMbols

Symbols and numbers differ
by the operations they support.
Both can be sorted and both
have measures of (a) central
tendancies and (b) diversity around
tha central tendandcy. But only
numbers can be added, divided,
subtraced, multiplied, etc.

The central tendancy of NUM,SYMs
is called the mean (`mu`) and
`mode`, respectively. The diversity
measures are `entropy` and `sd`
(standard deviation). These
diversity measures are a measure of
confusion and when we go learning,
we prefer ranges where that dviersity is 
minimized.

```lua
l=require"lib" ; local o,oo=l.o,l.oo
d=require"data"; local NUM=d.NUM; SYM=d.SYM

f=function(n) return l.rnd(n,3) end

num1 = NUM.new()
for i = 1,1000 do num1:add(i) end
print(f(num1:mid()), f(num1:div()))
assert(500.5 == f(num1:mid()) and 288.819 == f(num1:div()),"bad nums")

sym1 = SYM.new()
for c in ("verify range target"):gmatch"." do sym1:add(c) end
print(sym1:mid(), f(sym1:div()))
```

The standard deviation is zero when the numbers are all the same.
```lua
num2 = NUM.new()
for i = 1,1000 do num2:add(1) end
print(f(num2:mid()), f(num2:div()))
assert(1 == f(num2:mid()) and 0 == f(num2:div()),"non-zero ent")
```
The standard deviation is zero when the numbers are all the same.
```lua
num2 = NUM.new()
for i = 1,1000 do num2:add(1) end
print(f(num2:mid()), f(num2:div()))
assert(1 == f(num2:mid()) and 0 == f(num2:div()),"non-zero ent")
```


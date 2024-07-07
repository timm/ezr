# About this code

## Input Data Format
Sample data for this code can be downloaded from
github.com/timm/ezr/tree/main/data/\*/\*.csv    
(pleae ignore the "old" directory)

This data is in a  csv format.  The names in row1 indicate which
columns are:

- numeric columns as this starting in upper case (and other columns  
  are symbolic)
- goal columns are numerics ending in "+,-" for "maximize,minize".  

After row1, the other rows are floats or integers or strings
booleans ("true,false") or "?" (for don't know). e.g

     Clndrs, Volume,  HpX,  Model, origin,  Lbs-,   Acc+,  Mpg+
     4,      90,       48,   80,   2,       2335,   23.7,   40
     4,      98,       68,   78,   3,       2135,   16.6,   30
     4,      86,       65,   80,   3,       2019,   16.4,   40
     ...     ...      ...   ...    ...      ...     ...    ...
     4,      121,      76,   72,   2,       2511,   18,     20
     8,      302,     130,   77,   1,       4295,   14.9,   20
     8,      318,     210,   70,   1,       4382,   13.5,   10

Internally, rows are sorted by the the goal columns. e.g. in the above
rows, the top rows are best (minimal Lbs, max Acc, max Mpg). 

## Coding conventions

- Line width = 90 characters.
- Indentation = 2 characters.
- Methods = yes; Encapsulation = yes; Polymorphism = yes;  but inheritance = no  (I'll let other people
  explain why no inheritance; see 
  Hatton's [Does OO sync with the way we think?](https://www.cs.kent.edu/~jmaletic/cs69995-PC/papers/Hatton98.pdf)
  and 
  Diederich's [Stop Writing Classes](https://www.youtube.com/watch?v=o9pEzgHorH0)).
- Group methods by functionality, not class (e.g. so all the `add` methods of different classes are together).
- In function args, 2 blanks denote start of optionals. 4 blanks denote start of locals.

## Type hints for function arguments

- Function args uses Alfold-style type hints[^plain].
- Function arguments lists end with return types; e.g. `function most(n1,n2) --> n `
- `z` is anything.
- `t,d,a` are table,array,dict. Arrays have numeric keys; dicts have symbolic keys. 
- `s,n,b` are strings, numbers,booleans. 
- `fun` is a function
- Suffix `s`" is a list of things; e.g. `ns` = list of numbers.
- When used as prefixes, these denote types; e.g. `sFile` is a file name that is a string.
  e.g.  `n1,n2` are two numbers
- Classes are UPPER CASE; e.g NUM. Lower case class numbers denote instances; e.g. `num`.
- `rows` = `list[n | s | "?"]`
- `rows` = `list[row]`

[^plain]:  Alfold is a small plain in Hungary, so "Alfold" is my name for an lightweight plain version of the  Hungarian prefix notation.

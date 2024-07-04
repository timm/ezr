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
- Polymorphic = yes;  inheritance = no. I'll let other people
  explain why: see 
  Hatton's [Does OO sync with the way we think?](https://www.cs.kent.edu/~jmaletic/cs69995-PC/papers/Hatton98.pdf)
  and 
  Diederich's [Stop Writing Classes](https://www.youtube.com/watch?v=o9pEzgHorH0).
- Function args prefixed by two spaces are optional inputs.
  In the type hints, these arguments are marked with a "?".
- Function args prefixed by four spaces are local to that function.
- UPPPER CASE words are classes; 
- Type `table`s are either of type `list` (numberic indexes) or 
  `dict` (symbolic indexes). 
- Type `num` (not to be confused with class NUM) are floats or ints. 
- Type `atom` are bools, strs, or nums.
- Type `thing` are atoms or "?" (for "don't know").
- Type `rows` are lists of things; i.e. `row  =  list[thing]`. ]]

 

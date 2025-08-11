File imports and code size (Aug1, 2025).

```mermaid
graph LR;
lib(<b>lib.py</b><hr>misc code<br>loc=85);
about(<b>about.py</b><hr>config control<br>loc=23);
data(<b>data.py</b><hr>structs definition<br>loc=110)
dist(<b>dist.py</b><hr>distance code<br>loc=147);
like(<b>like.py</b><hr>likelihood code<br>loc=83);
likely(<b>likely.py</b><hr>incremental learning<br>loc=93);
prep(<b>prep.py</b><hr>data preprocessing<br>loc=83);
tm(<b>tm.py</b><hr>text mining ex<br>loc=96);
rq(<b>rq.py</b><hr>experiments<br>loc=13);
stats(<b>stats.py</b><hr>stats code<br>loc=154);
tree(<b>tree.py</b><hr>tree generation<br>loc=95);

lib --> data;
stats --> like;
stats --> rq;
data --> dist;
data --> prep;
about --> lib;
data --> like;
dist --> likely;
like --> likely;
like --> tm;
prep --> tm;
lib --> stats;
data --> tree;
dist --> tree;
tree --> rq;
likely --> rq;
```



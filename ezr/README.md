File imports and code size (Aug1, 2025).

```mermaid
graph LR;
lib(lib.py<hr>misc code<br>loc=85);
about(about.py<br>config control<br>loc=23);
data(data.py<br>structs definition<br>loc=110)
dist(dist.py<br>distance code<br>loc=147);
like(like.py<br>likelihood code<br>loc=83);
likely(likely.py<br>explore code<br>loc=93);
rq(rq.py<br>experiments<br>loc=13);
stats(stats.py<br>stats cide<br>loc=154);
tree(tree.py<br>tree generatin<br>loc=95);
lib --> data;
data --> dist;
about --> lib;
data --> like;
dist --> likely;
like --> likely;
lib --> stats;
data --> tree;
dist --> tree;
tree --> rq;
likely --> rq;
```



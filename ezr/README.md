File imports and code size (Aug1, 2025).

```mermaid
graph LR;
lib(lib.py<br>misc code, loc=85);
about(config control, loc=23);
dist(distance code, loc=147);
like(likelihood code, loc=83);
likely(explore code, loc=93);
rq(experimentss, loc=13);
stats(stats cide, loc=154);
tree(tree generation, loc=95);
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



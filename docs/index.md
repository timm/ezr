
# Why Micro Modeling?

Some of us (many of us) work to  find valuable insights from small,
localized datasets. Not everyone has the resources to build models
with over a trillion parameters. And the consumers
of those models
need, a locally-built
reference model is essential for testing.  E.g.

- Poor results from the local  model can underline the value of the more general model.
- When the general model fails, the local model can become a useful replacement.
- When used in conjunction, the local model can be used to improve what
  comes out of the larger model.

The advantage of micro modeling is that since it is learned from fewer data points, the
learning process becomes faster, and the AI tools can become simpler and more
explainable. This efficiency allows for rapid iteration and easier
interpretation, enabling us to unlock significant value from minimal
data.

To demonstrate principles of micro modeling, this site is organized around a set of hand-on
coding tutorials. All the code is written in Lua (cause that is
such a simple language) and, using any number of auto-translate tools, you can
translate  that code to anything else you want (\*).

- Setting up
  - [Editing and Debugging](dev.md)
  - [Coding experiments](Code.md)
- [Developing Code, 101](dev.md)
- [Numbers and Symbols](Numsym.md)
- Theory
  - [Algorithms](algos.md)


(\*) Of course that translation will not be perfect, but in the process of debugging the broken code you will
learn so much that is useful.

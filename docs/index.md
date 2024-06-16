# Why AI Micro Modeling?

Many organizations
lack the resources to build massive models with trillions of parameters trained on vast datasets. For trustworthy insights, we must build small if we can't build big.

Micro modeling, creating tiny AI models from local data, offers several benefits:

- It allows quick interaction with subject matter experts to build a test suite of highly informative examples.
- Good local model results avoid big model issues like validation, reproducibility, understandability, high CPU costs, privacy concerns, and poor performance on specific problems.
- Poor local model can be used to justify the use of larger models.
- Good local models can replace failing general models.
- Together, local models can enhance the output of larger models.

Micro modeling, learned from fewer data points, speeds up the process
and simplifies AI tools, enabling rapid iteration and easier
interpretation, unlocking significant value from minimal data.

To demonstrate principles of AI micro modeling, this site is organized around a set of hand-on
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

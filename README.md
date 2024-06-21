# EZR AI: Why Micro Modeling?

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
coding tutorials. All the code is written in a simplified Python-like language called Lua.
One way to learn/teach this code is to make all the files in `/tests` class exercises (one per week)
where the code has to be ported to (say) Python, and then some code modification is and you have to explain
how/why that code modification effects the output (and say whether or not that change could be a good thing).

The test code of this site is written  in `ezr/docs` inside markdown files. To run them:

     cd ezr/docs
     make eg=Code

> [!IMPORTANT]
| Note that only markdown file with leading upper case names have tests.

The above idiom will convert Code.md to Code.lua, then execute it
(importing what it needs from `/src/*.lua`).


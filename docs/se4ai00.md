% Intro SE 4 AI
% Tim Menzies
% March 22, 2024

# Changing How we Think About AI

The next slide may change, forever, all you think you know about AI.

# Surfing the long tail


- LLMs for specific problems?
  - LLMs  know a lot, about things we do a lot (e.g.  "if" statements in code)
  - And they know _less_ about things we do _less_ often
- Model collapse: 
  - We are about to run out of training data [^less24] for LLMs.
  - Can't reply of synthetic data generation (no new information from data already seen)
- So,  we make do with _less_ data?
  - Are their domain,  were models need less, not more, data?

[^less24]:  Udandarao, V., Prabhu, A., Ghosh, A., Sharma, Y., Torr, P.H., Bibi, A., Albanie, S. and Bethge, M., 2024.  No" zero-shot" without exponential data: Pretraining concept frequency determines multimodal model performance. arXiv preprint arXiv:2404.04125.

#  Software Review (1)

- The more we use AI in SE, the more code will be auto-generated. 
- The more we auto-generate code, the less time software engineers 
  spend writing and reviewing new code, written by someone or something
  else (the internals of which they may not understand).
- The less we understand code, the more we will use black-boxes components,
  where, once a system is assembled, its control settings are tuned. 
- In this scenario, it becomes very important to reduce the human effort
  and CPU effort required for that tuning.

# Software Review (2)

- We define “software review” as a panel of SMEs (subject matter experts),
  looking at examples of behavior to recommend how to improve software.
- SME time is usually very limited so, such reviews must complete after 
  looking at just a small number of very informative examples. 
- To support the software review process, we explore methods that train 
  a predictive model to guess if some oracle will like/dislike the next example. 
- These predictive models work with SMEs to guide them as they explore the examples. Afterwards, the models
  can handle new examples, while the panelists are busy, elsewhere

# Q: How few questions can humans answer? A: Not so many


What | N
----:|-------
Standard theory: |  more is always better
Cognitive Science: | 7 plus or minus 2
From human studies (cost estimation, rep grids) : |  10 to 20 examples per 1-4 hours
Regression theory| 10 examples per attribute
Semi-supervised learning | $\sqrt{N}$
Zhu et al. [^zhu16] | 100 images
Menzies et al. 2008 [^Me08] | 50 examples
Chessboard model    | 200 examples
Probable Correctness theory | simpler cases: 50 to 6 (if we can binary chop)<br> safety-critical cases: 272 to 8 (if we can binary chop)<
 

[^zhu16]: Zhu, X., Vondrick, C., Fowlkes, C.C. et al. Do We Need More Training Data?.  Int J Comput Vis 119, 76–92 (2016). https://doi-org.prox.lib.ncsu.edu/10.1007/s11263-015-0812-2

[^Me08]: Menzies, T., Turhan, B., Bener, A., Gay, G., Cukic, B.,  PROMISE workshop, 2008, (pp. 47-54).

# Maths: Gasussians


# Maths: Probabi;ity Theory

- Confidence $C$ to see an event at prob.  $p$ after $n$ trials $C = (1 - p)^n$.
  - So $n = \frac{log(1-C)}{log(1-p)}$
- If we have any tricks for order examples best to worst, we can do a binary chop
  - So $n = log_2\left( \frac{log(1-C)}{log(1-p)}\right)$
- Guassians 

# adas

[.column]

### The First column

[.column]

### Second column.

# aasdas

asdada

```mermaid
pie showData
    title Key elements in Product X
    "Calcium" : 42.96
    "Potassium" : 50.05
    "Magnesium" : 10.01
    "Iron" :  5
```

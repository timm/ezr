% Open Problems in Active Learning for Multi-Objective Optimization
% by timm, <timm@ieee.org>
% &copy; 2024, BSD-2 license
<hr>

## The general problem: 

- Given rows of data with many $X$ independent values and many $Y$ goals where $Y=f(X)$:
  - Look at the fewest $Y$ values 
  - To find what $X$ values predict for the best $Y$ values
- Curently, we are stuck at  at around 30-40 labels (have been for about a year). Can we get 
  this down to 15-20?

## More specific problems:

### Exploring Quirks with the Oracle 
- Assume X% wrong, try things with increasing X (e.g. 0,10,20,40%)
- Assuming N oracles all give different opinions,
  is there value in  combining results from different sessions with different
  oracles? Should we run such sessions in parrallel or in series (the latter is
  attractive since it means experience from one expert could simplify into the 
  experiernce of the next expert).

### Acquisition functions
- Explore? exploit? adaptive?
- Uncertainty (or not)
- Different for different kinds of data?
- Membership query synthesis

### Initial label selection (avoiding the "cold start" problem)
- Heuristics to intiialize the labeled set?
- Random, diversity, rrp?

### Initial data selection
- Full dendogram generation, then reflection across the whole structure.
  - e.g. sample rows at a frequency equal to leaf diversity
- Divide larger data sets in two (at random)
  - Does a model learnt from first half part work for second part?
  - How large must the first part be before we can  learn a model stable for the second part?

### Clustering
- Anything better than twoFar?
- Can we discover important clusters as we go (regions that need their own model). 
  - If we fork a new cluster, what of the old model can we take to it?

### Streaming
- Early stopping? Track progress to date then stop early
- Pool learning:
  - Current tool is a "pool" learner that can access all the unlabelled examples.
  - An alternate approach is a "stream" learner that eats the data in "eras" of size (say) 1000
  - So instead of starting from zero all the time
    - Restart each era with the model learned from era[-1] 
- Why does the faster heuristic work? can we use that to build a better algorithm?

### Explanation 
- Can we learn a  stable symbolic model that predicts for better?
- What is the "explanation tax"; i.e. how much do we lose if we use the rules?

### Higher dimensional data
- Text mining
- Audio data
- Image data

### Other data
- How much of fig7 of https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/MSR-TR-2011-8.pdf
  can we cover?
- some of the goals we are exploring are a little dull. Can we do better?
  - For https://arxiv.org/pdf/2311.17483.pdf, fig 9, what support can you add to support (say) 5 of the 
    lefthand side requirements? 
  - This one is challenging. How would you generate the data to explore?
    - But wait! we only need under 40 examples. Does that help us?

### Benchmark against standard optimizers
- e.g. optuna, hyperplan (BOHB), DE
  - Will need an oracle that can label any example (see "regression" or "data synthesis",  below)
  - Or, apply all this to known models 
      - e.g  [Pymoo](https://github.com/anyoptimization/pymoo) has hundreds
        of such models
      - See [here](https://pymoo.org/problems/test_problems.html)
      - The DTLZ models are really widely used (but I fret they are simplistic):
        - and [DF](https://pymoo.org/problems/dynamic/df.html) looks pretty cool.
      - Try to avoid the really simple ones. Try to do something SE relevant

### Hyper-parameter optimization
- Can ezr tune ezr?
- Can ezr tune other algorithms?

### Non-optimization
- Classification
- Regression
- Anomaly detection
- Data synthesis
  - Need a measure of new data being the same as old
- Data de-biasing

### LLMs
- Better than LLM?
- Use to select for questions in few shot learning?
- Use to select prompts for case based reasoning?

# Open problems

The general problem: 

- do everything with least labels
- seem stuck at around 30-40 labels. Can we get it to 15-20?

More specific problems:

- acquisition functions
  - explore? exploit? adaptive?
  - uncertainty (or not)
  - different for different kinds of data?
  - membership query synthesis
- initial label selection
  - random, diversity, rrp
- initial data selection
  - full dendogram generation, then reflection across the whole structure.
    - e.g. sample rows at a frequency equal to leaf diversity
  - divide larger data sets in two (at random)
    - does a model learnt from first half part work for second part?
    - how large must the first part be before we can  learn a model stable for the second part?
- clustering
  - anything better than twoFar?
- streaming
  - early stopping?
- oracle errors
  - assume X% wrong, try things with increasing X (e.g. 0,10,20,40%)
- explanation 
  - can we learn a  stable symbolic model that predicts for better?
  - what is the "explanation tax"; i.e. how much do we lose if we use the rules?
- higher dimensional data
  - text mining
  - audio data
  - image data
- other data
  - Some of the goals we are exploring are a little dull. Can we do better?
    - For https://arxiv.org/pdf/2311.17483.pdf, fig 9, what support can you add to support (say) 5 of the 
      lefthand side requirements? 
    - This one is challenging. How would you generate the data to explore?
      - But wait! we only need under 40 examples. Does that help us?
- benchmark against standard optimizers
  - e.g. optuna, hyperplan (BOHB), DE
    - will need an oracle that can label any example (see "regression" or "data synthesis",  below)
    - or, apply all this to known models 
        - e.g  [Pymoo](https://github.com/anyoptimization/pymoo) has hundreds
          of such models
        - See [here](https://pymoo.org/problems/test_problems.html)
        - The DTLZ models are really widely used (but I fret they are simplistic):
          - and [DF](https://pymoo.org/problems/dynamic/df.html) looks pretty cool.
        - Try to avoid the really simple ones. Try to do something SE relevant
- hyper-parameter optimization
- non-optimization
  - classification
  - regression
  - anomaly detection
  - data synthesis
    - need a measure of new data being the same as old
  - data de-biasing
- LLMs
  - better than LLM?
  - use to select for questions in few shot learning?
  - use to select prompts for case based reasoning?

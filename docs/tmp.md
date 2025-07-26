# Don't read this.

This is a dumping ground for side excursions, some of which will be folded back into main.

Years ago, in a graduate AI class, a student asked why our models needed so much data.  
“They don’t,” I said. “We just haven’t learned how to ask the right questions.”  

That turned into a dare: could we build useful models from just a few labeled examples? So we wrote a quick prototype. It peeked at a handful of data points, built two tiny models—one for “good,” one for “bad”—then guided learning by comparing the two. It was fast, simple, and surprisingly effective.

That spirit—minimalist, contrastive, purposeful—runs counter to much of today’s AI. The dominant trend is maximalist: larger models, larger datasets, larger compute. But with scale comes cost: complexity, slowness, and opacity. Reproducibility suffers. In a recent review of 229 software engineering papers using LLMs, only 13 (just 5%) compared their results to any alternative. Students and practitioners alike are left in the dark—unable to look inside, to question, or to adapt.

This report proposes a different path. We introduce **EZR**, a fast, compact active learner built around the idea that small, well-chosen examples can carry most of the signal. EZR builds interpretable models from minimal data and uses them to guide optimization, classification, and explanation. It’s not just a tool—it’s a case study in what becomes possible when we reclaim simplicity and control.

Others explore similar options—**active learning**, **semi-supervised learning**, and **contrastive sampling**—but often through thousands of lines of evolutionary algorithms, Parzen windows, or Gaussian process models. **EZR achieves similar goals with just a few dozen lines of ultra-simple code**: fast Bayes classifiers, greedy search, and decision trees. That brevity isn’t just aesthetic—it makes EZR easier to teach, easier to maintain, and far easier to modify or extend. It’s a tool built for **experimentation and understanding**, not just automation. It’s also fast: **1,000+ experiments across 100+ datasets run in under two minutes**. And unlike incomprehensible LLMs, EZR is grounded in **explicit theory**—transparent, auditable, and open to critique (or even complaint).

We evaluate EZR using over 100 diverse examples from the [MOOT repository](https://github.com/timm/moot), drawn from real-world SE tasks like tuning, configuration, and process design. Our goal is not just performance—but also clarity, speed, and insight.

**Our research questions:**

- **RQ1: Is it simple?**  
  Does EZR offer a compact, readable codebase for teaching and tinkering?

- **RQ2: Is it fast?**  
  Can it complete tasks in milliseconds rather than hours?

- **RQ3: Is it effective?**  
  Can it achieve strong results after seeing only a few examples?

- **RQ4: Is it insightful?**  
  Does it support explainability, critique, and understanding?

- **RQ5: Is it general?**  
  How well does it apply across varied SE optimization tasks?

----------
_____
In an ideal world, some AI tool could help by learning from a large
log that shows what options lead to what effects.
In such a log,
the _control options_ are shown at left (these are all the 0,1s) and the _effects_
are shown at right (_energy, time, cpu_). If we sorted those rows best to worst
then, as shown here:

- The four first rows have low energy, runtimes, and cpu;
- While the final four rows run much slower and use more energy and cpu.


                                                     Energy-, time-,t   cpu- 
    0, 0, 0, 0, 1, 0, 1, 0, 1, 1, 0, 0, 0, 1, 1, 1, 0,   6.6, 248.4,  2.1
    0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0,   6.6, 248.6,  2.0
    0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0,   6.6, 249.2,  2.0
    0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 0, 0,   6.6, 248.6,  2.1

    [skipping 800 lines...]

    0, 1, 0, 1, 1, 1, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1,  16.7, 519.8, 14.1
    1, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1,  16.8, 518.8, 14.1
    1, 1, 0, 1, 1, 1, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1,  16.7, 519.0, 14.1
    1, 1, 0, 1, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1,  16.8, 518.6, 14.1


At this point EZr's memory contains (i) a few rows with labelled effects;
and (ii) many more rows 
showing many control options, but without any effect information. For _A=4_,
this looks
like this:


    2 Best rows:
                                                         Energy-, time-,  cpu- 
        0, 0, 0, 0, 1, 0, 1, 0, 1, 1, 0, 0, 0, 1, 1, 1, 0,   6.6, 248.4,  2.1 <== Best1
        0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0,   6.6, 248.6,  2.0 <== Best2
    
    2 Rest rows:
    
        0, 1, 0, 1, 1, 1, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1,  16.7, 519.8, 14.1 <== Rest1
        1, 1, 0, 1, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1,  16.8, 518.6, 14.1 <== Rest2
    
    Many more rows, with nothing known about their effects:
    
        0, 1, 0, 1, 1, 1, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1,     ?,     ?,    ?
        1, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1,     ?,     ?,    ?
        1, 1, 0, 1, 1, 1, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1,     ?,     ?,    ?
        1, 1, 0, 1, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1,     ?,     ?,    ?
    
        [skipping 800 lines...]
    


    2 Best rows:
                                                         Energy-, time-,  cpu- 
        0, 0, 0, 0, 1, 0, 1, 0, 1, 1, 0, 0, 0, 1, 1, 1, 0,   6.6, 248.4,  2.1 <== Best1
        0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0,   6.6, 248.6,  2.0 <== Best2
    
    3 Rest rows:
    
        0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0,   6.6, 249.2,  2.0 <== Rest1
        0, 1, 0, 1, 1, 1, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1,  16.7, 519.8, 14.1 <== Rest2
        1, 1, 0, 1, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1,  16.8, 518.6, 14.1 <== Rest3
    
    Many more rows, with nothing known about their effects:
    
        0, 1, 0, 1, 1, 1, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1,     ?,     ?,    ?
        1, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1,     ?,     ?,    ?
        1, 1, 0, 1, 1, 1, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1,     ?,     ?,    ?
        1, 1, 0, 1, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1,     ?,     ?,    ?
    
        [skipping 800 lines...]

"Build" repeats itself until _B_ items are labelled.  The labelled rows are then given
to a tree learner that 
is given to a tree learner. For _B=24_,  that generates  a tree with 21 nodes and niWe ne leaf nodes:
    
     win 
    ----
      74    crypt_blowfish == 0
      90    |  memory_tables == 1
      96    |  |  small_log == 0
      97    |  |  |  logging == 0
      98    |  |  |  |  txc_mvlocks == 0
      99    |  |  |  |  |  no_write_delay == 0;   <==== LEAF #1
      97    |  |  |  |  |  no_write_delay == 1
      97    |  |  |  |  |  |  encryption == 1;    <==== LEAF #2
      95    |  |  |  logging == 1
      95    |  |  |  |  no_write_delay == 1
      96    |  |  |  |  |  encryption == 1;       <==== LEAF #3
      95    |  |  |  |  |  encryption == 0;       <==== LEAF #4
      80    |  |  small_log == 1
      84    |  |  |  txc_mvcc == 0
      87    |  |  |  |  compressed_script == 0
      90    |  |  |  |  |  encryption == 0;       <==== LEAF #5
      85    |  |  |  |  |  encryption == 1;       <==== LEAF #6
      76    |  |  |  |  compressed_script == 1;   <==== LEAF #7
     -23    |  memory_tables == 0
     -15    |  |  compressed_script == 0;         <==== LEAF #8
    -518    crypt_blowfish == 1
    -273    |  txc_mvlocks == 0;                  <==== LEAD #9
      
In this tree, "win" reports how close we get to the best value. 
In this example, we have over 800 rows. 
"Win" is calculated by an agent with  magical powers that  knows all the effects on all the rows.
In our 800 rows there is a middle and best value for all effects. If this tree selects rows with a mean effect of _x_,  then: 

$$win=100*(1- (x-best)/(middle-best))$$

Negative "wins" mean you are making things worst. A zero "win" means not improvement. And a "win" of 100 means you have found the best.
We see in this tree that of the 18 configurations we might use, we only need to adjust give to achieve
the
largest win (see the 99% win of "LEAF \#1"). Reading from the top of the tree, those five choices are:

    crypt_blowfish == 0
    |  memory_tables == 1
    |  |  small_log == 0
    |  |  |  logging == 0
    |  |  |  |  txc_mvlocks == 0
    |  |  |  |  |  no_write_delay == 0;   <==== LEAF #1; win = 99%
    
It is prudent to ask if this tree, learned from just _B=24_ examples, is a good summary of
the 800 rows used to generate it.
Hence in the _C_ phas ("C" for "check") we apply the tree to all the rows.
Each row selects for one of the leaves of the trees. Rows are then sorted by the mean of their selected leaves.
If the  top _C=5_ rows are evaluated, the best row found in this way has a win in 98% (i.e. just a tiny
bit less than the win predicted by the tree).



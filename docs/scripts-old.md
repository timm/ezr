_________

# coding101

- in complete

- tim's zeroth rule: LLMs wont replace programmers
- how to use the code . knn (simplest)
  - shebang, vim settings
  - Githib, branching, merging, readme, license, .gitignore
     - action ci/cd  
  - docs/index.md (from README.md)
    - proj1: folrk issues. milestones. doc
  - bob's rule (5 lines)
  - sven's rule (config crisis)
  - tim's rule (use less globals)
  - "Any code of your own that you haven't looked at for six or more months might as well have been written by someone else." — Eagleson's law
    - thou shalt document
    - thou shalt add a regresson/demo suite
  - indent with spaces, not tabs. or indent with tabs. just dont do both
  - aunt barby's rule (use abstraction, functional programming)

coal-face scripting
- edit and run at the same time
  - e.g. vscode
  - lsp (langauge sever protocol. static analysis)
  - watch 
  - reset status badge
  - test driven development
  - big example: the google story, sebastian
- licenses
  - open source
  - big example: project health- debugging
  - vscode debugger
  - big example: delta debugging, shaperio,code repair
- dependancies
  - make
    - the cult of no recrusve makes  
  - autobuild
  - big example: GH workflows
- decomposition / composition
  - DRY, or you will be WET
  - pipes
  - regular expressions
  - patterns (e.g. DATA's services defined by recursive call to NUM or SYM)
    - others factory (e.g. COLS), visitor (tree printing)
    - LSP
  - big example : LSP
- documentation
  - self-documenting code (my scripts, make with help file)
  - type hints
  - big example: rust
- testing
  - test driven development
    - unit test, watch
  - ziztler's papers on differnt debugging
  - fuzzing
  - sharperio's debbuging 
- - abstraction
  - separate mechanism from policy (my data little language)
  - iterators, try catch
  - functional programming

python
-  Destructuring

SE theory
- decomposition: parnas. interface, polymorphism
- testing (black box. white box, format) static analysis
    - "If debugging is the process of removing bugs, then programming must be the process of putting them in."
    "Writing code without tests is like driving a car with your eyes closed."
- types.strongly typed languages. haskell. rust.

- something about scale. e.g. jenkins
   -  config in xml build scropt ==> ant script ==> tests
   -  tempaltes for build . make make
   -  create 300 jenkins jobs in 30 seconds
- crontab:
- cloud
  - containers. docker. docker compse.
  - serverless
- make expanded into maven/gradle/ build supprot tools.
 
-----

self critique: LLM is written by google and they check it. right? no!

From here down, probably a second grad class on ?knowledge engineering.

Maths
- NUMs, SYMs
- welford,chebyshev (and other distance measures)
- fastmap, nystrom, PCA

Stats:
- mean, standard devation, pooled variance
- expected value, cull if
- effect size, significance tests
- cohen, cliffs, bootstraop
- Hamlet's probablity theory. maths of sampling

Learning theor
- unsupervised: clustering, dendograms
- supervised: optimziation, classificatio, regression
- semi-supervised: smo, rrp
- discretization
  - surprisingly few rows
  - surprisingly few important rows
- decision trees, rules, equations, 
- feature selection, row selection, range selection
- hyperaprater optimization

micro modeling 
- most of the behavior in a small corner of the state space
  - dont expand, then contract
  - just search for the keys
- ranges ==> trees ==> regression (or classification)
- dendograpms ==> optimization

exercses
- code sharing (Github)
- scripting environents (Makefile, shell)

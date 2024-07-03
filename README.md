# EZR AI: Why Micro Modeling?

Micro modeling, learned from fewer data points, speeds up the process
and simplifies AI tools, enabling rapid iteration and easier
interpretation, unlocking significant value from minimal data.

Why why explore micro-modeling? Why not just (e.g.) use large language models are as our oracles for everything?

Well, just to say the obvious, it takes a lot of resources to learn a (say) trillion parameter model. Most organizations lack those resources
which  means most people have to rent (and trust) models built by other people.
That would be fine in the larger models never hallucinated bad output
or if those larger models knew everything, or could be quickly tuned to local data.  

So let us try that. Here's the results of
applying few short and zero-shot learning to a LLM (Google's Gemini model) for the process of reviewing 400 used cars 
(zero-shot and few-shot learning are ways of presenting a few examples to an LLM, in order to tune it to some local task).
In this example,  we are looking for good lightweight cars
that are fast and which have good gas mileage 
The way we scores our cars then in that plot, better cars are found lower down. 

The green curve in that plot compares the EZR results to the LLMs. 
The EZR curve is lower than the LLM which means if finds better cars, much faster than the LLM.
Note only that, but the EZR models are much easier to build than the LLMs  (EZR took
milliseconds of training a model with 8 variables while the LLM needed hundreds of millions of dollars to train a model with trillions of parameters). 

Which is not to say that EZR always wins for all tasks. But it does mean that there are range of tasks for which lightweight AI tools are getting really good and really simple and really fast.
So I would say that a modern AI practitioner, or user of AI, needs to know about very big modeling methods (using LLMs). But that same practitioner should
know about  EZR modeling methods. In fact, I'd recommend trying EZR before LLM since then:

- Poor results with tiny EZR  model can tell you if and when you need to a larger model.
- On the other hand, if the tiny EZR models get good results, then maybe you won't need a much bigger model. This would avoid numerous problems
   with understandability, validation, reproducing results, high CPU costs, privacy concerns, and poor performance on specific problems.
- And it need not be just one of the other. Together, tiny EZR  models can be used to enhance LLMs. For 
   example, once you build a  tiny EZR model, you have an oracle that can generate test cases for the LLM (so tiny EZR modeling can help you understanding those bigger models).

The rest of this document show
principles of AI micro modeling. The text
is organized around a set of hand-on
coding tutorials. All the code is written in a simplified Python-like language called Lua.
One way to learn/teach this code is to read this briefing document then, when it tells you to,
go explore a file in 
`/tests`. THere:
- the code has to be ported to (say) Python; That porting should be pretty straightforward but there will be enogugh "gotchas" to make you pause, somethings, and thing hard about
    what is going on.
- then some code modification is and you have to explain
how/why that code modification effects the output (and say whether or not that change could be a good thing).

The test code of this site is written  in `ezr/docs` inside markdown files. To run them:

     cd ezr/docs
     make eg=Code

> [!IMPORTANT]
| Note that only markdown file with leading upper case names have tests.

The above idiom will convert Code.md to Code.lua, then execute it
(importing what it needs from `/src/*.lua`).


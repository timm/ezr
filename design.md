# Earned Simplicity

> "Simplicity does not precede complexity, but follows
> it." -- Alan Perlis, epigram 31

Earned simplicity is that effect where, given enough experience,
many surface tasks collapse, onto one mucher smaller (possibly much
stranger) machine. Earned simplicity asks do we  know enough about
our tools and processes to replace them with some things that are
much smaller and much more essential.

Earned simplicity cannot be created after seeing one design, You
arrive at it after living with the system, then rebuild everything
on it again and again.  And it is anti-information-hiding: the whole
point is to expose the inner workings and show how small they are.
The kernel is not designed; it is earned.

The counterclaim to earned simplicity comes in two
strengths. Tesler's Law (conservation of complexity): a
system's complexity can only be moved, never removed, so
design's job is to hide it behind a good surface.
Stronger, Brooks's "No Silver Bullet" (1986): software
complexity divides into essence, which no tool or method
can much shrink, and accident, which is mostly gone
already. Earned simplicity doubts that boundary. Each
entry below is a case where "essence", after long
acquaintance, was reclassified as accident -- costume
that someone finally deleted. (Norman, "Living with
Complexity" 2011, half-concedes: "what is complex on the
surface can be simple inside" -- but then argues for
taming complexity. This lineage argues for shrinking it
until there is nothing left to tame.)

Why is earned simplicity so rare? Because it is very
complex to find. Rushing out tomorrow's product leaves no
time to reflect on the past and unify ten things into
one. And the market's incentives point the other way:
industry wants ten things to sell, and complexity that
makes us dependent on its services -- one person's
problem is another's consultancy opportunity. Wirth said
it plainly in "A Plea for Lean Software" (1995): fat
software is not an accident but a vendor strategy.
Gabriel's "worse is better" (1991) explains the ratchet:
the complicated-but-shippable thing wins the market
before the simple thing is found. Upton Sinclair supplies
the epitaph: "It is difficult to get a man to understand
something when his salary depends upon his not
understanding it."

## Examples of Earned Simplicity

- **The alphabet, c. 1050 BC**. Thousands of picture-signs
  collapse onto ~22 letters that spell anything. The
  scribes of logographic scripts did not plan it; traders
  found it.
- **Newton 1687**. Apples, tides, moons and cannonballs
  collapse onto three laws and one gravitation. The
  best-known found kernel there is.
- **Darwin 1859**. All the apparent design in life
  collapses onto one dumb loop: vary, select, retain.
  Nobody expected the designer to be a machine that small.
- **Maxwell 1865**. Electricity, magnetism and light:
  four equations. The source of Kay's metaphor below.
- **Mendeleev 1869**. Every substance collapses onto ~90
  elements -- and later, those onto three particles.
- **Sheffer 1913**. Logic's rich basis (and, or, not,
  implies) collapses onto one strange operator: NAND.
  Nobody designed toward the Sheffer stroke; it was found.
  Nicod then derived all of propositional logic from one
  axiom over it.
- **Church 1932 / Turing 1936**. All computation into the
  lambda calculus, or one machine.
- **Shannon 1937**. Ad-hoc relay circuit craft collapses
  onto Boole's half-forgotten algebra. Surface expertise,
  reconstructed on a strange old machine.
- **Shannon 1948**. Every medium (voice, pictures,
  telegraph) collapses onto one primitive, the bit, and
  one measure, entropy. The engineers' many notions of
  "amount of signal" turn out to be one found number --
  which still runs inside ezr's div().
- **Watson & Crick 1953; Crick et al. 1961**. All of
  life's inheritance collapses onto a four-letter tape and
  one triplet code. A digital machine inside cells, which
  no biologist ordered in advance.
- **McCarthy 1960**. Lisp's eval/apply on half a page.
  Alan Kay later called this "the Maxwell's equations of
  software" -- the popular name for the whole aesthetic.
- **Robinson 1965**. All logical inference into one rule:
  resolution.
- **Landin 1966**. "The Next 700 Programming Languages."
  The methodological statement (notes below).
- **Patterson & Ditzel 1980**. RISC: the empirical
  version. Measure real instruction traces, then shrink to
  the strange small core the data reveals. Experience
  guides you there.
- **Ingalls 1981**. "Design Principles Behind Smalltalk":
  the spec-on-a-postcard aesthetic stated as principle
  ("provide a single uniform metaphor").
- **Liedtke 1995**. Microkernels. The engineering
  criterion: "a concept is tolerated inside the mu-kernel
  only when moving it outside would prevent the system's
  required functionality." A necessity test, built for
  privilege boundaries; see below for why ezr's test is
  Landin's, not this one.


Philosophy-of-science name: **rational reconstruction**
(Carnap) -- rebuilding a rich domain from a minimal
primitive basis, retrospectively. One-liner: Perlis,
epigram 31: "Simplicity does not precede complexity, but
follows it."

For papers: "found kernel" or "post-hoc core calculus",
with Landin as the anchor and RISC as the empirical twin.

## Notes on Landin

Peter Landin, "The Next 700 Programming Languages", CACM
9(3), 1966. Written when ~1,700 languages already existed;
the title is a jab at that census.

1. **The claim**: most languages differ in vocabulary and
   costume, not substance. So do not design the next
   language; design a *family*: fix a tiny applicative
   core, then vary the surface.
2. **ISWIM** ("If you See What I Mean") is that family,
   not a language: a lambda-calculus core plus a
   replaceable "physical" layer (notation) and "logical"
   layer (choice of data primitives). Fix the core, swap
   the layers, get 700 languages for free.
3. **"Syntactic sugar"** is coined here. Where-clauses,
   let-bindings, operators: all defined by translation
   into core applications. Sugar is honest only if the
   translation is published.
4. **The strange machine**: Landin 1964 ("The mechanical
   evaluation of expressions") had already given the core
   its engine -- the SECD machine: four registers (Stack,
   Environment, Control, Dump) that run everything. Nobody
   asks for SECD up front; it is what remains when the
   expected machinery is boiled away.
5. **The offside rule** (meaning from indentation) also
   debuts here -- surface syntax treated as a pluggable,
   cheap decision, because the core carries the meaning.
6. **Descendants**: ML and Haskell (whose "Core" is an
   ISWIM), every PL paper that says "we reduce to a core
   calculus", and every title of the form "The next 700
   X".

**Relevance to ezr**: ezr is an ISWIM move on AI tooling.
The core is Num/Sym plus one update primitive and two
distances; naive bayes, trees, clustering, optimizers and
active learning are the sugar -- each defined by a short,
published translation onto the core. y1, y2, y3 were the
next 700 ezrs: same core, varying costume.

**ezr's kernel test is Landin's, not Liedtke's.** Liedtke
admits a concept only when it is impossible outside the
kernel -- a necessity test, built for privilege
boundaries. ezr has no privilege boundary; its admission
rule is a sharing test: a function belongs in ezr.py only
if two or more learners ask questions of it. That is
Landin's criterion: the core is what stays fixed while
the sugar varies. (Audited over the call graph: 17
functions pass; the cut/label/stats plumbing serves them;
evaluation and display stay by mission, since
self-checking and self-explanation are the product's
claim, not conveniences.)

## References

- Brooks, F. "No Silver Bullet: Essence and Accidents of
  Software Engineering." IEEE Computer 20(4), 1987
  (first presented IFIP 1986).
- Carnap, R. Der logische Aufbau der Welt. 1928.
- Church, A. "A Set of Postulates for the Foundation of
  Logic." Annals of Mathematics 33, 1932.
- Crick, F., Barnett, L., Brenner, S., Watts-Tobin, R.
  "General Nature of the Genetic Code for Proteins."
  Nature 192, 1961.
- Daniels, P., Bright, W. (eds). The World's Writing
  Systems. Oxford, 1996. (On the alphabet's origins.)
- Darwin, C. On the Origin of Species. John Murray, 1859.
- Gabriel, R. "Lisp: Good News, Bad News, How to Win
  Big." AI Expert, 1991. (The "worse is better" essay.)
- Ingalls, D. "Design Principles Behind Smalltalk."
  Byte 6(8), 1981.
- Kay, A. "A Conversation with Alan Kay." ACM Queue
  2(9), 2004. (Lisp as "the Maxwell's equations of
  software".)
- Landin, P. "The Mechanical Evaluation of Expressions."
  Computer Journal 6(4), 1964. (The SECD machine.)
- Landin, P. "The Next 700 Programming Languages."
  CACM 9(3), 1966.
- Liedtke, J. "On mu-Kernel Construction." SOSP 15, 1995.
- Maxwell, J.C. "A Dynamical Theory of the
  Electromagnetic Field." Phil. Trans. Royal Society
  155, 1865.
- McCarthy, J. "Recursive Functions of Symbolic
  Expressions and Their Computation by Machine, Part I."
  CACM 3(4), 1960.
- Mendeleev, D. "On the Relationship of the Properties
  of the Elements to their Atomic Weights." Zeitschrift
  fur Chemie 12, 1869.
- Newton, I. Philosophiae Naturalis Principia
  Mathematica. 1687.
- Nicod, J. "A Reduction in the Number of Primitive
  Propositions of Logic." Proc. Cambridge Philosophical
  Society 19, 1917.
- Norman, D. Living with Complexity. MIT Press, 2011.
  (Also the standard source for Tesler's Law,
  c. 1984.)
- Parnas, D. "On the Criteria To Be Used in Decomposing
  Systems into Modules." CACM 15(12), 1972.
- Patterson, D., Ditzel, D. "The Case for the Reduced
  Instruction Set Computer." SIGARCH Computer
  Architecture News 8(6), 1980.
- Perlis, A. "Epigrams on Programming." SIGPLAN Notices
  17(9), 1982.
- Robinson, J.A. "A Machine-Oriented Logic Based on the
  Resolution Principle." JACM 12(1), 1965.
- Shannon, C. "A Symbolic Analysis of Relay and
  Switching Circuits." MSc thesis, MIT, 1937 (Trans.
  AIEE 57, 1938).
- Shannon, C. "A Mathematical Theory of Communication."
  Bell System Technical Journal 27, 1948.
- Sheffer, H.M. "A Set of Five Independent Postulates
  for Boolean Algebras." Trans. AMS 14, 1913.
- Sinclair, U. I, Candidate for Governor: And How I Got
  Licked. 1935.
- Turing, A. "On Computable Numbers, with an Application
  to the Entscheidungsproblem." Proc. London
  Mathematical Society 42, 1936.
- Watson, J., Crick, F. "Molecular Structure of Nucleic
  Acids." Nature 171, 1953.
- Wirth, N. "A Plea for Lean Software." IEEE Computer
  28(2), 1995.

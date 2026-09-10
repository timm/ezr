# The Found Kernel

A design lineage: many surface tasks collapse, after the
fact, onto one small strange machine. The kernel is not
pre-specified (contra Parnas); it is discovered by living
with the system, then everything is rebuilt on it. And it
is anti-information-hiding: the whole point is to expose
the inner workings and show how small they are.

## The precedent chain

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
  required functionality."


Philosophy-of-science name: **rational reconstruction**
(Carnap) -- rebuilding a rich domain from a minimal
primitive basis, retrospectively. One-liner: Perlis,
epigram 31: "Simplicity does not precede complexity, but
follows it."

For papers: "found kernel" or "post-hoc core calculus",
with Landin + Liedtke + RISC as the precedent triangle.

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

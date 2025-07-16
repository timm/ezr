# What is this directory?

By placing personal scripts directory (,) inside a project's root
and tracking it with Git, we ensure that  tooling travels with the
code. When you clone a repository onto a new machine, the entire
personalized command set is instantly available and works out of
the box.

This is a is similar in principle to more conventional methods like:

- Makefile: Bundling common project commands (make build, make test).
- A scripts/ or .bin/ directory: A more conventionally named folder for the same purpose.
- Devcontainers (.devcontainer/): A modern approach that packages the entire development environment, 
  including the OS and installed tools, into a container that travels with the repository.

The ,/ directory is a lightweight implementation of this same core
idea, helping with consistency and reducing setup friction when
working with code.

Goals (not all here):

- lint:	Basic syntax/style checkers
- doc:	Pull inline docs, or generate .md files
- log:	Tail recent logs, prettify timestamps
- web:	Quick curl or ping tests
- conf:	Shell env tweaks, prompt setup
- new:	Script scaffolder, e.g., make a new shy/ script
- env:	Dump, activate, or load environments
- test:	Run regression/unit tests on your scrip

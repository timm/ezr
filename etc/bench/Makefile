# Ten ports of the ezr.py kernel, verified against one reference output.
#   make        - build, verify and time every port
#   make sizes  - loc/char counts only (no toolchains needed)
#   make ref    - regenerate ref.txt from the Python reference
#   make clean

REPS ?= 8 60

all: build
	python3 run.py $(REPS)

sizes:
	python3 count.py

build: run.js drivehs driveml

# slice.js declares top-level consts; node modules do not share scope, so the
# driver is built by concatenation rather than require(). Loading it through
# eval() instead costs ~9x at runtime -- do not.
run.js: slice.js drive.js
	@{ echo 'var P = 2, Few = 128, Start = 4, Stop = 50, SEED = 1'; \
	  cat slice.js; grep -v '^var P = 2' drive.js; } > $@

drivehs: Slice.hs DriveHs.hs
	ghc -O2 -o $@ DriveHs.hs Slice.hs

driveml: slice.ml drive.ml
	ocamlopt -I $$(ocamlc -where) unix.cmxa slice.ml drive.ml -o $@

ref:
	python3 drive.py $(REPS) 2>/dev/null > ref.txt

data:
	python3 mkdata.py

clean:
	rm -f run.js drivehs driveml *.hi *.o *.cmi *.cmx sizes.json times.json out.*.txt

.PHONY: all sizes build ref data clean

~/tmp/%.pdf : %.py
	echo "making $@"
	a2ps                      \
  --file-align=virtual       \
	--line-numbers=1            \
	--pro=color                  \
	--pretty=python               \
	--chars-per-line=80            \
	--left-title=""                 \
	--borders=no                     \
  --right-footer='page %s. of %s#' \
	--portrait                         \
	--columns 2                         \
	-M letter                            \
	-o - $^ | ps2pdf - $@
	open $@

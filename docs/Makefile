%.pdf : %.md
	@pandoc "$^" \
	    -f gfm \
			--toc \
			-V toc-title:"$^" \
  	  -V geometry:margin=1cm \
			-V fontsize=8pt \
			-V 'fontfamily:dejavu' \
			--highlight-style tango \
			-o "$@"

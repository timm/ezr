-include ../Makefile
R=20

silly:
	cp ../etc/tree.jpeg ../etc/icons8-globe-24.png ../etc/art1.png ~/tmp
	python3 -m pdoc \
	        --footer-text "(c)2024, Tim Menzies <timm@ieee.org>" \
					--favicon icons8-globe-24.png \
	        --logo tree.jpeg  --no-search  -o ~/tmp trees.py
	rm ~/tmp/index.html


bores=~/gits/txt/aa24/data/Process/small

X=-p10000-d27-o4-dataset1

bore:
	$(MAKE) -j 8 -B  \
	  ../out/xomo_flight.out ../out/xomo_ground.out ../out/xomo_osp.out ../out/xomo_osp2.out \
		../out/pom3a.out ../out/pom3b.out ../out/pom3c.out ../out/pom3d.out  

flashes=~/gits/txt/aa24/data/flash

flash:
	$(MAKE) -j 8 -B ../out/SS-A.out ../out/SS-B.out ../out/SS-C.out ../out/SS-D.out ../out/SS-E.out  \
					../out/SS-F.out ../out/SS-G.out ../out/SS-H.out ../out/SS-I.out ../out/SS-J.out  \
					../out/SS-K.out ../out/SS-L.out ../out/SS-M.out ../out/SS-N.out ../out/SS-O.out 

usuals=../data
usual:
	$(MAKE) -j 8 -B ../out/auto93.out   ../out/healthCloseIsses12mths0001-hard.out     \
					../out/china.out   ../out/healthCloseIsses12mths0011-easy.out \
				../out/coc1000.out ../out/nasa93dem.out  ../out/pom.out


one:
	echo $(bores)

../out/%.out : $(usuals)/%.csv
	echo "-- $@"; python3 eg.py -R $R -f $^ -t smoy | tee $@

../out/%.out : $(bores)/%.csv
	echo $^
	echo "-- $@"; python3 eg.py -R $R -f $^ -t smoy | tee $@

../out/%.out : $(flashes)/%.csv
	echo "-- $@"; python3 eg.py -R $R -f $^ -t smoy | tee $@


../%.html : %.adoc
	asciidoctor  -o $@ $^

../docs/%.html : %.py
	pycco -d ../docs $^

../docs/%.pdf : %.md
	echo "# $^ ==> $@"
	pandoc "$^" \
	    -f gfm \
		-V toc-title:"$^" \
  	  -V geometry:margin=1cm \
		-V fontsize=7pt \
		-V 'fontfamily:dejavu' \
		--highlight-style tango \
		-o "$@"


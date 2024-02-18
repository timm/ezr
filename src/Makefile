-include ../Makefile
R=20

bores=~/gits/txt/aa24/data/Process

bore:
	$(MAKE) ../var/pom3a.out ../var/pom3b.out ../var/pom3c.out ../var/pom3d.out \
				  ../var/xomo_flight.out ../var/xomo_ground.out ../var/xomo_osp.out ../var/xomo_osp2.out

flashes=~/gits/txt/aa24/data/flash

flash:
	$(MAKE) ../var/SS-A.out ../var/SS-B.out ../var/SS-C.out ../var/SS-D.out ../var/SS-E.out  \
					../var/SS-F.out ../var/SS-G.out ../var/SS-H.out ../var/SS-I.out ../var/SS-J.out  \
					../var/SS-K.out ../var/SS-L.out ../var/SS-M.out ../var/SS-N.out ../var/SS-O.out 

usuals=../data
usual:
	$(MAKE) ../var/auto93.out   ../var/healthCloseIsses12mths0001-hard.out     \
					../var/china.out   ../var/healthCloseIsses12mths0011-easy.out \
				../var/coc1000.out ../var/nasa93dem.out ../var/nasa93demNums ../var/pom.out


one:
	echo $(bores)

../var/%.out : $(usuals)/%.csv
	echo "-- $@"; python3 eg.py -R $R -f $^ -t smoy | tee $@

../var/%.out : $(bores)/%.csv
	echo "-- $@"; python3 eg.py -R $R -f $^ -t smoy | tee $@

../var/%.out : $(flashes)/%.csv
	echo "-- $@"; python3 eg.py -R $R -f $^ -t smoy | tee $@

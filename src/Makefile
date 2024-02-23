-include ../Makefile
R=20

bores=~/gits/txt/aa24/data/Process/large
B=-p10000-d9-o3-dataset1
X=-p10000-d27-o4-dataset1

bore:
	$(MAKE) ../out/POM3A$B.out ../out/POM3B$B.out ../out/POM3C$B.out ../out/POM3D$B.out \
				  ../out/xomo_flight$X.out ../out/xomo_ground$X.out ../out/xomo_osp$X.out ../out/xomoo2$X.out

flashes=~/gits/txt/aa24/data/flash

flash:
	$(MAKE) ../out/SS-A.out ../out/SS-B.out ../out/SS-C.out ../out/SS-D.out ../out/SS-E.out  \
					../out/SS-F.out ../out/SS-G.out ../out/SS-H.out ../out/SS-I.out ../out/SS-J.out  \
					../out/SS-K.out ../out/SS-L.out ../out/SS-M.out ../out/SS-N.out ../out/SS-O.out 

usuals=../data
usual:
	$(MAKE) ../out/auto93.out   ../out/healthCloseIsses12mths0001-hard.out     \
					../out/china.out   ../out/healthCloseIsses12mths0011-easy.out \
				../out/coc1000.out ../out/nasa93dem.out ../out/nasa93demNums ../out/pom.out


one:
	echo $(bores)

../out/%.out : $(usuals)/%.csv
	echo "-- $@"; python3 eg.py -R $R -f $^ -t smoy | tee $@

../out/%.out : $(bores)/%.csv
	echo $^
	echo "-- $@"; python3 eg.py -R $R -f $^ -t smoy | tee $@

../out/%.out : $(flashes)/%.csv
	echo "-- $@"; python3 eg.py -R $R -f $^ -t smoy | tee $@

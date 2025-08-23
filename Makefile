SHELL     := bash
MAKEFLAGS += --warn-undefined-variables
.SILENT:

LOUD = \033[1;34m#
HIGH = \033[1;33m#
SOFT = \033[0m#

Top=$(shell git rev-parse --show-toplevel)

help:  ## show help
	gawk -f $(Top)/sh/help.awk $(MAKEFILE_LIST) 

pull: ## update from main
	git pull

../docs/%.html : %.py
	echo pdoc -o ../docs --logo ezr.png $^ 
	pdoc      -o ../docs --logo ezr.png $^ 

#--------------------------------------------------------------------------------
stats:
	gawk -F, '\
	 FNR==1  { x=y=0; for(i=1;i<=NF;i++) $$i ~ /[+!\-]$$/ ? y++ : x++ } \
 	 ENDFILE { print(FNR, x, y, gensub(".*/", "", "g", FILENAME) ) }'    \
	 $(Top)/../moot/optimize/*/*.csv                                      \
	 | sort -t, -k1,1n -k2,2n -k3,3n | column -t

~/tmp/overall.log: 
	$(MAKE) todo=overall files="$(Top)/../moot/optimize/*/*.csv" worker | tee $@; \
	gawk -f $(Top)/sh/bang.awk $@ | column -s \& -t

# 5000 +- 4000;  6 += 10; 3 += 1; n=118 lines

~/tmp/treeSelect.log: 
	$(MAKE) todo=treeSelect files="$(Top)/../moot/optimize/config/*.csv" worker | tee $@; \
	gawk -f $(Top)/sh/likely.awk Max=24 $@ 

# 46 56 63 76 88               ---- *    -----     build10
# 34 47 64 76 86           -----|    *   ----      check10
# 43 63 75 85 95              -------   *   ----   check20
# 49 74 77 88 95                ---------*   ---   build20
# 44 70 83 91 95              ----------   *  --   check30
# 63 77 85 90 96                |   ------  *---   build30
# 53 76 86 92 96                |---------  * --   check40
# 60 83 87 93 97                |  ---------* ---  build40
# 54 89 92 95 98                |-------------*--  check80
# 55 85 93 96 98                | ----------- *--  check120
# 66 91 93 96 98                |    ---------*--  build80
# 68 92 96 97 98                |     ---------*-  build120
#
~/tmp/xploit.log: 
	$(MAKE) todo=xploit files="$(Top)/../moot/optimize/*/*.csv" worker | tee $@; \
	gawk -f $(Top)/sh/likely.awk Max=10 $@ 

# gawk -f etc/likely.awk Max=8 ~/tmp/xploit.log
# 25 47 58 65 88        --------|  * ---------     10
# 33 57 70 77 96          ---------    * -------   20
# 36 66 80 87 98           -----------    * -----  40
# 44 79 88 94 98              -------------  * --  80
#

~/tmp/likelyAll.log: 
	$(MAKE) todo=likely files="$(Top)/../moot/optimize/*/*.csv" worker | tee $@; \
	gawk -f $(Top)/sh/likely.awk $@ 

# 33 61 70 80 98          -----------  *  -------  xplor
# 33 61 71 82 97          -----------  *   ------  adapt
# 36 62 71 83 97           ----------  *   ------  rands
# 38 62 72 83 96            ---------  *   -----   klass
# 35 62 74 81 93           ----------   * -----    bore
# 36 66 75 85 96           -----------  *   ----   near
# 37 63 78 83 98            ---------    * ------  xploit

~/tmp/likelySome.log: 
	$(MAKE) todo=likely files="$(Top)/../moot/optimize/config/SS-[A-J]*.csv" worker | tee $@ ; \
	gawk -f $(Top)/sh/likely.awk $@ 

worker:
	@mkdir -p ~/tmp
	time ls -r $(files) \
	  | xargs -P 32 -n 1 -I{} sh -c 'python3 -B -m ezr -f "{}" --$(todo)'

# cat ~/tmp/likelyAll.log
# 1    near  22   klass  13   bore  8    xploit  18   xplor  21   adapt  30   rands  14   |  10000   5     3  Health-ClosedIssues0007.csv
# 2    near  19   klass  17   bore  18   xploit  19   xplor  21   adapt  20   rands  16   |  10000   5     3  Health-ClosedIssues0010.csv
# 3    near  36   klass  51   bore  24   xploit  20   xplor  10   adapt  14   rands  34   |  1460    77    4  home_data_for_ml_course.csv
# 4    near  3    klass  6    bore  5    xploit  24   xplor  33   adapt  20   rands  16   |  1121    14    2  accessories.csv
# 5    near  35   klass  32   bore  27   xploit  25   xplor  27   adapt  26   rands  35   |  10000   5     3  Health-ClosedIssues0004.csv
# 6    near  28   klass  26   bore  23   xploit  27   xplor  31   adapt  31   rands  29   |  10000   5     3  Health-ClosedPRs0009.csv
# 7    near  26   klass  26   bore  28   xploit  29   xplor  30   adapt  26   rands  27   |  10000   5     3  Health-Commits0004.csv
# 8    near  36   klass  32   bore  35   xploit  29   xplor  28   adapt  32   rands  30   |  10000   5     3  Health-ClosedIssues0009.csv
# 9    near  33   klass  29   bore  31   xploit  30   xplor  37   adapt  28   rands  30   |  10000   5     3  Health-ClosedPRs0010.csv
# 10   near  73   klass  61   bore  35   xploit  36   xplor  44   adapt  44   rands  55   |  21759   35    3  Data_COVID19_Indonesia.csv
# 11   near  35   klass  34   bore  34   xploit  37   xplor  41   adapt  36   rands  38   |  10000   5     3  Health-Commits0002.csv
# 12   near  44   klass  38   bore  41   xploit  37   xplor  44   adapt  37   rands  63   |  10000   5     3  Health-ClosedPRs0008.csv
# 13   near  47   klass  47   bore  53   xploit  45   xplor  34   adapt  33   rands  36   |  317     7     4  A2C_CartPole.csv
# 14   near  39   klass  40   bore  43   xploit  47   xplor  37   adapt  33   rands  41   |  53662   17    2  SS-N.csv
# 15   near  44   klass  45   bore  41   xploit  47   xplor  41   adapt  42   rands  43   |  10000   5     3  Health-ClosedIssues0001.csv
# 16   near  63   klass  61   bore  45   xploit  47   xplor  27   adapt  35   rands  56   |  20000   31    5  Loan.csv
# 17   near  57   klass  52   bore  40   xploit  49   xplor  59   adapt  56   rands  46   |  10000   5     3  Health-Commits0003.csv
# 18   near  45   klass  50   bore  50   xploit  50   xplor  42   adapt  41   rands  54   |  10000   5     3  Health-Commits0008.csv
# 19   near  5    klass  29   bore  0    xploit  50   xplor  30   adapt  49   rands  5    |  913     20    2  dress-up.csv
# 20   near  85   klass  61   bore  42   xploit  50   xplor  22   adapt  37   rands  49   |  205     38    5  Car_price_cleaned.csv
# 21   near  71   klass  62   bore  43   xploit  51   xplor  35   adapt  37   rands  56   |  17737   55    2  all_players.csv
# 22   near  52   klass  49   bore  56   xploit  53   xplor  60   adapt  58   rands  49   |  65536   16    2  SS-W.csv
# 23   near  65   klass  39   bore  39   xploit  54   xplor  39   adapt  34   rands  65   |  10000   5     3  Health-ClosedPRs0006.csv
# 24   near  58   klass  57   bore  56   xploit  55   xplor  51   adapt  51   rands  51   |  20000   9     3  pom3c.csv
# 25   near  59   klass  53   bore  53   xploit  56   xplor  54   adapt  54   rands  57   |  10000   5     3  Health-Commits0006.csv
# 26   near  71   klass  71   bore  74   xploit  57   xplor  48   adapt  48   rands  63   |  2205    31    8  Marketing_Analytics.csv
# 27   near  73   klass  54   bore  39   xploit  60   xplor  67   adapt  78   rands  52   |  247     22    2  wallpaper.csv
# 28   near  77   klass  89   bore  73   xploit  60   xplor  75   adapt  66   rands  84   |  196     3     2  SS-F.csv
# 29   near  58   klass  58   bore  59   xploit  61   xplor  56   adapt  57   rands  48   |  10000   5     3  Health-ClosedIssues0003.csv
# 30   near  60   klass  54   bore  55   xploit  61   xplor  62   adapt  65   rands  53   |  86058   11    2  SS-X.csv
# 31   near  75   klass  86   bore  74   xploit  61   xplor  68   adapt  71   rands  84   |  196     3     2  SS-G.csv
# 32   near  88   klass  83   bore  74   xploit  62   xplor  65   adapt  58   rands  80   |  2938    20    2  Life_Expectancy_Data.csv
# 33   near  62   klass  60   bore  62   xploit  63   xplor  62   adapt  61   rands  62   |  10000   5     3  Health-ClosedIssues0005.csv
# 34   near  78   klass  78   bore  55   xploit  64   xplor  50   adapt  47   rands  68   |  1470    32    3  WA_Fn-UseC_-HR-Employee-Attrition.csv
# 35   near  68   klass  63   bore  64   xploit  65   xplor  63   adapt  67   rands  62   |  10000   5     3  Health-Commits0010.csv
# 36   near  65   klass  62   bore  63   xploit  66   xplor  62   adapt  61   rands  60   |  1599    10    2  Wine_quality.csv
# 37   near  65   klass  67   bore  64   xploit  67   xplor  67   adapt  68   rands  66   |  10127   19    4  BankChurners.csv
# 38   near  67   klass  70   bore  64   xploit  67   xplor  70   adapt  69   rands  60   |  500     9     3  pom3c_old.csv
# 39   near  59   klass  72   bore  68   xploit  68   xplor  60   adapt  62   rands  77   |  756     3     2  SS-E.csv
# 40   near  72   klass  75   bore  74   xploit  70   xplor  72   adapt  73   rands  67   |  10000   5     3  Health-Commits0000.csv
# 41   near  67   klass  63   bore  64   xploit  71   xplor  65   adapt  70   rands  71   |  1000    20    5  coc1000.csv
# 42   near  75   klass  72   bore  66   xploit  71   xplor  72   adapt  70   rands  63   |  20000   9     3  pom3b.csv
# 43   near  66   klass  67   bore  64   xploit  72   xplor  69   adapt  85   rands  84   |  93      22    3  nasa93dem.csv
# 44   near  73   klass  71   bore  74   xploit  72   xplor  65   adapt  69   rands  72   |  10000   5     3  Health-ClosedIssues0008.csv
# 45   near  77   klass  77   bore  81   xploit  73   xplor  76   adapt  74   rands  70   |  10000   5     3  Health-ClosedIssues0000.csv
# 46   near  78   klass  71   bore  68   xploit  74   xplor  72   adapt  75   rands  70   |  20000   9     3  pom3a.csv
# 47   near  82   klass  78   bore  66   xploit  74   xplor  70   adapt  71   rands  80   |  1512    3     2  SS-C.csv
# 48   near  89   klass  81   bore  60   xploit  74   xplor  63   adapt  87   rands  79   |  10000   5     3  Health-Commits0007.csv
# 49   near  92   klass  91   bore  77   xploit  75   xplor  88   adapt  91   rands  71   |  10000   5     3  Health-ClosedPRs0004.csv
# 50   near  73   klass  66   bore  70   xploit  76   xplor  68   adapt  67   rands  67   |  4653    38    1  SQL_AllMeasurements.csv
# 51   near  82   klass  71   bore  70   xploit  76   xplor  72   adapt  74   rands  68   |  10000   25    4  xomo_ground.csv
# 52   near  94   klass  94   bore  52   xploit  76   xplor  100  adapt  100  rands  100  |  649     33    1  student_dropout.csv
# 53   near  65   klass  73   bore  79   xploit  77   xplor  78   adapt  71   rands  66   |  223     10    3  A2C_Acrobot.csv
# 54   near  83   klass  76   bore  81   xploit  77   xplor  78   adapt  84   rands  74   |  10000   25    4  xomo_flight.csv
# 55   near  67   klass  61   bore  85   xploit  78   xplor  74   adapt  65   rands  71   |  10000   1044  3  FFM-1000-200-0.50-SAT-1.csv
# 56   near  70   klass  80   bore  80   xploit  78   xplor  57   adapt  62   rands  83   |  196     3     2  SS-D.csv
# 57   near  77   klass  79   bore  76   xploit  78   xplor  76   adapt  77   rands  79   |  10000   5     3  Health-ClosedIssues0006.csv
# 58   near  82   klass  72   bore  76   xploit  78   xplor  77   adapt  71   rands  69   |  10000   25    4  xomo_osp2.csv
# 59   near  88   klass  78   bore  87   xploit  78   xplor  90   adapt  78   rands  73   |  500     9     3  pom3a_old.csv
# 60   near  65   klass  65   bore  77   xploit  79   xplor  79   adapt  70   rands  62   |  100000  124   3  Scrum100k.csv
# 61   near  76   klass  79   bore  78   xploit  79   xplor  78   adapt  80   rands  74   |  10000   5     3  Health-Commits0009.csv
# 62   near  78   klass  79   bore  80   xploit  79   xplor  83   adapt  80   rands  79   |  10000   5     3  Health-ClosedIssues0002.csv
# 63   near  79   klass  78   bore  50   xploit  79   xplor  80   adapt  81   rands  78   |  3008    14    2  SS-R.csv
# 64   near  92   klass  89   bore  88   xploit  79   xplor  56   adapt  66   rands  71   |  1080    5     2  SS-I.csv
# 65   near  85   klass  80   bore  73   xploit  80   xplor  69   adapt  73   rands  77   |  972     11    2  SS-O.csv
# 66   near  69   klass  61   bore  80   xploit  81   xplor  62   adapt  68   rands  68   |  10000   517   3  FM-500-100-0.25-SAT-1.csv
# 67   near  82   klass  86   bore  78   xploit  81   xplor  68   adapt  81   rands  74   |  398     4     3  auto93.csv
# 68   near  78   klass  68   bore  79   xploit  82   xplor  84   adapt  84   rands  69   |  10000   128   3  FFM-125-25-0.50-SAT-1.csv
# 69   near  88   klass  67   bore  75   xploit  82   xplor  80   adapt  70   rands  85   |  10000   5     3  Health-Commits0005.csv
# 70   near  89   klass  88   bore  75   xploit  82   xplor  69   adapt  76   rands  83   |  1343    3     2  SS-A.csv
# 71   near  93   klass  80   bore  73   xploit  82   xplor  79   adapt  87   rands  77   |  206     3     2  SS-B.csv
# 72   near  71   klass  63   bore  70   xploit  83   xplor  48   adapt  50   rands  72   |  2880    6     2  SS-K.csv
# 73   near  72   klass  65   bore  84   xploit  83   xplor  80   adapt  75   rands  67   |  10000   88    3  billing10k.csv
# 74   near  72   klass  70   bore  78   xploit  83   xplor  85   adapt  90   rands  69   |  1000    124   3  Scrum1k.csv
# 75   near  72   klass  70   bore  81   xploit  83   xplor  70   adapt  66   rands  68   |  10000   256   3  FFM-250-50-0.50-SAT-1.csv
# 76   near  81   klass  82   bore  83   xploit  83   xplor  81   adapt  82   rands  87   |  500     9     3  pom3d.csv
# 77   near  82   klass  84   bore  82   xploit  83   xplor  76   adapt  81   rands  75   |  500     9     3  pom3b_old.csv
# 78   near  83   klass  75   bore  74   xploit  83   xplor  85   adapt  74   rands  70   |  10000   25    4  xomo_osp.csv
# 79   near  87   klass  91   bore  93   xploit  83   xplor  70   adapt  62   rands  85   |  1023    11    2  SS-L.csv
# 80   near  70   klass  63   bore  78   xploit  84   xplor  61   adapt  67   rands  57   |  10000   513   3  FM-500-100-0.50-SAT-1.csv
# 81   near  79   klass  83   bore  64   xploit  84   xplor  85   adapt  86   rands  74   |  6840    16    2  SS-V.csv
# 82   near  96   klass  97   bore  75   xploit  84   xplor  95   adapt  97   rands  94   |  2736    13    3  SS-Q.csv
# 83   near  65   klass  66   bore  82   xploit  85   xplor  70   adapt  68   rands  63   |  10000   511   3  FM-500-100-0.75-SAT-1.csv
# 84   near  66   klass  66   bore  81   xploit  85   xplor  88   adapt  83   rands  65   |  10000   124   3  Scrum10k.csv
# 85   near  70   klass  71   bore  82   xploit  86   xplor  66   adapt  68   rands  61   |  10000   510   3  FFM-500-100-0.50-SAT-1.csv
# 86   near  90   klass  83   bore  87   xploit  86   xplor  76   adapt  51   rands  90   |  3840    6     2  SS-J.csv
# 87   near  94   klass  93   bore  79   xploit  87   xplor  90   adapt  92   rands  95   |  5184    12    2  SS-T.csv
# 88   near  94   klass  93   bore  82   xploit  87   xplor  92   adapt  88   rands  95   |  3840    6     2  SS-S.csv
# 89   near  73   klass  62   bore  86   xploit  89   xplor  77   adapt  73   rands  74   |  10000   511   3  FM-500-100-1.00-SAT-1.csv
# 90   near  100  klass  81   bore  82   xploit  90   xplor  80   adapt  83   rands  85   |  350     20    1  socks.csv
# 91   near  85   klass  84   bore  90   xploit  90   xplor  90   adapt  93   rands  90   |  81      26    1  player_statistics_cleaned_final.csv
# 92   near  96   klass  96   bore  94   xploit  93   xplor  88   adapt  88   rands  98   |  2880    6     1  wc-6d-c1-obj1.csv
# 93   near  94   klass  93   bore  93   xploit  94   xplor  88   adapt  90   rands  93   |  2866    6     1  sol-6d-c2-obj1.csv
# 94   near  85   klass  93   bore  70   xploit  96   xplor  79   adapt  81   rands  85   |  259     4     2  SS-H.csv
# 95   near  93   klass  92   bore  78   xploit  96   xplor  86   adapt  90   rands  93   |  4608    21    2  SS-U.csv
# 96   near  96   klass  96   bore  96   xploit  96   xplor  96   adapt  96   rands  96   |  10000   5     3  Health-Commits0001.csv
# 97   near  97   klass  98   bore  90   xploit  97   xplor  98   adapt  96   rands  97   |  7043    19    2  WA_Fn-UseC_-Telco-Customer-Churn.csv
# 98   near  89   klass  96   bore  97   xploit  98   xplor  98   adapt  96   rands  85   |  1023    11    2  SS-P.csv
# 99   near  96   klass  98   bore  98   xploit  98   xplor  97   adapt  99   rands  94   |  3456    14    1  HSMGP_num.csv
# 100  near  96   klass  98   bore  98   xploit  98   xplor  98   adapt  99   rands  98   |  196     3     1  wc+wc-3d-c4-obj1.csv
# 101  near  97   klass  100  bore  92   xploit  98   xplor  99   adapt  97   rands  100  |  10000   5     3  Health-ClosedPRs0002.csv
# 102  near  97   klass  98   bore  98   xploit  98   xplor  99   adapt  98   rands  98   |  196     3     1  wc+rs-3d-c4-obj1.csv
# 103  near  97   klass  99   bore  87   xploit  98   xplor  98   adapt  99   rands  98   |  864     17    3  SS-M.csv
# 104  near  97   klass  99   bore  97   xploit  98   xplor  97   adapt  94   rands  99   |  3840    6     1  rs-6d-c3_obj1.csv
# 105  near  98   klass  98   bore  98   xploit  98   xplor  98   adapt  98   rands  98   |  10000   5     3  Health-ClosedPRs0003.csv
# 106  near  95   klass  94   bore  98   xploit  99   xplor  99   adapt  99   rands  94   |  192     9     1  Apache_AllMeasurements.csv
# 107  near  97   klass  96   bore  91   xploit  99   xplor  98   adapt  99   rands  96   |  1152    16    1  X264_AllMeasurements.csv
# 108  near  98   klass  98   bore  94   xploit  99   xplor  99   adapt  99   rands  98   |  196     3     1  wc+sol-3d-c4-obj1.csv
# 109  near  99   klass  99   bore  99   xploit  99   xplor  99   adapt  99   rands  99   |  3840    6     1  rs-6d-c3_obj2.csv
# 110  near  100  klass  100  bore  100  xploit  100  xplor  100  adapt  100  rands  100  |  10000   5     2  Health-ClosedPRs0000.csv
# 111  near  100  klass  100  bore  100  xploit  100  xplor  100  adapt  100  rands  100  |  10000   5     3  Health-ClosedPRs0005.csv
# 112  near  100  klass  100  bore  100  xploit  100  xplor  100  adapt  100  rands  100  |  10000   5     3  Health-ClosedPRs0011.csv
# 113  near  100  klass  100  bore  100  xploit  100  xplor  100  adapt  100  rands  100  |  25000   64    1  Medical_Data_and_Hospital_Readmissions.csv
# 114  near  100  klass  100  bore  100  xploit  100  xplor  100  adapt  100  rands  100  |  5160    9     1  dataset600.csv
# 115  near  100  klass  100  bore  100  xploit  100  xplor  96   adapt  100  rands  100  |  5160    9     1  dataset120.csv
# 116  near  100  klass  100  bore  92   xploit  100  xplor  100  adapt  100  rands  100  |  10000   5     3  Health-Commits0011.csv
# 117  near  100  klass  100  bore  93   xploit  100  xplor  100  adapt  100  rands  100  |  10000   5     3  Health-ClosedIssues0011.csv
# 118  near  100  klass  94   bore  94   xploit  100  xplor  100  adapt  94   rands  100  |  10000   5     3  Health-ClosedPRs0007.csv

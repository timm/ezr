f="2bSS-A.csv 2bSS-B.csv 2bSS-C.csv 2bSS-D.csv 2bSS-E.csv 2bSS-F.csv 2bSS-G.csv 2bSS-H.csv 2bSS-I.csv 2bSS-J.csv 2bSS-K.csv 2bSS-L.csv 2bSS-M.csv 2bSS-N.csv 2bSS-O.csv"
gnuplot << EOF
set terminal pngcairo
set output 'dtrends.png'
 set xlabel "bsample size"
set ylabel "normalized( d2h )"
plot \
"trends/bSS-A.csv" title "SS-A" with lines lw 1,\
"trends/bSS-B.csv" title "SS-B" with lines lw 1,\
"trends/bSS-C.csv" title "SS-C" with lines lw 1,\
"trends/bSS-D.csv" title "SS-D" with lines lw 1,\
"trends/bSS-E.csv" title "SS-E" with lines lw 8,\
"trends/bSS-F.csv" title "SS-F" with lines lw 1,\
"trends/bSS-G.csv" title "SS-G" with lines lw 1,\
"trends/bSS-H.csv" title "SS-H" with lines lw 1,\
"trends/bSS-I.csv" title "SS-I" with lines lw 1,\
"trends/bSS-J.csv" title "SS-J" with lines lw 8,\
"trends/bSS-K.csv" title "SS-K" with lines lw 8,\
"trends/bSS-L.csv" title "SS-L" with lines lw 1,\
"trends/bSS-M.csv" title "SS-M" with lines lw 1,\
"trends/bSS-N.csv" title "SS-N" with lines lw 1,\
"trends/bSS-O.csv" title "SS-O" with lines lw 1,\
"trends/bauto93.csv" title "auto93" with lines lw 8,\
"trends/bcoc1000.csv" title "coc1000" with lines lw 1,\
"trends/bhealthCloseIsses12mths0001-hard.csv" title "hard" with lines lw 1,\
"trends/bhealthCloseIsses12mths0011-easy.csv" title "easy" with lines lw 1,\
"trends/bchina.csv" title "china" with lines lw 1,\
"trends/bpom3a.csv" title "pom3a" with lines lw 1,\
"trends/bpom3b.csv" title "pom3b" with lines lw 1,\
"trends/bpom3c.csv" title "pom3c" with lines lw 1,\
"trends/bpom3d.csv" title "pom3d" with lines lw 1,\
"trends/bxomo_flight.csv" title "flight" with lines lw 1,\
"trends/bxomo_ground.csv" title "groud" with lines lw 8,\
"trends/bxomo_osp.csv" title "osp" with lines lw 1,\
"trends/bxomo_osp2.csv" title "osp2" with lines lw 1
EOF
gnuplot << EOF
set terminal pngcairo
set output 'randtrends.png'
 set xlabel "randsample size"
set ylabel "normalized( d2h )"
set logscale x
plot \
"trends/randSS-A.csv" title "SS-A" with lines lw 1,\
"trends/randSS-B.csv" title "SS-B" with lines lw 1,\
"trends/randSS-C.csv" title "SS-C" with lines lw 1,\
"trends/randSS-D.csv" title "SS-D" with lines lw 1,\
"trends/randSS-E.csv" title "SS-E" with lines lw 1,\
"trends/randSS-F.csv" title "SS-F" with lines lw 1,\
"trends/randSS-G.csv" title "SS-G" with lines lw 1,\
"trends/randSS-H.csv" title "SS-H" with lines lw 1,\
"trends/randSS-I.csv" title "SS-I" with lines lw 1,\
"trends/randSS-J.csv" title "SS-J" with lines lw 1,\
"trends/randSS-K.csv" title "SS-K" with lines lw 1,\
"trends/randSS-L.csv" title "SS-L" with lines lw 1,\
"trends/randSS-M.csv" title "SS-M" with lines lw 1,\
"trends/randSS-N.csv" title "SS-N" with lines lw 1,\
"trends/randSS-O.csv" title "SS-O" with lines lw 1,\
"trends/randauto93.csv" title "auto93" with lines lw 1,\
"trends/randcoc1000.csv" title "coc1000" with lines lw 1,\
"trends/randhealthCloseIsses12mths0001-hard.csv" title "hard" with lines lw 1,\
"trends/randhealthCloseIsses12mths0011-easy.csv" title "easy" with lines lw 1,\
"trends/randchina.csv" title "china" with lines lw 1,\
"trends/randpom3a.csv" title "pom3a" with lines lw 1,\
"trends/randpom3b.csv" title "pom3b" with lines lw 1,\
"trends/randpom3c.csv" title "pom3c" with lines lw 1,\
"trends/randpom3d.csv" title "pom3d" with lines lw 1,\
"trends/randxomo_flight.csv" title "flight" with lines lw 1,\
"trends/randxomo_ground.csv" title "groud" with lines lw 1,\
"trends/randxomo_osp.csv" title "osp" with lines lw 1,\
"trends/randxomo_osp2.csv" title "osp2" with lines lw 1
EOF
#2bauto93.csv
#2bchina.csv
#2bcoc1000.csv
#2bhealthCloseIsses12mths0001-hard.csv
#2bpom3a.csv
#2bpom3b.csv
#2bpom3c.csv
#2bpom3d.csv
#2bxomo_flight.csv
#2bxomo_ground.csv
#2bxomo_osp.csv
#2bxomo_osp2.csv
#2rrpSS-A.csv
#2rrpSS-B.csv
#2rrpSS-C.csv
#2rrpSS-D.csv
#2rrpSS-E.csv
#2rrpSS-F.csv
#2rrpSS-G.csv
#2rrpSS-H.csv
#2rrpSS-I.csv
#2rrpSS-J.csv
#2rrpSS-K.csv
#2rrpSS-L.csv
#2rrpSS-M.csv
#2rrpSS-N.csv
#2rrpSS-O.csv
#2rrpauto93.csv
#2rrpchina.csv
#2rrpcoc1000.csv
#2rrphealthCloseIsses12mths0001-hard.csv
#2rrphealthCloseIsses12mths0011-easy.csv
#2rrpnasa93dem.csv
#2rrppom3a.csv
#2rrppom3b.csv
#2rrppom3c.csv
#2rrppom3d.csv
#2rrpxomo_flight.csv
#2rrpxomo_ground.csv
#2rrpxomo_osp.csv
#2rrpxomo_osp2.csv
#bSS-A.csv
#bSS-B.csv
#bSS-C.csv
#bSS-D.csv
#bSS-E.csv
#bSS-F.csv
#bSS-G.csv
#bSS-H.csv
#bSS-I.csv
#bSS-J.csv
#bSS-K.csv
#bSS-L.csv
#bSS-M.csv
#bSS-N.csv
#bSS-O.csv
#baseSS-A.csv
#baseSS-B.csv
#baseSS-C.csv
#baseSS-D.csv
#baseSS-E.csv
#baseSS-F.csv
#baseSS-G.csv
#baseSS-H.csv
#baseSS-I.csv
#baseSS-J.csv
#baseSS-K.csv
#baseSS-L.csv
#baseSS-M.csv
#baseSS-N.csv
#baseSS-O.csv
#baseauto93.csv
#basechina.csv
#basecoc1000.csv
#basehealthCloseIsses12mths0001-hard.csv
#basehealthCloseIsses12mths0011-easy.csv
#basenasa93dem.csv
#basepom3a.csv
#basepom3b.csv
#basepom3c.csv
#basepom3d.csv
#basexomo_flight.csv
#basexomo_ground.csv
#basexomo_osp.csv
#basexomo_osp2.csv
#bauto93.csv
#bchina.csv
#bcoc1000.csv
#bhealthCloseIsses12mths0001-hard.csv
#bhealthCloseIsses12mths0011-easy.csv
#bnasa93dem.csv
#bonrSS-A.csv
#bonrSS-B.csv
#bonrSS-C.csv
#bonrSS-D.csv
#bonrSS-E.csv
#bonrSS-F.csv
#bonrSS-G.csv
#bonrSS-H.csv
#bonrSS-I.csv
#bonrSS-J.csv
#bonrSS-K.csv
#bonrSS-L.csv
#bonrSS-M.csv
#bonrSS-N.csv
#bonrSS-O.csv
#bonrauto93.csv
#bonrchina.csv
#bonrcoc1000.csv
#bonrhealthCloseIsses12mths0001-hard.csv
#bonrhealthCloseIsses12mths0011-easy.csv
#bonrnasa93dem.csv
#bonrpom3a.csv
#bonrpom3b.csv
#bonrpom3c.csv
#bonrpom3d.csv
#bonrxomo_flight.csv
#bonrxomo_ground.csv
#bonrxomo_osp.csv
#bonrxomo_osp2.csv
#bpom3a.csv
#bpom3b.csv
#bpom3c.csv
#bpom3d.csv
#bxomo_flight.csv
#bxomo_ground.csv
#bxomo_osp.csv
#bxomo_osp2.csv
#randSS-A.csv
#randSS-B.csv
#randSS-C.csv
#randSS-D.csv
#randSS-E.csv
#randSS-F.csv
#randSS-G.csv
#randSS-H.csv
#randSS-I.csv
#randSS-J.csv
#randSS-K.csv
#randSS-L.csv
#randSS-M.csv
#randSS-N.csv
#randSS-O.csv
#randauto93.csv
#randchina.csv
#randcoc1000.csv
#randhealthCloseIsses12mths0001-hard.csv
#randhealthCloseIsses12mths0011-easy.csv
#randnasa93dem.csv
#randpom3a.csv
#randpom3b.csv
#randpom3c.csv
#randpom3d.csv
#randxomo_flight.csv
#randxomo_ground.csv
#randxomo_osp.csv
#randxomo_osp2.csv
#rrpSS-A.csv
#rrpSS-B.csv
#rrpSS-C.csv
#rrpSS-D.csv
#rrpSS-E.csv
#rrpSS-F.csv
#rrpSS-G.csv
#rrpSS-H.csv
#rrpSS-I.csv
#rrpSS-J.csv
#rrpSS-K.csv
#rrpSS-L.csv
#rrpSS-M.csv
#rrpSS-N.csv
#rrpSS-O.csv
#rrpauto93.csv
#rrpchina.csv
#rrpcoc1000.csv
#rrphealthCloseIsses12mths0001-hard.csv
#rrphealthCloseIsses12mths0011-easy.csv
#rrpnasa93dem.csv
#rrppom3a.csv
#rrppom3b.csv
#rrppom3c.csv
#rrppom3d.csv
#rrpxomo_flight.csv
#rrpxomo_ground.csv
#rrpxomo_osp.csv
#rrpxomo_osp2.csv

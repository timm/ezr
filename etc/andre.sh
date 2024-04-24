D="/Users/timm/gits/andre/ez/out/SNEAK"
for f in $D/*.out
do  
  echo ""
  tac $f | gawk -F, 'NF>7' $f | sort -t, -n -k 1 -k 2 -k 3 | gawk '
done

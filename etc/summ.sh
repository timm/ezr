d=$HOME/tmp/clusters12

#k,n,stop,err

one() { 
gawk -F, '
$1==K && $2==Some && $3==Stop { a[++n]= $5}
END  { print("K, "   ,  K,
             ",Some,",  Some,
             ",Stop, ", Stop, per(a)) }

function per(a,  n,m) {
  n=asort(a)
  m = int(n/8)
  return sprintf(", %.2f, %.2f, %.2f, %.2f, %.2f, %.2f, %.2f",  
                  a[m],a[m*2],a[m*3],a[m*4],a[m*5],a[m*6],a[m*7]) }
       
function mu(a,     n,sum) {
  for(i in a) {
    n++
    sum += a[i] }
  return sum/n }

function sd(a,     m,n) {
  n=asort(a)
  m = int(n/10)
  print(m,n)
  return (a[m*9] - a[m])/ 2.56 } ' K=$1  Some=$2 Stop=$3 $d/* 
}
for K in 1 2 4; do
  for Stop in 12 24 48;  do
    one  $K 10000000000 $Stop
  done
done


#!/usr/bin/env ./auk
# X,Y for independent and depedndent columns
# Lo,Hi,Mu,N  for numerics
# B for bins
BEGIN { FS=","; BINS=4; srand(SEED); main()}

function main(data,   a,row) {
  row = -1
   while(getline>0)  {
     row++
     if (row>0) {split($0,rows[row],","); body(data,rows[row])
     } else     {split($0,a,",");         head(data,a)}
  }
   stop(data) }

function head(data,row,     c,z) { print(1000)
  start(data)
  for(c in row) {
    z = row[c]
    if(z !~ /X$/) {
      name[c] = z
      if (z~/^[A-Z]/) num0(data,c);
      if (z~/-$/)    yy[c]=0;
      if (z~/+$/)    yy[c]=1;
      if (!(c in yy)) xx[c] }}}

function start(data) {print(10)}
function stop(data,     k)  { 
  for(k in SYMTAB) if (k ~ /^[a-z]/) print "?? "k }
  
function body(data,row,    c,d) {
  for (c in nn) if (row[c] != "?") {row[c] += 0; num(data,c,row[c]) }}

function learn(data,row,    c,d) {
  d = chebyshev(data,row) 
  for(c in xx) { 
    br[c][bin(c,row[c])] += d }}

function chebyshev(data,row,     c,d) {
  d=0; for(c in yy) d = max(d, abs(norm(data,c,row[c]) - yy[c]));
  return d }

function bin(data,c,x) { return int(BINS*cdf(x,lo[c],hi[c],mu[c])) }

function cdf(x,a,b,c) {
  if (a < x && x <= c) return     (x-a)^2/((b-a)*(c-a));
  if (c < x && x <= b) return 1 - (b-x)^2/((b-a)*(b-c));
  return 0 }

function num0(data,c) { nn[c]=0; lo[c]=1E32; hi[c]=-1E32 }

function num(data,c,x,     d) {
  if (x > hi[c]) hi[c]=x;
  if (x < lo[c]) lo[c]=x;
  nn[c]  += 1;
  d      = x - mu[c];
  mu[c] += d/nn[c] }

function norm(data,c,x) { return (x-lo[c])/(hi[c]-lo[c] + 1E-32) }
function max(x,y)  { return x>y? x : y }
function abs(x)    { return x>0? x : -x }
function cat(a, s,k) { s=a[1]; for(k=2;k<=length(a);k++) s=s ", " a[k]; return "("s")" } 

# https://real-statistics.com/other-key-distributions/uniform-distribution/triangular-distribution/
function fdc(data,c,p) { return fdc1(p, lo[c],hi[c],mu[c]) }
function fdc1(p,a,b,c) {
  return (0 <= p && p < (c-a)/(b-a)) ? a+sqrt((b-a)*(c-a)*p) : b-sqrt((b-a)*(b-c)*(1-p)) }




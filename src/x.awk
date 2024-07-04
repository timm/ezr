#!/usr/bin/env gawk -f
# X,Y for independent and depedndent columns
# Lo,Hi,Mu,N  for numerics
# B for bins
BEGIN { FS=","; BINS=4; srand(SEED) }
      { if(NR==1) {
          split($0,a,","); head(a) 
        } else {
          split($0,D[NR-1],",")
          body(D[NR-1]) }}
END   { for(i in D) learn(D[i]) 
         for(c in B) {
           print ""
           for(x in B[c]) print(c,Name[c],x,B[c][x]) }
      }

function head(row,     z,c)  {
  for(c in row) {
    z = row[c]
    if(!(z ~ /X$/)) {
      Name[c] = z
      if (z~/^[A-Z]/) num0(c);
      if (z~/-$/)    Y[c]=0;
      if (z~/+$/)    Y[c]=1;
      if (!(c in Y)) X[c] }}}

function body(row,    c,d) {
  for (c in N) if (row[c] != "?") {row[c] += 0; num(c,row[c]) }}

function learn(row) {
  d = chebyshev(row) 
  for(c in X) { 
    B[c][bin(c,row[c])] += d }}

function chebyshev(row,     d) {
  d=0; for(c in Y) { d = max(d, abs(norm(c,row[c]) - Y[c]));}
  return d }

function bin(c,x) { return int(BINS*cdf(x,Lo[c],Hi[c],Mu[c])) }

function cdf(x,a,b,c) {
  if (a < x && x <= c) return     (x-a)^2/((b-a)*(c-a));
  if (c < x && x <= b) return 1 - (b-x)^2/((b-a)*(b-c));
  return 0 }

function num0(c) {
  N[c]=0; Lo[c]=1E32; Hi[c]=-1E32 }

function num(c,x,     d) {
  if (x > Hi[c]) Hi[c]=x;
  if (x < Lo[c]) Lo[c]=x;
  N[c]  += 1;
  d      = x - Mu[c];
  Mu[c] += d/N[c] }

function norm(c,x) { return (x-Lo[c])/(Hi[c]-Lo[c] + 1E-32) }
function max(i,j)  { return i>j? i : j }
function abs(i)    { return i>0? i : -i }
function cat(a, s) { s=a[1]; for(i=2;i<=length(a);i++) s=s ", " a[i]; return "("s")" } 

# https://real-statistics.com/other-key-distributions/uniform-distribution/triangular-distribution/
function fdc(c,p) { return fdc1(p, lo[c],hi[c],mu[c]) }
function fdc1(p,a,b,c) {
  return (0 <= p && p < (c-a)/(b-a)) ? a+sqrt((b-a)*(c-a)*p) : b-sqrt((b-a)*(b-c)*(1-p)) }




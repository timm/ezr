from math import *
def phi(x):
    #'Cumulative distribution function for the standard normal distribution'
    return (1.0 + erf(x / sqrt(2.0))) / 2.0


def pascal(n):
  line = [1]
  for k in range(n):
    line.append(line[k] * (n-k) / (k+1))
  return line

x=pascal(30)
s=sum(x)
y = [x1/s for x1 in x]
cdf = y[:]
for i in range(1,len(y)):
  cdf[i] = cdf[i-1] + y[i]
[print(i,"*" * int(x*50)) for i,x in enumerate(cdf)]

err=0
for x in range(-3,3):
  a   = phi(x)
  b   = cdf[x*5+3] 
  err+= a-b
  print(x,*[round(z,2) for z in [a,b,err]],sep="\t")

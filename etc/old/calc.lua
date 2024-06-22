-- Lib.lua : misc lua tools
-- (c) 2024 Tim Menzies, timm@ieee.org, BSD-2 license

-- ## calc
local calc={}

-- ## Cumulative Distribution Approximation
-- Lin, J.T. (1989). Approximating the Normal Tail Probability and its 
-- Inverse for use on a Pocket Calculator. Applied Statistics, 38, 69-70.
function calc.auc(x,mu,sigma,      cdf,z)
  cdf = function(z) return 1 - 0.5*2.718^(-0.717*z - 0.416*z*z) end
  z = (x - mu) / sd
  return z >= 0 and cdf(z) or 1 - cdf(-z) end

-- ## Distance
-- Chebyshev =  maximum of the distances in each coordinate.
function calc.chebyshev(row,cols,      c,tmp)
  c = 0
  for _,col in pairs(cols) do
    tmp = col:norm(row[col.pos]) -- normalize  0..1 
    c = math.max(c, math.abs(col.best - tmp)) end
  return c end -- so LARGER values are better

-- Minkowski Distance = sum of column distance^p, all ^(1/p) at end.
-- Euclidean distance is Minkowski with `p=2`.
function calc.minkowski(row1,row2,p,cols,     d,n)
  d,n = 0,0
  for _,col in pairs(cols) do
    n=n+1
    d = d + col:dist(row1[col.pos], row2[col.pos])^p end
  return (d/n)^(1/p) end

function calc.norms(mu,sd)
   return mu + sd* math.log(1/math.random())^.5*math.cos(math.pi*math.random()) end

-- ## Diversity
-- Standard deviation.
function calc.welford(x,  n,mu,m2,     d,sd)
  n,mu,m2 = n or 1, mu or 0, m2 or 0
  d  = x  - mu
  mu = mu + d/n
  m2 = m2 + d*(x- mu)
  sd = (m2/(n-1+1E-30))^0.5
  return mu,m2,sd end

-- Entropy
function calc.entropy(t,       N,e)
  N,e=0,0
  for _,v in pairs(t) do N = N + v end
  for _,v in pairs(t) do e = e - v/N * math.log(v/N,2)  end
  return e end 

-- ## Return
return calc

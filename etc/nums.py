from statistics import NormalDist
  
def lin_phi(z): return 1 - 0.5*2.718**(-0.717 * z - 0.416 * z * z)

def phi(x, mu=0, sigma=1, cdf=lin_phi):
  z = (x - mu) / sigma
  return cdf(z) if z>=0 else 1 - cdf(-z)

for x in range(-20,20):
  got =  phi(x, mu=0, sigma=6)
  want = NormalDist(mu=0, sigma=6).cdf(x)
  print(x, ', '.join([str(round(z,3)) for z in [got, want, 100*(abs(got-want))/want]]))

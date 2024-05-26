from statistics import NormalDist

def lin_phi(x, mu=0, sigma=1):
  z = (x - mu) / sigma
  cdf = lambda z: 1 - 0.5*2.718**(-0.717 * z - 0.416 * z * z)
  return cdf(z) if z>=0 else 1 - cdf(-z)

for x in range(-20,20):
  got =  lin_phi(x, mu=0, sigma=6)
  want = NormalDist(mu=0, sigma=6).cdf(x)
  print(x, ', '.join([str(round(z,3)) for z in [got, want, 100*(abs(got-want))/want]]))

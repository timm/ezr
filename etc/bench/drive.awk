BEGIN {
  P = 2; FEW = 128; START = 4; STOP = 50; SEED = 1
  while ((getline line < "data.csv") > 0) {
    if (line !~ /[^ \t\r]/) continue
    gsub(/[ \t\r]+$/, "", line)
    nf = split(line, f, ",")
    if (NCOL == 0) { NCOL = nf
      for (i = 1; i <= nf; i++) NAMES[i-1] = f[i]; continue }
    NROW++
    for (i = 1; i <= nf; i++)
      ROWS[NROW][i-1] = (f[i] ~ /^-?[0-9]+$/ || f[i] ~ /^-?[0-9]*\.[0-9]+$/) ? f[i]+0 : f[i] }
  Tbl("main")
  for (r = 1; r <= NROW; r++) addRow("main", r, 1)
  n = TB["main"]["n"]
  for (i = 1; i <= TB["main"]["nx"]; i++) xs = xs (i>1?", ":"") TB["main"]["xat"][i]
  for (i = 1; i <= TB["main"]["ny"]; i++) ys = ys (i>1?", ":"") "(" TB["main"]["yat"][i] ", " TB["main"]["yw"][i] ")"
  printf("n %d x [%s] y [%s]\n", n, xs, ys)
  printf("ymu %.6f\n", ymu("main", n))
  printf("ydist0 %.6f\n", ydist("main", 1))
  printf("xdist01 %.6f\n", xdist("main", 1, ROWS[2]))
  s = "div"
  for (at = 0; at < NCOL; at++) if (USED[at]) s = s sprintf(" %.6f", div(TB["main"]["cols"][at]))
  print s
  mids("main"); s = "mids"
  for (i = 1; i <= TB["main"]["nx"]; i++) { at = TB["main"]["xat"][i]
    s = s sprintf(" %d:%.6f", at, TB["main"]["mids"][at]) }
  print s
  while ((getline line < "gauss.txt") > 0) { gi++
    gn[gi] = split(line, gf, ",")
    for (i = 1; i <= gn[gi]; i++) G[gi][i] = gf[i] + 0 }
  for (i = 1; i <= gn[1]; i++) { A[i] = G[1][i]; B[i] = G[2][i]; C[i] = G[3][i] }
  printf("same %d %d\n", same(A, gn[1], B, gn[2], 0) ? 1 : 0, same(A, gn[1], C, gn[3], 0) ? 1 : 0)
  t0 = systime()
  for (rep = 1; rep <= R1; rep++)
    for (i = 1; i <= 120; i++) for (j = i+1; j <= 120; j++)
      s1 += xdist("main", i, ROWS[j])
  printf("W1 %.6f\n", s1)
  for (rep = 1; rep <= R2; rep++) { acquire(0)
    s2 += ydist("main", TB["best"]["rows"][1]) }
  printf("W2 %.6f\n", s2)
  printf("SEED %d\n", SEED)
  printf("secs %.3f\n", systime() - t0) > "/dev/stderr" }

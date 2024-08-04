{a[NR]=$NF}
END {
  n   = asort(a)
  ten = int(n/10)
  printf("%7.2f %7.2f %7.2f %7.2f %7.2f\n", a[ten], a[2*ten], a[5*ten], a[7*ten], a[9*ten])
}

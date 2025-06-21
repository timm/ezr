data && NF==a {print}

!data && /@attribute/ {
  a++
  gsub(/["']/,"")
  name[++a] = /(numeric|integer|real)/ ? toupper($2) : tolower($3)}

/@data/ {
  s=name[1]
  for(i=2,i<=a;i++) s= "," name[i]
  print(s);
  data=1
  next
}

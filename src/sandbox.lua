local the={bins=17, cohen=0.35}

function train(file)
  cols={y={}, x{}, nump={}, names=nil}
  for row in csv(file) do
    if not head then 
      head=row  
      for c,x in pairs(head) do
        if x:find"^[A-Z]" then col.nump[c] = true end
        if x:find"[!+-]$" then col.y[c] = x:find"-$" and 0 or 1 
                             else col.x[c] = true end end
    else 
       for c,x in pairs(row) do
         rows[1+#rows]= row

function head(cols,row)
  i = {xs=row, x={}, y={}, nump={}, has={}}
  for k,v in pairs(row) do
    i.has[k] = {}
    if v:find"^[A-Z]" then i.nump[k] = true end
    if v:find"[!+-]$" then i.y[k] = v:find"-$" and 0 or 1 
                      else i.x[k] = true end end
  return i end 

function body(data,row)
  for c,x in pairs(row) do
    if x ~= "!" then data.cols.has[c]
end

function push

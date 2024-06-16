l=require"lib"
d=require"data"
r=require"ranger"

local function ranger(     rows,i)
  rows = r.DATA.new():read(r.the.train):sort().rows
  for i=1,#rows,25 do
    print(i, l.o(rows[i])) end end

ranger()

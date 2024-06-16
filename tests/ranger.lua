l=require"lib"
d=require"data"
r=require"ranger"

local function ranger1(     rows,i)
  rows = r.DATA.new():read(r.the.train)
                     :sort().rows
  for i=1,#rows,25 do
    print(i, l.o(rows[i])) end end

-- ranger1()

local function ranger2(     rows,i)
  d = r.DATA.new()
  for row in l.csv(r.the.train) do
    d:add(row) 
     :arranges(row) end end

ranger2()

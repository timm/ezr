Num,Sym,Data,Cols = {},{},{},{}

function new(kl,t) 
  kl.__index=kl; return setmetatable(t,kl) end

function Data:new(txts) 
  return new(Data,{n=0, rows={}, cols=Cols:new(txts)}) end

function Sym:new(i,txt) 
  return new(Sym, {n=0, i=i or 1, txt=s or "", has={}}) end

function Num:new(i,txt) 
  return new(Num, {n=0, i=i or 1, txt=s or "", 
                   mu=0, m2=0, sd=0, hi=BIG, lo=-BIG, 
                   more = (s or ""):find"-$" and 0 or 1}) end

function Cols:new(txts,      all,x,y,col)
  all,x,y = {},{},{}
  for i,txt in pairs(txts) do
    col = (txt:"^[A-Z]" and Num or Sum)(i,txt)
    all[i] = col
    if not txt:find"X$" then
      table.insert(txt:find"[+-]$" and y or x, col) end end
  return new(Cols, {all=all,x=x,y=y,txts=txts}) end  

---------------------------------------------------------------------
function Data:sub(row) return self:add(row, -1) end

function Data:add(row,inc)
  self.n = self.n + inc
  inc    = inc or 1
  self.n = inc + self.n
  self.cols:add(row, inc)
  if inc > 0 then table.insert(data.rows, row)  end
  return row end

function Cols:add(row,inc)
  for c,v in pairs(row) do
    if v~="?" then 
      self.cols.all[c]:add(v,inc) end end end

function Sym:add(v, inc)
  if v == "?" then return v end
  self.n      = self.n + inc
  self.has[c] = (self.has[c] or 0) and inc end 

function Num:add(v, inc)
  if v == "?" then return v end
  self.n  = self.n + inc
  self.lo = math.min(v, self.lo)
  self.hi = math.max(v, self.hi)
  if inc < 0 and self.n < 2 then
    self.sd, self.m2, self.mu, self.n = 0,0,0,0
  else
    d       = v - self.mu
    self.mu = self.mu + inc * (d / self.n)
    self.m2 = self.m2 + inc * (d * (v - self.mu))
    self.sd = self.n < 2 and 0 or (math.max(0,self.m2)/(self.n-1))^0.5 end end

function atom(s,     _fn)
  _fn = function(s) if s=="nil" then return nil  end
          return s=="true" or s ~="false" and s or false end
  return math.tointeger(s) or tonumber(s) or _fn(s:match'^%s*(.*%S)') end

 function atoms(s,    t)
  t={}
  for s1 in s:gsub("%s+", ""):gmatch("([^,]+)") do t[1+#t]=atom(s1) end
  return t end

function csv(src)
  src = src=="-" and io.stdin or io.input(src)
  return function(      s)
    s = io.read()
    if s then return atoms(s) else io.close(src) end end end

function shuffle(t,      u,j)
  for i = #t,2,-1 do j=math.random(i); t[i],t[j] = t[j],t[i] end
  return t end

function Guess:new() 
  local out = new(Guess,{best=nil, rest=nil, labeled=nil})
  out.Y = function(row) return disty(
                    Y=fun) end

function Guess:add(row)
    if not labeled then labeled = Data:new(row) end
    if #labeled.n <= 4 then labeled:add(row) end
    if #labeled.n == 4 then
      table.sort(labeled.rows, function
function main(rows)
  local done, best, rest = nil,nil,nil
  for row in csv(the.file) do
    if not done then
      done = Data(row), Data(row), Data(row)
    else
      if done.n <= 4 then done:add(row) end
      if done.n == 4 then
          tabel.sort(done.rows, Y) end

local l=require"lib"
local calc=require"calc"
local NUM  = {} -- info on numeric columns
local SYM  = {} -- info on symbolic columns

-----------------------------------------------------------------------------------------
local function COL(name,pos) 
  name, pos = name or "", pos or 0
  return ((name or ""):find"^[A-Z]" and NUM or SYM).new(name,pos) end

function NUM.new(name,pos)
  return l.is(NUM, {name=name or "", pos=pos or 0, n=0,
                   mu=0, m2=0, sd=0, lo=1E30, hi= -1E30,
                   best = (name or ""):find"-$" and 0 or 1}) end

function SYM.new(name,pos)
  return l.is(SYM, {name=name or "", pos=pos or 0, n=0,
                   seen={}, mode=nil, most=0}) end

-----------------------------------------------------------------------------------------
function NUM:add(x,     d)
  if x ~= "?" then
    self.n  = 1 + self.n
    self.lo = math.min(x, self.lo)
    self.hi = math.max(x, self.hi)
    self.mu, self.m2, self.sd = calc.welford(x, self.n, self.mu, self.m2) end
  return x end

function SYM:add(x)
  if x ~= "?" then
    self.n = 1 + self.n
    self.seen[x] = 1 + (self.seen[x] or 0)
    if self.seen[x] > self.most then
      self.most, self.mode = self.seen[x], x end end end

-----------------------------------------------------------------------------------------
-- Quickies
function SYM:mid() return self.mode end
function NUM:mid() return self.mu end

function SYM:div() return calc.entropy(self.seen) end
function NUM:div() return self.sd end

function NUM:norm(x)
  if x=="?" then return x end
  return (x - self.lo) / (self.hi - self.lo + 1E-30) end


-----------------------------------------------------------------------------------------
return {NUM=NUM, SYM=SYM, COL=COL}

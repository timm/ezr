----------------------------------------------------------------------------------------
-- ## RULE

-- To generate rules, only exploring combinations of the.top scored bins
function DATA:rules(rows,     tmp,ys)
  ys,tmp = {},{}
  for _,row in pairs(rows) do ys[row.id] = 1 - self:chebyshev(row) end 
  for _,bins in pairs(powerset(self:topScoredBins(rows,ys))) do 
    if #bins > 1 -- ignore empty set
    then push(tmp, RULE.new(bins,ys,#rows)) end end
  return self:topScoredRules(tmp) end

-- Return just the.top number of bins. 
function DATA:topScoredBins(rows,ys,    out,binScoreDown)
  out,binScoreDown = {},function(a,b) return a.y.mu > b.y.mu end
  for k,bin in pairs(sort(self:bins(rows,ys), binScoreDown)) do
    if k > the.top then break else push(out,bin) end end 
  return out end

-- Return just the.top number of rukes. 
function DATA:topScoredRules(rules,   out, ruleRankDown)
  out,ruleRankDown  = {}, function(a,b) return a.rank < b.rank   end
  rules = sort(rules, ruleRankDown)
  for k,rule in pairs(rules) do
    if k > the.top then break else push(out,rule) end end
  return out end

-- Rules are  combinations of a set or rule ids, score by their mean chebyshev.
-- (a) The set  of rule ids for each attribute are OR-ed together.
-- (b) This is then AND-ed and (c) scored.
-- (d) If the rule selects for everything, it has no information. So we ignore it.
-- (e) Rule is ranked to minimize size and maximize score.
function RULE.new(bins,ys,tooMuch,    mu,n,nbins,tmp)
  mu,n,nbins,tmp = 0,0,0,{}
  for _,bin in pairs(bins) do 
    nbins = nbins + 1
    tmp[bin.y.pos] = OR(tmp[bin.y.pos] or {}, bin._rules) end -- (a)
  for k,_ in pairs( ANDS(tmp)) do n=n+1; mu = mu + (ys[k]  - mu)/n end  -- (b),(c)
  order=function(a,b) return a.y.pos==b.y.pos and (a.lo<b.lo) or (a.y.pos<b.y.pos) end
  if n < tooMuch then -- (d)
     return new(RULE,{rank= ((1 - n/tooMuch)^2 + (0 - nbins/the.top)^2 + (1 - mu)^2)^0.5, -- (e)
                      bins=sort(bins,order), score=mu, }) end end

-- To print a RULE, group its bins by position number, then sorted by `lo`.
function RULE:__tostring(     order,tmp)
  tmp ={}; for k,bin in pairs(self.bins) do tmp[k] = tostring(bin) end
  return "("..table.concat(tmp,"), (")..")" end

function RULE:selects(rows,     out)
  out={}; for _,row in pairs(rows) do if self:select(row) then push(out,row) end end
  return out end

function RULE:select(row,     tmp)
  tmp={}
  for _,bin in pairs(self.bins) do 
    tmp[bin.y.pos] = (tmp[bin.y.pos] or 0) + (bin:select(row) and 1 or 0)  end
  for _,n in pairs(tmp) do if n==0 then return false end end
  return true end
-- Sets
function ANDS(t,     out)
  for _,u in pairs(t) do if not out then out=u else out=AND(u,out) end end; return out end 

function AND(t,u,    out) 
  out={}; for k,_ in pairs(t) do if u[k] then out[k]=k end end; return out end 

function OR(t,u,     out) 
  out={}; for _,w in pairs{t,u} do for k,_ in pairs(w) do out[k]=k end end; return out end



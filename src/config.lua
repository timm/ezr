-- <!-- vim : set ts=4 sts=4 et : -->

-- first better of each option must be unique. upper and lower case is allowed.
return {
  bins  = 17,                       -- number of bins (before merging) 
  cohen = 0.35,                     -- less than cohen*sd means "same" 
  fmt   = "%g",                     -- format string for number 
  help  = false,                     -- show help    
  inf   = 1E32, 
  seed  = 1234567891,               -- random number seed   
  train = "../data/misc/auto93.csv" -- training data    
}

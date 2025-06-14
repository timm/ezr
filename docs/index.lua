local W=require"web"
local h1,h2,p,code=W.h1, W.h2,W.p, W.code

print[[<html><head><style>
@import url("https://fonts.googleapis.com/css2?family=Lato:wght@400;700&display=swap");
body{
  font-family:"Lato",sans-serif;
  xmargin:0 auto;           /* centres 800 px block */
  padding: 10px;
  max-width:600px;
  text-align:left;
  line-height:1.6;
  color:#333;
}
pre{
  font:12px/1.5 "Fira Code",monospace;
  background:#f5f5f5;   /* soft grey */
  color:#333;
  padding:.7em .9em;
  border:1px solid #ddd;
  border-radius:6px;
  box-shadow:0 1px 4px #0001;
  overflow:auto;
}
</style></head><body>]]

h1"asdas"

p[[asdasa
asdas
adas
]]

code"../src/adds.py"

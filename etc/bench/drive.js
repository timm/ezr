const fs = require("fs")
var SEED
var P = 2, Few = 128, Start = 4, Stop = 50, SEED = 1

const atom = s => /^-?\d+$/.test(s) ? +s : (/^-?\d*\.\d+$/.test(s) ? +s : s)
const lines = fs.readFileSync("data.csv","utf8").split("\n").filter(x=>x.trim()).map(l=>l.trim().split(","))
const src = [lines[0], ...lines.slice(1).map(r => r.map(atom))]
const t = Tbl(src), R = t.rows
const f6 = x => x.toFixed(6)
console.log(`n ${R.length} x [${t.x.join(", ")}] y [${Object.keys(t.y).map(a=>`(${a}, ${t.y[a]})`).join(", ")}]`)
console.log("ymu " + f6(ymu(t, R)))
console.log("ydist0 " + f6(ydist(t, R[0])))
console.log("xdist01 " + f6(xdist(t, R[0], R[1])))
console.log("div " + Object.keys(t.cols).map(a => f6(div(t.cols[a]))).join(" "))
console.log("mids " + Object.keys(mids(t)).map(a => `${a}:${typeof mids(t)[a]==="number"?f6(mids(t)[a]):mids(t)[a]}`).join(" "))
const g = fs.readFileSync("gauss.txt","utf8").trim().split("\n").map(l=>l.split(",").map(Number))
console.log(`same ${same(g[0],g[1])?1:0} ${same(g[0],g[2])?1:0}`)
const t0 = Date.now()
let s = 0
for (let rep = 0; rep < +process.argv[2]; rep++)
  for (let i = 0; i < 120; i++) for (let j = i+1; j < 120; j++) s += xdist(t, R[i], R[j])
console.log("W1 " + f6(s))
let s2 = 0
for (let rep = 0; rep < +process.argv[3]; rep++) s2 += ydist(t, acquire(t)[0])
console.log("W2 " + f6(s2))
console.log("SEED " + SEED)
process.stderr.write(`secs ${((Date.now()-t0)/1000).toFixed(3)}\n`)

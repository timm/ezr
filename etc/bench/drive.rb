include Math
$P, $Few, $Start, $Stop, $seed = 2, 128, 4, 50, 1
require_relative "slice"
def atom(s) = s =~ /\A-?\d+\z/ ? s.to_i : (s =~ /\A-?\d*\.\d+\z/ ? s.to_f : s)
L = File.readlines("data.csv").map(&:strip).reject(&:empty?).map { |l| l.split(",") }
t = Tbl([L[0]] + L[1..].map { |r| r.map { |x| atom(x) } })
R = t[:rows]
puts "n #{R.size} x [#{t[:x].join(', ')}] y [#{t[:y].map { |a, w| "(#{a}, #{w})" }.join(', ')}]"
puts "ymu %.6f" % ymu(t, R)
puts "ydist0 %.6f" % ydist(t, R[0])
puts "xdist01 %.6f" % xdist(t, R[0], R[1])
puts "div " + t[:cols].keys.sort.map { |a| "%.6f" % div(t[:cols][a]) }.join(" ")
puts "mids " + mids(t).keys.sort.map { |a| "#{a}:%.6f" % mids(t)[a].to_f }.join(" ")
g = File.readlines("gauss.txt").map { |l| l.split(",").map(&:to_f) }
puts "same #{same(g[0], g[1]) ? 1 : 0} #{same(g[0], g[2]) ? 1 : 0}"
t0 = Time.now
s = 0.0
ARGV[0].to_i.times { (0...120).each { |i| ((i+1)...120).each { |j| s += xdist(t, R[i], R[j]) } } }
puts "W1 %.6f" % s
s2 = 0.0
ARGV[1].to_i.times { s2 += ydist(t, acquire(t)[0]) }
puts "W2 %.6f" % s2
puts "SEED #{$seed}"
STDERR.puts "secs %.3f" % (Time.now - t0)

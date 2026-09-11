use Time::HiRes qw(time);
our ($P, $Few, $Start, $Stop, $SEED) = (2, 128, 4, 50, 1);
require "./slice.pl";
open(my $fh, "<", "data.csv") or die;
my @raw; while (<$fh>) { s/\s+$//; next unless /\S/; push @raw, [split /,/] }
my $src = [$raw[0], map { [map { /^-?\d+$/ || /^-?\d*\.\d+$/ ? $_+0 : $_ } @$_] } @raw[1..$#raw]];
my $t = Tbl($src); my $R = $t->{rows};
printf("n %d x [%s] y [%s]\n", scalar @$R, join(", ", @{$t->{x}}),
       join(", ", map { "($_->[0], $_->[1])" } @{$t->{y}}));
printf("ymu %.6f\n", ymu($t, $R));
printf("ydist0 %.6f\n", ydist($t, $R->[0]));
printf("xdist01 %.6f\n", xdist($t, $R->[0], $R->[1]));
print "div ".join(" ", map { sprintf("%.6f", div($t->{cols}{$_})) } sort { $a <=> $b } keys %{$t->{cols}})."\n";
print "mids ".join(" ", map { sprintf("%d:%.6f", $_, mids($t)->{$_}) } @{$t->{x}})."\n";
open(my $gh, "<", "gauss.txt") or die;
my @g; while (<$gh>) { chomp; push @g, [split /,/] }
printf("same %d %d\n", same($g[0], $g[1]) ? 1 : 0, same($g[0], $g[2]) ? 1 : 0);
my $t0 = time; my $s = 0;
for (1 .. $ARGV[0]) { for my $i (0..119) { for my $j ($i+1..119) { $s += xdist($t, $R->[$i], $R->[$j]) } } }
printf("W1 %.6f\n", $s);
my $s2 = 0;
for (1 .. $ARGV[1]) { $s2 += ydist($t, acquire($t)->[0]) }
printf("W2 %.6f\n", $s2);
print "SEED $SEED\n";
printf STDERR ("secs %.3f\n", time - $t0);

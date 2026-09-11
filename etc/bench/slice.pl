sub Num { [0, 0, 0] }                        # n, mu, m2: all Welford keeps
sub Sym { {has => []} }                      # [[v,count],..], in order
sub isSym { ref($_[0]) eq 'HASH' }
sub rnd {                                    # MINSTD, shared by all ports
  $SEED = ($SEED * 16807) % 2147483647;
  $SEED / 2147483647 }
sub shuffle {                                # Fisher-Yates, shared rnd order
  my @a = @{$_[0]};
  for (my $i = $#a; $i > 0; $i--) {
    my $j = int(rnd() * ($i + 1));
    @a[$i, $j] = @a[$j, $i] }
  \@a }
sub sortBy {                                 # decorate, sort, undecorate
  my ($t, $f) = @_;
  [map { $_->[1] } sort { $a->[0] <=> $b->[0] } map { [$f->($_), $_] } @$t] }
sub sd { my $c = shift; $c->[0] < 2 ? 0 : sqrt($c->[2] / ($c->[0] - 1)) }
sub add {                                    # inc=-1 undoes
  my ($c, $v, $inc) = @_; $inc //= 1;
  return $c if $v eq "?";
  if (isSym($c)) {
    for my $kv (@{$c->{has}}) {
      if ($kv->[0] eq $v) { $kv->[1] += $inc; return $c } }
    push @{$c->{has}}, [$v, $inc];
    return $c }
  my ($n, $mu, $m2) = @$c;
  $n += $inc;
  my $d = $v - $mu;
  $mu += $inc * $d / ($n > 1 ? $n : 1);
  [$n, $mu, ($m2 + $inc * $d * ($v - $mu)) > 0
            ? $m2 + $inc * $d * ($v - $mu) : 0] }
sub adds { my ($lst, $it) = @_; $it //= Num();
  $it = add($it, $_) for @$lst; $it }
sub size { my $c = shift;
  return $c->[0] unless isSym($c);
  my $s = 0; $s += $_->[1] for @{$c->{has}}; $s }
sub div {                                    # Num: sd. Sym: entropy
  my $c = shift;
  return sd($c) unless isSym($c);
  my ($n, $s) = (size($c), 0);
  for (@{$c->{has}}) {
    $s += $_->[1]/$n * log($_->[1]/$n)/log(2) if $_->[1] > 0 }
  -$s }
sub addRow {                                 # inc=-1 pops the last row
  my ($tbl, $row, $inc) = @_; $inc //= 1;
  $tbl->{_mids} = undef;
  if ($inc > 0) { push @{$tbl->{rows}}, $row }
  else { $row = pop @{$tbl->{rows}} }
  for my $at (keys %{$tbl->{cols}}) {
    $tbl->{cols}{$at} = add($tbl->{cols}{$at}, $row->[$at], $inc) }
  $row }
sub Tbl {
  my $src = shift;
  my $tbl = {rows => [], cols => {}, x => [], y => [],
             names => $src->[0], klass => undef};
  my @names = @{$src->[0]};
  for my $at (0 .. $#names) {
    my $s = $names[$at]; my $last = substr($s, -1);
    next if $last eq "X";
    $tbl->{cols}{$at} = substr($s,0,1) =~ /[A-Z]/ ? Num() : Sym();
    if    ($last eq "!") { $tbl->{klass} = $at }
    elsif ($last =~ /[+-]/) { push @{$tbl->{y}}, [$at, $last eq "+" ? 1 : 0] }
    else  { push @{$tbl->{x}}, $at } }
  addRow($tbl, $_) for @{$src}[1 .. $#$src];
  $tbl }
sub clone { my ($tbl, $rows) = @_; Tbl([$tbl->{names}, @{$rows // []}]) }
sub norm {
  my ($col, $v) = @_;
  my $z = ($v - $col->[1]) / (1e-32 + sd($col));
  $z = $z < -3 ? -3 : $z > 3 ? 3 : $z;
  1 / (1 + exp(-1.7 * $z)) }
sub mid {
  my $col = shift;
  return $col->[1] unless isSym($col);
  my $best = $col->{has}[0];
  for (@{$col->{has}}) { $best = $_ if $_->[1] > $best->[1] }
  $best->[0] }
sub mids {                                   # x centroid; cached
  my $tbl = shift;
  $tbl->{_mids} //= {map { $_ => mid($tbl->{cols}{$_}) } @{$tbl->{x}}};
  $tbl->{_mids} }
sub mink { my $g = shift; my $s = 0; $s += $_ ** $P for @$g;
  ($s / scalar @$g) ** (1/$P) }
sub ydist { my ($tbl, $row) = @_;
  mink([map { abs(norm($tbl->{cols}{$_->[0]}, $row->[$_->[0]]) - $_->[1]) }
        @{$tbl->{y}}]) }
sub dist1 {
  my ($col, $a, $b) = @_;
  return 1 if $a eq "?" || $b eq "?";
  return $a ne $b ? 1 : 0 if isSym($col);
  abs(norm($col, $a) - norm($col, $b)) }
sub xdist { my ($tbl, $row, $m) = @_;
  mink([map { dist1($tbl->{cols}{$_}, $row->[$_],
              ref($m) eq 'HASH' ? $m->{$_} : $m->[$_]) } @{$tbl->{x}}]) }
sub ymu { my ($tbl, $rows) = @_;
  my $s = 0; $s += ydist($tbl, $_) for @$rows; $s / scalar @$rows }
sub ymids { my ($tbl, $rows) = @_;
  [map { my $at = $_->[0]; my $s = 0; $s += $_->[$at] for @$rows;
         $s / scalar @$rows } @{$tbl->{y}}] }
sub centroid {                               # near best, far from rest
  my ($tbl, $best, $rest) = @_;
  sub { xdist($tbl, $_[0], mids($rest)) - xdist($tbl, $_[0], mids($best)) } }
sub label {                                  # keep best pool near sqrt
  my ($tbl, $best, $rest, $row) = @_;
  addRow($best, $row);
  $best->{rows} = sortBy($best->{rows}, sub { ydist($tbl, $_[0]) });
  my ($b, $r) = (scalar @{$best->{rows}}, scalar @{$rest->{rows}});
  addRow($rest, addRow($best, undef, -1)) if $b > sqrt(1 + $b + $r) }
sub acquire {                                # pop the top scorer
  my ($tbl, $cap, $score) = @_;
  $score //= \&centroid;
  my ($best, $rest) = (clone($tbl), clone($tbl));
  my @todo = @{shuffle($tbl->{rows})}[0 .. $Few - 1];
  label($tbl, $best, $rest, pop @todo) for 1 .. $Start;
  $cap //= $Stop;
  while (@todo && @{$best->{rows}} + @{$rest->{rows}} < $cap) {
    @todo = @{sortBy(\@todo, $score->($tbl, $best, $rest))};
    label($tbl, $best, $rest, pop @todo) }
  [@{$best->{rows}}, @{$rest->{rows}}] }
sub cohen {                                  # gap vs pooled sd, floored
  my ($xs, $ys, $d, $eps) = @_; $d //= 0.35; $eps //= 0;
  my ($a, $b) = (adds($xs), adds($ys));
  my $pool = (($a->[0]-1) * sd($a)**2 + ($b->[0]-1) * sd($b)**2)
             / ($a->[0] + $b->[0] - 2);
  my $t = $d * sqrt($pool);
  abs($a->[1] - $b->[1]) <= ($eps > $t ? $eps : $t) }
sub cliffs {                                 # sorted in. rank imbalance ok?
  my ($xs, $ys, $d) = @_; $d //= 0.197;
  my ($gt, $lt, $j, $k, $m) = (0, 0, 0, 0, scalar @$ys);
  for my $x (@$xs) {
    while ($j < $m && $ys->[$j] <  $x) { $j++; $k = $j }
    while ($k < $m && $ys->[$k] <= $x) { $k++ }
    $gt += $j; $lt += $m - $k }
  abs($gt - $lt) / (@$xs * $m) <= $d }
sub ks {                                     # sorted in. 95% K-S
  my ($xs, $ys, $a) = @_; $a //= 1.36;
  my ($n, $m, $i, $j, $d) = (scalar @$xs, scalar @$ys, 0, 0, 0);
  while ($i < $n && $j < $m) {
    my $v = $xs->[$i] < $ys->[$j] ? $xs->[$i] : $ys->[$j];
    $i++ while $i < $n && $xs->[$i] <= $v;
    $j++ while $j < $m && $ys->[$j] <= $v;
    my $g = abs($i/$n - $j/$m); $d = $g if $g > $d }
  $d <= $a * sqrt(($n + $m) / ($n * $m)) }
sub same {                                   # indistinguishable, all three
  my ($xs, $ys, $eps) = @_; $eps //= 0;
  my @x = sort { $a <=> $b } @$xs;
  my @y = sort { $a <=> $b } @$ys;
  cliffs(\@x, \@y) && ks(\@x, \@y) && cohen(\@x, \@y, 0.35, $eps) }
1;

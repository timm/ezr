<?php
function Num() { return [0, 0, 0]; }         // n, mu, m2: all Welford keeps
function isSym($c) { return is_array($c) && array_key_exists("has", $c); }
function Sym() { return ["has" => []]; }     // [[v,count],..], in order
function rnd() {                             // MINSTD, shared by all ports
  global $SEED;
  $SEED = ($SEED * 16807) % 2147483647;
  return $SEED / 2147483647; }
function shuffled($a) {                      // Fisher-Yates, shared order
  for ($i = count($a) - 1; $i > 0; $i--) {
    $j = (int)(rnd() * ($i + 1));
    [$a[$i], $a[$j]] = [$a[$j], $a[$i]]; }
  return $a; }
function sortBy($t, $f) {                    // decorate, sort, undecorate
  $d = array_map(fn($v) => [$f($v), $v], $t);
  usort($d, fn($p, $q) => $p[0] <=> $q[0]);
  return array_map(fn($p) => $p[1], $d); }
function sd($c) { return $c[0] < 2 ? 0 : sqrt($c[2] / ($c[0] - 1)); }
function add($c, $v, $inc = 1) {             // inc=-1 undoes
  if ($v === "?") return $c;
  if (isSym($c)) {
    foreach ($c["has"] as $i => $kv)
      if ($kv[0] == $v) { $c["has"][$i][1] += $inc; return $c; }
    $c["has"][] = [$v, $inc];
    return $c; }
  [$n, $mu, $m2] = $c;
  $n += $inc;
  $d = $v - $mu;
  $mu += $inc * $d / max(1, $n);
  return [$n, $mu, max(0, $m2 + $inc * $d * ($v - $mu))]; }
function adds($lst, $it = null) {
  $it = $it ?? Num();
  foreach ($lst as $y) $it = add($it, $y);
  return $it; }
function size($c) {
  if (!isSym($c)) return $c[0];
  return array_sum(array_map(fn($kv) => $kv[1], $c["has"])); }
function divc($c) {                          // Num: sd. Sym: entropy
  if (!isSym($c)) return sd($c);
  $n = size($c); $s = 0;
  foreach ($c["has"] as $kv)
    if ($kv[1] > 0) $s += $kv[1]/$n * log($kv[1]/$n, 2);
  return -$s; }
function addRow(&$tbl, $row = null, $inc = 1) {   // inc=-1 pops the last row
  $tbl["_mids"] = null;
  if ($inc > 0) $tbl["rows"][] = $row; else $row = array_pop($tbl["rows"]);
  foreach ($tbl["cols"] as $at => $c)
    $tbl["cols"][$at] = add($c, $row[$at], $inc);
  return $row; }
function Tbl($src) {
  $tbl = ["rows" => [], "cols" => [], "x" => [], "y" => [],
          "names" => $src[0], "klass" => null, "_mids" => null];
  foreach ($src[0] as $at => $s) {
    $last = substr($s, -1);
    if ($last === "X") continue;
    $tbl["cols"][$at] = ctype_upper($s[0]) ? Num() : Sym();
    if ($last === "!") $tbl["klass"] = $at;
    elseif ($last === "+" || $last === "-") $tbl["y"][$at] = $last === "+" ? 1 : 0;
    else $tbl["x"][] = $at; }
  foreach (array_slice($src, 1) as $row) addRow($tbl, $row);
  return $tbl; }
function clone_tbl($tbl, $rows = []) {
  return Tbl(array_merge([$tbl["names"]], $rows)); }
function norm($col, $v) {
  $z = ($v - $col[1]) / (1e-32 + sd($col));
  $z = max(-3, min(3, $z));
  return 1 / (1 + exp(-1.7 * $z)); }
function mid($col) {
  if (!isSym($col)) return $col[1];
  $best = $col["has"][0];
  foreach ($col["has"] as $kv) if ($kv[1] > $best[1]) $best = $kv;
  return $best[0]; }
function mids(&$tbl) {                       // x centroid; cached
  if (!$tbl["_mids"]) {
    $m = [];
    foreach ($tbl["x"] as $at) $m[$at] = mid($tbl["cols"][$at]);
    $tbl["_mids"] = $m; }
  return $tbl["_mids"]; }
function mink($gaps) {
  global $P;
  $s = 0;
  foreach ($gaps as $g) $s += $g ** $P;
  return ($s / count($gaps)) ** (1 / $P); }
function ydist($tbl, $row) {
  $g = [];
  foreach ($tbl["y"] as $at => $w)
    $g[] = abs(norm($tbl["cols"][$at], $row[$at]) - $w);
  return mink($g); }
function dist1($col, $a, $b) {
  if ($a === "?" || $b === "?") return 1;
  if (isSym($col)) return $a != $b ? 1 : 0;
  return abs(norm($col, $a) - norm($col, $b)); }
function xdist($tbl, $row, $m) {
  $g = [];
  foreach ($tbl["x"] as $at) $g[] = dist1($tbl["cols"][$at], $row[$at], $m[$at]);
  return mink($g); }
function ymu($tbl, $rows) {
  $s = 0;
  foreach ($rows as $r) $s += ydist($tbl, $r);
  return $s / count($rows); }
function centroid($tbl, &$best, &$rest) {    // near best, far from rest
  $mb = mids($best); $mr = mids($rest);
  return fn($z) => xdist($tbl, $z, $mr) - xdist($tbl, $z, $mb); }
function label($tbl, &$best, &$rest, $row) { // keep best pool near sqrt
  addRow($best, $row);
  $best["rows"] = sortBy($best["rows"], fn($r) => ydist($tbl, $r));
  $b = count($best["rows"]); $r = count($rest["rows"]);
  if ($b > sqrt(1 + $b + $r)) addRow($rest, addRow($best, null, -1)); }
function acquire($tbl, $cap = null) {        // pop the top scorer
  global $Few, $Start, $Stop;
  $best = clone_tbl($tbl); $rest = clone_tbl($tbl);
  $todo = array_slice(shuffled($tbl["rows"]), 0, $Few);
  for ($i = 0; $i < $Start; $i++) label($tbl, $best, $rest, array_pop($todo));
  $cap = $cap ?? $Stop;
  while ($todo && count($best["rows"]) + count($rest["rows"]) < $cap) {
    $todo = sortBy($todo, centroid($tbl, $best, $rest));
    label($tbl, $best, $rest, array_pop($todo)); }
  return array_merge($best["rows"], $rest["rows"]); }
function cohen($xs, $ys, $eps = 0) {         // gap vs pooled sd, floored
  $a = adds($xs); $b = adds($ys);
  $pool = (($a[0]-1) * sd($a)**2 + ($b[0]-1) * sd($b)**2) / ($a[0]+$b[0]-2);
  return abs($a[1] - $b[1]) <= max($eps, 0.35 * sqrt($pool)); }
function cliffs($xs, $ys) {                  // sorted in. rank imbalance ok?
  $gt = $lt = $j = $k = 0; $m = count($ys);
  foreach ($xs as $x) {
    while ($j < $m && $ys[$j] <  $x) { $j++; $k = $j; }
    while ($k < $m && $ys[$k] <= $x) $k++;
    $gt += $j; $lt += $m - $k; }
  return abs($gt - $lt) / (count($xs) * $m) <= 0.197; }
function ks($xs, $ys) {                      // sorted in. 95% K-S
  $n = count($xs); $m = count($ys); $i = $j = 0; $d = 0;
  while ($i < $n && $j < $m) {
    $v = min($xs[$i], $ys[$j]);
    while ($i < $n && $xs[$i] <= $v) $i++;
    while ($j < $m && $ys[$j] <= $v) $j++;
    $d = max($d, abs($i/$n - $j/$m)); }
  return $d <= 1.36 * sqrt(($n + $m) / ($n * $m)); }
function same($xs, $ys, $eps = 0) {          // indistinguishable, all three
  sort($xs); sort($ys);
  return cliffs($xs, $ys) && ks($xs, $ys) && cohen($xs, $ys, $eps); }

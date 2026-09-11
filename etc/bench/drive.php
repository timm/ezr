<?php
$P = 2; $Few = 128; $Start = 4; $Stop = 50; $SEED = 1;
require "slice.php";
function atomv($s) {
  return preg_match('/^-?\d+$/', $s) || preg_match('/^-?\d*\.\d+$/', $s) ? $s + 0 : $s; }
$lines = array_values(array_filter(array_map('trim', file("data.csv")), fn($l) => $l !== ""));
$cells = array_map(fn($l) => explode(",", $l), $lines);
$src = array_merge([$cells[0]], array_map(fn($r) => array_map('atomv', $r), array_slice($cells, 1)));
$t = Tbl($src); $R = $t["rows"];
$ys = [];
foreach ($t["y"] as $a => $w) $ys[] = "($a, $w)";
printf("n %d x [%s] y [%s]\n", count($R), implode(", ", $t["x"]), implode(", ", $ys));
printf("ymu %.6f\n", ymu($t, $R));
printf("ydist0 %.6f\n", ydist($t, $R[0]));
printf("xdist01 %.6f\n", xdist($t, $R[0], $R[1]));
$dv = [];
foreach ($t["cols"] as $at => $c) $dv[] = sprintf("%.6f", divc($c));
echo "div ".implode(" ", $dv)."\n";
$md = [];
foreach (mids($t) as $at => $v) $md[] = sprintf("%d:%.6f", $at, $v);
echo "mids ".implode(" ", $md)."\n";
$g = array_map(fn($l) => array_map('floatval', explode(",", trim($l))), file("gauss.txt"));
printf("same %d %d\n", same($g[0], $g[1]) ? 1 : 0, same($g[0], $g[2]) ? 1 : 0);
$t0 = microtime(true);
$s = 0.0;
for ($rep = 0; $rep < (int)$argv[1]; $rep++)
  for ($i = 0; $i < 120; $i++) for ($j = $i+1; $j < 120; $j++) $s += xdist($t, $R[$i], $R[$j]);
printf("W1 %.6f\n", $s);
$s2 = 0.0;
for ($rep = 0; $rep < (int)$argv[2]; $rep++) $s2 += ydist($t, acquire($t)[0]);
printf("W2 %.6f\n", $s2);
echo "SEED $SEED\n";
fprintf(STDERR, "secs %.3f\n", microtime(true) - $t0);

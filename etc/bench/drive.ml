open Slice
let atom s =
  match float_of_string_opt s with Some f -> N f | None -> S s
let split c s =
  String.split_on_char c s
let () =
  let p = 2.0 and few = 128 and start = 4 and stop = 50 in
  let ic = open_in "data.csv" in
  let ls = ref [] in
  (try while true do
    let l = String.trim (input_line ic) in
    if l <> "" then ls := l :: !ls
  done with End_of_file -> close_in ic);
  let cells = List.map (split ',') (List.rev !ls) in
  let names = List.hd cells in
  let rs = List.map (fun r -> Array.of_list (List.map atom r)) (List.tl cells) in
  let t = mktbl names rs in
  Printf.printf "n %d x [%s] y [%s]\n" (List.length t.rows)
    (String.concat ", " (List.map string_of_int t.xat))
    (String.concat ", " (List.map (fun (a,w) ->
       Printf.sprintf "(%d, %d)" a (int_of_float w)) t.yat));
  Printf.printf "ymu %.6f\n" (ymu p t t.rows);
  let rv = Array.of_list t.rows in
  Printf.printf "ydist0 %.6f\n" (ydist p t rv.(0));
  Printf.printf "xdist01 %.6f\n" (xdistr p t rv.(0) rv.(1));
  Printf.printf "div %s\n"
    (String.concat " " (List.map (fun (_,c) -> Printf.sprintf "%.6f" (divc c)) t.cols));
  Printf.printf "mids %s\n"
    (String.concat " " (List.map (fun (a,v) ->
       Printf.sprintf "%d:%.6f" a (numf v)) (mids t)));
  let ic2 = open_in "gauss.txt" in
  let gl = ref [] in
  (try while true do gl := input_line ic2 :: !gl done with End_of_file -> close_in ic2);
  let g = Array.of_list (List.rev_map (fun l ->
    List.map float_of_string (split ',' (String.trim l))) !gl) in
  Printf.printf "same %d %d\n"
    (if same g.(0) g.(1) 0.0 then 1 else 0)
    (if same g.(0) g.(2) 0.0 then 1 else 0);
  let t0 = Unix.gettimeofday () in
  let r1 = int_of_string Sys.argv.(1) and r2 = int_of_string Sys.argv.(2) in
  let s = ref 0.0 in
  for _ = 1 to r1 do
    for i = 0 to 119 do
      for j = i + 1 to 119 do s := !s +. xdistr p t rv.(i) rv.(j) done
    done
  done;
  Printf.printf "W1 %.6f\n" !s;
  let s2 = ref 0.0 in
  for _ = 1 to r2 do
    s2 := !s2 +. ydist p t (List.hd (acquire p few start stop t))
  done;
  Printf.printf "W2 %.6f\n" !s2;
  Printf.printf "SEED %d\n" !seed;
  Printf.eprintf "secs %.3f\n" (Unix.gettimeofday () -. t0)

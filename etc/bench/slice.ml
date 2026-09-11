type atom = N of float | S of string
type row = atom array
type col = Nm of nm | Sy of (atom * float) list ref
and nm = { mutable n : float; mutable mu : float; mutable m2 : float }
type tbl = { mutable rows : row list; cols : (int * col) list;
             xat : int list; yat : (int * float) list; nms : string list }
let seed = ref 1
let rnd () =                                 (* MINSTD, shared by all ports *)
  seed := !seed * 16807 mod 2147483647;
  float_of_int !seed /. 2147483647.0
let shuffle lst =                            (* Fisher-Yates, shared order *)
  let a = Array.of_list lst in
  for i = Array.length a - 1 downto 1 do
    let j = int_of_float (rnd () *. float_of_int (i + 1)) in
    let t = a.(i) in a.(i) <- a.(j); a.(j) <- t
  done;
  Array.to_list a
let numf = function N v -> v | S _ -> nan
let isq = function S "?" -> true | _ -> false
let sd = function
  | Nm c -> if c.n < 2.0 then 0.0 else sqrt (c.m2 /. (c.n -. 1.0))
  | Sy _ -> 0.0
let add c v inc =                            (* inc=-1 undoes *)
  if isq v then () else
  match c with
  | Sy h ->
      if List.mem_assoc v !h
      then h := List.map (fun (k, n) -> if k = v then (k, n +. inc) else (k, n)) !h
      else h := !h @ [ (v, inc) ]
  | Nm c ->
      let x = numf v in
      c.n <- c.n +. inc;
      let d = x -. c.mu in
      c.mu <- c.mu +. inc *. d /. (max 1.0 c.n);
      c.m2 <- max 0.0 (c.m2 +. inc *. d *. (x -. c.mu))
let adds lst =
  let c = Nm { n = 0.0; mu = 0.0; m2 = 0.0 } in
  List.iter (fun v -> add c (N v) 1.0) lst; c
let size = function
  | Nm c -> c.n
  | Sy h -> List.fold_left (fun s (_, v) -> s +. v) 0.0 !h
let divc c =                                 (* Num: sd. Sym: entropy *)
  match c with
  | Nm _ -> sd c
  | Sy h ->
      let n = size c in
      -. List.fold_left (fun s (_, v) ->
           if v > 0.0 then s +. v /. n *. (log (v /. n) /. log 2.0) else s) 0.0 !h
let midc = function
  | Nm c -> N c.mu
  | Sy h -> fst (List.fold_left (fun a b -> if snd b > snd a then b else a)
                   (List.hd !h) !h)
let normc c v =
  match c with
  | Sy _ -> 0.0
  | Nm k ->
      let z = (numf v -. k.mu) /. (1e-32 +. sd c) in
      1.0 /. (1.0 +. exp (-1.7 *. (max (-3.0) (min 3.0 z))))
let addrow t row inc =                       (* inc=-1 pops the last row *)
  let row = if inc > 0.0 then row
            else (let r = List.nth t.rows (List.length t.rows - 1) in
                  t.rows <- List.filteri (fun i _ -> i < List.length t.rows - 1) t.rows; r) in
  if inc > 0.0 then t.rows <- t.rows @ [ row ];
  List.iter (fun (a, c) -> add c row.(a) inc) t.cols;
  row
let fresh_cols names =
  List.concat (List.mapi (fun a s ->
    if s.[String.length s - 1] = 'X' then []
    else [ (a, if s.[0] >= 'A' && s.[0] <= 'Z'
               then Nm { n = 0.0; mu = 0.0; m2 = 0.0 } else Sy (ref [])) ])
    names)
let mktbl names rs =
  let last s = s.[String.length s - 1] in
  let idx = List.concat (List.mapi (fun a s ->
              if last s = 'X' then [] else [ (a, s) ]) names) in
  let t = { rows = []; cols = fresh_cols names;
            xat = List.filter_map (fun (a, s) ->
                    if List.mem (last s) [ '+'; '-'; '!' ] then None else Some a) idx;
            yat = List.filter_map (fun (a, s) ->
                    if last s = '+' then Some (a, 1.0)
                    else if last s = '-' then Some (a, 0.0) else None) idx;
            nms = names } in
  List.iter (fun r -> ignore (addrow t r 1.0)) rs; t
let clone t rs = mktbl t.nms rs
let colof t a = List.assoc a t.cols
let mids t = List.map (fun a -> (a, midc (colof t a))) t.xat   (* x centroid *)
let mink p gs =
  (List.fold_left (fun s g -> s +. (g ** p)) 0.0 gs
   /. float_of_int (List.length gs)) ** (1.0 /. p)
let ydist p t row =
  mink p (List.map (fun (a, w) -> abs_float (normc (colof t a) row.(a) -. w)) t.yat)
let dist1 c a b =
  if isq a || isq b then 1.0
  else match c with
    | Sy _ -> if a <> b then 1.0 else 0.0
    | Nm _ -> abs_float (normc c a -. normc c b)
let xdist p t row m =
  mink p (List.map (fun a -> dist1 (colof t a) row.(a) (List.assoc a m)) t.xat)
let xdistr p t row (m : row) =
  xdist p t row (List.map (fun a -> (a, m.(a))) t.xat)
let ymu p t rs =
  List.fold_left (fun s r -> s +. ydist p t r) 0.0 rs /. float_of_int (List.length rs)
let centroid p t best rest z =               (* near best, far from rest *)
  xdist p t z (mids rest) -. xdist p t z (mids best)
let sort_by f lst =                          (* stable, key computed once *)
  List.map snd (List.stable_sort (fun a b -> compare (fst a) (fst b))
                  (List.map (fun v -> (f v, v)) lst))
let label p t best rest row =                (* keep best pool near sqrt *)
  ignore (addrow best row 1.0);
  best.rows <- sort_by (ydist p t) best.rows;
  let b = float_of_int (List.length best.rows) in
  let r = float_of_int (List.length rest.rows) in
  if b > sqrt (1.0 +. b +. r) then
    ignore (addrow rest (addrow best [||] (-1.0)) 1.0)
let rec take n = function
  | [] -> []
  | x :: r -> if n <= 0 then [] else x :: take (n - 1) r
let last_of l = List.nth l (List.length l - 1)
let init_of l = List.filteri (fun i _ -> i < List.length l - 1) l
let acquire p few start stop t =             (* pop the top scorer *)
  let best = clone t [] and rest = clone t [] in
  let todo = ref (take few (shuffle t.rows)) in
  for _ = 1 to start do
    label p t best rest (last_of !todo); todo := init_of !todo
  done;
  while !todo <> [] && List.length best.rows + List.length rest.rows < stop do
    todo := sort_by (centroid p t best rest) !todo;
    label p t best rest (last_of !todo);
    todo := init_of !todo
  done;
  best.rows @ rest.rows
let cohen xs ys eps =                        (* gap vs pooled sd, floored *)
  let a = adds xs and b = adds ys in
  let na = size a and nb = size b in
  let mua = numf (midc a) and mub = numf (midc b) in
  let pool = ((na -. 1.0) *. (sd a ** 2.0) +. (nb -. 1.0) *. (sd b ** 2.0))
             /. (na +. nb -. 2.0) in
  abs_float (mua -. mub) <= max eps (0.35 *. sqrt pool)
let cliffs xs ys =                           (* sorted in. rank imbalance ok? *)
  let ya = Array.of_list ys in
  let m = Array.length ya in
  let gt = ref 0 and lt = ref 0 and j = ref 0 and k = ref 0 in
  List.iter (fun x ->
    while !j < m && ya.(!j) < x do incr j; k := !j done;
    while !k < m && ya.(!k) <= x do incr k done;
    gt := !gt + !j; lt := !lt + m - !k) xs;
  float_of_int (abs (!gt - !lt)) /. float_of_int (List.length xs * m) <= 0.197
let ks xs ys =                               (* sorted in. 95% K-S *)
  let xa = Array.of_list xs and ya = Array.of_list ys in
  let n = Array.length xa and m = Array.length ya in
  let i = ref 0 and j = ref 0 and d = ref 0.0 in
  while !i < n && !j < m do
    let v = min xa.(!i) ya.(!j) in
    while !i < n && xa.(!i) <= v do incr i done;
    while !j < m && ya.(!j) <= v do incr j done;
    d := max !d (abs_float (float_of_int !i /. float_of_int n
                          -. float_of_int !j /. float_of_int m))
  done;
  !d <= 1.36 *. sqrt (float_of_int (n + m) /. float_of_int (n * m))
let same xs ys eps =                         (* indistinguishable, all three *)
  let xs = List.sort compare xs and ys = List.sort compare ys in
  cliffs xs ys && ks xs ys && cohen xs ys eps

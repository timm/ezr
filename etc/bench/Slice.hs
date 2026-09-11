module Slice where
import Data.List (sortOn, foldl')
import Data.Char (isUpper)
data Atom = N !Double | S String deriving (Eq, Show)
type Row  = [Atom]
data Col  = Nm !Double !Double !Double | Sy [(Atom, Double)]
data Tbl  = Tbl { rows :: [Row], cols :: [(Int, Col)]
                , xat :: [Int], yat :: [(Int, Double)], nms :: [String] }
num :: Atom -> Double                        -- numeric view of a cell
num (N v) = v
num _     = 0 / 0
isQ :: Atom -> Bool
isQ (S "?") = True
isQ _       = False
rnd :: Int -> (Double, Int)                  -- MINSTD, shared by all ports
rnd s = let s' = s * 16807 `mod` 2147483647
        in (fromIntegral s' / 2147483647, s')
shuffle :: Int -> [a] -> ([a], Int)          -- Fisher-Yates, shared order
shuffle s0 xs = go s0 (length xs - 1) xs
  where go s i a | i <= 0 = (a, s)
                 | otherwise =
                     let (r, s') = rnd s
                         j = floor (r * fromIntegral (i + 1))
                     in go s' (i - 1) (swap i j a)
        swap i j a | i == j = a
                   | otherwise =
                       [ if k == i then a !! j else
                         if k == j then a !! i else v
                       | (k, v) <- zip [0 ..] a ]
sd :: Col -> Double
sd (Nm n _ m2) = if n < 2 then 0 else sqrt (m2 / (n - 1))
sd _           = 0
add :: Col -> Atom -> Double -> Col          -- inc=-1 undoes
add c v inc | isQ v = c
add (Sy h) v inc
  | any ((== v) . fst) h = Sy [ if k == v then (k, c + inc) else (k, c)
                              | (k, c) <- h ]
  | otherwise            = Sy (h ++ [(v, inc)])
add (Nm n mu m2) v inc =
  let x   = num v
      n'  = n + inc
      d   = x - mu
      mu' = mu + inc * d / max 1 n'
  in Nm n' mu' (max 0 (m2 + inc * d * (x - mu')))
adds :: [Double] -> Col
adds = foldl' (\c v -> add c (N v) 1) (Nm 0 0 0)
size :: Col -> Double
size (Nm n _ _) = n
size (Sy h)     = sum (map snd h)
divC :: Col -> Double                        -- Num: sd. Sym: entropy
divC c@(Nm _ _ _) = sd c
divC c@(Sy h) = negate (sum [ v/n * logBase 2 (v/n) | (_, v) <- h, v > 0 ])
  where n = size c
midC :: Col -> Atom
midC (Nm _ mu _) = N mu
midC (Sy h)      = fst (foldl1 (\a b -> if snd b > snd a then b else a) h)
normC :: Col -> Atom -> Double
normC c v = 1 / (1 + exp (-1.7 * max (-3) (min 3 z)))
  where Nm _ mu _ = c
        z = (num v - mu) / (1e-32 + sd c)
addRow :: Tbl -> Row -> Double -> Tbl        -- inc=-1 pops the last row
addRow t row inc = t { rows = if inc > 0 then rows t ++ [row]
                                         else init (rows t)
                     , cols = [ (a, add c (row !! a) inc) | (a, c) <- cols t ] }
popRow :: Tbl -> (Tbl, Row)
popRow t = (addRow t r (-1), r) where r = last (rows t)
mkTbl :: [String] -> [Row] -> Tbl
mkTbl names rs = foldl' (\t r -> addRow t r 1) blank rs
  where blank = Tbl [] cs xs ys names
        tagged = [ (a, s, last s) | (a, s) <- zip [0 ..] names, last s /= 'X' ]
        cs = [ (a, if isUpper (head s) then Nm 0 0 0 else Sy []) 
             | (a, s, _) <- tagged ]
        xs = [ a | (a, _, e) <- tagged, e `notElem` "+-!" ]
        ys = [ (a, if e == '+' then 1 else 0) | (a, _, e) <- tagged, e `elem` "+-" ]
clone :: Tbl -> [Row] -> Tbl
clone t = mkTbl (nms t)
mids :: Tbl -> [(Int, Atom)]                 -- x centroid
mids t = [ (a, midC c) | (a, c) <- cols t, a `elem` xat t ]
mink :: Double -> [Double] -> Double
mink p gs = (sum (map (** p) gs) / fromIntegral (length gs)) ** (1 / p)
ydist :: Double -> Tbl -> Row -> Double
ydist p t row = mink p [ abs (normC (col t a) (row !! a) - w) | (a, w) <- yat t ]
col :: Tbl -> Int -> Col
col t a = maybe (Nm 0 0 0) id (lookup a (cols t))
dist1 :: Col -> Atom -> Atom -> Double
dist1 c a b | isQ a || isQ b = 1
dist1 (Sy _) a b = if a /= b then 1 else 0
dist1 c a b      = abs (normC c a - normC c b)
xdist :: Double -> Tbl -> Row -> [(Int, Atom)] -> Double
xdist p t row m =
  mink p [ dist1 (col t a) (row !! a) (maybe (S "?") id (lookup a m))
         | a <- xat t ]
xdistR :: Double -> Tbl -> Row -> Row -> Double
xdistR p t row m = xdist p t row [ (a, m !! a) | a <- xat t ]
ymu :: Double -> Tbl -> [Row] -> Double
ymu p t rs = sum (map (ydist p t) rs) / fromIntegral (length rs)
centroid :: Double -> Tbl -> Tbl -> Tbl -> Row -> Double   -- near best, far rest
centroid p t best rest z = xdist p t z (mids rest) - xdist p t z (mids best)
label :: Double -> Tbl -> (Tbl, Tbl) -> Row -> (Tbl, Tbl)  -- best pool ~ sqrt
label p t (best, rest) row =
  let b1 = addRow best row 1
      b2 = b1 { rows = sortOn (ydist p t) (rows b1) }
      nb = fromIntegral (length (rows b2))
      nr = fromIntegral (length (rows rest))
  in if nb > sqrt (1 + nb + nr)
       then let (b3, gone) = popRow b2 in (b3, addRow rest gone 1)
       else (b2, rest)
acquire :: Double -> Int -> Int -> Int -> Int -> Tbl -> ([Row], Int)
acquire p few start stop s0 t =
  let (sh, s1) = shuffle s0 (rows t)
      todo0    = take few sh
      warm k (br, td) | k <= 0 = (br, td)
                      | otherwise = warm (k - 1) (label p t br (last td), init td)
      (br1, td1) = warm start ((clone t [], clone t []), todo0)
      loop (best, rest) td
        | null td = (best, rest)
        | length (rows best) + length (rows rest) >= stop = (best, rest)
        | otherwise =
            let sorted = sortOn (centroid p t best rest) td
            in loop (label p t (best, rest) (last sorted)) (init sorted)
      (bF, rF) = loop br1 td1
  in (rows bF ++ rows rF, s1)
cohen :: [Double] -> [Double] -> Double -> Bool    -- gap vs pooled sd, floored
cohen xs ys eps = abs (mua - mub) <= max eps (0.35 * sqrt pool)
  where a@(Nm na mua _) = adds xs
        b@(Nm nb mub _) = adds ys
        pool = ((na - 1) * sd a ** 2 + (nb - 1) * sd b ** 2) / (na + nb - 2)
cliffs :: [Double] -> [Double] -> Bool             -- rank imbalance ok?
cliffs xs ys = fromIntegral (abs (gt - lt)) / fromIntegral (n * m) <= 0.197
  where n = length xs
        m = length ys
        go (g, l, j, k) x =
          let j' = length (takeWhile (<  x) (drop j ys)) + j
              k' = length (takeWhile (<= x) (drop j' ys)) + j'
          in (g + j', l + m - k', j', k')
        (gt, lt, _, _) = foldl' go (0, 0, 0, 0) xs
ks :: [Double] -> [Double] -> Bool                 -- 95% kolmogorov-smirnov
ks xs ys = d <= 1.36 * sqrt (fromIntegral (n + m) / fromIntegral (n * m))
  where n = length xs
        m = length ys
        go i j best
          | i >= n || j >= m = best
          | otherwise =
              let v  = min (xs !! i) (ys !! j)
                  i' = length (takeWhile (<= v) (drop i xs)) + i
                  j' = length (takeWhile (<= v) (drop j ys)) + j
                  g  = abs (fromIntegral i' / fromIntegral n
                          - fromIntegral j' / fromIntegral m)
              in go i' j' (max best g)
        d = go 0 0 0
same :: [Double] -> [Double] -> Double -> Bool     -- by all three
same xs0 ys0 eps = cliffs xs ys && ks xs ys && cohen xs ys eps
  where xs = sortOn id xs0
        ys = sortOn id ys0

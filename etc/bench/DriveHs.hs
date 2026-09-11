import Slice
import Data.List (foldl', intercalate, isSuffixOf)
import Data.Char (isDigit)
import Text.Printf (printf)
import System.Environment (getArgs)
import Data.IORef
import Data.Time.Clock
atom :: String -> Atom
atom s | all (\c -> isDigit c || c == '-' || c == '.') s && any isDigit s = N (read (fix s))
       | otherwise = S s
  where fix t = if head t == '.' then '0':t else t
splitOn :: Char -> String -> [String]
splitOn c s = case break (== c) s of
  (a, [])     -> [a]
  (a, _:rest) -> a : splitOn c rest
f6 :: Double -> String
f6 = printf "%.6f"
main :: IO ()
main = do
  args <- getArgs
  let p = 2 :: Double
      few = 128; start = 4; stop = 50
  raw <- readFile "data.csv"
  let ls = [ l | l <- lines raw, any (`notElem` " \t\r") l ]
      cells = map (splitOn ',') (map (filter (/= '\r')) ls)
      names = head cells
      rs = map (map atom) (tail cells)
      t = mkTbl names rs
      rws = rows t
  printf "n %d x [%s] y [%s]\n" (length rws)
    (intercalate ", " (map show (xat t)))
    (intercalate ", " [ "(" ++ show a ++ ", " ++ show (round w :: Int) ++ ")" | (a,w) <- yat t ])
  putStrLn ("ymu " ++ f6 (ymu p t rws))
  putStrLn ("ydist0 " ++ f6 (ydist p t (head rws)))
  putStrLn ("xdist01 " ++ f6 (xdistR p t (head rws) (rws !! 1)))
  putStrLn ("div " ++ unwords [ f6 (divC c) | (_, c) <- cols t ])
  putStrLn ("mids " ++ unwords [ show a ++ ":" ++ f6 (num v) | (a, v) <- mids t ])
  g <- readFile "gauss.txt"
  let gs = [ map read (splitOn ',' l) :: [Double] | l <- lines g, not (null l) ]
  printf "same %d %d\n" (b2i (same (gs!!0) (gs!!1) 0)) (b2i (same (gs!!0) (gs!!2) 0))
  t0 <- getCurrentTime
  let r1 = read (args !! 0) :: Int
      r2 = read (args !! 1) :: Int
      rv = take 120 rws
      w1 = sum [ xdistR p t a b | _ <- [1..r1], (i,a) <- zip [0..] rv, (j,b) <- zip [0..] rv, j > (i::Int) ]
  putStrLn ("W1 " ++ f6 w1)
  let step (acc, s) _ = let (lab, s') = acquire p few start stop s t
                        in (acc + ydist p t (head lab), s')
      (w2, seedF) = foldl' step (0, 1) [1..r2]
  putStrLn ("W2 " ++ f6 w2)
  putStrLn ("SEED " ++ show seedF)
  t1 <- getCurrentTime
  printf "secs %.3f\n" (realToFrac (diffUTCTime t1 t0) :: Double)
  where b2i b = if b then 1 else 0 :: Int

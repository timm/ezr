# Exercises

## -1 isntall a edit/run environemtn

includeing oythoin3.12

wsl : wsl
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.10
python3.10 --version #Python 3.10.4
which python3.10 #/usr/bin/python3.10


## 0, Install the latest version of Python 3.12

- mac: `brew upgrade python`
- unix/linux: ??
- widnows: download the installer from  https://www.python.org/downloads/

Test the install:

    % python3 --version
    Python 3.12.3

## 1. Get the EZR code

    git clone http://github.com/timm/ezr
    
Make sure you select the right branch:

     % git branch -r
     origin/24feb28
     origin/24feb6
     origin/24may19
     origin/25may12
     origin/HEAD -> origin/main
     origin/Stable-EMSE-paper
     origin/main
     origin/sneak

You will told which branch to go to

     git checkout new_branch

Once you get there, make sure the code runs

     python3 ezr.py

This should print a whole lot of help information:

      ezr.py : an experiment in easier explainable AI (less is more).
      (C) 2024 Tim Menzies (timm@ieee.org) BSD-2 license.

      OPTIONS:
        -a --any     #todo's to explore             = 100
        -c --cohen   size of the Cohen d            = 0.35
        -d --decs    #decimals for showing floats   = 3
        -e --enough  want cuts at least this good   = 0.1
        -F --Far     how far to seek faraway        = 0.8
        -h --help    show help                      = False
        -H --Half    #rows for searching for poles  = 128
        -k --k       bayes low frequency hack #1    = 1
        -l --label   initial number for labelling    = 4
        -L --Last    max allow #labelling            = 30
        -m --m       bayes low frequency hack #2    = 2
        -n --n       tinyN                          = 12
        -N --N       smallN                         = 0.5
        -p --p       distance function coefficient  = 2
        -R --Run     start up action method         = help
        -s --seed    random number seed             = 1234567891
        -t --train   training data                  = data/misc/auto93.csv
        -T --test    test data (defaults to train)  = None
        -v --version show version                   = False
        -x --xys     max #bins in discretization    = 16

## 2. Practice running  the code

In the code repo, create a test directory under the root and 
create a test file `the.py`

        import sys; sys.path.append("..")
        from ezr import show,the
         
        print(show(the))

Now run that code

        cd tests
        python3 the.py

This should generate something like:

        (:any 100 :cohen 0.35 :decs 3 :enough 0.1 :Far 0.8 
         :help False :Half 128 :k 1 :label 4 :Last 30 :m 2 
         :n 12 :N 0.5 :p 2 :Run "help" :seed 1234567891 
         :train "data/misc/auto93.csv" :test None :version False :xys 16)

For all the other exercises, you can write one file `tests/xxx.py`

Note that you may need to adjust path names. E.g. see `tests/csv.py`,
which fiddles with `the.train`  pathname:

       import sys; sys.path.append("..")
       from ezr import csv,the
                
       for n,row in enumerate(csv("../" + the.train)) :
         if n % 50 == 0: print(row)

## 3. Using NUMs

Add in 1000 `random.random()**0.5` numbers to a NUMs instance.
Report the `mid()` and `div()` of those NUMs.

       import sys; sys.path.append("..")
       from ezr import NUM,adds,mid,div
       import random
           
       s = adds(NUM(),[random.random()**0.5 for _ in range(1000)])
       print(round(mid(s),3), round(div(s),3))

## 4. Using SYMs

Fin a page of text and paste it into a Python code file. Add all its
characters into a SYM. Report the entropy of that string

Hints:

      from ezr import adds, SYM
      sym = adds(SYM(),[c for c in string])
      print(div(sym))

## 4. Get specs on your data.

- Find all the `*.csv` files in the 
  [data](https://github.com/timm/ezr/tree/main/data) directory.
- For each of those files use the `csv()` function to read the first row in each file.
- Using the `COLS()` function, convert that first line into some NUMs and SYMs.
- For each file, print comma separated a line with 
         
                               x cols             y cols
                               -----------------  ------------------
         filename,#rows,#cols, #symCols,#numCols, #sy,Cols, #numCols

All the following are small extensions to the current `ezr` code base. So before anything,
you have to get the code

## 5. Clustering with dendograms
Without looking at the y values, we can cluster by finding two distant points, then divide
the data according which of those two points are nearest.  THe we recurse on each half,
stopping when we have (say) ony qrt(N) of the N rows in any division.

(While this sounds simple (it is),
it actually implements a non-parametric PCA-kike approach to 
synthesizing some combination of all the attributes along the dimension of greatest variance.)

Cluster some data using e.g.

     ./ezr.py -N 0.5 -t data/config/SS-A.csv -R dendogram

FYI: SS-A is a data set with the header

       Spout_wait,Spliters,Counters,Throughput+,Latency-

`N` is a parameter that can be varied 0.2 to 0.8. What is the effect of different `N` values?
Why? Looking at the y-values shown at each leaf (by dendogram) , do different `N` s select for
better goals?

## 6. From clustering to optimization

A slight extension to the above takes us to an optimization method.
As before, we divide the data on two distant points. But now we look at those y-values and prune half
the data associates with the worst half.

     ./ezr.py -N 0.5 -t data/config/SS-A.csv -R branch  | head -20

Please check: are the best results found by `branch` better or worse that those found by `dendogram`. Why?

Compare the config/SS-A.csv results with config/auto93.csv results from `dendogram` and `branch` . Once again,
are the best results found by `branch` better or worse that those found by `dendogram`?

## 6. From optimization to explanation
The above optimizer selects a `best` set of rows (those in the final leaf cluster).
This means that everything else is `rest`.  We can explain the delta between these
by applying our decision tree to the results:


      ./ezr.py -N 0.5 -t data/misc/auto93.csv -R branchTree


## Exercise1

Make your own data. At least 50 lines. e.g. 

- find 50 movies
- then 20 times,
  - pick 3 items at random and ask people which one is best. Add one to the score of that movie
    and zero to the others). 
  - List some details about the movie (location, running time,  number of big name stars, get creative)

      Echo the format of
the data in that directory. See what you get:

```
ezr -t yourfile.csv -R tree
```
E.g. 
```
ezr -t data/misc/auto93.csv -R tree
```
produces tree that says min `rest` and max `best` is achieved by `Volume &lt; 105` and `Cylindeers &ge; 4`.
```

                                    (:best 19 :rest 379)
if Volume < 105                     (:best 18 :rest 82)
|.. if Clndrs >= 4                  (:best 18 :rest 78)
|.. else                            (:best 0 :rest 4)
else                                (:best 1 :rest 297)
|.. if origin == 2                  (:best 1 :rest 34)
|.. |.. if Model >= 79              (:best 1 :rest 8)
|.. |.. else                        (:best 0 :rest 26)
|.. else                            (:best 0 :rest 263)
```

## Exercise2

Use the data structures of `ezr` to write a K-means cluster which

1. picks `k` centroids at random (use k=10)
2. label every example with its nearest centroid
3. for all things with the same label,
  - move their centoid to the middle of those points
4. and loop back to 1. (repeat this for 10 loops).

Try doing the above using

```
impprt ezr

erz.the.train = "yourfile"
# your code here
```

For each pass of the loop 1,2,3,4, generate a plot whose y values
are the average distance between cluster members and their centroid and the x values are  the
loop numbers. Feel free not to automate this plot generation (you can collect data from a few print
statements of your code, then manually make the plot in Google Sheets).

Hint: ignoring the  data generation stuff, your code should be less than 10 lines code. 

## Exercise3
## Exercise4
## Exercise5
## Exercise6
## Exercise7
## Exercise8
## Exercise9
## Exercise10


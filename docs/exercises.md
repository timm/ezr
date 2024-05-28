.

# Exercises

All the following are small extensions to the current `ezr` code base. So before anything,
you have to get the code

```
pip install ezr
ezr -R all; echo "errors= $?"
```

This should print a lot of output, then green "PASS" message followed by "errors= 0".

Also, you'll need data: see https://github.com/timm/ezr/tree/main/data. Any of
the csv files in that directory tree can be called using, e.g.

```
ezr -t fie.csv -R smo20
```

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


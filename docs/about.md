# The Big Picture

Much current work focuses on on the use of large general models.  That
works fine, except if your problems are so specific that they are not
covered by the general models.

When generality fails, you need to build local models. Local data
can be scarce. Hence it is important to do as much as you can with
whatever is available.  Hemce, local learning first focuses  on
easily accessible features (independent variables) in order to
quickly identify and select the most informative samples for labeling.
This reduces the overall cost and time required to train the model
effectively (as we only spend resources on obtaining labels for the
most valuable data points).

This trick works since a lot of data contains spurious information.
Much resaerch shows that a small number of rows can server as
exemplrs for the rest, Also, for any task, only a few attributes
are relevant. For example, if we look at 10% of the attributes
and the square root of the number of rows then a table of data with
100 attributes and 10,000 rows only has  1% of most information
cells (10 attriutes and 100 rows).

So local learning can be really fast since it only needs
to explore (say) the square root
of the number of rows and only a handful of attributes. For example,

<table>
<tr><td> n <td> name <td> what <td> notes </tr>
<tr><td> 1
<td> faraway
<td> find 2 points, faraway from each other 
<td> To find quickly find 2 distant points, pick anything at random, 
     find something else furthese from that,
     find something furhest from that second point.
     To avoid strange outliers, only go (say) 90% to the furthese point. </tr>
<tr><td> 2
<td> rank
<td> Given two faraway points, sort them by their y-values.
<td> Y-values can be sorted via 
     (a) binary domination 
         (the best is worse on none, better or at lease one);
     (b) Ziztler's predicate (the best loses less when you move 
         from other to best rather than best to other);
     (c) distance fo heaven- the (Euclidean distance of y-values to
         best possible;
     (d) Chebyshev distance- the max of the difference between y-values on any axis.</tr>
<tr><td> 3
<td> half
<td> 
</table>


Algo2: half = divide data according to its distance to 2 faraway points.

# Todo

- shufflethe rows
- sort examples by cheb

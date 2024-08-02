# Contribute

## Data conventions

- In our data, the  string "?" is used to denote a missing value.
- In our data,  row one  list the columns names. Those names
  define the various roles of our columns:
  - NUMeric column names start with an upper case letter. All
    other columns are SYMbolic.
  - Names ending with "+" or "-" are things we want to maximize
    or minimize(respectively). 
  - Anything ending in "X" is a column we should ignore.
  - For example, here is some car data where the goals are
    `Lbs-,Acc+,Mpg+`; i.e. we want
    to minimize car weight and maximize our acceleration and 
    maximize fuel consumption.

        {Clndrs  Volume  HpX      Model  origin  Lbs-  Acc+  Mpg+}
        -------  ------  ---      -----  ------  ----  ----  ----
        {8       302     129      75     1       3169  12    10}
        {8       318     150      72     1       4135  13.5  20}
        {6       168     120      76     2       3820  16.7  20}
        {3       70      90       73     3       2124  13.5  20}
        {6       232     90       78     1       3210  17.2  20}
        {6       231     110      75     1       3039  15    20}
        {6       173     110      81     1       2725  12.6  20}
        {4       140     92       76     1       2572  14.9  30}
        {4       97      88       72     3       2100  16.5  30}
        {4       90      70       76     2       1937  14.2  30}
        {4       85      65       79     3       2020  19.2  30}
        {4       98      65       81     1       2045  16.2  30}
        {4       85      70       78     3       2070  18.6  40}





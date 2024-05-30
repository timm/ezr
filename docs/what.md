.

# Projects


## Redo Old Algorithms

| what | notes| needs| who|
|------|--| ---|------|
| KNN regression ||sktool | |
| KNN classification ||sktool | |
| NB ||sktool | |
| Cart ||sktool | |
| Kmeans ||sktool | |
| configuration | | | |
| hyper-parameter optimization | | | |
| apriori || | |
| multi-regression |apriori| | |
| multi-classification |apriori| | |
| DATA synthesis | | |  |
| Anomaly detection | includes runtime checking of "certification envelope" |synthesis | |
| Fairness || synthesis  | |

## Tools

|what | notes| needs | who|
|-----|--|------|----|
|Text tool| tokeniztion, stemming, markov chains, tf\*idf | |
|SktooL| translate data formats scikitlearn and DATA |
|evalsym| eval stats for classifiers |
|evalnum| eval stats for classifiers||
|evalfake| eval stats for data synthesis||
|missingy| handle case where the y values are actually empty| 
|missingx| handle case where some of the x columns are not known e.g. multiregression||


## Reading

|what | notes| needs | who|
|-----|--|------|----|
|acquisition functions| what acqusition functions are in the literature?| |
|sample sizes| who has what sample sizes for "limited learning"? | |
| privacy | what are SOTA methods?||

## Writing (lecture notes to do)

|what | notes| needs | who|
|-----|--|------|----|
|discretization  | | timm |

## Extend

| what | notes| needs | who |
|------|--|-----|-----|
| early stop |  |     |     |
| streaming| updating the model| | |
| runtime  cerification assurance | monitoring, planning  [google](https://scholar.google.com/scholar?q=runtime+Certificate+Envelope&hl=en&as_sdt=0%2C34&as_ylo=2014&as_yhi=) | |
| pivacy | | readings on privacy | |
| standard rig | ensembles, smote, hpo. can do all in one with our tools?|classifiers | |
| discretization| so many [methods](https://wires.onlinelibrary.wiley.com/doi/pdf/10.1002/widm.1173?casa_token=NTyydyjnWw0AAAAA%3AgWvpK6MHSEoHuCDPli-n3e153WReVvhg7jFo1OcKnUo6P07XGIoYhvxb3NiId88LaHlLHfgsoDoH9Q). are any of them better than min? | | |
| explanation tax | We have rule generation in current version. Not tested on N data sets. No check if it selects useful items. No comparison to other rule generation methods.  | discretization | |
| Acquire | Try different actuation functions (based on [these](https://drive.google.com/file/d/1wBomkbXmel1z5_XAkXOcbW6WZG74hQn6/view) [papers](https://rdcu.be/dIuj4) [here](https://rdcu.be/dIume) and [here](https://citeseerx.ist.psu.edu/document?repid=rep1&type=pdf&doi=7397180b88b40bb7185a165cbbfcc22d581f86c9) and [here](https://rdcu.be/dIume) or  [exploit/explore](https://drive.google.com/file/d/1wBomkbXmel1z5_XAkXOcbW6WZG74hQn6/view)  Recall that our training curve is initially steep then goes shallow. Can we se that? | |
| Text mining| recommendation system: reporduce zhe using [this data](https://github.com/fastread/src/tree/master/workspace/data) |text tool | |
| Nshot| Few shot /1 shot learning : compare to SMO (based on [this paper](https://drive.google.com/file/d/1wBomkbXmel1z5_XAkXOcbW6WZG74hQn6/view) and [these notes](https://github.com/txt/aa24/blob/main/docs/09size.md) | | Lohith |
| hyperband |smo+hyperband | | Andre |
| surrogate| Can SMO become a human surrogate?  | maybe text mining? | | |
| humans| SMO for a human surrogate, then (a) does human confuse AI?; (b) does AI confuse human? | | Andre, Sai Raj |
|strange| Tims’s strange optimization why does it work?  (Time to ablate everything? What can change and it all still works?) | | |
| neural | Neural architecture search. Warning: slow | | |

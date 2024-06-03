# Welcome to Easier AI


&copy; 2024 by Tim Menzies and the EZR, BSD2 license.

## About
**Analytics** is how we extract high-quality insights from low
quality data. Here, we  use a "less is more" approach to create a
simple, fast toolkit that can tackle complex problems with just a
few data points (using incremental sampling).  The tool supports
classification, regression, optimization, fairness, explanation,
data synthesis, privacy, compression, planning, monitoring, and
runtime certification (but not  generative tasks).  For all these
tasks, our  minimal data usage simplifies verification.

The lesson from all this work is not everything can be simplified,
but many things can. When simplicity works, we should embrace it.
Who can argue against that?

### Audience
We write this  for programmers (or those that teach programmers).
Here, we show the most we  can do with AI, using the least amount
of code.

In our own work, this material is used to teach a one semester
graduate class in SE for AI.

### About the Authors
This work was written by the EZR mob (students from North Carolina
State University, USA) in a two-month hackathon June,July 2024.

That work was coordinated  by Tim Menzies, a professor of Computer
Science at NC State University (USA).  Tim is the Editor-in-Chief
of the Automated Software Engineering journal; an IEEE Fellow; and
the recipient of over over 13 million in grant money and industrial
contracts.  In the literature, Google Scholar ranks him as \#2 for
AI for SE and software cost estimation, \#1 for defect prediction,
and \#3 for software analytics.  He has graduated 50 research
students-by-thesis (including 20 Ph.D.s).  This work is reversed
engineered from the work of those students, who have explored
applications of analytics for spacecraft control, fairness,
explanation, configuration, cloud computing,  security, literature
reviews, technical  debt,  vulnerability prediction, defect prediction,
effort estimation,  and the management of open source software
projects.

### Profits from this Work
All profits from this work will be donated to the 
[Direct Relief & Direct Relief Foundation](https://directrelief.org)
to improve the health and lives of people affected by poverty or
emergency situations by mobilizing and providing essential medical
resources needed for their care.

## Quick Start

### Install

```
git clone http://github.com/timm/ezr
chmod +x ezr.py
./ezr.py -R all; echo "errors: $?"
```
This should generate a lot of output, then report zero errors.

### Check what you know

Before you read this code, 
if you are a Data Mining newbie, 
you might want to brush up on
[some data mining concepts](xxx).

### Do you Know your Python?
If you are a Python newbie, before you read the code, you might want to 
brush up on:

- Regular expressions                 (the [re](https://www.w3schools.com/python/python_regex.asp) package)
- Some of the dunder methods such as [\_\_repr\_\_](https://www.geeksforgeeks.org/python-__repr__-magic-method/?ref=ml_lbp)

Also, this code makes
extensive use of  

a.                 [Destructuring](https://blog.ashutoshkrris.in/mastering-list-destructuring-and-packing-in-python-a-comprehensive-guide)   
b. some       [other Python tricks](https://www.datacamp.com/tutorial/python-tips-examples)         
c. some  common [Python one-liners](https://allwin-raju-12.medium.com/50-python-one-liners-everyone-should-know-182ea7c8de9d)   
d. some other          [one-liners](https://github.com/Allwin12/python-one-liners?tab=readme-ov-file#unpacking-elements)

| # | Note| 
---|----|
|b4|generators|
|b16| leading underscore|
|b18| \_\_name\_\_ == “\_\_main\_\_”}
|b26| exception handling|
|b28| args & kwargs|
|c4| swap to values|
|c11| combine nested lists to a single list|
|c15| List comprehension using “for” and “if”|
|c17, c18, c19 | list, dictionary and set compreshsions|
|c20| if-else (ternery)|
|c23| lambda bodies|
|c45| sort dictionary with values|
|d| unpacking elements|

You might also want to review
[Python type hints](https://realpython.com/python-type-checking/).

## Contents
- [Introduction (all you need is less)](/docs/less.md)
- Bacground
  - Just  enough SE
  
## Software Engineering Notes
### Idioms
#### Config from __doc__
#### Types
#### Tests
test driven development;

### Python
#### \*lst,\* *kw

#### __dict__ 

the o class

#### Meta Programming: magic methds

##### __repr___

#### Regular Expressions


#### Comprehensions

#### List Comprehensions

#### Dictionary Comprehensions


```python
def a(): return 1
```

## Knowledge Engineering Notes

## References

# Easier  AI (just the important bits)


&copy; 2024 Tim Menzies, timm@ieee.org     
BSD-2 license. Share and enjoy.  

----------------------------------

For over two decades, I have been mentoring people about SE and AI.
When you do that, after a while, you realize:

- When it is all said and done, you only need  a dozen or so cool tricks;
- Other people really only need a  few dozen or so bits of AI theory;
- Everyone  could have more fun, and get more done, if we avoided
  the same dozen or so traps.

So I decided to write down that theory and those tricks and    traps
(see below).  I took some XAI code (explainable AI) I'd written for
semi-supervised multiple-objective optimization. Then I wrote notes
on any part of the code where  I had spent time helping helping
people with  those tricks, theory and traps.

Here is how the notes are labelled. For way-out ideas, read the 500+ ones.
For good-old-fashioned command-line warrior stuff, see 100-200

- Odd number items are about SE;
- So even numbers are about AI;
- 

|Anit-patterns<br>(things not to do) | SE system | SE coding | AI coding | AI theory<br>(standard) | New AI ideas| 
|:----------------------------------:|:---------:|:---------:|:---------:|:-----------------------:|:-----------:|
|00 - 99                             | 100 - 199 |  200-299  | 300-399   | 400 - 499               |  500-599    | 


One more thing.  The SE and AI literature is full of bold experiments
that try a range of new ideas.  But some new ideas are better than
others. With all little time, and lots of implementation experience,
we can focus of which  ideas offer the "most bang per buck".

Share and enjoy.

## Setting Up

### Get some example data

### Installation

First get some test data:

    git clone http://github.com/timm/data

Just grab the code:

    git clone http://github.com/timm/ezr
    cd ezr/src
    python3 -B ezr.py -t path2data/misc/auto93.csv -e all

Or install from local code (if you edit the code, those changes are
instantly accessible):

    git clone http://github.com/timm/ezr
    cd ezr
    pip [-e] install ./setup.py
    ezr -t path2data/misc/auto93.csv -e all # test the isntall

Install from the web. Best if you want to just want to import the code,
the write you own extensions

    pip install ezr
    ezr -t path2data/misc/auto93.csv -e all # test the install


###  Running the code 

This code has lots of
`eg.xxx()` functions. Each of these can be called on the command line
using, say:

     python3 -B ezr.py -e klass      # calls the eg.klass() function

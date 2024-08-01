&copy; 2024 Tim Menzies, timm@ieee.org     
BSD-2 license. Share and enjoy.  

----------------------------------

For over two decades, I have been mentoring people
 about SE and AI.  When you do that, after
a while, you realize:

- When it is all said and done, you only have a dozen or so cool tricks;
- Other people really only need a  few dozen or so bits of AI theory;
- Everyone  could have more fun if we avoided the same 
  dozen or so traps.

So I decided to write down that theory and those tricks and    traps.
I took some XAI code (explainable AI) I'd written for semi-supervised
multiple-objective optimization. Then I wrote notes on any
part of the code where  I had spent time helping helping people
with  those tricks, theory and traps.

Those notes  divided into five groups of things about AI and SE
that you might want to learn:

- <i class="_ikon"></i>  &nbsp; &nbsp; SE system issues
- <i class="_tools"></i> &nbsp; &nbsp; SE coding  
- <i class="_robot"></i> &nbsp;        AI coding 
- <i class="_flask"></i> &nbsp; &nbsp; AI theory 
- <i class="_skull"></i> &nbsp; &nbsp; Anti-pattern (things not to do)

So here is my code, annotated with those  notes. 
For those who want to try some exercises along the way, watch for the icon

- <i class="_todo"></i> This icons comes with a pointer to some small
  [homeworks](https://github.com/timm/ezr/tree/main/docs/hw)


Share and enjoy.

## Setting Up

### Installation

First get some test data:

    git clone http://github.com/timm/data

Just grab the code:

    git clone http://github.com/timm/ezr
    cd ezr/src
    python3 ezr.lua -t path2data/misc/auto93.csv -e all

Or nstall from local code (if you edit the code, those changes are
instantly accessible):

    git clone http://github.com/timm/ezr
    cd ezr
    pip [-e] install ./setup.py
    ezr -t path2data/misc/auto93.csv -e all # test the isntall

Install from the web. Best if you want to just want to import the code,
the write you own extensions

    pip install ezr
    ezr -t path2data/misc/auto93.csv -e all # test the install

<i class="_todo"></i>   _Packaging tools (pip) enables easy sharing of code.
  [Try it yourself](https://github.com/timm/ezr/tree/main/docs/hw/package.md)_.


###  Running the code 

This code has lots of
`eg.xxx()` functions. Each of these can be called on the command line
using, say:

     lua ez.lua -e klass      # calls the eg.klass() function

asdasasd 

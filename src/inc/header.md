# Scripting AI (just the important bits)

&copy; 2024 Tim Menzies, timm@ieee.org    
BSD-2 license. Share and enjoy.  

----------------------------------

I've had two decades now ot teaching people about SE and AI.  After
a whole you realize that:

- you only have a few  dozen cool tricks;
- other people really only need to know a  dozen or so bits of AI theory
- and other people could save a lot of time, if they knew to avoid the same one or two dozen traps.

So I decided to write down that theory and those tricks, tips and  traps. I took some XAI code (explainable AI)
I'd written for semi-supervised multiple-objective optimization. Then I wrote little notes
on any part of the code
where I often spend time helping helpong people about the tricks, theory and traps.

The results were two lists of notes that I you might want to elan you might not know already,
and which maybe you that I think you need to know. One list is about
the mechanics of software engineering (e.g. some interesting Python stuff) and the other
was about AI and data mining.

Here is that code, annoted with those 
Some kinds of AI and very easy to script. Let me show you how.

Here
we code up an explanation system for semi-supervised
multi-objective optimization. Internally, this is coded via
sequential model optimization and
membership query synthesis. 

Sounds complicated, right?  But it ain't. In fact, as shown below,
all the above is just a hundred lines of code (caveat: provided  you are using
the right  underlying object model). 

Which raised the question: what
else is similarly  simple? How many of our complex problems... aren't?
My challenge to you is this: please go and find out. That is, take  a working system,
see what you can throw away (while the reaming system is still useful and fast).
Let me know happens  so I can add your fantastic new, and simple,
idea to this code (and add you to the author list).

For
access to this file (ez.lua), see [github.com/4src/lua](http://github.com/4src/lua).

Since this code are showing off simplicity, we will use Lua for the
implementation.  Lua is  easy to learm, is resource light, and
compiles everywhere (for more on Lua see
https://learnxinyminutes.com/docs/lua/).  The best way to learn
this code is port it to Python, Julia, Java or  whatever is you favorite
language.

Since this code is meant to show off things, this code has lots of
`eg.xxx()` functions. Each of these can be called on the command line
using, say:

    lua ez.lua -e klass      # calls the eg.klass() function

Note that these `eg` examples can be used to guide your port to your favorite language.
Your first step could be to get the first `eg` working, then the second, then the
third etc. And at each step you could compare what you are getting to what comes out of my code.



:- [d].

report(P) :- 
   findall(P, P,L),
   length(L,N),
   format("~w ~w ~n",[P,N]).

good(File,Rx,Sample,Mu,Tiny):-
   d(File,Rank,Rx,Sample,Mu,Tiny), Sample =< 100, member(Rank,[0,1,2]).

great(File,Rx,Sample1):-
  good(File,Rx,Sample1,_,_),
  \+ (( good(File,Rx1,Sample2,_,_), %
        Sample2 < Sample1)).

% go:-
%   setof(T,F^R^X^D^d(F,R,T,X,D),L),
%   forall(member(T,L), report(beaten(T))),
%   forall(member(T,L), report(S,winner(T,S))).
%
:- great(File,Rx,Sample), print(great(File,Rx,Sample)),nl,fail.

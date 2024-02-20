:- [d].

report(P) :- 
   findall(P, P,L),
   length(L,N),
   format("~w ~w ~n",[P,N]).

good(File,Rank,Rx,Sample,Mu,Tiny):-
   d(File,Rank,Rx,Sample,Mu,Tiny), Sample =< 100, member(Rank,[0,1,2]).

great(File,Rx1,Sample1):-
  good(File,Rank1,Rx1,Sample1,_,_),
  \+ (( good(File,Rank2,_,Sample2,_,_),
        Sample2 < Sample1, Rank2 =< Rank1)).

go :- great(File,Rx,Sample), print(great(File,Rx,Sample)),nl,fail.
:- ignore(go),halt.

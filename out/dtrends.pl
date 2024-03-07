% d(file,rank,rx,n,mu,_).
:- [d].

range1(F,M):- d(F,_,_,_,M,_).
file1(F) :- d(F,_,_,_,_,_).
rx1(R)   :- d(_,_,R,_,_,_).

range(F,Min,Max) :- setof(S0,S0^range1(F,S0),[Min|L]),last(L,Max).
file(F) :- setof(F0,F0^file1(F0),L), member(F,L).
rx(R)   :- setof(R0,R0^rx1(R0),  L), member(R,L).

last([H],H).
last([_,H1|T],Last) :- last([H1|T],Last).

two(F,Rx, (N2,D2)):-
  range(F,Lo,Hi),
  d(F,_,base,_,_,_),
  d(F,_,Rx,  N1,D1,_),
  N2 is N1, %(N0+0.0001),
  D2 is (D1 - Lo)/(Hi - Lo + 0.0001).

twos(F,Rx,L) :- 
  atomics_to_string([Rx,F],F1),
  atomics_to_string(["trends",F1],"/",Path0),string_to_atom(Path0,Path),
  tell(Path),
  setof(X,F^Rx^two(F,Rx,X),L),
  forall( member((A,B),L),
          format("~5f\t~5f\n",[A,B])),
  told.


go :- file(F), rx(X),  once(twos(F,X,_)),fail.
go.

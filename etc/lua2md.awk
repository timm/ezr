BEGIN {yes=0; com=0}
/^-- ##/ { yes=1 ; end=""}
! yes   { next }
g/^-- / && !com { print end; print; next}

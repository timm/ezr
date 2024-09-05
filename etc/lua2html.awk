BEGIN                          { STOP="" }
NR < 3                         { next } 
comment($0)  && !comment(last) { printf STOP }
!comment($0) && comment(last)  { print "\n```lua"; STOP="```\n\n" }
END                            { if(!comment(last)) print STOP }
                               { last = $0;
                                 sub(/^-- ?/,"")
                                 print $0
                               }

function comment(s) { return s ~ /^-- ?/ }

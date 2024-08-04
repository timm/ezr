BEGIN                         { STOP="" }
NR < 3                        { next } 
sub(/"""/,"")                 { three= 1- three }
three                         { $0 = "# " $0 }
sub(/^@of."/,"#")             { sub(/"./,"") }
comment($0) && !comment(last) { printf STOP }
!comment($0) && comment(last) { print "\n```python"; STOP="```\n\n" }
END                           { if(!comment(last)) print STOP }
                              { last = $0;
                                sub(/^# ?/,"")
                                print $0
                              }

function comment(s) { return s ~ /^# ?/ }

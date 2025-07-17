BEGIN { on=0 }
END   { if (on) print "```" }
{ if ($0 ~ /^    /) {
    if (!on) print "```python"; on=1
    sub(/^    /, ""); print
  } else {
    if (on) print "```"; on=0
    print } }

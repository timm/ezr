# do it for each treatment
BEGIN   { FS="[,:/]" }

function n(x) { return (x - $(NF-1))/($NF - $(NF-1)) }

/^ /    { gsub(/[ \t]*/,"")
          print FILENAME, $2, $3, n($4), n($5) }

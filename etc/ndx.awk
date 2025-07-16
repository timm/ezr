#!/usr/bin/gawk -f

BEGIN {
    # alphabetical iteration
    PROCINFO["sorted_in"] = "@ind_str_asc"
    # stop-list from heuristics 1–6
    split(\
      "False None True and as assert break class continue def del elif else except finally " \
      "for from global if import in is lambda nonlocal not or pass raise return try while with yield " \
      "__annotations__ __class__ __dict__ __doc__ __init__ __name__ __repr__ " \
      "the this any all many first me it go now " \
      "id s1 r1 r2 n1 m1 m2 " \
      "get set add print map list len range split join " \
      "i x y idx tmp err errs history",
      stop, " "\
    )
}

{
    # strip comments & strings
    gsub(/#.*|"(\\.|[^"])*"|'(\\.|[^'])*'/, "")
    # collect each symbol ≥2 chars
    while (match($0, /\<[A-Za-z_][A-Za-z0-9_]*\>/)) {
        s = substr($0, RSTART, RLENGTH)
        if (length(s)>1 && !(s in stop))
            idx[s] = idx[s] ? idx[s] "," NR : NR
        $0 = substr($0, RSTART + RLENGTH)
    }
}

END {
    # find longest symbol name for alignment
    max = 0
    for (s in idx) if (length(s) > max) max = length(s)

    # print sorted, aligned, wrapped at 70 chars
    for (s in idx) {
        out = sprintf("%-*s: %s", max, s, idx[s])
        while (length(out) > 70) {
            print substr(out, 1, 70)
            out = sprintf("%*s%s", max+2, "", substr(out, 71))
        }
        print out
    }
}


# include.awk
BEGIN { in = 0 }
in==0 && match($0, /^```[a-zA-Z]+\s+\S+/) {
	print
	split($0, f, " ")
	length(f) >= 3 ? x(f[2], f[3]) : (while ((getline < f[2]) > 0) print; close(f[2]))
	in = 1; next
}
in && /^```/ { print; in = 0; next }
in { next }
1

function x(file, pat) {
	while ((getline l < file) > 0)
		if (l ~ pat) {
			print l
			while ((getline l < file) > 0 && l !~ /^$/) print l
			break }
	close(file) }


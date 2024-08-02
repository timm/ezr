cat <<EOF
<!DOCTYPE html>
<html lang="en">
<head>
<title>$1</title>
<meta charset="UTF-8">
<link rel="icon" type="image/x-icon" href="favicon.ico">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/vs.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/python.min.js"></script>
<script>hljs.highlightAll();</script>
<link rel="stylesheet" href="ezr.css">
</head><body>
<small><p align="left"><a href="home">home</a> :: <a href="issues">issues</a> :: <a href="license">license</a>
</p></small>
<h1>$1</h1>
<hr>
EOF

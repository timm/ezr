// tiny python highlighter for pre.py blocks; no dependencies
document.querySelectorAll('pre.py').forEach(function (p) {
  var esc = function (s) {
    return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  };
  p.innerHTML = p.textContent.split('\n').map(function (line) {
    var i = line.indexOf('#');
    var code = i < 0 ? line : line.slice(0, i);
    var com  = i < 0 ? ''   : line.slice(i);
    code = esc(code)
      .replace(/\b(def|return|while|for|in|if|else|not|and|or|lambda|None|True|False)\b/g,
               '<span class="k">$1</span>')
      .replace(/(^|[^\w.])(\.?\d+(?:\.\d+)?(?:e-?\d+)?)/g,
               '$1<span class="n">$2</span>');
    if (com) com = '<span class="c">' + esc(com) + '</span>';
    return code + com;
  }).join('\n');
});

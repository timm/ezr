// click-to-popup for figure thumbnails; click anywhere to close
document.querySelectorAll('a.pop').forEach(function (a) {
  a.addEventListener('click', function (e) {
    e.preventDefault();
    var o = document.createElement('div');
    o.className = 'overlay';
    var img = document.createElement('img');
    img.src = a.getAttribute('href');
    o.appendChild(img);
    o.addEventListener('click', function () { o.remove(); });
    document.addEventListener('keydown', function esc(ev) {
      if (ev.key === 'Escape') { o.remove(); document.removeEventListener('keydown', esc); }
    });
    document.body.appendChild(o);
  });
});

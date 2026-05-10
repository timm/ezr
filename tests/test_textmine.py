"""Textmine: CNB classifier and preprocessing."""
from conftest import *
from ezr import *
import textmine as tm

def test_cnb_like():
  data = Data(csv(need(EGCNB, "label!")))
  ws = tm.cnb(data)
  assert len(ws) >= 2

def test_cnb_sweep():
  f = need(EGCNB, "label!")
  for y in [10, 20, 40]:
    the.textmine.yes = the.textmine.no = y
    assert tm.text_mining(f)

def test_cnb_data():
  assert tm.text_mining(need(EGCNB, "label!"))

def test_cnb_active():
  assert tm.active(need(EGCNB, "label!"))

def test_tokenize():
  p = tm.tokenize(need(EGTXT, "abstract", "label"))
  assert len(p.docs) > 0 and len(p.docs[0].words) > 0

def test_nostop():
  p = tm.tokenize(need(EGTXT, "abstract", "label"))
  b = p.docs[0].words[:12][:]
  tm.nostop(p)
  removed = [w for w in b if w not in p.docs[0].words]
  assert removed

def test_stem():
  p = tm.nostop(tm.tokenize(need(EGTXT, "abstract", "label")))
  b = p.docs[0].words[:8][:]
  tm.stem(p)
  changed = sum(1 for a, b1 in zip(b, p.docs[0].words[:8]) if a != b1)
  assert changed > 0

def test_tfidf():
  p = tm.prepare(need(EGTXT, "abstract", "label"))
  assert len(p.top) >= 20
  assert all(s >= 0 for _, s in p.top)

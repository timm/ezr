"""Shared pytest fixtures and helpers."""
import sys, os, random
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ezr import *

EGOPT1   = Path.home() / "gits/moot/optimize/misc/auto93.csv"
EGCLASS1 = Path.home() / "gits/moot/classify/soybean.csv"
EGCLASS2 = Path.home() / "gits/moot/classify/diabetes.csv"
EGCNB    = Path.home() / "gits/moot/text_mining/reading/processed/Hall.csv"
EGTXT    = Path.home() / "gits/moot/text_mining/reading/raw/Hall.csv"

try:
  import pytest
  @pytest.fixture(autouse=True)
  def _seed(): random.seed(the.seed)
except ImportError: pass

def ready(file):
  """Shuffle, split data into train/test."""
  d = file if Data == type(file) else Data(csv(str(file)))
  random.shuffle(d.rows)
  half = len(d.rows) // 2
  return (d, clone(d, d.rows[:half][:the.few]), d.rows[half:])

def need(f, *cols):
  """Return str(f) if file exists with required header cols, else skip."""
  import pytest
  p = Path(f)
  if not p.exists(): pytest.skip(f"missing {f}")
  if cols:
    import textmine as tm
    if not all(c in next(tm._csv(str(p))) for c in cols):
      pytest.skip(f"{f} missing one of {cols}")
  return str(p)

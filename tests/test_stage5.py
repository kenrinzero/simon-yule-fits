"""Stage 5: the (4.2) pmf and sampler, tokenizer behaviour, and pins on the frozen run."""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import stage5 as s5  # noqa: E402


def test_42_pmf_telescopes():
    for x in (0.0, 0.2, -1.0):
        i = np.arange(1, 1001, dtype=float)
        assert abs(np.exp(s5.lp42(i, x)).sum() + (1 - x) / (1001 - x) - 1) < 1e-12


def test_42_sampler_survival():
    s = s5.draw42(0.2, 400_000, np.random.default_rng(3))
    for i in (1, 2, 5, 20):
        assert abs((s >= i).mean() - 0.8 / (i - 0.2)) < 0.003


def test_tokenizers_on_tricky_text():
    t = "don't well-known o'er bloom’s café 1904 _x_"
    t = t.replace("’", "'")
    assert s5.TOKENIZERS["T1"].findall(t) == ["don", "t", "well", "known", "o", "er", "bloom", "s", "café", "x"]
    assert s5.TOKENIZERS["T2"].findall(t) == ["don't", "well-known", "o'er", "bloom's", "café", "x"]
    assert s5.TOKENIZERS["T3"].findall(t) == ["don't", "well", "known", "o'er", "bloom's", "café", "x"]


def test_frozen_run_pins():
    s = json.loads((ROOT / "results" / "stage5-summary.json").read_text(encoding="utf-8"))
    assert s["gates"]["pass"] and s["B"] == 500
    r = s["results"]
    assert (r["eldridge"]["n"], r["eldridge"]["k"], r["eldridge"]["f1"], r["eldridge"]["f2"], r["eldridge"]["f3"]) == \
        (6002, 43989, 2976, 1079, 516)
    assert [r[t]["n"] for t in ("T1", "T2", "T3")] == [29021, 29776, 29737]
    assert s["predictions"] == dict(P16=True, P17=True, P18=True, P19=True, P20=False, P21=True)

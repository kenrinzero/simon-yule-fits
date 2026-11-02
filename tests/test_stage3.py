"""Stage 3: simulator and estimator unit checks, plus pins on the frozen-run summary."""
import json
import random
import sys
from pathlib import Path

import numpy as np
from scipy.stats import yulesimon

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import stage3 as s3  # noqa: E402


def test_section_ii_matches_yule_theory():
    a, k = 0.3, 100_000
    rho = 1 / (1 - a)
    p1, r21 = [], []
    for sd in range(20):
        sz = s3.stream_sizes(k, np.full(k, a), np.random.default_rng(sd))
        assert sz.sum() == k
        f = np.bincount(sz)
        p1.append(f[1] / sz.size); r21.append(f[2] / f[1])
    assert abs(np.mean(p1) - 1 / (2 - a)) < 0.003
    assert abs(np.mean(r21) - 1 / (2 + rho)) < 0.004


def test_case_ii_schedule_hits_n():
    # A2.2 clips alpha(t) at 1, so E[n] falls short at low beta: at most 4.9%
    # (Econometrica, beta=0.6) on the six real sets. Pinned here; stated in REPORT.md.
    for k, n in ((1124, 278), (22939, 6891), (3398, 1325), (1759, 721), (43989, 6002), (260430, 29899)):
        for beta in (0.9, 0.6):
            al = s3.alpha_schedule(k, n, beta)
            short = (n - al.sum()) / n
            assert al.max() <= 1.0 and -1e-9 <= short < (0.001 if beta == 0.9 else 0.05)


def test_section_iii_length_rule():
    k, n = 3398, 1325
    sz = s3.slice_sizes(k, n / k, 3 * k, np.random.default_rng(5), random.Random(6))
    assert sz.sum() <= k and sz.min() >= 1


def test_loglik_matches_scipy():
    x = np.array([1, 1, 2, 3, 7, 40], dtype=float)
    xs, ms = np.unique(x, return_counts=True)
    for r in (0.8, 1.3, 2.5):
        assert abs(s3.ll_full(r, xs, ms.astype(float)) - yulesimon.logpmf(x, r).sum()) < 1e-9
        hx = xs[xs < 4]; hm = ms[xs < 4].astype(float)
        want = yulesimon.logpmf(x[x < 4], r).sum() + (x >= 4).sum() * np.log(yulesimon.sf(3, r))
        assert abs(s3.ll_cens(r, hx, hm, float((x >= 4).sum()), 4) - want) < 1e-9


def test_frozen_run_pins():
    s = json.loads((ROOT / "results" / "stage3-summary.json").read_text(encoding="utf-8"))
    assert not s["quick"]
    assert all(v["passes"] for v in s["selftest"].values())
    joint = sorted(k for k, v in s["nulls"].items() if v["joint"])
    assert joint == ["chicago__II_beta0.6", "chicago__II_beta0.7", "econometrica__III_B3k",
                     "econometrica__II_beta0.9", "eldridge__III_B3k", "physicists__II_beta0.9"]
    for nm in ("chicago", "chem", "physicists", "econometrica", "eldridge", "ulysses"):
        assert not s["nulls"][f"{nm}__II_beta1.0"]["G"]["inside"]

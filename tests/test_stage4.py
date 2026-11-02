"""Stage 4: pmf identities, an independent GIGP check, sampler sanity, and pins on the frozen run."""
import json
import math
import sys
from pathlib import Path

import mpmath as mp
import numpy as np
from scipy.stats import yulesimon

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import stage4 as s4  # noqa: E402

M = s4.BY_NAME


def test_yule_matches_scipy():
    x = np.arange(1, 50, dtype=float)
    assert np.allclose(M["yule"].lp(x, 1.3), yulesimon.logpmf(x, 1.3), atol=1e-12)


def test_nesting_identities():
    d = s4.data_from_sets()["chem"]
    y = s4.loglik(M["yule"], [1.277], d)
    assert abs(s4.loglik(M["waring"], [1.277, 0.0], d) - y) < 1e-6
    assert abs(s4.loglik(M["cutoff"], [1.277, 1.0], d) - y) < 1e-6
    assert abs(s4.loglik(M["gigp"], [0.7, 1e-9, 0.95], d) - s4.loglik(M["enb"], [0.7, 0.95], d)) < 1e-6


def test_gigp_against_mpmath():
    nu, a, t = -0.5, 0.8, 0.97
    mp.mp.dps = 40
    s = mp.sqrt(1 - t)
    f = lambda j: (1 - t) ** (nu / 2) / mp.besselk(nu, a * s) * (a * t / 2) ** j / mp.factorial(j) * mp.besselk(nu + j, a)
    f0 = f(0)
    for j in (1, 2, 5, 40, 300):
        want = float(mp.log(f(j) / (1 - f0)))
        assert abs(M["gigp"].lp(np.array([float(j)]), nu, a, t)[0] - want) < 1e-9


def test_table_sampler_mean_small_support():
    # log-series at theta=0.5: E[X] = -theta/((1-theta) log(1-theta))
    s = s4.TableSampler(M["logseries"], [0.5]).draw(200_000, np.random.default_rng(1))
    assert abs(s.mean() - (-0.5 / (0.5 * math.log(0.5)))) < 0.01


def test_frozen_run_pins():
    s = json.loads((ROOT / "results" / "stage4-summary.json").read_text(encoding="utf-8"))
    assert s["reps"] == 500 and all(not g["failed"] for v in s["gof"].values() for g in v.values())
    assert s["sichel"]["grade"] == "reproduced"
    ch = s["fits"]["chem"]
    assert ch["enb"]["aic"] < ch["yule"]["aic"]  # P7a failed
    assert min(ch, key=lambda m: ch[m]["aic"]) == "gigp"
    grades = {k: s["gof"][k]["yule"]["x2_p"] >= 0.05 for k in ("chicago", "chem", "physicists", "econometrica")}
    assert grades == dict(chicago=False, chem=False, physicists=True, econometrica=False)
    el = s["fits"]["eldridge"]
    assert min(el, key=lambda m: el[m]["aic"]) == "waring"

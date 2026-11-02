"""Stage 4 (PREREGISTRATION Amendment 3): the Yule against its rivals on the
untruncated source tables. Fits, nesting/sampler gates, likelihood-ratio and
Vuong comparisons, parametric-bootstrap goodness of fit, and the Sichel theta.

    python src/stage4.py --gates          # A3.7 gates only
    python src/stage4.py --workers 6      # gates, fits, bootstrap, summary
"""
import argparse
import itertools
import json
import math
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from scipy import stats
from scipy.optimize import brentq, minimize, minimize_scalar
from scipy.special import gammaln, hyp2f1, kve, zeta

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from stage3 import load_sets  # noqa: E402

MASTER_SEED = 19551102
B_BOOT = 500
C = 11
SETS = ["chicago", "chem", "physicists", "eldridge", "econometrica"]
SICHEL_THETA = 0.96876
TOP = 1.0 - 1e-12
OUT = ROOT / "results" / "stage4"


# ---------------------------------------------------------------- log-pmfs on x >= 1
def lp_yule(x, r):
    return math.log(r) + gammaln(x) + gammaln(r + 1) - gammaln(x + r + 1)


def lp_zeta(x, s):
    return -s * np.log(x) - math.log(zeta(s, 1))


def lp_logser(x, t):
    return x * math.log(t) - np.log(x) - math.log(-math.log1p(-t))


def lp_enb(x, r, t):
    # Engen's extended NB (r in (-1, 0)) and the zero-truncated NB (r > 0).
    # gammaln is log|Gamma|; for r < 0 Gamma(r) and the denominator are both negative.
    logden = 0.0 if t >= 1.0 else math.log(abs(math.expm1(-r * math.log1p(-t))))
    return gammaln(x + r) - gammaln(x + 1) - gammaln(r) + x * math.log(t) - logden


def lp_sichel(x, t):
    return lp_enb(x, -0.5, t)


def lp_waring(x, r, c):
    return math.log(r) + gammaln(1 + c + r) - gammaln(1 + c) + gammaln(x + c) - gammaln(x + 1 + c + r)


def lp_cutoff(x, r, b):
    norm = b / (r + 1) * hyp2f1(1.0, 1.0, r + 2.0, b)
    return gammaln(x) + gammaln(r + 1) - gammaln(x + r + 1) + x * math.log(b) - math.log(norm)


def log_k_orders(nu, z, jmax):
    """log K_{nu+j}(z) for j = 0..jmax by the forward recurrence (stable for K)."""
    out = np.empty(jmax + 1)
    k0, k1 = kve(nu, z), kve(nu + 1, z)
    acc = math.log(k0) - z
    out[0] = acc
    ratio = k1 / k0  # K_{nu+1}/K_nu
    for j in range(jmax):
        acc += math.log(ratio)
        out[j + 1] = acc
        ratio = 1.0 / ratio + 2.0 * (nu + j + 1) / z
    return out


def lp_gigp(x, nu, a, t):
    """Sichel's GIGP (Bogachev et al. 2023, eq. 3.1), zero-truncated."""
    xi = np.asarray(x).astype(np.int64)
    lk = log_k_orders(nu, a, int(xi.max()))
    zs = a * math.sqrt(1.0 - t)
    lkb = math.log(kve(nu, zs)) - zs
    base = 0.5 * nu * math.log1p(-t) - lkb
    log1mf0 = math.log(-math.expm1(base + lk[0]))
    return base + xi * math.log(0.5 * a * t) - gammaln(xi + 1.0) + lk[xi] - log1mf0


class Model:
    def __init__(self, name, lp, boxes, starts):
        self.name, self.lp, self.boxes, self.starts = name, lp, boxes, starts
        self.npar = len(boxes[0])


def _grid(*vals):
    return [list(v) for v in itertools.product(*vals)]


MODELS = [
    Model("yule", lp_yule, [[(0.05, 20.0)]], None),
    Model("zeta", lp_zeta, [[(1.0001, 10.0)]], None),
    Model("logseries", lp_logser, [[(1e-9, TOP)]], None),
    Model("sichel", lp_sichel, [[(1e-9, 1.0)]], None),
    Model("waring", lp_waring, [[(0.05, 20.0), (-0.999, 50.0)]],
          [_grid((0.5, 1.5, 4.0), (-0.5, 0.5, 5.0))]),
    Model("cutoff", lp_cutoff, [[(0.05, 20.0), (1e-3, 1.0)]],
          [_grid((0.5, 1.5, 4.0), (0.9, 0.99, 0.9999))]),
    Model("enb", lp_enb, [[(-0.999, -1e-6), (1e-9, 1.0)], [(1e-6, 50.0), (1e-9, TOP)]],
          [_grid((-0.8, -0.4, -0.1), (0.5, 0.9, 0.99)), _grid((0.1, 1.0, 5.0), (0.5, 0.9, 0.99))]),
    Model("gigp", lp_gigp, [[(-5.0, 5.0), (1e-6, 50.0), (1e-9, TOP)]],
          [_grid((-2.0, -0.5, 1.0), (0.01, 0.5, 5.0), (0.5, 0.9, 0.99))]),
]
BY_NAME = {m.name: m for m in MODELS}


# ---------------------------------------------------------------- data and likelihood
def data_from_sets():
    out = {}
    for name, s in load_sets().items():
        if name not in SETS:
            continue
        if "full" in s:
            xs = np.array(sorted(s["full"]), dtype=float)
            ms = np.array([s["full"][int(v)] for v in xs], dtype=float)
            out[name] = dict(kind="full", xs=xs, ms=ms, n=s["n"], k=s["k"])
        else:
            hx = np.arange(1, C, dtype=float)
            hm = np.array([s["head"][i] for i in range(1, C)], dtype=float)
            out[name] = dict(kind="cens", hx=hx, hm=hm, mge=float(s["cens"]), n=s["n"], k=s["k"])
    return out


def data_from_sample(sample, kind):
    xs, ms = np.unique(sample, return_counts=True)
    xs, ms = xs.astype(float), ms.astype(float)
    if kind == "full":
        return dict(kind="full", xs=xs, ms=ms, n=int(ms.sum()), k=int((xs * ms).sum()))
    hm = np.array([ms[xs == i].sum() for i in range(1, C)], dtype=float)
    return dict(kind="cens", hx=np.arange(1, C, dtype=float), hm=hm, mge=float(ms[xs >= C].sum()),
                n=int(ms.sum()), k=None)


def log_surv(model, p, c=C):
    head = np.exp(model.lp(np.arange(1, c, dtype=float), *p)).sum()
    return math.log1p(-head) if head < 1 else -np.inf


def loglik(model, p, d):
    if d["kind"] == "full":
        return float(np.sum(d["ms"] * model.lp(d["xs"], *p)))
    ll = float(np.sum(d["hm"] * model.lp(d["hx"], *p)))
    return ll + (d["mge"] * log_surv(model, p) if d["mge"] else 0.0)


def pointwise(model, p, d):
    """Per-cell log-likelihood contributions and multiplicities (for Vuong)."""
    if d["kind"] == "full":
        return model.lp(d["xs"], *p), d["ms"]
    return np.append(model.lp(d["hx"], *p), log_surv(model, p)), np.append(d["hm"], d["mge"])


def _safe_negll(model, d):
    def f(v):
        try:
            ll = loglik(model, list(v), d)
        except (ValueError, OverflowError, ZeroDivisionError, FloatingPointError):
            return 1e300
        return -ll if np.isfinite(ll) else 1e300
    return f


def fit(model, d):
    f = _safe_negll(model, d)
    best = None
    if model.npar == 1:
        lo, hi = model.boxes[0][0]
        res = minimize_scalar(lambda v: f([v]), bounds=(lo, hi), method="bounded",
                              options={"xatol": 1e-11})
        best = ([float(res.x)], -float(res.fun))
    else:
        for box, starts in zip(model.boxes, model.starts):
            for x0 in starts:
                with np.errstate(all="ignore"):
                    res = minimize(f, x0, method="L-BFGS-B", bounds=box,
                                   options={"maxiter": 500, "ftol": 1e-13, "gtol": 1e-9})
                if res.fun < 1e299 and (best is None or -res.fun > best[1]):
                    best = ([float(v) for v in res.x], -float(res.fun))
    if best is None:
        raise RuntimeError(f"no finite fit for {model.name}")
    box = [b for b in model.boxes if all(lo <= v <= hi for v, (lo, hi) in zip(best[0], b))][0]
    at_bound = any(min(abs(v - lo), abs(hi - v)) <= 1e-6 * max(1.0, abs(v)) for v, (lo, hi) in zip(best[0], box))
    return dict(params=best[0], ll=best[1], at_bound=at_bound)


# ---------------------------------------------------------------- samplers
class TableSampler:
    """Inverse-CDF sampler from the pmf on 1..X, with a Pareto continuation for the tail mass."""

    def __init__(self, model, p, X=10 ** 6):
        x = np.arange(1, X + 1, dtype=float)
        pm = np.exp(model.lp(x, *p))
        cdf = np.cumsum(pm)
        self.tail = max(0.0, 1.0 - cdf[-1])
        if self.tail < 1e-12:
            self.tail = 0.0
            cdf /= cdf[-1]
        self.cdf, self.X = cdf, X
        if self.tail:
            s_half = self.tail + pm[X // 2:].sum()
            self.gamma = math.log(s_half / self.tail) / math.log(2.0)

    def draw(self, n, rng):
        u = rng.random(n)
        out = np.searchsorted(self.cdf, u, side="right").astype(np.int64) + 1
        hit = out > self.X
        if hit.any():
            v = rng.random(int(hit.sum()))
            out[hit] = np.minimum(np.floor(self.X * v ** (-1.0 / self.gamma)) + 1, 1e15).astype(np.int64)
        return out


def exact_sample(name, p, n, rng):
    """Mixture/closed-form samplers, used only to check the pmfs (gate A3.7)."""
    if name == "yule":
        return stats.yulesimon.rvs(p[0], size=n, random_state=rng)
    if name == "zeta":
        return stats.zipf.rvs(p[0], size=n, random_state=rng)
    if name == "logseries":
        return rng.logseries(p[0], n)
    if name == "waring":  # I - 1 ~ beta-negative-binomial(r=1+c, alpha=rho, beta=1)
        q = rng.beta(p[0], 1.0, n)
        return rng.negative_binomial(1.0 + p[1], q) + 1
    if name == "cutoff":  # Yule thinned by b^(x-1)
        out = np.empty(0, dtype=np.int64)
        while out.size < n:
            y = stats.yulesimon.rvs(p[0], size=2 * n, random_state=rng)
            out = np.concatenate([out, y[rng.random(y.size) < p[1] ** (y - 1.0)]])
        return out[:n]

    def _ztrunc(gen):
        out = np.empty(0, dtype=np.int64)
        while out.size < n:
            y = gen()
            out = np.concatenate([out, y[y > 0]])
        return out[:n]

    if name == "enb" and p[0] > 0:
        return _ztrunc(lambda: rng.negative_binomial(p[0], 1.0 - p[1], 4 * n))
    if name == "gigp":  # Poisson mixed over GIG(nu, a=2(1-t)/t, b=alpha^2 t/2)
        nu, a, t = p
        ga, gb = 2.0 * (1.0 - t) / t, a * a * t / 2.0
        lam = lambda: stats.geninvgauss.rvs(nu, math.sqrt(ga * gb), scale=math.sqrt(gb / ga),
                                            size=4 * n, random_state=rng)
        return _ztrunc(lambda: rng.poisson(lam()))
    return None


def x2_cells(sample_or_data, model, p, n):
    """Pearson X^2 on Simon's cells 1..10 and >= 11."""
    if isinstance(sample_or_data, dict):
        d = sample_or_data
        if d["kind"] == "full":
            obs = np.array([d["ms"][d["xs"] == i].sum() for i in range(1, C)] + [d["ms"][d["xs"] >= C].sum()])
        else:
            obs = np.append(d["hm"], d["mge"])
    else:
        s = np.asarray(sample_or_data)
        obs = np.array([(s == i).sum() for i in range(1, C)] + [(s >= C).sum()], dtype=float)
    pr = np.exp(model.lp(np.arange(1, C, dtype=float), *p))
    exp_ = n * np.append(pr, max(0.0, 1.0 - pr.sum()))
    return float(np.sum((obs - exp_) ** 2 / exp_))


def ks_full(d, model, p, chunk=10 ** 6):
    """sup_x |F_emp(x) - F_model(x)| over x = 1..max. F_emp is flat between support points
    and F_model rises, so the sup is attained at a support point s_j or just before s_{j+1}.
    The model CDF is accumulated in chunks, so a sample max of 1e8 costs time, not memory."""
    s = d["xs"].astype(np.int64)
    fe = np.cumsum(d["ms"]) / d["n"]
    want = np.unique(np.concatenate([s, s - 1]))
    want = want[want >= 1]
    fm = np.empty(want.size)
    acc, lo, i = 0.0, 1, 0
    while i < want.size:
        hi = min(int(want[-1]), lo + chunk - 1)
        cdf = acc + np.cumsum(np.exp(model.lp(np.arange(lo, hi + 1, dtype=float), *p)))
        j = np.searchsorted(want, hi, side="right")
        fm[i:j] = cdf[want[i:j] - lo]
        acc, lo, i = cdf[-1], hi + 1, j
    at = dict(zip(want.tolist(), fm.tolist()))
    gaps = [at.get(int(s[0]) - 1, 0.0)]  # x < s_1, where F_emp = 0
    gaps += [abs(fe[j] - at[int(s[j])]) for j in range(s.size)]
    gaps += [abs(fe[j] - at[int(s[j + 1]) - 1]) for j in range(s.size - 1)]
    return float(max(gaps))


# ---------------------------------------------------------------- gates (A3.7)
GATE_PARAMS = {
    "yule": [[1.3]], "zeta": [[2.0]], "logseries": [[0.99]], "sichel": [[0.97]],
    "waring": [[1.3, 0.7], [1.3, -0.5]], "cutoff": [[1.3, 0.999], [1.3, 1.0]],
    "enb": [[-0.5, 0.97], [-0.5, 1.0], [0.7, 0.9]], "gigp": [[-0.5, 0.5, 0.97], [1.2, 2.0, 0.9]],
}


def gate_normalization(X=10 ** 6):
    rows = []
    for name, plist in GATE_PARAMS.items():
        m = BY_NAME[name]
        for p in plist:
            x = np.arange(1, X + 1, dtype=float)
            lp = m.lp(x, *p)
            body = float(np.exp(lp).sum())
            g1 = -(lp[-1] - lp[X // 2 - 1]) / math.log(2.0)  # pmf ~ x^(-g1) at the end
            tail = float(np.exp(lp[-1]) * X / (g1 - 1.0)) if g1 > 1.0 and np.isfinite(lp[-1]) else 0.0
            tot = body + tail
            rows.append(dict(model=name, params=p, total=tot, ok=abs(tot - 1.0) < 1e-6))
    return rows


def gate_nesting(d):
    rows = []
    for rho in (1.0, 1.277, 1.6):
        y = loglik(BY_NAME["yule"], [rho], d)
        rows.append(dict(check="waring c=0", rho=rho, diff=loglik(BY_NAME["waring"], [rho, 0.0], d) - y))
        rows.append(dict(check="cutoff b=1", rho=rho, diff=loglik(BY_NAME["cutoff"], [rho, 1.0], d) - y))
    for t in (0.9, 0.99):
        rows.append(dict(check="enb r->0 (r=1e-12)", theta=t,
                         diff=loglik(BY_NAME["enb"], [1e-12, t], d) - loglik(BY_NAME["logseries"], [t], d)))
        rows.append(dict(check="gigp alpha->0 (nu=0.7, alpha=1e-9)", theta=t,
                         diff=loglik(BY_NAME["gigp"], [0.7, 1e-9, t], d) - loglik(BY_NAME["enb"], [0.7, t], d)))
    rows.append(dict(check="sichel = enb(r=-0.5)", theta=0.97,
                     diff=loglik(BY_NAME["sichel"], [0.97], d) - loglik(BY_NAME["enb"], [-0.5, 0.97], d)))
    for r in rows:
        r["ok"] = abs(r["diff"]) < 1e-6
    # reported, not gated: the nu < 0 approach, where 1 - f0 -> 0 as alpha -> 0
    trend = [dict(alpha=a, diff=loglik(BY_NAME["gigp"], [-0.5, a, 0.97], d) - loglik(BY_NAME["enb"], [-0.5, 0.97], d))
             for a in (1e-2, 1e-4, 1e-6)]
    return rows, trend


def gate_samplers(n=100_000):
    rows = []
    rng = np.random.default_rng([MASTER_SEED, 999])
    for name, plist in GATE_PARAMS.items():
        m = BY_NAME[name]
        for p in plist:
            for how in ("exact", "table"):
                s = exact_sample(name, p, n, rng) if how == "exact" else TableSampler(m, p).draw(n, rng)
                if s is None:
                    continue
                x2 = x2_cells(s, m, p, n)
                pv = float(stats.chi2.sf(x2, C - 1))
                rows.append(dict(model=name, params=p, sampler=how, x2=x2, p=pv, ok=pv > 0.001))
    return rows


def run_gates(data):
    z = fit(BY_NAME["zeta"], data["chem"])
    g = dict(normalization=gate_normalization(), samplers=gate_samplers())
    g["nesting"], g["gigp_negative_nu_trend"] = gate_nesting(data["chem"])
    g["smolinsky"] = dict(s=z["params"][0], ok=round(z["params"][0], 4) == 1.9665)
    g["pass"] = (all(r["ok"] for r in g["normalization"]) and all(r["ok"] for r in g["nesting"])
                 and all(r["ok"] for r in g["samplers"]) and g["smolinsky"]["ok"])
    return g


# ---------------------------------------------------------------- comparisons
def compare(data, fits):
    rows = []
    for s, d in data.items():
        y = fits[s]["yule"]
        ly, my = pointwise(BY_NAME["yule"], y["params"], d)
        for m in MODELS[1:]:
            f = fits[s][m.name]
            row = dict(set=s, rival=m.name, dll=f["ll"] - y["ll"])
            if m.name in ("waring", "cutoff"):
                lr = max(0.0, 2.0 * row["dll"])
                p = stats.chi2.sf(lr, 1) if m.name == "waring" else (0.5 * stats.chi2.sf(lr, 1) if lr > 0 else 1.0)
                row.update(test="LR", stat=lr, p=float(p), verdict="rival favoured" if p < 0.05 else "no significant improvement over Yule")
            else:
                lr_, mr = pointwise(m, f["params"], d)
                diff = ly - lr_
                keep = mr > 0
                diff, w = diff[keep], mr[keep]
                nn = w.sum()
                mean = float(np.sum(w * diff) / nn)
                var = float(np.sum(w * diff ** 2) / nn - mean ** 2)
                z = math.sqrt(nn) * mean / math.sqrt(var) if var > 0 else 0.0
                verdict = "Yule favoured" if z > 1.96 else ("rival favoured" if z < -1.96 else "indistinguishable")
                row.update(test="Vuong", stat=z, p=float(2 * stats.norm.sf(abs(z))), verdict=verdict)
            rows.append(row)
    return rows


def sichel_target(d, fits):
    th_mle = fits["chem"]["sichel"]["params"][0]
    mean_obs = d["k"] / d["n"]
    r = -0.5

    def mean_enb(t):
        return (r * t / (1 - t)) / (1 - (1 - t) ** r)

    th_mm = brentq(lambda t: mean_enb(t) - mean_obs, 1e-6, 1 - 1e-12, xtol=1e-14)
    grade = lambda t: ("reproduced" if round(t, 5) == SICHEL_THETA else
                       ("consistent with" if abs(t - SICHEL_THETA) <= 5e-4 else "not reproduced"))
    # exploratory X^2: cells 1..m with expected >= 5, the rest pooled (also >= 5)
    m = BY_NAME["sichel"]
    n = d["n"]
    pr = np.exp(m.lp(np.arange(1, 2001, dtype=float), th_mle))
    cells, j = [], 1
    while n * pr[j - 1] >= 5 and n * (1 - pr[:j].sum()) >= 5:
        cells.append(j)
        j += 1
    obs = [d["ms"][d["xs"] == i].sum() for i in cells] + [d["ms"][d["xs"] > cells[-1]].sum()]
    exp_ = [n * pr[i - 1] for i in cells] + [n * (1 - pr[:cells[-1]].sum())]
    x2 = float(sum((o - e) ** 2 / e for o, e in zip(obs, exp_)))
    dof = len(obs) - 2
    return dict(theta_mle=th_mle, theta_mean_match=th_mm, target=SICHEL_THETA,
                grade_mle=grade(th_mle), grade_mean_match=grade(th_mm),
                grade=("reproduced" if "reproduced" in (grade(th_mle), grade(th_mm)) else
                       "consistent with" if "consistent with" in (grade(th_mle), grade(th_mm)) else "not reproduced"),
                exploratory_x2=dict(cells=len(obs), last_single_cell=cells[-1], x2=x2, dof=dof,
                                    p=float(stats.chi2.sf(x2, dof))))


# ---------------------------------------------------------------- bootstrap
def boot_task(args):
    sname, mname, chunk, reps, params, kind, n = args
    m = BY_NAME[mname]
    rng = np.random.default_rng([MASTER_SEED, SETS.index(sname), [x.name for x in MODELS].index(mname), chunk])
    sampler = TableSampler(m, params)
    out = []
    for _ in range(reps):
        s = sampler.draw(n, rng)
        d = data_from_sample(s, kind)
        try:
            f = fit(m, d)
        except RuntimeError:
            out.append(dict(fail=True))
            continue
        row = dict(fail=False, x2=x2_cells(d, m, f["params"], n), params=f["params"])
        if kind == "full":
            row["ks"] = ks_full(d, m, f["params"])
        out.append(row)
    return sname, mname, chunk, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--gates", action="store_true", help="run the A3.7 gates only")
    ap.add_argument("--reps", type=int, default=B_BOOT)
    ap.add_argument("--only", default=None, help="comma list of set names (bootstrap)")
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    data = data_from_sets()
    t0 = time.time()
    gates = run_gates(data)
    (ROOT / "results" / "stage4-gates.json").write_bytes((json.dumps(gates, indent=1) + "\n").encode("utf-8"))
    print(f"gates pass={gates['pass']} ({time.time() - t0:.0f}s)")
    if a.gates or not gates["pass"]:
        return
    fits = {s: {m.name: fit(m, d) for m in MODELS} for s, d in data.items()}
    for s in fits:
        best = min(2 * m_["params"].__len__() - 2 * m_["ll"] for m_ in fits[s].values())
        for mn, f in fits[s].items():
            f["aic"] = 2 * len(f["params"]) - 2 * f["ll"]
            f["daic"] = f["aic"] - best
    print(f"fits done ({time.time() - t0:.0f}s)")
    comp = compare(data, fits)
    sich = sichel_target(data["chem"], fits)
    obs_gof = {s: {mn: dict(x2=x2_cells(data[s], BY_NAME[mn], f["params"], data[s]["n"]),
                            ks=ks_full(data[s], BY_NAME[mn], f["params"]) if data[s]["kind"] == "full" else None)
                   for mn, f in fits[s].items()} for s in data}
    chunk = 25
    sets = a.only.split(",") if a.only else SETS
    tasks = [(s, m.name, c, min(chunk, a.reps - c * chunk), fits[s][m.name]["params"], data[s]["kind"], data[s]["n"])
             for s in sets for m in MODELS for c in range(math.ceil(a.reps / chunk))]
    reps = {}
    with Pool(a.workers) as pool:
        for i, (s, mn, c, out) in enumerate(pool.imap_unordered(boot_task, tasks), 1):
            reps.setdefault((s, mn), {})[c] = out
            if i % 40 == 0:
                print(f"  boot {i}/{len(tasks)} ({time.time() - t0:.0f}s)", flush=True)
    gof = {}
    for (s, mn), chunks in reps.items():
        rows = [r for c in sorted(chunks) for r in chunks[c]]
        ok = [r for r in rows if not r["fail"]]
        o = obs_gof[s][mn]
        g = dict(B=len(rows), failed=len(rows) - len(ok), x2_obs=o["x2"],
                 x2_p=sum(r["x2"] >= o["x2"] for r in ok) / len(ok))
        if o["ks"] is not None:
            g.update(ks_obs=o["ks"], ks_p=sum(r["ks"] >= o["ks"] for r in ok) / len(ok))
        gof.setdefault(s, {})[mn] = g
        with open(OUT / f"{s}__{mn}.json", "wb") as fh:
            fh.write((json.dumps(rows) + "\n").encode("utf-8"))
    summary = dict(master_seed=MASTER_SEED, reps=a.reps, sets=sets, fits=fits, compare=comp, sichel=sich, gof=gof,
                   n=dict((s, data[s]["n"]) for s in data), seconds=round(time.time() - t0, 1))
    (ROOT / "results" / "stage4-summary.json").write_bytes((json.dumps(summary, indent=1) + "\n").encode("utf-8"))
    print(f"done ({time.time() - t0:.0f}s)")


if __name__ == "__main__":
    main()

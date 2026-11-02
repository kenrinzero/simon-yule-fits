"""Stage 3: method-of-moments vs likelihood inside Simon's own processes.

Implements PREREGISTRATION.md Amendment 2 exactly: six data sets (A2.1), the
section II / Case II / section III processes at each set's real k (A2.2),
1,000 replicates (200 for Ulysses section III) (A2.3), percentile verdicts
(A2.4) and the iid-Yule estimator self-test (A2.5).

Usage: python src/stage3.py [--workers 6] [--only SET] [--quick]
Writes results/stage3/<set>__<process>.csv (one row per replicate),
results/stage3-selftest.csv and results/stage3-summary.json.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import random
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from scipy.optimize import brentq, minimize_scalar
from scipy.special import gammaln
from scipy.stats import yulesimon

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "sources"
RES = ROOT / "results"
OUT = RES / "stage3"
BETAS = [1.0, 0.9, 0.8, 0.7, 0.6]
REPS = 1000
REPS_III_ULYSSES = 200
MASTER_SEED = 19551201


# ---------------------------------------------------------------- data (A2.1)
def _rows(name):
    return list(csv.DictReader(open(SRC / name, encoding="utf-8")))


def load_sets():
    sets = {}
    chi = {}
    for r in _rows("davis1941_p429_chicago.csv"):
        if r["n"] != "Total":
            chi[int(r["n"])] = int(r["persons"])
    sets["chicago"] = dict(full=chi, c=11)
    for tab, name in (("chem", "chem"), ("auerbach", "physicists")):
        d = {}
        for r in _rows("davis1941_p431.csv"):
            if r["table"] == tab and r["n"] != "Total":
                d[int(r["n"])] = d.get(int(r["n"]), 0) + int(r["persons"])
        sets[name] = dict(full=d, c=11)
    pt = {(r["table"], r["set"], r["kind"], r["row"]): r["printed"]
          for r in csv.DictReader(open(ROOT / "data" / "printed_tables.csv", encoding="utf-8"))}
    econ = {i: int(pt[("T3", "econometrica", "actual", str(i))]) for i in range(1, 11)}
    sets["econometrica"] = dict(head=econ, cens=int(pt[("T3", "econometrica", "actual", "11+")]),
                                k=int(pt[("T3", "econometrica", "k", "")]), c=11)
    eld = {}
    for r in _rows("eldridge1911_list5_headers.csv"):
        if r["i"]:
            eld[int(r["i"])] = int(r["stated_count"])
    for r in _rows("eldridge1911_list5_counts.csv"):
        eld[int(r["count"])] = eld.get(int(r["count"]), 0) + 1
    sets["eldridge"] = dict(full=eld, c=11)
    z = {r["quantity"]: int(r["value"]) for r in _rows("zipf1949_ulysses.csv")}
    head = {1: z["f1"], 2: z["f2"], 3: z["f3"]}
    sets["ulysses"] = dict(head=head, cens=z["n_types"] - sum(head.values()), k=z["k_tokens"], c=4)
    # normalise: every set gets n, k, head (1..c-1), cens (>= c)
    for s in sets.values():
        c = s["c"]
        if "full" in s:
            f = s["full"]
            s["n"] = sum(f.values())
            s["k"] = sum(x * m for x, m in f.items())
            s["head"] = {i: f.get(i, 0) for i in range(1, c)}
            s["cens"] = sum(m for x, m in f.items() if x >= c)
        else:
            s["n"] = sum(s["head"].values()) + s["cens"]
    return sets


# ---------------------------------------------------------------- estimators
def _logp(x, r):
    return math.log(r) + gammaln(x) + gammaln(r + 1) - gammaln(x + r + 1)


def ll_full(r, xs, ms):
    return float(np.sum(ms * _logp(xs, r)))


def ll_cens(r, head_x, head_m, m_ge, c):
    ll = float(np.sum(head_m * _logp(head_x, r))) if len(head_x) else 0.0
    if m_ge:
        log_surv = math.log(c - 1) + gammaln(c - 1) + gammaln(r + 1) - gammaln(c + r)
        ll += m_ge * float(log_surv)
    return ll


def _argmax(f):
    res = minimize_scalar(lambda r: -f(r), bounds=(0.05, 20.0), method="bounded", options={"xatol": 1e-7})
    return float(res.x), float(-res.fun)


def mle_full(xs, ms):
    return _argmax(lambda r: ll_full(r, xs, ms))


def mle_cens(head_x, head_m, m_ge, c):
    return _argmax(lambda r: ll_cens(r, head_x, head_m, m_ge, c))


def profile_ci(f, rhat, llmax, drop=1.92):
    g = lambda r: f(r) - (llmax - drop)
    lo = brentq(g, 0.0501, rhat) if g(0.0501) < 0 else 0.05
    hi = brentq(g, rhat, 20.0) if g(20.0) < 0 else 20.0
    return lo, hi


def stats_from_sizes(sizes, c, want_full=True):
    """Statistics of A2.1 from an array of type sizes (one entry per type)."""
    sizes = np.asarray(sizes)
    n = int(sizes.size)
    k = int(sizes.sum())
    xs, ms = np.unique(sizes, return_counts=True)
    xs = xs.astype(float); ms = ms.astype(float)
    head_mask = xs < c
    rc, _ = mle_cens(xs[head_mask], ms[head_mask], float(ms[~head_mask].sum()), c)
    rf = mle_full(xs, ms)[0] if want_full else float("nan")
    f1 = float(ms[xs == 1].sum()); f2 = float(ms[xs == 2].sum())
    mom = k / (k - n) if k > n else float("inf")
    return dict(n=n, k=k, mom=mom, cens=rc, full=rf, G=rc - mom, G_full=rf - mom,
                p1=f1 / n, r21=(f2 / f1 if f1 else float("nan")), n_over_k=n / k)


def observed_stats(s):
    c = s["c"]
    hx = np.array(sorted(s["head"]), dtype=float)
    hm = np.array([s["head"][int(x)] for x in hx], dtype=float)
    rc, _ = mle_cens(hx, hm, float(s["cens"]), c)
    if "full" in s:
        xs = np.array(sorted(s["full"]), dtype=float)
        ms = np.array([s["full"][int(x)] for x in xs], dtype=float)
        rf = mle_full(xs, ms)[0]
    else:
        rf = float("nan")
    n, k = s["n"], s["k"]
    mom = k / (k - n)
    return dict(n=n, k=k, mom=mom, cens=rc, full=rf, G=rc - mom, G_full=rf - mom,
                p1=s["head"][1] / n, r21=s["head"][2] / s["head"][1], n_over_k=n / k)


# ---------------------------------------------------------------- processes (A2.2)
def stream_sizes(k, alpha_t, rng):
    """Section II / Case II stream of k tokens; returns type sizes.

    Token t (0-based) is new with prob alpha_t[t] (token 0 always new), else a
    copy of a uniformly chosen earlier token. Labels are resolved by pointer
    jumping: root[t] = t for new tokens, parent otherwise, iterated to a fixed
    point.
    """
    t = np.arange(k)
    new = rng.random(k) < alpha_t
    new[0] = True
    parent = np.floor(rng.random(k) * t).astype(np.int64)
    root = np.where(new, t, parent)
    while True:
        nxt = root[root]
        if np.array_equal(nxt, root):
            break
        root = nxt
    return np.bincount(root, minlength=k)[new]  # one size per new-type token


def alpha_schedule(k, n, beta):
    t = np.arange(1, k + 1, dtype=float)
    A = n / k ** beta
    return np.minimum(1.0, beta * A * t ** (beta - 1.0))


def stream_labels(k, alpha, rng):
    t = np.arange(k)
    new = rng.random(k) < alpha
    new[0] = True
    parent = np.floor(rng.random(k) * t).astype(np.int64)
    root = np.where(new, t, parent)
    while True:
        nxt = root[root]
        if np.array_equal(nxt, root):
            break
        root = nxt
    _, labels = np.unique(root, return_inverse=True)
    return labels


def slice_sizes(k, alpha, steps, rng, pyrng):
    """Section III: section II additions; whenever the length exceeds k, delete
    whole types chosen uniformly among current types (Assumption III)."""
    labels = stream_labels(k, alpha, rng)
    ntypes = int(labels.max()) + 1
    size = np.bincount(labels).tolist()
    alive = [True] * ntypes
    alive_list = list(range(ntypes))
    pos = list(range(ntypes))
    tok = labels.tolist()
    L = k
    dead_tok = 0
    rnd = pyrng.random
    for _ in range(steps):
        if rnd() < alpha:
            j = len(size)
            size.append(1); alive.append(True); pos.append(len(alive_list)); alive_list.append(j)
            tok.append(j)
        else:
            nt = len(tok)
            while True:
                j = tok[int(rnd() * nt)]
                if alive[j]:
                    break
            size[j] += 1
            tok.append(j)
        L += 1
        while L > k:
            idx = int(rnd() * len(alive_list))
            j = alive_list[idx]
            last = alive_list[-1]
            alive_list[idx] = last; pos[last] = idx; alive_list.pop()
            alive[j] = False
            L -= size[j]
            dead_tok += size[j]
        if dead_tok * 2 > len(tok):
            tok = [x for x in tok if alive[x]]
            dead_tok = 0
    return np.array([size[j] for j in alive_list])


# ---------------------------------------------------------------- tasks
def run_task(task):
    name, proc, beta, seeds, s, steps_mult = task
    c = s["c"]
    want_full = "full" in s
    out = []
    for sd in seeds:
        rng = np.random.default_rng(sd)
        if proc == "II":
            sizes = stream_sizes(s["k"], alpha_schedule(s["k"], s["n"], beta), rng)
        else:
            pyrng = random.Random(int(rng.integers(2**63)))
            sizes = slice_sizes(s["k"], s["n"] / s["k"], steps_mult * s["k"], rng, pyrng)
        st = stats_from_sizes(sizes, c, want_full)
        st.update(seed=sd, beta=beta)
        out.append(st)
    return name, proc, beta, steps_mult, out


def selftest_task(task):
    name, seeds, s = task
    c = s["c"]
    rho = s["k"] / (s["k"] - s["n"])
    out = []
    for sd in seeds:
        x = yulesimon.rvs(rho, size=s["n"], random_state=np.random.default_rng(sd))
        xs, ms = np.unique(x, return_counts=True)
        xs = xs.astype(float); ms = ms.astype(float)
        if "full" in s:
            f = lambda r: ll_full(r, xs, ms)
        else:
            hm = xs < c
            f = lambda r, hx=xs[hm], hmm=ms[hm], mg=float(ms[~hm].sum()): ll_cens(r, hx, hmm, mg, c)
        rhat, llmax = _argmax(f)
        lo, hi = profile_ci(f, rhat, llmax)
        out.append(dict(set=name, seed=sd, planted=rho, rhat=rhat, lo=lo, hi=hi, covered=lo <= rho <= hi))
    return out


def chunks(seq, n):
    return [seq[i:i + n] for i in range(0, len(seq), n)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--only", default=None)
    ap.add_argument("--quick", action="store_true", help="20 replicates, for smoke tests only")
    args = ap.parse_args()
    reps = 20 if args.quick else REPS
    sets = load_sets()
    names = [args.only] if args.only else list(sets)
    OUT.mkdir(parents=True, exist_ok=True)
    ss = np.random.SeedSequence(MASTER_SEED)
    seed_pool = [int(x) for x in ss.generate_state(200000, dtype=np.uint64) % (2**63)]
    sp = iter(seed_pool)

    obs = {nm: observed_stats(sets[nm]) for nm in sets}
    t0 = time.time()
    # self-test (A2.5)
    st_tasks = []
    st_seeds = {nm: [next(sp) for _ in range(REPS)] for nm in sets}
    for nm in names:
        for ch in chunks(st_seeds[nm][:reps], 50):
            st_tasks.append((nm, ch, sets[nm]))
    # process nulls
    tasks = []
    for nm in sets:
        for beta in BETAS:
            sd = [next(sp) for _ in range(REPS)]
            if nm in names:
                for ch in chunks(sd[:reps], 25):
                    tasks.append((nm, "II", beta, ch, sets[nm], 0))
        r3 = REPS_III_ULYSSES if nm == "ulysses" else REPS
        sd = [next(sp) for _ in range(REPS)]
        if nm in names:
            for ch in chunks(sd[:min(r3, reps)], 5):
                tasks.append((nm, "III", None, ch, sets[nm], 3))
        sd6 = [next(sp) for _ in range(REPS)]
        if nm == "physicists" and nm in names:
            for ch in chunks(sd6[:reps], 5):
                tasks.append((nm, "III", None, ch, sets[nm], 6))
    with Pool(args.workers) as pool:
        st_res = [r for chunk in pool.map(selftest_task, st_tasks) for r in chunk]
        # longest tasks first
        tasks.sort(key=lambda t: -(t[4]["k"] * (3 if t[1] == "III" else 0.05)))
        results = pool.map(run_task, tasks, chunksize=1)
    with open(RES / ("stage3-selftest.csv" if not args.quick else "stage3-selftest-quick.csv"),
              "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(st_res[0]), lineterminator="\n"); w.writeheader(); w.writerows(st_res)
    grouped = {}
    for name, proc, beta, mult, out in results:
        key = (name, proc if proc == "II" else f"III_B{mult}k", beta)
        grouped.setdefault(key, []).extend(out)
    summary = dict(observed=obs, selftest={}, nulls={}, runtime_s=None, quick=args.quick)
    for nm in names:
        cov = [r["covered"] for r in st_res if r["set"] == nm]
        rate = float(np.mean(cov))
        summary["selftest"][nm] = dict(reps=len(cov), coverage=rate, passes=0.929 <= rate <= 0.971,
                                       bias=float(np.mean([r["rhat"] - r["planted"] for r in st_res if r["set"] == nm])))
    for (nm, proc, beta), out in sorted(grouped.items(), key=lambda kv: (kv[0][0], kv[0][1], -(kv[0][2] or 0))):
        tag = f"{nm}__{proc}" + (f"_beta{beta}" if beta is not None else "")
        fields = ["seed", "beta", "n", "k", "n_over_k", "mom", "cens", "full", "G", "G_full", "p1", "r21"]
        with open(OUT / f"{tag}{'-quick' if args.quick else ''}.csv", "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n", extrasaction="ignore")
            w.writeheader(); w.writerows(out)
        o = obs[nm]
        entry = dict(reps=len(out))
        for stat in ("G", "p1", "r21", "n_over_k", "mom", "cens"):
            v = np.array([r[stat] for r in out], dtype=float)
            v = v[np.isfinite(v)]
            lo, med, hi = np.percentile(v, [2.5, 50, 97.5])
            q1, q3 = np.percentile(v, [25, 75])
            d = dict(lo=float(lo), median=float(med), hi=float(hi), width=float(hi - lo))
            if stat in ("G", "p1", "r21"):
                d["observed"] = o[stat]
                d["inside"] = bool(lo <= o[stat] <= hi)
                d["obs_percentile"] = float(np.mean(v <= o[stat]) * 100)
                iqr = q3 - q1
                d["robust_z"] = float((o[stat] - med) / (iqr / 1.349)) if iqr > 0 else None
            entry[stat] = d
        entry["joint"] = all(entry[s]["inside"] for s in ("G", "p1", "r21"))
        summary["nulls"][tag] = entry
    summary["runtime_s"] = round(time.time() - t0, 1)
    name = "stage3-summary-quick.json" if args.quick else "stage3-summary.json"
    (RES / name).write_bytes((json.dumps(summary, indent=2) + "\n").encode("utf-8"))
    print(json.dumps(dict(observed=obs, selftest=summary["selftest"], runtime=summary["runtime_s"]), indent=1))


if __name__ == "__main__":
    main()

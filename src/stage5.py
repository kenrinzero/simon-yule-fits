"""Stage 5 (PREREGISTRATION Amendment 4): the p. 436 word-count sentences on full
distributions. Eldridge from List 5, Hanley's Ulysses figures (censored at 4) and
three tokenizer recounts of Gutenberg #4300 (not a replication of Hanley).

    python src/stage5.py      # gates, counts, estimators, bootstrap, verdicts
"""
import csv
import json
import math
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

import numpy as np
from scipy import stats
from scipy.optimize import minimize_scalar

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import stage3 as s3  # noqa: E402
import stage4 as s4  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")

MASTER_SEED = 19551103
B_BOOT = 500
HANLEY = dict(n=29_899, k=260_430, f=(16_432, 4_776, 2_194))
ELDRIDGE = dict(n=6_002, k=43_989, f=(2_976, 1_079, 516))
LEISEN = dict(rho=1.09, lo=1.08, hi=1.11, n=29_841)
TEXT = ROOT / "data" / "raw" / "gutenberg4300" / "pg4300.txt"
LETTER = r"[^\W\d_]"
TOKENIZERS = {
    "T1": re.compile(f"{LETTER}+"),
    "T2": re.compile(f"{LETTER}+(?:['-]{LETTER}+)*"),
    "T3": re.compile(f"{LETTER}+(?:'{LETTER}+)*"),
}
PART = re.compile("^— (I|II|III) —$")
EPISODE = re.compile(r"^\[\s*\d+\s*\]$")


# ---------------------------------------------------------------- the recounts
def body_text():
    t = TEXT.read_text(encoding="utf-8")
    start = t.index("Stately, plump Buck Mulligan")
    end = t.index("*** END OF THE PROJECT GUTENBERG EBOOK")
    lines = [ln for ln in t[start:end].split("\n")
             if not PART.match(ln.strip()) and not EPISODE.match(ln.strip())]
    body = unicodedata.normalize("NFC", "\n".join(lines)).replace("’", "'")
    return body.lower()


def recount(name, body):
    words = TOKENIZERS[name].findall(body)
    types = Counter(words)
    return Counter(types.values()), len(words)


# ---------------------------------------------------------------- (4.2): p(i) = (1-x)/((i-x)(i+1-x))
def lp42(i, x):
    return math.log(1 - x) - np.log(i - x) - np.log(i + 1 - x)


def ll42(x, d):
    if d["kind"] == "full":
        return float(np.sum(d["ms"] * lp42(d["xs"], x)))
    c = d["c"]
    return float(np.sum(d["hm"] * lp42(d["hx"], x)) + d["mge"] * math.log((1 - x) / (c - x)))


def fit42(d, lo):
    r = minimize_scalar(lambda x: -ll42(x, d), bounds=(lo, 0.999), method="bounded", options={"xatol": 1e-10})
    return float(r.x), -float(r.fun)


def draw42(x, n, rng):
    u = 1.0 - rng.random(n)  # (0, 1]
    return np.floor(x + (1 - x) / u).astype(np.int64)


def cells(d, c):
    if d["kind"] == "full":
        return np.array([d["ms"][d["xs"] == i].sum() for i in range(1, c)] + [d["ms"][d["xs"] >= c].sum()])
    return np.append(d["hm"][: c - 1], d["mge"])


def x2_42(d, x, c):
    obs = cells(d, c)
    n = obs.sum()
    i = np.arange(1, c, dtype=float)
    exp_ = n * np.append(np.exp(lp42(i, x)), (1 - x) / (c - x))
    return float(np.sum((obs - exp_) ** 2 / exp_))


def sample_data(s, kind, c):
    xs, ms = np.unique(s, return_counts=True)
    xs, ms = xs.astype(float), ms.astype(float)
    if kind == "full":
        return dict(kind="full", xs=xs, ms=ms)
    hm = np.array([ms[xs == i].sum() for i in range(1, c)], dtype=float)
    return dict(kind="cens", hx=np.arange(1, c, dtype=float), hm=hm, mge=float(ms[xs >= c].sum()), c=c)


def boot42(d, x, c, seed):
    rng = np.random.default_rng([MASTER_SEED, seed])
    n = int(cells(d, c).sum())
    obs = x2_42(d, x, c)
    stat = []
    for _ in range(B_BOOT):
        sd = sample_data(draw42(x, n, rng), d["kind"], c)
        xb, _ = fit42(sd, 0.0)
        stat.append(x2_42(sd, xb, c))
    return obs, float(np.mean(np.array(stat) >= obs))


# ---------------------------------------------------------------- power-law slopes (C3)
def slopes(xs, ms):
    e1 = s4.fit(s4.BY_NAME["zeta"], dict(kind="full", xs=xs, ms=ms))["params"][0] - 1.0
    b2 = np.polyfit(np.log(xs), np.log(ms), 1)[0]
    edges = 2 ** np.arange(0, int(math.log2(xs.max())) + 2)
    bx, by = [], []
    for lo, hi in zip(edges[:-1], edges[1:]):
        cnt = ms[(xs >= lo) & (xs < hi)].sum()
        if cnt:
            bx.append(math.sqrt(lo * hi))
            by.append(cnt / (hi - lo))
    b3 = np.polyfit(np.log(bx), np.log(by), 1)[0]
    return dict(E1=float(e1), E2=float(-b2 - 1.0), E3=float(-b3 - 1.0))


# ---------------------------------------------------------------- per-count analysis
def recipe_t2(n, k):
    a = n / k
    rho = 1 / (1 - a)
    f1 = n / (2 - a)
    f2 = f1 * 1 / (2 + rho)
    f3 = f2 * 2 / (3 + rho)
    return dict(alpha=a, rho_mom=rho, est_f1=f1, est_f2=f2, est_f3=f3)


def analyse(name, d, n, k, f, seed):
    c = 11 if d["kind"] == "full" else 4
    out = dict(count=name, n=n, k=k, f1=f[0], f2=f[1], f3=f[2], p1=f[0] / n, r21=f[1] / f[0])
    out.update(recipe_t2(n, k))
    if d["kind"] == "full":
        rho, llm = s3.mle_full(d["xs"], d["ms"])
        g = lambda r: s3.ll_full(r, d["xs"], d["ms"])
        out.update(slopes(d["xs"], d["ms"]))
    else:
        rho, llm = s3.mle_cens(d["hx"], d["hm"], d["mge"], d["c"])
        g = lambda r: s3.ll_cens(r, d["hx"], d["hm"], d["mge"], d["c"])
    lo, hi = s3.profile_ci(g, rho, llm)
    out.update(yule_mle=rho, yule_lo=lo, yule_hi=hi, leisen_overlap=(lo <= LEISEN["hi"] and hi >= LEISEN["lo"]))
    x, _ = fit42(d, 0.0)
    xu, _ = fit42(d, -5.0)
    x2, p = boot42(d, x, c, seed)
    out.update(x42=x, x42_unconstrained=xu, x42_at_zero=x <= 1e-6, x2_42=x2, p_42=p, cells_42=c)
    return out


def full_data(freq):
    xs = np.array(sorted(freq), dtype=float)
    ms = np.array([freq[int(v)] for v in xs], dtype=float)
    return dict(kind="full", xs=xs, ms=ms)


def gates(counts):
    g = {}
    norm = []
    for x in (0.0, 0.2, 0.5, -0.5):
        i = np.arange(1, 10 ** 6 + 1, dtype=float)
        norm.append(abs(np.exp(lp42(i, x)).sum() + (1 - x) / (10 ** 6 + 1 - x) - 1.0))
    g["normalization_max_err"] = max(norm)
    rng = np.random.default_rng([MASTER_SEED, 999])
    s = draw42(0.2, 100_000, rng)
    sd = sample_data(s, "full", 11)
    g["sampler_p"] = float(stats.chi2.sf(x2_42(sd, 0.2, 11), 10))
    el = counts["eldridge"]
    g["eldridge_totals"] = (el["n"], el["k"])
    g["tokenizer_k"] = {t: counts[t]["k"] for t in TOKENIZERS}
    g["pass"] = (g["normalization_max_err"] < 1e-12 and g["sampler_p"] > 0.001
                 and g["eldridge_totals"] == (ELDRIDGE["n"], ELDRIDGE["k"])
                 and all(abs(kk / HANLEY["k"] - 1) <= 0.05 for kk in g["tokenizer_k"].values()))
    return g


def main():
    sets = s3.load_sets()
    el = sets["eldridge"]
    data, counts = {}, {}
    data["eldridge"] = full_data(el["full"])
    counts["eldridge"] = dict(n=el["n"], k=el["k"], f=tuple(el["full"][i] for i in (1, 2, 3)))
    u = sets["ulysses"]
    data["hanley"] = dict(kind="cens", hx=np.array([1.0, 2.0, 3.0]),
                          hm=np.array([u["head"][i] for i in (1, 2, 3)], dtype=float), mge=float(u["cens"]), c=4)
    counts["hanley"] = dict(n=u["n"], k=u["k"], f=tuple(u["head"][i] for i in (1, 2, 3)))
    body = body_text()
    out_dir = ROOT / "results" / "stage5"
    out_dir.mkdir(parents=True, exist_ok=True)
    for t in TOKENIZERS:
        freq, k = recount(t, body)
        data[t] = full_data(freq)
        counts[t] = dict(n=sum(freq.values()), k=k, f=tuple(freq.get(i, 0) for i in (1, 2, 3)))
        rows = "".join(f"{i},{freq[i]}\n" for i in sorted(freq))
        (out_dir / f"freq_{t}.csv").write_bytes(("i,types\n" + rows).encode("utf-8"))
    g = gates(counts)
    print(f"gates pass={g['pass']}")
    if not g["pass"]:
        (ROOT / "results" / "stage5-summary.json").write_bytes((json.dumps(dict(gates=g), indent=1) + "\n").encode("utf-8"))
        return
    res = {name: analyse(name, data[name], counts[name]["n"], counts[name]["k"], counts[name]["f"], j)
           for j, name in enumerate(["eldridge", "hanley", "T1", "T2", "T3"])}
    toks = list(TOKENIZERS)
    gr = dict(
        C1_eldridge=(counts["eldridge"]["n"], counts["eldridge"]["k"], counts["eldridge"]["f"])
        == (ELDRIDGE["n"], ELDRIDGE["k"], ELDRIDGE["f"]),
        C2={c: 1.05 <= r["rho_mom"] <= 1.25 for c, r in res.items()},
        C3={c: {e: 0.85 <= r[e] <= 1.15 for e in ("E1", "E2", "E3")} for c, r in res.items() if "E1" in r},
        C4_about_02={c: 0.1 <= res[c]["x42"] <= 0.3 for c in ["hanley"] + toks},
        C4_close_to_zero_eldridge=res["eldridge"]["x42"] <= 0.1,
        C4_good_fit={c: r["p_42"] >= 0.05 for c, r in res.items()},
        C4_ordering=all(res[c]["x42"] > res["eldridge"]["x42"] for c in ["hanley"] + toks),
    )
    pred = dict(
        P16=gr["C1_eldridge"],
        P17=all(counts[t]["n"] < HANLEY["n"] for t in toks),
        P18=all(gr["C4_about_02"][t] for t in toks),
        P19=gr["C4_close_to_zero_eldridge"] and gr["C4_ordering"],
        P20=not gr["C4_good_fit"]["eldridge"] and not any(gr["C4_good_fit"][t] for t in toks),
        P21=not gr["C3"]["eldridge"]["E1"],
    )
    summary = dict(master_seed=MASTER_SEED, B=B_BOOT, gates=g, results=res, grades=gr, predictions=pred,
                   hanley=HANLEY, leisen=LEISEN)
    (ROOT / "results" / "stage5-summary.json").write_bytes((json.dumps(summary, indent=1, default=float) + "\n").encode("utf-8"))
    keys = list(res["T1"].keys())
    with open(ROOT / "results" / "stage5-counts.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=keys, lineterminator="\n")
        w.writeheader()
        for r in res.values():
            w.writerow({k_: r.get(k_, "") for k_ in keys})
    print(json.dumps(dict(grades=gr, predictions=pred), indent=1, default=str))


if __name__ == "__main__":
    main()

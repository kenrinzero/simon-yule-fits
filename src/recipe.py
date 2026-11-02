"""Stage 1: recompute Simon (1955) Tables 1-3 from the stated recipe.

Implements PREREGISTRATION.md section 3 exactly: conventions A1-A4 x B1-B3 x
R1-R3 (+ C6a/C6b for Chicago), the four cell labels, the S1-S3 grading, the
rho-prime search and the (4.2) head-ratio check. Writes results/stage1-*.csv
and results/stage1-summary.json. No network, no randomness.
"""
from __future__ import annotations

import csv
import json
import math
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

import numpy as np
from scipy.special import beta as B

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RES = ROOT / "results"

T3_SETS = ["chicago", "chem", "physicists", "econometrica"]
T2_SETS = ["ulysses", "eldridge"]


# ---------------------------------------------------------------- inputs
def load_printed():
    rows = list(csv.DictReader(open(DATA / "printed_tables.csv", encoding="utf-8")))
    out: dict = {}
    for r in rows:
        key = (r["table"], r["set"], r["kind"], r["row"])
        out[key] = r["printed"]
    return out


def load_external():
    rows = list(csv.DictReader(open(DATA / "external_inputs.csv", encoding="utf-8")))
    return {(r["set"], r["quantity"]): int(r["value"]) for r in rows}


# ---------------------------------------------------------------- rounding
def round_half_up(x: float, ndigits: int = 0) -> float:
    q = Decimal(1).scaleb(-ndigits)
    return float(Decimal(repr(x)).quantize(q, rounding=ROUND_HALF_UP))


def round_sig(x: float, sig: int = 3) -> float:
    if x == 0:
        return 0.0
    digits = sig - int(math.floor(math.log10(abs(x)))) - 1
    return round_half_up(x, digits)


ROUNDERS = {
    "R1": lambda x: round_half_up(x, 0),
    "R2": lambda x: round_sig(x, 3),
    "R3": lambda x: round_half_up(x, -1),
}


# ---------------------------------------------------------------- recipe
def rho_of_alpha(a: float) -> float:
    return 1.0 / (1.0 - a)


def yule_chain(f1: float, rho: float, imax: int = 10) -> list[float]:
    f = [f1]
    for i in range(2, imax + 1):
        f.append(f[-1] * (i - 1) / (i + rho))
    return f


def table1_interp(alpha: float, printed) -> dict[int, float]:
    """Linear interpolation of printed Table 1 f*(i)/n_k in alpha (rows 1-3)."""
    grid = [0.0, 0.1, 0.2, 0.3, 0.5, 0.7, 0.9]
    lo = max(a for a in grid if a <= alpha)
    hi = min(a for a in grid if a >= alpha)
    out = {}
    for i in (1, 2, 3):
        vlo = float(printed[("T1", f"alpha={lo}", f"f{i}_over_n", "")])
        vhi = float(printed[("T1", f"alpha={hi}", f"f{i}_over_n", "")])
        w = 0.0 if hi == lo else (alpha - lo) / (hi - lo)
        out[i] = vlo + w * (vhi - vlo)
    return out


# ---------------------------------------------------------------- Table 1
def table1(printed):
    rows = []
    for a in [0.0, 0.1, 0.2, 0.3, 0.5, 0.7, 0.9]:
        rho = rho_of_alpha(a)
        f1 = 1.0 / (2.0 - a)
        f = yule_chain(f1, rho, 3)
        exact = {"rho": rho, "f1_over_n": f[0], "f2_over_n": f[1], "f3_over_n": f[2]}
        for kind, val in exact.items():
            ptxt = printed[("T1", f"alpha={a}", kind, "")]
            nd = len(ptxt.split(".")[1]) if "." in ptxt else 0
            rv = round_half_up(val, nd)
            p = float(ptxt)
            if abs(rv - p) < 1e-12:
                label = "exact"
            elif abs(abs(rv - p) - 10 ** -nd) < 1e-12:
                label = "rounding slip"
            else:
                label = "not reproduced"
            rows.append(dict(table="T1", set=f"alpha={a}", cell=kind, printed=ptxt,
                             recipe=f"{val:.6f}", recipe_rounded=f"{rv:.{nd}f}", label=label,
                             reproducing="", n_tried=1))
    return rows


# ---------------------------------------------------------------- Tables 2/3
def set_inputs(table, s, printed, ext):
    if table == "T3":
        k = int(printed[("T3", s, "k", "")])
        n = int(printed[("T3", s, "n_k", "")])
        obs = {i: int(printed[("T3", s, "actual", str(i))]) for i in range(1, 11)}
        obs["11+"] = int(printed[("T3", s, "actual", "11+")])
        est = {i: int(printed[("T3", s, "estimate", str(i))]) for i in range(1, 11)
               if ("T3", s, "estimate", str(i)) in printed}
        est["11+"] = int(printed[("T3", s, "estimate", "11+")])
        a_pr = float(printed[("T3", s, "alpha", "")])
        r_pr = float(printed[("T3", s, "rho", "")])
        imax = 10
    else:
        k = ext[(s, "k")]
        n = ext[(s, "n_k")]
        obs = {i: int(printed[("T2", s, "actual", str(i))]) for i in (1, 2, 3)}
        est = {i: int(printed[("T2", s, "estimate", str(i))]) for i in (1, 2, 3)}
        a_pr = float(printed[("T2", s, "alpha", "")])
        r_pr = None
        imax = 3
    return dict(k=k, n=n, obs=obs, est=est, a_pr=a_pr, r_pr=r_pr, imax=imax)


def combos_for(table, s, inp, printed):
    """Yield (name, rho, anchor, values-dict) for every applicable combination.

    values maps i -> unrounded value for rows 1..imax; for B3 the value at i is
    computed from the printed previous cell, so it is returned as a function of
    the printed table (resolved here since printed cells are known).
    """
    n, k, imax = inp["n"], inp["k"], inp["imax"]
    a_exact = n / k
    rho_sources = {"A1": (a_exact, rho_of_alpha(a_exact)),
                   "A2": (inp["a_pr"], rho_of_alpha(inp["a_pr"]))}
    if inp["r_pr"] is not None and s != "chicago":
        rp = inp["r_pr"]
        rho_sources["A3"] = (1 - 1 / rp, rp)
    if s == "chicago":
        f1o = inp["obs"][1]
        rho_sources = {"C6a": (0.0, f1o / (n - f1o))}
        p1 = round_half_up(f1o / n, 3)
        rho_sources["C6b"] = (0.0, p1 / (1 - p1))
    out = []
    for aname, (a, rho) in rho_sources.items():
        anchors = ["B2", "B3"] if s == "chicago" else ["B1", "B2", "B3"]
        for b in anchors:
            vals = {}
            for i in range(1, imax + 1):
                if i == 1:
                    if s == "chicago":
                        vals[1] = float(inp["obs"][1])
                    elif b == "B2":
                        vals[1] = float(inp["obs"][1])
                    else:
                        vals[1] = n / (2 - a)
                    continue
                if b == "B3":
                    prev = inp["est"].get(i - 1)
                    if prev is None:  # chicago i=2 has no printed row 1
                        prev = vals[i - 1]
                    vals[i] = prev * (i - 1) / (i + rho)
                else:
                    vals[i] = vals[i - 1] * (i - 1) / (i + rho)
            out.append((f"{aname}+{b}", rho, vals))
    if s != "chicago":  # A4: Table-1 interpolation, rows 1-3 only
        ti = table1_interp(a_exact, printed)
        out.append(("A4", None, {i: ti[i] * n for i in (1, 2, 3)}))
    return out


def label_cells(table, s, inp, printed):
    combos = combos_for(table, s, inp, printed)
    base_name = "C6a+B2" if s == "chicago" else "A1+B1"
    base_vals = dict(next(v for nm, _, v in combos if nm == base_name))
    n = inp["n"]
    rows = []
    # rounded predictions per (combo, rounding), with 11+ residual for T3
    preds = {}
    for nm, rho, vals in combos:
        for rn, rf in ROUNDERS.items():
            r = {i: rf(v) for i, v in vals.items()}
            if table == "T3" and len(vals) == inp["imax"]:
                r["11+"] = n - sum(r[i] for i in range(1, 11))
            preds[f"{nm}+{rn}"] = r
    base_unr = dict(base_vals)
    if table == "T3":
        base_unr["11+"] = n - sum(base_vals[i] for i in range(1, 11))
    cells = [c for c in inp["est"]]
    for c in cells:
        p = inp["est"][c]
        exact_key = f"{base_name}+R1"
        reps = sorted(name for name, r in preds.items() if c in r and abs(r[c] - p) < 1e-9)
        n_tried = sum(1 for r in preds.values() if c in r)
        if exact_key in reps:
            label = "exact"
        elif reps:
            label = "reproduced-under-X"
            if len(reps) == 1 and not reps[0].startswith("A1"):
                label += " (weak)"
        else:
            rv = round_half_up(base_unr[c], 0)
            label = "rounding slip" if abs(abs(rv - p) - 1) < 1e-9 else "not reproduced"
        rows.append(dict(table=table, set=s, cell=str(c), printed=str(p),
                         recipe=f"{base_unr[c]:.2f}", recipe_rounded=f"{round_half_up(base_unr[c], 0):.0f}",
                         label=label, reproducing=";".join(reps), n_tried=n_tried))
    # single-combination headline
    full = [name for name, r in preds.items()
            if all(c in r and abs(r[c] - inp["est"][c]) < 1e-9 for c in cells)]
    return rows, full, base_unr


# ---------------------------------------------------------------- S1-S3
def grade(sets_inp, base):
    out = {}
    for which in ("printed", "recipe"):
        s1, s2p, s2s, s3 = {}, {}, {}, {}
        for s in T3_SETS:
            obs = sets_inp[s]["obs"]
            est = sets_inp[s]["est"] if which == "printed" else base[s]
            if s == "chicago" and which == "printed":
                s1[s] = bool(est[2] > obs[2])
            elif s == "chicago":
                s1[s] = bool(est[2] > obs[2])
            else:
                s1[s] = bool(est[1] > obs[1] and est[2] > obs[2])
            se = sum(est[i] for i in range(3, 11))
            so = sum(obs[i] for i in range(3, 11))
            s2p[s] = bool(se < so)
            s2s[s] = sum(1 for i in range(3, 11) if est[i] < obs[i])
            s3[s] = bool(est["11+"] > obs["11+"])
        n3 = sum(s3.values())
        out[which] = dict(
            S1=dict(per_column=s1, holds=all(s1.values())),
            S2=dict(primary_per_column=s2p, cells_est_lt_obs_of_8=s2s, holds=all(s2p.values())),
            S3=dict(per_column=s3, count=n3, holds=(n3 == 3)),
        )
    return out


# ---------------------------------------------------------------- rho-prime
def yule_censored_mle(counts: dict, n: int, cens_at: int = 11) -> float:
    def ll(r):
        lp = lambda i: math.log(r) + math.lgamma(i) + math.lgamma(r + 1) - math.lgamma(i + r + 1)
        s = sum(counts[i] * lp(i) for i in range(1, cens_at))
        surv = (cens_at - 1) * B(cens_at - 1, r + 1)  # P(I > 10)
        return s + counts["11+"] * math.log(surv)
    grid = np.linspace(0.2, 5.0, 48001)
    vals = [ll(r) for r in grid]
    return float(grid[int(np.argmax(vals))])


def rho_prime_search(inp):
    obs = inp["obs"]
    n = inp["n"]
    cands = {}
    cands["E1 f1/f2-2"] = obs[1] / obs[2] - 2
    S = {}
    for i in range(1, 12):
        S[i] = obs["11+"] + sum(obs[j] for j in range(i, 11)) if i <= 10 else obs["11+"]
    for i in range(2, 12):
        cands[f"E2 log(S1/S{i})/log{i}"] = math.log(S[1] / S[i]) / math.log(i)
    for lo in (1, 2, 3):
        xs = np.log(np.arange(lo, 11))
        ys = np.log(np.array([obs[i] for i in range(lo, 11)], dtype=float))
        slope = np.polyfit(xs, ys, 1)[0]
        cands[f"E3 OLS logf i={lo}..10"] = -1 - slope
    xs = np.log(np.arange(1, 12))
    ys = np.log(np.array([S[i] for i in range(1, 12)], dtype=float))
    cands["E4 OLS logS i=1..11"] = -np.polyfit(xs, ys, 1)[0]
    cands["E5 Yule MLE censored 11+"] = yule_censored_mle(obs, n)
    rows = [dict(candidate=k, value=f"{v:.4f}", rounds_to=f"{round_half_up(float(v), 2):.2f}",
                 matches_1_07=abs(round_half_up(float(v), 2) - 1.07) < 1e-9) for k, v in cands.items()]
    return rows


# ---------------------------------------------------------------- (4.2) head
def head_check(ext, printed):
    out = {}
    for s in T2_SETS:
        n = ext[(s, "n_k")]
        f = {i: int(printed[("T2", s, "actual", str(i))]) for i in (1, 2, 3)}
        x1 = 2 - 1 / (f[1] / n)                 # f1/n = 1/(2-x)
        r2 = f[2] / f[1]; x2 = (1 - 3 * r2) / (1 - r2)   # (1-x)/(3-x) = r2
        r3 = f[3] / f[2]; x3 = (2 - 4 * r3) / (1 - r3)   # (2-x)/(4-x) = r3
        xs = [x1, x2, x3]
        if s == "ulysses":
            ok = all(0.1 <= x <= 0.3 for x in xs)
        else:
            ok = all(abs(x) <= 0.1 for x in xs)
        out[s] = dict(x_from_f1_over_n=x1, x_from_f2_over_f1=x2, x_from_f3_over_f2=x3,
                      head_consistent=ok, any_negative=any(x < 0 for x in xs))
    return out


# ---------------------------------------------------------------- main
def main():
    printed = load_printed()
    ext = load_external()
    RES.mkdir(exist_ok=True)
    cell_rows = table1(printed)
    singles, base, inps = {}, {}, {}
    for s in T2_SETS:
        inp = set_inputs("T2", s, printed, ext)
        rows, full, b = label_cells("T2", s, inp, printed)
        cell_rows += rows; singles[s] = full; inps[s] = inp
    for s in T3_SETS:
        inp = set_inputs("T3", s, printed, ext)
        rows, full, b = label_cells("T3", s, inp, printed)
        cell_rows += rows; singles[s] = full; base[s] = b; inps[s] = inp
    with open(RES / "stage1-cells.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(cell_rows[0].keys()), lineterminator="\n")
        w.writeheader(); w.writerows(cell_rows)
    rp = rho_prime_search(inps["chicago"])
    with open(RES / "stage1-rho-prime.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rp[0].keys()), lineterminator="\n")
        w.writeheader(); w.writerows(rp)
    footer = {}
    for s in T3_SETS[1:]:
        a = inps[s]["n"] / inps[s]["k"]
        footer[s] = dict(alpha_exact=a, rho_exact=rho_of_alpha(a),
                         alpha_printed=inps[s]["a_pr"], rho_printed=inps[s]["r_pr"],
                         alpha_ok=round_half_up(a, 2) == inps[s]["a_pr"],
                         rho_ok=round_half_up(rho_of_alpha(a), 2) == inps[s]["r_pr"])
    c = inps["chicago"]
    footer["chicago"] = dict(rho_bar_exact=c["obs"][1] / (c["n"] - c["obs"][1]),
                             rho_bar_p1_3dp=(lambda p: p / (1 - p))(round_half_up(c["obs"][1] / c["n"], 3)),
                             rho_printed=c["r_pr"], alpha_exact_n_over_k=c["n"] / c["k"])
    for s in T2_SETS:
        a = inps[s]["n"] / inps[s]["k"]
        footer[s] = dict(alpha_exact=a, alpha_printed=inps[s]["a_pr"],
                         alpha_ok=round_half_up(a, 3) == inps[s]["a_pr"], rho_exact=rho_of_alpha(a))
    labels = {}
    for r in cell_rows:
        labels.setdefault(r["table"], {}).setdefault(r["label"], 0)
        labels[r["table"]][r["label"]] += 1
    summary = dict(
        label_counts=labels,
        single_combination_reproducing_whole_column=singles,
        sentence_grades=grade(inps, base),
        footer=footer,
        rho_prime_any_match=any(r["matches_1_07"] for r in rp),
        head_check_4_2=head_check(ext, printed),
    )
    (RES / "stage1-summary.json").write_bytes(
        (json.dumps(summary, indent=2, default=float) + "\n").encode("utf-8"))
    print(json.dumps(summary, indent=2, default=float))


if __name__ == "__main__":
    main()

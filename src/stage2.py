"""Stage 2: assert the ingested source tables and re-test Chicago rho-prime.

Implements PREREGISTRATION.md Amendment 1 (A1.3 assertions, A1.4 rho-prime
candidates F1-F5). Reads data/sources/*.csv (adjudicated double entries) and
writes results/stage2-summary.json plus results/stage2-rho-prime.csv.
"""
from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import numpy as np
from scipy.optimize import minimize_scalar
from scipy.special import zeta

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "sources"
RES = ROOT / "results"


def rows(name):
    return list(csv.DictReader(open(SRC / name, encoding="utf-8")))


def table_counts(rs, key="persons"):
    """Return {n: count} for non-total rows plus the printed total."""
    out, total = {}, None
    for r in rs:
        if r["n"] == "Total":
            total = int(r[key])
        else:
            out[int(r["n"])] = out.get(int(r["n"]), 0) + int(r[key])
    return out, total


def k_of(c):
    return sum(n * m for n, m in c.items())


# ---------------------------------------------------------------- fits
def zeta_mle(c, xmin=1):
    xs = {x: m for x, m in c.items() if x >= xmin and m > 0}
    N = sum(xs.values())
    slog = sum(m * math.log(x) for x, m in xs.items())
    nll = lambda a: a * slog + N * math.log(zeta(a, xmin))
    r = minimize_scalar(nll, bounds=(1.0001, 6.0), method="bounded", options={"xatol": 1e-10})
    return float(r.x), float(-r.fun), N


def yule_mle(c):
    xs = {x: m for x, m in c.items() if m > 0}
    def nll(r):
        return -sum(m * (math.log(r) + math.lgamma(x) + math.lgamma(r + 1) - math.lgamma(x + r + 1))
                    for x, m in xs.items())
    r = minimize_scalar(nll, bounds=(0.05, 10.0), method="bounded", options={"xatol": 1e-10})
    return float(r.x)


def survival(c):
    xs = sorted(x for x, m in c.items() if m > 0)
    tot = sum(c.values())
    S, run = {}, tot
    for x in xs:
        S[x] = run
        run -= c[x]
    return S


def r2(v):
    return round(v + 1e-12, 2)


# ---------------------------------------------------------------- assertions
def check(results, name, ok, detail):
    results.append(dict(check=name, ok=bool(ok), detail=detail))


def main():
    out = []
    # Davis p.429 Chicago
    chi, chi_tot = table_counts(rows("davis1941_p429_chicago.csv"))
    check(out, "Davis p.429 Chicago persons sum = printed total = 278",
          sum(chi.values()) == chi_tot == 278, f"sum={sum(chi.values())} printed={chi_tot}")
    check(out, "Davis p.429 Chicago k = 1,124 (Simon's k)", k_of(chi) == 1124, f"k={k_of(chi)}")
    # Davis p.430 cumulative classes: y_actual = S(x-3), classes 7 wide
    S = survival(chi)
    def S_at(lo):
        return sum(m for n, m in chi.items() if n >= lo)
    p430 = rows("davis1941_p430_cumulative.csv")
    mism = [(r["x"], r["y_actual"], S_at(int(r["x"]) - 3)) for r in p430 if int(r["y_actual"]) != S_at(int(r["x"]) - 3)]
    check(out, "Davis p.430 y(actual) = #persons with >= x-3 contributions (7-wide classes)", not mism, f"mismatches={mism}")
    # Davis p.431
    p431 = rows("davis1941_p431.csv")
    chem, chem_tot = table_counts([r for r in p431 if r["table"] == "chem"])
    aue, aue_tot = table_counts([r for r in p431 if r["table"] == "auerbach"])
    check(out, "Davis p.431 Chem persons sum = printed total = 6,891",
          sum(chem.values()) == chem_tot == 6891, f"sum={sum(chem.values())}")
    check(out, "Davis p.431 Chem k vs Simon's 22,939", k_of(chem) == 22939, f"k={k_of(chem)}")
    check(out, "Davis p.431 Auerbach persons sum = printed total = 1,325",
          sum(aue.values()) == aue_tot == 1325, f"sum={sum(aue.values())}")
    check(out, "Davis p.431 Auerbach k vs Simon's 3,396 (report)", k_of(aue) == 3396, f"k={k_of(aue)} (Simon prints 3,396)")
    # Lotka Table 1 vs Davis p.431
    lotka_path = SRC / "lotka1926_table1.csv"
    if lotka_path.exists():
        L = rows("lotka1926_table1.csv")
        body = [r for r in L if r["n_label"] != "Total"]
        tot = next(r for r in L if r["n_label"] == "Total")
        for col, want in (("A", 1543), ("B", 5348), ("AB", 6891), ("auerbach", 1325)):
            s = sum(int(r[col] or 0) for r in body)
            check(out, f"Lotka Table 1 column {col} sums to printed Total {tot[col]}", s == int(tot[col]) == want,
                  f"sum={s} printed={tot[col]}")
        bad = [r["n_label"] for r in body if int(r["A"] or 0) + int(r["B"] or 0) != int(r["AB"] or 0)]
        check(out, "Lotka Table 1 A + B = A+B in every row", not bad, f"failing rows={bad}")
        for col, davis in (("AB", chem), ("auerbach", aue)):
            diffs = []
            for r in body:
                lo, hi = int(r["n_lo"]), int(r["n_hi"])
                d = sum(m for n, m in davis.items() if lo <= n <= hi)
                if d != int(r[col] or 0):
                    diffs.append((r["n_label"], r[col], d))
            extra = [n for n in davis if not any(int(r["n_lo"]) <= n <= int(r["n_hi"]) for r in body)]
            check(out, f"Davis p.431 = Lotka Table 1 ({col}) row by row after resolving ranges",
                  not diffs and not extra, f"diffs={diffs} davis_n_outside_lotka_rows={extra}")
    # Eldridge List 5
    el_path = SRC / "eldridge1911_list5_counts.csv"
    if el_path.exists():
        E = rows("eldridge1911_list5_counts.csv")
        H = rows("eldridge1911_list5_headers.csv")
        cnt = [int(r["count"]) for r in E]
        g20 = [int(r["count"]) for r in E if r["group"].startswith("20")]
        g10 = [int(r["count"]) for r in E if r["group"].startswith("19")]
        check(out, "Eldridge: 238 words with >= 20 and 261 with 10-19",
              len(g20) == 238 and len(g10) == 261 and min(g20) >= 20 and all(10 <= c <= 19 for c in g10),
              f"n20={len(g20)} n10={len(g10)}")
        fhead = {int(r["i"]): int(r["stated_count"]) for r in H if r.get("i")}
        types = len(cnt) + sum(fhead.values())
        tokens = sum(cnt) + sum(i * f for i, f in fhead.items())
        check(out, "Eldridge: 6,002 types", types == 6002, f"types={types}")
        check(out, "Eldridge: 43,989 tokens", tokens == 43989,
              f"tokens={tokens}; i>=10 tokens={sum(cnt)} (needed {43989 - sum(i * f for i, f in fhead.items())})")
    # Zipf
    Z = {r["quantity"]: int(r["value"]) for r in rows("zipf1949_ulysses.csv")}
    check(out, "Zipf 1949: Ulysses k=260,430, n=29,899, f1..f3 = 16,432/4,776/2,194",
          (Z["k_tokens"], Z["n_types"], Z["f1"], Z["f2"], Z["f3"]) == (260430, 29899, 16432, 4776, 2194), str(Z))
    # External: Smolinsky 2015 zeta MLE on Chem
    a, ll, N = zeta_mle(chem, 1)
    check(out, "Chem zeta MLE (x_min=1) = 1.9665 (Smolinsky 2015)", round(a, 4) == 1.9665,
          f"alpha={a:.6f} LL={ll:.2f} (Smolinsky -11705.1) N={N}")

    # rho-prime (A1.4) on Davis p.429
    cands = []
    for x in sorted(S):
        if x > 1:
            cands.append(("F1", f"log(S(1)/S({x}))/log {x}", math.log(S[1] / S[x]) / math.log(x)))
    for xm in range(1, 6):
        a, _, n = zeta_mle(chi, xm)
        cands.append(("F2", f"zeta MLE x_min={xm} (n={n}), alpha-1", a - 1))
    cands.append(("F3", "Yule MLE, full table", yule_mle(chi)))
    xs = np.log(np.array(sorted(S), dtype=float)); ys = np.log(np.array([S[x] for x in sorted(S)], dtype=float))
    cands.append(("F4", "OLS log S(x) on log x, full support", -float(np.polyfit(xs, ys, 1)[0])))
    cands.append(("F5", "Davis p.429 slope 2.11012 minus 1", 2.11012 - 1))
    rp = [dict(family=f, candidate=c, value=f"{v:.4f}", rounds_to=f"{r2(v):.2f}", matches_1_07=r2(v) == 1.07)
          for f, c, v in cands]
    matches = [r["candidate"] for r in rp if r["matches_1_07"]]
    grade = ("not reproduced" if not matches else
             f"consistent with {matches[0]}" if len(matches) == 1 else "underdetermined")
    RES.mkdir(exist_ok=True)
    with open(RES / "stage2-rho-prime.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rp[0]), lineterminator="\n"); w.writeheader(); w.writerows(rp)
    summ = dict(checks=out, all_pass=all(c["ok"] for c in out if "report" not in c["check"]),
                rho_prime=dict(grade=grade, matches=matches, n_candidates=len(rp)))
    (RES / "stage2-summary.json").write_bytes((json.dumps(summ, indent=2) + "\n").encode("utf-8"))
    for c in out:
        print(("PASS " if c["ok"] else ("DIFF " if "report" in c["check"] else "FAIL ")) + c["check"] + " :: " + c["detail"])
    print("rho-prime:", grade, matches)


if __name__ == "__main__":
    main()

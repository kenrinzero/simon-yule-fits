"""Numeric receipts for the Step 0 derivations D1-D5 and D9 (PREREGISTRATION.md section 2).

Writes results/step0-derivation-checks.txt. Exits non-zero if any check fails.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
from mpmath import mp, mpf, beta as mbeta, nsum, inf
from scipy.special import gammaln

mp.dps = 30
OUT = Path(__file__).resolve().parents[1] / "results" / "step0-derivation-checks.txt"
lines, ok = [], True


def check(name, cond, detail):
    global ok
    ok &= bool(cond)
    lines.append(f"{'PASS' if cond else 'FAIL'}  {name}: {detail}")


def yule(i, rho):
    return rho * mbeta(i, rho + 1)


def partial_plus_tail(rho, power, N=2_000_000):
    """sum_{i>=1} i^power * rho*B(i,rho+1): direct float sum to N plus the
    leading asymptotic tail rho*Gamma(rho+1)*N^(power-rho)/(rho-power)
    (heavy tails defeat mpmath nsum's default extrapolation)."""
    i = np.arange(1, N + 1, dtype=float)
    logp = math.log(rho) + gammaln(i) + gammaln(rho + 1) - gammaln(i + rho + 1)
    s = float(np.sum(np.exp(logp + power * np.log(i))))
    tail = rho * math.gamma(rho + 1) * N ** (power - rho) / (rho - power)
    return s + tail


for a in (mpf("0.1"), mpf("0.3"), mpf("0.40989198")):
    rho = 1 / (1 - a)
    tot = partial_plus_tail(float(rho), 0)
    mean = partial_plus_tail(float(rho), 1)
    check(f"D1 sum p(i)=1 (alpha={a})", abs(tot - 1) < 1e-9, f"sum={tot:.12f}")
    check(f"D1 p(1)=1/(2-alpha) (alpha={a})", abs(yule(1, rho) - 1 / (2 - a)) < mpf("1e-25"),
          f"p1={mp.nstr(yule(1, rho), 15)}")
    r = yule(5, rho) / yule(4, rho)
    check(f"D1 ratio (2.11) at i=5 (alpha={a})", abs(r - mpf(4) / (5 + rho)) < mpf("1e-25"), f"{mp.nstr(r, 15)}")
    check(f"D2 mean = 1/alpha (alpha={a})", abs(mean - float(1 / a)) / float(1 / a) < 1e-4,
          f"mean={mean:.8f} 1/alpha={float(1 / a):.8f}")

# D3: Yule survival P(I > x) = x B(x, rho+1); 11+ residual equals n_k * P(I >= 11)
rho = 1 / (1 - mpf(6891) / 22939)
surv = 10 * mbeta(10, rho + 1)
direct = 1 - nsum(lambda i: yule(i, rho), [1, 10])
check("D3 survival identity P(I>10)=10B(10,rho+1) (Chem rho)", abs(surv - direct) < mpf("1e-25"),
      f"{mp.nstr(surv, 15)} vs {mp.nstr(direct, 15)}; n_k*P = {mp.nstr(6891 * surv, 8)}")
printed_chem = [4050, 1160, 522, 288, 179, 120, 86, 64, 49, 38]
check("D3 printed Chem 11+ = n_k - printed rows 1-10", 6891 - sum(printed_chem) == 335,
      f"6891-{sum(printed_chem)}={6891 - sum(printed_chem)}")
for name, n, rows, p11 in [("chicago", 278, [133, 46, 23, 14, 10, 7, 5, 4, 3, 3], 30),
                           ("physicists", 1325, [824, 217, 94, 50, 30, 20, 14, 10, 8, 6], 52),
                           ("econometrica", 721, [453, 119, 51, 27, 16, 11, 7, 5, 4, 3], 25)]:
    check(f"D3 printed {name} 11+ = n_k - printed rows 1-10", n - sum(rows) == p11,
          f"{n}-{sum(rows)}={n - sum(rows)} (printed {p11})")

# D4: (4.2) telescopes; f1/n = 1/(2-x), tail ~ i^-2
for x in (mpf(0), mpf("0.2"), mpf("0.5")):
    g = lambda i: 1 / ((i - x) * (i + 1 - x))
    tot = nsum(g, [1, inf])
    check(f"D4 sum telescopes to 1/(1-x) (x={x})", abs(tot - 1 / (1 - x)) < mpf("1e-20"), mp.nstr(tot, 15))
    check(f"D4 f1/n = 1/(2-x) (x={x})", abs(g(1) / tot - 1 / (2 - x)) < mpf("1e-20"), mp.nstr(g(1) / tot, 15))
    rr = g(2) / g(1)
    check(f"D4 ratio (4.2) at i=2 (x={x})", abs(rr - (1 - x) / (3 - x)) < mpf("1e-25"), mp.nstr(rr, 15))
    slope = (math.log(float(g(10 ** 6))) - math.log(float(g(10 ** 5)))) / math.log(10)
    check(f"D4 tail slope -2 (x={x})", abs(slope + 2) < 1e-4, f"{slope:.6f}")

# D5: Case II (2.34) with n'=alpha, n_k=alpha k reduces to 1/(1-alpha)
for a in (0.1, 0.3, 0.41):
    k = 1000.0
    rho2 = (a * k / (a * k)) / (1 - a)
    check(f"D5 (2.34) reduces (alpha={a})", abs(rho2 - 1 / (1 - a)) < 1e-12, f"{rho2:.6f}")

# D9: Chicago rho-bar
rb = 133 / 145
p1 = round(133 / 278, 3)
check("D9 rho-bar exact does not round to 0.916", round(rb, 3) != 0.916, f"{rb:.5f}")
check("D9 rho-bar from p1 at 3dp rounds to 0.916", round(p1 / (1 - p1), 3) == 0.916, f"p1={p1} -> {p1 / (1 - p1):.5f}")

OUT.write_bytes(("\n".join(lines) + f"\n\n{'ALL PASS' if ok else 'FAILURES PRESENT'}\n").encode("utf-8"))
print("\n".join(lines))
print("ALL PASS" if ok else "FAILURES PRESENT")
sys.exit(0 if ok else 1)

# Claim inventory: Simon (1955), "On a Class of Skew Distribution Functions"

*Biometrika* 42(3/4), 425–440. The claims checked here are those about
Simon's own empirical tables and his verbal readings of them. Each row gives
the page locator, how the claim can be checked, the tier assigned before any
analysis, and where it was settled.

**Tiers.**
- **T1:** design-heavy.
- **T2:** statistical work on data.
- **T3:** deterministic recomputation.

**Standing rule.** Every claim was walked against
[`INVESTIGATION_CHECKLIST.md`](INVESTIGATION_CHECKLIST.md) before the
write-up.

| ID | Claim (paper locator) | Checkability | Tier | Settled in |
|---|---|---|---|---|
| C1 | Tables 2–3 estimates follow from (2.11) + (2.21), p. 436 (Chicago via ρ̄, footer §) | Deterministic | T3 | Stage 1 |
| C2 | §IV.B: estimates too high for i = 1, 2, too low for 3..10, and too high in the tails in 3 of 4 cases (p. 437 top) | Deterministic given C1 | T3 | Stage 1 |
| C3 | Table 1 values follow from (2.11), (2.12), (2.21) (p. 430) | Deterministic | T3 | Stage 1 |
| C4 | "The fit is reasonably good" with one parameter (p. 436) | Statistical: Yule against rivals on the untruncated tables | T2 | Stage 4 |
| C5 | n_k/k gives ρ ≈ 1.1–1.2, and a whole-distribution K·i^−(ρ+1) fit gives ρ ≈ 1 for both word counts (p. 436) | Needs Eldridge List 5 and a *Ulysses* recount | T2 | Stages 2, 5 |
| C6 | (4.2) fits *Ulysses* with c ≈ 0.2 and Eldridge with c ≈ 0 (p. 436) | Head check, then a full fit (only cβ is identified) | T2 | Stages 1, 5 |
| C7 | The negative binomial cannot give k > 1 together with f(2)/f(1) < 1/2 when b ≈ 1 (§I, p. 426) | Deterministic plus a fit | T2 | Stage 4 (see below) |
| C8 | The empirical sets arise from Simon's mechanisms (§II, the §III slice, Case II) | Statistical: process nulls at the real (k, n_k) | T1 design, T2 run | Stage 3 |
| C9 | Chicago ρ′ = 1.07 (footer; undefined in the text) | Search over candidate definitions | T2 | Stages 1, 2 |

**Note on C7.** Simon's §I statement concerns the negative binomial with
r > 0. Stage 4 fitted the wider family that includes Engen's extension to
r ∈ (−1, 0). On every set, the best member of that family has r < 0. The
r > 0 claim is therefore neither contradicted nor separately graded.

The outcome of each claim, with its qualifiers, is in [`REPORT.md`](REPORT.md).

# Step 0: derivation pre-pass and Stage 1 contract

- **Frozen:** 2026-11-01, before any Stage 1 code was written. The SHA-256 of
  this file at freeze is recorded in the project log.
- **Governs:** `src/recipe.py`, `src/step0_checks.py` and every Stage 1 number
  in `results/`.
- **Amendment rule:** any change after the freeze is a dated amendment
  appended at the bottom, with its reason. Nothing above the amendments line is
  edited.
- **Sources:** page images `results/pages/p430.png`, `p436.png`, `p437.png`;
  transcribed cells in `data/printed_tables.csv`. Table 2's k and n_k are
  external inputs (`data/external_inputs.csv`), carried from the 2026-09-30
  idea check and re-verified at Stage 2.

## 1. The recipe (R)

Simon's estimates in Tables 1–3 are said to come from (2.11), (2.12) and (2.21)
(p. 436 for both tables):

- α = n_k / k, ρ = 1/(1−α)
- f(1) = n_k/(2−α)
- f(i) = f(i−1)·(i−1)/(i+ρ) for i ≥ 2

For Chicago the footer (§) replaces this with ρ = ρ̄ from (2.31)–(2.32):
ρ̄ = p₁/(1−p₁), where p₁ = f(1)/n_k. The estimate column prints "—" at i = 1,
so that chain starts from the observed f(1).

## 2. Derivations (each re-checked numerically by `src/step0_checks.py`)

- **D1 — R is n_k times the Yule–Simon pmf.** The pmf is
  p(i) = ρ·B(i, ρ+1). Then p(1) = ρ/(ρ+1), and with ρ = 1/(1−α) that equals
  1/(2−α), which matches (2.21). The ratio p(i)/p(i−1) = (i−1)/(i+ρ) matches
  (2.11). So the recipe column is n_k·p(i), and over infinite support it sums
  to n_k exactly.
- **D2 — α = n_k/k is the method-of-moments estimator.** For ρ > 1 the Yule
  mean is ρ/(ρ−1). Substituting ρ = 1/(1−α) gives 1/α = k/n_k, which is the
  observed mean count per type. The recipe therefore fits ρ by moments,
  without likelihood. For ρ ≤ 2 the variance is infinite.
- **D3 — The 11+ row.** Simon's printed 11+ estimate is n_k minus his printed
  rows 1–10. Checked for Chem: 6,891 − 6,556 = 335. Under R the same
  construction gives n_k·P(I ≥ 11) = n_k·10·B(10, ρ+1), the Yule survival
  P(I > x) = x·B(x, ρ+1). The recipe 11+ cell is defined as that residual, so
  it follows the paper's own construction.
- **D4 — (4.2) is a shifted ρ = 1 Yule.** Write x = cβ. The ratio
  f(i)/f(i−1) = (i−1−x)/(i+1−x) gives f(i) ∝ 1/((i−x)(i+1−x)). From i = 1 the
  sum telescopes to 1/(1−x). Hence:
  - f(1)/n = 1/(2−x)
  - f(2)/f(1) = (1−x)/(3−x)
  - f(3)/f(2) = (2−x)/(4−x)
  - the tail is ∝ i⁻² for every x, so the tail ρ is 1 whatever c is.

  The p. 436 claim (c ≈ 0.2 for *Ulysses*, ≈ 0 for Eldridge) is therefore a
  claim about the head only, and it identifies x = cβ, not c. Note also that
  0 < c < 1 together with β ∈ [0, 1] forces x ≥ 0, so f(2)/f(1) ≤ 1/3 and
  f(1)/n ≥ 1/2.
- **D5 — Case II reduces correctly.** In (2.34), set n′ = α and n_k = αk. This
  gives ρ = 1/(1−α), which is (2.12). The equation is consistent.
- **D6 — Boundary row.** (2.12) states 1 < ρ < ∞, yet Table 1 prints an
  α = 0.0 row with ρ = 1. That is the boundary (1.6) case, where the mean is
  infinite. The row is a limit, not a member of the stated range. Minor.
- **D7 — (2.18) notation.** The display writes `Σ iB(i,ρ+1) ∼ i·i^{-(ρ+1)}`,
  which equates a series with its general term. The conclusion still holds:
  the mean converges if and only if ρ > 1. Notational only.
- **D8 — Printed typos (no effect on numbers).**
  - p. 436 `f(i) = Ka^{-(ρ+1)}` should read `i` for `a`.
  - p. 436 says the estimates come "from equation (1·3)". (1.3) defines the
    Beta function, and (1.2) is the distribution. The same sentence names
    (2.11) and (2.21), which settles the intent.
- **D9 — The Chicago ρ̄ derivation (seen; not a prediction).** 133/145 =
  0.91724 does not round to the printed 0.916. Rounding p₁ to three decimals
  first gives 0.478/0.522 = 0.91571, which does round to 0.916. Stage 1 tests
  this as convention C6b.

## 3. Stage 1 contract

### 3.1 Conventions (the complete list; nothing outside it counts as a reproduction)

Each Table 2/3 estimate cell is recomputed under every combination of the
following options.

- **ρ source**
  - A1: exact α = n_k/k.
  - A2: printed α (Table 2/3 α as printed).
  - A3: printed ρ (Table 3 footer; not available for Table 2).
  - A4: Table-1 interpolation, only for rows 1–3. f\*(i)/n_k is linearly
    interpolated in α between the bracketing printed Table 1 rows, at exact α.
- **Anchor**
  - B1: f(1) from (2.21), then chained.
  - B2: chained from the observed f(1).
  - B3: each cell from the *printed* previous estimate cell; row 1 falls back
    to B1. Under A4 the anchor is moot.
- **Rounding**
  - R1: nearest unit.
  - R2: three significant figures.
  - R3: nearest 10.

  All rounding is half-up.

That is 4 × 3 × 3 = 36 combinations, minus the ones that do not apply.

- **Chicago only:**
  - C6a: ρ = ρ̄ = 133/145, chained from the observed f(1).
  - C6b: ρ = ρ̄ from p₁ rounded to 3 decimals, chained the same way.

  Both are crossed with B3 and R1–R3.
- **11+ cell:** under every combination it is n_k minus that combination's
  rounded rows 1–10, following D3. The unrounded residual is reported
  alongside.

Table 1 is recomputed from its exact α grid with 3-decimal rounding, and ρ with
2-decimal rounding.

### 3.2 Labels (one per printed cell; precedence in this order)

1. **exact**: A1 + B1 (Chicago: C6a) with R1 equals the printed value.
2. **reproduced-under-X**: not exact, but at least one combination X gives the
   printed value. Every reproducing X is listed, together with the number of
   combinations tried. A cell reproduced by only one combination that is not
   A1 is flagged *weak* (forking-paths guard).
3. **rounding slip**: no combination reproduces the cell, and the printed
   value is exactly one unit in its last printed place away from the exact
   value rounded to the printed precision.
4. **not reproduced**: anything else. There is no ±1 tolerance outside label 3.

The **headline per column** is whether one single combination reproduces every
estimate cell in that column (the idea's kill criterion).

### 3.3 Grading the §IV.B sentences (p. 437 top)

Each sentence is graded under (i) the printed estimates and (ii) the recipe
values (A1 + B1, unrounded; for Chicago, C6a).

- **S1** "too high for i = 1, 2": per column, est > obs at i = 1 and at i = 2.
  Chicago i = 1 is undefined, so only i = 2 counts.
- **S2** "too low for i = 3, …, 10":
  - primary test, per column: Σ est over i = 3..10 < Σ obs.
  - secondary test: the count of individual cells with est < obs, out of 8.
  - verdict: **holds** if the primary test is true in all four columns.
- **S3** "in three of the four cases … again too high for the tails": the
  number of columns where est(11+) > obs(11+). The sentence **holds** if and
  only if that count is exactly 3.

### 3.4 The Chicago ρ′ = 1.07 search (exploratory; Table 3 counts only)

Candidates:

- E1: f(1)/f(2) − 2, which inverts (2.11) at i = 2.
- E2: log(S(1)/S(i))/log i for i = 2..11, where S(i) = #{≥ i} and S(11) = 23.
- E3: −1 − the OLS slope of log f on log i over i = 1..10, 2..10 and 3..10.
  Zero counts are excluded; Chicago has none.
- E4: OLS of log S(i) on log i over i = 1..11.
- E5: the Yule MLE with the 11+ cell censored.

A candidate **matches** if it rounds to 1.07 at 2 decimals. All candidates are
reported, and so is the number tried.

### 3.5 The p. 436 head-ratio check for (4.2)

Solve x = cβ from each of three head statistics, f(1)/n, f(2)/f(1) and
f(3)/f(2), for each word count, using D4.

- **Ulysses** is *head-consistent* with c ≈ 0.2 if all three x lie in
  [0.1, 0.3].
- **Eldridge** is *head-consistent* with c ≈ 0 if all three satisfy
  |x| ≤ 0.1.

A negative x is reported as lying outside the model's own range. This is a
head check only. The full (4.2) fit is Stage 5.

## 4. Contamination ledger (results already seen before the freeze)

Seen from the 2026-09-29/30 idea prospecting, or while deriving this contract:

- The recipe values f(1) for Chem, Physicists and Econometrica (4,054.5,
  823.1, 453.4), and the recipe f(2) values.
- Chicago's printed column matches ρ̄ to rounding (idea).
- Under the recipe, the 11+ cells are 29.9, 275.8, 36.6 and 18.1. As printed
  S3 holds (3 of 4); under the recipe it comes out 1 of 4.
- Table 2 recipe values: 15,860 / 5,068 / 2,454 and 3,221 / 1,020 / 491.
- D9.
- The head x values: Ulysses 0.18 / 0.18 (f(1)/n, f(2)/f(1)); Eldridge −0.02 /
  −0.14 / +0.17.

These are **leads**. Stage 1 re-derives them in code and reports them. They are
not counted as confirmed predictions.

## 5. Predictions (written before the Stage 1 code; not yet computed)

- **P1.** Physicists f(1) = 824 is reproduced by none of the combinations.
- **P2.** No single combination reproduces every estimate cell in the Chem,
  Physicists or Econometrica column.
- **P3.** At least one Chem cell in rows 3–10 is *not* reproduced under B3
  (chaining from the printed previous cell), so Simon's Chem column is not a
  clean chain from its own printed f(2).
- **P4.** Under R1–R3, no combination reproduces *Ulysses* f(1) = 15,850.
  Eldridge f(1) = 3,220 is reproduced under R2 or R3. No f(2) or f(3) cell of
  Table 2 is reproduced.
- **P5.** No ρ′ candidate in §3.4 rounds to 1.07.
- **P6.** S1 and S2 hold under both the printed and the recipe estimates.
- **P7 (carried to Stage 3; bands frozen at Stage 3 design):** the
  ENB loses to the Yule on Chem; the §III null for n_k/k is wider than the
  §II null; the declining-α null gives MLE < MoM.

---

## Amendments

### Amendment 1 (2026-11-01, before any Stage 2 fit): the Stage 2 contract

**Reason.** §3 froze Stage 1 only. This amendment fixes Stage 2's assertions
and the ρ′ re-test before any of them is computed. It adopts the seed idea's
Stage 2 "done when" and adds the ρ′ re-test.

- **A1.1 Custody.** Every download is kept unchanged under
  `data/raw/<source>/` and listed in `data/raw/MANIFEST.csv` with its URL,
  retrieval date, byte size and SHA-256. Upright renders are derived files and
  are labelled as such.
- **A1.2 Double entry.** Each table is entered twice, independently:
  - **First entry:** a fresh-context transcriber reads the page image and is
    barred from the OCR text.
  - **Second entry:** one of the following.
    - the OCR text layer (Lotka, Eldridge);
    - the other printing of the same table (Davis p. 431 against Lotka
      Table 1);
    - my own reading of the page image (Davis p. 429, Zipf's prose).
  - **Adjudication:** every disagreement is settled from the page image at
    zoom and logged in `data/sources/ADJUDICATION.md`. A sum constraint is
    never used to pick a reading. The final CSVs live in `data/sources/`.
- **A1.3 Type-A assertions**, each a test.
  - **Lotka Table 1:**
    - every count column sums to its printed Total;
    - A + B = A+B in every row;
    - k(A+B) = Σ n·count is reported against Simon's 22,939;
    - k(Auerbach) is reported against Simon's 3,396.
  - **Davis p. 431 against Lotka:** the two agree row by row after Lotka's
    ranged rows are resolved.
  - **Davis p. 429:** n = 278 and k = 1,124.
  - **Eldridge List 5:**
    - 6,002 types and 43,989 tokens;
    - f(1..9) equal the group headers;
    - the 499 words with i ≥ 10 sum to 43,989 − Σ_{i≤9} i·f(i) tokens.
  - **Zipf 1949:** 260,430 tokens, 29,899 types and 16,432 / 4,776 / 2,194,
    each with a page locator.
  - **External check:** the discrete power-law (zeta, x_min = 1) MLE on the
    Chem A+B table equals Smolinsky 2015's 1.9665 at 4 decimals. The
    log-likelihood is reported against their −11,705.1.
- **A1.4 The ρ′ re-test on Davis p. 429's full Chicago table.** The candidate
  list is closed.
  - F1: log(S(1)/S(x))/log x for every x in the support.
  - F2: the discrete power-law (Hurwitz) MLE with x_min ∈ {1, …, 5}, reported
    as α̂ − 1.
  - F3: the Yule MLE on the full table.
  - F4: OLS of log S(x) on log x over the support.
  - F5: Davis's printed graduation slope (p. 429, `log y = 3.74877 − 2.11012
    log x`) minus 1.
  - (2.29)'s ρ_i needs growth data and is recorded as *not testable*.

  **Grading.**
  - exactly one candidate rounds to 1.07 → "consistent with X";
  - several do → "underdetermined among …";
  - none does → "not reproduced".

  **Leads seen before this amendment** (seed idea): F2 at x_min = 3 gave
  1.067, and F1 at x = 10 gave 1.064.

  **Prediction P8:** ρ′ grades *underdetermined*, meaning at least two
  candidates round to 1.07.

### Amendment 2 (2026-11-01, before any Stage 3 code): the Stage 3 contract

**Reason.** The seed idea specifies Stage 3 only in outline. This freezes the
process definitions, estimators, datasets, verdict rule and the P7 bands
before any simulation is written or run.

- **A2.1 Data sets and the observed statistics.**

  | Set | Source | n | k | Censor point c | Full-table MLE? |
  |---|---|---|---|---|---|
  | Chicago | Davis p. 429 | 278 | 1,124 | 11 | yes |
  | Chem | Davis p. 431 | 6,891 | 22,939 | 11 | yes |
  | Physicists | Davis p. 431, source k | 1,325 | 3,398 | 11 | yes |
  | Econometrica | Simon Table 3 (rows 1–10 and 11+ only) | 721 | 1,759 | 11 | no |
  | Eldridge | List 5 (f(1..9) from the headers, plus 499 counts) | 6,002 | 43,989 | 11 | yes |
  | Ulysses | Zipf (f(1..3), n, k) | 29,899 | 260,430 | 4 | no |

  Statistics computed on each set:
  - ρ_MoM = k/(k−n), the recipe;
  - ρ_cens, the Yule MLE with categories 1..c−1 and "≥ c", where
    P(I ≥ c) = (c−1)·B(c−1, ρ+1);
  - ρ_full, the Yule MLE on the whole table, where available;
  - the gap G = ρ_cens − ρ_MoM (primary) and G_full = ρ_full − ρ_MoM;
  - p1 = f(1)/n and r21 = f(2)/f(1).

  Each MLE is a bounded scalar maximisation over ρ ∈ [0.05, 20].
- **A2.2 The processes.** All are simulated at the set's real k. Throughout,
  "copy" means: pick one existing token uniformly at random and repeat its
  type.
  - **§II (constant α).** α = n/k. Token 1 is a new type. For t ≥ 2, with
    probability α the token is a new type, otherwise a copy.
  - **Case II (declining α).** As §II, but α(t) = min(1, β·A·t^(β−1)) with
    A = n/k^β, so E[n(k)] ≈ n. The grid is β ∈ {1.0, 0.9, 0.8, 0.7, 0.6}, and
    β = 1.0 is §II itself. No β is fitted; every grid point is reported.
  - **§III (slice with Assumption III).**
    1. Start from a §II sample of length k with α = n/k.
    2. Run B = 3k steps. Each step adds one token by the §II rule.
    3. While the length exceeds k, delete one whole type, chosen uniformly
       among the current types, with all its tokens.
    4. Take the snapshot after B steps.

    This is one concrete reading of "drop words at the same average rate so
    the length remains k". Convergence check: for Physicists, the medians of
    p1 and G at B = 3k and B = 6k differ by less than one null-SD. Otherwise
    report it as a caveat.
- **A2.3 Replicates.** 1,000 per (set, process, β), except §III for
  *Ulysses*, which gets 200 for compute. Seeds are fixed and recorded. Each
  replicate yields the same statistics as A2.1, computed the same way. A
  replicate's n is random, and its MoM uses that replicate's own n and k.
- **A2.4 Verdicts, effect sizes and joint reproduction.**
  - **Reproduction of a statistic:** a process reproduces it if the observed
    value lies within the null's central 95% interval (2.5th–97.5th
    percentiles).
  - **Joint reproduction:** a (set, process, β) reproduces jointly if G, p1
    and r21 are all reproduced.
  - **Effect size:** the robust z = (G_obs − median)/(IQR/1.349), plus the
    observed G's percentile.
  - **What is not claimed:** a significance test of "the Yule is wrong"; see
    the idea's narrowing.
- **A2.5 Self-test (estimator validation; Type-A gate).**
  - For each set, draw 1,000 iid Yule samples of size n at ρ = ρ_MoM
    (`scipy.stats.yulesimon`).
  - The profile-likelihood 95% CI (log-likelihood drop 1.92) of ρ_full (of
    ρ_cens for Econometrica and Ulysses) must cover the planted ρ in
    [92.9%, 97.1%] of replicates (±3 SE).
  - A failure blocks the Stage 3 verdicts until fixed.
  - The process nulls' own coverage is reported as a result, not a gate.
- **A2.6 Leads seen before this amendment** (seed idea, 200-replicate pilot):
  - observed G of −0.371 (Chicago, censored), −0.185 (Chem), −0.202
    (Physicists) and −0.177 (Econometrica);
  - a §II null gap of −0.002 ± 0.019 for Chem.
- **A2.7 Predictions.**
  - **P7b:** for every set, the 95% width of n/k under §III exceeds the width
    under §II.
  - **P7c:** for every set, the median null G is < 0 at every β < 1, and it
    falls monotonically as β decreases.
  - **P9 (lead):** §II does not reproduce the observed G for Chem,
    Physicists or Econometrica.
  - **P10:** no (process, β) reproduces Chem jointly.
  - **P11:** the self-test passes for all six sets.

### Amendment 3 (2026-11-02, before any Stage 4 code): the Stage 4 contract

**Reason.** The seed idea specifies Stage 4 only in outline. This freezes the
data sets, the model list, the estimators, the comparison and grading rules,
the Sichel target and P7a before any Stage 4 fit is written or run. The reprint
check came first: *Models of Man* (1957) ch. 9 prints all 152 table cells
unchanged (`paper/PROVENANCE.md`), so the Stage 1 labels stand as labels of
the text in both printings.

- **A3.1 Data sets** (from `load_sets()` in `src/stage3.py`, unchanged).

  | Set | Table used | n | k |
  |---|---|---|---|
  | Chicago | full, Davis p. 429 | 278 | 1,124 |
  | Chem | full, Davis p. 431 (A+B) | 6,891 | 22,939 |
  | Physicists | full, Davis p. 431, source k | 1,325 | 3,398 |
  | Eldridge | full, List 5 | 6,002 | 43,989 |
  | Econometrica | censored: rows 1–10 and "11 or more" | 721 | — |

  *Ulysses* is left to Stage 5: four cells cannot separate models with up to
  three parameters.
- **A3.2 Models.** All are on x ≥ 1 (zero-truncated where the family has a
  zero class). Parameter ranges are the optimizer bounds.

  | Model | Params | Form | Range |
  |---|---|---|---|
  | Yule | 1 | ρB(x, ρ+1) | ρ ∈ [0.05, 20] |
  | Zeta | 1 | x^(−s)/ζ(s) | s ∈ (1, 10] |
  | Log-series | 1 | −θ^x/(x·log(1−θ)) | θ ∈ (0, 1) |
  | Sichel (GIGP ν=−0.5, α=0) | 1 | ENB with r = −0.5 fixed | θ ∈ (0, 1] |
  | Waring (3.8) | 2 | ρΓ(1+c+ρ)/Γ(1+c) · Γ(x+c)/Γ(x+1+c+ρ) | ρ ∈ [0.05, 20], c ∈ (−1, 50] |
  | Cutoff Yule (1.1) | 2 | B(x, ρ+1)·b^x / [b/(ρ+1)·₂F₁(1,1;ρ+2;b)] | ρ ∈ [0.05, 20], b ∈ [10⁻³, 1] |
  | ENB / ZTNB | 2 | Γ(x+r)/(x!Γ(r)) θ^x / ((1−θ)^(−r) − 1) | r ∈ (−1, 50], r ≠ 0; θ ∈ (0, 1], with θ = 1 only for r < 0 |
  | GIGP (Sichel 1985 form, zero-truncated) | 3 | (3.1) of Bogachev et al. 2023 / (1 − f₀) | ν ∈ [−5, 5], α ∈ [10⁻⁶, 50], θ ∈ (0, 1) |

  - Waring at c = 0 and the cutoff at b = 1 are the Yule. The ENB at r → 0 is
    the log-series. The GIGP at α → 0 is the ENB with r = ν. These identities
    are unit tests (A3.7) before any data fit.
  - The Waring is Simon's own generalization: (3.8) with 1/λ = ρ.
- **A3.3 Estimation.**
  - All fits are maximum likelihood on the table as given: full tables
    exactly; Econometrica with the 11+ cell as survival mass.
  - One-parameter models use a bounded scalar search. Models with two or three
    parameters use L-BFGS-B on the stated box, from a fixed grid of starts
    (all combinations of 3 values per parameter, spread across each range),
    keeping the best.
  - A fit at a box bound is reported as such.
- **A3.4 Comparison.**
  - Per set: log-likelihood, AIC and ΔAIC to the best model.
  - **Against the Yule, nested rivals** (likelihood ratio):
    - Waring: c = 0 is interior, so χ²₁;
    - cutoff: b = 1 is a boundary, so ½χ²₀ + ½χ²₁.

    The rival is favoured if p < 0.05; otherwise "Yule adequate".
  - **Against the Yule, non-nested rivals** (zeta, log-series, Sichel, ENB,
    GIGP): the Vuong z on per-observation log-likelihood differences, with
    no parameter-count correction. |z| > 1.96 favours the side it points to;
    otherwise "indistinguishable". AIC is reported beside it.
- **A3.5 Goodness of fit and the grade of "reasonably good".**
  - **Parametric bootstrap:** B = 500 samples of size n from each fitted
    model, each refitted by A3.3.
  - **Statistics:** Pearson X² on Simon's 11 cells (1, …, 10, ≥ 11), for
    every set; and the KS distance on the CDF, for the full tables only.
  - **Model p-value:** the share of replicates whose statistic is at least
    the observed value.
  - **Grade of "reasonably good" (p. 437):**
    - *holds* for a set if the Yule's X² p ≥ 0.05;
    - *fails* if p < 0.05;
    - in either case, also report whether the Yule is within ΔAIC ≤ 2 of
      the best model.

    Graded on the four Table 3 sets. Eldridge is reported but not graded,
    since Table 2 prints only f(1..3).
- **A3.6 The Sichel target.**
  - Sichel 1985 (via Bogachev et al. 2023 §7.1) fixed ν = −0.5 and α = 0
    and estimated θ = 0.96876 on Lotka's Chem data (χ² p = 91.8%, grouping
    not stated).
  - **Two candidate estimators of θ:**
    - the MLE;
    - the mean-matching estimator, i.e. the model mean set equal to k/n.
  - **Grades:**
    - *reproduced* if either estimator rounds to 0.96876 at five decimals;
    - *consistent with* if either is within ±0.0005;
    - otherwise *not reproduced*.
  - Sichel's χ² is not re-graded, because his grouping is unknown. An X² with
    tail cells merged to expected ≥ 5 is reported as exploratory only.
- **A3.7 Gates (Type A; any failure blocks the verdicts).**
  - **Pmf normalization:** each pmf sums to 1 within 10⁻⁶, using
    tail-inclusive sums where the tail is heavy.
  - **Nesting identities (A3.2)** hold within 10⁻⁶ in log-likelihood on
    Chem.
  - **Samplers:** each matches its pmf on 10⁵ draws (Pearson X² on cells
    1..10 and ≥ 11, p > 0.001).
  - **Smolinsky:** the zeta fit reproduces Smolinsky's Chem MLE 1.9665 to
    four decimals (as in Stage 2).
- **A3.8 Leads seen before this amendment.** These are not counted as
  predictions:
  - the seed's full-table Yule MLEs (Chem 1.277, Physicists 1.472,
    Chicago 1.018);
  - the Yule-over-zeta ΔLL of +24.0 / +14.7 / +4.9;
  - the seed's ENB arithmetic on Chem: the head implies r ≈ −0.47 and the
    tail r ≈ −0.97;
  - Sichel's α = 0, read while writing this amendment, which makes his
    model an ENB with r = −0.5 and his 91.8% χ² p a fit of that ENB.
- **A3.9 Predictions** (written before any Stage 4 code).
  - **P7a:** on Chem, the two-parameter ENB loses to the Yule on AIC
    (AIC_ENB > AIC_Yule).
  - **P12 (lead):** the Yule beats the zeta on Vuong (z > 1.96) for Chem
    and Physicists.
  - **P13:** the Yule's X² bootstrap p < 0.05 on Chem; that is,
    "reasonably good" fails there.
  - **P14:** the Sichel θ is reproduced or consistent (A3.6).
  - **P15:** the best-AIC model on Chem has at least two parameters.
- **A3.10 Seeds and size.** MASTER_SEED 19551102, recorded per task. All
  fits and bootstraps are in `src/stage4.py`, written to
  `results/stage4/`.

### Amendment 4 (2026-11-02, before any Stage 5 code): the Stage 5 contract

**Reason.** Stage 5 tests the word-count sentences of p. 436 on full
distributions. The seed idea gives only an outline. This freezes the counts,
tokenizers, estimators, grades and predictions before any Stage 5 code.

- **A4.1 The claims under test** (p. 436, below Table 2):
  - **C1:** Table 2's actual columns: f(1..3), with n and k.
  - **C2:** "the observed value of n_k/k leads to an estimate of ρ in the
    neighbourhood of 1.1 to 1.2".
  - **C3:** "an empirical fit to the whole distribution of a function of the
    form f(i) = Ki^(−(ρ+1)) gives an estimated value of ρ, in both cases, of
    about one".
  - **C4:** "a good fit to both … can also be obtained from (4.2), with c
    equal to about 0.2 in the former case, and close to zero in the latter".
    p. 435 adds that c should be larger for *Ulysses* than for Eldridge.
  - **C5:** property (c) of p. 426: f(2)/f(1) near one-third, f(1)/n near
    one-half. Reported, not graded.
- **A4.2 Counts.**
  - **Eldridge:** List 5 as ingested (Stage 2).
  - **Hanley:** the Zipf figures (f(1..3), n, k), censored at 4. It enters
    only the censored estimators.
  - **Three Gutenberg recounts.** Source: `data/raw/gutenberg4300/pg4300.txt`
    (edition updated 2025-11-27; MANIFEST row). Common preparation:
    1. Take the body from the line beginning "Stately, plump Buck Mulligan"
       up to the `*** END` marker.
    2. Drop the part markers ("— I —", "— II —", "— III —") and the
       episode markers ("[ n ]").
    3. NFC-normalize, map ’ to ', and lowercase.

    The three tokenizers:
    - **T1 (letters):** maximal runs of letters, where a letter is any
      Unicode alphabetic character.
    - **T2 (internal ' and -):** runs of letters joined by single internal
      apostrophes or hyphens.
    - **T3 (internal ' only):** as T2, but hyphens split.

  The recounts are labelled **not a replication** of Hanley, who used his own
  text and his own rules for what counts as a word.
- **A4.3 Estimators, per count.**
  - **For C2:** ρ_MoM = k/(k − n), plus the recipe's Table 2 estimates of
    f(1..3).
  - **For C3, on full counts only:**
    - **E1:** the discrete power-law MLE on x ≥ 1, with ρ = s − 1;
    - **E2:** the OLS slope of log f(i) on log i over all i with f(i) > 0,
      with ρ = −slope − 1;
    - **E3:** the OLS slope over log₂ bins [2^j, 2^(j+1)), using the bin count
      divided by the bin width and the bin's geometric midpoint, with
      ρ = −slope − 1.
  - **The Yule MLE**, full or censored, with a profile 95% CI. This is
    compared with Leisen et al. (Gutenberg *Ulysses*, n = 29,841,
    ρ = 1.09, CrI 1.08–1.11).
  - **For C4:** the (4.2) pmf p(i) = (1−x)/((i−x)(i+1−x)), with x = cβ.
    Its survival function is P(I ≥ i) = (1−x)/(i−x), and exact draws come
    from I = ⌊x + (1−x)/U⌋.
    - Fit by MLE, full or censored, constrained to x ∈ [0, 0.999] (the
      verdict).
    - Also fit unconstrained, x ∈ [−5, 0.999], as a diagnostic only.
    - Goodness of fit: a parametric bootstrap with B = 500 and a refit per
      replicate, using Pearson X² on cells 1..10 and ≥ 11 (for Hanley:
      cells 1, 2, 3 and ≥ 4). The p-value is the share of replicates at or
      above the observed statistic.
- **A4.4 Grades.**
  - **C1:** holds for Eldridge if all five numbers equal the printed or
    stated values. For *Ulysses*, report each tokenizer's distance from
    Hanley; this is not graded.
  - **C2:** holds for a count if ρ_MoM ∈ [1.05, 1.25].
  - **C3:** holds for a count and estimator if ρ ∈ [0.85, 1.15].
  - **C4 "about 0.2" (each *Ulysses* count):** holds if the constrained
    x̂ ∈ [0.1, 0.3]. Since x = cβ ≤ c, this bounds c from below only.
  - **C4 "close to zero" (Eldridge):** holds if the constrained x̂ ≤ 0.1.
  - **C4 "a good fit":** holds if the X² p ≥ 0.05.
  - **C4 ordering:** holds if every *Ulysses* x̂ exceeds Eldridge's.
- **A4.5 Gates** (Type A):
  - **Pmf normalization:** the (4.2) pmf sums, with its exact tail, to 1
    within 10⁻¹².
  - **Sampler:** the exact (4.2) sampler matches its pmf on 10⁵ draws (X²
    p > 0.001).
  - **Eldridge totals** equal 6,002 types and 43,989 tokens.
  - **Tokenizer sanity:** each tokenizer's k lies within ±5% of Hanley's
    260,430.
- **A4.6 Leads seen before this amendment.** These are not counted as
  predictions:
  - Stage 1's head x for Hanley (0.180 / 0.180 / 0.3005);
  - Stage 4's Eldridge zeta MLE s = 1.8323, i.e. E1 ρ = 0.83;
  - the Eldridge Yule MLE 1.054;
  - the seed's prospecting on an older Gutenberg file with a T2-like
    tokenizer: n = 29,752, k = 264,411, f(1..3) = 16,207 / 4,799 / 2,190,
    MoM 1.127, Yule MLE 1.091;
  - the current file's character inventory: 4,495 right single quotes and
    247 hyphens in the whole file.
- **A4.7 Predictions.**
  - **P16 (lead):** C1 holds for Eldridge.
  - **P17:** every tokenizer's n is below Hanley's 29,899.
  - **P18:** C4 "about 0.2" holds for all three tokenizers.
  - **P19:** C4 "close to zero" holds for Eldridge, and the ordering holds.
  - **P20:** C4 "a good fit" fails for Eldridge and for every tokenizer.
  - **P21 (lead):** C3 under E1 fails for Eldridge.
- **A4.8 Seeds.** MASTER_SEED 19551103. Code in `src/stage5.py`; outputs
  in `results/stage5-*`.

### Erratum 1 (2026-11-02, after the reviewer audit in `audit.md`)

A3.5 locates "reasonably good" on p. 437. The sentence is on p. 436: it
ends just before the page break, and the tail sentence that follows it is at
the top of p. 437. The grading rule and every outcome are unchanged.

### Erratum 2 (2026-11-02, at publication)

The reviewer audit cited in Erratum 1 as `audit.md` is published as
`AUDIT-2026-11-02.md`, with the same content apart from two local paths
(see its opening note).

### Erratum 3 (2026-11-02, at publication, after the reader review)

Erratum 2 says the published audit differs "apart from two local paths". It
differs in three: the reviewed-project path and the two evidence links. Every
frozen version of this file, and its recorded SHA-256, can be rebuilt and checked
with `python src/verify_prereg_freezes.py`.


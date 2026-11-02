# Report: Simon (1955), recomputing the printed Yule fits

The report follows the six stages in order, with the reprint check between
Stages 3 and 4. Each section names its own scripts and outputs, and
`README.md` lists the full rebuild. Stage 1's numbers come from
`src/recipe.py` (frozen contract: `PREREGISTRATION.md`) or
`src/implied_rho.py` (exploratory, written after the freeze). A reviewer
audit by a different model family is in `AUDIT-2026-11-02.md`; the corrections it led
to are listed at the end of this report.

## Stage 1 (2026-11-01): recipe recompute and convention search

### Headline

1. **Simon's §IV.B tail sentence does not survive his own recipe.** As
   printed, the "11 or more" estimates exceed the observed counts in 3 of 4
   columns, which is what the text says. Recomputed from (2.11) + (2.21), they
   exceed them in 1 of 4: Chicago only.

   | 11+ cell | Chicago | Chem | Physicists | Econometrica |
   |---|---|---|---|---|
   | observed | 23 | 419 | 48 | 22 |
   | printed estimate | 30 | 335 | 52 | 25 |
   | recipe estimate | 29.9 | 275.8 | 36.6 | 18.1 |

   Every printed 11+ cell is n_k minus the printed rows 1–10, so any shortfall
   in rows 1–10 lands in the tail. The rows run low from the f(2) step down:
   - The step from f(1) to f(2) is off in every printed series. Inverting
     (2.11) on the printed f(2)/f(1) gives a ρ above the recipe ρ by:
     - Chem: 1.49 vs 1.43
     - Physicists: 1.80 vs 1.64
     - Econometrica: 1.81 vs 1.69
     - *Ulysses*: 1.25 vs 1.13
     - Eldridge: 1.30 vs 1.16
   - In Table 3 the later steps then scatter around the recipe ρ
     (`results/stage1-implied-rho.csv`).
   - For Chem the shortfall in rows 1–10 is 59.2 persons. By construction that
     equals the gap between the printed 11+ (335) and the recipe 11+ (275.8),
     since both 11+ cells are n_k minus rows 1–10.
2. **No single stated convention reproduces a whole column, except Chicago's.**
   Each column was tested against up to 36 combinations:
   - ρ source: α exact, α printed, ρ printed, or Table-1 interpolation
   - anchor: (2.21), the observed f(1), or the previous printed cell
   - rounding: units, 3 significant figures, or tens

   None reproduces every estimate cell of Chem, Physicists, Econometrica or
   either Table 2 row. Chicago's column (ρ̄, chained from the observed f(1),
   rounded to units) reproduces every cell, including 11+.
3. **The sentences about the head hold.** "Too high for i = 1, 2" holds in all
   four columns, both as printed and under the recipe (Chicago at i = 2 only:
   its f(1) estimate is printed "—"). "Too low for i = 3..10"
   holds only for the summed band, which is the contract's primary test, in
   every column. Cell by cell it is roughly a coin toss: est < obs in 4, 6, 6
   and 4 of the 8 cells.
4. **No constant-ρ chain can produce the printed Chem column, whatever ρ and
   f(1) are.**
   - Allow the four-digit cells ±5 (rounding to tens) and f(3) ±0.5.
   - The printed f(2)/f(1) step then needs ρ ∈ [1.472, 1.511].
   - The printed f(3)/f(2) step needs ρ ∈ [1.421, 1.468].
   - The two intervals do not overlap, so the column is not a single (2.11)
     chain under any ρ.

   The fresh-context reviewer found this, and it was re-derived by hand here.
   It is outside the frozen contract and is reported as an observation.
5. **Table 2 is not reproducible from the stated recipe.**
   - The recipe gives 15,860 / 5,068 / 2,454 for *Ulysses* and 3,221 / 1,020 /
     491 for Eldridge.
   - Simon printed 15,850 / 4,870 / 2,220 and 3,220 / 977 / 400.
   - Only Eldridge f(1) reproduces (3 s.f., tens, or the printed α 0.136 with
     unit rounding).
   - The printed ratios imply ρ 1.25 then 1.39 (*Ulysses*) and 1.30 then 1.89
     (Eldridge), so no single Yule fits either printed row.
   - Caveat: k and n_k for Table 2 are not printed in the paper. They are
     carried from a pre-study source check; Stage 2 re-read them from the
     sources and they hold.

### Cell labels (`results/stage1-cells.csv`)

| Table | exact | reproduced under a convention | rounding slip | not reproduced |
|---|---|---|---|---|
| Table 1 (28 cells) | 26 | n/a | 2 | 0 |
| Table 2 (6 cells) | 0 | 1 | 0 | 5 |
| Table 3 (43 cells) | 22 | 13 (one weak) | 2 | 6 |

Points worth naming:

- **Table 1.** f\*(1)/n_k at α = 0.1 is printed 0.527 (true 0.52632), and
  f\*(2)/n_k at α = 0.3 is printed 0.171 (true 0.17157). Both are rounding
  slips. Simon & Van Wormer 1963 print the 0.527 again (their Table 1, col. 1a;
  not re-checked here).
- **Physicists f(1)** is printed 824, against a recipe value of 823.07. No
  convention gives 824, so it is a rounding slip.
- **Chem.**
  - f(2) = 1,160 reproduces only when chained from the *observed* f(1)
    (3,991) at 3 s.f. or tens. That is not what the text says.
  - f(3) = 522 is reproduced by no convention, including chaining from the
    printed f(2), which gives 523.8.
  - f(10) = 38 is a rounding slip (39.42).
- **Not reproduced (6 cells):**
  - Chem f(3)
  - the f(2) cells of Physicists (217 vs 226.1) and Econometrica (119 vs
    122.7)
  - the Chem, Physicists and Econometrica 11+ cells listed above
- **Footer.** α and ρ for Chem, Physicists and Econometrica round correctly.
  Chicago's ρ̄ = 133/145 = 0.9172 does not round to the printed 0.916. Rounding
  p₁ = 0.478 first gives 0.9157, which does.

### Chicago ρ′ = 1.07

Sixteen candidates computable from Table 3 alone were tried (§3.4 of the
contract). None rounds to 1.07. The nearest are:

- the survival slope to i = 10: 1.064
- the f(1)/f(2) inversion: 1.093
- the survival OLS: 1.033

The censored Yule MLE is 0.958. Stage 2 re-tests ρ′ on Davis p. 429's full
table.

### The (4.2) head check, *Ulysses* c ≈ 0.2 and Eldridge c ≈ 0

Under (4.2) the quantity identified is x = cβ, not c (contract D4).

- **Ulysses.** f(1)/n and f(2)/f(1) both give x = 0.180. f(3)/f(2) gives
  0.3005, which is 0.0005 outside the frozen [0.1, 0.3] band, so the frozen
  verdict is *not head-consistent*. The disagreement between the third
  statistic and the first two is the substantive part, not the margin.
- **Eldridge.** x = −0.017, −0.138 and +0.167. That is *not head-consistent*
  with c ≈ 0, and two of the three values lie outside the model's own x ≥ 0
  range.

The full-distribution (4.2) fit is Stage 5.

### Predictions (contract §5)

| | Prediction | Outcome |
|---|---|---|
| P1 | Physicists f(1) = 824 is reproduced by no convention | held |
| P2 | No single convention reproduces Chem, Physicists or Econometrica | held |
| P3 | At least one Chem cell in rows 3–10 is not reproduced by chaining from the printed previous cell | held (rows 3, 7, 10) |
| P4 | *Ulysses* f(1) is not reproduced; Eldridge f(1) is reproduced under R2/R3; no Table 2 f(2)/f(3) cell is reproduced | held |
| P5 | No ρ′ candidate gives 1.07 | held |
| P6 | S1 and S2 hold under both | held |

P3–P6 rest partly on leads seen before the freeze (contract §4). Only P1, P2
and P5 were blind.

### Independent check (2026-11-01)

**Who checked, and how independent.** A fresh-context Claude subagent (same
model family) worked from the page images and the PDF alone. It was barred
from `src/`, `results/` (except the page renders), the contract, this report
and the project's planning notes. It wrote its own scripts outside the project. The
check is independent in context and implementation, not in model family.

**What it confirmed:**
- All 152 transcribed cells match the images.
- The 11+ residual construction holds in all four columns.
- Every recipe value agrees with the ones above.
- So do the S1/S3 grades (S3: 3 of 4 printed, 1 of 4 recipe) and both Table 1
  slips.
- ρ′ is not reproduced. Its nearest values were 1.064, 1.080 and 1.093.
- f(1)→f(2) is the main misfit. The ρ implied by the printed step is
  1.49 / 1.80 / 1.81 / 1.25 / 1.30, against the recipe's 1.43 / 1.64 / 1.69 /
  1.13 / 1.16.

**What it added:**
- the Chem no-overlap result (headline 4);
- (4.2) does not fit Table 2's *printed estimates* either: x = 0.113 vs 0.324
  for *Ulysses*, 0.129 vs 0.616 for Eldridge;
- an unstated shifted ratio (i−1+c)/(i+ρ+c) with ρ refitted per column fits all
  of Table 3. That is a three-parameter description, not the stated recipe. It
  is recorded as a lead only.

**Disagreements:** none.

## Stage 2 (2026-11-01): source tables ingested, Chicago ρ′ re-tested

Contract: PREREGISTRATION.md Amendment 1, frozen before any fit (SHA-256 and freeze time in `results/prereg-freezes.txt`). Code: `src/stage2.py`. Data: `data/sources/`, double-entered
and adjudicated; see `data/sources/ADJUDICATION.md`. Custody:
`data/raw/MANIFEST.csv`. Tests: `tests/test_stage2.py`.

### What is now on disk, page-located

| Source | Pages | Table | n | k |
|---|---|---|---|---|
| Lotka 1926, *J. Wash. Acad. Sci.* 16(12), Table 1 | 318–319 | Chem A, B and A+B; Auerbach | 1,543 / 5,348 / 6,891; 1,325 | A+B 22,939; Auerbach 3,398 |
| Davis 1941, *Analysis of Economic Time Series* | 429 | Chicago (AMS) | 278 | 1,124 |
| Davis 1941 | 430 | the cumulative graduation table | | |
| Davis 1941 | 431 | Chem (A+B); Auerbach | 6,891; 1,325 | 22,939; 3,398 |
| Eldridge 1911, List 5 | 49–56 | the 499 words with i ≥ 10 (counts), plus the f(1..9) headers | 6,002 | 43,989 |
| Zipf 1949 | 23, 31 | *Ulysses* totals and f(1..3) | 29,899 | 260,430 |

All 18 hard assertions pass:
- every column total;
- A + B = A+B in every row;
- Davis = Lotka row by row;
- Eldridge closes at 6,002 types and 43,989 tokens (the 10+ words carry
  31,984);
- the Zipf numbers.

**External check.** The zeta MLE on the Chem table is α̂ = 1.966494, which
matches Smolinsky 2015's 1.9665. The log-likelihood is −11,705.31 against
their −11,705.1.

### Findings

1. **Simon's k for the Physicists is 2 papers short of his source.** Both
   printings of the Auerbach table give Σ n·count = 3,398. Simon prints 3,396.
   No Stage 1 label changes: the recipe's f(1) moves from 823.07 to 822.95.
   This is a transcription-level discrepancy, not a reproducibility problem.
2. **Davis's Chicago graduation is a cumulative fit.**
   - The p. 430 table's "y (actual)" is the number of people with at least
     (x − 3) papers, in classes 7 wide: 278, 36, 13, …. All 10 rows reproduce
     from p. 429.
   - So the p. 429 equation, log y = 3.74877 − 2.11012 log x, regresses
     *cumulative* counts on class midpoints. Its 2.11 is not a pmf exponent.
3. **Chicago ρ′ = 1.07.**
   - Exactly one of the 34 frozen candidates rounds to 1.07: the
     discrete power-law MLE above x_min = 3, at 1.0673 (n = 102).
   - Under the contract's rule that grades "consistent with zeta MLE,
     x_min = 3". **The prediction P8 (underdetermined) failed.**
   - That label should not be read as evidence about how Simon got 1.07. The
     34 candidates spread over 0.80–1.37, so about 0.6 hits in a 0.01-wide
     window are expected by chance. A Hurwitz-zeta MLE is also an unlikely
     1955 hand computation.
   - The nearest hand-computable candidates were the two-point survival
     slopes to x = 10 and x = 12. Both give 1.06.
   - ρ′ stays unexplained in any sense stronger than "one numerical
     coincidence fits".

### Predictions (Amendment 1)

| | Prediction | Outcome |
|---|---|---|
| P8 | ρ′ grades *underdetermined*: at least two candidates round to 1.07 | **failed**: exactly one of 34 candidates rounds to 1.07 (the zeta MLE above x_min = 3, 1.0673), at about the rate chance gives |

## Stage 3 (2026-11-01): moments against likelihood, inside Simon's own processes

Contract: PREREGISTRATION.md Amendment 2, frozen before any Stage 3 code
(SHA-256 and freeze time in `results/prereg-freezes.txt`). Code: `src/stage3.py` (run in 84 s on 6
workers) and `src/stage3_table.py`. Outputs:
- `results/stage3-summary.json`
- `results/stage3-verdicts.md` (the full tables)
- `results/stage3/` (one CSV per null, one row per replicate)
- `results/stage3-selftest.csv`

Tests: `tests/test_stage3.py`.

### The question

Simon's recipe α = n/k is the method-of-moments (MoM) estimate of the Yule ρ.
On the real tables it sits well above the likelihood estimate. The gap is
G = ρ_MLE(censored) − ρ_MoM.

| Set | ρ MoM | ρ MLE (censored) | ρ MLE (full) | G |
|---|---|---|---|---|
| Chicago | 1.329 | 0.958 | 1.018 | −0.370 |
| Chem | 1.429 | 1.244 | 1.277 | −0.185 |
| Physicists | 1.639 | 1.438 | 1.472 | −0.202 |
| Econometrica | 1.695 | 1.518 | — | −0.177 |
| Eldridge | 1.158 | 1.052 | 1.054 | −0.106 |
| *Ulysses* (censored at 4+) | 1.130 | 1.158 | — | **+0.028** |

Is a gap this size what Simon's processes produce at these sample sizes, and
if so, which process?

### Results

**The estimators are sound.** Profile-likelihood 95% intervals on iid Yule
samples cover the planted ρ in 93.5–95.3% of 1,000 replicates per set. That
is inside the frozen band in every set.

**§II, constant α (the recipe's own premise), produces no gap.**
- Its median G is −0.023 to 0.000 in every set.
- Each observed G lies outside its 95% interval: at the 0.0th percentile for
  the five negative gaps, and at the 99.8th for *Ulysses*, whose gap has the
  opposite sign.
- So the distance between moments and likelihood is not estimator noise. At
  these sample sizes it is evidence against the constant-α process itself.

**Case II, declining α, produces the gap's direction.**
- Its median G falls monotonically as the decline steepens (β = 0.9 → 0.6),
  in every set.
- **Joint reproduction** (G, p1 = f(1)/n and r21 = f(2)/f(1) all inside the
  null's 95% interval) occurs for Chicago at β = 0.7 and 0.6, and for
  Physicists and Econometrica at β = 0.9.

**§III, the slice with whole-type deletion, is much more variable.**
- Its 95% interval for n/k is 2.8–19× wider than §II's.
- It reproduces Econometrica and Eldridge jointly.

**Nothing in the frozen grid reproduces Chem or *Ulysses* jointly.**
- **Chem:** its gap lies between Case II β = 0.9 (median −0.137) and 0.8
  (median −0.258). But f(1)/n and f(2)/f(1) both fall outside the null at both
  neighbours, and f(2)/f(1) also falls outside under §II and §III. So a β
  between the grid points would fix G but not the shape.
- ***Ulysses*:** §III covers its G but not its head shape.

| Set | §II | Case II (β that reproduces jointly) | §III |
|---|---|---|---|
| Chicago | ✗ | 0.7, 0.6 | ✗ |
| Chem | ✗ | none | ✗ |
| Physicists | ✗ | 0.9 | ✗ |
| Econometrica | ✗ | 0.9 | ✓ |
| Eldridge | ✗ | none (G fits at 0.9; shape does not) | ✓ |
| *Ulysses* | ✗ | none | ✗ (G fits; shape does not) |

### Reading

- **Simon & Van Wormer's direction holds.** Moments run above likelihood
  when α declines, as they said. In this grid, declining α is consistent
  with the gap and the head shape together for three of the four bibliometric
  sets, at one or two adjacent grid points (Chicago at β 0.7 and 0.6;
  Physicists and Econometrica at 0.9). Econometrica is also reproduced by §III, so the grid
  does not single out one mechanism there.
- **No single mechanism covers all six sets.** The largest bibliometric set
  (Chem, n = 6,891) is reproduced by none of the six process settings.
  That is consistent with Simon's own closing remark on Table 3 that "a
  further refinement of the model is apparently needed".
- ***Ulysses* behaves differently.** Its likelihood estimate is above MoM. Its
  data are thinner, though (f(1..3) only, censored at 4).

### Predictions (Amendment 2)

| | Prediction | Outcome |
|---|---|---|
| P7b | §III's n/k interval is wider than §II's in every set | held (2.8–19× wider) |
| P7c | Case II median G < 0 for β < 1, falling as β falls, in every set | held |
| P9 | §II does not reproduce G for Chem, Physicists, Econometrica | held (a lead; in fact it fails in all six) |
| P10 | nothing reproduces Chem jointly | held |
| P11 | the self-test passes in all six sets | held |

### Caveats

- **β is a grid, not a fit.** "Reproduces" means each of three statistics
  lies inside its own 95% interval. It is not a joint test. With up to
  six settings per set, some coverage by chance is expected. Treat a single
  ✓ as "consistent with", not as identification.
- **Case II's n runs slightly short.** Clipping α(t) at 1 makes the expected
  n fall short of the target at low β: up to 4.9% (Econometrica, β = 0.6).
  Every joint reproduction occurs where the shortfall is ≤ 2.4%. Each
  replicate's MoM uses its own n and k, so G is internally consistent.
- **§III snapshots can be shorter than k.** The median snapshot length is
  within 0.4% of k in every set. The 2.5th percentile is lower, down to 64% of
  k for Chicago, because deleting one large type removes many tokens at once.
  This is the literal Amendment 2 rule.
- **The §III convergence check passed only in an approximate sense.** For
  Physicists, the medians of p1 and G at B = 3k and 6k differ by less than one
  null-SD. Here the null-SD is approximated as the 95% width / 3.92.
- **Data limits.** Econometrica rests on Simon's printed table only. *Ulysses*
  rests on f(1..3), n and k, censored at 4, so it is not comparable with the
  others' censoring at 11.

**Independent check.** A fresh-context subagent (same model family) audited
`src/stage3.py` against Amendment 2. It was barred from `results/`. It found
no blocking defect:
- the estimators match scipy to 6e-14;
- the §II stream and the §III slice match naive sequential implementations
  within 1–2 SE;
- every seed is distinct: 42,200 of them (36,200 null replicates and 6,000
  self-test replicates), recounted at publication. The audit itself reported
  48,000, a miscount; distinctness holds.
- one null is smaller than the rest: the §III slice for *Ulysses* has 200
  replicates, not 1,000 (contract A2.3, for compute).

Its minor notes are the snapshot length and the n shortfall (both stated
above), plus three cosmetic items in the code.

## Reprint check (2026-11-02): *Models of Man* (1957) changes nothing

The paper is reprinted as chapter 9 of *Models of Man* (Wiley, 1957), reset
in new type. Carnegie Mellon's Herbert Simon Collection scanned Simon's own
copy. The Internet Archive copy is borrow-only and was not used.

All 152 table cells were typed from the reprint images in a separate entry
pass by the same agent, without viewing the Biometrika transcription. They match one for one (`tests/test_reprint.py`).
Details and custody are in `paper/PROVENANCE.md`.

The reprint carries over every Stage 1 slip:
- 0.527 and 0.171 in Table 1;
- Physicists f(1) = 824 and k = 3,396;
- Chem f(10) = 38;
- the low f(2) cells;
- the `Ka^{-(ρ+1)}` typo.

So the Stage 1 labels describe the text in both printings. Simon did not
correct the tables when he reprinted the paper; motive is not inferred.
Ijiri & Simon (1977) is not checked.

## Stage 4 (2026-11-02): the Yule against its rivals on the source tables

Contract: PREREGISTRATION.md Amendment 3, frozen before any Stage 4 code
(SHA-256 and freeze time in `results/prereg-freezes.txt`). Code: `src/stage4.py` (about 12 minutes on 6 workers) and
`src/stage4_table.py`. Outputs:
- `results/stage4-summary.json`
- `results/stage4-verdicts.md` (the full tables)
- `results/stage4-gates.json`
- `results/stage4/` (one JSON per set and model, one row per bootstrap
  replicate)

Tests: `tests/test_stage4.py`.

**Models.** Eight, all on x ≥ 1, fitted by maximum likelihood:
- Yule;
- zeta;
- log-series;
- Sichel's GIGP with ν = −0.5 and α = 0, which is an extended negative
  binomial (ENB) with r = −0.5;
- Simon's own Waring generalization (3.8);
- the Yule with Simon's convergence factor b^i (1.1);
- the ENB/ZTNB with r free;
- the full three-parameter GIGP.

**Data.**
- Full tables for Chicago, Chem, Physicists and Eldridge.
- Econometrica only as Simon printed it: rows 1–10 plus 11+.

**Gates.** Before any data fit, each pmf passed three checks:
- it normalizes to 1 within 10⁻⁶;
- it agrees with an independent mixture sampler, for every family that has
  one;
- the nesting identities hold (Waring c = 0, cutoff b = 1, GIGP α → 0 = ENB).

The zeta fit also reproduces Smolinsky's Chem MLE of 1.9665.

### Headline

1. **Sichel's θ reproduces exactly.** On Chem, the ENB with r = −0.5 has MLE
   θ = 0.968759, which rounds to Sichel's 0.96876. That target is Sichel's value as
   reported by Bogachev, Nuermaimaiti & Voss (2023, §7.1); Sichel's 1985 paper
   itself was not inspected. An exploratory X² (tail
   pooled to expected ≥ 5; 32 cells, 30 df) gives p = 0.88, against his 91.8%
   (also as reported by Bogachev et al.) on a grouping that is not stated.
   "Reproduces exactly" means the MLE rounds to the reported five decimals.
2. **The refitted Yule is rejected at 5% by the preregistered 11-cell test
   for three of the four Table 3 sets**, so the frozen grade of "reasonably
   good" (p. 436) fails there. The test is an iid parametric bootstrap of a
   newly fitted Yule (each sample has n independent type sizes), with X² on
   Simon's own 11 cells. It is not a test of Simon's printed estimates, nor a
   calibrated test of his dependent growth process (Stage 3 asks that), nor
   the only possible reading of his qualitative phrase.

   | Set | Exceedances (of 500) | Yule X² p | Grade | Yule ΔAIC to best | Best model |
   |---|---|---|---|---|---|
   | Chicago | 8 | 0.016 | rejected | 8.6 | ENB |
   | Chem | 0 | 0.000 | rejected | 73.3 | GIGP |
   | Physicists | 32 | 0.064 | not rejected | 7.2 | ENB |
   | Econometrica | 3 | 0.006 | rejected | 0.2 | ENB |
   | Eldridge (not graded) | 3 | 0.006 | — | 8.3 | Waring |

   - **Monte Carlo resolution.** The p column is the frozen exceedance
     fraction. Chem's 0/500 does not show p < 1/500: the exact one-sided
     95% upper bound on the bootstrap probability is 0.006. Physicists'
     32/500 has a 95% simulation interval of 0.044–0.089, which crosses
     0.05. The reviewer's separately labelled supplemental run, an
     independent implementation with 10,000 replicates, gave 711/10,000 =
     0.071 (0.066–0.076) (`AUDIT-2026-11-02.md`, A3). It supports the non-rejection; it
     does not replace the frozen run. Not rejecting the Yule does not show
     that it fits well.
   - **Physicists** is not rejected by X², but is rejected by the
     supplementary KS test (p = 0.028).
   - **Econometrica.** Its Yule is within ΔAIC 0.2 of the best model, yet it
     is rejected by X² like its rivals: on 11 censored cells, every candidate
     is rejected at 0.05.
3. **Authors and words part ways.**
   - **Author counts.** On all four author sets the best-AIC model is a power
     law with an exponential cutoff (on Econometrica only by ΔAIC 0.2, where
     every model is rejected): the ENB with r between −0.30 and −0.49 and
     θ between 0.90 and 0.97, or the GIGP. Each such best model is not
     rejected by X² at 0.05, except Econometrica's. Physicists' ENB has
     KS p = 0.042, close to the threshold at B = 500 (simulation interval
     0.026–0.063). On Chem the GIGP (ν = −0.58, α = 0.21,
     θ = 0.974) has X² p = 0.85 and KS p = 0.65, while the Yule has 0.000
     on both.
   - **Prior work on Chem.** For the chemistry table this is not new.
     Smolinsky (2015, arXiv:1512.08754) compared a discrete power law with and
     without an exponential cutoff on Lotka's chemistry data, and Sichel
     (1985, as reported by Bogachev et al.) fitted the GIGP to it. What this stage adds is the same comparison
     on Chicago, Physicists, Econometrica and Eldridge, with the Yule family
     and Simon's own Waring among the rivals.
   - **Eldridge's words.** The cutoff models collapse here (ENB ΔAIC 388.5).
     The best model is Simon's own Waring (3.8), with ρ = 1.14 and c = 0.15
     (X² p = 0.21, KS p = 0.45). It is the only model that neither test
     rejects there.
4. **The Yule still beats the zeta everywhere.** The Vuong z ranges from
   +2.05 (Econometrica) to +7.51 (Eldridge). It also beats the log-series
   everywhere except Chicago, where the two are indistinguishable.

### Predictions (Amendment 3)

| | Prediction | Outcome |
|---|---|---|
| P7a | on Chem the ENB loses to the Yule on AIC | **failed**: the ENB wins by ΔAIC 66.6 (r = −0.49, θ = 0.968) |
| P12 | the Yule beats the zeta on Vuong for Chem and Physicists | held (z = +2.94, +4.16); a lead |
| P13 | "reasonably good" fails on Chem | held (0/500 exceedances; upper bound on p ≈ 0.006) |
| P14 | Sichel's θ reproduced or consistent | held (reproduced, against Sichel's value as reported by Bogachev et al.) |
| P15 | the best model on Chem has ≥ 2 parameters | held (GIGP, 3) |

**Why P7a failed.** It came from arithmetic done before the freeze (a lead
recorded in Amendment 3):
- that arithmetic assumed θ ≈ 1;
- on that assumption the head implies r ≈ −0.47 while a power tail needs
  r ≈ −0.97;
- the fitted θ = 0.968 makes the tail geometric instead.

So one r fits the head, and the cutoff takes the tail. The ENB's r̂ = −0.49
is the head value. Sichel's choice of r = −0.5 (ν = −0.5 with α = 0, as
reported by Bogachev et al.) sits within 0.01 of the free fit. The arithmetic itself was right; the θ = 1 power-tail
approximation was inappropriate at the fitted θ. A θ numerically close to 1
does not justify dropping θ^i at large i.

### Caveats

- **Many tests.** There are forty bootstrap p-values (8 models × 5 sets) and
  35 rival comparisons (7 rivals × 5 sets), none corrected for multiplicity. Read them as
  descriptions. The headline grades use one test per set, fixed in advance.
- **The Vuong test is uncorrected** for parameter count, as frozen. ΔAIC is
  reported beside it in `results/stage4-verdicts.md`.
- **Two GIGP fits sit at the α lower bound.** On Chicago and Econometrica the
  GIGP collapses onto the ENB (same log-likelihood) and is flagged.
- **Econometrica is censored at 11.** Tail models are barely separable there:
  six of the eight models lie within ΔAIC 2.0.
- **The A3.6 "either estimator" clause gave no second chance.** With r
  fixed, the ENB is a power-series family, so its MLE and the mean-matching
  estimate coincide: 0.9687590 against 0.9687590.

**Independent check.** A fresh-context subagent (same model family) audited
`src/stage4.py` against Amendment 3 while the run was in progress. It was
barred from `results/`.

- **What it re-checked:**
  - every log-pmf against mpmath, to within 1.3e-11 (GIGP against eq. 3.1
    with besselk, to within 2.7e-10);
  - all 40 fits, by differential evolution and dense grids, finding no better
    optimum;
  - Vuong, LR and the bootstrap p-values;
  - the Sichel mean formula.
- **Its one material finding: a memory risk.** It replayed the run's seeds
  and found zeta bootstrap samples with maxima up to 2.8 × 10⁸. At those
  sizes the original KS code would need about 13 GB in one worker.
  - The KS now evaluates the model CDF only at the support points,
    accumulated in chunks. This is the same statistic: 0.0 difference on the
    data and on test samples.
  - The whole run was repeated with the fixed code. The summary is identical
    to the first run apart from the timing field.
- **Latent risk, not hit.** It also flagged precision loss in the GIGP's
  log(1 − f₀) for ν ≤ −1 at α near 10⁻⁶. No fit goes there: the fitted ν
  values are −0.30 to −0.93, with errors ≤ 10⁻¹⁴.

## Stage 5 (2026-11-02): the word-count sentences on full distributions

Contract: PREREGISTRATION.md Amendment 4, frozen before any Stage 5 code
(SHA-256 and freeze time in `results/prereg-freezes.txt`). Code: `src/stage5.py` (runs in seconds). Outputs:
- `results/stage5-summary.json`
- `results/stage5-counts.csv`
- `results/stage5/freq_T*.csv` (the recount frequency tables)

Tests: `tests/test_stage5.py`.

**Counts.**
- Eldridge's List 5.
- Hanley's *Ulysses* figures, as quoted by Zipf: f(1..3), n and k only,
  censored at 4.
- Three recounts of Project Gutenberg #4300 (the edition updated
  2025-11-27):
  - T1: letter runs only;
  - T2: letter runs joined by internal apostrophes and hyphens;
  - T3: internal apostrophes only.

**The recounts are not a replication of Hanley.** He indexed his own text
under his own rules for what counts as a word. The three tokenizers show how
far those rules alone move the numbers.

### C1, C2 and the Table 2 rebuild

| Count | n | k | f(1) | f(2) | f(3) | α = n/k | ρ_MoM | recipe f(1..3) |
|---|---|---|---|---|---|---|---|---|
| Eldridge | 6,002 | 43,989 | 2,976 | 1,079 | 516 | 0.136 | 1.158 | 3,221 / 1,020 / 491 |
| Hanley (via Zipf) | 29,899 | 260,430 | 16,432 | 4,776 | 2,194 | 0.115 | 1.130 | 15,860 / 5,068 / 2,454 |
| T1 letters | 29,021 | 268,727 | 15,691 | 4,674 | 2,163 | 0.108 | 1.121 | 15,339 / 4,915 / 2,385 |
| T2 internal ' and - | 29,776 | 264,276 | 16,231 | 4,804 | 2,189 | 0.113 | 1.127 | 15,777 / 5,045 / 2,445 |
| T3 internal ' | 29,737 | 264,481 | 16,194 | 4,794 | 2,189 | 0.112 | 1.127 | 15,754 / 5,039 / 2,442 |

- **C1 holds for Eldridge.** List 5 gives Table 2's actuals exactly.
- **The recounts bracket Hanley without matching him.**
  - Every tokenizer finds fewer types than Hanley's 29,899 (0.4–2.9% fewer)
    and more tokens than his 260,430 (1.5–3.2% more).
  - f(2) and f(3) land within 2.2% and 1.5% of his.
- **C2 holds everywhere.** ρ_MoM lies between 1.12 and 1.16, inside "1.1 to
  1.2", for all five counts.
- **The recipe misfit is a property of the recipe, not of Hanley's count.**
  The recipe rebuild repeats Stage 1: under Simon's own recipe, Table 2's
  estimate columns are 15,860 / 5,068 / 2,454 and 3,221 / 1,020 / 491. The
  recounts show the same pattern: the recipe overshoots f(2) by 5–6% and f(3)
  by 10–12%.

### C3: "ρ, in both cases, of about one" (band 0.85–1.15)

| Count | E1 power-law MLE | E2 OLS, unbinned | E3 OLS, log₂ bins |
|---|---|---|---|
| Eldridge | 0.83 ✗ | −0.03 ✗ | 1.01 ✓ |
| T1 | 0.86 ✓ | −0.04 ✗ | 1.00 ✓ |
| T2 | 0.87 ✓ | −0.03 ✗ | 1.01 ✓ |
| T3 | 0.87 ✓ | −0.03 ✗ | 1.01 ✓ |

Simon's sentence holds on the binned log-log slope (E3), to two decimals in
every count. It fails for Eldridge under the likelihood estimate (E1) and
holds only narrowly for the recounts. The unbinned slope (E2) is meaningless
here. The high-frequency end has many occupied classes with f(i) = 1, each
a separate regression point. That plateau flattens the fit to a slope near
−1, which gives ρ ≈ 0.

So "about one" depends on the estimator, and the estimator that confirms it
is the graphical, binned kind available in 1955. This is reported, not
explained. Simon does not say how he fitted.

### C4: (4.2) with c ≈ 0.2 (*Ulysses*) and c ≈ 0 (Eldridge)

(4.2) identifies only the product x = cβ. Everything below is about x, the
frozen contract's product-based proxy for Simon's c. It is not about c
itself.

| Count | x̂ = cβ (MLE) | X² p (bootstrap, B = 500) | x̂ in band ("about 0.2" / "close to zero") | rejected by X²? |
|---|---|---|---|---|
| Eldridge | 0.021 | 0.000 (0/500; 11 cells) | close to zero ✓ | rejected |
| Hanley (censored at 4) | 0.178 | 0.154 (4 cells) | ✓ | not rejected |
| T1 | 0.145 | 0.198 (11 cells) | ✓ | not rejected |
| T2 | 0.162 | 0.204 | ✓ | not rejected |
| T3 | 0.160 | 0.230 | ✓ | not rejected |

- ***Ulysses*.** Under every tokenizer, the 11-cell X² does not reject
  (4.2) at n ≈ 30,000, with x̂ between 0.145 and 0.162 (0.178 on Hanley's
  figures). These products are
  compatible with Simon's c ≈ 0.2 for β near 0.7–0.9. They do not identify
  c.
- **Eldridge.**
  - x̂ = 0.02, inside the frozen "close to zero" band for the product.
  - x̂(*Ulysses*) > x̂(Eldridge) in every count. That is an ordering of the
    products. It does not show the ordering of c that Simon predicts on
    p. 435. A small x̂ can come from a small β with any c in (0, 1), and the
    same two fits are equally compatible with the opposite ordering of c
    (`AUDIT-2026-11-02.md`, A1).
  - (4.2) is rejected for Eldridge (X² = 30.6 on 11 cells; 0/500 bootstrap
    replicates as large). This matches Stage 4, where only the
    two-parameter Waring escapes rejection on Eldridge.
- **What x can and cannot say.** x = cβ ≤ c, so x̂ ≈ 0.16 says c is at least
  0.16. It does not say c ≈ 0.2 unless β ≈ 1.
- **The unconstrained fits are interior.** They equal the constrained ones in
  all five counts.

### Other comparisons

- **Yule MLE against Leisen et al. (ρ = 1.09, CrI 1.08–1.11, on a Gutenberg
  text, n = 29,841).**
  - T2 gives 1.092 (CI 1.077–1.108) and T3 gives 1.091 (1.075–1.107). Both
    sit on their estimate.
  - T1 gives 1.078 (1.062–1.094), which overlaps their CrI.
  - Hanley's censored figures give 1.158 (1.138–1.179), which does not
    overlap. Censoring at 4 uses only the head, where Hanley's f(1)/n is
    high.
- **Property (c).**
  - f(1)/n is 0.50 for Eldridge, against 0.54–0.55 for the *Ulysses* counts.
  - f(2)/f(1) is 0.36 for Eldridge, against 0.29–0.30 for *Ulysses*.

  Both stay near one-half and one-third.

### Predictions (Amendment 4)

| | Prediction | Outcome |
|---|---|---|
| P16 | C1 holds for Eldridge | held (a lead) |
| P17 | every tokenizer's n is below Hanley's 29,899 | held (29,021 / 29,776 / 29,737) |
| P18 | "c about 0.2" holds for all three tokenizers (graded on the product x = cβ) | held (x̂ 0.145–0.162) |
| P19 | "c close to zero" for Eldridge, and the ordering (both graded on x) | held (x̂ = 0.021; the products are ordered, c is not identified) |
| P20 | (4.2) is not a good fit for Eldridge or any tokenizer | **failed**: Eldridge is rejected; none of the three recounts is rejected by the pooled 11-cell test (p 0.20–0.23) |
| P21 | C3 under E1 fails for Eldridge | held (0.83; a lead) |

**Why P20 failed.** It assumed a model with the tail fixed at ρ = 1 would be
rejected at n ≈ 30,000. But the X² pools everything from 11 up into one cell,
so it tests the head and the tail mass, not the tail's slope. Within that
reach, the test does not reject (4.2). That does not show that (4.2) is
adequate in the tail.

### Caveats

- **The fit tests check the head.** All X² verdicts use Simon's cells 1–10
  plus 11+. A test of the tail shape would need finer cells or a KS-type
  statistic, which Amendment 4 did not freeze.
- **The text is one edition.** The tokenizer band is narrow (n spans 2.6%),
  but the Gutenberg file's provenance is not established. Hanley's index
  remains borrow-only.
- **The C3 band is the contract's choice.** "About one" was frozen as
  [0.85, 1.15].
  E1's recount values (0.86–0.87) sit just inside it.

**Independent check.** A fresh-context subagent (same model family) audited
`src/stage5.py` against Amendment 4. It was barred from `results/`. It found
no blocking defect.

- **What it re-checked:**
  - an independent tokenizer, written without regex, reproduces T1, T2 and
    T3 exactly (the same k, n and frequency spectra);
  - exactly the 19 marker lines are dropped;
  - the (4.2) sampler's survival matches within 4e-4 for x from −5 to
    0.999;
  - X², E1–E3, the recipe and the Yule MLE match its re-implementations;
  - each likelihood has a single maximum.
- **Its minor finding: the `[Illustration]` placeholders.** Three Gutenberg
  `[Illustration]` placeholders stay in the body, as the contract wording
  allows. The effect is one type moved from f(1) to f(4) and 3 extra tokens.
- **Cosmetic notes:**
  - the letter class accepts non-decimal numerals (none occur in the text);
  - a 2⁻⁵³ edge case in the sampler at x < −3 (never sampled);
  - "distance from Hanley" is reported in prose here, not in the CSV.

## Stage 6 (2026-11-02): the figures

Code: `src/stage6.py`. Outputs:
- `results/stage6-table3.png` and `.svg`
- `results/stage6-table2.png` and `.svg`
- `results/stage6-series.csv`, every plotted value: the table view of the
  figures, 198 points

Test: `tests/test_stage6.py`.

**Sources.** The figures read committed files only:
- the observed and printed cells: `data/printed_tables.csv`;
- the recipe values: `results/stage1-cells.csv`;
- the censored Yule MLE: `results/stage3-summary.json`.

Reruns are byte-identical; the SVG IDs are salted. The test draws both
figures and checks every plotted printed and observed point against the
transcription: 99 cells, the 8–10 brackets excluded.

**Layout.**
- **Panels.** One per data set.
  - The top row shows counts on a log axis.
  - The bottom row shows each estimate divided by the observed count, so
    "too high" sits above the line at 1.
- **Series.** Observed counts are black dots. The three estimate series are
  blue (printed), orange (recipe) and aqua (MLE), each with its own marker
  shape. The palette passes the colorblind and contrast checks for three
  series, with aqua relieved by the marker shapes and the CSV.
- **The 11+ cell** is pooled, so it sits apart after a dotted separator, and
  no line joins it to row 10.

**What the Table 3 figure shows.**
- **Chicago.** The printed and recipe series lie on top of each other, the
  one column that reproduces exactly.
- **Chem.** The printed and recipe series fall below observed from row 6
  on, while the Yule MLE stays closer. Chem's 11+ cell does not change sign:
  both the printed estimate (0.80 of observed) and the recipe (0.66) are
  below it. It is the clearest case of the residual-tail shortfall. The
  sign changes behind the Stage 1 reversal are in Physicists and
  Econometrica.
- **Physicists and Econometrica.** The printed f(2) sits below the recipe's.

**Two things to know when reading it:**
- Chicago's "recipe" series is Simon's own ρ̄ chain (no f(1)), as printed
  for that column. The figure's legend says "stated recipe", and a footnote
  in each figure states this exception and the MLE censor points.
- Econometrica's observed f(10) = 0 is in the data and the CSV. It cannot
  appear on a log axis, so its ratio point is absent.

## Corrections after external review (2026-11-02)

A reviewer from a different model family (Codex) audited the project. The
audit is saved as `AUDIT-2026-11-02.md` in this folder; it is not a publication
approval. It confirmed:
- the tail reversal;
- the unchanged reprint cells;
- Stage 4's three-of-four result under its stated test;
- both failed-prediction grades;
- all 198 figure values and the byte-identical rebuilds.

Each correction below was checked against the code, the data or the page
before it was applied. No frozen grade, prediction outcome or contract text
changed.

- **A1, c against cβ (Stage 5 and the README).** Claims about c, its
  ordering and "c ≈ 0" now speak of the identified product x = cβ.
- **A2, "not rejected" is not "adequate" (Stage 4 code, verdicts, Stages 4
  and 5 prose).**
  - The likelihood-ratio label "Yule adequate" is now "no significant
    improvement over Yule". Stage 4 was rerun; the summary is identical
    apart from that label and the timing field.
  - Grade wording now says rejected or not rejected, and the headline names
    the test's scope.
- **A3, Monte Carlo resolution (Stages 4 and 5).** 0/500 is reported as
  exceedances, with its upper bound (about 0.006). Physicists' 32/500 gets
  its simulation interval and the reviewer's labelled supplemental run.
- **A4, figure labels (Stage 6 code and figures).** The legend says "stated
  recipe". Each figure carries a footnote:
  - Table 3: Chicago's ρ̄ exception and Econometrica's f(10) = 0;
  - Table 2: the MLE censor points.
- **Editorial fixes:**
  - the "reasonably good" locator is p. 436, not p. 437; a contract erratum
    is appended to `PREREGISTRATION.md`;
  - the report introduction is now Stage-1-specific;
  - the E2 explanation now names the f(i) = 1 plateau at the high-frequency
    end;
  - Chem's 11+ cell is no longer called a reversal;
  - P7a's explanation is reworded as the reviewer suggested.

## Pre-publication reader review (2026-11-02)

The published package went through the pre-publication reader gate in
`INVESTIGATION_CHECKLIST.md`.

**Layer A, the deterministic release checks, passes** (`tests/test_reader_site.py`
and a browser check):
- The Overview is the default tab.
- No private paths or work-order wording appear in public prose.
- In-page anchors resolve and IDs are unique. External links resolve; the two
  DOIs redirect to the publishers.
- The tabs work from the keyboard. At 375 px no tab overflows, and the
  browser console is clean.
- The page and figures rebuild byte-for-byte.
- The headline numbers are pinned (`src/verify_report_numbers.py`, 27
  claims).
- Every frozen version of the contract rebuilds to its recorded hash
  (`src/verify_prereg_freezes.py`).

**Layer B, the fresh-context reader review.** A fresh-context Claude reader
(same model family, no part in the writing) read the site as a visitor would.
It spot-checked four headline claims against the page images and results,
and all four passed. It found no numerical error. Its findings, all applied:

- **Count.** The Stage 3 grid has six process settings per set, not
  "eleven". The wrong count was corrected here, in the README and on the
  Overview.
- **Proportion.** The Overview led with the Stage 3 simulation result, which
  the cross-family audit did not check. It now leads with the deterministic
  Stage 1 result.
- **Qualifiers next to claims.**
  - The Stage 3 claims now say "did not produce the gap in 1,000 runs" and
    "consistent with, at a single grid point". Econometrica is also matched
    by §III, so "the only mechanism" was withdrawn.
  - Sichel's θ is labelled as reported by Bogachev et al. wherever it
    appears.
  - "Fits" became "not rejected" for the Waring on Eldridge.
  - The cutoff-power-law claim is limited to the three author tables where
    it holds.
- **Scope of "independent".**
  - The Overview now says which stages the cross-family audit re-derived.
  - "Typed independently" now says what it was: a separate entry pass by the
    same agent, without viewing the first.
- **Precision.** The 59.2-person shortfall equals the tail gap by
  construction, and now says so.
- **Locators.** The head sentence's Chicago check is at i = 2 only.
- **Freeze proofs.** The pre-registration hashes had been recorded only in a
  private log.
  - They are now checkable by anyone: `src/verify_prereg_freezes.py` rebuilds
    all eight frozen versions from the current file and matches every
    recorded hash.
  - The freeze times are still attested only by the implementing session's
    log, and say so (`results/prereg-freezes.txt`).
- **Counts.** The audit preface's edit count and Erratum 2's path count
  were corrected (Erratum 3).

A second fresh-context reader then rechecked the failed items. Its findings
were applied too:
- the verdict sentence and the Overview now say what fails, which is whole
  columns, not most cells: of 77 estimate cells, 62 are exact or reproduce
  under a stated convention, 4 are rounding slips, and 11 reproduce under
  none;
- "ρ about one" by likelihood is reported per count;
- the Chicago grid match is two adjacent points;
- the Chem shape statement and the Stage 3 seed count were corrected;
- each audit is described by what it covered.

A third fresh-context check covered only the two items that had failed
(voice and consistency). It found one count error, corrected here: 35 rival
comparisons, not 32. It also found three smaller inconsistencies, all
corrected: the tokenizer range, one implied-ρ rounding, and one Sichel label.
The README's note on working files not in this repository was kept as
written.


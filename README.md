# Simon (1955) "On a Class of Skew Distribution Functions" — the printed Yule fits, recomputed

An executable verification of the empirical half of Herbert Simon's 1955
*Biometrika* paper: his Yule fits to word counts (Table 2) and to counts of
authors by number of papers (Table 3), his verbal reading of where they fail,
and the mechanisms he offered for them.

**Verdict, one sentence:** *No convention Simon states reproduces any whole
column of his estimates except Chicago's (11 of 77 printed estimate cells
reproduce under none), and under his stated recipe his "too high in the tails
in three of four cases" becomes one of four; the 1957 reprint changes
no cell; on the source tables the refitted one-parameter Yule is rejected by a
pre-registered test (an iid parametric bootstrap of the refitted model) for
three of his four author tables, power laws with an
exponential cutoff fit three of them better, and his own two-parameter
generalization is the one model not rejected on Eldridge's word count.*

**Project status:** complete. Publication followed a cross-family audit and a
pre-publication reader review; every correction is listed at the end of
[`REPORT.md`](REPORT.md).

Simon's recipe is α = n_k/k, f(1) = n_k/(2−α), then f(i)/f(i−1) = (i−1)/(i+ρ),
with ρ = 1/(1−α). That α is the method-of-moments estimate of the Yule ρ, so
it can be set against the likelihood. The project asks four questions:
- Do his printed cells follow from that recipe?
- Do his verbal readings of the misfit survive it?
- How far is moments from likelihood, and which of his own mechanisms could
  produce the gap?
- Does the Yule beat its rivals on the untruncated source tables?

Everything was estimated under a pre-registration whose amendments were each
frozen before the code of their stage ([`PREREGISTRATION.md`](PREREGISTRATION.md)).
Anyone can check that every frozen version is unchanged
(`src/verify_prereg_freezes.py`); the freeze times themselves are attested only
by the implementing session's own log.

**Site:** a short overview, the full report, the prediction scoreboard, the
figures and the custody record are at
https://kenrinzero.github.io/simon-yule-fits/. It is a self-contained
`docs/index.html` (no network, no external assets) built by
`src/build_reader.py`. The Overview tab is the reader-facing entry point. The
Full report tab is rendered verbatim from `REPORT.md`, so the page cannot drift
from the text that `src/verify_report_numbers.py` pins.

## Headline findings

1. **The tail sentence reverses under Simon's own recipe.**
   - As printed, the "11 or more" estimates exceed the observed counts in 3 of
     4 columns, as his text says.
   - Recomputed from his stated recipe, they exceed them in 1 of 4 (Chicago
     only).
   - Every printed 11+ cell is n_k minus the printed rows 1–10, and the
     printed f(2) cells run low, so (by construction) the rows 1–10
     shortfall lands in the tail: 59.2 persons for Chem, the gap between the
     printed 11+ (335) and the recipe's (275.8).
2. **Only Chicago's column reproduces.**
   - No stated convention reproduces any whole column of Chem, Physicists,
     Econometrica or Table 2.
   - Chicago's column reproduces in full under Simon's ρ̄ chain.
   - The 1957 reprint in *Models of Man* prints all 152 table cells
     unchanged, slips included.
   - These are reproducibility findings about a 1955 hand computation; no
     motive is inferred.
3. **Moments against likelihood.**
   - The likelihood estimate of ρ sits below Simon's moment estimate in five
     of six data sets (for example Chicago −0.370, Chem −0.185).
   - Simulated at the real sample sizes, his constant-rate process (§II)
     did not produce the gap in 1,000 runs for any set.
   - The declining rate proposed by Simon & Van Wormer (1963) is consistent
     with the gap and the head shape for three of the four author sets, at
     one or two adjacent points of a fixed grid; Econometrica is also matched
     by the §III slice. Each match means three statistics fall inside their
     own 95% intervals, not a joint test, and this stage had a same-family
     code audit only.
   - Chem, the largest, is matched by none of the six process settings tried.
4. **"Reasonably good" fails for three of four author tables.**
   - The test: the refitted Yule against the pre-registered 11-cell
     parametric-bootstrap X². It is an iid bootstrap of a newly fitted Yule,
     not a test of Simon's printed estimates or of his growth process.
   - It is rejected for Chicago, Chem and Econometrica.
   - For Physicists it is not rejected (p = 0.064, simulation interval
     0.044–0.089), but the supplementary KS test rejects it.
   - Sichel's 1985 GIGP parameter for Chem, as reported by Bogachev et al.
     (2023), reproduces exactly (θ = 0.968759).
   - Power laws with an exponential cutoff (the extended negative binomial
     and the GIGP) give the best fits for Chicago, Chem and Physicists. On
     Econometrica's 11-cell table the models are barely separable and every
     one is rejected.
     For Chem that agrees with earlier work (Sichel 1985, as reported by
     Bogachev et al. 2023; Smolinsky 2015);
     the comparison on the other author tables is new here.
5. **Words part ways with authors.**
   - On Eldridge's count, Simon's own two-parameter Waring generalization is
     the only model not rejected.
   - On three Project Gutenberg recounts of *Ulysses* (not a replication of
     Hanley's 1937 index), Simon's equation (4.2) is not rejected.
     - Only the product cβ is identified: 0.145–0.162.
     - That is compatible with his c ≈ 0.2 for suitable β.
     - "ρ about one" holds on a binned log-log slope for every count; by
       likelihood it holds only narrowly for the recounts (0.86–0.87) and
       not for Eldridge (0.83).
6. **Three of 23 pre-registered predictions failed and are reported as
   failed:**
   - P8, the ρ′ = 1.07 search (one candidate matched, at about chance rate);
   - P7a, which expected the ENB to lose to the Yule on Chem;
   - P20, which expected (4.2) to be rejected on the recounts.

## The evidence chain

| File | Role |
|---|---|
| [`PREREGISTRATION.md`](PREREGISTRATION.md) | The frozen contract: derivations D1–D9, the Stage 1 convention grid and grading rules, then dated Amendments 1–4 (one per stage, each frozen before that stage's code) and three errata |
| [`src/verify_prereg_freezes.py`](src/verify_prereg_freezes.py) · [`results/prereg-freezes.txt`](results/prereg-freezes.txt) | Rebuilds every frozen version of the contract from the current file and checks it against the SHA-256 recorded at freezing: all match, so nothing above an amendment was edited afterwards. The freeze times come from the implementing session's private log and cannot be verified from outside; the public git history begins at publication. |
| [`CLAIM_INVENTORY.md`](CLAIM_INVENTORY.md) | Simon's nine checkable claims, with locators, checkability and tier |
| [`REPORT.md`](REPORT.md) | Findings by stage, the prediction tables, caveats, the fresh-context and cross-family checks (each named by what it covered), and the corrections after review |
| [`AUDIT-2026-11-02.md`](AUDIT-2026-11-02.md) · [`results/audit-2026-11-02/`](results/audit-2026-11-02/) | The cross-family audit (Codex) and its independent check script and evidence |
| [`CREDITS.md`](CREDITS.md) | Who did what, the independence structure, and what each agent got wrong |
| [`data/printed_tables.csv`](data/printed_tables.csv) | Every printed cell of Tables 1–3, page-located |
| [`data/reprint_1957_models_of_man.csv`](data/reprint_1957_models_of_man.csv) | The same 152 cells as reprinted in 1957, entered in a separate pass without viewing the first |
| [`data/sources/`](data/sources/) · [`ADJUDICATION.md`](data/sources/ADJUDICATION.md) | Davis (1941), Lotka (1926), Eldridge (1911) and Zipf (1949) tables, double-entered, with every disagreement settled from the page image |
| [`data/raw/MANIFEST.csv`](data/raw/MANIFEST.csv) | Every downloaded file: URL, retrieval date, bytes, SHA-256 |
| [`paper/PROVENANCE.md`](paper/PROVENANCE.md) | The paper scan's identity, transcription notes, and the reprint check |
| `results/` | Stage outputs, verdict tables, bootstrap replicates, figures, and `deliver-number-checks.txt` |

## Reproduce

```bash
python src/step0_checks.py
python src/recipe.py
python src/implied_rho.py
python src/stage2.py
python src/stage3.py --workers 6   # about 1.5 minutes
python src/stage3_table.py
python src/stage4.py --workers 6   # about 12 minutes
python src/stage4_table.py
python src/stage5.py               # seconds
python src/stage6.py               # figures
python src/verify_report_numbers.py
python src/build_reader.py
python -m pytest -q tests
```

Run with Python 3.13.13, NumPy 2.5.4, SciPy 1.18.1, mpmath 1.3.0 and
Matplotlib 3.11.2. The seeds are fixed (Stage 3: 19551201; Stage 4: 19551102;
Stage 5: 19551103). The figures and the reader page carry no timestamp and
rebuild byte-for-byte.

## Source material

The paper (a JSTOR scan of a copyrighted *Biometrika* article), its page
renders, the 1957 reprint, and the scans and OCR layers of Davis, Lotka,
Eldridge and Zipf are not redistributed. What the analysis rests on is shipped
instead:
- the transcriptions, each cell with its page locator;
- the double-entry adjudication;
- the SHA-256 of every source file, so a reader who obtains the same file can
  confirm it is byte-identical.

Project Gutenberg eBook #4300 (*Ulysses*) is public domain in the United
States. It is shipped unchanged, with its own header and licence, because the
Stage 5 recounts are built from it.

## Working files not in this repository

`AGENTS.md` is excluded: it is the stub that orients an AI agent inside the
owner's private project tracker. Where the pre-registration refers to the
project's planning note, that note is private too. Its source URLs, traps and
prior-work list are carried into the pre-registration, the adjudication record
and this repository's citations.

## Licence

- Code: MIT ([`LICENSE`](LICENSE)).
- Analysis documents: CC-BY-4.0 ([`REPORT-LICENSE`](REPORT-LICENSE)).
- Source material remains under its own terms.

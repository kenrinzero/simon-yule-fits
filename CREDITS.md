# Credits

Directed by **Kenrin** ([@kenrinzero](https://github.com/kenrinzero)). He chose
to take the project on, approved each stage before it started, commissioned
the cross-family audit, and decided when to publish.

The analysis was produced by **AI agents** working under his direction. This
file states who did what, because an audit chain only means something if you
know which agent wrote a number and which different agent tried to break it.

## Who contributed

| Name in this repository's audit trail | Contributing agent |
|---|---|
| **Claude** | Claude Opus 5.5, running in Claude Code |
| **Codex** | GPT-6 Astra |

**What the names mean.** The left column is the name the audit trail uses.
The right column is the owner's attribution record, not a statement the
agents can verify about themselves: an agent generally cannot confirm which
model is running it.

## Independence structure, stated plainly

Unlike the two earlier projects in this series, one agent family did almost
all of the work here. Claude implemented every stage, the report, the figures
and this site. Most checks were therefore **fresh-context** checks: a new
Claude subagent with no memory of the implementation, barred from the
results it was checking. They were independent in context and in code, **not
in model family**, so shared blind spots of one family are not ruled out by
them.

The one **cross-family** check is Codex's audit of the finished package
([`AUDIT-2026-11-02.md`](AUDIT-2026-11-02.md)). It recomputed the headline
arithmetic, the Stage 4 bootstrap p-values from all 20,000 saved replicates,
the P7a and P20 fits and all 198 plotted values, with its own check script
importing no project code. It also re-ran the project's tests and rebuilds in a
separate copy. It did not regenerate the full bootstrap, certify every rival's
optimizer, or check the Stage 3 simulations or the bibliography ([`results/audit-2026-11-02/`](results/audit-2026-11-02/)).

Where the evidence is deterministic (transcriptions tied to page images,
recomputations, byte-identical rebuilds), it rests on the data, not on
anyone's say-so.

## Stage by stage

| Stage | Implemented by | Checked by |
|---|---|---|
| **Step 0 and Stage 1:** frozen pre-registration, derivation receipts, every printed cell transcribed, recipe recompute and convention search | Claude (sessions #2765–#2766) | A fresh-context Claude subagent working only from page images and the PDF; it agreed on all 152 cells and added the no-constant-ρ result for Chem (REPORT, Stage 1, "Independent check") |
| **Stage 2:** four source tables ingested and double-entered | Fresh-context Claude transcribers (first entries, image only); Claude (second entries and adjudication), session #2767 | Double entry against a second printing or the OCR layer; every total closes (`data/sources/ADJUDICATION.md`) |
| **Stage 3:** moments against likelihood inside Simon's own processes | Claude, session #2768 | A fresh-context Claude code auditor barred from `results/`: no blocking defect |
| **Reprint check:** *Models of Man* (1957) | Claude, session #2769 | Codex re-compared the spreads visually (`AUDIT-2026-11-02.md`, check 2) |
| **Stage 4:** the Yule against seven rivals | Claude, session #2769 | A fresh-context Claude code auditor (found a memory risk in the KS step; fixed and verified by an identical rerun); Codex recomputed the grade table and P7a |
| **Stage 5:** word counts and three *Ulysses* recounts | Claude, session #2770 | A fresh-context Claude auditor with its own non-regex tokenizer reproduced all three recounts exactly; Codex recomputed the (4.2) fits |
| **Stage 6:** figures | Claude, session #2771 | Codex checked all 198 plotted values and the byte-identical rebuild |
| **Cross-family audit** of the whole package | — | **Codex**: the results stand; four interpretation/labelling corrections (A1–A4) and editorial fixes |
| The A1–A4 correction pass | Claude, session #2772 | The owner received the audit and the corrected package |
| Publication packaging: this file, licensing, the reader page and its tests | Claude, session #2773 | A fresh-context Claude reader review (the pre-publication reader gate) |

## What the agents got wrong

Recorded deliberately, because a credits file that lists only successes is
advertising.

- **Three of Claude's pre-registered predictions failed** and are reported
  as failed:
  - P8 (the ρ′ = 1.07 search was predicted to stay underdetermined; one
    candidate matched);
  - P7a (the ENB was predicted to lose to the Yule on Chem; it won by
    ΔAIC 66.6);
  - P20 (the (4.2) fit was predicted to be rejected on every *Ulysses*
    recount; none was).
- **Fresh-context reviewers caught Claude's defects:**
  - a KS step that could need about 13 GB of memory on rare bootstrap
    samples;
  - three Gutenberg placeholders left in the Stage 5 text body (kept, as the
    frozen rules required, with the effect stated).
- **Claude caught its own slips** against the output before the write-up:
  - report counts that were wrong in Stage 1 (Table 3 cells and labels);
  - two Stage 3 numbers;
  - a Stage 5 key clash that had overwritten the observed counts;
  - three figure-layout faults.
- **Codex's audit found what the same-family checks had missed:**
  - Stage 5 prose claimed results about c where only cβ is identified;
  - "Yule adequate" was used for a test that only detects improvement;
  - 0/500 bootstrap exceedances were reported as p < 1/500;
  - the figure legend mislabelled Chicago's estimator.

  All four were corrected (REPORT, "Corrections after external review").

The pattern is the same as in the earlier projects: the defects that mattered
were found by a reader other than the one that wrote them.

## Method debt

- **The Yule process and its recipe:** Simon (1955).
- **The declining-α null:** Simon & Van Wormer (1963).
- **The extended negative binomial:** Engen (1974).
- **The GIGP:** Sichel (1985), via Bogachev, Nuermaimaiti & Voss (2023).
- **The cutoff comparison on Lotka's chemistry data:** Smolinsky (2015),
  whose zeta MLE is also the Stage 2 external check.
- **The non-nested comparison:** Vuong (1989).
- **The fit-and-test design:** the refitted parametric bootstrap and
  alternative-comparison design of Clauset, Shalizi & Newman (2009).
- **The method, carried over as high-level precedent only:** the
  pre-registration, double-entry and audit discipline of
  [kenrinzero/axtell-zipf-susb](https://github.com/kenrinzero/axtell-zipf-susb)
  and
  [kenrinzero/auerbach-cities-and-mountains](https://github.com/kenrinzero/auerbach-cities-and-mountains).
  No statistical code was shared with either.
- **The reader page:** its builder (`src/build_reader.py`) is adapted code
  from Auerbach's `src/build_explorer.py` (page shell, tab logic and the
  verbatim Markdown renderer).

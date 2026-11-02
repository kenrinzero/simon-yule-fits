# Investigation checklist — standing lens for every paper

Adopted 2026-07-24 (ARIS doctrine item 8 —
`.atelier/suggestions/archive/2026-07-21-aris-doctrine-adoption.md`; ARIS's
self-audit taxonomies inverted into an audit lens for *published* papers;
credit wanshuiyin/Auto-claude-code-research-in-sleep, MIT). Each new paper
folder's `AGENTS.md` references this file. Walk it during step 1 (claim
inventory) and again before any defensible-claim writeup.

## Failure-mode lenses (from `paper-claim-audit`, inverted)

- [ ] **Number inflation** — headline numbers larger than what the tables and
      figures support; check abstract/intro claims against the actual result
      tables.
- [ ] **Best-seed cherry-pick** — single-run or best-of-N results presented as
      typical; look for missing variance, missing seed counts, suspiciously
      clean curves.
- [ ] **Config mismatch** — the described setup (architecture, hyperparams,
      data splits) doesn't match what the results require or what appendix /
      code fragments reveal.
- [ ] **Aggregation mismatch** — means, medians, and maxes mixed or swapped
      between text and tables; per-task vs averaged numbers conflated.
- [ ] **Delta arithmetic error** — claimed improvements that don't equal the
      difference of the two numbers cited; recompute every delta.
- [ ] **Caption–table mismatch** — captions or prose claiming what the panel
      doesn't show (the steerable-lens case: prose says "moves smoothly in the
      intended direction," pixels show deform-and-flip).
- [ ] **Scope overclaim** — general claims from narrow evidence (one dataset,
      one metric, one regime); map each claim to the exact evidence backing it.

## Fraud-pattern screens (from `experiment-integrity`, inverted)

- [ ] **Fake ground truth from model outputs** — "labels" or references that
      are themselves model-generated, then scored against.
- [ ] **Self-normalized scores** — metrics normalized by the method's own
      quantities, so improvement is built into the denominator.
- [ ] **Phantom results** — numbers, panels, or baselines referenced but never
      shown, or shown but traceable to no described procedure.
- [ ] **Pilot-called-comprehensive** — small exploratory runs narrated as full
      evaluations ("we evaluate extensively on…").

## Pre-publication reader gate

Run this on the built release candidate after the technical audits and before
the user's publication signal. A checked Layer-A item is a deterministic pass;
a checked Layer-B item means a fresh-context reviewer answered the question and
the member project's existing audit or correction record carries the verdict.

### Layer A — deterministic release checks

- [ ] The intended reader-facing surface is the default entry.
- [ ] Current public prose contains no stale draft, unpublished, work-order,
      owner-call, private-path or unsubstituted-placeholder language.
- [ ] Internal actions, tabs, anchors and required external links resolve.
- [ ] Keyboard navigation, focus transfer, responsive widths, overflow and
      browser-console behavior pass for the delivery shape.
- [ ] Generated public copies are byte-identical when the project promises a
      deterministic build.
- [ ] Consequential headline wording is regression-pinned against accidental
      drift.
- [ ] The current reader surface agrees with the complete report and README.

### Layer B — fresh-context reader review

- [ ] Can the reviewer state the principal contribution after reading the
      default surface without first reading the audit trail?
- [ ] Does the strongest result receive the most space, with exploratory or
      lower-information arms kept in proportion?
- [ ] Is every material qualifier adjacent to the claim it limits?
- [ ] Does numerical precision match evidential precision for coarse proxies,
      small samples and wide intervals?
- [ ] Are failures to reject described as uncertainty rather than proof of no
      change?
- [ ] Has each headline external claim been checked against its source-native
      page, figure, table or dataset?
- [ ] Does the report read as a completed publication rather than a task status
      or pending deliverable?
- [ ] Is audit and custody information preserved but subordinate to the
      reader's scientific path?
- [ ] Does every use of “independent” name the dimension actually achieved?
- [ ] Are the reader entry, complete report, README, figures and interactive
      labels mutually consistent?

### Headline source rule

Each headline claim must map to at least one of: direct inspection of the
source-native page/figure/table/dataset; independently double-entered
transcription tied to a physical scan; deterministic derivation from manifested
data; or an explicit inference whose premises and residual uncertainty are
stated. A locally missing but reasonably obtainable source figure remains an
open source task, not a permanent reason to harden a provisional claim.

### Cross-project method provenance

For every reused method, record exactly one class: **copied/shared code**,
**adapted code**, **independent reimplementation of a common design**, or
**high-level precedent only**. Compare implementations far enough to decide
whether a discovered defect could propagate to the earlier project. Do not say
“imported” when only the framework or precedent was reused.

### Recording rule

Record concrete passages/interactions, severity, the smallest defensible
correction and the reviewer's actual independence dimension in the member
project's existing audit or correction record. A same-family or cross-agent
review can catch implementation defects; it is not independent human conceptual replication.
If a correction lands, rebuild and repeat the failed checks. Do not create a
mandatory standalone reader-gate receipt.

## Usage notes

- These are **lenses, not verdicts**: a checked box means "screened," and any
  hit still needs the full evidence chain (reproduction, measurement,
  pre-registered predictions) before it lands in a writeup.
- No intent language anywhere — findings are stated as incompatibilities and
  unsupported claims, per the project's honesty ceiling.

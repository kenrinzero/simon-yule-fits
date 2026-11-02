# Paper provenance

- **Paper:** Herbert A. Simon, "On a Class of Skew Distribution Functions",
  *Biometrika* 42(3/4), 425–440 (December 1955). JSTOR stable 2333389.
- **File:** `paper.pdf`: the JSTOR scan, 17 pages (1 JSTOR cover page + printed
  pp. 425–440). Printed page *p* is PDF page index *p* − 424 (0-based).
- **Obtained:** a JSTOR download (stable URL https://www.jstor.org/stable/2333389),
  copied into the working folder on 2026-11-01. The scan is copyrighted and is
  not redistributed; the hash below identifies the exact file every page
  locator refers to.
- **SHA-256:** `116c2ede858f5117c56b88622672d8ef7b091a874f3ae32396f155e156f6bd72`
- **Bytes:** 1,528,127

## Transcription

The printed tables used here are in `../data/printed_tables.csv`. Every cell
was read from 200-dpi renders of pp. 430, 436 and 437, which are kept in
`../results/pages/`. An earlier Markdown transcription of the paper, made
for a separate reading project, served only as a second reading. Where the two disagree, the page image is the source of record. They
did not disagree on any table cell.

Non-table differences between the page and `paper.md`, found while reading:

- p. 436 prints `f(i) = Ka^{-(ρ+1)}`. `paper.md` silently corrects this to
  `Ki^{-(ρ+1)}`. The printed `a` is a typo for `i`
  (`results/pages/p436-fit-sentence.png`).
- p. 436 prints "4½ million words" for Thorndike's count, but `paper.md` reads
  "41 million". The page also reads "our ρ̄ at 0·45" and
  `p₁ = ρ̄/(ρ̄+1) = 0·31`, where `paper.md` drops the bar.

## Reprint check (*Models of Man*, 1957)

The paper is reprinted as chapter 9 of Simon, *Models of Man* (Wiley, 1957),
pp. 145–164, reset in new type. The Internet Archive copy
(`modelsofman0000herb`) is borrow-only, so it was not used. A 10-page PDF of
the chapter, produced by the Carnegie Mellon University Library (Herbert Simon
Collection), is hosted at http://languagelog.ldc.upenn.edu/myl/SimonSkew.pdf
(SHA-256 `47ca6e8d…a678d6`, retrieved 2026-11-02). It shows Simon's own copy:
a handwritten note on p. 145 gives the original Biometrika citation. Only the
two spreads with the tables are kept, as renders in
`../data/raw/modelsofman1957/` (custody in `MANIFEST.csv`).

All 152 table cells were typed from the reprint images into
`../data/reprint_1957_models_of_man.csv` in a separate entry pass by the same
agent, without viewing `printed_tables.csv`. They equal the Biometrika cells one for one
(`tests/test_reprint.py`). The reprint corrects nothing:

- Table 1 keeps 0.527 and 0.171;
- Tables 2 and 3 are unchanged, including Physicists k = 3,396;
- the fit sentence keeps `Ka^{-(ρ+1)}`, and the Thorndike sentence reads
  "4½ million".

The table pages carry a few specks near Table 2's 4,870 and 2,220. They are
illegible and are read as scan noise. Not checked: Ijiri & Simon (1977) and any
later printing of *Models of Man*.

# Stage 2: double entry and adjudication

Each source table was entered twice, independently (PREREGISTRATION.md
Amendment 1, A1.2). Every disagreement was settled from the page image. No
reading was chosen to make a sum work. The first entries were made by
fresh-context Claude subagents working from the images alone; the second
entries are named per row. The images, their URLs and their
SHA-256 hashes are in `../raw/MANIFEST.csv`.

## The entries

| File | First entry | Second entry | Disagreements | Result |
|---|---|---|---|---|
| `davis1941_p429_chicago.csv` | fresh-context transcriber, image only | the implementing agent's own read of `leaf452.jpg` | 0 of 26 rows | 278 persons, k = 1,124 |
| `davis1941_p430_cumulative.csv` | transcriber | recomputed from p. 429: y(actual) = #persons with ≥ x−3 papers | 0 of 10 | confirms these are cumulative counts in 7-wide classes |
| `davis1941_p431.csv` | transcriber | Lotka Table 1, the other printing, entered by a separate transcriber | 0 rows (Chem A+B and Auerbach, after resolving Lotka's ranged rows) | 6,891 / k 22,939; 1,325 / k 3,398 |
| `lotka1926_table1.csv` | transcriber, image only | Davis p. 431 for A+B and Auerbach. A and B are covered by their own printed per-cent columns (every printed % matches count/total) and by A + B = A+B in every row | 0 | the column totals 1,543 / 5,348 / 6,891 / 1,325 all hold |
| `eldridge1911_list5_counts.csv` (499 words) | transcriber, image only | the djvu OCR text layer, plus the the implementing agent's own read of 45 high-frequency words the OCR mangled | 3 of 371 OCR-matched words, 0 of 45 own reads | all three settled to the transcriber's reading (below) |
| `eldridge1911_list5_headers.csv` | transcriber (pp. 49–52) | the implementing agent's read pp. 54 and 56 for the twice/once headers | none | 6,002 types and 43,989 tokens close exactly |
| `zipf1949_ulysses.csv` | the implementing agent's read of pp. 23 and 31 (leaves 41, 49) | the djvu OCR text layer | none | |

## Eldridge disagreements (OCR against transcriber; page p. 49, `leaf52.jpg`)

| Word | Transcriber | OCR | Image | Note |
|---|---|---|---|---|
| To | 1309 | 10 | **1309** | Eldridge's own preface also prints "to, 1309 times" (OCR text l. 500) |
| Says | 42 | 43 | **42** | The OCR took the 43 from "Did" in the row above |
| Cause | 15 | 16 | **15** | |

## Traps flagged in the pre-study plan, and how each came out

- Lotka's OCR reads B = 148 at n = 5. The image reads **143**, and its per-cent
  column and A+B = 184 agree.
- Davis's OCR drops the persons column for x ≥ 14. This did not matter, because
  the transcription came from the image.
- Eldridge's OCR corrupts counts. That was seen three times above, and each was
  settled from the image.

## Annotations on the scans (none changes a digit)

- **Eldridge pp. 49–50:** pen ticks, underlines and one marginal "26" on several
  entries (Recently, Told, Obtained, Baby, Young, Taken, Making, Give, Family).
  Each printed digit was read under the mark at 2–3× zoom.
- **Davis p. 429, n = 8:** a tick beside "3".
- **Lotka p. 318:** specks next to the n = 30 Auerbach "1" and the n = 31 A
  "0".

## Source discrepancy against Simon

The Physicists (Auerbach) table gives k = Σ n·count = **3,398** in both
printings (Lotka and Davis). Simon's Table 3 footer prints **3,396**. It
changes no Stage 1 label: with k = 3,398 the recipe's f(1) is 822.95 instead
of 823.07, and every rounded cell stays the same.

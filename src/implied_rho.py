"""Exploratory (post-freeze, not a convention): the rho implied by each pair of
adjacent printed estimate cells, inverting (2.11): rho = (i-1)*f(i-1)/f(i) - i.
Writes results/stage1-implied-rho.csv."""
import csv
from pathlib import Path
import recipe

ROOT = Path(__file__).resolve().parents[1]
p = recipe.load_printed(); ext = recipe.load_external()
rows = []
for table, sets in (("T2", recipe.T2_SETS), ("T3", recipe.T3_SETS[1:])):
    for s in sets:
        inp = recipe.set_inputs(table, s, p, ext)
        est = inp["est"]
        rho_exact = recipe.rho_of_alpha(inp["n"] / inp["k"])
        for i in range(2, inp["imax"] + 1):
            r = (i - 1) * est[i - 1] / est[i] - i
            rows.append(dict(table=table, set=s, pair=f"{i-1}->{i}", implied_rho=f"{r:.3f}",
                             recipe_rho=f"{rho_exact:.3f}"))
with open(ROOT / "results" / "stage1-implied-rho.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator="\n"); w.writeheader(); w.writerows(rows)
for r in rows: print(r)

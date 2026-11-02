"""Render results/stage3-summary.json as the verdict tables used in REPORT.md
(results/stage3-verdicts.md) and evaluate the Amendment 2 predictions."""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
S = json.loads((ROOT / "results" / "stage3-summary.json").read_text(encoding="utf-8"))
SETS = ["chicago", "chem", "physicists", "econometrica", "eldridge", "ulysses"]
PROCS = [f"II_beta{b}" for b in (1.0, 0.9, 0.8, 0.7, 0.6)] + ["III_B3k"]
L = []
L.append("| Set | n | k | ρ MoM | ρ MLE cens | ρ MLE full | G obs | p1 obs | r21 obs |")
L.append("|---|---|---|---|---|---|---|---|---|")
for s in SETS:
    o = S["observed"][s]
    full = "—" if o["full"] != o["full"] else f"{o['full']:.3f}"
    L.append(f"| {s} | {o['n']:,} | {o['k']:,} | {o['mom']:.3f} | {o['cens']:.3f} | {full} | {o['G']:+.3f} | {o['p1']:.3f} | {o['r21']:.3f} |")
L.append("")
L.append("Null medians [95% interval] of G; ✓ = observed inside. Then p1 / r21 inside? and joint.")
L.append("")
L.append("| Set | Process | G null median [2.5, 97.5] | G obs pct | robust z | G | p1 | r21 | joint |")
L.append("|---|---|---|---|---|---|---|---|---|")
for s in SETS:
    for p in PROCS:
        e = S["nulls"].get(f"{s}__{p}")
        if not e:
            continue
        g = e["G"]
        z = "—" if g["robust_z"] is None else f"{g['robust_z']:+.1f}"
        mark = lambda b: "✓" if b else "✗"
        L.append(f"| {s} | {p.replace('II_beta1.0', 'II (β=1)').replace('II_beta', 'CaseII β=').replace('III_B3k', '§III')} | "
                 f"{g['median']:+.3f} [{g['lo']:+.3f}, {g['hi']:+.3f}] | {g['obs_percentile']:.1f} | {z} | "
                 f"{mark(g['inside'])} | {mark(e['p1']['inside'])} | {mark(e['r21']['inside'])} | {mark(e['joint'])} |")
L.append("")
# predictions
pred = {}
w = {s: (S["nulls"][f"{s}__III_B3k"]["n_over_k"]["width"], S["nulls"][f"{s}__II_beta1.0"]["n_over_k"]["width"]) for s in SETS}
pred["P7b"] = dict(holds=all(a > b for a, b in w.values()), widths_III_vs_II={s: [round(a, 5), round(b, 5)] for s, (a, b) in w.items()})
meds = {s: [S["nulls"][f"{s}__II_beta{b}"]["G"]["median"] for b in (1.0, 0.9, 0.8, 0.7, 0.6)] for s in SETS}
pred["P7c"] = dict(holds=all(all(m < 0 for m in v[1:]) and all(v[i + 1] < v[i] for i in range(4)) for v in meds.values()),
                   medians_beta_1_to_0_6={s: [round(m, 4) for m in v] for s, v in meds.items()})
pred["P9"] = dict(holds=all(not S["nulls"][f"{s}__II_beta1.0"]["G"]["inside"] for s in ("chem", "physicists", "econometrica")))
pred["P10"] = dict(holds=not any(S["nulls"][f"chem__{p}"]["joint"] for p in PROCS if f"chem__{p}" in S["nulls"]))
pred["P11"] = dict(holds=all(v["passes"] for v in S["selftest"].values()),
                   coverage={s: v["coverage"] for s, v in S["selftest"].items()})
conv = S["nulls"].get("physicists__III_B6k")
if conv:
    b3 = S["nulls"]["physicists__III_B3k"]
    sd = lambda e, st: (e[st]["hi"] - e[st]["lo"]) / 3.92
    pred["convergence_III"] = {st: dict(med3=b3[st]["median"], med6=conv[st]["median"],
                                        ok=abs(b3[st]["median"] - conv[st]["median"]) < sd(b3, st)) for st in ("p1", "G")}
L.append("```json")
L.append(json.dumps(pred, indent=1))
L.append("```")
out = ROOT / "results" / "stage3-verdicts.md"
out.write_bytes(("\n".join(L) + "\n").encode("utf-8"))
print("\n".join(L))

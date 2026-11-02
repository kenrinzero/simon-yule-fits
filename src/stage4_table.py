"""Render results/stage4-summary.json as the verdict tables used in REPORT.md
(results/stage4-verdicts.md) and evaluate the Amendment 3 predictions."""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
S = json.loads((ROOT / "results" / "stage4-summary.json").read_text(encoding="utf-8"))
SETS = ["chicago", "chem", "physicists", "eldridge", "econometrica"]
GRADED = ["chicago", "chem", "physicists", "econometrica"]
MODELS = ["yule", "zeta", "logseries", "sichel", "waring", "cutoff", "enb", "gigp"]
PNAMES = dict(yule="ρ", zeta="s", logseries="θ", sichel="θ", waring="ρ, c", cutoff="ρ, b", enb="r, θ",
              gigp="ν, α, θ")
cmp_ = {(r["set"], r["rival"]): r for r in S["compare"]}
L = []
for s in SETS:
    fits, gof = S["fits"][s], S["gof"].get(s, {})
    L.append(f"### {s} (n = {S['n'][s]:,})")
    L.append("")
    L.append("| Model | Params | LL | ΔAIC | X² obs | X² p | KS p | vs Yule | stat | p | verdict |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for m in MODELS:
        f, g = fits[m], gof.get(m, {})
        par = ", ".join(f"{v:.4g}" for v in f["params"]) + (" (bound)" if f["at_bound"] else "")
        ks = f"{g['ks_p']:.3f}" if "ks_p" in g else "—"
        x2p = f"{g['x2_p']:.3f}" if "x2_p" in g else "—"
        x2o = f"{g['x2_obs']:.1f}" if "x2_obs" in g else "—"
        c = cmp_.get((s, m))
        vs = (f"{c['test']} | {c['stat']:+.2f} | {c['p']:.3g} | {c['verdict']}" if c else "— | — | — | —")
        L.append(f"| {m} | {PNAMES[m]} = {par} | {f['ll']:.2f} | {f['daic']:.1f} | {x2o} | {x2p} | {ks} | {vs} |")
    L.append("")

pred = {}
ch = S["fits"]["chem"]
pred["P7a"] = dict(holds=ch["enb"]["aic"] > ch["yule"]["aic"], aic_enb=ch["enb"]["aic"], aic_yule=ch["yule"]["aic"],
                   enb_params=ch["enb"]["params"])
pred["P12"] = dict(holds=all(cmp_[(s, "zeta")]["verdict"] == "Yule favoured" for s in ("chem", "physicists")),
                   z={s: cmp_[(s, "zeta")]["stat"] for s in ("chem", "physicists")})
pred["P13"] = dict(holds=S["gof"]["chem"]["yule"]["x2_p"] < 0.05, x2_p=S["gof"]["chem"]["yule"]["x2_p"])
pred["P14"] = dict(holds=S["sichel"]["grade"] in ("reproduced", "consistent with"), **S["sichel"])
best = min(MODELS, key=lambda m: ch[m]["aic"])
pred["P15"] = dict(holds=len(ch[best]["params"]) >= 2, best=best)
grade = {}
for s in GRADED:
    f = S["fits"][s]
    grade[s] = dict(yule_x2_p=S["gof"][s]["yule"]["x2_p"],
                    reasonably_good="holds" if S["gof"][s]["yule"]["x2_p"] >= 0.05 else "fails",
                    yule_daic=f["yule"]["daic"], yule_within_2_of_best=f["yule"]["daic"] <= 2,
                    best=min(MODELS, key=lambda m: f[m]["aic"]))
fails = {s: {m: g["failed"] for m, g in S["gof"][s].items() if g["failed"]} for s in S["gof"]}
L.append("```json")
L.append(json.dumps(dict(predictions=pred, reasonably_good=grade, bootstrap_failures=fails), indent=1))
L.append("```")
out = ROOT / "results" / "stage4-verdicts.md"
out.write_bytes(("\n".join(L) + "\n").encode("utf-8"))
print("\n".join(L))

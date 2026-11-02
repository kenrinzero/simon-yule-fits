"""Re-derive the headline numbers REPORT.md states, and require each one verbatim.

Every claim is computed from the committed data and results (no refits), then
formatted the way the report writes it. The formatted string (the "needle") must
occur in REPORT.md; a missing needle is a MISMATCH. This pins the consequential
wording against accidental drift (reader gate, Layer A).

    python src/verify_report_numbers.py     # writes results/deliver-number-checks.txt

Exit status 0 when every claim is re-derived and every needle found; 1 otherwise.
Precedent: ../1913-auerbach-das-gesetz-der-bevoelkerungskonzentration/src/verify_report_numbers.py
(the needle idea only; this file shares no code with it).
"""
import csv
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results"
REPORT = ROOT / "REPORT.md"
OUTFILE = RES / "deliver-number-checks.txt"
MINUS = "−"


def _json(name):
    return json.loads((RES / name).read_text(encoding="utf-8"))


def _rows(path):
    return list(csv.DictReader(open(path, encoding="utf-8")))


def signed(v, nd):
    s = f"{abs(v):.{nd}f}"
    return (MINUS + s) if v < 0 else ("+" + s if v > 0 else s)


def claims():
    out = []
    add = lambda cid, value, needle: out.append((cid, value, needle))

    # ---------------- Stage 1
    pt = {(r["table"], r["set"], r["kind"], r["row"]): r["printed"] for r in _rows(ROOT / "data" / "printed_tables.csv")}
    cells = {(r["table"], r["set"], r["cell"]): float(r["recipe"]) for r in _rows(RES / "stage1-cells.csv")}
    sets = ["chicago", "chem", "physicists", "econometrica"]
    # recomputed exactly (the stage1-cells CSV stores two decimals, too coarse for 36.55 -> 36.6);
    # Chicago's column is Simon's rho-bar chain, taken from the CSV
    rec11 = {"chicago": cells[("T3", "chicago", "11+")]}
    for s in sets[1:]:
        n, k = float(pt[("T3", s, "n_k", "")]), float(pt[("T3", s, "k", "")])
        a, rho = n / k, k / (k - n)
        f = [n / (2 - a)]
        for i in range(2, 11):
            f.append(f[-1] * (i - 1) / (i + rho))
        rec11[s] = n - sum(f)
    obs11 = {s: float(pt[("T3", s, "actual", "11+")]) for s in sets}
    prn11 = {s: float(pt[("T3", s, "estimate", "11+")]) for s in sets}
    add("S1.recipe11", rec11, "| recipe estimate | %.1f | %.1f | %.1f | %.1f |" % tuple(rec11[s] for s in sets))
    n_rec = sum(rec11[s] > obs11[s] for s in sets)
    n_prn = sum(prn11[s] > obs11[s] for s in sets)
    assert (n_prn, n_rec) == (3, 1) and rec11["chicago"] > obs11["chicago"]
    add("S1.tail_counts", (n_prn, n_rec), "exceed them in 1 of 4: Chicago only")
    add("S1.chem_shortfall", prn11["chem"] - rec11["chem"], "%.1f persons" % (prn11["chem"] - rec11["chem"]))
    lc = _json("stage1-summary.json")["label_counts"]["T3"]
    weak = lc.get("reproduced-under-X (weak)", 0)
    add("S1.labels_T3", lc, "| Table 3 (43 cells) | %d | %d (one weak) | %d | %d |"
        % (lc["exact"], lc["reproduced-under-X"] + weak, lc["rounding slip"], lc["not reproduced"]))
    ir = {(r["set"], r["pair"]): r for r in _rows(RES / "stage1-implied-rho.csv")}
    r = ir[("chem", "1->2")]
    add("S1.chem_step_rho", r["implied_rho"], "Chem: %.2f vs %.2f" % (float(r["implied_rho"]), float(r["recipe_rho"])))

    # ---------------- Stage 2
    s4 = _json("stage4-summary.json")
    zeta = s4["fits"]["chem"]["zeta"]["params"][0]
    add("S2.smolinsky", zeta, "α̂ = %.6f" % zeta)
    rp = [r for r in _rows(RES / "stage2-rho-prime.csv") if r["matches_1_07"] == "True"]
    assert len(rp) == 1
    add("S2.rho_prime_hit", rp[0]["value"], "at %s (n = 102)" % rp[0]["value"])

    # ---------------- Stage 3
    s3 = _json("stage3-summary.json")
    g = s3["observed"]["chicago"]["G"]
    add("S3.G_chicago", g, "| %s |" % signed(g, 3))
    cov = [v["coverage"] for v in s3["selftest"].values()]
    add("S3.selftest", (min(cov), max(cov)), "%.1f–%.1f%%" % (100 * min(cov), 100 * max(cov)))

    # ---------------- reprint
    rep = _rows(ROOT / "data" / "reprint_1957_models_of_man.csv")
    bio = {(r["table"], r["set"], r["kind"], r["row"]): r["printed"] for r in _rows(ROOT / "data" / "printed_tables.csv")}
    same = sum(bio[(r["table"], r["set"], r["kind"], r["row"])] == r["printed"] for r in rep)
    assert same == len(rep) == len(bio)
    add("R.cells", same, "All %d table cells were typed from the reprint images" % same)

    # ---------------- Stage 4
    th = s4["sichel"]["theta_mle"]
    add("S4.sichel", th, "θ = %.6f, which rounds to Sichel's 0.96876" % th)
    ch = s4["fits"]["chem"]
    add("S4.P7a", ch["yule"]["aic"] - ch["enb"]["aic"], "ΔAIC %.1f" % (ch["yule"]["aic"] - ch["enb"]["aic"]))
    names = dict(chicago="Chicago", chem="Chem", physicists="Physicists", econometrica="Econometrica")
    for s in sets:
        gf = s4["gof"][s]["yule"]
        hits = round(gf["x2_p"] * gf["B"])
        grade = "rejected" if gf["x2_p"] < 0.05 else "not rejected"
        add(f"S4.grade.{s}", gf["x2_p"], "| %s | %d | %.3f | %s | %.1f |"
            % (names[s], hits, gf["x2_p"], grade, s4["fits"][s]["yule"]["daic"]))
    zs = [c["stat"] for c in s4["compare"] if c["rival"] == "zeta"]
    add("S4.zeta_range", (min(zs), max(zs)), "%s (Econometrica) to %s (Eldridge)" % (signed(min(zs), 2), signed(max(zs), 2)))
    ub = 1 - 0.05 ** (1 / 500)
    add("S4.zero_bound", ub, "upper bound on the bootstrap probability is %.3f" % ub)
    from scipy.stats import beta
    lo, hi = beta.ppf(0.025, 32, 469), beta.ppf(0.975, 33, 468)
    add("S4.phys_mc", (lo, hi), "95%% simulation interval of %.3f–%.3f" % (lo, hi))

    # ---------------- Stage 5
    s5 = _json("stage5-summary.json")["results"]
    ns = [s5[t]["n"] for t in ("T1", "T2", "T3")]
    add("S5.n", ns, "held (%s)" % " / ".join(f"{v:,}" for v in ns))
    xs = [s5[t]["x42"] for t in ("T1", "T2", "T3")]
    add("S5.x_recounts", (min(xs), max(xs)), "held (x̂ %.3f–%.3f)" % (min(xs), max(xs)))
    add("S5.x_eldridge", s5["eldridge"]["x42"], "| Eldridge | %.3f |" % s5["eldridge"]["x42"])
    add("S5.x_hanley", s5["hanley"]["x42"], "| Hanley (censored at 4) | %.3f |" % s5["hanley"]["x42"])
    ps = [s5[t]["p_42"] for t in ("T1", "T2", "T3")]
    add("S5.p_recounts", (min(ps), max(ps)), "(p %.2f–%.2f)" % (min(ps), max(ps)))
    e3 = [s5[c]["E3"] for c in ("eldridge", "T1", "T2", "T3")]
    add("S5.E3", e3, "| Eldridge | %.2f ✗ | %s ✗ | %.2f ✓ |" % (s5["eldridge"]["E1"], signed(s5["eldridge"]["E2"], 2), s5["eldridge"]["E3"]))
    add("S5.leisen_T2", s5["T2"]["yule_mle"], "T2 gives %.3f (CI %.3f–%.3f)" % (s5["T2"]["yule_mle"], s5["T2"]["yule_lo"], s5["T2"]["yule_hi"]))

    # ---------------- Stage 6
    n6 = len(_rows(RES / "stage6-series.csv"))
    add("S6.points", n6, "figures, %d points" % n6)
    return out


def main():
    text = REPORT.read_text(encoding="utf-8")
    lines, bad = [], []
    for cid, value, needle in claims():
        ok = needle in text
        lines.append(f"CLAIM {cid} {value} :: {'found' if ok else 'MISSING'} :: {needle}")
        if not ok:
            bad.append(cid)
    lines.append(f"{len(lines)} claims, {len(bad)} mismatches" + (": " + ", ".join(bad) if bad else ""))
    body = "\n".join(lines) + "\n"
    OUTFILE.write_bytes(body.encode("utf-8"))
    sys.stdout.buffer.write(body.encode("utf-8"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

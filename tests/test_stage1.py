"""Pins the transcription invariants and the Stage 1 headline results."""
import csv
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import recipe  # noqa: E402


def printed():
    return recipe.load_printed()


def test_observed_columns_sum_to_n_k():
    p = printed()
    for s in recipe.T3_SETS:
        n = int(p[("T3", s, "n_k", "")])
        tot = sum(int(p[("T3", s, "actual", str(i))]) for i in range(1, 11)) + int(p[("T3", s, "actual", "11+")])
        assert tot == n, s


def test_pooled_cells_equal_row_sums():
    p = printed()
    for s in ("chicago", "physicists", "econometrica"):
        for kind in ("actual", "estimate"):
            rows = sum(int(p[("T3", s, kind, str(i))]) for i in (8, 9, 10))
            assert rows == int(p[("T3", s, kind, "8-10")]), (s, kind)


def test_printed_11plus_is_residual():
    p = printed()
    for s in recipe.T3_SETS:
        n = int(p[("T3", s, "n_k", "")])
        rows = [("T3", s, "estimate", str(i)) for i in range(1, 11)]
        est = sum(int(p[r]) for r in rows if r in p)
        if s == "chicago":
            est += int(p[("T3", s, "actual", "1")])
        assert n - est == int(p[("T3", s, "estimate", "11+")]), s


def test_stage1_headlines():
    subprocess.run([sys.executable, str(ROOT / "src" / "recipe.py")], check=True, capture_output=True)
    summ = json.loads((ROOT / "results" / "stage1-summary.json").read_text(encoding="utf-8"))
    singles = summ["single_combination_reproducing_whole_column"]
    assert singles["chicago"] and not any(singles[s] for s in ("chem", "physicists", "econometrica", "ulysses", "eldridge"))
    g = summ["sentence_grades"]
    assert g["printed"]["S3"]["count"] == 3 and g["recipe"]["S3"]["count"] == 1
    assert g["printed"]["S1"]["holds"] and g["recipe"]["S1"]["holds"]
    assert g["printed"]["S2"]["holds"] and g["recipe"]["S2"]["holds"]
    assert summ["rho_prime_any_match"] is False
    cells = {(r["table"], r["set"], r["cell"]): r["label"]
             for r in csv.DictReader(open(ROOT / "results" / "stage1-cells.csv", encoding="utf-8"))}
    assert cells[("T1", "alpha=0.1", "f1_over_n")] == "rounding slip"
    assert cells[("T1", "alpha=0.3", "f2_over_n")] == "rounding slip"
    assert cells[("T3", "physicists", "1")] == "rounding slip"
    assert cells[("T2", "ulysses", "1")] == "not reproduced"


def test_step0_checks_pass():
    r = subprocess.run([sys.executable, str(ROOT / "src" / "step0_checks.py")], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout

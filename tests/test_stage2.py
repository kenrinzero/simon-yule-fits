"""Pins the Stage 2 source assertions (PREREGISTRATION.md Amendment 1)."""
import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_stage2_assertions():
    subprocess.run([sys.executable, str(ROOT / "src" / "stage2.py")], check=True, capture_output=True)
    s = json.loads((ROOT / "results" / "stage2-summary.json").read_text(encoding="utf-8"))
    hard = [c for c in s["checks"] if "report" not in c["check"]]
    assert len(hard) == 18
    assert all(c["ok"] for c in hard), [c for c in hard if not c["ok"]]
    rep = [c for c in s["checks"] if "report" in c["check"]]
    assert rep and "k=3398" in rep[0]["detail"]
    assert s["rho_prime"]["matches"] == ["zeta MLE x_min=3 (n=102), alpha-1"]


# Scans and OCR layers that are not redistributed (see .gitignore). In a public clone
# they are absent; where present (the working copy) they must still match.
NOT_REDISTRIBUTED = ("davis1941/", "lotka1926/", "eldridge1911/", "zipf1949/", "modelsofman1957/")


def test_raw_manifest_hashes():
    raw = ROOT / "data" / "raw"
    rows = list(csv.DictReader(open(raw / "MANIFEST.csv", encoding="utf-8")))
    assert rows
    for r in rows:
        f = raw / r["path"]
        if not f.exists():
            assert r["path"].startswith(NOT_REDISTRIBUTED), r["path"]
            continue
        b = f.read_bytes()
        assert len(b) == int(r["bytes"]) and hashlib.sha256(b).hexdigest() == r["sha256"], r["path"]
    assert (raw / "gutenberg4300" / "pg4300.txt").exists()


def test_source_csvs_are_lf_utf8():
    for f in (ROOT / "data" / "sources").glob("*.csv"):
        b = f.read_bytes()
        b.decode("utf-8")
        assert b"\r\n" not in b, f.name

"""Reprint check: Models of Man (1957) ch. 9 prints the same 152 table cells as Biometrika."""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _cells(name):
    rows = csv.DictReader(open(ROOT / "data" / name, encoding="utf-8"))
    return {(r["table"], r["set"], r["kind"], r["row"]): r["printed"] for r in rows}


def test_reprint_equals_biometrika():
    bio, rep = _cells("printed_tables.csv"), _cells("reprint_1957_models_of_man.csv")
    assert len(bio) == len(rep) == 152
    assert bio == rep


def test_reprint_csv_is_lf_utf8():
    b = (ROOT / "data" / "reprint_1957_models_of_man.csv").read_bytes()
    b.decode("utf-8")
    assert b"\r\n" not in b

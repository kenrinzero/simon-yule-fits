"""Stage 6: the plotted printed and observed values equal the transcribed cells."""
import csv
import math
import sys
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import stage6 as s6  # noqa: E402


def _cells():
    rows = csv.DictReader(open(ROOT / "data" / "printed_tables.csv", encoding="utf-8"))
    return {(r["table"], r["set"], r["kind"], r["row"]): float(r["printed"]) for r in rows
            if r["kind"] in ("actual", "estimate") and r["row"] != "8-10" and r["printed"] not in ("", "—")}


def _plotted(line):
    row = {s6._x(r): r for r in s6.T3_ROWS + s6.T2_ROWS}
    return {row[int(x)]: float(y) for x, y in zip(line.get_xdata(), line.get_ydata()) if not math.isnan(y)}


def test_plotted_cells_equal_transcription():
    cells = _cells()
    checked = 0
    for table, sets in (("T3", s6.T3_SETS), ("T2", s6.T2_SETS)):
        fig, lines = s6.draw(table)
        for s, _ in sets:
            for series, kind in (("printed", "estimate"), ("observed", "actual")):
                got = _plotted(lines[(s, series, "count")])
                want = {r: v for (t, ss, k, r), v in cells.items() if (t, ss, k) == (table, s, kind)}
                # Econometrica's observed f(10) = 0 is in the data but cannot show on the log axis
                assert got == want, (table, s, series)
                checked += len(got)
        plt.close(fig)
    assert checked == len(cells) == 99  # every actual/estimate cell except the 8-10 brackets and Chicago's blank f(1)


def test_series_csv_is_complete_and_lf():
    b = (ROOT / "results" / "stage6-series.csv").read_bytes()
    assert b"\r\n" not in b
    rows = list(csv.DictReader(b.decode("utf-8").splitlines()))
    assert len(rows) == len(s6.series())

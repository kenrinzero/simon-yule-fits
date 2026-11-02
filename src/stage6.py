"""Stage 6: Tables 3 and 2 drawn from committed files only.

Observed and printed cells come from data/printed_tables.csv, the recipe values
from results/stage1-cells.csv, and the Yule MLE (censored, Stage 3) from
results/stage3-summary.json. Every plotted value is also written to
results/stage6-series.csv, the table view of the figures.

    python src/stage6.py      # writes results/stage6-table3.{png,svg}, stage6-table2.{png,svg}
"""
import csv
import io
import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["svg.hashsalt"] = "simon-1955"  # stable SVG ids, so reruns are byte-identical
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.ticker import FixedLocator, FuncFormatter, NullFormatter  # noqa: E402
from scipy.special import gammaln  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results"
T3_SETS = [("chicago", "Chicago Math. Soc."), ("chem", "Chem. Abstracts"),
           ("physicists", "Physicists"), ("econometrica", "Econometrica")]
T2_SETS = [("ulysses", "Ulysses (Hanley)"), ("eldridge", "Eldridge")]
T3_ROWS = [str(i) for i in range(1, 11)] + ["11+"]
T2_ROWS = ["1", "2", "3"]
# reference palette, first three categorical slots (validated all-pairs, light surface)
INK, INK2, GRID, SURFACE = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
SERIES = {
    "observed": dict(color=INK, marker="o", label="observed", line=False),
    "printed": dict(color="#2a78d6", marker="s", label="printed estimate"),
    "recipe": dict(color="#eb6834", marker="D", label="stated recipe"),
    "mle": dict(color="#1baf7a", marker="^", label="Yule MLE (censored)"),
}


def _x(row):
    # the pooled 11+ cell sits apart, after a gap at 11 (see _gap)
    return 12 if row == "11+" else int(row)


def _gap(xs, ys):
    """Break the line between row 10 and the pooled 11+ cell."""
    if 12 in xs and xs.index(12) > 0:
        k = xs.index(12)
        return xs[:k] + [11] + xs[k:], ys[:k] + [float("nan")] + ys[k:]
    return xs, ys


def series():
    """One row per plotted point: table, set, row, series, value."""
    pt = {(r["table"], r["set"], r["kind"], r["row"]): r["printed"]
          for r in csv.DictReader(open(ROOT / "data" / "printed_tables.csv", encoding="utf-8"))}
    rc = {(r["table"], r["set"], r["cell"]): r["recipe"]
          for r in csv.DictReader(open(RES / "stage1-cells.csv", encoding="utf-8"))}
    obs3 = json.loads((RES / "stage3-summary.json").read_text(encoding="utf-8"))["observed"]
    out = []
    for table, sets, rows in (("T3", T3_SETS, T3_ROWS), ("T2", T2_SETS, T2_ROWS)):
        for s, _ in sets:
            rho, n = obs3[s]["cens"], obs3[s]["n"]
            for row in rows:
                for name, val in (("observed", pt.get((table, s, "actual", row))),
                                  ("printed", pt.get((table, s, "estimate", row))),
                                  ("recipe", rc.get((table, s, row)))):
                    if val not in (None, "", "—"):
                        out.append(dict(table=table, set=s, row=row, series=name, value=float(val)))
                out.append(dict(table=table, set=s, row=row, series="mle", value=n * _yule(rho, row)))
    return out


def _yule(rho, row):
    """Yule pmf at i, or the survival P(I >= 11) for the 11+ row."""
    if row == "11+":
        return math.exp(math.log(10) + gammaln(10) + gammaln(rho + 1) - gammaln(11 + rho))
    i = int(row)
    return math.exp(math.log(rho) + gammaln(i) + gammaln(rho + 1) - gammaln(i + rho + 1))


RATIO_TICKS = [0.25, 0.33, 0.5, 0.67, 0.8, 0.9, 1.0, 1.1, 1.25, 1.5, 2.0, 3.0, 4.0]


def _plain(v, _pos=None):
    return f"{v:,.0f}" if v >= 10 else f"{v:g}"


def _log_axis(ax, ticks=None):
    ax.set_yscale("log")
    lo, hi = ax.get_ylim()
    if ticks is not None:
        keep, step = [1.0], math.log10(hi / lo) / 5
        for v in sorted((v for v in ticks if lo <= v <= hi and v != 1.0), key=lambda v: abs(math.log10(v))):
            if all(abs(math.log10(v / k)) >= step for k in keep):
                keep.append(v)
        ax.yaxis.set_major_locator(FixedLocator(sorted(keep)))
    ax.yaxis.set_major_formatter(FuncFormatter(_plain))
    ax.yaxis.set_minor_formatter(NullFormatter())


def _style(ax):
    ax.set_facecolor(SURFACE)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(INK2)
    ax.tick_params(colors=INK2, labelsize=8)
    ax.grid(True, axis="y", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)


def draw(table, rows_out=None):
    """Draw one table. Returns (figure, {(set, series, panel): Line2D})."""
    sets, rows = (T3_SETS, T3_ROWS) if table == "T3" else (T2_SETS, T2_ROWS)
    pts = [p for p in (rows_out or series()) if p["table"] == table]
    val = {(p["set"], p["series"], p["row"]): p["value"] for p in pts}
    fig, axes = plt.subplots(2, len(sets), figsize=(3.6 * len(sets) + 0.4, 6.0), sharex=True,
                             gridspec_kw=dict(height_ratios=[1.3, 1]), squeeze=False)
    fig.patch.set_facecolor(SURFACE)
    lines = {}
    for j, (s, title) in enumerate(sets):
        top, bot = axes[0][j], axes[1][j]
        for ax in (top, bot):
            _style(ax)
        top.set_title(title, fontsize=10, color=INK, loc="left")
        for name, st in SERIES.items():
            rr = [r for r in rows if (s, name, r) in val]
            xs = [_x(r) for r in rr]
            ys = [val[(s, name, r)] for r in rr]
            kw = dict(color=st["color"], marker=st["marker"], markersize=5, linewidth=0 if st.get("line") is False else 1.6,
                      label=st["label"], markeredgecolor=SURFACE, markeredgewidth=0.8, zorder=3 if name == "observed" else 2)
            lines[(s, name, "count")] = top.plot(*_gap(xs, ys), **kw)[0]
            if name != "observed":
                ratio = [(x_, val[(s, name, r)] / val[(s, "observed", r)]) for x_, r in zip(xs, rr)
                         if val.get((s, "observed", r))]
                lines[(s, name, "ratio")] = bot.plot(*_gap([a for a, _ in ratio], [b for _, b in ratio]), **kw)[0]
        _log_axis(top)
        bot.axhline(1.0, color=INK2, linewidth=0.8, zorder=1)
        _log_axis(bot, RATIO_TICKS)
        bot.set_xticks([_x(r) for r in rows], rows)
        if table == "T3":
            for ax in (top, bot):
                ax.axvline(11, color=GRID, linewidth=1.0, linestyle=":", zorder=0)
        bot.set_xlabel("contributions" if table == "T3" else "occurrences", fontsize=8, color=INK2)
        if j == 0:
            top.set_ylabel("persons" if table == "T3" else "words", fontsize=8, color=INK2)
            bot.set_ylabel("estimate ÷ observed", fontsize=8, color=INK2)
    handles = [lines[(sets[0][0], name, "count")] for name in SERIES]
    fig.legend(handles, [SERIES[n]["label"] for n in SERIES], loc="upper left", bbox_to_anchor=(0.01, 0.955),
               ncol=4 if table == "T3" else 2, frameon=False, fontsize=8, labelcolor=INK)
    head = ("Table 3: persons by number of contributions" if table == "T3"
            else "Table 2: words occurring once, twice, three times")
    fig.suptitle(head, x=0.01, y=0.995, ha="left", fontsize=11, color=INK)
    note = ("Recipe: α = n/k with f(1) = n/(2−α), except Chicago, where Simon's footer uses ρ̄ = 133/145 chained "
            "from observed f(1). Econometrica's observed f(10) = 0 cannot show on the log axis and has no ratio. "
            "Yule MLE censored at 11+."
            if table == "T3" else
            "Recipe: α = n/k with f(1) = n/(2−α). Yule MLE censored at 4+ for Ulysses (Hanley's figures via Zipf) "
            "and at 11+ for Eldridge.")
    fig.text(0.01, 0.01, note, ha="left", va="bottom", fontsize=7, color=INK2, wrap=True)
    fig.tight_layout(rect=(0, 0.05 if table == "T3" else 0.07, 1, 0.92 if table == "T3" else 0.86))
    return fig, lines


def main():
    pts = series()
    with open(RES / "stage6-series.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["table", "set", "row", "series", "value"], lineterminator="\n")
        w.writeheader()
        w.writerows(pts)
    for table, stem in (("T3", "stage6-table3"), ("T2", "stage6-table2")):
        fig, _ = draw(table, pts)
        fig.savefig(RES / f"{stem}.png", dpi=160, facecolor=SURFACE)
        # SVG through a buffer, written with LF endings: matplotlib's text-mode file write
        # would give CRLF on Windows, and the committed bytes must match on every platform
        buf = io.BytesIO()
        fig.savefig(buf, format="svg", dpi=160, facecolor=SURFACE, metadata={"Date": None})
        (RES / f"{stem}.svg").write_bytes(buf.getvalue().replace(b"\r\n", b"\n"))
        plt.close(fig)
    print(f"{len(pts)} points; figures in results/stage6-table3.* and stage6-table2.*")


if __name__ == "__main__":
    main()

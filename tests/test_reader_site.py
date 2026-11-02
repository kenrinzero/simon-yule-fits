"""The published surface: reader page, headline pins and public-prose hygiene (reader gate, Layer A)."""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import build_reader as B  # noqa: E402

PUBLIC_PROSE = ["README.md", "REPORT.md", "CREDITS.md", "CLAIM_INVENTORY.md", "REPORT-LICENSE",
                "paper/PROVENANCE.md", "data/sources/ADJUDICATION.md", "AUDIT-2026-11-02.md", "docs/index.html"]


def _page():
    return (ROOT / "docs" / "index.html").read_text(encoding="utf-8")


def test_page_is_current_deterministic_and_mirrored():
    html, _, _ = B.build()
    assert html == B.build()[0]
    assert (ROOT / "docs" / "index.html").read_bytes() == html.encode("utf-8")
    assert (ROOT / "results" / "reader.html").read_bytes() == html.encode("utf-8")
    assert (ROOT / "docs" / ".nojekyll").exists()


def test_page_is_self_contained():
    html = _page()
    B.assert_self_contained_html(html)
    assert html.count(B.SELF_CONTAINED_FAVICON) == 1


def test_overview_is_the_default_landing_tab():
    html = _page()
    assert 'show("overview");  // a cold reader lands on the concise synthesis' in html
    assert re.search(r'<section id="tab-overview" role="tabpanel">', html)
    for tab in ("report", "score", "figs", "data"):
        assert '<section id="tab-%s" role="tabpanel" hidden>' % tab in html


def test_tabs_have_keyboard_semantics_and_overview_actions_move_focus():
    html = _page()
    for needle in ('setAttribute("role","tab")', "aria-controls", "aria-labelledby", "ArrowRight", "Home", "End",
                   "panel.focus()", "b.tabIndex"):
        assert needle in html


def test_overview_headline_and_adjacent_qualifiers_are_pinned():
    html = _page()
    for needle in ["rejected by a pre-registered test for three of his four author tables",
                   "<strong>not\n        rejected</strong> by the 11-cell test (p = 0.064, 32 of 500 bootstrap replicates",
                   "0.044&ndash;0.089), which does not show that it fits well",
                   "Only the product c&beta; is identified: 0.145&ndash;0.162",
                   "not a replication of Hanley&rsquo;s 1937 index",
                   "no motive inferred",
                   "0 of 500 exceedances bounds the bootstrap\n        probability only below about 0.006",
                   "Shared blind spots of one family are not ruled out"]:
        assert needle in html, needle


def test_scoreboard_lists_every_prediction_and_the_three_failures():
    rows = B.scoreboard()
    assert len(rows) == 23
    assert {r[1] for r in rows if "failed" in r[3].lower()} == {"P8", "P7a", "P20"}


def test_figures_are_inlined_with_unique_ids():
    html = _page()
    assert html.count("<svg ") == 2 and 'id="t3-' in html and 'id="t2-' in html
    ids = re.findall(r'\bid="([^"]+)"', html)
    assert len(ids) == len(set(ids))


def test_report_numbers_are_pinned():
    r = subprocess.run([sys.executable, str(ROOT / "src" / "verify_report_numbers.py")], capture_output=True)
    assert r.returncode == 0, r.stdout.decode("utf-8")[-800:]


def test_public_prose_has_no_private_paths_or_work_order_voice():
    bad = [r"C:[\\/]", r"\.atelier", r"\.papers\b", r"katflow", r"\bTODO\b", r"\bTBD\b", r"work order",
           r"not yet done", r"so far\b", r"seed idea"]
    for f in PUBLIC_PROSE:
        text = (ROOT / f).read_text(encoding="utf-8")
        for pat in bad:
            assert not re.search(pat, text, re.I), (f, pat)


def test_release_has_no_unfilled_fields():
    # Blocks publication until the owner supplies the Codex model for CREDITS.md.
    for f in PUBLIC_PROSE:
        assert not re.search(r"\[\[[A-Z][A-Z0-9-]*\]\]", (ROOT / f).read_text(encoding="utf-8")), f


def test_every_frozen_contract_version_rebuilds_to_its_recorded_hash():
    r = subprocess.run([sys.executable, str(ROOT / "src" / "verify_prereg_freezes.py")], capture_output=True)
    assert r.returncode == 0, r.stdout.decode("utf-8")

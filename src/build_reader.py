"""Build docs/index.html: the self-contained reader page.

One file, no network, no external assets, no webfonts. Five tabs:

- Overview: the short reader-facing synthesis, the default landing tab.
- Full report: REPORT.md rendered verbatim at build time (render_report_md), so the
  page cannot drift from the text that src/verify_report_numbers.py pins.
- Scoreboard: every "### Predictions" table in REPORT.md, parsed rather than retyped.
- Figures: the Stage 6 SVGs (results/stage6-table*.svg), inlined.
- Data & custody: data/raw/MANIFEST.csv and the transcription files.

Deterministic: no timestamp, no random ids, so a rebuild is byte-identical.

    python src/build_reader.py

Adapted code: the page shell, CSS, tab logic and the Markdown renderer come from
../1913-auerbach-das-gesetz-der-bevoelkerungskonzentration/src/build_explorer.py.
The content, the scoreboard parser, the figure inlining and the custody table are new.
"""
import csv
import hashlib
import io
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results"
REPORT = ROOT / "REPORT.md"
OUT = RES / "reader.html"
DOCS_INDEX = ROOT / "docs" / "index.html"
REPO_URL = "https://github.com/kenrinzero/simon-yule-fits"
BLOB_URL = REPO_URL + "/blob/main/"
SELF_CONTAINED_FAVICON = '<link rel="icon" href="data:,">'
# scans and OCR layers listed in the manifest but not redistributed (see .gitignore)
NOT_REDISTRIBUTED = ("davis1941/", "lotka1926/", "eldridge1911/", "zipf1949/", "modelsofman1957/")


def codex_model():
    m = re.search(r"^\| \*\*Codex\*\* \| (.+?) \|$", (ROOT / "CREDITS.md").read_text(encoding="utf-8"), re.M)
    assert m, "CREDITS.md has no Codex row"
    return m.group(1)


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ---------------------------------------------------------------- Markdown (adapted)
def render_report_md(path):
    """Render REPORT.md (the Markdown subset it uses) to static HTML.

    Nested list items (two-space indent) are kept as nested lists, and relative
    links to repository files point at the repository on GitHub.
    """
    lines = path.read_text(encoding="utf-8").split("\n")

    def inline(s):
        s = esc(s)
        s = re.sub(r"\[([^\]\n]+)\]\((https?://[^\s<>()]+)\)", r'<a href="\2">\1</a>', s)
        s = re.sub(r"\[([^\]\n]+)\]\(([^\s<>():]+)\)", lambda m: '<a href="%s%s">%s</a>' % (BLOB_URL, m.group(2), m.group(1)), s)
        s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
        s = re.sub(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])", r"<em>\1</em>", s)
        s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
        return s

    out, toc = [], []
    para, quote, items, table = [], [], [], []
    blank = [False]
    sec = [0]
    group = [False]

    def open_group():
        if not group[0]:
            out.append('<div class="rp-measure">')
            group[0] = True

    def close_group():
        if group[0]:
            out.append("</div>")
            group[0] = False

    def flush_para():
        if para:
            out.append("<p>%s</p>" % inline(" ".join(para)))
            del para[:]

    def flush_quote():
        if quote:
            out.append("<blockquote>%s</blockquote>" % "".join("<p>%s</p>" % inline(q) for q in quote))
            del quote[:]

    def flush_items():
        # items: (depth, ordered, number, text). A level with no item of its own (a deeper list
        # after an interruption) is a markerless wrapper; an ordered list resumes at its number.
        if not items:
            return
        html, stack = [], []
        base = min(d for d, _, _, _ in items)
        for depth, ordered, number, text in items:
            depth -= base
            tag = "ol" if ordered else "ul"  # ordered is None for a paragraph inside a list
            while len(stack) > depth + 1:
                html.append("</li></%s>" % stack.pop())
            if len(stack) == depth + 1 and stack[-1] != tag:
                html.append("</li></%s>" % stack.pop())
            if len(stack) == depth + 1:
                html.append("</li>")
            while len(stack) < depth:
                html.append('<ul class="bare"><li>')
                stack.append("ul")
            if len(stack) == depth:
                start = ' start="%d"' % number if ordered and number > 1 else ""
                html.append("<%s%s>" % (tag, start))
                stack.append(tag)
            html.append(('<li class="para">%s' if ordered is None else "<li>%s") % inline(text))
        while stack:
            html.append("</li></%s>" % stack.pop())
        out.append("".join(html))
        del items[:]

    def flush_table():
        if not table:
            return
        close_group()
        rows = [r for r in table if not re.match(r"^\s*\|[\s:|-]+\|$", r)]
        head, body = rows[0], rows[1:]
        cells = lambda r: [c.strip() for c in r.strip().strip("|").split("|")]
        th = "".join("<th>%s</th>" % inline(c) for c in cells(head))
        trs = "".join("<tr>%s</tr>" % "".join("<td>%s</td>" % inline(c) for c in cells(r)) for r in body)
        out.append('<div class="tw" role="region" tabindex="0" aria-label="Report table; scroll horizontally to see all columns">'
                   "<table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>" % (th, trs))
        del table[:]

    def flush_all():
        flush_para(); flush_quote(); flush_items(); flush_table()

    for raw in lines:
        line = raw.rstrip()
        if line.lstrip().startswith("|"):
            flush_para(); flush_quote(); flush_items()
            table.append(line.strip())
            continue
        flush_table()
        open_group()
        m_item = re.match(r"^( *)([-*]|\d+\.) (.*)$", line)
        if line.startswith("# "):
            flush_all()
            out.append('<h2 class="rp-title" id="rp-top">%s</h2>' % inline(line[2:]))
        elif line.startswith("## "):
            flush_all()
            sec[0] += 1
            title = inline(line[3:])
            toc.append('<li><a href="#rp-s%d">%s</a></li>' % (sec[0], title))
            out.append('<h2 id="rp-s%d">%s</h2>' % (sec[0], title))
        elif line.startswith("### "):
            flush_all()
            out.append("<h3>%s</h3>" % inline(line[4:]))
        elif line.strip() == "---":
            flush_all()
            out.append("<hr>")
        elif line.startswith("> "):
            flush_para(); flush_items()
            quote.append(line[2:])
        elif m_item:
            blank[0] = False
            flush_para(); flush_quote()
            marker = m_item.group(2)
            items.append((len(m_item.group(1)) // 2, marker[0].isdigit(),
                          int(marker[:-1]) if marker[0].isdigit() else 0, m_item.group(3)))
        elif line.strip() == "":
            if items:
                blank[0] = True
                continue  # a blank line inside a list keeps the list open
            flush_all()
        elif items and raw.startswith("  ") and blank[0]:
            blank[0] = False  # an indented paragraph after a blank line: its own unbulleted entry
            items.append(((len(raw) - len(raw.lstrip(" "))) // 2, None, 0, line.strip()))
        elif items and raw.startswith("  "):
            depth, ordered, number, text = items[-1]
            items[-1] = (depth, ordered, number, text + " " + line.strip())  # continuation of a list item
        else:
            flush_quote(); flush_items()
            para.append(line.strip())
    flush_all()
    close_group()
    return "".join(out), "".join(toc)


# ---------------------------------------------------------------- scoreboard
def scoreboard():
    """Every row of every '### Predictions' table in REPORT.md, with its stage."""
    rows, stage, in_pred = [], "", False
    for line in REPORT.read_text(encoding="utf-8").split("\n"):
        if line.startswith("## "):
            stage = re.sub(r"\s*\(.*$", "", line[3:]).strip()
            in_pred = False
        elif line.startswith("### "):
            in_pred = line.startswith("### Predictions")
        elif in_pred and re.match(r"^\| P\d", line):
            c = [x.strip() for x in line.strip().strip("|").split("|")]
            rows.append((stage, c[0], c[1], c[2]))
    return rows


def render_scoreboard(rows):
    def pill(outcome):
        o = outcome.lower()
        cls = "bad" if "failed" in o else "ok"
        return '<span class="pill %s">%s</span>' % (cls, "failed" if cls == "bad" else "held")

    inline = lambda s: re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", re.sub(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])", r"<em>\1</em>", esc(s)))
    body = "".join("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
                   % (esc(st), pid, inline(pr), pill(oc), inline(oc)) for st, pid, pr, oc in rows)
    n_fail = sum("failed" in r[3].lower() for r in rows)
    return n_fail, ('<div class="score-wrap" role="region" tabindex="0" aria-label="Prediction scoreboard">'
                    "<table><thead><tr><th>Stage</th><th>ID</th><th>Prediction (frozen before the stage's code)</th>"
                    "<th>Verdict</th><th>Outcome as reported</th></tr></thead><tbody>%s</tbody></table></div>" % body)


# ---------------------------------------------------------------- figures
def inline_svg(path, prefix):
    s = path.read_text(encoding="utf-8")
    s = s[s.index("<svg"):]
    s = re.sub(r"<metadata>.*?</metadata>\s*", "", s, flags=re.S)
    s = re.sub(r"<style[^>]*>.*?</style>\s*", "", s, flags=re.S)
    s = s.replace('id="', 'id="%s-' % prefix).replace('href="#', 'href="#%s-' % prefix).replace("url(#", "url(#%s-" % prefix)
    s = re.sub(r'<svg ([^>]*?)width="[^"]*" height="[^"]*"', r'<svg role="img" \1', s, count=1)
    return s.strip()


# ---------------------------------------------------------------- custody
def custody_table():
    rows = list(csv.DictReader(open(ROOT / "data" / "raw" / "MANIFEST.csv", encoding="utf-8")))
    body = []
    for r in rows:
        shipped = not r["path"].startswith(NOT_REDISTRIBUTED)
        status = '<span class="pill ok">shipped</span>' if shipped else '<span class="pill mut">not redistributed</span>'
        body.append("<tr><td><code>%s</code></td><td>%s</td><td>%s</td><td class='n'>%s</td><td><code>%s&hellip;</code></td><td>%s</td></tr>"
                    % (esc(r["path"]), esc(r["kind"]), esc(r["retrieved"]), "{:,}".format(int(r["bytes"])), r["sha256"][:16], status))
    return len(rows), ('<div class="table-scroll" role="region" tabindex="0" aria-label="Raw-source manifest">'
                       "<table><thead><tr><th>File</th><th>Kind</th><th>Retrieved</th><th class='n'>Bytes</th>"
                       "<th>SHA-256</th><th>In this repository</th></tr></thead><tbody>%s</tbody></table></div>" % "".join(body))


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="icon" href="data:,">
<title>Simon 1955 - the printed Yule fits, recomputed</title>
<style>
:root{--bg:#0f1115;--fg:#e6e6e6;--mut:#9aa4b2;--card:#171a21;--line:#2a2f3a;
      --ok:#5ad19a;--warn:#e8c468;--bad:#e8797b;--acc:#6fb3f2;--acc2:#c792ea}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);
     font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
header{padding:22px max(26px,calc((100% - 1180px)/2 + 26px)) 14px;border-bottom:1px solid var(--line)}
h1{margin:0 0 4px;font-size:21px;letter-spacing:.2px}
header p{margin:2px 0;color:var(--mut);font-size:13px}
nav{display:flex;flex-wrap:wrap;gap:6px;padding:12px max(26px,calc((100% - 1180px)/2 + 26px));
    border-bottom:1px solid var(--line);position:sticky;top:0;background:var(--bg);z-index:5}
nav button{background:var(--card);color:var(--fg);border:1px solid var(--line);border-radius:999px;
           padding:7px 14px;font-size:13px;cursor:pointer}
nav button[aria-selected="true"]{border-color:var(--acc);color:#fff;background:#1b2534}
main{padding:18px 26px 60px;max-width:1180px;margin:0 auto}
section[hidden]{display:none}
h2{font-size:17px;margin:18px 0 6px}
h3{font-size:14px;margin:16px 0 4px;color:var(--mut);text-transform:uppercase;letter-spacing:.08em}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px;margin:12px 0;min-width:0}
table{border-collapse:collapse;width:100%;font-size:13px}
th,td{text-align:left;padding:5px 8px;border-bottom:1px solid var(--line);vertical-align:top}
th{color:var(--mut);font-weight:600}
td.n,th.n{text-align:right;font-variant-numeric:tabular-nums}
.pill{display:inline-block;padding:1px 8px;border-radius:999px;font-size:11.5px;border:1px solid var(--line);white-space:nowrap}
.pill.ok{color:var(--ok);border-color:#2c5544}.pill.warn{color:var(--warn);border-color:#5a4c26}
.pill.bad{color:var(--bad);border-color:#5c3236}.pill.mut{color:var(--mut)}
.note{color:var(--mut);font-size:12.5px;margin:6px 0 0}
code{background:#12151c;padding:1px 5px;border-radius:4px;font-size:12.5px;
     overflow-wrap:anywhere;word-break:break-word}
.table-scroll{max-width:100%;overflow-x:auto;-webkit-overflow-scrolling:touch}
.table-scroll table{width:max-content;min-width:100%}
.table-scroll:focus,.tw:focus{outline:2px solid var(--acc);outline-offset:2px}
footer{color:var(--mut);font-size:12px;padding:0 26px 40px;max-width:1180px;margin:0 auto}
header .repo-line{margin:6px 0 2px;font-size:13px;color:var(--fg)}
header .credit-line{margin:2px 0;color:var(--mut);font-size:13px}
header a,footer a,.rp a,.overview a,.fig a{color:#8ab4ff;text-decoration:none}
header a:hover,footer a:hover,.rp a:hover{text-decoration:underline}
footer .fblock{margin:14px 0 0;line-height:1.65}
footer ul.cites{margin:4px 0 0;padding-left:18px}
footer ul.cites li{margin:3px 0}
footer .footer-lead{margin:18px 0 10px;line-height:1.55}
footer details{border-top:1px solid var(--line);padding-top:10px}
footer summary{color:var(--fg);cursor:pointer;font-weight:600}
footer .fineprint{margin-top:16px;padding-top:10px;border-top:1px solid var(--line)}
/* ---- Overview: the short reader-facing entry point ---- */
.overview{max-width:980px;margin:0 auto;padding:10px 0 24px}
.overview-kicker{margin:0 0 6px;color:var(--acc);font-size:12px;font-weight:700;
                 letter-spacing:.1em;text-transform:uppercase}
.overview h2{font-size:28px;line-height:1.2;margin:0 0 12px}
.overview-lede{max-width:none;margin:0 0 22px;font-size:17px;line-height:1.65;color:#d7dce5}
.overview-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
.overview-grid .card{margin:0;padding:18px}
.overview h3{margin:0 0 8px;color:var(--fg);font-size:15px;letter-spacing:0;text-transform:none}
.overview-grid p{margin:0;line-height:1.6}
.overview-caveats{margin:16px 0 0;padding:16px 18px;border-left:3px solid var(--warn);
                  background:var(--card);border-radius:0 10px 10px 0}
.overview-caveats h3{margin:0 0 6px;color:var(--fg);font-size:14px;letter-spacing:0;text-transform:none}
.overview-caveats ul{margin:4px 0 0;padding-left:20px}
.overview-caveats li{margin:5px 0}
.overview-actions{display:flex;gap:10px;flex-wrap:wrap;margin-top:18px}
.overview-actions button{border:1px solid var(--acc);border-radius:7px;background:#1b2534;color:#fff;
                         padding:9px 14px;font:inherit;cursor:pointer}
.overview-actions button.secondary{border-color:var(--line);background:var(--card)}
@media(max-width:760px){.overview-grid{grid-template-columns:1fr}.overview h2{font-size:24px}}
/* ---- Figures ---- */
.fig{background:#fcfcfb;border-radius:10px;padding:10px;margin:12px 0}
.fig svg{display:block;width:100%;height:auto}
.fig svg *{stroke-linejoin:round;stroke-linecap:butt}
.figcap{color:var(--mut);font-size:13px;line-height:1.6;margin:6px 0 22px;max-width:900px}
.fig.narrow{max-width:720px}
.score-wrap{max-width:100%;overflow-x:auto}
.score-wrap table{min-width:720px}
.score-wrap td{white-space:normal}
.score-wrap:focus{outline:2px solid var(--acc);outline-offset:2px}
/* ---- Report tab: reading typography ---- */
.rp{font-size:15px;line-height:1.7;color:var(--fg)}
.rp-lede{color:var(--mut);font-size:13.5px;line-height:1.6;border-left:3px solid var(--acc);
          padding:2px 0 2px 14px;margin:0 0 20px}
.rp-toc{margin:0 0 30px}
.rp-toc strong{display:block;margin:0 0 8px;color:var(--mut);font-size:11.5px;
               text-transform:uppercase;letter-spacing:.08em}
.rp-toc ul{list-style:none;margin:0;padding:12px 18px;background:var(--card);
           border:1px solid var(--line);border-radius:10px}
.rp-toc li{margin:4px 0}
.rp h2.rp-title{font-size:22px;line-height:1.35;margin:0 0 8px;border:0;padding:0;color:var(--fg);
                text-transform:none;letter-spacing:0}
.rp h2{font-size:18px;margin:36px 0 10px;padding-top:20px;border-top:1px solid var(--line);
       color:var(--fg);text-transform:none;letter-spacing:0}
.rp h3{font-size:15.5px;margin:24px 0 6px;color:var(--fg);text-transform:none;letter-spacing:0}
.rp p{margin:10px 0}
.rp ul,.rp ol{margin:10px 0;padding-left:22px}
.rp li{margin:6px 0}
.rp ul.bare{list-style:none;padding-left:0;margin:0}
.rp ul.bare>li{margin:0}
.rp li.para{list-style:none;margin-left:-22px}
.rp blockquote{margin:18px 0;padding:14px 20px;background:var(--card);border:1px solid var(--line);
               border-left:3px solid var(--acc);border-radius:0 10px 10px 0}
.rp blockquote p{margin:8px 0}
.rp .tw{max-width:100%;overflow-x:auto;margin:16px 0}
.rp table{margin:0;font-size:12.5px;min-width:680px}
.rp code{font-size:12.5px;overflow-wrap:anywhere}
/* one shared measure: every heading and paragraph inside .rp-measure shares exactly the same
   box, centered in the page column; tables stay outside it and break out to full width */
.rp-measure{max-width:800px;margin-inline:auto}
</style>
</head>
<body>
<header>
  <h1>Simon (1955) &ldquo;On a Class of Skew Distribution Functions&rdquo; &mdash; the printed Yule fits, recomputed</h1>
  <div class="repo-line"><a href="__REPO__">github.com/kenrinzero/simon-yule-fits</a>
    &mdash; source, data, methods, tests and audit records.</div>
  <div class="credit-line">Directed by Kenrin (<a href="https://github.com/kenrinzero">@kenrinzero</a>).
    Analysis by AI agents under his direction: <b>Claude (Claude Opus 5.5)</b>, with a cross-family audit by
    <b>Codex (__CODEX__)</b>.
    <a href="__REPO__/blob/main/CREDITS.md">Full attribution and independence record</a>.</div>
</header>
<nav id="nav" role="tablist"></nav>
<main>
  <section id="tab-overview" role="tabpanel">
    <div class="overview">
      <p class="overview-kicker">The headline, without the technical ledger</p>
      <h2>What we found</h2>
      <p class="overview-lede">Herbert Simon&rsquo;s 1955 paper fits the Yule distribution to word counts and to
      counts of authors by number of papers, using one stated recipe, and calls the fit &ldquo;reasonably good&rdquo;.
      Recomputed, no convention he states reproduces any whole column except Chicago&rsquo;s, and his own reading
      of where the fit fails partly reverses under his recipe. On the source tables, the one-parameter Yule refitted by likelihood is
      rejected by a pre-registered test for three of his four author tables (an iid parametric bootstrap of the
      refitted model, not a test of his printed estimates). Power laws with an exponential
      cutoff fit three of the four better, and Simon&rsquo;s own two-parameter generalization is the only model
      not rejected on Eldridge&rsquo;s word count.</p>
      <div class="card"><h3>What is new here</h3><p>Under his own stated recipe, Simon&rsquo;s sentence that the
      estimates are &ldquo;too high for the tails&rdquo; in three of four cases becomes one of four. The printed
      f(2) cells run low, and since every printed &ldquo;11 or more&rdquo; cell is the remainder after rows 1&ndash;10,
      the shortfall lands in the tail by construction. No stated convention reproduces any whole column except
      Chicago&rsquo;s (of 77 estimate cells, 62 are exact or reproduce under a stated convention, 4 are rounding slips, 11 reproduce under none), and the 1957
      reprint in <em>Models of Man</em> prints all 152 table cells unchanged, slips included. These are
      reproducibility findings about a 1955 hand computation, with no motive inferred; a cross-family audit
      re-derived the tail arithmetic from the page.</p></div>
      <div class="overview-grid">
        <article class="card"><h3>Moments against likelihood</h3><p>Simon&rsquo;s recipe, &alpha; = n/k, is the
        method-of-moments estimate of the Yule &rho;; the likelihood estimate sits below it on five of six data sets.
        Simulated at the real sample sizes, his constant-rate process (&sect;II) did not produce that gap in 1,000 runs
        for any set. The declining rate of Simon and Van Wormer (1963) is <em>consistent with</em> the gap and the
        head shape for three of the four author sets, at one or two adjacent points of a fixed grid, and none of the six settings
        matches Chem. This stage had a same-family code audit only.</p></article>
        <article class="card"><h3>The fit and its rivals</h3><p>Sichel&rsquo;s 1985 parameter for the chemistry
        authors, as reported by Bogachev et al. (2023), is reproduced to its five reported decimals (&theta; = 0.968759). The extended negative binomial beats the Yule on Chem by
        &Delta;AIC 66.6, failing a prediction made before the fit; for Chem the cutoff result agrees with
        Sichel (as reported) and Smolinsky (2015), and the comparison on the other author tables is new. For Physicists the Yule is <strong>not
        rejected</strong> by the 11-cell test (p = 0.064, 32 of 500 bootstrap replicates; simulation interval
        0.044&ndash;0.089), which does not show that it fits well: the supplementary KS test rejects it.</p></article>
        <article class="card"><h3>Word counts</h3><p>On three recounts of <em>Ulysses</em> from Project Gutenberg
        &mdash; not a replication of Hanley&rsquo;s 1937 index &mdash; Simon&rsquo;s equation (4.2) is not rejected
        by the 11-cell test. Only the product c&beta; is identified: 0.145&ndash;0.162, compatible with his
        c &asymp; 0.2 for suitable &beta;. For Eldridge, c&beta; is about 0.02 but (4.2) is rejected. &ldquo;&rho;
        about one&rdquo; holds on a binned log-log slope; by likelihood only narrowly for the recounts, and not for
        Eldridge.</p></article>
      </div>
      <div class="overview-caveats"><h3>What the headline does not mean</h3><ul>
        <li>The goodness-of-fit test is an iid parametric bootstrap of a newly fitted Yule, not a test of Simon&rsquo;s
        printed estimates or of his dependent growth process, and not the only reading of &ldquo;reasonably good&rdquo;.</li>
        <li>Not rejecting a model is not evidence that it fits; 0 of 500 exceedances bounds the bootstrap
        probability only below about 0.006.</li>
        <li>Most checks were fresh-context reviews by the same model family. One cross-family audit (Codex) re-derived the Stage 1 tail arithmetic from the page, the Stage 4 grade table from all 20,000 saved bootstrap replicates, the P7a and P20 fits and the 198 plotted values; it did not regenerate the bootstrap, certify every rival&rsquo;s optimizer, or check the Stage 3 simulations, which had a same-family code audit only.
        Shared blind spots of one family are not ruled out.</li>
        <li>The pre-registration&rsquo;s frozen versions are checkable by anyone; the freeze times are attested only by
        the implementing session&rsquo;s own log.</li>
      </ul></div>
      <div class="overview-actions">
        <button type="button" onclick="activateFromOverview('report')">Read the full report</button>
        <button type="button" class="secondary" onclick="activateFromOverview('score')">See the prediction scoreboard</button>
        <button type="button" class="secondary" onclick="activateFromOverview('figs')">See the figures</button>
      </div>
    </div>
  </section>
  <section id="tab-report" role="tabpanel" hidden>
    <div class="rp">
      <div class="rp-measure">
        <p class="rp-lede">The complete technical record, rendered verbatim from <code>REPORT.md</code> at build time
        (SHA-256 <code>__REPORTSHA__</code>&hellip;). Nothing on this tab is retyped by hand. Its headline numbers are
        re-derived from the committed results by <code>src/verify_report_numbers.py</code>, which requires each one
        verbatim in the report.</p>
        <div class="rp-toc"><strong>Contents</strong><ul>__TOC__</ul></div>
      </div>
      __REPORT__
    </div>
  </section>
  <section id="tab-score" role="tabpanel" hidden><h2>Prediction scoreboard</h2>
    <p class="note">Every prediction was frozen in <code>PREREGISTRATION.md</code> before the code of its stage was
    written. __NPRED__ predictions; __NFAIL__ failed, and the failures get the same prominence as the rest. Some were
    leads (results partly seen before the freeze); the report says which. The rows are parsed from the report&rsquo;s
    own prediction tables at build time.</p>
    __SCORE__
  </section>
  <section id="tab-figs" role="tabpanel" hidden><h2>Figures</h2>
    <p class="note">Built by <code>src/stage6.py</code> from committed files only; every plotted value is in
    <code>results/stage6-series.csv</code>, and a test checks the plotted printed and observed cells against the
    transcription.</p>
    <div class="fig" role="group" aria-label="Table 3 figure">__FIG3__</div>
    <p class="figcap">Table 3, the author counts. Top row: persons by number of contributions, log scale. Bottom row:
    each estimate divided by the observed count, so &ldquo;too high&rdquo; sits above the line at 1. The pooled
    11+ cell stands apart. Chicago&rsquo;s recipe series is Simon&rsquo;s own &rho;&#772; chain from the observed f(1);
    Econometrica&rsquo;s observed f(10) = 0 cannot show on a log axis.</p>
    <div class="fig narrow" role="group" aria-label="Table 2 figure">__FIG2__</div>
    <p class="figcap">Table 2, the word counts: words occurring once, twice and three times, with the same two rows.
    The Yule MLE is censored at 4+ for <em>Ulysses</em> (Hanley&rsquo;s figures via Zipf) and at 11+ for Eldridge.</p>
  </section>
  <section id="tab-data" role="tabpanel" hidden><h2>Data, custody, and what is not redistributed</h2>
    <p class="note">The paper, the 1957 reprint and the third-party scans are not redistributed. Every printed cell
    the analysis uses is transcribed with its page locator in <code>data/printed_tables.csv</code>; the source
    tables were double-entered (<code>data/sources/ADJUDICATION.md</code>). Each downloaded file is listed below
    with its SHA-256, so a reader who obtains the same file can confirm it is byte-identical. __NMAN__ files.</p>
    __CUSTODY__
  </section>
</main>
<footer>__FOOTER__</footer>
<script>
const TABS=[["overview","Overview"],["report","Full report"],["score","Scoreboard"],["figs","Figures"],["data","Data & custody"]];
function show(id){
  TABS.forEach(t=>{
    const panel=document.getElementById("tab-"+t[0]);
    const b=document.querySelector("button[data-tab='"+t[0]+"']");
    panel.hidden=(t[0]!==id);
    b.setAttribute("aria-selected",t[0]===id?"true":"false");
    b.tabIndex=t[0]===id?0:-1;});
}
function activateFromOverview(id){
  show(id);
  const panel=document.getElementById("tab-"+id);
  panel.tabIndex=-1;
  panel.focus();
}
function moveTab(ev,index){
  if(!["ArrowLeft","ArrowRight","Home","End"].includes(ev.key))return;
  ev.preventDefault();
  let next=index;
  if(ev.key==="Home")next=0;
  else if(ev.key==="End")next=TABS.length-1;
  else next=(index+(ev.key==="ArrowRight"?1:-1)+TABS.length)%TABS.length;
  show(TABS[next][0]);
  document.getElementById("navtab-"+TABS[next][0]).focus();
}
function bindReportContents(){
  document.querySelectorAll(".rp-toc a[href^='#']").forEach(link=>{
    link.addEventListener("click",()=>{
      const target=document.getElementById(link.hash.slice(1));
      if(!target)return;
      target.tabIndex=-1;
      requestAnimationFrame(()=>target.focus({preventScroll:true}));
    });
  });
}
function boot(){
  const nav=document.getElementById("nav");
  TABS.forEach((t,index)=>{const b=document.createElement("button");b.textContent=t[1];
    const panel=document.getElementById("tab-"+t[0]);
    b.id="navtab-"+t[0];
    b.setAttribute("role","tab");b.setAttribute("data-tab",t[0]);
    b.setAttribute("aria-selected","false");
    b.setAttribute("aria-controls","tab-"+t[0]);
    panel.setAttribute("aria-labelledby",b.id);
    b.onclick=()=>show(t[0]);
    b.onkeydown=ev=>moveTab(ev,index);
    nav.appendChild(b);});
  bindReportContents();
  show("overview");  // a cold reader lands on the concise synthesis
}
boot();
</script>
</body>
</html>
"""


def footer():
    cites = [
        "Simon, H. A. (1955). &ldquo;On a Class of Skew Distribution Functions.&rdquo; <em>Biometrika</em> <b>42</b>(3/4), "
        '425&ndash;440. <a href="https://doi.org/10.1093/biomet/42.3-4.425">doi:10.1093/biomet/42.3-4.425</a> &mdash; the paper under test.',
        "Simon, H. A. (1957). <em>Models of Man: Social and Rational</em>. New York: Wiley. Chapter 9 reprints the 1955 paper.",
        "Simon, H. A., &amp; Van Wormer, T. A. (1963). &ldquo;Some Monte Carlo Estimates of the Yule Distribution.&rdquo; "
        "<em>Behavioral Science</em> <b>8</b>, 203&ndash;210 &mdash; the declining-&alpha; account.",
        "Davis, H. T. (1941). <em>The Analysis of Economic Time Series</em>. Cowles Commission Monograph No. 6 &mdash; "
        "pp. 429&ndash;431, Simon&rsquo;s source for Table 3.",
        "Lotka, A. J. (1926). &ldquo;The Frequency Distribution of Scientific Productivity.&rdquo; <em>Journal of the "
        "Washington Academy of Sciences</em> <b>16</b>(12), 317&ndash;323.",
        "Eldridge, R. C. (1911). <em>Six Thousand Common English Words</em> &mdash; List 5.",
        "Zipf, G. K. (1949). <em>Human Behavior and the Principle of Least Effort</em>. Cambridge, MA: Addison-Wesley &mdash; "
        "the source of Hanley&rsquo;s <em>Ulysses</em> figures.",
        "Joyce, J. <em>Ulysses</em>. Project Gutenberg eBook #4300 "
        '(<a href="https://www.gutenberg.org/ebooks/4300">gutenberg.org/ebooks/4300</a>), the recount text.',
        "Engen, S. (1974). &ldquo;On Species Frequency Models.&rdquo; <em>Biometrika</em> <b>61</b>(2), 263&ndash;270 "
        "&mdash; the extended negative binomial.",
        "Sichel, H. S. (1985). &ldquo;A Bibliometric Distribution Which Really Works.&rdquo; <em>Journal of the American "
        "Society for Information Science</em> <b>36</b>(5), 314&ndash;321.",
        "Bogachev, Nuermaimaiti &amp; Voss (2023). &ldquo;Limit Shape of the Generalized Inverse "
        'Gaussian-Poisson Distribution.&rdquo; <a href="https://arxiv.org/abs/2303.08139">arXiv:2303.08139</a> '
        "&mdash; &sect;7.1 reports Sichel&rsquo;s fit.",
        "Smolinsky, L. (2015). &ldquo;Discrete power law with exponential cutoff and Lotka&rsquo;s Law.&rdquo; "
        '<a href="https://arxiv.org/abs/1512.08754">arXiv:1512.08754</a> &mdash; the zeta MLE on Lotka&rsquo;s chemistry '
        "table, and prior work on the cutoff comparison there.",
        "Leisen, Rossini &amp; Villa (2016). &ldquo;A Note on the Posterior Inference for the Yule-Simon "
        'Distribution.&rdquo; <a href="https://arxiv.org/abs/1604.07304">arXiv:1604.07304</a> &mdash; '
        "Table 2, the Yule &rho; for a Gutenberg <em>Ulysses</em>.",
        "Vuong, Q. H. (1989). &ldquo;Likelihood Ratio Tests for Model Selection and Non-Nested Hypotheses.&rdquo; "
        "<em>Econometrica</em> <b>57</b>(2), 307&ndash;333.",
        "Clauset, A., Shalizi, C. R., &amp; Newman, M. E. J. (2009). &ldquo;Power-Law Distributions in Empirical Data.&rdquo; "
        '<em>SIAM Review</em> <b>51</b>(4), 661&ndash;703. <a href="https://doi.org/10.1137/070710111">doi:10.1137/070710111</a>',
    ]
    return "".join([
        '<div class="footer-lead">Methods, credits and citations, kept below the findings.</div>',
        "<details><summary>Technical provenance, credits and citations</summary>",
        '<div class="fblock"><h3>Reproducibility</h3><div>The full pipeline is listed in '
        '<a href="' + BLOB_URL + 'README.md">README.md</a>; the tests run with <code>python -m pytest -q tests</code>. '
        "Stage seeds: 19551201 (Stage 3), 19551102 (Stage 4), 19551103 (Stage 5). The figures and this page carry no "
        "timestamp and rebuild byte-for-byte. Deviations from the frozen contract exist only as dated appended "
        'amendments and errata in <a href="' + BLOB_URL + 'PREREGISTRATION.md">PREREGISTRATION.md</a>.</div></div>',
        '<div class="fblock"><h3 id="credits">Credits</h3><div>Directed by Kenrin '
        '(<a href="https://github.com/kenrinzero">@kenrinzero</a>). <b>Claude (Claude Opus 5.5)</b> implemented every '
        "stage, the report, the figures and this page; fresh-context Claude subagents transcribed the source tables and "
        "audited each stage&rsquo;s code without seeing its results. <b>Codex (__CODEX__)</b> audited the finished package "
        'from a different model family. Who did what, and what each got wrong: <a href="' + BLOB_URL + 'CREDITS.md">CREDITS.md</a>.</div></div>',
        '<div class="fblock"><h3 id="citations">Citations</h3><ul class="cites">'
        + "".join("<li>%s</li>" % c for c in cites) + "</ul></div>",
        "</details>",
        '<div class="fineprint">&copy; 2026 kenrinzero &middot; code MIT (<a href="' + BLOB_URL + 'LICENSE">LICENSE</a>) '
        '&middot; documents CC-BY-4.0 (<a href="' + BLOB_URL + 'REPORT-LICENSE">REPORT-LICENSE</a>) &middot; source '
        "material under its own terms, not ours to relicense &middot; built by <code>src/build_reader.py</code>; "
        "deterministic, self-contained (no network, no external assets &mdash; the links are references, not loads).</div>",
    ])


def assert_self_contained_html(html):
    """Reject every loading surface except the exact inert data-URI favicon."""
    for link in re.findall(r"<link\b[^>]*>", html, re.I):
        assert link == SELF_CONTAINED_FAVICON, "external reference found: %s" % link
    for pat in (r"<script[^>]+src=", r"@import", r"url\(\s*['\"]?https?:", r"<img\b", r"<iframe\b",
                r"fetch\(", r"XMLHttpRequest", r"<image\b"):
        assert not re.search(pat, html, re.I), "external reference found: %s" % pat


def build():
    report_html, toc = render_report_md(REPORT)
    rows = scoreboard()
    n_fail, score = render_scoreboard(rows)
    n_man, custody = custody_table()
    model = codex_model()
    html = (HTML_TEMPLATE
            .replace("__FOOTER__", footer())
            .replace("__REPORT__", report_html)
            .replace("__TOC__", toc)
            .replace("__REPORTSHA__", hashlib.sha256(REPORT.read_bytes()).hexdigest()[:16])
            .replace("__SCORE__", score)
            .replace("__NPRED__", str(len(rows)))
            .replace("__NFAIL__", str(n_fail))
            .replace("__FIG3__", inline_svg(RES / "stage6-table3.svg", "t3"))
            .replace("__FIG2__", inline_svg(RES / "stage6-table2.svg", "t2"))
            .replace("__CUSTODY__", custody)
            .replace("__NMAN__", str(n_man))
            .replace("__REPO__", REPO_URL)
            .replace("__CODEX__", esc(model)))
    for tok in re.findall(r"__[A-Z0-9]+__", html):
        raise AssertionError("unsubstituted template placeholder: %s" % tok)
    assert html.count(SELF_CONTAINED_FAVICON) == 1
    assert_self_contained_html(html)
    assert "\r" not in html
    return html, len(rows), n_fail


def main():
    html, n, n_fail = build()
    DOCS_INDEX.parent.mkdir(parents=True, exist_ok=True)
    for target in (OUT, DOCS_INDEX):
        with io.open(target, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(html)
    (ROOT / "docs" / ".nojekyll").write_bytes(b"")
    b = OUT.read_bytes()
    assert DOCS_INDEX.read_bytes() == b
    print("wrote %s and %s (byte-identical); %d bytes, sha256 %s; %d predictions, %d failed"
          % (OUT.relative_to(ROOT), DOCS_INDEX.relative_to(ROOT), len(b), hashlib.sha256(b).hexdigest()[:16], n, n_fail))
    return 0


if __name__ == "__main__":
    sys.exit(main())

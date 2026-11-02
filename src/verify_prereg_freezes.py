"""Rebuild every frozen version of PREREGISTRATION.md from the current file and check its hash.

The contract is append-only, so each frozen version is a prefix of today's file. The
one exception is Step 0: its "## Amendments" section held the line "(none)", which
Amendment 1 replaced; the rebuild restores that line.

What this proves: the text of each frozen version is exactly what the recorded hash
says, and nothing above an amendment was edited afterwards. What it cannot prove: when
each hash was recorded. The times below come from the implementing session's own log,
which is private; the public git history begins at publication.

    python src/verify_prereg_freezes.py     # writes results/prereg-freezes.txt
"""
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREREG = ROOT / "PREREGISTRATION.md"
OUTFILE = ROOT / "results" / "prereg-freezes.txt"

# (version, SHA-256 recorded at freeze, freeze time UTC, first code of that stage UTC, the code)
FREEZES = [
    ("Step 0", "c089b3a03a389ece6bf72d434d3df593d19f66039da2cb79585b76ceaf66ae1c",
     "2026-11-01T21:02:34Z", "2026-11-01T21:03:25Z", "src/recipe.py"),
    ("Amendment 1", "aa1f7e35352766daac8bd17ca8349b39788f381fd591aa4d7da85cfe3c7f48b4",
     "2026-11-01T21:23:56Z", "2026-11-01T21:25:27Z", "src/stage2.py"),
    ("Amendment 2", "376d2e99723f0fbe5a0726eca953feb650fb4a8139cdb694ac00b6850bd14e35",
     "2026-11-01T21:31:51Z", "2026-11-01T21:32:58Z", "src/stage3.py"),
    ("Amendment 3", "77d4dd9280dfdba35cde467cf030cf658d075e2b6315842802c7f46b04e12548",
     "2026-11-01T23:10:42Z", "2026-11-01T23:13:57Z", "src/stage4.py"),
    ("Amendment 4", "3e9b615c2179283c20a39d509856465402106e21ee21f7a3c7a1018d78608e12",
     "2026-11-01T23:49:08Z", "2026-11-01T23:49:54Z", "src/stage5.py"),
    ("Erratum 1", "7cdac4227a3a4231b3034414b699cc671bee740165f01dbcfccf7933433fe91a",
     "2026-11-02T00:22:06Z", "", ""),
    ("Erratum 2", "b81676c9ce9ff632eb87dfe6c5d029e31131be6f29a89c4db37e623dbf399686",
     "2026-11-02T00:38:57Z", "", ""),
    ("Erratum 3", "ccd3d9538509440af07d49552e9d9686ba7670f2978f11f759ee4392aeba0068",
     "2026-11-02T00:59:00Z", "", ""),
]


def versions():
    b = PREREG.read_bytes()
    # (version, heading that follows it, bytes to drop before that heading). The amendments
    # were appended with one blank line before the next heading, the errata with none.
    bounds = [("Amendment 1", b"### Amendment 2", 1), ("Amendment 2", b"### Amendment 3", 1),
              ("Amendment 3", b"### Amendment 4", 1), ("Amendment 4", b"### Erratum 1", 1),
              ("Erratum 1", b"### Erratum 2", 0), ("Erratum 2", b"### Erratum 3", 0),
              ("Erratum 3", b"### Erratum 4", 0)]
    out = {"Step 0": b[:b.index(b"### Amendment 1")] + b"(none)\n"}
    for name, head, drop in bounds:
        i = b.find(head)
        out[name] = b if i < 0 else b[:i - drop]
    return out


def main():
    v = versions()
    lines, bad = [], 0
    for name, sha, frozen, first_code, code in FREEZES:
        got = hashlib.sha256(v[name]).hexdigest()
        ok = got == sha
        bad += not ok
        after = f"; first code ({code}) {first_code}" if code else ""
        lines.append(f"{name}: {'OK' if ok else 'MISMATCH'} sha256 {sha} (rebuilt {got[:16]}...); frozen {frozen}{after}")
    lines.append(f"{len(FREEZES)} versions, {bad} mismatches. Hashes are checkable by anyone; the times come from "
                 "the implementing session's private log and are not externally verifiable.")
    body = "\n".join(lines) + "\n"
    OUTFILE.write_bytes(body.encode("utf-8"))
    sys.stdout.buffer.write(body.encode("utf-8"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

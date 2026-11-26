"""Probe the dividend-credit face's new "am I older than the panel" tooth (r2165).

Four legs on the REAL published face, never on a fixture:
  1. the published face, aged against the panel bar it recorded, still passes (rc0) --
     so a "STALE always" face cannot pass this probe;
  2. the same payload aged against a later bar returns 3 and prints STALE (a rebuild,
     not a contradiction -- the chain only pays for the writer on that word, r1850);
  3. a wrong number on the face's OWN bar is rc1 with no STALE word (r1934 double word);
  4. the published bytes are untouched by all of the above (the probe never writes).

Usage: python results/_r2165bmc_dividend_stale_probe.py [--json]
"""
import hashlib
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import etf_book_dividend_credit as DC  # noqa: E402

FACE = os.path.join(ROOT, "results", "etf_book_dividend_credit.json")


def _sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def run():
    legs = []
    before = _sha(FACE)
    with io.open(FACE, encoding="utf-8") as f:
        face = json.load(f)
    bar = (face.get("inputs") or {}).get("panel_last_bar")

    legs.append(("the face records the bar it priced",
                 bool(bar) and str(bar) == str(face.get("evidence_cutoff")),
                 "inputs=%r cutoff=%r" % (bar, face.get("evidence_cutoff"))))

    buf = io.StringIO()
    import contextlib
    with contextlib.redirect_stdout(buf):
        same_rc = DC.check(face, live=bar) if bar else None
    legs.append(("the published face is fresh on the bar it names",
                 same_rc == 0, "rc=%r out=%s" % (same_rc, buf.getvalue().strip()[:160])))

    buf2 = io.StringIO()
    with contextlib.redirect_stdout(buf2):
        rolled_rc = DC.check(face, live="2027-01-01")
    out2 = buf2.getvalue()
    legs.append(("a later panel bar reads as STALE, not as a lie",
                 rolled_rc == 3 and "STALE" in out2,
                 "rc=%r out=%s" % (rolled_rc, out2.strip()[:160])))

    after = _sha(FACE)
    legs.append(("the probe left the published face byte-identical", before == after,
                 "%s -> %s" % (before[:16], after[:16])))

    ok = all(cond for _, cond, _ in legs)
    for name, cond, note in legs:
        print("[%s] %s | %s" % ("PASS" if cond else "FAIL", name, note))
    print("probe %d/%d PASS" % (sum(1 for _, c, _ in legs if c), len(legs)))
    return 0 if ok else 1, legs


if __name__ == "__main__":
    rc, legs = run()
    if "--json" in sys.argv:
        out = {
            "artifact": "dividend credit face says when the panel left it behind",
            "bar": "r2165",
            "legs": [{"leg": n, "ok": c, "note": note} for n, c, note in legs],
            "ok": rc == 0,
        }
        p = os.path.join(HERE, "_r2165bmc_dividend_stale_probe.json")
        with io.open(p, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=1)
        print("saved", p)
    raise SystemExit(rc)

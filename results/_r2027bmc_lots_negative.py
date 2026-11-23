"""Negative control for r2027's order ticket (scripts/astock_veto_hedge_lots.py).

Every leg breaks one thing, calls the real check(), asserts the exact wording of the
verdict (STALE vs CHECK FAILED -- they are different diagnoses), then restores and
proves the published face is still green and byte-identical.

Run:  python results/_r2027bmc_lots_negative.py
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import astock_veto_hedge_lots as M  # noqa: E402

PASS = []
FAIL = []


def leg(name, cond, detail=""):
    if cond:
        PASS.append(name)
    else:
        FAIL.append("%s %s" % (name, detail))


def sha(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def capture(fn):
    """Run a callable and return (rc, stdout)."""
    import io
    import contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = fn()
    return rc, buf.getvalue()


def mutate_face(tmp, key_path, value):
    face = json.load(open(M.OUT_JSON, encoding="utf-8"))
    node = face
    for k in key_path[:-1]:
        node = node[k]
    node[key_path[-1]] = value
    path = os.path.join(tmp, "face.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
    return path


def main() -> int:
    json_sha = sha(M.OUT_JSON)
    md_sha = sha(M.OUT_MD)
    tmp = tempfile.mkdtemp(prefix="r2027lots_")

    # 0. as published
    rc, out = capture(M.check)
    leg("as published -> rc0", rc == 0, out.strip())
    leg("as published -> says CHECK OK", "CHECK OK" in out, out.strip())

    # 1. readings moved, one at a time
    cases = [
        ("beta", ["beta"], 0.95),
        ("lots needed", ["ladders", "1000000", "etf", "lots_needed"], 1234.5),
        ("beta achieved", ["ladders", "3000000", "im", "round", "beta_achieved"], 0.5),
        ("margin cny", ["ladders", "1000000", "etf", "margin", "0.80", "margin_cny"], 1.0),
        ("committed cny", ["ladders", "1000000", "etf", "margin", "0.80", "committed_cny"], 1.0),
        ("funding efficiency", ["funding_efficiency", "1000000", "im_0.12"], 9.99),
        ("granularity ratio", ["granularity", "ratio_one_contract_over_one_lot"], 2.0),
        ("neutral capital", ["granularity", "exact_neutral_capital", "1", "capital_cny"], 1.0),
        ("carry", ["carry", "etf_roll_cost_per_year_on_capital"], 0.0),
        ("one lot price", ["prices", "etf", "one_lot_notional"], 999.0),
        ("verdict", ["verdict"], "THE_ROUNDING_IS_FREE_ON_BOTH_ARMS"),
    ]
    for name, path, value in cases:
        p = mutate_face(tmp, path, value)
        rc, out = capture(lambda p=p: M.check(json_path=p))
        leg("%s -> rc3 CHECK FAILED" % name,
            rc == 3 and "CHECK FAILED" in out and "STALE" not in out, out.strip()[:160])

    # 2. the page edited by hand (the face is right, the page is not)
    md_lines = open(M.OUT_MD, encoding="utf-8").read().split("\n")
    tampered = os.path.join(tmp, "page.md")
    body = "\n".join(
        ["# The order ticket: what 90.13% of the book is in lots"] + md_lines[1:])
    with open(tampered, "w", encoding="utf-8") as fh:
        fh.write(body.replace("1,109,120", "1,109,121", 1))
    rc, out = capture(lambda: M.check(md_path=tampered))
    leg("hand-edited page -> rc3 and names the page",
        rc == 3 and "page is not the rendered face" in out, out.strip()[:160])

    # 3. an input moved: the parent face (STALE, not CHECK FAILED)
    orig_parent = M.PARENT
    try:
        moved = json.load(open(M.PARENT, encoding="utf-8"))
        moved["default"]["beta"] = 0.9123
        moved_parent = os.path.join(tmp, "parent.json")
        with open(moved_parent, "w", encoding="utf-8") as fh:
            json.dump(moved, fh, ensure_ascii=False, indent=1, sort_keys=True)
        M.PARENT = moved_parent
        rc, out = capture(M.check)
        leg("parent moved -> rc3 STALE", rc == 3 and "STALE" in out and "CHECK FAILED" not in out,
            out.strip()[:160])
    finally:
        M.PARENT = orig_parent

    # 4. an input moved: the price panel (STALE, not CHECK FAILED)
    orig_csv = M.ETF_CSV
    try:
        src = open(M.ETF_CSV, encoding="utf-8").read().rstrip("\n")
        last = src.split("\n")[-1].split(",")
        bumped = list(last)
        bumped[4] = "%.4f" % (float(last[4]) + 0.01)
        extra = os.path.join(tmp, "etf.csv")
        with open(extra, "w", encoding="utf-8") as fh:
            fh.write(src + "\n" + ",".join(bumped) + "\n")
        M.ETF_CSV = extra
        rc, out = capture(M.check)
        leg("panel moved -> rc3 STALE", rc == 3 and "STALE" in out and "CHECK FAILED" not in out,
            out.strip()[:160])
    finally:
        M.ETF_CSV = orig_csv

    # 5. missing files do not crash
    rc, out = capture(lambda: M.check(json_path=os.path.join(tmp, "nope.json")))
    leg("missing face -> rc3, no traceback",
        rc == 3 and "CHECK FAILED" in out and "Traceback" not in out, out.strip()[:160])
    rc, out = capture(lambda: M.check(md_path=os.path.join(tmp, "nope.md")))
    leg("missing page -> rc3, no traceback",
        rc == 3 and "Traceback" not in out, out.strip()[:160])

    # 6. an unreadable parent is STALE, not a crash
    orig_parent = M.PARENT
    try:
        junk = os.path.join(tmp, "junk.json")
        open(junk, "w", encoding="utf-8").write("{not json")
        M.PARENT = junk
        rc, out = capture(M.check)
        leg("unreadable parent -> STALE, no traceback",
            rc == 3 and "STALE" in out and "Traceback" not in out, out.strip()[:160])
    finally:
        M.PARENT = orig_parent

    # 7. the recovered face is untouched and still green
    leg("the published face is byte-identical after the run",
        sha(M.OUT_JSON) == json_sha and sha(M.OUT_MD) == md_sha)
    rc, out = capture(M.check)
    leg("the published face is still green after the run", rc == 0, out.strip()[:160])

    shutil.rmtree(tmp, ignore_errors=True)

    print("negative control %d/%d PASS" % (len(PASS), len(PASS) + len(FAIL)))
    for f in FAIL:
        print("  - FAIL %s" % f)
    return 0 if not FAIL else 1


if __name__ == "__main__":
    sys.exit(main())

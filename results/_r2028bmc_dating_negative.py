"""Negative control for results/astock_veto_hedge_dating.json (r2028 bm-c).

Proves the face's `check` can actually say no, in the two shapes that matter:
  1. a number that disagrees with its own inputs -> CHECK FAILED, and *not* the word
     STALE (a defect must not be excused as drift, r1934);
  2. an input/derived date that moved -> STALE, so the chain pays to re-derive;
  3. a page that lost the verdict -> CHECK FAILED.

Nothing here touches the real face: every case runs on a temp copy.
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import astock_veto_hedge_dating as face  # noqa: E402


def run_case(name, poison, expect_in, expect_not_in):
    tmp = tempfile.mkdtemp(prefix="neg_")
    jp = os.path.join(tmp, "face.json")
    mp = os.path.join(tmp, "page.md")
    shutil.copy(face.OUT_JSON, jp)
    shutil.copy(face.OUT_MD, mp)
    try:
        data = json.load(open(jp, encoding="utf-8"))
        page = open(mp, encoding="utf-8").read()
        data, page = poison(data, page)
        json.dump(data, open(jp, "w", encoding="utf-8"))
        open(mp, "w", encoding="utf-8").write(page)
        rc, text = face._check_capture(jp, mp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    ok = (rc == 3 and expect_in in text and (expect_not_in is None or expect_not_in not in text))
    print("%s %s | rc=%d | %s" % ("PASS" if ok else "FAIL", name, rc,
                                  text.strip().splitlines()[0] if text.strip() else ""))
    return ok


def p_number(data, page):
    data["ladder"][0]["at_price_date"]["needed"] = float(
        data["ladder"][0]["at_price_date"]["needed"]) * 1.05
    return data, page


def p_date(data, page):
    data["dates"]["book"] = "1999-01-01"
    return data, page


def p_page(data, page):
    return data, page.replace("`%s`" % data["verdict"], "`NOT_THE_VERDICT`")


def p_verdict(data, page):
    data["verdict"] = "DATING_IS_IMMATERIAL_AT_THE_LOT_LEVEL"
    return data, page


def main() -> int:
    cases = [
        run_case("a number that disagrees with its inputs", p_number,
                 "CHECK FAILED", "STALE"),
        run_case("a date that moved", p_date, "STALE", None),
        run_case("a page that lost the verdict", p_page, "CHECK FAILED", None),
        run_case("a verdict that was flipped", p_verdict, "CHECK FAILED", None),
    ]
    print("negative control %d/%d" % (sum(cases), len(cases)))
    return 0 if all(cases) else 1


if __name__ == "__main__":
    sys.exit(main())

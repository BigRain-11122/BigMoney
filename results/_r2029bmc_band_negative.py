"""Negative control for results/astock_veto_hedge_band.json (r2029 bm-c).

Proves the face's `check` can actually say no, in the three shapes that matter
(r1934 / r1850 family):
  1. a number that disagrees with its own inputs -> CHECK FAILED, and *not* the word
     STALE (a defect must not be excused as drift);
  2. an upstream face that moved one step -> STALE, so the chain pays to re-derive,
     and *not* CHECK FAILED (drift must not be sold as a defect);
  3. a page that lost a verdict word -> CHECK FAILED.

Plus the two states that are easy to get wrong: a missing face is STALE (not ok), and
after every poison case the published face on disk is still byte-identical and green.

Nothing here touches the real face: every case runs on a temp copy.
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

import astock_veto_hedge_band as face  # noqa: E402


def _sha(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def _load(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def run_case(name, poison, expect_in, expect_not_in):
    tmp = tempfile.mkdtemp(prefix="neg_")
    jp = os.path.join(tmp, "face.json")
    mp = os.path.join(tmp, "page.md")
    shutil.copy(face.OUT_JSON, jp)
    shutil.copy(face.OUT_MD, mp)
    try:
        data = _load(jp)
        with open(mp, encoding="utf-8") as fh:
            page = fh.read()
        data, page = poison(data, page)
        with open(jp, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False)
        with open(mp, "w", encoding="utf-8") as fh:
            fh.write(page)
        rc, text = face._check_capture(jp, mp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    ok = (rc == 3 and expect_in in text
          and (expect_not_in is None or expect_not_in not in text))
    head = text.strip().splitlines()[0] if text.strip() else ""
    print("%s %s | rc=%d | %s" % ("PASS" if ok else "FAIL", name, rc, head))
    return ok


# --- poisons: defect shapes (CHECK FAILED, never STALE) -----------------------
def p_lots(data, page):
    """One lot count no longer follows from beta, capital and price."""
    data["ladder"][0]["lots_needed"] = float(data["ladder"][0]["lots_needed"]) * 1.05
    return data, page


def p_se(data, page):
    """The standard error is the whole subject of this face -- poison it."""
    data["fit"]["etf_in_sample"]["se_beta"] = (
        float(data["fit"]["etf_in_sample"]["se_beta"]) * 0.5)
    return data, page


def p_band(data, page):
    """A band edge that no longer equals its own beta times the lot size."""
    data["ladder"][2]["lots_band_high"] = float(data["ladder"][2]["lots_band_high"]) + 100.0
    return data, page


def p_risk_vol(data, page):
    """The cost-of-being-wrong reading, out of line with its own beta."""
    data["risk"]["rows"][1]["residual_annual_vol"] = (
        float(data["risk"]["rows"][1]["residual_annual_vol"]) + 0.05)
    return data, page


def p_verdict(data, page):
    """The band verdict flipped without its arithmetic moving."""
    data["verdict"] = "THE_DATING_IS_WIDER_THAN_THE_BAND"
    return data, page


def p_risk_verdict(data, page):
    data["risk_verdict"] = "BETA_ERROR_COSTS_REAL_VOLATILITY"
    return data, page


def p_page_band(data, page):
    return data, page.replace("`%s`" % data["verdict"], "`NOT_THE_VERDICT`")


def p_page_risk(data, page):
    return data, page.replace("`%s`" % data["risk_verdict"], "`NOT_THE_RISK_VERDICT`")


# --- poisons: drift shapes (STALE, never CHECK FAILED) ------------------------
def p_parent(data, page):
    """An upstream face moved one step: that is drift, repaired by `run`."""
    data["parents"]["beta"]["content_sha256"] = "0" * 64
    return data, page


def p_csv(data, page):
    """A price panel moved: also drift, and this face must say so."""
    data["parents"]["etf_csv"]["file_sha256"] = "0" * 64
    return data, page


def main() -> int:
    before_json, before_md = _sha(face.OUT_JSON), _sha(face.OUT_MD)

    cases = [
        run_case("a lot count that disagrees with its inputs", p_lots,
                 "CHECK FAILED", "STALE"),
        run_case("a standard error out of line with its fit", p_se,
                 "CHECK FAILED", "STALE"),
        run_case("a band edge out of line with its beta", p_band,
                 "CHECK FAILED", "STALE"),
        run_case("a residual-vol reading out of line", p_risk_vol,
                 "CHECK FAILED", "STALE"),
        run_case("a band verdict flipped", p_verdict, "CHECK FAILED", "STALE"),
        run_case("a risk verdict flipped", p_risk_verdict, "CHECK FAILED", "STALE"),
        run_case("a page that lost the band verdict", p_page_band,
                 "CHECK FAILED", None),
        run_case("a page that lost the risk verdict", p_page_risk,
                 "CHECK FAILED", None),
        run_case("an upstream face that moved", p_parent, "STALE", "CHECK FAILED"),
        run_case("a price panel that moved", p_csv, "STALE", "CHECK FAILED"),
    ]

    # a missing face is STALE, not a pass
    tmp = tempfile.mkdtemp(prefix="neg_missing_")
    try:
        rc, text = face._check_capture(os.path.join(tmp, "nope.json"),
                                       os.path.join(tmp, "nope.md"))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    ok_missing = (rc == 3 and "STALE" in text and "CHECK FAILED" not in text)
    print("%s a missing face | rc=%d | %s"
          % ("PASS" if ok_missing else "FAIL", rc,
             text.strip().splitlines()[0] if text.strip() else ""))
    cases.append(ok_missing)

    # the published face itself: untouched, and still green
    ok_bytes = _sha(face.OUT_JSON) == before_json and _sha(face.OUT_MD) == before_md
    print("%s the published face is byte-identical after the poison cases" %
          ("PASS" if ok_bytes else "FAIL"))
    cases.append(ok_bytes)

    rc, _ = face._check_capture(face.OUT_JSON, face.OUT_MD)
    ok_green = rc == 0
    print("%s the published face still passes its own check (rc=%d)"
          % ("PASS" if ok_green else "FAIL", rc))
    cases.append(ok_green)

    print("negative control %d/%d" % (sum(cases), len(cases)))
    return 0 if all(cases) else 1


if __name__ == "__main__":
    sys.exit(main())

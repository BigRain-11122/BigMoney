# -*- coding: utf-8 -*-
"""r2046 negative control for cash_shelf_year_by_year.

Proves each guard fails on a poisoned input instead of staying green:
  N1 healthy copy passes check
  N2 a hand-edited per-year extra -> rc1 and the message names code/year/field, no STALE
  N3 a hand-edited window extra    -> rc1 names the field
  N4 one byte of an upstream face  -> rc3 STALE (and never the word CHECK FAILED)
  N5 disabling this face's flip neutralisation moves 511360's window extra back to the
     contaminated line (the flip handling is load-bearing, not decoration)
  N6 widening the upstream budget in memory flips the verdict (the verdict reads the
     upstream adoption block -- it does not carry its own budget)
  N7 a missing face reads as STALE, not as a crash
  N8 every published file is byte-identical after the run

Usage: python results/_r2046bmc_year_negative.py
"""
import hashlib
import io
import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import cash_shelf_year_by_year as CY  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")

REAL = {
    "FACE": os.path.join(ROOT, CY.FACE),
    "PAYBACK": os.path.join(ROOT, CY.PAYBACK_FACE),
    "SIZE": os.path.join(ROOT, CY.SIZE_FACE),
}
PUBLISHED = sorted(set(REAL.values()) | {os.path.join(ROOT, CY.DOC)})


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def run_check(face_path, payback_path, size_path):
    CY.FACE = face_path
    CY.PAYBACK_FACE = payback_path
    CY.SIZE_FACE = size_path
    buf = io.StringIO()
    old = sys.stdout
    sys.stdout = buf
    try:
        rc = CY.cmd_check()
    finally:
        sys.stdout = old
        CY.FACE = "results/cash_shelf_year_by_year.json"
        CY.PAYBACK_FACE = "results/cash_shelf_wait_payback.json"
        CY.SIZE_FACE = "results/cb_parking_shelf_at_size.json"
    return rc, buf.getvalue()


def main():
    legs = []

    def leg(name, ok, detail=""):
        legs.append((name, bool(ok), detail))

    before = {p: sha(p) for p in PUBLISHED if os.path.exists(p)}
    tmp = tempfile.mkdtemp(prefix="r2046neg_")

    # working copies
    face_p = os.path.join(tmp, "face.json")
    pay_p = os.path.join(tmp, "payback.json")
    size_p = os.path.join(tmp, "size.json")
    shutil.copyfile(REAL["FACE"], face_p)
    shutil.copyfile(REAL["PAYBACK"], pay_p)
    shutil.copyfile(REAL["SIZE"], size_p)

    # N1 healthy copy
    rc, out = run_check(face_p, pay_p, size_p)
    leg("N1 a healthy copy passes check", rc == 0, "rc=%s %s" % (rc, out[-200:]))

    # N2 edited per-year extra
    d = json.load(io.open(face_p, encoding="utf-8"))
    row = [r for r in d["rows"] if r["code"] == "511360"][0]
    year = sorted(row["years"])[1]
    row["years"][year]["extra_pp"] = round(row["years"][year]["extra_pp"] + 0.05, 4)
    bad_p = os.path.join(tmp, "face_bad_year.json")
    io.open(bad_p, "w", encoding="utf-8", newline="\n").write(json.dumps(d, ensure_ascii=False, indent=1))
    rc, out = run_check(bad_p, pay_p, size_p)
    leg("N2 edited per-year extra -> rc1", rc == 1, "rc=%s" % rc)
    leg("N2 message names code/year/field and does not say STALE",
        ("511360" in out and year in out and "extra_pp" in out and "STALE" not in out), out[-220:])

    # N3 edited window extra
    d2 = json.load(io.open(face_p, encoding="utf-8"))
    [r for r in d2["rows"] if r["code"] == "511360"][0]["window_extra_cny"] += 10.0
    bad2 = os.path.join(tmp, "face_bad_window.json")
    io.open(bad2, "w", encoding="utf-8", newline="\n").write(json.dumps(d2, ensure_ascii=False, indent=1))
    rc, out = run_check(bad2, pay_p, size_p)
    leg("N3 edited window extra -> rc1 naming window_extra_cny",
        rc == 1 and "window_extra_cny" in out, "rc=%s %s" % (rc, out[-160:]))

    # N4 upstream byte changed
    with open(pay_p, "ab") as f:
        f.write(b"\n")
    rc, out = run_check(face_p, pay_p, size_p)
    leg("N4 upstream byte change -> rc3 STALE without CHECK FAILED",
        rc == 3 and "STALE" in out and "CHECK FAILED" not in out, "rc=%s %s" % (rc, out[-160:]))
    shutil.copyfile(REAL["PAYBACK"], pay_p)

    # N5 flip neutralisation is load-bearing
    clean = CY.build()
    w360 = [r for r in clean["rows"] if r["code"] == "511360"][0]["window_extra_cny"]
    flip_effect = [r for r in clean["rows"] if r["code"] == "511360"][0]["quote_audit"]["flip_effect_pp_per_year"]
    orig = CY.find_flip_pairs
    CY.find_flip_pairs = lambda px: []
    try:
        dirty = CY.build()
    finally:
        CY.find_flip_pairs = orig
    w360_dirty = [r for r in dirty["rows"] if r["code"] == "511360"][0]["window_extra_cny"]
    ticket = clean["headline"]["ticket_cash_cny"]
    want = abs(flip_effect) / 100.0 * ticket
    leg("N5 without neutralisation 511360's extra rises by the flip's value",
        w360_dirty > w360 and abs((w360_dirty - w360) - want) < 0.05 * max(want, 1e-9),
        "clean=%.2f dirty=%.2f want_delta=%.2f got=%.2f" % (w360, w360_dirty, want, w360_dirty - w360))

    # N6 the verdict reads the upstream budget
    dp = json.load(io.open(REAL["PAYBACK"], encoding="utf-8"))
    dp["adoption"]["budget_sessions"] = 70
    pay_wide = os.path.join(tmp, "payback_wide.json")
    io.open(pay_wide, "w", encoding="utf-8", newline="\n").write(json.dumps(dp, ensure_ascii=False, indent=1))
    face_wide = os.path.join(tmp, "face_wide.json")
    CY.FACE = face_wide
    CY.PAYBACK_FACE = pay_wide
    CY.SIZE_FACE = REAL["SIZE"]
    try:
        wide_face = CY.build()
    finally:
        CY.FACE = "results/cash_shelf_year_by_year.json"
        CY.PAYBACK_FACE = "results/cash_shelf_wait_payback.json"
        CY.SIZE_FACE = "results/cb_parking_shelf_at_size.json"
    io.open(face_wide, "w", encoding="utf-8", newline="\n").write(
        json.dumps(wide_face, ensure_ascii=False, indent=1))
    wide = json.load(io.open(face_wide, encoding="utf-8"))
    base_v = [r["verdict"] for r in json.load(io.open(REAL["FACE"], encoding="utf-8"))["rows"]
              if r["code"] == "511360"][0]
    wide_v = [r["verdict"] for r in wide["rows"] if r["code"] == "511360"][0]
    leg("N6 a 70-session budget moves 511360 to every-full-year",
        wide_v == ["WAIT_FITS_IN_EVERY_FULL_YEAR"] and base_v != wide_v,
        "base=%s wide=%s" % (base_v, wide_v))

    # N7 missing face
    rc, out = run_check(os.path.join(tmp, "nope.json"), pay_p, size_p)
    leg("N7 a missing face reads STALE, no traceback",
        rc == 3 and "STALE" in out, "rc=%s %s" % (rc, out[-140:]))

    # N8 published files untouched
    after = {p: sha(p) for p in PUBLISHED if os.path.exists(p)}
    leg("N8 every published file is byte-identical after the run", before == after,
        str([p for p in before if before.get(p) != after.get(p)]))

    shutil.rmtree(tmp, ignore_errors=True)
    passed = sum(1 for _, ok, _ in legs if ok)
    for name, ok, detail in legs:
        print(("PASS " if ok else "FAIL ") + name + (("  [" + detail + "]") if detail and not ok else ""))
    print("NEGATIVE %d/%d" % (passed, len(legs)))
    return 0 if passed == len(legs) else 1


if __name__ == "__main__":
    sys.exit(main())

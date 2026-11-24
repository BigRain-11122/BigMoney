#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""negative control for cb_parking_bakeoff -- prove the check can say no

Every leg plants one defect in a COPY and asserts that `check()` notices it with the
right word: a moved input is STALE (so the S6 chain pays to rebuild), a self-
contradiction is CHECK FAILED (so it is a defect, not drift).  The published files
are never touched; the last leg re-hashes them to prove it.

Run:  python results/_r2040bmc_parking_negative.py
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

import cb_parking_bakeoff as S  # noqa: E402

REAL_JSON = os.path.join(ROOT, "results", "cb_parking_bakeoff.json")
REAL_MD = os.path.join(ROOT, "research", "CB_PARKING_BAKEOFF.md")

errs = []
legs = [0]


def chk(cond, msg):
    legs[0] += 1
    if not cond:
        errs.append(msg)


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def load(p):
    with io.open(p, encoding="utf-8") as f:
        return json.load(f)


def dump(obj, p):
    with io.open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)


def rehash(face):
    face["content_sha256"] = S._content_sha(
        {k: v for k, v in face.items() if k not in ("content_sha256", "elapsed_sec", "generated")})
    return face


def run_check(tmpdir, face=None, md=None):
    jp = os.path.join(tmpdir, "face.json")
    mp = os.path.join(tmpdir, "page.md")
    if face is None:
        shutil.copyfile(REAL_JSON, jp)
    else:
        dump(face, jp)
    if md is None:
        shutil.copyfile(REAL_MD, mp)
    else:
        with io.open(mp, "w", encoding="utf-8") as f:
            f.write(md)
    buf = io.StringIO()
    out, err = sys.stdout, sys.stderr
    sys.stdout = buf
    try:
        rc = S.check(jp, mp)
    finally:
        sys.stdout = out
    return rc, buf.getvalue()


def main():
    if not (os.path.exists(REAL_JSON) and os.path.exists(REAL_MD)):
        print("NEGATIVE SKIP: the face has not been built yet")
        return 2

    before = {p: sha(p) for p in (REAL_JSON, REAL_MD)}
    tmp = tempfile.mkdtemp(prefix="cbpark_neg_")

    # L1 a healthy copy must pass
    rc, out = run_check(tmp)
    chk(rc == 0 and "CHECK OK" in out, "a healthy copy must pass (rc=%s, %r)" % (rc, out[:120]))

    # L2 a moved input is STALE, and must not say CHECK FAILED
    face = load(REAL_JSON)
    face["data_sha"]["cb_panel"] = "0" * 64
    rc, out = run_check(tmp, face=rehash(face))
    chk(rc == 3 and "STALE" in out and "CHECK FAILED" not in out,
        "a moved parent face must read STALE only (rc=%s, %r)" % (rc, out[:120]))

    # L3 a patched headline number is a defect, and must not read as drift
    face = load(REAL_JSON)
    face["headline"]["repo_net_pct"] = round(face["headline"]["repo_net_pct"] + 0.5, 4)
    rc, out = run_check(tmp, face=rehash(face))
    chk(rc == 3 and "CHECK FAILED" in out and "STALE" not in out,
        "a patched headline must read CHECK FAILED only (rc=%s, %r)" % (rc, out[:140]))

    # L4 a patched dosage row is caught by the money identity
    face = load(REAL_JSON)
    face["dosage"][2]["cny_per_year_on_one_million_book"] += 7.0
    rc, out = run_check(tmp, face=rehash(face))
    chk(rc == 3 and "dosage cny" in out, "a patched dosage row must be caught (rc=%s)" % rc)

    # L5 dose 0 must be the repo arm: patching it is a defect
    face = load(REAL_JSON)
    for d in face["dosage"]:
        if abs(d["dose_of_cash_leg"]) < 1e-12:
            d["net_cagr_pct"] = round(d["net_cagr_pct"] + 1.0, 4)
            break
    rc, out = run_check(tmp, face=rehash(face))
    chk(rc == 3 and "dose0 level" in out, "a broken dose-0 identity must be caught (rc=%s)" % rc)

    # L6 the page must carry the verdict tokens
    md = io.open(REAL_MD, encoding="utf-8").read().replace(
        "`THE_INSTRUMENT_ON_SALE_DOES_NOT_HOLD_THE_CLASS_RETURN`", "`SOMETHING_ELSE`")
    rc, out = run_check(tmp, md=md)
    chk(rc == 3 and "missing verdict token" in out, "a page missing a verdict must be caught")

    # L7 the parking-lot column must be on the page
    md = io.open(REAL_MD, encoding="utf-8").read().replace("最差 20 根", "回撤")
    rc, out = run_check(tmp, md=md)
    chk(rc == 3 and "parking-lot column" in out, "a page without the tail column must be caught")

    # L8 a percent-of-percent print is a defect even though arithmetic legs pass
    md = io.open(REAL_MD, encoding="utf-8").read() + "\n参考：1658.03%\n"
    rc, out = run_check(tmp, md=md)
    chk(rc == 3 and "percent-of-percent" in out, "a percent-of-percent print must be caught")

    # L9 a missing face is STALE and does not crash
    buf = io.StringIO()
    out, sys.stdout = sys.stdout, buf
    try:
        rc = S.check(os.path.join(tmp, "nope.json"), os.path.join(tmp, "nope.md"))
    finally:
        sys.stdout = out
    chk(rc == 3 and "STALE" in buf.getvalue(), "a missing face must be STALE, not a traceback")

    # L10 a string where a number belongs is a defect, not a traceback
    face = load(REAL_JSON)
    face["headline"]["cb_etf_net_pct"] = str(face["headline"]["cb_etf_net_pct"])
    rc, out = run_check(tmp, face=rehash(face))
    chk(rc == 3, "a string in a numeric slot must be refused (rc=%s)" % rc)

    # L11 a content hash that no longer describes the face is a defect
    face = load(REAL_JSON)
    face["arm_info"]["repo_gc001"]["orders"] = 1
    rc, out = run_check(tmp, face=face)
    chk(rc == 3 and "content_sha256" in out, "a stale content hash must be caught")

    # L12 the published files were never written by this control
    for p, h in before.items():
        chk(sha(p) == h, "the control must not modify %s" % os.path.basename(p))

    shutil.rmtree(tmp, ignore_errors=True)
    if errs:
        for e in errs:
            print("NEGATIVE FAIL:", e)
        print("NEGATIVE %d/%d" % (legs[0] - len(errs), legs[0]))
        return 1
    print("NEGATIVE OK %d/%d PASS" % (legs[0], legs[0]))
    return 0


if __name__ == "__main__":
    sys.exit(main())

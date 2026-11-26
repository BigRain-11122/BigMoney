"""r2162: prove on the real check() that a moved input prints STALE and a real arithmetic
error does not -- the two halves of the r1934 contract, run against the published face.

Run: python results/_r2162bmc_width_fit_stale_probe.py
"""
import io
import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import etf_book_width_fit as M                      # noqa: E402

FACE = M.OUT


def one(label, mutate, expect_rc, expect_word):
    tmpdir = tempfile.mkdtemp(prefix="r2162_")
    tmp = os.path.join(tmpdir, "face.json")
    with io.open(FACE, encoding="utf-8") as fh:
        payload = json.load(fh)
    mutate(payload)
    with io.open(tmp, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
    old = M.OUT
    M.OUT = tmp
    try:
        buf = io.StringIO()
        keep = sys.stdout
        sys.stdout = buf
        try:
            rc = M.main_check()
        finally:
            sys.stdout = keep
        text = buf.getvalue()
    finally:
        M.OUT = old
        shutil.rmtree(tmpdir, ignore_errors=True)
    hit = (expect_word is None) or (expect_word in text)
    ok = (rc == expect_rc) and hit
    print("[%s] %-58s rc=%s expect=%s word=%r" %
          ("PASS" if ok else "FAIL", label, rc, expect_rc, expect_word))
    if not ok:
        print(text)
    return ok


legs = []
legs.append(one("untouched face -> CHECK_OK", lambda p: None, 0, "CHECK_OK"))
legs.append(one("decision_bar rolled back one bar -> CHECK_STALE",
                lambda p: p.__setitem__("decision_bar", "2026-01-05"), 3, "STALE"))
legs.append(one("gate_bar rolled back one bar -> CHECK_STALE",
                lambda p: (p.get("gate_reads") or {}).__setitem__("gate_bar", "2026-01-05"),
                3, "STALE"))
legs.append(one("width-5 impact no longer equals per_name/adv -> CHECK_FAIL, no STALE",
                lambda p: [r for r in p["rows"] if r["n"] == 5][0].__setitem__(
                    "per_name_cny", 1.0), 1, None))
print("probe %d/%d" % (sum(1 for x in legs if x), len(legs)))
raise SystemExit(0 if all(legs) else 1)

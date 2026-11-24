"""Negative control for scripts/etf_book_cap_trim_toll.py (r2073, bm-c).

Every leg tampers one thing, runs the real `--check`, asserts the sentence it must print
(and the sentence it must NOT print), then restores the byte-exact original.  A face that
stays green after its own numbers are edited is not a check.

  python results/_r2073bmc_cap_trim_toll_negctl.py
"""
import hashlib
import io
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
SCRIPT = os.path.join(REPO, "scripts", "etf_book_cap_trim_toll.py")
OUT = os.path.join(REPO, "results", "etf_book_cap_trim_toll.json")
PAGE = os.path.join(REPO, "research", "ETF_BOOK_CAP_TRIM_TOLL.md")

INPUTS = [
    os.path.join(REPO, "results", "etf_book_cap_beta_units.json"),
    os.path.join(REPO, "results", "etf_book_beta_paths.json"),
]

cases = []


def leg(name, fn):
    try:
        fn()
        cases.append((name, True, ""))
    except AssertionError as e:
        cases.append((name, False, str(e)))


def run_check():
    p = subprocess.run([sys.executable, SCRIPT, "--check"], capture_output=True, text=True,
                       env=dict(os.environ, PYTHONIOENCODING="utf-8"))
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def snapshot():
    with io.open(OUT, "rb") as fh:
        out = fh.read()
    with io.open(PAGE, "rb") as fh:
        page = fh.read()
    return out, page


def restore(out_bytes, page_bytes):
    with io.open(OUT, "wb") as fh:
        fh.write(out_bytes)
    with io.open(PAGE, "wb") as fh:
        fh.write(page_bytes)


def with_restore(fn):
    out_b, page_b = snapshot()
    try:
        fn()
    finally:
        restore(out_b, page_b)


def t_baseline_green():
    rc, txt = run_check()
    assert rc == 0, "baseline check not green: rc=%s %s" % (rc, txt.strip()[:400])
    assert "CHECK OK" in txt, txt[:200]


def t_tamper_number_is_check_failed():
    def body():
        out_b, _ = snapshot()
        data = json.loads(out_b.decode("utf-8"))
        data["facts"]["toll"]["round_trip_cny"] = round(data["facts"]["toll"]["round_trip_cny"] + 1.0, 2)
        with io.open(OUT, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=1, sort_keys=True)
            fh.write("\n")
        rc, txt = run_check()
        assert rc == 3, "tampered number must be rc3, got %s" % rc
        assert "CHECK FAILED" in txt, txt[:300]
        assert "STALE" not in txt, "a same-input disagreement must not excuse itself as stale: " + txt[:300]
        assert "round_trip_cny" in txt, "the failing field must be named: " + txt[:300]
    with_restore(body)


def t_tamper_digest_is_stale():
    def body():
        out_b, _ = snapshot()
        data = json.loads(out_b.decode("utf-8"))
        data["inputs_digest"] = "0" * 64
        with io.open(OUT, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=1, sort_keys=True)
            fh.write("\n")
        rc, txt = run_check()
        assert rc == 3, "a moved digest must be rc3, got %s" % rc
        assert "STALE" in txt, txt[:300]
        assert "CHECK FAILED" not in txt, "a stale face is not a wrong face: " + txt[:300]
    with_restore(body)


def t_tamper_page_block():
    def body():
        with io.open(PAGE, "r", encoding="utf-8") as fh:
            page = fh.read()
        needle = "| 连续超帽段数（= 卖出的次数） | 2 |"
        assert needle in page, "the page under test does not carry the line this leg edits"
        with io.open(PAGE, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(page.replace(needle, "| 连续超帽段数（= 卖出的次数） | 3 |", 1))
        rc, txt = run_check()
        assert rc == 3, "an edited page must be rc3, got %s" % rc
        assert "page block" in txt, txt[:300]
    with_restore(body)


def t_page_marker_missing():
    def body():
        with io.open(PAGE, "r", encoding="utf-8") as fh:
            page = fh.read()
        with io.open(PAGE, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(page.replace("<!-- CAP-TRIM-END -->", "", 1))
        rc, txt = run_check()
        assert rc == 3, "a page without its closing marker must be rc3, got %s" % rc
        assert "page block" in txt, txt[:300]
    with_restore(body)


def t_restored_green_and_inputs_untouched():
    before = {p: hashlib.sha256(io.open(p, "rb").read()).hexdigest() for p in INPUTS}
    rc, txt = run_check()
    assert rc == 0 and "CHECK OK" in txt, "restored face must be green: rc=%s %s" % (rc, txt[:300])
    after = {p: hashlib.sha256(io.open(p, "rb").read()).hexdigest() for p in INPUTS}
    assert before == after, "the negative control touched an input face"


def t_absent_face_is_stale():
    def body():
        os.remove(OUT)
        rc, txt = run_check()
        assert rc == 3, "a missing face must be rc3, got %s" % rc
        assert "STALE" in txt, txt[:300]
    with_restore(body)


for name, fn in [("baseline is green", t_baseline_green),
                 ("an edited number is CHECK FAILED, not STALE", t_tamper_number_is_check_failed),
                 ("a moved digest is STALE, not CHECK FAILED", t_tamper_digest_is_stale),
                 ("an edited page block is named", t_tamper_page_block),
                 ("a page without its marker is refused", t_page_marker_missing),
                 ("a missing face is STALE", t_absent_face_is_stale),
                 ("restore is green and inputs untouched", t_restored_green_and_inputs_untouched)]:
    leg(name, fn)

bad = [c for c in cases if not c[1]]
for n, ok, why in cases:
    print("%s %s%s" % ("[PASS]" if ok else "[FAIL]", n, "" if ok else " | " + why))
print("%d/%d legs pass" % (len(cases) - len(bad), len(cases)))
sys.exit(0 if not bad else 1)

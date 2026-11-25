"""Negative control for scripts/policy_return_lattice.py.

Proves the judge can actually say no: a hand-edited number must come out as
CHECK FAILED (and must not print the word STALE), a moved input byte must come
out as STALE, and the two verdict switches must flip. Everything happens on
copies in a temp directory -- the published face is never touched.
"""
import contextlib
import importlib.util
import io
import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "scripts", "policy_return_lattice.py")

spec = importlib.util.spec_from_file_location("prl", SCRIPT)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

legs = 0


def ok(cond, name):
    global legs
    legs += 1
    if not cond:
        raise AssertionError("negative leg %d failed: %s" % (legs, name))


def check_capture():
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = m.cmd_check()
    return rc, buf.getvalue()


def main():
    tmp = tempfile.mkdtemp(prefix="r2100lattice_")
    face = os.path.join(tmp, "face.json")
    page = os.path.join(tmp, "page.md")
    shutil.copyfile(m.OUT, face)
    shutil.copyfile(m.PAGE, page)
    m.OUT, m.PAGE = face, page

    rc, out = check_capture()
    ok(rc == 0 and "CHECK_OK" in out, "a clean copy verifies")

    stored = json.load(io.open(face, encoding="utf-8"))

    # 1. hand-edited number -> CHECK FAILED, and the word STALE must not appear
    bad = json.loads(json.dumps(stored))
    bad["engine_rung"]["expected_total_cny"] += 5000
    with io.open(face, "w", encoding="utf-8", newline="\n") as f:
        json.dump(bad, f, ensure_ascii=False)
    rc, out = check_capture()
    ok(rc == 3 and "CHECK FAILED" in out, "a hand-edited number fails the check")
    ok("STALE" not in out, "a defect does not get the word STALE (r1934 contract)")

    # 2. moved input byte -> STALE, and it must be the stale branch, not a defect
    moved = json.loads(json.dumps(stored))
    moved["input_digest"]["GC001.csv"] = "0" * 64
    with io.open(face, "w", encoding="utf-8", newline="\n") as f:
        json.dump(moved, f, ensure_ascii=False)
    rc, out = check_capture()
    ok(rc == 3 and "STALE" in out and "CHECK FAILED" not in out,
       "a moved input is STALE, not a defect")

    # 3. missing face -> STALE, and it names the path
    os.replace(face, face + ".bak")
    rc, out = check_capture()
    ok(rc == 3 and "face missing" in out, "a missing face is STALE and says so")
    os.replace(face + ".bak", face)

    # 4. the band is judged from the printed pct, not from a stored verdict token
    old_lo, old_hi = m.TARGET_LO, m.TARGET_HI
    m.TARGET_LO, m.TARGET_HI = 20.0, 25.0
    with io.open(face, "w", encoding="utf-8", newline="\n") as f:
        json.dump(stored, f, ensure_ascii=False)
    rc, out = check_capture()
    ok(rc == 3, "moving the target band invalidates the stored judgment")
    m.TARGET_LO, m.TARGET_HI = old_lo, old_hi

    # 5. a dropped rung is detected (the lattice must be complete)
    hole = json.loads(json.dumps(stored))
    hole["lattice"] = [r for r in hole["lattice"] if not (r["ic_lots"] == 1 and r["im_lots"] == 1)]
    with io.open(face, "w", encoding="utf-8", newline="\n") as f:
        json.dump(hole, f, ensure_ascii=False)
    rc, out = check_capture()
    ok(rc == 3 and "CHECK FAILED" in out, "a missing rung is caught")

    # 6. internal arithmetic in the published face is self-consistent
    tot = sum(r["l1_cny"] + r["carry_cny"] + r["cash_interest_cny"] for r in stored["lattice"])
    printed = sum(r["expected_total_cny"] for r in stored["lattice"])
    ok(abs(tot - printed) <= 2 * len(stored["lattice"]), "rung totals add up to their parts")
    ok(all(r["margin_cny"] >= 0 and r["notional_cny"] >= 0 for r in stored["lattice"]),
       "no negative margin or notional")
    ok(len(stored["lattice"]) == (m.MAX_LOTS + 1) ** 2, "every lattice point is present")

    # 7. the two rungs the verdict leans on are ordered the way the story claims
    def pct(ic, im):
        for r in stored["lattice"]:
            if r["ic_lots"] == ic and r["im_lots"] == im:
                return r["expected_return_pct"]
        raise AssertionError("rung missing from face")

    ok(pct(0, 1) < pct(1, 1) and pct(0, 0) < pct(0, 1),
       "a heavier carry rung earns more than a lighter one")
    ok(stored["judgment"]["engine_pct"] == pct(1, 1), "the verdict leans on the engine's own rung")

    # 8. the page is not allowed to be missing or empty
    body = io.open(page, encoding="utf-8").read()
    ok(len(body) > 500 and "判词" in body, "the reader page exists and carries the verdict section")

    shutil.rmtree(tmp, ignore_errors=True)
    print("negative-control %d/%d OK" % (legs, legs))
    return 0


if __name__ == "__main__":
    sys.exit(main())

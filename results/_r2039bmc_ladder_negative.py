"""Negative controls for the wait-ladder face (r2039, bm-c).

Each leg makes the face wrong in exactly one way and asserts that `check()` names that
wrong thing -- and, for the two kinds of red the chain distinguishes (r1934), names only
that one: an upstream that moved is STALE, a number that disagrees with its own inputs is
CHECK FAILED and must not also carry STALE.

Path swaps go through module globals, never default arguments (r2038's trap), and every
copy lands in a throwaway temp dir so nothing is copied onto itself (r2037's SameFileError).

    python results/_r2039bmc_ladder_negative.py
"""

import io
import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import astock_veto_hedge_wait_ladder as W  # noqa: E402

PUBLISHED = [
    W.OUT_JSON,
    W.OUT_MD,
    W.BAND_FACE,
    W.WAIT_FACE,
    os.path.join(ROOT, "scripts", "astock_veto_hedge_wait_ladder.py"),
]


def _sha(path):
    return W._sha_file(path)


def _read(path):
    with io.open(path, encoding="utf-8") as f:
        return f.read()


def _write(path, text):
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)


def _write_json(path, obj):
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1, sort_keys=True)


def main() -> int:
    before = {p: _sha(p) for p in PUBLISHED}
    ok = 0
    fail = 0

    def chk(name, cond, detail=""):
        nonlocal ok, fail
        if cond:
            ok += 1
        else:
            fail += 1
            print("FAIL: %s %s" % (name, detail))

    real = {"OUT_JSON": W.OUT_JSON, "OUT_MD": W.OUT_MD,
            "BAND_FACE": W.BAND_FACE, "WAIT_FACE": W.WAIT_FACE}
    tmp = tempfile.mkdtemp(prefix="r2039neg_")
    try:
        base_face = json.load(io.open(W.OUT_JSON, encoding="utf-8"))
        base_page = _read(W.OUT_MD)

        def arm(face_obj, page_text, band_bytes_extra="", wait_bytes_extra=""):
            """Point the module at a throwaway triple of face/page/parents."""
            j = os.path.join(tmp, "face.json")
            m = os.path.join(tmp, "page.md")
            b = os.path.join(tmp, "band.json")
            w = os.path.join(tmp, "wait.json")
            _write_json(j, face_obj)
            _write(m, page_text)
            shutil.copyfile(real["BAND_FACE"], b)
            shutil.copyfile(real["WAIT_FACE"], w)
            if band_bytes_extra:
                with io.open(b, "a", encoding="utf-8", newline="") as f:
                    f.write(band_bytes_extra)
            if wait_bytes_extra:
                with io.open(w, "a", encoding="utf-8", newline="") as f:
                    f.write(wait_bytes_extra)
            W.OUT_JSON, W.OUT_MD = j, m
            W.BAND_FACE, W.WAIT_FACE = b, w
            return j, m

        def disarm(j, m):
            W.OUT_JSON, W.OUT_MD = j, m

        def reseal(j):
            obj = json.load(io.open(j, encoding="utf-8"))
            obj.pop("content_sha256", None)
            obj["content_sha256"] = W.content_sha(obj)
            _write_json(j, obj)

        def capture(fn):
            buf = io.StringIO()
            old = sys.stdout
            sys.stdout = buf
            try:
                rc = fn()
            finally:
                sys.stdout = old
            return rc, buf.getvalue()

        # L1 a healthy copy of the real face passes (proves the harness itself can go green)
        j, m = arm(base_face, base_page)
        rc, out = capture(W.check)
        chk("L1 healthy copy is green", rc == 0, "(rc=%d %s)" % (rc, out.strip()[:120]))
        chk("L1 green output says CHECK_OK", "CHECK_OK" in out)

        # L2 one ladder cell moved -> CHECK FAILED, and not STALE
        bad = json.loads(json.dumps(base_face))
        bad["ladder"][3]["yearly_cost_pp"] = round(bad["ladder"][3]["yearly_cost_pp"] + 0.05, 4)
        j, m = arm(bad, base_page)
        reseal(j)
        rc, out = capture(W.check)
        chk("L2 a moved ladder cell is red", rc == 3, "(rc=%d)" % rc)
        chk("L2 it is named CHECK FAILED", "CHECK FAILED" in out, out.strip()[:160])
        chk("L2 it is not named STALE", "STALE" not in out, out.strip()[:160])

        # L3 the break-even edge moved -> CHECK FAILED
        bad = json.loads(json.dumps(base_face))
        bad["break_even"]["k_low"] = float(bad["break_even"]["k_low"]) + 0.01
        j, m = arm(bad, base_page)
        reseal(j)
        rc, out = capture(W.check)
        chk("L3 a moved break-even edge is red", rc == 3)
        chk("L3 it is named CHECK FAILED", "CHECK FAILED" in out)
        chk("L3 it does not pretend to be STALE", "STALE" not in out)

        # L4 the identity stops holding -> CHECK FAILED by name
        bad = json.loads(json.dumps(base_face))
        bad["quadratic"]["max_row_error"] = 0.5
        j, m = arm(bad, base_page)
        reseal(j)
        rc, out = capture(W.check)
        chk("L4 rows that are not a quadratic are red", rc == 3)
        chk("L4 it names the identity", "not a quadratic" in out, out.strip()[:160])

        # L5 the page lost a verdict -> CHECK FAILED
        page = base_page.replace(base_face["holding_verdict"], "(removed)")
        j, m = arm(base_face, page)
        rc, out = capture(W.check)
        chk("L5 a page missing a verdict is red", rc == 3, "(rc=%d)" % rc)
        chk("L5 it names the missing token", "missing token" in out, out.strip()[:160])
        chk("L5 it is not named STALE", "STALE" not in out)

        # L6 a parent grew one byte -> STALE, and not CHECK FAILED
        j, m = arm(base_face, base_page, band_bytes_extra="\n")
        rc, out = capture(W.check)
        chk("L6 a moved parent is STALE", rc == 3 and "STALE" in out, out.strip()[:160])
        chk("L6 it is not called a CHECK FAILED", "CHECK FAILED" not in out)

        # L7 the other parent moved -> also STALE
        j, m = arm(base_face, base_page, wait_bytes_extra=" ")
        rc, out = capture(W.check)
        chk("L7 the second parent is watched too", rc == 3 and "STALE" in out)

        # L8 the face file is missing -> STALE, no traceback
        j = os.path.join(tmp, "absent.json")
        W.OUT_JSON = j
        W.OUT_MD = os.path.join(tmp, "page.md")
        rc, out = capture(W.check)
        chk("L8 a missing face is STALE", rc == 3 and "STALE" in out)
        chk("L8 a missing face does not crash", "Traceback" not in out)

        # L9 the face is there but the page is gone -> STALE
        W.OUT_JSON = os.path.join(tmp, "face.json")
        W.OUT_MD = os.path.join(tmp, "no-such-page.md")
        rc, out = capture(W.check)
        chk("L9 a missing page is STALE", rc == 3 and "STALE" in out)
        chk("L9 it does not crash", "Traceback" not in out)

        # L10 a number turned into a string -> CHECK FAILED, not a traceback
        bad = json.loads(json.dumps(base_face))
        bad["ladder"][0]["yearly_cost_pp"] = "16.580"
        j, m = arm(bad, base_page)
        reseal(j)
        rc, out = capture(W.check)
        chk("L10 a string where a number belongs is red", rc == 3, "(rc=%d)" % rc)
        chk("L10 it does not crash", "Traceback" not in out)

        # L11 the k=0 rung stops being r2038's price -> CHECK FAILED
        bad = json.loads(json.dumps(base_face))
        bad["anchor"]["reproduced_yearly_cost_pp"] = 16.0
        j, m = arm(bad, base_page)
        reseal(j)
        rc, out = capture(W.check)
        chk("L11 a ladder that is not r2038's ladder is red", rc == 3)
        chk("L11 it names the anchor", "does not reproduce" in out, out.strip()[:160])

        disarm(real["OUT_JSON"], real["OUT_MD"])
        W.BAND_FACE, W.WAIT_FACE = real["BAND_FACE"], real["WAIT_FACE"]
    finally:
        W.OUT_JSON, W.OUT_MD = real["OUT_JSON"], real["OUT_MD"]
        W.BAND_FACE, W.WAIT_FACE = real["BAND_FACE"], real["WAIT_FACE"]
        shutil.rmtree(tmp, ignore_errors=True)

    after = {p: _sha(p) for p in PUBLISHED}
    for path in PUBLISHED:
        chk("published file untouched: %s" % os.path.relpath(path, ROOT),
            before[path] == after[path])

    print("%d/%d PASS" % (ok, ok + fail))
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

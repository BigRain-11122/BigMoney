"""Negative control for scripts/etf_book_unreadable_rail_floor.py (r2071 bm-c).

Why a separate file: the face's `--check` is the only thing that decides whether the
published numbers still describe the inputs.  A check that cannot fail is not a check
(r1935 family), and a check that fails with the wrong word makes the S6 chain pay for a
rebuild it does not need (r1850 family: drift -> STALE, disagreement -> CHECK FAILED).

Every leg below runs the **real** `cmd_check()` against a temporary copy of the face and
page.  Nothing under results/ or research/ is touched: the production face, the
permission face and the gap face are read byte-identical before and after.
"""

from __future__ import annotations

import hashlib
import io
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(REPO, "scripts"))

import etf_book_unreadable_rail_floor as F  # noqa: E402

ok = 0
bad = []


def leg(name, cond, detail=""):
    global ok
    if cond:
        ok += 1
    else:
        bad.append("%s %s" % (name, detail))


def sha(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def capture(path):
    with open(path, "rb") as fh:
        return fh.read()


def restore(path, blob):
    with open(path, "wb") as fh:
        fh.write(blob)


def run_check_capture():
    """Call the real cmd_check() and capture its stdout."""
    buf = io.StringIO()
    old = sys.stdout
    sys.stdout = buf
    try:
        rc = F.cmd_check()
    finally:
        sys.stdout = old
    return rc, buf.getvalue()


def main() -> int:
    tmp = tempfile.mkdtemp(prefix="r2071_negctl_")

    # the three shared faces must be byte-identical when we are done
    shared = [F.PERM, F.GAP, F.LEGS]
    before = {p: sha(p) for p in shared if os.path.exists(p)}

    try:
        # 0. snapshot the real face + page, then point the module at the copies
        real_face = capture(F.OUT)
        real_page = capture(F.PAGE)
        face_tmp = os.path.join(tmp, "face.json")
        page_tmp = os.path.join(tmp, "page.md")
        with open(face_tmp, "wb") as fh:
            fh.write(real_face)
        with open(page_tmp, "wb") as fh:
            fh.write(real_page)
        F.OUT, F.PAGE = face_tmp, page_tmp

        # 1. untouched copy -> rc0
        rc, out = run_check_capture()
        leg("pristine copy reads CHECK OK", rc == 0, "%s | %s" % (rc, out[:120]))

        # 2. one number changed -> disagreement: rc3, CHECK FAILED, and NOT the word STALE
        face = json.loads(real_face.decode("utf-8"))
        face["permitted_k"] = round(float(face["permitted_k"]) + 0.01, 6)
        with open(face_tmp, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=2)
            fh.write("\n")
        rc, out = run_check_capture()
        leg("a changed number reads rc3", rc == 3, rc)
        leg("a changed number says CHECK FAILED", "CHECK FAILED" in out, out[:160])
        leg("a changed number does NOT say STALE (no paid rebuild)", "STALE" not in out, out[:160])
        leg("the disagreement names the field", "permitted_k" in out, out[:160])

        # 3. inputs moved -> drift: rc3, STALE, and NOT CHECK FAILED
        face = json.loads(real_face.decode("utf-8"))
        face["inputs_digest"] = "0" * 64
        with open(face_tmp, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=2)
            fh.write("\n")
        rc, out = run_check_capture()
        leg("a moved digest reads rc3", rc == 3, rc)
        leg("a moved digest says STALE", "STALE" in out, out[:160])
        leg("a moved digest does NOT say CHECK FAILED", "CHECK FAILED" not in out, out[:160])

        # 4. the page block is edited -> rc3 and the page is named
        with open(face_tmp, "wb") as fh:
            fh.write(real_face)
        page = real_page.decode("utf-8")
        tampered = page.replace("| 可保留 | 可保留 |", "| 可保留 | 不可保留 |", 1)
        leg("the page really contains the row we tamper",
            tampered != page, "row not found -- the leg would be vacuous")
        with open(page_tmp, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(tampered)
        rc, out = run_check_capture()
        leg("an edited page block reads rc3", rc == 3, rc)
        leg("an edited page block names the page", "page block" in out, out[:160])

        # 5. restore both copies byte-identically -> rc0 again
        with open(face_tmp, "wb") as fh:
            fh.write(real_face)
        with open(page_tmp, "wb") as fh:
            fh.write(real_page)
        rc, out = run_check_capture()
        leg("restored copies read CHECK OK again", rc == 0, "%s | %s" % (rc, out[:120]))

        # 6. the production claim itself: three legs die on the stub
        reading = F.derive(now_epoch=1795551234.0)
        leg("production face finds exactly 3 cascade legs",
            len(reading.get("cascade_legs") or []) == 3,
            [c["leg"] for c in reading.get("cascade_legs") or []])
        leg("production face says the gap stub has no gap_k",
            reading.get("gap_face_has_gap_k") is False, reading.get("gap_face_has_gap_k"))
        leg("production face prices a permission (not blank)",
            reading.get("permitted_k") is not None, reading.get("permitted_k"))

        # 7. a rail below the floor line must NOT be priced (the rule is not "always print")
        low = dict(reading.get("readable_paths") or {})
        readings = {n: {"kind": "path", "k": k} for n, k in low.items()}
        readings["baseline_published"] = {"kind": "unreadable", "k": 0.10}
        must_wait = F.floor_from_readings(readings, reading["k_now"], reading["size_tol"])
        leg("a low unreadable rail flips the verdict",
            must_wait["verdict"] == "FLOOR_MUST_WAIT", must_wait["verdict"])
        leg("and prints no permission", must_wait["permitted_k"] is None,
            must_wait["permitted_k"])
    finally:
        # 8. the shared faces were read only -- prove it
        for path, digest in before.items():
            leg("shared face untouched: %s" % os.path.basename(path),
                os.path.exists(path) and sha(path) == digest)
        shutil.rmtree(tmp, ignore_errors=True)

    if bad:
        print("NEGCTL FAILED %d/%d" % (ok, ok + len(bad)))
        for b in bad:
            print("  -", b)
        return 1
    print("NEGCTL OK %d/%d" % (ok, ok))
    return 0


if __name__ == "__main__":
    sys.exit(main())

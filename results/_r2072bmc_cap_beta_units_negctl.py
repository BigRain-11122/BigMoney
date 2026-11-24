"""Negative control for scripts/etf_book_cap_beta_units.py (r2072 bm-c).

Why a separate file: the face's `--check` is the only thing that decides whether the two
readings still describe the inputs.  A check that cannot fail is not a check (r1935
family), and a check that fails with the wrong word makes the S6 chain pay for a rebuild it
does not need (r1850/r1934 family: inputs moved -> STALE, same inputs / different numbers
-> CHECK FAILED).

Every leg runs the **real** `cmd_check()` against temporary copies of the face and page.
Nothing under results/ or research/ is touched: the five input faces and the production
face/page are read byte-identical before and after.
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

import etf_book_cap_beta_units as F  # noqa: E402

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
    buf = io.StringIO()
    old = sys.stdout
    sys.stdout = buf
    try:
        rc = F.cmd_check()
    finally:
        sys.stdout = old
    return rc, buf.getvalue()


def main() -> int:
    tmp = tempfile.mkdtemp(prefix="r2072_negctl_")
    ptr = json.load(io.open(F.TICKET_PTR, encoding="utf-8"))
    ticket_path = os.path.join(os.path.dirname(F.TICKET_PTR), ptr["file"])
    shared = F.input_paths(ticket_path)
    before = {p: sha(p) for p in shared if os.path.exists(p)}
    prod_face_sha = sha(F.OUT)
    prod_page_sha = sha(F.PAGE)

    try:
        real_face = capture(F.OUT)
        real_page = capture(F.PAGE)
        face_tmp = os.path.join(tmp, "face.json")
        page_tmp = os.path.join(tmp, "page.md")
        restore(face_tmp, real_face)
        restore(page_tmp, real_page)
        F.OUT, F.PAGE = face_tmp, page_tmp

        # 1. untouched copies -> rc0
        rc, out = run_check_capture()
        leg("pristine copy reads CHECK OK", rc == 0, "%s | %s" % (rc, out[:120]))

        # 2. one beta number changed -> disagreement: rc3, CHECK FAILED, never STALE
        face = json.loads(real_face.decode("utf-8"))
        face["facts"]["beta_now"] = round(float(face["facts"]["beta_now"]) + 0.05, 6)
        with io.open(face_tmp, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1)
            fh.write("\n")
        rc, out = run_check_capture()
        leg("a changed beta reads rc3", rc == 3, rc)
        leg("a changed beta says CHECK FAILED", "CHECK FAILED" in out, out[:160])
        leg("a changed beta does NOT say STALE (no paid rebuild)", "STALE" not in out,
            out[:160])
        leg("the disagreement names beta_now", "beta_now" in out, out[:160])

        # 3. the verdict itself changed -> still CHECK FAILED, still no STALE
        face = json.loads(real_face.decode("utf-8"))
        face["facts"]["verdict"] = "OVER_CAP_BEYOND_THE_RULER"
        with io.open(face_tmp, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1)
            fh.write("\n")
        rc, out = run_check_capture()
        leg("a rewritten verdict reads rc3", rc == 3, rc)
        leg("a rewritten verdict says CHECK FAILED", "CHECK FAILED" in out, out[:160])
        leg("a rewritten verdict does NOT say STALE", "STALE" not in out, out[:160])
        leg("the disagreement names verdict", "verdict" in out, out[:160])

        # 4. inputs moved -> drift: rc3, STALE, and NOT CHECK FAILED
        face = json.loads(real_face.decode("utf-8"))
        face["inputs_digest"] = "0" * 64
        with io.open(face_tmp, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1)
            fh.write("\n")
        rc, out = run_check_capture()
        leg("a moved digest reads rc3", rc == 3, rc)
        leg("a moved digest says STALE", "STALE" in out, out[:160])
        leg("a moved digest does NOT say CHECK FAILED", "CHECK FAILED" not in out, out[:160])

        # 5. the page block is edited -> rc3 and the page is named
        restore(face_tmp, real_face)
        page = real_page.decode("utf-8")
        tampered = page.replace("**AT_CAP_WITHIN_RULER_NOISE**",
                                "**OVER_CAP_BEYOND_THE_RULER**", 1)
        leg("the page really contains the number we tamper", tampered != page,
            "string not found -- the leg would be vacuous")
        with io.open(page_tmp, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(tampered)
        rc, out = run_check_capture()
        leg("an edited page block reads rc3", rc == 3, rc)
        leg("an edited page block names the page", "page block" in out, out[:160])

        # 6. a page with no rendered block is not silently accepted
        with io.open(page_tmp, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("# a page that lost its block\n")
        rc, out = run_check_capture()
        leg("a page without the block reads rc3", rc == 3, rc)
        leg("a page without the block says CHECK FAILED", "CHECK FAILED" in out, out[:160])

        # 7. restore both copies byte-identically -> rc0 again
        restore(face_tmp, real_face)
        restore(page_tmp, real_page)
        rc, out = run_check_capture()
        leg("restored copies read CHECK OK again", rc == 0, "%s | %s" % (rc, out[:120]))

        # 8. the five shared input faces are untouched
        after = {p: sha(p) for p in shared if os.path.exists(p)}
        leg("the shared input faces are byte-identical", after == before,
            "%s vs %s" % (sorted(before), sorted(after)))
    finally:
        F.OUT, F.PAGE = os.path.join(REPO, "results", "etf_book_cap_beta_units.json"), \
            os.path.join(REPO, "research", "ETF_BOOK_CAP_BETA_UNITS.md")
        shutil.rmtree(tmp, ignore_errors=True)

    leg("the production face is byte-identical", sha(F.OUT) == prod_face_sha)
    leg("the production page is byte-identical", sha(F.PAGE) == prod_page_sha)

    for name in bad:
        print("[FAIL] %s" % name)
    print("%d legs pass, %d fail" % (ok, len(bad)))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())

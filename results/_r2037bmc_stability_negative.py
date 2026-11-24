"""Negative control for r2037's stability face.

The face is only worth its verdict if ``check`` can tell four different failures apart.  Each
leg below breaks one thing on a throwaway copy and asserts the *right* exit code and the *right*
wording:

  * a hand-edited number is a defect (rc1, ``CHECK FAILED``, and no ``STALE`` token, so a chain
    leg will not pay to rewrite it);
  * a moved parent is drift (rc3, ``STALE``, and no ``CHECK FAILED``);
  * a missing face is drift, not a crash;
  * a page that has lost a token the face published is a defect;
  * and after all of it the four published files are byte-identical to what they were before.

Usage
    python results/_r2037bmc_stability_negative.py
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

import astock_veto_hedge_stability as S  # noqa: E402

LEGS = []


def leg(name, ok, detail=""):
    LEGS.append((name, bool(ok), detail))


def _sha(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def _snapshot(paths):
    return {p: _sha(p) for p in paths if os.path.exists(p)}


def _swap(tmp, **paths):
    """Point the module at the throwaway copies; return the previous bindings."""
    prev = {name: getattr(S, name) for name in paths}
    for name, value in paths.items():
        setattr(S, name, value)
    return prev


def _restore(prev):
    for name, value in prev.items():
        setattr(S, name, value)


def main() -> int:
    real_json, real_md, real_parent = S.OUT_JSON, S.OUT_MD, S.PARENT
    published = [S.PARENT, S.CARRIER, S.FUNDING, S.OUT_JSON, S.OUT_MD]
    before = _snapshot(published)
    if not os.path.exists(S.OUT_JSON):
        print("FAIL the face has not been run yet: %s" % S.OUT_JSON)
        return 1

    tmp = tempfile.mkdtemp(prefix="r2037bmc_neg_")
    try:
        face_src = os.path.join(tmp, "face.json")
        page_src = os.path.join(tmp, "page.md")
        shutil.copyfile(real_json, face_src)
        shutil.copyfile(real_md, page_src)

        # --- 0. the copy itself is clean
        prev = _swap(tmp, OUT_JSON=face_src, OUT_MD=page_src)
        try:
            rc = S.check()
            leg("L0 an unmodified copy passes", rc == 0, "rc=%d" % rc)

            # --- 1. a hand-edited number is a defect, not drift
            face = json.load(open(face_src, encoding="utf-8"))
            face["full"]["gap_ann_pp"] = float(face["full"]["gap_ann_pp"]) + 0.5
            json.dump(face, open(face_src, "w", encoding="utf-8"), ensure_ascii=False,
                      indent=1, sort_keys=True)
            out = _capture(S.check)
            leg("L1 a hand-edited gap is CHECK FAILED", out[0] == 1, out[1].splitlines()[0] if out[1] else "")
            leg("L1b and it is not called STALE", "STALE" not in out[1], out[1][:120])
            shutil.copyfile(real_json, face_src)

            # --- 2. a page that lost a token is a defect
            text = open(page_src, encoding="utf-8").read()
            token = "`%s`" % json.load(open(face_src, encoding="utf-8"))["verdict"]
            open(page_src, "w", encoding="utf-8", newline="\n").write(text.replace(token, "VERDICT-GONE"))
            out = _capture(S.check)
            leg("L2 a page missing the verdict token is CHECK FAILED", out[0] == 1, out[1][:160])
            shutil.copyfile(real_md, page_src)

            # --- 3. a moved parent is drift, not a defect
            parent_copy = os.path.join(tmp, "beta.json")
            shutil.copyfile(real_parent, parent_copy)
            with open(parent_copy, "a", encoding="utf-8", newline="\n") as fh:
                fh.write("\n")
            prev_parent = _swap(tmp, PARENT=parent_copy)
            try:
                out = _capture(S.check)
                leg("L3 a moved parent is STALE", out[0] == 3, out[1].splitlines()[0] if out[1] else "")
                leg("L3b and it is not called CHECK FAILED", "CHECK FAILED" not in out[1], out[1][:120])
            finally:
                _restore(prev_parent)

            # --- 4. a missing face is drift, not a crash
            prev_missing = _swap(tmp, OUT_JSON=os.path.join(tmp, "nope.json"))
            try:
                out = _capture(S.check)
                leg("L4 a missing face is STALE", out[0] == 3, out[1].splitlines()[0] if out[1] else "")
            finally:
                _restore(prev_missing)

            # --- 5. a missing page is drift too
            prev_page = _swap(tmp, OUT_MD=os.path.join(tmp, "nope.md"))
            try:
                out = _capture(S.check)
                leg("L5 a missing page is STALE", out[0] == 3, out[1].splitlines()[0] if out[1] else "")
            finally:
                _restore(prev_page)

            # --- 6. a corrupted face body is caught by its own hash
            face = json.load(open(face_src, encoding="utf-8"))
            face["rolling_summary"]["im_leads"] = 1
            json.dump(face, open(face_src, "w", encoding="utf-8"), ensure_ascii=False,
                      indent=1, sort_keys=True)
            out = _capture(S.check)
            leg("L6 a self-inconsistent face is CHECK FAILED", out[0] == 1, out[1][:160])
            shutil.copyfile(real_json, face_src)
        finally:
            _restore(prev)

        # --- 7. nothing the control did touched the published four
        after = _snapshot(published)
        leg("L7 the published files are byte-identical after the control",
            before == after,
            ", ".join("%s" % os.path.basename(k) for k in before if before[k] != after.get(k)) or "all equal")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    width = max((len(n) for n, _, _ in LEGS), default=10)
    for name, ok, detail in LEGS:
        print("%s %-*s %s" % ("PASS" if ok else "FAIL", width, name, detail))
    bad = [x for x in LEGS if not x[1]]
    print("%d/%d PASS" % (len(LEGS) - len(bad), len(LEGS)))
    return 0 if not bad else 1


def _capture(fn):
    """Run a command function and keep both its exit code and everything it printed."""
    import io
    from contextlib import redirect_stdout

    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = fn()
    return rc, buf.getvalue()


if __name__ == "__main__":
    raise SystemExit(main())

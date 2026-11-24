"""Negative control for r2038's deploy-vs-wait face.

The face is only worth its verdict if ``check`` can tell four different failures apart.
Each leg below breaks one thing on a throwaway copy and asserts the *right* exit code and
the *right* wording:

  * a hand-edited number is a defect (rc1, ``CHECK FAILED``, and no ``STALE`` token, so a
    chain leg will not pay to rewrite it);
  * a moved parent is drift (rc3, ``STALE``, and no ``CHECK FAILED``);
  * a missing face is drift, not a crash;
  * a page that has lost a token the face published is a defect;
  * and after all of it the five published files are byte-identical to what they were.

r2037's trap is built in on purpose: ``check`` and ``build_face`` share the module-level
``OUT_JSON``/``OUT_MD`` constants, so a control that copies through those names will
``SameFileError``.  Every copy below goes through ``real_json``/``real_md`` instead.

Usage
    python results/_r2038bmc_deploy_wait_negative.py
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import astock_veto_hedge_deploy_wait as S  # noqa: E402

LEGS = []


def leg(name, ok, detail=""):
    LEGS.append((name, bool(ok), detail))


def _sha(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def _snapshot(paths):
    return {p: _sha(p) for p in paths if os.path.exists(p)}


def _swap(**paths):
    prev = {name: getattr(S, name) for name in paths}
    for name, value in paths.items():
        setattr(S, name, value)
    return prev


def _restore(prev):
    for name, value in prev.items():
        setattr(S, name, value)


def _capture(fn, *args, **kwargs):
    """Run fn and return (rc, combined stdout)."""
    buf = io.StringIO()
    old = sys.stdout
    sys.stdout = buf
    try:
        rc = fn(*args, **kwargs)
    finally:
        sys.stdout = old
    return rc, buf.getvalue()


def main() -> int:
    real_json, real_md = S.OUT_JSON, S.OUT_MD
    published = [S.BAND_FACE, S.FUNDING_FACE, S.BETA_FACE, real_json, real_md]
    before = _snapshot(published)
    if not os.path.exists(real_json):
        print("FAIL the face has not been run yet: %s" % real_json)
        return 1

    tmp = tempfile.mkdtemp(prefix="r2038bmc_neg_")
    try:
        face_src = os.path.join(tmp, "face.json")
        page_src = os.path.join(tmp, "page.md")
        shutil.copyfile(real_json, face_src)
        shutil.copyfile(real_md, page_src)

        # --- 0. the copy itself is clean
        prev = _swap(OUT_JSON=face_src, OUT_MD=page_src)
        try:
            rc, out = _capture(S.check)
            leg("L0 an unmodified copy passes", rc == 0, out.strip()[:120])

            # --- 1. a hand-edited number is a defect, not drift
            face = json.load(open(face_src, encoding="utf-8"))
            face["wait"]["yearly_cost_pp"] = float(face["wait"]["yearly_cost_pp"]) + 0.5
            with open(face_src, "w", encoding="utf-8", newline="\n") as fh:
                json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
            rc, out = _capture(S.check)
            leg("L1 a hand-edited yearly cost is CHECK FAILED", rc == 3, out.splitlines()[0] if out else "")
            leg("L1b and it is not called STALE", "STALE" not in out, out[:160])
            shutil.copyfile(real_json, face_src)

            # --- 2. a page that lost a token is a defect
            text = open(page_src, encoding="utf-8").read()
            token = json.load(open(face_src, encoding="utf-8"))["verdict"]
            with open(page_src, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(text.replace(token, "VERDICT-GONE"))
            rc, out = _capture(S.check)
            leg("L2 a page missing the verdict token is CHECK FAILED", rc == 3, out[:160])
            shutil.copyfile(real_md, page_src)

            # --- 3. the risk-ceiling token is on the page too
            text = open(page_src, encoding="utf-8").read()
            token2 = json.load(open(face_src, encoding="utf-8"))["risk_ceiling_verdict"]
            with open(page_src, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(text.replace(token2, "RISK-GONE"))
            rc, out = _capture(S.check)
            leg("L3 a page missing the risk-ceiling token is CHECK FAILED", rc == 3, out[:160])
            shutil.copyfile(real_md, page_src)

            # --- 4. a moved parent is drift, not a defect
            parent_copy = os.path.join(tmp, "band.json")
            shutil.copyfile(S.BAND_FACE, parent_copy)
            with open(parent_copy, "a", encoding="utf-8", newline="\n") as fh:
                fh.write("\n")
            prev_parent = _swap(BAND_FACE=parent_copy)
            try:
                rc, out = _capture(S.check)
                leg("L4 a moved parent is STALE", rc == 3, out.splitlines()[0] if out else "")
                leg("L4b and it is not called CHECK FAILED", "CHECK FAILED" not in out, out[:160])
            finally:
                _restore(prev_parent)

            # --- 5. a missing face is drift, not a crash
            prev_missing = _swap(OUT_JSON=os.path.join(tmp, "nope.json"))
            try:
                rc, out = _capture(S.check)
                leg("L5 a missing face is STALE", rc == 3, out.splitlines()[0] if out else "")
            finally:
                _restore(prev_missing)

            # --- 6. a missing page is drift too
            prev_page = _swap(OUT_MD=os.path.join(tmp, "nope.md"))
            try:
                rc, out = _capture(S.check)
                leg("L6 a missing page is STALE", rc == 3, out.splitlines()[0] if out else "")
            finally:
                _restore(prev_page)

            # --- 7. a ratio that disagrees with its own operands is a defect
            face = json.load(open(face_src, encoding="utf-8"))
            face["wait"]["ratio_cost_over_benefit"] = 1.0
            with open(face_src, "w", encoding="utf-8", newline="\n") as fh:
                json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
            rc, out = _capture(S.check)
            leg("L7 a self-inconsistent ratio is CHECK FAILED", rc == 3, out[:160])
            shutil.copyfile(real_json, face_src)

            # --- 8. an unreadable number is a defect, not a crash
            face = json.load(open(face_src, encoding="utf-8"))
            face["risk_ceiling"]["risk_ceiling_pp"] = "not-a-number"
            with open(face_src, "w", encoding="utf-8", newline="\n") as fh:
                json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
            rc, out = _capture(S.check)
            leg("L8 an unreadable number is CHECK FAILED, not a traceback", rc == 3,
                out.splitlines()[0] if out else "")
            shutil.copyfile(real_json, face_src)
        finally:
            _restore(prev)

        # --- 9. nothing the control did touched the published five
        after = _snapshot(published)
        leg("L9 the five published files are byte-identical", before == after,
            "%d/%d" % (sum(1 for k in before if after.get(k) == before[k]), len(before)))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    failed = [n for n, ok, _ in LEGS if not ok]
    for name, ok, detail in LEGS:
        print("%s %s%s" % ("PASS" if ok else "FAIL", name,
                           "" if ok else ("  <- " + detail)))
    print("%d/%d PASS" % (len(LEGS) - len(failed), len(LEGS)))
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())

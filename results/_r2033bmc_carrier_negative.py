"""Negative control for r2033 (astock_veto_hedge_carrier).

A verdict is worth nothing if the machinery prints it regardless of the data.  This control
feeds the *same* loaders and arithmetic inputs whose answers must differ from the published
one, and then checks that the three failure modes stay distinct:

  A. FUTURES WIN BIG   -- poison the futures hedge leg so the short compounds far above the
     ETF short.  The discount-artifact flag must die (the gap is no longer small) and the
     headline must stop naming the capital case alone.
  B. ETF WINS BIG      -- poison the same leg the other way.  CARRIER_ETF_WINS must fire;
     if the ladder were hardcoded to prefer the futures this fails.
  C. SMALL SURFACE     -- keep the clean legs, shrink the quoted median discount to 2pp.
     DISCOUNT_IS_A_MEDIAN_ARTIFACT must vanish; it may not survive on a small reading.

Then the failure states, which must never be confused with each other:

  D. clean face + disturbed parent  -> STALE (and no CHECK FAILED wording)
  E. clean face + clean parent + a page missing its token -> CHECK FAILED (and no STALE)
  F. missing published face -> STALE, no crash

Nothing here touches the published face: it asserts that the machinery disagrees with itself
when the data disagrees, and that the published files are byte-identical afterwards.

Usage:
    python results/_r2033bmc_carrier_negative.py
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

import astock_veto_hedge_carrier as M  # noqa: E402

ok = fail = 0


def _ok(cond, msg):
    global ok, fail
    if cond:
        ok += 1
        print("PASS  %s" % msg)
    else:
        fail += 1
        print("FAIL  %s" % msg)


def _sha(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def main() -> int:
    published = [M.PARENT, M.BASIS, M.OUT_JSON, M.OUT_MD]
    before = {p: _sha(p) for p in published if os.path.exists(p)}
    _ok(len(before) == 4, "published four files are on disk to protect")

    parent = json.load(open(M.PARENT, encoding="utf-8"))
    basis = json.load(open(M.BASIS, encoding="utf-8"))
    clean_verdict = M.build_face()["verdict"]

    tmp = tempfile.mkdtemp(prefix="r2033carrier_")
    try:
        def with_poisoned_parent(mutator, tag):
            """Build a face off a temporary copy of the parent with one field changed."""
            clone = json.loads(json.dumps(parent))
            mutator(clone)
            path = os.path.join(tmp, "parent_%s.json" % tag)
            with open(path, "w", encoding="utf-8", newline="\n") as fh:
                json.dump(clone, fh, ensure_ascii=False)
            old = M.PARENT
            M.PARENT = path
            try:
                face = M.build_face()
            finally:
                M.PARENT = old
            return face

        def poison_hedge_im(value):
            def mutate(face):
                n = 0
                for row in face.get("rows") or []:
                    if row.get("im_window") and row.get("hedge_im") is not None:
                        row["hedge_im"] = value
                        n += 1
                assert n > 20, "too few rows to poison"
            return mutate

        # ------------------------------------------------------------ A: futures win big
        fa = with_poisoned_parent(poison_hedge_im(-0.03), "im_big_win")
        rca = fa.get("realised_carrier") or {}
        _ok((rca.get("im_minus_etf_pp_per_year") or 0) > M.TIE_PP,
            "A: poisoned futures short leads by more than the tie band (%.2f pp)"
            % (rca.get("im_minus_etf_pp_per_year") or 0))
        _ok(fa["verdicts"][M.VERDICT_ARTIFACT] is False,
            "A: the artifact flag dies when the realised gap is no longer small")
        _ok(fa["verdicts"][M.VERDICT_ETF] is False,
            "A: a futures lead does not summon the ETF flag")
        _ok(fa["verdict"] != clean_verdict,
            "A: the headline moves away from the published one (%s)" % fa["verdict"])

        # ------------------------------------------------------------ B: ETF wins big
        fb = with_poisoned_parent(poison_hedge_im(0.03), "im_big_loss")
        rcb = fb.get("realised_carrier") or {}
        _ok((rcb.get("im_minus_etf_pp_per_year") or 0) < -M.TIE_PP,
            "B: poisoned futures short trails by more than the tie band (%.2f pp)"
            % (rcb.get("im_minus_etf_pp_per_year") or 0))
        _ok(fb["verdicts"][M.VERDICT_ETF] is True,
            "B: CARRIER_ETF_WINS fires when the futures leg is paid for in realised return")
        _ok(fb["verdict"] == M.VERDICT_ETF,
            "B: and it becomes the headline, so the ladder is not stuck on the futures")

        # ------------------------------------------------------------ C: small surface
        def shrink_surface(face):
            face["pairs"]["IM"]["carry"]["median_ann_pct"] = 2.0

        clone = json.loads(json.dumps(basis))
        shrink_surface(clone)
        bpath = os.path.join(tmp, "basis_small.json")
        with open(bpath, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(clone, fh, ensure_ascii=False)
        old_basis = M.BASIS
        M.BASIS = bpath
        try:
            fc = M.build_face()
        finally:
            M.BASIS = old_basis
        _ok(fc["verdicts"][M.VERDICT_ARTIFACT] is False,
            "C: a 2pp surface reading cannot keep the artifact flag alive")
        _ok(fc["verdict"] == M.VERDICT_TIE,
            "C: with clean legs the headline falls to the tie (%s)" % fc["verdict"])

        # ------------------------------------------------------------ D: parent disturbed
        poisoned = os.path.join(tmp, "parent_disturbed.json")
        pc = json.loads(json.dumps(parent))
        pc["spec"]["periods_per_year"] = 13.0
        with open(poisoned, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(pc, fh, ensure_ascii=False)
        old = M.PARENT
        M.PARENT = poisoned
        try:
            import io
            from contextlib import redirect_stdout
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = M.check()
            out = buf.getvalue()
        finally:
            M.PARENT = old
        _ok(rc == 3, "D: a disturbed parent returns rc3 (got %d)" % rc)
        _ok("STALE" in out, "D: and says STALE")
        _ok("CHECK FAILED" not in out,
            "D: drift is not reported as an arithmetic disagreement")

        # ------------------------------------------------------------ E: page loses a token
        pub_md = os.path.join(tmp, "page_missing.json.md")
        body = open(M.OUT_MD, encoding="utf-8").read()
        face = json.load(open(M.OUT_JSON, encoding="utf-8"))
        stripped = body.replace("`%s`" % face["verdict"], "(verdict removed)")
        with open(pub_md, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(stripped)
        old_md = M.OUT_MD
        M.OUT_MD = pub_md
        try:
            import io
            from contextlib import redirect_stdout
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc_e = M.check()
            out_e = buf.getvalue()
        finally:
            M.OUT_MD = old_md
        _ok(rc_e == 1, "E: a page without the verdict token returns rc1 (got %d)" % rc_e)
        _ok("CHECK FAILED" in out_e, "E: and says CHECK FAILED")
        _ok("STALE" not in out_e, "E: a defect is not excused as drift")

        # ------------------------------------------------------------ F: missing face
        old_out = M.OUT_JSON
        M.OUT_JSON = os.path.join(tmp, "does_not_exist.json")
        try:
            import io
            from contextlib import redirect_stdout
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc_f = M.check()
            out_f = buf.getvalue()
        finally:
            M.OUT_JSON = old_out
        _ok(rc_f == 3 and "STALE" in out_f,
            "F: a missing published face is STALE, not a crash (rc=%d)" % rc_f)

        # ------------------------------------------------------------ G: live face self-consistent
        _ok(M.check() == 0, "G: the untouched published face still checks green")

    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    after = {p: _sha(p) for p in published if os.path.exists(p)}
    _ok(before == after, "the four published files are byte-identical after the control")

    print("%d/%d PASS" % (ok, ok + fail))
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

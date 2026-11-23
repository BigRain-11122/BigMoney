"""Negative control for r2024's daily-mark drawdown face.

The face's whole value is that it says "the budget does not hold".  A checker
that says OK no matter what is worth nothing, so this script tampers with a
copy of the published face and requires ``check()`` to name each tampering --
and then requires it to go green again, byte for byte, once the file is put
back.
"""

import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import astock_veto_hedge_daily as F  # noqa: E402

FACE = os.path.join(ROOT, "results", "astock_veto_hedge_daily.json")
ok_all = True


def _ok(cond, msg):
    global ok_all
    ok_all = ok_all and bool(cond)
    print(("  ok   " if cond else "  FAIL ") + msg)


def _silent(fn):
    import io
    import contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = fn()
    return rc, buf.getvalue()


def _run_case(name, mutate, expect_rc, expect_words=None):
    with tempfile.TemporaryDirectory() as td:
        copy = os.path.join(td, "face.json")
        shutil.copyfile(FACE, copy)
        payload = json.load(open(copy, encoding="utf-8"))
        mutate(payload)
        json.dump(payload, open(copy, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        old = F.OUT
        F.OUT = copy
        try:
            rc, out = _silent(F.check)
        finally:
            F.OUT = old
        words_ok = True
        if expect_words:
            words_ok = all(w in out for w in expect_words)
        _ok(rc == expect_rc and words_ok,
            "%s -> rc=%d (wanted %d)%s" % (name, rc, expect_rc,
                                          "" if words_ok else " [missing words: %s]" % expect_words))


def main():
    print("r2024 hedge-daily negative control")
    before = open(FACE, "rb").read()

    _ok(F.main(["--check"]) == 0, "the published face passes its own check untouched")

    _run_case("flip one budget verdict", lambda p: p["cells"]["0.20"].__setitem__(
        "verdict", "DAILY_MARKS_KEEP_THE_BUDGET"), 3, ["CHECK FAILED"])
    _run_case("shrink one daily drawdown below its period drawdown",
              lambda p: (p["curves"]["0.65"]["daily_dd"].__setitem__("full", 0.10),
                         p["curves"]["0.65"].__setitem__("ratio_full", 0.10 / p["curves"]["0.65"]["period_dd_full"])),
              3, ["CHECK FAILED"])
    _run_case("lie about the ratio", lambda p: p["curves"]["1.00"].__setitem__("ratio_full", 1.0),
              3, ["CHECK FAILED"])
    _run_case("change a period drawdown", lambda p: p["curves"]["0.35"].__setitem__(
        "period_dd_full", 0.05), 3, ["CHECK FAILED"])
    _run_case("truncate a curve", lambda p: p["curves"]["0.50"]["daily_dd"].pop("out_of_sample"),
              3, ["CHECK FAILED"])
    _run_case("drop the curves entirely", lambda p: p.__setitem__("curves", {}),
              3, ["CHECK FAILED"])

    _ok(open(FACE, "rb").read() == before, "the real face was never touched")
    rc = F.main(["--check"])
    _ok(rc == 0, "after every case the published face is still green (rc=%d)" % rc)
    print("NEGATIVE-CONTROL %s" % ("PASS" if ok_all else "FAIL"))
    return 0 if ok_all else 1


if __name__ == "__main__":
    raise SystemExit(main())

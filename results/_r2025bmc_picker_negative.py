"""Negative control for results/astock_veto_hedge_picker.json (r2025, bm-c).

Proves the face's own ``--check`` fails on each way the published numbers could
go wrong, and that the real face is not touched: every case copies the face to a
temp file, points the module's OUT at the copy through ``globals()``, mutates the
copy, and calls the real ``check()``.  The original is re-read byte for byte at
the end.

Nothing here writes to results/ except this script's own stdout.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import astock_veto_hedge_picker as F  # noqa: E402

REAL = F.OUT


def _sha(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def _run_case(label: str, mutate, expect_fail: bool = True) -> bool:
    tmpdir = tempfile.mkdtemp(prefix="picker_neg_")
    tmp = os.path.join(tmpdir, "face.json")
    try:
        shutil.copyfile(REAL, tmp)
        payload = json.load(open(tmp, encoding="utf-8"))
        mutate(payload)
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=1)
        F.OUT = tmp
        try:
            rc = F.check()
        finally:
            F.OUT = REAL
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
    ok = (rc != 0) if expect_fail else (rc == 0)
    print(("  ok   " if ok else "  FAIL ") + "%s -> rc=%d" % (label, rc))
    return ok


def main() -> int:
    ok = True
    print("astock_veto_hedge_picker negative control")
    before = _sha(REAL)
    base = json.load(open(REAL, encoding="utf-8"))

    F.OUT = REAL
    rc = F.check()
    ok &= (rc == 0)
    print(("  ok   " if rc == 0 else "  FAIL ") + "untouched face -> rc=%d" % rc)

    ok &= _run_case("one published out-of-sample drawdown changed", lambda p: (
        [c.update({"oos_dd": c["oos_dd"] + 0.01})
         for n in ("FIXED_ONE",) for c in [p["pickers"][n]["cells"]["0.20"]] if c.get("oos_dd")]))

    def _shift_k(p):
        cell = p["pickers"]["A_DAILY"]["cells"]["0.20"]
        cell["k"] = 0.95
    ok &= _run_case("a picker's chosen size moved", _shift_k)

    def _flip_holds(p):
        cell = p["pickers"]["B_DAILY"]["cells"]["0.20"]
        cell["holds"] = not cell["holds"]
    ok &= _run_case("a holds flag flipped", _flip_holds)

    def _drop_curve(p):
        p["curves"].pop("0.65", None)
    ok &= _run_case("a curve the picker points at removed", _drop_curve)

    def _invert_ruler(p):
        c = p["curves"]["0.50"]
        c["period"]["dd"] = c["daily"]["dd"] * 1.5
    ok &= _run_case("daily drawdown printed below the period drawdown (impossible)", _invert_ruler)

    def _deeper_is(p):
        c = p["curves"]["0.75"]
        c["daily"]["dd"] = c["daily_full"]["dd"] * 2.0
    ok &= _run_case("in-sample drawdown deeper than its own full window", _deeper_is)

    def _flip_race(p):
        p["race"]["0.20"]["verdict"] = "FITTING_ADDS_NOTHING"
    ok &= _run_case("race verdict contradicted by its own table", _flip_race)

    def _truncate(p):
        p["curves"] = {}
    ok &= _run_case("every curve deleted (must fail, not crash)", _truncate)

    def _unregistered(p):
        p["pickers"]["SHORTCUT"] = copy.deepcopy(p["pickers"]["FIXED_ONE"])
    ok &= _run_case("a picker that was never pre-registered", _unregistered)

    def _bogus_verdict(p):
        p["race"]["0.25"]["verdict"] = "LOOKS_GOOD_TO_ME"
    ok &= _run_case("a verdict outside the pre-registered set", _bogus_verdict)

    def _missing_reading(p):
        p["curves"]["1.00"].pop("daily_oos")
    ok &= _run_case("a curve missing its out-of-sample reading", _missing_reading)

    F.OUT = REAL
    rc = F.check()
    after = _sha(REAL)
    ok &= (rc == 0 and after == before)
    print(("  ok   " if rc == 0 and after == before else "  FAIL ")
          + "real face untouched and still green (sha %s)" % after[:16])

    def _as_is(p):
        return None
    ok &= _run_case("unmodified copy still passes", _as_is, expect_fail=False)

    print("NEGATIVE %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

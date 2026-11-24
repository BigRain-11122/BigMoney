"""r2036 negative control: does the funding face move when its own inputs move?

Every assertion here is the opposite of what the published face says, so a green run is evidence
the verdict is computed rather than written down.  Nothing on disk is left changed.
"""
from __future__ import annotations

import importlib.util
import io
import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPEC = os.path.join(ROOT, "scripts", "astock_veto_hedge_funding.py")

legs = []


def leg(name, ok, detail=""):
    legs.append((name, bool(ok), detail))


def load_module():
    spec = importlib.util.spec_from_file_location("_r2036bmc_funding", SPEC)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def dump(path, face):
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")


def main() -> int:
    mod = load_module()
    tmp = tempfile.mkdtemp(prefix="r2036bmc_")
    published = {p: open(p, "rb").read() for p in (mod.OUT_JSON, mod.OUT_MD)}
    orig = {name: getattr(mod, name) for name in
            ("PARENT", "CARRIER", "MARGIN", "OUT_JSON", "OUT_MD")}
    base = json.load(open(mod.OUT_JSON, encoding="utf-8"))
    try:
        # --- 1. rent at zero: the tie comes back, and the ranking stops flipping
        zero_rent = json.loads(json.dumps(base))
        for kkey, cell in (zero_rent.get("net_of_borrow", {}).get("etf") or {}).items():
            for fkey in list(cell):
                cell[fkey]["annualized_compound"] = (
                    (base.get("gross") or {}).get("etf", {}).get(kkey, {})
                    .get("annualized_compound"))
        zero_rent["net_gap_pp"] = {f: base.get("gross_gap_pp") for f in base.get("net_gap_pp") or {}}
        zero_rent["funded_gap_pp"] = {f: 0.1 for f in base.get("funded_gap_pp") or {}}
        zero_rent["verdicts"] = mod.decide(base.get("gross_gap_pp") or 0.0,
                                           zero_rent["net_gap_pp"], zero_rent["funded_gap_pp"],
                                           base.get("funded_rows") or [], 
                                           next(r for r in base["funded_rows"]
                                                if r["carrier"] == "im"),
                                           base["spec"]["im_cash_cny"],
                                           base["spec"]["im_cash_sweep_cny"],
                                           base.get("ref_haircut"))
        zero_rent["verdict"] = mod.headline(zero_rent["verdicts"])
        leg("N1 with no rent the gross-tie flag goes off",
            zero_rent["verdicts"][mod.VERDICT_GROSS] is False, zero_rent["verdict"])
        # the flip reads the FUNDED gap, so the same zero-rent face still flips when the funded
        # gap keeps the futures leg ahead -- and stops flipping when it does not
        ahead = json.loads(json.dumps(zero_rent))
        ahead["funded_gap_pp"] = {f: 0.1 for f in zero_rent["funded_gap_pp"]}
        ahead["verdicts"] = mod.decide(base.get("gross_gap_pp") or 0.0, ahead["net_gap_pp"],
                                       ahead["funded_gap_pp"], base["funded_rows"],
                                       next(r for r in base["funded_rows"]
                                            if r["carrier"] == "im"),
                                       base["spec"]["im_cash_cny"],
                                       base["spec"]["im_cash_sweep_cny"],
                                       base.get("ref_haircut"))
        leg("N1b the flip needs a positive funded gap, not just a negative gross one",
            ahead["verdicts"][mod.VERDICT_FLIP] is True
            and ahead["verdicts"][mod.VERDICT_GROSS] is False)
        behind = json.loads(json.dumps(ahead))
        behind["funded_gap_pp"] = {f: -0.2 for f in ahead["funded_gap_pp"]}
        behind["verdicts"] = mod.decide(base.get("gross_gap_pp") or 0.0, behind["net_gap_pp"],
                                        behind["funded_gap_pp"], base["funded_rows"],
                                        next(r for r in base["funded_rows"]
                                             if r["carrier"] == "im"),
                                        base["spec"]["im_cash_cny"],
                                        base["spec"]["im_cash_sweep_cny"],
                                        base.get("ref_haircut"))
        leg("N1c a funded gap that keeps the ETF leg ahead kills the flip",
            behind["verdicts"][mod.VERDICT_FLIP] is False)

        # --- 2. a futures block as thin as the 12% ratio: the collateral flag goes off
        thin = json.loads(json.dumps(base))
        im_row = next(r for r in thin["funded_rows"] if r["carrier"] == "im")
        im_row["collateral_cny"] = 90_000.0        # above the ETF block's give-up
        thin["verdicts"] = mod.decide(thin.get("gross_gap_pp") or 0.0, thin.get("net_gap_pp"),
                                      thin.get("funded_gap_pp"), thin["funded_rows"], im_row,
                                      thin["spec"]["im_cash_cny"],
                                      thin["spec"]["im_cash_sweep_cny"],
                                      thin.get("ref_haircut"))
        leg("N2 a thin futures block makes the collateral flag go off",
            thin["verdicts"][mod.VERDICT_COLLATERAL] is False)
        leg("N2b but the gross-tie flag stands on its own input",
            thin["verdicts"][mod.VERDICT_GROSS] is True)

        # --- 3. a parent that moved must be STALE, not a defect
        moved = json.loads(json.dumps(base))
        moved["parents"]["carrier"]["file_sha256"] = "0" * 64
        dump(os.path.join(tmp, "stale.json"), moved)
        mod.OUT_JSON = os.path.join(tmp, "stale.json")
        rc = mod.check()
        leg("N3 a moved parent is STALE (rc 3)", rc == 3, "rc=%s" % rc)

        # --- 4. a tampered number with every parent untouched is CHECK FAILED
        mod.OUT_JSON = orig["OUT_JSON"]
        poisoned = json.loads(json.dumps(base))
        poisoned["funded_rows"][-1]["funded_ann"] = (
            (poisoned["funded_rows"][-1]["funded_ann"] or 0.0) + 0.0123)
        dump(os.path.join(tmp, "face.json"), poisoned)
        mod.OUT_JSON = os.path.join(tmp, "face.json")
        rc = mod.check()
        leg("N4 a tampered funded return is CHECK FAILED (rc 1)", rc == 1, "rc=%s" % rc)

        # --- 5. a page that lost the verdict token is CHECK FAILED
        mod.OUT_JSON = orig["OUT_JSON"]
        pm = os.path.join(tmp, "face.md")
        with io.open(pm, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(open(orig["OUT_MD"], encoding="utf-8").read().replace(
                "`%s`" % base["verdict"], "removed"))
        mod.OUT_MD = pm
        rc = mod.check()
        leg("N5 a page missing its verdict token is CHECK FAILED (rc 1)", rc == 1, "rc=%s" % rc)

        # --- 6. a missing face is STALE, and does not crash
        mod.OUT_MD = orig["OUT_MD"]
        mod.OUT_JSON = os.path.join(tmp, "nope.json")
        rc = mod.check()
        leg("N6 a missing face is STALE (rc 3)", rc == 3, "rc=%s" % rc)

        # --- 7. the published files are untouched
        mod.OUT_JSON, mod.OUT_MD = orig["OUT_JSON"], orig["OUT_MD"]
        leg("N7 the published face is byte-identical after the poison run",
            all(open(p, "rb").read() == published[p] for p in published))
        leg("N7b and it still checks clean", mod.check() == 0)
    finally:
        for name, value in orig.items():
            setattr(mod, name, value)
        shutil.rmtree(tmp, ignore_errors=True)

    width = max(len(n) for n, _, _ in legs) + 2
    bad = 0
    for name, ok, detail in legs:
        if not ok:
            bad += 1
        print("%s %-*s %s" % ("PASS" if ok else "FAIL", width, name, detail))
    print("%d/%d PASS" % (len(legs) - bad, len(legs)))
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

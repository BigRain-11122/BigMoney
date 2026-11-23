"""r2035 negative control: does the margin face move when its own inputs move?

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
SPEC = os.path.join(ROOT, "scripts", "astock_veto_hedge_margin.py")

legs = []


def leg(name, ok, detail=""):
    legs.append((name, bool(ok), detail))


def load_module():
    spec = importlib.util.spec_from_file_location("_r2035bmc_margin", SPEC)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def write_series(path, rows):
    with io.open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write("date,open,high,low,close,volume,oi,settle\n")
        for d, c in rows:
            fh.write("%s,%.4f,%.4f,%.4f,%.4f,1,1,0\n" % (d, c, c, c, c))


def business_days(n, start=1000.0):
    out = []
    y, m, d = 2022, 7, 22
    import datetime
    cur = datetime.date(y, m, d)
    price = start
    for i in range(n):
        out.append((cur.isoformat(), price))
        price *= 1.0
        cur += datetime.timedelta(days=1)
        while cur.weekday() >= 5:
            cur += datetime.timedelta(days=1)
    return out


def main() -> int:
    mod = load_module()
    tmp = tempfile.mkdtemp(prefix="r2035bmc_")
    published = {p: open(p, "rb").read() for p in (mod.OUT_JSON, mod.OUT_MD)}
    orig_panel = mod.IM_CSV
    orig_json, orig_md = mod.OUT_JSON, mod.OUT_MD
    base = mod._read_json(mod.OUT_JSON)
    try:
        # --- 1. a panel that only ever rises: the short is bled dry
        dates = [d for d, _ in mod.load_series(orig_panel)]
        rising = [(d, 5000.0 * (1.0008 ** i)) for i, d in enumerate(dates)]
        p1 = os.path.join(tmp, "rising.csv")
        write_series(p1, rising)
        mod.IM_CSV = p1
        f1 = mod.build_face()
        ns1 = ((f1.get("required_margin_cny") or {}).get("no_sweep") or {}).get("0.12", 0.0)
        base_ns = ((base.get("required_margin_cny") or {}).get("no_sweep") or {}).get("0.12", 0.0)
        leg("N1 a rising index makes the account need more cash than the published path",
            ns1 > base_ns * 1.8, "%.0f vs %.0f" % (ns1, base_ns))
        leg("N1b and the early-call flag stays on",
            (f1.get("verdicts") or {}).get(mod.VERDICT_EARLY) is True)

        # --- 2. a panel that only ever falls: no call at all
        falling = [(d, 5000.0 / (1.0008 ** i)) for i, d in enumerate(dates)]
        p2 = os.path.join(tmp, "falling.csv")
        write_series(p2, falling)
        mod.IM_CSV = p2
        f2 = mod.build_face()
        leg("N2 a falling index is never called",
            all((r["no_sweep"]["first_breach_index"] is None) for r in f2.get("ladder") or []))
        leg("N2b so the verdict is the opposite of the published one",
            f2.get("verdict") == "ACCOUNT_SURVIVES_AS_POSTED", f2.get("verdict"))

        # --- 3. a panel that moved must be STALE, not a defect
        mod.IM_CSV = orig_panel
        moved = os.path.join(tmp, "moved.csv")
        shutil.copyfile(orig_panel, moved)
        with io.open(moved, "a", encoding="utf-8", newline="") as fh:
            fh.write("2026-11-23,5500,5500,5500,5500,1,1,0\n")
        mod.IM_CSV = moved
        rc = mod.check()
        leg("N3 a moved panel is STALE (rc 3)", rc == 3, "rc=%s" % rc)

        # --- 4. a tampered number with the panel untouched is CHECK FAILED, not STALE
        mod.IM_CSV = orig_panel
        poisoned = json.loads(json.dumps(base))
        key = "%.2f" % 0.12
        poisoned["required_margin_cny"]["no_sweep"][key] = (
            poisoned["required_margin_cny"]["no_sweep"][key] + 12_345.0)
        pj = os.path.join(tmp, "face.json")
        with io.open(pj, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(poisoned, fh, ensure_ascii=False, indent=1, sort_keys=True)
            fh.write("\n")
        mod.OUT_JSON = pj
        rc = mod.check()
        leg("N4 a tampered required-cash number is CHECK FAILED (rc 1)", rc == 1, "rc=%s" % rc)

        # --- 5. a page that lost the verdict token is CHECK FAILED
        mod.OUT_JSON = orig_json
        pm = os.path.join(tmp, "face.md")
        with io.open(pm, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(open(orig_md, encoding="utf-8").read().replace(
                "`%s`" % base["verdict"], "removed"))
        mod.OUT_MD = pm
        rc = mod.check()
        leg("N5 a page missing its verdict token is CHECK FAILED (rc 1)", rc == 1, "rc=%s" % rc)

        # --- 6. a missing face is STALE, and does not crash
        mod.OUT_JSON = os.path.join(tmp, "nope.json")
        rc = mod.check()
        leg("N6 a missing face is STALE (rc 3)", rc == 3, "rc=%s" % rc)

        # --- 7. the four published files are untouched
        mod.OUT_JSON, mod.OUT_MD = orig_json, orig_md
        leg("N7 the published face is byte-identical after the poison run",
            all(open(p, "rb").read() == published[p] for p in published))
        leg("N7b and it still checks clean", mod.check() == 0)
    finally:
        mod.IM_CSV = orig_panel
        mod.OUT_JSON, mod.OUT_MD = orig_json, orig_md
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

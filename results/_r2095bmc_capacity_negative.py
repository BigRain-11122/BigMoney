#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""negative control for scripts/idx_fut_carry_capacity_lots.py (r2095 bm-c)

Proves the capacity face is red-capable and that its own choices matter:
  N1  an absent contract panel must refuse (DATA_BLOCKED), never extrapolate one lot
  N2  halving every volume must halve the capacity in lots (the ladder is not a constant)
  N3  a 30x desk rung must move the verdict from "market is not the gate" to "capacity bites"
  N4  a hand-edited adopted_lots with an unchanged panel must be CHECK FAILED, and the
      message must NOT claim STALE (r1850: the word is a contract, not a description)
  N5  a hand-edited panel digest must be STALE, and must say so
  N6  quoting the median-ADV leg instead of the binding leg overstates capacity by >2x
Exit 0 = every control fired.
"""
import importlib
import io
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

mod = importlib.import_module("idx_fut_carry_capacity_lots")

results = []


def leg(name, ok, detail=""):
    results.append((name, bool(ok), detail))


def capture(fn):
    """(rc, stdout) for a check-style call."""
    buf = io.StringIO()
    old = sys.stdout
    sys.stdout = buf
    try:
        rc = fn()
    finally:
        sys.stdout = old
    return rc, buf.getvalue()


base = mod.derive()
leg("baseline derives", base["verdict"] in mod.VERDICTS, base["verdict"])
ok_rows = {p: r for p, r in base["products"].items() if r.get("status") == "ok"}

# N1 -- an absent panel must refuse
tmp = tempfile.mkdtemp(prefix="r2095neg_empty_")
try:
    blocked = mod.derive(fut_dir=tmp)
finally:
    shutil.rmtree(tmp, ignore_errors=True)
leg("N1 empty panel refuses", blocked["verdict"] == mod.V_BLOCK, blocked.get("verdict", ""))

# N2 -- halving volume halves capacity
orig_load = mod.load_contracts


def halved(prod, fut_dir=None):
    cs = orig_load(prod, fut_dir)
    return {n: {d: (v * 0.5, h, c) for d, (v, h, c) in rows.items()}
            for n, rows in cs.items()}


mod.load_contracts = halved
try:
    half = mod.derive()
finally:
    mod.load_contracts = orig_load
half_rows = {p: r for p, r in half["products"].items() if r.get("status") == "ok"}
ratios = {p: half_rows[p]["capacity"]["adopted_lots"] / ok_rows[p]["capacity"]["adopted_lots"]
          for p in half_rows if p in ok_rows}
leg("N2 halving volume halves lots", all(abs(r - 0.5) < 1e-3 for r in ratios.values()),
    str({p: round(v, 4) for p, v in ratios.items()}))

# N3 -- a 30x desk rung must flip the verdict to CAPACITY_BITES
spec = mod._read_json(mod.SPEC_PATH) or {}
price = mod._read_json(mod.PRICE_PATH) or {}
scaled = json.loads(json.dumps(spec))
for prod in mod.PRODUCTS:
    acct = (scaled.get("accounts") or {}).get(prod) or {}
    for rung in acct.get("capital_rungs") or []:
        if int(rung.get("lots", 0)) >= 1:
            rung["lots"] = int(rung["lots"]) * 30
            rung["capital_cny"] = float(rung["capital_cny"]) * 30
flipped = [mod.price_product(p, price, scaled) for p in mod.PRODUCTS]
worst = min(r["headroom_multiple"] for r in flipped if r.get("status") == "ok")
leg("N3 30x rung makes capacity bite", worst < mod.DISTANT, "worst headroom=%.2fx" % worst)

# N4 -- a hand-edited number is a defect, not staleness
tmp2 = tempfile.mkdtemp(prefix="r2095neg_edit_")
saved_out = mod.OUT_PATH
try:
    publish = mod.derive()
    fake = json.loads(json.dumps(publish))
    fake["products"]["IC"]["capacity"]["adopted_lots"] += 1.0
    path = os.path.join(tmp2, "face.json")
    with io.open(path, "w", encoding="utf-8") as fh:
        json.dump(fake, fh, ensure_ascii=False)
    mod.OUT_PATH = path
    rc4, text4 = capture(lambda: mod.check(quiet=True))

    fake2 = json.loads(json.dumps(publish))
    fake2["products"]["IC"]["window_digest"] = "0" * 64
    with io.open(path, "w", encoding="utf-8") as fh:
        json.dump(fake2, fh, ensure_ascii=False)
    rc5, text5 = capture(lambda: mod.check(quiet=True))
finally:
    mod.OUT_PATH = saved_out
    shutil.rmtree(tmp2, ignore_errors=True)
leg("N4 edited number -> rc3 and no STALE word",
    rc4 == 3 and "STALE" not in text4 and "CHECK FAILED" in text4,
    "rc=%s has_STALE=%s" % (rc4, "STALE" in text4))
leg("N5 moved digest -> rc3 with STALE word",
    rc5 == 3 and "STALE" in text5, "rc=%s" % rc5)

# N6 -- the binding leg is not the median leg
gaps = {}
for prod, row in ok_rows.items():
    median_lots = row["legs"]["adv20_median"]["lots_at_primary"]
    gaps[prod] = median_lots / row["capacity"]["adopted_lots"]
leg("N6 median leg overstates capacity >2x", all(g > 2.0 for g in gaps.values()),
    str({p: round(v, 2) for p, v in gaps.items()}))

passed = sum(1 for _n, ok, _d in results if ok)
for name, ok, detail in results:
    print(("PASS " if ok else "FAIL ") + name + (("  [" + detail + "]") if detail else ""))
print("NEGATIVE-CONTROL %d/%d" % (passed, len(results)))
sys.exit(0 if passed == len(results) else 1)

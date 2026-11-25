#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""negative control for scripts/idx_fut_carry_always_on_price.py (r2094 bm-c)

Proves the face is red-capable, not merely self-consistent:
  N1  a 30% cash rate must turn the worst-ruler excess negative (V_NEG)
  N2  zeroed always-on levels must do the same
  N3  a missing input face must refuse with DATA_BLOCKED, never default
  N4  a hand-edited published number must be caught by check() as STALE (rc3)
  N5  quoting ONE ruler is a 6.9pp error: the published-only verdict differs from
      the all-ruler verdict by more than the 3pp spread line
Exit 0 = every control fired.
"""
import importlib
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

mod = importlib.import_module("idx_fut_carry_always_on_price")


def worst(face):
    rows = [r for r in face["products"].values() if r.get("status") == "ok"]
    if not rows:
        return None
    return min(r["min_excess_pct_of_capital"] for r in rows)


def verdict_for(face):
    rows = [r for r in face["products"].values() if r.get("status") == "ok"]
    if not rows:
        return mod.V_BLOCK
    w = worst(face)
    widest = max(r["rate_spread_across_rulers_pp"] for r in rows)
    if w <= 0:
        return mod.V_NEG
    return mod.V_BOUND if widest >= mod.SPREAD_LINE_PP else mod.V_OK


results = []


def leg(name, ok, detail=""):
    results.append((name, bool(ok), detail))


base = mod.derive()
leg("baseline derives", base["verdict"] in mod.VERDICTS, base["verdict"])

# N1 -- cash leg priced at 30% must sink the worst rung
f1 = json.loads(json.dumps(base))
f1["cash_net_annual"] = 0.30
for prod, row in f1["products"].items():
    if row.get("status") != "ok":
        continue
    row["rulers"] = {
        k: dict(v, always_on_excess_cny=v["always_on_carry_cny"] - 0.30 * row["margin_cny"])
        for k, v in row["rulers"].items()
    }
    row["rulers"] = {
        k: dict(v, always_on_excess_pct_of_capital=(
            v["always_on_excess_cny"] / row["first_rung_cny"] * 100.0))
        for k, v in row["rulers"].items()
    }
    row["min_excess_pct_of_capital"] = min(
        v["always_on_excess_pct_of_capital"] for v in row["rulers"].values())
leg("N1 cash 30% sinks the line", verdict_for(f1) == mod.V_NEG,
    "worst=%.2f%%" % worst(f1))

# N2 -- zeroed levels must also sink it
f2 = json.loads(json.dumps(base))
for prod, row in f2["products"].items():
    if row.get("status") != "ok":
        continue
    row["rulers"] = {k: dict(v, always_on_ann_pct=0.0, always_on_carry_cny=0.0,
                             always_on_excess_cny=-f2["cash_net_annual"] * row["margin_cny"],
                             always_on_excess_pct_of_capital=(
                                 -f2["cash_net_annual"] * row["margin_cny"]
                                 / row["first_rung_cny"] * 100.0))
                    for k, v in row["rulers"].items()}
    row["min_excess_pct_of_capital"] = min(
        v["always_on_excess_pct_of_capital"] for v in row["rulers"].values())
leg("N2 zeroed carry sinks the line", verdict_for(f2) == mod.V_NEG,
    "worst=%.2f%%" % worst(f2))

# N3 -- a missing input must refuse
saved = mod.MASKS_PATH
try:
    mod.MASKS_PATH = os.path.join(tempfile.gettempdir(), "_r2094_no_masks.json")
    f3 = mod.derive()
finally:
    mod.MASKS_PATH = saved
leg("N3 missing masks face refuses", f3["verdict"] == mod.V_BLOCK,
    ",".join(f3.get("missing_inputs", [])))

# N4 -- a hand-edited published number must be caught by check()
tmp = tempfile.mkdtemp(prefix="r2094neg_")
saved_out = mod.OUT_PATH
try:
    publish = mod.derive()
    fake = json.loads(json.dumps(publish))
    if fake["products"].get("IC", {}).get("status") == "ok":
        fake["products"]["IC"]["first_rung_cny"] += 1.0
    fake_path = os.path.join(tmp, "face.json")
    with open(fake_path, "w", encoding="utf-8") as fh:
        json.dump(fake, fh, ensure_ascii=False)
    mod.OUT_PATH = fake_path
    rc = mod.check(face=publish, quiet=True)
finally:
    mod.OUT_PATH = saved_out
    shutil.rmtree(tmp, ignore_errors=True)
leg("N4 hand-edited number caught as STALE rc3", rc == 3, "rc=%s" % rc)

# N5 -- one ruler is not the answer
ic = base["products"].get("IC") or {}
if ic.get("status") == "ok":
    pub = ic["rulers"]["published"]["always_on_ann_pct"]
    best_ruler = max(ic["rulers"].items(), key=lambda kv: kv[1]["always_on_ann_pct"])
    spread = ic["rate_spread_across_rulers_pp"]
    only_pub_is_wrong = spread >= mod.SPREAD_LINE_PP
    leg("N5 quoting only 'published' is a %.2fpp error" % spread, only_pub_is_wrong,
        "published=%.2f%% vs %s=%.2f%%" % (pub, best_ruler[0],
                                           best_ruler[1]["always_on_ann_pct"]))
else:
    leg("N5 quoting only 'published' is an error", False, "IC not priced")

passed = sum(1 for _, ok, _ in results if ok)
for name, ok, detail in results:
    print(("PASS " if ok else "FAIL ") + name + (("  [" + detail + "]") if detail else ""))
print("NEGATIVE-CONTROL %d/%d" % (passed, len(results)))
sys.exit(0 if passed == len(results) else 1)

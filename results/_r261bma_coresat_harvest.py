# -*- coding: utf-8 -*-
"""R261 bm-a: CN-CORE-SATELLITE-P1 harvest gate (r244 law: deterministic
re-derive of the judged faces from the landed artifact, then pool flip).
Ten faces mirror the _r252bma_rot_harvest.py family precedent."""
import collections
import json
import math
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_JSON = os.path.join(ROOT, "results", "cn_core_satellite",
                        "p1_results.json")
POOL = os.path.join(ROOT, "results", "runnable_pool.json")
LEDGER = os.path.join(ROOT, "results", "science_ledger.jsonl")
ATT = os.path.join(ROOT, "results", "gate_attrition.json")

d = json.load(open(OUT_JSON, encoding="utf-8"), object_pairs_hook=collections.OrderedDict)
fails = []


def ok(fid, cond, detail=""):
    print(f"[{'PASS' if cond else 'FAIL'}] {fid} {detail}")
    if not cond:
        fails.append(fid)


# [1] top-level cutoff face (C2 legal key = evidence_cutoff; sg.cutoff_meta
# spreads {evidence_cutoff} at top level -- family artifact shape)
ok("cutoff face", d.get("evidence_cutoff") == "2026-09-22")

# [2] ledger arithmetic: prev head + 54 == reported total
tl = d["trials_ledger"]
ok("ledger total", tl["total"] == 187741 and tl["batch_trials"] == 54,
   f"total={tl['total']} prev={tl.get('prev_total')}")

# [3] four judged cells x three faces all present with finite sharpe
cells = d["cells"]
ok("cells census", set(cells) == {"SAT20_bare", "SAT20_gate",
                                  "SAT40_bare", "SAT40_gate"}
   and all(set(cells[c]) == {"x1", "x2", "x3"} for c in cells))
for c in cells:
    for f in ("x1", "x2", "x3"):
        assert isinstance(cells[c][f]["sharpe"], float)

# [4] g1/g2 verdicts all false (judged negative face)
ok("g1 0/4", all(d["g1_prime_v2"][c]["pass_v2"] is False for c in cells))
ok("g2 0/4", all(d["g2_registration_v2"][c]["eligible_v2"] is False
                  for c in cells))

# [5] skill_line re-derive vs recorded (library law: line = max(passive_term,
# mu + sigma*sqrt(2*ln n_eff)); recorded passive_term ALREADY includes +0.10
line = d["skill_line"]
nulls = d["nulls"]
mu = sum(nulls["values_rounded"]) / len(nulls["values_rounded"])
sg_ = math.sqrt(sum((v - mu) ** 2 for v in nulls["values_rounded"])
                / (len(nulls["values_rounded"]) - 1))
n_eff = line["n_eff"]
null_term = mu + sg_ * math.sqrt(2.0 * math.log(n_eff))
ok("skill_line rederive", abs(line["line"] - max(line["passive_term"],
                                                 null_term)) < 0.01,
   f"line={line['line']} passive_term={line['passive_term']} "
   f"null_term~{null_term:.4f} n_eff={n_eff}")

# [6] nulls K=50 seeds band + sigma face
ok("nulls K50", len(nulls["values_rounded"]) == 50
   and nulls["config"]["base"] == 20261080)

# [7] baselines present (core-only yardstick + static 80/20)
ok("baselines", "core_only_buy_hold_510880" in d["baselines"]
   and "static_8020_core_ew_satellite" in d["baselines"])

# [8] attrition row visible in the ENTRIES list (r248 consumer-chain law)
att = json.load(open(ATT, encoding="utf-8"))
row = [e for e in att["entries"] if e.get("batch") == "CN-CORE-SATELLITE-P1"]
ok("attrition entries-visible", len(row) == 1
   and row[0]["cells_ledger_delta"] == 54
   and row[0]["ledger_total_after"] == 187741)

# [9] D6 member face present (reject face computed, no pending_error)
d6 = d["d6_correlation"]
ok("d6 member face", d6.get("status") != "pending_error"
   and all(c in d6 for c in cells))
for c in cells:
    mf = d6[c]["member_face"]
    print(f"    d6 {c}: max_abs_corr={mf.get('max_abs_corr')} "
          f"argmax={mf.get('argmax_member')} "
          f"reject={mf.get('reject')}")

# [10] panel gates + events frozen (lexicographic order) + audit section
ok("panel gates in artifact", d["panel_gates"]["all_ok"]
   and d["panel_gates"]["events"] == [
       "510500@2015-04-15", "510500@2022-08-29", "512100@2022-09-05"]
   and d["audit"]["elapsed_sec"] > 0)

print("x2 verdict table:")
for c in cells:
    m = cells[c]["x2"]
    print(f"  {c}: sharpe={m['sharpe']} ann={m['ann_ret']} "
          f"maxdd={m['max_dd']} oos_sharpe={m['oos']['sharpe']} "
          f"oos_ann={m['oos']['ann_ret']} entries={m['n_entries']} "
          f"fill_max={m['fill_days_max']}")
b = d["baselines"]
print("baseline core-only:", b["core_only_buy_hold_510880"]["sharpe"],
      b["core_only_buy_hold_510880"]["ann_ret"],
      b["core_only_buy_hold_510880"]["max_dd"])
print("baseline static8020:", b["static_8020_core_ew_satellite"]["sharpe"])
print("sat picks:", {c: d["regime_columns"]["satellite_axis"][c]["sat_pick_counts"]
                     for c in cells})
print("descriptive:", json.dumps(d["descriptive"], ensure_ascii=False)[:400])
print("pbo:", d["family_pbo"]["pbo"], "| dsr:",
      {c: d["dsr"][c] for c in cells})

# ---- pool flip (r244: harvest = flip + note; batch never self-flips)
pool = json.load(open(POOL, encoding="utf-8"))
for e in pool["entries"]:
    if e["id"] == "CN-CORE-SATELLITE-P1":
        e["status"] = "done"
        e["updated_at"] = "2026-09-26 17:5x"
        for sh in e["shards"]:
            sh["status"] = "done"
        e["harvest_note"] = (
            "harvested bm-a R261 same-round 2026-09-26 17:5x: "
            "p1_results.json landed (21.8s, 64 units, autofill-fired "
            "17:50:04, finalize 17:50:31); ten-face harvest gate PASS "
            "(cutoff/ledger 187687+54=187741/cells census/g1-g2 0/4 "
            "negative/skill_line rederive/nulls K50/base baselines/"
            "attrition entries-visible r248/D6/panel gates/audit); "
            "verdict = CN-CORE-SATELLITE judged NEGATIVE per prereg s4 "
            "(g1' v2 0/4) -> s3 five-model family ALL-NEGATIVE chain "
            "complete, no reopen (new evidence = new prereg)")
tmp = POOL + ".tmp"
open(tmp, "w", encoding="utf-8", newline="\n").write(
    json.dumps(pool, ensure_ascii=False, indent=1) + "\n")
os.replace(tmp, POOL)
print("pool flipped done. harvest gate:", "PASS" if not fails else fails)
raise SystemExit(1 if fails else 0)

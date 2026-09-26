"""R256 bm-a: deterministic harvest gate for CN-REGIME-POLICY-P1 (r244 law).

Re-derives the landed batch's gates from the stored artifact (zero
re-run of the sim), refuses on any mismatch, then flips the pool entry
+ shard to done with a harvest_note (batch never flips itself).

Checks (deterministic re-derive):
 1. landed marker: p1_results.json exists with trials_ledger block
 2. ledger arithmetic: prev_total + batch_trials == total
 3. cutoff_meta evidence_cutoff == 2026-09-22 at top level
 4. panel gates all true (rows/first/cutoff/NaN/volume/cover/monotonic)
 5. A-face re-derive: 3-condition AND from stored fields
 6. B-face re-derive: p_one_sided_A within [1/495, 1.0] and signal flag
    consistent with p<=0.05
 7. C-face: all three cells' g1 pass_v2 flags stored + line > best cell
 8. N census: n_trials==993, nulls family counts 495+495, cells 3
 9. attrition row visible in the ENTRIES list (r248 consumer law)
10. pool entry CN-REGIME-POLICY-P1 exists and is flipped ready->done
"""
import io
import json
import time

POOL = "results/runnable_pool.json"
ART = "results/cn_regime_policy/p1_results.json"
ATT = "results/gate_attrition.json"

j = json.load(io.open(ART, encoding="utf-8"))

# 1. landed marker
led = j.get("trials_ledger")
assert led, "no trials_ledger block (landed-marker law)"

# 2. ledger arithmetic
assert led["prev_total"] + led["batch_trials"] == led["total"], \
    f"ledger arithmetic broken: {led}"
assert (led["prev_total"], led["batch_trials"], led["total"]) == \
    (186592, 993, 187585), f"unexpected ledger faces: {led}"

# 3. cutoff lockbox (sg.cutoff_meta spreads {"evidence_cutoff": ...}
#    at top level -- the C2 legal key)
assert j["evidence_cutoff"] == "2026-09-22", "cutoff drift"

# 4. panel gates
g = j["panel_gates"]
for k in ("rows_ok", "first_ok", "cutoff_ok", "ohlcv_nan_free",
          "volume_positive", "monotonic_dates", "v3_full_cover"):
    assert g.get(k) is True, f"panel gate red: {k}"
assert sorted(g["v3_states_known"]) == ["GREEN", "ORANGE", "RED", "YELLOW"]

# 5. A-face re-derive
a = j["a_face_model_question"]
exp = bool(a["full_sharpe_c2"] > a["full_sharpe_c1"]
           and a["oos_sharpe_c2"] > a["oos_sharpe_c1"]
           and a["full_maxdd_c2"] > a["full_maxdd_c1"])
assert exp == a["policy_axis_value"] == False, \
    f"A-face re-derive mismatch: {a}"

# 6. B-face re-derive
b = j["b_face_month_set_signal"]
assert 1.0 / 495 - 1e-9 <= b["p_one_sided_A"] <= 1.0, "p out of range"
assert b["signal_A"] == (b["p_one_sided_A"] <= 0.05) == False, \
    f"B-face re-derive mismatch: {b}"

# 7. C-face
cells = ("v3_base", "v3_policy", "policy_only")
best = max(j["cells"][c]["x2"]["sharpe"] for c in cells)
line = j["skill_line"]["line"]
for c in cells:
    assert j["g1_prime_v2"][c]["pass_v2"] is False, \
        f"unexpected g1 pass: {c}"
    assert j["g2_registration_v2"][c]["eligible_v2"] is False, \
        f"unexpected g2 pass: {c}"
assert best < line, "line/best inconsistency for a 0/3 verdict"

# 8. N census
assert j["n_trials"] == 993
assert j["nulls"]["family_A_ladder_shaped"]["n_sets"] == 495
assert j["nulls"]["family_B_calendar_only"]["n_sets"] == 495
assert len(j["cells"]) == 3

# 9. attrition row visible in ENTRIES (r248 consumer law)
att = json.load(io.open(ATT, encoding="utf-8"))
rows = [r for r in att["entries"] if r.get("batch") == "CN-REGIME-POLICY-P1"]
assert rows, "attrition row not visible in entries list"
assert rows[-1]["cells_ledger_delta"] == 993
assert rows[-1]["ledger_total_after"] == 187585

# 10. pool flip ready -> done + harvest_note
p = json.load(io.open(POOL, encoding="utf-8"))
e = [x for x in p["entries"] if x.get("id") == "CN-REGIME-POLICY-P1"][0]
assert e["status"] in ("ready", "running"), f"unexpected status {e['status']}"
ts = time.strftime("%Y-%m-%d %H:%M:%S")
e["status"] = "done"
e["updated_at"] = ts
sh = e["shards"][0]
assert sh["key"] == "regimepolicy-0of1"
sh["status"] = "done"
sh["owner"] = "bm-a"
sh["owner_since"] = ts
e["harvest_note"] = (
    "harvested bm-a r256 same-round 2026-09-26 ~16:2x: p1_results.json "
    "landed (28.7s, 993 units, zero RNG exhaustive C(12,4)x2 nulls); "
    "R256 bm-a deterministic harvest gate PASS (10-face re-derive: "
    "ledger 186592+993=187585 arithmetic, cutoff lockbox 2026-09-22, "
    "panel gates, A-face 3-condition AND re-derived FALSE, B-face "
    "p=0.7798 re-derived no-signal, C-face 0/3 vs line 0.5691, N "
    "census 3+495+495, attrition row entries-visible); VERDICT "
    "CN-REGIME-POLICY judged NEGATIVE per frozen prereg (A/B/C all "
    "fail) -> no paper account, family slot closed, new-evidence-reopen "
    "law applies")
p["updated_at"] = ts
with io.open(POOL, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(p, fh, ensure_ascii=False, indent=1)

print("HARVEST PASS: CN-REGIME-POLICY-P1 pool entry+shard flipped done")
print("verdict: A-face FALSE / B-face no-signal / C-face 0/3 -> NEGATIVE")

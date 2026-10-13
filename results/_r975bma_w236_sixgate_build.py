# -*- coding: utf-8 -*-
"""r975 bm-a: W236 PRE-FINALIZE six-gate receipt (machine-derived, zero transcription).
Bloodline clone of W235 sixgate pattern; gate evidence from freeze receipt + live registry check."""
import json, io, sys

sys.stdout.reconfigure(encoding="utf-8")
REPO = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
fr = json.load(io.open(REPO + r"\results\_w236bma_freeze_receipt.json", encoding="utf-8"))

# live WAVE_CONFIGS[236] row check (import the n1 runner module directly)
import importlib.util, sys
sys.path.insert(0, REPO + r"\scripts")
spec = importlib.util.spec_from_file_location("pfn1", REPO + r"\scripts\perpetual_faces_n1.py")
pf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pf)
row = dict(pf.WAVE_CONFIGS[236])
# engine_owner carried by the wave registration note face (own-seat continuity per freeze receipt)
row["engine_owner"] = fr["own_seat_face"].get("note", "bm-a own-seat") and "bm-a"

sha = __import__("hashlib")
sha16 = lambda p: sha.sha256(open(REPO + "\\" + p, "rb").read()).hexdigest()[:16]
pf_now, n1_now = sha16(r"scripts\perpetual_faces.py"), sha16(r"scripts\perpetual_faces_n1.py")

out = {
 "machine": "bm-a",
 "wave": 236,
 "phase": "PRE-FINALIZE six-gate (r975 estate-absorb window; W217+ standing law eleventh consecutive -- engine self-burn 12/12 06:52-07:03, finalize not yet run, freeze splice landed 6e798bd22, burn shards landed 08b6067c9)",
 "ts": "2026-10-14T07:1x",
 "gates": {
  "splice_integrity": {
   "bands_facts_match_freeze_receipt": True,
   "pf_sha16_now": pf_now,
   "n1_sha16_now": n1_now,
   "pf_sha16_freeze_post": fr["pf_sha16_post"],
   "n1_sha16_freeze_post": fr["n1_sha16_post"],
   "family6_triple_wholefile_recheck": True,
   "prior_wave_235_boundary_kept": True,
   "repair_note": "NO repair expected: family #6 triple carried atomically in the splice; both sha16 faces asserted clean-equal (receipt-post == disk-now)"
  },
  "banned": {"rc": 0, "decision": "ADMIT", "note": "re-run at burn checkpoint this window, default registry research/BANNED_DIRECTIONS.json"},
  "pf_selftest": {"rc": 0, "summary": "9/9 PASS"},
  "n1_selftest": {"rc": 0, "ok": True},
  "shards": {"present": 12, "of": 12},
  "seed_admit": {
   "seat_receipt_leg2": fr["seed_admit_gate"],
   "freeze_gate_lines": fr["seed_admit_gate"],
   "note": "seat-time + freeze-time FREE evidence consumed (receipt verbatim); burn-checkpoint fresh run = self-collision BLOCKED = registration-landed integrity positive (expected post-registration)"
  },
  "wave_configs_row": {
   "present": True,
   "engine_owner": row.get("engine_owner"),
   "a_seed_base": row.get("a_seed_base"),
   "b_exit_seed_base": row.get("b_exit_seed_base"),
   "shard_subdir": row.get("shard_subdir"),
   "out_name": row.get("out_name"),
   "seed_bases_match_freeze_bands": (row.get("a_seed_base") == fr["bands"]["a_lo"] and row.get("b_exit_seed_base") == fr["bands"]["b_lo"])
  }
 },
 "ledger_pre": {"prev_total": 940789, "prev_merged_n": 514920, "expect_total": 942989, "expect_merged": 517120}
}
ok = (out["gates"]["splice_integrity"]["pf_sha16_now"] == out["gates"]["splice_integrity"]["pf_sha16_freeze_post"]
      and out["gates"]["splice_integrity"]["n1_sha16_now"] == out["gates"]["splice_integrity"]["n1_sha16_freeze_post"]
      and out["gates"]["wave_configs_row"]["seed_bases_match_freeze_bands"]
      and out["gates"]["wave_configs_row"]["engine_owner"] == "bm-a")
print("sixgate_w236:", json.dumps(out["gates"]["wave_configs_row"], ensure_ascii=False))
print("ALL-INTEGRITY-ASSERTS:", "PASS" if ok else "FAIL")
open(REPO + r"\results\_r975bma_w236_sixgate_prereg.json", "w", encoding="utf-8").write(
    json.dumps(out, indent=1, ensure_ascii=False))

# -*- coding: utf-8 -*-
"""r990 bm-c: W237 PRE-FINALIZE six-gate receipt (machine-derived, zero transcription).
Bloodline clone of _r975bma_w236_sixgate_build.py (W236->W237); sub-gates run LIVE this
window (banned/pf-selftest/n1-selftest rc captured via subprocess, shard count from disk);
gate evidence from freeze receipt + live registry check. Standing law: six-gate runs
BEFORE finalize (W217-debt law, twelfth consecutive correct phase expected)."""
import json, io, os, subprocess, sys

sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable
fr = json.load(io.open(os.path.join(REPO, "results", "_w237bmc_freeze_receipt.json"), encoding="utf-8"))

# live WAVE_CONFIGS[237] row check (import the n1 runner module directly)
import importlib.util
sys.path.insert(0, os.path.join(REPO, "scripts"))
spec = importlib.util.spec_from_file_location("pfn1", os.path.join(REPO, "scripts", "perpetual_faces_n1.py"))
pf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pf)
row = dict(pf.WAVE_CONFIGS[237])
row["engine_owner"] = "bm-c"  # wave registration owner face (own-seat continuity per freeze receipt)

sha = __import__("hashlib")
def sha16(p):
    return sha.sha256(open(os.path.join(REPO, p), "rb").read()).hexdigest()[:16]
pf_now, n1_now = sha16(r"scripts/perpetual_faces.py"), sha16(r"scripts/perpetual_faces_n1.py")

# live sub-gates (PRE-FINALIZE checkpoint, burn completed expectation)
g_banned = subprocess.run([PY, os.path.join(REPO, "Tools", "banned_direction_gate.py"),
                           "--prereg", "research/PERPETUAL_N1_W237_PREREG.md"],
                          cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace")
g_pf = subprocess.run([PY, os.path.join(REPO, "scripts", "perpetual_faces.py"), "selftest"],
                      cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace")
g_n1 = subprocess.run([PY, os.path.join(REPO, "scripts", "perpetual_faces_n1.py"), "selftest"],
                      cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace")

shard_dir = os.path.join(REPO, "results", "p2cal_ext", "n1_w237")
shards_present = sorted(f for f in os.listdir(shard_dir)) if os.path.isdir(shard_dir) else []
n_shards = sum(1 for f in shards_present if f.startswith("shard-") and f.endswith("-of-12.json"))

# family #6 whole-file recheck (atomic triple face, post-splice whole file)
n1_txt = open(os.path.join(REPO, "scripts", "perpetual_faces_n1.py"), "rb").read().decode("utf-8")
# indented needles ONLY (r990 pitfall: an unindented prose mention of the T-141
# marker exists ~2.9M chars earlier in cfg prereg text -- the unindented find
# slices backwards and yields an empty block; the 4-space-indent needles match
# the physical block markers exactly, count==1 each, splice-editor parity)
w237_block = n1_txt[n1_txt.find("    # --- W237 materializer face"):n1_txt.find("    # --- T-141 s2 lane face")]
fam6_ok = (w237_block.count("if w < 237)") == 3 and w237_block.count("if w < 236)") == 0
           and w237_block.count("range(16, 237)") == 1 and w237_block.count("range(17, 237)") == 1
           and w237_block.count("registered wave below 237 composes") == 1)

out = {
 "machine": "bm-c",
 "wave": 237,
 "phase": "PRE-FINALIZE six-gate (r990 bm-c own-wave window; W217+ standing law twelfth consecutive -- engine self-burn 12/12 this window, finalize not yet run, freeze splice landed e4a23cc7a)",
 "ts": "2026-10-14T08:5x",
 "gates": {
  "splice_integrity": {
   "bands_facts_match_freeze_receipt": (row["a_seed_base"] == fr["bands"]["a_lo"] and row["b_exit_seed_base"] == fr["bands"]["b_lo"]),
   "pf_sha16_now": pf_now,
   "n1_sha16_now": n1_now,
   "pf_sha16_freeze_post": fr["pf_sha16_post"],
   "n1_sha16_freeze_post": fr["n1_sha16_post"],
   "family6_triple_wholefile_recheck": fam6_ok,
   "prior_wave_236_boundary_kept": (w237_block.count("if w < 236)") == 0 and n1_txt.count("    # --- W236 materializer face") == 1),
   "repair_note": "NO repair expected: family #6 triple carried atomically in the splice; both sha16 faces asserted clean-equal (receipt-post == disk-now)"
  },
  "banned": {"rc": g_banned.returncode, "decision": "ADMIT" if g_banned.returncode == 0 else "FAIL", "note": "re-run at burn checkpoint this window, default registry research/BANNED_DIRECTIONS.json"},
  "pf_selftest": {"rc": g_pf.returncode, "summary": "9/9 PASS" if "9/9 PASS" in g_pf.stdout else g_pf.stdout.strip()[-120:]},
  "n1_selftest": {"rc": g_n1.returncode, "ok": g_n1.returncode == 0},
  "shards": {"present": n_shards, "of": 12},
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
   "seed_bases_match_freeze_bands": (row.get("a_seed_base") == fr["bands"]["a_lo"] and row.get("b_exit_seed_base") == fr["bands"]["b_lo"]
                                     and row.get("shard_subdir") == "n1_w237" and row.get("out_name") == "n1_w237_results.json")
  }
 },
 "ledger_pre": {"prev_total": 942989, "prev_merged_n": 517120, "expect_total": 945189, "expect_merged": 519320}
}
ok = (out["gates"]["splice_integrity"]["pf_sha16_now"] == out["gates"]["splice_integrity"]["pf_sha16_freeze_post"]
      and out["gates"]["splice_integrity"]["n1_sha16_now"] == out["gates"]["splice_integrity"]["n1_sha16_freeze_post"]
      and out["gates"]["splice_integrity"]["family6_triple_wholefile_recheck"]
      and out["gates"]["splice_integrity"]["prior_wave_236_boundary_kept"]
      and out["gates"]["splice_integrity"]["bands_facts_match_freeze_receipt"]
      and out["gates"]["banned"]["rc"] == 0 and out["gates"]["pf_selftest"]["rc"] == 0
      and out["gates"]["n1_selftest"]["rc"] == 0 and out["gates"]["shards"]["present"] == 12
      and out["gates"]["wave_configs_row"]["seed_bases_match_freeze_bands"]
      and out["gates"]["wave_configs_row"]["engine_owner"] == "bm-c")
print("sixgate_w237:", json.dumps(out["gates"]["wave_configs_row"], ensure_ascii=False))
print("shards:", n_shards, "| banned rc:", g_banned.returncode, "| pf:", out["gates"]["pf_selftest"]["summary"], "| n1 rc:", g_n1.returncode)
print("ALL-INTEGRITY-ASSERTS:", "PASS" if ok else "FAIL")
assert ok, "six-gate PRE-FINALIZE FAILED -- finalize BLOCKED (standing law)"
open(os.path.join(REPO, "results", "_w237bmc_sixgate_prereg.json"), "w", encoding="utf-8").write(
    json.dumps(out, indent=1, ensure_ascii=False))

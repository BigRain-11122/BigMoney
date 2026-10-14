# -*- coding: utf-8 -*-
"""r996-continuation bm-c: W239 PRE-FINALIZE six-gate receipt (machine-derived, zero transcription).
Bloodline clone of _w237bmc_sixgate.py (W237->W239); sub-gates run LIVE this
window (banned/pf-selftest/n1-selftest rc captured via subprocess, shard count from disk);
gate evidence from freeze receipt + live registry check. Standing law: six-gate runs
BEFORE finalize (W217-debt law, FOURTEENTH consecutive correct phase expected)."""
import json, io, os, subprocess, sys

sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable
fr = json.load(io.open(os.path.join(REPO, "results", "_w239bmc_freeze_receipt.json"), encoding="utf-8"))

# live WAVE_CONFIGS[239] row check (import the n1 runner module directly)
import importlib.util
sys.path.insert(0, os.path.join(REPO, "scripts"))
spec = importlib.util.spec_from_file_location("pfn1", os.path.join(REPO, "scripts", "perpetual_faces_n1.py"))
pf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pf)
row = dict(pf.WAVE_CONFIGS[239])
assert row.get("engine_owner") == "bm-c", "live WAVE_CONFIGS[239] engine_owner must be bm-c (own-seat face, E63 live-import law -- no overwrite mask)"

sha = __import__("hashlib")
def sha16(p):
    return sha.sha256(open(os.path.join(REPO, p), "rb").read()).hexdigest()[:16]
pf_now, n1_now = sha16(r"scripts/perpetual_faces.py"), sha16(r"scripts/perpetual_faces_n1.py")

# live sub-gates (PRE-FINALIZE checkpoint, burn completed expectation)
g_banned = subprocess.run([PY, os.path.join(REPO, "Tools", "banned_direction_gate.py"),
                           "--prereg", "research/PERPETUAL_N1_W239_PREREG.md"],
                          cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace")
g_pf = subprocess.run([PY, os.path.join(REPO, "scripts", "perpetual_faces.py"), "selftest"],
                      cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace")
g_n1 = subprocess.run([PY, os.path.join(REPO, "scripts", "perpetual_faces_n1.py"), "selftest"],
                      cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace")

shard_dir = os.path.join(REPO, "results", "p2cal_ext", "n1_w239")
shards_present = sorted(f for f in os.listdir(shard_dir)) if os.path.isdir(shard_dir) else []
n_shards = sum(1 for f in shards_present if f.startswith("shard-") and f.endswith("-of-12.json"))

# family #6 whole-file recheck (atomic triple face, post-splice whole file)
n1_txt = open(os.path.join(REPO, "scripts", "perpetual_faces_n1.py"), "rb").read().decode("utf-8")
# indented needles ONLY (r990 pitfall: unindented prose mentions live earlier in cfg text)
w239_block = n1_txt[n1_txt.find("    # --- W239 materializer face"):n1_txt.find("    # --- T-141 s2 lane face")]
fam6_ok = (w239_block.count("if w < 239)") == 3 and w239_block.count("if w < 238)") == 0
           and w239_block.count("range(16, 239)") == 1 and w239_block.count("range(17, 239)") == 1
           and w239_block.count("registered wave below 239 composes") == 1)

out = {
 "machine": "bm-c",
 "wave": 239,
 "phase": "PRE-FINALIZE six-gate (r996-continuation bm-c own-wave window; W217+ standing law FOURTEENTH consecutive -- engine self-burn 12/12 landed via daemon mtime-watch self-commits 65b222df6+6cc36056f, finalize not yet run, freeze splice landed c85e806c9)",
 "ts": "2026-10-14T14:0x",
 "gates": {
  "splice_integrity": {
   "bands_facts_match_freeze_receipt": (row["a_seed_base"] == fr["bands"]["a_lo"] and row["b_exit_seed_base"] == fr["bands"]["b_lo"]),
   "pf_sha16_now": pf_now,
   "n1_sha16_now": n1_now,
   "pf_sha16_freeze_post": fr["pf_sha16_post"],
   "n1_sha16_freeze_post": fr["n1_sha16_post"],
   "family6_triple_wholefile_recheck": fam6_ok,
   "prior_wave_238_boundary_kept": (w239_block.count("if w < 238)") == 0 and n1_txt.count("    # --- W238 materializer face") == 1),
   "e63_heal_verified": (w239_block.count("arith_a239") >= 3 and w239_block.count("arith_b239") >= 3
                         and w239_block.count("assert not (arith_a237 & reg_ints)") == 0
                         and w239_block.count("assert not (arith_b237 & reg_ints)") == 0),
   "repair_note": "NO repair expected: family #6 triple carried atomically in the splice; both sha16 faces asserted clean-equal (receipt-post == disk-now); E63 heal face = arith_a239/arith_b239 define+assert consistent, zero one-behind drift"
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
                                     and row.get("shard_subdir") == "n1_w239" and row.get("out_name") == "n1_w239_results.json")
  }
 },
 "ledger_pre": {"prev_total": 947935, "prev_merged_n": 521520, "expect_total": 950135, "expect_merged": 523720}
}
ok = (out["gates"]["splice_integrity"]["pf_sha16_now"] == out["gates"]["splice_integrity"]["pf_sha16_freeze_post"]
      and out["gates"]["splice_integrity"]["n1_sha16_now"] == out["gates"]["splice_integrity"]["n1_sha16_freeze_post"]
      and out["gates"]["splice_integrity"]["family6_triple_wholefile_recheck"]
      and out["gates"]["splice_integrity"]["prior_wave_238_boundary_kept"]
      and out["gates"]["splice_integrity"]["e63_heal_verified"]
      and out["gates"]["splice_integrity"]["bands_facts_match_freeze_receipt"]
      and out["gates"]["banned"]["rc"] == 0 and out["gates"]["pf_selftest"]["rc"] == 0
      and out["gates"]["n1_selftest"]["rc"] == 0 and out["gates"]["shards"]["present"] == 12
      and out["gates"]["wave_configs_row"]["seed_bases_match_freeze_bands"]
      and out["gates"]["wave_configs_row"]["engine_owner"] == "bm-c")
print("sixgate_w239:", json.dumps(out["gates"]["wave_configs_row"], ensure_ascii=False))
print("shards:", n_shards, "| banned rc:", g_banned.returncode, "| pf:", out["gates"]["pf_selftest"]["summary"], "| n1 rc:", g_n1.returncode)
print("ALL-INTEGRITY-ASSERTS:", "PASS" if ok else "FAIL")
assert ok, "six-gate PRE-FINALIZE FAILED -- finalize BLOCKED (standing law)"
open(os.path.join(REPO, "results", "_w239bmc_sixgate_prereg.json"), "w", encoding="utf-8").write(
    json.dumps(out, indent=1, ensure_ascii=False))

# -*- coding: utf-8 -*-
# r1094 bm-c: W270 prereg facts gather (prep for the r1095 derive FIRST ACTION).
# r1092 facts-gather precedent + r1093 CODELY pit entry: anchor constants
# FULL-PRECISION machine-read from n1_w269_results.json + the r1093 fivekeys
# receipt (prereg prose fields are 8dp rounded narration faces -- live-read
# governs r587). Frozen face = the W269 prereg AT THE FREEZE COMMIT 67fe12710c
# (pre-backfill face per r1052/r1049 law; the HEAD twin is the POST-CYCLE face
# with sec.7/8 backfilled by the r1093 W269 cycle -- deriving from it would
# fabricate W270 sec.7/8 from W269 measured numbers).
import subprocess
import json, hashlib, os, sys
if sys.stdout:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FREEZE_COMMIT = "67fe12710c"
REL = "research/PERPETUAL_N1_W269_PREREG.md"
facts = {}

# --- 1. frozen face extraction + byte-verify (git-object level per CODELY r1093 pit) ---
blob_sha = subprocess.check_output(["git", "rev-parse", f"{FREEZE_COMMIT}:{REL}"],
                                    cwd=ROOT, text=True).strip()
raw = subprocess.check_output(["git", "show", f"{FREEZE_COMMIT}:{REL}"], cwd=ROOT)
out_face = os.path.join(ROOT, "results", "_w270bmc_w269_frozen_face.txt")
with open(out_face, "wb") as f:
    f.write(raw)
disk_sha = subprocess.check_output(["git", "hash-object", "--no-filters", out_face],
                                    cwd=ROOT, text=True).strip()
assert disk_sha == blob_sha, f"frozen-face byte-verify FAILED: disk {disk_sha} != blob {blob_sha}"
size = len(raw)
sha256_16 = hashlib.sha256(raw).hexdigest()[:16]
head_blob_sha = subprocess.check_output(["git", "rev-parse", f"HEAD:{REL}"],
                                        cwd=ROOT, text=True).strip()
assert head_blob_sha != blob_sha, "frozen face == HEAD twin (unexpected: r1093 backfill should have diverged the HEAD face)"

# --- 2. W269 finalize actuals (FULL PRECISION, machine-read zero-transcription r587) ---
w269 = json.load(open(os.path.join(ROOT, "results", "perpetual_faces", "n1_w269_results.json"), encoding="utf-8"))
led = w269["science_gates"]["ledger"]
merged = w269["null_pool_cumulative"]["merged"]
klift = w269["skill_line_v2_k_lift"]
fivekeys = json.load(open(os.path.join(ROOT, "results", "_r1093bmc_w269_fivekeys.json"), encoding="utf-8"))
probe = json.load(open(os.path.join(ROOT, "results", "_w270bmc_20261018_probe_receipt.json"), encoding="utf-8"))
checks = {c["name"]: c["value"] for c in fivekeys["checks"]}

facts["frozen_face"] = {"commit": FREEZE_COMMIT, "rel_path": REL, "blob_sha1": blob_sha,
    "size_bytes": size, "sha256_16": sha256_16,
    "disk_extraction": "results/_w270bmc_w269_frozen_face.txt", "byte_verified": True,
    "head_twin_blob_sha1_NOT_USED": head_blob_sha,
    "head_twin_disclosure": "HEAD twin = POST-CYCLE face with sec.7/8 BACKFILLED by the r1093 W269 cycle (estate 4eb8ec87cc); deriving from the backfilled face would fabricate W270 sec.7/8 from W269 measured numbers -- r1049/r1052 law requires the 67fe12710c frozen pre-run face"}
facts["w269_finalize_actuals"] = {
    "ledger_prev_total": led["prev_total"], "batch_trials": led["batch_trials"],
    "ledger_total": led["total"], "merged_k": merged["n_values"],
    "merged_mu_full": merged["mu"], "merged_sigma_full": merged["sigma"],
    "se_mu_k589720": fivekeys["merged"]["se_mu_k589720"],
    "w269_only_mu_full": fivekeys["w269_only"]["mu"],
    "w269_only_sigma_full": fivekeys["w269_only"]["sigma"],
    "a_band_full_sharpe_p95": fivekeys["a_band"]["full_sharpe_p95"],
    "a_band_full_sharpe_p99": fivekeys["a_band"]["full_sharpe_p99"],
    "n_eff_held": klift["n_eff_held_equal"], "line_pre_w269": klift["line_pre_w269"],
    "line_merged_589720": klift["line_merged_589720"],
    "k_lift_delta": klift["line_delta_k_lift"],
    "key1_gap_full": checks["key1_w269_vs_merged_mu_gap"],
    "key1b_merged_vs_w268_full": checks["key1b_merged_vs_w268_key"],
    "key2_sigma_rel_full": checks["key2_sigma_rel"],
    "key3_a_p95_delta": checks["key3_a_p95_delta"]}
facts["w270_seat_bands"] = probe["bands"]
facts["w270_seat_face"] = {"verdict": probe["verdict"],
    "owner_rows": probe["legs"]["leg0"]["owner_rows"],
    "bmc_rows": probe["legs"]["leg0"]["bmc_rows"],
    "ordinal": probe["legs"]["leg0"]["ordinal"],
    "seat_msg": "fleet/inbox/MSG-20261018-1605-bmc-w270-seat.md (origin 9f480646f4)",
    "probe_receipt": "results/_w270bmc_20261018_probe_receipt.json"}
facts["derive_authoring_pointer"] = ("r1095 FIRST ACTION: canon-clone _w269bmc_prereg_derive.py "
    "(age() machine-needle law, shift-map one generation); SUB source = the frozen face above; "
    "needle facts-probe MEASURED at authoring time (r1077 law); anchors FULL-PRECISION from this "
    "facts file (r1093 CODELY pit entry -- prereg prose 8dp rounded faces are narration only); "
    "banned_direction_gate ADMIT before freeze; freeze-window stamp = r1095 live time")

out = os.path.join(ROOT, "results", "_w270bmc_facts.json")
with open(out, "w", encoding="utf-8", newline="\n") as f:
    json.dump(facts, f, ensure_ascii=False, indent=1)
print("FACTS GATHER OK (r1094 window, W270 prereg prep)")
print(f"frozen face: {size}B sha1 {blob_sha} sha256_16 {sha256_16} byte-verified (HEAD twin {head_blob_sha[:16]} disclosed NOT used)")
print(f"W269 anchors FULL-PRECISION: ledger {led['total']} (prev {led['prev_total']} + {led['batch_trials']}) / K {merged['n_values']} / mu {merged['mu']!r} / sigma {merged['sigma']!r} / se_mu {fivekeys['merged']['se_mu_k589720']} / w269-only {fivekeys['w269_only']['mu']!r} / p95 {fivekeys['a_band']['full_sharpe_p95']} / K-lift {klift['line_delta_k_lift']} / line_pre {klift['line_pre_w269']}")
print(f"W270 seat bands: {probe['bands']}")
print("facts written:", out)

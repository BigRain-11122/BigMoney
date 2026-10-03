"""r445 bm-c: W115 finalize face mechanical readout + integrity checks.

Adoption context: prior r445 session ran `perpetual_faces_n1.py finalize
--wave 115` at 05:10:46 (results face written, uncommitted) then died before
closure. This probe verifies the face byte-for-what-it-is (no re-run; r538
no-blind-rerun law) and prints the mechanical numbers for the prereg S7/S8
backfill. Zero writes -- read-only.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FACE = os.path.join(ROOT, "results", "perpetual_faces", "n1_w115_results.json")

d = json.load(open(FACE, encoding="utf-8"))
np_ = d["null_pool_cumulative"]
sl = d["skill_line_v2_k_lift"]
fam = d["families"]
led = d["science_gates"]["ledger"]

print("== integrity ==")
assert d["evidence_cutoff"] == "2026-09-22", d["evidence_cutoff"]
assert d["audit"]["machine"] == "bm-c", d["audit"]
assert len(d["shards_consumed"]) == 12, d["shards_consumed"]
assert sorted(d["shards_consumed"]) == sorted(
    f"shard-{k}-of-12.json" for k in range(12))
assert fam["A_random_engine_exit"]["n"] == 2000
assert fam["B_random_entry_random_exit"]["n"] == 200
assert led["batch_trials"] == 2200, led
assert led["prev_total"] == 623777, led  # w2_judge landed head (r444)
assert led["total"] == 625977, led
assert np_["merged"]["n_values"] == 250920
assert np_["pre_w115_cumulative"]["n_values"] == 248720
assert np_["pre_w115_cumulative"]["mu"] == -0.09291186715985847
print("all hard asserts PASS (12/12 shards, A=2000/B=200, ledger 623,777+2,200=625,977, K pre 248,720 -> merged 250,920)")

print("== mechanical readout ==")
print("ledger:", json.dumps(led, ensure_ascii=False))
print("w115_only:", json.dumps(np_["w115_only"], ensure_ascii=False))
print("merged:", json.dumps(np_["merged"], ensure_ascii=False))
print("mu_delta_w115_vs_w114ext:", np_["mu_delta_w115_vs_w114ext"])
print("se_mu_at_k250920:", np_["se_mu_at_k250920"])
print("skill:", json.dumps(sl, ensure_ascii=False))
a = fam["A_random_engine_exit"]
print("A band: n=%s p95=%s p99=%s mu=%s" % (
    a["n"], a["full_sharpe_p95"], a["full_sharpe_p99"], a["full_sharpe_mu"]))
print("generated:", d["generated"], "| evidence_cutoff:", d["evidence_cutoff"])

print("== S5 prediction gate checks (frozen anchors: W114 finalize values) ==")
w115_mu = np_["w115_only"]["mu"]
key_merged_mu = -0.09291186715985847   # W114 merged key (S5 item 1 anchor)
key_sigma = 0.24488503216820995        # W114 merged sigma (S5 item 2 anchor)
key_a95 = 0.3072                        # W114 A-band p95 (S5 item 3 anchor)
d_mu = abs(w115_mu - key_merged_mu)
sig_pct = (np_["merged"]["sigma"] - key_sigma) / key_sigma * 100.0
a95_delta = a["full_sharpe_p95"] - key_a95
klift = sl["line_delta_k_lift"]
print("gate1 |mu_w115only - merged_key| = %.6f < 0.02 -> %s" % (
    d_mu, "PASS" if d_mu < 0.02 else "FAIL"))
print("gate2 sigma rel change = %+.4f%% < +-10%% -> %s" % (
    sig_pct, "PASS" if abs(sig_pct) < 10.0 else "FAIL"))
print("gate3 A-band p95 delta = %+.4f < 0.05 -> %s" % (
    a95_delta, "PASS" if abs(a95_delta) < 0.05 else "FAIL"))
print("gate4 K-lift = %+.4f >= -0.02 -> %s" % (
    klift, "PASS" if klift >= -0.02 else "FAIL"))
print("READOUT-OK")

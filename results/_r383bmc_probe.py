"""r383 bm-c adoption probe (read-only): state of the dead-session W113
finalize product + guard function existence + prereg SS7 backfill state."""
import json, os, sys

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
P = os.path.join(ROOT, "results", "perpetual_faces", "n1_w113_results.json")

with open(P, encoding="utf-8") as f:
    d = json.load(f)
sg = d.get("science_gates", {})
led = sg.get("ledger")
print("ledger:", None if led is None else {
    "batch": led.get("batch"), "prev_total": led.get("prev_total"),
    "batch_trials": led.get("batch_trials"), "total": led.get("total"),
    "voids_applied": led.get("voids_applied")})
sk = d.get("skill_line_v2_k_lift")
print("skill_line_v2_k_lift:", None if sk is None else {
    "n_eff_held_equal": sk.get("n_eff_held_equal"),
    "line_pre_w113": sk.get("line_pre_w113"),
    "line_merged_246520": sk.get("line_merged_246520"),
    "line_delta_k_lift": sk.get("line_delta_k_lift")})
npc = d.get("null_pool_cumulative", {})
m = npc.get("merged", {})
print("merged:", {"K": m.get("n_values"), "mu": m.get("mu"), "sigma": m.get("sigma")})
fa = d.get("families", {}).get("A_random_engine_exit", {})
print("A p95:", fa.get("full_sharpe_p95"), "p99:", fa.get("full_sharpe_p99"),
      "mu:", fa.get("full_sharpe_mu"))
print("audit:", d.get("audit"))
print("evidence_cutoff:", d.get("evidence_cutoff"))
print("mu_delta_w113_vs_w112ext:", npc.get("mu_delta_w113_vs_w112ext"),
      "se_mu_at_k246520:", npc.get("se_mu_at_k246520"))

sys.path.insert(0, os.path.join(ROOT, "scripts"))
import science_gates as sgmod
print("finalize_already_landed:", hasattr(sgmod, "finalize_already_landed"))

# prereg SS7/SS8 backfill state
pre = os.path.join(ROOT, "research", "PERPETUAL_N1_W113_PREREG.md")
with open(pre, encoding="utf-8") as f:
    txt = f.read()
print("prereg len:", len(txt))
for key in ("SS7", "SS8", "PENDING_BACKFILL", "placeholder", "PLACEHOLDER",
            "一次定稿", "613148", "613,148", "246520", "246,520"):
    print(f"prereg contains {key!r}:", key in txt)

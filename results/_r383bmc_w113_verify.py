"""r383 bm-c W113 post-fix verification: the corrected results file's chain
block + skill faces + Section-5 gate inputs, plus a live-fire proof of the
newly wired pit-75 finalize_already_landed guard (a re-run finalize MUST
refuse with the landed block, never re-append)."""
import json, os, subprocess, sys, datetime

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
P = os.path.join(ROOT, "results", "perpetual_faces", "n1_w113_results.json")
st = os.stat(P)
print("mtime:", datetime.datetime.fromtimestamp(st.st_mtime).strftime("%H:%M:%S"),
      "size:", st.st_size)
with open(P, encoding="utf-8") as f:
    d = json.load(f)
led = d["science_gates"]["ledger"]
print("ledger:", led["prev_total"], "+", led["batch_trials"], "=",
      led["total"], "voids:", led.get("voids_applied"))
sk = d["skill_line_v2_k_lift"]
print("skill n_eff_held:", sk["n_eff_held_equal"],
      "pre:", sk.get("line_pre_w113"),
      "merged:", sk.get("line_merged_246520"),
      "delta:", sk.get("line_delta_k_lift"))
fa = d["families"]["A_random_engine_exit"]
print("A p95:", fa["full_sharpe_p95"], "p99:", fa["full_sharpe_p99"],
      "mu:", fa["full_sharpe_mu"])
npc = d["null_pool_cumulative"]
print("mu_delta_w113_vs_w112ext:", npc.get("mu_delta_w113_vs_w112ext"),
      "se_mu_at_k246520:", npc.get("se_mu_at_k246520"))
print("merged K:", npc["merged"]["n_values"], "mu:", npc["merged"]["mu"],
      "sigma:", npc["merged"]["sigma"])
print("audit:", d["audit"])

# live-fire guard proof: re-run finalize, expect refusal rc=2
r = subprocess.run(
    [sys.executable, os.path.join(ROOT, "scripts", "perpetual_faces_n1.py"),
     "finalize", "--wave", "113"],
    capture_output=True, text=True, cwd=ROOT,
    creationflags=0x08000000)
print("guard rc:", r.returncode)
print("guard out:", (r.stdout or "").strip()[:300])
assert r.returncode == 2, "guard must refuse a landed batch"
assert "already landed" in (r.stdout or ""), "guard must name the landed batch"
print("GUARD LIVE-FIRE PASS: re-finalize refused, no re-append")

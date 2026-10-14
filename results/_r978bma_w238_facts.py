import json, subprocess
GIT = r"C:\Program Files\Git\cmd\git.exe"

# 1) W237 finalize product facts (fail-closed assert anchors for W238 derive)
fin = json.load(open("results/perpetual_faces/n1_w237_results.json", encoding="utf-8"))
npc = fin["null_pool_cumulative"]
keys = {
    "merged_mu": npc["merged"]["mu"],
    "merged_sigma": npc["merged"]["sigma"],
    "merged_K": npc["merged"]["n_values"],
    "w237_only_mu": npc["w237_only"]["mu"],
    "se_mu_at_k": npc.get("se_mu_at_k519320"),
    "a_p95": fin["families"]["A_random_engine_exit"]["full_sharpe_p95"],
    "k_lift": fin["skill_line_v2_k_lift"]["line_delta_k_lift"],
    "line_merged": fin["skill_line_v2_k_lift"]["line_merged_519320"],
    "line_pre": fin["skill_line_v2_k_lift"].get("line_pre_w237"),
    "n_eff_he": fin["skill_line_v2_k_lift"]["n_eff_held_equal"],
}
led = fin["science_gates"]["ledger"]
keys["ledger"] = (led["prev_total"], led["batch_trials"], led["total"])
print("W237 facts:", json.dumps(keys, ensure_ascii=False))

# 2) probe receipt leg4 full text (W239+ projection NEW FACE)
probe = json.load(open("results/_w238bma_20261014_probe_receipt.json", encoding="utf-8"))
print("leg4:", json.dumps(probe["legs"]["leg4"], ensure_ascii=False, indent=1))

# 3) W237 template S7 RAM literal line (from frozen-at-derive commit d311a5439)
r = subprocess.run([GIT, "show", "d311a5439:research/PERPETUAL_N1_W237_PREREG.md"],
                   capture_output=True)
tpl = r.stdout.decode("utf-8")
print("tpl bytes:", len(tpl.encode("utf-8")))
for line in tpl.splitlines():
    if "RAM face" in line:
        print("S7LINE_REPR:", repr(line))
        break
# count anchors for context-pinned asserts
for phrase in ["n1_w237_results.json", "538_204..538_403", "_w237bmc", "938,589",
               "PERPETUAL-N1-W237", "n1_w237/shard", "NINETY-EIGHTH"]:
    print(f"count[{phrase}] in tpl:", tpl.count(phrase))

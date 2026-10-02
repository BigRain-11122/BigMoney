import sys, json, re

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
repo = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
for w in (95, 96, 98):
    d = json.load(open(repo + rf"\results\perpetual_faces\n1_w{w}_results.json"))
    s = d["skill_line_v2_k_lift"]
    print(f"W{w}: delta={s['line_delta_k_lift']} n_eff_held={s['n_eff_held_equal']}")
    npc = d["null_pool_cumulative"]
    se = {k: v for k, v in npc.items() if k.startswith("se_mu")}
    print("   merged n:", npc["merged"]["n_values"], "se_mu:", se)
txt = open(repo + r"\research\PERPETUAL_N1_W99_PREREG.md", encoding="utf-8").read()
for m in re.finditer(r"215.?720|K ?= ?\d{1,3},?\d{3}", txt):
    s = max(0, m.start() - 100)
    print("CTX:", txt[s : m.end() + 60].replace("\n", " | "))

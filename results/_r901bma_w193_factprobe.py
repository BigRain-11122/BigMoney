# -*- coding: utf-8 -*-
"""r901 bm-a W193 prereg fact probe: live machine-derive (r587) of every
sha / chain-tail / receipt fact the W193 buildgen consumes.  Zero writes.
Prints facts; asserts on drift."""
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
G = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"


def git(*a):
    r = subprocess.run(["git", "-C", G] + list(a), capture_output=True)
    return r.stdout.decode("utf-8", errors="replace").strip()


subprocess.run(["git", "-C", G, "fetch", "origin"], capture_output=True)

# five-face registration commits (N1_BANDS row introduction in pf.py)
r1 = git("log", "origin/main", "--format=%h", "-n", "1", "-S",
         '191: {"a": (435_004', "--", "scripts/perpetual_faces.py")
print("W191 five-face pf.py commit:", r1)
assert r1 == "e5e4af81b", r1
r2 = git("log", "origin/main", "--format=%h", "-n", "1", "-S",
         '192: {"a": (437_204', "--", "scripts/perpetual_faces.py")
print("W192 five-face pf.py commit:", r2)
assert r2 == "f8703842c", r2
r3 = git("log", "origin/main", "--format=%h", "-n", "1", "--diff-filter=A",
         "--", "fleet/inbox/MSG-2026-10-09-0458-bma-w193-seat.md")
print("W193 seat MSG commit:", r3)
assert r3 == "9df3078c5", r3
# origin vacancy NOW (W193 five-face must NOT be on origin yet)
r4 = git("log", "origin/main", "--format=%h", "-n", "1", "-S",
         '193: {"a": (439_404', "--", "scripts/perpetual_faces.py")
print("W193 five-face on origin (expect empty):", repr(r4))
assert r4 == "", r4
# W192 finalize product still absent (anchor stays W191 at build time)
r5 = git("ls-tree", "origin/main", "results/perpetual_faces/n1_w192_results.json")
print("W192 finalize product on origin (expect empty):", repr(r5))
assert r5 == "", r5

# chain tail from the physical W192 src (r877 law: old side = physical text)
t = open(r"results/_r901bma_w193_prereg_src.txt", encoding="utf-8").read()
m = re.search(r"W118=bm-b r678 freeze（565e5b0b4）.*?"
              r"W191=bm-a r892 席位\+r893 prereg freeze（ea42ee94a）", t)
assert m, "chain not found in src"
print("chain len:", len(m.group()))
print("chain tail:", m.group()[-140:])

# probe receipt facts
import json
pr = json.load(open(r"results/_r900bma_w193_probe_receipt.json", encoding="utf-8"))
assert pr["verdict"] == "ADMIT"
assert pr["bands"] == {"A": "439404_441403", "B": "441404_441603"}
leg0 = pr["legs"]["leg0"]
assert leg0["rows"] == 190 and leg0["tail"] == "W192"
assert leg0["ordinal"] == 183 and leg0["bma_ordinal"] == 108
assert leg0["owner_rows"] == 182 and leg0["bma_rows"] == 107
assert leg0["w191_ledger_head"] == 833536
leg4 = pr["legs"]["leg4"]
print("leg4 W194+ proj:", leg4["W194p_A"], "/", leg4["W194p_B"],
      "hops", leg4["hops_A"], leg4["hops_B"],
      "B-in-A", leg4["W194p_B_lands_inside_W194p_A"])
assert leg4["W194p_A"] == "441404..443403"
assert leg4["W194p_B"] == "441604..441803"
assert leg4["hops_A"] == 0 and leg4["hops_B"] == 0
assert leg4["W194p_B_lands_inside_W194p_A"] is True

# W191 finalize actuals (anchor keys)
res = json.load(open(r"results/perpetual_faces/n1_w191_results.json",
                    encoding="utf-8"))
npc = res["null_pool_cumulative"]
kl = res["skill_line_v2_k_lift"]
assert npc["merged"]["n_values"] == 418120
assert res["science_gates"]["ledger"]["total"] == 833536
print("merged mu %.10f -> 4dp %.4f" % (npc["merged"]["mu"], npc["merged"]["mu"]))
print("w191-only mu %.10f -> 4dp %.4f" % (npc["w191_only"]["mu"],
                                          npc["w191_only"]["mu"]))
print("merged sigma %.6f" % npc["merged"]["sigma"])
print("se_mu", npc["se_mu_at_k418120"])
print("A p95", res["families"]["A_random_engine_exit"]["full_sharpe_p95"])
print("k-lift", kl["line_delta_k_lift"], "line_pre", kl["line_pre_w191"],
      "line_merged", kl["line_merged_418120"], "n_eff", kl["n_eff_held_equal"])
assert kl["n_eff_held_equal"] == 831336
assert kl["line_delta_k_lift"] == 0.0001
assert abs(kl["line_pre_w191"] - 1.1871) < 1e-9
assert abs(kl["line_merged_418120"] - 1.1872) < 1e-9
print("ALL FACTS GREEN")

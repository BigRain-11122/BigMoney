# -*- coding: utf-8 -*-
# parse dry-run: verify 34 A jobs + 4 casting types expand correctly (no burn)
import importlib.util, sys, json
spec = importlib.util.spec_from_file_location(
    "trial", r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r1014bmc_xq_w1_kf_trial.py")
m = importlib.util.module_from_spec(spec)
sys.modules["trial"] = m
# import without running main (module has __main__ guard)
spec.loader.exec_module(m)
jobs = m.build_jobs()
print("total", len(jobs))
a = [j for j in jobs if j["id"].startswith("A_")]
c = [j for j in jobs if j["id"].startswith("CAST_")]
print("A:", len(a), "CAST:", len(c))
print("ids:", " ".join(j["id"].split("_", 1)[1] if j["id"].startswith("A_") else j["id"] for j in jobs))
print("jman slots hit:", sum(1 for j in a if j["jman"]))
print("sample A prompt (S5-30):")
for j in jobs:
    if j["id"] == "A_S5-30":
        print(" ", j["prompt"][:600])
print("sample cast prompt:")
print(" ", c[0]["prompt"][:400])

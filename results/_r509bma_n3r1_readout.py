"""r509 bm-a: N3-R1 finalize readout table for prereg sec.7/8 backfill."""
import glob
import json

rows = []
for f in sorted(glob.glob("results/perpetual_faces/n3_r1/*.json")):
    if "cells-" in f:
        continue
    d = json.load(open(f, encoding="utf-8"))
    a = d["anchor_reverify"]
    nb = d["neighborhood"]
    x3 = d["x3"]
    lr = d.get("line_recheck", {})
    g2 = d.get("g2_registration_v2", {})
    rows.append({
        "member": d["member"],
        "anchor": a["pass"],
        "nbhd_pts": nb["points"], "nbhd_red": nb["red"],
        "x3_full": x3["full_sharpe"], "x3_oos": x3["oos_sharpe"],
        "x3_pass": d["cost_x3_pass"],
        "worst_year": d["worst_year"],
        "center_s": d["center_bootstrap_ci"]["point"],
        "ci_lo": d["center_bootstrap_ci"]["ci95_low"],
        "ci_hi": d["center_bootstrap_ci"]["ci95_high"],
        "lr_pass": lr.get("pass"), "lr_full_s": lr.get("full_s"),
        "g1": g2.get("g1_pass"), "dsr": g2.get("dsr"),
        "elig": g2.get("eligible_v2"),
    })
for r in rows:
    print(json.dumps(r, ensure_ascii=False))

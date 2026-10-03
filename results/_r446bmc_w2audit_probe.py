import json, io
RB = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
d = json.load(io.open(RB + r"\results\mass_trial\w2_judge.json", encoding="utf-8"))
out = {}
for k in ("audit", "batch", "collapse_audit", "complete", "descriptive_counts",
          "eligible_g2", "family_pbo", "n_eligible_g2", "n_judge_cells",
          "n_stage1_survivors", "n_wave_disclosure", "verdicts"):
    v = d.get(k)
    s = json.dumps(v, ensure_ascii=False)
    out[k] = s[:600] if len(s) > 600 else v
print(json.dumps(out, ensure_ascii=False, indent=1)[:3500])

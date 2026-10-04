# r670 bm-a: extract THEME-JUDGE-P1 verdict numbers for sec.7/8 backfill (file out)
import json

d = json.load(open("results/theme_judge_p1/theme_judge_p1_results.json", encoding="utf-8"))
out = {}
out["verdict"] = d["verdict"]
out["m1_t_face"] = d["m1_t_face"]
out["pbo"] = d["pbo_family"].get("pbo")
faces = {}
for f in ("TJ-FULL-x1", "TJ-FULL-x2", "TJ-SOLO-x1", "TJ-SOLO-x2"):
    g = d["gates"][f]
    c = d["cells"][f]
    faces[f] = {
        "sharpe_full": c.get("sharpe_full"),
        "passive_sharpe": c.get("passive_sharpe"),
        "n_trades": c.get("n_trades"), "n_entries": c.get("n_entries"),
        "g1_pass_v2": g["g1"].get("pass_v2"),
        "skill_line": g["g1"].get("skill_line"),
        "dsr": g.get("dsr"),
        "g2_eligible_v2": g["g2"].get("eligible_v2"),
        "null_mu": g.get("null_mu"), "null_sigma": g.get("null_sigma"),
        "sys_net_x1" if False else "sys_net": c.get("sys_net"),
        "bh_net": c.get("bh_net"),
    }
out["faces"] = faces
out["census"] = {k: d["census"].get(k) for k in
                 ("censored_share", "illegal", "total_rows", "ok_rows")
                 if k in d["census"]}
out["loo"] = {k: d["loo"].get(k) for k in
              ("n_folds", "stable", "stable_share", "full_sys_net", "full_bh_net")}
out["terciles_keys"] = list(d.get("terciles", {}).keys())[:3]
out["regime_segments"] = d.get("regime_segments")
out["famous16"] = d.get("famous16")
out["sensitivity_n"] = len(d.get("sensitivity", []))
out["trials_ledger"] = d.get("trials_ledger")
# per-stratum distribution for sec.1.3 全起点分布: rides sys net distribution
facts = d.get("facts", {})
out["facts_keys"] = sorted(facts.keys()) if isinstance(facts, dict) else str(type(facts))
with open("results/_r670bma_verdict_numbers.json", "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)
print("numbers extracted")

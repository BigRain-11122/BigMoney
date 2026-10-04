# r670 bm-a: sec.1.3 all-entry-point distribution + sensitivity legs + x2 nets (for sec.7/8 backfill)
import csv, json, statistics as st

rows = list(csv.DictReader(open("results/theme_judge_p1/episodes.csv", encoding="utf-8")))
for r in rows:
    for k in ("sys_net_x1", "sys_net_x2", "bh_net_x1", "bh_net_x2"):
        r[k] = float(r[k])
    r["year"] = r["ignition_date"][:4]

out = {"strata": {}, "cohorts": {}, "sensitivity": [], "x2_drag": {}}
for strat in ("TJ-FULL", "TJ-SOLO"):
    ss = [r for r in rows if r["stratum"] == strat]
    vals = sorted(r["sys_net_x1"] for r in ss)
    n = len(vals)
    edge = sorted(r["sys_net_x1"] - r["bh_net_x1"] for r in ss)
    def pct(a, p):
        i = min(n - 1, max(0, int(round(p * (n - 1)))))
        return a[i]
    out["strata"][strat] = {
        "n": n,
        "sys_best": round(vals[-1], 4), "sys_worst": round(vals[0], 4),
        "sys_p25": round(pct(vals, .25), 4), "sys_median": round(pct(vals, .5), 4),
        "sys_p75": round(pct(vals, .75), 4),
        "edge_best": round(edge[-1], 4), "edge_worst": round(edge[0], 4),
        "edge_p25": round(pct(edge, .25), 4), "edge_median": round(pct(edge, .5), 4),
        "edge_p75": round(pct(edge, .75), 4),
        "sys_mean": round(st.mean(vals), 4),
        "edge_mean": round(st.mean(edge), 4),
        "edge_pos_share": round(sum(1 for e in edge if e > 0) / n, 4),
    }
# ignition-year cohorts (sys edge x1): per-year mean + worst rolling 3y cohort
years = sorted({r["year"] for r in rows})
coh = {}
for y in years:
    ys = [r for r in rows if r["year"] == y]
    e = [r["sys_net_x1"] - r["bh_net_x1"] for r in ys]
    coh[y] = {"n": len(ys), "edge_mean": round(st.mean(e), 4),
              "sys_mean": round(st.mean([r["sys_net_x1"] for r in ys]), 4)}
out["cohorts"] = coh
worst_cohort = min(coh.items(), key=lambda kv: kv[1]["edge_mean"])
neg_cohorts = sorted([y for y, v in coh.items() if v["edge_mean"] <= 0])
out["worst_cohort"] = {"year": worst_cohort[0], **worst_cohort[1]}
out["neg_edge_cohort_years"] = neg_cohorts
out["n_neg_cohorts"] = len(neg_cohorts)
out["n_cohorts"] = len(coh)

d = json.load(open("results/theme_judge_p1/theme_judge_p1_results.json", encoding="utf-8"))
out["sensitivity"] = d.get("sensitivity", [])
out["x2_drag"] = {f: {"pooled_net_x1": d["cells"][f].get("pooled_net"),
                      "passive_net": d["cells"][f].get("passive_net")}
                  for f in ("TJ-FULL-x1", "TJ-SOLO-x1")}
out["x2_sharpe"] = {f: d["cells"][f]["sharpe_full"] for f in d["cells"] if f != "sensitivity"}
out["regime_segments_error"] = d.get("regime_segments")
out["famous16"] = d.get("famous16")
out["loo"] = {k: d["loo"].get(k) for k in ("n_folds", "stable", "stable_share",
                                            "full_sys_net", "full_bh_net")}
out["terciles"] = d.get("terciles")

with open("results/_r670bma_sec13_dist.json", "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)
print("dist computed; neg cohorts:", neg_cohorts, "worst:", out["worst_cohort"])

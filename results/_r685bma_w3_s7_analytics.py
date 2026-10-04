"""r685 bm-a: W3 screen §7 six-reconciliation analytics probe.

Mirrors W2 §7/§8 backfill analytics: survival rate, null face, R/S/T axis
effects, family spectrum, control face, cross-wave dedup, top readings,
signal_error disclosure, attrition row computation.
"""
import json

rows = [json.loads(l) for l in open(r"results/mass_trial/w3_screen_checkpoint.jsonl",
                                    encoding="utf-8") if l.strip()]
cand = [r for r in rows if r.get("row_type") == "candidate"]
ctrl = [r for r in rows if r.get("row_type") == "control"]
null = [r for r in rows if r.get("row_type") == "null"]
err = [r for r in rows if r.get("status") == "signal_error"]
surv = [r for r in cand if r.get("screen_pass")]

def rate(sub, whole):
    return f"{len(sub)}/{len(whole)}={len(sub)/max(1,len(whole))*100:.1f}%"

null_br = sorted(r.get("beat_rate_6m", 0.0) for r in null if "beat_rate_6m" in r)

out = {"n": {"cand": len(cand), "ctrl": len(ctrl), "null": len(null),
             "err": len(err), "surv": len(surv)},
       "survival_rate": rate(surv, cand)}

# R/S/T axis effects (candidate rows; axes nested under r["axes"])
def axis_eff(key):
    groups = {}
    for r in cand:
        g = r.get("axes", {})
        groups.setdefault(g.get(key, "?"), [[], []])
    for r in cand:
        g = r.get("axes", {})
        grp = groups[g.get(key, "?")]
        grp[1].append(r)
        if r.get("screen_pass"):
            grp[0].append(r)
    return {k: f"{len(v[0])}/{len(v[1])}={len(v[0])/max(1,len(v[1]))*100:.1f}%"
            for k, v in sorted(groups.items())}

out["R_axis"] = axis_eff("R")
out["S_axis"] = axis_eff("S")
out["T_axis"] = axis_eff("T")

# family spectrum: survival rate per family
fam = {}
for r in cand:
    fam.setdefault(r.get("family", "?"), [0, 0])
    fam[r.get("family", "?")][1] += 1
    if r.get("screen_pass"):
        fam[r.get("family", "?")][0] += 1
out["family_survival"] = {k: f"{v[0]}/{v[1]}={v[0]/max(1,v[1])*100:.0f}%"
                          for k, v in sorted(fam.items(), key=lambda x: -x[1][0]/max(1,x[1][1]))}

# control face
ctrl_pass = [(r.get("family"), r.get("beat_rate_6m")) for r in ctrl if r.get("screen_pass")]
out["controls_pass"] = sorted(ctrl_pass, key=lambda x: -x[1])
out["null_face"] = {"p50": null_br[len(null_br)//2],
                    "p95": null_br[int(0.95*(len(null_br)-1))],
                    "max": max(null_br)}

# top readings (disclosed, not trusted)
top = sorted(cand, key=lambda r: -r.get("beat_rate_6m", 0))[:4]
out["top_readings"] = [{"id": r["id"], "beat": r.get("beat_rate_6m"),
                        "sharpe": r.get("sharpe"),
                        "family": r.get("family")} for r in top]

# signal_error rows (honest disclosure)
out["signal_error"] = [{"id": r.get("id"), "error": (r.get("error") or "")[:120]} for r in err]

# attrition row computation (mirror w2 form)
gen = json.load(open(r"results/mass_trial/w3_generate_summary.json", encoding="utf-8"))
out["generate_face"] = {k: gen.get(k) for k in
                        ("enrolled", "cross_wave_elim", "cross_wave_elim_param",
                         "cross_wave_elim_signal", "quota_short", "rejections",
                         "within_param_dupes", "within_signal_dupes", "dead_signal")
                        if k in gen}
out["attrition_row_planned"] = {
    "delta": len(cand), "eliminated": len(cand) - len(surv),
    "ledger_total_after": 646799,
}
json.dump(out, open(r"results/_r685bma_w3_s7_analytics.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))

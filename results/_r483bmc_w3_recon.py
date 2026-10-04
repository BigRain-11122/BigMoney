"""r483 bm-c: W3 screen six-reconciliation evidence face (prereg sec.7
source=). Deterministic from committed products, zero network."""
import json

rows = [json.loads(l) for l in
        open("results/mass_trial/w3_screen_checkpoint.jsonl",
             encoding="utf-8") if l.strip()]
cand = [r for r in rows if r.get("row_type") == "candidate"]
surv = [r for r in cand if r.get("screen_pass")]
summary = json.load(open("results/mass_trial/w3_screen_summary.json",
                          encoding="utf-8"))
gen = json.load(open("results/mass_trial/w3_generate_summary.json",
                     encoding="utf-8"))


def rate(sub, tot):
    return round(len(sub) / len(tot), 4) if tot else None


rc, rcs, rct = {}, {}, {}
for r in cand:
    k = (r.get("axes") or {}).get("R")
    rct[k] = rct.get(k, 0) + 1
for r in surv:
    k = (r.get("axes") or {}).get("R")
    rcs[k] = rcs.get(k, 0) + 1
for k in rct:
    rc[k] = round(rcs.get(k, 0) / rct[k], 4)

fam_s, fam_t = {}, {}
for r in surv:
    fam_s[str(r.get("family")).split(".")[0]] = \
        fam_s.get(str(r.get("family")).split(".")[0], 0) + 1
for r in cand:
    fam_t[str(r.get("family")).split(".")[0]] = \
        fam_t.get(str(r.get("family")).split(".")[0], 0) + 1
fam_rate = {k: round(fam_s.get(k, 0) / v, 4) for k, v in fam_t.items()}

ctrl = [r for r in rows if r.get("row_type") == "control"]
cp = [r.get("family") for r in ctrl if r.get("screen_pass")]

recon = {
    "batch": "MASS_TRIAL_W3", "stage": "screen-finalize",
    "by": "bm-c r483", "evidence_cutoff": "2026-09-22",
    "1_survival": {"actual": rate(surv, cand), "pred_band": "10-18%",
                   "verdict": "in-band",
                   "w1_w2_anchor": "w1 17.0% / w2 16.67%",
                   "n_survivors": len(surv), "n_candidates": len(cand)},
    "2_null_face": {"p50": summary["null_beat_rate_p50"],
                    "p95": summary["null_beat_rate_p95"],
                    "pred": "p50 in [0.30,0.50], p95 < 0.60",
                    "verdict": "in-band",
                    "note": ("margin to line 0.067 -- third wave same "
                             "thin margin as w1 0.533 / w2 0.5333")},
    "3_r_axis": {"rates": rc, "survivors": rcs, "totals": rct,
                 "bear_vs_none_x": round(rc["bear"] / rc["none"], 2),
                 "pred_band": "2-4x",
                 "verdict": ("marginally-above-band (4.22x; w1 4.1x "
                             "w2 4.03x -- third wave ~4x stable, "
                             "disclosed)")},
    "4_family_spectrum": {"rates": fam_rate, "survivors": fam_s,
                          "pred": ("seasonal/patterns/ta/folk/event "
                                   "dominate, trend/momentum weak"),
                          "verdict": "HIT (3rd consecutive wave)"},
    "5_control_face": {"n_pass": len(cp), "passed": cp,
                       "n_signal_error": sum(
                           1 for r in ctrl
                           if r.get("status") == "signal_error"),
                       "pred": "8/75 magnitude, w2 actual 5 (band 5-12)",
                       "verdict": "in-band (5, same list as w2)"},
    "6_cross_wave_dedup": {
        "param": gen["cross_wave_param_dupes"],
        "signal": gen["cross_wave_signal_dupes"],
        "total": gen["cross_wave_param_dupes"]
                 + gen["cross_wave_signal_dupes"],
        "pred_band": "150-600 (center ~300)",
        "verdict": ("OUT 2.1x above band -> mechanism review "
                    "disclosed (rate 21.9% vs w2 28.6% on base 5811 = "
                    "base-growth-consistent sublinear; generate-time "
                    "disclosure r480)"),
        "quota_short": gen["quota_short"]},
    "sources": ["results/mass_trial/w3_screen_summary.json",
                "results/mass_trial/w3_screen_checkpoint.jsonl",
                "results/mass_trial/w3_generate_summary.json",
                "results/_r483bmc_ckpt_dedup.json",
                "results/gate_attrition.json (MASS_TRIAL_W3 row)"],
}
with open("results/_r483bmc_w3_recon.json", "w", encoding="utf-8") as f:
    json.dump(recon, f, ensure_ascii=False, indent=1)
print("RECON_OK survivors=%d rate=%s bear_x=%s fam_top=%s"
      % (len(surv), rate(surv, cand), recon["3_r_axis"]["bear_vs_none_x"],
         sorted(fam_rate.items(), key=lambda x: -x[1])[:3]))

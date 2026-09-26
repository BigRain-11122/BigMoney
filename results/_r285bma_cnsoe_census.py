"""R285 bm-a: CN_SOE_ETF_P1 results census for harvest + s7/s8 backfill."""
import json, io

d = json.load(open("results/cn_soe_ETF/p1_results.json", encoding="utf-8-sig"))
out = io.open("results/_r285bma_cnsoe_census.txt", "w", encoding="utf-8")

out.write("[top keys] " + str(list(d.keys())) + "\n")
out.write("[evidence_cutoff] " + str(d.get("evidence_cutoff")) + "\n")
out.write("[cutoff_meta] " + json.dumps(d.get("cutoff_meta"), ensure_ascii=False) + "\n")
out.write("[panel] " + json.dumps(d.get("panel"), ensure_ascii=False, default=str)[:400] + "\n")
out.write("[seed] " + str(d.get("seed")) + "\n")
out.write("[trials_ledger] " + json.dumps(d.get("trials_ledger"), ensure_ascii=False) + "\n")
out.write("[verdict_line] " + str(d.get("verdict_line"))[:300] + "\n")

cells = d.get("cells") or {}
out.write("\n=== cells ===\n")
for name, cv in cells.items():
    for face in (k for k in cv.keys() if not k.startswith("_")):
        f = cv[face]
        if not isinstance(f, dict):
            continue
        st = f.get("stats", {})
        out.write(name + "/" + face + ": sharpe=" + str(st.get("sharpe_full"))
                  + " ann=" + str(st.get("ann_ret"))
                  + " dd=" + str(st.get("max_dd"))
                  + " n_days=" + str(st.get("n_days"))
                  + " median|r|=" + str(st.get("median_abs_r"))
                  + " p999|r|=" + str(st.get("p999_abs_r"))
                  + " entries=" + str(f.get("entries"))
                  + " trades=" + str(f.get("trades")) + "\n")
        sk = f.get("skips") or {}
        if any((sk or {}).values()):
            out.write("   skips=" + json.dumps(sk, ensure_ascii=False) + "\n")
        ex = f.get("exits") or {}
        if ex:
            out.write("   exits=" + json.dumps(ex, ensure_ascii=False) + "\n")

gates = d.get("gates") or {}
out.write("\n=== gates (judged face) ===\n")
for name, g in gates.items():
    if not isinstance(g, dict):
        continue
    for gk, gv in g.items():
        if gk == "g1_prime_v2":
            ci = gv.get("bootstrap_ci", {})
            sl = gv.get("skill_line", {})
            out.write(name + " g1: pass_v2=" + str(gv.get("pass_v2"))
                      + " line_ok=" + str(gv.get("line_ok"))
                      + " sharpe=" + str(gv.get("sharpe_full"))
                      + " line=" + str(sl.get("line"))
                      + " n_eff=" + str(sl.get("n_eff"))
                      + " passive=" + str(sl.get("passive_term"))
                      + " mu_null=" + str(sl.get("mu_null"))
                      + " sigma_null=" + str(sl.get("sigma_null"))
                      + " pool=" + str(sl.get("pool"))
                      + " ci=[" + str(ci.get("ci95_low")) + "," + str(ci.get("ci95_high")) + "]"
                      + " ci_pos=" + str(gv.get("ci_lower_bound_positive"))
                      + " trade_gate=" + json.dumps(gv.get("trade_gate", {})) + "\n")
        elif gk == "dsr":
            out.write(name + " dsr: " + json.dumps(gv, ensure_ascii=False, default=str)[:260] + "\n")
        elif gk in ("g2", "g2_registration_v2"):
            out.write(name + " g2: " + json.dumps(gv, ensure_ascii=False, default=str)[:260] + "\n")
        elif gk == "d6_reject":
            out.write(name + " d6_reject: " + str(gv) + "\n")

d6 = d.get("d6") or {}
out.write("\n=== d6 ===\nreject_line=" + str(d6.get("reject_line"))
          + " members=" + str(d6.get("members")) + "\n")
for cname, cvals in (d6.get("cells") or {}).items():
    out.write("D6 " + cname + ": max_abs_corr=" + str(cvals.get("max_abs_corr"))
              + " reject=" + str(cvals.get("reject")) + "\n")

nul = d.get("nulls") or {}
out.write("\n=== nulls ===\ncoverage=" + json.dumps(nul.get("coverage"), ensure_ascii=False)
          + " pooled=" + str(nul.get("pooled_cohort_returns")) + "\n")

vs = d.get("virtual_starts") or {}
out.write("\n=== virtual_starts ===\nn_starts=" + str(vs.get("n_starts")) + "\n")
segs = vs.get("segments") or {}
out.write("segments=" + json.dumps(segs, ensure_ascii=False) + "\n")
for cname, cvals in (vs.get("cells") or {}).items():
    segline = " | ".join(k + ": n=" + str(s.get("n")) + " ret=" + str(s.get("mean_win_ret"))
                         + " beat=" + str(s.get("beat_rate"))
                         for k, s in (cvals.get("segments") or {}).items())
    out.write(cname + ": mean_ret=" + str(cvals.get("mean_win_ret"))
              + " beat6m=" + str(cvals.get("beat_rate_6m")) + " | " + segline + "\n")
    out.write("   oos_halves=" + json.dumps(cvals.get("oos_halves"), ensure_ascii=False)
              + " wf=" + json.dumps(cvals.get("walk_forward_sharpe"), ensure_ascii=False)
              + " split_agree=" + str(cvals.get("split_sign_agreement_pct")) + "\n")

rob = d.get("robust") or {}
out.write("\n=== robust dual nulls ===\n")
out.write(json.dumps(rob, ensure_ascii=False, default=str)[:1200] + "\n")

fp = d.get("family_pbo") or {}
out.write("\n=== family_pbo ===\n")
out.write(json.dumps({k: v for k, v in fp.items() if k != "per_combination"},
                     ensure_ascii=False, default=str)[:400] + "\n")

crisis = d.get("crisis_single_list")
out.write("\n=== crisis_single_list ===\n" + json.dumps(crisis, ensure_ascii=False, default=str)[:400] + "\n")

out.write("\n=== defect_disclosure ===\n"
          + json.dumps(d.get("defect_disclosure"), ensure_ascii=False, default=str)[:600] + "\n")
out.close()
print("census written")

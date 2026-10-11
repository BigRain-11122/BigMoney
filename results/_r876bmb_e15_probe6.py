import json
d = json.load(open(r"results\emotion_reeval\E15-REEVAL-2026-09-22.json", encoding="utf-8"))
out = {"batch": d["batch"], "cutoff": d["evidence_cutoff"], "m": d["member_count_m"],
       "eligible": d["eligible_reform"], "onboard": d["onboard_list"],
       "d6_rejected": d["d6_rejected"], "fdr": d["fdr"],
       "ew_ann": d["gates"]["five_member_ew_ann"],
       "ledger": d["ledger_delta"], "attrition": d["attrition_rows"]}
print(json.dumps(out, ensure_ascii=False, indent=1))
for cid, m in sorted(d["members"].items()):
    r = m["reform"]
    print(f"{cid} fam={m['details']['family']}")
    print(f"  p={r['p']} bh_q={r['bh_q']} fdr_pass={r['fdr_pass']} "
          f"composite={r['composite']} missing={r['missing_dims']} "
          f"eligible={m['eligible_reform']} d6_adm={m['d6_admitted']}")
    print(f"  d6_max={m['d6']['max_corr_vs_registered']} clash={m['d6']['clash']}")
    mm = m["member_metrics"]
    print(f"  ret: sharpe={mm['ret']['sharpe_full_L']} ann={mm['ret']['annualized_ret_L']} "
          f"ceiling={mm['ret']['return_ceiling_O1126']} beat6m={mm['ret']['beat6m_rate_L']} "
          f"beat12m={mm['ret']['beat12m_rate_L']}")
    print(f"  robust: x2={mm['robust']['cost_x2_sharpe_L']} "
          f"regime_min={mm['robust']['regime_min_sharpe_L']} "
          f"ci_low={mm['robust']['bootstrap_ci_low_L']}")
    print(f"  anti_of: pbo={mm['anti_overfit']['family_pbo']} "
          f"d6={mm['anti_overfit']['d6_max_abs_corr']}")
    print(f"  luck: batch_dsr={mm['anti_luck']['batch_dsr']}")
    print(f"  dim_scores={r['dim_scores']}")
    seg = m["details"]["regime_segments"]
    print(f"  segs: bear(n={seg['bear']['n_days']},s={seg['bear']['sharpe']}) "
          f"bull(n={seg['bull']['n_days']},s={seg['bull']['sharpe']}) "
          f"chop(n={seg['chop']['n_days']},s={seg['chop']['sharpe']})")
    old = m["details"]["old_line_face"]
    print(f"  old: g1={old['g1_sharpe_full']} line={old['g1_skill_line']} "
          f"margin={old['g1_margin']} global_dsr={old['global_dsr']} "
          f"g2={old['g2_eligible']}")

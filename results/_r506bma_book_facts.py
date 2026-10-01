# -*- coding: utf-8 -*-
"""r506 one-shot: pull PORTFOLIO_BOOK_P1 result facts for prereg §7 backfill."""
import json

r = json.load(open("results/portfolio_book/BOOK-2026-09-22.json", encoding="utf-8"))
print("verdict:", r["verdict"], "| ledger:", json.dumps(r.get("trials_ledger"), ensure_ascii=False))
g2m = r["g2_reform"]["members"]
for cid, p in r["configs"].items():
    sc = g2m[cid]
    print(f"{cid}: n={p['n_members']} sel={p['selected']}")
    print(f"  sharpe={p['sharpe_full_L']} x2={p['sharpe_x2_L']} x1dd={p['max_dd_x1']} "
          f"x2dd={p['max_dd_x2']} ann={p['annualized_ret_L']} ceiling={p['return_ceiling_O1126']}")
    print(f"  p={p['p_value']} bh_q={sc.get('fdr_q')} fdr_pass={sc.get('fdr_pass')} "
          f"composite={sc.get('composite')}")
    print(f"  loo_min={p['loo_min_sharpe']} loo_ratio={p['loo_ratio']} "
          f"div={p['diversification_delta']} ci_low={p['bootstrap_ci_low_L']} dsr={p['batch_dsr']}")
    print(f"  beat6m={p['beat6m']} rebal_cost={p['rebalance_cost_total']} "
          f"rebal_events={p['rebalance_events']} entry={p['entry_cost']} "
          f"cap_ann={p['cap_face']['annualized_ret_capped']}")
    print(f"  seg_min={p['regime_min_sharpe']} msa={p['monthly_start_ann']}")
rows = [json.loads(l) for l in open("results/gate_attrition.json", encoding="utf-8") if l.strip()]
print("attr tail:", [(x.get("batch"), x.get("verdict")) for x in rows[-2:]])

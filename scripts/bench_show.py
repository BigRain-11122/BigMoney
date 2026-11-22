"""Print a readable summary of a bench result file (no recomputation).

Usage: python scripts/bench_show.py results/bench_fut_trend.json
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main(path):
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    print(f"cell={d.get('cell')} cutoff={d.get('evidence_cutoff')} bars={d.get('coverage', {}).get('bars')}")
    for arm in d.get("arms", []):
        f, o = arm.get("common_window") or arm["full"], arm.get("oos_2024_after", {})
        print("-" * 100)
        print(f"{arm['style']:10s} {arm['verdict']:10s} full={f['ann_pct']}% sr={f['sharpe']} "
              f"mdd={f['mdd_pct']}%  oos={o.get('ann_pct')}% sr={o.get('sharpe')}")
        print(f"   halves={arm.get('first_half_ann_pct')}/{arm.get('second_half_ann_pct')}  "
              f"drop_best={f.get('drop_best_year_ann_pct')}  t={f.get('t_stat')}  "
              f"turnover={arm.get('turnover_per_year')}  cost={arm.get('cost_drag_ann_pct')}pp  "
              f"corr_csi={arm.get('corr_csi300')}")
        print(f"   control={arm.get('control')}")
        print(f"   checks={arm.get('checks')}")
        print(f"   years={f.get('years')}")
        print(f"   pnl_share={arm.get('per_product_pnl_share_pct')}")
    bh = d.get("benchmark_buy_and_hold")
    if bh:
        print("-" * 100)
        bw = bh.get("common_window") or bh["full"]
        print(f"buy_and_hold {bw['ann_pct']}% sr={bw['sharpe']} "
              f"mdd={bw['mdd_pct']}% oos={bh['oos_2024_after']['ann_pct']}% "
              f"sr={bh['oos_2024_after']['sharpe']}")
    ens = d.get("ensemble_of_passing")
    if ens:
        print("-" * 100)
        ew = ens.get("common_window") or ens["full"]
        print(f"ensemble {ens['styles']} {ew['ann_pct']}% sr={ew['sharpe']} "
              f"oos={ens['oos_2024_after']['ann_pct']}%")


if __name__ == "__main__":
    p = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "results", "bench_fut_trend.json")
    if not os.path.isabs(p):
        p = os.path.join(ROOT, p)
    main(p)

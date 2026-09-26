import json
d = json.load(open('results/aggr_capacity_face/p1_results.json', encoding='utf-8-sig'))
ay = d['adv_yearly']
# max demands across all units: COMPOSITE-CE-01 0.5*1e6*0.19=95k; VOLATILITY-CE-01 0.8*1e6*0.10=80k
mx = 95000.0
print("member-years whose cap1pct_median < 95k (max CE-sleeve demand):")
for s, years in sorted(ay.items()):
    for y, v in sorted(years.items()):
        if v['cap1pct_median'] < mx:
            print(f"  {s} {y}: cap1pct_median={v['cap1pct_median']:.0f} "
                  f"(p25 {v['p25']:.0f}) adv_med={v['median']/1e6:.2f}M")

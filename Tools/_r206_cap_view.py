import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
r = json.load(open("results/bond_capacity_wave3a.json", encoding="utf-8"))
print("evidence_cutoff:", r["evidence_cutoff"])
print("spot bucket_dist:", r["spot"]["bucket_dist"], "| non_convertible_n:", r["spot"]["non_convertible_n"])
u = r["unit"]
print("unit k median/p25/p75:", u["k_median"], u["k_p25"], u["k_p75"], "| n active:", u["n"])
print("measured_frac_of_sample:", r["capacity_verdict"]["measured_frac_of_sample"])
print()
print("== per-year (measured only) ==")
for y, v in r["per_year_adv20"].items():
    print("%s: n=%2d med=%14.0f p25=%14.0f p75=%14.0f uni_cap1pct=%14.0f"
          % (y, v["n_bonds"], v["median_adv20_cny"], v["p25_cny"], v["p75_cny"], v["universe_cap1pct_est_cny"]))
print()
print("== designs ==")
for d in r["capacity_verdict"]["designs"]:
    print("per_bond=%6d x n=%2d sleeve=%7d | tradable now all=%s top_third=%s"
          % (d["per_bond_cny"], d["n_bonds"], d["sleeve_cny"], d["tradable_frac_now_all"], d["tradable_frac_now_top_third"]))
    ys = d["tradable_frac_by_year"]
    print("   by year:", {y: f for y, f in ys.items() if f is not None})
print()
print("== top-third members (most liquid stratum) ==")
for b in r["per_bond"][:12]:
    if b.get("no_face"):
        tail = " NO-FACE"
    else:
        tail = " rows=%d last=%s adv20_last=%.0f zero_frac=%s" % (
            b["rows"], b["last_date"], b["adv20_last20_cny"], b["zero_volume_frac"])
    print(b["代码"], b["名称"], "| spot_amt=%.0f" % b["spot_amount_cny"], tail)

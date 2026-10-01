import json

r = json.load(open("results/refine_bench_stock/rev_p2/p2_results.json",
                   encoding="utf-8"))
print("batch:", r["batch"], "| cutoff:", r["evidence_cutoff"])
cf = r["closed_family"]
print("closed_family:", cf if not isinstance(cf, dict) else cf.get("closed",
      cf))
pbo = r["family_pbo"]
print("family_pbo:", round(pbo["pbo"], 3) if isinstance(pbo, dict) else pbo)
hdr = "{:34s} {:>7s} {:>5s} {:>5s} {:>5s} {:>5s}".format(
    "cell", "shp", "g1", "m1", "g2", "d6rj")
print(hdr)
npass = 0
for n, g in r["gates"].items():
    st = r["cells"][n]["x1"]["stats"]
    dsr = g["dsr"]
    dsr_ok = dsr.get("dsr_pass", dsr.get("pass", "?")) if isinstance(dsr,
             dict) else "?"
    g1p = g["g1_prime_v2"]["pass_v2"]
    if g1p:
        npass += 1
    print("{:34s} {:7.3f} {:>5s} {:>5s} {:>5s} {:>5s}".format(
        n, st["sharpe_full"], str(g1p), str(g["m1_t_face"]["gate"]),
        str(g["g2"]["eligible_v2"]), str(g["d6_reject"])))
print("G1'v2 pass:", npass, "/", len(r["gates"]))
print("verdict_line:", r["verdict_line"][:90])

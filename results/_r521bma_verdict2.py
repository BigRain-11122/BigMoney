import json

r = json.load(open("results/refine_bench_stock/rev_p2/p2_results.json",
                   encoding="utf-8"))
g0 = r["gates"]["D-15|raw|base|time|h20"]["g1_prime_v2"]
sl = g0["skill_line"]
print("skill_line keys:", sorted(sl.keys()))
for k in ("n_eff", "threshold", "passive", "null_mu", "null_sigma",
          "active", "line", "basis"):
    if k in sl:
        print("  ", k, "=", sl[k])
print("g1 block:", {k: g0[k] for k in g0 if k != "skill_line"})
d = r["gates"]["D-15|raw|base|time|h20"]["dsr"]
print("dsr keys:", sorted(d.keys())[:8])
print("dsr sample:", {k: d[k] for k in list(d)[:5]})
rob = r["robust"]["D-15|raw|base|time|h20"]
print("robust keys:", sorted(rob.keys()))
print("robust sample:", json.dumps(rob, ensure_ascii=False)[:400])
vs = r["virtual_starts"]
print("virtual_starts type:", type(vs).__name__)
if isinstance(vs, dict):
    k0 = list(vs)[:2]
    for k in k0:
        print("  ", k, ":", json.dumps(vs[k], ensure_ascii=False)[:240])
crisis = r["crisis_single_list"]
print("crisis type:", type(crisis).__name__, str(crisis)[:200])
for n in ("D-15|raw|base|time|h20", "D-15|yang|liq2|time|h20"):
    c = r["cells"][n]["x1"]
    st = c["stats"]
    print(n, "entries=", c["entries"], "trades=", c["trades"],
          "sharpe=", round(st["sharpe_full"], 4),
          "maxdd=", round(st.get("max_dd", -9), 4) if "max_dd" in st
          else [k for k in st])
print("stats keys:", sorted(r["cells"]["D-15|raw|base|time|h20"]["x1"]["stats"].keys()))
print("pbo block:", json.dumps(r["family_pbo"], ensure_ascii=False)[:200])

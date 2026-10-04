import json, os, csv
B = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
res = json.load(open(os.path.join(B, "results", "theme_judge_p2", "theme_judge_p2_results.json"), encoding="utf-8"))
o = []
def w(s):
    o.append(s)
w("== FACES ==")
for f, g in res["gates"].items():
    g1 = g["g1"]; sl = g1.get("skill_line", {})
    w("%s: sharpe_full=%s passive=%s null_mu=%s null_sigma=%s line=%s pass_v2=%s | g2_eligible=%s dsr=%s pbo_family_in_g2=%s n_entries=%s n_trades=%s t=%s" % (
        f, g1.get("sharpe_full"), g1.get("passive_sharpe") or sl.get("passive_source"), g["null_mu"], g["null_sigma"],
        sl.get("line"), g1.get("pass_v2"), g["g2"].get("eligible_v2"), g["dsr"].get("dsr"), g["g2"].get("family_pbo"),
        g1.get("trade_gate", {}).get("n_entries"), g1.get("trade_gate", {}).get("n_trades"), g["dsr"].get("T")))
    w("  skill_line detail: null_term=%s passive_term=%s mu_null=%s sigma_null=%s n_eff=%s pool=%s" % (
        sl.get("null_term"), sl.get("passive_term"), sl.get("mu_null"), sl.get("sigma_null"), sl.get("n_eff"), sl.get("pool")))
    w("  g1 sub: ci95=[%s,%s] ci_lower_bound_positive=%s" % (g1.get("bootstrap_ci", {}).get("ci95_low"), g1.get("bootstrap_ci", {}).get("ci95_high"), g1.get("ci_lower_bound_positive")))
w("== MAIN FACE ==")
w(json.dumps(res.get("m1_t_face"), ensure_ascii=False))
w(json.dumps(res.get("pbo_family"), ensure_ascii=False)[:400])
w("== CENSUS ==")
w(json.dumps(res.get("census"), ensure_ascii=False)[:600])
w("== LOO ==")
w(json.dumps(res.get("loo"), ensure_ascii=False)[:400])
w("== FAMOUS16 ==")
w(json.dumps(res.get("famous16"), ensure_ascii=False))
w("== TERCILES ==")
w(json.dumps(res.get("terciles"), ensure_ascii=False))
w("== REGIME ==")
w(json.dumps(res.get("regime_segments"), ensure_ascii=False))
w("== TRIALS LEDGER ==")
w(json.dumps(res.get("trials_ledger"), ensure_ascii=False)[:600])
w("== D6 ==")
w(json.dumps(res.get("d6_real"), ensure_ascii=False)[:400])
w("== FACTS ==")
w(json.dumps(res.get("facts"), ensure_ascii=False)[:800])
w("== SENSITIVITY keys ==")
sens = res.get("sensitivity") or (res.get("cells") or {}).get("sensitivity")
if isinstance(sens, dict):
    for k, v in list(sens.items())[:40]:
        if isinstance(v, dict):
            w("  %s: %s" % (k, json.dumps({kk: v[kk] for kk in list(v)[:8]}, ensure_ascii=False)[:240]))
        else:
            w("  %s: %s" % (k, str(v)[:200]))
# attrition row
att = json.load(open(os.path.join(B, "results", "gate_attrition.json"), encoding="utf-8"))
for e in att["entries"]:
    if e.get("batch") == "THEME-JUDGE-P2":
        w("== ATTRITION ROW ==")
        w("ts=%s delta=%s total_after=%s" % (e.get("ts"), e.get("cells_ledger_delta"), e.get("ledger_total_after")))
        w("gates.verdict main_face=%s" % e.get("gates", {}).get("main_face"))
# episodes cohort analysis (like P1)
import statistics
rows = list(csv.DictReader(open(os.path.join(B, "results", "theme_judge_p2", "episodes.csv"), encoding="utf-8")))
w("== EPISODES cohort (n=%d) ==" % len(rows))
cols = rows[0].keys()
w("columns=%s" % ",".join(cols))
by_face = {}
for r in rows:
    by_face.setdefault(r.get("face") or r.get("cell") or "?", []).append(r)
for face, rs in by_face.items():
    edges = [float(r["edge_pp"]) for r in rs if r.get("edge_pp") not in (None, "", "nan")]
    if not edges:
        # derive from sys_net_x1 - bh_net_x1 if present
        try:
            edges = [(float(r["sys_net_x1"]) - float(r["bh_net_x1"])) * 100 for r in rs]
        except Exception:
            edges = []
    if edges:
        edges.sort()
        n = len(edges)
        w("%s: n=%d best=%.1f%% worst=%.1f%% p25=%.1f%% med=%.1f%% p75=%.1f%% edge_mean=%.2fpp pos_share=%.1f%%" % (
            face, n, max(edges), min(edges), edges[n//4], edges[n//2], edges[3*n//4], sum(edges)/n, 100*sum(1 for x in edges if x>0)/n))
    # per-year cohort
    years = {}
    for r in rs:
        y = (r.get("entry_date") or r.get("date") or "?")[:4]
        try:
            e_ = (float(r["sys_net_x1"]) - float(r["bh_net_x1"])) * 100
        except Exception:
            continue
        years.setdefault(y, []).append(e_)
    neg_years = [y for y, v in sorted(years.items()) if sum(v) < 0]
    w("  neg_edge_years=%s" % ",".join(neg_years))
    for y in sorted(years):
        v = years[y]
        w("  %s: n=%d mean=%.2fpp" % (y, len(v), sum(v)/len(v)))
open(os.path.join(B, "results", "_r678bma_p2_numbers.txt"), "w", encoding="utf-8").write("\n".join(o))
print("WROTE %d lines" % len(o))

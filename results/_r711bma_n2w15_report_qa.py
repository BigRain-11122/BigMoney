# -*- coding: utf-8 -*-
"""r711 bm-a: QA evidence leg for CEO-REPORT-N2W15-20261005.md (product-priority law #4).

Re-derives every number cited in the report from the frozen source products
(zero hand-copy): screen json + judge json + r710 adoption receipt + prereg.
Receipt -> results/_r711bma_n2w15_report_qa.json + qa/report-n2w15-r711.md.
"""
import json, io, sys, re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

CHECKS = []


def ck(name, ok, detail=""):
    CHECKS.append((name, bool(ok), str(detail)))


screen = json.load(open("results/n2_w15/n2_w15_screen.json", encoding="utf-8"))
judge = json.load(open("results/n2_w15/n2_w15_judge.json", encoding="utf-8"))
verify = json.load(open("results/_r710bma_n2_judge_verify.json", encoding="utf-8"))
prereg = open("research/PERPETUAL_N2_W15_PREREG.md", encoding="utf-8").read()
report = open("docs/trial_labor/CEO-REPORT-N2W15-20261005.md", encoding="utf-8").read()

# -- funnel numbers --
ck("raw_5000_prereg", bool(re.search(r"raw \*\*5,000\*\*", prereg)), "prereg sec.3 draw volume")
ck("distinct_954", screen["n_distinct"] == 954, screen["n_distinct"])
ck("nulls_200", screen["k_nulls"] == 200, screen["k_nulls"])
ck("enrolled_1154", screen["batch_cells"] == 1154 == 954 + 200, screen["batch_cells"])
ck("survivors_281", screen["n_survivors"] == 281, screen["n_survivors"])
surv_rate_distinct = screen["n_survivors"] / screen["n_distinct"]
ck("surv_rate_29p5", abs(surv_rate_distinct - 0.295) < 0.0005, "%.4f" % surv_rate_distinct)
surv_rate_raw = screen["n_survivors"] / 5000
ck("surv_rate_raw_5p62", abs(surv_rate_raw - 0.0562) < 0.00005, "%.4f" % surv_rate_raw)
ck("predict_line_3pct_prereg", bool(re.search(r"存活者 \*\*≤ 3%\*\*", prereg)), "prereg sec.4 frozen prediction")
ck("enrichment_clause", bool(re.search(r"5\.62%（≥3%→富集条款触发", prereg)), "prereg sec.7 enrichment reconciliation")

# -- judge numbers --
ck("judge_cells_281", judge["n_judge_cells"] == 281, judge["n_judge_cells"])
ck("stage1_281", judge["n_stage1_survivors"] == 281, judge["n_stage1_survivors"])
ck("collapse_elim_0", judge["collapse_audit"]["eliminated"] == [], "eliminated empty")
ck("verdict_pass_0", judge["verdicts"]["pass"] == 0, judge["verdicts"]["pass"])
ck("verdict_fail_281", judge["verdicts"]["fail"] == 281, judge["verdicts"]["fail"])
ck("e_fp_14p05", abs(judge["n_wave_disclosure"]["E_FP_nominal_5pct"] - 14.05) < 1e-9,
   judge["n_wave_disclosure"]["E_FP_nominal_5pct"])
ck("e_fp_math", abs(281 * 0.05 - 14.05) < 1e-9, "281*0.05")
ck("pbo_A", abs(judge["family_pbo"]["A"]["pbo"] - 0.6857) < 1e-9 and judge["family_pbo"]["A"]["n_cells"] == 35,
   "pbo=%.4f n=%d" % (judge["family_pbo"]["A"]["pbo"], judge["family_pbo"]["A"]["n_cells"]))
ck("pbo_B", abs(judge["family_pbo"]["B"]["pbo"] - 0.4571) < 1e-9 and judge["family_pbo"]["B"]["n_cells"] == 246,
   "pbo=%.4f n=%d" % (judge["family_pbo"]["B"]["pbo"], judge["family_pbo"]["B"]["n_cells"]))
dc = judge["descriptive_counts"]
ck("dd_ok_281", dc["dd_ok"] == 281, dc["dd_ok"])
ck("no_crash_year_281", dc["no_crash_year"] == 281, dc["no_crash_year"])
ck("x2_stable_281", dc["x2_yearly_stable"] == 281, dc["x2_yearly_stable"])
ck("eligible_0", judge["n_eligible_g2_d6"] == 0 == len(judge["eligible_g2_d6"]), judge["n_eligible_g2_d6"])
ck("complete_true", judge["complete"] is True, judge["complete"])

# -- k_active segments (screen audit face) --
ka = screen.get("k_active_segmented_survival") or {}
ck("k1_25p1", ka.get("1", {}).get("n_survivors") == 74 and ka.get("1", {}).get("n_cells") == 295
   and abs(ka.get("1", {}).get("survival_rate", 0) - 0.251) < 0.0005, json.dumps(ka.get("1"), ensure_ascii=False))
ck("k4_35p9", ka.get("4", {}).get("n_survivors") == 47 and ka.get("4", {}).get("n_cells") == 131
   and abs(ka.get("4", {}).get("survival_rate", 0) - 0.359) < 0.0005, json.dumps(ka.get("4"), ensure_ascii=False))
ck("k7_peak_44p4", ka.get("7", {}).get("n_survivors") == 4 and ka.get("7", {}).get("n_cells") == 9
   and abs(ka.get("7", {}).get("survival_rate", 0) - 0.444) < 0.0005, json.dumps(ka.get("7"), ensure_ascii=False))

# -- ledger chain --
ts_screen = screen["trials_ledger"]
ck("screen_ledger", ts_screen["prev_total"] == 646799 and ts_screen["batch_trials"] == 1154
   and ts_screen["total"] == 647953, "%s+%s=%s" % (ts_screen["prev_total"], ts_screen["batch_trials"], ts_screen["total"]))
ts_judge = judge["trials_ledger"]
ck("judge_ledger", ts_judge["prev_total"] == 648730 and ts_judge["batch_trials"] == 281
   and ts_judge["total"] == 649011, "%s+%s=%s" % (ts_judge["prev_total"], ts_judge["batch_trials"], ts_judge["total"]))
ck("single_block", judge["n_trials_head_at_finalize"] == ts_judge["prev_total"],
   "head==prev %s" % judge["n_trials_head_at_finalize"])

# -- adoption receipt --
ck("adopt_verdict_pass", verify.get("verdict") == "ADOPT_PASS", verify.get("verdict"))
ck("adopt_pool_12of12", verify.get("pool_12of12_done") is True and verify.get("pool_prep_done") is True,
   "pool done=%r prep=%r" % (verify.get("pool_12of12_done"), verify.get("pool_prep_done")))
ck("adopt_ledger_head_live", verify.get("ledger_head_live") == 649011, verify.get("ledger_head_live"))
n_checks = len(verify.get("checks", {}))
ck("adopt_19_checks", n_checks == 19, n_checks)
_chk_vals = verify.get("checks", {})
n_ok = sum(1 for c in (_chk_vals.values() if isinstance(_chk_vals, dict) else _chk_vals)
           if c is True or (isinstance(c, dict) and c.get("ok") is True))
ck("adopt_all_checks_ok", n_ok == 19, "%d/19 ok" % n_ok)
seed_ok = json.dumps(verify, ensure_ascii=False)
ck("seed_545500", "545,500" in seed_ok or "545500" in seed_ok or
   "545,500" in json.dumps(judge, ensure_ascii=False), "seed face in receipts")

# -- timestamps --
ck("judge_ts", judge["generated"].startswith("2026-10-05T05:38:14"), judge["generated"])
ck("screen_ts", screen["generated"].startswith("2026-10-05T00:02:27"), screen["generated"])

# -- report file claims present --
for needle in ["5.62%", "29.5%", "14.05", "0.69", "0.46", "649,011", "ADOPT_PASS 19/19",
               "281/281", "44.4%", "25.1%", "2026-10-07 05:38"]:
    ck("report_has:" + needle, needle in report, needle[:40])

n_pass = sum(1 for _, ok, _ in CHECKS if ok)
n_fail = len(CHECKS) - n_pass
print("QA %d/%d PASS" % (n_pass, len(CHECKS)))
for name, ok, detail in CHECKS:
    print("  [%s] %s | %s" % ("PASS" if ok else "FAIL", name, detail))

receipt = {"ts": __import__("time").strftime("%Y-%m-%dT%H:%M:%S"),
           "round": "r711", "machine": "bm-a", "face": "CEO-REPORT-N2W15-20261005 QA",
           "n_pass": n_pass, "n_total": len(CHECKS), "all_ok": n_fail == 0,
           "checks": [{"name": n, "ok": o, "detail": d} for n, o, d in CHECKS]}
with open("results/_r711bma_n2w15_report_qa.json", "w", encoding="utf-8") as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)

lines = ["# QA evidence · CEO-REPORT-N2W15-20261005 (r711 bm-a)", "",
         "- source products: results/n2_w15/n2_w15_screen.json + n2_w15_judge.json + _r710bma_n2_judge_verify.json + research/PERPETUAL_N2_W15_PREREG.md",
         "- verifier: results/_r711bma_n2w15_report_qa.py (deterministic re-derivation, zero hand-copy)",
         "- verdict: **%d/%d PASS** @ %s" % (n_pass, len(CHECKS), receipt["ts"]), ""]
for name, ok, detail in CHECKS:
    lines.append("- [%s] %s | %s" % ("PASS" if ok else "FAIL", name, detail))
with open("qa/report-n2w15-r711.md", "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")

sys.exit(0 if n_fail == 0 else 1)

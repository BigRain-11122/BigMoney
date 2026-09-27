# r306 bm-a: post_review criteria registration for T-87 queue #5
# CN_MKTNEUTRAL_P1 (D-20260927-04 anchoring law: single stable artifact =
# results/cn_mkneutral/p1_results.json json_field faces + prereg s7/s8
# file_contains anchors + gate_attrition row; sectldr precedent shape).
import json

CRIT = "results/post_review_criteria.json"
with open(CRIT, encoding="utf-8-sig") as fh:
    c = json.load(fh)

c["items"] = [i for i in c["items"] if i.get("id") != "T-87-CN-MKTNEUTRAL-P1"]

item = {
    "id": "T-87-CN-MKTNEUTRAL-P1",
    "claim": "T-87 s2 queue #5 CN_MKTNEUTRAL_P1 (market-neutral stock-quintile x IC constant-short per SCHOOL_SUPPLY_S1 sec.4 queue ledger, heaviest-engineering slot: futures margin/roll cost + CTA no-reopen boundary disclosures) full arc: prereg frozen commit 3c71ddb4 BEFORE runner build BEFORE any run (R99 law; seed cn_mkneutral_p1=20279300 registered at freeze; N bill 2004) + runner selftest 42/42 hermetic incl hedge machinery (beta OLS/caps/fallback, lots rounding+sign, margin budget gate, roll-day proxy, NAV identity vs independent hand loop, cost twins) + real-data gate PASS R304 -> pool entry (workers_plan omission defect fixed R305, submit contract gate mechanized R306) -> autofill claim 08:40:08 latency 18.9min honest -> burn ~7min -> done-flip R306 BEFORE analysis (r302 law) -> 4/4 judged cells NEGATIVE per frozen s4 on x2 faces: Sharpe MN-REV20-BETA 0.4975 / MN-REV60-BETA 0.5577 / MN-REV20-H1 0.4680 / MN-REV60-H1 0.4802 vs own-null skill lines 0.6834/0.6862 (null_term, mu_null 0.3752) and 0.5606 (passive_term, mu_null 0.2244) ALL line_ok=False; bootstrap CI lower -0.107..-0.182 all <=0; DSR 0.0009-0.0021; family PBO 0.9286 >> 0.25 -> G2 eligible_v2=False 4/4; batch face cells_ok 4/4 TRUE (ann +4.7-5.9% / OOS 2025+ positive / maxDD -21.5..-25.4% / no crash year) = judged-negative semantics 'positive absolute returns but does not cross own-null calibrated line'; mu_null 0.3752 > 0.3 engineering flag FIRED per s5.1 -> post-flag check = beta machinery audit clean (caps binding both sides, fallbacks 2 window-start only, margin peak 14.7-16.8% in budget, NAV identity) -> drift attribution = mechanism face not accounting defect, verdict independent of attribution; D6 vs ew6 max 0.1196 zero reject, intra-batch 0.7526-0.9418 in predicted band; x1 > x2 4/4; robust sign-flip p 0.098-0.157 not significant; virtual starts 2026 (bull 416 / deep_bear 6 insufficient honest) beat_rate_6m 0.41-0.44 all <0.5; trials ledger 204,445+2,004=206,449 exact; row-16 market-neutral stream judged-closed with REV-TILT (hedged vehicle does not rescue the alpha; REV-TILT negative stands); reopen = new-evidence new-prereg only; s4 supply report = ZERO survivors to T-85 fusion pool (queue #1-#5 all judged-negative)",
    "claim_source": "research/CN_MKTNEUTRAL_PREREG.md (frozen 3c71ddb4, s7/s8 backfilled R306 single-finalization) + results/cn_mkneutral/p1_results.json product + results/gate_attrition.json entries row ts 2026-09-27 08:42:59 (runner self-landed) + pool done-flip R306 with result_ref",
    "status": "closed",
    "checks": [
        {"kind": "file_exists", "args": ["scripts/cn_mkneutral_p1.py"]},
        {"kind": "file_exists", "args": ["results/cn_mkneutral/p1_results.json"]},
        {"kind": "file_exists", "args": ["results/cn_mkneutral/cells_summary.csv"]},
        {"kind": "file_exists", "args": ["research/CN_MKTNEUTRAL_PREREG.md"]},
        {"kind": "json_field", "args": ["results/cn_mkneutral/p1_results.json", "evidence_cutoff", "2026-09-22"]},
        {"kind": "json_field", "args": ["results/cn_mkneutral/p1_results.json", "batch", "CN_MKTNEUTRAL_P1"]},
        {"kind": "json_field", "args": ["results/cn_mkneutral/p1_results.json", "trials_ledger.total", "206449"]},
        {"kind": "json_field", "args": ["results/cn_mkneutral/p1_results.json", "trials_ledger.batch_trials", "2004"]},
        {"kind": "json_field", "args": ["results/cn_mkneutral/p1_results.json", "panel.universe_n", "3106"]},
        {"kind": "json_field", "args": ["results/cn_mkneutral/p1_results.json", "gates.MN-REV20-BETA.g1_prime_v2.sharpe_full", "0.4975"]},
        {"kind": "json_field", "args": ["results/cn_mkneutral/p1_results.json", "gates.MN-REV60-BETA.g1_prime_v2.sharpe_full", "0.5577"]},
        {"kind": "json_field", "args": ["results/cn_mkneutral/p1_results.json", "gates.MN-REV20-H1.g1_prime_v2.sharpe_full", "0.468"]},
        {"kind": "json_field", "args": ["results/cn_mkneutral/p1_results.json", "gates.MN-REV60-H1.g1_prime_v2.sharpe_full", "0.4802"]},
        {"kind": "json_field", "args": ["results/cn_mkneutral/p1_results.json", "gates.MN-REV20-BETA.g1_prime_v2.pass_v2", "False"]},
        {"kind": "json_field", "args": ["results/cn_mkneutral/p1_results.json", "gates.MN-REV60-H1.g2.eligible_v2", "False"]},
        {"kind": "json_field", "args": ["results/cn_mkneutral/p1_results.json", "gates.MN-REV20-H1.dsr.dsr", "0.000912"]},
        {"kind": "json_field", "args": ["results/cn_mkneutral/p1_results.json", "gates.MN-REV20-BETA.g1_prime_v2.skill_line.line", "0.6834"]},
        {"kind": "json_field", "args": ["results/cn_mkneutral/p1_results.json", "family_pbo.pbo", "0.9286"]},
        {"kind": "json_field", "args": ["results/cn_mkneutral/p1_results.json", "virtual_starts.n_starts", "2026"]},
        {"kind": "json_field", "args": ["results/cn_mkneutral/p1_results.json", "d6.cells.MN-REV60-BETA.max_abs_corr", "0.0882"]},
        {"kind": "file_contains", "args": ["research/CN_MKTNEUTRAL_PREREG.md", "4/4 cells 判负照报"]},
        {"kind": "file_contains", "args": ["research/CN_MKTNEUTRAL_PREREG.md", "行 16 市场中性流派面 judged-closed"]},
        {"kind": "file_contains", "args": ["research/CN_MKTNEUTRAL_PREREG.md", "判负关槽"]},
        {"kind": "file_contains", "args": ["results/gate_attrition.json", "CN_MKTNEUTRAL_P1"]},
    ],
}
c["items"].append(item)
tmp = CRIT + ".tmp"
with open(tmp, "w", encoding="utf-8") as fh:
    json.dump(c, fh, ensure_ascii=False, indent=1)
import os
os.replace(tmp, CRIT)
chk = json.load(open(CRIT, encoding="utf-8-sig"))
it = [i for i in chk["items"] if i["id"] == "T-87-CN-MKTNEUTRAL-P1"][0]
print("criteria registered:", it["id"], "checks:", len(it["checks"]),
      "items total:", len(chk["items"]))

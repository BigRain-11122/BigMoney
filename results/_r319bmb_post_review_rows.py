"""R319 bm-b: post_review criteria rows for T-89/T-90 faces (O-20260924-2115).

Registers four review rows (append-only to results/post_review_criteria.json):
  1. T-89-S1-PROSPECT-SEGMENTS-FINALIZE  (r318 harvest finalize, backfill-in-
     registration: artifacts stable, claim frozen from prereg s6 caliber)
  2. T-90-V1-E2E-FINALIZE                (r318 chain verdict, same backfill law)
  3. T-89-S3-ATTACK-SUPPLY-MEMO           (this round, GM queue M-20260927-01)
  4. T-90-D4-CHAIN-HEALTH-WIRING          (this round, monthly four-piece wiring)

Check kinds restricted to the established registry set
(file_exists / json_field / file_contains); every json_field path probed
live before freezing (no invented paths). Idempotent: skips ids already
present.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CRIT = ROOT / "results" / "post_review_criteria.json"


def _fe(p):
    return {"kind": "file_exists", "args": [p]}


def _jf(p, expected):
    return {"kind": "json_field", "args": [p[0], p[1], expected]}


def _fc(p, needle):
    return {"kind": "file_contains", "args": [p, needle]}


ITEMS = [
    {
        "id": "T-89-S1-PROSPECT-SEGMENTS-FINALIZE",
        "claim": "T-89 slice-1 PROS_REGIME_SEGMENTS_P1 finalize PASS (bm-b r318, after T-93 30-shard receive dual-manifest verify): G-ANCHOR 22/22 byte-reconciled + G-CENSUS legacy n=1256/deep n=1506; pooled 6m base member-caliber legacy 0.5134 (n=27,632) / deep 0.4122 (n=33,132) both below 0.70 promotion line; segment pools legacy bear 0.6005/bull 0.3686/chop 0.5967; attack-corps candidates 0/22 both axes (top legacy bull DUCK-CE 0.4809); roles bear/chop dual-type only, zero bull-type; batch trials 60,764+2,762 passive = 63,526 (ledger total 269,975 single-count); MARKET_STAGE_TABLE 22x2 PROSPECT rows + change-log appended",
        "claim_source": "research/PROS_REGIME_SEGMENTS_P1.md (frozen prereg, s5 caliber) + results/prospect_regime_segments.json product + research/shortline/prospect_regime_segments_results.csv (528 rows) + ticket T-2026-09-26-89 progress_r318_bmb",
        "status": "open",
        "checks": [
            _fe("results/prospect_regime_segments.json"),
            _fe("research/shortline/prospect_regime_segments_results.csv"),
            _fe("research/PROS_REGIME_SEGMENTS_P1.md"),
            _jf(("results/prospect_regime_segments.json",
                 "evidence_cutoff"), "2026-09-22"),
            _jf(("results/prospect_regime_segments.json",
                 "axes.legacy.pooled_member_caliber_base_6m.beat_rate"), "0.5134"),
            _jf(("results/prospect_regime_segments.json",
                 "axes.legacy.pooled_member_caliber_base_6m.n"), "27632"),
            _jf(("results/prospect_regime_segments.json",
                 "axes.deep.pooled_member_caliber_base_6m.beat_rate"), "0.4122"),
            _jf(("results/prospect_regime_segments.json",
                 "axes.legacy.segments_pooled_base_6m.bull.beat_rate"), "0.3686"),
            _jf(("results/prospect_regime_segments.json",
                 "trials_ledger.batch_trials"), "63526"),
            _jf(("results/prospect_regime_segments.json",
                 "audit.verdict"), "CLEAN"),
            _fc("research/MARKET_STAGE_TABLE.md", "0/22"),
        ],
    },
    {
        "id": "T-90-V1-E2E-FINALIZE",
        "claim": "T-90 DECISION_CHAIN_E2E_P1 v1.1 verdict LANDED (bm-b r318): chain_win=False (base/x2 both faces, J-C1..C3 all fail, J-C4 dd line pass), J-TARGET 0/12 cells pass (worst legacy x2 24m A1 0.0228 vs B 0.5758, min_dd -0.3194), J-L half-ladder PASS both faces (base uplift 0.0363/0.0362, x2 0.0656/0.0312, dd within line); four-ring localization: ring1 temperature day-disagreement 0.7304 (1,032 days, disagreement starts -0.0203 vs agreement -0.0164 = version choice no rescue) + ring2 routing negative ALL regimes (base bear -0.0613/bull -0.0528/chop -0.0795, x2 all ~-0.12) + ring3 friction -0.0665pp base / -0.1266pp x2 (A1' zero-fee counterfactual still loses) + ring4 seat vacancy (attack corps 0 live, GREEN starts -0.0847 vs other -0.0987); batch N=16,566 envelope cells; version ledger v1.1 verdict LANDED (r319 record-flip, criteria untouched)",
        "claim_source": "research/DECISION_CHAIN_E2E_P1.md (v1.1 frozen, s9/s10 caliber) + results/decision_chain_e2e.json verdict face + research/DECISION_CHAIN_LEDGER.md v1.1 row + ticket T-2026-09-27-90 progress_r318_bmb",
        "status": "open",
        "checks": [
            _fe("results/decision_chain_e2e.json"),
            _fe("research/DECISION_CHAIN_LEDGER.md"),
            _jf(("results/decision_chain_e2e.json",
                 "verdict.chain_win"), "False"),
            _jf(("results/decision_chain_e2e.json",
                 "verdict.j_target_pass"), "False"),
            _jf(("results/decision_chain_e2e.json",
                 "verdict.ladder_pass"), "True"),
            _jf(("results/decision_chain_e2e.json",
                 "verdict.j_target.legacy.x2.24m.a1_beat_rate"), "0.0228"),
            _jf(("results/decision_chain_e2e.json",
                 "verdict.ring_table.base.ring2_routing.bull.mean_a1_minus_d_12m"),
                "-0.0528"),
            _jf(("results/decision_chain_e2e.json",
                 "seat_vacancy.attack_corps_live_count"), "0"),
            _jf(("results/decision_chain_e2e.json",
                 "trials_ledger.batch_trials"), "16566"),
            _fc("research/DECISION_CHAIN_LEDGER.md",
                "LANDED 2026-09-27 r318 finalize"),
        ],
    },
    {
        "id": "T-89-S3-ATTACK-SUPPLY-MEMO",
        "claim": "T-89 slice-3 attack-corps supply acceleration review memo delivered to GM queue (bm-b r319): M-20260927-01 in research/GM_REVIEW_MEMOS.md status PENDING; proposal = bull-specialist supply lanes to queue front (wave-1 momentum trio #81/#82/#83 prereg first, 35-library trend schools next); evidence = PROSPECT 0/22 attack candidates (T-89 finalize) + T-90 ring2 routing negative all regimes + ring4 seat vacancy + SCHOOL_SUPPLY_S1 queue #1-#5 all judged-negative (zero in-flight candidates = zero exclusion cost); queue re-order authority = GM face per O-20260927-0752 sec.2, zero law-touch before signature",
        "claim_source": "research/GM_REVIEW_MEMOS.md M-20260927-01 section + O-20260927-0752 sec.2 + ticket T-2026-09-26-89 spec item (3)",
        "status": "open",
        "checks": [
            _fc("research/GM_REVIEW_MEMOS.md",
                "M-20260927-01 · 进攻军供给提速提案"),
            _fc("research/GM_REVIEW_MEMOS.md", "PENDING（待 GM 审阅）"),
            _fc("research/GM_REVIEW_MEMOS.md", "0/22 进攻军候选"),
            _fc("research/GM_REVIEW_MEMOS.md", "queue #1-#5 已全判负收线"),
        ],
    },
    {
        "id": "T-90-D4-CHAIN-HEALTH-WIRING",
        "claim": "T-90 deliverable-4 monthly four-piece chain-health section wired (bm-b r319): scripts/monthly_briefing.py new section 六 (①当值态 + ②换军事件 + ③断环扫描 + ④偏好面进度) consuming results/decision_chain_e2e.json (verdict/ring_table/seat_vacancy/trials_ledger) + research/DECISION_CHAIN_LEDGER.md version rows + preference prereg glob (honest 缺件/缺口 branches on every input); selftest 19/19 incl. five new chain-health legs (four-piece render, verdict numbers, ledger version parse, preference honest gap, missing-file honesty); live-fire BRIEF-202609.md mid-month idempotent regeneration carries the section with real v1.1 numbers",
        "claim_source": "scripts/monthly_briefing.py (gather chain_health block + render section 六 + selftest legs) + results/briefings/BRIEF-202609.md + prereg DECISION_CHAIN_E2E_P1.md s7 downstream clause",
        "status": "open",
        "checks": [
            _fe("results/briefings/BRIEF-202609.md"),
            _fc("results/briefings/BRIEF-202609.md", "六、链条健康"),
            _fc("results/briefings/BRIEF-202609.md", "①当值态"),
            _fc("results/briefings/BRIEF-202609.md", "④偏好面进度"),
            _fc("results/briefings/BRIEF-202609.md", "45.57"),
            _fc("scripts/monthly_briefing.py", "chain_health"),
        ],
    },
]


def main():
    d = json.loads(CRIT.read_text(encoding="utf-8"))
    have = {it.get("id") for it in d["items"]}
    added = 0
    for item in ITEMS:
        if item["id"] in have:
            print(f"skip (present): {item['id']}")
            continue
        d["items"].append(item)
        added += 1
        print(f"append: {item['id']} ({len(item['checks'])} checks)")
    tmp = CRIT.with_suffix(".tmp")
    tmp.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n",
                   encoding="utf-8")
    tmp.replace(CRIT)
    print(f"registry now {len(d['items'])} items (+{added})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

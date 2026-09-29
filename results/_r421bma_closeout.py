# -*- coding: utf-8 -*-
"""_r421bma_closeout.py -- one-shot r421 closeout: round report line + state + heartbeat.

File-face writes per r406bm-b file-face law (CJK never through PS command channel).
Idempotent guards on each leg. Heartbeat epoch = python int(time.time()) (R170/R178
int-type law); clock_read = ISO 8601 with T separator (R262 law).
"""
import json
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "logs" / "iteration-loop" / "round_reports-bm-a.md"
STATE = ROOT / "state-bm-a.json"
HB = ROOT / "fleet" / "machines" / "bm-a.json"

NOW = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")
EPOCH = int(time.time())

REPORT_LINE = (
    NOW + " | r421 bm-a (dept:策略+研究·TRIAL_LABOR_LAW §1 常供线 W7 冻结轮) | "
    "WM-VERDICT: green-with-supply-floor-annotation (red=false lane healthy @09:02 watermark_red; "
    "probe py_low insufficient_history boot-window n=1 local_batch_running=true [moneyflow rank+AH refresh detached]; "
    "audit v2.4.1 FLAG supply_floor ready=0<3 standing + cap_violation [py 7.4%/cpu_total 93-97%=非仓面外部负载] -- "
    "supply duty ANSWERED THIS ROUND: W7 prereg freeze landed = supply line back in flight, "
    "W7-GENERATE pool entry = next-round runner-build slice) | did: "
    "S0-1 anchor bm-a; S0 pull x2 (bm-c r205/r206 dead-session harvests via stash-dance for autofill_state tick; "
    "MSG-0735 bmb->bmc archived by bm-c r205 confirmed); "
    "S0.5 orders 122/122 zero-diff (script diff) + decisions.md new rows D-20260929-02/03: "
    "D-02 (BigMoney slice-claim fetch law)= ALREADY EXECUTED by own r415, in-tree verified this round "
    "(fleet/README sec.4 v1.1 + Tools/inbox_guard.py + autofill submit()/pool_worker wiring + F-20260929-01 receipt) "
    "= receipt-only zero new execution; D-03 (BigDomain legal route) not-this-repo zero action; "
    "S1 smoke 26/26; S2 job_list 0 + board 0 open + watermark red=false next_pick=claimed; "
    "S3 MAIN = TRIAL_LABOR_W7 DRAFT+FREEZE same-window per standing law (pool 110/110 drained + W6 chain "
    "fully consumed = freeze trigger dual-gate MET): (1) probe results/_r421bma_tstate_probe.py built+fired "
    "-- census-verbatim TSTATE gates on sh510300 raw face: deep_pullback MAD60_q10 warmup 178 bars gate-true 383 "
    "open 11.59%; oversold_rsv RSV60_low<0.2 warmup 59 gate-true 632 open 18.46%; five-gate 32 cells 29 non-empty "
    "3 empty all in bull|calm|mad60 corner; 7 extreme days: 2015-07-27 mad true / 2025-04-07 both true / 5 closed; "
    "post-cutoff 3 rows excluded; in-round self-caught pandas dual-artifact pit (NaN<x->False pseudo-decidable + "
    "bool first_valid_index==0; honest decidable from underlying notna + argmax; CODELY.md batch-95) ; "
    "(2) research/TRIAL_LABOR_W7_PREREG.md sec.0-sec.9 FULL FROZEN (ten-tuple "
    "R/X/S/T/STOP/GATE/VOL/YANG/VCONF/TSTATE=580,608 axis combos; TSTATE mechanism=behavioral reversal at "
    "drawdown extremes, who-pays=panic sellers at extremes; honest not-orthogonal disclosure: bear-loading "
    "19.28%/33.44% vs bull 5.22%/5.62% = depth-refinement conditional gate NOT W6-VCONF-type independent dim; "
    "horizon-mismatch weak anchor census 20d vs engine 6m/12m/24m two-way martyrdom; exclusion book=judged "
    "7-sources ALL-landed zero declared-unavailable + screen 7-lists 149/404/166/513/461/372/293; DSR n_trials "
    "live head 333,432 cross-wave no-reset; consumer_plan O-1820(3)); (3) SEED_REGISTRY 3-keys same commit "
    "(trial_labor_w7_gen/scrnull/unc=20305000/20305500/20306000, three-step law ALL GREEN: 102-key inventory "
    "band zero-collision + first-elements distinct + rg code-face zero seed-face hits; data/daily CSV "
    "volume-column numeric hits=数据面非种子面 per W6 doc-berth precedent); (4) ticket T-2026-09-29-118 "
    "opened+claimed same round per O-1730; (5) F-04 MSG-20260929-0935-bma-ALL declared; "
    "S4 pit appended CODELY.md batch-95 (9,066B under 10KB hard line); "
    "S6 chain ALL exit-0 (dualrun ZERO-DRIFT streak 1/3; audit FLAG supply_floor+cap_violation honest; "
    "probe insufficient_history boot-window; update_daily/status; market_regime trigger breadth 0.83>=65%; "
    "scorecard 6/28/7 cards; clock_call ORANGE_COOL sleeves=4 activated=0; lhb/heat/futures/repo/options/"
    "sina_mf/ths_panel no-op or fresh; moneyflow+AH spawned detached; b_layer_filter verdict OK; system_v1 "
    "no-op idempotent; t35_export 09-28; daily_scorecard+report faces=5 token=1+ceo_live LIVE-2026-09-29 "
    "ORANGE rung 50% COOL; build_status; token_meter L2 0 today) | "
    "verify: prereg+probe facts+seeds+ticket+MSG all staged this window; science_gates import OK keys=102 "
    "w7=20305000/20305500/20306000; smoke 26/26 pre-S3; dualrun ZERO-DRIFT | "
    "next: W7 runner build slice OPEN to any healthy machine per prereg sec.9 (fetch-re-read inbox per "
    "D-02 dual-signal law): scripts/trial_labor_w7.py = W6 lineage + TSTATE overlay + bool-artifact selftest "
    "leg -> w7_grammar.json + TRIAL_GRAMMAR_LEDGER wave-7 row -> TRIAL-LABOR-W7-GENERATE pool entry with "
    "consumer_plan; W7-JUDGE = deep-panel host + RAM r354 + serial gate; 48h CEO clocks standing: W6 judge "
    "deadline 2026-10-01 08:14 (bm-b owns); 10-01 month-first triple + REGIME_GUARD v3 activate.\n"
)

STATE_OBJ = {
    "round_no": 421,
    "did": "r421: TRIAL_LABOR_W7 prereg DRAFT+FREEZE same-window (standing-law supply step, trigger dual-gate MET: "
           "W6 chain fully consumed ledger 333,432 + pool 110/110 drained): ten-tuple TSTATE timing-gate wave "
           "(deep_pullback MAD60_q10 + oversold_rsv RSV60_low<0.2 census-verbatim, 580,608 axis combos) frozen in "
           "research/TRIAL_LABOR_W7_PREREG.md + probe _r421bma_tstate_probe facts + SEED 3-keys "
           "20305000/20305500/20306000 same-commit + ticket T-118 claimed + F-04 MSG-0935 declared; "
           "D-20260929-02 receipt-only (r415 already executed, in-tree verified); CODELY pit batch-95 pandas "
           "NaN-comparison/bool-first_valid_index dual artifact; S6 chain all exit-0",
    "verify": "prereg+seeds+ticket+MSG committed this window; science_gates import OK (102 keys); smoke 26/26; "
              "dualrun ZERO-DRIFT streak 1/3; audit FLAG supply_floor standing answered by W7 supply action",
    "next": "W7 runner build slice open (any healthy machine, fetch-re-read first per D-02): trial_labor_w7.py "
            "(W6 lineage + TSTATE overlay + bool-artifact selftest leg) -> w7_grammar.json -> LEDGER wave-7 row -> "
            "TRIAL-LABOR-W7-GENERATE pool entry; W6 judge 48h CEO clock deadline 2026-10-01 08:14 (bm-b); "
            "10-01 month-first triple + REGIME_GUARD v3",
    "last_round_at": NOW,
    "current_task": "r421 W7 freeze round",
    "updated": NOW,
}

HB_EXTRA = {
    "last_seen": NOW,
    "current_task": "r421: W7 prereg frozen (TSTATE ten-tuple wave) + seeds + T-118 claimed + MSG-0935 declared; "
                    "runner build slice open next",
    "verdict": "r421 green: standing-law supply step executed -- WAVE-7 prereg DRAFT+FREEZE same-window "
               "(TSTATE timing-gate census-sourced axis, 580,608 combos, probe-anchored, seeds registered "
               "same commit, ticket T-118 claimed, F-04 MSG declared); D-02 receipt-only (r415 executed, "
               "in-tree verified); supply_floor breach answered by supply action (W7 chain = next pool entries "
               "after runner build); smoke 26/26; dualrun ZERO-DRIFT",
    "heartbeat_epoch_utc": EPOCH,
    "clock_read": NOW,
    "round_no": 421,
}


def main() -> int:
    # leg 1: round report append (idempotent on round marker)
    text = REPORT.read_text(encoding="utf-8")
    marker = NOW[:16] + " | r421 bm-a"
    if " | r421 bm-a (" in text:
        print("report: already-present no-op")
    else:
        if not text.endswith("\n"):
            text += "\n"
        REPORT.write_text(text + REPORT_LINE, encoding="utf-8")
        print("report: appended r421 line")

    # leg 2: state rewrite
    st = json.loads(STATE.read_text(encoding="utf-8"))
    st.update(STATE_OBJ)
    STATE.write_text(json.dumps(st, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("state: round_no ->", st["round_no"])

    # leg 3: heartbeat merge (preserve orders_ack + machine fields)
    hb = json.loads(HB.read_text(encoding="utf-8"))
    hb.update(HB_EXTRA)
    HB.write_text(json.dumps(hb, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    check = json.loads(HB.read_text(encoding="utf-8"))
    assert isinstance(check["heartbeat_epoch_utc"], int), "epoch must be JSON int (R170/R178 law)"
    print("heartbeat: epoch=%d (int OK) clock=%s orders_ack=%d" % (
        check["heartbeat_epoch_utc"], check["clock_read"], len(check.get("orders_ack", []))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

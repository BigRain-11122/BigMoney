# r771 bm-b bookkeeping: ledger row r771 + state.json round bump 770->771 + heartbeat bm-b.json write.
# Lineage: _r768bmb_bookkeeping.py pattern verbatim; CJK append utf-8 + tolerant read-back per pit-encoding.
import json, time, datetime

now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
epoch = int(time.time())

ROW_771 = (
 "2026-10-06T10:2x+08:00 | round 771 (bm-b, dept:engineering, r771 dead-session adoption + merge-mode integrate round) "
 "| [watermark verdict: GREEN (red=false lane healthy; satengine alive rc0 idle queue_depth=0; board 0 open jobs both "
 "boards; trio-in-flight = trial-labor line satisfied; free RAM 3.56GB <4GB heavy gate = zero new burn drafting "
 "legal)] | CEO three-line: current-work = FUND trio NULLS burns V1864/Q1534/D1256 of 2000 @10:2x (autofill+workers "
 "alive; V eta ~5h ~10-06 15:30 first-to-2000, Q eta ~10-07 morning, D eta ~10-08 morning; gate mechanical_ready=False "
 "G1=False G2/G3=True G4=PENDING governance window 10-05..10-09) | latest-artifact = qa/smoke-r771.md + qa/equity-"
 "curve-r771.png (QA charter pack 5/5: 3 syms x 800 bars real backtest 93 trades determinism=True sharpe 0.1586) + "
 "merge b7970cb2f (14-UU family-recipe resolve: compute_audit history union 201+207->208 + regime union + ts-new x11 "
 "all-ours 10:00-10:04 vs 09:52-09:54 + md twins follow-json; receipt results/_r771bmb_merge2_resolve.py "
 "VALIDATION ALL-PASS) + adopted dead-r771 S6 chain results/_r771bmb_s6_chain.json (35 executed legs all rc0 "
 "10:00-10:04) | next-milestone = trio V finalize ~10-06 15:30 (first-to-2000 same-window pool dual-flip per r668 "
 "law) + D-06 group closeout report 10-07 12:00 (23 pit files <=30KB re-verified r760) + market reopen 10-08 "
 "(REGIME_GUARD v3 first new bar) | S0: r771 dead-session adoption 5839782cc (S6 35-leg rc0 faces + chain "
 "driver/resolve workfiles + daemon churn; dead session committed pre-seat merge 4e07a066f then ran chain then died "
 "pre-QA/pre-S7, state stayed 770) + guarded-quartet origin-verbatim restore commit (host=bm-a faces per r769 merge "
 "law) + merge b7970cb2f 14-UU canonical + push rc0 ffce2936f..b7970cb2f verified 0/0 | S0.5: orders 154/154 zero "
 "unacked (O-*.md filter, README.md non-order per r764 law) + D-19 dual MATCH 7674E37B/2E73244B (results/"
 "_r771bmb_d19_read.py, sparse-clone r631/r677 recipe, zero disposition) + inbox MSG-2026-10-06-1009-bma-w156-seat "
 "processed (bm-a 72nd seat A 358_004..360_003 staircase 15th + B 360_004..360_203; bm-b zero rival seat, ack only, "
 "moved processed) | S1: smoke 48/48 | S3: satengine alive rc0 idle 0; watermark red=false next_pick=claimed advisory "
 "consumed as-is (moneyflow IC panel parked source-blocked bm-a lane legal); board 0 open (job_list empty + "
 "fleet/tasks zero status=open); leg39 trio probe V1864/Q1534/D1256 dup_k=0 x3 integrity True; finalize_trio_readiness "
 "mechanical_ready=False (G1=False G2=True G3=True) G4=PENDING | S6: adopted dead-session chain 35 legs rc0 (dualrun "
 "ZERO-DRIFT streak 51 face; compute_audit v2.4.2 rc0; golden-week legs 25-28 honest-skip cutoff 2026-09-30 unchanged "
 "reopen 10-08; REPORT-2026-10-06 + LIVE-2026-10-06 faces regen 10:00-10:04; token leg38 delta=0) | S7: quartet 4/4 "
 "(loop pin=2 no-op first-fire 10:32 + watchdog re-registered first-fire 10:32 + precommit/prepush claws "
 "LF-normalized content-match) + attrition guard CLEAN (4 ledgers, healed notes only) + inbox zero unread | "
 "verification: python -m smoke_test 48/48; QA pack r771 5/5 (qa/smoke-r771.md); adopted chain 35 legs rc=0 x35; "
 "merge resolver VALIDATION ALL-PASS; treasure zero-hit claim: no sweep/archive action this round (prescan not "
 "triggered) | next pointer: leg39 trio probe every round; V finalize dual-flip same-window per r668; D-06 closeout "
 "10-07 12:00 | local undelivered-to-origin commit count: PENDING_FILL_R771 | product score 2 (QA pack r771 real "
 "backtest 5/5 + adopted S6 35-leg product chain + 14-UU zero-loss merge landed)"
)

def main() -> int:
    # 1) ledger append (utf-8, append mode; tolerant read-back per r607; idempotent guard vs rerun)
    p = "logs/iteration-loop/round_reports.md"
    with open(p, "r", encoding="utf-8", errors="replace") as f:
        pre_tail = f.read()[-12000:]
    if "round 771 (bm-b" in pre_tail:
        print("ledger: r771 row already present (prior partial run), append skipped")
    else:
        with open(p, "a", encoding="utf-8", newline="") as f:
            f.write(ROW_771 + "\n")
    with open(p, "r", encoding="utf-8", errors="replace") as f:
        tail = f.read()[-12000:]
    assert "round 771" in tail, "ledger read-back miss"
    assert tail.count("round 771 (bm-b") == 1, "duplicate r771 row"
    print("ledger: r771 row in place, read-back ok (12KB window)")

    # 2) state.json (bm-b face) round bump 770 -> 771 per S7
    with open("state.json", "r", encoding="utf-8") as f:
        st = json.load(f)
    prev = st.get("round_no")
    assert prev == 770, "unexpected prev round_no %r" % prev
    st["round_no"] = 771
    st["round_no_label"] = "r771"
    st["note"] = ("r771: dead-session adoption close -- dead r771 session (pre-seat merge 4e07a066f + S6 chain "
                  "10:00-10:04 then died pre-QA/pre-S7) adopted this window: absorb 5839782cc + quartet origin-verbatim "
                  "+ merge b7970cb2f 14-UU canonical + push rc0; S0.5 154/154 + D-19 dual MATCH 7674E37B/2E73244B; "
                  "smoke 48/48; QA pack r771 5/5; trio V1864/Q1534/D1256 dup_k=0 G1 pending G4 PENDING; W156 seat "
                  "ack-only (bm-a 72nd)")
    st["last_round_at"] = now
    st["last_round_ts"] = now
    st["ts"] = now
    st["updated"] = now
    st["last_seen"] = now
    st["clock_read"] = now
    st["last_decisions_read_at"] = now
    st["last_orders_read_at"] = now
    st["next"] = ("(a) trio finalize windows: V 1864/2000 eta ~5h ~10-06 15:30 (first-to-2000 -> finalize round "
                  "same-window pool dual-flip per r668 law), Q 1534/2000 eta ~10-07 morning, D 1256/2000 eta ~10-08 "
                  "morning -- leg39 probe every round; (b) D-06 group closeout report 10-07 12:00 (23 pit files "
                  "<=30KB re-verified r760); (c) 10-08 market reopen window (external data legs + paper marks resume "
                  "+ REGIME_GUARD v3 first new bar)")
    with open("state.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(st, f, ensure_ascii=False, indent=1)
    with open("state.json", "r", encoding="utf-8") as f:
        st2 = json.load(f)
    assert st2["round_no"] == 771, "state round_no verify miss"
    print("state.json: r771 written, round_no verified")

    # 3) heartbeat bm-b.json (own file only; epoch int per R170/R178; clock_read T-sep per R262)
    with open("fleet/machines/bm-b.json", "r", encoding="utf-8") as f:
        hb = json.load(f)
    hb["last_seen"] = now
    hb["heartbeat_epoch_utc"] = epoch
    assert isinstance(hb["heartbeat_epoch_utc"], int), "epoch must be python int"
    hb["clock_read"] = now
    hb["cpu_cores"] = 16
    hb["free_ram_gb"] = 3.56
    hb["verdict"] = ("healthy: r771 complete (dead-session adoption + 14-UU merge b7970cb2f landed + QA 5/5); trio "
                     "burns in flight V1864/Q1534/D1256 of 2000; RAM 3.56GB <4GB heavy gate = zero new burn drafting "
                     "legal")
    hb["current_task"] = ("r771 dead-session adoption close: absorb + quartet restore + 14-UU canonical merge + QA "
                          "pack r771 landed")
    hb["now_active"] = ("FUND trio NULLS judgment batch lane V1864/Q1534/D1256 of 2000 @10:2x (autofill+workers "
                        "alive; V eta ~5h ~10-06 15:30 first-to-2000, Q eta ~10-07 morning, D eta ~10-08 morning)")
    hb["latest_artifact"] = ("qa/smoke-r771.md + qa/equity-curve-r771.png (QA pack 5/5, real backtest 93 trades "
                             "determinism=True sharpe 0.1586) + merge b7970cb2f (14-UU family-recipe zero-loss "
                             "resolve) + results/_r771bmb_s6_chain.json (35 legs rc0 adopted)")
    hb["next_milestone"] = ("trio V finalize ~10-06 15:30 (first-to-2000 same-window dual-flip per r668); D-06 group "
                            "closeout 10-07 12:00; market reopen 10-08 (REGIME_GUARD v3 first new bar)")
    hb["last_action"] = ("r771 closed: dead-session adoption + quartet origin-verbatim + merge b7970cb2f push rc0 + "
                         "S0.5 154/154 + D-19 dual MATCH + smoke 48/48 + QA r771 5/5 + S7 quartet green + attrition "
                         "CLEAN + W156 seat ack")
    hb["last_round_at"] = now
    hb["round_no"] = 771
    hb["round"] = 771
    hb["task"] = "FUND trio NULLS judgment batch lane (per-family finalize windows)"
    hb["ts"] = now
    hb["updated"] = now
    with open("fleet/machines/bm-b.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(hb, f, ensure_ascii=False, indent=1)
    with open("fleet/machines/bm-b.json", "r", encoding="utf-8") as f:
        hb2 = json.load(f)
    assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch int re-verify"
    assert "T" in hb2["clock_read"][:11], "clock_read T-separator re-verify"
    print("heartbeat: r771 written, epoch int + clock_read verified")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

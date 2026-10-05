# r767 bm-b bookkeeping: ledger rows x3 (r765/r766 POST-MORTEM backfill per r714 law + r767 own row)
# + state.json r767 write + heartbeat bm-b.json write.
# Lineage: r764/r766 bookkeeping pattern; CJK append utf-8 + tolerant read-back per pit-encoding
# (r607 legacy bad byte at 1432397 -> full-file strict reads forbidden, append-mode + errors='replace').
import json, time, datetime

now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
epoch = int(time.time())

ROW_765 = (
 "2026-10-06T07:5x+08:00 | round 765 (bm-b, POST-MORTEM BACKFILL per r714 law -- lane session died 06:5x pre-QA/pre-S7, "
 "state stayed 764; row backfilled by r767 from commit 73c5b1e6e absorb evidence + state r766 note) | S6: 39-leg chain "
 "35 executed legs all rc0 06:46:xx-06:51:44 (products REPORT-2026-10-06/LIVE-2026-10-06/scorecard/dualrun/panel regen; "
 "legs 25-28 golden-week honest-skip, cutoff 2026-09-30 unchanged) | merges: r764 integration merge-1 b884d4d16 06:26 + "
 "r765 merge-2 behind-5 14-UU canonical resolve receipts (both absorbed verbatim by 73c5b1e6e 06:56 46-face churn-absorb; "
 "session died pre-QA/pre-S7/pre-state-write) | product disposition: all products landed via r766 absorb commit + r767 "
 "closeout 1f82049a6 | product score 0 for this disclosure row (products credited to absorb windows per r620 law)"
)

ROW_766 = (
 "2026-10-06T07:5x+08:00 | round 766 (bm-b, POST-MORTEM BACKFILL per r714 law -- session died post-state-write 07:16:46 "
 "pre-final-commit pre-ledger-row; row backfilled by r767 from commits bb18daf0c/3f2278e98 + state.json r766 note + "
 "qa/smoke-r766.md pack) | S0: r765 dead-session full-product absorb 73c5b1e6e (46 faces) + merge behind-5 15-UU "
 "canonical bb18daf0c 07:01 (bm-c r601 close + r602 churn + bm-a r761 W149 freeze+ignition absorbed; 6 CLI "
 "merge_lane_views union/cutoff + 9 regen twins ts-newer-wins all-ours 06:48-06:50 vs theirs 06:37-06:38; receipt "
 "_r766bmb_merge_resolve.json) + phantom-deletion claw push-race loop-2 13-UU 3f2278e98 07:03 per r759 law (origin +4 = "
 "bm-c r602 W149-held + bm-a r762 W149 finalize ledger 723,811 + W150 seat; 6 CLI all-theirs-newer 06:56 + 7 regen "
 "twins theirs 06:56:23-47 vs ours 06:50; receipt _r766bmb_merge2_resolve.json) zero --no-verify | S0.5: orders 154/154 "
 "zero unacked + D-19 dual MATCH 7674E37B/2E73244B (sparse-clone r677 recipe _r766bmb_d19_read.py) | S1: smoke 48/48 | "
 "S6: r765 39-leg face absorbed | QA pack r766 5/5 (qa/smoke-r766.md + equity-curve-r766.png, 93 trades determinism=True) "
 "| 5x HANDOVER backfill row r756-766 (missed cuts r760/r765 disclosed) | state honest jump 764->766 per r714 law | "
 "leg39 trio probe V1777/Q1460/D1199 dup_k=0 G1 pending | final products commit eaten by session death -> landed by "
 "r767 S0 closeout absorb 1f82049a6 | product score 2 (dual merge windows landed + QA pack 5/5 + 5x HANDOVER backfill)"
)

ROW_767 = (
 "2026-10-06T07:5x+08:00 | round 767 (bm-b, dept:engineering, golden-week steady-state guard round + r765/r766 "
 "dead-tail ledger backfill + r758 rebase-cure S0 window) | [watermark verdict: GREEN (red=false lane healthy; "
 "satengine alive rc0 idle queue_depth=0 py 56.8%; board 0 open jobs both boards; trio-in-flight = trial-labor line "
 "satisfied; free RAM 2.81GB <4GB heavy gate = zero new burn drafting legal)] | CEO three-line: current-work = FUND "
 "trio NULLS burns V1795/Q1474/D1212 of 2000 @07:35 (+18/+14/+13 vs r766 06:51 face; autofill+workers alive; V eta "
 "3.42h ~11:00 today = first-to-2000, Q eta 8.77h ~16:20, D eta 42.9h ~10-08; G4 PENDING sha unmoved 7674E37B r638 "
 "fallback armed, window 10-05..10-09) | latest-artifact = qa/smoke-r767.md + qa/equity-curve-r767.png (QA charter "
 "pack 5/5: 3 syms x 800 bars real backtest 93 trades determinism=True sharpe 0.1586) + results/_r767bmb_s6_chain.log "
 "(35 executed legs all rc0 07:31:xx-07:35:11, lineage r765 verbatim zero legdiff, detached ignition PID 55952 "
 "both-redirect per r737 law) | next-milestone = trio V finalize ~11:00 today (first-to-2000 same-window pool "
 "dual-flip per r668 law) + D-06 group closeout report 10-07 12:00 (23 pit files <=30KB re-verified r760) + market "
 "reopen 10-08 (REGIME_GUARD v3 first new bar) | S0: r766 closeout absorb committed d7953893c (24 files: qa r766 pack "
 "+ merge resolve receipts/workfiles + HANDOVER 5x backfill + state r766 + lane daemon churn) -> pull --rebase 1-UU "
 "(results/_attrition_guard_scan.json regen twin: origin ts 07:15:33 bm-c r603 > ours 07:14:37 r766 S7 -> HEAD side "
 "taken per ts-newer-wins, rest byte-identical) -> rebase --continue fake refusal per r758 law (index clean, "
 "ls-files -u=0, zero UU) -> manual cure chain: git commit -F .git/rebase-merge/message = 1f82049a6 + rebase --quit + "
 "branch -f main first-attempt blocked (main used-by-worktree mid-rebase state) + stash-guard (4 daemon live faces) "
 "+ git reset --hard 1f82049a6 + stash pop clean -> main reattached, ahead-of-origin +2, merge-base = origin tip "
 "54912422a verified | S0.5: orders 154/154 zero unacked (full-set diff; own-probe .md-suffix format miss caught "
 "in-window, re-diff clean) + D-19 dual MATCH 7674E37B/2E73244B (verbatim lineage script _r767bmb_d19_read.py, "
 "sparse-clone r631/r677 recipe) | S1: smoke 48/48 | S3: satengine alive rc0 idle 0; watermark red=false "
 "next_pick=claimed advisory consumed as-is (moneyflow IC panel parked source-blocked bm-a lane legal); board 0 open "
 "(job_list empty + fleet/tasks zero status=open, 172 tickets all claimed/closed); trio in-flight = trial-labor "
 "satisfied | S6: 35 executed legs all rc0 (dualrun ZERO-DRIFT streak 51/403 entries; compute_audit v2.4.2 py 86.9% "
 "burning-healthy zero flags; golden-week legs 25-28 honest-skip cutoff 2026-09-30 unchanged reopen 10-08; "
 "REPORT-2026-10-06 + LIVE faces regen; token delta=0; leg39 trio probe V1795/Q1474/D1212 integrity True dup_k=0 "
 "mechanical_ready=False G1 burn_complete=False G4 PENDING) | S7: quartet 4/4 (loop pin=2 phase-ok no-op first-fire "
 "07:32 + watchdog re-registered idempotent first-fire 07:33 + precommit/prepush claws LF-normalized content-match) + "
 "attrition guard CLEAN (4 ledgers, healed rows historical) + inbox zero unread | verification: python -m smoke_test "
 "48/48; QA pack r767 5/5 (qa/smoke-r767.md); S6 summary 35 legs rc=0 x35; treasure zero-hit claim: no sweep/archive "
 "action this round (prescan not triggered) | ledger backfill: r765/r766 rows backfilled same-window per r714 law | "
 "next pointer: leg39 trio probe every round; V finalize dual-flip same-window per r668; D-06 closeout 10-07 12:00 | "
 "local undelivered-to-origin commit count: PENDING_FILL_R767 | product score 2 (S6 product chain 35 rc0 + QA pack "
 "r767 5/5 + r765/r766 recovery backfill + rebase cure zero-loss)"
)

def main() -> int:
    # 1) ledger append (utf-8, append mode; tolerant read-back per r607; idempotent guard vs rerun)
    p = "logs/iteration-loop/round_reports.md"
    rows = [ROW_765, ROW_766, ROW_767]
    with open(p, "r", encoding="utf-8", errors="replace") as f:
        pre_tail = f.read()[-12000:]
    if "round 767 (bm-b" in pre_tail:
        print("ledger: r767 row already present (prior partial run), append skipped")
    else:
        with open(p, "a", encoding="utf-8", newline="") as f:
            f.write("\n".join(rows) + "\n")
    with open(p, "r", encoding="utf-8", errors="replace") as f:
        tail = f.read()[-12000:]
    assert "round 765" in tail and "round 766" in tail and "round 767" in tail, "ledger read-back miss"
    assert tail.count("round 767 (bm-b") == 1, "duplicate r767 row"
    print("ledger: 3 rows in place, read-back ok (12KB window)")

    # 2) state.json (bm-b face)
    with open("state.json", "r", encoding="utf-8") as f:
        st = json.load(f)
    st["round_no"] = 767
    st["round_no_label"] = "r767"
    st["note"] = ("r767: r766 closeout absorb landed 1f82049a6 (rebase 1-UU attrition regen twin ts-newer-wins + r758 "
                  "fake-refusal cure chain + main reattach merge-base=origin tip) + ledger backfill r765/r766 per r714 "
                  "+ S6 35 legs rc0 07:31-07:35 + QA pack r767 5/5 + S0.5 orders 154/154 + D-19 dual MATCH "
                  "7674E37B/2E73244B + leg39 trio probe V1795/Q1474/D1212 G1 pending G4 PENDING")
    st["last_round_at"] = now
    st["last_round_ts"] = now
    st["ts"] = now
    st["updated"] = now
    st["last_seen"] = now
    st["clock_read"] = now
    st["last_decisions_read_at"] = now
    st["last_orders_read_at"] = now
    st["next"] = ("(a) trio finalize windows: V 1795/2000 eta 3.42h ~10-06 11:00 (first-to-2000 -> finalize round "
                  "same-window pool dual-flip per r668 law), Q 1474/2000 eta 8.77h ~10-06 16:20, D 1212/2000 eta "
                  "42.9h ~10-08 morning -- leg39 probe every round; (b) D-06 group closeout report 10-07 12:00 "
                  "(23 pit files <=30KB re-verified r760); (c) 10-08 market reopen window (external data legs + "
                  "paper marks resume + REGIME_GUARD v3 first new bar)")
    with open("state.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(st, f, ensure_ascii=False, indent=1)
    with open("state.json", "r", encoding="utf-8") as f:
        st2 = json.load(f)
    assert st2["round_no"] == 767, "state round_no verify miss"
    print("state.json: r767 written, round_no verified")

    # 3) heartbeat bm-b.json (own file only; epoch int per R170/R178; clock_read T-sep per R262)
    with open("fleet/machines/bm-b.json", "r", encoding="utf-8") as f:
        hb = json.load(f)
    hb["last_seen"] = now
    hb["heartbeat_epoch_utc"] = epoch
    assert isinstance(hb["heartbeat_epoch_utc"], int), "epoch must be python int"
    hb["clock_read"] = now
    hb["cpu_cores"] = 16
    hb["free_ram_gb"] = 2.81
    hb["gpu_free_vram_gb"] = 3.2
    hb["gpu_free_vram_mb"] = 3280
    hb["verdict"] = ("healthy: r767 complete (r766 closeout absorb + rebase cure + S6 35 rc0 + QA 5/5 + ledger "
                     "backfill r765/r766); trio burns in flight V1795/Q1474/D1212 of 2000; RAM 2.81GB <4GB heavy "
                     "gate = zero new burn drafting legal")
    hb["current_task"] = ("r767 golden-week steady-state guard: r766 closeout absorb + r758 rebase-cure window + "
                         "S6 35 legs + QA pack + r765/r766 ledger backfill landed")
    hb["now_active"] = ("FUND trio NULLS judgment batch lane V1795/Q1474/D1212 of 2000 @07:35 (autofill+workers "
                        "alive; V eta 3.42h ~11:00 first-to-2000, Q eta 8.77h ~16:20, D eta 42.9h ~10-08)")
    hb["latest_artifact"] = ("qa/smoke-r767.md + qa/equity-curve-r767.png (QA pack 5/5, real backtest 93 trades "
                             "determinism=True sharpe 0.1586) + results/_r767bmb_s6_chain.log (35 legs rc0)")
    hb["next_milestone"] = ("trio V finalize ~10-06 11:00 (first-to-2000 same-window dual-flip per r668); D-06 "
                            "group closeout 10-07 12:00; market reopen 10-08 (REGIME_GUARD v3 first new bar)")
    hb["last_action"] = ("r767 closed: S0 closeout absorb 1f82049a6 + rebase 1-UU ts-newer-wins + r758 cure + "
                         "S0.5 154/154 + D-19 dual MATCH + S6 35 rc0 + QA r767 5/5 + S7 quartet green + ledger "
                         "backfill r765/r766")
    hb["last_round_at"] = now
    hb["round_no"] = 767
    hb["round"] = 767
    hb["task"] = "FUND trio NULLS judgment batch lane (per-family finalize windows)"
    hb["ts"] = now
    hb["updated"] = now
    with open("fleet/machines/bm-b.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(hb, f, ensure_ascii=False, indent=1)
    with open("fleet/machines/bm-b.json", "r", encoding="utf-8") as f:
        hb2 = json.load(f)
    assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch int re-verify"
    assert "T" in hb2["clock_read"][:11], "clock_read T-separator re-verify"
    print("heartbeat: r767 written, epoch int + clock_read verified")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

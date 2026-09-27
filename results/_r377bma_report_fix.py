# r377 bm-a: fix the R377 round-report line mangled by the PS console
# codepage (GBK) on its first append -- rewrite ONLY that last line with
# the intended UTF-8 text; every other line stays byte-untouched.
import io

PATH = r"logs/iteration-loop/round_reports-bm-a.md"
FIXED = (
    "2026-09-28T04:20:00+08:00 | R377 bm-a (dept:工程+舰队·r376 坑律工程债收口=resolve 配方统一轮) "
    "| WM first-line verdict: green (red=false lane healthy; probe 03:43 py_low_board_clear "
    "legal-idle n=3 span 29.1min avg_py 0.4%: board 0 open / bandit 0 / pool non-done 7 = "
    "W2B waiting lane=bm-b + V2-P1 ready lane=bm-b R31 no-touch + 4 MASS-TRIAL judge shards + "
    "TRIAL-LABOR-W1-JUDGE waiting on bm-b declare/RAM gates; audit v2.3 03:43 CLEAN py 0.8% "
    "flags=[] load_state pool-supply-gap) | did: S0-1 anchor bm-a + S0 clean-tree pull FF "
    "cff07511 (bmb r357 W2A flip: CENSUS-FUS-S2-W2A done, N=5,920=5,456cand+64rs+400nulls, "
    "ledger 294,304, pool 88) + S0.5 orders 99/99 zero-unacked + decisions: D-20260928-02①/"
    "D-03① receipts maintained (autofill r201 guard in-tree + loop phase pin bm-a=8 live "
    "no-op this round), D-04/05/06 non-BigMoney zero-action, council C-01 seat-3 opinion "
    "issued r326 F-20260927-02 zero re-issue (window 09-29 12:00) + C-02 seat-3 issued "
    "F-20260928-01 (window 09-29 ~10:0x) + S1 smoke 25/25 + S2 board zero-open job_list "
    "empty + S3 CLOSED LOOP = D-03③ resolve-recipe-unification engineering debt LANDED "
    "(r376 pitlaw: resolve 件禁手写 union): merge_lane_views.py NEW resolve subcommand -- "
    "detect_face fail-closed (lane files R31 machine-authority / non-ALL_FACES -> skill "
    "recipes) + resolve_face_from_blobs (sources order :2:=origin-side first r351 "
    "orientation, :3:=replay-side, :1: merge-base last; same-second tie -> origin r140) + "
    "CLI reads git index stages directly + --stageN/--out forensics replay mode + "
    "parse-verify r185 + same-window reconcile reminder + CRLF mirror r223/r234 + selftest "
    "+7 legs (detect x3 / autofill double-store collapse r376 shape / pool gov-pinned r370 / "
    "take-new tie origin / no-stages fail-closed) 44/44 PASS + LIVE-FIRE = r376 historical "
    "three blobs (:2:=c130be39 bmb 51-double-store / :3:=88140393 bma fixed / :1:=53be4125 "
    "base) via CLI resolve --out -> SEMANTIC-EQUAL True vs landed 63dbbc0e (50 launches, "
    "V2-P1 enriched single row crash_counted=true preserved, last_tick 03:30:02) = pitlaw "
    "upgraded from should-import to one-command + SKILL twins (Tools + .codely-cli) routing "
    "line synced twins-identical True + LANE_MIGRATION_S1 §六 r377 record + S4 CODELY.md +1 "
    "pointer line 7,812B<=10KB + S6 31 legs ALL rc=0 Monday pre-market no-op family "
    "zero-masked (daily 0-new cutoff 09-24 + regime ORANGE shadow #10 hs300<MA200 breadth "
    "0.77 + scorecard 6strat/28trader/7port S=2 A=4 best VOLATILITY-CE-01 87.0 + clock "
    "CALL-0924 ORANGE_COOL sleeves=4 activated=0 + lhb <30min + heat pre-15:30 + futures/"
    "repo/options cutoff-covered zero-network + MF rank-throttle 10.4min + sinaMF covered + "
    "astock/revosc/alloc/fp lane-guards stdout-only honest + ths same-day idempotent + ah "
    "spawn-throttle 9min + fundamental 6.0h fresh-skip + b_layer 5222 5-gates pass "
    "ok_static 3517 excluded 1705 + 3 bar-gated legal skips live.paper/t35v/t24a + t24 "
    "promo 0/22 honest NOT-ELIGIBLE legs 0/0/0 + aggr/grid/sysv1 idempotent marks@cutoff + "
    "t35exp 09-24 6traders 18pos equity 5,996,645 + dsc + daily_report REPORT-2026-09-28 "
    "faces=4 token=1 + build_status 432combos + token delta=0 crash-fuse refusals=4/2sig "
    "owner-face disclosed) + post-chain reconcile 14/14 ZERO-DRIFT (consumer-switch stable "
    "readings continue) + S7 self-heal 4/4 (IterationLoop Running / LoopWatchdog Ready "
    "04:10 / Autofill Ready 03:50 / IntradayMarks Ready Mon 09:25 = T-91 ARMED) + claw "
    "identical + inbox zero-inbound | verify: smoke 25/25 + merger selftest 44/44 + resolve "
    "live-fire SEMANTIC-EQUAL True + py_compile rc=0 + twins-identical True + S6 31 rc=0 "
    "zero-masked + reconcile 14/14 zero-drift + orders 99/99 + schtasks 4/4 | next: "
    "①batch-3 C-family (dashboard_status/daily_scorecard/paper 族确定性重 derive+"
    "l3_activation_table) 照 §五协议 ②B 面读数随 bmb/bmc 拉取累计（三源拓扑）③批1 撤共享写面="
    "全机队消费切换码拉齐+读数稳定后 ④TODAY 09:15 T-91 s3 first-marks auto-fire (IntradayMarks "
    "09:25 armed; first bar ~15:30 -> live.paper enforce + t35 verify + exports; sysv1 "
    "first SIG via bm-b BARS evening) ⑤V2-P1 finalize done-flip watch (bm-b lane owner "
    "face; fuse refusals accumulating) ⑥MASS-TRIAL judge shards + TRIAL-LABOR-W1-JUDGE "
    "flip-ready watch -> my s3 dual-axis shard claim per MSG-0030 on bm-b declare "
    "⑦council C-01 window 09-29 12:00 / C-02 09-29 ~10:0x; next 5x=R380 HANDOVER"
)

with io.open(PATH, encoding="utf-8") as fh:
    lines = fh.read().splitlines(keepends=False)
assert lines and lines[-1].startswith("2026-09-28T04:20:00+08:00 | R377 bm-a"), \
    "last line is not the mangled R377 line -- abort"
assert "宸ョ▼" in lines[-1] or "鈶" in lines[-1], "mojibake marker absent -- abort"
lines[-1] = FIXED
with io.open(PATH, "w", encoding="utf-8", newline="") as fh:
    fh.write("\n".join(lines) + "\n")

with io.open(PATH, encoding="utf-8") as fh:
    back = fh.read().splitlines()
assert back[-1] == FIXED, "read-back mismatch"
assert "宸" not in back[-1] and "鈶" not in back[-1], "mojibake survived"
print(f"R377 line fixed in place: {len(back)} lines, last line {len(back[-1])}B, clean")

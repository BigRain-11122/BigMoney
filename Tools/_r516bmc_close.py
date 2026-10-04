# -*- coding: utf-8 -*-
"""r516 bm-c close: state round 516, heartbeat, round-report ledger row,
scratch mirror cleanup. JSON in/out via python (PS ConvertTo-Json pit-free),
UTF-8 no BOM, EOL preserved per host file (append-mode probe)."""
import datetime
import json
import os
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TS = "2026-10-05T05:38:55+08:00"
EPOCH = 1791149937
CPU = 15
RAM = 6.5
GPU = 765

DID = ("r516 bm-c: watch/maintenance + QA-charter evidence-pack round (boards open=0, "
       "judgment seats on other machines, golden-week no bar). (1) S0 fetch behind=0 "
       "ahead=0, dual watermark MATCH (decisions 755428F8 / orders 3BF0F16E) zero action. "
       "(2) S0.5 dual scan orders 154/154 acked rc0, inbox 0 unread. (3) S1 smoke 48/48 "
       "(05:26). (4) S2 boards empty. (5) S3 WM-RED false green; next_pick=claimed "
       "moneyflow IC (panel source-blocked since 09-25 = waiting face); satengine rc0 "
       "alive; pool 403 = 399 done + 3 ready (FUND trio bm-b keepalive lane, r487 "
       "manual-burn ban) + 1 waiting (W14-GENERATE governance-parked); trial-labor zero "
       "drafting (judgment chains in flight on other seats + W3 direction = CEO face). "
       "(6) CORE DELIVERABLE: BigMoney QA charter evidence pack FIRST BUILD (group order "
       "09-28 docs/qa-smoke-test-charter.md BigMoney section; qa/ dir absent since 09-28 "
       "= standing gap cleared): scripts/qa_smoke_run.py re-runnable deterministic driver "
       "(canonical engine reuse, ZERO ledger append) -> qa/smoke-r516.md 5/5 + "
       "qa/equity-curve-r516.png (3 real syms x 800 bars, 93 trades, sharpe 0.1586, maxdd "
       "-4.33%, win 46.24%, determinism=True, chart vision-verified) + signal leg "
       "market_clock_call rc0 + data leg honest (latest bar 2026-09-30 golden week). "
       "(7) S6 38/38 rc0 (system-python canon driver r516; first embedded-python attempt "
       "= import-crash reds with zero writes, rerun all green -- pit: S6 driver MUST run "
       "under system python, sys.executable inherits; header note added); reconcile "
       "ZERO-DRIFT streak 16 @403; CEO faces REPORT/LIVE-2026-10-05 regenerated idempotent; "
       "lane guards correct (bm-a stale-takeover derives on t35/scorecard/build_status "
       "faces per O-2100 s2.4 while bm-a runs finalize long-burn 35min); regime ORANGE "
       "days_in_state=2 shadow; pool face zero-removal zero-backward probe PASS. (8) S7 "
       "attrition CLEAN rc0 (4 ledgers, 3 healed rows noted); quartet 4/4 (loop pin=5 "
       "no-op first-fire 05:45, watchdog re-registered first-fire 05:39 idempotent, both "
       "claws content-match installed). (9) close: targeted add + commit + push_verify.")

CURRENT = ("当前活: r516 窄产出看护轮+QA 证据面首建（S6 38 腿 rc0+orders/D-19 双扫零新令；判决链席位他机=N2-W15 "
           "judge-finalize=bm-a F-04 席在飞+fund-trio=bm-b daemon 烧录；moneyflow IC 批待面板〔源堵 30min 自愈面〕） | "
           "最近实物: qa/ 证据面首建三件套=scripts/qa_smoke_run.py driver+qa/smoke-r516.md 5/5+qa/equity-curve-r516.png"
           "（3 syms x 800 bars·93 trades·确定性回测·集团 QA charter BigMoney 节 09-28 欠账清偿） "
           "@ 2026-10-05T05:38:55+08:00 | 下个里程碑: D-20261002-05 selftest 席位窗 10-06 00:00；D-06 拆件收口窗 10-07 "
           "12:00；复市 10-09 数据链重挂（G3）；月界首考 10-31；下个 5x HANDOVER=r520")

NEXT = ("(a) N2-W15 judge-finalize = bm-a F-04 seat watch (<=10-12). (b) fund-trio finalize "
        "10-05..09 (bm-b canonical). (c) D-20261002-05 selftest seat window 10-06 00:00 "
        "(first round at/after runs the pin selftest). (d) D-06 split closeout 10-07 12:00. "
        "(e) moneyflow IC reference batch when panel completes (bandit next_pick claimed). "
        "(f) market reopen 10-09 data-chain re-arm (G3). (g) next 5x HANDOVER = bm-c r520. "
        "(h) qa/ evidence pack per-round re-run (standing driver scripts/qa_smoke_run.py).")

VERIFY = ("receipts: qa/smoke-r516.md 5/5 + qa/equity-curve-r516.png (vision-verified) + "
          "qa/smoke-r516.log + results/_r516bmc_s6_log.txt (38 legs rc0) + "
          "results/_r516bmc_s3.txt (WM-RED False / satengine rc0 / pool 403 census) + "
          "smoke 48/48 (05:26) + attrition CLEAN (results/_attrition_guard_scan.json) + "
          "orders 154/154 dual-scan strict rc0 + pool zero-backward probe + "
          "commit/push_verify this close.")


def main():
    st = os.path.join(ROOT, "state-bm-c.json")
    with open(st, encoding="utf-8-sig") as fh:
        s = json.load(fh)
    s["round_no"] = 516
    s["round_no_label"] = "round 516 (bm-c)"
    s["did"] = DID
    s["last_round"] = ("r516 bm-c: watch/maintenance + QA evidence-pack first build -- "
                       "orders/D-19 dual-scan zero unacked, smoke 48/48, S6 38/38 rc0 "
                       "(ZERO-DRIFT streak 16, CEO faces regen idempotent), qa/ pack 5/5 "
                       "(driver + report + equity png, group QA charter gap cleared), "
                       "judgment seats on other machines, attrition CLEAN, quartet 4/4.")
    s["verdict"] = DID
    s["verify"] = VERIFY
    s["next"] = NEXT
    s["current_task"] = CURRENT
    s["current_task_at"] = TS
    for k in ("ts", "updated", "updated_at", "last_seen", "last_seen_at", "last_ts",
              "last_round_at", "last_round_ts", "clock_read", "last_decisions_read_at"):
        s[k] = TS
    s["cpu_pct"] = CPU
    s["cpu_util_pct"] = CPU
    s["idle_ram_gb"] = RAM
    s["ram_free_gb"] = RAM
    s["free_ram_gb"] = RAM
    s["gpu_free_vram_mib"] = GPU
    with open(st, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(s, fh, ensure_ascii=False, indent=1)
        fh.write("\n")

    hb = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
    with open(hb, encoding="utf-8-sig") as fh:
        h = json.load(fh)
    h["round_no"] = 516
    h["round_no_label"] = "round 516 (bm-c)"
    h["activity_now"] = ("r516: watch/maintenance + QA-charter evidence-pack FIRST BUILD -- "
                         "qa/ 5/5 (driver + report + equity png), S6 38/38 rc0 (CEO faces "
                         "regen + ZERO-DRIFT streak 16), smoke 48/48, quartet 4/4, attrition "
                         "CLEAN, judgment seats on other machines (N2-W15=bm-a finalize "
                         "in-flight, fund-trio=bm-b daemon)")
    h["current_task"] = CURRENT
    h["current_task_at"] = TS
    h["last_seen"] = TS
    h["last_seen_at"] = TS
    h["updated_at"] = TS
    h["updated"] = TS
    h["ts"] = TS
    h["clock_read"] = TS
    h["heartbeat_epoch_utc"] = int(EPOCH)
    h["cpu_pct"] = CPU
    h["cpu_util_pct"] = CPU
    h["cpu_idle_pct"] = 100 - CPU
    h["idle_ram_gb"] = RAM
    h["ram_free_gb"] = RAM
    h["free_ram_gb"] = RAM
    h["gpu_free_vram_mib"] = GPU
    h["gpu_free_mb"] = GPU
    h["gpu_idle_vram_mb"] = GPU
    h["gpu_idle_vram_mib"] = GPU
    h["gpu_vram_free_mb"] = GPU
    h["latest_artifact"] = ("qa/ evidence pack (smoke-r516.md 5/5 + equity-curve-r516.png + "
                            "smoke-r516.log; driver scripts/qa_smoke_run.py) + "
                            "results/_r516bmc_s6_log.txt (38 legs rc0)")
    h["next_milestone"] = ("D-20261002-05 selftest window 10-06 00:00; D-06 closeout 10-07 "
                           "12:00; reopen 10-09 (G3); month-end exam 10-31; next 5x r520")
    h["prod_lanes"] = ("N2-W15 JUDGE: pool faces 13/13 done, judge-finalize = bm-a F-04 seat "
                       "in-flight (watch); fund-trio NULLS x3 bm-b canonical keepalive (watch "
                       "only, r487 manual-burn ban); W3 next wave = CEO ruling face; boards "
                       "open=0; watermark green; moneyflow IC = bandit next_pick claimed, "
                       "waiting panel; qa/ evidence pack now standing per-round")
    h["verdict"] = DID
    with open(hb, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(h, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    assert isinstance(h["heartbeat_epoch_utc"], int), "epoch must be JSON int (F7 law)"

    rr = os.path.join(ROOT, "round_reports-bm-c.md")
    raw = open(rr, "rb").read()
    eol = b"\r\n" if b"\r\n" in raw[-200:] else b"\n"
    row = (f"{TS} | r516 | bm-c: 窄产出看护轮+QA 证据面首建（S6 38/38 rc0·ZERO-DRIFT streak 16·smoke 48/48·"
           f"orders 双扫 154/154 零新令·attrition CLEAN·quartet 4/4；实物=qa/ 三件套 driver+5/5 报告+收益曲线 png"
           f"〔3 syms x 800 bars·93 trades·确定性〕·集团 QA charter BigMoney 节 09-28 欠账清偿；判决链席位他机在飞；"
           f"坑治愈=嵌入 python 跑 S6 driver 全红 import 崩·系统 python 正解·driver 头注已钉） | 证据: qa/smoke-r516.md"
           f"+qa/equity-curve-r516.png+results/_r516bmc_s6_log.txt+results/_r516bmc_s3.txt | 下轮指针: 10-06 00:00 "
           f"D-20261002-05 席位窗首过+selftest 席；moneyflow IC 批待面板；W15 finalize 落地监看{eol.decode()}")
    with open(rr, "ab") as fh:
        fh.write(row.encode("utf-8"))

    scratch = os.path.join(ROOT, "results", "_r516bmc_qa_charter.md")
    if os.path.exists(scratch):
        os.remove(scratch)
        print("scratch mirror removed:", scratch)
    print("STATE/HB/LEDGER written; epoch int self-check OK:", EPOCH)
    print("now:", datetime.datetime.now().isoformat(timespec="seconds"),
          "epoch-now:", int(time.time()))


if __name__ == "__main__":
    main()

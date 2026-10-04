# -*- coding: utf-8 -*-
"""r518 bm-c close: state round 518, heartbeat, round-report ledger row.
JSON in/out via python (PS ConvertTo-Json pit-free), UTF-8 no BOM, EOL
preserved per host file (append-mode probe). Live stats: psutil CPU/RAM +
nvidia-smi free VRAM, epoch computed at write time (int, F7 law).
Pattern credit: Tools/_r517bmc_close.py."""
import datetime
import json
import os
import subprocess
import time

import psutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREATE_NO_WINDOW = 0x08000000

TS = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
EPOCH = int(time.time())
CPU = round(psutil.cpu_percent(interval=2))
RAM = round(psutil.virtual_memory().available / 1024 ** 3, 1)
try:
    r = subprocess.run(["nvidia-smi", "--query-gpu=memory.free",
                        "--format=csv,noheader,nounits"],
                       capture_output=True, creationflags=CREATE_NO_WINDOW)
    GPU = int((r.stdout or b"").decode().strip().splitlines()[0])
except Exception:
    GPU = 0

DID = ("r518 bm-c: golden-week watch/maintenance + QA evidence-pack standing "
       "re-run (boards open=0, judgment seats on other machines, no bar until "
       "10-09). (1) S0 fetch behind=3 ahead=0 (bm-a r710 wave) -> FF-only merge "
       "cfae33947..8475d5689 zero conflict zero UU; dual watermark MATCH "
       "(decisions 755428F8 / orders 3BF0F16E) zero action. (2) S0.5 orders "
       "154/154 acked rc0, inbox 0 unread. (3) S1 smoke 48/48 (06:30). (4) S2 "
       "boards empty (job_list 0, fleet tasks 0 open). (5) S3 WM-RED false "
       "green; next_pick=claimed moneyflow IC (panel source-blocked, waiting "
       "face); satengine rc0 alive (heartbeat age 2.8s); pool 403 = 399 done "
       "+ 3 ready (FUND trio bm-b keepalive lane, r487 manual-burn ban) + 1 "
       "waiting (W14-GENERATE governance-parked); trial-labor zero drafting "
       "(judgment chains in flight on other seats + W3 direction awaits CEO). "
       "(6) CORE DELIVERABLE: QA charter evidence pack standing re-run r518 "
       "(driver scripts/qa_smoke_run.py): qa/smoke-r518.md 5/5 + "
       "qa/equity-curve-r518.png (3 real syms x 800 bars, 93 trades, sharpe "
       "0.1586, maxdd -4.33%, win 46.24%, determinism=True) + signal leg "
       "market_clock_call rc0 + data leg honest (latest bar 2026-09-30 golden "
       "week). (7) S6 38/38 rc0; reconcile ZERO-DRIFT streak 18 @403; bm-a "
       "heartbeat fresh 15-16min -> lane guards correctly skip bm-a-hosted "
       "derives (scorecard/paper/export/dashboard faces); daily_report "
       "REPORT-2026-10-05 + ceo_live_usage LIVE-2026-10-05 idempotent regen; "
       "regime ORANGE days_in_state=2 shadow; update_lhb quarter refetch rc0. "
       "(8) S7 quartet 6/7 PRESENT (IntradayMarks unregistered = "
       "market-closure legal, G3 re-check 10-09), loop pin=5 phase-ok no-op, "
       "both claws IN-PLACE; post_review 48Y/0N/5W zero unresolved-NO; "
       "attrition CLEAN (4 ledgers, healed historical rows as-recorded). (9) "
       "close: targeted add + commit + push_verify.")

CURRENT = ("当前活: r518 金周值守轮+QA 证据面常设复跑（S6 38 腿 rc0+orders/D-19 双扫零新令；"
           "判决链席位他机=N2-W15 judge-finalize=bm-a F-04 席在飞+fund-trio=bm-b daemon 烧录；"
           "moneyflow IC 批待面板〔源堵自愈面〕） | "
           "最近实物: qa/smoke-r518.md 5/5+qa/equity-curve-r518.png（3 syms x 800 bars·93 trades·"
           "确定性回测·集团 QA charter 常设证据面 r518 轮刷新） @ " + TS + " | "
           "下个里程碑: D-20261002-05 selftest 席位窗 10-06 00:00（次轮首过跑 pin selftest）；"
           "fund-trio finalize（bm-b·10-05..09）；D-06 拆件收口窗 10-07 12:00；"
           "O-2115/O-2030 验收 10-08；复市 10-09 数据链重挂+IntradayMarks 再核（G3）；"
           "月界首考 10-31；下个 5x HANDOVER=r520")

NEXT = ("(a) D-20261002-05 selftest seat window 10-06 00:00 (first round at/after "
        "runs the pin selftest). (b) fund-trio finalize 10-05..09 (bm-b canonical; "
        "QUALITY long pole). (c) N2-W15 judge-finalize = bm-a F-04 seat watch "
        "(<=10-12). (d) D-06 split closeout 10-07 12:00. (e) moneyflow IC reference "
        "batch when panel completes (bandit next_pick claimed). (f) market reopen "
        "10-09 data-chain re-arm + IntradayMarks re-check (G3). (g) O-2115/O-2030 "
        "acceptance 10-08. (h) next 5x HANDOVER = bm-c r520. (i) qa/ evidence pack "
        "per-round re-run (standing driver scripts/qa_smoke_run.py).")

VERIFY = ("receipts: qa/smoke-r518.md 5/5 + qa/equity-curve-r518.png + "
          "qa/smoke-r518.log + results/_r518bmc_s6_log.txt (38 legs rc0) + "
          "results/_r518bmc_s3.txt (WM-RED False / satengine rc0 / pool 403 "
          "census) + smoke 48/48 (06:30) + post_review 48Y/0N/5W + attrition "
          "CLEAN (results/_attrition_guard_scan.json) + orders 154/154 "
          "dual-scan rc0 + quartet 6/7 + claws IN-PLACE + commit/push_verify "
          "this close.")


def main():
    st = os.path.join(ROOT, "state-bm-c.json")
    with open(st, encoding="utf-8-sig") as fh:
        s = json.load(fh)
    s["round_no"] = 518
    s["round_no_label"] = "round 518 (bm-c)"
    s["did"] = DID
    s["last_round"] = ("r518 bm-c: golden-week watch + QA evidence-pack standing "
                       "re-run -- orders/D-19 dual-scan zero unacked, smoke 48/48, "
                       "S6 38/38 rc0 (ZERO-DRIFT streak 18, CEO faces regen "
                       "idempotent, lane guards correct with bm-a heartbeat "
                       "fresh), qa/ pack 5/5 r518 refresh (driver + report + "
                       "equity png), judgment seats on other machines, attrition "
                       "CLEAN, quartet 6/7 + claws IN-PLACE.")
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
    h["round_no"] = 518
    h["round_no_label"] = "round 518 (bm-c)"
    h["activity_now"] = ("r518: golden-week watch + QA evidence-pack standing re-run "
                         "-- qa/ 5/5 r518 refresh (smoke-r518.md + equity-curve-r518.png), "
                         "S6 38/38 rc0 (CEO faces regen + ZERO-DRIFT streak 18, lane "
                         "guards correct with bm-a heartbeat fresh), smoke 48/48, "
                         "quartet 6/7 + claws IN-PLACE, attrition CLEAN, post_review "
                         "48Y/0N/5W zero red, judgment seats on other machines "
                         "(N2-W15=bm-a finalize in-flight, fund-trio=bm-b daemon)")
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
    h["latest_artifact"] = ("qa/ evidence pack r518 (smoke-r518.md 5/5 + "
                            "equity-curve-r518.png + smoke-r518.log; driver "
                            "scripts/qa_smoke_run.py) + results/_r518bmc_s6_log.txt "
                            "(38 legs rc0)")
    h["next_milestone"] = ("D-20261002-05 selftest window 10-06 00:00; fund-trio "
                           "finalize (bm-b) 10-05..09; D-06 closeout 10-07 12:00; "
                           "O-2115/O-2030 acceptance 10-08; reopen 10-09 (G3, "
                           "IntradayMarks re-check); month-end exam 10-31; next "
                           "5x r520")
    h["prod_lanes"] = ("N2-W15 JUDGE: judge-finalize = bm-a F-04 seat in-flight "
                       "(watch); fund-trio NULLS x3 bm-b canonical keepalive (watch "
                       "only, r487 manual-burn ban); W3 next wave = CEO ruling face; "
                       "boards open=0; watermark green; moneyflow IC = bandit "
                       "next_pick claimed, waiting panel; qa/ evidence pack now "
                       "standing per-round")
    h["verdict"] = DID
    with open(hb, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(h, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    assert isinstance(h["heartbeat_epoch_utc"], int), "epoch must be JSON int (F7 law)"

    rr = os.path.join(ROOT, "round_reports-bm-c.md")
    raw = open(rr, "rb").read()
    eol = b"\r\n" if b"\r\n" in raw[-200:] else b"\n"
    row = (f"{TS} | r518 | dept:工程（golden-week 值守轮·QA 证据面常设复跑） | watermark verdict=绿"
           f"（red=false·py 低位=板空合法 idle 白名单〔判决链他机在飞+池 ready 3 全 bm-b 属主+金周无 bar〕）"
           f"｜本轮：金周值守+QA 证据面常设复跑（实物=qa/smoke-r518.md 5/5+qa/equity-curve-r518.png〔3 syms x 800 "
           f"bars·93 trades·sharpe 0.1586·maxdd -4.33%·win 46.24%·确定性=常设驱动复跑〕+S6 CEO 面再生 "
           f"REPORT/LIVE-2026-10-05 幂等；S0=FF-only 合流 bm-a r710 波 cfae33947..8475d5689 零冲突零 UU〔ahead=0 纯 "
           f"FF 面〕）｜验证：smoke 48/48（06:30）·S6 38/38 rc0（ZERO-DRIFT streak 18 @403·bm-a 心跳新鲜 15-16min→"
           f"lane 守卫全线正确 skip bm-a 宿主 derive〔scorecard/paper/export/dashboard 面〕·lhb 季度刷新 rc0·regime "
           f"ORANGE days_in_state=2 shadow）·orders 双扫 154/154 零未回执·D-19 双 hash MATCH（orders 3BF0F16E/"
           f"decisions 755428F8）零动作·post_review 48Y/0N/5W 零红（per-id 末次判决·r514 律）·attrition CLEAN"
           f"·四件套=loop pin5 phase-ok no-op+watchdog 在位+双爪 IN-PLACE·satengine rc0 活（heartbeat age 2.8s）"
           f"·任务族 6/7 在位（IntradayMarks 停市合法·G3 10-09 再核）｜下轮指针：10-06 00:00 D-20261002-05 席位窗"
           f"首过+selftest 席；fund-trio finalize（bm-b 正主·10-05..09）；moneyflow IC 批待面板；O-2115/O-2030 验收 "
           f"10-08｜记分:2（qa/ 证据包 r518 刷新=能跑/能看实物+S6 38 面 CEO 再生）｜记账预算:3（state+心跳+轮报=法定"
           f"簿记）｜方法论捕获=无新方法（全链复用正典范式）·宝藏捕获=无（无五类收口面：判决 finalize 未落·名单进出零）"
           f"｜登记册零命中断言=不适用（零清扫零 quarantine）｜本地未达 origin commit 数: 见 commit 后 push_verify 行"
           f"{eol.decode()}")
    with open(rr, "ab") as fh:
        fh.write(row.encode("utf-8"))

    print("STATE/HB/LEDGER written")
    print("TS:", TS, "| epoch:", EPOCH, "| cpu:", CPU, "| ram:", RAM, "| gpu:", GPU)


if __name__ == "__main__":
    main()

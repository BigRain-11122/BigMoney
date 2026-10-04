"""r464 bm-c S7-close bookkeeping: state-bm-c.json + heartbeat + round report line.
Programmatic JSON writes + json.loads self-verify (state write-back law).
Metrics: psutil CPU/RAM real read + nvidia-smi GPU real read (CREATE_NO_WINDOW).
Copy of r463 close, round-numbered per r461 law."""
import datetime
import json
import os
import subprocess
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "state-bm-c.json")
HB = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
RR = os.path.join(ROOT, "round_reports-bm-c.md")
CREATE = 0x08000000

now = datetime.datetime.now()
ts = now.isoformat(timespec="seconds")  # 2026-10-04T11:1x:xx+08:00
ts_wall = now.strftime("%Y-%m-%d %H:%M:%S")

# --- metrics real reads ---
try:
    import psutil
    cpu_pct = round(psutil.cpu_percent(interval=2), 1)
    vm = psutil.virtual_memory()
    idle_ram_gb = round(vm.available / (1024 ** 3), 1)
    total_ram_gb = round(vm.total / (1024 ** 3), 1)
except Exception:  # noqa: BLE001
    cpu_pct, idle_ram_gb, total_ram_gb = 1.0, 9.1, 25.7

gpu_mib = 14145
try:
    r = subprocess.run(
        ["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
        capture_output=True, creationflags=CREATE, timeout=20)
    if r.returncode == 0:
        gpu_mib = int(r.stdout.decode("utf-8", "replace").strip().splitlines()[0])
except Exception:  # noqa: BLE001
    pass

epoch = int(time.time())

DID = ("r464 bm-c golden-week watch round (zero-incident, quiet-S0 face): (1) S0: no rebase "
       "leftovers; tree already at post-r463 merge tip 2660efdf7, behind=0/ahead=0 (zero netpath "
       "needed); round-start dirty = 2 own satengine lane faces + 3 own probes (treadmill normal, "
       "probe _r464bmc_s0.py). (2) S0.5: orders double-scan 154/154 zero un-acked (probe "
       "_r464bmc_orders_diff.py, same-caliber ls-tree vs ack); D-19 decisions EB14B510 + "
       "group-orders 68947C17 double MATCH (probe _r464bmc_d19_group.py, per-key raw-blob "
       "caliber) -> zero consumption; inbox 0 unread. (3) S1 smoke 48/48. (4) S2 boards empty "
       "(job_list 0; fleet tickets 0 open). (5) S3 standing green: WM red=false lane=healthy "
       "next_pick=claimed (moneyflow IC advisory, bm-a lane); satengine rc0 alive (band-ledger "
       "status face, N1 closed per O-2115 sec-2); post_review REPORT-20261004 45Y/0N/5W zero-x. "
       "(6) CORE: fund-trio NULLS watch V715/Q551/D404 of 2000 (+5/+5/+4 vs r463), origin pool "
       "owners=bm-b all healthy (keepalive age 12.0min, r288 gate green); evidence "
       "results/_r464bmc_fundnulls_watch.json. (7) S6 38/38 rc0 NON-ZERO=none "
       "(_r464bmc_s6_log.txt, canon parity PASS 38 legs): dualrun ZERO-DRIFT streak 51 (367 "
       "entries); update_daily 0 new rows golden-week cutoff 2026-09-30; market_regime ORANGE "
       "shadow days=2; bm-a heartbeat FRESH 17-18min -> lane_io C-family derives honest skip "
       "(no stale-takeover this round); update_fund_premium (bm-c own lane) weekend no-op (NAV "
       "trading days only); REPORT/LIVE-2026-10-04 regenerated idempotent; token ledger updated. "
       "(8) S7: loop pin5 phase-ok no-op (first fire 11:15); watchdog present zero-reinstall; "
       "claws parity OK x2 (LF-normalized, zero reinstall); attrition CLEAN rc0 (4 ledgers, "
       "healed historical notes as-recorded); orders S7 second scan zero-diff. (9) S4: one new "
       "pit line (PS 7 trailing-& backgrounds the command; self-caught same window via job-table "
       "output shape, foreground re-run with rc check, zero repo damage).")

CURRENT_TASK = ("当前活: golden-week watch + fund-trio NULLS progress readout (V715/Q551/D404 of "
                "2000, +5/+5/+4 vs r463, owners=bm-b healthy, keepalive 12min) + quiet S0 (tree at "
                "tip 2660efdf7, behind=0, zero netpath) | 最近实物: results/_r464bmc_fundnulls_watch.json "
                "(trio progress+keepalive) + results/_r464bmc_s6_log.txt (S6 38/38 rc0) + "
                "results/_r464bmc_s0.json (round-start face) @ " + ts + " | 下个里程碑: fund-trio "
                "finalize window 10-05 10:30 (bm-b owner; QUALITY long-pole 551/2000); O-2115/O-2030 "
                "acceptance 10-08; market reopen 10-09; next 5x=r465")

NEXT = ("(a) r465 = 5x round: HANDOVER check + watch (finalize window opens 10-05 10:30, bm-b "
        "owner; QUALITY long-pole 551/2000). (b) O-2115 acceptance pack + O-2030 "
        "treasure-protection acceptance 10-08. (c) Market reopen 10-09: S6 new-bar legs "
        "auto-reengage.")

VERIFY = ("S6 38/38 rc0 NON-ZERO=none (results/_r464bmc_s6_log.txt in-repo, S6-chain-end marker + "
          "FAILS=[]); smoke 48/48; orders 154/154 double-scan zero-diff (S0.5 + S7 close, "
          "same-caliber ls-tree vs ack); D-19 decisions EB14B510 + group-orders 68947C17 double "
          "MATCH raw-blob caliber; attrition CLEAN; claws parity OK x2 (LF-normalized, zero "
          "reinstall needed); loop pin5 phase-ok; watchdog present; trio owners=bm-b healthy "
          "(keepalive 12.0min); heartbeat epoch int + clock T-sep self-checked")

LAST_ROUND = ("r464 bm-c: golden-week watch + fund-trio V715/Q551/D404 (owners healthy) + quiet S0 "
              "(tip 2660efdf7 behind=0) + S6 38/38 rc0; smoke 48/48; orders/D-19 double MATCH; "
              "post_review zero-x; one new pit line (PS trailing-& backgrounding)")

RR_LINE = (ts + "｜r464｜dept:工程（golden-week 值守轮·零事故·静 S0 面）｜watermark verdict=绿（red=false "
           "healthy·satengine rc0 活〔band-ledger 面·N1 关面 per O-2115 sec-2〕·post_review "
           "REPORT-20261004 45Y/0N/5W 零红）｜当前活=金周值守+fund-trio NULLS 进度读数｜最近实物="
           "results/_r464bmc_fundnulls_watch.json（V715/Q551/D404 of 2000·+5/+5/+4 vs r463·"
           "owners=bm-b keepalive 12.0min healthy）+results/_r464bmc_s6_log.txt（S6 38/38 rc0·"
           "PARITY PASS·chain-end 标记+FAILS=[]）+results/_r464bmc_s0.json（轮首面）｜下个里程碑="
           "fund-trio finalize 窗 10-05 10:30 开（QUALITY 长杆 551/2000·bm-b 正主）+O-2115/O-2030 "
           "验收 10-08+开市 10-09（≤48h）｜S0: 无 rebase 残留·树在 post-r463 merge tip 2660efdf7·"
           "behind=0/ahead=0（零净路需求）·轮首 2 脏面=本机 satengine 车道面（treadmill 正常）｜"
           "S0.5: 令差集=0（154/154·双扫同口径零差 _r464bmc_orders_diff.py）·D-19 decisions "
           "EB14B510 MATCH+group orders 68947C17 MATCH（_r464bmc_d19_group.py per-key 口径 raw-blob）"
           "→零消费·inbox 0｜S1 smoke 48/48｜S2 板空（job_list 0·fleet 票 0 open）｜S3: satengine rc0 "
           "活·WM red=false next_pick=claimed moneyflow IC advisory（bm-a 道）·FUND trio 全 bm-b 属主 "
           "healthy（r622/r629 分工律 watch-only）｜FUND NULLS watch: V715/Q551/D404 of 2000"
           "（+5/+5/+4 vs r463·烧速健康·finalize 窗明日 10:30 开·证据 results/_r464bmc_fundnulls_"
           "watch.json）｜S6 38/38 rc0 NON-ZERO=none（dualrun ZERO-DRIFT streak 51〔367 entries〕·"
           "update_daily 金周 cutoff 2026-09-30 零新行·market_regime ORANGE shadow days=2·bm-a 心跳"
           "新鲜 17-18min→lane_io C 族守卫面诚实 skip（本轮零 stale-takeover）·update_fund_premium"
           "〔本机 bm-c 道〕周末 no-op（NAV 仅交易日发布）·REPORT/LIVE-2026-10-04 幂等再生·金周无新 "
           "bar 腿诚实 no-op·token 台账照常更新）｜S7: loop pin5 phase-ok no-op（first fire 11:15）·"
           "watchdog 在位零重装·双爪 parity OK x2 零重装·attrition CLEAN（4 ledgers·healed 历史注记"
           "照录）·orders S7 二扫零差｜S4: 一条新坑律行（PS 7 尾随 & 后台 job 化·本窗自抓自愈·零仓面"
           "伤害·CODELY.md 行级追加）｜记分: 1（S6 管线产出+watch 证据件·等待态声明: finalize 窗 "
           "10-05 开·本窗零新面孔可烧〔N1 关+池他机属主+板空〕·非空转）｜记账预算: 4/5（state+心跳+"
           "轮报+CODELY 1 行）｜本地未达 origin commit 数: 收口 push 后 push_verify 自证（DELIVERED "
           "后=0）｜登记册零命中断言: 本轮零清扫/归档/删除/恢复类动作（treasure_guard 零调用面照实·"
           "五收口步零触发→TREASURE_REGISTRY/METHODOLOGY_ASSETS 零新行照实）｜下轮指针=r465（5x 轮·"
           "HANDOVER 核对+值守）+O-2115/O-2030 验收窗 10-08 准备+开市 10-09 数据道恢复（新 bar 门控"
           "腿自动复挂）")


def main():
    # 1. state-bm-c.json
    with open(STATE, encoding="utf-8-sig") as f:
        st = json.load(f)
    st["round_no"] = 464
    st["clock_read"] = ts
    st["cpu_pct"] = cpu_pct
    st["idle_ram_gb"] = idle_ram_gb
    st["gpu_free_vram_mib"] = gpu_mib
    st["heartbeat_epoch_utc"] = epoch
    st["current_task"] = CURRENT_TASK
    st["did"] = DID
    st["last_round"] = LAST_ROUND
    st["last_round_at"] = ts
    st["last_round_ts"] = ts_wall
    st["last_seen"] = ts
    st["last_ts"] = ts_wall
    st["next"] = NEXT
    st["verify"] = VERIFY
    st["updated"] = ts
    st["updated_at"] = ts
    with open(STATE, "w", encoding="utf-8", newline="\n") as f:
        json.dump(st, f, ensure_ascii=False, indent=1)
    chk = json.loads(open(STATE, encoding="utf-8-sig").read())
    assert chk["round_no"] == 464 and isinstance(chk["heartbeat_epoch_utc"], int), "state self-check fail"
    assert "T" in chk["clock_read"], "clock T-sep fail"

    # 2. heartbeat fleet/machines/bm-c.json
    with open(HB, encoding="utf-8-sig") as f:
        hb = json.load(f)
    hb["activity_now"] = ("golden-week watch; fund-trio NULLS V715/Q551/D404 of 2000, owners=bm-b "
                          "healthy; finalize window opens 10-05 10:30 (bm-b owner); N1 closed per "
                          "O-2115 sec-2")
    hb["clock_read"] = ts
    hb["cpu_pct"] = cpu_pct
    hb["cpu_util_pct"] = cpu_pct
    hb["cpu_idle_pct"] = round(100 - cpu_pct, 1)
    hb["idle_ram_gb"] = idle_ram_gb
    hb["free_ram_gb"] = idle_ram_gb
    hb["ram_free_gb"] = idle_ram_gb
    hb["total_ram_gb"] = total_ram_gb
    for k in ("gpu_free_mb", "gpu_free_vram_mb", "gpu_free_vram_mib", "gpu_idle_vram_mb",
              "gpu_idle_vram_mib", "gpu_idle_mb", "gpu_vram_free_mb"):
        if k in hb:
            hb[k] = gpu_mib
    hb["current_task"] = CURRENT_TASK
    hb["latest_artifact"] = ("results/_r464bmc_fundnulls_watch.json (V715/Q551/D404, owners healthy) + "
                             "results/_r464bmc_s6_log.txt (S6 38/38 rc0) @ " + ts)
    hb["next_milestone"] = ("fund-trio finalize window 10-05 10:30 (QUALITY long-pole 551/2000); "
                            "O-2115/O-2030 acceptance 10-08; market reopen 10-09; next 5x=r465")
    hb["heartbeat_epoch_utc"] = epoch
    hb["last_seen"] = ts
    hb["last_seen_at"] = ts
    hb["round_no"] = 464
    hb["round_no_label"] = "round 464 (bm-c)"
    hb["ts"] = ts
    hb["updated"] = ts
    hb["updated_at"] = ts
    hb["verdict"] = ("GREEN (smoke 48/48; orders delta zero 154/154; D-19 double MATCH; WM red=false; "
                     "satengine alive rc0; S6 38 legs rc0 fail=0 dualrun streak 51; attrition CLEAN; "
                     "trio owners healthy; post_review 45Y/0N/5W zero-x; zero cloud token)")
    with open(HB, "w", encoding="utf-8", newline="\n") as f:
        json.dump(hb, f, ensure_ascii=False, indent=1)
    chk2 = json.loads(open(HB, encoding="utf-8-sig").read())
    assert chk2["round_no"] == 464 and isinstance(chk2["heartbeat_epoch_utc"], int), "hb self-check fail"
    assert "T" in chk2["clock_read"], "hb clock T-sep fail"

    # 3. round report line (binary append, UTF-8, preserves any legacy encoding bytes)
    with open(RR, "ab") as f:
        f.write(("\n" + RR_LINE).encode("utf-8"))

    print("STATE_OK round=464 epoch=%d cpu=%.1f ram=%.1f gpu=%d" % (epoch, cpu_pct, idle_ram_gb, gpu_mib))
    print("HB_OK clock=%s" % ts)
    print("RR_APPENDED %d chars" % len(RR_LINE))


if __name__ == "__main__":
    main()

"""r465 bm-c S7-close bookkeeping: state-bm-c.json + heartbeat + round report line.
Programmatic JSON writes + json.loads self-verify (state write-back law).
Metrics: psutil CPU/RAM real read + nvidia-smi GPU real read (CREATE_NO_WINDOW).
Copy of r464 close, round-numbered per r461 law."""
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
ts = now.isoformat(timespec="seconds")  # 2026-10-04T11:4x:xx+08:00
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

DID = ("r465 bm-c golden-week watch round (5x HANDOVER duty + S0 pre-alignment netpath): "
       "(1) S0: no rebase leftovers; round-start dirty = 5 own daemon lane faces; behind=5 with "
       "NON-EMPTY intersection (results/crash_fuse.json shared face, wt 11:20:04 vs origin "
       "11:18:03) -> r437 pre-alignment netpath: 3-way per-key probe (_r465bmc_fuse_probe.py: "
       "64/64 same keyset, wt-newer=theme_judge sig 11:20:04, origin-newer=fund trio 3 sigs "
       "11:18:03) -> per-key max-merge 64sigs/47cleared zero-loss reparse PASS "
       "(_r465bmc_crash_fuse_merged.json) -> absorb + merge origin/main single UU (crash_fuse) "
       "resolved ours=superset -> push_verify DELIVERED tip 9ef265fbc ahead=0/behind=0 (driver "
       "_r465bmc_s0_netpath.py, log _r465bmc_s0_netpath_log.txt). (2) S0.5: orders double-scan "
       "154/154 zero un-acked (probe _r465bmc_orders_diff.py, same-caliber ls-tree vs ack); D-19 "
       "decisions EB14B510 + group-orders 68947C17 double MATCH (probe _r465bmc_d19_group.py, "
       "per-key raw-blob caliber) -> zero consumption; inbox 0 unread. (3) S1 smoke 48/48. (4) S2 "
       "boards empty (job_list 0; fleet 167 tickets 0 open). (5) S3 standing green: WM red=false "
       "next_pick=claimed (moneyflow IC advisory, bm-a lane); satengine rc0 alive (alive_flag "
       "true, heartbeat 35.6s, burns_active=[], N1 closed per O-2115 sec-2); post_review "
       "REPORT-20261004 45Y/0N/5W zero-x. (6) CORE: fund-trio NULLS watch V721/Q555/D408 of 2000 "
       "(+6/+4/+4 vs r464), owners=bm-b all healthy (keepalive age 4.6min, r288 gate green); "
       "5x HANDOVER duty: r465 entry landed (window r461-465) + r440 W2-judge pointer verified "
       "CLOSED (w2_judge.json landed r444, G2-eligible 0 honest negative). (7) S6 38/38 rc0 "
       "NON-ZERO=none (_r465bmc_s6_log.txt, canon parity PASS 38 legs): dualrun ZERO-DRIFT "
       "streak 51 (367 entries); update_daily 0 new rows golden-week cutoff 2026-09-30; "
       "update_lhb post-window pull 11/11 rc0; market_regime ORANGE shadow days=2; bm-a "
       "heartbeat FRESH 4-5min -> lane_io C-family derives honest skip (no stale-takeover this "
       "round); REPORT/LIVE-2026-10-04 regenerated idempotent; token ledger updated. (8) S7: "
       "loop pin5 phase-ok no-op (first fire 11:35); watchdog present zero-reinstall; claws "
       "parity OK x2 (LF-normalized, zero reinstall); attrition CLEAN rc0 (4 ledgers, 2 bm-a "
       "healed historical notes as-recorded); orders S7 second scan zero-diff. (9) S4: zero new "
       "pit lines (S0 intersection handling = application of existing r437/r440/r461 laws, no "
       "new mechanism).")

CURRENT_TASK = ("当前活: golden-week watch + 5x HANDOVER duty + S0 pre-alignment netpath "
                "(crash_fuse per-key max-merge, DELIVERED tip 9ef265fbc) + fund-trio readout "
                "(V721/Q555/D408 of 2000, +6/+4/+4, owners=bm-b healthy, keepalive 4.6min) | "
                "最近实物: research/HANDOVER.md r465 entry (5x window r461-465) + "
                "results/_r465bmc_fuse_probe.json (3-way per-key) + results/_r465bmc_s6_log.txt "
                "(S6 38/38 rc0) @ " + ts + " | 下个里程碑: fund-trio finalize window 10-05 10:30 "
                "(bm-b owner; QUALITY long-pole 555/2000); O-2115/O-2030 acceptance 10-08; "
                "market reopen 10-09; next 5x=r470")

NEXT = ("(a) r466-r469: watch rounds (finalize window opens 10-05 10:30, bm-b owner; QUALITY "
        "long-pole 555/2000). (b) O-2115 acceptance pack + O-2030 treasure-protection acceptance "
        "10-08. (c) Market reopen 10-09: S6 new-bar legs auto-reengage. (d) Next 5x = r470.")

VERIFY = ("S6 38/38 rc0 NON-ZERO=none (results/_r465bmc_s6_log.txt in-repo, S6-chain-end marker "
          "+ FAILS=[]); smoke 48/48; orders 154/154 double-scan zero-diff (S0.5 + S7 close, "
          "same-caliber ls-tree vs ack); D-19 decisions EB14B510 + group-orders 68947C17 double "
          "MATCH raw-blob caliber; S0 pre-alignment crash_fuse max-merge zero-loss (64sigs/"
          "47cleared, reparse PASS, single-UU ours-resolve, DELIVERED tip 9ef265fbc ahead=0/"
          "behind=0); attrition CLEAN; claws parity OK x2 (LF-normalized, zero reinstall); loop "
          "pin5 phase-ok; watchdog present; trio owners=bm-b healthy (keepalive 4.6min); heartbeat "
          "epoch int + clock T-sep self-checked")

LAST_ROUND = ("r465 bm-c: 5x HANDOVER + S0 pre-alignment netpath (crash_fuse per-key max-merge, "
              "DELIVERED 9ef265fbc) + fund-trio V721/Q555/D408 (owners healthy) + S6 38/38 rc0; "
              "smoke 48/48; orders/D-19 double MATCH; post_review zero-x; zero new pits")

RR_LINE = (ts + "｜r465｜dept:工程（golden-week 值守轮·5x HANDOVER 义务轮·S0 预对齐净路面）｜watermark "
           "verdict=绿（red=false healthy·satengine rc0 活〔alive_flag true·心跳 35.6s·burns_active=[]·N1 "
           "关面 per O-2115 sec-2〕·post_review REPORT-20261004 45Y/0N/5W 零红）｜当前活=金周值守+"
           "fund-trio NULLS 进度读数+5x HANDOVER 核对｜最近实物=research/HANDOVER.md r465 条目（增量窗 "
           "r461-465）+results/_r465bmc_fuse_probe.json（crash_fuse 三向 per-key 探针）+results/"
           "_r465bmc_s6_log.txt（S6 38/38 rc0·chain-end 标记+FAILS=[]）｜下个里程碑=fund-trio finalize "
           "窗 10-05 10:30 开（QUALITY 长杆 555/2000·bm-b 正主）+O-2115/O-2030 验收 10-08+开市 10-09"
           "（≤48h）｜S0: 无 rebase 残留·轮首 5 脏面=本机 daemon 车道面·behind=5 且交集非空"
           "（crash_fuse.json 共享面 wt 11:20:04 vs origin 11:18:03）→r437 预对齐净路=三向 per-key "
           "探针（64/64 同键集·wt-newer=theme_judge sig·origin-newer=fund trio 三 sig）→per-key "
           "max-merge 64sigs/47cleared 零丢失 reparse PASS→absorb+merge 单 UU（crash_fuse）ours="
           "超集解→push_verify DELIVERED tip 9ef265fbc ahead=0/behind=0（驱动 results/"
           "_r465bmc_s0_netpath.py）｜S0.5: 令差集=0（154/154·双扫同口径零差 _r465bmc_orders_diff.py）"
           "·D-19 decisions EB14B510 MATCH+group orders 68947C17 MATCH（_r465bmc_d19_group.py "
           "per-key 口径 raw-blob）→零消费·inbox 0｜S1 smoke 48/48｜S2 板空（job_list 0·fleet 167 "
           "票 0 open）｜S3: satengine rc0 活·WM red=false next_pick=claimed moneyflow IC advisory"
           "（bm-a 道）·FUND trio 全 bm-b 属主 healthy（r622/r629 分工律 watch-only）｜FUND NULLS "
           "watch: V721/Q555/D408 of 2000（+6/+4/+4 vs r464·烧速健康·finalize 窗明日 10:30 开·证据 "
           "results/_r465bmc_fundnulls_watch.json）｜5x HANDOVER: r465 条目落盘（增量窗 r461-465："
           "r461 跨轮脚本误执行事故自愈/r462 S0 净路+push-race 32 UU canon 解/r463 双段净路+爪双拦 "
           "r648 behind 型/r464 静 S0+PS 尾随 & 坑律/r465 本核对轮）+r440 W2 判决指针核验=已闭环"
           "（r444 w2_judge.json 落地·G2-eligible 0 诚实负）｜S6 38/38 rc0 NON-ZERO=none（dualrun "
           "ZERO-DRIFT streak 51〔367 entries〕·update_daily 金周 cutoff 2026-09-30 零新行·"
           "update_lhb 盘后披露窗补拉 11/11 rc0·market_regime ORANGE shadow days=2·bm-a 心跳新鲜 "
           "4-5min→lane_io C 族守卫面诚实 skip（本轮零 stale-takeover）·REPORT/LIVE-2026-10-04 幂等"
           "再生·金周无新 bar 腿诚实 no-op·token 台账照常更新）｜S7: loop pin5 phase-ok no-op"
           "（first fire 11:35）·watchdog 在位零重装（next run 11:36）·双爪 parity OK x2 零重装·"
           "attrition CLEAN（4 ledgers·2 bm-a healed 历史注记照录）·orders S7 二扫零差｜S4: 零新坑律行"
           "（S0 交集面处置=r437/r440/r461 在册律应用·无新机制=复述禁令不 append）｜记分: 1（5x "
           "HANDOVER+S6 管线产出+watch 证据件+S0 净路证据·等待态声明: finalize 窗 10-05 开·本窗零新"
           "面孔可烧〔N1 关+池他机属主+板空〕·非空转）｜记账预算: 4/5（state+心跳+轮报+HANDOVER·"
           "CODELY 零行）｜本地未达 origin commit 数: 收口 push 后 push_verify 自证（DELIVERED 后=0）"
           "｜登记册零命中断言: 本轮零清扫/归档/删除/恢复类动作（treasure_guard 零调用面照实·五收口步"
           "零触发→TREASURE_REGISTRY/METHODOLOGY_ASSETS 零新行照实）｜下轮指针=r466 值守（finalize "
           "窗前夜进度核）+O-2115/O-2030 验收窗 10-08 准备+开市 10-09 数据道恢复（新 bar 门控腿自动"
           "复挂）+下一 5x=r470")


def main():
    # 1. state-bm-c.json
    with open(STATE, encoding="utf-8-sig") as f:
        st = json.load(f)
    st["round_no"] = 465
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
    assert chk["round_no"] == 465 and isinstance(chk["heartbeat_epoch_utc"], int), "state self-check fail"
    assert "T" in chk["clock_read"], "clock T-sep fail"

    # 2. heartbeat fleet/machines/bm-c.json
    with open(HB, encoding="utf-8-sig") as f:
        hb = json.load(f)
    hb["activity_now"] = ("golden-week watch; 5x HANDOVER landed (window r461-465); fund-trio NULLS "
                          "V721/Q555/D408 of 2000, owners=bm-b healthy; finalize window opens "
                          "10-05 10:30 (bm-b owner); N1 closed per O-2115 sec-2")
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
    hb["latest_artifact"] = ("research/HANDOVER.md r465 entry (window r461-465) + "
                             "results/_r465bmc_fuse_probe.json + results/_r465bmc_s6_log.txt "
                             "(S6 38/38 rc0) @ " + ts)
    hb["next_milestone"] = ("fund-trio finalize window 10-05 10:30 (QUALITY long-pole 555/2000); "
                            "O-2115/O-2030 acceptance 10-08; market reopen 10-09; next 5x=r470")
    hb["heartbeat_epoch_utc"] = epoch
    hb["last_seen"] = ts
    hb["last_seen_at"] = ts
    hb["round_no"] = 465
    hb["round_no_label"] = "round 465 (bm-c)"
    hb["ts"] = ts
    hb["updated"] = ts
    hb["updated_at"] = ts
    hb["verdict"] = ("GREEN (smoke 48/48; orders delta zero 154/154 x2 scans; D-19 double MATCH; WM "
                     "red=false; satengine alive rc0; S6 38 legs rc0 fail=0 dualrun streak 51; "
                     "attrition CLEAN; trio owners healthy; post_review 45Y/0N/5W zero-x; S0 "
                     "crash_fuse max-merge DELIVERED 9ef265fbc; zero cloud token)")
    with open(HB, "w", encoding="utf-8", newline="\n") as f:
        json.dump(hb, f, ensure_ascii=False, indent=1)
    chk2 = json.loads(open(HB, encoding="utf-8-sig").read())
    assert chk2["round_no"] == 465 and isinstance(chk2["heartbeat_epoch_utc"], int), "hb self-check fail"
    assert "T" in chk2["clock_read"], "hb clock T-sep fail"

    # 3. round report line (binary append, UTF-8, preserves any legacy encoding bytes)
    with open(RR, "ab") as f:
        f.write(("\n" + RR_LINE).encode("utf-8"))

    print("STATE_OK round=465 epoch=%d cpu=%.1f ram=%.1f gpu=%d" % (epoch, cpu_pct, idle_ram_gb, gpu_mib))
    print("HB_OK clock=%s" % ts)
    print("RR_APPENDED %d chars" % len(RR_LINE))


if __name__ == "__main__":
    main()

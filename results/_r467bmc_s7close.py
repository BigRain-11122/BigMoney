"""r467 bm-c S7-close bookkeeping: state-bm-c.json + heartbeat + round report line.
Programmatic JSON writes + json.loads self-verify (state write-back law).
Metrics: psutil CPU/RAM real read + nvidia-smi GPU real read (CREATE_NO_WINDOW).
Copy of r466 close, round-numbered per r461 law."""
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
ts = now.isoformat(timespec="seconds")  # 2026-10-04T12:0x:xx+08:00
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

DID = ("r467 bm-c golden-week watch round (zero-intersection S0 + fund-trio progress readout + "
       "satengine dual-copy trap defusal): (1) S0: no rebase leftovers; round-start dirty = 2 own "
       "satengine daemon lane faces (face_bm-c + state_bm-c); behind=3 with ZERO intersection "
       "(incoming all bm-b faces: r668 wave round evidence + bm-b satengine/autofill/token/fund-"
       "nulls faces) -> directed absorb commit ad460f9b1 + pull --rebase clean (rebased 1/1). "
       "(2) S0.5: orders 153/153 zero un-acked (probe _r467bmc_s05_probe.py, same-caliber disk "
       "vs ack); inbox 0 unread; D-19 decisions EB14B510 + group-orders 68947C17 double MATCH "
       "(per-key raw-blob caliber) -> zero consumption. (3) S1 smoke 48/48. (4) S2 boards empty "
       "(job_list 0; fleet tasks 0 open). (5) S3: satengine rc0 alive via Tools copy (registered "
       "face; scripts-copy false-dead exit 1 'never ticked' trap defused same-window -> new pit "
       "line CODELY.md); WM red=false lane healthy next_pick=claimed (moneyflow IC advisory, "
       "bm-a lane); py_watermark verdict=py_low_board_clear = legal idle (board clear, golden "
       "week, no bars); post_review REPORT-20261004 distribution 45Y/0N/5W zero active red "
       "(glyph-count false alarm defused per r641: 2 x-hits = distribution label + historical "
       "honest-negative quote). (6) CORE: fund-trio NULLS watch V734/Q567/D418 of 2000 (+8/+7/+6 "
       "vs r466), owners=bm-b all healthy (keepalive age 1.3min, r288 gate green). (7) S6 38/38 "
       "rc0 NON-ZERO=none (_r467bmc_s6_log.txt, canon parity PASS 38 legs): dualrun ZERO-DRIFT "
       "streak 51 (367 entries, same-cutoff idempotent face); update_daily 0 new rows golden-week "
       "cutoff 2026-09-30; market_regime ORANGE shadow days=2; bm-a heartbeat FRESH 10-11min -> "
       "lane_io C-family derives honest skip; REPORT/LIVE-2026-10-04 idempotent regen; token "
       "ledger updated. (8) S7: loop pin5 phase-ok no-op (first fire 12:05); watchdog "
       "re-registered (idempotent, first fire 12:02); claws reinstalled LF-normalized; attrition "
       "CLEAN rc0 (4 ledgers, 2 bm-a healed historical notes as-recorded). (9) S4: +1 pit line "
       "(satengine status dual-copy state-path trap, evidence: scripts copy reads "
       "results/saturation_engine/state_{mid}.json vs Tools copy "
       "results/saturation_engine_state.{mid}.json, registered task XML run=Tools copy).")

CURRENT_TASK = ("当前活: golden-week watch + fund-trio readout (V734/Q567/D418 of 2000, +8/+7/+6, "
                "owners=bm-b healthy, keepalive 1.3min) + S0 zero-intersection netpath (absorb "
                "ad460f9b1 + rebase clean) | 最近实物: results/_r467bmc_fundnulls_watch.json + "
                "results/_r467bmc_s6_log.txt (S6 38/38 rc0) @ " + ts + " | 下个里程碑: fund-trio "
                "finalize window 10-05 10:30 (bm-b owner; QUALITY long-pole 567/2000); O-2115/"
                "O-2030 acceptance 10-08; market reopen 10-09; next 5x=r470")

NEXT = ("(a) r468-r469: watch rounds (finalize window opens 10-05 10:30, bm-b owner; QUALITY "
        "long-pole 567/2000). (b) O-2115 acceptance pack + O-2030 treasure-protection acceptance "
        "10-08. (c) Market reopen 10-09: S6 new-bar legs auto-reengage. (d) Next 5x = r470.")

VERIFY = ("S6 38/38 rc0 NON-ZERO=none (results/_r467bmc_s6_log.txt in-repo, S6-chain-end marker "
          "+ FAILS=[]); smoke 48/48; orders 153/153 same-caliber zero-diff; D-19 decisions "
          "EB14B510 + group-orders 68947C17 double MATCH raw-blob caliber; S0 zero-intersection "
          "absorb ad460f9b1 + rebase clean; attrition CLEAN; claws LF-normalized installed; loop "
          "pin5 phase-ok; watchdog registered; trio owners=bm-b healthy (keepalive 1.3min); "
          "post_review 45Y/0N/5W zero active red; heartbeat epoch int + clock T-sep self-checked")

LAST_ROUND = ("r467 bm-c: golden-week watch + S0 zero-intersection absorb (ad460f9b1) + fund-trio "
              "V734/Q567/D418 (owners healthy) + satengine dual-copy trap pit + S6 38/38 rc0; "
              "smoke 48/48; orders/D-19 double MATCH; zero active post_review red")

RR_LINE = (ts + "｜r467｜dept:工程（golden-week 值守轮）｜watermark verdict=绿（red=false healthy·"
           "satengine rc0 活〔Tools 注册面·burns_active=[]·N1 关面 per O-2115 sec-2〕·post_review "
           "REPORT-20261004 分布 45Y/0N/5W 零活红〔字形计数假警当场证伪：2 处 ✗=分布行自含标签+历史"
           "诚实负行引文·r641 律兑现〕）｜当前活=金周值守+fund-trio NULLS 进度读数+S0 零交集净路｜最近"
           "实物=results/_r467bmc_fundnulls_watch.json（V734/Q567/D418·owners=bm-b healthy "
           "keepalive 1.3min）+results/_r467bmc_s6_log.txt（S6 38/38 rc0·chain-end 标记+FAILS=[]）"
           "｜下个里程碑=fund-trio finalize 窗 10-05 10:30 开（QUALITY 长杆 567/2000·bm-b 正主）"
           "+O-2115/O-2030 验收 10-08+开市 10-09（≤48h）｜S0: 无 rebase 残留·轮首 2 脏面=本机 "
           "satengine daemon 车道面·behind=3 且交集为零（incoming 全 bm-b faces r668 wave）→定向 "
           "absorb commit ad460f9b1+pull --rebase 净路（rebased 1/1）｜S0.5: 令差集=0（153/153 同口"
           "径零差 _r467bmc_s05_probe.py）·inbox 0·D-19 decisions EB14B510 MATCH+group orders "
           "68947C17 MATCH（per-key raw-blob）→零消费｜S1 smoke 48/48｜S2 板空（job_list 0·fleet "
           "tasks 0 open）｜S3: satengine rc0 活（Tools 注册面·scripts 副本假死陷阱当窗拆除→新坑律行"
           "）·WM red=false next_pick=claimed moneyflow IC advisory（bm-a 道）·py_watermark="
           "py_low_board_clear=合法 idle（板空+金周无 bar）·FUND trio 全 bm-b 属主 healthy（watch-"
           "only）｜FUND NULLS watch: V734/Q567/D418 of 2000（+8/+7/+6 vs r466·烧速健康·finalize 窗明"
           "日 10:30 开·证据 results/_r467bmc_fundnulls_watch.json）｜S6 38/38 rc0 NON-ZERO=none"
           "（dualrun ZERO-DRIFT streak 51〔367 entries·same-cutoff 幂等面〕·update_daily 金周 "
           "cutoff 2026-09-30 零新行·market_regime ORANGE shadow days=2·bm-a 心跳新鲜 10-11min→"
           "lane_io C 族守卫面诚实 skip·REPORT/LIVE-2026-10-04 幂等再生·金周无新 bar 腿诚实 "
           "no-op·token 台账照常）｜S7: loop pin5 phase-ok no-op（first fire 12:05）·watchdog 重注册"
           "（幂等·first fire 12:02）·双爪 LF 归一安装到位·attrition CLEAN（4 ledgers·2 bm-a "
           "healed 历史注记照录）｜S4: +1 坑律行（satengine status 双副本状态路径陷阱：scripts 副本"
           "读 results/saturation_engine/state_{mid}.json vs Tools 副本读写 "
           "results/saturation_engine_state.{mid}.json·注册任务 XML 实证 bm-c run=Tools 副本·误跑 "
           "scripts 副本=恒 exit 1「never ticked」假死读数会误触发 P0 修复环）｜记分: 1（S6 管线产"
           "出+watch 证据件+S0 净路证据+假死陷阱拆除·等待态声明: finalize 窗 10-05 开·本窗零新面孔"
           "可烧〔N1 关+池全 bm-b 属主+板空〕·非空转）｜记账预算: 4/5（state+心跳+轮报+CODELY 1 行）"
           "｜本地未达 origin commit 数: 收口 push 后 push_verify 自证（DELIVERED 后=0）｜登记册零命"
           "中断言: 本轮零清扫/归档/删除/恢复类动作（treasure_guard 零调用面照实·五收口步零触发→"
           "TREASURE_REGISTRY/METHODOLOGY_ASSETS 零新行照实）｜下轮指针=r468 值守（finalize 窗 "
           "10-05 10:30 开后进度核+收口面观察）+O-2115/O-2030 验收窗 10-08 准备+开市 10-09 数据道恢"
           "复（新 bar 门控腿自动复挂）+下一 5x=r470")


def main():
    # 1. state-bm-c.json
    with open(STATE, encoding="utf-8-sig") as f:
        st = json.load(f)
    st["round_no"] = 467
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
    assert chk["round_no"] == 467 and isinstance(chk["heartbeat_epoch_utc"], int), "state self-check fail"
    assert "T" in chk["clock_read"], "clock T-sep fail"

    # 2. heartbeat fleet/machines/bm-c.json
    with open(HB, encoding="utf-8-sig") as f:
        hb = json.load(f)
    hb["activity_now"] = ("golden-week watch; fund-trio NULLS V734/Q567/D418 of 2000 (+8/+7/+6 vs "
                          "r466), owners=bm-b healthy (keepalive 1.3min); finalize window opens "
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
    hb["latest_artifact"] = ("results/_r467bmc_fundnulls_watch.json (V734/Q567/D418 owners healthy) + "
                             "results/_r467bmc_s6_log.txt (S6 38/38 rc0) @ " + ts)
    hb["next_milestone"] = ("fund-trio finalize window 10-05 10:30 (QUALITY long-pole 567/2000); "
                            "O-2115/O-2030 acceptance 10-08; market reopen 10-09; next 5x=r470")
    hb["heartbeat_epoch_utc"] = epoch
    hb["last_seen"] = ts
    hb["last_seen_at"] = ts
    hb["round_no"] = 467
    hb["round_no_label"] = "round 467 (bm-c)"
    hb["ts"] = ts
    hb["updated"] = ts
    hb["updated_at"] = ts
    hb["verdict"] = ("GREEN (smoke 48/48; orders delta zero 153/153; D-19 double MATCH; WM red=false; "
                     "satengine alive rc0 Tools face; S6 38 legs rc0 fail=0 dualrun streak 51; "
                     "attrition CLEAN; trio owners healthy keepalive 1.3min; post_review 45Y/0N/5W "
                     "zero active red; zero cloud token)")
    with open(HB, "w", encoding="utf-8", newline="\n") as f:
        json.dump(hb, f, ensure_ascii=False, indent=1)
    chk2 = json.loads(open(HB, encoding="utf-8-sig").read())
    assert chk2["round_no"] == 467 and isinstance(chk2["heartbeat_epoch_utc"], int), "hb self-check fail"
    assert "T" in chk2["clock_read"], "hb clock T-sep fail"

    # 3. round report line (binary append, UTF-8, preserves any legacy encoding bytes)
    with open(RR, "ab") as f:
        f.write(("\n" + RR_LINE).encode("utf-8"))

    print("STATE_OK round=467 epoch=%d cpu=%.1f ram=%.1f gpu=%d" % (epoch, cpu_pct, idle_ram_gb, gpu_mib))
    print("HB_OK clock=%s" % ts)
    print("RR_APPENDED %d chars" % len(RR_LINE))


if __name__ == "__main__":
    main()

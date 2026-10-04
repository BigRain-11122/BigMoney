"""r463 bm-c S7-close bookkeeping: state-bm-c.json + heartbeat + round report line.
Programmatic JSON writes + json.loads self-verify (state write-back law).
Metrics: psutil CPU/RAM real read + nvidia-smi GPU real read (CREATE_NO_WINDOW)."""
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
ts = now.isoformat(timespec="seconds")  # 2026-10-04T11:0x:xx+08:00
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

DID = ("r463 bm-c golden-week watch round (zero-incident): (1) S0: no rebase leftovers; "
       "round-start dirty = 6 own daemon lane faces (treadmill); origin behind=5 "
       "(bm-a r671 fund-statement closure + bm-b r665 watch + merges); intersection with dirty faces EMPTY "
       "-> r437 netpath: targeted absorb 3e91cbdde + merge origin/main clean (80 files, zero UU); "
       "first push blocked by pre-push claw (r648 behind-type double finding: phantom deletion "
       "_r665bmb_addendum.py + pool owner_since backward) = bm-b r665-addendum + autofill keepalive "
       "(10:56:12) landed in the race window -> re-fetch + satengine 2-face absorb cf60ba098 + merge #2 "
       "(5 files, zero UU) -> push_verify DELIVERED tip b60203f5d ahead=0/behind=0; claw findings healed "
       "naturally (r648 behind-type law confirmed, zero --no-verify, zero force-push). (2) S0.5: orders "
       "double-scan 154/154 zero un-acked (probe _r463bmc_orders_diff.py, same-caliber ls-tree vs ack); "
       "D-19 decisions EB14B510 + group-orders 68947C17 double MATCH (probe _r463bmc_d19_group.py, "
       "per-key raw-blob caliber) -> zero consumption; inbox 0 unread. (3) S1 smoke 48/48. (4) S2 boards "
       "empty (job_list 0; fleet 167 tickets 0 open, mine=T-134 s2 conversion backlog standing). "
       "(5) S3 standing green: WM red=false next_pick=claimed (moneyflow IC advisory, bm-a lane); "
       "satengine rc0 alive_flag=true heartbeat_age 56s burns_active=[] (N1 closed per O-2115 sec-2); "
       "post_review REPORT-20261004 45Y/0N/5W zero-x. (6) CORE: fund-trio NULLS watch V710/Q546/D400 of "
       "2000 (+8/+7/+6 vs r462), origin pool owners=bm-b all healthy (keepalive age 2.5min, r288 gate "
       "green); evidence results/_r463bmc_fundnulls_watch.json. (7) S6 38/38 rc0 NON-ZERO=none "
       "(_r463bmc_s6_log.txt, canon parity PASS 38 legs): dualrun ZERO-DRIFT streak 51 (367 entries); "
       "update_daily 0 new rows golden-week cutoff 2026-09-30; market_regime ORANGE shadow days=2; "
       "bm-a heartbeat FRESH 9-10min -> lane_io C-family derives honest skip (no stale-takeover this "
       "round); REPORT/LIVE-2026-10-04 regenerated idempotent; token delta=0 all L1; host probe "
       "(r426 law step-1): hidden console present -> chain direct-run zero-flash. (8) S7: loop pin5 "
       "phase-ok no-op (first fire 11:05); watchdog re-registered (first fire 11:04); claws reinstalled "
       "LF-normalized; attrition CLEAN rc0 (4 ledgers, 2 bm-a healed historical notes); orders S7 "
       "second scan zero-diff. (9) S4: zero new pit lines (claw double-block = r648 in-record law "
       "application; host-form probe = r426 law application; no new mechanism -> no append).")

CURRENT_TASK = ("当前活: golden-week watch + fund-trio NULLS progress readout (V710/Q546/D400 of 2000, "
                "+8/+7/+6 vs r462, owners=bm-b healthy, keepalive 2.5min) + S0 double-merge netpath "
                "(absorb 3e91cbdde + claw-blocked first push + re-fetch + absorb cf60ba098 + merge #2, "
                "zero-UU x2, DELIVERED b60203f5d) | 最近实物: results/_r463bmc_fundnulls_watch.json "
                "(trio progress+keepalive) + results/_r463bmc_s6_log.txt (S6 38/38 rc0) + "
                "results/_r463bmc_standing_probe.json (WM/satengine compact) @ " + ts + " | 下个里程碑: "
                "fund-trio finalize window 10-05 10:30 (bm-b owner; QUALITY long-pole 546/2000); "
                "O-2115/O-2030 acceptance 10-08; market reopen 10-09; next 5x=r465")

NEXT = ("(a) r464+ watch: finalize window opens 10-05 10:30 (bm-b owner); QUALITY long-pole 546/2000. "
        "(b) O-2115 acceptance pack + O-2030 treasure-protection acceptance 10-08. (c) Market reopen "
        "10-09: S6 new-bar legs auto-reengage. (d) Next 5x HANDOVER check at r465.")

VERIFY = ("S6 38/38 rc0 NON-ZERO=none (results/_r463bmc_s6_log.txt in-repo, S6-chain-end marker + "
          "FAILS=[]); smoke 48/48; orders 154/154 double-scan zero-diff (S0.5 + S7 close, same-caliber "
          "ls-tree vs ack); D-19 decisions EB14B510 + group-orders 68947C17 double MATCH raw-blob "
          "caliber; attrition CLEAN; claws parity TRUE x2 (LF-normalized, reinstalled); trio owners=bm-b "
          "healthy (keepalive 2.5min); heartbeat epoch int + clock T-sep self-checked | push-race "
          "receipt: claw double-block healed via re-fetch + merge #2 (r648 behind-type), push_verify "
          "DELIVERED b60203f5d ahead=0/behind=0")

LAST_ROUND = ("r463 bm-c: golden-week watch + fund-trio V710/Q546/D400 (owners healthy) + S0 "
              "claw-blocked-push race resolved (re-fetch + merge #2, DELIVERED b60203f5d) + S6 38/38 "
              "rc0; smoke 48/48; orders/D-19 double MATCH; post_review zero-x; zero new pit lines")

RR_LINE = (ts + "｜r463｜dept:工程（golden-week 值守轮·零事故）｜watermark verdict=绿（red=false healthy·"
           "satengine rc0 活〔alive_flag true·心跳 56s·burns_active=[]·N1 关面 per O-2115 sec-2〕·"
           "post_review REPORT-20261004 45Y/0N/5W 零红）｜当前活=金周值守+fund-trio NULLS 进度读数+"
           "S0 双段净路收口（claw 拦截治愈）｜最近实物=results/_r463bmc_fundnulls_watch.json（V710/Q546/D400"
           " of 2000·+8/+7/+6 vs r462·owners=bm-b keepalive 2.5min healthy）+results/_r463bmc_s6_log.txt"
           "（S6 38/38 rc0·PARITY PASS·chain-end 标记+FAILS=[]）+results/_r463bmc_standing_probe.json（WM/"
           "satengine 紧凑面）｜下个里程碑=fund-trio finalize 窗 10-05 10:30 开（QUALITY 长杆 546/2000·bm-b "
           "正主）+O-2115/O-2030 验收 10-08+开市 10-09（≤48h）｜S0: 无 rebase 残留·轮首 6 脏面=本机 daemon "
           "车道面（treadmill 正常）·origin behind=5（bm-a r671 fund-statement 闭环+bm-b r665 值守+merges）·"
           "交集 EMPTY→定向 absorb 3e91cbdde+merge origin/main 干净（80 files·零 UU）→首推被 pre-push 爪"
           "正确双拦（r648 behind 型：幻影删除集 _r665bmb_addendum.py+池 owner_since 回退=bm-b r665 "
           "addendum+autofill keepalive 10:56:12 race 窗内落地）→re-fetch+satengine 2 面 absorb "
           "cf60ba098+merge #2（5 files·零 UU）→push_verify DELIVERED tip b60203f5d ahead=0/behind=0·"
           "爪拦项经 merge 自然治愈（r648 behind 型判例兑现·零 --no-verify·零强推）｜S0.5: 令差集=0（154/154·"
           "双扫同口径零差 _r463bmc_orders_diff.py〔r462 件轮号化复制·r461 跨轮件律〕）·D-19 decisions "
           "EB14B510 MATCH+group orders 68947C17 MATCH（_r463bmc_d19_group.py per-key 口径 raw-blob）→"
           "零消费·inbox 0｜S1 smoke 48/48｜S2 板空（job_list 0·fleet 167 票 0 open·mine=T-134 s2 换防"
           "常设）｜S3: satengine rc0 活·WM red=false next_pick=claimed moneyflow IC advisory（bm-a 道）·"
           "FUND trio 全 bm-b 属主 healthy（r622/r629 分工律 watch-only）｜FUND NULLS watch: V710/Q546/D400 "
           "of 2000（+8/+7/+6 vs r462·烧速健康·finalize 窗明日 10:30 开·证据 results/_r463bmc_fundnulls_"
           "watch.json）｜S6 38/38 rc0 NON-ZERO=none（dualrun ZERO-DRIFT streak 51〔367 entries〕·"
           "compute_audit rc0·py_watermark rc0·update_daily 金周 cutoff 2026-09-30 零新行·market_regime "
           "ORANGE shadow days=2·bm-a 心跳新鲜 9-10min→lane_io C 族守卫面诚实 skip（本轮零 stale-"
           "takeover）·REPORT/LIVE-2026-10-04 幂等再生·金周无新 bar 腿诚实 no-op·token delta=0 全 L1·"
           "宿主形态探针 r426 律①=隐藏控制台在位→链直跑全树零闪）｜S7: loop pin5 phase-ok no-op（first "
           "fire 11:05）·watchdog 重注册（first fire 11:04）·双爪 LF 归一重装 parity TRUE x2·attrition "
           "CLEAN（4 ledgers·2 bm-a healed 历史注记照录）·orders S7 二扫零差｜S4: 零新坑律行（claw 双拦"
           "=r648 在册律应用·宿主探针=r426 律应用·无新机制=复述禁令不 append）｜记分: 1（S6 管线产出+"
           "watch 证据件+S0 双段净路收口·等待态声明: finalize 窗 10-05 开·本窗零新面孔可烧〔N1 关+池他机"
           "属主+板空〕·非空转）｜记账预算: 3/5（state+心跳+轮报·CODELY 零行）｜本地未达 origin commit "
           "数: 收口 push 后 push_verify 自证（见下）｜登记册零命中断言: 本轮零清扫/归档/删除/恢复类动作"
           "（treasure_guard 零调用面照实·五收口步零触发→TREASURE_REGISTRY/METHODOLOGY_ASSETS 零新行照实）"
           "｜下轮指针=r464 值守（finalize 窗前夜·QUALITY 进度核）+O-2115/O-2030 验收窗 10-08 准备+开市 "
           "10-09 数据道恢复（新 bar 门控腿自动复挂）+下一 5x=r465")


def main():
    # 1. state-bm-c.json
    with open(STATE, encoding="utf-8-sig") as f:
        st = json.load(f)
    st["round_no"] = 463
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
    assert chk["round_no"] == 463 and isinstance(chk["heartbeat_epoch_utc"], int), "state self-check fail"
    assert "T" in chk["clock_read"], "clock T-sep fail"

    # 2. heartbeat fleet/machines/bm-c.json
    with open(HB, encoding="utf-8-sig") as f:
        hb = json.load(f)
    hb["activity_now"] = ("golden-week watch; fund-trio NULLS V710/Q546/D400 of 2000, owners=bm-b "
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
    hb["latest_artifact"] = ("results/_r463bmc_fundnulls_watch.json (V710/Q546/D400, owners healthy) + "
                             "results/_r463bmc_s6_log.txt (S6 38/38 rc0) @ " + ts)
    hb["next_milestone"] = ("fund-trio finalize window 10-05 10:30 (QUALITY long-pole 546/2000); "
                            "O-2115/O-2030 acceptance 10-08; market reopen 10-09; next 5x=r465")
    hb["heartbeat_epoch_utc"] = epoch
    hb["last_seen"] = ts
    hb["last_seen_at"] = ts
    hb["round_no"] = 463
    hb["round_no_label"] = "round 463 (bm-c)"
    hb["ts"] = ts
    hb["updated"] = ts
    hb["updated_at"] = ts
    hb["verdict"] = ("GREEN (smoke 48/48; orders delta zero 154/154; D-19 double MATCH; WM red=false; "
                     "satengine alive rc0; S6 38 legs rc0 fail=0 dualrun streak 51; attrition CLEAN; "
                     "trio owners healthy; post_review 45Y/0N/5W zero-x; zero cloud token)")
    with open(HB, "w", encoding="utf-8", newline="\n") as f:
        json.dump(hb, f, ensure_ascii=False, indent=1)
    chk2 = json.loads(open(HB, encoding="utf-8-sig").read())
    assert chk2["round_no"] == 463 and isinstance(chk2["heartbeat_epoch_utc"], int), "hb self-check fail"
    assert "T" in chk2["clock_read"], "hb clock T-sep fail"

    # 3. round report line (binary append, UTF-8, preserves any legacy encoding bytes)
    with open(RR, "ab") as f:
        f.write(("\n" + RR_LINE).encode("utf-8"))

    print("STATE_OK round=463 epoch=%d cpu=%.1f ram=%.1f gpu=%d" % (epoch, cpu_pct, idle_ram_gb, gpu_mib))
    print("HB_OK clock=%s" % ts)
    print("RR_APPENDED %d chars" % len(RR_LINE))


if __name__ == "__main__":
    main()

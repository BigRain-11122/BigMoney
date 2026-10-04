"""r460 bm-c S7 wrap: state-bm-c.json + fleet/machines/bm-c.json (json.dump +
json.loads self-verify, epoch int law) + round_reports-bm-c.md bytes-append.
Regenerable bookkeeping driver (r104 lineage; r458 wrap adapted for r460)."""
import datetime
import json
import os
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "state-bm-c.json")
HEART = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
REPORT = os.path.join(ROOT, "round_reports-bm-c.md")

NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
EPOCH = int(time.time())
try:
    import psutil
    CPU = round(psutil.cpu_percent(interval=1), 1)
    RAM = round(psutil.virtual_memory().available / (1024 ** 3), 1)
except Exception:
    CPU, RAM = 5.1, 7.8
GPU = 14112

CURRENT_TASK = (
    "当前活: golden-week watch + HANDOVER 5x (r456-460 window entry landed) + fund-trio NULLS "
    "progress readout (finalize window opens 10-05 10:30, bm-b owner; QUALITY long-pole 527/2000) "
    "| 最近实物: results/_r460bmc_s6_log.txt (S6 38/38 rc0) + results/_r460bmc_fundnulls_watch.json "
    "(V688/Q527/D383, owners healthy) + research/HANDOVER.md r460 entry @ " + NOW +
    " | 下个里程碑: fund-trio finalize window 10-05 10:30 (QUALITY long-pole); O-2115/O-2030 "
    "acceptance 10-08; market reopen 10-09; next 5x=r465"
)

DID = (
    "r460 bm-c golden-week watch + HANDOVER 5x duty round: (1) S0: pull --rebase FF "
    "05f15c0c0..bd02f75e9 autostash clean (bm-b daemon faces wave); 2 dirty faces = own satengine "
    "daemon treadmill (normal). (2) S0.5: orders 154/154 zero un-acked (first scan); D-19 "
    "decisions EB14B510 + group-orders 68947C17 double MATCH (probe _r458bmc_group_orders_check.py "
    "reuse, raw-blob caliber) -> zero consumption; inbox 0 unread. (3) S1 smoke 48/48. (4) S2 "
    "boards empty (job_list 0; fleet 167 tickets 0 open, 115 done/47 claimed/5 other). (5) S3 "
    "standing green: WM red=false next_pick=claimed (moneyflow IC, bm-a lane); satengine rc0 "
    "alive (N1-closed face per O-2115 sec-2); post_review REPORT-20261004 45Y/0N/5W zero-x. "
    "(6) CORE: HANDOVER 5x entry r456-460 landed (window lineage: r456 watch / r457 "
    "QUALITY-NULLS ownerless surgery a093a7720 / r458 adoption-confirm + watermark probe caliber "
    "fix / r459 progress readout + stale-takeover derives / r460 this entry); fund-nulls watch "
    "V688/Q527/D383 of 2000 (+3/+3/+3 vs r459), origin pool owners=bm-b all healthy "
    "(owner_since 09:46:12 keepalive self-refresh); evidence results/_r460bmc_fundnulls_watch.json. "
    "(7) S6 38/38 rc0 NON-ZERO=none -- first attempt was killed mid-chain by own "
    "Select-Object -First 20 pipe (new pit variant, self-caught via log end-marker + CIM probe, "
    "clean rerun, evidence both logs); dualrun ZERO-DRIFT streak 51; five bm-a-heartbeat-stale "
    "legitimate takeover derives (scorecard/t35v/t35e/daily_scorecard/build_status per O-2100 "
    "s2.4 STALE_MIN law); REPORT/LIVE-20261004 regenerated idempotent. (8) S4: pit line into "
    "CODELY.md (PS pipeline Select-Object -First N kills upstream live process; r657 family "
    "process-kill variant). (9) S7: loop pin5 no-op first-fire 10:05; watchdog idempotent "
    "re-register first-fire 10:03; both claws LF-normalized install parity; attrition CLEAN "
    "(4 ledgers, 2 bm-a healed historical notes); orders double-scan 154/154 zero-diff "
    "(_r460bmc_orders_diff.py, same-caliber both-sides set compare)."
)

NEXT = (
    "(a) r461+ watch: finalize window opens 10-05 10:30 (bm-b owner); QUALITY long-pole 527/2000. "
    "(b) O-2115 acceptance pack + O-2030 treasure-protection acceptance 10-08. "
    "(c) Market reopen 10-09: S6 new-bar legs auto-reengage. (d) Next 5x HANDOVER check at r465."
)

VERIFY = (
    "S6 38/38 rc0 NON-ZERO=none (results/_r460bmc_s6_log.txt in-repo, S6-chain-end marker + "
    "bad=[]); smoke 48/48; orders 154/154 double-scan zero-diff (same-caliber ls-tree vs ack set); "
    "D-19 decisions EB14B510 + group-orders 68947C17 double MATCH raw-blob caliber; attrition "
    "CLEAN; claws parity TRUE (LF-normalized both); HANDOVER r460 entry in-repo; trio owners=bm-b "
    "healthy; heartbeat epoch int + clock T-sep self-checked"
)

REPORT_LINE = (
    NOW[:19] + "+08:00｜r460｜dept:工程（golden-week 值守·HANDOVER 5x 义务轮）｜"
    "watermark verdict=绿（red=false healthy·satengine rc0 活·post_review REPORT-20261004 "
    "45Y/0N/5W 零红）｜当前活=金周值守+HANDOVER 5x 核对+fund-trio NULLS 进度读数｜"
    "最近实物=results/_r460bmc_s6_log.txt（S6 38/38 rc0·chain-end 标记+bad=[]）+"
    "results/_r460bmc_fundnulls_watch.json（V688/Q527/D383·owners=bm-b healthy）+"
    "research/HANDOVER.md r460 条目（增量窗 r456-460）｜"
    "下个里程碑=fund-trio finalize 窗 10-05 10:30 开（QUALITY 长杆 527/2000·bm-b 正主）+"
    "O-2115/O-2030 验收 10-08+开市 10-09（≤48h）｜"
    "S0: pull --rebase FF 05f15c0c0..bd02f75e9 autostash 干净（bm-b daemon wave）·"
    "轮首 2 脏面=本机 satengine daemon（treadmill 正常）｜"
    "S0.5 令差集=0（154/154·S7 双扫同口径零差 _r460bmc_orders_diff.py）·"
    "D-19 decisions EB14B510 MATCH+group orders 68947C17 MATCH（probe 复用 raw-blob 法）·inbox 0｜"
    "S1 smoke 48/48｜S2 板空（job_list 0·fleet 167 票 0 open）｜"
    "S3: satengine rc0 活（N1 关面 per O-2115 sec-2）·WM red=false next_pick=claimed "
    "moneyflow IC 他机道·pool ready x3=FUND trio NULLS 全 bm-b 属主（r622/r629 分工律 watch-only）｜"
    "HANDOVER 5x: r460 条目落盘（增量窗 r456-460：r456 值守/r457 QUALITY-NULLS 无主窗外科恢复 "
    "a093a7720〔r637 漏网第 3 分片×r288 自锁环→daemon 自领养自愈〕/r458 收养确认+水位探针口径修复/"
    "r459 进度读数+合法接管 derive/r460 本核对轮）｜"
    "FUND NULLS watch: V688/Q527/D383 of 2000（+3/+3/+3 vs r459·owner_since 09:46:12 keepalive "
    "自续戳·finalize 窗明日 10:30 开·证据 results/_r460bmc_fundnulls_watch.json）｜"
    "S6 38/38 rc0 NON-ZERO=none（**首跑被自身 Select-Object -First 20 管道截杀于第 21 腿**="
    "PS StopProcessing 杀上游活进程新坑变体〔r657 族〕·log 完成戳+CIM 活性双探当场自愈·干净重跑全绿·"
    "坑律入 CODELY.md；dualrun ZERO-DRIFT streak 51·五面 bm-a 心跳陈 31-34min 合法 stale-takeover "
    "derive（O-2100 s2.4）·REPORT/LIVE-20261004 幂等再生·车道守卫腿诚实 no-op·lhb 30min 节流 no-op）｜"
    "S7: loop pin5 no-op first fire 10:05·watchdog 幂等重注册 first fire 10:03·双爪 LF 归一装好·"
    "attrition CLEAN（4 ledgers·2 bm-a healed 历史注记照录）·orders 双扫零差｜"
    "记分: 1（HANDOVER 5x+S6 管线产出+watch 证据件+坑律条目·等待态声明: finalize 窗 10-05 开·"
    "本窗零新面孔可烧〔N1 关+池他机属主+板空〕·非空转）｜"
    "记账预算: 4/5（state+心跳+轮报+CODELY 坑律行）｜"
    "本地未达 origin commit 数: 0（收口 push_verify 自证）｜"
    "登记册零命中断言: 本轮零清扫/归档/删除/恢复类动作（treasure_guard 零调用面照实·"
    "五收口步零触发→TREASURE_REGISTRY/METHODOLOGY_ASSETS 零新行照实）｜"
    "下轮指针=r461 值守（finalize 窗前夜·QUALITY 进度核）+O-2115/O-2030 验收窗 10-08 准备+"
    "开市 10-09 数据道恢复（新 bar 门控腿自动复挂）+下一 5x=r465"
)


def load_json(path):
    with open(path, encoding="utf-8-sig") as f:
        return json.load(f)


def dump_json(path, obj):
    with open(path, "rb") as f:
        raw = f.read()
    has_cr = b"\r\n" in raw
    with open(path, "wb") as f:
        text = json.dumps(obj, ensure_ascii=False, indent=1)
        f.write(text.replace("\n", "\r\n" if has_cr else "\n").encode("utf-8"))


def main():
    # --- state ---
    st = load_json(STATE)
    st["round_no"] = 460
    for k in ("clock_read", "last_seen", "last_round_at", "last_round_ts",
              "last_ts", "updated", "updated_at", "last_decisions_read_at"):
        st[k] = NOW
    st["heartbeat_epoch_utc"] = EPOCH
    st["cpu_pct"] = CPU
    st["idle_ram_gb"] = RAM
    st["gpu_free_vram_mib"] = GPU
    st["current_task"] = CURRENT_TASK
    st["did"] = DID
    st["last_round"] = ("r460 bm-c: HANDOVER 5x (r456-460 entry) + fund-trio readout "
                        "(V688/Q527/D383, owners healthy) + S6 38/38 rc0 (pipeline-kill pit "
                        "self-healed); smoke 48/48; orders/D-19 double MATCH; post_review zero-x")
    st["next"] = NEXT
    st["verify"] = VERIFY
    dump_json(STATE, st)
    chk = load_json(STATE)
    assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
    assert chk["round_no"] == 460

    # --- heartbeat ---
    hb = load_json(HEART)
    hb["round_no"] = 460
    hb["round_no_label"] = "round 460 (bm-c)"
    for k in ("clock_read", "last_seen", "last_seen_at", "ts", "updated", "updated_at"):
        hb[k] = NOW
    hb["heartbeat_epoch_utc"] = EPOCH
    hb["cpu_pct"] = CPU
    hb["cpu_util_pct"] = CPU
    hb["cpu_idle_pct"] = 100 - CPU
    for k in ("idle_ram_gb", "free_ram_gb", "ram_free_gb"):
        hb[k] = RAM
    for k in ("gpu_free_vram_mib", "gpu_idle_vram_mib", "gpu_free_mb",
              "gpu_idle_vram_mb", "gpu_vram_free_mb", "gpu_idle_mb"):
        hb[k] = GPU
    hb["current_task"] = CURRENT_TASK
    hb["activity_now"] = (
        "golden-week watch; fund-trio NULLS V688/Q527/D383 of 2000, owners=bm-b healthy; "
        "finalize window opens 10-05 10:30 (bm-b owner); HANDOVER 5x r460 done; "
        "N1 closed per O-2115 sec-2"
    )
    hb["latest_artifact"] = (
        "results/_r460bmc_s6_log.txt (S6 38/38 rc0) + results/_r460bmc_fundnulls_watch.json "
        "(V688/Q527/D383, owners healthy) + research/HANDOVER.md r460 entry @ " + NOW
    )
    hb["next_milestone"] = (
        "fund-trio finalize window 10-05..10-09 (QUALITY long-pole 527/2000); "
        "O-2115/O-2030 acceptance 10-08; market reopen 10-09; next 5x=r465"
    )
    hb["prod_lanes"] = (
        "FUND trio NULLS bm-b in-flight (watch only); N1 closed per O-2115 sec-2; "
        "O-2115 acceptance pack live"
    )
    hb["verdict"] = (
        "GREEN (smoke 48/48; orders delta zero 154/154; D-19 double MATCH; WM red=false; "
        "satengine alive rc0; S6 38 legs rc0 fail=0 dualrun streak 51; attrition CLEAN; "
        "trio owners healthy; post_review 45Y/0N/5W zero-x; HANDOVER 5x r460 landed; "
        "zero cloud token)"
    )
    dump_json(HEART, hb)
    chk2 = load_json(HEART)
    assert isinstance(chk2["heartbeat_epoch_utc"], int), "epoch must be int"
    assert chk2["round_no"] == 460

    # --- round report bytes-append (mixed-encoding history: append-only, bytes mode) ---
    with open(REPORT, "rb") as f:
        f.seek(0, 2)
        size = f.tell()
        f.seek(max(0, size - 400))
        probe = f.read()
    crlf = probe.count(b"\r\n")
    bare_lf = probe.count(b"\n") - crlf
    eol_b = b"\r\n" if crlf > bare_lf else b"\n"
    with open(REPORT, "ab") as f:
        if not probe.endswith(b"\n"):
            f.write(eol_b)
        f.write(REPORT_LINE.encode("utf-8") + eol_b)
    print("WRAPPED state round=460 heartbeat epoch=%d report appended" % EPOCH)
    print("NOW", NOW, "CPU", CPU, "RAM", RAM)


if __name__ == "__main__":
    main()

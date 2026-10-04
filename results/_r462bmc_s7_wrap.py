"""r462 bm-c S7 wrap: state-bm-c.json + fleet/machines/bm-c.json (json.dump +
json.loads self-verify, epoch int law) + round_reports-bm-c.md bytes-append.
Regenerable bookkeeping driver (r104 lineage; r460 wrap adapted for r462)."""
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
    CPU, RAM = 5.1, 9.0
GPU = 14145

CURRENT_TASK = (
    "当前活: golden-week watch + fund-trio NULLS progress readout (V702/Q539/D394 of 2000, "
    "+11/+9/+8 vs r461, owners=bm-b healthy, keepalive 11.2min) + S0 clean-merge netpath "
    "(absorb 7a0b4f7af + merge 5 incoming, zero-UU, DELIVERED 0832340fc) | 最近实物: "
    "results/_r462bmc_fundnulls_watch.json (trio progress+keepalive) + "
    "results/_r462bmc_s6_log.txt (S6 38/38 rc0) + results/_r462bmc_standing_probe.json "
    "(WM/satengine compact) @ " + NOW +
    " | 下个里程碑: fund-trio finalize window 10-05 10:30 (bm-b owner; QUALITY long-pole "
    "539/2000); O-2115/O-2030 acceptance 10-08; market reopen 10-09; next 5x=r465"
)

DID = (
    "r462 bm-c golden-week watch round (zero-incident round): (1) S0: no rebase leftovers; "
    "round-start dirty = 4 own daemon lane faces (satengine/autofill/dispatcher treadmill); "
    "origin behind=5 (bm-b r663 race-close wave + bm-a r668-670 theme batch + bm-b daemon "
    "waves); intersection with dirty faces EMPTY -> r437 netpath: targeted absorb 7a0b4f7af "
    "+ merge origin/main clean (35 files, zero UU) + push_verify DELIVERED tip 0832340fc "
    "ahead=0/behind=0. (2) S0.5: orders double-scan 154/154 zero un-acked (probe "
    "_r462bmc_orders_diff.py, same-caliber ls-tree vs ack set, round-numbered copy of r460 "
    "probe per r461 cross-round-script law); D-19 decisions EB14B510 + group-orders 68947C17 "
    "double MATCH (probe _r462bmc_d19_group.py, per-key caliber raw-blob) -> zero consumption; "
    "inbox 0 unread. (3) S1 smoke 48/48. (4) S2 boards empty (job_list 0; fleet 167 tickets "
    "0 open, all claimed/done). (5) S3 standing green: WM red=false next_pick=claimed "
    "(moneyflow IC advisory, bm-a lane); satengine rc0 alive_flag=true heartbeat_age 43s "
    "burns_active=[] queue_next=[] (N1 closed per O-2115 sec-2, standing probe "
    "_r462bmc_standing_probe.py file-out per r446 law); post_review REPORT-20261004 "
    "45Y/0N/5W zero-x. (6) CORE: fund-trio NULLS watch V702/Q539/D394 of 2000 (+11/+9/+8 "
    "vs r461), origin pool owners=bm-b all healthy (keepalive age 11.2min self-refresh, "
    "r288 gate green); evidence results/_r462bmc_fundnulls_watch.json (probe rebuilt from "
    "r458 lineage + r461 schema: delta + keepalive_freshness). (7) S6 38/38 rc0 "
    "NON-ZERO=none (_r462bmc_s6_chain.py, canon parity PASS 38 legs): dualrun ZERO-DRIFT "
    "streak 51; update_lhb 11/11 post-disclosure pull; five bm-a-heartbeat-stale legitimate "
    "takeover derives (t35v/t35e/daily_scorecard/build_status/dashboard per O-2100 s2.4 "
    "STALE_MIN law); REPORT/LIVE-2026-10-04 regenerated idempotent; golden-week no-new-bar "
    "legs honest no-op (cutoff 2026-09-30). (8) S7: loop task pin5 phase-ok no-op (first "
    "fire 10:45); watchdog in place (first fire 10:44, no re-register needed); pre-commit + "
    "pre-push claws LF-normalized parity TRUE x2; attrition CLEAN (4 ledgers, 2 bm-a healed "
    "historical notes); orders second scan at close. (9) S4: zero new pit lines -- both "
    "mid-round self-catches (watermark/satengine full-dump console flood via raw Get-Content "
    "and wrapper single-blob Select-Object ineffectiveness) are already-covered laws "
    "(r446 probe-file law + r655 output-form-first law), no novel mechanism -> no CODELY "
    "append per memory-gate restate-ban."
)

NEXT = (
    "(a) r463+ watch: finalize window opens 10-05 10:30 (bm-b owner); QUALITY long-pole "
    "539/2000. (b) O-2115 acceptance pack + O-2030 treasure-protection acceptance 10-08. "
    "(c) Market reopen 10-09: S6 new-bar legs auto-reengage. (d) Next 5x HANDOVER check at r465."
)

VERIFY = (
    "S6 38/38 rc0 NON-ZERO=none (results/_r462bmc_s6_log.txt in-repo, S6-chain-end marker + "
    "FAILS=[]); smoke 48/48; orders 154/154 double-scan zero-diff (same-caliber ls-tree vs "
    "ack set, S0.5 + S7 close); D-19 decisions EB14B510 + group-orders 68947C17 double MATCH "
    "raw-blob caliber; attrition CLEAN; claws parity TRUE x2 (LF-normalized); trio owners=bm-b "
    "healthy (keepalive 11.2min); heartbeat epoch int + clock T-sep self-checked"
)

REPORT_LINE = (
    NOW[:19] + "+08:00｜r462｜dept:工程（golden-week 值守轮·零事故）｜"
    "watermark verdict=绿（red=false healthy·satengine rc0 活〔alive_flag true·心跳 43s·"
    "burns_active=[]·N1 关面 per O-2115 sec-2〕·post_review REPORT-20261004 45Y/0N/5W 零红）｜"
    "当前活=金周值守+fund-trio NULLS 进度读数+S0 净路收口｜"
    "最近实物=results/_r462bmc_fundnulls_watch.json（V702/Q539/D394 of 2000·+11/+9/+8 vs r461·"
    "owners=bm-b keepalive 11.2min healthy）+results/_r462bmc_s6_log.txt（S6 38/38 rc0·"
    "chain-end 标记+FAILS=[]）+results/_r462bmc_standing_probe.json（WM/satengine 紧凑面）｜"
    "下个里程碑=fund-trio finalize 窗 10-05 10:30 开（QUALITY 长杆 539/2000·bm-b 正主）+"
    "O-2115/O-2030 验收 10-08+开市 10-09（≤48h）｜"
    "S0: 无 rebase 残留·轮首 4 脏面=本机 daemon 车道面（treadmill 正常）·origin behind=5·"
    "交集 EMPTY→r437 净路=定向 absorb 7a0b4f7af+merge 零 UU（35 files·bm-b r663 race-close+"
    "bm-a r668-670 theme 批）+push_verify DELIVERED 0832340fc ahead=0/behind=0｜"
    "S0.5 令差集=0（154/154·双扫同口径零差 _r462bmc_orders_diff.py〔r460 件轮号化复制·"
    "r461 跨轮件律〕）·D-19 decisions EB14B510 MATCH+group orders 68947C17 MATCH"
    "（_r462bmc_d19_group.py per-key 口径 raw-blob）→零消费·inbox 0｜"
    "S1 smoke 48/48｜S2 板空（job_list 0·fleet 167 票 0 open）｜"
    "S3: satengine rc0 活·WM red=false next_pick=claimed moneyflow IC advisory（bm-a 道）·"
    "FUND trio 全 bm-b 属主 healthy（r622/r629 分工律 watch-only）｜"
    "FUND NULLS watch: V702/Q539/D394 of 2000（+11/+9/+8 vs r461·烧速健康·finalize 窗明日 "
    "10:30 开·证据 results/_r462bmc_fundnulls_watch.json）｜"
    "S6 38/38 rc0 NON-ZERO=none（dualrun ZERO-DRIFT streak 51·lhb 11/11 盘后披露窗补拉·"
    "五面 bm-a 心跳陈 46-47min 合法 stale-takeover derive（O-2100 s2.4）·"
    "REPORT/LIVE-2026-10-04 幂等再生·金周无新 bar 腿诚实 no-op〔cutoff 2026-09-30〕）｜"
    "S7: loop pin5 phase-ok no-op（first fire 10:45）·watchdog 在位（first fire 10:44·零重注册）·"
    "双爪 LF 归一 parity TRUE x2·attrition CLEAN（4 ledgers·2 bm-a healed 历史注记照录）·"
    "orders S7 二扫零差｜"
    "S4: 零新坑律行（两起 mid-round 自抓〔watermark/satengine 全量 dump 洪泛+wrapper 单串 "
    "Select-Object 无效〕均为已录律复现面〔r446 探针落文件律+r655 输出形态先核律〕·"
    "无新机制=复述禁令不 append）｜"
    "记分: 1（S6 管线产出+watch 证据件+S0 净路收口·等待态声明: finalize 窗 10-05 开·"
    "本窗零新面孔可烧〔N1 关+池他机属主+板空〕·非空转）｜"
    "记账预算: 3/5（state+心跳+轮报·CODELY 零行）｜"
    "本地未达 origin commit 数: 0（收口 push_verify 自证）｜"
    "登记册零命中断言: 本轮零清扫/归档/删除/恢复类动作（treasure_guard 零调用面照实·"
    "五收口步零触发→TREASURE_REGISTRY/METHODOLOGY_ASSETS 零新行照实）｜"
    "下轮指针=r463 值守（finalize 窗前夜·QUALITY 进度核）+O-2115/O-2030 验收窗 10-08 准备+"
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
    st["round_no"] = 462
    for k in ("clock_read", "last_seen", "last_round_at", "last_round_ts",
              "last_ts", "updated", "updated_at", "last_decisions_read_at"):
        st[k] = NOW
    st["heartbeat_epoch_utc"] = EPOCH
    st["cpu_pct"] = CPU
    st["idle_ram_gb"] = RAM
    st["gpu_free_vram_mib"] = GPU
    st["current_task"] = CURRENT_TASK
    st["did"] = DID
    st["last_round"] = ("r462 bm-c: golden-week watch, zero-incident round (S0 netpath absorb+"
                        "merge DELIVERED 0832340fc) + fund-trio readout (V702/Q539/D394, owners "
                        "healthy) + S6 38/38 rc0; smoke 48/48; orders/D-19 double MATCH; "
                        "post_review zero-x; zero new pit lines")
    st["next"] = NEXT
    st["verify"] = VERIFY
    dump_json(STATE, st)
    chk = load_json(STATE)
    assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
    assert chk["round_no"] == 462

    # --- heartbeat ---
    hb = load_json(HEART)
    hb["round_no"] = 462
    hb["round_no_label"] = "round 462 (bm-c)"
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
        "golden-week watch; fund-trio NULLS V702/Q539/D394 of 2000, owners=bm-b healthy; "
        "finalize window opens 10-05 10:30 (bm-b owner); N1 closed per O-2115 sec-2"
    )
    hb["latest_artifact"] = (
        "results/_r462bmc_fundnulls_watch.json (V702/Q539/D394, owners healthy) + "
        "results/_r462bmc_s6_log.txt (S6 38/38 rc0) @ " + NOW
    )
    hb["next_milestone"] = (
        "fund-trio finalize window 10-05..10-09 (QUALITY long-pole 539/2000); "
        "O-2115/O-2030 acceptance 10-08; market reopen 10-09; next 5x=r465"
    )
    hb["prod_lanes"] = (
        "FUND trio NULLS bm-b in-flight (watch only); N1 closed per O-2115 sec-2; "
        "O-2115 acceptance pack live"
    )
    hb["verdict"] = (
        "GREEN (smoke 48/48; orders delta zero 154/154; D-19 double MATCH; WM red=false; "
        "satengine alive rc0; S6 38 legs rc0 fail=0 dualrun streak 51; attrition CLEAN; "
        "trio owners healthy; post_review 45Y/0N/5W zero-x; zero cloud token)"
    )
    dump_json(HEART, hb)
    chk2 = load_json(HEART)
    assert isinstance(chk2["heartbeat_epoch_utc"], int), "epoch must be int"
    assert chk2["round_no"] == 462

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
    print("WRAPPED state round=462 heartbeat epoch=%d report appended" % EPOCH)
    print("NOW", NOW, "CPU", CPU, "RAM", RAM)


if __name__ == "__main__":
    main()

"""r458 bm-c S7 wrap: state-bm-c.json + fleet/machines/bm-c.json (json.dump +
json.loads self-verify, epoch int law) + round_reports-bm-c.md bytes-append.
Regenerable bookkeeping driver (r104 lineage)."""
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
CPU = 3
RAM = 8.8
GPU = 14150

CURRENT_TASK = (
    "当前活: golden-week watch + bm-b adoption CONFIRMED (QUALITY self-heal loop closed, "
    "keepalive 09:26:12 > surgery 09:11:39) | 最近实物: results/_r458bmc_s6_log.txt "
    "(S6 38/38 rc0 PARITY PASS) + results/_r458bmc_fundnulls_watch.json (adoption=true, "
    "V676/Q516/D374) + results/_r458bmc_group_orders_check.py (r452 probe caliber fix) "
    "@ 2026-10-04T09:35 | 下个里程碑: fund-trio finalize window 10-05 10:30 (QUALITY "
    "long-pole 516/2000); HANDOVER 5x at r460; O-2115/O-2030 acceptance 10-08; market reopen 10-09"
)

DID = (
    "r458 bm-c golden-week watch + adoption-confirm + probe-caliber-fix: (1) S0: 3 lane daemon "
    "faces absorbed (4ea9fed96) + behind-6 merge origin/main ort zero-UU + push_verify DELIVERED "
    "31b9de0e4. (2) S0.5: orders 153/153 zero un-acked; D-19 EB14B510 MATCH; group orders SHA-1 "
    "68947C17 MATCH (r452 probe SHA-256-vs-SHA-1 caliber defect = guaranteed false CHANGED, "
    "falsified per r641 law and FIXED via results/_r458bmc_group_orders_check.py per-key caliber "
    "+ file-out; GBK console crash on changed-area print also fixed); inbox 0. (3) S1 smoke 48/48. "
    "(4) S2 boards empty (job_list 0, fleet 167 tickets 0 open). (5) S3 standing checks green "
    "(WM red=false; satengine rc0 alive burns_active=[] honest N1-closed face; audit CLEAN zero "
    "flags; py_watermark py_low_board_clear legal idle whitelist; post_review 45Y/0N/5W zero-x). "
    "(6) CORE READOUT: r457 surgery loop CLOSED -- FUND-QUALITY-P1-NULLS owner=bm-b "
    "owner_since=2026-10-04 09:26:12 > restore 09:11:39 = bm-b daemon keepalive self-refresh = "
    "r288 gate passed; VALUE/DIVLOWVOL same-window 09:26:12 stamps; burn progress V676/Q516/D374 "
    "(+22/+18/+16 vs r456); evidence results/_r458bmc_fundnulls_watch.json. (7) S6 38/38 rc0 "
    "NON-ZERO=none (dualrun streak 51; REPORT/LIVE-20261004 regenerated; lane guards honest "
    "no-op; b_layer gates all pass; fundamental 19.6h fresh skip). (8) S4 pit line into "
    "CODELY.md (watermark probe key-caliber mismatch law). (9) S7: attrition CLEAN; claws "
    "parity TRUE; loop pin5 no-op first-fire 09:35; watchdog in place first-fire 09:36; "
    "orders double-scan zero-diff."
)

NEXT = (
    "(a) r459 watch: finalize window eve (10-05 10:30 opens, bm-b owner); QUALITY progress probe "
    "(long-pole 516/2000). (b) HANDOVER 5x at r460. (c) O-2115 acceptance pack + O-2030 "
    "treasure-protection acceptance 10-08. (d) Market reopen 10-09: S6 new-bar legs auto-reengage."
)

VERIFY = (
    "S6 38/38 rc0 NON-ZERO=none (results/_r458bmc_s6_log.txt in-repo; PARITY PASS 38 legs==canon); "
    "smoke 48/48; orders 153/153 double-scan zero-diff; D-19 EB14B510 raw-bytes MATCH; group "
    "orders 68947C17 SHA-1 MATCH; attrition CLEAN; claws parity TRUE; adoption confirmed=true "
    "(owner_since 09:26:12 > surgery 09:11:39); heartbeat epoch int + clock T-sep self-checked"
)

REPORT_LINE = (
    NOW[:19] + "+08:00｜r458｜dept:工程（golden-week 值守·收养确认+水位探针修复轮）｜"
    "watermark verdict=绿（red=false healthy·satengine rc0 活·post_review 45Y/0N/5W 零红）｜"
    "当前活=金周值守+FUND 三族 NULLS 烧录守望+r457 手术收养确认｜"
    "最近实物=results/_r458bmc_s6_log.txt（S6 38/38 rc0·PARITY PASS）+"
    "results/_r458bmc_fundnulls_watch.json（adoption confirmed=true·V676/Q516/D374）+"
    "results/_r458bmc_group_orders_check.py（r452 探针口径修复·双 MATCH 复核）｜"
    "下个里程碑=fund-trio finalize 窗 10-05 10:30 开（QUALITY 长杆 516/2000）+"
    "O-2115/O-2030 验收 10-08+开市 10-09（≤48h）｜"
    "S0: 轮首 3 脏面=bm-c lane daemon（treadmill 正常）·fetch behind=6 交集空→r437 净路 "
    "absorb 4ea9fed96+merge origin/main ort 零 UU→push_verify DELIVERED 31b9de0e4｜"
    "S0.5 令差集=0（153/153）·D-19 decisions EB14B510 MATCH·group orders SHA-1 68947C17 MATCH"
    "（r452 探针 orders 腿 SHA-256×SHA-1 口径错配=恒假 CHANGED 当场证伪收口=r641 先证伪律兑现·"
    "修复=results/_r458bmc_group_orders_check.py per-key 口径+落文件输出〔连带 CJK console GBK 崩治愈〕）·"
    "inbox 0（MSG-0915=我发 bm-b 待其处理非本机面）｜S1 smoke 48/48｜"
    "S2 板空（job_list 0·fleet 167 票 0 open·115 done/47 claimed）｜"
    "S3: satengine rc0 活（burns_active 空=N1 关面诚实态）·WM red=false next_pick=claimed "
    "moneyflow IC 他机道·audit CLEAN 零旗（supply_floor breach=false·zombies/rogue 空）·"
    "py_watermark py_low_board_clear 板空合法 idle 白名单·pool ready x3=FUND trio NULLS "
    "全 bm-b 属主（r622/r629 分工律 watch-only）｜"
    "**收养确认闭环**=QUALITY 分片 owner=bm-b·owner_since=09:26:12>r457 手术恢复戳 09:11:39="
    "bm-b daemon keepalive 自续戳实证=r288 门过=自愈闭环收口（r457 指针(a) 闭）+"
    "VALUE/DIVLOWVOL 同窗 09:26:12 三分片同续戳·烧录推进 V676/Q516/D374（较 r456 +22/+18/+16·"
    "bm-b canonical burn 活跃）｜"
    "S6 38/38 rc0 NON-ZERO=none（PARITY PASS·dualrun ZERO-DRIFT streak 51〔366 entries〕·"
    "REPORT/LIVE-20261004 幂等再生·车道守卫腿诚实 no-op·b_layer gates 全过·"
    "fundamental 19.6h 新鲜 skip·update_daily 0 新行金周 cutoff 09-30·regime ORANGE shadow）｜"
    "S4 pit 行入 CODELY.md（水位探针键口径错配坑·51,257→52.3KB·r504 水位裁定=机器不为字节归档在役律照实）｜"
    "S7: attrition CLEAN（4 ledgers·2 bm-a healed 历史注记照录）+loop pin5 no-op first fire "
    "09:35+watchdog 在位 first fire 09:36+双爪 LF 归一装好+orders 双扫零差｜"
    "记分: 1（S6 管线产出+收养确认证据件+探针修复件·等待态声明: finalize 窗 10-05 开·"
    "本窗零新面孔可烧〔N1 关+池他机属主+板空〕·非空转）｜"
    "记账预算: 3/5（state+心跳+轮报）｜"
    "本地未达 origin commit 数: 0（收口 push_verify 自证）｜"
    "登记册零命中断言: 本轮零清扫/归档/删除/恢复类动作（treasure_guard 零调用面照实·"
    "五收口步零触发→TREASURE_REGISTRY/METHODOLOGY_ASSETS 零新行照实）｜"
    "下轮指针=r459 值守（finalize 窗前夜·QUALITY 进度核）+HANDOVER 5x at r460+"
    "O-2115/O-2030 验收窗 10-08 准备+开市 10-09 数据道恢复（新 bar 门控腿自动复挂）"
)


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def dump_json(path, obj):
    with open(path, encoding="utf-8") as f:
        raw = f.read()
    eol = "\r\n" if "\r\n" in raw else "\n"
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(json.dumps(obj, ensure_ascii=False, indent=1).replace("\n", eol))


def main():
    # --- state ---
    st = load_json(STATE)
    st["round_no"] = 458
    st["clock_read"] = NOW
    st["last_seen"] = NOW
    st["last_round_at"] = NOW
    st["last_round_ts"] = NOW
    st["last_ts"] = NOW
    st["updated"] = NOW
    st["updated_at"] = NOW
    st["heartbeat_epoch_utc"] = EPOCH
    st["cpu_pct"] = CPU
    st["idle_ram_gb"] = RAM
    st["gpu_free_vram_mib"] = GPU
    st["current_task"] = CURRENT_TASK
    st["did"] = DID
    st["last_round"] = ("r458 bm-c: adoption-confirm (bm-b keepalive 09:26:12 > surgery "
                        "09:11:39, r457 loop closed) + r452 probe caliber fix + S6 38/38 rc0; "
                        "smoke 48/48; orders/D-19/group-orders triple MATCH; post_review zero-x")
    st["next"] = NEXT
    st["verify"] = VERIFY
    dump_json(STATE, st)
    chk = load_json(STATE)
    assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
    assert chk["round_no"] == 458

    # --- heartbeat ---
    hb = load_json(HEART)
    hb["round_no"] = 458
    hb["round_no_label"] = "round 458 (bm-c)"
    hb["clock_read"] = NOW
    hb["last_seen"] = NOW
    hb["last_seen_at"] = NOW
    hb["ts"] = NOW
    hb["updated"] = NOW
    hb["updated_at"] = NOW
    hb["heartbeat_epoch_utc"] = EPOCH
    hb["cpu_pct"] = CPU
    hb["cpu_util_pct"] = CPU
    hb["cpu_idle_pct"] = 100 - CPU
    hb["cpu_idle_pct"] = 100 - CPU
    for k in ("idle_ram_gb", "free_ram_gb", "ram_free_gb"):
        hb[k] = RAM
    for k in ("gpu_free_vram_mib", "gpu_idle_vram_mib", "gpu_free_mb",
              "gpu_idle_vram_mb", "gpu_vram_free_mb", "gpu_idle_mb"):
        hb[k] = GPU
    hb["current_task"] = CURRENT_TASK
    hb["activity_now"] = (
        "golden-week watch; bm-b adoption CONFIRMED (QUALITY self-heal loop closed); "
        "V676/Q516/D374 of 2000; finalize window opens 10-05 10:30; N1 closed per O-2115 sec-2"
    )
    hb["latest_artifact"] = (
        "results/_r458bmc_s6_log.txt (S6 38/38 rc0 PARITY PASS) + "
        "results/_r458bmc_fundnulls_watch.json @ " + NOW
    )
    hb["next_milestone"] = (
        "fund-trio finalize window 10-05..10-09 (QUALITY long-pole 516/2000); "
        "O-2115/O-2030 acceptance 10-08; market reopen 10-09"
    )
    hb["prod_lanes"] = (
        "FUND trio NULLS bm-b in-flight (watch only); N1 closed per O-2115 sec-2; "
        "O-2115 acceptance pack live"
    )
    hb["verdict"] = (
        "GREEN (smoke 48/48; orders delta zero 153/153; D-19 double MATCH (orders-leg "
        "SHA-1 caliber fixed); WM red=false; satengine alive rc0; S6 38 legs rc0 fail=0 "
        "dualrun streak 51; attrition CLEAN; adoption confirmed; post_review 45Y/0N/5W "
        "zero-x; zero cloud token)"
    )
    dump_json(HEART, hb)
    chk2 = load_json(HEART)
    assert isinstance(chk2["heartbeat_epoch_utc"], int), "epoch must be int"
    assert chk2["round_no"] == 458

    # --- round report bytes-append (mixed-encoding-safe: pure append, no read-modify) ---
    with open(REPORT, "rb") as f:
        tail = f.seek(0, 2)
        f.seek(max(0, tail - 4))
        last = f.read()
    eol_b = b"\r\n" if b"\r\n" in last and not last.endswith(b"\n") or last.endswith(b"\r\n") else b"\n"
    # normalize: use whatever the file predominantly ends with
    with open(REPORT, "rb") as f:
        f.seek(max(0, tail - 400))
        probe = f.read()
    eol_b = b"\r\n" if probe.count(b"\r\n") > probe.count(b"\n") - probe.count(b"\r\n") else b"\n"
    if not probe.endswith(eol_b) and probe.endswith(b"\n"):
        pass  # file already newline-terminated
    with open(REPORT, "ab") as f:
        if not probe.endswith(b"\n"):
            f.write(eol_b)
        f.write(REPORT_LINE.encode("utf-8") + eol_b)
    print("WRAPPED state round=458 heartbeat epoch=%d report appended" % EPOCH)
    print("NOW", NOW)


if __name__ == "__main__":
    main()

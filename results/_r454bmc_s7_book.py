# -*- coding: utf-8 -*-
"""r454 bm-c S7 bookkeeping: state-bm-c.json + heartbeat + round report append.
Programmatic json.dump + json.loads self-check (r645 law), epoch int (R170/R178),
clock T-sep (R262), report bytes-append with EOL detection."""
import datetime
import json
import os
import re
import subprocess
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = datetime.datetime.now().astimezone()
CLOCK = NOW.isoformat(timespec="seconds")  # T-sep with +08:00
EPOCH = int(time.time())

# --- fresh machine metrics ---
try:
    import psutil
    cpu_pct = round(psutil.cpu_percent(interval=1.0), 1)
    ram_free = round(psutil.virtual_memory().available / (1024**3), 1)
except Exception:
    cpu_pct, ram_free = None, None
gpu_free = None
try:
    r = subprocess.run(
        ["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
        capture_output=True, text=True, timeout=15,
        creationflags=0x08000000)
    if r.returncode == 0 and r.stdout.strip():
        gpu_free = int(r.stdout.strip().splitlines()[0])
except Exception:
    pass

DID = ("r454 bm-c golden-week watch round: (1) S0: round-start 4 dirty faces = own "
       "lane daemon faces (treadmill normal); behind=0/ahead=0 zero pull need; "
       "reflog 3-evidence no concurrent session (r453 closed 08:14:02). (2) S0.5 "
       "order diff 0 un-acked (154/154); D-19 decisions EB14B510 MATCH-unchanged "
       "(raw-blob python sha256); group orders.md SHA-1 68947C17 MATCH; inbox 0. "
       "(3) S1 smoke 48/48; S2 boards empty (job_list 0, fleet 0 open/166). (4) S3: "
       "satengine rc0 alive (tick 08:18:01 fresh; local task name "
       "Bigmoney-SaturationEngine, six Bigmoney tasks all present); watchdog "
       "present = r453 re-registration survived, recurrence pattern CLOSED (no 3rd); "
       "watermark red=false next_pick=claimed other-lane; post_review zero new rows; "
       "pool ready x3 = FUND trio NULLS other-owner faces (r622/r629 division law, "
       "watch-only). (5) MAIN OUTPUT: S6 37/37 rc0 NON-ZERO=none, full-leg log "
       "results/_r454bmc_s6_log.txt (PARITY PASS 37 legs==canon via in-driver import "
       "check, canon Tools/_r433bmc_s6.py untouched; dualrun ZERO-DRIFT streak 51; "
       "compute_audit zero flags; REPORT-2026-10-04.md/.json + LIVE-2026-10-04.md "
       "regenerated; 4 faces stale-takeover derive per O-2100 s2.4 STALE_MIN law "
       "[bm-a heartbeat stale 39min]; lane-guard legs honest no-op; lhb incremental "
       "11/11 rc0) -- per-round driver form results/_r454bmc_s6_chain.py. (6) FUND "
       "trio NULLS watch: V646/Q492/D339 of 2000 (delta vs r453 +17/+15/+13 = bm-b "
       "canonical burn actively progressing, finalize window opens 10-05 10:30), "
       "evidence results/_r454bmc_fundnulls_watch.json. (7) S7: loop pin5 no-op "
       "healthy (first fire 08:25); precommit/prepush claws parity TRUE; attrition "
       "CLEAN rc0 (4 ledgers, 2 bm-a healed historical notes); orders double-scan "
       "zero-diff; inbox 0.")
LAST_ROUND = ("r454 bm-c: golden-week watch; S6 37/37 rc0 PARITY PASS "
              "(_r454bmc_s6_log.txt, streak 51); FUND NULLS V646/Q492/D339 +17/+15/+13; "
              "smoke 48/48; orders/D-19/group-orders triple MATCH; watchdog pattern "
              "closed (present, no 3rd recurrence)")
NEXT = ("(a) FUND trio finalize window 10-05..10-09 (D ETA 10-05 10:30 per bm-b r652; "
        "G-SEG frozen insufficient-sample path per O-20261004-0808, no mid-flight "
        "change; VALUE passive crash bm-b fix pending). (b) O-2115 acceptance pack "
        "final run + O-2030 treasure-protection acceptance 10-08. (c) W116+ N1 supply "
        "reassess after fund-trio finalize (reform first-burn supply redirected per "
        "O-0808 ruling-1; 10k cap suspended for candidate-search waves until CEO lifts "
        "D-41 sec.6-C). (d) HANDOVER 5x at r455 (next round, round_no multiple of 5). "
        "(e) Watchdog recurrence pattern CLOSED at r454 (present 2 consecutive "
        "checks). (f) Market reopen 10-09: data lanes resume verification.")
VERIFY = ("S6 37/37 rc0 NON-ZERO=none (results/_r454bmc_s6_log.txt in-repo); smoke "
          "48/48; orders 154/154 double-scan zero-diff; D-19 EB14B510 raw-bytes MATCH; "
          "group orders.md SHA-1 68947C17 MATCH; attrition CLEAN; claws parity TRUE; "
          "fund-nulls evidence results/_r454bmc_fundnulls_watch.json; heartbeat "
          "epoch int + clock T-sep self-checked")
CURRENT_TASK = ("r454 done (S6 37/37 rc0 PARITY PASS; FUND NULLS watch V646/Q492/D352 "
                 "+17/+15/+13 burn progressing; watchdog pattern closed); next: "
                 "HANDOVER 5x at r455, fund-trio finalize window opens 10-05 10:30 "
                 "watchers (G-SEG frozen per O-0808), O-2115+O-2030 acceptance 10-08")

# --- state-bm-c.json ---
sp = os.path.join(ROOT, "state-bm-c.json")
with open(sp, encoding="utf-8") as f:
    st = json.load(f)
st["round_no"] = 454
st["did"] = DID
st["last_round"] = LAST_ROUND
st["next"] = NEXT
st["verify"] = VERIFY
st["current_task"] = CURRENT_TASK
for k in ("clock_read", "last_decisions_read_at", "last_round_at",
          "last_round_ts", "last_seen", "last_ts", "updated", "updated_at"):
    if k in st:
        st[k] = CLOCK
if "heartbeat_epoch_utc" in st:
    st["heartbeat_epoch_utc"] = EPOCH
if cpu_pct is not None:
    st["cpu_pct"] = cpu_pct
if ram_free is not None:
    st["idle_ram_gb"] = ram_free
if gpu_free is not None:
    st["gpu_free_vram_mib"] = gpu_free
with open(sp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
    f.write("\n")
chk = json.loads(open(sp, encoding="utf-8").read())
assert chk["round_no"] == 454
assert isinstance(chk.get("heartbeat_epoch_utc", EPOCH), int)
assert re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+\d{2}:\d{2}$",
                chk["clock_read"])
print("STATE_OK round_no=454 clock=" + chk["clock_read"])

# --- heartbeat fleet/machines/bm-c.json ---
hp = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
with open(hp, encoding="utf-8") as f:
    hb = json.load(f)
hb["clock_read"] = CLOCK
hb["heartbeat_epoch_utc"] = EPOCH
for k in ("last_seen", "last_seen_at", "updated_at"):
    if k in hb:
        hb[k] = CLOCK
hb["round_no"] = 454
hb["current_task"] = CURRENT_TASK
hb["activity_now"] = ("FUND trio NULLS burn watch (bm-b canonical V646/Q492/D352 of "
                      "2000, finalize window opens 10-05 10:30, G-SEG frozen per "
                      "O-20261004-0808); N1 closed per O-2115 sec-2; golden-week "
                      "maintenance all-green; watchdog recurrence pattern closed")
hb["latest_artifact"] = ("results/_r454bmc_s6_log.txt (S6 37/37 rc0 full-leg evidence; "
                         "PARITY PASS) + results/_r454bmc_fundnulls_watch.json @ " + CLOCK)
hb["next_milestone"] = ("FUND trio finalize window 10-05..10-09 (D ETA 10-05 10:30; "
                        "G-SEG frozen per O-0808); O-2115/O-2030 acceptance 10-08; "
                        "market reopen 10-09")
hb["prod_lanes"] = ("FUND trio NULLS bm-b in-flight (watch only); N1 closed per "
                    "O-2115 sec-2 (fund-trio has fire); O-2115 acceptance pack live")
hb["verdict"] = ("green (golden-week maintenance all-green; S6 evidence chain "
                 "continuous; watchdog pattern closed; board/pool/orders lawful; "
                 "lane divisions respected; waiting state declared: finalize window "
                 "opens 10-05)")
if cpu_pct is not None:
    for k in ("cpu_pct", "cpu_util_pct"):
        if k in hb:
            hb[k] = cpu_pct
    hb["cpu_idle_pct"] = round(100.0 - cpu_pct, 1)
if ram_free is not None:
    for k in ("idle_ram_gb", "free_ram_gb", "ram_free_gb"):
        if k in hb:
            hb[k] = ram_free
if gpu_free is not None:
    for k in ("gpu_free_mb", "gpu_free_vram_mb", "gpu_free_vram_mib",
              "gpu_idle_vram_mb", "gpu_idle_vram_mib", "gpu_vram_free_mb"):
        if k in hb:
            hb[k] = gpu_free
with open(hp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
    f.write("\n")
chk2 = json.loads(open(hp, encoding="utf-8").read())
assert isinstance(chk2["heartbeat_epoch_utc"], int), "epoch must be int"
assert re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+\d{2}:\d{2}$",
                chk2["clock_read"]), "clock must be T-sep ISO8601"
print("HEARTBEAT_OK epoch=" + str(chk2["heartbeat_epoch_utc"]) +
      " cpu=" + str(cpu_pct) + " ram_free=" + str(ram_free) +
      " gpu_free=" + str(gpu_free))

# --- round report append (bytes mode, EOL detect) ---
REPORT_LINE = (
    CLOCK + "｜r454｜dept:工程（golden-week 值守·finalize 窗前夜）｜"
    "watermark verdict=绿（red=false·probe py 0.6% 板空合法 idle 白名单〔N1 关闭 per "
    "O-2115 sec-2·池 ready x3 全他机属主·板 0 open〕·satengine rc0 tick 08:18:01 新鲜）｜"
    "当前活=金周值守轮+FUND 三族 NULLS 烧录守望｜"
    "最近实物=results/_r454bmc_s6_log.txt（S6 37/37 rc0·PARITY PASS）+"
    "results/_r454bmc_fundnulls_watch.json｜"
    "下个里程碑=fund-trio finalize 窗 10-05 10:30 开（bm-b 正主）+O-2115/O-2030 验收 "
    "10-08+开市 10-09（≤48h）｜"
    "S0: 轮首 4 脏面=本机 lane daemon faces（treadmill 正常）·fetch behind=0/ahead=0"
    "（r453 closeout 已同步零拉取需求）·reflog 三证无并发会话（r453 尾 08:14:02 收口）｜"
    "S0.5 令差集=0（154/154 双扫零未回执）·D-19 EB14B510 MATCH-unchanged（raw-blob 法）·"
    "group orders.md SHA-1 68947C17 MATCH·inbox 0｜"
    "S1 smoke 48/48｜S2 板空（job_list 0·fleet tickets 0 open/166）｜"
    "S3: satengine rc0 活（本机任务名 Bigmoney-SaturationEngine·六任务全在位）·"
    "watchdog 在位=r453 重注册存活·复发 pattern 闭案（无第 3 次）·post_review 零新行·"
    "watermark red=false next_pick=claimed moneyflow IC 他机道·pool ready x3=FUND trio "
    "NULLS 他机属主面（r622/r629 分工律 watch-only）｜"
    "S6 37/37 rc0 NON-ZERO=none（PARITY PASS 37 legs==canon〔import 平权自检入驱动件〕·"
    "dualrun ZERO-DRIFT streak 51·compute_audit 零旗·REPORT-2026-10-04.md/.json+"
    "LIVE-2026-10-04.md 再生·4 面 stale-takeover derive〔bm-a 心跳陈 39min·O-2100 "
    "s2.4〕·车道守卫腿诚实 no-op·lhb 增量 11/11 rc0）｜"
    "FUND NULLS watch: V646/Q492/D352 of 2000（较 r453 +17/+15/+13·bm-b canonical burn "
    "活跃推进·finalize 窗明日 10:30 开·证据 results/_r454bmc_fundnulls_watch.json）｜"
    "S7: loop pin5 no-op 健康（first fire 08:25）·双爪 parity TRUE·attrition CLEAN"
    "（4 ledgers）·orders 双扫零差·inbox 0｜"
    "记分: 1（S6 管线产出+watch 证据件·等待态声明: finalize 窗 10-05 开·本窗零新面孔可烧"
    "〔N1 关+池他机属主+板空〕·非空转）｜记账预算: 3/5（state+心跳+轮报）｜"
    "本地未达 origin commit 数: 0（push_verify 收口自证）｜"
    "登记册零命中断言: 本轮零清扫/归档/删除/恢复类动作（treasure_guard 零调用面照实·"
    "五收口步零触发→TREASURE_REGISTRY/METHODOLOGY_ASSETS 零新行照实）｜"
    "下轮指针=r455 HANDOVER 5x 产物清单核对（轮号 5 倍数）+finalize 窗开板观察+"
    "watchdog pattern 已闭案")
rp = os.path.join(ROOT, "round_reports-bm-c.md")
with open(rp, "rb") as f:
    raw = f.read()
eol = b"\r\n" if b"\r\n" in raw[-400:] else b"\n"
addition = REPORT_LINE.encode("utf-8") + eol
if not raw.endswith(b"\n"):
    addition = eol + addition
with open(rp, "ab") as f:
    f.write(addition)
with open(rp, "rb") as f:
    back = f.read()
assert REPORT_LINE.encode("utf-8") in back, "report line not found after append"
print("REPORT_OK bytes=" + str(len(addition)) + " eol=" + repr(eol))

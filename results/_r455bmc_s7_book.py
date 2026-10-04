# -*- coding: utf-8 -*-
"""r455 bm-c S7 bookkeeping: state-bm-c.json + heartbeat + round report append.
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

DID = ("r455 bm-c golden-week watch + HANDOVER 5x round: (1) S0: fetch behind=9 "
       "(bm-b r657 wave, 4 merge commits + absorbs) -> own 2 dirty faces (satengine "
       "daemon) intersection EMPTY vs origin change-set -> absorb 4a3db883d + merge "
       "origin/main ort CLEAN 0 UU. (2) S0.5 orders diff 0 un-acked (153/153 "
       "double-scan); D-19 decisions EB14B510 MATCH-unchanged (raw-blob sha256); "
       "group orders.md SHA-1 68947C17 MATCH; inbox 0. (3) S1 smoke 48/48; S2 "
       "boards empty (job_list 0, fleet 0 open/166). (4) S3: satengine rc0 alive; "
       "watermark red=false next_pick=claimed other-lane (moneyflow IC, bm-a lane); "
       "post_review 45 YES/0 NO/5 WAIT zero new x rows; pool ready x3 = FUND trio "
       "NULLS other-owner faces (r622/r629 division law, watch-only). (5) MAIN "
       "OUTPUT: S6 canon upgrade 37->38 legs (Tools/_r433bmc_s6.py + update_fund_"
       "statements leg per T-2026-10-04-166-P1 prompt wiring, position after "
       "b_layer_filter; lane guard bm-c honest no-op rc0 live-proven) + S6 38/38 "
       "rc0 NON-ZERO=none (PARITY PASS 38 legs==canon in-driver import check; "
       "dualrun ZERO-DRIFT streak 51; compute_audit zero flags; REPORT/LIVE-"
       "2026-10-04 regenerated; C-family lane guards honest skip [bm-a heartbeat "
       "fresh 17min]; lhb 30min-throttle no-op) -- driver results/_r455bmc_s6_"
       "chain.py, full log results/_r455bmc_s6_log.txt. (6) FUND trio NULLS "
       "watch: V654/Q498/D358 of 2000 (delta vs r454 +8/+6/+6 = bm-b canonical "
       "burn progressing), evidence results/_r455bmc_fundnulls_watch.json. (7) "
       "HANDOVER 5x entry landed (r451-455 window, canon-upgrade + watch lineage). "
       "(8) S7: loop pin5 no-op healthy (first fire 08:45); watchdog re-registered "
       "idempotent rc0 (task present, next fire 08:42); precommit/prepush claws "
       "parity TRUE (re-installed idempotent); attrition CLEAN rc0 (4 ledgers, 2 "
       "bm-a healed historical notes); orders double-scan zero-diff; inbox 0.")
LAST_ROUND = ("r455 bm-c: golden-week watch + HANDOVER 5x; S6 canon 37->38 legs "
              "(update_fund_statements per T-166 wiring) + 38/38 rc0 PARITY PASS "
              "(_r455bmc_s6_log.txt, streak 51); FUND NULLS V654/Q498/D358 "
              "+8/+6/+6; smoke 48/48; orders/D-19/group-orders triple MATCH")
NEXT = ("(a) FUND trio finalize window 10-05..10-09 (D ETA 10-05 10:30 per bm-b "
        "r652; G-SEG frozen insufficient-sample path per O-20261004-0808, no "
        "mid-flight change; VALUE passive crash bm-b fix pending). (b) O-2115 "
        "acceptance pack final run + O-2030 treasure-protection acceptance 10-08. "
        "(c) W116+ N1 supply reassess after fund-trio finalize (reform first-burn "
        "supply redirected per O-0808 ruling-1; 10k cap suspended for "
        "candidate-search waves until CEO lifts D-41 sec.6-C). (d) Market reopen "
        "10-09: data lanes resume verification (S6 new-bar legs auto-reengage). "
        "(e) Next HANDOVER 5x at r460.")
VERIFY = ("S6 38/38 rc0 NON-ZERO=none (results/_r455bmc_s6_log.txt in-repo; canon "
          "parity PASS 38 legs); smoke 48/48; orders 153/153 double-scan "
          "zero-diff; D-19 EB14B510 raw-bytes MATCH; group orders.md SHA-1 "
          "68947C17 MATCH; attrition CLEAN; claws parity TRUE; HANDOVER r455 "
          "entry landed; fund-nulls evidence results/_r455bmc_fundnulls_watch.json; "
          "heartbeat epoch int + clock T-sep self-checked")
CURRENT_TASK = ("r455 done (S6 canon 37->38 legs upgrade + 38/38 rc0; HANDOVER 5x "
                "landed; FUND NULLS watch V654/Q498/D358 burn progressing); next: "
                "fund-trio finalize window opens 10-05 10:30 watchers (G-SEG "
                "frozen per O-0808), O-2115+O-2030 acceptance 10-08, market "
                "reopen 10-09")

# --- state-bm-c.json ---
sp = os.path.join(ROOT, "state-bm-c.json")
with open(sp, encoding="utf-8") as f:
    st = json.load(f)
st["round_no"] = 455
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
assert chk["round_no"] == 455
assert isinstance(chk.get("heartbeat_epoch_utc", EPOCH), int)
assert re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+\d{2}:\d{2}$",
                chk["clock_read"])
print("STATE_OK round_no=455 clock=" + chk["clock_read"])

# --- heartbeat fleet/machines/bm-c.json ---
hp = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
with open(hp, encoding="utf-8") as f:
    hb = json.load(f)
hb["clock_read"] = CLOCK
hb["heartbeat_epoch_utc"] = EPOCH
for k in ("last_seen", "last_seen_at", "updated_at"):
    if k in hb:
        hb[k] = CLOCK
hb["round_no"] = 455
hb["current_task"] = CURRENT_TASK
hb["activity_now"] = ("FUND trio NULLS burn watch (bm-b canonical V654/Q498/D358 "
                      "of 2000, finalize window opens 10-05 10:30, G-SEG frozen per "
                      "O-20261004-0808); N1 closed per O-2115 sec-2; golden-week "
                      "maintenance all-green; S6 canon upgraded to 38 legs")
hb["latest_artifact"] = ("results/_r455bmc_s6_log.txt (S6 38/38 rc0 full-leg "
                         "evidence; PARITY PASS 38 legs) + results/"
                         "_r455bmc_fundnulls_watch.json @ " + CLOCK)
hb["next_milestone"] = ("FUND trio finalize window 10-05..10-09 (D ETA 10-05 "
                        "10:30; G-SEG frozen per O-0808); O-2115/O-2030 "
                        "acceptance 10-08; market reopen 10-09")
hb["prod_lanes"] = ("FUND trio NULLS bm-b in-flight (watch only); N1 closed per "
                    "O-2115 sec-2 (fund-trio has fire); O-2115 acceptance pack live")
hb["verdict"] = ("green (golden-week maintenance all-green; S6 evidence chain "
                 "continuous at 38 legs; board/pool/orders lawful; lane divisions "
                 "respected; waiting state declared: finalize window opens 10-05)")
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
    CLOCK + "｜r455｜dept:工程（golden-week 值守·HANDOVER 5x 义务轮）｜"
    "watermark verdict=绿（red=false·probe py 0.0% 板空合法 idle 白名单〔N1 关闭 per "
    "O-2115 sec-2·池 ready x3 全他机属主·板 0 open〕·satengine rc0 活）｜"
    "当前活=金周值守+S6 canon 38 腿升级+HANDOVER 5x 核对｜"
    "最近实物=results/_r455bmc_s6_log.txt（S6 38/38 rc0·PARITY PASS）+"
    "results/_r455bmc_fundnulls_watch.json+Tools/_r433bmc_s6.py（canon 升级）｜"
    "下个里程碑=fund-trio finalize 窗 10-05 10:30 开（bm-b 正主·G-SEG 冻结 per O-0808）+"
    "O-2115/O-2030 验收 10-08+开市 10-09（≤48h）｜"
    "S0: fetch behind=9（bm-b r657 wave·4 merge commits+absorbs）→本机 2 脏面（satengine "
    "daemon）与 origin 改动集交集空→absorb 4a3db883d+merge origin/main ort 干净零 UU｜"
    "S0.5 令差集=0（153/153 双扫零未回执）·D-19 EB14B510 MATCH-unchanged（raw-blob 法）·"
    "group orders.md SHA-1 68947C17 MATCH·inbox 0｜"
    "S1 smoke 48/48｜S2 板空（job_list 0·fleet tickets 0 open/166）｜"
    "S3: satengine rc0 活·watermark red=false next_pick=claimed 他机道（moneyflow IC·bm-a "
    "lane）·post_review 45✓/0✗/WAIT 5 零新✗行·pool ready x3=FUND trio NULLS 他机属主面"
    "（r622/r629 分工律 watch-only）｜"
    "S6 38/38 rc0 NON-ZERO=none（**canon 37→38 腿升级**：update_fund_statements 腿入列 per "
    "T-2026-10-04-166-P1 prompt 接线·位=b_layer_filter 后·车道护栏 bm-c 面 stdout-only "
    "诚实 no-op 实证 rc0·PARITY PASS 38 legs==canon〔canon 与驱动件同窗升级〕·dualrun "
    "ZERO-DRIFT streak 51·compute_audit 零旗·REPORT-2026-10-04.md/.json+LIVE-2026-10-04.md "
    "再生·C 族守卫面=bm-a 心跳新鲜 17min 诚实 skip·lhb 30min 节流 no-op）｜"
    "FUND NULLS watch: V654/Q498/D358 of 2000（较 r454 +8/+6/+6·bm-b canonical burn 推进·"
    "finalize 窗明日 10:30 开·证据 results/_r455bmc_fundnulls_watch.json）｜"
    "HANDOVER 5x: r455 条目落盘（增量窗 r451-455·canon 升级+金周值守+GM O-0808 双裁令消费 "
    "lineage）｜"
    "S7: loop pin5 no-op 健康（first fire 08:45）·watchdog 幂等重注册 rc0（任务在位·next "
    "08:42）·双爪重装 parity TRUE·attrition CLEAN（4 ledgers）·orders 双扫零差·inbox 0｜"
    "记分: 1（S6 管线产出+canon 升级+watch 证据件+HANDOVER 5x·等待态声明: finalize 窗 "
    "10-05 开·本窗零新面孔可烧〔N1 关+池他机属主+板空〕·非空转）｜记账预算: 3/5"
    "（state+心跳+轮报）｜"
    "本地未达 origin commit 数: 0（push_verify 收口自证）｜"
    "登记册零命中断言: 本轮零清扫/归档/删除/恢复类动作（treasure_guard 零调用面照实·"
    "五收口步零触发→TREASURE_REGISTRY/METHODOLOGY_ASSETS 零新行照实）｜"
    "下轮指针=finalize 窗开板观察+O-2115/O-2030 验收窗 10-08 准备+开市 10-09 数据道恢复"
    "（新 bar 门控腿自动复挂）+下一 5x=r460")
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

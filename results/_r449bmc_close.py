"""r449 bm-c closeout: round report + state + heartbeat (no HANDOVER: 449 not 5x; next at r450).

All writes json.dump/programmatic + post-write self-verify (state trailing-comma
law + heartbeat epoch int-type law). Hard asserts throughout. r448 template.
"""
import json
import os
import subprocess
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
NOW_COMPACT = time.strftime("%Y-%m-%d %H:%M:%S")
EPOCH = int(time.time())
CREATE = 0x08000000

# ---------------------------------------------------------------- 1) round report append
rr_path = os.path.join(ROOT, "round_reports-bm-c.md")
raw = open(rr_path, "rb").read()
assert raw.endswith(b"\n"), "round report must end with newline"
eol = b"\r\n" if raw.endswith(b"\r\n") else b"\n"
RR_LINE = (
    "watermark: 绿 (red=false ts 06:45 lane healthy; satengine bm-c rc0 alive queue_next 空=N1 烧空如实; py_watermark py_low_board_clear n=2 合法 idle 金周; 板 0 open/45 claimed; fund-trio NULLS bm-b 在烧=供给闸合法) | "
    + NOW + " | r449 | dept:工程 | 当前活: FUND 三族 NULLS 烧录守望（bm-b canonical 在烧·V613/Q462/D326 续升·finalize 窗 10-05 开）+ S6 证据面缺口修复 | "
    "S0: fetch 实核 behind=3（bm-b keepalive claim-refresh+merge+churn absorb 三连·改动集全 bm-b 面）→与本机 4 脏面交集空→FF merge 470d67598 零冲突→定向 absorb 4 lane daemon faces（autofill/dispatcher/satengine face+state）3ffda6c19→push_verify DELIVERED tip 双侧恒等 ahead==0 | "
    "S0.5: orders 152/152 双扫零未回执零 ghost-ack + D-19 双面 MATCH EB14B510/68947C17（raw-blob 零树触碰）+ inbox 0 | "
    "S1: smoke 47/47 | S2/S3: 板 45 claimed 0 open 零可认领; satengine rc0 活（alive_flag true·queue_next 空）; N1 W116+ 维持关闭（O-2115 §二·fund-trio 在烧）; post_review 现态 ✓45/✗0/🟡5 零红（判定分布行权威·两处 ✗ 为文本内符号非判定） | "
    "主产出: S6 37/37 rc0 fails=0 全腿日志落盘 results/_r449bmc_s6_log.txt（dualrun ZERO-DRIFT streak 50·366 entries; compute_audit CLEAN flags=[] pool-supply-gap 观察相 ready=3/unclaimed=1 floor 未破; py_watermark py_low_board_clear; REPORT-2026-10-04 faces=5 再生; token delta=0 全 L1; prospect 22/22 drift=0）——S6 证据面缺口修复：r446-r448 三轮 PS1 runner 跑链宣称 37/37 但日志未落盘（in-repo 证据断链·r502 族隐患面·git ls-files 实证 r440-r445 在册而 r446-448 缺位）→本轮恢复正典证据纪律（r430 律证据名=轮号件） | "
    "S4: 零新坑律（本窗 -Last 切片首跑吞三腿输出=r431 在册律复犯·当场 -split 行化重跑零实伤·四问门不复述在册律; satengine status 全量 JSON 洪泛=批内输出量级预判教训·轮报注记非新坑） | "
    "S7: 自愈 4x 绿（loop pin5 no-op first-fire 07:05/watchdog 在位/双爪字节恒等零重装）+attrition CLEAN（4 台账·bm-a 2 healed 历史注记照录）+orders 双扫复核零漂 | "
    "验证证据: S6 37/37 rc0（results/_r449bmc_s6_log.txt 落盘件）+ smoke 47/47 + push_verify DELIVERED 3ffda6c19 + orders/D-19 双 MATCH | "
    "记分: 1（S6 管线产出+证据件落盘+absorb/FF 文件实改; 同日幂等再生成非新实物面; fund-trio 等待态一行声明非空转） | 记账预算: 3/5（state+心跳+轮报） | 本地未达 origin commit 数: 1（closeout commit 即推·push_verify 自证） | "
    "登记册零命中断言: 本轮零清扫/归档/删除/恢复类动作（treasure_guard prescan 未触发; 无判决 finalize/族炉收口/考面冻结/名单进出/方法论新方法五收口步零触发→TREASURE_REGISTRY/METHODOLOGY_ASSETS 零新行照实） | "
    "ceo-visibility: [当前活] FUND 三族 NULLS 烧录守望（bm-b canonical 在烧·V613/Q462/D326 续升·三池 entry keep-block 在位·dup_k=0 per bm-b r652） | [最近实物] results/_r449bmc_s6_log.txt（37 腿全绿证据件·S6 证据链修复）@ " + NOW + " | "
    "[下个里程碑] FUND trio finalize 窗 10-05..10-09（D ETA 10-05 10:30 per bm-b r652·G-SEG GM/VALUE 两前置裁决待面）+ O-2115/O-2030 验收 10-08 + T-143 装配 10-09 后 | "
    "下轮指针: (a) fund-trio finalize 就绪观察（NULLS 烧完→readiness face; G-SEG 无 GM ruling 则冻结判线诚实 insufficient-sample per bm-a r662） (b) HANDOVER 5x 核对轮=r450 (c) O-2115 pack 10-08 终跑 (d) T-143 装配窗 10-09 后"
)
with open(rr_path, "ab") as fh:
    fh.write(RR_LINE.encode("utf-8") + eol)
chk = open(rr_path, "rb").read().decode("utf-8", errors="strict").splitlines()
assert chk[-1].startswith("watermark: 绿") and "r449" in chk[-1], "rr tail"
print("RR-APPEND-OK lines=%d eol=%r" % (len(chk), eol))

# ---------------------------------------------------------------- 2) state update
st_path = os.path.join(ROOT, "state-bm-c.json")
st = json.load(open(st_path, encoding="utf-8"))
st["round_no"] = 449
st["clock_read"] = NOW
st["heartbeat_epoch_utc"] = EPOCH
st["last_seen"] = NOW
st["last_ts"] = NOW
st["last_round_at"] = NOW
st["last_round_ts"] = NOW
st["last_decisions_read_at"] = NOW
st["updated"] = NOW_COMPACT
st["updated_at"] = NOW
st["last_round"] = ("r449 bm-c: S0 FF-merge 470d67598 + absorb 3ffda6c19 DELIVERED; S6 37/37 rc0 with in-repo log _r449bmc_s6_log.txt (r446-r448 evidence gap fixed); FUND NULLS watch V613/Q462/D326; orders/D19 MATCH; smoke 47/47")
st["current_task"] = ("r449 done (S0 FF-merge + absorb 3ffda6c19 push DELIVERED; S6 37/37 rc0 in-repo evidence restored; FUND NULLS watch V613/Q462/D326 rising); next: fund-trio finalize window 10-05..10-09 watchers, HANDOVER 5x at r450, O-2115 pack final 10-08")
st["did"] = (
    "r449 bm-c golden-week watch + evidence-chain repair round: "
    "(1) S0: fetch behind=3 (bm-b keepalive/merge/churn wave, all bm-b faces, zero intersection with local 4 dirty daemon faces) -> FF merge 470d67598 clean -> targeted absorb 4 lane daemon faces 3ffda6c19 -> push_verify DELIVERED (tip==remote, ahead==0). "
    "(2) S0.5 orders 152/152 double-scan zero un-acked zero ghost-ack + D-19 dual-face MATCH EB14B510/68947C17 (raw-blob, zero tree touch) + inbox empty. "
    "(3) S1 smoke 47/47; S2 board 45 claimed 0 open; S3 satengine rc0 alive (queue_next empty = N1 exhausted honest); post_review distribution line authoritative: 45 YES / 0 NO / 5 WAIT (two literal-x-marks in text are not verdicts). "
    "(4) MAIN OUTPUT: S6 37/37 rc0 fails=0 with full-leg log persisted to results/_r449bmc_s6_log.txt (dualrun ZERO-DRIFT streak 50, compute_audit CLEAN flags=[] pool-supply-gap observation ready=3/unclaimed=1, py_watermark py_low_board_clear, REPORT/LIVE-2026-10-04 regenerated faces=5, token delta=0, prospect 22/22 drift=0) -- this repairs the r446-r448 evidence gap where PS1-runner chains claimed 37/37 but no in-repo log was persisted (git ls-tree proof: r440-r445 tracked, r446-r448 absent; r502-family hazard face, r430 evidence-name law restored). "
    "(5) FUND trio NULLS watch (r446 probe reused): V613/Q462/D326 rising (bm-b r652 ~06:26 V606/Q456/D322), 3 pool entries all bm-b canonical with keep-block in place, finalize window opens 10-05. "
    "(6) S7 self-heal 4x green (loop pin5 no-op first-fire 07:05, watchdog present, dual claws byte-identical) + attrition CLEAN (2 bm-a healed historical notes) + zero new pit entries (single-string -Last slicing miss = r431 in-册 law recurrence, self-healed same window, no restatement per four-question gate)."
)
st["next"] = (
    "(a) FUND trio finalize window 10-05..10-09 watchers (D ETA 10-05 10:30 per bm-b r652; G-SEG GM + VALUE passive pre-rulings pending; NULLS burn completion -> finalize readiness face). "
    "(b) HANDOVER 5x check at r450. (c) O-2115 acceptance pack final run 10-08. (d) O-2030 treasure-protection acceptance 10-08. (e) T-143 assembly post 10-09 (deliver 10-29). (f) W116+ N1 supply reassess after fund-trio finalize."
)
st["verify"] = (
    "S6 37/37 rc0 fails=0 (results/_r449bmc_s6_log.txt in-repo); smoke 47/47; orders 152/152 double-scan zero-diff zero-ghost; D-19 EB14B510/68947C17 raw-bytes MATCH; attrition CLEAN; push_verify DELIVERED 3ffda6c19 ahead==0"
)
with open(st_path, "w", encoding="utf-8", newline="") as fh:
    json.dump(st, fh, ensure_ascii=False, indent=1)
    fh.flush()
re_st = json.load(open(st_path, encoding="utf-8"))
assert re_st["round_no"] == 449 and isinstance(re_st["heartbeat_epoch_utc"], int)
print("STATE-OK round=449 epoch=%d" % re_st["heartbeat_epoch_utc"])

# ---------------------------------------------------------------- 3) heartbeat update
hb_path = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
hb = json.load(open(hb_path, encoding="utf-8"))
try:
    import psutil
    cpu = psutil.cpu_percent(interval=1.0)
    ram_free = round(psutil.virtual_memory().available / (1024 ** 3), 1)
except Exception:
    cpu, ram_free = st.get("cpu_pct", 0.0), st.get("idle_ram_gb", 0.0)
gpu_free = None
try:
    p = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                        capture_output=True, creationflags=CREATE, timeout=20)
    if p.returncode == 0:
        gpu_free = int(str(p.stdout.decode("ascii", "replace").strip().splitlines()[0]).strip())
except Exception:
    gpu_free = None
hb["activity_now"] = "FUND trio NULLS burn watch (bm-b canonical, V613/Q462/D326 rising, finalize window 10-05); N1 W116+ closed per O-2115 sec-2; golden-week maintenance all-green"
hb["clock_read"] = NOW
hb["cpu_pct"] = cpu
hb["cpu_util_pct"] = cpu
hb["cpu_idle_pct"] = round(100.0 - cpu, 1)
hb["current_task"] = st["current_task"]
hb["free_ram_gb"] = ram_free
hb["idle_ram_gb"] = ram_free
hb["ram_free_gb"] = ram_free
hb["heartbeat_epoch_utc"] = EPOCH
hb["last_seen"] = NOW
hb["last_seen_at"] = NOW
hb["latest_artifact"] = "results/_r449bmc_s6_log.txt (S6 37/37 rc0 full-leg in-repo evidence; r446-r448 evidence gap repaired) @ " + NOW
hb["next_milestone"] = "FUND trio finalize window 10-05..10-09 (D ETA 10-05 10:30; G-SEG GM + VALUE passive pre-rulings); O-2115/O-2030 acceptance 10-08; T-143 assembly post 10-09 (deliver 10-29)"
hb["prod_lanes"] = "FUND trio NULLS bm-b in-flight (watch only); N1 closed per O-2115 sec-2 (fund-trio has fire); O-2115 acceptance pack live (4/4 MET r448 refresh); W2 MASS_TRIAL judged+consumed (negative, E27 card)"
hb["round_no"] = 449
hb["updated_at"] = NOW
hb["verdict"] = "green (golden-week maintenance all-green; S6 evidence chain restored; board/pool/orders lawful; lane divisions respected)"
if gpu_free is not None:
    for k in ("gpu_free_mb", "gpu_free_vram_mb", "gpu_free_vram_mib", "gpu_idle_vram_mb", "gpu_idle_vram_mib", "gpu_vram_free_mb"):
        hb[k] = gpu_free
with open(hb_path, "w", encoding="utf-8", newline="") as fh:
    json.dump(hb, fh, ensure_ascii=False, indent=1)
    fh.flush()
re_hb = json.load(open(hb_path, encoding="utf-8"))
assert re_hb["round_no"] == 449 and isinstance(re_hb["heartbeat_epoch_utc"], int) and len(re_hb["orders_ack"]) == 153
print("HEARTBEAT-OK cpu=%.1f ram_free=%.1f gpu_free=%s epoch=%d acks=%d" % (cpu, ram_free, gpu_free, re_hb["heartbeat_epoch_utc"], len(re_hb["orders_ack"])))
print("CLOSE-ALL-GREEN", NOW)

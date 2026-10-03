"""r451 bm-c closeout: round report + state + heartbeat (golden-week watch round).

r450 template minus the HANDOVER 5x leg (next 5x = r455). All writes
json.dump/programmatic + post-write self-verify (state trailing-comma law r645
+ heartbeat epoch int-type law R170/R178). Hard asserts throughout.
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
    "watermark: 绿 (red=false ts 07:25 lane healthy; satengine bm-c rc0 alive; py_watermark py_low_board_clear 金周合法 idle; 板 0 open/45 claimed; fund-trio NULLS bm-b canonical 在烧=供给闸合法) | "
    + NOW + " | r451 | dept:工程 | 当前活: 金周值守轮 + FUND 三族 NULLS 烧录守望（V623/Q471/D335 续升·07:16 三族同窗新鲜·finalize 窗明日 10-05 10:30 开）+ S6 正典证据链续作 | "
    "S0: fetch 实核 behind=0（origin==HEAD 零拉取需求）; 轮首 4 脏面=bm-c 自有 lane daemon faces（autofill/dispatcher/satengine×2·treadmill 正常态）| "
    "S0.5: orders 152/152 首扫零未回执（Tools/orders_diff.py 正典件 v2 list 口径）+ D-19 MATCH EB14B510（decisions 水位不变零消费）+ inbox 0 | "
    "S1: smoke 47/47 | S2/S3: job_list 空+板 0 open 零可认领; satengine rc0 活（Tools\\saturation_engine.py status）; watermark red=false next_pick=claimed moneyflow IC 他机道; post_review ✓45/✗0/🟡5 维持（零新红）; N1 W116+ 维持关闭（O-2115 §二·fund-trio 占火力）; 池 ready×3=FUND 三族 NULLS 他机属主面（r622/r629 分工律 watch-only） | "
    "主产出: S6 37/37 rc0 NON-ZERO=none 全腿日志落盘 results/_r451bmc_s6_log.txt（dualrun ZERO-DRIFT streak 51·366 entries; compute_audit 零旗 floor ready3/3 无 breach; py_watermark py_low_board_clear; REPORT/LIVE-2026-10-04 faces 再生; 4 面 stale-takeover derive per O-2100 s2.4 STALE_MIN 律〔bm-a 心跳陈 68min·daily_scorecard/dashboard_status/paper_export/t35_fill_verify〕）——per-round 驱动件形态（results/_r451bmc_s6_chain.py·正典 Tools 驱动零触碰·零 adapt/restore 手术·r442-448 lineage）| "
    "FUND watch: V623/Q471/D335（较 r450 +5/+4/+5; 三族 nulls.jsonl 07:16 同窗新鲜; cells 401x2 逐族〔VALUE 双因子 1604〕+sens 500x3 全落地; 证据 results/_r451bmc_fundnulls_watch.json）| "
    "S7: 自愈 4x 绿（loop pin5 no-op first-fire 07:35/watchdog 在位 07:31/双爪 LF 归一字节恒等零差异）+attrition CLEAN rc0（4 台账·bm-a 2 healed 历史注记照录）+orders S7 双扫复核 | "
    "验证证据: results/_r451bmc_s6_log.txt（37 腿逐 rc）+ smoke 47/47 + orders/D-19 MATCH + watch JSON 落盘 | "
    "记分: 1（S6 管线产出+watch 证据件; 等待态轮一行声明: finalize 窗 10-05 开·本窗零新面孔可烧〔N1 关+池=FUND 他机属主+板空〕·非空转） | 记账预算: 3/5（state+心跳+轮报） | 本地未达 origin commit 数: 1（closeout commit 即推·push_verify 自证·若撞拒按 r449/r450 配方 merge 收尾） | "
    "登记册零命中断言: 本轮零清扫/归档/删除类动作（无 restore/重落/池面恢复类动作→treasure_guard 零调用面照实; 五收口步〔判决 finalize/族炉收口/考面冻结/名单进出/方法论新方法〕零触发→TREASURE_REGISTRY/METHODOLOGY_ASSETS 零新行照实） | "
    "ceo-visibility: [当前活] 金周值守+FUND 三族 NULLS 判决批烧录守候（bm-b canonical 623/471/335 of 2000） | [最近实物] results/_r451bmc_s6_log.txt（07:28·37/37 rc0）+LIVE-2026-10-04.md 再生 @ " + NOW + " | "
    "[下个里程碑] FUND 三族 finalize 窗 10-05 开（D ETA 10:30 per bm-b r652）+O-2115/O-2030 验收 10-08+开市 10-09 数据面恢复 | "
    "下轮指针: (a) fund-trio finalize 就绪观察（readiness probe bm-b r651/654 在册禁重建; G-SEG 无 GM ruling=冻结判线 insufficient-sample per bm-a r662; VALUE passive crash bm-b 修复面） (b) O-2115 pack 终跑+O-2030 验收 10-08 (c) W116+ N1 供给重估候 finalize (d) HANDOVER 5x r455 (e) 开市 10-09 数据面恢复核验"
)
with open(rr_path, "ab") as fh:
    fh.write(RR_LINE.encode("utf-8") + eol)
chk = open(rr_path, "rb").read().decode("utf-8", errors="strict").splitlines()
assert chk[-1].startswith("watermark: 绿") and "r451" in chk[-1], "rr tail"
print("RR-APPEND-OK lines=%d eol=%r" % (len(chk), eol))

# ---------------------------------------------------------------- 2) state update
st_path = os.path.join(ROOT, "state-bm-c.json")
st = json.load(open(st_path, encoding="utf-8"))
st["round_no"] = 451
st["clock_read"] = NOW
st["heartbeat_epoch_utc"] = EPOCH
st["last_seen"] = NOW
st["last_ts"] = NOW
st["last_round_at"] = NOW
st["last_round_ts"] = NOW
st["last_decisions_read_at"] = NOW
st["updated"] = NOW_COMPACT
st["updated_at"] = NOW
st["last_round"] = ("r451 bm-c: golden-week watch round: S6 37/37 rc0 _r451bmc_s6_log.txt (streak 51, per-round driver form, canon untouched); FUND NULLS watch V623/Q471/D335 (+5/+4/+5); orders/D19 MATCH; smoke 47/47; 4 stale-takeover derives per O-2100 s2.4")
st["current_task"] = ("r451 done (S6 37/37 rc0 per-round driver; FUND NULLS watch V623/Q471/D335; zero board/pool claimable, N1 closed per O-2115 sec-2); next: fund-trio finalize window opens 10-05 10:30 watchers, O-2115+O-2030 acceptance 10-08, HANDOVER 5x at r455")
st["did"] = (
    "r451 bm-c golden-week watch round: "
    "(1) S0: fetch behind=0 (origin==HEAD, no pull needed); round-start 4 dirty faces = bm-c own lane daemon faces (treadmill normal). "
    "(2) S0.5 orders 152/152 first scan zero un-acked via canonical Tools/orders_diff.py + D-19 MATCH EB14B510 (decisions watermark unchanged, zero consumption) + inbox empty. "
    "(3) S1 smoke 47/47; S2 boards: job_list empty + fleet tickets 0 open (45 claimed); S3 satengine rc0 alive; watermark red=false next_pick=claimed moneyflow-IC other-lane; post_review 45 YES/0 NO/5 WAIT (zero new red); N1 W116+ held closed per O-2115 sec-2; pool ready x3 = FUND trio NULLS other-machine-owner faces (r622/r629 division law, watch-only). "
    "(4) MAIN OUTPUT: S6 37/37 rc0 NON-ZERO=none with full-leg log persisted to results/_r451bmc_s6_log.txt (dualrun ZERO-DRIFT streak 51; compute_audit zero flags, floor 3/3 no breach; py_watermark py_low_board_clear legal idle; REPORT/LIVE-2026-10-04 faces regenerated; 4 stale-takeover derives per O-2100 s2.4 STALE_MIN law, bm-a heartbeat stale 68min) -- per-round driver form results/_r451bmc_s6_chain.py, canon Tools driver untouched, zero adapt/restore surgery. "
    "(5) FUND trio NULLS watch: V623/Q471/D335 of 2000 (+5/+4/+5 vs r450), three nulls.jsonl same-window fresh 07:16, cells 401x2 per family (VALUE dual-factor 1604) + sens 500x3 all landed; evidence results/_r451bmc_fundnulls_watch.json (read-only probe _r451bmc_fundnulls_watch.py). "
    "(6) S7 self-heal 4x green (loop pin5 no-op first-fire 07:35, watchdog present 07:31, dual claws byte-identical CR-normalized) + attrition CLEAN (4 ledgers, 2 bm-a healed historical notes) + S7 orders second scan."
)
st["next"] = (
    "(a) FUND trio finalize window 10-05..10-09 watchers (D ETA 10-05 10:30 per bm-b r652; readiness probe bm-b r651/654 in-register do-not-rebuild; G-SEG GM ruling + VALUE passive crash bm-b fix pending). "
    "(b) O-2115 acceptance pack final run + O-2030 treasure-protection acceptance 10-08. (c) W116+ N1 supply reassess after fund-trio finalize. (d) HANDOVER 5x at r455. (e) Market reopen 10-09: data lanes resume verification."
)
st["verify"] = (
    "S6 37/37 rc0 NON-ZERO=none (results/_r451bmc_s6_log.txt in-repo); smoke 47/47; orders 152/152 double-scan zero-diff; D-19 EB14B510 raw-bytes MATCH; attrition CLEAN; dual claws in place byte-identical; FUND watch evidence results/_r451bmc_fundnulls_watch.json"
)
with open(st_path, "w", encoding="utf-8", newline="") as fh:
    json.dump(st, fh, ensure_ascii=False, indent=1)
    fh.flush()
re_st = json.load(open(st_path, encoding="utf-8"))
assert re_st["round_no"] == 451 and isinstance(re_st["heartbeat_epoch_utc"], int)
print("STATE-OK round=451 epoch=%d" % re_st["heartbeat_epoch_utc"])

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
hb["activity_now"] = "FUND trio NULLS burn watch (bm-b canonical, V623/Q471/D335 rising, finalize window opens 10-05 10:30); N1 W116+ closed per O-2115 sec-2; golden-week maintenance all-green"
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
hb["latest_artifact"] = "results/_r451bmc_s6_log.txt (S6 37/37 rc0 full-leg evidence; streak 51) + results/_r451bmc_fundnulls_watch.json @ " + NOW
hb["next_milestone"] = "FUND trio finalize window 10-05..10-09 (D ETA 10-05 10:30; G-SEG GM + VALUE passive pre-rulings); O-2115/O-2030 acceptance 10-08; market reopen 10-09"
hb["prod_lanes"] = "FUND trio NULLS bm-b in-flight (watch only); N1 closed per O-2115 sec-2 (fund-trio has fire); O-2115 acceptance pack live (4/4 MET r448 refresh); W2 MASS_TRIAL judged+consumed (negative, E27 card)"
hb["round_no"] = 451
hb["updated_at"] = NOW
hb["verdict"] = "green (golden-week maintenance all-green; S6 evidence chain continuous; board/pool/orders lawful; lane divisions respected; waiting state declared: finalize window opens 10-05)"
if gpu_free is not None:
    for k in ("gpu_free_mb", "gpu_free_vram_mb", "gpu_free_vram_mib", "gpu_idle_vram_mb", "gpu_idle_vram_mib", "gpu_vram_free_mb"):
        hb[k] = gpu_free
with open(hb_path, "w", encoding="utf-8", newline="") as fh:
    json.dump(hb, fh, ensure_ascii=False, indent=1)
    fh.flush()
re_hb = json.load(open(hb_path, encoding="utf-8"))
assert re_hb["round_no"] == 451 and isinstance(re_hb["heartbeat_epoch_utc"], int) and len(re_hb["orders_ack"]) == 153
print("HEARTBEAT-OK cpu=%.1f ram_free=%.1f gpu_free=%s epoch=%d acks=%d" % (cpu, ram_free, gpu_free, re_hb["heartbeat_epoch_utc"], len(re_hb["orders_ack"])))
print("CLOSE-ALL-GREEN", NOW)

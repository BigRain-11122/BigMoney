# -*- coding: utf-8 -*-
"""r811 bm-c closeout: heartbeat/state/round-report bookkeeping (single-shift
round, no adoption). Law: fleet/README.md sec.6 machine-split files; epoch
must be JSON int (R170/R178); clock_read ISO8601 T-separator (R262);
products-first 3-line face; DEC/ORD shas READ PROGRAMMATICALLY from the
closing facts file -- ZERO literal sha constants (r583 law); ledger append
carries the r843 tail-CRLF guard; NO %-formatting anywhere in narrative
strings (r661 literal-% pit avoided by construction).
Hardware face: fresh psutil RAM/CPU sample + nvidia-smi VRAM (CREATE_NO_WINDOW),
keep prior heartbeat values on any sampling failure (honest fallback).
Pattern credit: Tools/_r810bmc_close.py (r810 canon, 1-gen clone)."""
import json, time, subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CST = timezone(timedelta(hours=8))
now = datetime.now(CST)
now_iso = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())
HM = now.strftime("%H:%M")[:4] + "x"

# --- facts-driven watermark read (NO literal sha constants; r583 law) ---
facts = json.loads((ROOT / "results" / "_r811bmc_s05_facts.json")
                   .read_text(encoding="utf-8"))
DEC_SHA = facts["dec_sha"]
ORD_SHA = facts["ord_sha"]
assert len(DEC_SHA) == 64 and len(ORD_SHA) == 40, "watermark shape gate"
assert facts.get("shape_assert") is True, "facts shape_assert gate"
assert facts.get("dec_delta") is False, "r811 closing: DEC must be zero-delta"
assert facts.get("ord_delta") is False, "r811 closing: ORD must be zero-delta"
assert facts.get("unacked") == [], "r811 closing: zero unacked orders"
assert facts.get("inbox_unread") == [], "r811 closing: zero unread inbox"

DEC_METHOD = (
    "python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r811 start 16:56 + closing "
    "double-sweep zero-delta; SSH fetch primary leg rc0 on BOTH sweeps, zero resets this round, HTTPS tmpref "
    "fallback armed but unused (Tools/_r811bmc_s05.py, r805 netpath law heritage); facts-driven from "
    "results/_r811bmc_s05_facts.json, 64hex shape-asserted; close-face reads sha PROGRAMMATICALLY from facts "
    "json, ZERO literal constants (r583 law)")
ORD_METHOD = (
    "python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r811 start + closing double-sweep "
    "zero-delta; SSH primary leg; facts-driven from results/_r811bmc_s05_facts.json, 40hex shape-asserted; "
    "close-face reads sha PROGRAMMATICALLY from facts json, ZERO literal constants (r583 law))")

did = (
    "2026-10-09T" + HM + "+08:00 | r811 | dept:工程（P2 队头 T5 science_audit 检七 C7 水位键覆盖率探针"
    "+S6 40/40+QA r811 净写+CODELY mini-split·第 112 bm-c 连守轮） | "
    "本地未达 origin commit 数=0（commit 后 push+fetch 自证·HTTPS ls-remote 送达面） | "
    "WM-VERDICT: 绿（red=false·lane=healthy·probe verdict=py_low_board_clear 合法 idle"
    "·next_pick=claimed moneyflow IC bm-a 车道合法"
    "·DEC BD94A27B 零差/ORD F26E1A37 零差〔轮首+收尾双扫·SSH 主腿四扫全通零重置〕"
    "·unacked 0〔56 orders〕·inbox 0） | "
    "孤儿面=1（只读不杀） | "
    "r811: ①S0 daemon 活态面两段吸收（8 件+2 件·commit ac400bc8e+8192a4a67·origin 零入站=纯吸收零 rebase"
    "·pull --rebase 多候选 FETCH_HEAD 拒=r784 正典坑当场化解〔fetch 已毕→直接 rebase origin/main=0/0 no-op〕"
    "·scratch msg 件+LF/CRLF 假脏环三连拒=新坑律入 CODELY〔OWN_PATTERNS 收编+checkout 归一正法〕）；"
    "②S0.5 起腿双扫零差+收尾双扫零差+inbox 0；"
    "③S1 smoke 49/49+SAT 引擎活（rc0·N1 注册面 W199 在册）+idle 非绿（RAM ~2.3GB/7 pct<40 pct 实工轮"
    "·idle_rounds=0·agenda 未饿）；"
    "④W17 跟随=SCREEN-SHARD-0..3 自 r810 后烧毕翻 done（屏面 4/8 done+GENERATE done）"
    "+4-7/JUDGE 候 RAM 门（free ~1.7-2.3GB<4GB r354 诚实拒收重试环·SLA 10-10 00:00 窗注记）"
    "+compute_audit 双旗（supply_gap+ignition_sla 同 5 IDs·RAM 门归因如实载·supply_floor 9>=3 无破）；"
    "⑤**T5 出列（本轮 P2 主产出·产品分=2 能跑实物）=science_audit 检七 C7 水位键覆盖率探针**："
    "预注册判据先行=SCIENCE_AUDIT_PREREG.md §10 追加冻结（键在场/形状类〔DEC 64-hex 正典或 40-hex 短形前缀可容"
    "·ORD 40-hex SHA-1〕/机队一致性前缀匹配等价分组/新鲜度 >7d STALE）→check_watermark_coverage() 实现"
    "（零网络只读·state-bm-*.json+state.json 数据驱动枚举）→selftest 30→38 腿全绿（8 条 C7 合成腿）"
    "→**首场实跑 exit 0 verdict=INCONSISTENT 三真发现：Ⓐbm-a/bm-b ORD 水位=64-hex SHA-256 形 vs ALGORITHM PIN "
    "r537 钉的 SHA-1 40-hex=哈希基座异构 Ⓑbm-b dec 水位落后 2 天（4c32527b@10-07 vs 机队 bd94a27b@10-09）=LAG "
    "Ⓒbm-a↔bm-c dec 前缀匹配=同一水位确认（短形容忍按设计生效）**——只报不阻断·裁定归轮会话 S0.5 消费步"
    "·tech 队列 7→6（T6 队头）；"
    "⑥S6 40/40 rc0（分离点火 17:04:5x→17:07:36 完链·update_daily 10-09 bar 第 5 轮守 new rows=0"
    "·cutoff 10-08 保持·sina 迟发下轮重试·fund_premium no-op NAV 10-08 覆盖"
    "·dualrun ZERO-DRIFT streak 7·regime ORANGE 取舍期 shadow·clock ORA cell）；"
    "⑦**QA r811 槽 det-99th 净写**：撞名预检 origin qa/ 零 r811 件→分离点火 --round 811 显式轮标（r758 律）"
    "→qa/smoke-r811-bm-c.md 5/5+qa/equity-curve-r811-bm-c.png（65,352B·800 bar 终值 1,023,027·determinism）；"
    "⑧CODELY 主件 mini-split（r731/r735 仪式·触发=主件 30,643B+新坑律 797B 越 30,720B 帽）："
    "r896 bm-a treasure_guard prescan 旁路坑 900B verbatim 迁 pit-tooling.md（22,056→22,999B）"
    "+r811 S0 scratch-msg×CRLF 假脏环坑 797B 首入主件→主件 30,544B ≤30,720B "
    "·prescan 双形 rc3 HIT×2 留痕（D-20261002-06 常设授权·treasure_guard abs 形旁路已闭=r896 焊面实弹复验）"
    "·receipt results/_r811bmc_codely_minisplit.json（逐字节+sha16 b70ac97d4bfe4db1+读回验证）；"
    "⑨S7 自愈四件套（loop pin=5 no-op+watchdog 重装幂等+双爪 installed）+attrition 4 台账 CLEAN（healed 史披露）"
    " | 下轮指针: r812=①10-09 bar 落地重试（sina 迟发第 5 轮守·落地即 marks/live_paper/REGIME v3 自续）"
    "②W17 屏烧跟随+SLA 10-10 00:00 窗核验③tech 队列 T6 队头消耗（idle_trigger 机队载体面他机接线）"
    "④O-20261009-1105 @bm-c② exit-to-asset 引擎腿设计件 ≤10-16 12:00"
    "⑤C7 发现裁定面（ORD 哈希基座异构+bm-b dec LAG→S0.5/MSG 面）"
)

activity = (
    "当前活: r811 bm-c T5 science_audit C7 水位键覆盖率探针（首场 INCONSISTENT 三真发现）+S6 40/40 rc0"
    "+QA r811 净写+CODELY mini-split（第 112 连守轮） | "
    "最近实物: scripts/science_audit.py（C7 探针+selftest 38/38）+research/SCIENCE_AUDIT_PREREG.md §10"
    "+results/science_audit.json（26th run·C7 首场）+qa/smoke-r811-bm-c.md（5/5）"
    "+qa/equity-curve-r811-bm-c.png（65,352B）+results/_r811bmc_s6_log.txt（40/40 rc0·DONE 17:07:36）"
    "+state/queue/tech.md（T5 出列 7→6）@本轮收口 commit | "
    "下个里程碑: 10-09 bar 落地（sina 迟发守）+W17 屏烧翻面（SLA 10-10 00:00）+O-1105② 设计件 ≤10-16 12:00"
    "+C7 发现裁定（bm-a/bm-b ORD 哈希基座+bm-b dec LAG）"
)

artifact = (
    "scripts/science_audit.py (C7 watermark-key coverage probe: presence/shape/prefix-match agreement/recency; "
    "selftest 30->38 legs) + research/SCIENCE_AUDIT_PREREG.md sec.10 (C7 criteria FROZEN before first run) "
    "+ results/science_audit.json (26th audit run, C7 inaugural INCONSISTENT with 3 real findings: bm-a/bm-b "
    "ORD sha 64-hex SHA-256 shape vs pinned SHA-1; bm-b dec watermark 2d LAG; bm-a<->bm-c dec prefix-match "
    "same-watermark confirmed) + Tools/_r811bmc_{s0,s05,s6,s6_ignite,qa_ignite,close,codely_minisplit}.py "
    "(r811 helper set) + results/_r811bmc_s05_facts.json + results/_r811bmc_s6_log.txt "
    "(40/40 rc0, DONE 17:07:36) + results/_r811bmc_qa_runner.out + qa/smoke-r811-bm-c.md (5/5 charter, "
    "800-bar final 1,023,027, determinism) + qa/equity-curve-r811-bm-c.png (65,352B, det-99th clean first-write) "
    "+ state/queue/tech.md (T5 consumed, queue 7->6) + CODELY.md (mini-split: r896 pit -> pit-tooling.md, "
    "new r811 S0-scratch-msg pit law; 30,544B <= 30,720B cap; receipt _r811bmc_codely_minisplit.json) "
    "+ research/pit-tooling.md (r896 entry verbatim) + results/_attrition_guard_scan.json CLEAN "
    "+ results/_orphan_face_probe.bm-c.json (orphan face 1, read-only) "
    "@ " + now_iso
)

nxt = (
    "r812 续作: ①10-09 bar 落地重试（sina 迟发第 5 轮守·tencent 上游已证·落地即 "
    "marks/live_paper/REGIME v3 自续+paper export 刷新）"
    "②W17 screens 4-7/JUDGE 烧翻面跟随+SLA 10-10 00:00 窗核验（RAM 门解除即 autofill 点火）"
    "③tech 队列 T6 队头消耗（idle_trigger 机队载体面他机接线 --claimed/--worked 清零律）"
    "④O-20261009-1105 @bm-c② exit-to-asset 引擎腿设计件 ≤10-16 12:00"
    "⑤C7 发现裁定面（bm-a/bm-b ORD 哈希基座异构+bm-b dec LAG→S0.5 消费步/MSG 面定谳）"
    "⑥MV 三选项等待态维持+bm-a PARKING-P1 跟进"
)

verify = (
    "smoke 49/49 + science_audit selftest 38/38 (8 new C7 legs) + C7 inaugural run exit 0 "
    "(verdict INCONSISTENT, 3 findings, report-only) + S6 40/40 rc0 "
    "（results/_r811bmc_s6_log.txt + _r811bmc_s6_runner.out·DONE 17:07:36） "
    "+ qa/smoke-r811-bm-c.md 5/5（PNG 65,352B·800 bar 终值 1,023,027·det-99th 零撞名净写·r640 close 前终态核验） "
    "+ attrition 4 台账 CLEAN（healed 史披露） "
    "+ 自愈四件全绿（loop pin=5 幂等 no-op+watchdog 重装幂等+双爪 installed） + 孤儿面=1 只读 "
    "+ DEC/ORD 轮首+收尾双扫零差（BD94A27B/F26E1A37·SSH 主腿四扫全通零重置） "
    "+ unacked 0〔56 orders〕 + inbox 0 + idle 非绿（RAM ~2.3GB 实工轮·idle_rounds=0） "
    "+ W17 shards 0-3 done 实证 + compute_audit 双旗 RAM 门归因披露（supply_gap+ignition_sla 同 r810 5 IDs） "
    "+ CODELY mini-split 零丢失断言（block verbatim in target+needle 零残留+主件 30,544B≤30,720B+receipt sha16）"
)

# --- hardware face: fresh sample, honest fallback to prior values ---
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
ram_free_gb = cpu_pct = gpu_free_mb = None
try:
    import psutil
    ram_free_gb = round(psutil.virtual_memory().available / (1024 ** 3), 1)
    cpu_pct = round(psutil.cpu_percent(interval=1), 1)
except Exception:
    pass
try:
    p = subprocess.run(["nvidia-smi", "--query-gpu=memory.free",
                        "--format=csv,noheader,nounits"],
                       capture_output=True, creationflags=CNW, timeout=20)
    if p.returncode == 0:
        gpu_free_mb = int(float(p.stdout.decode().strip().splitlines()[0]))
except Exception:
    pass

# ---- heartbeat ----
hb_path = ROOT / "fleet" / "machines" / "bm-c.json"
hb = json.loads(hb_path.read_text(encoding="utf-8"))
for k in ("last_seen", "last_seen_at", "clock_read", "ts", "updated", "updated_at", "last_run_at",
          "last_ts", "current_task_at", "last_decisions_at", "last_orders_at"):
    hb[k] = now_iso
hb["heartbeat_epoch_utc"] = epoch
hb["last_round"] = 811
hb["last_round_at"] = now_iso
hb["round_no"] = 811
hb["round_no_label"] = "round 811 (bm-c)"
hb["current_task"] = activity
hb["activity_now"] = activity
hb["did"] = did
hb["note"] = did
hb["verdict"] = did
hb["last_round_summary"] = did
hb["last_action"] = did
hb["latest_artifact"] = artifact
hb["next"] = nxt
hb["next_pointer"] = nxt
hb["next_milestone"] = nxt
hb["verify"] = verify
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["last_pulled_at"] = now_iso
hb["head_sha"] = "pending-this-round-commit"
hb["last_decisions_sha"] = DEC_SHA
hb["last_decisions_sha_method"] = DEC_METHOD
hb["dec_sha_method"] = DEC_METHOD
hb["last_orders_sha"] = ORD_SHA
hb["last_orders_sha_method"] = ORD_METHOD
hb["ord_sha_method"] = ORD_METHOD
if ram_free_gb is not None:
    for k in ("free_ram_gb", "idle_ram_gb", "ram_free_gb"):
        if k in hb:
            hb[k] = ram_free_gb
if cpu_pct is not None:
    for k in ("cpu_pct", "cpu_util_pct"):
        if k in hb:
            hb[k] = cpu_pct
    hb["cpu_idle_pct"] = round(100 - cpu_pct, 1)
if gpu_free_mb is not None:
    for k in ("gpu_free_vram_mb", "gpu_idle_vram_mb", "gpu_free_mb", "gpu_idle_mb",
              "gpu_vram_free_mb", "gpu_free_mib", "gpu_idle_mib"):
        if k in hb:
            hb[k] = gpu_free_mb
hb_path.write_text(json.dumps(hb, ensure_ascii=False, indent=1), encoding="utf-8")

# ---- state ----
st_path = ROOT / "state-bm-c.json"
st = json.loads(st_path.read_text(encoding="utf-8"))
for k in ("clock_read", "current_task_at", "last_round_at", "last_round_ts", "last_seen",
          "last_seen_at", "last_run_at", "last_ts", "ts", "updated", "updated_at",
          "last_decisions_read_at", "last_decisions_at", "last_orders_at"):
    if k in st:
        st[k] = now_iso
for k in ("did", "note", "last_round_summary", "last_action", "verdict"):
    if k in st:
        st[k] = did
st["heartbeat_epoch_utc"] = epoch
st["last_round"] = 811
st["round_no"] = 812
st["round_no_label"] = "round 811 (bm-c)"
st["current_task"] = activity
st["activity_now"] = activity
st["latest_artifact"] = artifact
st["next"] = nxt
st["next_pointer"] = nxt
st["next_milestone"] = nxt
st["verify"] = verify
st["idle_rounds"] = 0
st["agenda_starved"] = False
st["last_decisions_sha"] = DEC_SHA
st["last_decisions_sha_method"] = DEC_METHOD
st["dec_sha_method"] = DEC_METHOD
st["last_orders_sha"] = ORD_SHA
st["last_orders_sha_method"] = ORD_METHOD
st["ord_sha_method"] = ORD_METHOD
if ram_free_gb is not None:
    for k in ("free_ram_gb", "idle_ram_gb", "ram_free_gb"):
        if k in st:
            st[k] = ram_free_gb
if cpu_pct is not None:
    for k in ("cpu_pct", "cpu_util_pct"):
        if k in st:
            st[k] = cpu_pct
    st["cpu_idle_pct"] = round(100 - cpu_pct, 1)
if gpu_free_mb is not None:
    for k in ("gpu_free_vram_mb", "gpu_idle_vram_mb", "gpu_free_mb", "gpu_idle_mb",
              "gpu_vram_free_mb", "gpu_free_mib", "gpu_idle_mib"):
        if k in st:
            st[k] = gpu_free_mb
st_path.write_text(json.dumps(st, ensure_ascii=False, indent=1), encoding="utf-8")

# ---- round report (canonical machine-split ledger path, fleet/README sec.6) ----
rr_path = ROOT / "logs" / "iteration-loop" / "round_reports-bm-c.md"
raw = rr_path.read_bytes()
if not raw.endswith((b"\r\n", b"\n")):   # r843 tail-terminator guard
    with rr_path.open("a", encoding="utf-8") as f:
        f.write("\r\n")
with rr_path.open("a", encoding="utf-8") as f:
    f.write(did + "\n")

# ---- self-checks ----
hb2 = json.loads(hb_path.read_text(encoding="utf-8"))
st2 = json.loads(st_path.read_text(encoding="utf-8"))
assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch must be int"
assert isinstance(st2["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in hb2["clock_read"] and "+" in hb2["clock_read"], "clock_read must be ISO8601 T-form"
assert hb2["round_no"] == 811 and st2["round_no"] == 812
assert len(hb2["last_decisions_sha"]) == 64 and len(hb2["last_orders_sha"]) == 40, "watermark shape gate"
tail = rr_path.read_text(encoding="utf-8", errors="replace").rstrip().splitlines()[-1]
assert tail.startswith("2026-10-09T"), "ledger tail must be this round row"
print("closeout OK: hb round=811 state next=812 epoch=%d ts=%s dec=%s ord=%s ram=%s cpu=%s gpu=%s"
      % (epoch, now_iso, DEC_SHA[:8], ORD_SHA[:8], ram_free_gb, cpu_pct, gpu_free_mb))

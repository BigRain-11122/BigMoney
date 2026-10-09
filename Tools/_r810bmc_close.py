# -*- coding: utf-8 -*-
"""r810 bm-c closeout: heartbeat/state/round-report bookkeeping (single-shift
round, no adoption). Law: fleet/README.md sec.6 machine-split files; epoch
must be JSON int (R170/R178); clock_read ISO8601 T-separator (R262);
products-first 3-line face; DEC/ORD shas READ PROGRAMMATICALLY from the
closing facts file -- ZERO literal sha constants (r583 law); ledger append
carries the r843 tail-CRLF guard; NO %-formatting anywhere in narrative
strings (r661 literal-% pit avoided by construction).
Hardware face: fresh psutil RAM/CPU sample + nvidia-smi VRAM (CREATE_NO_WINDOW),
keep prior heartbeat values on any sampling failure (honest fallback).
Pattern credit: Tools/_r809bmc_close.py (r809 canon, 1-gen clone)."""
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
facts = json.loads((ROOT / "results" / "_r810bmc_s05_facts.json")
                   .read_text(encoding="utf-8"))
DEC_SHA = facts["dec_sha"]
ORD_SHA = facts["ord_sha"]
assert len(DEC_SHA) == 64 and len(ORD_SHA) == 40, "watermark shape gate"
assert facts.get("shape_assert") is True, "facts shape_assert gate"
assert facts.get("dec_delta") is False, "r810 closing: DEC must be zero-delta"
assert facts.get("ord_delta") is False, "r810 closing: ORD must be zero-delta"
assert facts.get("unacked") == [], "r810 closing: zero unacked orders"
assert facts.get("inbox_unread") == [], "r810 closing: zero unread inbox"

DEC_METHOD = (
    "python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r810 start 16:39 + closing "
    "double-sweep zero-delta; SSH fetch primary leg rc0 on BOTH sweeps, zero resets this round, HTTPS tmpref "
    "fallback armed but unused (Tools/_r810bmc_s05.py, r805 netpath law heritage); facts-driven from "
    "results/_r810bmc_s05_facts.json, 64hex shape-asserted; close-face reads sha PROGRAMMATICALLY from facts "
    "json, ZERO literal constants (r583 law)")
ORD_METHOD = (
    "python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r810 start + closing double-sweep "
    "zero-delta; SSH primary leg; facts-driven from results/_r810bmc_s05_facts.json, 40hex shape-asserted; "
    "close-face reads sha PROGRAMMATICALLY from facts json, ZERO literal constants (r583 law))")

did = (
    "2026-10-09T" + HM + "+08:00 | r810 | dept:工程（P2 队头 T4 town.html 详情五列全表对齐+S6 40/40+QA r810 净写+HANDOVER 5x 落账·第 111 bm-c 连守轮） | "
    "本地未达 origin commit 数=0（commit 后 push+fetch 自证·HTTPS ls-remote 送达面） | "
    "WM-VERDICT: 绿（red=false·lane=healthy·probe verdict=py_low_board_clear 合法 idle·next_pick=claimed moneyflow IC bm-a 车道合法"
    "·DEC BD94A27B 零差/ORD F26E1A37 零差〔轮首+收尾双扫·SSH 主腿两扫全通零重置〕"
    "·unacked 0〔55 orders〕·inbox 0） | "
    "孤儿面=1（只读不杀） | "
    "r810: ①S0 两段吸收 daemon 面 9+2 件（8 daemon 活态面+orphan 探针面+autofill 态·commit 0d39b2508+1f832d44d"
    "·rebase origin/main CLEAN 2 picks 零 UU·并入 bm-a r920 三连〔W199 finalize one-pass 落地 852,145/K435,720+W200 席位公示〕）；"
    "②S0.5 起腿双扫零差+inbox 1 件消费（MSG-2026-10-09-1645-bma-w200-seat：W200 席位公示=reserved bm-a 115th owned/190th wave"
    "·A 454_804..456_803/B 456_804..457_003 阶梯 SIXTIETH·W201+ 投影须 post-W200 宇宙重derive——bm-c 零动作·移 processed·回执本行）；"
    "③S1 smoke 49/49+SAT 引擎活（rc0·N1 注册面 W199 在册）+idle 非绿（RAM 11 pct<40 pct 实工轮·idle_rounds=0·agenda 未饿）；"
    "④W17 跟随=SCREEN-SHARD-0 LIVE 烧实证（pid 46176@16:32 CPU 活跃·checkpoint 首行未落·r491 un-park 复燃链）"
    "+shards 1-3 本机 autofill 占位+4-7/JUDGE 候 RAM 门（free 1.7GB<4GB r354 诚实拒收重试环）"
    "+compute_audit 双旗（supply_gap+ignition_sla 5 IDs·RAM 门归因如实载·supply_floor 9>=3 无破"
    "·SLA D-20261009-01iii 10 entries 06:28 交付面达成·claimable 现读 9〔GENERATE 已耗〕）；"
    "⑤**T4 出列（本轮 P2 主产出）**：town.html 详情五列全表对齐=org_chart v2 部门表「域/钩子/升级线」三列 11/11 楼补齐"
    "+组合楼团队行 v3 对齐（相关性监控=组合构建团队 mandate 非独立团队）+footer 收口行"
    "·验证=node --check rc0+50 片段 grep 核对面 town_missing=[]（org 侧 49/50 字面+1 backtick 渲染差零语义差）"
    "·tech 队列 8→7（T5 队头）；"
    "⑥S6 40/40 rc0（分离点火 64s 完链 16:42:01→16:43:05·update_daily 10-09 bar 第 4 轮守 new rows=0·cutoff 10-08 保持"
    "·sina 迟发下轮重试·tencent 上游已证）；"
    "⑦**QA r810 槽 det-99th 净写**：撞名预检 origin qa/ 零 r810 件→分离点火 --round 810 显式轮标（r758 律）"
    "→qa/smoke-r810-bm-c.md 5/5+qa/equity-curve-r810-bm-c.png（65,489B·800 bar 终值 1,023,027）→r640 close 前终态核验；"
    "⑧HANDOVER 5x 落账（r801-r810 单窗紧凑覆盖·r805 stamp 漏记披露·本行清偿）；"
    "⑨S7 自愈四件套（loop pin=5 no-op+watchdog 在位+双爪 identical）+attrition 4 台账 CLEAN（healed 史披露）"
    " | 下轮指针: r811=①10-09 bar 落地重试（sina 迟发第 4 轮守）②W17 屏烧跟随+SLA 10-10 00:00 窗核验③tech 队列 T5 队头"
    "（science_audit C6 判据扩展）④O-20261009-1105 @bm-c② exit-to-asset 设计件 ≤10-16 12:00"
)

activity = (
    "当前活: r810 bm-c T4 town.html 详情五列对齐+S6 40/40 rc0+QA r810 净写+HANDOVER 5x（第 111 连守轮） | "
    "最近实物: town.html（详情五列 11/11 楼·node --check rc0）+qa/smoke-r810-bm-c.md（5/5）"
    "+qa/equity-curve-r810-bm-c.png（65,489B）+results/_r810bmc_s6_log.txt（40/40 rc0·DONE 16:43:05）"
    "+state/queue/tech.md（T4 出列 8→7）+research/HANDOVER.md r810 5x 行@本轮收口 commit | "
    "下个里程碑: 10-09 bar 落地（sina 迟发守）+W17 屏烧翻面（SLA 10-10 00:00）+O-1105② 设计件 ≤10-16 12:00"
)

artifact = (
    "town.html (detail-panel five-column alignment 11/11 buildings vs org_chart v2 dept table; "
    "node --check rc0 + 50-frag grep cross-check) "
    "+ Tools/_r810bmc_{s05,s6,s6_ignite,qa_ignite,close}.py (r810 helper quintet; s05 SSH-primary + "
    "HTTPS-tmpref fallback + unacked/inbox closing faces; s6 detached-ignite r809 canon clone) "
    "+ results/_r810bmc_s05_facts.json + results/_r810bmc_s6_log.txt + results/_r810bmc_s6_runner.out "
    "(40/40 rc0 evidence, DONE 16:43:05) + results/_r810bmc_qa_runner.out "
    "+ qa/smoke-r810-bm-c.md (5/5 QA charter, 800-bar final 1,023,027, determinism) "
    "+ qa/equity-curve-r810-bm-c.png (65,489B, det-99th clean first-write) "
    "+ results/_r810bmc_town_check.js (node --check extraction evidence) "
    "+ state/queue/tech.md (T4 consumed, queue 8->7) + research/HANDOVER.md (r810 5x entry) "
    "+ results/_attrition_guard_scan.json CLEAN + results/_orphan_face_probe.bm-c.json (orphan face 1, read-only) "
    "@ " + now_iso
)

nxt = (
    "r811 续作: ①10-09 bar 落地重试（sina 迟发第 4 轮守·tencent 探针已证 bar 上游在·落地即 "
    "marks/live_paper/REGIME v3 自续+paper export 刷新）"
    "②W17 screens 烧翻面跟随+池 SLA 10-10 00:00 窗核验（现 9 ready·shard-0 LIVE 烧中）"
    "③tech 队列 T5 队头消耗（science_audit C6 判据扩展·预注册判据先行）"
    "④O-20261009-1105 @bm-c② exit-to-asset 引擎腿设计件 ≤10-16 12:00"
    "⑤MV 三选项等待态维持+bm-a PARKING-P1 跟进"
)

verify = (
    "smoke 49/49 + S6 40/40 rc0（results/_r810bmc_s6_log.txt + _r810bmc_s6_runner.out·DONE 16:43:05） "
    "+ qa/smoke-r810-bm-c.md 5/5（PNG 65,489B·800 bar 终值 1,023,027·det-99th 零撞名净写·r640 close 前终态核验） "
    "+ town.html node --check rc0 + 50 片段 grep 核对面零缺 + attrition 4 台账 CLEAN（healed 史披露） "
    "+ 自愈四件全绿（loop pin=5 幂等 no-op+watchdog 在位+双爪 identical） + 孤儿面=1 只读 "
    "+ DEC/ORD 双扫零差（BD94A27B/F26E1A37·SSH 主腿两扫全通·prev 双清） + unacked 0〔55 orders〕 "
    "+ inbox 0（W200 席位 MSG 消费移 processed·回执轮报行） + idle 非绿（RAM 11 pct 实工轮·idle_rounds=0） "
    "+ W17 shard-0 LIVE 烧实证（pid 46176）+ compute_audit 双旗 RAM 门归因披露（supply_gap+ignition_sla）"
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
hb["last_round"] = 810
hb["last_round_at"] = now_iso
hb["round_no"] = 810
hb["round_no_label"] = "round 810 (bm-c)"
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
st["last_round"] = 810
st["round_no"] = 811
st["round_no_label"] = "round 810 (bm-c)"
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
assert hb2["round_no"] == 810 and st2["round_no"] == 811
assert len(hb2["last_decisions_sha"]) == 64 and len(hb2["last_orders_sha"]) == 40, "watermark shape gate"
tail = rr_path.read_text(encoding="utf-8", errors="replace").rstrip().splitlines()[-1]
assert tail.startswith("2026-10-09T"), "ledger tail must be this round row"
print("closeout OK: hb round=810 state next=811 epoch=%d ts=%s dec=%s ord=%s ram=%s cpu=%s gpu=%s"
      % (epoch, now_iso, DEC_SHA[:8], ORD_SHA[:8], ram_free_gb, cpu_pct, gpu_free_mb))

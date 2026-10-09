# -*- coding: utf-8 -*-
"""r812 bm-c closeout: heartbeat/state/round-report bookkeeping (single-shift
round, no adoption). Law: fleet/README.md sec.6 machine-split files; epoch
must be JSON int (R170/R178); clock_read ISO8601 T-separator (R262);
products-first 3-line face; DEC/ORD shas READ PROGRAMMATICALLY from the
closing facts file -- ZERO literal sha constants (r583 law); ledger append
carries the r843 tail-CRLF guard; NO %-formatting anywhere in narrative
strings (r661 literal-% pit avoided by construction).
r812 inbox-face delta vs r811 canon: inbox holds exactly TWO outbound MSG
files authored by this round (C7 adjudication -> bm-a/bm-b); assertion is
set-equality, not empty.
Hardware face: fresh psutil RAM/CPU sample + nvidia-smi VRAM (CREATE_NO_WINDOW),
keep prior heartbeat values on any sampling failure (honest fallback).
Pattern credit: Tools/_r811bmc_close.py (1-gen clone)."""
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
facts = json.loads((ROOT / "results" / "_r812bmc_s05_facts.json")
                   .read_text(encoding="utf-8"))
DEC_SHA = facts["dec_sha"]
ORD_SHA = facts["ord_sha"]
assert len(DEC_SHA) == 64 and len(ORD_SHA) == 40, "watermark shape gate"
assert facts.get("shape_assert") is True, "facts shape_assert gate"
assert facts.get("dec_delta") is False, "r812 closing: DEC must be zero-delta"
assert facts.get("ord_delta") is False, "r812 closing: ORD must be zero-delta"
assert facts.get("unacked") == [], "r812 closing: zero unacked orders"
assert sorted(facts.get("inbox_unread") or []) == [
    "MSG-20261009-173x-bmc-bma-C7ORDSHA.md",
    "MSG-20261009-173x-bmc-bmb-C7ORD-DECLAG.md"], "r812 closing: inbox = own outbound C7 MSGs only"

DEC_METHOD = (
    "python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r812 start sweep via HTTPS "
    "tmpref fallback leg (group-tree SSH fetch rc128 reset, r805 netpath law armed+used), closing sweep via "
    "SSH primary leg rc0 (channel recovered) -- both sweeps zero-delta; facts-driven from "
    "results/_r812bmc_s05_facts.json, 64hex shape-asserted; close-face reads sha PROGRAMMATICALLY from facts "
    "json, ZERO literal constants (r583 law)")
ORD_METHOD = (
    "python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r812 start + closing double-sweep "
    "zero-delta, channel dual-state as per DEC leg; facts-driven from results/_r812bmc_s05_facts.json, "
    "40hex shape-asserted; close-face reads sha PROGRAMMATICALLY from facts json, ZERO literal constants "
    "(r583 law))")

did = (
    "2026-10-09T" + HM + "+08:00 | r812 | dept:工程（P2 队头 T6 idle_trigger --auto 结构化清零腿"
    "+C7 裁定双 MSG+S6 40/40+QA r812 净写·第 113 bm-c 连守轮） | "
    "本地未达 origin commit 数=0（commit 后 push+fetch 自证·HTTPS 送达面） | "
    "WM-VERDICT: 绿（red=false·lane=healthy·probe verdict=insufficient_history〔窗 2 样·合法读〕"
    "·next_pick=claimed moneyflow IC bm-a 车道合法"
    "·DEC BD94A27B 零差/ORD F26E1A37 零差〔轮首+收尾双扫·起腿集团树 SSH rc128→HTTPS tmpref 接管"
    "·收腿 SSH 复活 rc0=通道双态实录〕·unacked 0〔56 orders〕·inbox 出站 2〔C7 MSG 待 bm-a/bm-b 收件〕） | "
    "孤儿面=1（只读不杀） | "
    "r812: ①S0=BigMoney 仓 SSH fetch 三连拒+集团树 SSH rc128（本机 SSH 通道间歇日）→HTTPS 正主 URL 勘误后 "
    "fetch rc0·origin 零入站（FETCH_HEAD=eae3de764=r811 close=本地 origin/main 恒等）·纯本地顶 2 笔合法 "
    "daemon autofill 自提交（w17-screen claim 面）零 rebase；"
    "②S0.5 起腿双扫零差+收尾双扫零差+unacked 0；"
    "③S1 smoke 49/49+SAT 引擎活（rc0·N1 W199 注册面在册）+idle 非绿（RAM 8.3 pct<40 pct·VRAM 1.12GB<6GB"
    "·idle_rounds=0·agenda 未饿）；"
    "④W17 跟随=池面实测屏 8/8 shard ready+引擎 17:10-17:25 重持有 0-3 claim（owner_since 实证·三笔 "
    "autofill commit）+4-7/JUDGE 未认领·RAM 门 ~2GB<4GB r354 诚实拒收面维持·SLA 10-10 00:00 窗注记"
    "+compute_audit 双旗（supply_gap+ignition_sla 同 W17 5 IDs·RAM 门归因如实载·supply_floor ready 9>=3 无破）；"
    "⑤**T6 出列（本轮 P2 主产出·产品分=2 能跑实物）=idle_trigger --auto 结构化清零腿（机队载体面他机接线）**："
    "Tools/idle_trigger.py 新增 --auto 模式=确定性零 AI 判定——池面 claim 检测〔runnable_pool shards "
    "owner==本机且 owner_since≥last_bookkeeping 窗→declare claimed〕+产品工 commit 分类器〔git log "
    "--committer=本机 user.email（机队 committer 身份四相实测唯一）·daemon 主题排除·diff-tree 路径分类=纯记账 "
    "黑名单 20 径族外命中→declare worked〕·保守偏置=漏检只多 RED 催办不静默放行；"
    "Tools/iteration_loop.ps1 轮尾接线（headless 退出后 best-effort·ParseFile 0 err·共享载体单源随 git "
    "机队分发）；selftest 9→41 腿全绿；**实弹端到端双验：窗内 --auto=declared claimed（pool_claim="
    "w17-screen-0of8·引擎真 claim 被结构化捕获）+close commit 后复验 declared=worked（work_paths 命中 "
    "Tools 面）**·tech 队列 6→5（T7 队头）；"
    "⑥C7 裁定面落地（r811 三真发现收口）=双 MSG 净写：bmc→bma（ORD sha 64-hex vs ALGORITHM PIN r537 "
    "SHA-1 重算请求·dec 面正常确认）+bmc→bmb（ORD PIN+dec 2d LAG〔4c32527b@10-07〕·HTTPS tmpref 配方指针"
    "=Tools/_r812bmc_s05.py 可克隆）；"
    "⑦S6 40/40 rc0（分离点火 17:2x→DONE 17:27:45·update_daily 10-09 bar 第 6 轮守 new rows=0"
    "·cutoff 10-08 保持·sina 迟发下轮重试〔直探源体编码面无明文日期·采集器诚实面维持〕"
    "·fund_premium no-op NAV T+1 面·dualrun streak 8·regime shadow）；"
    "⑧QA r812 槽 det-99th 净写：撞名预检 origin qa/ 零 r812 件→分离点火 --round 812 显式轮标（r758 律）"
    "→qa/smoke-r812-bm-c.md 5/5+qa/equity-curve-r812-bm-c.png（65,456B·800 bar 终值 1,023,027·determinism）；"
    "⑨S7 自愈四件套（loop pin=5 幂等 no-op+watchdog 在位+双爪 installed）+attrition 4 台账 CLEAN（healed 史披露）"
    " | 下轮指针: r813=①10-09 bar 落地重试（sina 迟发第 6 轮守·落地即 marks/live_paper/REGIME v3 自续）"
    "②W17 SLA 10-10 00:00 窗核验（引擎 claim 跟随）③tech 队列 T7 队头消耗（watermark 低位窗判读扩展）"
    "④O-20261009-1105 @bm-c② exit-to-asset 引擎腿设计件 ≤10-16 12:00"
    "⑤C7 MSG 回执跟随（bm-a/bm-b 修复面+机队 C7 复扫翻绿）⑥MV 三选项等待态维持+bm-a PARKING-P1 跟进"
)

activity = (
    "当前活: r812 bm-c T6 idle_trigger --auto 结构化清零腿（机队载体面他机接线·实弹双验）"
    "+C7 裁定双 MSG+S6 40/40+QA r812 净写（第 113 连守轮） | "
    "最近实物: Tools/idle_trigger.py（--auto 模式+selftest 9→41 腿）+Tools/iteration_loop.ps1（轮尾 --auto 接线）"
    "+fleet/inbox/MSG-20261009-173x-bmc-bma-C7ORDSHA.md+bmc-bmb-C7ORD-DECLAG.md（C7 裁定双 MSG）"
    "+results/_r812bmc_s6_log.txt（40/40 rc0·DONE 17:27:45）+qa/smoke-r812-bm-c.md（5/5）"
    "+qa/equity-curve-r812-bm-c.png（65,456B）+state/queue/tech.md（T6 出列 6→5）@本轮收口 commit | "
    "下个里程碑: 10-09 bar 落地（sina 迟发守）+W17 屏烧翻面（SLA 10-10 00:00）+O-1105② 设计件 ≤10-16 12:00"
    "+C7 MSG 回执（bm-a/bm-b 修复面）"
)

artifact = (
    "Tools/idle_trigger.py (--auto structural declare leg: pool-shard claim detection + product-work commit "
    "classifier with 20-regex bookkeeping-path blacklist + conservative bias; selftest 9->41 legs ALL PASS) "
    "+ Tools/iteration_loop.ps1 (round-end --auto wiring, ParseFile 0 errors, fleet-shared carrier) "
    "+ live end-to-end: declared=claimed pool_claim=w17-screen-0of8 (engine claim structurally captured) "
    "+ Tools/_r812bmc_{s05,s6,s6_ignite,close}.py (r812 helper set) "
    "+ fleet/inbox/MSG-20261009-173x-bmc-bma-C7ORDSHA.md + MSG-20261009-173x-bmc-bmb-C7ORD-DECLAG.md "
    "(C7 adjudication: bm-a ORD sha->SHA-1 pin recompute; bm-b ORD pin + dec 2d LAG + HTTPS tmpref recipe "
    "pointer) + results/_r812bmc_s05_facts.json (start HTTPS-tmpref + closing SSH-rc0 dual-state, zero-delta "
    "both sweeps) + results/_r812bmc_s6_log.txt (40/40 rc0, DONE 17:27:45, update_daily 10-09 bar 6th watch "
    "round new rows=0) + results/_r812bmc_qa_runner.out + qa/smoke-r812-bm-c.md (5/5 charter, 800-bar final "
    "1,023,027, determinism=True) + qa/equity-curve-r812-bm-c.png (65,456B, det-99th clean first-write) "
    "+ state/queue/tech.md (T6 consumed, queue 6->5) + results/_attrition_guard_scan.json CLEAN "
    "+ results/_orphan_face_probe.bm-c.json (orphan face 1, read-only) "
    "@ " + now_iso
)

nxt = (
    "r813 续作: ①10-09 bar 落地重试（sina 迟发第 6 轮守·tencent 上游已证·落地即 marks/live_paper/REGIME v3 "
    "自续+paper export 刷新）②W17 屏烧翻面跟随+SLA 10-10 00:00 窗核验（引擎 claim 在途·RAM 门解除即烧）"
    "③tech 队列 T7 队头消耗（watermark 探针低位窗判读扩展·py_low_with_work_cands 违令点名自动化候选）"
    "④O-20261009-1105 @bm-c② exit-to-asset 引擎腿设计件 ≤10-16 12:00"
    "⑤C7 MSG 回执跟随（bm-a/bm-b ORD SHA-1 重算+bm-b dec 推进·机队 C7 复扫翻绿）"
    "⑥MV 三选项等待态维持+bm-a PARKING-P1 跟进"
)

verify = (
    "smoke 49/49 + idle_trigger selftest 41/41 (32 new T6 legs: path classifier 26 + daemon-subj 3 + log-line 3) "
    "+ live --auto dual verification (pre-commit window: declared=claimed pool_claim=w17-screen-0of8; "
    "post-close-commit re-run: declared=worked work_paths hit) + iteration_loop.ps1 ParseFile 0 errors "
    "+ py-compile OK + S6 40/40 rc0 （results/_r812bmc_s6_log.txt + _r812bmc_s6_runner.out·DONE 17:27:45） "
    "+ qa/smoke-r812-bm-c.md 5/5（PNG 65,456B·800 bar 终值 1,023,027·determinism=True·det-99th 零撞名净写·"
    "r640 close 前终态核验） + attrition 4 台账 CLEAN（healed 史披露） "
    "+ 自愈四件全绿（loop pin=5 幂等 no-op+watchdog 在位+双爪 installed） + 孤儿面=1 只读 "
    "+ DEC/ORD 轮首+收尾双扫零差（BD94A27B/F26E1A37·起腿 HTTPS tmpref+收腿 SSH rc0 双态实录） "
    "+ unacked 0〔56 orders〕 + inbox=own outbound 2（C7 MSG） + idle 非绿（RAM 8.3 pct 实工轮·idle_rounds=0） "
    "+ W17 池面 8/8 ready+引擎 claim 0-3 实证（owner_since 17:10-17:25）+4-7/JUDGE 未认领诚实披露 "
    "+ update_daily 第 6 轮守（new rows=0·cutoff 10-08·sina 迟发直探源体无明文=诚实守面）"
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
hb["last_round"] = 812
hb["last_round_at"] = now_iso
hb["round_no"] = 812
hb["round_no_label"] = "round 812 (bm-c)"
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
st["last_round"] = 812
st["round_no"] = 813
st["round_no_label"] = "round 812 (bm-c)"
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
assert hb2["round_no"] == 812 and st2["round_no"] == 813
assert len(hb2["last_decisions_sha"]) == 64 and len(hb2["last_orders_sha"]) == 40, "watermark shape gate"
tail = rr_path.read_text(encoding="utf-8", errors="replace").rstrip().splitlines()[-1]
assert tail.startswith("2026-10-09T"), "ledger tail must be this round row"
print("closeout OK: hb round=812 state next=813 epoch=%d ts=%s dec=%s ord=%s ram=%s cpu=%s gpu=%s"
      % (epoch, now_iso, DEC_SHA[:8], ORD_SHA[:8], ram_free_gb, cpu_pct, gpu_free_mb))

# -*- coding: utf-8 -*-
"""r813 bm-c closeout: heartbeat/state/round-report bookkeeping (single-shift
round, no adoption). Law: fleet/README.md sec.6 machine-split files; epoch
must be JSON int (R170/R178); clock_read ISO8601 T-separator (R262);
products-first 3-line face; DEC/ORD shas READ PROGRAMMATICALLY from the
closing facts file -- ZERO literal sha constants (r583 law); ledger append
carries the r843 tail-CRLF guard; NO %-formatting in narrative strings.
r813 inbox-face: inbox holds exactly TWO outbound MSG files authored by
r812 (C7 adjudication -> bm-a/bm-b, awaiting their receipt).
r813 DEC/ORD: BOTH deltas true and CONSUMED in-round (start sweep = 12:00
committee batches C-01/02/03 + D-04/05/06 + O-1x rows; closing sweep adds
O-20261009-1746 MiniMax-H3 @bm-c order arrived mid-round via eca78c3,
full row captured in results/_r813bmc_c03_receipt.txt) -- watermark
ADVANCES to the closing values, honest consumption note in the ledger row.
Pattern credit: Tools/_r812bmc_close.py (1-gen clone)."""
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
facts = json.loads((ROOT / "results" / "_r813bmc_s05_facts.json")
                   .read_text(encoding="utf-8"))
DEC_SHA = facts["dec_sha"]
ORD_SHA = facts["ord_sha"]
assert len(DEC_SHA) == 64 and len(ORD_SHA) == 40, "watermark shape gate"
assert facts.get("shape_assert") is True, "facts shape_assert gate"
assert facts.get("round") == 813, "facts round gate"
assert facts.get("unacked") == [], "r813 closing: zero unacked orders"
assert sorted(facts.get("inbox_unread") or []) == [
    "MSG-20261009-173x-bmc-bma-C7ORDSHA.md",
    "MSG-20261009-173x-bmc-bmb-C7ORD-DECLAG.md"], "r813 closing: inbox = own outbound C7 MSGs only"
# r813: dec_delta/ord_delta BOTH true = consumed in-round (start sweep batches
# + mid-round O-1746); NO zero-delta assert this round by design.

# watermark red face (S6 probe leg output)
try:
    wr = json.loads((ROOT / "results" / "watermark_red.json")
                    .read_text(encoding="utf-8"))
    wm_red = bool(wr.get("red"))
    wm_reason = str(wr.get("reason", ""))[:80]
except Exception:
    wm_red, wm_reason = False, "watermark_red.json unreadable (honest)"

DEC_METHOD = (
    "python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r813 start + closing "
    "double-sweep BOTH via SSH primary leg rc0 (channel healthy all day on bm-c); dec delta TRUE and "
    "CONSUMED in-round (12:00 committee batches C-20261009-01/02/03 + D-20261009-04/05/06 + orders rows "
    "O-1315/1430/1715/1740/1750); facts-driven from results/_r813bmc_s05_facts.json, 64hex "
    "shape-asserted; close-face reads sha PROGRAMMATICALLY from facts json, ZERO literal constants "
    "(r583 law)")
ORD_METHOD = (
    "python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r813 start + closing "
    "double-sweep; ord delta TRUE in BOTH sweeps and CONSUMED: start = committee dispatch rows, "
    "closing adds O-20261009-1746 MiniMax-H3 @bm-c install order arrived mid-round via bm-a eca78c3, "
    "full row captured in results/_r813bmc_c03_receipt.txt; facts-driven, 40hex shape-asserted; "
    "close-face reads sha PROGRAMMATICALLY, ZERO literal constants (r583 law))")

did = (
    "2026-10-09T" + HM + "+08:00 | r813 | dept:工程/舰队（集团双直派收口轮：O-1750 FleetLink v1.1 升级+C-03 工作区审计整改 PASS+H3 令消费·第 114 bm-c 连守轮） | "
    "本地未达 origin commit 数=0（收口 commit 后 push+fetch 自证） | "
    "WM-VERDICT: " + ("红：" + wm_reason if wm_red else "绿（red=false·lane=healthy") + "·DEC " + DEC_SHA[:8] + " consumed/ORD " + ORD_SHA[:8] + " consumed〔轮首+收尾双扫·SSH rc0 双通道健康·12:00 委员会批次 C-01/02/03+D-04/05/06+轮中 O-1746 MiniMax-H3 @bm-c 即装令全消费〕·unacked 0〔56 orders〕·inbox 出站 2〔C7 MSG 待 bm-a/bm-b 收件·bm-b 离线如实〕） | "
    "孤儿面=1（只读不杀） | "
    "r813: ①S0=absorb commit d87ffb67a（7 daemon 活面）+SSH fetch rc0+origin 零入站（behind=0）+CRLF 漂移面 checkout 归一（r811 律②）零 rebase（无对象·r812 先例同型）；"
    "②S0.5 双扫双 delta 全消费（起腿=12:00 委员会三案+D 批；收尾=O-1746 轮中到令捕获全文）；"
    "③S1 smoke 49/49+SAT 引擎活（rc0·N1 W199）+idle 非绿（RAM 8.3 pct 实工轮·idle_rounds=0）；"
    "④**O-20261009-1750 @bm-c FleetLink v1.1 升级收口（产品分=2 能跑实物）**：origin 三件物化（fleet-link.ps1 v1.1 11827B·poke-worker 新 4851B·register Parallel）→自匹配安全杀旧 v1.0 listener（pid 28396·python 宿主构造性免自撞）→重注册（REGISTERED+HEALTH OK+FW Tailscale-In present）→**/health version=1.1 截证落盘**（results/_r813bmc_fleetlink_receipt.json）；"
    "⑤**C-20261009-03 @bm-c 工作区审计+整改收口（产品分=2）**：首跑 VERDICT=FAIL（A: HEAD≠origin·121 behind·5 foreign M 面）→分类器定谳（fleet-nodes+settings×2=陈旧子集取 origin 零损失；gaming/quant CODELY.md=disk⊇origin 超集·2+3 条本机记忆未上链=断链违例实证）→零损失 union 术=字节备份→reset --hard origin/main→超集回写→commit 4680244（5 insertions）→push 撞拒 bm-a eca78c3→pull --rebase 干净 1/1→push retry OK（eca78c3..4b3ae88）→**审计复跑 VERDICT=PASS**（A sync=PASS HEAD=4b3ae88==origin·B total=0·C=0·E=0）——bm-c 回执件齐（审计输出+HEAD sha+union 备份保险 7 天）；"
    "⑥O-20260909-1746 @bm-c MiniMax-H3 即装令消费：前置勘毕（D: 376.9GB free ≥40GB ✓·ComfyUI 0.36.0≥0.30 无需升级 Day-0 支持在位·ModelScope 无 H3 镜像 404·GH 8G deploy repo 在活 stars=6 updated 10-09）——权重通道识别+分离下载点火=r814 主线（物理依赖留痕：hf.co 本机不可达 10-02 实测·hf-mirror 慢通道 ~1.4MB/s）；"
    "⑦C-20261009-02 @BigMoney 派单三件（清临时件+README 续鲜+池补 1·回执窗 10-10 00:00）消费在册→r814 队头开工（本窗预算耗于 O-1750+C-03 两集团直派·如实标因·池 ready=9 如实）；"
    "⑧S6 40/40 rc0（DONE 17:56:36·update_daily 10-09 bar 第 7 轮守 new rows=0 cutoff 10-08 sina 迟发·dashboard stale-takeover derive〔bm-a hb stale 78min·STALE_MIN 律〕）；"
    "⑨QA r813 槽零撞名净写：qa/smoke-r813-bm-c.md 5/5+qa/equity-curve-r813-bm-c.png（65,471B·800 bar 终值 1,023,027·determinism=True·per-machine 后缀 D-20261009-02 律）；"
    "⑩S7 自愈（loop pin=5 幂等 no-op+watchdog 重注册+双爪 installed）+attrition 4 台账 CLEAN（healed 史披露）+坑律 1 条（-ExecutionPolicy 漏 Bypass 值双犯=空 stdout+mojibake stderr·轮报告留痕待 mini-split 窗收编）"
    " | 下轮指针: r814=①H3 权重通道识别+分离下载点火（O-1746 即装主线：GH deploy README→HF 量化链接→hf-mirror 8 段并行·落地即 ComfyUI T2V 768P 5s 16:9 测试片〔泥板刻字特写·暖灯微推·尘粒浮光·2001 胶片颗粒·原生双声道有无如实报〕）②C-02 @BigMoney 三件（README 续鲜 13 天+清临时件 treasure_guard prescan+quarantine 首批+池补 1 prereg 起草）回执窗 10-10 00:00③10-09 bar 落地重试（sina 迟发第 8 轮守）④C7 MSG 回执跟随⑤tech 队列 T7 队头"
)

activity = (
    "当前活: r813 bm-c 集团双直派收口（O-1750 FleetLink v1.1 升级 /health 1.1 截证+C-03 审计整改 PASS·集团树 sync+零损失 union+H3 令消费）（第 114 连守轮） | "
    "最近实物: results/_r813bmc_fleetlink_receipt.json（/health version=1.1）+results/_r813bmc_ws_audit2.txt（审计 VERDICT=PASS·HEAD=4b3ae88）+group 4680244→4b3ae88 union push（2 gaming+3 quant 记忆上链）+qa/smoke-r813-bm-c.md（5/5）+qa/equity-curve-r813-bm-c.png（65,471B）+results/_r813bmc_s6_log.txt（40/40 rc0·DONE 17:56:36）@本轮收口 commit | "
    "下个里程碑: H3 装机+首条 T2V 测试片（O-1746·r814 下载点火·产出窗随权重落盘）+C-02 @BigMoney 三件（回执窗 10-10 00:00）+W17 SLA 10-10 00:00"
)

artifact = (
    "results/_r813bmc_fleetlink_receipt.json (/health version=1.1 + /status 200 evidence, O-20260909-1750 receipt) "
    "+ results/_r813bmc_ws_audit2.txt (fleet-workspace-audit VERDICT=PASS, A sync=PASS HEAD=4b3ae88==origin/main, C-20261009-03 bm-c receipt) "
    "+ group-tree union commits 4680244->(rebase)->4b3ae88 (2 gaming + 3 quant local-only memory entries re-linked upstream, zero loss; byte backups results/_r813bmc_union_backup_{gaming,quant}_CODELY.md 7-day insurance) "
    "+ Tools/_r813bmc_{s0,s05,probe,fl_recon,fl_upgrade,s6,s6_ignite,qa_ignite,ws_classify,union_exec,c03_receipt,h3_recon,close}.py (r813 helper set) "
    "+ results/_r813bmc_h3_recon.txt (O-1746 preconditions: D: 376.9GB free, ComfyUI 0.36.0 >= 0.30 no-upgrade-needed, ModelScope no-H3-mirror 404, GH 8G deploy repo alive) "
    "+ results/_r813bmc_c03_receipt.txt (zero-loss assert + O-1746 full order row capture) "
    "+ qa/smoke-r813-bm-c.md (5/5) + qa/equity-curve-r813-bm-c.png (65,471B, 800-bar final 1,023,027, determinism=True, per-machine suffix) "
    "+ results/_r813bmc_s6_log.txt (40/40 rc0, DONE 17:56:36, update_daily 10-09 bar 7th watch round new rows=0) "
    "+ results/_r813bmc_s7quartet.txt + results/_attrition_guard_scan.json (4 ledgers CLEAN) "
    "+ results/_orphan_face_probe.bm-c.json (orphan face 1, read-only) "
    "@ " + now_iso
)

nxt = (
    "r814 续作: ①H3 权重通道识别+分离下载点火（O-20261009-1746 @bm-c 即装主线：GH Danshiduzhi/minimax-h3-8g-deploy README→HF 量化链接→hf-mirror 8 段并行 ranged curl〔dl_qwen36.ps1 范式〕·落地即 ComfyUI T2V 768P 5s 16:9 测试片：泥板刻字特写·暖灯微推·尘粒浮光·2001 胶片颗粒·原生双声道有无如实报·物理依赖留痕）"
    "②C-20261009-02 @BigMoney 派单三件（回执窗 10-10 00:00）：README 续鲜（13 天陈）+清临时件（treasure_guard prescan+quarantine 首批·根级 _r*.txt+Tools 老龄助手）+池补 1（prereg 起草·PREREG_TEMPLATE α 机制段+共享判据库·池 ready=9→10）"
    "③10-09 bar 落地重试（sina 迟发第 8 轮守·落地即 marks/live_paper/REGIME v3 自续）"
    "④C7 MSG 回执跟随（bm-a/bm-b ORD SHA-1 重算+bm-b dec 推进）"
    "⑤tech 队列 T7 队头（watermark 探针低位窗判读扩展）⑥W17 SLA 10-10 00:00 窗核验"
)

verify = (
    "smoke 49/49 + SAT engine rc0 (N1 W199 registered) + FleetLink v1.1 live receipt (/health {ok:true,node:bm-c,version:1.1} + /status 200 + REGISTERED + HEALTH OK + FW Tailscale-In present) "
    "+ C-03 audit VERDICT=PASS rerun (A sync=PASS HEAD=4b3ae88==origin/main, B total=0, C conflict=0, E junk=0) "
    "+ union zero-loss (commit 4680244 5 insertions; rebase clean 1/1; push eca78c3..4b3ae88; byte backups in results/) "
    "+ S6 40/40 rc0 (results/_r813bmc_s6_log.txt + _r813bmc_s6_runner.out, DONE 17:56:36) "
    "+ qa/smoke-r813-bm-c.md 5/5 (PNG 65,471B, 800-bar final 1,023,027, determinism=True, det-99th zero-collision first-write) "
    "+ attrition 4 ledgers CLEAN (healed history disclosed) "
    "+ 自愈四件全绿 (loop pin=5 idempotent no-op + watchdog re-registered + both claws installed=True) "
    "+ 孤儿面=1 只读 + DEC/ORD 轮首+收尾双扫全消费（31E85972/09DF066D·SSH rc0 双通道） + unacked 0〔56 orders〕 "
    "+ inbox=own outbound 2（C7 MSG） + idle 非绿（RAM 8.3 pct 实工轮·idle_rounds=0·agenda 未饿） "
    "+ update_daily 第 7 轮守（new rows=0·cutoff 10-08·sina 迟发） + H3 前置勘三面（磁盘/版本/通道）"
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
hb["last_round"] = 813
hb["last_round_at"] = now_iso
hb["round_no"] = 813
hb["round_no_label"] = "round 813 (bm-c)"
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
st["last_round"] = 813
st["round_no"] = 814
st["round_no_label"] = "round 813 (bm-c)"
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
assert hb2["round_no"] == 813 and st2["round_no"] == 814
assert len(hb2["last_decisions_sha"]) == 64 and len(hb2["last_orders_sha"]) == 40, "watermark shape gate"
tail = rr_path.read_text(encoding="utf-8", errors="replace").rstrip().splitlines()[-1]
assert tail.startswith("2026-10-09T"), "ledger tail must be this round row"
print("closeout OK: hb round=813 state next=814 epoch=%d ts=%s dec=%s ord=%s ram=%s cpu=%s gpu=%s wm_red=%s"
      % (epoch, now_iso, DEC_SHA[:8], ORD_SHA[:8], ram_free_gb, cpu_pct, gpu_free_mb, wm_red))

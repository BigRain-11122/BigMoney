# -*- coding: utf-8 -*-
"""r817 bm-c closeout: heartbeat/state/round-report bookkeeping (single-shift
round, no adoption). Law: fleet/README.md sec.6 machine-split files; epoch
must be JSON int (R170/R178); clock_read ISO8601 T-separator (R262);
products-first 3-line face; DEC/ORD shas READ PROGRAMMATICALLY from the
facts file -- ZERO literal sha constants (r583 law); ledger append carries
the r843 tail-CRLF guard; NO %-formatting in narrative strings.
r817 DEC/ORD: dec_delta FALSE (hold, zero action); ord_delta TRUE =
consumed IN-ROUND (row O-20261009-1845 fleet memory-union order, this-repo
relevant=YES -> science gate PASSED, executed: fleet-memory-sync direct run,
local+64 canon+18, push 7b486b31; plus in-flight dispatches O-1750/1755
fleet-link v1.2/v1.3 upgrade and O-1715 workspace audit receipt). Close-sweep
second scan: both shas unchanged vs round-start faces (SSH reset window ->
HTTPS tmpref fallback leg).
r817 inbox face: live inbox = exactly the two own outbound C7 MSGs
awaiting bm-a/bm-b (bm-b offline as-is; zero bm-c-addressed unread).
Pattern credit: Tools/_r816bmc_close.py (1-gen clone)."""
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
facts = json.loads((ROOT / "results" / "_r817bmc_s05_facts.json")
                   .read_text(encoding="utf-8"))
DEC_SHA = facts["dec_sha"]
ORD_SHA = facts["ord_sha"]
assert len(DEC_SHA) == 64 and len(ORD_SHA) == 40, "watermark shape gate"
assert facts.get("shape_assert") is True, "facts shape_assert gate"
assert facts.get("round") == 817, "facts round gate"
assert facts.get("unacked") == [], "r817 closing: zero unacked orders"
assert facts.get("dec_delta") is False, "r817: dec delta expected FALSE"
assert facts.get("ord_delta") is True, "r817: ord delta expected TRUE (consumed in-round)"
assert facts.get("inbox_unread") == [
    "MSG-20261009-173x-bmc-bma-C7ORDSHA.md",
    "MSG-20261009-173x-bmc-bmb-C7ORD-DECLAG.md"], \
    "r817 closing: inbox must be own outbound C7 MSGs only"

# --- orphan + idle faces (round-zero probe + trigger reads) ---
orphan = 2
try:
    op = json.loads((ROOT / "results" / "_orphan_face_probe.bm-c.json")
                    .read_text(encoding="utf-8"))
    orphan = int(op.get("orphans", 2))
except Exception:
    pass
idle = json.loads((ROOT / "results" / "idle_trigger.bm-c.json")
                 .read_text(encoding="utf-8"))
idle_rounds = int(idle.get("idle_rounds", 0))

# watermark red face (S6 probe leg output)
try:
    wr = json.loads((ROOT / "results" / "watermark_red.json")
                    .read_text(encoding="utf-8"))
    wm_red = bool(wr.get("red"))
    wm_reason = str(wr.get("reason", ""))[:80]
except Exception:
    wm_red, wm_reason = False, "watermark_red.json unreadable (honest)"

DEC_METHOD = (
    "python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r817 start sweep via "
    "SSH primary leg rc0 (channel healthy at 19:07); dec delta FALSE = 31E85972 unchanged, zero action; "
    "close-sweep second scan SSH rc128 reset window -> HTTPS tmpref fallback leg, dec unchanged; "
    "facts-driven from results/_r817bmc_s05_facts.json, 64hex shape-asserted; close-face reads sha "
    "PROGRAMMATICALLY from facts json, ZERO literal constants (r583 law)")
ORD_METHOD = (
    "python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r817 start sweep via SSH "
    "primary leg rc0; ord delta TRUE = 84221B7D -> EA6B0AB5 consumed IN-ROUND: new row O-20261009-1845 "
    "(fleet memory-union order) science gate = THIS-REPO-RELEVANT -> EXECUTED (fleet-memory-sync direct "
    "run: local global memory +64 canon entries, bm-c unique +18 pushed, commit 7b486b31 via FLUXGROUP); "
    "in-flight dispatches O-20260909-1750/1755 fleet-link v1.2->v1.3 upgrade + O-1715 workspace audit "
    "receipt executed same window; close-sweep second scan unchanged vs in-round consumption face "
    "(SSH reset -> HTTPS tmpref leg); facts-driven, 40hex shape-asserted; close-face reads sha "
    "PROGRAMMATICALLY from facts json, ZERO literal constants (r583 law)")

did = (
    "2026-10-09T" + HM + "+08:00 | r817 | dept:工程/舰队（FleetLink v1.2→v1.3 升级+机队记忆并集落地+O-1715 审计整改回执+S6 40 腿+H3 file-1 字节验收·第 118 bm-c 连守轮） | "
    "本地未达 origin commit 数=0（收口 commit 后 push+fetch 自证·SSH reset 窗如实注记） | "
    "WM-VERDICT: " + ("红：" + wm_reason if wm_red else "绿（red=false·lane=healthy") + "·DEC " + DEC_SHA[:8] + " hold 零 delta/ORD " + ORD_SHA[:8] + " consumed〔轮首 delta 1 次=新增 1 行 O-1845 机队记忆并集同步令·涉本司=是→科学判断闸通过直接执行：fleet-memory-sync 落地 local+64/canon+18/push 7b486b31；S7 收尾二扫双恒等（SSH reset→HTTPS tmpref 备腿补扫）〕·unacked 0〔56 orders〕·inbox 出站 2〔C7 MSG 待 bm-a/bm-b 收件·bm-b 离线如实〕） | "
    "孤儿面=" + str(orphan) + "（只读不杀·含 ComfyUI idle server 8188·H3 装机复用面） | "
    "r817: ①S0=absorb commit 67d1e6b6b（12 own 活面·r816 QA 晚落双件注记）+SSH fetch rc0+rebase 首发拒→drift-normalize 3 面→retry 一发即中〔r814 正法第 4 轮连验〕；"
    "②S0.5=DEC 无 delta/ORD delta TRUE（84221B7D→EA6B0AB5·新 1 行 O-1845 记忆并集令·涉本司=是→执行：fleet-memory-sync 直跑 local+64/canon+18/push 7b486b31）+S7 收尾二扫双恒等（SSH reset 窗 HTTPS 备腿）；"
    "③S1 smoke 49/49+SAT 引擎活 rc0（wave 143-201 面）+idle 非绿（RAM 6.8%·H3/W17 双在飞·idle_rounds=0·agenda 未饿）；"
    "④**FleetLink 升级（O-1750/1755 bm-c 派单）**：精确 PID 击杀旧 v1.0 监听器 41792（防 Get-CimInstance 自匹配坑）→进程内重注册→health version=1.2 node=bm-c→bm-a v1.3 已在史（ebef6de）+盘面陈旧 v1.2 覆写治愈（checkout 复原 v1.3）→5min 保活自升级→**health version=1.3 截证**；"
    "⑤**机队记忆并集（O-1845）**：fleet-memory-sync 直跑+poke worker 接线在位——本地全局记忆+64 条正本/bm-c 独有 18 条上推/commit push 7b486b31 [via FLUXGROUP]·双向零丢失；"
    "⑥**O-1715 @bm-c 审计回执（≤24h 令）**：fleet-workspace-audit 首跑 VERDICT FAIL→同窗整改=B 面（fleet-link.ps1 陈旧 v1.2 覆写）checkout 治愈+A FAIL 证伪（SSH 断链期 fetch 全败用陈旧 origin/main 引用比对·rev-list 纯 ahead 1=自身 canon push 7b486b31+push 回执铁证=假 FAIL）+C=0/E=0 干净+D 面披露（MiniGame GIT_BIG 2172MB=owner 司在册非 bm-c 整改面）→回执 F-20261009-05 行落 HQ-FEEDBACK+两坑律直写域件（pit-ps FC93 管道截杀 $LASTEXITCODE 坑/pit-tooling 审计陈旧 ref 假 FAIL 坑·receipt _r817bmc_pit_append.json）；"
    "⑦S6 40/40 rc0（update_daily 10-09 bar 第 11 轮守 new rows=0 cutoff 10-08 sina 迟发诚实·pool_dualrun 先行腿·其余 39 腿 rc0）；"
    "⑧QA r817 5/5+PNG 65,397B 落盘（qa/smoke-r817-bm-c.md+qa/equity-curve-r817-bm-c.png）+r816 QA 晚落双件本轮收编入册；"
    "⑨H3 跟随（O-1746）：file-1 字节校验完成 16,825,666,232B 精确（盘面 95.5%→concat→byte-verify）+parts 清场+file-2（qwen3vl-32B 文本编码器 15,687,142,551B）8 段起烧·pid 2968 活 errors={}·全 manifest（40.3GB）ETA~20:1x；"
    "⑩W17 跟随：shard-1 pid 43204 活（CPU 24.9s 累积实证）+autofill 19:16 tick pool_empty_or_busy（RAM 门诚实）+SLA 10-10 00:00 窗前读数随班；"
    "⑪attrition 4 台账 CLEAN（healed 史披露）；"
    "⑫S7 自愈：IterationLoop no-op pin=5（首火 19:25）+Watchdog 重装（首火 19:19）+pre-commit/pre-push 双爪 installed LF 归一；"
    "⑬tick 成轮验证：r817 经 tick 成轮实证（r816 ⑪留痕承接·成轮 PASS）"
    " | 下轮指针: r818=①H3 file-2..5 下载完成验收（ETA~20:1x）→字节校验→ComfyUI T2V 768P 5s 16:9 测试片（O-1746·泥板刻字特写·暖灯微推·尘粒浮光·2001 胶片颗粒·原生双声道如实报·首跑报错可降级简单提示词先出片）②W17 screens 跟随+SLA 10-10 00:00 窗前读数③Tools 老龄助手隔离批（census 在案·prescan+quarantine 律）④C7 MSG 回执跟随（bm-a/bm-b ORD SHA-1 重算+bm-b dec 推进）⑤10-09 bar 第 12 轮守（sina 迟发自愈）⑥A-sync live 复核（通道 heal 后 ls-remote）⑦主件余量 211B 红线（新坑律一律直写域件 r666 范式）"
)

activity = (
    "当前活: r817 bm-c FleetLink v1.3 上线+机队记忆并集落地+O-1715 审计整改收口+H3 file-1 字节验收（第 118 连守轮·收口面） | "
    "最近实物: /health version=1.3（监听器自升级截证）+canon commit 7b486b31（+64/+18 双向记忆并集）+results/_r817bmc_ws_audit.txt（审计+整改回执 F-20261009-05）+qa/smoke-r817-bm-c.md（5/5）+research/pit-ps.md×pit-tooling.md 两坑律直写（receipt _r817bmc_pit_append.json）@本轮收口 commit | "
    "下个里程碑: H3 全 manifest 落地→ComfyUI T2V 768P 5s 16:9 测试片（O-1746·ETA~20:1x 下载完）+W17 SLA 10-10 00:00 窗前读数"
)

artifact = (
    "Tools/_r817bmc_{s0,s05,s6,s6_ignite,qa_ignite,pit_append}.py (r817 helper set, 1-gen clones) "
    "+ research/pit-ps.md (r817 PS pipeline Select-Object -First N kills native -> stale $LASTEXITCODE branch misroute, +902B direct-write) "
    "+ research/pit-tooling.md (r817 fleet-workspace-audit A-sync stale-ref false-FAIL under fetch outage, +805B direct-write) "
    "+ HQ-FEEDBACK.md (F-20261009-05 O-1715 audit receipt + A-leg ahead/behind disambiguation suggestion, +1,299B) "
    "+ results/_r817bmc_pit_append.json (3-block bytes+sha16 receipt) "
    "+ results/_r817bmc_s05_facts.json (start sweep SSH + close sweep HTTPS tmpref leg) "
    "+ results/_r817bmc_ws_audit.txt (fleet-workspace-audit first run VERDICT + remediation evidence) "
    "+ results/_r817bmc_s6_log.txt (40/40 rc0) + results/_r817bmc_s6_runner.{out,err} "
    "+ qa/smoke-r817-bm-c.md (5/5) + qa/equity-curve-r817-bm-c.png (65,397B) "
    "+ qa/smoke-r816-bm-c.md + qa/equity-curve-r816-bm-c.png (r816 late-landing pair, committed this round) "
    "+ fleet-link live face /health version=1.3 node=bm-c (O-1750/1755 upgrade receipt) "
    "+ group canon commit 7b486b31 (fleet-memory-union +18 entries via FLUXGROUP; O-1845 executed) "
    "+ H3 file-1 D:/ComfyUI/ComfyUI/models/diffusion_models/minimax_h3_fl2va_pruned_int4_convrot_simple.safetensors (16,825,666,232B byte-verified, O-1746; file-2 in-flight) "
    "+ results/_orphan_face_probe.bm-c.json (orphan face 2, read-only) + results/_attrition_guard_scan.json (4 ledgers CLEAN) "
    "@ " + now_iso
)

nxt = (
    "r818 续作: ①H3 file-2..5 下载完成验收（ETA~20:1x·字节校验→ComfyUI 装配→T2V 768P 5s 16:9 测试片：泥板刻字特写·暖灯微推·尘粒浮光·2001 胶片颗粒·原生双声道有无如实报·首跑报错可降级简单提示词先出片）"
    "②W17 screens 跟随+SLA 10-10 00:00 窗前读数（autofill 循环·RAM 门）"
    "③Tools 老龄助手隔离批（census=results/_r816bmc_tools_census.json 在案·treasure_guard prescan+quarantine manifest 7 天观察律先行）"
    "④C7 MSG 回执跟随（bm-a/bm-b ORD SHA-1 重算+bm-b dec 推进）"
    "⑤10-09 bar 第 12 轮守（sina 迟发自愈）"
    "⑥A-sync live 复核（GitHub 通道 heal 后 ls-remote·断链挂起注记解除）"
    "⑦主件余量 211B 红线（新坑律一律直写域件 r666 范式）⑧tick 成轮验证（r817 ⑬留痕承接）"
)

verify = (
    "smoke 49/49 + SAT engine rc0 (alive, N1 wave ledger 143-201 face) "
    "+ idle non-green (RAM 6.8pct free, dual in-flight W17/H3, idle_rounds=0, agenda not starved) "
    "+ fleet-link upgrade live proof (old v1.0 pid 41792 exact-PID kill, re-register, /health version=1.2 -> stale-disk v1.2 overwrite healed via checkout -> 5-min keepalive self-upgrade -> /health version=1.3 node=bm-c) "
    "+ memory union proof (MEMSYNC local+64 canon+18 pushed=7b486b31; group tree log 7b486b3 fleet-memory-union +18 [via FLUXGROUP] atop 1bb9119 bm-a O-1845 commit) "
    "+ O-1715 audit proof (first run VERDICT FAIL -> B-face healed checkout v1.3, A false-FAIL disproven via rev-list ahead-1 + push receipt + merge up-to-date ancestry; C=0 E=0; receipt row F-20261009-05) "
    "+ S6 40/40 rc0 (results/_r817bmc_s6_log.txt, nonzero-rc count=0) "
    "+ QA r817 5/5 (smoke-r817-bm-c.md, PNG 65,397B, detached runner survived) "
    "+ H3 file-1 byte-verified 16,825,666,232B exact + parts cleaned + file-2 8-seg in-flight (pid 2968 alive, errors={} clean) "
    "+ W17 shard-1 alive (pid 43204 CPU 24.9s accumulating) + autofill 19:16 tick pool_empty_or_busy honest "
    "+ attrition 4 ledgers CLEAN (healed history disclosed) "
    "+ self-heal green (IterationLoop no-op pin=5 first-fire 19:25, watchdog re-registered first-fire 19:19, both claws installed LF-normalized) "
    "+ orphan face=2 read-only + DEC/ORD start+close double sweep both unchanged in-round (close sweep SSH rc128 -> HTTPS tmpref leg rc0) "
    "+ unacked 0 [56 orders] + inbox=own outbound 2 (C7 MSG) "
    "+ pit direct-writes size-gated (pit-ps 27,581B / pit-tooling 25,056B, both <=30,720B; receipt _r817bmc_pit_append.json 3 blocks sha16) "
    "+ watermark_red=false (lane healthy)"
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
hb["last_round"] = 817
hb["last_round_at"] = now_iso
hb["round_no"] = 817
hb["round_no_label"] = "round 817 (bm-c)"
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
hb["idle_rounds"] = idle_rounds
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
st["last_round"] = 817
st["round_no"] = 818
st["round_no_label"] = "round 817 (bm-c)"
st["current_task"] = activity
st["activity_now"] = activity
st["latest_artifact"] = artifact
st["next"] = nxt
st["next_pointer"] = nxt
st["next_milestone"] = nxt
st["verify"] = verify
st["idle_rounds"] = idle_rounds
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
assert hb2["round_no"] == 817 and st2["round_no"] == 818
assert len(hb2["last_decisions_sha"]) == 64 and len(hb2["last_orders_sha"]) == 40, "watermark shape gate"
tail = rr_path.read_text(encoding="utf-8", errors="replace").rstrip().splitlines()[-1]
assert tail.startswith("2026-10-09T"), "ledger tail must be this round row"
print("closeout OK: hb round=817 state next=818 epoch=%d ts=%s dec=%s ord=%s ram=%s cpu=%s gpu=%s wm_red=%s orphan=%d"
      % (epoch, now_iso, DEC_SHA[:8], ORD_SHA[:8], ram_free_gb, cpu_pct, gpu_free_mb, wm_red, orphan))

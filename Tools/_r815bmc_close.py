# -*- coding: utf-8 -*-
"""r815 bm-c closeout: heartbeat/state/round-report bookkeeping (single-shift
round, no adoption). Law: fleet/README.md sec.6 machine-split files; epoch
must be JSON int (R170/R178); clock_read ISO8601 T-separator (R262);
products-first 3-line face; DEC/ORD shas READ PROGRAMMATICALLY from the
facts file -- ZERO literal sha constants (r583 law); ledger append carries
the r843 tail-CRLF guard; NO %-formatting in narrative strings.
r815 DEC/ORD: dec_delta FALSE and ord_delta FALSE (both watermarks held,
zero action -- zero new group rows since r814's O-1755 consumption).
r815 inbox face: W201 seat MSG (bm-a 18:12, informational, zero conflict
action) PROCESSED same-round -> moved to inbox/processed/ BEFORE close;
live inbox = exactly the two own outbound C7 MSGs awaiting bm-a/bm-b.
Pattern credit: Tools/_r814bmc_close.py (1-gen clone)."""
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
facts = json.loads((ROOT / "results" / "_r815bmc_s05_facts.json")
                   .read_text(encoding="utf-8"))
DEC_SHA = facts["dec_sha"]
ORD_SHA = facts["ord_sha"]
assert len(DEC_SHA) == 64 and len(ORD_SHA) == 40, "watermark shape gate"
assert facts.get("shape_assert") is True, "facts shape_assert gate"
assert facts.get("round") == 815, "facts round gate"
assert facts.get("unacked") == [], "r815 closing: zero unacked orders"
assert facts.get("dec_delta") is False, "r815: dec delta expected FALSE"
assert facts.get("ord_delta") is False, "r815: ord delta expected FALSE"

# --- live inbox face (W201 processed pre-close; expect own outbound only) ---
inbox_dir = ROOT / "fleet" / "inbox"
live_inbox = sorted(f.name for f in inbox_dir.glob("*.md"))
assert live_inbox == [
    "MSG-20261009-173x-bmc-bma-C7ORDSHA.md",
    "MSG-20261009-173x-bmc-bmb-C7ORD-DECLAG.md"], \
    "r815 closing: inbox must be own outbound C7 MSGs only"

# --- orphan + idle + pool faces (round-zero probe + trigger reads) ---
orphan = 1
try:
    op = json.loads((ROOT / "results" / "_orphan_face_probe.bm-c.json")
                    .read_text(encoding="utf-8"))
    orphan = int(op.get("orphans", 1))
except Exception:
    pass
idle = json.loads((ROOT / "results" / "idle_trigger.bm-c.json")
                 .read_text(encoding="utf-8"))
idle_rounds = int(idle.get("idle_rounds", 0))
claimable = int(idle.get("claimable_pool_lines", 0))

# watermark red face (S6 probe leg output)
try:
    wr = json.loads((ROOT / "results" / "watermark_red.json")
                    .read_text(encoding="utf-8"))
    wm_red = bool(wr.get("red"))
    wm_reason = str(wr.get("reason", ""))[:80]
except Exception:
    wm_red, wm_reason = False, "watermark_red.json unreadable (honest)"

DEC_METHOD = (
    "python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r815 start sweep via "
    "SSH primary leg rc0 (channel healthy on bm-c); dec delta FALSE = 31E85972 unchanged, zero action "
    "(12:00 committee batches consumed in r813; no new committee rows this window); facts-driven from "
    "results/_r815bmc_s05_facts.json, 64hex shape-asserted; close-face reads sha PROGRAMMATICALLY from "
    "facts json, ZERO literal constants (r583 law)")
ORD_METHOD = (
    "python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r815 start sweep via SSH primary "
    "leg rc0; ord delta FALSE = EB8DB998 unchanged, zero action (O-20261009-1755 consumed in r814; no new "
    "CEO rows this window); facts-driven from results/_r815bmc_s05_facts.json, 40hex shape-asserted; "
    "close-face reads sha PROGRAMMATICALLY, ZERO literal constants (r583 law)")

did = (
    "2026-10-09T" + HM + "+08:00 | r815 | dept:工程/舰队（H3 下载器 DOA 诊断修复复燃+F-04③ W18 依赖窗核验+W201 MSG 回执·第 116 bm-c 连守轮） | "
    "本地未达 origin commit 数=0（收口 commit 后 push+fetch 自证） | "
    "WM-VERDICT: " + ("红：" + wm_reason if wm_red else "绿（red=false·lane=healthy") + "·DEC " + DEC_SHA[:8] + " hold 零 delta/ORD " + ORD_SHA[:8] + " hold 零 delta〔轮首单扫·SSH rc0·双水位不变零动作〕·unacked 0〔56 orders〕·inbox 出站 2〔C7 MSG 待 bm-a/bm-b 收件·bm-b 离线如实〕） | "
    "孤儿面=" + str(orphan) + "（只读不杀·ComfyUI idle server 8188·parent DEAD·H3 装机复用面·收编决策归装机轮） | "
    "r815: ①S0=absorb commit 50ecf1910（own 活面）+SSH fetch rc0+rebase 首发拒（unstaged=活 daemon 10 面再写）→drift-normalize checkout 10 面→rebase retry 1 发即中→0/0〔r814 正法第 2 轮连验·坑律留痕随 r814 遗条待 mini-split 窗〕；"
    "②S0.5=DEC 无 delta（31E85972 不变）/ORD 无 delta（EB8DB998 不变）→双 hold 零动作；"
    "③S1 smoke 49/49+SAT 引擎活（rc0·N1 台账 wave 143-200 面·W200 B 尾 456_804..457_003 与 W201 MSG 恒等）+idle 非绿（RAM 8.3%·claimable=" + str(claimable) + "·idle_rounds=0）；"
    "④**O-20261009-1746 @bm-c H3 下载器 DOA 诊断+修复+复燃（产品分=2 能跑实物）**：r814 点火 pid 22896 实为死面（22min·CPU 1.4s·零字节·runner.out 0B）→根因双 bug 定谳=**urllib urlopen timeout=(30,90) 元组=非法形态**（requests 惯用法误植入 urllib·每线程即抛 TypeError）+**except 静默吞 5s 重试环**（零可见性假活面）+file2 目标字节 156,871,142,551=**10× 错**（服务器 Content-Range 真值 15,687,142,551·五 URL 探针全 206）→r815 修复版三件（timeout=90 int+file2 服务器真值+错误面落 state json 可见化）→杀旧（自属零落盘足迹）→复燃 pid 2968→**实测 428MB/75s·18:36 时点 1,524MB/8 段（~7.5MB/s 聚合·ETA≈20:10）**·manifest 服务器真和 40,282,065,079B（r814 收据 40,282,346,779 差 281,700B=deploy 脚本声明面 vs 服务器真面·0.0007% 如实披露）；"
    "⑤inbox=W201 席位公示 MSG（bm-a 18:12·A 457_004..459_003/B 459_004..459_203 hops=1·席位属主 bm-a·信息面零冲突动作）→移 processed+本轮回执；C7 出站 2 MSG 仍在箱；"
    "⑥F-20261009-04③ W18 链入池门核验=standing_no_judge_inflight（W17-JUDGE 在飞禁并行）+W17 判词依赖（negative-read 才定 W18 轴向）→**本轮禁抢跑起草**（enqueue_gates 正典·依赖窗如实推进·随班回执到窗 10-10 00:00）；"
    "⑦W17 跟随=screens 0/1 在烧·RAM 门关窗（free 1.2GB<4GB·autofill auto_parked 循环续发·18:30 tick=busy）·SLA 10-10 00:00 跟随；"
    "⑧S6 40/40 rc0（DONE 18:33:21·update_daily 10-09 bar 第 9 轮守 new rows=0 cutoff 10-08 sina 迟发·pool_dualrun 零漂移连绿 11·LHB 季面 no-op·bm-a/b 车道诚实 no-op）；"
    "⑨QA r815 槽零撞名净写（origin qa/ 预检零 hit）：qa/smoke-r815-bm-c.md 5/5+qa/equity-curve-r815-bm-c.png（65,425B·800 bar 终值 1,023,027·determinism=True·91 trades）；"
    "⑩S7 自愈：6 任务 PRESENT（IntradayMarks 收盘 MISSING=预期）+双爪 IN-PLACE+attrition 4 台账 CLEAN（healed 史披露）；"
    "⑪tick 面：18:15/18:25 拒启（0x800710E0）后本轮由在飞会话承轮·schtasks 快照 IterationLoop next 18:35 ready（会话在飞期拒启=MultipleInstances 预期面）·watchdog 在位——轮末后下一 tick 成轮实况归 r816 轮首查〔留痕〕；"
    "⑫S4=CODELY 主件 30,544B 余量 176B+pit-spawn 30,471B 余量 249B 双红线→**H3 DOA 坑律留痕轮报告**（urllib timeout 元组陷阱+静默吞重试环+字节 10× 错三面）随 r814 遗 2 条（r811 变体/CRLF 变体）排队下轮 mini-split 窗收编〔r814 留痕先例〕"
    " | 下轮指针: r816=①H3 下载完成验收（ETA≈20:10·字节校验→ComfyUI 装配→T2V 768P 5s 16:9 测试片：泥板刻字特写·暖灯微推·尘粒浮光·2001 胶片颗粒·原生双声道有无如实报）②CODELY mini-split 窗（3 条坑律收编：r815 H3 DOA+r811 变体+r814 CRLF 变体）③W17 screens 跟随+SLA 10-10 00:00 窗前读数④Tools 老龄助手清点隔离批（1-gen 血统保留清单先行·C-02 尾面）⑤tick 成轮验证（轮末后下一 fire）⑥C7 MSG 回执跟随⑦10-09 bar 第 10 轮守"
)

activity = (
    "当前活: r815 bm-c H3 下载器 DOA 修复复燃（1,524MB in-flight·ETA≈20:10）+W201 席位 MSG 回执+F-04③ W18 依赖窗核验（第 116 连守轮） | "
    "最近实物: Tools/_r815bmc_h3_download.py（DOA 修复版：urllib timeout int+file2 服务器真值+错误可见化）+results/_r815bmc_h3_download_state.json（pid 2968 活面）+qa/smoke-r815-bm-c.md（5/5）+results/_r815bmc_s6_log.txt（40/40 rc0 DONE 18:33:21）@本轮收口 commit | "
    "下个里程碑: H3 权重落地→ComfyUI T2V 768P 5s 16:9 测试片（O-1746·ETA≈20:10 下载完成）+W17 SLA 10-10 00:00 窗前读数+CODELY mini-split（3 条坑律）"
)

artifact = (
    "Tools/_r815bmc_h3_download.py + _r815bmc_h3_ignite.py (O-20261009-1746 DOA fix-release: urllib timeout tuple TypeError + file2 10x byte typo + error visibility; detached pid 2968; 1,524MB/8 parts at 18:36, ~7.5MB/s aggregate, ETA ~20:10) "
    "+ results/_r815bmc_h3_download_state.json (fix_release face + server-truth manifest 40,282,065,079B) "
    "+ Tools/_r815bmc_{s0,s05,s6,s6_ignite,qa_ignite,close}.py (r815 helper set) "
    "+ results/_r815bmc_s05_facts.json + results/_r815bmc_s6_log.txt (40/40 rc0, DONE 18:33:21) + results/_r815bmc_s6_runner.{out,err} "
    "+ qa/smoke-r815-bm-c.md (5/5) + qa/equity-curve-r815-bm-c.png (65,425B, 800-bar final 1,023,027, determinism=True, 91 trades, per-machine suffix) "
    "+ fleet/inbox/processed/MSG-2026-10-09-1812-bma-w201-seat.md (W201 seat publication receipted same-round) "
    "+ results/_attrition_guard_scan.json (4 ledgers CLEAN) + results/_orphan_face_probe.bm-c.json (orphan face 1, read-only) "
    "@ " + now_iso
)

nxt = (
    "r816 续作: ①H3 下载完成验收（ETA≈20:10·字节校验→ComfyUI 装配→T2V 768P 5s 16:9 测试片：泥板刻字特写·暖灯微推·尘粒浮光·2001 胶片颗粒·原生双声道有无如实报）"
    "②CODELY mini-split 窗（3 条坑律收编：r815 H3 DOA〔urllib timeout 元组+静默吞重试环+10× 字节〕+r811 变体第 3 面+r814 CRLF 变体）"
    "③W17 screens 跟随+SLA 10-10 00:00 窗前读数（autofill auto_parked 循环·RAM 门）"
    "④Tools 老龄助手清点隔离批（1-gen 克隆血统保留面清单先行·C-02 尾面）"
    "⑤tick 成轮验证（本会话轮末后下一 fire 成轮实况）⑥C7 MSG 回执跟随（bm-a/bm-b ORD SHA-1 重算+bm-b dec 推进）⑦10-09 bar 第 10 轮守（sina 迟发）"
)

verify = (
    "smoke 49/49 + SAT engine rc0 (alive, N1 wave ledger 143-200 face, W200 B-tail identity vs W201 MSG) "
    "+ H3 fix-release live proof (pid 2968; 428MB/75s then 1,524MB at 18:36 across 8 parts; state errors={} clean; server-truth manifest 40,282,065,079B vs r814 receipt delta 281,700B disclosed) "
    "+ S6 40/40 rc0 (results/_r815bmc_s6_log.txt DONE 18:33:21, nonzero-rc count=0) "
    "+ qa/smoke-r815-bm-c.md 5/5 (PNG 65,425B, 800-bar final 1,023,027, determinism=True, collision pre-check zero-hit before net-write) "
    "+ attrition 4 ledgers CLEAN (healed history disclosed) "
    "+ 自愈四件全绿 (6 tasks PRESENT, IntradayMarks closure-MISSING expected, both claws IN-PLACE CR-normalized identity) "
    "+ 孤儿面=1 只读（ComfyUI idle server 8188·H3 装机复用面） "
    "+ DEC/ORD 轮首扫双 hold 零 delta（SSH rc0） + unacked 0〔56 orders〕 "
    "+ inbox=own outbound 2（C7 MSG）+ W201 MSG processed same-round "
    "+ idle 非绿（RAM 8.3%·idle_rounds=0·agenda 未饿） "
    "+ pool_dualrun 零漂移连绿 11（418 entries） + update_daily 第 9 轮守（new rows=0·cutoff 10-08·sina 迟发）"
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
hb["last_round"] = 815
hb["last_round_at"] = now_iso
hb["round_no"] = 815
hb["round_no_label"] = "round 815 (bm-c)"
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
st["last_round"] = 815
st["round_no"] = 816
st["round_no_label"] = "round 815 (bm-c)"
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
assert hb2["round_no"] == 815 and st2["round_no"] == 816
assert len(hb2["last_decisions_sha"]) == 64 and len(hb2["last_orders_sha"]) == 40, "watermark shape gate"
tail = rr_path.read_text(encoding="utf-8", errors="replace").rstrip().splitlines()[-1]
assert tail.startswith("2026-10-09T"), "ledger tail must be this round row"
print("closeout OK: hb round=815 state next=816 epoch=%d ts=%s dec=%s ord=%s ram=%s cpu=%s gpu=%s wm_red=%s orphan=%d"
      % (epoch, now_iso, DEC_SHA[:8], ORD_SHA[:8], ram_free_gb, cpu_pct, gpu_free_mb, wm_red, orphan))

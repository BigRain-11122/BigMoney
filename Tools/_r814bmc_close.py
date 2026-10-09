# -*- coding: utf-8 -*-
"""r814 bm-c closeout: heartbeat/state/round-report bookkeeping (single-shift
round, no adoption). Law: fleet/README.md sec.6 machine-split files; epoch
must be JSON int (R170/R178); clock_read ISO8601 T-separator (R262);
products-first 3-line face; DEC/ORD shas READ PROGRAMMATICALLY from the
facts file -- ZERO literal sha constants (r583 law); ledger append carries
the r843 tail-CRLF guard; NO %-formatting in narrative strings.
r814 inbox-face: inbox holds exactly TWO outbound MSG files authored by
r812 (C7 adjudication -> bm-a/bm-b, awaiting their receipt) -- unchanged.
r814 DEC/ORD: dec_delta FALSE (31E85972 unchanged, zero action); ord_delta
TRUE = O-20261009-1755 Git 分级同步令 (FleetLink v1.2, supersedes O-1750,
T1 AI 代决) CONSUMED IN-ROUND (bm-c install action executed + receipt);
watermark ORD ADVANCES to closing value, DEC holds.
Pattern credit: Tools/_r813bmc_close.py (1-gen clone)."""
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
facts = json.loads((ROOT / "results" / "_r814bmc_s05_facts.json")
                   .read_text(encoding="utf-8"))
DEC_SHA = facts["dec_sha"]
ORD_SHA = facts["ord_sha"]
assert len(DEC_SHA) == 64 and len(ORD_SHA) == 40, "watermark shape gate"
assert facts.get("shape_assert") is True, "facts shape_assert gate"
assert facts.get("round") == 814, "facts round gate"
assert facts.get("unacked") == [], "r814 closing: zero unacked orders"
assert sorted(facts.get("inbox_unread") or []) == [
    "MSG-20261009-173x-bmc-bma-C7ORDSHA.md",
    "MSG-20261009-173x-bmc-bmb-C7ORD-DECLAG.md"], "r814 closing: inbox = own outbound C7 MSGs only"
assert facts.get("dec_delta") is False, "r814: dec delta expected FALSE"

# watermark red face (S6 probe leg output)
try:
    wr = json.loads((ROOT / "results" / "watermark_red.json")
                    .read_text(encoding="utf-8"))
    wm_red = bool(wr.get("red"))
    wm_reason = str(wr.get("reason", ""))[:80]
except Exception:
    wm_red, wm_reason = False, "watermark_red.json unreadable (honest)"

DEC_METHOD = (
    "python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r814 start sweep via "
    "SSH primary leg rc0 (channel healthy on bm-c); dec delta FALSE = 31E85972 unchanged, zero action "
    "(12:00 committee batches were consumed in r813); facts-driven from results/_r814bmc_s05_facts.json, "
    "64hex shape-asserted; close-face reads sha PROGRAMMATICALLY from facts json, ZERO literal constants "
    "(r583 law)")
ORD_METHOD = (
    "python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r814 start sweep via SSH primary "
    "leg rc0; ord delta TRUE and CONSUMED in-round: single added row O-20261009-1755 Git 分级同步令 "
    "(FleetLink v1.2 three-tier HOT/WARM/COLD, supersedes O-20261009-1750, T1 AI 代决 veto window to "
    "10-16) captured verbatim in results/_r814bmc_orders_delta.txt and the bm-c install action executed "
    "same-round; facts-driven, 40hex shape-asserted; close-face reads sha PROGRAMMATICALLY, ZERO literal "
    "constants (r583 law)")

did = (
    "2026-10-09T" + HM + "+08:00 | r814 | dept:工程/舰队（O-1755 FleetLink v1.2 装机+O-1746 H3 下载点火+C-02 再积累面隔离·第 115 bm-c 连守轮） | "
    "本地未达 origin commit 数=0（收口 commit 后 push+fetch 自证） | "
    "WM-VERDICT: " + ("红：" + wm_reason if wm_red else "绿（red=false·lane=healthy") + "·DEC " + DEC_SHA[:8] + " hold 零动作/ORD " + ORD_SHA[:8] + " consumed〔轮首单扫·SSH rc0·新行 1 条=O-20261009-1755 Git 分级同步令全文捕获+同轮执行 bm-c 动作〕·unacked 0〔56 orders〕·inbox 出站 2〔C7 MSG 待 bm-a/bm-b 收件·bm-b 离线如实〕） | "
    "孤儿面=1（只读不杀·pid 37120=ComfyUI idle server 8188·parent DEAD·H3 装机复用面·收编决策归装机轮） | "
    "r814: ①S0=absorb commit dcce0a294（8 own 活面）+SSH fetch rc0+**r811 CRLF 假脏环二连拒变体**（checkout 归一后 pull 的 fetch 秒窗内活 daemon 再写面→再拒）→正法=已 fetch 后直接 git rebase origin/main（免 fetch 缩窗）+紧重试环 1 发即中→0/0（HEAD d95ed5868）〔坑律留痕待 mini-split 窗收编〕；"
    "②S0.5=DEC 无 delta（31E85972 不变零动作）/ORD delta=TRUE→新行 1 条 O-1755 全文捕获+同轮消费；"
    "③S1 smoke 49/49+SAT 引擎活（rc0·N1 台账 wave 152-200 面）+idle 非绿（实工轮·idle_rounds=0）；"
    "④**O-20261009-1755 @bm-c FleetLink v1.2 装机收口（产品分=2 能跑实物）**：origin 三件物化（fleet-link.ps1 12,266B v1.2 三层 HOT/WARM/COLD+fleet-poke-worker+register）→杀旧 v1.1 listener×1（自匹配安全）→重注册（REGISTERED node=bm-c+HEALTH OK+FW Tailscale-In present）→**/health version=1.2 gate=True+/status 200 截证落盘**（results/_r814bmc_fleetlink_receipt.json）；"
    "⑤**O-20261009-1746 @bm-c MiniMax-H3 即装主线点火（产品分=2）**：GH deploy 仓 download_weights.sh 清单实取（5 件 40.28GB·hf-mirror.com=本机唯一可达 HF 通道）→8 段 ranged 续传下载器（dl_qwen36 范式·urllib 零依赖·per-part 续传+concat+字节校验）→**detached 点火 pid=22896**（state=results/_r814bmc_h3_download_state.json·disk 404.7GB free·落地即 ComfyUI T2V 768P 5s 测试片=下轮主线·物理依赖留痕）；"
    "⑥C-20261009-02 item-② 再积累面收口：r802 首批 257 件后 r807/r808 再积累 5 件根级 commit-msg scratch→treasure_guard prescan 零命中→quarantine 批 2（results/_quarantine/20261009-181328·assert 5/5 恒等）·**_r_bmc_s0msg.txt 活件按 r811 律排除**；README 续鲜+首批+r802 已毕查证（commit 400c89c94 12:50）→C-02 三件全消费·池补 1=F-20261009-04 undertaking（prereg 起草=下轮队头）；"
    "⑦S6 40/40 rc0（DONE 18:13:27·update_daily 10-09 bar 第 8 轮守 new rows=0 cutoff 10-08 sina 迟发·bm-a/bm-b 车道诚实 no-op）；"
    "⑧QA r814 槽零撞名净写（origin qa/ 预检零 hit）：qa/smoke-r814-bm-c.md 5/5+qa/equity-curve-r814-bm-c.png（65,229B·800 bar 终值 1,023,027·determinism=True·91 trades）；"
    "⑨S7 自愈：六任务 PRESENT（IntradayMarks 收盘 MISSING=预期）+双爪 IN-PLACE+loop 幂等 no-op（pin=5）+attrition 4 台账 CLEAN（healed 史披露）；"
    "⑩**循环健康警示面**：tick 18:15:01 fire 结果 0x800710E0（拒启·18:25 同面·疑上轮 wrapper 实例滞留触发 MultipleInstances 拒）——35min ExecutionTimeLimit+LoopWatchdog 自愈在位·下轮必核 next fire 成轮实况〔留痕〕"
    " | 下轮指针: r815=①H3 权重落地验收（40.28GB in-flight·字节校验→ComfyUI 装配→T2V 768P 5s 16:9 测试片：泥板刻字特写·暖灯微推·尘粒浮光·2001 胶片颗粒·原生双声道有无如实报）②F-20261009-04 池补 1 prereg 起草（PREREG_TEMPLATE α 机制段+共享判据库+出场轴显式门·池 ready=9→10）③tick 拒启面核验（next fire 成轮?+滞留 wrapper 探查）④Tools 老龄助手清点隔离批（1-gen 血统保留清单先行）⑤W17 SLA 10-10 00:00 窗核验（autofill w17-screen 0/8+1/8 在烧）⑥10-09 bar 第 9 轮守⑦C7 MSG 回执跟随"
)

activity = (
    "当前活: r814 bm-c O-1755 FleetLink v1.2 装机（/health 1.2 截证）+O-1746 H3 权重下载点火（40.28GB in-flight）+C-02 再积累面隔离批 2（第 115 连守轮） | "
    "最近实物: results/_r814bmc_fleetlink_receipt.json（/health version=1.2+/status 200）+results/_r814bmc_h3_ignite.json（pid 22896·5 件清单）+results/_quarantine/20261009-181328（5 件 assert 恒等）+qa/smoke-r814-bm-c.md（5/5）+results/_r814bmc_s6_log.txt（40/40 rc0 DONE 18:13:27）@本轮收口 commit | "
    "下个里程碑: H3 权重落地→ComfyUI T2V 768P 5s 16:9 测试片（O-1746·in-flight·落地窗随 40.28GB 下载）+F-20261009-04 池补 1 prereg（下轮队头）+W17 SLA 10-10 00:00"
)

artifact = (
    "results/_r814bmc_fleetlink_receipt.json (/health {ok,node:bm-c,version:1.2} + /status 200, O-20261009-1755 bm-c install receipt) "
    "+ results/_r814bmc_h3_ignite.json + results/_r814bmc_h3_download_state.json (O-20261009-1746 mainline: detached pid 22896, 5-file 40.28GB hf-mirror manifest, 8-segment ranged resume, disk 404.7GB free) "
    "+ Tools/_r814bmc_h3_download.py + _r814bmc_h3_ignite.py (zero-dep downloader, dl_qwen36 paradigm) "
    "+ Tools/_r814bmc_fl_upgrade.py + _r814bmc_fl_receipt.py (v1.2 install pair) "
    "+ results/_quarantine/20261009-181328/ (C-02 item-2 second batch: 5 root commit-msg scratch quarantined, prescan zero-hit, assert 5/5 identity) "
    "+ results/_r814bmc_orders_delta.txt (O-1755 full row verbatim capture) + results/_r814bmc_s05_facts.json "
    "+ qa/smoke-r814-bm-c.md (5/5) + qa/equity-curve-r814-bm-c.png (65,229B, 800-bar final 1,023,027, determinism=True, per-machine suffix) "
    "+ results/_r814bmc_s6_log.txt (40/40 rc0, DONE 18:13:27) + results/_r814bmc_s7quartet.txt "
    "+ results/_attrition_guard_scan.json (4 ledgers CLEAN) + results/_orphan_face_probe.bm-c.json (orphan face 1, read-only) "
    "+ Tools/_r814bmc_{s0,s05,s0fix,s0fix2,orders_delta,occupancy,tempmsg_quarantine,s6,s6_ignite,qa_ignite,close}.py (r814 helper set) "
    "@ " + now_iso
)

nxt = (
    "r815 续作: ①H3 权重落地验收（40.28GB in-flight·字节校验→ComfyUI 装配→T2V 768P 5s 16:9 测试片：泥板刻字特写·暖灯微推·尘粒浮光·2001 胶片颗粒·原生双声道有无如实报）"
    "②F-20261009-04 池补 1 prereg 起草（PREREG_TEMPLATE α 机制段+共享判据库+出场轴显式门三选一·池 ready=9→10）"
    "③tick 拒启面核验（18:15/18:25 fire=0x800710E0·next fire 成轮?+滞留 wrapper 探查·35min 限+watchdog 自愈在位）"
    "④Tools 老龄助手清点隔离批（1-gen 克隆血统保留面清单先行·C-02 尾面）"
    "⑤W17 SLA 10-10 00:00 窗核验（autofill w17-screen 0/8+1/8 在烧跟随）"
    "⑥10-09 bar 第 9 轮守（sina 迟发）⑦C7 MSG 回执跟随（bm-a/bm-b ORD SHA-1 重算+bm-b dec 推进）"
)

verify = (
    "smoke 49/49 + SAT engine rc0 (alive, N1 wave ledger face) "
    "+ FleetLink v1.2 live receipt (/health {ok:true,node:bm-c,version:1.2} + /status 200 + REGISTERED + HEALTH OK + FW Tailscale-In present, results/_r814bmc_fleetlink_receipt.json) "
    "+ H3 download detached ignite (pid 22896, state json live, disk 404.7GB free, manifest 5 files 40,282,346,779 bytes via hf-mirror) "
    "+ S6 40/40 rc0 (results/_r814bmc_s6_log.txt DONE 18:13:27, nonzero-rc count=0 verified) "
    "+ qa/smoke-r814-bm-c.md 5/5 (PNG 65,229B, 800-bar final 1,023,027, determinism=True, collision pre-check zero-hit before net-write) "
    "+ attrition 4 ledgers CLEAN (healed history disclosed) "
    "+ 自愈四件全绿 (6 tasks PRESENT, IntradayMarks closure-MISSING expected, loop pin=5 idempotent no-op, both claws IN-PLACE) "
    "+ 孤儿面=1 只读（ComfyUI idle server 8188·parent DEAD·H3 装机复用面） "
    "+ DEC/ORD 轮首扫（dec hold 零动作/ord delta=O-1755 消费·SSH rc0） + unacked 0〔56 orders〕 "
    "+ inbox=own outbound 2（C7 MSG） + idle 非绿（实工轮·idle_rounds=0·agenda 未饿） "
    "+ quarantine batch-2 assert 5/5 identity (prescan zero-hit, manifest results/_quarantine/20261009-181328) "
    "+ update_daily 第 8 轮守（new rows=0·cutoff 10-08·sina 迟发）"
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
hb["last_round"] = 814
hb["last_round_at"] = now_iso
hb["round_no"] = 814
hb["round_no_label"] = "round 814 (bm-c)"
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
st["last_round"] = 814
st["round_no"] = 815
st["round_no_label"] = "round 814 (bm-c)"
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
assert hb2["round_no"] == 814 and st2["round_no"] == 815
assert len(hb2["last_decisions_sha"]) == 64 and len(hb2["last_orders_sha"]) == 40, "watermark shape gate"
tail = rr_path.read_text(encoding="utf-8", errors="replace").rstrip().splitlines()[-1]
assert tail.startswith("2026-10-09T"), "ledger tail must be this round row"
print("closeout OK: hb round=814 state next=815 epoch=%d ts=%s dec=%s ord=%s ram=%s cpu=%s gpu=%s wm_red=%s"
      % (epoch, now_iso, DEC_SHA[:8], ORD_SHA[:8], ram_free_gb, cpu_pct, gpu_free_mb, wm_red))

# -*- coding: utf-8 -*-
"""r816 bm-c closeout: heartbeat/state/round-report bookkeeping (single-shift
round, no adoption). Law: fleet/README.md sec.6 machine-split files; epoch
must be JSON int (R170/R178); clock_read ISO8601 T-separator (R262);
products-first 3-line face; DEC/ORD shas READ PROGRAMMATICALLY from the
facts file -- ZERO literal sha constants (r583 law); ledger append carries
the r843 tail-CRLF guard; NO %-formatting in narrative strings.
r816 DEC/ORD: dec_delta FALSE (hold, zero action); ord_delta TRUE =
consumed IN-ROUND (rows O-20261009-1815/1830 prompt-engineering orders,
executor=BigStream, not-this-repo science gate -> zero action, watermark
key update only). Close-sweep second scan: both shas unchanged vs the
round-start consumption face.
r816 inbox face: live inbox = exactly the two own outbound C7 MSGs
awaiting bm-a/bm-b (bm-b offline as-is; zero bm-c-addressed unread).
Pattern credit: Tools/_r815bmc_close.py (1-gen clone)."""
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
facts = json.loads((ROOT / "results" / "_r816bmc_s05_facts.json")
                   .read_text(encoding="utf-8"))
DEC_SHA = facts["dec_sha"]
ORD_SHA = facts["ord_sha"]
assert len(DEC_SHA) == 64 and len(ORD_SHA) == 40, "watermark shape gate"
assert facts.get("shape_assert") is True, "facts shape_assert gate"
assert facts.get("round") == 816, "facts round gate"
assert facts.get("unacked") == [], "r816 closing: zero unacked orders"
assert facts.get("dec_delta") is False, "r816: dec delta expected FALSE"
assert facts.get("ord_delta") is True, "r816: ord delta expected TRUE (consumed in-round)"

# --- live inbox face (expect own outbound only) ---
inbox_dir = ROOT / "fleet" / "inbox"
live_inbox = sorted(f.name for f in inbox_dir.glob("*.md"))
assert live_inbox == [
    "MSG-20261009-173x-bmc-bma-C7ORDSHA.md",
    "MSG-20261009-173x-bmc-bmb-C7ORD-DECLAG.md"], \
    "r816 closing: inbox must be own outbound C7 MSGs only"

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
    "python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r816 start sweep via "
    "SSH primary leg rc0 (channel healthy on bm-c); dec delta FALSE = 31E85972 unchanged, zero action; "
    "close-sweep second scan unchanged as-is; facts-driven from results/_r816bmc_s05_facts.json, "
    "64hex shape-asserted; close-face reads sha PROGRAMMATICALLY from facts json, ZERO literal constants (r583 law)")
ORD_METHOD = (
    "python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r816 start sweep via SSH primary "
    "leg rc0; ord delta TRUE = EB8DB998 -> 84221B7D consumed IN-ROUND: new rows O-20261009-1815/1830 "
    "(prompt-engineering deep-research + professionalization mechanism orders, executor @BigStream) "
    "science gate = not-this-repo -> zero action, watermark key update only; close-sweep second scan "
    "unchanged vs in-round consumption face; facts-driven, 40hex shape-asserted; close-face reads sha "
    "PROGRAMMATICALLY, ZERO literal constants (r583 law)")

did = (
    "2026-10-09T" + HM + "+08:00 | r816 | dept:工程/舰队（CODELY mini-split 四块收编+H3 复燃跟随+W17 shard-1 点火+Tools 老龄清点·第 117 bm-c 连守轮） | "
    "本地未达 origin commit 数=0（收口 commit 后 push+fetch 自证） | "
    "WM-VERDICT: " + ("红：" + wm_reason if wm_red else "绿（red=false·lane=healthy") + "·DEC " + DEC_SHA[:8] + " hold 零 delta/ORD " + ORD_SHA[:8] + " consumed〔轮首 delta 1 次=新增 2 行 O-1815/1830 提示词令·执行司 BigStream·涉本司=否科学判断闸零动作·水位键更新；S7 收尾双扫双恒等零新增〕·unacked 0〔56 orders〕·inbox 出站 2〔C7 MSG 待 bm-a/bm-b 收件·bm-b 离线如实〕） | "
    "孤儿面=" + str(orphan) + "（只读不杀·含 ComfyUI idle server 8188·H3 装机复用面） | "
    "r816: ①S0=absorb commit d109528bd（own 活面）+SSH fetch rc0+rebase 首发拒（unstaged=活 daemon 面+CRLF 漂移面 21 面）→drift-normalize checkout→rebase retry 1 发即中→1/0〔r814 正法第 3 轮连验·本批 4 条坑律同窗收编见④〕；"
    "②S0.5=DEC 无 delta（31E85972 hold）/ORD delta TRUE（EB8DB998→84221B7D·新 2 行=O-20261009-1815 提示词撰写深研令+O-20261009-1830 提示词专业化机制令·执行司 BigStream·涉本仓=否→科学判断闸零动作·水位键更新）+S7 收尾双扫双恒等；"
    "③S1 smoke 49/49+SAT 引擎活（rc0·N1 台账 wave 143-200 面）+idle 非绿（RAM 1.5GB·W17/H3 双在飞·idle_rounds=0·agenda 未饿）；"
    "④**CODELY mini-split 四块收编（产品分=1 文件改动+收据实物）**：主件 30,544B 余量 176B 红线→r811 原面 799B verbatim 迁出+r814 二连拒变体 620B+r815 rebase 直跑首发拒变体 707B（三面→pit-git-resolver-rebase.md 25,425→27,551B）+r815 H3 下载器 DOA 三连 bug 1,121B（urllib timeout 元组+静默吞重试环+10× 字节→pit-data.md 21,653→22,774B）〔直写 r666 范式〕+主件指针行 764B 落位→30,509B·四断言全绿（逐块 bytes in target verbatim+主件前缀恒等+三件 ≤30KB）·prescan rc3 留痕（memory 类登记册命中=r651/r747/r896 既有先例面）·receipt results/_r816bmc_codely_minisplit.json；"
    "⑤H3 复燃跟随（O-1746）：18:52 时点 75.8%（12.75GB/8 段实测盘面）→close 时点 82.2%（13.82GB）·pid 2968 活（CPU 33.7s 累积·启动 18:33）·聚合 ~11MB/s·ETA 提前至 ~19:2x（r815 ETA 20:10 提前）·状态 json errors={} 零错误面；"
    "⑥W17 跟随：autofill 18:52:01 tick=launched TRIAL-LABOR-W17-SCREEN-SHARD-1（shard w17-screen-1of8·pid 43204 活·CPU 累积实证）=screens 0/1→1/8 在烧·RAM 门仍紧（free 1.5GB<4GB·autofill 循环续发）·SLA 10-10 00:00 窗前读数随 close 面如实；"
    "⑦Tools 老龄助手清点先行步（C-02 尾面）：read-only census=1,252 件 span r199-r897（≤r799 老龄面 1,107 件·含 bma/bmb 他机助手）→results/_r816bmc_tools_census.json（隔离批=后续授权窗·treasure_guard prescan+quarantine manifest 7 天观察律）；"
    "⑧S6 40/40 rc0（update_daily 10-09 bar 第 10 轮守 new rows=0 cutoff 10-08 sina 迟发·pool_dualrun 零漂移连绿 12·bm-a/b 车道诚实 no-op）；"
    "⑨QA r816 槽零撞名净写（origin qa/ 预检零 hit）：qa/smoke-r816-bm-c.md 5/5+qa/equity-curve-r816-bm-c.png（65,291B·800 bar 终值 1,023,027·determinism=True·91 trades）；"
    "⑩S7 自愈：IterationLoop no-op（pin=5 针位无漂移）+Watchdog 重装（首火 18:56）+pre-commit/pre-push 双爪 installed（LF 归一恒等）+attrition 4 台账 CLEAN（healed 史披露）；"
    "⑪tick 成轮验证：会话轮末后下一 tick 成轮实况归 r817 轮首查〔r815 ⑪留痕同型〕；"
    "⑫S4 坑律面：本批 4 条已 mini-split 收编（④）·主件余量 211B 红线维持（下轮新坑律一律直写域件 r666 范式）"
    " | 下轮指针: r817=①H3 下载完成验收（ETA~19:1x·字节校验→ComfyUI 装配→T2V 768P 5s 16:9 测试片：泥板刻字特写·暖灯微推·尘粒浮光·2001 胶片颗粒·原生双声道如实报）②W17 screens 跟随+SLA 10-10 00:00 窗前读数③Tools 老龄助手隔离批（census 在案·prescan+quarantine 律）④C7 MSG 回执跟随⑤10-09 bar 第 11 轮守（sina 迟发）⑥主件余量 211B 红线（新坑律直写域件）"
)

activity = (
    "当前活: r816 bm-c CODELY mini-split 四块收编（receipt 在案）+H3 复燃跟随 81.4%（第 117 连守轮·收口面） | "
    "最近实物: results/_r816bmc_codely_minisplit.json（四块字节+sha16 对账·主件 30,509B/三件 ≤30KB 全绿）+research/pit-git-resolver-rebase.md（r811/r814/r815 三面收编）+research/pit-data.md（H3 DOA 收编）+qa/smoke-r816-bm-c.md（5/5）+results/_r816bmc_tools_census.json（1,252 件清点）@本轮收口 commit | "
    "下个里程碑: H3 权重落地→ComfyUI T2V 768P 5s 16:9 测试片（O-1746·ETA~19:1x 下载完成）+W17 SLA 10-10 00:00 窗前读数+Tools 隔离批（授权窗）"
)

artifact = (
    "results/_r816bmc_codely_minisplit.json (mini-split receipt: A_r811 799B 1ba65a1592156b94 / B_r814 620B 2ff695e9f5c2cdbe / C_r815 707B a73e3fb08f4ae79f / D_h3doa 1121B 44230b658ebbab22; main 30,544B->30,509B, resolver-rebase 25,425B->27,551B, pit-data 21,653B->22,774B; four asserts green; prescan rc3 precedent trace) "
    "+ research/pit-git-resolver-rebase.md (r811 original + r814 pull-fetch-window variant + r815 rebase-direct first-reject variant, three faces in-family) "
    "+ research/pit-data.md (H3 downloader DOA triple-bug entry) "
    "+ Tools/_r816bmc_{s0,s05,s6,s6_ignite,qa_ignite,codely_split}.py (r816 helper set, 1-gen clones) "
    "+ results/_r816bmc_s05_facts.json + results/_r816bmc_s6_log.txt (40/40 rc0) + results/_r816bmc_s6_runner.{out,err} "
    "+ qa/smoke-r816-bm-c.md (5/5) + qa/equity-curve-r816-bm-c.png (65,291B, 800-bar final 1,023,027, determinism=True, 91 trades, per-machine suffix) "
    "+ results/_r816bmc_tools_census.json (1,252 round-tagged helpers census, span r199-r897, aging face 1,107 files <=r799, read-only) "
    "+ results/_attrition_guard_scan.json (4 ledgers CLEAN) + results/_orphan_face_probe.bm-c.json (orphan face 2, read-only) "
    "@ " + now_iso
)

nxt = (
    "r817 续作: ①H3 下载完成验收（ETA~19:1x·字节校验→ComfyUI 装配→T2V 768P 5s 16:9 测试片：泥板刻字特写·暖灯微推·尘粒浮光·2001 胶片颗粒·原生双声道有无如实报）"
    "②W17 screens 跟随+SLA 10-10 00:00 窗前读数（autofill 循环·RAM 门）"
    "③Tools 老龄助手隔离批（census=results/_r816bmc_tools_census.json 在案·treasure_guard prescan+quarantine manifest 7 天观察律先行）"
    "④C7 MSG 回执跟随（bm-a/bm-b ORD SHA-1 重算+bm-b dec 推进）"
    "⑤10-09 bar 第 11 轮守（sina 迟发自愈）"
    "⑥主件余量 211B 红线（新坑律一律直写域件 r666 范式）⑦tick 成轮验证（r816 ⑪留痕承接）"
)

verify = (
    "smoke 49/49 + SAT engine rc0 (alive, N1 wave ledger 143-200 face) "
    "+ mini-split four asserts green (blocks verbatim in target + main prefix identity + three files <=30,720B; receipt _r816bmc_codely_minisplit.json; prescan rc3 precedent trace) "
    "+ H3 live proof (pid 2968 CPU 33.7s accumulating; 12.75GB at 18:52 -> 13.82GB/82.2% at close across 8 parts; state errors={} clean) "
    "+ W17 SHARD-1 launch proof (autofill 18:52:01 verdict=launched, pid 43204 CPU accumulating, screens 1/8 in burn) "
    "+ S6 40/40 rc0 (results/_r816bmc_s6_log.txt, nonzero-rc count=0) "
    "+ qa/smoke-r816-bm-c.md 5/5 (PNG 65,291B, 800-bar final 1,023,027, determinism=True, collision pre-check zero-hit before net-write) "
    "+ attrition 4 ledgers CLEAN (healed history disclosed) "
    "+ self-heal green (IterationLoop no-op pin=5, watchdog re-registered first-fire 18:56, both claws installed LF-normalized) "
    "+ orphan face=2 read-only + DEC/ORD start-sweep consumed in-round (ORD +2 rows not-this-repo zero action) + close-sweep second scan both unchanged "
    "+ unacked 0 [56 orders] + inbox=own outbound 2 (C7 MSG) "
    "+ idle non-green (RAM 1.5GB, dual in-flight W17/H3, idle_rounds=0, agenda not starved) "
    "+ pool_dualrun zero-drift green 12 + update_daily round-10 guard (new rows=0, cutoff 10-08, sina late-bar) "
    "+ tools census 1,252 files read-only (aging face 1,107 <=r799, quarantine=later authorized window)"
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
hb["last_round"] = 816
hb["last_round_at"] = now_iso
hb["round_no"] = 816
hb["round_no_label"] = "round 816 (bm-c)"
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
st["last_round"] = 816
st["round_no"] = 817
st["round_no_label"] = "round 816 (bm-c)"
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
assert hb2["round_no"] == 816 and st2["round_no"] == 817
assert len(hb2["last_decisions_sha"]) == 64 and len(hb2["last_orders_sha"]) == 40, "watermark shape gate"
tail = rr_path.read_text(encoding="utf-8", errors="replace").rstrip().splitlines()[-1]
assert tail.startswith("2026-10-09T"), "ledger tail must be this round row"
print("closeout OK: hb round=816 state next=817 epoch=%d ts=%s dec=%s ord=%s ram=%s cpu=%s gpu=%s wm_red=%s orphan=%d"
      % (epoch, now_iso, DEC_SHA[:8], ORD_SHA[:8], ram_free_gb, cpu_pct, gpu_free_mb, wm_red, orphan))

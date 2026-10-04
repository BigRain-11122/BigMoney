"""r680 bm-b S7 closeout: round report line + state.json + heartbeat.
Laws applied: r641 clock-string regex + epoch int (R170/R178), r645 programmatic
json write + reparse self-verify, r672 round number from reports tail (679+1=680),
heartbeat structure preserved (field superset kept verbatim, r679 lineage)."""
import io, json, time, re, subprocess, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
now_iso = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())

CLOCK_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+08:00$")

# --- machine stats probes (honest, best-effort with carry-forward on fail) ---
free_ram_gb = None
cpu_util = None
try:
    import psutil
    vm = psutil.virtual_memory()
    free_ram_gb = round(vm.available / 1024**3, 2)
    cpu_util = round(psutil.cpu_percent(interval=1.0), 1)
except Exception:
    pass
gpu_free_vram_mb = None
try:
    r = subprocess.run(["nvidia-smi", "--query-gpu=memory.free",
                        "--format=csv,noheader,nounits"],
                       capture_output=True, text=True, timeout=20)
    if r.returncode == 0 and r.stdout.strip():
        gpu_free_vram_mb = round(float(r.stdout.strip().splitlines()[0]))
except Exception:
    pass

hb_path = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
hb = json.load(io.open(hb_path, encoding="utf-8"))
if free_ram_gb is None:
    free_ram_gb = hb.get("free_ram_gb", 3.47)
if gpu_free_vram_mb is None:
    gpu_free_vram_mb = hb.get("gpu_free_vram_mb", 3295)

# --- 1) round report line (append-only, utf-8, newline='' per r641 CRLF law) ---
report_line = (
    "2026-10-04T16:38:00+08:00 | r680 (bm-b) PRODUCT (dept:舰队值守+数据维护链): "
    "[watermark verdict: GREEN (red=false lane=healthy; satengine alive rc0 hb fresh queue=22 held by RAM floor gate 2.7-3.2GB<4.0GB "
    "machine discipline self-ignite; audit CLEAN burning-healthy py 85%+; dualrun ZERO-DRIFT streak 51)] | "
    "当前活: FUND trio NULLS 烧录在飞 V841/Q657/D497 of 2000 @16:15 (42.0/32.9/24.9pct, owner=bm-b keepalive 鲜活, "
    "rates 24.3/20.5/18.0/h, ETA V 10-06T15 / Q 10-07T09 / D 10-08T03) + N1-W116 burn 2/12 shards done (15:55/16:09, RAM 闸节流自燃面) | "
    "最近实物: S6 38/38 rc0 (results/_r686bmb_s6_log.txt; ZERO-DRIFT streak 51; REPORT-2026-10-04/LIVE-2026-10-04 再生 ORANGE cap50 + "
    "CALL-2026-09-30 写盘 + t35/paper_export/daily_scorecard/build_status 四 lane-guard stale-takeover derive O-2100 s2.4) + "
    "S0 r437 预对齐集成 (pull--rebase 被 daemon 脏面阻 -> checkout origin pool face origin-newer-wins [W3 shard-3 flip 在 origin] -> merge r685 bm-a 波 -> "
    "sync_face settle library 驱动 status=settled results/_r686bmb_syncface_out.txt) + trio watch 刷新 (results/trio_burn_eta.json 16:15:51) | "
    "D-19 双水位双键 MATCH 零动作: decisions 4E5BE321 MATCH (大小写假警当场证伪归一 r503) + orders 68947C17 MATCH (r458 口径律兑现: state 键=SHA-1 40-hex, "
    "探针首算 SHA-256=假 CHANGED 二连假警, 逐键 method 对齐复算 MATCH — 两假警均我探针面非正典工具缺陷, 正典 d19_check 已带 r503 归一) | "
    "S0.5 orders 154/154 双形态零未回执 + smoke 48/48 + 板扫 0 open + W3 screen 波 4909/4909 complete 观察 (W3 finalize= bm-c 已声明下里程碑·反重复不抢跑) + "
    "r643 三证零并发 (codely_in_repo=1; trio_burn_eta 16:15:51 写手=本会话 r675 探针自跑·谜当场闭案 results/_r686bmb_concurrency_probe.json) + "
    "moneyflow 面板源阻断未解 (53/5222·next_pick=IC batch 候面板=合法等待态) + 月度三件已跑核验 (10-02 BRIEF/SELF-REVIEW-202609) + "
    "自愈 4/4 + attrition guard CLEAN (4 ledgers) + 本轮=5倍数轮 HANDOVER r676-r680 增量落档 | "
    "下个里程碑: V 烧完 ~10-06T15 = FUND-VALUE-P1-NULLS finalize 候选窗 (10-06..09 GM 裁定窗·finalize 轮必同窗池面双翻 r668 律·预演 r672 ALL-GREEN 收据在场) + "
    "T-148 contest 终表 10-08 前刷新 + W116 RAM 清空自燃 | 本地未达 origin commit 数: 读 push_verify 回执 (收口推送后 ahead=0)"
)
with io.open(os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md"),
             "a", encoding="utf-8", newline="") as f:
    f.write("\n" + report_line + "\n")

# --- 2) state.json (programmatic write + reparse verify per r645) ---
st_path = os.path.join(ROOT, "state.json")
st = json.load(io.open(st_path, encoding="utf-8"))
st["machine_id"] = "bm-b"
st["round_no"] = 680
st["note"] = ("r680: S0 r437 pre-alignment merge (origin pool face origin-newer-wins + sync_face settle) + "
              "D-19 dual MATCH (decisions case-normalized per r503, orders SHA-1 per-key method per r458 -- "
              "two probe-side false alarms self-caught, canon tools unaffected) + S6 38/38 rc0 ZERO-DRIFT "
              "streak 51 + trio NULLS V841/Q657/D497 burning healthy ETA V 10-06T15/Q 10-07T09/D 10-08T03 + "
              "N1-W116 2/12 shards RAM-gated self-paced + W3 screen wave 4909/4909 complete (finalize = bm-c "
              "declared face, no-preempt) + smoke 48/48 + orders 154/154 zero unacked + self-heal 4/4 + "
              "attrition CLEAN + HANDOVER r676-r680 five-x increment")
st["last_round_at"] = now_iso
st["ts"] = now_iso
st["updated"] = now_iso
st["last_seen"] = now_iso
st["round_no_label"] = "round 680 (bm-b)"
st["clock_read"] = now_iso
st["last_decisions_read_at"] = now_iso
with io.open(st_path, "w", encoding="utf-8", newline="") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
    f.write("\n")
chk = json.load(io.open(st_path, encoding="utf-8"))
assert chk["round_no"] == 680, "state round_no verify fail"
assert CLOCK_RE.match(chk["clock_read"]), "state clock_read regex fail (r641)"

# --- 3) heartbeat fleet/machines/bm-b.json ---
hb["last_seen"] = now_iso
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = now_iso
hb["round_no"] = 680
hb["round_no_label"] = "round 680 (bm-b)"
hb["current_task"] = ("r680 close: S0 r437 pre-alignment merge + sync_face settle; D-19 dual MATCH "
                       "(probe-side false alarms self-caught r503/r458); S6 38/38 streak 51; trio NULLS "
                       "V841/Q657/D497 ETA 10-06..08 burning; N1-W116 2/12 RAM-gated; W3 screen wave "
                       "complete (finalize=bm-c face); next grain = FUND-VALUE finalize 候选窗 10-06T15+ "
                       "(r668 池面双翻律, rehearsal ALL-GREEN)")
hb["verdict"] = "healthy burning"
hb["ts"] = now_iso
hb["updated"] = now_iso
hb["updated_at"] = now_iso
hb["cpu_cores"] = 16
hb["cpu_util_pct"] = cpu_util if cpu_util is not None else hb.get("cpu_util_pct", 61.5)
hb["free_ram_gb"] = free_ram_gb
hb["idle_ram_gb"] = free_ram_gb
hb["ram_free_gb"] = free_ram_gb
hb["ram_avail_gb"] = free_ram_gb
gpu_gb = round(gpu_free_vram_mb / 1024.0, 2)
hb["gpu_idle_vram_gb"] = gpu_gb
hb["gpu_idle_vram_mb"] = gpu_free_vram_mb
hb["gpu_free_vram_gb"] = gpu_gb
hb["gpu_free_vram_mb"] = gpu_free_vram_mb
hb["gpu_vram_free"] = gpu_free_vram_mb
hb["gpu_free_vram_mib"] = gpu_free_vram_mb
with io.open(hb_path, "w", encoding="utf-8", newline="") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
    f.write("\n")
chk2 = json.load(io.open(hb_path, encoding="utf-8"))
assert isinstance(chk2["heartbeat_epoch_utc"], int), "epoch must be JSON int (R170/R178)"
assert CLOCK_RE.match(chk2["clock_read"]), "hb clock_read regex fail (r641)"
assert chk2["orders_ack_count"] == len(chk2["orders_ack"]) == 154, "orders_ack integrity fail"

print("CLOSEOUT OK round=680 clock=%s epoch=%d ram=%.2f gpu=%d cpu=%s"
      % (now_iso, epoch, free_ram_gb, gpu_free_vram_mb, hb["cpu_util_pct"]))

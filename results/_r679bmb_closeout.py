"""r679 bm-b S7 closeout: round report line + state.json + heartbeat.
Laws applied: r641 clock-string regex + epoch int (R170/R178), r645 programmatic
json write + reparse self-verify, r672 round number from reports tail,
heartbeat structure preserved (field superset kept verbatim)."""
import io, json, time, re, subprocess, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
now_iso = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())

CLOCK_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+08:00$")

# --- machine stats probes (honest, best-effort with carry-forward on probe fail) ---
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
    "2026-10-04T16:01:30+08:00 | r679 (bm-b) PRODUCT (dept:舰队值守+数据维护链): "
    "[watermark verdict: GREEN (red=false; satengine alive hb 61s queue=24 held by py headroom gate 82.7%>=75% self-ignite; "
    "post_review REPORT face ✓45/✗0; audit CLEAN py 85.4%=trio+w3-screen 合法占用; dualrun ZERO-DRIFT streak 51)] | "
    "当前活: FUND trio NULLS 烧录在飞 V833/Q650/D491 of 2000 @15:55 (41.6/32.5/24.6pct, owner=bm-b keepalive 15:46:12 鲜活, "
    "rates 24.2/20.7/18.2/h, ETA V 10-06T16 / Q 10-07T09 / D 10-08T02) + MASS_TRIAL_W3 screen shard w3-screen-1of4 (bm-b autofill r199 claim, "
    "bm-c r480 prereg 席位面) | 最近实物: S6 38/38 rc0 单段 (results/_r679bmb_s6_log.txt; ZERO-DRIFT streak 51; update_lhb 本轮 refetch rc0 "
    "=r675 exit2 SSL 自愈兑现; REPORT/LIVE-2026-10-04 再生 ORANGE cap50) + trio watch 刷新 (results/trio_burn_eta.json) | "
    "本轮同窗=死会话收养: r678 会话 15:45 S7 中途断气 (W118 freeze 五面+席位已 commit 且经 daemon push DELIVERED origin -- merge-base 实证; "
    "S6 chain 15:29 FAILS=[] 收据在场; D-19 双键 MATCH 收据在场) -> 本轮 r679 承接收口: MSG-2026-10-04-1520 (bm-c MASS_TRIAL_W3 席位公示 无需回执) "
    "move 收账 + 全部簿记补齐 (state/心跳/轮报); r643 三证探测=本仓零并发 (他 codely=Phantom/minigame 各自仓) | "
    "orders/D-19 双扫: 154/154 zero-unacked 双跑 (S0.5 收养收据 + S7.5 本轮复扫 results/_r679bmb_d19_check.txt), decisions 4E5BE321 + "
    "orders 68947C17 双键 MATCH 水位零动作 | smoke 48/48 | 板扫 169 票 0 open | 自愈 4/4 (loop pin=2 no-op / watchdog 16:00 首燃 / 双爪 OK) | "
    "下轮指针: trio 看护续航 + V 烧完 (~10-06T16) = FUND-VALUE-P1-NULLS 首族 finalize 候选窗 (10-06..09 GM 裁定窗; finalize 轮必同窗池面双翻 r668 律) + "
    "w3-screen-1of4 烧完收口 + 引擎点火观察 (queue 24, py<75% 自燃) | 本地未达 origin commit 数: 读 push_verify 回执 (收口推送后 ahead=0)"
)
with io.open(os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md"),
             "a", encoding="utf-8", newline="") as f:
    f.write("\n" + report_line + "\n")

# --- 2) state.json (programmatic write + reparse verify per r645) ---
st_path = os.path.join(ROOT, "state.json")
st = json.load(io.open(st_path, encoding="utf-8"))
st["machine_id"] = "bm-b"
st["round_no"] = 679
st["note"] = ("r679: r678 dead-session closeout adopted -- r678 died mid-S7 15:45 "
              "(W118 freeze five faces + seat commit DELIVERED via daemon push, merge-base verified; "
              "S6 chain FAILS=[] 15:29; D-19 dual MATCH receipts on file); this round: MSG-1520 move "
              "收账 + bookkeeping backfill + S6 38/38 rc0 (ZERO-DRIFT streak 51, update_lhb refetch "
              "rc0 self-heal) + D-19 dual-scan zero unacked 154/154 both keys MATCH + smoke 48/48 + "
              "trio NULLS V833/Q650/D491 burning healthy ETA V 10-06T16/Q 10-07T09/D 10-08T02 + "
              "MASS_TRIAL_W3 screen shard w3-screen-1of4 claimed by bm-b autofill + satengine alive "
              "queue=24 (W116+W118 materialized, ignition held by py headroom gate, self-ignites) + "
              "S7 self-heal 4/4")
st["last_round_at"] = now_iso
st["ts"] = now_iso
st["updated"] = now_iso
st["last_seen"] = now_iso
st["round_no_label"] = "round 679 (bm-b)"
st["clock_read"] = now_iso
st["last_decisions_read_at"] = now_iso
with io.open(st_path, "w", encoding="utf-8", newline="") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
    f.write("\n")
chk = json.load(io.open(st_path, encoding="utf-8"))
assert chk["round_no"] == 679, "state round_no verify fail"
assert CLOCK_RE.match(chk["clock_read"]), "state clock_read regex fail (r641)"

# --- 3) heartbeat fleet/machines/bm-b.json ---
hb["last_seen"] = now_iso
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = now_iso
hb["round_no"] = 679
hb["round_no_label"] = "round 679 (bm-b)"
hb["current_task"] = ("r679 close: r678 dead-session closeout adopted (W118 freeze DELIVERED verify + "
                      "MSG-1520 move 收账); trio NULLS V833/Q650/D491 ETA 10-06..08 burning; w3-screen-1of4 "
                      "shard in flight; engine queue=24 held by py headroom gate self-ignite; next grain = "
                      "FUND-VALUE finalize 候选窗 10-06+ (r668 池面双翻律) + w3-screen 收口")
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

print("CLOSEOUT OK round=679 clock=%s epoch=%d ram=%.2f gpu=%d cpu=%s"
      % (now_iso, epoch, free_ram_gb, gpu_free_vram_mb, hb["cpu_util_pct"]))

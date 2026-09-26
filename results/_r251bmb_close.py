# r251 bm-b close: state 250->251 + round report line + heartbeat (epoch int law) -- r97 pattern
import json, glob, os, time, subprocess

now = time.strftime("%Y-%m-%d %H:%M:%S")
now_short = time.strftime("%Y-%m-%d %H:%M")
now_iso = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")

# --- resource sample (heartbeat fields, same faces as prior rounds) ---
import psutil
cpu_pct = psutil.cpu_percent(interval=2)
vm = psutil.virtual_memory()
free_ram_gb = round(vm.available / 1024**3, 1)
total_ram_gb = round(vm.total / 1024**3, 1)
gpu_free_mb = None
try:
    out = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                         capture_output=True, text=True, timeout=10)
    gpu_free_mb = int(out.stdout.strip().splitlines()[0])
except Exception:
    pass
if gpu_free_mb is None:
    gpu_free_mb = 0

# --- 1. state.json round 250 -> 251 ---
sp = "logs/iteration-loop/state.json"
st = json.load(open(sp, encoding="utf-8-sig"))
st["round_no"] = 251
st["did"] = ("r251: maintenance round sixth census (zero-claim honest); S6 28 legs all exit 0 "
             "(weekend no-ops, cutoff 09-24 [09-25 Mid-Autumn holiday]); orders 79/79 both scans zero unacked; "
             "pool_starvation 6th consecutive -> S8.3 three-face supply check = legal idle "
             "(MF-IC-P1 panel still source-blocked bm-a self-heal in flight; board 0 open; no P1 face)")
st["verdict"] = "GREEN"
st["next"] = ("09-28 Monday new-bar full chain (grid_paper 5 accounts first marks + wired exit_overrides first paper run "
              "+ bm-c T-16 takeover evaluation 15:30); 10-01 month-first three-pack (science_audit/monthly_briefing/self_review) "
              "+ corr-watch W3 + REGIME_GUARD v3 date-gate enforce window; 10-31 six-member first review all-HOLD")
st["last_round_ts"] = now_short
st["last_result"] = ("S6 28 legs all exit 0 (weekend no-ops honest, cutoff 09-24; live.paper 6 anchors OK, "
                     "x2 watch ENGULF 0.0143 probation as recorded; t35 open_fill PASS zero-pending; t24 22/22 drift=0; "
                     "promotion 0/22 honest; aggr/alloc/grid marks no-op at cutoff; market_clock CALL-2026-09-24 "
                     "ORANGE_COOL sleeves=2 idempotent regen; smoke 25/25; watermark py_low_board_clear py 0.4% legal idle; "
                     "pool_starvation 6th round supply-check legal per S8.3; orders 79/79 both scans zero unacked")
st["current_task"] = ("r251 closed: maintenance round sixth census; next action face = 09-28 Monday new-bar full chain "
                      "+ T-16 takeover evaluation 15:30")
st["last_tick"] = time.strftime("%H:%M")
for k in ("updated_at", "last_seen", "ts", "updated"):
    st[k] = now_short
st["last_run"] = "R251 " + time.strftime("%Y-%m-%dT%H:%M:%S")
st["last_round_at"] = st["last_run"]
json.dump(st, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("state.json: round_no ->", st["round_no"])

# --- 2. round report line (binary append, CRLF, r97 pattern) ---
rr = ("%s | r251 bm-b | maintenance round sixth census (zero-claim honest), dept:\u5de5\u7a0b+\u8230\u961f | "
      "WM-VERDICT: py_low_board_clear = legal idle (probe 13:22 window n=4 avg py 0.4%%; board 0 open / "
      "bandit next_pick claimed-parked / pool 0 ready 43/43 done) | did: S0 stash-pull-pop FF up-to-date; "
      "S0.5 \u53cc\u626b 79/79 \u96f6\u672a\u56de\u6267 + decisions.md \u7f3a\u4f4d\u96f6\u52a8\u4f5c (P-32); "
      "S1 smoke 25/25; S3 board census zero-claim honest (queue J-items all done, Optuna gated per \u89e3\u5c01\u5224\u636e, "
      "T-77 slice-4 GPU lane harvested by bm-a r244, T-78 remaining faces wait 09-28 new bar, MF-IC-P1 panel "
      "source-blocked bm-a self-heal in flight); S6 28 legs all exit 0 (weekend no-ops cutoff 09-24 [09-25 "
      "Mid-Autumn holiday]; live.paper 6 anchors OK; x2 watch ENGULF 0.0143 probation as recorded; t35 "
      "open_fill PASS zero-pending; t24 22/22 drift=0; promotion 0/22 honest; aggr/alloc/grid marks no-op at "
      "cutoff; market_clock CALL-2026-09-24 ORANGE_COOL sleeves=2 idempotent regen; paper_export 2026-09-24 "
      "written; scorecard 6 traders; daily report REPORT-2026-09-26 4 faces; compute_audit pool_starvation "
      "6th consecutive -> S8.3 supply check legal idle; token L1 +1 leg ~6135 tok local) | next: 09-28 Monday "
      "new-bar full chain (grid_paper 5 accounts first marks + wired exit_overrides first paper run + bm-c "
      "T-16 takeover evaluation 15:30); 10-01 month-first three-pack + REGIME_GUARD v3 enforce window | "
      "state 250->251, heartbeat epoch int-verified\r\n" % now)
with open("logs/iteration-loop/round_reports.md", "ab") as fh:
    fh.write(rr.encode("utf-8"))
print("round report appended")

# --- 3. heartbeat bm-b.json (epoch MUST be JSON int -- R170/R178 law) ---
hp = "fleet/machines/bm-b.json"
hb = json.load(open(hp, encoding="utf-8-sig"))
tokens = []
for p in sorted(glob.glob("fleet/orders/O-*.md")):
    stem = os.path.splitext(os.path.basename(p))[0]
    tokens.append("-".join(stem.split("-")[:3]))
hb["orders_ack"] = " ".join(tokens)
hb["last_seen"] = now_short
hb["heartbeat_epoch_utc"] = int(time.time())
hb["clock_read"] = now_iso
hb["current_task"] = st["current_task"]
hb["cpu_cores"] = 16
hb["free_ram_gb"] = free_ram_gb
hb["gpu_free_vram_gb"] = round(gpu_free_mb / 1024, 1)
hb["total_ram_gb"] = total_ram_gb
hb["cpu_util_pct"] = cpu_pct
hb["round_no"] = 251
hb["verdict"] = "GREEN"
hb["cores"] = 16
hb["idle_ram_gb"] = free_ram_gb
hb["gpu_free_vram_mb"] = gpu_free_mb
hb["idle_ram_mb"] = int(free_ram_gb * 1024)
hb["gpu_idle_vram_mb"] = gpu_free_mb
json.dump(hb, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

# --- self-verify (E1 law: verify after write) ---
chk = json.load(open(hp, encoding="utf-8-sig"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
chk2 = json.load(open(sp, encoding="utf-8-sig"))
assert chk2["round_no"] == 251
print("heartbeat: epoch=%d (int OK) clock=%s round=%d ack_tokens=%d ram_free=%.1fGB gpu_free=%dMB cpu=%.1f%%"
      % (chk["heartbeat_epoch_utc"], chk["clock_read"], chk["round_no"], len(tokens), free_ram_gb, gpu_free_mb, cpu_pct))
# POST-RUN CORRECTION (r251 closing double-scan catch, zero leakage): the orders_ack token pattern above
# was copied from r97-era script (_r97_ack.py 3-segment tokens) -- STALE. Current law (r220, see
# Tools/orders_diff.py header 'Ack format contract' + _r241bma_wrapup.py header) = FULL filename incl .md
# suffix. The 3-segment write made the closing scan report 79/79 false-unacked (format mismatch vs fleet
# canonical bm-a face). Fixed same minute by full-filename regeneration + Tools/orders_diff.py re-verify
# (diff empty 79/79). Lesson: before copying a pattern from a historical one-shot script, grep the LIVE
# canonical carrier for the current contract; run orders diffs via Tools/orders_diff.py, never hand-rolled.

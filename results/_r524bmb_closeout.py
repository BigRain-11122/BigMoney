"""r524 bm-b closeout bookkeeping: round report + state.json + heartbeat (format-preserving)."""
import json, io, os, time, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
now_iso = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
epoch = int(time.time())

# --- detect EOL helper ---
def eol_of(path):
    with open(path, "rb") as f:
        data = f.read(4000)
    return "\r\n" if b"\r\n" in data else "\n"

def load_json(path):
    with io.open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, obj, indent=1):
    eol = eol_of(path)
    text = json.dumps(obj, ensure_ascii=False, indent=indent) + eol
    text = text.replace("\n", eol)
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)

# --- 1. state.json ---
sp = os.path.join(ROOT, "state.json")
st = load_json(sp)
st["round_no"] = 524
st["note"] = ("r524 COMPLETED: W28 finalize one-pass same-round closed loop (17th engine wave bm-b eighth-owned; "
    "pre-gate 12/12 r310 ls-tree + audit.machine=bm-b ownership verify + payload 2,200=2000A+200B; "
    "prev 423,948 = W27-on-origin derive (bm-a r540 landed mid-round = chain gate auto-released) + 2,200 = 426,148 chain-linear, "
    "K=59,520 [drafting-window floor 55,120 + W26/W27 landed +4,400 slip disclosed]; S5 4/4 PASS [mu-drift 0.0045 / sigma +0.11% / "
    "A p95 0.3278 vs 0.3262 / K-lift +0.0007 @n_eff_held 423,948, canon_flip NOT performed]; merged mu -0.0915 sigma 0.2449 n=59,520; "
    "ledger block persisted in product per r509; first-run no-rerun per r538; sec.7/8 backfill same-window + default-wave selftest PASS (r522); "
    "push FF a49cd8062 delivery verified) + r523-closeout violation consumed as lesson (bm-a r540 restored my accidental deletion of bm-c r336 "
    "products = r519 family 5th; this round zero surgical full-tree payloads, targeted adds only) + S6 37 legs rc0 holiday no-ops "
    "(dualrun streak 14/3; audit pool_starvation/supply_floor flags answered = W29 bm-c rotation slot pending, between-wave transient; "
    "WM py_low_board_clear legal) + S7 self-heal all-green (loop pin=2 no-op, watchdog S4U, claw installed, attrition CLEAN) "
    "= next bm-b round: W29=bm-c slot watch (not mine), post-holiday first-bar S6 processing when market resumes, next bm-b engine slot=W31 per rotation")
st["last_round_at"] = now_iso
st["last_round_ts"] = epoch
st["ts"] = now_iso
st["updated"] = now_iso
st["updated_at"] = now_iso
save_json(sp, st, indent=1)
print("state.json: round_no=524, ts=" + now_iso)

# --- 2. heartbeat fleet/machines/bm-b.json ---
hp = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
hb = load_json(hp)
try:
    import psutil
    vm = psutil.virtual_memory()
    free_ram = round(vm.available / (1024**3), 1)
    import ctypes
    # gpu via existing probe files if nvidia-smi unavailable in this context: fall back to prior fields
    gpu_free = hb.get("gpu_free_vram_gb", 0.0)
    gpu_free_mb = hb.get("gpu_free_vram_mb", 0)
    try:
        out = os.popen("nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits").read().strip()
        if out:
            gpu_free_mb = int(float(out.splitlines()[0]))
            gpu_free = round(gpu_free_mb / 1024, 1)
    except Exception:
        pass
    cpu_cores = psutil.cpu_count(logical=True)
    cpu_util = psutil.cpu_percent(interval=None)
except Exception:
    free_ram = hb.get("free_ram_gb", 0.0)
    cpu_cores = hb.get("cpu_cores", 16)
    cpu_util = hb.get("cpu_util_pct", 0.0)

hb["last_seen"] = now_iso
hb["heartbeat_epoch_utc"] = epoch  # int per R170/R178
hb["clock_read"] = now_iso  # T-separator per R262
hb["current_task"] = ("W28 engine wave finalize closed same-round (chain 426,148, K=59,520, S5 4/4); engine idle honest, "
    "W29=bm-c rotation slot watch")
hb["cpu_cores"] = cpu_cores
hb["free_ram_gb"] = free_ram
hb["idle_ram_gb"] = free_ram
hb["gpu_free_vram_gb"] = gpu_free
hb["gpu_idle_vram_gb"] = gpu_free
hb["gpu_free_vram_mb"] = gpu_free_mb
hb["gpu_idle_vram_mb"] = gpu_free_mb
hb["cpu_util_pct"] = cpu_util
hb["round_no"] = 524
hb["verdict"] = ("healthy: W28 closed (finalize landed origin a49cd8062); watermark green; board closed; "
    "S6 all rc0; pool_starvation flag = W29 bm-c slot transient, answered")
save_json(hp, hb, indent=1)
assert isinstance(hb["heartbeat_epoch_utc"], int)
print("heartbeat: epoch=%d (int verified), free_ram=%.1fGB, gpu_free=%.1fGB" % (epoch, free_ram, gpu_free))

# --- 3. round report append ---
rp = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
line = (
"2026-10-01T22:22:00+08:00 | r524 | bm-b | [watermark verdict: GREEN (red=false; 22:10 probe py_low_board_clear=legal idle: board closed + bandit empty + no runnable batch; engine queue 0 honest = W28 closed same-round, W29=bm-c rotation slot not yet registered = between-wave transient)] | "
"main artifact: N1-W28 ENGINE WAVE FINALIZE CLOSED (17th engine wave bm-b 8th own, dept:research): pre-gate 12/12 = origin ls-tree completeness (r310) + audit.machine=bm-b ownership three-verify + json.loads all green + payload 2,200=2,000A+200B continuous-slice sum (_r524bmb_w28_verify.py); "
"finalize one-pass: prev 423,948 (W27-on-origin derive, bm-a r540 landed mid-round = chain gate auto-released, W27 file pulled into working tree BEFORE finalize per r538 prev-scan law) + 2,200 = 426,148 CHAIN-LINEAR, K=59,520 (drafting-window floor 55,120 + W26/W27 landed +4,400 slip disclosed per r336 precedent); "
"S5 4/4 PASS (W28-only mu -0.0879 vs W25 anchor -0.09240 drift 0.0045<0.02 / sigma 0.2449 vs 0.24460 = +0.11%<10% / A p95 0.3278 vs 0.3262 delta +0.0016<0.05 / K-lift +0.0007<=0.02 @n_eff_held 423,948, canon_flip NOT performed governance face); merged pool mu -0.0915 sigma 0.2449 n=59,520; ledger block persisted in product science_gates.ledger per r509; first-run no-rerun per r538; sec.7/8 mechanical backfill same-window (r307 two-state) + post-backfill default-wave selftest PASS (r522 law) | "
"chain-order discipline: finalize held until W27 landed (r518 double-head law) | "
"r523-closeout violation consumed as lesson: bm-a r540 (b526746ed) restored my r523 closeout's accidental deletion of bm-c r336 products (r519 family 5th occurrence); THIS round zero surgical full-tree payloads: targeted pathspec adds + regular commits + FF push only | "
"S6 37 legs all rc0 holiday no-ops (dualrun ZERO-DRIFT streak 14/3; compute_audit idle-starvation pool_starvation+supply_floor flags ANSWERED: W29=bm-c rotation slot registration expected in bm-c next 10-min round, my slot W28 closed same-round with finalize = not a supply failure; py_watermark py_low_board_clear legal; update_daily 0 rows cutoff 2026-09-30 holiday; CALL-2026-09-30 ORANGE_COOL idempotent regen; REPORT-2026-10-01+LIVE-2026-10-01 regenerated; bm-b lanes astock/etf/rev_osc/minute_feed all fresh no-op; host=bm-a guard legs honest skips) | monthly trio already-landed skip (per r523 verify) | "
"evidence: n1_w28_results.json on origin (a49cd8062 FF verified by fetch+log), selftest PASS, attrition guard CLEAN (healed 4-row historical shrink annotated), orders double-scan 0 unacked, inbox 0, S1 smoke 47/47, D-19 SHA MATCH-unchanged zero action, engine alive (heartbeat 14s queue 0 idle honest) | "
"executive 3-line: NOW=W28 wave fully closed, engine idle awaiting W29 (bm-c slot); LATEST=results/perpetual_faces/n1_w28_results.json on origin (a49cd8062, 22:07) + research/PERPETUAL_N1_W28_PREREG.md sec.7/8 backfilled; NEXT=W29=bm-c registration watch (not mine), post-holiday first-bar S6 processing when market resumes (~10-09), next bm-b engine slot=W31 per rotation, window <=48h | "
"local-not-at-origin commits: 0 at closeout push (self-verified post-push) | [via bm-b]")
eol = eol_of(rp)
with io.open(rp, "a", encoding="utf-8", newline="") as f:
    f.write(line + eol)
print("round report: r524 line appended")

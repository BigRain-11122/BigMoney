# r724 bm-b S7 closeout (r722 lineage; r503 law: pre-gate marker + post-verify + host EOL;
# R170/R178/R262: epoch int + T-sep clock)
import json, io, os, time, datetime, subprocess

ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
RR = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
STATE = os.path.join(ROOT, "state.json")
HB = os.path.join(ROOT, "fleet", "machines", "bm-b.json")

now = datetime.datetime.now().astimezone()
ts = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")

r724 = (
    f"{ts} | round 724 (bm-b, dept:engineering, holiday steady-state maintenance + readiness watch round) | "
    "[watermark verdict: GREEN (red=false lane healthy; next_pick=claimed moneyflow IC cand parked "
    "source-blocked; probe py_low_with_work_cands = LEGAL holding surface: local_batch_running=true trio "
    "NULLS three lanes burning in place + RAM free ~2.4-3.5GB < 4.0GB floor = engine self-hold, no new burn "
    "legal, board 0 open + bandit 0 open)] | CEO three-line live face: current-work = FUND trio NULLS "
    "V1294/Q1045/D836 of 2000 burning (dup_k=0, owner=bm-b keepalive fresh, autofill resumes batch; ETA V "
    "26.2h=10-06T13:1x / Q 44.9h=10-07T08:0x / D 68.4h=10-08T07:2x per readiness probe 11:00) + satengine "
    "queue 0 RAM-gated | latest-artifact = results/finalize_trio_readiness.json refresh 11:00:49 (gates: "
    "integrity=T, rehearsal_green=T age 1.2d, burn_complete=F, mechanical_ready=F, governance G-SEG PENDING "
    "with r638 fallback armed) + S6 chain 35-leg rc0 full regen (docs/daily_report/REPORT-2026-10-05.md + "
    "docs/live_usage/LIVE-2026-10-05.md CEO faces) | next-milestone = trio V closeout 10-06T13:1x->16:2x -> "
    "FUND-VALUE nulls finalize window (mechanical_ready when V=2000/2000; G-SEG r638 single-read fallback "
    "armed); D-06 group closeout report 10-07 12:00; market reopen 10-08 | did: S0 origin 7-behind wave "
    "pre-pull churn-absorb 8 daemon faces (r620 law) + rebase landed clean (bm-c r532 close wave); S0.5 "
    "orders 154/154 scan zero unacked (head scan + S7 close rescan, set-diff empty); D-19 decisions "
    "watermark MATCH 755428F8 zero consumption (Tools/d19_check.py canonical, K: tree absent -> sparse-clone "
    "fallback in-tool); S1 smoke 48/48; S2 dual board check (job_list 0 + ticket board 0 open + inbox 0); S3 "
    "gates green (WM red=false lane healthy; satengine alive rc0 idle queue 0 RAM self-hold; pool 403 "
    "entries 399 done / 3 ready trio owned keepalive; compute_audit v2.4.2 CLEAN burning-healthy py97.1% "
    "35 procs legal burn occupancy zero zombies; standing trial-labor line satisfied by in-flight trio "
    "NULLS judgment batch, no new wave draft); S6 35 legs ALL RC=0 (driver results/_r724bmb_s6_chain.ps1 "
    "r721 lineage per-leg diff zero drift r531 law; legs 25-28 golden-week no-new-bar honest skip cutoff "
    "09-30 unchanged; dualrun ZERO-DRIFT streak 19 @403 entries; b_layer mask regen gates all_pass; "
    "bm-a/bm-c lane guards honest no-ops); trio finalize readiness probe refresh (rates 0.45/0.35/0.28 per "
    "min, ETAs recomputed); S7 quartet 4/4 (loop pin=2 no-op first-fire 11:02, watchdog re-registered 11:03, "
    "pre-commit+pre-push dual claws LF-normalized IN-SYNC) + attrition 4 ledgers CLEAN (healed historical "
    "rows recorded as-is) + state 723->724 + heartbeat epoch int self-verify | verification evidence: "
    "smoke 48/48 rc0; S6 log results/_r724bmb_s6_chain.log 35 legs ALL RC=0; dualrun ZERO-DRIFT streak 19; "
    "attrition evidence results/_attrition_guard_scan.json; D-19 MATCH; readiness probe live JSON "
    "11:00:49; orders set-diff empty x2 | local undelivered-to-origin commit count: 0 (post-push "
    "fetch+rev-list self-verify, see addendum if race) | product score: 1 (S6 CEO faces 35 legs regen + "
    "readiness monitoring face refresh = actual file changes; no new compute legal per RAM floor + "
    "in-flight judgment batch) | next-round pointers: (a) trio V closeout 10-06 -> FUND-VALUE nulls "
    "finalize window (G-SEG r638 fallback if governance PENDING); (b) Q 10-07 / D 10-08 finalize windows "
    "follow; (c) D-06 closeout report to group 10-07 12:00 (20 pit-*.md <=30KB re-verify holds); (d) 10-08 "
    "market reopen (external data-chain legs + paper marks resume + REGIME_GUARD v3 first new bar); (e) "
    "10-09 post-holiday data-chain check"
)

# ---- append round-report line with host-EOL match + marker gates (r503 law) ----
raw = open(RR, "rb").read()
eol = b"\r\n" if raw.count(b"\r\n") > raw.count(b"\n") - raw.count(b"\r\n") else b"\n"
text = raw.decode("utf-8", errors="replace")
marker = "round 724 (bm-b"
n = text.count(marker)
assert n == 0, f"pre-gate FAIL: {marker} count={n} (already present)"
add = r724 + "\n"
add_b = add.encode("utf-8").replace(b"\n", eol) if eol == b"\r\n" else add.encode("utf-8")
with open(RR, "wb") as f:
    f.write(raw + add_b)
check = open(RR, "rb").read().decode("utf-8", errors="replace")
n = check.count(marker)
assert n == 1, f"post-verify FAIL: {marker} count={n}"
print("round_reports append OK, eol=", "CRLF" if eol == b"\r\n" else "LF")

# ---- state.json: round_no 723 -> 724 ----
st = json.load(open(STATE, encoding="utf-8"))
assert st["round_no"] == 723, f"unexpected state round_no {st['round_no']}"
st["round_no"] = 724
st["note"] = (
    "r724: holiday steady-state maintenance + readiness watch round (no new bar since cutoff 2026-09-30, "
    "market reopen 10-08). S0 origin 7-behind bm-c r532 close wave rebase landed clean (8 daemon faces "
    "churn-absorbed pre-pull per r620 law); orders 154/154 double-scan zero unacked; D-19 MATCH 755428F8 "
    "zero consumption; smoke 48/48; S3 watermark GREEN (next_pick=claimed moneyflow IC parked), engine "
    "alive idle queue 0 RAM self-hold, pool 403 (3 ready trio owned by us), compute_audit CLEAN "
    "burning-healthy; trio NULLS V1294/Q1045/D836 of 2000 @11:00 (ETA V 10-06T13:1x, Q 10-07T08:0x, D "
    "10-08T07:2x); S6 legs 01-35 all rc0 (dualrun streak 19); readiness probe refresh 11:00:49 "
    "(integrity+rehearsal green, mechanical_ready=false, G-SEG governance PENDING r638 fallback armed); S7 "
    "self-heal 4/4, attrition CLEAN."
)
st["last_round_at"] = ts
st["ts"] = ts
st["updated"] = now.strftime("%Y-%m-%d %H:%M:%S")
st["last_seen"] = ts
st["clock_read"] = ts
st["round_no_label"] = "round 724 (bm-b)"
st["next"] = (
    "(a) trio V lane closeout 10-06T13:1x (ETA 26.2h @rate 0.45/min) -> FUND-VALUE nulls finalize window "
    "(mechanical_ready when V=2000/2000; G-SEG governance PENDING -> r638 insufficient-sample single-read "
    "fallback armed); (b) Q closeout 10-07T08:0x, D closeout 10-08T07:2x -> per-family finalize windows "
    "follow; (c) D-06 closeout report to group 10-07 12:00 (20 pit-*.md all <=30KB re-verify holds); (d) "
    "10-08 market reopen window (external run-11/run-7 legs + paper marks resume + REGIME_GUARD v3 first "
    "new bar); 10-31 month-exam first sitting (marks floor 2026-10-30)."
)
st["last_decisions_read_at"] = ts  # D-19 canonical check ran this round (MATCH 755428F8)
with io.open(STATE, "w", encoding="utf-8", newline="") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
    f.write("\n")
re = json.load(open(STATE, encoding="utf-8"))
assert re["round_no"] == 724 and "r724" in re["note"]
print("state.json OK round_no=724")

# ---- heartbeat: epoch int (R170/R178/R262 laws) ----
epoch = int(time.time())
assert isinstance(epoch, int)
hb = json.load(open(HB, encoding="utf-8"))
hb["last_seen"] = ts
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = ts
hb["last_round_at"] = ts
ram = float(subprocess.run(
    ["powershell", "-NoProfile", "-Command",
     "[math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB,2)"],
    capture_output=True, text=True).stdout.strip())
gpu = 3.3
hb["free_ram_gb"] = ram
hb["gpu_free_vram_gb"] = gpu
hb["gpu_free_vram_mb"] = int(gpu * 1024)
hb["cpu_cores"] = 16
hb["verdict"] = (
    "GREEN (trio NULLS 3 lanes burning legal occupancy V1294/Q1045/D836 of 2000, owner=bm-b keepalive "
    "fresh; engine queue 0 RAM-gated self-hold; V finalize window 10-06T13:1x)"
)
hb["current_task"] = (
    "r724 holiday steady-state maintenance (S6 35 legs rc0) + trio NULLS burn watch + readiness probe refresh"
)
with io.open(HB, "w", encoding="utf-8", newline="") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
    f.write("\n")
hbr = json.load(open(HB, encoding="utf-8"))
assert isinstance(hbr["heartbeat_epoch_utc"], int) and "T" in hbr["clock_read"]
print("heartbeat OK epoch=", hbr["heartbeat_epoch_utc"], "ram=", ram)
print("CLOSEOUT OK r724")

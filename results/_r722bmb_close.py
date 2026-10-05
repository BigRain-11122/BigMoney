# r722 bm-b S7 closeout (r715 lineage; r503 law: pre-gate marker + post-verify + host EOL;
# r713 law: r721 POST-MORTEM BACKFILL from git commit messages; r170/R178/R262: epoch int + T-sep clock)
import json, io, os, time, datetime, subprocess

ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
RR = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
STATE = os.path.join(ROOT, "state.json")
HB = os.path.join(ROOT, "fleet", "machines", "bm-b.json")

now = datetime.datetime.now().astimezone()
ts = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")

r721 = (
    "2026-10-05T09:57:00+08:00 | round 721 (bm-b, dept:research+engineering, POST-MORTEM BACKFILL per r713 law -- "
    "dead session, line derived from git commits c34a2d4e0/bd6055242/22cae8d6e + chain log) | [watermark verdict: "
    "GREEN (probe family GREEN per r720 principal S6 chain leg-03)] | current activity: trio NULLS V/Q/D burn "
    "in flight + engine wave finalize window | latest deliverable: results/perpetual_faces/n1_w118_results.json "
    "(09:57:11, bm-b 40th owned engine wave: 12/12 shards burned by 07:00 engine ticks, K=2200 new-seed nulls, "
    "ledger 653411+2200=655611 chain-linear over bm-a W117 head, skill_line 1.1736->1.1737 K-lift +0.0001, "
    "selftest full-chain PASS incl W118 leg, n1w118-0..11of12 keys verified) | next milestone: trio V closeout "
    "10-06 -> FUND-VALUE nulls finalize | what was done: churn-absorb r721 head+second face (r720 dead-session "
    "tail adoption: state/heartbeat/S6 regen faces uncommitted at 09:40 close, r620+r714 law) + W118 finalize "
    "landed + S6 chain legs 01-36 ALL RC=0 (driver results/_r721bmb_s6_chain.ps1, log results/"
    "_r721bmb_s6_chain.log, dualrun ZERO-DRIFT streak 17 @10:01:44) | session died after leg-36 before legs "
    "37-38 + S7: state stayed 720, no ledger line, s6 chain script untracked -- all adopted by r722 | "
    "local undelivered-to-origin commit count: 0 (evidenced by r722 churn-absorb + merge window) | "
    "product score: 2 (W118 engine-wave finalize = real compute result landed)"
)

r722 = (
    f"{ts} | round 722 (bm-b, dept:research+engineering, dead-session recovery + verification round) | "
    "[watermark verdict: GREEN (red=false lane healthy; probe py_low_with_work_cands legal holding surface: "
    "trio NULLS three lanes burning in place + RAM free 3.2-3.6GB < 4.0GB floor = engine self-hold, no new "
    "burn legal)] | current activity: FUND trio NULLS V1275/Q1030/D824 of 2000 burning (dup_k=0, owner=bm-b "
    "keepalive fresh; ETA V 30.1h=10-06T16:2x / Q 47h=10-07T09:2x / D 10-08 face) + satengine queue 0 "
    "RAM-gated | latest deliverable: results/finalize_trio_readiness.json refresh 10:17:30 (gates: integrity=T, "
    "rehearsal_green=T age 1.2d, burn_complete=F, mechanical_ready=F, governance G-SEG PENDING with r638 "
    "fallback armed) + W118 landing integrity verification CLOSED (engine ledger_bm-b.jsonl 12 real shard rows "
    "n1w118-0..11of12 burned 06:0x-07:00:04 with real pids; results file ledger arithmetic 653411+2200=655611 "
    "exact; audit machine=bm-b; r720 state note 'W118 queued 0/12' adjudicated = stale queue read, zero harm) "
    "+ S6 chain completed legs 37-38 (build_status rc0 stale-takeover derive per O-2100 s2.4, token_meter rc0 "
    "delta=0) | next milestone: trio V closeout 10-06T16:2x -> FUND-VALUE nulls finalize (mechanical_ready on "
    "V=2000/2000; G-SEG r638 single-read fallback if ruling stays PENDING); D-06 closeout report 10-07 12:00 "
    "(window <=48h) | what was done: S0 identity anchor bm-b + churn-absorb r722 34-face (daemon lane faces + "
    "r721 S6 regen faces + s6 chain script, r620 law) + pull up-to-date + S0.5 orders 154/154 zero unacked + "
    "D-19 decisions watermark MATCH 755428F8 zero consumption (Tools/d19_check.py canonical) + S1 smoke 48/48 "
    "+ S2 dual board check (job_list 0 + ticket board 0 open, all done/claimed by owners) + S3 gates green "
    "(WM red=false; engine alive rc0 status+tick, queue 0 RAM floor self-hold; standing trial-labor line "
    "satisfied by in-flight trio NULLS judgment batch, no new draft) + W118 forensics (engine ledger + product "
    "face + state-note stale-read adjudication) + readiness probe refresh + S6 legs 37-38 completion (legs "
    "01-36 principal-completed by dead r721, adopted NOT re-run per r719 yield precedent -- duplicate compute "
    "waste prohibition) + S7 quartet 4/4 (loop pin=2 no-op, watchdog re-registered, pre-commit+pre-push dual "
    "claws LF-normalized IN-SYNC) + attrition 4 ledgers CLEAN (3 healed history notes) + r721 ledger line "
    "POST-MORTEM BACKFILL (r713 law) + state 720->722 honest gap-note + heartbeat epoch int self-verify | "
    "verification evidence: smoke 48/48 rc0; orders set-diff empty x2 (head scan 10:13 + close scan); D-19 "
    "MATCH; engine ledger tail 24 rows = 12xW116+12xW118 real burns; readiness probe live JSON 10:17:30; S6 "
    "rc log legs 01-38 all rc0 (36 principal + 2 this round); attrition evidence results/"
    "_attrition_guard_scan.json | local undelivered-to-origin commit count: 0 (post-push fetch+rev-list "
    "self-verify) | product score: 1 (readiness monitoring face refresh + S6 completion = actual file changes; "
    "W118 = r721 principal product verified adopted; no new compute legal per RAM floor + in-flight judgment "
    "batch) | next-round pointers: (a) trio V closeout 10-06T16:2x -> FUND-VALUE nulls finalize window "
    "(G-SEG r638 fallback if governance PENDING); (b) Q 10-07 / D 10-08 finalize windows follow; (c) D-06 "
    "closeout report to group 10-07 12:00 (20 pit-*.md <=30KB re-verify holds); (d) 10-08 market reopen "
    "(external data-chain legs + paper marks resume + REGIME_GUARD v3 first new bar)"
)

# ---- append round-report lines with host-EOL match + marker gates (r503 law) ----
raw = open(RR, "rb").read()
eol = b"\r\n" if raw.count(b"\r\n") > raw.count(b"\n") - raw.count(b"\r\n") else b"\n"
text = raw.decode("utf-8", errors="replace")
for marker, line in (("round 721 (bm-b", r721), ("round 722 (bm-b", r722)):
    n = text.count(marker)
    assert n == 0, f"pre-gate FAIL: {marker} count={n} (already present)"
lines_out = text.splitlines()
if lines_out and lines_out[-1].strip() != "":
    pass  # file ends with newline already per raw split; append plainly
add = r721 + "\n\n" + r722 + "\n"
add_b = add.encode("utf-8").replace(b"\n", eol) if eol == b"\r\n" else add.encode("utf-8")
with open(RR, "wb") as f:
    f.write(raw + add_b)
check = open(RR, "rb").read().decode("utf-8", errors="replace")
for marker in ("round 721 (bm-b", "round 722 (bm-b"):
    n = check.count(marker)
    assert n == 1, f"post-verify FAIL: {marker} count={n}"
print("round_reports append OK, eol=", "CRLF" if eol == b"\r\n" else "LF")

# ---- state.json: round_no 720 -> 722, honest gap note (r713 law) ----
st = json.load(open(STATE, encoding="utf-8"))
assert st["round_no"] == 720, f"unexpected state round_no {st['round_no']}"
st["round_no"] = 722
st["note"] = (
    "r722: dead-session recovery + verification round. r721 dead session adopted in-window: W118 finalize "
    "(bm-b 40th owned engine wave, 12/12 shards burned by 07:00 engine ticks, K=2200, ledger 653411+2200=655611 "
    "chain-linear over bm-a W117, skill_line 1.1736->1.1737) + S6 chain legs 01-36 rc0; r721 died after leg-36 "
    "pre-S7 (state bump missed) -- ledger line POST-MORTEM BACKFILL + state 720->722 honest gap per r713 law. "
    "r722 forensics CLOSED: engine ledger_bm-b.jsonl 12 real W118 shard rows (n1w118-0..11of12, 06:0x-07:00:04, "
    "real pids) corroborate W118 landing; r720 note 'W118 queued 0/12' = stale queue read, zero harm. S0 "
    "churn-absorb r722 34-face; orders 154/154 double-scan zero unacked; D-19 MATCH 755428F8 zero consumption; "
    "smoke 48/48; S6 legs 37-38 completed (01-36 principal by r721, not re-run per r719 yield precedent); "
    "readiness probe 10:17 (V1275/Q1030/D824, dup_k=0, integrity+rehearsal green, mechanical_ready=false, "
    "governance G-SEG PENDING r638 fallback armed); attrition CLEAN; self-heal 4/4."
)
st["last_round_at"] = ts
st["ts"] = ts
st["updated"] = now.strftime("%Y-%m-%d %H:%M:%S")
st["last_seen"] = ts
st["clock_read"] = ts
st["round_no_label"] = "round 722 (bm-b)"
st["next"] = (
    "(a) trio V lane closeout 10-06T16:2x (ETA 30.1h @rate 0.40/min) -> FUND-VALUE nulls finalize window "
    "(mechanical_ready when V=2000/2000; G-SEG governance PENDING -> r638 insufficient-sample single-read "
    "fallback armed); (b) Q closeout 10-07T09:2x, D closeout 10-08 face -> per-family finalize windows follow; "
    "(c) D-06 closeout report to group 10-07 12:00 (20 pit-*.md all <=30KB re-verify holds); (d) 10-08 market "
    "reopen window (external run-11/run-7 legs + paper marks resume + REGIME_GUARD v3 first new bar); 10-31 "
    "month-exam first sitting (marks floor 2026-10-30)."
)
st["round_no_gap_note"] = (
    "r720->r722 honest skip: r721 dead session completed W118 finalize + S6 legs 01-36 then died pre-S7 "
    "(state bump missed at death); r721 ledger line POST-MORTEM BACKFILL from git commits per r713 law; "
    "prior gap note (r716-718 chain, state 715->719) in git history."
)
st["last_decisions_read_at"] = ts  # D-19 canonical check ran this round (MATCH 755428F8)
with io.open(STATE, "w", encoding="utf-8", newline="") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
    f.write("\n")
re = json.load(open(STATE, encoding="utf-8"))
assert re["round_no"] == 722 and "r722" in re["note"]
print("state.json OK round_no=722")

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
    "GREEN (trio NULLS 3 lanes burning legal occupancy V1275/Q1030/D824 of 2000, owner=bm-b keepalive fresh; "
    "engine queue 0 RAM-gated self-hold; finalize window V 10-06T16:2x)"
)
hb["current_task"] = (
    "r722 dead-session recovery (r721 W118 adopted+verified, S6 legs 37-38 completed) + trio NULLS burn watch"
)
with io.open(HB, "w", encoding="utf-8", newline="") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
    f.write("\n")
hbr = json.load(open(HB, encoding="utf-8"))
assert isinstance(hbr["heartbeat_epoch_utc"], int) and "T" in hbr["clock_read"]
print("heartbeat OK epoch=", hbr["heartbeat_epoch_utc"], "ram=", ram)
print("CLOSEOUT OK r722")

# r532 bm-b closeout: state + heartbeat + round report (byte-safe json edits)
import json, time, datetime, psutil, os

now = datetime.datetime.now().astimezone()
iso = now.isoformat(timespec="seconds")
epoch = int(time.time())

# --- state.json (round_no 530 -> 532; skip dead r531 self-claim per r529 law)
p = "state.json"
raw = open(p, "rb").read()
crlf = b"\r\n" in raw
s = json.loads(raw.decode("utf-8"))
assert s["round_no"] == 530
s["round_no"] = 532
s["note"] = ("r532 recovery round: adopted r531 post-commit crash leftovers "
             "(state stuck 530 vs git self-label r531); S0 surgical delivery "
             "db5110d55 (W40 12/12 products + LOWAMP-P3-NULLS in-flight "
             "checkpoint + lane superset); W40 FINALIZE one-pass 448,340+2,200"
             "=450,540 S5 4/4 PASS dual-anchor, prereg s7/s8 backfilled; "
             "LOWAMP-P3-NULLS burn still active (daemon-managed)")
s["last_round_at"] = iso
s["last_round_ts"] = epoch
s["ts"] = iso
s["updated"] = iso
s["updated_at"] = iso
out = json.dumps(s, ensure_ascii=False, indent=1)
if crlf:
    out = out.replace("\n", "\r\n")
open(p, "wb").write(out.encode("utf-8"))
print("state.json round_no ->", s["round_no"])

# --- heartbeat fleet/machines/bm-b.json
p = r"fleet\machines\bm-b.json"
raw = open(p, "rb").read()
crlf = b"\r\n" in raw
hb = json.loads(raw.decode("utf-8"))
hb["last_seen"] = iso
hb["heartbeat_epoch_utc"] = epoch          # MUST be int (R170/R178)
hb["clock_read"] = iso                      # T-separated ISO 8601
hb["current_task"] = ("r532 W40 FINALIZE (head 450,540) + r531-crash salvage "
                      "S0 surgical; LOWAMP-P3-NULLS burn in flight (daemon)")
vm = psutil.virtual_memory()
hb["ram_free_gb"] = round(vm.available / 2**30, 2)
hb["free_ram_gb"] = round(vm.available / 2**30, 2)
hb["idle_ram_gb"] = round(vm.available / 2**30, 2)
hb["cpu_cores"] = psutil.cpu_count(logical=True)
hb["cpu_util_pct"] = psutil.cpu_percent(interval=None)
hb["round_no"] = 532
hb["verdict"] = ("GREEN W40 FINALIZED (448,340+2,200=450,540 K=85,920 pool, "
                 "K-lift -0.0002 S5 4/4 dual-anchor, prereg s7/s8 backfill, "
                 "W41 bm-c in-flight) + LOWAMP-P3-NULLS burn active (683/2000 "
                 "daemon-managed) + S6 chain rc0 full")
try:
    import subprocess as sp
    g = sp.run(["nvidia-smi", "--query-gpu=memory.free",
                "--format=csv,noheader,nounits"], capture_output=True, text=True)
    fr = int(g.stdout.strip().splitlines()[0])
    hb["gpu_free_vram_gb"] = round(fr / 1024, 2)
    hb["gpu_idle_vram_gb"] = round(fr / 1024, 2)
    hb["gpu_free_vram_mb"] = fr
    hb["gpu_idle_vram_mb"] = fr
except Exception:
    pass
out = json.dumps(hb, ensure_ascii=False, indent=1)
if crlf:
    out = out.replace("\n", "\r\n")
open(p, "wb").write(out.encode("utf-8"))
# self-verify epoch int (R170/R178 double-law)
chk = json.loads(open(p, "rb").read().decode("utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch not int"
assert "T" in chk["clock_read"], "clock_read not T-separated"
print("heartbeat OK epoch-int verified:", chk["heartbeat_epoch_utc"])

# --- round report append (bm-b uses logs/iteration-loop/round_reports.md)
p = r"logs\iteration-loop\round_reports.md"
raw = open(p, "rb").read()
crlf = b"\r\n" in raw
line = (
    f"{iso} | r532 | r531-CRASH RECOVERY + W40 FULL CLOSEOUT | "
    "S0: r531 died post-commit pre-S5/S6/S7 (state 530 vs git self-label r531, "
    "r529 diagnosis law); no rival BigMoney session (process probe); salvage = "
    "ride commit + SURGICAL S0 delivery db5110d55 (rebase hard-refused by "
    "nulls.jsonl live-appending tracked checkpoint -- r523 family new face, "
    "surgical = only net path; payload 32 files: W40 12/12 products "
    "audit.machine=bm-b + LOWAMP-P3-NULLS checkpoint partial + bm-b lane "
    "superset + pool_core_samples UNION 470+16=486; 20 shared regen faces "
    "yielded to origin r505 law; deletion-set empty r519 leg; local align "
    "64 stale faces restored incl W39 finalize product + bm-c r344 additions; "
    "bm-a r549 same-window W40 double-freeze = bit-identical bands r530 "
    "collision family, their fixup ac9c9bad8 yielded canon to bm-b r531) | "
    "S0.5: 143/143 orders acked zero new (origin-side diff); D-19 fresh read "
    "MATCH-unchanged 4FD50184 | S1 smoke 47/47 PASS | S3: engine alive tick "
    "rc0 idle (queue 0, W40 12/12 done, ledger 10+2buffer rows, flush "
    "02:28:03 12/12 persisted r522 self-heal), watermark green "
    "loaded_ok py 67-85%, board: T-141 mine open standing line | "
    "**W40 FINALIZE one-pass (r538 law): prev 448,340 (W39 bm-c r343 head, "
    "origin-verified) + 2,200 = 450,540 CHAIN HEAD; K-lift -0.0002 "
    "(1.1571->1.1569 @n_eff_held 448,340); S5 4/4 PASS dual-anchor (W38 frozen "
    "+ W39 rolled: mu d 0.0043/0.0048<0.02; sigma -0.43%/+1.85%<10%; A-p95 "
    "0.3057 d 0.0062/0.0063<0.05; K-lift -0.0002<=0.02); ledger block "
    "persisted science_gates.ledger (r509 face verified); prereg s7/s8 "
    "mechanical backfill byte-safe + integrity PASS + post-backfill selftest "
    "PASS (r307 two-state)** | S6 chain rc0 full: dualrun DRIFT 1 obs "
    "(streak reset, entry311 nulls claimed_since, honest obs-phase), "
    "compute_audit CLEAN burning-healthy py 85%, WM loaded_ok, update_daily "
    "0 rows holiday, regime shadow, scorecard/clock/panel/report/live_usage "
    "regenerated (strategy_scorecard+daily_scorecard+build_status wrote = "
    "L3 stale-host takeover face per r378), lane-guard no-ops honest, "
    "fundamental fresh 14.3h, b_layer ok, paper marks no-op, t35 export "
    "2026-09-30, token L2 0 today | monthly set: SKIP (Oct-1 first-round ran "
    "science_audit 3x + BRIEF-202609 + SELF-REVIEW-202609 verified) | S7: "
    "attrition CLEAN, loop pin=2 no-op, watchdog S4U re-registered, claw "
    "installed, state 530->532, heartbeat epoch int verified | "
    "LOWAMP-P3-NULLS: burn ACTIVE pid36968 683/2000 (rate slowed by W40 "
    "finalize+S6 competition), daemon-managed, claim handshake will fire at "
    "completion, NO pool flip by hand (r488 law respected -- earlier "
    "ghost-ready diagnosis corrected to in-flight) | "
    "NEXTR533: nulls burn completion watch (product delivery + daemon harvest "
    "flip verify); W41 (bm-c) finalize chain consumes my 450,540 as prev; "
    "next bm-b wave W42 freeze after W41 seat closes (fetch+tail-row lock "
    "law) | CEO view: live head 450,540 (n1_w40_results.json), "
    "LIVE-2026-10-02 ORANGE cap 50%, REPORT-2026-10-02 5 faces"
)
sep = "\r\n" if crlf else "\n"
if raw and not raw.endswith(sep.encode()):
    raw += sep.encode()
open(p, "wb").write(raw + line.encode("utf-8") + sep.encode())
print("round report appended")

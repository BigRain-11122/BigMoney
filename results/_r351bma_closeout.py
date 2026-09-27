"""R351 bm-a closeout: state round_no+1, heartbeat refresh (epoch int / clock T-sep), round report line."""
import json, time, datetime, subprocess, os

NOW = datetime.datetime.now()
ISO = NOW.isoformat(timespec="seconds")  # T-separated local with offset? datetime.now() has no tz -> build with +08:00
EPOCH = int(time.time())
# machine clock ISO 8601 WITH UTC offset, T separator (R170/R178/R262 law: int epoch + T-sep)
clock_read = NOW.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"

# --- state-bm-a.json: round_no + 1 ---
sp = "state-bm-a.json"
st = json.load(open(sp, encoding="utf-8"))
st["round_no"] = int(st.get("round_no", 0)) + 1
st["updated"] = clock_read
json.dump(st, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chk = json.load(open(sp, encoding="utf-8"))
assert chk["round_no"] == 351, chk["round_no"]

# --- heartbeat fleet/machines/bm-a.json ---
hp = "fleet/machines/bm-a.json"
hb = json.load(open(hp, encoding="utf-8"))
hb["last_seen"] = clock_read
hb["heartbeat_epoch_utc"] = EPOCH
hb["clock_read"] = clock_read
hb["current_task"] = "r351 closed: bmb-r340 fold-landing complete + MSG-2010 W2-B/UNC mirror fix landed"
hb["round_no"] = 351
hb["round"] = 351
hb["loop_round"] = 351
hb["verdict"] = "healthy"
cpu = float(subprocess.run(["powershell", "-NoProfile", "-Command",
    "(Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average"],
    capture_output=True, text=True).stdout.strip() or 0)
hb["cpu_util_pct"] = cpu
os_mem = subprocess.run(["powershell", "-NoProfile", "-Command",
    "[math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB,1)"],
    capture_output=True, text=True).stdout.strip()
hb["free_ram_gb"] = float(os_mem or 0)
json.dump(hb, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), type(chk["heartbeat_epoch_utc"])
assert "T" in chk["clock_read"], chk["clock_read"]

# --- round report line (bm-a per-machine ledger, S5) ---
rp = "logs/iteration-loop/round_reports-bm-a.md"
line = (f"{clock_read} | R351 | watermark GREEN (py_low_board_clear legal idle; pool_ready=1=W2-A in-flight "
        f"bm-b owner lane per r341 dual-evidence, no takeover) | FIRST-DUTY bmb-r340 fold-landing COMPLETE: "
        f"9-commit chain (r339+6 ticks+r340+addendum) rebased onto main, 2 storm passes (pass-1 28-UU: snapshots "
        f"deep-ts take-new 16ours/4theirs, compute_audit union 213, regime union 2, token_usage bucket-merge, "
        f"x2 line-union 954+900->960, pool done-absorption 80, CODELY memory-union + in-window 27th-batch archival; "
        f"pass-2 6-UU vs bmc r101: CODELY entry-level union 8316B keeps bmc full-rows face + bmb r340 pitlaw row, "
        f"archive batch renumber ours 27->28 per r176 yield, 4 snapshots take-bmc 20:11) + PUSHED "
        f"3e7593ec..604b3a87 + escape-valve machine/bm-b-r340 GC-deleted (content-anchor verify PASS incl "
        f"parallel_runner on_result byte-identical) + MSG-2010 EXECUTED: W2-B run() + W1 run_unc() collect-only-tail "
        f"-> on_result=_flush incremental-ckpt mirror fix (flushed-set safety net), selftests ALL PASS (w2b "
        f"7/7+D8-fail-closed, w1 22 legs incl UNC glue), W1 main-run path untouched (finalized batch) + MSG-2010 "
        f"processed + reply MSG-2055 to bmb + S6 33/33 rc=0 zero-masked Sunday no-op family (cutoff 09-24; moneyflow "
        f"rank pass + AH refresh spawned detached per design) + smoke 25/25 + orders 96/96 double-scan zero-unacked "
        f"+ decisions no-new-past-D-10 + CODELY 2 pitlaw rows (stage-mapping law + tick stage-destruction recovery) "
        f"9560B<=10KB | evidence: results/_r351bma_resolve_*.py x8 + _r351bma_codely_archival.py + git "
        f"3e7593ec..d5fd9c8a | next: T-91 s3 auto-fires Mon 2026-09-28 09:15 (launch-eve), W2-A finalize watch "
        f"(bmb ETA ~21:10), W2-B pool entry waiting on bmb D8-receive + W2A-finalize deps\n")
with open(rp, "a", encoding="utf-8") as f:
    f.write(line)
print(f"closeout: state 351, epoch={EPOCH} (int), clock={clock_read}, report line appended")

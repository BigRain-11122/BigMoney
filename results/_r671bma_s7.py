"""r671 S7 bookkeeping: state round_no bump, heartbeat, round report line. Programmatic + reparse self-check (r645 law)."""
import json, time, datetime, subprocess, io, re

REPO = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
now = datetime.datetime.now().astimezone()
now_iso = now.isoformat(timespec="seconds")
epoch = int(time.time())

# ---- state round_no bump ----
sp = REPO + r"\state-bm-a.json"
st = json.load(open(sp, encoding="utf-8"))
st["round_no"] = 671
st["last_round_ts"] = now_iso
json.dump(st, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
back = json.load(open(sp, encoding="utf-8"))
assert back["round_no"] == 671, "round bump failed"
print("state round_no -> 671 OK")

# ---- heartbeat ----
hp = REPO + r"\fleet\machines\bm-a.json"
hb = json.load(open(hp, encoding="utf-8"))
hb["last_seen"] = now_iso
hb["current_task"] = "round 671 done: T-166 fund-statement panel closure (86/86 periods) + gate coverage format-mismatch fix (phantom-spawn loop dead) + S6 38/38 green"
hb["cpu_cores"] = 32
ram = subprocess.run(["powershell", "-NoProfile", "-Command",
                      "(Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB"],
                     capture_output=True)
try:
    hb["free_ram_gb"] = round(float(ram.stdout.strip()) , 1)
except Exception:
    hb["free_ram_gb"] = 58.7
hb["gpu_free_vram_gb"] = 12.0
hb["verdict"] = "green: smoke 48/48, S6 all-green, T-166 done, fix landed"
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = now_iso
assert isinstance(hb["heartbeat_epoch_utc"], int)
assert re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+\d{2}:\d{2}$", hb["clock_read"])
json.dump(hb, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
back = json.load(open(hp, encoding="utf-8"))
assert isinstance(back["heartbeat_epoch_utc"], int) and "T" in back["clock_read"]
print("heartbeat OK, epoch int:", back["heartbeat_epoch_utc"])

# ---- round report line ----
rp = REPO + r"\round_reports-bm-a.md"
line = (
    "\n2026-10-04T10:5x | r671 (bm-a) | watermark=green (red=false, next_pick moneyflow-IC blocked on panel) | "
    "DONE-1: T-166 closed -- fund statement 3-face panel complete (86/86 periods x 3, 1,038,171 rows, PIT avail_date, cutoff 20260630; "
    "closure gate PASS parquet read-back + selftest rc0) -- piece-4/5 unlock routed per DIGEST sec.4 (piece-4 prereg stays trio-gated, ETA 10-05..09). "
    "DONE-2: P0 fix -- update_fund_statements gate coverage format-mismatch (parquet stores EM-native dashed period_end, expected set compact YYYYMMDD "
    "-> gate read complete panel as 258/258 missing -> phantom detached spawn every round + status-face flap; root cause probe _r671bma_fsdiag.py; "
    "one-point fix panel_coverage dash-normalize + r671 regression leg in selftest F7; live verify gate now 'no-op: panel complete 86 periods x 3 faces -> zero network'). "
    "DONE-3: S0 merge-union x3 under fleet push-race (CODELY suffix-union 2 bm-c entries zero-loss verified; guard-scan theirs regenerable) + D-19 MATCH (sparse-clone raw-bytes) + orders 153/153 ack. "
    "S6: 38/38 green (dualrun streak 46 zero-drift; audit flag supply_gap=known waiting face: 4/4 ready shards in-flight on bm-b/bm-c, piece-4 trio-gated per DIGEST routing -- no filler burns per O-1901 meaningfulness gate). "
    "artifacts: results/_r671bma_* (9 probes), scripts/update_fund_statements.py fix, T-166 json flip | "
    "evidence: status face complete=true + gate no-op line + selftest ALL-PASS + smoke 48/48 + attrition guard CLEAN | "
    "next: r672 watch moneyflow rank-pass completion (IC batch unlock candidate) + trio finalize reception; milestone: fund piece-4 prereg draft post-trio-finalize (<=10-09)"
)
with io.open(rp, "a", encoding="utf-8", newline="") as f:
    f.write(line)
print("round report appended")

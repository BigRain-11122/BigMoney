# -*- coding: utf-8 -*-
# r641 bm-b clockfix: strftime %H produced literal 'H' on this CRT (Windows
# quirk) -> clock strings malformed as '2026-10-04TH:02:06+08:00' in
# state.json + heartbeat + round-report last line. Manual f-string rebuild,
# strict regex self-verify (the previous weak 'T in clock' assert passed garbage).
import json, os, re, time, datetime, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

n = datetime.datetime.now().astimezone()
off = n.utcoffset().total_seconds() // 3600
iso = f"{n.year:04d}-{n.month:02d}-{n.day:02d}T{n.hour:02d}:{n.minute:02d}:{n.second:02d}+{int(off):02d}:00"
epoch = int(time.time())
RX = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+[0-9]{2}:00$")

# state.json
sp = "state.json"
st = json.load(open(sp, encoding="utf-8"))
for k in ("ts", "updated", "last_round_at", "last_seen", "clock_read"):
    st[k] = iso
json.dump(st, open(sp, "w", encoding="utf-8", newline=""), ensure_ascii=False, indent=1)

# heartbeat
hp = os.path.join("fleet", "machines", "bm-b.json")
hb = json.load(open(hp, encoding="utf-8"))
for k in ("ts", "updated", "updated_at", "last_seen", "clock_read"):
    hb[k] = iso
hb["heartbeat_epoch_utc"] = epoch
json.dump(hb, open(hp, "w", encoding="utf-8", newline=""), ensure_ascii=False, indent=1)

# round report last line: replace malformed leading timestamp
rp = os.path.join("logs", "iteration-loop", "round_reports.md")
with open(rp, encoding="utf-8") as f:
    lines = f.readlines()
fixed = 0
if lines and " | round 641 (bm-b" in lines[-1]:
    m0 = re.match(r"^([^\s|]+)\s\|\s", lines[-1])
    if m0 and not RX.match(m0.group(1)):
        lines[-1] = iso + lines[-1][len(m0.group(1)):]
        fixed = 1
with open(rp, "w", encoding="utf-8", newline="") as f:
    f.writelines(lines)

# strict self-verify
st2 = json.load(open(sp, encoding="utf-8"))
hb2 = json.load(open(hp, encoding="utf-8"))
assert st2["round_no"] == 641
for label, val in (("state.clock_read", st2["clock_read"]), ("hb.clock_read", hb2["clock_read"])):
    assert RX.match(val), f"{label} malformed: {val}"
assert isinstance(hb2["heartbeat_epoch_utc"], int)
assert abs(hb2["heartbeat_epoch_utc"] - time.time()) < 60
last = open(rp, encoding="utf-8").readlines()[-1]
assert last.startswith(iso[:11]), f"report line prefix bad: {last[:40]}"
print(f"CLOCKFIX OK: iso={iso} epoch={epoch} report_line_fixed={fixed}")

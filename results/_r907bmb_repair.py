# -*- coding: utf-8 -*-
# r907 repair: restore state.json from parent commit 5a668750b (full content), fix clock typo
# in state.json + bm-b.json + round_reports.md. No lambda tricks: read-first-write-second.
import subprocess, json

ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
BAD = b"2026-10-12TH:35:15+08:00"
GOOD = b"2026-10-12T23:35:15+08:00"

# 1) state.json: restore full bytes from parent commit, patch typo, write bytes-pure
r = subprocess.run(["git", "-C", ROOT, "show", "5a668750b:state.json"], capture_output=True)
assert r.returncode == 0, r.stderr[:200]
raw = r.stdout
assert BAD in raw, "bad clock string not found in parent state.json"
open(ROOT + r"\state.json", "wb").write(raw.replace(BAD, GOOD))

# 2) bm-b.json heartbeat
p = ROOT + r"\fleet\machines\bm-b.json"
c = open(p, encoding="utf-8").read()
assert "2026-10-12TH:35:15+08:00" in c, "bad clock not in heartbeat"
c = c.replace("2026-10-12TH:35:15+08:00", "2026-10-12T23:35:15+08:00")
open(p, "w", encoding="utf-8", newline="").write(c)

# 3) round_reports.md report line ts
rp = ROOT + r"\logs\iteration-loop\round_reports.md"
c = open(rp, encoding="utf-8").read()
c = c.replace("2026-10-12TH:35:15+08:00", "2026-10-12T23:35:15+08:00")
open(rp, "w", encoding="utf-8", newline="").write(c)

# verify all three
s = json.load(open(ROOT + r"\state.json", encoding="utf-8"))
h = json.load(open(p, encoding="utf-8"))
assert isinstance(h["heartbeat_epoch_utc"], int), "epoch must be int"
assert s["clock_read"] == "2026-10-12T23:35:15+08:00", s["clock_read"]
assert h["clock_read"] == "2026-10-12T23:35:15+08:00", h["clock_read"]
assert s["round_no"] == 908 and h["round_no"] == 908
print("RECOVER_OK state.clock=%s hb.clock=%s state.round_no=%d hb.epoch=%d(int) hb.ack_count=%d" % (
    s["clock_read"], h["clock_read"], s["round_no"], h["heartbeat_epoch_utc"], h.get("orders_ack_count", -1)))

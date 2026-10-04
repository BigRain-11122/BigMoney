# -*- coding: utf-8 -*-
"""r693 bm-a S7: state round_no increment + heartbeat update (programmatic,
json.loads self-proof; epoch must be JSON int; clock_read T-format)."""
import json, time, datetime, subprocess

# state round_no 692 -> 693
with open("state-bm-a.json", encoding="utf-8") as f:
    st = json.load(f)
prev = st.get("round_no")
st["round_no"] = 693
st["next"] = ("r693+: (1) W3 judge verdict product harvest FIRST CHECK each round "
              "(bm-c pid 33768 in flight, ETA ~22:1x; on landing: run "
              "results/_r693bma_w3_adopt_probe.py --live -> ADOPTION_READY -> adoption commit "
              "per W2 precedent 4f4100dc1 -> CEO 48h report clock starts; probe verified 10/10 "
              "on W2 precedent dry-run this round) "
              "(2) N2 slice-3 freeze = bm-c r492 seat claim (MSG-1918) -- bm-a zero-touch; "
              "bm-b slice-2 review window continues (MSG-1930) "
              "(3) W117 finalize GATED on bm-b W116 (RAM floor; rehearsal r684 armed) "
              "(4) fund trio NULLS finalize 10-05..09 (bm-b canonical) "
              "(5) 10-06+ style-rotation next-wave drafting (needs bm-b astock_daily panel) "
              "(6) 10-08 opening window external run-11/run-7 legs")
with open("state-bm-a.json", "w", encoding="utf-8") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
with open("state-bm-a.json", encoding="utf-8") as f:
    assert json.load(f)["round_no"] == 693
print("state round_no %s->693 reparse OK" % prev)

# heartbeat fleet/machines/bm-a.json
def sysinfo():
    import psutil
    return psutil.cpu_count(logical=True), psutil.virtual_memory().available / (1 << 30)

cores, free_gb = sysinfo()
epoch = int(time.time())
clock = datetime.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S+08:00")
with open("fleet/machines/bm-a.json", encoding="utf-8") as f:
    hb = json.load(f)
hb["last_seen"] = clock
hb["current_task"] = "r693: W3 judge adoption probe pre-built+verified (W2 dry 10/10); slice-3 freeze yielded to bm-c; W3 verdict watch ETA ~22:1x"
hb["cpu_cores"] = cores
hb["free_ram_gb"] = round(free_gb, 1)
hb["verdict"] = "waiting-state honorable: all major lines in-flight elsewhere or gated; product=adoption probe"
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = clock
with open("fleet/machines/bm-a.json", "w", encoding="utf-8") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
with open("fleet/machines/bm-a.json", encoding="utf-8") as f:
    d2 = json.load(f)
assert isinstance(d2["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in d2["clock_read"] and "+08:00" in d2["clock_read"], "clock must be T-format"
print("heartbeat epoch=%d int OK clock=%s OK" % (d2["heartbeat_epoch_utc"], d2["clock_read"]))

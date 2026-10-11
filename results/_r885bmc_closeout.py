# -*- coding: utf-8 -*-
"""r885 round-close bookkeeping: state round_no++, activity/verdict refresh,
D-19 watermark update, heartbeat epoch/clock fields. Zero-window safe."""
import json, time, datetime

root = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"

# --- state-bm-c.json ---
sp = root + r"\state-bm-c.json"
st = json.load(open(sp, encoding="utf-8"))
prev_round = st.get("round_no", 0)
st["round_no"] = int(prev_round) + 1
st["activity_now"] = (
    "current activity: W208 engine_owner takeover bm-a->bm-c executed "
    "(commit 4682d6b19 pushed; bm-a hb-stall 1291min >> 20min gate; bands "
    "unchanged R250) + W208 IGNITED 3 shards burning (0/1/3 pids live, 12 "
    "shards sequential, queue_next ranked) | round proof: smoke 49/49 + "
    "S6 38/38 rc0 + pf selftest 9/9 + n1 materializer faces green + "
    "O-1917 (bm-b dispatch) scanned non-recipient + D-20261011-05/06/07 "
    "consumed (watermark advanced f22e42..) | next milestone: W208 12/12 "
    "burn -> finalize -> W209 M10 freeze chain (seat registered, watch armed)"
)
st["verdict"] = (
    "green: W208 takeover+ignite = real product round (engine burn resumed "
    "on CEO fill-order law); board empty / judge pool = bm-b lane (MSG-1922 "
    "acknowledged, no dual-head)"
)
st["last_decisions_sha"] = "f22e42ef45bd4ec757dc773c40e583e3a7e1b4392119b350501ea94bf5a90e7e"
st["last_decisions_seen"] = "2026-10-11T19:35:00+08:00"
json.dump(st, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("state round_no:", prev_round, "->", st["round_no"])

# --- heartbeat fleet/machines/bm-c.json ---
hp = root + r"\fleet\machines\bm-c.json"
hb = json.load(open(hp, encoding="utf-8"))
now_epoch = int(time.time())
now_iso = datetime.datetime.now(datetime.timezone.utc).astimezone().isoformat(timespec="seconds")
hb["last_seen"] = now_iso
hb["heartbeat_epoch_utc"] = now_epoch  # int type per smoke F7
hb["clock_read"] = now_iso
hb["ts"] = now_iso
hb["now_active"] = "r885: W208 takeover+ignite (3 shards burning) + S6 38/38 + judge-pool await bm-b"
hb["verdict"] = "green"
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["cpu_cores"] = 32
try:
    import psutil
    hb["free_ram_gb"] = round(psutil.virtual_memory().available / (1024**3), 1)
except Exception:
    pass
json.dump(hb, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
print("heartbeat epoch:", chk["heartbeat_epoch_utc"], "clock:", chk["clock_read"])
print("OK r885 bookkeeping")

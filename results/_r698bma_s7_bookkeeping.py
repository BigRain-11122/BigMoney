# -*- coding: utf-8 -*-
"""r698 bm-a S7: state round_no bump + heartbeat write (json.dump + self-check
per r645; epoch int + T-format clock per R170/R262)."""
import json, time, datetime

# --- state: round_no absolute write 697 -> 698 ---
SP = "state-bm-a.json"
with open(SP, encoding="utf-8-sig") as fh:
    st = json.load(fh)
prev = st.get("round_no")
assert str(prev) == "697", "unexpected round_no %r" % prev
st["round_no"] = "698" if isinstance(prev, str) else 698
st["next"] = "r699: continue N2-W15 screen shard burns via daemon (SHARD-3..11 unclaimed pool shards); moneyflow panel refresh landing ~00:40 -> IC reference batch prereg (bandit next_pick); W3 judge finalize (bm-c lane, ETA ~22:1x) watch"
st["last_round_at"] = "2026-10-04T21:3x+08:00"
with open(SP, "w", encoding="utf-8", newline="") as fh:
    json.dump(st, fh, ensure_ascii=False, indent=1)
with open(SP, encoding="utf-8-sig") as fh:
    chk = json.load(fh)
assert str(chk["round_no"]) == "698", "state self-check failed"

# --- heartbeat: fleet/machines/bm-a.json ---
HB = "fleet/machines/bm-a.json"
with open(HB, encoding="utf-8-sig") as fh:
    hb = json.load(fh)
now = datetime.datetime.now()
hb["last_seen"] = now.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
hb["current_task"] = "N2-W15 screen shard burns (SHARD-1 done 97/97 cells 21:26, daemon continues unclaimed shards)"
hb["verdict"] = "healthy"
hb["heartbeat_epoch_utc"] = int(time.time())
hb["clock_read"] = now.astimezone().strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
try:
    import psutil
    hb["cpu_cores"] = psutil.cpu_count(logical=True)
    hb["idle_ram_gb"] = round(psutil.virtual_memory().available / 1e9, 1)
except Exception:
    pass
with open(HB, "w", encoding="utf-8", newline="") as fh:
    json.dump(hb, fh, ensure_ascii=False, indent=1)
with open(HB, encoding="utf-8-sig") as fh:
    chk = json.load(fh)
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in chk["clock_read"] and "+" in chk["clock_read"], "clock T-format"
print("state round_no=698 OK; heartbeat epoch=%d clock=%s OK" % (
    chk["heartbeat_epoch_utc"], chk["clock_read"]))

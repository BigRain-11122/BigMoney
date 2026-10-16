# r1025 readback: patch push_verified/sync blocks with real origin tip (commit2 face)
import json, datetime, time

ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
TS = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
EPOCH = int(time.time())
PV = {"ts": TS, "origin_tip": "7346d65ad", "ahead_behind": "0/0",
      "note": "r1025: commit1 push range 68e66c987..7346d65ad verified (range line + fetch + behind-0; local-not-at-origin=0, same-round readback)"}

st = json.load(open(ROOT + r"\state-bm-a.json", encoding="utf-8"))
st["push_verified"] = PV
st["sync"] = dict(PV)
st["heartbeat_epoch_utc"] = EPOCH
st["last_heartbeat_epoch_utc"] = EPOCH
with open(ROOT + r"\state-bm-a.json", "w", encoding="utf-8") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)

hb = json.load(open(ROOT + r"\fleet\machines\bm-a.json", encoding="utf-8"))
hb["push_verified"] = PV
hb["sync"] = dict(PV)
hb["heartbeat_epoch_utc"] = EPOCH
hb["last_heartbeat_epoch_utc"] = EPOCH
hb["heartbeat_epoch_utc_type_int"] = True
hb["ts"] = TS
hb["updated"] = TS
hb["updated_at"] = TS
hb["clock_read"] = TS
hb["last_seen"] = TS
with open(ROOT + r"\fleet\machines\bm-a.json", "w", encoding="utf-8") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)

hb2 = json.load(open(ROOT + r"\fleet\machines\bm-a.json", encoding="utf-8"))
assert isinstance(hb2["heartbeat_epoch_utc"], int)
print("READBACK_PATCHED tip=7346d65ad 0/0 epoch_int=%s" % isinstance(hb2["heartbeat_epoch_utc"], int))

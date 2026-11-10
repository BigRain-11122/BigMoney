import json, os, time
from datetime import datetime

ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
os.chdir(ROOT)
now = datetime.now().astimezone()
iso = now.strftime("%Y-%m-%dT%H:%M:%S%z")
iso = iso[:-2] + ":" + iso[-2:]
epoch = int(time.time())

sp = "state-bm-a.json"
with open(sp, "r", encoding="utf-8") as fh:
    st = json.load(fh)
st["updated"] = iso
st["verify_r1283"] = st.get("verify_r1283", "") + (
    " | attrition CLEAN 4 ledgers (3 historical shrinks healed) | loop task pin=8 no-op | pre-commit claw "
    "reinstalled (LF-normalised) | full smoke started detached on the final tree (pid 45600, "
    ".codely-cli/tmp/smoke-r1283.out) -- its result is NOT claimed by this window | delivery: fallback branch "
    "machine/bm-a-r1283 because origin moved 6 commits while ~500 inherited chain artifacts stayed uncommitted.")
with open(sp, "w", encoding="utf-8") as fh:
    json.dump(st, fh, ensure_ascii=False, indent=1)
    fh.write("\n")

hp = "fleet/machines/bm-a.json"
with open(hp, "r", encoding="utf-8") as fh:
    hb = json.load(fh)
hb.update({
    "last_seen": iso, "ts": iso, "clock_read": iso,
    "heartbeat_epoch_utc": epoch,
    "doing": "r1283 closed: base-basis audit published + disclosure; smoke running detached (result unclaimed)",
    "verdict": "green",
})
with open(hp, "w", encoding="utf-8") as fh:
    json.dump(hb, fh, ensure_ascii=False, indent=1)
    fh.write("\n")
assert isinstance(hb["heartbeat_epoch_utc"], int)
print("ok", iso)

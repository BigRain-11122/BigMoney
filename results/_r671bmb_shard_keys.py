import json, io, subprocess

OUT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r671bmb_shard_keys.txt"
lines = []
KEYS = ["key", "status", "owner", "owner_since", "last_tick", "keepalive_ts", "claimed_at", "pid"]

def dump(tag, raw):
    obj = json.loads(raw.decode("utf-8")) if isinstance(raw, (bytes, bytearray)) else raw
    entries = obj.get("entries") or obj.get("shards") or {}
    if isinstance(entries, list):
        entries = {e.get("id", str(i)): e for i, e in enumerate(entries)}
    for k in ("FUND-VALUE-P1-NULLS", "FUND-QUALITY-P1-NULLS", "FUND-DIVLOWVOL-P1-NULLS"):
        e = entries.get(k)
        if not e:
            continue
        for sh in e.get("shards", []):
            frag = {kk: sh.get(kk) for kk in KEYS if kk in sh}
            lines.append("%s %s: %s" % (tag, k, json.dumps(frag, ensure_ascii=False)))

wt = json.load(io.open(r"results\runnable_pool.json", encoding="utf-8"))
dump("WT", wt)
b = subprocess.run(["git", "show", "HEAD:results/runnable_pool.json"], capture_output=True).stdout
dump("HEAD", b)
b2 = subprocess.run(["git", "show", "origin/main:results/runnable_pool.json"], capture_output=True).stdout
dump("ORIGIN", b2)

# also check other pool candidates that are ready (hungry pool check)
ents = wt.get("entries") or wt.get("shards") or {}
if isinstance(ents, list):
    ents = {e.get("id", str(i)): e for i, e in enumerate(ents)}
ready = []
for k, e in ents.items():
    for sh in e.get("shards", []):
        if sh.get("status") == "ready":
            ready.append((k, sh.get("owner")))
lines.append("READY shards: %d" % len(ready))
for k, o in ready:
    lines.append("  ready: %s owner=%s" % (k, o))

with io.open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("written")

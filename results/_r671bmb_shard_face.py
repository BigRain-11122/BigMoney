import json, io, subprocess

OUT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r671bmb_shard_face.txt"
lines = []

def dump_shards(tag, raw):
    obj = json.loads(raw.decode("utf-8")) if isinstance(raw, (bytes, bytearray)) else raw
    entries = obj.get("entries") or obj.get("shards") or {}
    if isinstance(entries, list):
        entries = {e.get("id", str(i)): e for i, e in enumerate(entries)}
    for k in ("FUND-VALUE-P1-NULLS", "FUND-QUALITY-P1-NULLS", "FUND-DIVLOWVOL-P1-NULLS"):
        e = entries.get(k)
        if e is None:
            lines.append("%s %s: MISSING" % (tag, k)); continue
        for sh in e.get("shards", []):
            lines.append("%s %s shard: %s" % (tag, k, json.dumps(sh, ensure_ascii=False)[:800]))

wt = json.load(io.open(r"results\runnable_pool.json", encoding="utf-8"))
dump_shards("WT", wt)
b = subprocess.run(["git", "show", "HEAD:results/runnable_pool.json"], capture_output=True).stdout
dump_shards("HEAD", b)
b2 = subprocess.run(["git", "show", "origin/main:results/runnable_pool.json"], capture_output=True).stdout
dump_shards("ORIGIN", b2)

with io.open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("written")

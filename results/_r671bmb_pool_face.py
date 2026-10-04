import json, io, subprocess

OUT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r671bmb_pool_face.txt"
lines = []

def dump_entry(obj, tag):
    entries = obj.get("entries") or obj.get("shards") or {}
    if isinstance(entries, list):
        entries = {e.get("id", str(i)): e for i, e in enumerate(entries)}
    for k in ("FUND-VALUE-P1-NULLS", "FUND-QUALITY-P1-NULLS", "FUND-DIVLOWVOL-P1-NULLS"):
        e = entries.get(k)
        if e is None:
            lines.append("%s %s: MISSING" % (tag, k))
        else:
            lines.append("%s %s: %s" % (tag, k, json.dumps(e, ensure_ascii=False)[:1200]))

# working tree
wt = json.load(io.open(r"results\runnable_pool.json", encoding="utf-8"))
dump_entry(wt, "WT")
# HEAD blob
b = subprocess.run(["git", "show", "HEAD:results/runnable_pool.json"], capture_output=True).stdout
dump_entry(json.loads(b.decode("utf-8")), "HEAD")
# origin tip blob
subprocess.run(["git", "fetch", "origin"], capture_output=True)
b2 = subprocess.run(["git", "show", "origin/main:results/runnable_pool.json"], capture_output=True).stdout
dump_entry(json.loads(b2.decode("utf-8")), "ORIGIN")

lines.append("---git log pool---")
out = subprocess.run(["git", "log", "--oneline", "-6", "--follow", "--", "results/runnable_pool.json"],
                      capture_output=True).stdout.decode("utf-8", "replace")
lines.append(out)

with io.open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("written")

"""r671 bm-a situation probe: pool shards, inbox unread, recent round lines."""
import json, glob, os, io, sys
REPO = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
out = open(r"C:\Users\sjs20\AppData\Local\Temp\r671_situ.txt", "w", encoding="utf-8")

# pool shards
try:
    pool = json.load(open(REPO + r"\results\runnable_pool.json", encoding="utf-8"))
    shards = pool.get("shards", pool if isinstance(pool, list) else [])
    if isinstance(shards, dict):
        shards = list(shards.values())
    out.write("== pool shards ==\n")
    for s in shards:
        if isinstance(s, dict):
            out.write(f"{s.get('shard_id','?')} | status={s.get('status','?')} | owner={s.get('owner','?')} | batch={s.get('batch_id', s.get('ticket','?'))}\n")
except Exception as e:
    out.write(f"pool read fail: {e}\n")

# crash fuse
try:
    fuse = json.load(open(REPO + r"\results\crash_fuse.json", encoding="utf-8"))
    out.write("\n== crash fuse ==\n")
    out.write(json.dumps(fuse, ensure_ascii=False, indent=1)[:1200] + "\n")
except Exception as e:
    out.write(f"fuse read fail: {e}\n")

# inbox unread
proc = os.path.join(REPO, "fleet", "inbox")
done = os.path.join(REPO, "fleet", "inbox", "processed")
out.write("\n== inbox unread (to bm-a or ALL) ==\n")
for f in sorted(glob.glob(proc + r"\*.md") + glob.glob(proc + r"\*.json")):
    name = os.path.basename(f)
    if os.path.exists(os.path.join(done, name)):
        continue
    try:
        head = open(f, encoding="utf-8", errors="replace").read()[:200]
        out.write(f"--- {name} ---\n{head}\n")
    except Exception as e:
        out.write(f"{name} read fail {e}\n")
out.close()
print("situ written")

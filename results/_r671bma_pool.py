"""r671 pool probe v2: introspect top-level structure then dump entries."""
import subprocess, json
REPO = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
r = subprocess.run(["git", "-C", REPO, "show", "origin/main:results/runnable_pool.json"], capture_output=True)
d = json.loads(r.stdout)
w = open(r"C:\Users\sjs20\AppData\Local\Temp\r671_pool.txt", "w", encoding="utf-8")
w.write(f"top keys: {list(d.keys())}\n")
ent = d.get("entries", {})
w.write(f"entries type: {type(ent).__name__} count: {len(ent)}\n")
if isinstance(ent, dict):
    it = ent.items()
else:
    it = enumerate(ent)
for k, v in it:
    if isinstance(v, dict):
        w.write(f"{k} | status={v.get('status','?')} | owner={v.get('owner','?')} | owner_since={v.get('owner_since','?')} | keepalive={v.get('last_keepalive_ts', v.get('last_keepalive','?'))} | note={str(v.get('note',''))[:80]}\n")
w.close()
print("done")

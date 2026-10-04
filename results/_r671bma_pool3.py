"""r671 pool probe v3: only non-done entries, with full identity fields."""
import subprocess, json
REPO = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
r = subprocess.run(["git", "-C", REPO, "show", "origin/main:results/runnable_pool.json"], capture_output=True)
d = json.loads(r.stdout)
w = open(r"C:\Users\sjs20\AppData\Local\Temp\r671_pool3.txt", "w", encoding="utf-8")
for e in d.get("entries", []):
    st = e.get("status", "?")
    if st in ("done",):
        continue
    w.write(json.dumps(e, ensure_ascii=False, indent=1)[:800] + "\n----\n")
w.close()
print("written")

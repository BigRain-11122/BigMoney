import json, subprocess, hashlib, os, sys
# r689 bm-a: group docs/orders.md watermark check (CEO 待办物理件区)
# r660 law: raw bytes via python subprocess git show (no PS pipeline, no disk copy)
group = r"C:\Users\sjs20\Desktop\FluxGroup"
repo = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"

r = subprocess.run(["git", "-C", group, "fetch", "origin"], capture_output=True)
if r.returncode != 0:
    print("FETCH_FAIL:", r.stderr.decode('utf-8', 'replace')[:300]); sys.exit(2)

r = subprocess.run(["git", "-C", group, "show", "origin/main:docs/orders.md"], capture_output=True)
if r.returncode != 0:
    print("SHOW_FAIL:", r.stderr.decode('utf-8', 'replace')[:300]); sys.exit(2)
blob = r.stdout
new_sha = hashlib.sha256(blob).hexdigest()

with open(os.path.join(repo, "state-bm-a.json"), "rb") as f:
    st = json.loads(f.read().decode('utf-8'))
old_sha = st.get("last_orders_sha", "")
print("orders.md sha256:", new_sha)
print("watermark:", old_sha)
print("MATCH" if new_sha == old_sha else "CHANGED")

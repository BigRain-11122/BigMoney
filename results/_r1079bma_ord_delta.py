import subprocess, hashlib

GRP = r"C:\Users\sjs20\Desktop\FluxGroup"

def show(path):
    r = subprocess.run(["git", "-C", GRP, "show", "origin/main:" + path], capture_output=True)
    if r.returncode != 0:
        raise SystemExit("show failed: " + r.stderr.decode("utf-8", "replace")[:200])
    return r.stdout

f = subprocess.run(["git", "-C", GRP, "fetch", "origin"], capture_output=True)
print("fetch_rc", f.returncode)

data = show("docs/orders.md")
sha = hashlib.sha256(data).hexdigest()
print("orders_sha", sha)
lines = data.decode("utf-8", "replace").splitlines()
print("total_lines", len(lines))
tail = "\n".join(lines[-50:])
with open(r"results\_r1079bma_group_orders_tail.txt", "w", encoding="utf-8") as fh:
    fh.write(tail)
print("tail_written", len(lines[-50:]))

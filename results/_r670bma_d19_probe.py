# r670 bm-a D-19 fresh read: decisions/orders sha via git show raw bytes (canon r660 law)
import json, subprocess, hashlib, sys

STATE = json.load(open("state-bm-a.json", encoding="utf-8"))

def sha_blob(repo, path):
    b = subprocess.run(["git", "-C", repo, "show", f"origin/main:{path}"], capture_output=True).stdout
    return hashlib.sha256(b).hexdigest(), b

repo = r"C:\Users\sjs20\Desktop\FluxGroup"
import os
if not os.path.isdir(repo):
    print("group tree MISSING -> need sparse clone fallback")
    sys.exit(3)

subprocess.run(["git", "-C", repo, "fetch", "origin"], capture_output=True)

d_sha, d_bytes = sha_blob(repo, "docs/decisions.md")
o_sha, o_bytes = sha_blob(repo, "docs/orders.md")

prev_d = STATE.get("last_decisions_sha")
prev_o = STATE.get("last_orders_sha")
print("decisions sha:", d_sha[:16], "state key:", (prev_d or "")[:16], "MATCH" if d_sha == prev_d else "CHANGED")
print("orders sha:", o_sha[:16], "state key:", (prev_o or "")[:16], "MATCH" if o_sha == prev_o else "CHANGED")

# if changed, dump the NEW lines (lines not in old content unknown; print tail 40 lines of each for eyeball)
if d_sha != prev_d or o_sha != prev_o:
    print("--- decisions tail 30 ---")
    print("\n".join(d_bytes.decode("utf-8", errors="replace").splitlines()[-30:]))
    print("--- orders tail 20 ---")
    print("\n".join(o_bytes.decode("utf-8", errors="replace").splitlines()[-20:]))

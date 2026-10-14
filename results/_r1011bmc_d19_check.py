# r1011 S0.5 D-19 group-tree fresh-read watermark check (bm-c)
import subprocess, hashlib, json, sys

GRP = r"K:\Fluxgroup\FluxGroup"
GIT = r"C:\Program Files\Git\cmd\git.exe"

def show(path):
    r = subprocess.run([GIT, "-C", GRP, "show", "origin/main:" + path],
                      capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout

f = subprocess.run([GIT, "-C", GRP, "fetch", "origin"], capture_output=True)
print("fetch rc:", f.returncode)

dec = show("docs/decisions.md")
if dec is None:
    print("DECISIONS: fetch-failed/absent"); sys.exit(2)
dec_sha = hashlib.sha256(dec).hexdigest()

state = json.load(open("state-bm-c.json", encoding="utf-8"))
prev = state.get("last_decisions_sha")
print("decisions sha256:", dec_sha[:16], "prev:", (prev or "NONE")[:16])
if dec_sha == prev:
    print("DECISIONS: unchanged -> zero action")
else:
    # print the 派工通告板 block + tail lines for consumption
    txt = dec.decode("utf-8", "replace")
    lines = txt.splitlines()
    idx = [i for i, l in enumerate(lines) if "派工通告板" in l]
    start = idx[-1] if idx else max(0, len(lines) - 60)
    print("--- DECISIONS delta region (派工通告板 block onward, tail 80) ---")
    print("\n".join(lines[start:start + 80]))
    # tail if block not found
    if not idx:
        print("--- tail 40 ---")
        print("\n".join(lines[-40:]))

ord_ = show("docs/orders.md")
if ord_ is None:
    print("ORDERS: fetch-failed/absent")
else:
    ord_sha = hashlib.sha256(ord_).hexdigest()
    prev_o = state.get("last_orders_sha")
    print("orders sha256:", ord_sha[:16], "prev:", (prev_o or "NONE")[:16])
    if ord_sha != prev_o:
        txt = ord_.decode("utf-8", "replace")
        lines = txt.splitlines()
        print("--- ORDERS tail 50 (CEO physical-items zone scan) ---")
        print("\n".join(lines[-50:]))

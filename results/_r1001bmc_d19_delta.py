# r1001 bm-c: ORD delta consume — pull origin blob via python subprocess (raw bytes, zero PS redirection)
import hashlib, json, subprocess

GIT = r"C:\Program Files\Git\cmd\git.exe"
GRP = r"K:\Fluxgroup\FluxGroup"

def blob_bytes(path):
    p = subprocess.run([GIT, "-C", GRP, "show", "origin/main:" + path],
                       capture_output=True)
    assert p.returncode == 0, p.stderr[:300]
    return p.stdout

orders = blob_bytes("docs/orders.md")
sha1 = hashlib.sha1(orders).hexdigest()
wm_old = "63da903e8b433a578fb201f85569cffbd4af99f0"
wm_new = "746ab69349891fbd810f2bcd7d34b8f1636063ce"
print("orders sha1:", sha1)
print("probe new  :", wm_new)
print("match probe:", sha1 == wm_new)

text = orders.decode("utf-8", errors="replace")
lines = text.splitlines()
print("total lines:", len(lines))

# find tail rows newer than last consume (16:37 = r1000 closeout). Print last 40 rows.
tail = lines[-40:]
for ln in tail:
    print("TAIL|", ln)

# also dump all lines carrying 10-14 1[6-9]/2x timestamps for delta scan
hits = [ln for ln in lines if (("10-14 1" in ln) or ("10-14 2" in ln))]
print("--- rows containing 10-14 1x/2x timestamps:", len(hits))
for ln in hits[-25:]:
    print("HIT|", ln)

json.dump({"orders_sha1": sha1, "lines": len(lines)},
          open("results/_r1001bmc_d19_delta.json", "w", encoding="utf-8"))

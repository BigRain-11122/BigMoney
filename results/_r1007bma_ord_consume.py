# r1007 bm-a: canonical orders delta extraction (D-19 face, raw-bytes lineage)
# old watermark sha256 = cff45c9e... -> find that blob in group git history, diff rows vs current origin blob
import subprocess, hashlib, sys, io

GRP = r"C:/Users/sjs20/Desktop/FluxGroup"
WM = "cff45c9ef6a937788fbb78020324b280d5fa8ab5f7a44d0d38443f60ada90d4e"

def sh(*args):
    return subprocess.run(["git", "-C", GRP] + list(args), capture_output=True).stdout

sh("fetch", "origin")
cur = sh("show", "origin/main:docs/orders.md")
cur_sha = hashlib.sha256(cur).hexdigest()
print("cur_sha", cur_sha)

if cur_sha == WM:
    print("VERDICT: zero delta (probe artifact mismatch)"); sys.exit(0)

# walk history to find blob matching watermark
found_old = None
log = sh("log", "origin/main", "--format=%H", "-n", "60").decode("ascii", "replace").split()
for c in log:
    b = sh("show", c + ":docs/orders.md")
    if hashlib.sha256(b).hexdigest() == WM:
        found_old = (c, b)
        print("old blob found at commit", c)
        break
if not found_old:
    print("WARN: old blob not in last 60 commits; falling back to row-tail heuristic")

old_rows = (found_old[1] if found_old else b"").decode("utf-8", "replace").replace("\r\n", "\n").split("\n")
new_rows = cur.decode("utf-8", "replace").replace("\r\n", "\n").split("\n")
old_set = set(r.strip() for r in old_rows if r.strip())
new_delta = [r for r in new_rows if r.strip() and r.strip() not in old_set]

out = io.StringIO()
out.write(f"rows old={len([r for r in old_rows if r.strip()])} new={len([r for r in new_rows if r.strip()])} delta={len(new_delta)}\n")
bm_hits = []
for r in new_delta:
    out.write(r + "\n")
    low = r.lower()
    if any(k in low for k in ["bigmoney", "量化", "回测", "w24", "n1", "fleet", "全司", "所有子"]):
        bm_hits.append(r)
print(out.getvalue()[:4000])
print("---BM-RELEVANT---")
print("\n".join(bm_hits) if bm_hits else "(zero BigMoney-directive rows)")
open(r"results/_r1007bma_ord_delta.txt", "w", encoding="utf-8", newline="").write(out.getvalue())

# r1002 bm-b S0.5: orders-ack diff + D-19 group watermark probe (decisions/orders)
import json, subprocess, hashlib, io, sys

REPO = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
GROUP = r"C:\Fluxgroup\FluxGroup"

def git_bytes(args, cwd):
    r = subprocess.run(["git"] + args, cwd=cwd, capture_output=True)
    if r.returncode != 0:
        raise RuntimeError("git rc=%d: %s" % (r.returncode, r.stderr.decode("utf-8", "replace")[:300]))
    return r.stdout

out = io.StringIO()

# 1) orders ack diff
hb = json.loads(open(REPO + r"\fleet\machines\bm-b.json", "rb").read().decode("utf-8-sig"))
import os, glob
files = sorted(os.path.basename(p) for p in glob.glob(REPO + r"\fleet\orders\O-*.md"))
ack = set(hb.get("orders_ack", []))
diff = [f for f in files if f not in ack]
out.write("ORDERS_TOTAL=%d ACKED=%d DIFF=%d\n" % (len(files), len(files) - len(diff), len(diff)))
for f in diff:
    out.write("UNACKED: %s\n" % f)

# 2) D-19 watermark probe (fresh read of group origin)
subprocess.run(["git", "-C", GROUP, "fetch", "origin"], capture_output=True)
st = json.loads(open(REPO + r"\state.json", "rb").read().decode("utf-8-sig"))
res = {}
for name, path, key in (("decisions", "docs/decisions.md", "last_decisions_sha"),
                        ("orders", "docs/orders.md", "last_orders_sha")):
    blob = git_bytes(["show", "origin/main:" + path], GROUP)
    sha = hashlib.sha256(blob).hexdigest()
    prev = st.get(key, "")
    res[name] = sha
    out.write("%s_SHA=%s\n%s_DELTA=%s\n" % (name.upper(), sha, name.upper(), sha != prev))
    if sha != prev:
        prev_lines = set(st.get("_" + key + "_lines_cache", []))  # optional cache, may be absent
        cur_lines = blob.decode("utf-8", "replace").splitlines()
        new = [l for l in cur_lines if ("BigMoney" in l or "bigmoney" in l or "quant" in l or "bm-b" in l) and l.strip()]
        out.write("%s_BM_ROWS_RECENT:\n" % name.upper())
        for l in new[-12:]:
            out.write("  | %s\n" % l.strip()[:240])

open(REPO + r"\results\_r1002bmb_s05_scan.out", "w", encoding="utf-8", newline="\n").write(out.getvalue())
print(out.getvalue())

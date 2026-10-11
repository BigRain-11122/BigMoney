import hashlib, io, subprocess
REPO = r"K:\Fluxgroup\FluxGroup"
TARGET = "0513e9e7c79aa12f45f0fd273007ada18e742d57"
def g(*a):
    return subprocess.run(["git", "-C", REPO] + list(a), capture_output=True).stdout
log = g("log", "origin/main", "-8", "--format=%H %ad", "--date=iso", "--", "docs/orders.md")
lines = [l for l in log.decode("utf-8", "replace").splitlines() if l.strip()]
out = []
match = None
for l in lines:
    parts = l.split(" ", 1)
    sha, date = parts[0], parts[1]
    blob = g("rev-parse", sha + ":docs/orders.md").decode().strip()
    raw = g("cat-file", "-p", blob + ":docs/orders.md") if False else g("show", sha + ":docs/orders.md")
    h = hashlib.sha1(raw).hexdigest()
    out.append("%s %s blob=%s content_sha1=%s%s" % (sha[:10], date, blob[:10], h[:12], " <== MATCH" if h == TARGET else ""))
    if h == TARGET:
        match = (sha, blob)
print("\n".join(out))
print("match_commit:", match)
if match:
    old = g("show", match[0] + ":docs/orders.md")
    io.open(r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r896bmc_orders_old.txt", "wb").write(old)
    print("old_content_written_bytes:", len(old))

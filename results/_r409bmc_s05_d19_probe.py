import subprocess, hashlib, io, sys
GR = r"K:\Fluxgroup\FluxGroup"
RB = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"

def sh(*a):
    return subprocess.check_output(list(a), stderr=subprocess.STDOUT)

try:
    sh("git", "-C", GR, "fetch", "origin")
    print("FETCH_OK")
except subprocess.CalledProcessError as e:
    print("FETCH_FAIL rc=%d" % e.returncode)
    sys.exit(2)

d = sh("git", "-C", GR, "show", "origin/main:docs/decisions.md")
h = hashlib.sha256(d).hexdigest().upper()
print("D19_SHA=" + h)

o = sh("git", "-C", GR, "show", "origin/main:docs/orders.md")
with io.open(RB + r"\results\_r409bmc_d19_decisions.md", "w", encoding="utf-8") as f:
    f.write(d.decode("utf-8", errors="replace"))
with io.open(RB + r"\results\_r409bmc_d19_orders.md", "w", encoding="utf-8") as f:
    f.write(o.decode("utf-8", errors="replace"))
print("D19_LEN=%d ORDERS_LEN=%d" % (len(d), len(o)))

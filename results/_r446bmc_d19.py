import subprocess, hashlib, io, sys
GR = r"K:\Fluxgroup\FluxGroup"
RB = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CRE = 0x08000000  # CREATE_NO_WINDOW (U060 zero-flash law)

def sh(*a):
    return subprocess.check_output(list(a), stderr=subprocess.STDOUT, creationflags=CRE)

try:
    sh("git", "-C", GR, "fetch", "origin")
    print("FETCH_OK")
except subprocess.CalledProcessError as e:
    print("FETCH_FAIL rc=%d" % e.returncode)
    sys.exit(2)

d = sh("git", "-C", GR, "show", "origin/main:docs/decisions.md")
print("D19_SHA256=" + hashlib.sha256(d).hexdigest().upper())
print("D19_LEN=%d" % len(d))

o = sh("git", "-C", GR, "show", "origin/main:docs/orders.md")
print("GORDERS_SHA1=" + hashlib.sha1(o).hexdigest().upper())
print("GORDERS_LEN=%d" % len(o))

with io.open(RB + r"\results\_r446bmc_d19_decisions.md", "wb") as f:
    f.write(d)
with io.open(RB + r"\results\_r446bmc_d19_orders.md", "wb") as f:
    f.write(o)
print("WROTE_TMP_FACES")

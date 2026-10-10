import subprocess, hashlib, sys
def blob(path):
    r = subprocess.run(["git","-C",r"K:\Fluxgroup\FluxGroup","show","origin/main:"+path],capture_output=True)
    return r.stdout
dec = blob("docs/decisions.md"); ordn = blob("docs/orders.md")
print("DEC_SHA="+hashlib.sha256(dec).hexdigest())
print("ORD_SHA="+hashlib.sha1(ordn).hexdigest())
print("---- decisions tail ----")
lines = dec.decode("utf-8","replace").splitlines()
print("\n".join(lines[-30:]))
print("---- orders tail ----")
olines = ordn.decode("utf-8","replace").splitlines()
print("\n".join(olines[-30:]))

import json, subprocess, hashlib
GRP = r"K:\Fluxgroup\FluxGroup"
def run_hard(cmd, timeout_s):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        out, err = p.communicate(timeout=timeout_s)
        return p.returncode, out.decode("utf-8","replace"), err.decode("utf-8","replace"), False
    except subprocess.TimeoutExpired:
        subprocess.run(["taskkill","/T","/F","/PID",str(p.pid)], capture_output=True)
        return -9, "", "", True
rc, out, err, to = run_hard(["git","-C",GRP,"fetch","origin"], 90)
print("fetch rc:", rc, "timeout:", to)
r = subprocess.run(["git","-C",GRP,"show","origin/main:docs/orders.md"], capture_output=True, timeout=30)
ob = r.stdout
r2 = subprocess.run(["git","-C",GRP,"show","origin/main:docs/decisions.md"], capture_output=True, timeout=30)
db = r2.stdout
print("orders_sha1:", hashlib.sha1(ob).hexdigest())
print("decisions_sha256:", hashlib.sha256(db).hexdigest())
lines = ob.decode("utf-8","replace").splitlines()
print("=== orders tail (last 14 rows) ===")
rows = [l for l in lines if l.startswith("|")]
for l in rows[-14:]:
    print(l[:400])
    print("---")
dl = db.decode("utf-8","replace").splitlines()
drows = [l for l in dl if l.startswith("|")]
print("=== decisions tail (last 6 rows) ===")
for l in drows[-6:]:
    print(l[:400])
    print("---")

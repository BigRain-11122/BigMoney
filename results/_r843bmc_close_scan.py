import subprocess, hashlib
GRP = r"K:\Fluxgroup\FluxGroup"
r = subprocess.run(["git","-C",GRP,"fetch","origin"], capture_output=True, timeout=60)
ob = subprocess.run(["git","-C",GRP,"show","origin/main:docs/orders.md"], capture_output=True, timeout=30).stdout
db = subprocess.run(["git","-C",GRP,"show","origin/main:docs/decisions.md"], capture_output=True, timeout=30).stdout
print("ORD sha:", hashlib.sha1(ob).hexdigest(), "| delta vs consumed 4d33cb4f:", hashlib.sha1(ob).hexdigest() != "4d33cb4fd796a84cae804963b03b572c03885ae3")
print("DEC sha:", hashlib.sha256(db).hexdigest(), "| delta vs consumed 68d13893:", hashlib.sha256(db).hexdigest() != "68d13893aa53a97bcee368fc03caf2b8a6fde9f5f65d155d6a55b581e946db07")

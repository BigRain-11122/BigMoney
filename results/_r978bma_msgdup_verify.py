import subprocess, sys

GIT = r"C:\Program Files\Git\cmd\git.exe"
files = [
    "fleet/inbox/processed/MSG-20261014-0715-bma-w236-finalize.md",
    "fleet/inbox/processed/MSG-20261014-0745-bma-w238-seat.md",
]
ok = True
for f in files:
    r = subprocess.run([GIT, "show", "origin/main:" + f], capture_output=True)
    if r.returncode != 0:
        print(f, "origin MISSING -> keep local")
        ok = False
        continue
    origin_bytes = r.stdout
    local_bytes = open(f, "rb").read()
    same = origin_bytes == local_bytes
    print(f, "byte-identical:", same, f"(origin {len(origin_bytes)}B vs local {len(local_bytes)}B)")
    if not same:
        ok = False
print("VERDICT:", "SAFE-DELETE" if ok else "KEEP-LOCAL")

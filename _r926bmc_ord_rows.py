import subprocess, sys
GIT = r"C:\Program Files\Git\cmd\git.exe"
blob = subprocess.run([GIT, "-C", r"K:\Fluxgroup\FluxGroup", "show", "origin/main:docs/orders.md"],
                      capture_output=True).stdout.decode("utf-8", "replace")
rows = [l for l in blob.splitlines() if l.startswith("| 10-12")]
for l in rows:
    ts = l[:16]
    if ts >= "| 10-12 11:1":
        print(l[:360])
        print("---")
print("TOTAL_ROWS_1012:", len(rows))

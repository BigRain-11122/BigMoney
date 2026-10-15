# r1026: extract full new DEC rows (2026-10-15 batch) + ORD token-law row
import subprocess, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
GT = r"K:\Fluxgroup\FluxGroup"
def show(path):
    p = subprocess.run(["git", "-C", GT, "show", "origin/main:" + path], capture_output=True)
    return p.stdout.decode('utf-8', 'replace')

dec = show("docs/decisions.md")
lines = dec.splitlines()
# print all lines belonging to 2026-10-15 rows in full
print("=== DEC 2026-10-15 rows (full text) ===")
keep = False
for l in lines:
    if l.startswith("| 2026-10-15 |"):
        keep = True
    elif l.startswith("| 2026-10-14 |"):
        keep = False
    if keep and l.strip() and not l.startswith("|---"):
        print(l)
        print("---")

ord_ = show("docs/orders.md")
olines = ord_.splitlines()
print("\n=== ORD rows after 11:30 today (full text) ===")
keep = False
for l in olines:
    if l.startswith("| 10-15 11:5") or l.startswith("| 10-15 12:"):
        keep = True
    if keep and l.strip():
        print(l)
        print("---")

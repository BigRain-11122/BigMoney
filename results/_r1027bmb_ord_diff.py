import subprocess

def blob(rev):
    b = subprocess.run(["git", "show", f"{rev}:results/_r686bmb_orders_fresh.md"], capture_output=True)
    return b.stdout.decode("utf-8", "replace").splitlines()

old = set(blob("8578dcadff"))     # r1026 consumed face (ord sha f2ccdac6)
new_lines = open("results/_r686bmb_orders_fresh.md", encoding="utf-8", errors="replace").read().splitlines()
new = set(new_lines)
added = [l for l in new_lines if l not in old and l.strip()]
print("added rows:", len(added))
for l in added:
    print("----")
    print(l[:600])

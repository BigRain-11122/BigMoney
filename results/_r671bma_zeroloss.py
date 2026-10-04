"""r671 zero-loss check for CODELY.md union merge."""
import subprocess
REPO = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
def show(ref, path):
    return subprocess.run(["git","-C",REPO,"show",f"{ref}:{path}"], capture_output=True).stdout
def lines(b):
    return set(l.rstrip(b"\r\n") for l in b.splitlines() if l.rstrip(b"\r\n") != b"")
ours = lines(show("HEAD","CODELY.md"))
their = lines(show("MERGE_HEAD","CODELY.md"))
work = lines(open(REPO+"\\CODELY.md","rb").read())
miss_ours = ours - work
miss_their = their - work
dup = 0
wl = [l.rstrip(b"\r\n") for l in open(REPO+"\\CODELY.md","rb").read().splitlines()]
seen = set()
for l in wl:
    if l in seen and l != b"":
        dup += 1
    seen.add(l)
print("miss_ours:", len(miss_ours), "miss_their:", len(miss_their), "dup_nonblank:", dup)
assert not miss_ours and not miss_their and dup == 0
print("ZERO-LOSS OK")

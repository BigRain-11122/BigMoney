import subprocess, os, io, sys
ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
os.chdir(ROOT)
_out = io.StringIO()
def P(*a):
    _out.write(" ".join(str(x) for x in a) + "\n")

def blob(ref, p):
    r = subprocess.run(["git", "show", f"{ref}:{p}"], capture_output=True)
    return r.stdout.decode("utf-8", "replace") if r.returncode == 0 else None

P("#" * 100)
P("# CODELY.md conflict blocks (working tree, byte-exact)")
c = open("CODELY.md", "rb").read().decode("utf-8", "replace")
lines = c.splitlines()
i = 0
while i < len(lines):
    if lines[i].startswith("<<<<<<<"):
        j = i
        while not lines[j].startswith(">>>>>>>"):
            j += 1
        P(f"### HUNK at lines {i+1}..{j+1}")
        for k in range(i, j + 1):
            P(f"  {k+1:4d}| {lines[k]}")
        i = j + 1
    else:
        i += 1

P("#" * 100)
P("# tails of stage1/2/3 (last 8 nonblank lines each)")
for ref, nm in ((":1", "stage1-base"), (":2", "stage2-origin"), (":3", "stage3-ours")):
    b = blob(ref, "CODELY.md")
    ls = [l for l in b.splitlines() if l.strip()]
    P(f"## {nm} ({len(ls)} nonblank lines) tail:")
    for l in ls[-8:]:
        P("   ", l)
P("#" * 100)
P("# r789-line and r644-line EXACT comparison across sides:")
import re
for ref, nm in ((":1", "base"), (":2", "origin"), (":3", "ours")):
    b = blob(ref, "CODELY.md")
    for pat, tag in ((r"^[-*].*r789 bm-b.*$", "r789-line"), (r"^[-*].*r644 bm-c.*$", "r644-line")):
        for m in re.finditer(pat, b, re.M):
            P(f"  [{nm}] {tag}: {m.group(0)}")
P("#" * 100)
P("# attrition both sides full:")
for ref, nm in ((":2", "origin"), (":3", "ours")):
    d = json.loads(blob(ref, "results/_attrition_guard_scan.json")) if False else None
import json as J
for ref, nm in ((":2", "origin"), (":3", "ours")):
    d = J.loads(blob(ref, "results/_attrition_guard_scan.json"))
    P(f"  {nm}: ts={d.get('ts')} rc={d.get('rc')} active_loss={d.get('active_loss')} files={len(d.get('files', {}))}")

with open("results/_r790bmb_exact_out.txt", "w", encoding="utf-8") as f:
    f.write(_out.getvalue())
sys.stdout.write("WROTE results/_r790bmb_exact_out.txt\n")

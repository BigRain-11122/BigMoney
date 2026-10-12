import subprocess, io, hashlib

G = r"K:\Fluxgroup\FluxGroup"
def run(args):
    return subprocess.run(["git", "-C", G] + args, capture_output=True)

target = "90dd3a63eb6845ba7e5c6df0ff2e9b6d587fe02d021a587180c190b636754d62"
r = run(["log", "origin/main", "--format=%H %ci", "--", "docs/orders.md"])
lines = r.stdout.decode("utf-8", "replace").strip().splitlines()
found = None
out = io.open(r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r937bmc_ord_bound.txt", "w", encoding="utf-8", newline="\n")
for l in lines[:10]:
    c = l.split()[0]
    b = run(["show", f"{c}:docs/orders.md"]).stdout
    h = hashlib.sha256(b).hexdigest()
    mark = " <== CONSUMED BOUNDARY" if h == target else ""
    out.write(f"{c[:12]} {l.split(' ', 1)[1].strip()} sha256={h[:16]}{mark}\n")
    if h == target:
        found = c
out.write(f"found={found}\n")
# if found: compute delta rows found..origin/main
if found:
    old_lines = set(run(["show", f"{found}:docs/orders.md"]).stdout.decode("utf-8", "replace").splitlines())
    new_lines = run(["show", "origin/main:docs/orders.md"]).stdout.decode("utf-8", "replace").splitlines()
    delta = [x for x in new_lines if x not in old_lines and x.strip().startswith("|")]
    out.write(f"true_delta_rows={len(delta)}\n")
    out.write("=" * 40 + "\n")
    for x in delta:
        out.write(x[:2500] + "\n")
out.close()
print("OK found=", bool(found))

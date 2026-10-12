import subprocess, io, hashlib

G = r"K:\Fluxgroup\FluxGroup"
def run(args):
    return subprocess.run(["git", "-C", G] + args, capture_output=True)

# last commits touching docs/orders.md
r = run(["log", "origin/main", "--format=%H %ci", "--", "docs/orders.md"])
lines = r.stdout.decode("utf-8", "replace").strip().splitlines()
out = io.open(r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r937bmc_ord_delta_rows.txt", "w", encoding="utf-8", newline="\n")
out.write("touch_commits=" + str(len(lines)) + "\n")
for l in lines[:5]:
    out.write("  " + l + "\n")

new_r = run(["show", "origin/main:docs/orders.md"])
new_bytes = new_r.stdout
new_sha256 = hashlib.sha256(new_bytes).hexdigest()
out.write(f"new_blob_sha256={new_sha256}\n")
out.write(f"state_last_orders_sha=90dd3a63eb6845ba7e5c6df0ff2e9b6d587fe02d021a587180c190b636754d62\n")
out.write(f"match={new_sha256 == '90dd3a63eb6845ba7e5c6df0ff2e9b6d587fe02d021a587180c190b636754d62'}\n")

if len(lines) >= 2:
    prev_commit = lines[1].split()[0]
    old_r = run(["show", f"{prev_commit}:docs/orders.md"])
    old_lines = set(old_r.stdout.decode("utf-8", "replace").splitlines())
    new_lines = new_bytes.decode("utf-8", "replace").splitlines()
    delta = [l for l in new_lines if l not in old_lines and l.strip().startswith("|")]
    out.write(f"prev_commit={prev_commit} delta_rows={len(delta)}\n")
    out.write("=" * 40 + "\n")
    for l in delta:
        out.write(l[:2000] + "\n")
out.close()
print("OK new_sha256=", new_sha256[:16])

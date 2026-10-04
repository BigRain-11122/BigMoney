# r669 bm-a: group orders.md diff vs r668-known content -> UTF-8 file
# r668 recorded sha 82a0cef9 (sha1). Find commits touching docs/orders.md since then.
import subprocess, io, os

repo = r"C:\Users\sjs20\Desktop\FluxGroup"
out_path = os.path.join(os.path.dirname(__file__), "_r669bma_orders_diff.txt")

def run(*args):
    return subprocess.run(["git", "-C", repo] + list(args), capture_output=True, timeout=120)

# locate the blob whose sha1(content) == 82a0cef9 by walking recent commits touching the file
log = run("log", "--since=2026-10-04T00:00:00+08:00", "--format=%H %ad %s", "--date=iso",
          "--", "docs/orders.md")
lines = log.stdout.decode("utf-8", errors="replace").strip().splitlines()

with io.open(out_path, "w", encoding="utf-8") as f:
    f.write("=== commits touching docs/orders.md today ===\n")
    f.write("\n".join(lines) + "\n\n")
    import hashlib
    for ln in lines:
        sha = ln.split()[0]
        show = run("show", "%s:docs/orders.md" % sha)
        c = hashlib.sha1(show.stdout).hexdigest()
        f.write("blob sha1(content) @ %s = %s\n" % (sha[:12], c))
    # newest commit full diff of the file
    if lines:
        newest = lines[0].split()[0]
        d = run("show", newest, "--format=COMMIT %h %ad %s", "--date=iso", "--", "docs/orders.md")
        f.write("\n=== newest commit diff ===\n")
        f.write(d.stdout.decode("utf-8", errors="replace"))
print("WROTE", out_path)

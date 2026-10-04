# r669 bm-a: group orders.md recent commit diff -> UTF-8 file (zero console CJK print, r458 law)
import subprocess, io, os, sys

repo = r"C:\Users\sjs20\AppData\Local\Temp\_r669bma_grp_sparse"
out_path = os.path.join(os.path.dirname(__file__), "_r669bma_orders_diff.txt")

r = subprocess.run(["git", "-C", repo, "log", "--since=2026-10-04T09:00:00+08:00",
                    "--format=COMMIT %h %ad %s", "--date=iso",
                    "--", "docs/orders.md"], capture_output=True, timeout=60)
log = r.stdout.decode("utf-8", errors="replace")

diffs = []
if log.strip():
    commits = [l.split()[1] for l in log.splitlines() if l.startswith("COMMIT")]
    for c in commits[:6]:
        d = subprocess.run(["git", "-C", repo, "show", c, "--format=COMMIT %h %ad %s",
                            "--date=iso", "--", "docs/orders.md"],
                           capture_output=True, timeout=60)
        diffs.append(d.stdout.decode("utf-8", errors="replace"))

with io.open(out_path, "w", encoding="utf-8") as f:
    f.write("=== LOG since 2026-10-04T09:00 ===\n")
    f.write(log)
    f.write("\n\n")
    for d in diffs:
        f.write(d)
        f.write("\n\n")
print("WROTE", out_path, len(log), len(diffs))

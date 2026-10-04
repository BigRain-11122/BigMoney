# r703 bm-a probe: full-text extract of new 10-05 decision rows (D-19 consumption leg)
# Law: D-20260930-19 fresh-read = git -C <group> fetch + git show origin/main:docs/decisions.md
import subprocess, io

GRP = r"C:\Users\sjs20\Desktop\FluxGroup"
subprocess.run(["git", "-C", GRP, "fetch", "origin"], capture_output=True)
raw = subprocess.run(["git", "-C", GRP, "show", "origin/main:docs/decisions.md"], capture_output=True)
t = raw.stdout.decode("utf-8", errors="replace")
lines = t.splitlines()
targets = ["D-20261005-02", "D-20261005-04", "D-20261005-05"]
out = io.StringIO()
for i, ln in enumerate(lines):
    for tg in targets:
        if tg in ln and ln.lstrip().startswith("|"):
            out.write(f"=== {tg} (line {i+1}) FULL ===\n{ln}\n\n")
            break
open(r"results\_r703bma_d19_fullrows.txt", "w", encoding="utf-8").write(out.getvalue())
print("rows captured:", out.getvalue().count("==="), "file chars:", len(out.getvalue()))

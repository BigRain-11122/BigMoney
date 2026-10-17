"""r1054 S0.5: dump group-tree origin orders tail for row-level delta consumption."""
import subprocess

out = subprocess.run(
    ["git", "-C", r"K:\Fluxgroup\FluxGroup", "show", "origin/main:docs/orders.md"],
    capture_output=True,
)
data = out.stdout
lines = data.decode("utf-8", "replace").splitlines()
print("total_lines", len(lines))
with open(r"results\_r1054bmc_ord_tail.md", "w", encoding="utf-8") as f:
    f.write("\n".join(lines[-70:]) + "\n")
print("tail written: results/_r1054bmc_ord_tail.md")

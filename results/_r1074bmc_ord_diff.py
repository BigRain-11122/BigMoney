"""r1074 bm-c: find the newest group-tree commits touching docs/orders.md and print the changed lines."""
import subprocess

GRP = r"K:\Fluxgroup\FluxGroup"


def run(args, binary=False):
    r = subprocess.run(args, capture_output=True)
    out = r.stdout
    if binary:
        return out
    return out.decode("utf-8", "replace")


# newest commits touching docs/orders.md
log = run(["git", "-C", GRP, "log", "--format=%h|%ad|%s", "--date=iso", "-4", "origin/main", "--", "docs/orders.md"])
print("=== recent commits touching docs/orders.md ===")
print(log)

# newest 5 commits overall
log2 = run(["git", "-C", GRP, "log", "--format=%h|%ad|%s", "--date=iso", "-5", "origin/main"])
print("=== recent group-tree commits ===")
print(log2)

# diff of orders.md across the last two touching commits
lines = [l for l in log.strip().splitlines() if l.strip()]
if len(lines) >= 2:
    new_c = lines[0].split("|")[0]
    old_c = lines[1].split("|")[0]
    diff = run(["git", "-C", GRP, "diff", old_c, new_c, "--", "docs/orders.md"])
    print("=== diff %s..%s docs/orders.md (changed lines only) ===" % (old_c, new_c))
    for dl in diff.splitlines():
        if dl.startswith("+") and not dl.startswith("+++"):
            print("ADD>", dl[:400])
        elif dl.startswith("-") and not dl.startswith("---"):
            print("DEL>", dl[:400])

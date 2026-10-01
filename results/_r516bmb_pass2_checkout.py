import subprocess

REPO = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
SKIP = {"results/p1d_gates.json"}


def git(a, check=True):
    r = subprocess.run(["git", "-C", REPO] + a, capture_output=True,
                       text=True, encoding="utf-8", errors="replace")
    if check and r.returncode != 0:
        raise RuntimeError(r.stderr)
    return r


st = git(["status", "--porcelain"]).stdout.splitlines()
todo = []
for line in st:
    code = line[:2].strip()
    path = line[3:].strip().strip('"')
    if path in SKIP or code == "??":
        continue
    todo.append(path)
print("restoring", len(todo))
if todo:
    git(["checkout", "--"] + todo)
st2 = git(["status", "--porcelain"]).stdout.splitlines()
print("remaining dirty:", len(st2))
for l in st2:
    print("  ", l)

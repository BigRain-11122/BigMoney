import subprocess, os

GIT = r"C:\Program Files\Git\cmd\git.exe"
ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"

def gitb(args):
    return subprocess.run([GIT] + args, cwd=ROOT, capture_output=True)

# 1. remove untracked-but-on-origin (backed up in quarantine)
for p in ["results/trial_labor_w17/w17_judge.json", "results/trial_labor_w17/w17_paired_deltas.json", "results/trial_labor_w17/w17_reform_face.json"]:
    os.remove(os.path.join(ROOT, p))
    print("removed", p)

# 2. restore modified tracked files to HEAD (all backed up)
status = gitb(["status", "--porcelain"]).stdout.decode("utf-8", "replace").splitlines()
mod = [l[3:].strip().strip('"') for l in status if l.strip() and l[:2].strip() == "M"]
r = gitb(["checkout", "HEAD", "--"] + mod)
print("checkout rc=", r.returncode, r.stderr.decode("utf-8", "replace")[:200])

# 3. pull --rebase (FF expected)
r = subprocess.run([GIT, "pull", "--rebase"], cwd=ROOT, capture_output=True)
print("pull rc=", r.returncode)
print("pull out:", r.stdout.decode("utf-8", "replace")[-500:])
print("pull err:", r.stderr.decode("utf-8", "replace")[-500:])

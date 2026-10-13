import subprocess, hashlib, os, sys

GIT = r"C:\Program Files\Git\cmd\git.exe"
ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"

def gitb(args):
    return subprocess.run([GIT] + args, cwd=ROOT, capture_output=True).stdout

def blob_of_origin(path):
    out = gitb(["show", f"origin/main:{path}"])
    return out if out else None

def has_origin(path):
    r = subprocess.run([GIT, "cat-file", "-e", f"origin/main:{path}"], cwd=ROOT, capture_output=True)
    return r.returncode == 0

status = gitb(["status", "--porcelain"]).decode("utf-8", "replace").splitlines()
report = []
for line in status:
    if not line.strip():
        continue
    code = line[:2].strip()
    path = line[3:].strip().strip('"')
    local = os.path.join(ROOT, path)
    if code == "??":
        # untracked: does origin track it?
        if has_origin(path):
            with open(local, "rb") as f:
                lb = f.read()
            ob = blob_of_origin(path)
            same = (lb == ob)
            report.append(f"UNTRACKED-BUT-ON-ORIGIN {'IDENTICAL' if same else 'DIFFERS'} {path} ({len(lb)}B local vs {len(ob) if ob else 0}B origin)")
        else:
            sz = os.path.getsize(local) if os.path.isfile(local) else -1
            report.append(f"UNTRACKED-NOT-ON-ORIGIN {path} ({sz}B) [pure estate, no FF conflict]")
    else:
        # tracked modified
        if has_origin(path):
            with open(local, "rb") as f:
                lb = f.read()
            ob = blob_of_origin(path)
            same = (lb == ob)
            # also vs HEAD
            hb = gitb(["show", f"HEAD:{path}"])
            samehead = (lb == hb)
            report.append(f"MODIFIED {'==ORIGIN' if same else ('' if samehead else '!=HEAD')} {'SAME-AS-ORIGIN(FF-safe drop)' if same else 'LOCAL-NEWER-OR-DIVERGED'} {path}")
        else:
            report.append(f"MODIFIED origin-missing {path}")

print("\n".join(report))
print(f"\nTOTAL {len(report)} faces")

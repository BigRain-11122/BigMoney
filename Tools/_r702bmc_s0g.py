"""r702 bm-c S0g: probe pull ambiguity + concurrent git state."""
import os
import subprocess

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"


def git(args):
    p = subprocess.run(["git", "-C", REPO] + args, capture_output=True)
    return p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")


for args in (["remote", "-v"], ["config", "--get-regexp", "^branch\\.main\\."], ["config", "--get", "pull.rebase"],
             ["symbolic-ref", "refs/remotes/origin/HEAD"], ["for-each-ref", "--format=%(refname)", "refs/remotes/origin"],
             ["status", "-sb"], ["rev-parse", "--abbrev-ref", "@{upstream}"]):
    rc, out, err = git(args)
    print("== git %s rc=%d" % (" ".join(args), rc))
    print(out.strip() or "(empty)")
    if err.strip():
        print("ERR:", err.strip()[:300])

for d in ("rebase-merge", "rebase-apply", "MERGE_HEAD", "CHERRY_PICK_HEAD", "index.lock"):
    p = os.path.join(REPO, ".git", d)
    print("== .git/%s exists=%s" % (d, os.path.exists(p)))
    if os.path.isdir(p):
        print("   contents:", os.listdir(p)[:10])

# concurrent git processes?
p = subprocess.run(["powershell", "-NoProfile", "-Command",
                    "Get-CimInstance Win32_Process -Filter \"Name='git.exe'\" | Select-Object ProcessId,CreationDate,CommandLine | ConvertTo-Json -Compress"],
                   capture_output=True)
print("== git.exe processes:", p.stdout.decode("utf-8", "replace").strip()[:600] or "(none)")

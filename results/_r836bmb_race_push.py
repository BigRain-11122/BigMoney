import subprocess, sys, os

ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
env = dict(os.environ)
env["GIT_EDITOR"] = "true"
env["GIT_TERMINAL_PROMPT"] = "0"
env["GCM_INTERACTIVE"] = "never"

def run(cmd):
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
    return r.returncode, (r.stdout or "") + (r.stderr or "")

def uu_paths():
    rc, out, _ = run(["git", "ls-files", "-u"])
    return sorted(set(l.split("\t")[1] for l in out.splitlines() if "\t" in l))

def marker_scan(paths):
    bad = []
    for p in paths:
        fp = os.path.join(ROOT, p)
        if os.path.exists(fp):
            for i, line in enumerate(open(fp, encoding="utf-8", errors="replace")):
                if line.startswith(("<<<<<<<", ">>>>>>>", "|||||||||")):
                    bad.append(f"{p}:L{i+1}")
    return bad

# step 1: absorb any local daemon churn as commit (rebase rejects dirty tree)
rc, out = run(["git", "status", "--porcelain"])
if out.strip():
    run(["git", "add", "-A"])
    rc, out = run(["git", "commit", "-m", "race absorb: own daemon live faces (pre-push window)"])
    print(f"[1] absorb: {out.strip().splitlines()[-1][:90] if out.strip() else 'clean'}")
else:
    print("[1] tree clean, no absorb needed")

# step 2: fetch
rc, out = run(["git", "fetch", "origin"])
print(f"[2] fetch rc={rc}")

# step 3: rebase onto origin/main (single try; conflicts auto-resolved below)
rc, out = run(["git", "rebase", "origin/main"])
print(f"[3] rebase rc={rc} :: {out.strip().splitlines()[-1][:120] if out.strip() else ''}")

# step 3b: auto-resolve loop (max 5)
for attempt in range(5):
    uu = uu_paths()
    if not uu:
        break
    print(f"[3b] attempt {attempt+1}: {len(uu)} UU -> take STAGE2(origin)+sync_face settle")
    for p in uu:
        run(["git", "checkout", "--ours", "--", p])
    run(["python", "scripts\\merge_lane_views.py", "sync_face"])
    bad = marker_scan(uu)
    if bad:
        print(f"[3b] MARKER-FAIL {bad[:5]}"); sys.exit(3)
    run(["git", "add", "-A"])
    rc, out = run(["git", "rebase", "--continue"])
    print(f"[3b] continue rc={rc}")

uu = uu_paths()
if uu:
    print(f"[3b] UNRESOLVED {uu}"); sys.exit(4)

# step 4: push
rc, out = run(["git", "push", "origin", "main"])
print(f"[4] push rc={rc} :: {out.strip()[:200]}")

# step 5: verify delivery
rc, out = run(["git", "ls-remote", "origin", "main"])
remote = out.split()[0] if out.split() else "?"
rc, out = run(["git", "rev-parse", "HEAD"])
local = out.strip()
rc, out = run(["git", "rev-list", "--count", "HEAD..origin/main"])
behind = out.strip()
print(f"[5] local={local[:9]} remote={remote[:9]} behind={behind} delivery={'OK' if local == remote else 'FAIL'}")

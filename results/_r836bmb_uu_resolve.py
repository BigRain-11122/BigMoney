import subprocess, sys, os

ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"

def run(cmd, **kw):
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, **kw)
    return r.returncode, r.stdout, r.stderr

# 1. full unmerged set (content-driven, r790 law)
rc, out, err = run(["git", "ls-files", "-u"])
paths = sorted(set(l.split("\t")[1] for l in out.splitlines() if "\t" in l))
print(f"[1] UU faces: {len(paths)}")

# 2. take stage2 (origin, ts-audit winner) per face
for p in paths:
    rc, out, err = run(["git", "checkout", "--ours", "--", p])
    if rc != 0:
        print(f"[2] CHECKOUT-FAIL {p}: {err.strip()}"); sys.exit(2)
print(f"[2] checkout --ours done on {len(paths)} faces (all STAGE2=origin per deep-ts audit)")

# 3. pool face settle per S0 reland law (idempotent heal after re-land)
rc, out, err = run(["python", "scripts\\merge_lane_views.py", "sync_face"])
print(f"[3] sync_face rc={rc} :: {(out or err).strip()[:200]}")

# 4. marker scan on resolved faces (r829 law: tree must be marker-free)
bad = []
for p in paths:
    fp = os.path.join(ROOT, p)
    if os.path.exists(fp):
        try:
            for i, line in enumerate(open(fp, encoding="utf-8", errors="replace")):
                if line.startswith("<<<<<<<") or line.startswith(">>>>>>>") or line.startswith("|||||||||"):
                    bad.append(f"{p}:L{i+1}")
        except Exception as e:
            bad.append(f"{p}:ERR {e}")
if bad:
    print(f"[4] MARKER-FAIL {bad}"); sys.exit(3)
print("[4] marker scan clean")

# 5. atomic add -A + rebase --continue (r787/r855: absorb daemon churn into continue commit)
env = dict(os.environ); env["GIT_EDITOR"] = "true"
rc, out, err = run(["git", "add", "-A"])
if rc != 0:
    print(f"[5] ADD-FAIL: {err.strip()}"); sys.exit(4)
rc, out, err = run(["git", "rebase", "--continue"], env=env)
print(f"[5] continue rc={rc}\n{out.strip()[:600]}\n{err.strip()[:600]}")

# 6. post-state
rc, out, err = run(["git", "status", "--porcelain"])
uu = [l for l in out.splitlines() if l.startswith("UU")]
print(f"[6] post: UU={len(uu)}\n{chr(10).join(uu[:10])}")
rc, out, err = run(["git", "log", "--oneline", "-3"])
print(f"[6] HEAD: {out.strip()}")

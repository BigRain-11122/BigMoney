import hashlib, json, os, subprocess, sys

TMP = os.path.join(os.environ.get("TEMP", "."), "fg-dec-bmb")
REPO = "git@github.com:BigRain-11122/FluxGroup.git"

def sh(args, cwd=None, **kw):
    return subprocess.run(args, capture_output=True, cwd=cwd, **kw)

# ensure temp partial clone (r481 bm-b recipe)
if not os.path.isdir(os.path.join(TMP, ".git")):
    r = sh(["git", "clone", "--depth", "1", "--filter=blob:none", "--no-checkout", REPO, TMP])
    if r.returncode != 0:
        print("CLONE FAIL:", r.stderr.decode()[:300]); sys.exit(2)
sh(["git", "-C", TMP, "fetch", "origin"])
r = sh(["git", "-C", TMP, "show", "origin/main:docs/decisions.md"])
if r.returncode != 0:
    print("SHOW FAIL:", r.stderr.decode()[:200]); sys.exit(2)
new_sha = hashlib.sha256(r.stdout).hexdigest().upper()
st = json.load(open("state.json", encoding="utf-8"))
old_sha = str(st.get("last_decisions_sha", "")).upper()
print("decisions.md sha(new):", new_sha)
print("state watermark       :", old_sha)
print("verdict:", "MATCH-unchanged" if new_sha == old_sha else "CHANGED")
# CEO physical-items section from orders.md (per D-19 law)
r2 = sh(["git", "-C", TMP, "show", "origin/main:docs/orders.md"])
tail = r2.stdout.decode("utf-8", "replace")
print("--- docs/orders.md CEO to-do tail (last 1200 chars) ---")
print(tail[-1200:] if tail else "(empty)")

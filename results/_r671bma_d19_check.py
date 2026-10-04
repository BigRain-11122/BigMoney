"""r671 bm-a D-19 decisions watermark check (r660: subprocess raw bytes only)."""
import subprocess, json, hashlib, os, sys

BIGMONEY = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
GRP = r"K:\Fluxgroup\FluxGroup"

def find_group_repo():
    if os.path.exists(GRP + r"\.git"):
        return GRP
    # fallback local paths
    for c in (r"C:\Fluxgroup\FluxGroup",):
        if os.path.exists(c + r"\.git"):
            return c
    return None

repo = find_group_repo()
if repo is None:
    print("GROUP_TREE: absent -> sparse clone fallback required")
    sys.exit(0)

subprocess.run(["git", "-C", repo, "fetch", "origin"], capture_output=True, timeout=120)
r = subprocess.run(["git", "-C", repo, "show", "origin/main:docs/decisions.md"], capture_output=True, timeout=60)
if r.returncode != 0:
    print("GIT_SHOW_FAIL:", r.stderr[:200])
    sys.exit(0)
blob = r.stdout
sha = hashlib.sha256(blob).hexdigest()

st = json.load(open(BIGMONEY + r"\state-bm-a.json", encoding="utf-8"))
wm = st.get("last_decisions_sha", "")
same = (sha == wm)
out = open(r"C:\Users\sjs20\AppData\Local\Temp\r671_d19.txt", "w", encoding="utf-8")
out.write(f"group_repo={repo}\nnew_sha={sha}\nstate_sha={wm}\nverdict={'MATCH-zero-action' if same else 'CHANGED'}\n")
if not same:
    # extract lines not yet consumed: show last 15 lines of blob
    tail = blob.decode("utf-8", "replace").splitlines()[-15:]
    out.write("--- tail 15 lines ---\n")
    out.write("\n".join(tail) + "\n")
out.close()
print("verdict:", "MATCH" if same else "CHANGED")

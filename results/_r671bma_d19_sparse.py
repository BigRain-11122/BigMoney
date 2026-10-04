"""r671 bm-a D-19 sparse clone fallback (r631 recipe + r660 git-show raw bytes law)."""
import subprocess, json, hashlib, os, shutil, tempfile

BIGMONEY = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
TMP = os.path.join(tempfile.gettempdir(), "fg_sparse_d19")
URL = "https://github.com/BigRain-11122/FluxGroup.git"

if os.path.exists(TMP):
    shutil.rmtree(TMP, ignore_errors=True)

r = subprocess.run(["git", "clone", "--depth", "1", "--filter=blob:none", "--sparse", URL, TMP],
                   capture_output=True, timeout=300)
if r.returncode != 0:
    print("CLONE_FAIL:", r.stderr.decode("utf-8", "replace")[:300])
    raise SystemExit(0)
subprocess.run(["git", "-C", TMP, "sparse-checkout", "set", "--skip-checks", "docs/decisions.md"], capture_output=True)
g = subprocess.run(["git", "-C", TMP, "show", "origin/main:docs/decisions.md"], capture_output=True)
if g.returncode != 0:
    print("SHOW_FAIL:", g.stderr.decode("utf-8", "replace")[:200])
    raise SystemExit(0)
blob = g.stdout
sha = hashlib.sha256(blob).hexdigest()

st = json.load(open(BIGMONEY + r"\state-bm-a.json", encoding="utf-8"))
wm = st.get("last_decisions_sha", "")
same = (sha == wm)
out = open(r"C:\Users\sjs20\AppData\Local\Temp\r671_d19.txt", "w", encoding="utf-8")
out.write(f"mode=sparse-clone\nnew_sha={sha}\nstate_sha={wm}\nverdict={'MATCH-zero-action' if same else 'CHANGED'}\n")
if not same:
    tail = blob.decode("utf-8", "replace").splitlines()[-20:]
    out.write("--- tail 20 ---\n" + "\n".join(tail) + "\n")
out.close()
shutil.rmtree(TMP, ignore_errors=True)
print("verdict:", "MATCH" if same else "CHANGED")

# r641 bm-b: D-19 decisions watermark check via temporary sparse clone
# (D-20261004-02③ fallback -- no group worktree visible in this session).
# Raw origin blob -> sha256 (upper-normalized), compare vs state.json watermark.
import hashlib, json, os, re, shutil, subprocess, sys, tempfile

CREATE_NO_WINDOW = 0x08000000
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RE_KEYWORD = re.compile(r"BigMoney|bigmoney|quant|bm-[abc]", re.IGNORECASE)

with open(os.path.join(ROOT, "state.json"), encoding="utf-8-sig") as fh:
    st = json.load(fh)
prev = (st.get("last_decisions_sha") or "").upper()

tmp = os.path.join(tempfile.gettempdir(), "fg-sparse-r641bmb")
if os.path.isdir(tmp):
    shutil.rmtree(tmp, ignore_errors=True)

r = subprocess.run(["git", "clone", "--depth", "1", "--filter=blob:none",
                    "--sparse", "https://github.com/BigRain-11122/FluxGroup.git", tmp],
                   capture_output=True, creationflags=CREATE_NO_WINDOW)
if r.returncode != 0:
    print("SPARSE CLONE FAIL rc=%d: %s" % (r.returncode, r.stderr.decode("utf-8", "replace")[:500]))
    sys.exit(2)
subprocess.run(["git", "-C", tmp, "sparse-checkout", "set", "--skip-checks",
                "docs/decisions.md", "docs/orders.md"], capture_output=True,
               creationflags=CREATE_NO_WINDOW)

def show(path):
    return subprocess.run(["git", "-C", tmp, "show", "origin/main:" + path],
                          capture_output=True, creationflags=CREATE_NO_WINDOW)

blob = show("docs/decisions.md").stdout
sha = hashlib.sha256(blob).hexdigest().upper()
print("D19_SPARSE_SHA:", sha[:16])
print("WATERMARK    :", prev[:16])
if sha == prev:
    print("D-19 MATCH (decisions watermark unchanged) -- zero action")
else:
    print("D-19 CHANGED: %s -> %s" % (prev[:12], sha[:12]))
    text = blob.decode("utf-8", "replace")
    hits = [ln for ln in text.splitlines() if RE_KEYWORD.search(ln)]
    print("--- keyword rows (%d, last 25) ---" % len(hits))
    for ln in hits[-25:]:
        print(ln[:280])
    print("--- decisions.md tail (last 15 lines) ---")
    for ln in text.splitlines()[-15:]:
        print(ln[:280])
    ob = show("docs/orders.md")
    if ob.returncode == 0:
        print("--- orders.md keyword rows (last 15) ---")
        for ln in ob.stdout.decode("utf-8", "replace").splitlines():
            if RE_KEYWORD.search(ln):
                print(ln[:280])

shutil.rmtree(tmp, ignore_errors=True)
print("TEMP CLEANED:", not os.path.isdir(tmp))
sys.exit(0)

# r655 bm-b D-19 fallback: temp sparse clone, hash origin blob bytes (r660 law: never hash checked-out files)
import json, hashlib, os, subprocess, tempfile

url = "https://github.com/BigRain-11122/FluxGroup.git"
tmp = os.path.join(tempfile.gettempdir(), "fg-sparse-r655")
if not os.path.isdir(os.path.join(tmp, ".git")):
    r = subprocess.run(["git", "clone", "--depth", "1", "--filter=blob:none", "--sparse", url, tmp],
                       capture_output=True)
    if r.returncode != 0:
        print("CLONE_FAIL", r.stderr.decode("utf-8", "replace")[:300]); raise SystemExit(2)
subprocess.run(["git", "-C", tmp, "fetch", "origin"], capture_output=True)

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
st = json.load(open(os.path.join(root, "state.json"), encoding="utf-8"))
for label, key, path in [("DECISIONS", "last_decisions_sha", "docs/decisions.md"),
                         ("GORDERS", "last_orders_sha", "docs/orders.md")]:
    r = subprocess.run(["git", "-C", tmp, "show", "origin/main:" + path], capture_output=True)
    if r.returncode != 0:
        print("%s SHOW_FAIL %s" % (label, r.stderr.decode("utf-8", "replace")[:200])); continue
    b = r.stdout
    sha = hashlib.sha256(b).hexdigest().upper()
    prev = st.get(key, "")
    print("%s sha=%s prev_match=%s bytes=%d" % (label, sha[:16], "MATCH" if sha == prev else "CHANGED", len(b)))
    if sha != prev:
        open(os.path.join(root, "results", "_r655bmb_%s_new.txt" % label.lower()), "wb").write(b)
        print("%s CHANGED -> blob dumped" % label)
print("PROBE_DONE")

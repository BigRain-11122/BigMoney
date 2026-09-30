# r495 bm-b S0.5: orders diff + D-19 group-ledger fresh read (r481 partial-clone recipe, r503 case-normalize law)
import hashlib, json, os, subprocess, sys, tempfile

ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
hb = json.load(open(os.path.join(ROOT, "fleet", "machines", "bm-b.json"), encoding="utf-8"))
acked = set(hb.get("orders_ack", []))
files = set(f for f in os.listdir(os.path.join(ROOT, "fleet", "orders")) if f.endswith(".md") and f.startswith("O-"))
missing = sorted(files - acked)
print("ORDERS_DIFF missing_ack:", missing if missing else "EMPTY (all %d acked)" % len(files))

# --- D-19 fresh read via temp partial clone (bm-b has no group tree) ---
tmp = os.path.join(tempfile.gettempdir(), "fg-dec-bmb")
G = ["git", "-C", tmp]
if not os.path.isdir(os.path.join(tmp, ".git")):
    r = subprocess.run(["git", "clone", "--depth", "1", "--filter=blob:none", "--no-checkout",
                        "git@github.com:BigRain-11122/FluxGroup.git", tmp], capture_output=True, text=True)
    if r.returncode != 0:
        print("CLONE_FAIL:", r.stderr.strip()[:300]); sys.exit(0)
else:
    subprocess.run(G + ["fetch", "origin"], capture_output=True)

def show(path):
    r = subprocess.run(G + ["show", "origin/main:" + path], capture_output=True)
    return r.stdout if r.returncode == 0 else None

dec = show("docs/decisions.md")
if dec is None:
    print("DECISIONS_READ_FAIL rc!=0"); sys.exit(0)
sha = hashlib.sha256(dec).hexdigest().upper()
st = json.load(open(os.path.join(ROOT, "state.json"), encoding="utf-8"))
prev = str(st.get("last_decisions_sha", "")).upper()
print("D19_DECISIONS_SHA:", sha)
print("D19_VERDICT:", "MATCH-unchanged" if sha == prev else "CHANGED prev=%s" % prev)
if sha != prev:
    text = dec.decode("utf-8", errors="replace")
    lines = text.splitlines()
    print("--- decisions.md TAIL-40 ---")
    for L in lines[-40:]:
        print(L)
    print("--- bigmoney-relevant lines ---")
    for i, L in enumerate(lines):
        low = L.lower()
        if ("bigmoney" in low or "quant" in low or "bm-" in low) and L.strip().startswith("|"):
            print("L%d: %s" % (i + 1, L.strip()[:200]))
    o = show("docs/orders.md")
    if o is not None:
        print("--- orders.md (group CEO pending physicals) ---")
        for L in o.decode("utf-8", errors="replace").splitlines():
            low = L.lower()
            if "bigmoney" in low or "quant" in low or "bm-" in low:
                print("O:", L.strip()[:200])

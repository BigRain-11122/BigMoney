# r1026 S0.5 dual-delta row extraction (pinned methods: ORD=content-bytes sha1, DEC=raw-blob sha256)
import subprocess, hashlib, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

GT = r"K:\Fluxgroup\FluxGroup"
def show(path):
    p = subprocess.run(["git", "-C", GT, "show", "origin/main:" + path], capture_output=True)
    if p.returncode != 0:
        print("SHOW FAIL", path, p.stderr.decode('utf-8', 'replace')); sys.exit(2)
    return p.stdout

subprocess.run(["git", "-C", GT, "fetch", "origin"], capture_output=True)

ord_blob = show("docs/orders.md")
dec_blob = show("docs/decisions.md")
ord_sha = hashlib.sha1(ord_blob).hexdigest()
dec_sha = hashlib.sha256(dec_blob).hexdigest()
print("ORD content-sha1:", ord_sha)
print("DEC raw-sha256 :", dec_sha)

state = json.load(open(r"K:\Fluxgroup\FluxGroup\quant\bigmoney\state-bm-c.json", encoding='utf-8'))
print("state ORD key  :", state.get("last_orders_sha"))
print("state DEC key  :", state.get("last_decisions_sha"))
print("ORD delta:", ord_sha != state.get("last_orders_sha"), "| DEC delta:", dec_sha != state.get("last_decisions_sha"))

# --- tail rows for eyeball: last 45 lines of orders.md ---
lines = ord_blob.decode('utf-8', 'replace').splitlines()
print("\n=== ORD tail 45 lines ===")
for l in lines[-45:]:
    print(l[:400])
print("\n=== DEC tail 15 lines ===")
dl = dec_blob.decode('utf-8', 'replace').splitlines()
for l in dl[-15:]:
    print(l[:400])

import subprocess, hashlib, sys, io, json, os, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
GRP = r"C:\Users\sjs20\Desktop\FluxGroup"
GIT = r"C:\Program Files\Git\cmd\git.exe"

def run(*a, cwd=os.getcwd()):
    r = subprocess.run([GIT] + list(a), capture_output=True, cwd=cwd)
    return r.stdout

dec = run('show', 'origin/main:docs/decisions.md', cwd=GRP)
ord_ = run('show', 'origin/main:docs/orders.md', cwd=GRP)
print("FULL dec sha1:", hashlib.sha1(dec).hexdigest())
print("FULL ord sha1:", hashlib.sha1(ord_).hexdigest())

# heartbeat structure
hb = json.load(open('fleet/machines/bm-a.json', encoding='utf-8'))
print("\nheartbeat keys:", sorted(hb.keys()))
ack = hb.get('orders_ack')
if isinstance(ack, list):
    print("orders_ack: list len", len(ack), "last3:", ack[-3:])
elif isinstance(ack, dict):
    print("orders_ack: dict keys sample:", list(ack.keys())[-3:])
else:
    print("orders_ack:", str(ack)[:200])

# fleet orders diff scan
order_files = sorted(glob.glob('fleet/orders/O-*.md'))
ids = [os.path.basename(f)[:-3] for f in order_files]
if isinstance(ack, list):
    unacked = [i for i in ids if i not in ack]
elif isinstance(ack, dict):
    unacked = [i for i in ids if i not in ack]
else:
    unacked = ids
print("\nfleet orders total:", len(ids), "| unacked:", unacked)

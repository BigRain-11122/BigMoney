"""r893(bm-a) closeout preflight: attrition scan + orders diff + inbox + self-heal quad."""
import subprocess, sys, os, io, json, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
out = []

def log(s):
    out.append(s)

# 1) attrition ledger guard scan
p = subprocess.run([sys.executable, "scripts/attrition_ledger_guard.py", "scan"],
                  capture_output=True, timeout=120)
log("attrition rc=%d" % p.returncode)
tail = (p.stdout or b"").decode("utf-8", "replace").strip().splitlines()
log("attrition tail: " + (tail[-1] if tail else "(none)"))

# 2) local orders diff vs heartbeat ack
import json as J
heart = J.load(io.open("fleet/machines/bm-a.json", encoding="utf-8"))
acked = set(heart.get("orders_ack") or [])
local_orders = set(os.path.basename(f) for f in glob.glob("fleet/orders/O-*.md"))
unacked = sorted(local_orders - acked)
log("local orders=%d acked=%d unacked=%s" % (len(local_orders), len(acked), unacked))

# 3) inbox unprocessed for bm-a/ALL
inbox_new = []
for f in glob.glob("fleet/inbox/*.md") + glob.glob("fleet/inbox/*.json"):
    base = os.path.basename(f)
    if os.path.exists(os.path.join("fleet/inbox/processed", base)):
        continue
    try:
        head = io.open(f, encoding="utf-8", errors="replace").read()[:300]
    except Exception:
        head = "(unreadable)"
    inbox_new.append((base, head.replace("\n", " | ")[:200]))
log("inbox unprocessed: %d" % len(inbox_new))
for b, h in inbox_new[:10]:
    log("  INBOX %s :: %s" % (b, h))

# 4) watermark verdict view
try:
    wm = J.load(io.open("results/watermark_red.json", encoding="utf-8"))
    log("watermark: red=%s reason=%s next_pick=%s" % (wm.get("red"), wm.get("reason"), wm.get("next_pick")))
except Exception as e:
    log("watermark read err %s" % e)

# 5) hooks existence (claws)
for hook in ("pre-commit", "pre-push"):
    hp = os.path.join(".git", "hooks", hook)
    log("hook %s: %s" % (hook, "PRESENT" if os.path.exists(hp) else "MISSING"))

# 6) scheduled tasks presence (read-only query via schtasks, silent wrapper not needed for /query? keep plain)
p = subprocess.run(["schtasks", "/query", "/tn", "Bigmoney-LoopWatchdog"],
                   capture_output=True, timeout=60)
log("watchdog task query rc=%d" % p.returncode)

io.open("results/_r893bma_closeout_preflight.txt", "w", encoding="utf-8").write("\n".join(out))
print("preflight done, lines=%d" % len(out))

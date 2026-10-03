"""_r425bmc_s7_probe.py -- S7 closing checks: orders double-scan + inbox unprocessed listing."""
import json, os

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
orders_dir = os.path.join(REPO, "fleet", "orders")
files = sorted(f for f in os.listdir(orders_dir) if f.startswith("O-") and f.endswith(".md"))
with open(os.path.join(REPO, "fleet", "machines", "bm-c.json"), encoding="utf-8") as fh:
    ack = set(json.load(fh).get("orders_ack", []))
unacked = [f for f in files if f not in ack]
print("S7 double-scan: orders_total=%d unacked=%d %s" % (len(files), len(unacked), unacked if unacked else "(zero-unacked)"))

inbox = os.path.join(REPO, "fleet", "inbox")
processed = os.path.join(REPO, "fleet", "inbox", "processed")
if os.path.isdir(inbox):
    live = [f for f in os.listdir(inbox) if f.endswith(".md") and os.path.isfile(os.path.join(inbox, f))]
    print("inbox live messages: %d %s" % (len(live), live if live else "(none)"))
    for f in live:
        p = os.path.join(inbox, f)
        head = open(p, encoding="utf-8", errors="replace").read(300).replace("\n", " | ")
        print("  %s :: %s" % (f, head))
else:
    print("inbox dir missing")

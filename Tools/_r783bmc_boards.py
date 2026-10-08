"""r783 bm-c S2 boards probe (1-gen clone of _r781bmc_boards.py):
fleet tasks open tickets, watermark_red state, inbox pending count."""
import glob
import json
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

open_tickets = []
claimed_by_me = []
for f in sorted(glob.glob(os.path.join(REPO, "fleet", "tasks", "*.json"))):
    try:
        with open(f, encoding="utf-8") as fh:
            t = json.load(fh)
    except Exception as e:
        print("PARSE_FAIL", os.path.basename(f), str(e)[:120])
        continue
    st = t.get("status")
    tid = t.get("id") or os.path.basename(f)
    if st == "open":
        open_tickets.append(tid)
    if st in ("claimed", "in_progress") and t.get("claimed_by") == "bm-c":
        claimed_by_me.append(tid)
print("tickets_total=", len(glob.glob(os.path.join(REPO, "fleet", "tasks", "*.json"))))
print("open_tickets=", open_tickets)
print("claimed_by_bm_c=", claimed_by_me)

wm_path = os.path.join(REPO, "results", "watermark_red.json")
if os.path.exists(wm_path):
    with open(wm_path, encoding="utf-8") as fh:
        wm = json.load(fh)
    print("watermark_red=", json.dumps(wm, ensure_ascii=False)[:600])
else:
    print("watermark_red= MISSING")

inbox = sorted(os.path.basename(f) for f in glob.glob(
    os.path.join(REPO, "fleet", "inbox", "*.md")))
print("inbox_pending=", inbox)

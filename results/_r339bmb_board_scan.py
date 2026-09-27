# r339 bm-b S2: dual task board scan + watermark verdict probe
import json, glob, os

# fleet\tasks board
rows = []
for p in sorted(glob.glob("fleet/tasks/*.json")):
    try:
        with open(p, encoding="utf-8") as f:
            t = json.load(f)
    except Exception as e:
        print("PARSE_FAIL", p, e); continue
    rows.append((os.path.basename(p), t.get("status"), t.get("claimed_by"), t.get("priority"), bool(t.get("immediate"))))
open_t = [r for r in rows if r[1] == "open"]
claimed_me = [r for r in rows if r[2] == "bm-b" and r[1] in ("claimed", "in_progress")]
immediate_open = [r for r in rows if r[4] and r[1] in ("open", "claimed")]
from collections import Counter
print("total tickets:", len(rows), "| status counts:", dict(Counter(r[1] for r in rows)))
print("OPEN tickets:", [r[0] for r in open_t] or "none")
print("immediate-flagged (open/claimed):", [(r[0], r[1], r[2]) for r in immediate_open] or "none")
print("claimed_by bm-b (active):", [(r[0], r[1], r[3]) for r in claimed_me] or "none")

# watermark red flag
wr_p = "results/watermark_red.json"
if os.path.exists(wr_p):
    with open(wr_p, encoding="utf-8") as f:
        wr = json.load(f)
    print("watermark_red:", json.dumps(wr, ensure_ascii=False)[:400])
else:
    print("watermark_red.json absent")

# py_watermark latest verdict from watermark.jsonl (local, gitignored)
try:
    with open("results/watermark.jsonl", encoding="utf-8") as f:
        lines = f.readlines()
    last = json.loads(lines[-1])
    print("watermark.jsonl last:", json.dumps({k: last.get(k) for k in ("ts", "verdict", "py_cpu_pct", "local_batch_running")}, ensure_ascii=False))
except Exception as e:
    print("watermark.jsonl:", "ERR", e)

# inbox
inbox = [os.path.basename(p) for p in glob.glob("fleet/inbox/*") if os.path.basename(p) not in ("processed", "README.md")]
print("inbox unprocessed:", inbox or "none")

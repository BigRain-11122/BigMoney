# -*- coding: utf-8 -*-
"""r835 bm-c rebase conflict resolver: receipts = ts-newer-wins (reland per-face law), T-182 = notes union."""
import subprocess, json, re

def stage(side, path):
    r = subprocess.run(["git", "show", ":%d:%s" % (side, path)], capture_output=True)
    return r.stdout.decode("utf-8", "replace")

def ts_of(text):
    m = re.search(r'"ts"\s*:\s*"([^"]+)"', text)
    return m.group(1) if m else ""

FILES_TS = [
    "results/_attrition_guard_scan.json",
    "results/_r686bmb_d19_check.json",
    "results/_r686bmb_orders_fresh.md",
    "results/d19_watermark.json",
]
for fp in FILES_TS:
    ours = stage(2, fp)   # remote (rebase: ours = onto-side = origin)
    theirs = stage(3, fp) # mine (commit being replayed)
    to, tt = ts_of(ours), ts_of(theirs)
    pick = theirs if tt >= to else ours
    side = "MINE(theirs)" if tt >= to else "REMOTE(ours)"
    open(fp, "w", encoding="utf-8", newline="").write(pick)
    print("%s -> %s (remote ts=%s mine ts=%s)" % (fp, side, to or "?", tt or "?"))

# T-182 notes union: remote full JSON + my note appended
tp = "fleet/tasks/T-2026-10-10-182-P1.json"
remote_raw = stage(2, tp)
mine_raw = stage(3, tp)
rj = json.loads(remote_raw)
mj = json.loads(mine_raw)
my_note = None
# my note is the suffix of mj["notes"] not present in rj["notes"]
mn, rn = mj.get("notes", ""), rj.get("notes", "")
if mn.startswith(rn[:40]):
    my_note = mn[len(rn):] if mn.startswith(rn) else None
if my_note is None:
    # fallback: take whatever in mj.notes is not in rj.notes (token-level diff)
    my_note = mn[len(rn):] if len(mn) > len(rn) and rn in mn else " | r835 3rd-session note (union fallback, see git history)"
rj["notes"] = rn + my_note
open(tp, "w", encoding="utf-8", newline="").write(json.dumps(rj, ensure_ascii=False, indent=1))
print("T-182: notes union, remote_len=%d + mine_suffix=%d" % (len(rn), len(my_note)))

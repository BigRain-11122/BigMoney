"""r263 bm-b: autofill_state UU resolver (rebase step 1, commit 036eee75 replay vs origin be404abe).

Recipe per classify_conflicts.py = mixed-dict+ledger (r203/R208/r215/r220/r245):
- launches: union both blobs -> sort ts desc -> cap 50 (R215 rolling window) -> re-sort ts ASC before write-back (r245 format-face law)
- last_tick: compare inner ts dicts (no str()), newer wins; same-second tie -> ours (r140)
- write-back: mirror base-blob line ending + indent; assert isinstance(last_tick, dict); json.loads verify (r185)
"""
import json
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")

PATH = "results/autofill_state.json"

def blob(stage):
    out = subprocess.run(["git", "show", f"{stage}:{PATH}"], capture_output=True)
    return out.stdout

ours = json.loads(blob(":2").decode("utf-8-sig"))    # ours (my 036eee75 face)
theirs = json.loads(blob(":3").decode("utf-8-sig"))  # theirs (origin be404abe face)
base = blob(":1")                                     # merge base bytes for format mirroring

print("ours last_tick.ts:", ours.get("last_tick", {}).get("ts"), "| machine:", ours.get("last_tick", {}).get("machine"))
print("theirs last_tick.ts:", theirs.get("last_tick", {}).get("ts"), "| machine:", theirs.get("last_tick", {}).get("machine"))

# ---- last_tick: newer inner ts wins, same-second tie -> ours (r140) ----
ot = ours.get("last_tick", {}).get("ts", "")
tt = theirs.get("last_tick", {}).get("ts", "")
if tt > ot:
    last_tick = theirs["last_tick"]
    tick_side = "theirs"
elif tt < ot:
    last_tick = ours["last_tick"]
    tick_side = "ours"
else:
    last_tick = ours["last_tick"]
    tick_side = "ours-tie"
print("last_tick take:", tick_side)

# ---- launches: union -> desc -> cap 50 -> asc (R215 + r245) ----
l_ours = ours.get("launches", [])
l_theirs = theirs.get("launches", [])
seen = {}
for row in l_ours + l_theirs:
    key = (row.get("ts"), row.get("machine"), row.get("batch"))
    if key not in seen:
        seen[key] = row
union = list(seen.values())
union.sort(key=lambda r: r.get("ts", ""), reverse=True)
capped = union[:50]
capped.sort(key=lambda r: r.get("ts", ""))  # r245: write-back order = producer append order (ts ASC)
print("launches: ours", len(l_ours), "| theirs", len(l_theirs), "| union", len(union), "| capped50->asc", len(capped))

# ---- merged face: start from theirs (upstream structure owner precedence for unknown keys), overlay decisions ----
merged = dict(theirs)
merged["launches"] = capped
merged["last_tick"] = last_tick

assert isinstance(merged.get("last_tick"), dict), "last_tick not dict"

# ---- format mirroring from base blob ----
crlf = base.count(b"\r\n") > 0 and base.count(b"\r\n") >= base.count(b"\n") - base.count(b"\r\n") * 0
use_crlf = base.count(b"\r\n") > 0
txt = base.decode("utf-8-sig") if base[:3] == b"\xef\xbb\xbf" else base.decode("utf-8")
bom = base[:3] == b"\xef\xbb\xbf"
indent = 1 if "\n \"launches\"" in txt or "\n \"ts\"" in txt else 2
for line in txt.splitlines():
    if line.startswith((" \"", "  \"")):
        indent = 1 if line.startswith(' "') else 2
        break
print("format: CRLF", use_crlf, "| BOM", bom, "| indent", indent)

out = json.dumps(merged, ensure_ascii=False, indent=indent)
if use_crlf:
    out = out.replace("\n", "\r\n")
if bom:
    out = "\ufeff" + out
with open("results/autofill_state.json", "w", encoding="utf-8", newline="") as f:
    f.write(out + ("\r\n" if use_crlf else "\n"))

# verify: re-read parse + keys
with open("results/autofill_state.json", encoding="utf-8-sig") as f:
    v = json.load(f)
assert isinstance(v["last_tick"], dict) and isinstance(v["launches"], list)
ts_seq = [r.get("ts", "") for r in v["launches"]]
assert ts_seq == sorted(ts_seq), "launches not ts-ascending (r245 violation)"
print("resolver done: last_tick", tick_side, "| launches", len(v["launches"]), "ts-asc verified | parse OK")

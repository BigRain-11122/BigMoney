"""r190 stash-pop autofill_state conflict resolver (r161/r185 recipe).

Single-block or multi-block conflict: scan marker lines, take both sides,
union launches by (ts,id) keys, last_tick take-new, rebuild canonical JSON.
Both-side texts lack the outside-block common tail (top-level '}') when the
conflict block is not at EOF -> append the post-block common tail before parse
(R185 law). Parse-verify BEFORE git add (r185 ordering law: no unconditional
add after the script).
"""
import json
import re
import subprocess
import sys

PATH = "results/autofill_state.json"
raw = open(PATH, encoding="utf-8").read()

lines = raw.splitlines()
blocks = []
i = 0
while i < len(lines):
    if lines[i].startswith("<<<<<<<"):
        start = i
        mid = None
        end = None
        for j in range(i + 1, len(lines)):
            if lines[j].startswith("=======") and mid is None:
                mid = j
            elif lines[j].startswith(">>>>>>>"):
                end = j
                break
        if mid is None or end is None:
            print("MALFORMED block at", start)
            sys.exit(2)
        blocks.append((start, mid, end))
        i = end + 1
    else:
        i += 1

print("conflict blocks:", len(blocks))
if not blocks:
    print("no markers -> nothing to do")
    sys.exit(0)

# outside-block common tail after the last block (R185: needed for both-side parse)
tail = "\n".join(lines[blocks[-1][2] + 1:])

sides = {0: [], 1: []}  # ours(stash pop = ours is stashed local), theirs
for (s, m, e) in blocks:
    sides[0].extend(lines[s + 1: m])
    sides[1].extend(lines[m + 1: e])

parsed = {}
for idx in (0, 1):
    txt = "\n".join(sides[idx]) + "\n" + tail
    try:
        parsed[idx] = json.loads(txt)
        print(f"side{idx} parse OK, top keys: {sorted(parsed[idx].keys())}")
    except json.JSONDecodeError as ex:
        print(f"side{idx} parse FAIL: {ex}")
        sys.exit(2)

a, b = parsed[0], parsed[1]
out = dict(b)  # start from theirs (upstream/current), overlay ours' new evidence


def key_of(l):
    return (l.get("ts"), l.get("id") or l.get("shard") or l.get("batch") or json.dumps(l, sort_keys=True)[:80])


la, lb = a.get("launches", []), b.get("launches", [])
union = {key_of(x): x for x in lb}
for x in la:
    union[key_of(x)] = x
merged = sorted(union.values(), key=lambda x: str(x.get("ts", "")))
out["launches"] = merged[-50:]
print("launches union:", len(la), "+", len(lb), "->", len(out["launches"]))

for k in ("last_tick", "updated_at", "generated_at"):
    if k in a or k in b:
        va, vb = a.get(k), b.get(k)
        out[k] = max(filter(None, [va, vb]), key=lambda s: str(s))
        print(k, "take-new:", out[k])

with open(PATH, "w", encoding="utf-8", newline="\n") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
chk = json.load(open(PATH, encoding="utf-8"))
print("reparse OK; launches:", len(chk.get("launches", [])), "; last_tick:", chk.get("last_tick"))

# marker re-scan (r161 step0)
rr = subprocess.run(["git", "diff", "--check"], capture_output=True, text=True)
if rr.stdout.strip():
    print("diff --check reports:", rr.stdout[:300])
    sys.exit(2)
print("clean: no conflict markers, valid JSON. Now: git add results/autofill_state.json")

"""r199bmc rebase conflict resolver: results/x2_watch_log.jsonl (single conflict block).

Batch-83 law: multiset-union, multiplicity preserved, ts-sorted.
HEAD side = bm-a r414 lines (05:12:30); c9b3c796 side = bm-c r199 S6 lines (05:08:46-52).
Line-level JSON parse-verify BEFORE write (r185 ordering law), full reparse after write.
"""
import json

PATH = "results/x2_watch_log.jsonl"
lines = open(PATH, encoding="utf-8").read().splitlines()

common, head_side, my_side = [], [], []
state = "common"
for ln in lines:
    if ln.startswith("<<<<<<<"):
        state = "head"
        continue
    if ln.startswith("|||||||"):       # diff3 base section: ancestor state, drop
        state = "base"
        continue
    if ln.startswith("======="):
        state = "mine"
        continue
    if ln.startswith(">>>>>>>"):
        state = "common"
        continue
    if state == "base":
        continue                        # append-only law: base superseded by union
    if ln.strip():          # skip blank artifacts inside conflict blocks
        {"common": common, "head": head_side, "mine": my_side}[state].append(ln)

def verify(side_lines, name):
    for i, ln in enumerate(side_lines):
        obj = json.loads(ln)
        assert "ts" in obj and "trader" in obj, (name, i)
    return [json.loads(ln) for ln in side_lines]

head_objs = verify(head_side, "head")
mine_objs = verify(my_side, "mine")
print(f"parse OK: common={len(common)} head={len(head_side)} mine={len(my_side)}")

union = head_objs + mine_objs          # multiset: both kept, multiplicity preserved
union.sort(key=lambda o: (o["ts"], o.get("trader", "")))

# common prefix must also parse (full-file integrity)
verify(common, "common")

final_lines = common + [json.dumps(o, ensure_ascii=False) for o in union]
with open(PATH, "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(final_lines) + "\n")

chk = [json.loads(ln) for ln in open(PATH, encoding="utf-8").read().splitlines()]
assert len(chk) == len(final_lines)
assert chk[-1]["ts"] >= chk[0]["ts"] or len(chk) <= 1
tail_ts = [o["ts"] for o in chk[-13:]]
print("reparse OK. total lines:", len(chk), "| tail ts:", tail_ts[0], "->", tail_ts[-1])

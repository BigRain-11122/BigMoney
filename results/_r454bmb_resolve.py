# r454 bm-b S0 rebase replay conflict resolver (canonical: append-log union, r188/r217)
# marks-20260930.jsonl add/add -> union both stage blobs line-level, parse-verify, write back.
import json, subprocess, sys

PATH = "results/paper/marks/marks-20260930.jsonl"

def blob_lines(rev):
    raw = subprocess.run(["git", "show", rev], capture_output=True, check=True).stdout
    text = raw.decode("utf-8")
    lines = [l for l in text.split("\n") if l.strip()]
    parsed = []
    for l in lines:
        parsed.append(json.loads(l))  # parse-verify every line (r185 law)
    return lines, parsed

_, ours = blob_lines(":2:" + PATH)   # ours = replayed r453 side
_, theirs = blob_lines(":3:" + PATH)  # theirs = origin/main side

# union preserving order: theirs (origin) first as base, then ours-new lines
seen, out = set(), []
for src in (theirs, ours):
    for obj in src:
        key = json.dumps(obj, sort_keys=True, ensure_ascii=False)
        if key not in seen:
            seen.add(key)
            out.append(json.dumps(obj, ensure_ascii=False))

union_text = "\n".join(out) + ("\n" if out else "")
with open(PATH, "wb") as f:
    f.write(union_text.encode("utf-8"))

print(json.dumps({
    "path": PATH,
    "theirs_lines": len(theirs),
    "ours_lines": len(ours),
    "union_lines": len(out),
    "zero_loss": len(out) == len(seen),
    "union_eq_union_count": len(out),
}, ensure_ascii=False))

"""r1049 bm-a: x2_watch_log.jsonl rebase-conflict union resolver.

Family law: shared append-only jsonl conflicts = UNION both sides (line-level
exact dedupe + ts-field sort), never take-one-side (r419 pit: jsonl union must
be raw-line, no pretty-blob). Markers: <<<<<<< / ======= / >>>>>>> structural.
Asserts: every kept line parses as JSON, zero markers remain, monotonic ts.
"""
import json
import re
import sys

PATH = r"results\x2_watch_log.jsonl"
TS_RE = re.compile(r'"ts":\s*"([^"]+)"')

with open(PATH, "rb") as f:
    raw = f.read()
text = raw.decode("utf-8")
eol = "\r\n" if "\r\n" in text else "\n"
lines = [l for l in text.replace("\r\n", "\n").split("\n") if l != ""]

marker_lines = [l for l in lines if l.startswith(("<<<<<<<", "=======", ">>>>>>>"))]
content_lines = [l for l in lines if not l.startswith(("<<<<<<<", "=======", ">>>>>>>"))]
assert marker_lines, "no conflict markers found -- file already resolved?"

# exact-line dedupe (order-preserving first-wins, then ts sort)
seen = set()
uniq = []
for l in content_lines:
    if l not in seen:
        seen.add(l)
        uniq.append(l)

def ts_key(l):
    m = TS_RE.search(l)
    return m.group(1) if m else ""

for l in uniq:
    json.loads(l)  # every line must be valid JSON
uniq.sort(key=ts_key)

# monotonic assertion
keys = [ts_key(l) for l in uniq]
assert keys == sorted(keys), "ts not monotonic after union"

out = eol.join(uniq) + eol
with open(PATH, "wb") as f:
    f.write(out.encode("utf-8"))
print(json.dumps({"resolved": True, "marker_lines_removed": len(marker_lines),
                  "content_lines_in": len(content_lines),
                  "union_lines_out": len(uniq),
                  "first": keys[0] if keys else None,
                  "last": keys[-1] if keys else None}))
sys.exit(0)

"""r501 bm-b rebase conflict resolver: pool_core_samples.jsonl append-log union.

Conflict region: origin side (3 bm-c lines 10:10-10:11) vs local side (1 bm-b line 10:12:33).
Law: r188 line-level union zero-loss, dedupe domain = conflict region only (r294).
Union order = ts ascending. Verify: json.loads per line, line count = |A∪B| = 4.
"""
import json, io, re, sys

PATH = r"results/pool_core_samples.jsonl"

with io.open(PATH, "r", encoding="utf-8", newline="") as f:
    raw = f.read()

# Detect newline style from file body
crlf = raw.count("\r\n")
lf = raw.count("\n") - crlf
nl = "\r\n" if crlf > lf else "\n"

m = re.search(r"(<<<<<<< HEAD\r?\n)(.*?)(\r?\n=======\r?\n)(.*?)(\r?\n>>>>>>> )", raw, re.S)
if not m:
    print("NO_CONFLICT_MARKERS")
    sys.exit(3)

side_head = m.group(2)
side_local = m.group(4)
lines_head = [l for l in re.split(r"\r?\n", side_head) if l.strip()]
lines_local = [l for l in re.split(r"\r?\n", side_local) if l.strip()]

union = sorted(set(lines_head + lines_local), key=lambda l: json.loads(l)["ts"])

# zero-loss assertion
assert len(union) == len(set(lines_head)) + len(set(lines_local)) - len(set(lines_head) & set(lines_local)), "union count mismatch"
for l in union:
    json.loads(l)  # parse check

resolved_block = nl.join(union)
start, end = m.start(), m.end()
# rebuild: everything before conflict, resolved block, rest after '>>>>>>> <label>' line
rest = raw[end:]
rest = re.sub(r"^[^\r\n]*\r?\n", "", rest, count=1)  # drop the remainder of the >>>>>>> line
out = raw[:start] + resolved_block + nl + rest

for l in out.splitlines():
    if l.strip():
        json.loads(l)

with io.open(PATH, "w", encoding="utf-8", newline="") as f:
    f.write(out)

print("RESOLVED union_lines=%d head=%d local=%d nl=%r" % (len(union), len(lines_head), len(lines_local), nl))

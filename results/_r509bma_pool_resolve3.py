"""r509 bm-a rebase resolver #3: same W5-SHARD-11 provenance block, take-my-union.

ours (bm-c r309 line) = older done_at 09:40:04 pre-heal shape;
theirs (my commit) = union superset (claimed_since + harvest_claim +
newest done_at 09:53:15). Take theirs -- r299 newer-wins + relay-provenance.
"""
import re

PATH = "results/runnable_pool.json"
raw = open(PATH, encoding="utf-8", newline="").read()
pat = re.compile(
    r"<<<<<<< HEAD\r?\n(.*?)\r?\n=======\r?\n(.*?)\r?\n>>>>>>>[^\r\n]*\r?\n",
    re.S,
)
m = list(pat.finditer(raw))
assert len(m) == 1, f"expected 1 block, got {len(m)}"
ours, theirs = m[0].group(1), m[0].group(2)
o_done = re.search(r'"done_at": "([^"]+)"', ours)
t_done = re.search(r'"done_at": "([^"]+)"', theirs)
print("ours done_at:", o_done and o_done.group(1))
print("theirs done_at:", t_done and t_done.group(1))
assert t_done.group(1) >= o_done.group(1), "theirs not newer -- manual adjudication"

resolved = raw[:m[0].start()] + theirs + raw[m[0].end():]
import json
json.loads(resolved)  # validate BEFORE write this time
with open(PATH, "w", encoding="utf-8", newline="") as fh:
    fh.write(resolved)
print("resolved take-theirs, JSON validated pre-write")

"""r509 bm-a rebase resolver #2: runnable_pool.json claim-provenance block.

Conflict = shard claim/harvest bookkeeping (W5-SHARD-11 family). r299 law:
claim-ledger face = newer-timestamps win + provenance superset preserved.
My side (theirs in rebase orientation) carries claimed_since (original claim
time 09:38:43) + newer done_at 09:53:15 -> superset, take mine.
"""
import re

PATH = "results/runnable_pool.json"
raw = open(PATH, encoding="utf-8", newline="").read()
pat = re.compile(
    r"<<<<<<< HEAD\r?\n(.*?)\r?\n=======\r?\n(.*?)\r?\n>>>>>>>[^\r\n]*\r?\n",
    re.S,
)
m = list(pat.finditer(raw))
assert len(m) == 1, f"expected 1 conflict block, got {len(m)}"

ours, theirs = m[0].group(1), m[0].group(2)
o_lines = [l for l in ours.splitlines() if l.strip()]
t_lines = [l for l in theirs.splitlines() if l.strip()]


def keyof(line):
    return line.split(":")[0].strip().strip('"') if ":" in line else None


# union: ours (bm-b heal: original claim owner_since + newest authoritative
# done_at 09:53:15 from owner bm-c's own final harvest) + theirs-only
# provenance keys (claimed_since, harvest_claim = my daemon's convergent
# harvest trail, r299 relay-provenance law)
o_keys = {keyof(l) for l in o_lines}
union = list(o_lines)
for l in t_lines:
    k = keyof(l)
    if k not in o_keys:
        union.append(l)
        print("union adds theirs-only key:", k, "=", l[:80])
for l in o_lines:
    print("ours kept:", l[:80])
resolved = raw[:m[0].start()] + "\r\n".join(union) + "\r\n" + raw[m[0].end():]
with open(PATH, "w", encoding="utf-8", newline="") as fh:
    fh.write(resolved)

import json
p = json.loads(resolved)
n3 = [e for e in p["entries"] if e["id"].startswith("PERPETUAL-N3-R1-")]
w5 = [e for e in p["entries"] if "N1-W5" in e["id"]]
print(f"parse OK; N3 done={sum(e['status']=='done' for e in n3)}/6, "
      f"W5 done={sum(e['status']=='done' for e in w5)}/12")

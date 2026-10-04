# -*- coding: utf-8 -*-
"""r518 bm-c post_review ledger count: per-id LAST verdict (r514/r517 law --
NO rows suppressed by a later same-id YES re-derive are not unresolved).
Prints YES/NO/WAITING census; zero unresolved-NO = green."""
import collections
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "results", "post_review.jsonl")
last = {}
with open(P, encoding="utf-8") as fh:
    for ln in fh:
        ln = ln.strip()
        if not ln:
            continue
        try:
            j = json.loads(ln)
        except ValueError:
            continue  # historical residual line tolerated (r707 law)
        last[j.get("id", "?")] = j.get("verdict", "?")
c = collections.Counter(last.values())
unresolved_no = [k for k, v in last.items() if v == "NO"]
print("POST-REVIEW per-id last-verdict census: %s (ids=%d)" % (dict(c), len(last)))
print("UNRESOLVED-NO: %s" % (unresolved_no if unresolved_no else "none"))

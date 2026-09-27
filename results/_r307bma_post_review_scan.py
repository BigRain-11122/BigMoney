# -*- coding: utf-8 -*-
"""R307 bm-a: post_review open-negative scan (S3 discipline leg)."""
import json

neg = []
total = 0
with open(r"results\post_review.jsonl", encoding="utf-8") as fh:
    for line in fh:
        line = line.strip()
        if not line:
            continue
        total += 1
        try:
            r = json.loads(line)
        except Exception:
            continue
        verdict = str(r.get("verdict", ""))
        v = json.dumps(r, ensure_ascii=False)
        if verdict.strip().upper() in ("X", "NEG", "NEGATIVE", "FAIL"):
            neg.append((r.get("ts"), r.get("batch") or r.get("id"), verdict))
print("total rows:", total)
print("open negative rows:", len(neg))
for row in neg[-5:]:
    print("  ", row)

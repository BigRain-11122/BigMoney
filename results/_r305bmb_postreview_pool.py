# -*- coding: utf-8 -*-
"""r305 bm-b: post_review verdict-line scan (O-20260924-2115 discipline).

Substring hits on bare cross marks are protocol/description text (r303/r304
lesson); the authoritative face = parsed per-line JSON "verdict" field.
Console-safe printing (GBK console cannot encode U+2717)."""
import io
import json
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

lines = [l for l in io.open(r"results\post_review.jsonl", encoding="utf-8")
         .read().strip().splitlines() if l.strip()]
parsed, unparsed = [], 0
for l in lines:
    try:
        parsed.append(json.loads(l))
    except Exception:
        unparsed += 1
verdict_fail = [d for d in parsed if d.get("verdict") in ("fail", "error")]
verdict_pending = [d for d in parsed if d.get("verdict") == "pending"]
print("post_review: total_lines=%d parsed=%d unparsed=%d" % (
    len(lines), len(parsed), unparsed))
from collections import Counter
vc = Counter(repr(d.get("verdict")) for d in parsed)
print("verdict_value_census", dict(vc))
neg = [d for d in parsed if str(d.get("verdict") or "").find("\u2717") >= 0
       or str(d.get("verdict") or "").strip().upper() in
       ("NO", "FAIL", "ERROR", "PENDING")]
print("negative_verdict_lines=%d" % len(neg))
for d in neg[-4:]:
    print("  NEG:", json.dumps({k: d.get(k) for k in
                                ("ts", "id", "verdict")},
                               ensure_ascii=True)[:300])

# per-id resolution: a NO line superseded by a later same-id YES/WAIT is closed;
# a NO that is still the id's latest line = OPEN P0 face (O-20260924-2115).
latest = {}
for d in parsed:
    key = d.get("id")
    prev = latest.get(key)
    if prev is None or str(d.get("ts", "")) >= str(prev.get("ts", "")):
        latest[key] = d
open_neg = [d for d in neg if latest.get(d.get("id")) is d
            or str(latest[d.get("id")].get("ts", "")) <= str(d.get("ts", ""))]
open_neg = [d for d in open_neg
            if str(latest[d.get("id")].get("verdict", "")).strip().upper()
            in ("NO", "FAIL", "ERROR", "PENDING")]
print("open_negative_latest_per_id=%d" % len(open_neg))
for d in open_neg:
    print("  OPEN-NEG:", json.dumps({k: d.get(k) for k in
                                     ("ts", "id", "verdict")},
                                    ensure_ascii=True)[:200])
print("--- tail3 raw ids ---")
for d in parsed[-3:]:
    print("  TAIL:", d.get("ts"), d.get("id"), "verdict=", d.get("verdict"),
          "reviewer=", d.get("reviewer_verdict"))

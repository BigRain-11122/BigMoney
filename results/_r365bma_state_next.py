# -*- coding: utf-8 -*-
"""r365 bm-a final closeout: state next-pointer refresh (post-yield accurate)."""
import io
import json

p = "state-bm-a.json"
s = json.load(io.open(p, encoding="utf-8"))
assert s.get("round_no") == 365
s["next"] = (
    "Mon 09-28 09:15 T-91 s3 auto-fire (IntradayMarks 09:25 armed; first bar ~15:30 -> live.paper + t35 + "
    "exports; sysv1 first SIG-09-24 Top10 marks via bm-b BARS evening); T-95 = owner bm-c (sec.4 yield, my s1 "
    "side-branch freeze + adoption MSG sent, no bm-a action unless owner requests shard); T-94 shard claim per "
    "MSG-2335 (owner bm-b declare gate); MF/AH EM self-heal watch; council window 09-29 12:00; next 5x=R370"
)
io.open(p, "w", encoding="utf-8").write(json.dumps(s, ensure_ascii=False, indent=2) + "\n")
print("state next refreshed")

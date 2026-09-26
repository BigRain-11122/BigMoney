# -*- coding: utf-8 -*-
"""R272 bm-a: byte-face probe for state/heartbeat write-backs (five-face law R255/R257)."""
import json
import re

for p in ("state-bm-a.json", "fleet/machines/bm-a.json"):
    raw = open(p, "rb").read()
    txt = raw.decode("utf-8-sig")
    m = re.search(rb"\n(\s+)\"", raw[:400])
    print(p,
          "| BOM:", raw[:3] == b"\xef\xbb\xbf",
          "| CRLF:", b"\r\n" in raw,
          "| tail-nl:", raw.endswith(b"\n"),
          "| indent:", len(m.group(1)) if m else "single",
          "| ascii_esc:", "\\u" in txt[:300])

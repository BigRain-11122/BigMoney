"""r488 one-shot: flip PERPETUAL-N1-W2-SHARD-{2..7} to done (GM takeover receipt).

r289 law: probe indent + line endings of shared JSON before full rewrite;
after write, verify surgical via git diff --stat (caller does that).
"""
import json
import time

POOL = r"results/runnable_pool.json"
TAKEOVER_NOTE = ("bm-b r488 GM-takeover inline multicore burn (22s @ 8 workers/shard, "
                 "law: claimant heartbeat stale >20min -> healthy machine takes over; "
                 "bm-a heartbeat 45.8min stale at 02:03, no burn commits for 2-7 on "
                 "origin; runner deterministic byte-equal so zero double-burn harm)")

raw = open(POOL, "rb").read()
crlf = raw.count(b"\r\n")
lf_only = raw.count(b"\n") - crlf
has_bom = raw[:3] == b"\xef\xbb\xbf"
text = raw.decode("utf-8-sig" if has_bom else "utf-8")
indent = 1  # probe: detect leading indent of "version" key
for line in text.splitlines():
    if line.strip().startswith('"version"'):
        indent = len(line) - len(line.lstrip())
        break
print(f"probe: CRLF={crlf} LF_only={lf_only} BOM={has_bom} indent={indent}")

d = json.loads(text)
now = time.strftime("%Y-%m-%d %H:%M:%S")
flipped = []
for e in d.get("entries", []):
    eid = str(e.get("id", ""))
    if eid.startswith("PERPETUAL-N1-W2-SHARD-"):
        suf = int(eid.rsplit("-", 1)[1])
        if 2 <= suf <= 7:
            for s in e.get("shards", []):
                if s.get("status") != "done":
                    s["status"] = "done"
                    s["owner"] = "bm-b"
                    s["done_at"] = now
                    s["done_by"] = TAKEOVER_NOTE
                    flipped.append(s["key"])

out = json.dumps(d, ensure_ascii=False, indent=indent)
if crlf > lf_only:
    out = out.replace("\n", "\r\n")
with open(POOL, "w", encoding="utf-8", newline="") as f:
    f.write(out)
print("flipped:", sorted(flipped))

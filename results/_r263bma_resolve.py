# -*- coding: utf-8 -*-
"""R263 bm-a: T-83 claim-collision resolver (r239 判例族·fleet/README.md §4).

Same-window double-claim on T-2026-09-26-83-P1.json:
  bm-b claim 18:46:30 (s1 nine-layer inventory + s2 mechanical detection; s3 GM
  reserved; s4 open) -- EARLIER = canonical per commit-time ordering.
  bm-a claim 18:47:11 (mechanical lane scoped) -- LATER = yields.
Resolution: keep bm-b claim fields verbatim; bm-a fields converted to a
yield_note with the L9 orders-index artifact DONATED to the s1/s2 owner
(raw material, not the s3 deliverable; adjudication stays GM).
Byte faces mirrored: BOM=F, CRLF, indent=1, trailing newline, raw UTF-8.
"""
import io
import json

P = "fleet/tasks/T-2026-09-26-83-P1.json"
raw = open(P, "rb").read()
assert b"<<<<<<<" in raw and b">>>>>>>" in raw, "no conflict markers present"

lines = raw.decode("utf-8").splitlines()
out = []
mode = "copy"
kept_head_claim = False
for ln in lines:
    s = ln.strip()
    if s.startswith("<<<<<<<"):
        mode = "head"
        continue
    if s.startswith("======="):
        mode = "mine"
        continue
    if s.startswith(">>>>>>>"):
        mode = "done"
        continue
    if mode == "head":
        out.append(ln)          # bm-b claim fields verbatim (canonical)
        kept_head_claim = True
        continue
    if mode == "mine":
        continue                # bm-a claim fields dropped (yield)
    out.append(ln)

txt = "\n".join(out)
assert kept_head_claim, "bm-b canonical claim face lost"
assert '"claimed_by": "bm-a"' not in txt, "bm-a claim field must be gone (yield)"

t = json.loads(txt)   # parse-verify BEFORE write-back (r185 law)
# inject yield note one key before closing brace
txt = txt[: txt.rfind("}")].rstrip()
if not txt.endswith(","):
    txt += ","
txt += ("\n \"yield_note_bm_a\": \"bm-a R263 claim 18:47:11 yielded to bm-b 18:46:30 "
        "per fleet/README.md \\u00a74 commit-time ordering (41s later). DONATION to "
        "s1/s2 owner: raw L9 orders index artifact results/orders_index.json "
        "(83 orders, 33 real cross-refs after self-cite phantom purge, 1 honest "
        "empty-quote row; deterministic re-runnable results/_r263bma_orders_index.py; "
        "supersession ADJUDICATION deliberately reserved GM s3). bm-a steps off "
        "s1/s2; s4 quarterly wiring confirmation open for future bm-a rounds.\"\n}")
json.loads(txt)       # re-verify after injection
body = txt.replace("\n", "\r\n")
if raw.endswith(b"\n") and not body.endswith("\r\n"):
    body += "\r\n"
open(P, "wb").write(body.encode("utf-8"))
print("resolved: bm-b canonical claim kept, bm-a yield_note injected, parse-verified")

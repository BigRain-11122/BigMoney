# -*- coding: utf-8 -*-
"""R263 bm-a: five-face byte probe of T-83 ticket (R254/R255/R257 law) + scoped claim.

Claim scope per ticket note lane-affinity: bm-a claims the MECHANICAL-SWEEPS
lane only (s2 script faces + L9 orders index raw generation). s1 nine-layer
inventory authorship + s3 seven GM deliverables + canon/firm edits stay with
the GM (quant 专管) session. Write-back mirrors probed byte faces exactly.
"""
import io
import json
import time

P = "fleet/tasks/T-2026-09-26-83-P1.json"
raw = open(P, "rb").read()
print("BOM:", raw[:3] == b"\xef\xbb\xbf")
print("CRLF:", b"\r\n" in raw, "| bare-LF:", raw.count(b"\n") - raw.count(b"\r\n"))
print("trailing_newline:", raw.endswith(b"\n"))
txt = raw.decode("utf-8-sig")
lines = txt.splitlines()
for i, l in enumerate(lines[1:4], start=2):
    print(f"L{i}: indent={len(l) - len(l.lstrip())} | {l[:50]}")
print("has_unicode_escape:", "\\u" in txt)

t = json.loads(txt)
print("status:", t.get("status"))
t["status"] = "claimed"
t["claimed_by"] = "bm-a"
t["claimed_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
t["claim_scope_note"] = (
    "bm-a scoped claim R263 18:5x: MECHANICAL-SWEEPS lane only per note "
    "(s2 scriptable detection faces + L9 orders index raw generation -- "
    "first artifact results/orders_index.json landed 83 orders / 33 real "
    "cross-refs, deterministic re-runnable, supersession ADJUDICATION "
    "deliberately left to GM s3). s1 inventory authorship + s3 seven "
    "deliverables + firm/ canon edits = GM session, untouched by bm-a."
)
body = json.dumps(t, ensure_ascii=False, indent=1)
if raw[:3] == b"\xef\xbb\xbf":
    body = "\xef\xbb\xbf" + body
if b"\r\n" in raw:
    body = body.replace("\n", "\r\n")
if raw.endswith(b"\n") and not body.endswith("\r\n" if b"\r\n" in raw else "\n"):
    body += "\r\n" if b"\r\n" in raw else "\n"
open(P, "wb").write(body.encode("utf-8"))
print("ticket claimed (scoped), bytes:", len(body))

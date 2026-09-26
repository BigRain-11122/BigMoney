# -*- coding: utf-8 -*-
"""R258 bm-a: ticket byte-face probe (five-face law, raw bytes via subprocess)."""
import subprocess

raw = subprocess.run(
    ["git", "show", "HEAD:fleet/tasks/T-2026-09-26-73-P1.json"],
    capture_output=True).stdout
print("BOM:", raw.startswith(b"\xef\xbb\xbf"))
print("CRLF:", b"\r\n" in raw, "| LF-only:", (b"\n" in raw and b"\r\n" not in raw))
print("trailing-nl:", raw.endswith(b"\n"))
txt = raw.decode("utf-8-sig")
lines = txt.splitlines()
for i, l in enumerate(lines[:6]):
    print(i, repr(l[:50]))
print("progress key line:", repr(next(
    l for l in lines if '"progress_r245"' in l)[:40]))
print("non-ascii present:", any(ord(c) > 127 for c in txt))
print("total lines:", len(lines))

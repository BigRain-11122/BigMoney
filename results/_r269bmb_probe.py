"""r269 bm-b: byte-face probe of fleet/tasks/T-2026-09-26-81-P1.json HEAD blob
(R254/R255/R257 five-face law; R255 channel law: git cat-file direct bytes,
no PowerShell redirection)."""
import json
import re
import subprocess

out = subprocess.run(["git", "show", "HEAD:fleet/tasks/T-2026-09-26-81-P1.json"],
                     capture_output=True).stdout
print("BOM:", out[:3] == b"\xef\xbb\xbf")
print("CRLF:", b"\r\n" in out)
print("LF_only:", b"\r" not in out)
print("trailing_newline:", out.endswith(b"\n"))
txt = out.decode("utf-8-sig")
lines = txt.split("\n")
m = re.match(r'( +)"', lines[1])
print("indent:", len(m.group(1)) if m else "?")
print("raw_non_ascii:", any(ord(c) > 127 for c in txt))
d = json.loads(txt)
print("keys:", list(d.keys()))
print("status:", d.get("status"))

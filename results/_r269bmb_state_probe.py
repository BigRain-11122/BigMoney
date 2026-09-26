"""r269 bm-b closeout: probe state.json byte-face, append round-report line,
update state.json (bm-b canonical path logs/iteration-loop/state.json)."""
import io
import json
import re
import subprocess

out = subprocess.run(["git", "show", "HEAD:logs/iteration-loop/state.json"],
                     capture_output=True).stdout
print("BOM:", out[:3] == b"\xef\xbb\xbf")
print("CRLF:", b"\r\n" in out)
print("tail_nl:", out.endswith(b"\n"))
txt = out.decode("utf-8-sig")
line2 = txt.split("\n")[1]
m = re.match(r'( +)"', line2)
print("indent:", len(m.group(1)) if m else "?")
print("ascii_raw:", any(ord(c) > 127 for c in txt))
d = json.loads(txt)
print("state keys:", list(d.keys()))
print("round_no:", d.get("round_no"))

# -*- coding: utf-8 -*-
"""R259 bm-a: five-face byte probe of the T-73 ticket JSON before the
progress_r259 write (R254/R255/R257 laws: BOM/EOL/ensure_ascii/indent/
trailing-newline all mirrored; post-write diff must be field-level)."""
import io
import json
import subprocess

P = "fleet/tasks/T-2026-09-26-73-P1.json"
raw = subprocess.run(["git", "show", f"HEAD:{P}"], capture_output=True,
                     check=True).stdout
print("BOM:", raw.startswith(b"\xef\xbb\xbf"))
print("CRLF:", b"\r\n" in raw)
print("trailing_newline:", raw.endswith(b"\n"))
txt = raw.decode("utf-8-sig")
print("ensure_ascii_escape:", "\\u" in txt)
lines = txt.splitlines()
first_key_line = next(ln for ln in lines if ln.startswith(" "))
print("indent_spaces_first_line:", len(first_key_line) - len(first_key_line.lstrip(" ")))
d = json.loads(txt)
print("top_keys:", list(d.keys())[:8])
print("has_progress_r258:", "progress_r258" in d)

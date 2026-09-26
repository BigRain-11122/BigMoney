"""r263 bm-b: T-76 ticket five-face byte probe (R254/R255 law) before progress_r263 append."""
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")
path = "fleet/tasks/T-2026-09-26-76-P1.json"
raw = subprocess.run(["git", "show", "HEAD:" + path], capture_output=True).stdout  # R255: raw bytes via subprocess, no PS redirect
print("bytes:", len(raw))
print("BOM:", raw[:3] == b"\xef\xbb\xbf")
print("CRLF:", raw.count(b"\r\n"), "LF-total:", raw.count(b"\n"))
print("trailing_newline:", raw.endswith(b"\n"))
print("has_ensure_ascii_escapes:", b"\\u" in raw)
txt = raw.decode("utf-8-sig" if raw[:3] == b"\xef\xbb\xbf" else "utf-8")
for line in txt.splitlines():
    if line.startswith((" {", "{")) or line.startswith("}"):
        print("indent_sample:", repr(line[:24]))
        break

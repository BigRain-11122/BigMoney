import json
import subprocess

raw = subprocess.run(["git", "show", "HEAD:fleet/tasks/T-2026-09-26-76-P1.json"],
                     capture_output=True).stdout
print("BOM:", raw.startswith(b"\xef\xbb\xbf"), "CRLF:", b"\r\n" in raw, "len", len(raw))
txt = raw.decode("utf-8-sig")
lines = txt.split("\n")
print("indent line2:", repr(lines[1][:20]))
print("progress keys:", [k for k in json.loads(txt) if k.startswith("progress")])
print("last line:", repr(lines[-1][:40]) if lines[-1] else repr(lines[-2][:40]))
# check working-tree copy matches HEAD for this file
cur = open("fleet/tasks/T-2026-09-26-76-P1.json", "rb").read()
print("worktree==HEAD blob:", cur == raw)

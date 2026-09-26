# r264 bm-b: T-76 ticket progress_r264 append (R254/R255/R257 five-face law:
# probe ORIGINAL bytes via git cat-file subprocess, no PS redirection).
import json
import subprocess

P = "fleet/tasks/T-2026-09-26-76-P1.json"
blob = subprocess.run(["git", "show", f"HEAD:{P}"], capture_output=True, cwd=".").stdout
print("BOM:", blob.startswith(b"\xef\xbb\xbf"),
      "CRLF:", b"\r\n" in blob,
      "tail_nl:", blob.endswith(b"\n"),
      "ascii_esc:", b"\\u" in blob)
txt = blob.decode("utf-8-sig")
lines = txt.split("\n")
for ln in lines[1:6]:
    if ln.startswith(" "):
        print("indent probe:", repr(ln[:14]))
        break
d = json.loads(txt)
print("round keys:", [k for k in d if k.startswith("progress_r26")])

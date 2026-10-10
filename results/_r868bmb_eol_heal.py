# -*- coding: utf-8 -*-
"""r868 EOL heal: state.json + heartbeat rewritten with host CRLF face
(r289 law: json.dumps(...).replace('\n','\r\n')); round_reports.md final
line re-terminated CRLF (host dominant face). Content untouched."""
import json
import subprocess

for path in ("state.json", "fleet/machines/bm-b.json"):
    p = json.load(open(path, encoding="utf-8"))
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(json.dumps(p, ensure_ascii=False, indent=1).replace("\n", "\r\n"))
    b = open(path, "rb").read()
    assert b.count(b"\r\n") == b.count(b"\n"), path  # pure CRLF
    json.loads(b.decode("utf-8"))
    st = subprocess.run(["git", "diff", "--numstat", path],
                        capture_output=True, text=True)
    print(path, "->", st.stdout.strip())

p = "logs/iteration-loop/round_reports.md"
b = open(p, "rb").read()
idx = b.rfind(b"\r\n")
my = b[idx + 2:]
assert my.endswith(b"\n") and b"\n" not in my[:-1], "tail not my single LF line"
new_b = b[:idx + 2] + my[:-1] + b"\r\n"
with open(p, "wb") as fh:
    fh.write(new_b)
rb = open(p, "rb").read()
assert rb.endswith(b"\r\n")
st = subprocess.run(["git", "diff", "--numstat", p], capture_output=True, text=True)
print(p, "->", st.stdout.strip())

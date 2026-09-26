# -*- coding: utf-8 -*-
"""R274 bm-a: T-84 progress write-back fix -- match original byte face exactly
(default separators 'key': 'value', CRLF per probe crlf=15, trailing newline, no BOM)."""
import json

P = "fleet/tasks/T-2026-09-26-84-P1.json"
raw = open(P, "rb").read()
t = json.loads(raw.decode("utf-8-sig"))
assert "progress_r274" in t
out = json.dumps(t, ensure_ascii=False, indent=1)  # default separators = (',', ': ') -> "key": "value"
out = out.replace("\r\n", "\n").replace("\n", "\r\n")  # CRLF mirror per probe
if not out.endswith("\r\n"):
    out += "\r\n"
open(P, "wb").write(out.encode("utf-8"))
raw2 = open(P, "rb").read()
print("bytes:", len(raw2), "crlf:", raw2.count(b"\r\n"), "lf_only:", raw2.count(b"\n") - raw2.count(b"\r\n"),
      "trailing:", raw2.endswith(b"\r\n"), "bom:", raw2.startswith(b"\xef\xbb\xbf"))

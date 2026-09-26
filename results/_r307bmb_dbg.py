# -*- coding: utf-8 -*-
"""r307 debug: which paths still differ in REPORT json AFTER strip_meta
(reusing resolver head definitions verbatim, no hand-copy)."""
import io
import json
import subprocess

src = io.open("results/_r307bmb_resolve.py", encoding="utf-8").read()
head = src.split("report = []")[0]
ns = {}
exec(compile(head, "resolve_head", "exec"), ns)
strip_meta = ns["strip_meta"]

P = "docs/daily_report/REPORT-2026-09-27.json"


def blob(stage):
    return subprocess.run(["git", "show", ":%d:%s" % (stage, P)],
                           capture_output=True).stdout

o = json.loads(blob(2).decode("utf-8-sig"))
t = json.loads(blob(3).decode("utf-8-sig"))
so, st = strip_meta(o), strip_meta(t)
print("stripped equal:", so == st)


def walk(a, b, path, out, depth=0):
    if depth > 10:
        return
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a:
                out.append((".".join(map(str, path + [k])), "ONLY-A", None))
            elif k not in b:
                out.append((".".join(map(str, path + [k])), "ONLY-B", None))
            else:
                walk(a[k], b[k], path + [k], out, depth + 1)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append((".".join(map(str, path)), "LEN %d vs %d" % (len(a), len(b)), None))
        else:
            for i, (x, y) in enumerate(zip(a, b)):
                walk(x, y, path + [i], out, depth + 1)
    else:
        if a != b:
            out.append((".".join(map(str, path)), repr(a)[:80], repr(b)[:80]))


out = []
walk(so, st, [], out)
print("post-strip differing paths:", len(out))
for p, va, vb in out[:40]:
    print("   %s | A=%s | B=%s" % (p, va, vb))

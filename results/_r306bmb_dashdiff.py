# -*- coding: utf-8 -*-
"""r306 bm-b: dump full ours-vs-theirs diff path list for dashboard_status.json."""
import subprocess, json

def blob(stage, path):
    r = subprocess.run(["git", "show", ":%d:%s" % (stage, path)], capture_output=True)
    return r.stdout

p = "results/dashboard_status.json"
o = json.loads(blob(2, p).decode("utf-8-sig"))
t = json.loads(blob(3, p).decode("utf-8-sig"))

def walk(a, b, path, out):
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a:
                out.append((".".join(path + [k]), "ONLY-B", None))
            elif k not in b:
                out.append((".".join(path + [k]), "ONLY-A", None))
            else:
                walk(a[k], b[k], path + [k], out)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append((".".join(path), "LEN %d vs %d" % (len(a), len(b)), None))
        else:
            for i, (x, y) in enumerate(zip(a, b)):
                walk(x, y, path + [str(i)], out)
    else:
        if a != b:
            out.append((".".join(map(str, path)), repr(a)[:50], repr(b)[:50]))

out = []
walk(o, t, [], out)
print("total %d paths" % len(out))
for pth, va, vb in out:
    print("%s | A=%s | B=%s" % (pth, va, vb))
# semantic faces to check explicitly
for face in ("pool_ready", "ready_ids", "autofill"):
    for side, d in (("A", o), ("B", t)):
        v = d.get("data", {}).get(face)
        if v is not None:
            print("FACE %s %s = %s" % (face, side, json.dumps(v, ensure_ascii=False)[:300]))

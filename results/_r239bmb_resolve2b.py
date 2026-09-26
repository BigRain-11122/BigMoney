# -*- coding: utf-8 -*-
"""r239 resolver FIX: dashboard pair re-adjudication. r226 law: js-wrapper
side judged by .json twin meta.generated_at (nested compute_audit ts as
fallback). Previous probe missed 'generated_at' key name."""
import json
import subprocess

ROOT = r"C:\Users\Administrator\Desktop\Bigmoney"


def stage(n, path):
    out = subprocess.run(["git", "-C", ROOT, "show", ":%d:%s" % (n, path)], capture_output=True)
    assert out.returncode == 0
    return out.stdout.decode("utf-8")


def gen_at(d):
    meta = d.get("meta") or {}
    v = meta.get("generated_at") or d.get("generated_at") or d.get("generated")
    if not v:
        ca = (d.get("compute_audit") or {})
        v = ((ca.get("latest") or {}).get("ts")) if isinstance(ca, dict) else None
    return str(v or "")


j2 = json.loads(stage(2, "results/dashboard_status.json"))
j3 = json.loads(stage(3, "results/dashboard_status.json"))
t2, t3 = gen_at(j2), gen_at(j3)
side = 3 if t3 > t2 else 2
print("twin generated_at: side2=%s side3=%s -> side%d" % (t2, t3, side))
for p in ("results/dashboard_status.js", "results/dashboard_status.json"):
    s = stage(side, p)
    if p.endswith(".js"):
        assert s.lstrip().startswith("window.DASH_DATA"), "wrapper missing on " + p
    else:
        json.loads(s)
    with open(ROOT + "\\" + p.replace("/", "\\"), "w", encoding="utf-8", newline="") as f:
        f.write(s)
    print("rewritten:", p)

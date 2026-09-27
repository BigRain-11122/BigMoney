"""r383 push-storm resolver: 3 faces outside the resolve registry
(r136 pitlaw: daily_report twins + fundamental_b_layer_filter are not in
ALL_FACES -- hand-rolled deep-scan per canon is the only path).

Side orientation: :2: = origin side (bm-c r137), :3: = replay side (mine).
Probes run on STAGED BLOBS (R350), not the working tree.
Twins: json generated_at probe decides the side; md is byte-copied from the
SAME side (r327/r329 twin coupling -- md is not JSON, never json.loads it).
"""
import subprocess
import sys


def blob(stage, path):
    out = subprocess.run(["git", "show", ":%s:%s" % (stage, path)],
                         capture_output=True, check=True)
    return out.stdout


def probe_updated(b):
    import json
    d = json.loads(b.decode("utf-8-sig"))
    return str(d.get("updated") or d.get("ts") or "")


def probe_generated(b):
    import json
    d = json.loads(b.decode("utf-8-sig"))
    return str(d.get("generated_at") or "")


faces = [
    ("docs/daily_report/REPORT-2026-09-28.json", probe_generated, "json"),
    ("docs/daily_report/REPORT-2026-09-28.md", None, "byte-copy-same-side"),
    ("results/fundamental_b_layer_filter.json", probe_updated, "json"),
]

json_side = None
results = []
for path, probe, kind in faces:
    b2 = blob(2, path)
    b3 = blob(3, path)
    if kind == "byte-copy-same-side":
        assert json_side in (2, 3), "md twin before json twin decided"
        src = b2 if json_side == 2 else b3
        open(path, "wb").write(src)
        results.append((path, "take :%s: (twin-coupled byte-copy)" % json_side))
        continue
    t2, t3 = probe(b2), probe(b3)
    if t2 == t3:
        side = 2  # same-second tie -> origin per r140
        note = "tie %s -> :2: origin (r140)" % t2
    else:
        side = 3 if t3 > t2 else 2
        note = "mine %s vs origin %s -> :%s:" % (t3, t2, side)
    src = b3 if side == 3 else b2
    open(path, "wb").write(src)
    if path.endswith(".json"):
        import json as _j
        _j.loads(open(path, "rb").read().decode("utf-8-sig"))
    if kind == "json" and "REPORT" in path:
        json_side = side
    results.append((path, note))

for r in results:
    print("  " + r[0] + " :: " + r[1])
print("resolver done")

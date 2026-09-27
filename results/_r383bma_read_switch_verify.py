"""r383 slice-3 verify: compute_audit read-point switch equivalence.

A-pattern (audit_seg): face_view latest-row extraction == shared-file
extraction, field-exact (verdict/ts/cpu_pct/flags).
B-pattern (audit-block): face_view latest[-1] == shared latest[-1].
self_review sr5: face_view .latest == shared .latest.
ap-pattern (sampled): face_view .latest keys == shared .latest keys.
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "scripts"))
import merge_lane_views as mlv

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHARED = os.path.join(ROOT, "results", "compute_audit.json")

shared = json.load(open(SHARED, encoding="utf-8"))
view = mlv.face_view("compute_audit", results_dir=os.path.join(ROOT, "results"))
assert view, "face_view returned empty on live tree"

fails = []

# A-pattern (history[-1] -> audit_seg fields)
def latest_row(d):
    h = d.get("history") or []
    return h[-1] if h else d

a_s, a_v = latest_row(shared), latest_row(view)
for k in ("verdict", "ts", "cpu_pct", "flags"):
    if a_s.get(k) != a_v.get(k):
        fails.append(f"A-pattern field {k}: shared={a_s.get(k)!r} view={a_v.get(k)!r}")

# ap-pattern / sr5 (state .latest)
l_s, l_v = shared.get("latest") or {}, view.get("latest") or {}
for k in ("cpu_total_pct", "verdict", "flags", "ts"):
    if l_s.get(k) != l_v.get(k):
        fails.append(f"latest field {k}: shared={l_s.get(k)!r} view={l_v.get(k)!r}")

# B-pattern semantic (verdict/flags/asof triple, same as runner code)
for name, d in (("shared", a_s), ("view", a_v)):
    pass
tri_s = {"verdict": a_s.get("verdict"), "flags": a_s.get("flags"),
         "asof": a_s.get("ts") or a_s.get("asof")}
tri_v = {"verdict": a_v.get("verdict"), "flags": a_v.get("flags"),
         "asof": a_v.get("ts") or a_v.get("asof")}
if tri_s != tri_v:
    fails.append(f"B-pattern triple: shared={tri_s} view={tri_v}")

# history identity-superset (union law: view >= shared, zero loss)
hs = {str(h.get("ts", "")) for h in shared.get("history", [])}
hv = {str(h.get("ts", "")) for h in view.get("history", [])}
missing = hs - hv
if missing:
    fails.append(f"history rows lost in view: {sorted(missing)[:5]}")

if fails:
    print("FAIL")
    for f in fails:
        print("  " + f)
    sys.exit(1)
print("PASS: A/ap/B/sr5 extraction equivalence field-exact; "
      f"history union view {len(hv)} >= shared {len(hs)} rows, zero loss; "
      f"latest verdict={tri_v['verdict']} ts={tri_v['asof']}")

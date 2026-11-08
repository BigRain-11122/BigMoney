"""E557 smoke leg, runnable on its own (the suite has no leg filter -- r1499 family).

Same shape as scripts/run_e556_smoke_leg.py: the leg lives inside smoke_test.py, so this
file re-runs its comparisons without launching the whole suite.
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts"))
import e557_face_entry_reach as m  # noqa: E402

FACE = os.path.join("results", "state_tilt", "faceentryreach_latest.json")
bad = []
f = json.load(open(FACE, encoding="utf-8"))
s = f.get("summary") or {}
rows = f.get("rows") or []
writers = f.get("writers") or []
bad.extend(m.face_problems(f))
if not rows:
    bad.append("the reachability population is empty")
if s.get("rows") != len(rows):
    bad.append("the summary row count is not the face's")
if sum((s.get("by_reach_class_rows") or {}).values()) != len(rows):
    bad.append("the reach table does not partition the rows")
if sum((s.get("by_reach_class_writers") or {}).values()) != len(writers):
    bad.append("the writer reach table does not partition the writers")
if not (s.get("control_arm") or {}).get("found"):
    bad.append("the entry-point census cannot see its own controls (blind)")
if any(r.get("reach_class") != m.classify_reach(r["naming_sites"]) for r in rows):
    bad.append("a row's reach class is not what its own sites say")
if any(r.get("reach_class") in m.REBUILD_CLASSES and not [
        x for x in r["naming_sites"] if x["kind"] == m.N_CHAIN_BUILD] for r in rows):
    bad.append("a row is called rebuildable without a build leg")
if f.get("verdict") == m.V_SOME_REBUILD and not s.get("writers_with_a_build_entry_point"):
    bad.append("a rebuild verdict sits beside zero rebuildable writers")
if f.get("verdict") == m.V_NONE_REBUILD and s.get("writers_with_a_build_entry_point"):
    bad.append("a no-rebuild verdict sits beside rebuildable writers")
if rows:
    doc = json.loads(json.dumps(f))
    doc["verdict"] = "a_verdict_this_study_never_publishes"
    if not m.face_problems(doc):
        bad.append("a hand-written verdict was accepted")
    doc = json.loads(json.dumps(f))
    doc["rows"][0]["naming_sites"].append(
        {"source": "Tools/_r1003bmb_s6.py", "kind": m.N_CHAIN_BUILD, "leg": "x",
         "argv": ["python", "scripts/x.py"], "verb": "build", "machine": "bm-b"})
    if not any("counted as a live chain build leg" in p for p in m.face_problems(doc)):
        bad.append("a one-off snapshot counted as a chain build leg was accepted")
    doc = json.loads(json.dumps(f))
    for row in doc["rows"]:
        if row["reach_class"] == m.R_GATED_ONLY:
            row["reach_class"] = m.R_OTHER_CHAIN_BUILD
            break
    if not any("reach class is not what its own sites say" in p for p in m.face_problems(doc)):
        bad.append("a gated-only row relabelled rebuildable was accepted")
    doc = json.loads(json.dumps(f))
    doc["summary"]["chain_inventory"][1]["legs_run_as_data"] = 0
    if not any("chain_inventory" in p for p in m.face_problems(doc)):
        bad.append("a leg count that does not re-derive was accepted")

print(json.dumps({"leg": "E557", "problems": bad,
                  "detail": "%d rows / %d writers / %d rebuildable / %d gated-only / control %s"
                            % (len(rows), len(writers),
                               s.get("writers_with_a_build_entry_point", 0),
                               s.get("writers_only_gated", 0),
                               (s.get("control_arm") or {}).get("found"))},
                 ensure_ascii=False))
sys.exit(1 if bad else 0)
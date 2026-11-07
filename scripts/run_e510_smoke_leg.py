"""Leg-level recheck of the E510 smoke block without running the whole suite (r1499 trap)."""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts"))
import e510_binding_scope as m

face = json.load(open(os.path.join("results", "state_tilt", "scopedbinding_latest.json"),
                      encoding="utf-8"))
bad = list(m.row_problems(face))
pairs = face.get("pairs") or []
rows = face.get("rows") or []
s = face.get("summary") or {}
if not pairs or not rows:
    bad.append("empty population")
if any(p.get("wide", {}).get("tracks") != m.T_MIXED for p in pairs):
    bad.append("a non-mixed pair was selected")
w = json.loads(json.dumps(face))
w["pairs"][0]["collapse"] = m.K_MIXED
if not m.row_problems(w):
    bad.append("flipped collapse survived")
w2 = json.loads(json.dumps(face))
w2["verdict"] = m.V_SCOPE
if not m.row_problems(w2):
    bad.append("hand-written verdict survived")
w3 = json.loads(json.dumps(face))
w3["pairs"][0]["scoped"]["tracks"] = "guessed"
if not m.row_problems(w3):
    bad.append("bad track survived")
print("leg510 bad=%r" % (bad,))
print("pairs=%d site_of=%s collapsed=%s ambiguous=%s fallback=%s verdict=%s"
      % (len(pairs), s.get("pair_sites"), s.get("collapsed_pairs"),
         s.get("stays_ambiguous_pairs"), s.get("pairs_needing_a_module_wide_fallback"),
         face.get("verdict")))
print("rc", 0 if not bad else 1)
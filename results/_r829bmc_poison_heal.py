"""r829 poison heal: settle shared faces to merged lane-union view.

Predecessor r829 session pushed conflict-marker-poisoned S6 output faces to
origin (15b4418b9). Fresh regeneration (heal step 1) rewrote shared files
from scratch -> shared lost the accumulated history union that lanes still
hold (bm-a/bm-b lane histories ~200 rows). This script writes the
merge_lane_views merged view back to shared (the exact equality reconcile
demands), restoring the union without losing the fresh latest snapshot.

Faces: compute_audit, regime_state (the two reconcile-DRIFT faces).
All other poisoned faces regenerated to zero-drift already.
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from merge_lane_views import load_sources, merge_face  # noqa: E402

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

def heal(face):
    shared_path = os.path.join(ROOT, "results", f"{face}.json")
    sources = load_sources(face)
    merged, notes = merge_face(face, sources)
    payload = json.dumps(merged, ensure_ascii=False, indent=1)
    with open(shared_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(payload + "\n")
    back = json.load(open(shared_path, encoding="utf-8"))
    assert back == merged, f"{face}: parse-verify failed"
    print(f"[{face}] healed shared -> merged view "
          f"({len(payload)}B, {len(notes)} note(s))")
    for n in notes:
        print(f"  - {n}")

if __name__ == "__main__":
    for face in ("compute_audit", "regime_state"):
        heal(face)
    print("heal: done")

"""r694 bm-b: freeze the stage-A' pinned mask copy (MSG-2026-10-04-2110
adjudication case B, owner=bm-b). Byte copy of the live
data/fundamental/b_layer_mask.csv -> data/fundamental/b_layer_mask
.stageA_prime_pin.csv + sha256 receipt (results/_r694bmb_stageA_prime_pin
.json). The live face keeps regenerating every S6 round (eligibility ->
b_layer_filter); the pinned copy freezes the contest-RC universe basis
against further drift. Read-only vs the live face; zero panel load;
deterministic; refuse to silently re-pin an existing divergent copy."""
import hashlib
import io
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "data", "fundamental", "b_layer_mask.csv")
DST = os.path.join(ROOT, "data", "fundamental",
                   "b_layer_mask.stageA_prime_pin.csv")
RCPT = os.path.join(ROOT, "results", "_r694bmb_stageA_prime_pin.json")

src_bytes = io.open(SRC, "rb").read()
assert src_bytes, "live mask empty"
src_sha = hashlib.sha256(src_bytes).hexdigest()
if os.path.exists(DST):
    old = io.open(DST, "rb").read()
    assert old == src_bytes, (
        "pinned copy exists with DIFFERENT bytes -- refusing silent re-pin "
        "(basis change requires a fresh adjudication receipt; delete the "
        "copy + re-pin via a new probe if intentional)")
else:
    with io.open(DST, "wb") as f:
        f.write(src_bytes)
dst_sha = hashlib.sha256(io.open(DST, "rb").read()).hexdigest()
assert dst_sha == src_sha, "copy sha mismatch"

doc = {
    "src": "data/fundamental/b_layer_mask.csv",
    "dst": "data/fundamental/b_layer_mask.stageA_prime_pin.csv",
    "sha256": src_sha,
    "bytes": len(src_bytes),
    "basis": "stage-A' pinned universe (MSG-2026-10-04-2110 adjudication "
             "case B, owner bm-b r694; freeze-date 2026-10-04 evening)",
    "live_face_note": "live b_layer_mask.csv keeps regenerating per S6 "
                      "round; the pinned copy is inert unless consumed by "
                      "scripts/contest_ytd_legs.py (revcensus RV.MASK pin)",
}
io.open(RCPT, "w", encoding="utf-8").write(json.dumps(doc, indent=1) + "\n")
print("PIN OK sha256=%s bytes=%d -> %s"
      % (src_sha[:16], len(src_bytes), os.path.relpath(DST, ROOT)))

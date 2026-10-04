"""r665: append progress_r665 row to T-165 ticket (continuation slice face, status unchanged)."""
import io, json

P = "fleet/tasks/T-2026-10-04-165-P1.json"
with io.open(P, "r", encoding="utf-8") as f:
    t = json.load(f)

t["progress_r665"] = (
    "r665 (bm-a): R6 continuation slice DELIVERED -- theme ignition START-face grid probe "
    "(E28 lagged-confirmer finding -> cheap next cut): scripts/theme_ignition_face_probe.py "
    "(L1 deterministic, selftest 13/13, budget-in-cap) + results/theme_ring/theme_ignition_face_probe."
    "json+csv (16 CEO anchors x 4 frozen faces: nearlimit7/volstart/break60/fast10; window "
    "anchor-60..+40 bars; primary pm10td + comparability pm30cal; B0 v0.3 burst rule cited "
    "not recomputed). Findings (descriptive, zero registration claims): fast10 (10td>=+10%) = "
    "best start face 7/16 within pm10td (median delta +2td) vs B0 2/16 pm30cal; volstart/"
    "break60 fire early but scattered (median -21/-24td, |delta| median 22/53); nearlimit7 "
    "rare 4/16 (A-share ETF theme starts rarely open near-limit); anchor-duality finding: 4/5 "
    "out-of-window fires are EARLY fires (CYB2013 -30/SOE2015 -38/TECH5G2019 -56/DEEPSEEK2025 "
    "-55) -- mechanical starts can precede CEO consensus anchors by weeks -> future start-"
    "criterion preregs must adjudicate anchor-truth semantics or use asymmetric tolerance, "
    "symmetric +-N forbidden; 4 no-fire events (BELTROAD2014/ZHONGTEIGU2023/AI2023/PV2021 "
    "head-truncated) disclosed. Canon: THEME_EVENT_LIBRARY.md sec.9 + METHODOLOGY_ASSETS.md "
    "E29 (start-face grid method + anchor-duality law) + TREASURE_REGISTRY row. Consumers: "
    "fast10 = candidate ignition face for any future theme judgment prereg (new frozen prereg "
    "required; E28 cluster-stratification law applies on the v0.3 algorithmic set)."
)

with io.open(P, "w", encoding="utf-8", newline="\n") as f:
    json.dump(t, f, ensure_ascii=False, indent=1)
# self-proof: strict reparse
with io.open(P, "r", encoding="utf-8") as f:
    t2 = json.load(f)
assert "progress_r665" in t2 and t2["status"] in ("done", "claimed")
print("ticket progress_r665 appended; status unchanged:", t2["status"])

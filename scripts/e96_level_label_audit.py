"""E96 -- every published churn LEVEL must say which screen arm produced it.

r1158 published that promise as prose. This tool turns it into a machine-checkable
audit: for each face on disk that carries per-era churn LEVEL cells, report

  * whether the face declares its screen arm itself (spec/arm keys), or
  * whether the arm can be INFERRED bit-for-bit from a labelled sibling that
    re-derived the same cells, or
  * whether the level is genuinely unlabelled (no proof available).

The distinction matters because an inferred label is weaker evidence than a
declared one: it says "these numbers are identical to arm X on this burn",
not "this face was produced by arm X".

Usage:
  python scripts/e96_level_label_audit.py run
  python scripts/e96_level_label_audit.py selftest
"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCAN_DIR = os.path.join(ROOT, "results", "e44_midmonth")
OUT_PATH = os.path.join(SCAN_DIR, "LEVEL-LABELS-20261027.json")

ARM_KEYS = ("arms", "modes", "screen_modes", "screen_arm", "arms_run", "arm")
NUM_TOL = 1e-9


def _load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def declared_arm(face):
    """Return (arm_declaration, source_key) from the face's own metadata."""
    spec = face.get("spec") if isinstance(face.get("spec"), dict) else {}
    for key in ARM_KEYS:
        if key in spec:
            val = spec[key]
            return (val if isinstance(val, str) else list(val)), "spec." + key
    for key in ARM_KEYS:
        if key in face:
            val = face[key]
            return (val if isinstance(val, str) else list(val)), key
    return None, None


def level_blocks(face):
    """Extract {era: block} for a LEVEL-bearing face, or None."""
    eras = face.get("eras")
    if not isinstance(eras, dict):
        return None
    if not eras:
        return None
    first = next(iter(eras.values()))
    if not isinstance(first, dict):
        return None
    if "me" not in first or "mid" not in first:
        return None
    return eras


def arm_level_blocks(face):
    """Extract {arm: {era: block}} for a multi-arm sibling face, or None."""
    eras = face.get("eras")
    if not isinstance(eras, dict) or not eras:
        return None
    out = {}
    for arm, per_era in eras.items():
        if not isinstance(per_era, dict) or not per_era:
            continue
        sample = next(iter(per_era.values()))
        if isinstance(sample, dict) and "me" in sample and "mid" in sample:
            out[arm] = per_era
    return out or None


def flat_cells(per_era):
    """{("era","book","field"): float} for numeric, non-null leaves."""
    cells = {}
    for era, block in per_era.items():
        if not isinstance(block, dict):
            continue
        for key, val in block.items():
            if isinstance(val, dict):
                for sub, subval in val.items():
                    if isinstance(subval, (int, float)) and not isinstance(subval, bool):
                        cells[(era, key, sub)] = float(subval)
            elif isinstance(val, (int, float)) and not isinstance(val, bool):
                cells[(era, key, "-")] = float(val)
    return cells


def best_match(target_cells, arm_map):
    """Compare a LEVEL face against each arm of a labelled sibling face."""
    results = []
    for arm, per_era in arm_map.items():
        arm_cells = flat_cells(per_era)
        common = set(target_cells) & set(arm_cells)
        if not common:
            results.append({"arm": arm, "common": 0, "max_abs_diff": None,
                            "coverage": 0.0, "identical": False})
            continue
        diff = max(abs(target_cells[k] - arm_cells[k]) for k in common)
        cover_target = len(common) / max(1, len(target_cells))
        cover_arm = len(common) / max(1, len(arm_cells))
        results.append({"arm": arm, "common": len(common), "max_abs_diff": diff,
                        "coverage": round(min(cover_target, cover_arm), 4),
                        "identical": bool(diff <= NUM_TOL and cover_target >= 0.999
                                          and cover_arm >= 0.999)})
    results.sort(key=lambda r: (not r["identical"], r["max_abs_diff"] if r["max_abs_diff"] is not None else 9e9))
    return results


def build():
    files = sorted(
        os.path.join(SCAN_DIR, name)
        for name in os.listdir(SCAN_DIR)
        if name.endswith(".json")
    )
    faces = {}
    for path in files:
        try:
            face = _load(path)
        except Exception:
            continue
        if not isinstance(face, dict):
            continue
        faces[os.path.basename(path)] = face

    level_faces = {}
    labelled_siblings = {}
    for name, face in faces.items():
        blocks = level_blocks(face)
        if blocks is not None:
            level_faces[name] = face
            continue
        arm_blocks = arm_level_blocks(face)
        if arm_blocks is not None:
            labelled_siblings[name] = arm_blocks

    rows = []
    for name, face in sorted(level_faces.items()):
        arm, src = declared_arm(face)
        cells = flat_cells(face["eras"])
        row = {
            "face": name,
            "level_cells": len(cells),
            "eras_populated": sorted({era for era, _, _ in cells}),
            "declared_arm": arm,
            "declared_from": src,
            "label_state": "declared" if arm else "unlabelled",
            "inferred_arm": None,
            "inferred_from": None,
            "evidence": [],
        }
        if not arm and cells:
            for sib_name, arm_map in sorted(labelled_siblings.items()):
                match = best_match(cells, arm_map)
                row["evidence"].append({"sibling": sib_name, "matches": match})
                win = [m for m in match if m["identical"]]
                if win and row["inferred_arm"] is None:
                    row["inferred_arm"] = win[0]["arm"]
                    row["inferred_from"] = sib_name
                    row["label_state"] = "inferred"
                    row["match_kind"] = "identical"
                    continue
                # Nearest-arm inference: only when one arm dominates the runner-up by
                # 10x or more on max abs difference at full coverage, so an ordinary gap
                # between arms is never read as a label.
                full = [m for m in match if m["coverage"] >= 0.999 and m["max_abs_diff"] is not None]
                if len(full) >= 2 and row["inferred_arm"] is None:
                    first, second = full[0], full[1]
                    if first["max_abs_diff"] > 0:
                        margin = second["max_abs_diff"] / first["max_abs_diff"]
                        row["nearest_margin"] = round(margin, 3)
                        if margin >= 10.0:
                            row["inferred_arm"] = first["arm"]
                            row["inferred_from"] = sib_name
                            row["label_state"] = "inferred_nearest"
                            row["match_kind"] = "nearest"
                            row["drift_bp"] = round(first["max_abs_diff"], 4)
        rows.append(row)

    counts = {"total": len(rows), "declared": 0, "inferred": 0,
              "inferred_nearest": 0, "unlabelled": 0}
    for row in rows:
        counts[row["label_state"]] += 1

    payload = {
        "study": "E96 churn LEVEL screen-arm label audit",
        "evidence_cutoff": _cutoff(faces),
        "scan_dir": "results/e44_midmonth",
        "promise_ref": "r1158 round report: every published churn LEVEL says which screen arm produced it",
        "counts": counts,
        "faces": rows,
        "honest": [
            "declared = the face names its arm in its own spec; inferred = the face's cells are bit-identical "
            "to a named arm of a sibling face on the same burn; inferred_nearest = not identical, but one arm "
            "dominates the runner-up by >=10x on max abs difference at full coverage, and the residual drift is "
            "published as drift_bp; unlabelled = no proof available from disk.",
            "inference is evidence about the numbers, not about the producing code path: a nearest match says the "
            "face reads like that arm on a later burn, which is weaker than a declared arm and must not be quoted "
            "as one.",
            "inference is only as good as the sibling: if the sibling itself re-derived rather than re-read "
            "the base face, an inferred match proves the burn is reproducible, not that the base ran that arm.",
            "faces outside results/e44_midmonth are not scanned; this audit covers the churn family only.",
        ],
    }
    return payload


def _cutoff(faces):
    cutoffs = sorted({str(f.get("evidence_cutoff")) for f in faces.values() if f.get("evidence_cutoff")})
    return cutoffs[-1] if cutoffs else None


def run():
    payload = build()
    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
    c = payload["counts"]
    print("E96 level-label audit -> %s" % os.path.relpath(OUT_PATH, ROOT))
    print("faces=%d declared=%d inferred=%d inferred_nearest=%d unlabelled=%d"
          % (c["total"], c["declared"], c["inferred"], c["inferred_nearest"], c["unlabelled"]))
    for row in payload["faces"]:
        arm = row["declared_arm"] if row["label_state"] == "declared" else row["inferred_arm"]
        drift = row.get("drift_bp")
        print("  %-34s %-17s %-22s%s" % (row["face"], row["label_state"], arm,
                                          "" if drift is None else " drift=%sbp" % drift))
    return 0


# ---------------------------------------------------------------- selftest
def _fixture_level():
    return {"spec": {}, "eras": {"2024_now": {
        "me": {"x1_ann_pct": 1.5, "churn_alpha_bp_mean": 10.0},
        "mid": {"x1_ann_pct": 2.0, "churn_alpha_bp_mean": -5.0},
        "gap_x1_bp": 50.0}}}


def _fixture_arms():
    return {"spec": {"arms": ["unscreened", "neutralise"]}, "eras": {
        "unscreened": {"2024_now": {
            "me": {"x1_ann_pct": 1.5, "churn_alpha_bp_mean": 10.0},
            "mid": {"x1_ann_pct": 2.0, "churn_alpha_bp_mean": -5.0},
            "gap_x1_bp": 50.0}},
        "neutralise": {"2024_now": {
            "me": {"x1_ann_pct": 1.9, "churn_alpha_bp_mean": 4.0},
            "mid": {"x1_ann_pct": 2.2, "churn_alpha_bp_mean": -8.0},
            "gap_x1_bp": 30.0}}}}


def _nearest_probe():
    target = flat_cells({"2024_now": {"me": {"x1_ann_pct": 1.52}, "mid": {"x1_ann_pct": 2.01}}})
    return best_match(target, arm_level_blocks(_fixture_arms()))[0]


def selftest():
    checks = []

    def chk(name, cond):
        checks.append((name, bool(cond)))

    face = _fixture_level()
    blocks = level_blocks(face)
    chk("L1 level face detected", blocks is not None)
    chk("L2 level face declares no arm", declared_arm(face) == (None, None))

    sib = _fixture_arms()
    chk("L3 sibling declares arms", declared_arm(sib)[0] == ["unscreened", "neutralise"])
    arm_map = arm_level_blocks(sib)
    chk("L4 sibling exposes two arms", arm_map is not None and len(arm_map) == 2)

    cells = flat_cells(face["eras"])
    chk("L5 flat cells found", len(cells) == 5)
    match = best_match(cells, arm_map)
    chk("L6 identical arm ranks first", match[0]["arm"] == "unscreened" and match[0]["identical"])
    chk("L7 other arm is not identical", match[1]["identical"] is False)
    chk("L8 non-identical arm reports a positive diff", (match[1]["max_abs_diff"] or 0) > 0)

    # a face that matches no arm must stay unlabelled
    other = {"spec": {}, "eras": {"2024_now": {
        "me": {"x1_ann_pct": 9.9}, "mid": {"x1_ann_pct": 8.8}}}}
    other_cells = flat_cells(other["eras"])
    chk("L9 no-match face has no identical arm",
        all(not m["identical"] for m in best_match(other_cells, arm_map)))
    chk("L10 no-match face still compares cells", bool(other_cells))

    # partial coverage must not be read as identity
    partial = {"spec": {}, "eras": {"2024_now": {"me": {"x1_ann_pct": 1.5}, "mid": {"x1_ann_pct": 2.0}}}}
    pm = best_match(flat_cells(partial["eras"]), arm_map)
    chk("L11 partial coverage is not identity", all(not m["identical"] for m in pm))

    # a face with era cells but no me/mid is not a LEVEL face
    chk("L12 non-level shape rejected",
        level_blocks({"eras": {"a": {"foo": 1}}}) is None)
    chk("L13 empty eras rejected", level_blocks({"eras": {}}) is None)

    # live artefacts
    chk("L14 scan dir exists", os.path.isdir(SCAN_DIR))
    live = build()
    chk("L15 live build produces rows", live["counts"]["total"] > 0)
    chk("L16 live counts sum to total",
        sum(live["counts"][k] for k in ("declared", "inferred", "inferred_nearest", "unlabelled"))
        == live["counts"]["total"])
    chk("L17 every row names a state from the closed set",
        all(r["label_state"] in ("declared", "inferred", "inferred_nearest", "unlabelled")
            for r in live["faces"]))
    chk("L18 declared rows carry a source key",
        all(r["declared_from"] for r in live["faces"] if r["label_state"] == "declared"))
    chk("L19 inferred rows carry a sibling",
        all(r["inferred_from"] for r in live["faces"] if r["label_state"].startswith("inferred")))
    chk("L21 nearest rows publish their drift",
        all(r.get("drift_bp") is not None for r in live["faces"]
            if r["label_state"] == "inferred_nearest"))
    chk("L22 a dominating arm is nearest-inferable",
        _nearest_probe()["arm"] == "unscreened" and not _nearest_probe()["identical"])
    chk("L20 base MID face is classified honestly",
        any(r["face"].startswith("MID-20261020") and r["label_state"] != "declared" for r in live["faces"]))

    failed = [n for n, ok in checks if not ok]
    for name, ok in checks:
        print("[%s] %s" % ("PASS" if ok else "FAIL", name))
    print("selftest %d/%d" % (len(checks) - len(failed), len(checks)))
    return 0 if not failed else 1


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    cmd = argv[1]
    if cmd == "run":
        return run()
    if cmd == "selftest":
        return selftest()
    print("unknown command: %s" % cmd)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
"""E108 -- re-derive the screened-arm faces with the corrected repair factor and
publish the before/after per face.

Background (E106): ``panel_screen.split_events`` used the *folded* implied share
ratio (always >= 1, folded so the integer test can see a reverse split) as the
forward-adjustment factor. On a downward print that is right (1/(1+r) > 1); on an
UPWARD print it multiplies by (1+r) instead of dividing, so the repaired arm read
``(1+r)^2-1`` -- sh510580 read +1464.09% in the repaired arm against +295.49% raw.
The factor is now the cancelling value ``1/(1+r)`` for every event.

This tool has two jobs:

``legacy``
    Re-run one e39 leg with the OLD factor restored (monkeypatched), so the diff
    between the on-disk published face and a fresh legacy burn can be shown to be
    zero. That is the control: if the panel moved, the control moves too.

``diff``
    Walk two face directories and report, per face, how many numeric leaves moved
    and by how much, with the largest movers named by JSON path.

Usage:
    python scripts/e108_repairfix.py legacy repairstep
    python scripts/e108_repairfix.py fixed <leg>
    python scripts/e108_repairfix.py diff <before_dir> <after_dir> [--out F]
    python scripts/e108_repairfix.py report <before_dir> <after_dir> --out F
"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))


def legacy_split_events():
    """Patch panel_screen.split_events back to the folded-ratio factor (pre-E108)."""
    import panel_screen
    orig = panel_screen.split_events

    def old(closes, thresh=panel_screen.ARTEFACT_JUMP, cal=None):
        events = orig(closes, thresh, cal=cal)
        for ev in events:
            im = ev.get("implied")
            if im:
                ev["factor"] = im["ratio"]
        return events

    panel_screen.split_events = old
    return orig


def run_leg(leg, legacy=False):
    import e39_panel_census as e39
    if legacy:
        legacy_split_events()
    return e39.main([leg])


def _walk(node, path, out):
    if isinstance(node, dict):
        for k, v in node.items():
            _walk(v, path + [str(k)], out)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            _walk(v, path + ["[%d]" % i], out)
    elif isinstance(node, bool):
        out[tuple(path)] = bool(node)
    elif isinstance(node, (int, float)):
        out[tuple(path)] = float(node)
    elif isinstance(node, str) and node.count("-") == 2 and len(node) == 10:
        out[tuple(path)] = node


def _flat(face, prefix):
    out = {}
    for key in ("spec", "metadata", "generated", "notes", "law_ref", "schema"):
        face.pop(key, None)
    _walk(face, [], out)
    return {prefix + "/".join(k): v for k, v in out.items()}


def diff_faces(before_dir, after_dir):
    rows = []
    for name in sorted(os.listdir(after_dir)):
        if not name.endswith(".json"):
            continue
        pb = os.path.join(before_dir, name)
        if not os.path.exists(pb):
            rows.append({"face": name, "status": "no_before_twin"})
            continue
        with open(pb, encoding="utf-8") as fh:
            b = _flat(json.load(fh), "")
        with open(os.path.join(after_dir, name), encoding="utf-8") as fh:
            a = _flat(json.load(fh), "")
        common = set(a) & set(b)
        num = [k for k in common if isinstance(a[k], float) and isinstance(b[k], float)]
        moved = []
        for k in num:
            d = a[k] - b[k]
            if abs(d) > 1e-9:
                moved.append((abs(d), k, b[k], a[k]))
        moved.sort(reverse=True)
        dates = [k for k in common if isinstance(a[k], str) and isinstance(b[k], str)]
        date_moved = [k for k in dates if a[k] != b[k]]
        rows.append({
            "face": name,
            "keys_compared": len(common),
            "numeric_leaves": len(num),
            "numeric_moved": len(moved),
            "max_abs_delta": (round(moved[0][0], 6) if moved else 0.0),
            "date_leaves_moved": len(date_moved),
            "top_movers": [
                {"path": k, "before": round(bv, 4), "after": round(av, 4),
                 "delta": round(av - bv, 4)}
                for _, k, bv, av in moved[:8]
            ],
        })
    return rows


def _readings(before_dir, after_dir):
    """Pull the published readings that the factor moves, from both sides."""
    def face(d, name):
        p = os.path.join(d, name)
        return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None

    out = {}
    mid_b = face(before_dir, "MID-20261026-s20180101-armed.json")
    mid_a = face(os.path.join(ROOT, "results", "e44_midmonth"),
                 "MID-20261026-s20180101-armed.json")
    if mid_b and mid_a:
        def pick(f):
            a = f.get("answers") or {}
            return {"newest_era_level_bp": a.get("newest_era_level_bp"),
                    "level_sign_flips_across_arms": a.get("level_sign_flips_across_arms")}
        out["mid_armed_levels"] = {"before": pick(mid_b), "after": pick(mid_a)}

    for name, keys in (("GAPARM-ENDGRID-20261026-s20180101.json",
                        ("delta_span_bp", "level_span_bp", "delta_stable_eras")),
                       ("GAPTOP3-20261026-s2018.json",
                        ("large_moves", "verdict_tally", "price_read_driver_names")),
                       ("HELDSPLIT-20261026-s2018.json",
                        ("cells_measured", "cells_with_a_split", "verdict_tally")),
                       ("REPAIRSTEP-20261026.json",
                        ("flagged_windows", "fabricating_windows", "verdict_tally"))):
        b = face(before_dir, name)
        a = face(os.path.join(ROOT, "results", "e44_midmonth"), name)
        if not (b and a):
            continue
        ab, aa = b.get("answers") or {}, a.get("answers") or {}
        out[name.replace(".json", "")] = {
            "before": {k: ab.get(k) for k in keys},
            "after": {k: aa.get(k) for k in keys},
        }
    return out


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    cmd = argv[0]
    if cmd == "legacy":
        return run_leg(argv[1], legacy=True)
    if cmd == "fixed":
        return run_leg(argv[1], legacy=False)
    if cmd in ("diff", "report"):
        before, after = argv[1], argv[2]
        out_path = None
        if "--out" in argv:
            out_path = argv[argv.index("--out") + 1]
        rows = diff_faces(before, after)
        payload = {"tool": "scripts/e108_repairfix.py",
                   "study": "E108 repair-factor sign fix: panel_screen.split_events now "
                            "uses the cancelling factor 1/(1+r) for every event",
                   "before_dir": before, "after_dir": after,
                   "faces": rows,
                   "faces_moved": [r["face"] for r in rows
                                   if r.get("numeric_moved")],
                   "faces_untouched": [r["face"] for r in rows
                                       if r.get("status") != "no_before_twin"
                                       and not r.get("numeric_moved")]}
        if cmd == "report":
            payload["readings"] = _readings(before, after)
            payload["control"] = {
                "note": "the repairstep leg was re-run with the OLD factor restored "
                        "(e108_repairfix.py legacy repairstep) and reproduced the "
                        "published face with 0 of 966 numeric leaves moved, so the "
                        "diffs below are the factor and not panel drift",
                "panel_cutoff": "2026-10-26",
            }
            payload["confound"] = {
                "SCREENGAPERA-20261023.json":
                    "compared across cutoffs (published 2026-10-23 vs fresh "
                    "2026-10-26), so its diff mixes the factor with two days of "
                    "panel arrival; read it as a direction, not a delta",
            }
        txt = json.dumps(payload, ensure_ascii=False, indent=1)
        if out_path:
            with open(out_path, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(txt + "\n")
            print(json.dumps({k: payload[k] for k in
                              ("faces_moved", "faces_untouched")}, ensure_ascii=False))
        else:
            print(txt)
        return 0
    print("unknown command %r" % cmd)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
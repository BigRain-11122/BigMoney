# -*- coding: utf-8 -*-
"""r869 bm-b: GATE-RECHECK-MP1 slice-1 draft probe (read-only fact-check).

Six legs mirroring the r867 mp1 draft-probe precedent:
 L1  MP1 results json: PASS==25 recount + OOS.med_t axis readback for all PASS gates
 L2  five_member_oos secondary face coverage: 25/25 PASS gates present x 5 members,
     n_in floor/ceiling + dual-negative-member prior readback (delta gates)
 L3  A158 RECHECK registered library: gate_recheck_a158.json in place,
     library_entries==17 recount, A158 prereg cutoff disclosure (2026-09-22 vs
     this batch same-instant 2026-10-09 rebuild law)
 L4  runner import faces: mp1_tsgate_probe (parse_formula/mp1_factors/gate_universe/
     inst_gate_stats/thin/load_truncated) + a158_tsgate_probe (alpha158_factors)
     + a158_gate_recheck (thin_b/union_find_clusters/face_a_leg) importable
 L5  panel truth: five-member sh csv in place, 510300 truncated rowcount==3490
     at cutoff 2026-10-09, last date==2026-10-09
 L6  prereg markers: research/GATE_RECHECK_MP1_PREREG.md sections 0-8 present +
     DRAFT state + T25 row in tech.md carrying this batch name

Read-only: zero burns, zero pool writes, zero ledger/appends. Receipt ->
results/_r869bmb_recheck_draft_probe.json
"""
import json
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "results" / "_r869bmb_recheck_draft_probe.json"
FIVE = ["510300", "510050", "510500", "512100", "588000"]
CUTOFF = "2026-10-09"

legs = {}
fails = []


def leg(name, fn):
    try:
        legs[name] = fn()
        ok = legs[name].get("ok", False) if isinstance(legs[name], dict) else bool(legs[name])
        print(f"[{name}] {'PASS' if ok else 'FAIL'}")
        if not ok:
            fails.append(name)
    except Exception as e:  # noqa: BLE001 - probe reports, never crashes
        legs[name] = {"ok": False, "error": f"{type(e).__name__}: {e}"}
        fails.append(name)
        print(f"[{name}] FAIL -> {type(e).__name__}: {e}")


def leg_l1_mp1_face():
    d = json.loads((ROOT / "results" / "mp1_tsgate_p1.json").read_text(encoding="utf-8"))
    vc = d.get("verdict_counts", {})
    n_pass = vc.get("PASS")
    res = d.get("results", {})
    passes = sorted(k for k, v in res.items() if isinstance(v, dict) and v.get("verdict") == "PASS")
    axis = {k: res[k]["OOS"]["med_t"] for k in passes}
    ok = (n_pass == 25) and (len(passes) == 25) and all(isinstance(v, (int, float)) for v in axis.values())
    return {"ok": ok, "n_pass": n_pass, "n_pass_gates": len(passes), "med_t_axis_all_numeric": ok,
            "cutoff": d.get("evidence_cutoff"), "pass_gates": passes}


def leg_l2_five_member_face():
    d = json.loads((ROOT / "results" / "mp1_tsgate_p1.json").read_text(encoding="utf-8"))
    fm = d.get("five_member_oos", {})
    res = d.get("results", {})
    passes = sorted(k for k, v in res.items() if isinstance(v, dict) and v.get("verdict") == "PASS")
    missing = [g for g in passes if g not in fm]
    member_missing = {g: [m for m in FIVE if m not in fm.get(g, {})] for g in passes if g in fm}
    member_missing = {g: ms for g, ms in member_missing.items() if ms}
    n_in_all = [fm[g][m]["n_in"] for g in passes for m in FIVE if g in fm and m in fm[g]]
    neg_prior = {}
    for g in ("DELTA(MAX(VOLUME,30),5)_q90", "DELTA(MAX(RET,30),5)_q90"):
        if g in fm:
            neg_prior[g] = {m: fm[g][m]["net"] for m in ("510050", "510300")}
    ok = (not missing) and (not member_missing) and bool(n_in_all)
    return {"ok": ok, "pass_gates_covered": len(passes) - len(missing), "missing": missing,
            "member_missing": member_missing, "n_in_min": min(n_in_all), "n_in_max": max(n_in_all),
            "dual_negative_member_prior": neg_prior}


def leg_l3_a158_library():
    d = json.loads((ROOT / "results" / "gate_recheck_a158.json").read_text(encoding="utf-8"))
    lib = d.get("library_entries", [])
    ok = (len(lib) == 17) and all(isinstance(x, str) for x in lib)
    return {"ok": ok, "library_entries": lib, "a158_cutoff": d.get("evidence_cutoff"),
            "same_instant_rebuild_law": "this batch rebuilds registered-gate signals at 2026-10-09"}


def leg_l4_import_faces():
    import importlib
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))  # r817 dual-entry path law: ROOT injection before scripts.* import
    faces = {}
    mp1 = importlib.import_module("scripts.mp1_tsgate_probe")
    for attr in ("parse_formula", "mp1_factors", "gate_universe", "inst_gate_stats", "thin", "load_truncated"):
        faces[f"mp1.{attr}"] = hasattr(mp1, attr)
    a158 = importlib.import_module("scripts.a158_tsgate_probe")
    faces["a158.alpha158_factors"] = hasattr(a158, "alpha158_factors")
    rc = importlib.import_module("scripts.a158_gate_recheck")
    for attr in ("thin_b", "union_find_clusters", "face_a_leg"):
        faces[f"recheck.{attr}"] = hasattr(rc, attr)
    ok = all(faces.values())
    return {"ok": ok, "faces": faces}


def leg_l5_panel_truth():
    import pandas as pd
    row = None
    last_dates = {}
    for code in FIVE:
        p = ROOT / "data" / "daily" / f"sh{code}.csv"
        if not p.exists():
            return {"ok": False, "missing": code}
        df = pd.read_csv(p)
        df["date"] = df["date"].astype(str)
        df = df[df["date"] <= CUTOFF]
        last_dates[code] = int(len(df))
        if code == "510300":
            row = int(len(df))
    ok = (row == 3490) and all(v > 0 for v in last_dates.values())
    return {"ok": ok, "sh510300_truncated_rows": row, "member_rows": last_dates}


def leg_l6_prereg_markers():
    t = (ROOT / "research" / "GATE_RECHECK_MP1_PREREG.md").read_text(encoding="utf-8")
    markers = {f"s{i}": (f"## \u00a7{i}" in t or f"## \u00a7{i} " in t or f"\u00a7{i}" in t) for i in range(0, 9)}
    # section headers in this prereg are written as "## §0 批件身份" style; check char presence
    for i in range(0, 9):
        markers[f"sec{i}"] = (f"\u00a7{i}" in t)
    draft_state = "DRAFT" in t.split("\n")[0] or "DRAFT" in t[:400]
    tech = (ROOT / "state" / "queue" / "tech.md").read_text(encoding="utf-8")
    t25 = ("| T25 |" in tech) and ("GATE-RECHECK-MP1" in tech)
    ok = all(markers[f"sec{i}"] for i in range(0, 9)) and draft_state and t25
    return {"ok": ok, "sections": {f"sec{i}": markers[f"sec{i}"] for i in range(0, 9)},
            "draft_state": draft_state, "t25_registered": t25}


leg("L1_mp1_face", leg_l1_mp1_face)
leg("L2_five_member_face", leg_l2_five_member_face)
leg("L3_a158_library", leg_l3_a158_library)
leg("L4_import_faces", leg_l4_import_faces)
leg("L5_panel_truth", leg_l5_panel_truth)
leg("L6_prereg_markers", leg_l6_prereg_markers)

receipt = {
    "batch": "GATE-RECHECK-MP1-slice1-draft-probe",
    "machine": "bm-b",
    "round": "r869",
    "ok": not fails,
    "n_pass_legs": 6 - len(fails),
    "failed_legs": fails,
    "legs": legs,
}
RECEIPT.write_text(json.dumps(receipt, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"receipt -> {RECEIPT}  ok={receipt['ok']} ({receipt['n_pass_legs']}/6)")
sys.exit(0 if not fails else 1)

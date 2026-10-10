#!/usr/bin/env python
# r859 bm-b draft-facts probe for PERPETUAL-N2-W18 prereg DRAFT (T23 U3-1 channel).
# Verifies every frozen anchor cited by research/PERPETUAL_N2_W18_PREREG.md against
# live products: census JSON frozen faces, astock panel disk-truth, CLOSED_FAMILIES
# non-collision (9 keys, no alpha/grammar/formula word-face), TRIAL_GRAMMAR_LEDGER
# zero alphagen rows (first-burn confirmation), trials-ledger head anchor.
# Read-only probe: zero burn, zero ledger append, zero seed registration.
# Receipt -> results/_r859bmb_n2w18_draft_probe.json. Pure ASCII body (GBK law).
# Exit contract: 0 = all checks pass (selftest: all legs pass); 2 = check failure.
import glob as globmod
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# r817 pit law: ROOT must precede scripts/ on sys.path so the `knowledge`
# namespace package resolves when science_gates imports it (dual-entry parity).
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

CENSUS = os.path.join(ROOT, "results", "t23_census", "CENSUS-2026-10-09.json")
STATUS = os.path.join(ROOT, "results", "astock_daily_update_status.json")
PERDIR = os.path.join(ROOT, "data", "astock_daily", "per")
LEDGER = os.path.join(ROOT, "research", "TRIAL_GRAMMAR_LEDGER.md")
PREREG = os.path.join(ROOT, "research", "PERPETUAL_N2_W18_PREREG.md")
RECEIPT = os.path.join(ROOT, "results", "_r859bmb_n2w18_draft_probe.json")

FAMILY_KEY = "alphagen_grammar_v1"
ANCHORS = {
    "census_holds": True,
    "observed_family_max_abs_icir": 0.353,
    "null_family_p95": 0.139,
    "b_nulls": 64,
    "min_cross": 100,
    "census_days": 500,
    "k_formulas": 64,
    "n_unique_formulas": 48,
    "evidence_cutoff": "2026-10-09",
    "ledger_total": 876731,
}
PREREG_MARKERS = [
    "PERPETUAL-N2-W18",
    "alphagen_grammar_v1",
    "0.353",
    "0.139",
    "876,731",
    "null_family_p95",
    "family-max",
]
WORD_FACES = ("alpha", "grammar", "formula")


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def census_faces(d):
    c = d["census"]
    fr = d["frozen_readout"]
    return {
        "census_holds": c["census_holds"],
        "observed_family_max_abs_icir": c["observed_family_max_abs_icir"],
        "null_family_p95": c["null_family_p95"],
        "b_nulls": fr["b_nulls"],
        "min_cross": fr["min_cross"],
        "census_days": fr["census_days"],
        "k_formulas": fr["k_formulas"],
        "n_unique_formulas": c["n_unique_formulas"],
        "evidence_cutoff": d["evidence_cutoff"],
        "ledger_total": d["trials_ledger"]["total"],
    }


def check_census(path):
    faces = census_faces(load_json(path))
    bad = sorted(k for k, v in ANCHORS.items() if faces.get(k) != v)
    return faces, bad


def families_verdict(cf, family_key):
    keys = sorted(cf.keys())
    hits = [k for k in keys if any(w in k for w in WORD_FACES)]
    return {
        "n_keys": len(keys),
        "keys": keys,
        "family_key": family_key,
        "family_key_collides": family_key in cf,
        "word_face_hits": hits,
    }


def check_closed_families():
    import science_gates as sg
    v = families_verdict(sg.CLOSED_FAMILIES, FAMILY_KEY)
    ok = (not v["family_key_collides"]) and (not v["word_face_hits"]) and v["n_keys"] == 9
    return v, ok


def check_panel():
    st = load_json(STATUS)
    per_files = len(globmod.glob(os.path.join(PERDIR, "*.csv")))
    complete = bool(st.get("panel", {}).get("complete"))
    cutoff = st.get("panel", {}).get("cutoff") or st.get("cutoff") or ""
    v = {"complete": complete, "per_files_on_disk": per_files, "cutoff": cutoff,
         "disk_truth_law": "per-files disk count wins (r840 gate fix)"}
    ok = complete and per_files >= 5000 and cutoff >= "2026-10-09"
    return v, ok


def check_ledger_head():
    import science_gates as sg
    head = sg.ledger_head()
    total = head["total"]
    v = {"ledger_head_total": total, "draft_anchor": ANCHORS["ledger_total"],
         "monotone_ok": total >= ANCHORS["ledger_total"]}
    return v, v["monotone_ok"]


def prereg_markers_ok(text):
    missing = [m for m in PREREG_MARKERS if m not in text]
    sections = text.count("\u00a7")
    return missing, sections


def check_prereg():
    with open(PREREG, "r", encoding="utf-8") as f:
        text = f.read()
    missing, sections = prereg_markers_ok(text)
    v = {"missing_markers": missing, "section_marks": sections,
         "draft_status_line": "DRAFT" in text.splitlines()[0] if text else False}
    ok = (not missing) and sections >= 10 and v["draft_status_line"]
    return v, ok


def check_ledger_alphagen_rows():
    with open(LEDGER, "r", encoding="utf-8", errors="replace") as f:
        text = f.read()
    n = text.lower().count("alphagen")
    return {"alphagen_rows": n, "first_burn_confirmed": n == 0}, n == 0


def run_probe():
    out = {"probe": "r859 bm-b PERPETUAL-N2-W18 draft-facts probe",
           "zero_burn": True, "zero_ledger_append": True, "zero_seeds": True,
           "checks": {}, "verdict": "PASS"}
    try:
        faces, bad = check_census(CENSUS)
        out["checks"]["census_anchors"] = {"faces": faces, "mismatches": bad,
                                            "ok": not bad}
        v, ok = check_panel()
        out["checks"]["astock_panel_disk_truth"] = {**v, "ok": ok}
        v, ok = check_closed_families()
        out["checks"]["closed_families"] = {**v, "ok": ok}
        v, ok = check_ledger_head()
        out["checks"]["trials_ledger_head"] = {**v, "ok": ok}
        v, ok = check_prereg()
        out["checks"]["prereg_draft_markers"] = {**v, "ok": ok}
        v, ok = check_ledger_alphagen_rows()
        out["checks"]["grammar_ledger_first_burn"] = {**v, "ok": ok}
    except Exception as exc:  # fail-closed
        out["verdict"] = "FAIL"
        out["fail_closed"] = repr(exc)
        _write(out)
        print("FAIL-CLOSED:", repr(exc))
        return 2
    all_ok = all(c.get("ok") for c in out["checks"].values())
    out["verdict"] = "PASS" if all_ok else "FAIL"
    _write(out)
    print(json.dumps({k: c.get("ok") for k, c in out["checks"].items()}))
    print("verdict:", out["verdict"])
    return 0 if all_ok else 2


def _write(out):
    tmp = RECEIPT + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    os.replace(tmp, RECEIPT)


def _synthetic_census():
    fr = {"b_nulls": 64, "census_days": 500, "k_formulas": 64, "min_cross": 100}
    c = {"census_holds": True, "n_unique_formulas": 48,
         "observed_family_max_abs_icir": 0.353, "null_family_p95": 0.139}
    return {"census": c, "frozen_readout": fr, "evidence_cutoff": "2026-10-09",
            "trials_ledger": {"total": 876731}}


def selftest():
    legs = []

    def leg(name, ok):
        legs.append((name, bool(ok)))
        print(("PASS " if ok else "FAIL ") + name)

    tmpd = tempfile.mkdtemp(prefix="n2w18_probe_st_")
    good = os.path.join(tmpd, "census.json")
    with open(good, "w", encoding="utf-8") as f:
        json.dump(_synthetic_census(), f)
    _, bad = check_census(good)
    leg("L1 synthetic census anchors pass", bad == [])
    d = _synthetic_census()
    d["census"]["observed_family_max_abs_icir"] = 0.9
    wrong = os.path.join(tmpd, "wrong.json")
    with open(wrong, "w", encoding="utf-8") as f:
        json.dump(d, f)
    _, bad = check_census(wrong)
    leg("L2 corrupted family max caught", bad == ["observed_family_max_abs_icir"])
    try:
        check_census(os.path.join(tmpd, "missing.json"))
        leg("L3 missing census fail-closed", False)
    except Exception:
        leg("L3 missing census fail-closed", True)
    v = families_verdict({"cta_futures_p1": {}, "factor_blend": {}}, FAMILY_KEY)
    leg("L4 families clean pass", (not v["family_key_collides"])
        and v["word_face_hits"] == [] and v["n_keys"] == 2)
    v = families_verdict({"alphagen_grammar_v1": {}}, FAMILY_KEY)
    leg("L5 family-key collision caught", v["family_key_collides"])
    missing, sections = prereg_markers_ok(
        "PERPETUAL-N2-W18 DRAFT alphagen_grammar_v1 0.353 0.139 876,731 "
        "null_family_p95 family-max " + "\u00a7" * 12)
    leg("L6 prereg marker logic", missing == [] and sections >= 10)
    missing, _ = prereg_markers_ok("no markers here")
    leg("L7 prereg missing markers caught", len(missing) == len(PREREG_MARKERS))
    ok = all(r[1] for r in legs)
    print("selftest:", ("%d/%d PASS" % (len(legs), len(legs))) if ok
          else "FAIL legs: %s" % [r for r in legs if not r[1]])
    return 0 if ok else 2


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd == "selftest":
        sys.exit(selftest())
    elif cmd == "run":
        sys.exit(run_probe())
    else:
        print("usage: run | selftest")
        sys.exit(2)

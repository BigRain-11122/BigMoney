"""E110 -- close the burncontrol MISMATCH: name the 11 cells and their reason.

Background
----------
``e39_panel_census.py burncontrol`` (E88) joins the published churn-robust face
against the interval face and against an earlier-start twin, cell by cell on
(book, universe|mode, era), and demands exact equality.  It exited rc=1 with
``status=MISMATCH`` on 11 of 56 shared cells in *both* arms of the E109 sweep.

The ticket read that as "so the mismatch is not the repair factor".  It is the
repair factor -- seen from the other side.  ``burncontrol`` recomputes nothing:
it reads faces off disk.  The 2013-start twin on disk was
``CHURNROBUST-20261022-s2013.json``, burned 2026-10-22, i.e. **before** the
E108 fix to ``panel_screen.split_events``.  A pre-fix face compared with a
post-fix face disagrees regardless of which arm the *current* leg was run in,
which is exactly what "both arms" looked like.

What this tool separates
------------------------
``burncontrol``'s before/after delta mixes two causes: the factor and four days
of panel arrival (the stale twin's cutoff is 2026-10-22, the fresh ones
2026-10-26).  So the delta is reported three ways:

* ``stale_vs_fixed``  -- old face (10-22, pre-fix) vs the refreshed face.
  This is the number the control originally read.  CONFOUNDED.
* ``legacy_vs_fixed`` -- same panel, same start, factor flipped only.  This is
  the clean attribution of the factor.
* ``control``         -- ``burncontrol`` re-run on the refreshed twin: 0
  mismatched cells at one cutoff, which is the part that carries no confound.

Usage:
    python scripts/e110_burncontrol_close.py run [--out F]
    python scripts/e110_burncontrol_close.py selftest
"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, os.path.join(ROOT, "results"))

FACE_DIR = os.path.join(ROOT, "results", "e44_midmonth")
STALE_TWIN = "CHURNROBUST-20261022-s2013.json"
FRESH_TWIN = "CHURNROBUST-20261026-s2013.json"
INTERVAL = "CHURNSE-20261026.json"
CONTROL = "CHURNROBUST-CONTROL-20261026.json"


def _cell_keys(face):
    """(book, universe|mode, era) -> value, for levels and deltas separately."""
    out = {"levels": {}, "deltas": {}}
    for c in face.get("cells") or []:
        out["levels"][(c.get("book"), c.get("universe"), c.get("era"))] = c.get("mean_bp")
    for c in face.get("delta_cells") or []:
        out["deltas"][(c.get("book"), c.get("mode"), c.get("era"))] = c.get("mean_bp")
    return out


def compare(a, b, label):
    """Join two cell dicts and report moved cells, largest first."""
    rows = []
    shared = 0
    for kind in ("levels", "deltas"):
        ka, kb = a.get(kind) or {}, b.get(kind) or {}
        for k in sorted(set(ka) & set(kb)):
            av, bv = ka[k], kb[k]
            if av is None or bv is None:
                continue
            shared += 1
            if av != bv:
                rows.append({"kind": kind, "keys": list(k), "a": av, "b": bv,
                             "delta": round(bv - av, 4)})
    rows.sort(key=lambda r: -abs(r["delta"]))
    return {"label": label, "shared_cells": shared, "moved": len(rows),
            "moved_rows": rows}


def _burn(start, legacy=False):
    """Burn one robustchurn face in memory; optionally with the old factor."""
    import e39_panel_census as e39
    import panel_screen
    orig = None
    if legacy:
        from e108_repairfix import legacy_split_events
        orig = legacy_split_events()
    try:
        return e39.run_robustchurn(None, start=start)
    finally:
        if orig is not None:
            panel_screen.split_events = orig


def _load(name):
    p = os.path.join(FACE_DIR, name)
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def run(out_path=None):
    stale, fresh = _load(STALE_TWIN), _load(FRESH_TWIN)
    interval, control = _load(INTERVAL), _load(CONTROL)
    missing = [n for n, v in ((STALE_TWIN, stale), (FRESH_TWIN, fresh),
                              (INTERVAL, interval), (CONTROL, control)) if v is None]
    if missing:
        return {"tool": "scripts/e110_burncontrol_close.py",
                "status": "awaiting_faces", "missing": missing}

    legacy_now = _burn("2013-01-01", legacy=True)
    fixed_now = _burn("2013-01-01", legacy=False)

    stale_k, fresh_k = _cell_keys(stale), _cell_keys(fresh)
    legacy_k, fixed_k = _cell_keys(legacy_now), _cell_keys(fixed_now)

    out = {
        "tool": "scripts/e110_burncontrol_close.py",
        "study": "E110 burncontrol MISMATCH: the 2013-start twin on disk predates the "
                 "E108 split_events factor, so the control compared a pre-fix face "
                 "with a post-fix one",
        "evidence_cutoff": fixed_now.get("evidence_cutoff"),
        "faces": {"stale_twin": STALE_TWIN, "fresh_twin": FRESH_TWIN,
                  "interval": INTERVAL, "control": CONTROL},
        "cutoffs": {"stale_twin": stale.get("evidence_cutoff"),
                    "fresh_twin": fresh.get("evidence_cutoff")},
        "stale_vs_fixed": compare(stale_k, fresh_k,
                                  "old face (2026-10-22, pre-E108) vs refreshed twin"),
        "legacy_vs_fixed": compare(legacy_k, fixed_k,
                                   "same panel same start, factor flipped only"),
        "control": {"status": control.get("status"),
                    "summary": control.get("summary")},
        "confound": "stale_vs_fixed mixes the factor with four days of panel arrival "
                    "(cutoffs 2026-10-22 vs 2026-10-26); legacy_vs_fixed is the clean "
                    "factor attribution and the control verdict is cutoff-clean",
    }
    if out_path:
        with open(out_path, "w", encoding="utf-8") as fh:
            json.dump(out, fh, ensure_ascii=False, indent=1)
    return out


def _mk(cells, deltas):
    return {"cells": [{"book": b, "universe": u, "era": e, "mean_bp": v}
                      for (b, u, e), v in cells.items()],
            "delta_cells": [{"book": b, "mode": m, "era": e, "mean_bp": v}
                            for (b, m, e), v in deltas.items()]}


def selftest():
    fails = []
    n = 0

    def chk(cond, label):
        nonlocal n
        n += 1
        if not cond:
            fails.append(label)

    # 1. identical faces move nothing
    a = _mk({("me", "unscreened", "2024_now"): 1.0}, {("me", "drop", "2024_now"): 2.5})
    c = compare(_cell_keys(a), _cell_keys(a), "same")
    chk(c["moved"] == 0 and c["shared_cells"] == 2, "identical faces must be silent")

    # 2. a single moved leaf is named with its keys
    b = _mk({("me", "unscreened", "2024_now"): 1.0}, {("me", "drop", "2024_now"): 9.5})
    c = compare(_cell_keys(a), _cell_keys(b), "one")
    chk(c["moved"] == 1 and c["moved_rows"][0]["keys"] == ["me", "drop", "2024_now"],
        "a moved leaf must be named")
    chk(abs(c["moved_rows"][0]["delta"] - 7.0) < 1e-9, "delta must be b-a")

    # 3. a None value is not counted as a move (unmeasurable != changed)
    d = _mk({("me", "unscreened", "2024_now"): None}, {})
    c = compare(_cell_keys(a), _cell_keys(d), "none")
    chk(c["moved"] == 0, "None must not read as a move")

    print(json.dumps({"selftest": "%d/%d" % (n - len(fails), n), "fails": fails}))
    return 0 if not fails else 1


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    if argv[0] == "selftest":
        return selftest()
    if argv[0] == "run":
        out = os.path.join(FACE_DIR, "BURNCONTROL-CLOSE-20261027.json")
        if "--out" in argv:
            out = argv[argv.index("--out") + 1]
        f = run(out)
        print(json.dumps({"status": f.get("status"),
                          "stale_vs_fixed": {k: f["stale_vs_fixed"][k]
                                             for k in ("shared_cells", "moved")}
                          if "stale_vs_fixed" in f else None,
                          "legacy_vs_fixed": {k: f["legacy_vs_fixed"][k]
                                              for k in ("shared_cells", "moved")}
                          if "legacy_vs_fixed" in f else None,
                          "control": f.get("control"),
                          "file": os.path.relpath(out, ROOT)}, ensure_ascii=False))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
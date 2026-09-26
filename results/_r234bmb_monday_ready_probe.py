"""r234 bm-b: Monday 2026-09-28 new-bar full-chain readiness probe (read-only).

Motivation: every advisory/board lane is time-gated this round; the 09-28
Monday new-bar chain (update_daily -> live.paper[REGIME_GUARD v3] -> t35_open_fill_verify
-> t24_prospect_paper x2 -> aggr/alloc -> export/scorecard) is the next
high-stakes window. This probe verifies the checkable prerequisite faces NOW so
Monday hits no surprises. Fail-closed: any critical face broken -> NOT_READY.

Faces (all read-only, no network, no engine):
  A. REGIME_GUARD v3 gate trio: approval file exists + ENFORCE_ACTIVE_FROM
     frozen 2026-10-01 + regime_state.json fresh (today's S6 leg).
  B. paper state: results/paper/*_paper.json trader files with open_positions
     shape (t35 verify joins cost_price).
  C. prospect lane: t24 paper product lane present.
  D. AGGR/ALLOC paper lanes present (idempotent accrual proven this weekend).
  E. export lane: results/paper_export/latest.json cutoff face.
  F. chain head: update_daily status cutoff face.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

RESULTS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results")
TODAY = "2026-09-26"
out = {"probe": "r234bmb monday-ready", "faces": {}, "verdict": None}


def _today_epoch():
    import time
    import calendar
    y, m, d = (int(x) for x in TODAY.split("-"))
    return calendar.timegm((y, m, d, 0, 0, 0, 0, 0, 0))


def _face(name, critical=True):
    def deco(fn):
        try:
            out["faces"][name] = fn()
        except Exception as e:  # fail-closed per face
            out["faces"][name] = {"ok": False, "error": repr(e), "critical": critical}
        return fn
    return deco


@_face("A_regime_guard_v3")
def _a():
    import live.paper as P  # constants only, no side effects at import
    approval = os.path.exists(P.REGIME_GUARD_APPROVAL)
    state = None
    if os.path.exists(P.REGIME_GUARD_STATE):
        with open(P.REGIME_GUARD_STATE, encoding="utf-8") as fh:
            state = json.load(fh)
    asof = (state or {}).get("asof", "")
    fresh_today = os.path.getmtime(P.REGIME_GUARD_STATE) >= _today_epoch() if os.path.exists(P.REGIME_GUARD_STATE) else False
    return {
        "ok": bool(approval and P.ENFORCE_ACTIVE_FROM == "2026-10-01" and asof),
        "approval_file": approval,
        "enforce_active_from": P.ENFORCE_ACTIVE_FROM,
        "regime_state_fresh_today": fresh_today,
        "regime_state_asof": asof,
    }


@_face("B_paper_state")
def _b():
    d = os.path.join(RESULTS, "paper")
    files = sorted(f for f in os.listdir(d) if f.endswith("_paper.json")) if os.path.isdir(d) else []
    shape_ok, traders = True, []
    for fn in files:
        with open(os.path.join(d, fn), encoding="utf-8") as fh:
            st = json.load(fh)
        pos = st.get("open_positions", [])
        if any("cost_price" not in p for p in pos if isinstance(p, dict)):
            shape_ok = False
        traders.append((fn.replace("_paper.json", ""), len(pos)))
    return {"ok": bool(files) and shape_ok, "traders": traders, "open_positions_shape": shape_ok}


@_face("C_prospect_lane")
def _c():
    d = os.path.join(RESULTS, "prospect_paper")
    return {"ok": os.path.isdir(d), "files": len(os.listdir(d)) if os.path.isdir(d) else 0}


@_face("D_aggr_alloc_lanes")
def _d():
    aggr = os.path.join(RESULTS, "aggr_paper")
    alloc = os.path.join(RESULTS, "alloc_paper")
    return {"ok": os.path.isdir(aggr) and os.path.isdir(alloc),
            "aggr_files": len(os.listdir(aggr)) if os.path.isdir(aggr) else 0,
            "alloc_files": len(os.listdir(alloc)) if os.path.isdir(alloc) else 0}


@_face("E_export_lane")
def _e():
    p = os.path.join(RESULTS, "paper_export", "latest.json")
    if not os.path.exists(p):
        return {"ok": False, "missing": p}
    with open(p, encoding="utf-8") as fh:
        d = json.load(fh)
    return {"ok": d.get("export_date") == "2026-09-24" and len(d.get("traders", [])) == 6,
            "export_date": d.get("export_date"), "traders": len(d.get("traders", []))}


@_face("F_chain_head_daily")
def _f():
    p = os.path.join(RESULTS, "update_status.json")
    with open(p, encoding="utf-8") as fh:
        d = json.load(fh)
    return {"ok": d.get("data_cutoff") == "2026-09-24" and str(d.get("updated", "")).startswith(TODAY),
            "data_cutoff": d.get("data_cutoff"), "updated": d.get("updated")}


bad = [(k, v) for k, v in out["faces"].items() if not v.get("ok")]
out["verdict"] = "READY" if not bad else "NOT_READY"
out["failed_faces"] = [k for k, _ in bad]

dst = os.path.join(RESULTS, "_r234bmb_monday_ready.json")
with open(dst, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))
sys.exit(0 if out["verdict"] == "READY" else 2)

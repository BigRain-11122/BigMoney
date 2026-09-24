"""T-2026-09-24-19 consolidation-break governance, stage-1 (offline, additive).

Ticket: fleet/tasks/T-2026-09-24-19-P1.json (GM adjudication of the bm-c r47
T-14 prereg finding). Stage-1 slice, all offline/deterministic, zero new trials:

  build    -> data/consolidation/registry.json
              21 events re-derived from raw bars via the frozen T-14 detector
              (build_guard diag), hard-reconciled against the frozen T-14 batch
              JSON break_days, enriched with tier / implied_ratio / prev-close
              evidence / prev-calendar-gap flag. Official-announcement
              evidence slots stay pending (stage-2 data-lane probe).
  exposure -> results/t19_exposure_audit.json
              Six-trader holding-path x break-day audit = recorded-cell
              reproduction of the registered A-rail (g25/corr-watch precedent:
              ledger_trials_added=0) + _break_intersections recompute, the
              break face consumed from the registry file itself.
  selftest -> offline synthetic checks (ratio math / gap flag / intersection
              semantics / reconciliation canonicalizer).

Zero-touch: raw bars, registered anchors (D2 lockbox), engine files,
live/paper.py (stage-2 flag), T-08 dual-leg WIP, XSTOCK lane.
Decision-pack skeleton (option a guard-style vs b adjusted-panel) lives in
research/CONSOLIDATION_GOVERNANCE.md -- adjudication = GM.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime

import pandas as pd

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from scripts.science_gates import cutoff_meta
from scripts.t14_rules_fidelity import (
    build_guard, run_rail, _break_intersections, _load_traders, _seg_clean,
    _tier, CONSOL_MAG,
)
import live.paper as LP

T14_BATCH = os.path.join(_REPO, "results", "rules_fidelity_t14.json")
REG_PATH = os.path.join(_REPO, "data", "consolidation", "registry.json")
OUT_PATH = os.path.join(_REPO, "results", "t19_exposure_audit.json")

DETECTOR = ("T-14 frozen semantics: |pct| beyond real board window "
            "(tier+1.5pp) on raw per-symbol rows (artifact-exclusion law, "
            "prereg s3); 21 events / 19 symbols reconcile prereg s5")


def _dk(d) -> str:
    return d.strftime("%Y-%m-%d") if hasattr(d, "strftime") else str(d)[:10]


def _implied_ratio(pct: float) -> float:
    """Approximate conversion ratio from the observed price discontinuity.

    Honest label: observed-discontinuity approximation; the exact official
    conversion ratio (fund announcement) is a stage-2 evidence slot.
    """
    return round(1.0 / (1.0 + pct), 6)


def _canon(events: list[dict]) -> list[tuple]:
    return sorted((e["sym"], e["date"], round(float(e["pct"]), 4)) for e in events)


def _enrich(prices_full: dict, ev: dict) -> dict:
    df = prices_full[ev["sym"]]
    d = pd.Timestamp(ev["date"])
    pos = df.index.get_loc(d)
    prev_close = float(df.iloc[pos - 1]["close"])
    close = float(df.iloc[pos]["close"])
    pct_full = close / prev_close - 1.0
    gap = (d - pd.Timedelta(days=1)) not in df.index
    amp = ("consolidation_scale" if abs(pct_full) >= CONSOL_MAG
           else "beyond_window_marginal")
    return {
        "sym": ev["sym"], "date": ev["date"], "tier": _tier(ev["sym"]),
        "pct_observed": round(pct_full, 6),
        "pct_detector_4dp": round(float(ev["pct"]), 4),
        "amplitude_class": amp,
        "prev_date": str(df.index[pos - 1].date()),
        "prev_close": prev_close, "close": close,
        "implied_ratio_approx": _implied_ratio(pct_full),
        "prev_calendar_day_gap": bool(gap),
        "evidence": {"scan": "results/rules_fidelity_t14.json (frozen, "
                              "re-derived bit-exact this build)",
                      "official_announcement": "pending (stage-2 data-lane "
                                               "probe; single-probe-first; "
                                               "marginal-class events may "
                                               "reclassify as real extreme "
                                               "days)"},
    }


def build() -> int:
    print("[t19] build: loading core-48 ...")
    prices_full = LP.load_core()
    _, diag = build_guard(prices_full)
    tot = diag["totals"]
    assert tot["break_days"] == 21, tot
    assert tot["break_days_distinct_syms"] == 19, tot
    frozen = json.load(open(T14_BATCH, encoding="utf-8-sig"))
    fcanon = _canon(frozen["break_days"])
    rcanon = _canon(diag["break_days"])
    assert fcanon == rcanon, "re-derived events drift vs frozen T-14 batch"
    print(f"[t19] reconciliation: 21/21 events bit-exact vs frozen batch "
          f"(sym/date/pct@4dp)")

    events = [_enrich(prices_full, e) for e in diag["break_days"]]
    n_gap = sum(1 for e in events if e["prev_calendar_day_gap"])
    reg = {
        "registry": "consolidation_break_events",
        "schema_version": 1,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "ticket": "T-2026-09-24-19",
        "stage": 1,
        "detector": DETECTOR,
        "counts": {"events": len(events), "symbols": 19,
                   "prev_calendar_day_gap": n_gap},
        "reconciliation": {"vs_frozen_t14": "bit-exact (sym/date/pct@4dp), "
                          f"{len(fcanon)}/{len(rcanon)} events"},
        "events": events,
        "governance": {
            "decision_pack": "research/CONSOLIDATION_GOVERNANCE.md "
                             "(option a guard-style vs b adjusted-panel) -> "
                             "GM adjudication",
            "paper_forward_protection": "stage-2: live/paper.py additive "
                                        "default-off flag consuming this "
                                        "registry (no-trade/exclude interim)",
            "adjusted_panel": "stage-3: adjustment-factor series after "
                              "official-ratio verification; raw panel stays "
                              "authoritative for frozen anchors (D2 lockbox)",
            "anchor_freeze_law": "registered evidence never recomputed; "
                                 "disclosure-only rows",
        },
    }
    os.makedirs(os.path.dirname(REG_PATH), exist_ok=True)
    with open(REG_PATH, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(reg, fh, ensure_ascii=False, indent=1)
    print(f"[t19] registry written: {REG_PATH} "
          f"(events={len(events)}, gap_prev_day={n_gap})")
    return 0


def exposure() -> int:
    print("[t19] exposure: registry + frozen batch + traders ...")
    reg = json.load(open(REG_PATH, encoding="utf-8-sig"))
    assert reg["counts"]["events"] == 21, reg["counts"]
    break_by_sym: dict[str, list[str]] = {}
    for e in reg["events"]:
        break_by_sym.setdefault(e["sym"], []).append(e["date"])

    frozen = json.load(open(T14_BATCH, encoding="utf-8-sig"))
    rows_f = {r["trader"]: r for r in frozen["traders"]}
    prices_full = LP.load_core()

    table, total_x, total_phantom, total_boundary = [], 0, 0, 0
    for t in _load_traders():
        tid = t["id"]
        cutoff = LP.evidence_cutoff(t, prices_full)
        ps = pd.Timestamp(cutoff)
        prices = {s: df[df.index <= ps] for s, df in prices_full.items()}
        P = LP.build_panels(prices)
        a = run_rail(t, prices, P)          # recorded-cell repro, unaccounted
        ag = LP.anchor_gate(t, prices_full)
        assert ag["ok"], f"anchor gate FAIL {tid}: {ag.get('error')}"
        # determinism gate: recomputed A face == frozen T-14 batch A face
        a_ok = (_seg_clean(a["got"]["in_sample"]) == _seg_clean(rows_f[tid]["A"]["is"])
                and _seg_clean(a["got"]["out_sample"]) == _seg_clean(rows_f[tid]["A"]["oos"]))
        assert a_ok, f"A-face drift vs frozen batch: {tid}"
        inter = _break_intersections(a, break_by_sym)
        assert len(inter) == rows_f[tid]["break_intersections"], \
            f"exposure drift vs frozen batch: {tid}"
        # post-enrich (t19 layer only; frozen t14 semantics untouched):
        # entry-date + phantom classification + boundary rows (exit ON a
        # break day is missed by the frozen strict-< face).
        pos_of = {_dk(d): i for i, d in enumerate(a["idx"])}
        tmap = {(tr["symbol"], _dk(tr["date"])): tr for tr in a["trades"]}
        for h in inter:
            tr = tmap[(h["sym"], h["exit_date"])]
            e_pos = pos_of[h["exit_date"]] - int(tr["hold_days"])
            h["entry_date"] = _dk(a["idx"][e_pos])
            h["phantom_accrued"] = h["entry_date"] < h["break_date"]
        boundary = []
        for tr in a["trades"]:
            sym, ex = tr["symbol"], _dk(tr["date"])
            if sym not in break_by_sym or ex not in pos_of:
                continue
            e_pos = pos_of[ex] - int(tr["hold_days"])
            for bd in break_by_sym[sym]:
                if bd in pos_of and e_pos < pos_of[bd] == pos_of[ex]:
                    boundary.append({"sym": sym, "break_date": bd,
                                     "entry_date": _dk(a["idx"][e_pos]),
                                     "exit_date": ex,
                                     "phantom_accrued": True})
        n_phantom = sum(1 for h in inter if h["phantom_accrued"])
        total_x += len(inter)
        total_phantom += n_phantom
        total_boundary += len(boundary)
        table.append({"trader": tid, "cutoff": cutoff,
                      "anchor_gate_pass": True,
                      "a_face_matches_frozen": True,
                      "break_intersections": len(inter),
                      "phantom_accrual_rows": n_phantom,
                      "boundary_rows_missed_by_frozen": len(boundary),
                      "break_detail": inter,
                      "boundary_detail": boundary[:20]})
        print(f"[t19] {tid}: frozen_x={len(inter)} phantom={n_phantom} "
              f"boundary={len(boundary)} (frozen batch "
              f"{rows_f[tid]['break_intersections']})")

    reg_pct = {e["sym"] + "@" + e["date"]: e["pct_observed"]
               for e in reg["events"]}
    phantom_summary = []
    for r in table:
        rows = [dict(h, face="frozen") for h in r["break_detail"]
                if h["phantom_accrued"]]
        rows += [dict(b, face="boundary") for b in r["boundary_detail"]]
        if rows:
            for x in rows:
                x["event_pct"] = reg_pct.get(x["sym"] + "@" + x["break_date"])
            phantom_summary.append({"trader": r["trader"],
                                    "phantom_exposed_rows": len(rows),
                                    "rows": rows})
    out = {
        **cutoff_meta("2026-09-23"),
        "batch": "consolidation_exposure_audit_t19",
        "ticket": "T-2026-09-24-19",
        "stage": 1,
        "deliverable": "six-trader holding-path x consolidation-break audit",
        "registry_source": "data/consolidation/registry.json (dogfood consumed)",
        "intersection_semantics": _break_intersections.__doc__.strip().splitlines()[0],
        "boundary_semantics": ("t19 layer, additive to frozen s5: exit ON a "
                               "break day (entry < break == exit) is a real "
                               "held-across exposure the frozen strict-< face "
                               "misses; all boundary rows are phantom-exposed"),
        "traders": table,
        "verdict": {
            "total_intersections_frozen_face": total_x,
            "phantom_accrual_rows": total_phantom,
            "boundary_rows_missed_by_frozen": total_boundary,
            "statement": (
                "After the T-19 type-vacuity fix the frozen face is no longer "
                "vacuous: registered faces carry REAL phantom P&L from "
                "share-consolidation breaks -- windfalls AND losses, in both "
                "IS and OOS windows (see phantom_exposure_summary rows for "
                "the exact trader/symbol/date/event_pct faces). Registered "
                "anchors stay frozen (D2 lockbox) -- disclosure only; "
                "contribution quantification = stage-2 preregged "
                "counterfactual face for the GM decision pack."
                if total_x else
                "ZERO registered trader ever held across a consolidation "
                "break day in IS/OOS windows"),
            "phantom_exposure_summary": phantom_summary,
            "anchor_rewrites": 0,
        },
        "audit": {
            "ledger_trials_added": 0,
            "basis": "recorded-cell reproduction of registered A-rail "
                     "(g25 family-matrix / corr-watch precedent); break-day "
                     "scan = data face, not a trial",
        },
    }
    with open(OUT_PATH, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print(f"[t19] exposure audit written: {OUT_PATH} "
          f"(total_intersections={total_x})")
    return 0


def selftest() -> bool:
    ok = True

    def _chk(name, cond):
        nonlocal ok
        print(f"  [t19] {name}: {'PASS' if cond else 'FAIL'}")
        ok = ok and bool(cond)

    # S1 ratio math: -50% discontinuity -> 2.0 shares-per-old-share scale
    _chk("implied_ratio(-0.5)==2.0", _implied_ratio(-0.5) == 2.0)
    _chk("implied_ratio(+1.0)==0.5", _implied_ratio(1.0) == 0.5)
    # S2 gap flag: break day after a weekend/holiday -> prev calendar day absent
    idx = pd.to_datetime(["2026-05-11", "2026-05-13"])  # 05-12 absent
    d = pd.Timestamp("2026-05-13")
    _chk("gap flag true when prev calendar day missing",
         (d - pd.Timedelta(days=1)) not in idx)
    idx2 = pd.to_datetime(["2026-05-12", "2026-05-13"])   # consecutive bdates
    _chk("gap flag false when prev calendar day present",
         (pd.Timestamp("2026-05-13") - pd.Timedelta(days=1)) in idx2)
    # S3 intersection semantics on a synthetic rail (real t14 function)
    days = pd.bdate_range("2026-01-05", periods=6)
    rail = {"idx": days, "trades": [
        {"symbol": "AAA", "date": str(days[5].date()), "hold_days": 3},  # spans d2
        {"symbol": "AAA", "date": str(days[2].date()), "hold_days": 2},  # ends on d2
    ]}
    hits = _break_intersections(rail, {"AAA": [str(days[2].date())]})
    _chk("synthetic rail: 1 hit (hold spans break day)",
         len(hits) == 1 and hits[0]["break_date"] == str(days[2].date()))
    # S4 reconciliation canonicalizer: order-insensitive equality
    a = [{"sym": "X", "date": "2026-01-02", "pct": -0.5103},
         {"sym": "Y", "date": "2026-01-05", "pct": 1.0094}]
    b = list(reversed(a))
    _chk("canon equal under reordering", _canon(a) == _canon(b))
    c = [{"sym": "X", "date": "2026-01-02", "pct": -0.51}]
    _chk("canon detects pct drift", _canon(a) != _canon(c))
    print(f"  [t19] selftest {'PASS' if ok else 'FAIL'}")
    return ok


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] == "selftest":
        return 0 if selftest() else 1
    if argv and argv[0] == "build":
        return build()
    if argv and argv[0] == "exposure":
        return exposure()
    if argv and argv[0] == "all":
        rc = build()
        return rc or exposure()
    print("usage: t19_consolidation_registry.py [build|exposure|all|selftest]")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

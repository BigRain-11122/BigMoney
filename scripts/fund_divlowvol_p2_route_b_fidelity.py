"""FUND-DIVLOWVOL-P2 route-B signal fidelity leg (r1069 bm-b).

WHY
---
FUND-DIVLOWVOL-P2 sec.2.2 ruled the burn face: route A = p1c re-delivery
(preferred, zero residual risk) vs route B = local substrate with
`vwap_raw_proxy` (P_raw = amount/volume on the signal date, which carries
splits natively). sec.2.2 only proved that the cash-only sidecar cannot
reconstruct raw close (rho test). It did NOT answer the decision-relevant
question: *does the split distortion actually change the picks?*

This leg answers exactly that, on the frozen substrate, with no burn:

  route A yield: y_A = ttm_cash / (close_qfq(t) * f_cash(t))
  route B yield: y_B = ttm_cash / (amount(t) / volume(t))

Same base eligibility mask, same sigma screen, same quality (PIT) leg, same
Top-N rule -- only the price that converts cash into a yield differs. Every
kernel is imported single-source from fund_divlowvol_p1 / p2_probe; nothing
is re-implemented here.

PRE-DECLARED DECISION RULE (written before running, not tuned after)
--------------------------------------------------------------------
Route B is ACCEPTED as signal-equivalent iff all three hold:
  (1) median monthly Top-20 Jaccard(A,B) >= 0.90
  (2) share of months with Jaccard < 0.50 <= 5%
  (3) UNIVERSE_FLOOR (>=60 candidates) verdict agreement >= 95%
Otherwise route B is REJECTED for the judged batch and route A (p1c
re-delivery) is mandatory. A missing vwap (amount/volume non-finite or <=0)
is an honest exclusion in route B, counted and disclosed -- never silently
backfilled with the route-A price.

Read-only: zero judged claims, zero ledger, zero pool writes.

Usage
-----
  python scripts/fund_divlowvol_p2_route_b_fidelity.py run [--limit N]
  python scripts/fund_divlowvol_p2_route_b_fidelity.py selftest
  python scripts/fund_divlowvol_p2_route_b_fidelity.py status
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

OUT_DIR = os.path.join("results", "fund_divlowvol_p2")
OUT_JSON = os.path.join(OUT_DIR, "route_b_fidelity.json")
TZ = timezone(timedelta(hours=8))

TOP_N = 20
UNIVERSE_FLOOR = 60
JACCARD_MEDIAN_FLOOR = 0.90
TAIL_SHARE_CAP = 0.05
FLOOR_AGREE_FLOOR = 0.95


def _now_iso():
    return datetime.now(TZ).isoformat(timespec="seconds")


def _log(msg, **kw):
    print(json.dumps({"ts": _now_iso(), "msg": msg, **kw}, ensure_ascii=False))


def _dump(obj, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


def _jaccard(a, b):
    sa, sb = set(a), set(b)
    if not sa and not sb:
        return 1.0
    return len(sa & sb) / float(len(sa | sb))


def _rank_top(pj, vals, codes, keep_mask=None, n=TOP_N):
    """Frozen tie-break: code ascending, then yield descending (cell_picks
    verbatim). keep_mask filters BEFORE ranking (the quality leg order)."""
    pj = np.asarray(pj, dtype=np.int64)
    vals = np.asarray(vals, dtype=np.float64)
    if keep_mask is not None:
        pj, vals = pj[keep_mask], vals[keep_mask]
    if len(pj) == 0:
        return pj
    order = np.lexsort((codes[pj], -vals))
    return pj[order[:min(n, len(pj))]]


# ------------------------------------------------------------------ run face
def _route_b_month(R2, F1, P2, p, cand_floor=UNIVERSE_FLOOR):
    """Route-B candidate set + Top-N for one signal month p."""
    G = F1._G                       # panel faces live in the P1 skeleton
    syms = G["syms"]
    by_sym = G["by_sym"]
    sidecars = G["sidecars"]
    codes = np.array([str(s) for s in syms])
    u = F1._month_universe(p)
    t_int, ws_int = u["t_int"], u["ws_int"]
    amt_row = np.asarray(G["amount_np"][p], dtype=np.float64)
    vol_row = np.asarray(G["volume_np"][p], dtype=np.float64)
    sigma, valid = F1._sigma_row(p)
    min_bars = F1.VOL_MIN_BARS

    cand_j, cand_y, cand_s = [], [], []
    n_cash_pos = 0
    n_vwap_missing = 0
    for j in u["base_j"]:
        code = str(syms[j])
        pack = by_sym.get(code)
        sc = sidecars.get(code)
        if pack is None or sc is None:
            continue
        cash = F1.ttm_cash_sum(pack[0], pack[1], t_int, ws_int)
        if cash <= 0:
            continue
        n_cash_pos += 1
        if valid[j] < min_bars or not np.isfinite(sigma[j]):
            continue
        p_raw = amt_row[j] / vol_row[j] if vol_row[j] > 0 else np.nan
        if not np.isfinite(p_raw) or p_raw <= 0:
            n_vwap_missing += 1
            continue
        cand_j.append(int(j))
        cand_y.append(float(cash) / float(p_raw))
        cand_s.append(float(sigma[j]))

    cj = np.array(cand_j, dtype=np.int64)
    cy = np.array(cand_y, dtype=np.float64)
    cs = np.array(cand_s, dtype=np.float64)
    n_cand = len(cj)
    skipped = n_cand < cand_floor
    if skipped or n_cand == 0:
        top = cj[:0]
    else:
        med = float(np.median(cs))
        m = cs <= med
        top = _rank_top(cj[m], cy[m], codes,
                        keep_mask=R2._quality_mask(t_int, cj[m]))
    return {"p": int(p), "t_int": t_int, "n_cand_b": int(n_cand),
            "n_cash_pos": int(n_cash_pos), "n_vwap_missing": int(n_vwap_missing),
            "skipped_b": bool(skipped), "top_b": top,
            "cand_j": cj, "cand_y": cy}


def cmd_run(args):
    import fund_divlowvol_p2_backtest as R2
    import fund_divlowvol_p1 as F1

    t0 = time.time()
    R2._init(basis=args.basis)
    picks = R2.cell_picks("TN20")          # route-A frozen cell, quality ON
    codes = R2._G["codes_arr"]
    basis = R2._G["basis"]
    rows = []

    limit = args.limit if args.limit and args.limit > 0 else len(picks)
    for (m, _end, top_a, _w) in picks[:limit]:
        rb = _route_b_month(R2, F1, None, m)
        u = F1._month_universe(m)
        ska = bool(u["skipped"])
        n_a = int(u["n_cand"])
        jac = _jaccard(top_a.tolist(), rb["top_b"].tolist())
        # yield ratio + rank agreement on the common candidate set
        common = np.intersect1d(u["cand_j"], rb["cand_j"])
        ratio_med = None
        if len(common):
            idx_a = {int(j): i for i, j in enumerate(u["cand_j"])}
            idx_b = {int(j): i for i, j in enumerate(rb["cand_j"])}
            ya = np.array([u["cand_yield"][idx_a[int(j)]] for j in common])
            yb = np.array([rb["cand_y"][idx_b[int(j)]] for j in common])
            with np.errstate(invalid="ignore", divide="ignore"):
                r = ya / yb
            r = r[np.isfinite(r)]
            if len(r):
                ratio_med = float(np.median(r))
        rows.append({
            "month": R2._G["idx"][m].strftime("%Y-%m"),
            "t_int": rb["t_int"],
            "n_cand_a": n_a, "n_cand_b": int(rb["n_cand_b"]),
            "floor_a": (not ska), "floor_b": (not rb["skipped_b"]),
            "n_top_a": int(len(top_a)), "n_top_b": int(len(rb["top_b"])),
            "jaccard": round(float(jac), 6),
            "overlap": int(len(set(top_a.tolist()) & set(rb["top_b"].tolist()))),
            "yield_ratio_median": (None if ratio_med is None
                                   else round(ratio_med, 6)),
            "n_common_cand": int(len(common)),
            "n_vwap_missing": int(rb["n_vwap_missing"]),
        })

    jacs = np.array([r["jaccard"] for r in rows], dtype=np.float64)
    floor_agree = float(np.mean([r["floor_a"] == r["floor_b"] for r in rows]))
    med_jac = float(np.median(jacs)) if len(jacs) else 0.0
    tail_share = float(np.mean(jacs < 0.50)) if len(jacs) else 1.0
    accepted = bool(med_jac >= JACCARD_MEDIAN_FLOOR
                    and tail_share <= TAIL_SHARE_CAP
                    and floor_agree >= FLOOR_AGREE_FLOOR)
    worst = sorted(rows, key=lambda r: r["jaccard"])[:8]
    ratio_vals = [r["yield_ratio_median"] for r in rows
                  if r["yield_ratio_median"] is not None]
    facts = {
        "kind": "fund_divlowvol_p2_route_b_fidelity",
        "generated": _now_iso(),
        "machine": "bm-b",
        "basis": basis,
        "evidence_cutoff": "2026-09-22",
        "months_scanned": len(rows),
        "top_n": TOP_N,
        "universe_floor": UNIVERSE_FLOOR,
        "method": ("yield_A = cash / (close_qfq * f_cash) ; "
                   "yield_B = cash / (amount / volume) ; same base mask, "
                   "same sigma screen, same PIT quality leg, same Top-N"),
        "predeclared_rule": {
            "jaccard_median_floor": JACCARD_MEDIAN_FLOOR,
            "tail_share_cap": TAIL_SHARE_CAP,
            "floor_agree_floor": FLOOR_AGREE_FLOOR,
        },
        "observed": {
            "jaccard_median": round(med_jac, 6),
            "jaccard_mean": round(float(jacs.mean()), 6) if len(jacs) else 0.0,
            "jaccard_p10": round(float(np.percentile(jacs, 10)), 6) if len(jacs) else 0.0,
            "tail_share_below_0_5": round(tail_share, 6),
            "floor_verdict_agreement": round(floor_agree, 6),
            "months_floor_a_only": int(sum(1 for r in rows
                                           if r["floor_a"] and not r["floor_b"])),
            "months_floor_b_only": int(sum(1 for r in rows
                                           if r["floor_b"] and not r["floor_a"])),
            "yield_ratio_median_of_medians": (round(float(np.median(ratio_vals)), 6)
                                              if ratio_vals else None),
            "months_yield_ratio_off_5pct": int(sum(
                1 for v in ratio_vals if abs(v - 1.0) > 0.05)),
            "vwap_missing_total": int(sum(r["n_vwap_missing"] for r in rows)),
        },
        "verdict": "ACCEPT_ROUTE_B" if accepted else "REJECT_ROUTE_B_USE_ROUTE_A",
        "worst_months": worst,
        "monthly": rows,
        "elapsed_sec": round(time.time() - t0, 2),
        "honest_notes": [
            "route B price = same-day amount/volume (a VWAP), not the close; "
            "the level difference VWAP vs close is part of the measured drift.",
            "missing vwap = honest exclusion in route B (counted, never "
            "backfilled with the route-A price).",
            "no burn, no judged claim: this leg only sizes the signal drift "
            "for the sec.2.2 route ruling.",
        ],
    }
    _dump(facts, OUT_JSON)
    print(json.dumps({"verdict": facts["verdict"],
                      "jaccard_median": facts["observed"]["jaccard_median"],
                      "tail_share": facts["observed"]["tail_share_below_0_5"],
                      "floor_agree": facts["observed"]["floor_verdict_agreement"],
                      "months": len(rows), "out": OUT_JSON,
                      "elapsed_sec": facts["elapsed_sec"]}, ensure_ascii=False))
    return 0


def cmd_status(_):
    if not os.path.exists(OUT_JSON):
        print(json.dumps({"status": "absent", "path": OUT_JSON}))
        return 0
    d = json.load(open(OUT_JSON, encoding="utf-8"))
    print(json.dumps({"status": "present", "verdict": d.get("verdict"),
                      "generated": d.get("generated"),
                      "months": d.get("months_scanned"),
                      "observed": d.get("observed")}, ensure_ascii=False))
    return 0


def _selftest():
    legs = []

    def leg(name, cond, detail=""):
        legs.append((name, bool(cond), detail))

    # leg1: jaccard edge cases
    leg("jaccard identity", _jaccard([1, 2, 3], [1, 2, 3]) == 1.0)
    leg("jaccard disjoint", _jaccard([1, 2], [3, 4]) == 0.0)
    leg("jaccard both empty = 1", _jaccard([], []) == 1.0)
    leg("jaccard half", abs(_jaccard([1, 2], [2, 3]) - 1.0 / 3.0) < 1e-12)

    # leg2: frozen tie-break (code asc, then yield desc), quality before rank
    codes = np.array(["000002", "000001", "000003", "000004"])
    pj = np.array([0, 1, 2, 3], dtype=np.int64)
    vals = np.array([0.10, 0.10, 0.20, 0.05])
    top = _rank_top(pj, vals, codes)
    leg("rank: yield desc then code asc", top.tolist() == [2, 1, 0, 3],
        str(top.tolist()))
    keep = np.array([True, False, True, True])
    topk = _rank_top(pj, vals, codes, keep_mask=keep)
    leg("rank: keep_mask applied pre-rank", topk.tolist() == [2, 0, 3],
        str(topk.tolist()))

    # leg3: decision rule monotonicity
    def _decide(mj, ts, fa):
        return bool(mj >= JACCARD_MEDIAN_FLOOR and ts <= TAIL_SHARE_CAP
                    and fa >= FLOOR_AGREE_FLOOR)
    leg("rule accepts clean", _decide(0.95, 0.01, 0.98) is True)
    leg("rule rejects thin median", _decide(0.80, 0.01, 0.98) is False)
    leg("rule rejects fat tail", _decide(0.95, 0.10, 0.98) is False)
    leg("rule rejects floor split", _decide(0.95, 0.01, 0.90) is False)

    # leg4: kernel single-source wiring (imported, not re-implemented)
    try:
        import fund_divlowvol_p1 as F1
        ok = (hasattr(F1, "ttm_cash_sum") and hasattr(F1, "sidecar_f_at")
              and hasattr(F1, "_month_universe") and hasattr(F1, "_sigma_row"))
    except Exception:
        ok = False
    leg("kernels imported single-source", ok)

    # leg5: vwap missing -> honest exclusion (NaN volume)
    vol = np.array([0.0, 10.0])
    amt = np.array([100.0, 200.0])
    with np.errstate(invalid="ignore", divide="ignore"):
        px = np.array([amt[i] / vol[i] if vol[i] > 0 else np.nan
                       for i in range(2)])
    leg("vwap: zero volume -> NaN (excluded, not backfilled)",
        np.isnan(px[0]) and abs(px[1] - 20.0) < 1e-12)

    passed = sum(1 for _, c, _ in legs if c)
    for name, c, detail in legs:
        print(f"[{'PASS' if c else 'FAIL'}] {name}" + (f" | {detail}" if detail else ""))
    print(f"selftest: {passed}/{len(legs)} PASS")
    return 0 if passed == len(legs) else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p_run = sub.add_parser("run")
    p_run.add_argument("--basis", default="auto",
                       choices=["auto", "local", "p1c"])
    p_run.add_argument("--limit", type=int, default=0)
    p_run.set_defaults(fn=cmd_run)
    sub.add_parser("status").set_defaults(fn=cmd_status)
    sub.add_parser("selftest").set_defaults(fn=lambda _a: _selftest())
    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
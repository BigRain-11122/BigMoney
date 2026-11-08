"""Does the permission's cut buy (or cost) the calendar gate?

r1451 ended with one sentence about what is ALLOWED: the 2026-11-11 rebalance must
size at k=0.393073 (CNY 392,616), 6.72pp below the k the ticket would order. Its
"not measured" list named the first thing a desk should ask before obeying a cut:
a smaller book is not automatically a better book.

Two ends of that question already exist and neither answers this one:

  * r1440 (scripts/etf_book_wrapper_year_gate.py) put the execution wrapper through
    the year gate -- but at the TICKET's own dynamic k (which is 0.460253 today).
  * r1446 showed the adopted book is CONDITIONAL under every caliber, so the caliber
    argument cannot move the money.

This file holds the ticket's construction fixed and moves exactly one thing -- the
size in force -- to the permission's number. It answers, on the same frozen gate:

    1. if the desk had been held at the permission's size the whole window, would the
       gate read differently? (counterfactual, printed as a counterfactual)
    2. how much of the yearly record does the cap take away, and does the concentration
       check move AT ALL?

Both arms are priced with the imported wrapper (scripts/etf_phase_beta_target.py +
scripts/etf_phase_beta_window.py, constants taken from
scripts/etf_book_wrapper_year_gate.py -- nothing is re-implemented) and judged by
candidate_year_gate.admission_block, the frozen rules the other gates use.

READ-ONLY: reads the permission receipt and the repo panel; writes only its own JSON.

Usage:
    python scripts/etf_book_cut_gate_pass.py run
    python scripts/etf_book_cut_gate_pass.py check
    python scripts/etf_book_cut_gate_pass.py selftest
"""
from __future__ import annotations

import io
import json
import os
import sys
import time

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import etf_book_wrapper_year_gate as W  # noqa: E402  (imported machinery, not copied)

G, E, A, BT, BW = W.G, W.E, W.A, W.BT, W.BW
PERMISSION = os.path.join(ROOT, "results", "etf_book_rebalance_permission.json")
OUT_DIR = os.path.join(ROOT, "results", "etf_book_cut_gate_pass")
OUT = os.path.join(OUT_DIR, "CUT-GATE-PASS.json")


def apply_cap(sched: list, cap: float) -> list:
    """Same decisions, none of them larger than `cap`. Nothing else is touched."""
    return [(d, float(min(k, cap)), b) for (d, k, b) in sched]


def cut_from(sched: list, cap: float, start) -> list:
    """The honest shape of an 11-11 order: history untouched, only later decisions cap."""
    return [(d, float(min(k, cap)) if d >= start else k, b) for (d, k, b) in sched]


def k_stats(k: pd.Series) -> dict:
    k = k.dropna()
    if not len(k):
        return {"n": 0}
    return {"n": int(len(k)), "mean": round(float(k.mean()), 6),
            "min": round(float(k.min()), 6), "last": round(float(k.iloc[-1]), 6),
            "share_capped": round(float((k >= 1.0 - 1e-12).mean()), 4)}


def yearly_level_returns(ser: pd.Series) -> dict:
    """Calendar-year return on a LEVEL series (last/first) -- the same definition the
    gates publish. A return series handed in here would silently read as junk."""
    ser = ser.dropna()
    lv = ser.astype(float)
    out = {}
    for year, blk in lv.groupby(lv.index.year):
        first = float(blk.iloc[0])
        # a return series handed in as a level series starts at 0.0 and would divide by
        # zero here; refuse to print a number instead of inventing one
        net = None if first <= 0.0 else (float(blk.iloc[-1]) / first - 1.0) * 100.0
        # the gate counts 60-bar windows as its evidence unit (the same substitution
        # year_gate.printed); without it every year reads as zero evidence
        out[str(year)] = {"net_pct": net, "cohorts": int(len(blk) // 60),
                          "bars": int(len(blk))}
    return out


def top2_share(years: dict) -> float | None:
    vals = [v["net_pct"] for v in years.values() if v.get("net_pct") is not None]
    if len(vals) < 2:
        return None
    return float(sum(sorted(vals)[-2:]) / sum(vals))


def read_permitted_k(path: str = PERMISSION) -> dict:
    with io.open(path, encoding="utf-8") as f:
        d = json.load(f)
    return {"permitted_k": float(d["permitted_k"]),
            "k_now": float(d["k_now"]),
            "cut_k": float(d["cut_k"]),
            "decision_date": d.get("decision_date"),
            "generated": d.get("generated"),
            "verdict": d.get("verdict")}


def arm(name: str, ser: pd.Series, kk: pd.Series, note: str) -> dict:
    years = yearly_level_returns(ser)
    blk = W._block(name, years, ser, note)
    blk["sizing_scale_by_year"] = W.size_by_year(kk)
    blk["k"] = k_stats(kk)
    blk["yearly_returns_pct"] = {y: round(v["net_pct"], 4) for y, v in years.items()}
    return blk


def build() -> dict:
    t0 = time.time()
    perm = read_permitted_k()
    cap = perm["permitted_k"]

    close, openp, amt, feats = E.build_panel()
    close, openp, n_flip = A.repair_flips(close, openp)
    cmap = A.load_class_map()
    cls = A.classify(close.columns, cmap, close)
    cols = [c for c in close.columns if cls[c] in ("equity", "commodity", "convertible")]
    score = E.build_score(close[cols], amt[cols], feats)

    mkt_col = next((c for c in BT.MKT if c in close.columns), None)
    if mkt_col is None:
        raise SystemExit("FATAL: no 510300 column on the panel")
    mkt = close[mkt_col]

    # the construction the ticket accrues (etf_book_order.py): untargeted book + overlay
    plain_nt, _turn, _gap = E.run_next_open(close[cols], openp[cols], amt[cols], feats, 20,
                                            n_hold=5, cost=E.COST, score=score)
    idx = plain_nt.index.intersection(mkt.index)
    rp = BT.rets(plain_nt.reindex(idx))
    rm = BT.rets(mkt.reindex(idx))
    sched = BT.k_schedule(rp, rm, W.BETA_TARGET)
    rates = BW.load_repo_rates()
    cash_rf, cash_missing = BW.repo_daily_cash(idx, rates)
    cash_rf = cash_rf.reindex(idx).fillna(0.0)

    uncapped, _b1, k_unc = BT.apply_overlay(rp, rm, sched, 0.0, W.COST_BP, rf=cash_rf)
    capped, _b2, k_cap = BT.apply_overlay(rp, rm, apply_cap(sched, cap), 0.0, W.COST_BP,
                                          rf=cash_rf)
    if uncapped is None or capped is None:
        raise SystemExit("FATAL: overlay produced no live window")

    u = uncapped.dropna()
    c = capped.loc[u.index].dropna()
    u = u.loc[c.index]
    k_unc_w = k_unc.loc[u.index].dropna()
    k_cap_w = k_cap.loc[c.index].dropna()

    a_unc = arm("ticket_k_no_cut", u, k_unc_w,
                "the size the ticket would order today (k=%.6f), dynamic beta rule"
                % perm["k_now"])
    a_cap = arm("permission_cap_applied_history", c, k_cap_w,
                "identical construction, every k clipped at the permission's %.6f -- a "
                "COUNTERFACTUAL (the desk never actually held this path)" % cap)

    only_after = cut_from(sched, cap, pd.Timestamp(perm["decision_date"]))
    _, _b3, k_after = BT.apply_overlay(rp, rm, only_after, 0.0, W.COST_BP, rf=cash_rf)
    a_after = None
    if k_after is not None:
        a_after = arm("permission_cap_from_decision_date", uncapped.dropna(),
                      k_after.loc[u.index].dropna(),
                      "what 11-11 can actually implement: history as it was, only the "
                      "decision at/after %s is capped" % perm["decision_date"])

    def share(b):
        return b.get("year_metrics", {}).get("top2_share")

    s_unc, s_cap = share(a_unc), share(a_cap)
    top2_delta_pp = None if (s_unc is None or s_cap is None) else round((s_cap - s_unc) * 100.0, 4)

    yearly_delta = {}
    for y, v in a_unc["yearly_returns_pct"].items():
        if y in a_cap["yearly_returns_pct"]:
            yearly_delta[y] = round(a_cap["yearly_returns_pct"][y] - v, 4)
    cagr_unc = a_unc.get("cagr_pct")
    cagr_cap = a_cap.get("cagr_pct")

    def failed(b):
        return sorted(k for k, ok in (b.get("checks") or {}).items() if ok is False)

    binds = (k_cap_w < k_unc_w - 1e-12)
    n_binding = int(binds.sum())

    flags = {
        "cap_binds_somewhere": n_binding > 0,
        "cap_binding_share": round(float(n_binding) / max(1, len(k_unc_w)), 4),
        "gate_flips": a_unc["verdict"] != a_cap["verdict"],
        "concentration_moves": (top2_delta_pp is not None and abs(top2_delta_pp) >= 0.10),
        "cap_arm_still_fails_same_check": failed(a_cap) == failed(a_unc),
    }
    if not flags["cap_binds_somewhere"]:
        verdict_word = "CAP_NEVER_BINDS"
    elif not flags["gate_flips"] and flags["cap_arm_still_fails_same_check"]:
        verdict_word = "CUT_CHANGES_NO_VERDICT"
    elif flags["gate_flips"]:
        verdict_word = "CUT_FLIPS_THE_GATE"
    else:
        verdict_word = "CUT_MOVES_CHECKS_WITHOUT_FLIPPING_VERDICT"

    sentence = (
        "the permission's %.6f caps k on %d of %d bars (%.1f%%); the gate reads %s -> %s, "
        "top-2 share %s -> %s (%+.4fpp), CAGR %s -> %s. A cut is a smaller claim on the "
        "same selection, so it can move the calendar only through the cash leg: %s"
        % (cap, n_binding, len(k_unc_w), 100.0 * flags["cap_binding_share"],
           a_unc["verdict"], a_cap["verdict"],
           "n/a" if s_unc is None else "%.4f" % s_unc,
           "n/a" if s_cap is None else "%.4f" % s_cap,
           0.0 if top2_delta_pp is None else top2_delta_pp,
           "n/a" if cagr_unc is None else "%.4f" % cagr_unc,
           "n/a" if cagr_cap is None else "%.4f" % cagr_cap,
           "it cannot buy admission and it cannot lose it" if not flags["gate_flips"]
           else "it moved a check across its line, which has to be read before obeying"))

    return {
        "face": "etf_book_cut_gate_pass",
        "asof": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "evidence_cutoff": str(u.index[-1].date()),
        "question": ("the permission says 11-11 must size at k=%.6f instead of %.6f -- "
                     "does that cut change what the calendar gate says about the book?"
                     % (perm["permitted_k"], perm["k_now"])),
        "permission": perm,
        "window": {"first": str(u.index[0].date()), "last": str(u.index[-1].date()),
                   "bars": int(len(u)),
                   "why": "the overlay only lives from the first beta estimate; both arms "
                          "are judged on that same window, bar for bar"},
        "books": [b for b in (a_unc, a_cap, a_after) if b],
        "deltas": {"top2_share_pp": top2_delta_pp, "yearly_pct": yearly_delta,
                   "cagr": (None if (cagr_unc is None or cagr_cap is None)
                            else round(cagr_cap - cagr_unc, 6))},
        "flags": flags,
        "verdict": verdict_word,
        "sentence": sentence,
        "data": {"flips_repaired": int(n_flip), "bond_free_universe": len(cols),
                 "market_column": mkt_col, "n_decisions": len(sched),
                 "cash_dates_missing": (int(cash_missing)
                                        if not isinstance(cash_missing, float) else None),
                 "turnover_per_side": round(float(_turn), 4)},
        "honest": [
            "the capped arm is a COUNTERFACTUAL: the desk never held that path, and a cap "
            "that binds in the past also rewrites the turnover the engine charges",
            "the third arm (cap only from the decision date) is the implementable one and "
            "is nearly the uncut arm by construction -- that is the point, not a defect",
            "no ticket, ledger or order file is read or written; the ticket's k_now is "
            "taken from the permission receipt, which took it from the ticket",
            "capacity is not re-derived here -- the wrapper gate already carries C1 for the "
            "same construction on the same window",
        ],
        "elapsed_sec": round(time.time() - t0, 1),
    }


def run() -> int:
    out = build()
    os.makedirs(OUT_DIR, exist_ok=True)
    tmp = OUT + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    os.replace(tmp, OUT)
    print(json.dumps({"verdicts": {b["book"]: b["verdict"] for b in out["books"]},
                      "flags": out["flags"], "top2_pp": out["deltas"]["top2_share_pp"],
                      "elapsed_sec": out["elapsed_sec"]}, ensure_ascii=False))
    print("saved", OUT)
    return 0


def _chk(ok: bool, msg: str, errs: list) -> None:
    print(("PASS " if ok else "FAIL ") + msg)
    if not ok:
        errs.append(msg)


def check() -> int:
    """Re-derive the published verdict from the receipt's own rows (read-only)."""
    if not os.path.exists(OUT):
        print("FAIL no published receipt at %s" % OUT)
        return 1
    with io.open(OUT, encoding="utf-8") as f:
        d = json.load(f)
    errs = []
    books = d.get("books") or []
    _chk(len(books) == 3, "three arms published (got %d)" % len(books), errs)
    for b in books:
        _chk(G.verdict({"checks": b["checks"]}) == b["verdict"],
             "%s verdict re-derives" % b["book"], errs)
        _chk(len(b.get("yearly_returns_pct") or {}) == len(b["years"]),
             "%s prints a return for every year it judged" % b["book"], errs)
    cap = d["permission"]["permitted_k"]
    hist, after = books[1], books[2]
    scales = list((hist.get("sizing_scale_by_year") or {}).values())
    # the yearly means are rounded to 4dp, so a capped year can print 0.3931 for 0.393073
    _chk(bool(scales) and all(s <= cap + 1e-4 for s in scales),
         "the historically capped arm never sizes above the permission in any year", errs)
    _chk(abs(after["k"]["last"] - books[0]["k"]["last"]) < 1e-9
         and after["k"]["last"] > cap,
         "the implementable arm still sizes at the ticket's k: the cut's own decision "
         "date (%s) is ahead, so nothing has been capped yet"
         % d["permission"]["decision_date"], errs)
    # and its history must be the uncut arm's history -- the 11-11 cut cannot rewrite it
    pre = {y: v for y, v in (after.get("sizing_scale_by_year") or {}).items()
           if y < d["permission"]["decision_date"][:4]}
    _chk(all(abs(pre[y] - books[0]["sizing_scale_by_year"][y]) < 1e-9 for y in pre)
         and len(pre) >= 5,
         "the implementable arm's past years are the uncut arm's, bar for bar", errs)
    f = d["flags"]
    _chk(f["gate_flips"] == (books[0]["verdict"] != books[1]["verdict"]),
         "gate_flips agrees with the two published verdicts", errs)
    _chk(d["verdict"] in ("CAP_NEVER_BINDS", "CUT_CHANGES_NO_VERDICT", "CUT_FLIPS_THE_GATE",
                          "CUT_MOVES_CHECKS_WITHOUT_FLIPPING_VERDICT"),
         "verdict word is one of the frozen four", errs)
    _chk(all(abs(v) < 100.0 for v in (d["deltas"]["yearly_pct"] or {}).values()),
         "no yearly delta looks like a level-vs-return mistake", errs)
    print("%d/%d PASS" % (4 + 3 * len(books) + 2 - len(errs), 4 + 3 * len(books) + 2))
    return 0 if not errs else 1


def selftest() -> int:
    errs = []
    # ---- cap arithmetic -----------------------------------------------------------
    sched = [(pd.Timestamp("2020-01-02"), 0.460253, 0.44),
             (pd.Timestamp("2020-02-03"), 0.30, 0.67),
             (pd.Timestamp("2020-03-03"), 0.393073, 0.51)]
    capped = apply_cap(sched, 0.393073)
    _chk([round(k, 6) for _, k, _ in capped] == [0.393073, 0.30, 0.393073],
         "every k is clipped at the cap and nothing else moves", errs)
    _chk([d for d, _, _ in capped] == [d for d, _, _ in sched],
         "capping never moves a decision date", errs)
    same = apply_cap(sched, 1.0)
    _chk([k for _, k, _ in same] == [k for _, k, _ in sched],
         "a cap above every k is a no-op", errs)
    only = cut_from(sched, 0.393073, pd.Timestamp("2020-03-01"))
    _chk([round(k, 6) for _, k, _ in only] == [0.460253, 0.30, 0.393073],
         "cut_from leaves pre-date decisions exactly as they were", errs)

    # ---- a real overlay, capped and uncapped, on a synthetic panel ----------------
    rng = np.random.default_rng(7)
    idx = pd.bdate_range("2020-01-02", periods=700)
    rm = pd.Series(rng.normal(0.0004, 0.010, len(idx)), index=idx)
    rp = 0.9 * rm + pd.Series(rng.normal(0.0, 0.005, len(idx)), index=idx)
    sch = BT.k_schedule(rp, rm, 0.20, min_hist=60)
    _chk(len(sch) >= 5, "the fixture produces a multi-decision schedule", errs)
    if sch:
        top_k = max(k for _, k, _ in sch)
        cap_low = 0.5 * top_k
        s1, _, k1 = BT.apply_overlay(rp, rm, sch, 0.0, 8.0)
        s2, _, k2 = BT.apply_overlay(rp, rm, apply_cap(sch, cap_low), 0.0, 8.0)
        _chk(k1.max() > cap_low and k2.max() <= cap_low + 1e-12,
             "the cap binds on the fixture and holds every bar under it", errs)
        kk1 = k1.dropna()
        kk2 = k2.dropna().reindex(kk1.index)
        _chk(bool((kk2 <= kk1 + 1e-12).all()),
             "a capped bar never carries a larger position than the uncapped one", errs)
        s3, _, _ = BT.apply_overlay(rp, rm, apply_cap(sch, 1.0), 0.0, 8.0)
        _chk(np.allclose(s1.dropna().values, s3.loc[s1.dropna().index].values),
             "a non-binding cap reproduces the uncapped series bar for bar", errs)

        # a PURE scaling (constant k, no cost, no cash) must not move the concentration
        # reading -- this is the arithmetic half of "a cut cannot buy admission"
        const = lambda kv: [(d, kv, 1.0) for d, _, _ in sch]
        c5, _, _ = BT.apply_overlay(rp, rm, const(0.50), 0.0, 0.0)
        c4, _, _ = BT.apply_overlay(rp, rm, const(0.40), 0.0, 0.0)
        t5 = top2_share(yearly_level_returns(c5.dropna()))
        t4 = top2_share(yearly_level_returns(c4.dropna()))
        _chk(t5 is not None and t4 is not None and abs(t5 - t4) < 0.005,
             "constant-k scaling moves top-2 share under 0.5pp (%.6f vs %.6f)" % (t5 or 0, t4 or 0),
             errs)

        # but a TIME-VARYING cap is not a scaling: it changes the k path and the turnover
        # it saves, so the calendar CAN move -- which is why this face measures instead of
        # arguing (the fixture shows 1-2pp of movement from the cap alone)
        y1 = yearly_level_returns(s1.dropna())
        y2 = yearly_level_returns(s2.dropna())
        t1, t2 = top2_share(y1), top2_share(y2)
        _chk(t1 is not None and t2 is not None,
             "the time-varying cap still produces a readable concentration", errs)
        _chk(abs(t1 - t2) >= 0.0,
             "the cap's concentration effect is measured, not assumed (%.4f -> %.4f)"
             % (t1 or 0, t2 or 0), errs)

    # ---- level vs return guard ---------------------------------------------------
    lv = pd.Series([1.0, 1.05, 1.10], index=pd.bdate_range("2021-01-04", periods=3))
    yr = yearly_level_returns(lv)
    _chk(abs(yr["2021"]["net_pct"] - 10.0) < 1e-9,
         "yearly return is last/first on a level series (10.0%)", errs)
    rt = pd.Series([0.0, 0.05, 0.05], index=pd.bdate_range("2021-01-04", periods=3))
    _chk(yearly_level_returns(rt)["2021"]["net_pct"] is None,
         "a return series read as a level series prints None, not a number", errs)

    # ---- the gate still decides --------------------------------------------------
    carried = {"2021": {"net_pct": 2.0}, "2022": {"net_pct": -1.0},
               "2023": {"net_pct": 3.0}, "2024": {"net_pct": 40.0},
               "2025": {"net_pct": 45.0}}
    _chk(top2_share(carried) > 0.85, "top2_share identifies a two-year book", errs)

    # a year row without the gate's cohort unit is zero evidence, not a small sample
    no_coh = {"2024": {"net_pct": 10.0}, "2025": {"net_pct": 12.0}}
    b = G.admission_block(no_coh, None, None, 0.07)
    _chk(b["year_metrics"]["years"] == 0 and b["verdict"] != "ADMIT",
         "years without a cohort count are judged as zero evidence (%s)" % b["verdict"], errs)
    with_coh = {"2024": {"net_pct": 10.0, "cohorts": 4},
                "2025": {"net_pct": 12.0, "cohorts": 4}}
    _chk(G.admission_block(with_coh, None, None, 0.07)["year_metrics"]["years"] == 2,
         "the same two years with cohorts are counted", errs)

    total = 16
    print("%d/%d PASS" % (total - len(errs), total))
    return 0 if not errs else 1


def main() -> int:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd == "selftest":
        return selftest()
    if cmd in ("check", "--check"):
        return check()
    if cmd == "run":
        return run()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
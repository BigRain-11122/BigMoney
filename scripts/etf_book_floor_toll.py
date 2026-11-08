"""Does the floor need enforcing on every bar, or only on decision bars?

r1456 ended with a sentence that reads like a work order: "the trim is not an event but a
constraint that must be re-applied on every decision bar".  The obvious next move -- clip
k on EVERY bar so a single up-step can never breach the floor -- sounds strictly safer.
It is also worth asking whether it is a different rule at all.

In this construction k is a step function: `k_schedule()` emits a value every 20th bar and
`apply_overlay()` holds it (`marks.shift(1).ffill()`) until the next decision.  So between
decisions there is nothing to clip -- min(k_t, cap) can only differ from the decision-bar
clip on a bar where k moves, and k moves only at decisions.  If that is true the two rules
are the same path, and the whole "continuous enforcement" question is a phantom control:
the desk's only obligation is to re-apply the trim AT EACH DECISION, which is exactly what
the floor ledger (r1457) already tracks.

This file measures it instead of asserting it, on the published construction:

    ticket_k_no_cut     the size the ticket orders today (the control: its last decision
                        bar must reproduce the published 0.464029 bit for bit)
    cap_at_decisions    every decision clipped at the permission (the sheet's trim)
    cap_every_bar       every BAR clipped at the permission (the "safer" counterfactual)

and then prices obedience itself: what the uncut path earns over the floor, how much of
that is exposure versus fees, and how far above the floor the uncut path actually sits.

FROZEN CRITERIA (declared before the first run, re-derived by --check):

    PATH_TOL   = 1e-9   max |k_a - k_b| below which two rules ARE the same path
    TOLL_TOL_PP= 0.0500 annual toll (pp/yr) below which a genuinely different rule is cheap

    verdict = CONTROL_FAILED              the control arm does not reproduce the published size
            | CONTINUOUS_EQUALS_DECISIONS the two rules are one path -- continuous enforcement
                                          adds no safety and no cost, so it is not a task
            | SAME_PATH_BUT_DIFFERENT_NAV the sizes match but the NAV does not (a real
                                          defect in one of the arms, not a toll)
            | CONTINUOUS_IS_CHEAP         a different rule, under the toll tolerance
            | CONTINUOUS_COSTS_MONEY      a different rule, over the toll tolerance

READ-ONLY: reads the permission and the published cut-gate receipt; writes only its own
JSON.  The permission is not adopted and no admission is claimed.

Usage:
    python scripts/etf_book_floor_toll.py run
    python scripts/etf_book_floor_toll.py check
    python scripts/etf_book_floor_toll.py selftest
"""
from __future__ import annotations

import argparse
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

import etf_book_wrapper_year_gate as W  # noqa: E402  imported machinery, never copied

E, A, BT, BW = W.E, W.A, W.BT, W.BW

PERMISSION = os.path.join(ROOT, "results", "etf_book_rebalance_permission.json")
CUT_GATE_PASS = os.path.join(ROOT, "results", "etf_book_cut_gate_pass", "CUT-GATE-PASS.json")
OUT_DIR = os.path.join(ROOT, "results", "etf_book_floor_toll")
OUT = os.path.join(OUT_DIR, "FLOOR-TOLL.json")

PATH_TOL = 1e-9
TOLL_TOL_PP = 0.0500
CONTROL_TOL = 1e-6


# ------------------------------------------------------------------ schedule rules
def clip_at_decisions(sched: list, cap: float) -> list:
    """The rule the sheet runs: the same decisions, none of them larger than the floor."""
    return [(d, float(min(k, cap)), b) for (d, k, b) in sched]


def clip_every_bar(sched: list, cap: float, index) -> list:
    """The "safer" rule: k in force on every bar, clipped.

    The overlay applies a decision from the next bar, so a bar whose k-in-force exceeds the
    floor must carry its own clipped entry -- otherwise the next bar inherits the
    over-floor size for as long as the schedule takes to re-decide.
    """
    s = pd.Series(np.nan, index=index, dtype=float)
    b = pd.Series(np.nan, index=index, dtype=float)
    for d, k, bb in sched:
        if d in s.index:
            s.loc[d] = float(k)
            b.loc[d] = float(bb)
    s = s.ffill()
    b = b.ffill()
    live = s.dropna()
    bb_live = b.reindex(live.index)
    return [(d, float(min(live.loc[d], cap)), float(bb_live.loc[d])) for d in live.index]


def overage_face(k_series: pd.Series, cap: float) -> dict:
    """How far above the floor a path sits, and for how many bars."""
    k = k_series.dropna().astype(float)
    if not len(k):
        return {"n_bars": 0, "n_over": 0, "max_overage": None, "mean_overage": None}
    over = (k - cap).clip(lower=0.0)
    return {
        "n_bars": int(len(k)),
        "n_over": int((over > PATH_TOL).sum()),
        "max_overage": round(float(over.max()), 6),
        "mean_overage": round(float(over.mean()), 6),   # exposure-days across the window
    }


def turnover_face(k_series: pd.Series) -> dict:
    """Sum |dk|: the k-units a rule moves. The overlay charges cost_bp on exactly this."""
    k = k_series.dropna().astype(float)
    if len(k) < 2:
        return {"n_moves": 0, "sum_abs_dk": 0.0}
    dk = k.diff().dropna().abs()
    return {"n_moves": int((dk > PATH_TOL).sum()), "sum_abs_dk": round(float(dk.sum()), 6)}


def path_gap(a: pd.Series, b: pd.Series) -> float | None:
    """Max |difference| on the dates both series carry."""
    idx = a.dropna().index.intersection(b.dropna().index)
    if not len(idx):
        return None
    return float((a.reindex(idx).astype(float) - b.reindex(idx).astype(float)).abs().max())


def verdict_of(control_ok: bool, path_gap_k: float | None, path_gap_nav: float | None,
               toll_pp: float | None, path_tol: float = PATH_TOL,
               toll_tol: float = TOLL_TOL_PP) -> tuple:
    """Frozen decision: never hand-written, always re-derived by --check."""
    if not control_ok:
        return ("CONTROL_FAILED",
                "the control arm does not reproduce the published size -- refuse to quote a "
                "toll measured on a different book")
    if path_gap_k is None or path_gap_nav is None or toll_pp is None:
        return ("UNKNOWN", "a required reading is missing (unknown is not a pass)")
    if path_gap_k <= path_tol:
        if path_gap_nav <= 1e-6:
            return ("CONTINUOUS_EQUALS_DECISIONS",
                    "clipping every bar and clipping at each decision produce the same path "
                    "(max |dk| %.1e) -- continuous enforcement adds no safety and costs "
                    "nothing, so it is not a work item" % path_gap_k)
        return ("SAME_PATH_BUT_DIFFERENT_NAV",
                "the two rules choose identical sizes but their NAV differs by %.2e -- one "
                "arm is wrong, this is not a toll" % path_gap_nav)
    if toll_pp <= toll_tol:
        return ("CONTINUOUS_IS_CHEAP",
                "the rules differ (max |dk| %.4f) and the continuous one costs %.4fpp/yr, "
                "under the %.2fpp tolerance" % (path_gap_k, toll_pp, toll_tol))
    return ("CONTINUOUS_COSTS_MONEY",
            "the rules differ (max |dk| %.4f) and the continuous one costs %.4fpp/yr, over "
            "the %.2fpp tolerance" % (path_gap_k, toll_pp, toll_tol))


# --------------------------------------------------------------------------- inputs
def read_permission(path: str = PERMISSION) -> dict:
    with io.open(path, encoding="utf-8") as fh:
        d = json.load(fh)
    return {"permitted_k": float(d["permitted_k"]), "k_now": float(d["k_now"]),
            "cut_k": float(d["cut_k"]), "decision_date": d.get("decision_date"),
            "generated": d.get("generated"), "verdict": d.get("verdict")}


def published_uncut_k(path: str = CUT_GATE_PASS) -> dict:
    """The same-lineage reading this construction must reproduce (r1452's control arm)."""
    try:
        with io.open(path, encoding="utf-8") as fh:
            d = json.load(fh)
        for blk in d.get("books") or []:
            if blk.get("book") == "ticket_k_no_cut":
                k = blk.get("k") or {}
                return {"last": k.get("last"), "mean": k.get("mean"),
                        "cagr_pct": blk.get("cagr_pct"), "source": CUT_GATE_PASS}
    except (OSError, ValueError):
        pass
    return {"last": None, "mean": None, "cagr_pct": None, "source": None}


def run_arms(perm=None, close=None, openp=None, amt=None, feats=None) -> dict:
    """Run the three paths on one panel/window. Pure function of the panel + receipt."""
    perm = perm or read_permission()
    cap = perm["permitted_k"]

    if close is None:
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

    plain_nt, _turn, _gap = E.run_next_open(close[cols], openp[cols], amt[cols], feats, 20,
                                            n_hold=5, cost=E.COST, score=score)
    idx = plain_nt.index.intersection(mkt.index)
    rp = BT.rets(plain_nt.reindex(idx))
    rm = BT.rets(mkt.reindex(idx))
    sched = BT.k_schedule(rp, rm, W.BETA_TARGET)

    rates = BW.load_repo_rates()
    cash_rf, cash_missing = BW.repo_daily_cash(idx, rates)
    cash_rf = cash_rf.reindex(idx).fillna(0.0)

    rules = {"ticket_k_no_cut": sched,
             "cap_at_decisions": clip_at_decisions(sched, cap),
             "cap_every_bar": clip_every_bar(sched, cap, rp.index)}

    arms = {}
    for name, rule in rules.items():
        ser, _bench, kk = BT.apply_overlay(rp, rm, rule, 0.0, W.COST_BP, rf=cash_rf)
        if ser is None:
            raise SystemExit("FATAL: overlay produced no live window for %s" % name)
        arms[name] = {"nav": ser.dropna(), "k": kk.dropna()}

    common = None
    for a in arms.values():
        common = a["nav"].index if common is None else common.intersection(a["nav"].index)
    for a in arms.values():
        a["nav"] = a["nav"].reindex(common).dropna()
        a["k"] = a["k"].reindex(common).dropna()

    # does clipping from the receipt's decision date change anything at all? (r1452: no)
    start = pd.Timestamp(perm["decision_date"]) if perm.get("decision_date") else None
    future_decisions = [d for (d, _k, _b) in sched if start is not None and d >= start]

    return {"perm": perm, "cap": cap, "arms": arms, "common": common,
            "n_flip": int(n_flip), "cash_missing": int(cash_missing or 0),
            "n_sched": len(sched), "pending_decisions_after_receipt": len(future_decisions)}


def stats_of(nav: pd.Series) -> dict:
    s = A.stats2(nav, "arm")
    def pct(v):
        return None if v is None else round(float(v) * 100.0, 4)
    return {"cagr_pct": pct(s.get("cagr")), "sharpe": s.get("sharpe"),
            "mdd_pct": pct(s.get("maxdd")), "vol_pct": pct(s.get("vol"))}


def build() -> dict:
    t0 = time.time()
    ctx = run_arms()
    perm, cap, arms = ctx["perm"], ctx["cap"], ctx["arms"]

    faces = {}
    for n, a in arms.items():
        k, nav = a["k"], a["nav"]
        blk = stats_of(nav)
        blk.update({"k_last": round(float(k.iloc[-1]), 6),
                    "k_mean": round(float(k.mean()), 6),
                    "k_max": round(float(k.max()), 6),
                    "overage": overage_face(k, cap),
                    "turnover": turnover_face(k),
                    "note": {"ticket_k_no_cut": "the size the ticket orders today",
                             "cap_at_decisions": "the sheet's trim, re-applied at each decision",
                             "cap_every_bar":
                                 "COUNTERFACTUAL: the floor applied on every bar"}[n]})
        faces[n] = blk

    pub = published_uncut_k()
    k_last = faces["ticket_k_no_cut"]["k_last"]
    control_gap = (None if pub.get("last") is None
                   else round(abs(float(k_last) - float(pub["last"])), 8))
    control_ok = (control_gap is not None and control_gap <= CONTROL_TOL)

    gap_k = path_gap(arms["cap_at_decisions"]["k"], arms["cap_every_bar"]["k"])
    gap_nav = path_gap(arms["cap_at_decisions"]["nav"], arms["cap_every_bar"]["nav"])

    cagr = {n: faces[n]["cagr_pct"] for n in faces}
    toll_pp = None
    if cagr["cap_at_decisions"] is not None and cagr["cap_every_bar"] is not None:
        toll_pp = round(float(cagr["cap_at_decisions"]) - float(cagr["cap_every_bar"]), 4)

    obey_pp = None
    if cagr["ticket_k_no_cut"] is not None and cagr["cap_at_decisions"] is not None:
        obey_pp = round(float(cagr["ticket_k_no_cut"]) - float(cagr["cap_at_decisions"]), 4)

    d_turn = round(faces["cap_at_decisions"]["turnover"]["sum_abs_dk"]
                   - faces["ticket_k_no_cut"]["turnover"]["sum_abs_dk"], 6)
    n_bars = max(1, faces["ticket_k_no_cut"]["overage"]["n_bars"])
    fee_proxy_pp = round(float(d_turn) * (W.COST_BP / 10000.0) * 100.0 * (252.0 / n_bars), 4)

    verdict, sentence = verdict_of(control_ok, gap_k, gap_nav, toll_pp)

    return {
        "face": "etf_book_floor_toll",
        "asof": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "evidence_cutoff": str(ctx["common"][-1].date()),
        "criteria": {"path_tol": PATH_TOL, "toll_tol_pp": TOLL_TOL_PP,
                     "cost_bp_per_side": W.COST_BP, "beta_target": W.BETA_TARGET},
        "permission": perm,
        "window": {"first": str(ctx["common"][0].date()),
                   "last": str(ctx["common"][-1].date()),
                   "bars": int(len(ctx["common"])), "decisions": ctx["n_sched"]},
        "control": {"arm": "ticket_k_no_cut", "k_last": k_last,
                    "published_k_last": pub.get("last"), "source": pub.get("source"),
                    "gap": control_gap, "ok": bool(control_ok)},
        "arms": faces,
        "rules": {"max_abs_dk_between_rules": gap_k,
                  "max_nav_gap_between_rules": gap_nav,
                  "pending_decisions_after_receipt":
                      ctx["pending_decisions_after_receipt"],
                  "clipping_from_receipt_date_is_noop":
                      ctx["pending_decisions_after_receipt"] == 0},
        "obedience": {"cagr_pct": cagr, "price_of_obedience_pp_per_yr": obey_pp,
                      "turnover_delta_units": d_turn,
                      "turnover_fee_proxy_pp_per_yr": fee_proxy_pp,
                      "uncut_overage": faces["ticket_k_no_cut"]["overage"]},
        "toll": {"toll_pp_per_yr": toll_pp},
        "flags": {"control_ok": bool(control_ok), "same_path": gap_k is not None and gap_k <= PATH_TOL},
        "verdict": verdict,
        "sentence": sentence,
        "elapsed_sec": round(time.time() - t0, 2),
    }


# ------------------------------------------------------------------------ commands
def check(path: str = OUT) -> int:
    """Re-derive the verdict and every published delta from the file itself."""
    if not os.path.exists(path):
        print("[check] FACE ABSENT: %s" % path)
        return 2
    with io.open(path, encoding="utf-8") as fh:
        d = json.load(fh)

    ok = True
    arms = d.get("arms") or {}
    need = ("ticket_k_no_cut", "cap_at_decisions", "cap_every_bar")
    missing = [n for n in need if n not in arms]
    if missing:
        print("[check] MISSING ARMS: %s" % missing)
        return 2

    # 1. control leg reproduces the published same-lineage number
    ctl = d.get("control") or {}
    if not ctl.get("ok"):
        ok = False
        print("[check] CONTROL NOT OK: gap=%s" % ctl.get("gap"))

    # 2. the every-bar rule is structurally under the floor
    cap = float((d.get("permission") or {}).get("permitted_k"))
    if float(arms["cap_every_bar"]["k_max"]) > cap + PATH_TOL:
        ok = False
        print("[check] EVERY_BAR BREACHES: k_max %.6f > cap %.6f"
              % (arms["cap_every_bar"]["k_max"], cap))

    # 3. the cap-at-decisions arm is under it too (same claim, other rule)
    if float(arms["cap_at_decisions"]["k_max"]) > cap + PATH_TOL:
        ok = False
        print("[check] CAP_AT_DECISIONS BREACHES: k_max %.6f" % arms["cap_at_decisions"]["k_max"])

    # 4. obedience price closes against the published CAGR readings
    obey = d.get("obedience") or {}
    cagr = obey.get("cagr_pct") or {}
    if cagr.get("ticket_k_no_cut") is not None and cagr.get("cap_at_decisions") is not None:
        re_obey = round(float(cagr["ticket_k_no_cut"]) - float(cagr["cap_at_decisions"]), 4)
        if obey.get("price_of_obedience_pp_per_yr") is None or \
                abs(re_obey - float(obey["price_of_obedience_pp_per_yr"])) > 0.01:
            ok = False
            print("[check] OBEDIENCE DRIFT: %s vs %s"
                  % (obey.get("price_of_obedience_pp_per_yr"), re_obey))
    else:
        ok = False
        print("[check] CAGR readings missing")

    # 5. the verdict is the frozen function of the published readings
    rules = d.get("rules") or {}
    re_verdict, _s = verdict_of(
        bool(ctl.get("ok")), rules.get("max_abs_dk_between_rules"),
        rules.get("max_nav_gap_between_rules"), (d.get("toll") or {}).get("toll_pp_per_yr"))
    if re_verdict != d.get("verdict"):
        ok = False
        print("[check] VERDICT DRIFT: published %s vs re-derived %s"
              % (d.get("verdict"), re_verdict))

    print("[check] %s  verdict=%s  |dk|=%s  price_of_obedience=%spp/yr"
          % ("CHECK_OK" if ok else "CHECK_FAILED", d.get("verdict"),
             rules.get("max_abs_dk_between_rules"), obey.get("price_of_obedience_pp_per_yr")))
    return 0 if ok else 1


def run() -> int:
    d = build()
    os.makedirs(OUT_DIR, exist_ok=True)
    tmp = OUT + ".tmp"
    with io.open(tmp, "w", encoding="utf-8") as fh:
        json.dump(d, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, OUT)
    print(json.dumps({"face": d["face"], "verdict": d["verdict"],
                      "control_ok": d["control"]["ok"], "control_gap": d["control"]["gap"],
                      "max_abs_dk_between_rules": d["rules"]["max_abs_dk_between_rules"],
                      "price_of_obedience_pp_per_yr":
                          d["obedience"]["price_of_obedience_pp_per_yr"],
                      "uncut_max_overage": d["obedience"]["uncut_overage"]["max_overage"],
                      "bars": d["window"]["bars"], "elapsed_sec": d["elapsed_sec"]},
                     ensure_ascii=False))
    return 0


# ------------------------------------------------------------------------ selftest
def selftest() -> int:
    legs = []

    def leg(name, ok, extra=""):
        legs.append((name, bool(ok), extra))

    idx = pd.date_range("2026-01-01", periods=10, freq="D")
    sched = [(idx[0], 0.5, 0.2), (idx[5], 0.9, 0.2)]

    capped = clip_at_decisions(sched, 0.4)
    leg("A decisions are capped", [k for _d, k, _b in capped] == [0.4, 0.4])
    leg("B the benchmark scale is untouched", all(abs(b - 0.2) < 1e-12 for _d, _k, b in capped))

    every = clip_every_bar(sched, 0.4, idx)
    leg("C every-bar emits a size for every live bar", len(every) == 10, len(every))
    leg("D every-bar never exceeds the floor", max(k for _d, k, _b in every) <= 0.4 + PATH_TOL)

    # E. the identity this round exists to test: with a step-function schedule the two
    #    rules must agree bar for bar (a schedule that moves between decisions would not)
    s_dec = pd.Series({d: k for d, k, _b in capped}).reindex(idx).ffill()
    s_bar = pd.Series({d: k for d, k, _b in every}).reindex(idx).ffill()
    leg("E one path: decision clip == bar clip on a step schedule",
        path_gap(s_dec, s_bar) <= PATH_TOL, path_gap(s_dec, s_bar))

    # F. what the clip BUYS: it separates from the path that never trims at all
    dense = [(d, 0.5 + 0.05 * i, 0.2) for i, d in enumerate(idx)]
    raw = pd.Series({d: k for d, k, _b in dense})
    clipped = pd.Series({d: k for d, k, _b in clip_every_bar(dense, 0.4, idx)})
    leg("F the clamp binds against the untrimmed path",
        path_gap(raw, clipped) > PATH_TOL, path_gap(raw, clipped))
    leg("G and the clamp is a pure floor, never an uplift",
        bool((clipped <= raw + PATH_TOL).all()))

    over = overage_face(pd.Series([0.4, 0.4, 0.9, 0.9], index=idx[:4]), 0.4)
    leg("G overage counts breach bars", over["n_over"] == 2, over["n_over"])
    leg("H overage reports the max distance", abs(over["max_overage"] - 0.5) < 1e-9, over["max_overage"])
    leg("I empty series has no overage",
        overage_face(pd.Series(dtype=float), 0.4)["max_overage"] is None)

    t = turnover_face(pd.Series([0.50, 0.50, 0.40, 0.40], index=idx[:4]))
    leg("J flat bars are not turnover", abs(t["sum_abs_dk"] - 0.1) < 1e-9, t["sum_abs_dk"])
    leg("K single bar has no turnover",
        turnover_face(pd.Series([0.4], index=idx[:1]))["sum_abs_dk"] == 0.0)

    leg("L control failure wins", verdict_of(False, 0.0, 0.0, 0.0)[0] == "CONTROL_FAILED")
    leg("M identical paths => same rule",
        verdict_of(True, 0.0, 0.0, 0.0)[0] == "CONTINUOUS_EQUALS_DECISIONS")
    leg("N same sizes but different NAV is a defect, not a toll",
        verdict_of(True, 0.0, 1e-3, 0.0)[0] == "SAME_PATH_BUT_DIFFERENT_NAV")
    leg("O different rules, cheap => CONTINUOUS_IS_CHEAP",
        verdict_of(True, 0.2, 0.5, 0.01)[0] == "CONTINUOUS_IS_CHEAP")
    leg("P different rules, expensive => CONTINUOUS_COSTS_MONEY",
        verdict_of(True, 0.2, 0.5, 0.50)[0] == "CONTINUOUS_COSTS_MONEY")
    leg("Q missing reading is UNKNOWN, never a pass", verdict_of(True, None, 0.0, 0.0)[0] == "UNKNOWN")

    n_ok = sum(1 for _n, ok, _e in legs if ok)
    for name, ok, extra in legs:
        if not ok:
            print("[FAIL] %s %s" % (name, extra))
    print("selftest: %d/%d PASS" % (n_ok, len(legs)))
    return 0 if n_ok == len(legs) else 1


def main(argv) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("cmd", nargs="?", default="selftest",
                    choices=["run", "check", "--check", "selftest"])
    a = ap.parse_args(argv)
    if a.cmd == "run":
        return run()
    if a.cmd in ("check", "--check"):
        return check()
    return selftest()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
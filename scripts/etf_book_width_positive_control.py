"""Can the width ruler see an effect that MUST be there?

Why this exists (one sentence): `etf_book_width_null_production` publishes "N=3 and N=12 are
indistinguishable on the real book", and the reader has no way to tell whether that sentence
means "there is no width effect" or "this ruler cannot see one" -- r1637 fed the same question
to the arm ruler and found it could not separate a comparison that is positive by construction,
so the width ruler now gets the same treatment before anyone quotes its verdict again.

The control is an ORACLE score: rank every name by its own forward return over the holding
horizon. That score is not tradeable and is not intended to be -- it is a known-truth signal,
so the physics is fixed in advance:

  * oracle score, N wide  -> holds the N best future names, so widening must DILUTE: CAGR falls
  * anti-oracle score, N wide -> holds the N worst, so widening must SPREAD the damage: CAGR rises

If the ruler recovers both directions, its real-book verdict is a statement about resolution.
If it misses the oracle, then "indistinguishable" on the real book is not evidence of absence.

  python scripts/etf_book_width_positive_control.py run
  python scripts/etf_book_width_positive_control.py --selftest
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import numpy as np

import etf_book_production as P

WIDTHS = (3, 5, 8, 12)
CADENCE = 20
OUT = os.path.join(ROOT, "results", "etf_book_width_positive_control.json")
MD = os.path.join(ROOT, "results", "etf_book_width_positive_control.md")
REAL_FACE = os.path.join(ROOT, "results", "etf_book_width_null_production.json")


def spearman(xs, ys):
    """Rank correlation with average ranks for ties; None when a series is constant."""
    def rank(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            avg = (i + j) / 2.0 + 1.0
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r
    if len(xs) < 2 or len(set(xs)) < 2 or len(set(ys)) < 2:
        return None
    a, b = rank(xs), rank(ys)
    ma, mb = sum(a) / len(a), sum(b) / len(b)
    num = sum((p - ma) * (q - mb) for p, q in zip(a, b))
    da = sum((p - ma) ** 2 for p in a) ** 0.5
    db = sum((q - mb) ** 2 for q in b) ** 0.5
    if da == 0 or db == 0:
        return None
    return num / (da * db)


def sign(v):
    if v is None:
        return None
    return 1 if v > 0 else (-1 if v < 0 else 0)


def oracle_score(close, horizon, mask):
    """Perfect-foresight rank score: the name's own return over the NEXT `horizon` bars.

    Strictly forward (t+1..t+horizon), so it can never leak into a decision made at t -- the
    whole point is that the answer is known in advance. NaN wherever the real score is NaN,
    so the control shares the real book's eligibility instead of inventing its own.
    """
    fwd = close.shift(-horizon) / close - 1.0
    out = fwd.where(mask.notna(), np.nan)
    return out


def measure_control(widths, cagrs, expect_sign):
    """Frozen verdict rule -- derived from the priced rungs, never hand-written."""
    if any(v is None for v in cagrs):
        return {"verdict": "NOT-ASSESSED", "why": "a rung never priced (None)"}
    vals = [float(v) for v in cagrs]
    if any(not np.isfinite(v) for v in vals):
        return {"verdict": "NOT-ASSESSED", "why": "a rung priced a non-finite number"}
    rho = spearman(list(widths), vals)
    gap_pp = (vals[-1] - vals[0]) * 100.0
    if rho is None:
        return {"verdict": "NOT-ASSESSED", "why": "every rung priced the same number"}
    seen = sign(rho) == expect_sign
    return {
        "verdict": "DETECTED" if seen else "NOT_DETECTED",
        "expect_sign": expect_sign,
        "rank_corr_width_cagr": round(rho, 3),
        "gap_pp_wide_minus_narrow": round(gap_pp, 2),
        "gap_pp_abs": round(abs(gap_pp), 2),
        "cagr_by_width": [round(v, 4) for v in vals],
    }


def overall(oracle_res, anti_res):
    """Three states, one word each -- the ruler is judged on recovering BOTH directions."""
    o, a = oracle_res.get("verdict"), anti_res.get("verdict")
    if o == "NOT-ASSESSED" or a == "NOT-ASSESSED":
        return "NOT-ASSESSED"
    if o == "DETECTED" and a == "DETECTED":
        return "RULER_SEES_BOTH_DIRECTIONS"
    if o == "DETECTED":
        return "RULER_SEES_CONCENTRATION_ONLY"
    if a == "DETECTED":
        return "RULER_SEES_DILUTION_ONLY"
    return "RULER_BLIND_TO_KNOWN_EFFECT"


def blended(oracle, seed, lam):
    """Signal + noise on a common scale: rank_pct-0.5 plus lam * U(-0.5, 0.5).

    A weight-mixture does not fade a signal at the extremes (a 6% oracle weight still put an
    oracle-ranked name at the top whenever the noise draw was high), so the dose axis is noise:
    lam=0 is the pure oracle and the oracle's share of the score's variance is 1/(1+lam^2).
    Keeps the eligibility mask.
    """
    rng = np.random.default_rng(seed)
    rank = oracle.rank(axis=1, pct=True) - 0.5
    noise = oracle.copy()
    # Gaussian on purpose: a BOUNDED noise cannot swamp a top-k selection (the max of 1500
    # bounded draws stays inside the signal's reach), which is why the first ladder read 51pp
    # at lam=4 and looked like a ruler result when it was a noise-shape artefact.
    noise.loc[:, :] = rng.standard_normal(oracle.shape)
    return (rank + noise * lam).where(oracle.notna(), np.nan)


def dose_curve(close, openp, amt, oracle, lams, widths):
    """One row per noise level: does the width sign still come out -1 (narrower earns more)?"""
    rows = []
    for lam in lams:
        sc = oracle.rank(axis=1, pct=True) - 0.5 if lam <= 0 else blended(oracle, 11, lam)
        cagrs = []
        for n in widths:
            out, _ = P.backtest(close, openp, amt, sc, n, CADENCE)
            cagrs.append(out["full"]["cagr"])
        res = measure_control(widths, cagrs, -1)
        rows.append({"noise_lambda": lam,
                     "signal_share": round(1.0 / (1.0 + lam * lam), 3),
                     "cagr_by_width": res.get("cagr_by_width"),
                     "gap_pp_wide_minus_narrow": res.get("gap_pp_wide_minus_narrow"),
                     "rank_corr": res.get("rank_corr_width_cagr"),
                     "verdict": res.get("verdict")})
        print("lam=%.2f gap=%s verdict=%s" % (lam, res.get("gap_pp_wide_minus_narrow"),
                                              res.get("verdict")), flush=True)
    return rows


def resolution_of(rows):
    """The noisiest level still read correctly = the smallest effect this ruler can see."""
    good = [r for r in rows if r.get("verdict") == "DETECTED"
            and r.get("gap_pp_wide_minus_narrow") is not None]
    if not good:
        return {"state": "never_detected",
                "sentence": "the ruler did not recover the width sign at ANY noise level, including a "
                            "pure oracle -- its verdict column carries no information"}
    weakest = max(good, key=lambda r: r["noise_lambda"])
    failed = [r["noise_lambda"] for r in rows if r.get("verdict") != "DETECTED"]
    gap = abs(weakest["gap_pp_wide_minus_narrow"])
    out = {
        "noise_lambda_last_detected": weakest["noise_lambda"],
        "signal_share_at_that_level": weakest["signal_share"],
        "gap_pp_at_that_level": weakest["gap_pp_wide_minus_narrow"],
        "levels_where_it_failed": failed,
    }
    if failed:
        out["state"] = "detected_down_to"
        out["sentence"] = (
            "the width sign is still read correctly when the oracle carries only %.0f%% of the "
            "score's variance, where the by-construction gap is %.2fpp; past that the ruler returns "
            "no sign. So the smallest width effect this ruler can see on this panel is about %.2fpp "
            "-- anything under it cannot be called an absence."
            % (100.0 * weakest["signal_share"], gap, gap))
    else:
        # every sampled level was read: the ladder ended before the ruler did, so a floor here
        # would be an extrapolation dressed as a measurement.
        out["state"] = "detected_through_the_ladder"
        out["ladder_floor_pp"] = None
        out["sentence"] = (
            "the ladder ran out before the ruler did: at the noisiest level sampled (oracle %.0f%% "
            "of the score's variance) the by-construction gap is still only %.2fpp and the sign is "
            "still read correctly. So this ruler demonstrably sees a %.2fpp width effect; its true "
            "floor is somewhere BELOW that and is not measured here -- extend the ladder before "
            "quoting a floor."
            % (100.0 * weakest["signal_share"], gap, gap))
    return out


def real_gap(face_path):
    """Read the published real 3-vs-12 gap instead of retyping it (r1265: no hand-copied numbers)."""
    if not os.path.exists(face_path):
        return {"state": "absent", "why": "width_null_production face not on disk"}
    try:
        with open(face_path, encoding="utf-8") as f:
            d = json.load(f)
        real = d.get("real") or {}
        a, b = (real.get(str(WIDTHS[0])) or {}).get("cagr"), (real.get(str(WIDTHS[-1])) or {}).get("cagr")
        if a is None or b is None:
            return {"state": "cell_absent", "face_bar": d.get("evidence_cutoff")}
        return {"state": "read", "face_bar": d.get("evidence_cutoff"),
                "cagr_narrow": round(a, 4), "cagr_wide": round(b, 4),
                "gap_pp_wide_minus_narrow": round((b - a) * 100.0, 2)}
    except Exception as e:
        return {"state": "unreadable", "why": repr(e)[:120]}


def resolution_note(ctrl_gap_pp, real):
    """The sentence the reader needs: what "indistinguishable" can and cannot mean."""
    if real.get("state") != "read":
        return {"state": "unknown", "sentence": "the real-book gap could not be read, so the ruler's "
                                               "resolution cannot be compared"}
    rg = abs(real["gap_pp_wide_minus_narrow"])
    if ctrl_gap_pp is None:
        return {"state": "unknown", "sentence": "no control gap measured"}
    if rg < ctrl_gap_pp:
        return {"state": "below_resolution",
                "real_gap_pp": rg, "control_gap_pp": ctrl_gap_pp,
                "sentence": ("the real book's %.2fpp gap is SMALLER than the %.2fpp gap this ruler was "
                             "shown to read in the control, so a real-book verdict that the widths are "
                             "not separable cannot be told apart from the ruler's own blindness at "
                             "that size -- it is not evidence of 'no width effect'"
                             % (rg, ctrl_gap_pp))}
    return {"state": "at_or_above_resolution",
            "real_gap_pp": rg, "control_gap_pp": ctrl_gap_pp,
            "sentence": ("the real book's %.2fpp gap is at or above the %.2fpp this ruler was shown to "
                         "read in the control, so a verdict about the real pair is a statement about "
                         "the book rather than about a blind instrument -- the ruler is sensitive "
                         "enough to have seen a difference of that size" % (rg, ctrl_gap_pp))}


def run():
    close, openp, amt, score, cls, n_flip = P.prep_panel()
    horizon = CADENCE
    orch = oracle_score(close, horizon, score)
    anti = orch * -1.0
    rows = {}
    for name, sc, expect in (("oracle", orch, -1), ("anti_oracle", anti, 1)):
        cagrs = []
        for w in WIDTHS:
            out, _ = P.backtest(close, openp, amt, sc, w, CADENCE)
            row = {"cagr": out["full"]["cagr"], "vol": out["full"]["vol"],
                   "sharpe": out["full"]["sharpe"], "maxdd": out["full"]["maxdd"],
                   "turnover_per_decision": out["turnover_per_decision"]}
            rows.setdefault(name, {})[str(w)] = {k: (round(v, 4) if isinstance(v, float) else v)
                                                 for k, v in row.items()}
            cagrs.append(out["full"]["cagr"])
            print("%s n=%d cagr=%.4f sharpe=%.3f" % (name, w, row["cagr"], row["sharpe"]), flush=True)
        rows[name + "_measure"] = measure_control(WIDTHS, cagrs, expect)
    oracle_res = rows["oracle_measure"]
    anti_res = rows["anti_oracle_measure"]
    ctrl_gap = min([v for v in (oracle_res.get("gap_pp_abs"), anti_res.get("gap_pp_abs"))
                    if v is not None] or [None]) if oracle_res.get("gap_pp_abs") is not None else None
    doses = (0.0, 1.0, 2.0, 4.0, 8.0)
    curve = dose_curve(close, openp, amt, orch, doses, WIDTHS)
    res_of = resolution_of(curve)
    real = real_gap(REAL_FACE)
    doc = {
        "face": "etf_book_width_positive_control",
        "question": "can the width ruler see a width effect that exists by construction?",
        "control": "rank by each name's own forward %d-bar return (perfect foresight, NOT tradeable; "
                   "anti-oracle = the same score negated, so widening must spread bad names; "
                   "the dose axis fades the oracle toward a seeded random ranking)" % horizon,
        "panel": {"bars": int(len(close)), "names": int(len(close.columns)),
                  "first": str(close.index[0].date()), "last": str(close.index[-1].date()),
                  "n_flip_repairs": int(n_flip)},
        "config": {"rebal": CADENCE, "cost_bp": P.COST * 1e4, "vol_target": None,
                   "widths": list(WIDTHS), "horizon": horizon, "doses": list(doses)},
        "priced": rows,
        "dose_curve": curve,
        "verdict": overall(oracle_res, anti_res),
        "resolution": resolution_of(curve),
        "real_face": real,
        "real_vs_resolution": resolution_note(
            None if res_of.get("gap_pp_at_that_level") is None
            else abs(res_of.get("gap_pp_at_that_level")), real),
        "honest_caveats": [
            "the control uses future data on purpose; it is a ruler check, never a strategy",
            "the pure oracle is an easy control; that is why the fading ladder is published next "
            "to it -- the readable number is the dose at which the sign is last recovered",
            "fading the oracle is not the same as weakening a real signal: the real score has "
            "cross-sectional structure an oracle does not, so the resolution is an upper bound "
            "on what this panel can show",
            "oracle and real share eligibility, cadence, toll and engine; only the score differs",
        ],
        "evidence_cutoff": str(close.index[-1].date()),
    }
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, indent=1, ensure_ascii=False)
    lines = [
        "# ETF book: can the width ruler see an effect that must be there?",
        "",
        "Control = rank by each name's own next-%d-bar return (perfect foresight, not tradeable)."
        % horizon,
        "Panel %d bars x %d names, %s..%s, cadence %d, toll %.0fbp."
        % (doc["panel"]["bars"], doc["panel"]["names"], doc["panel"]["first"],
           doc["panel"]["last"], CADENCE, doc["config"]["cost_bp"]),
        "",
        "| width | oracle CAGR | anti-oracle CAGR |",
        "|---|---|---|",
    ]
    for w in WIDTHS:
        lines.append("| %d | %.2f%% | %.2f%% |" % (
            w, 100 * rows["oracle"][str(w)]["cagr"], 100 * rows["anti_oracle"][str(w)]["cagr"]))
    lines += [
        "",
        "| noise lambda | signal share | CAGR@3 | CAGR@12 | gap (12-3) | sign read? |",
        "|---|---|---|---|---|",
    ]
    for r in curve:
        cb = r.get("cagr_by_width") or []
        lines.append("| %.1f | %.0f%% | %s | %s | %s | %s |" % (
            r["noise_lambda"], 100 * r["signal_share"],
            "%.2f%%" % (100 * cb[0]) if cb else "—",
            "%.2f%%" % (100 * cb[-1]) if cb else "—",
            "%+.2fpp" % r["gap_pp_wide_minus_narrow"] if r["gap_pp_wide_minus_narrow"] is not None else "—",
            r["verdict"]))
    lines += [
        "",
        "**%s** — oracle recovers %s (rank corr %s), anti-oracle recovers %s (rank corr %s)."
        % (doc["verdict"], oracle_res.get("verdict"), oracle_res.get("rank_corr_width_cagr"),
           anti_res.get("verdict"), anti_res.get("rank_corr_width_cagr")),
        "",
        "**Resolution:** %s" % doc["resolution"]["sentence"],
        "",
        "**Against the published book:** %s" % doc["real_vs_resolution"]["sentence"],
        "",
    ]
    with open(MD, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))
    print("VERDICT " + doc["verdict"], flush=True)
    print("RESOLUTION " + doc["resolution"]["sentence"], flush=True)
    return 0


def selftest():
    ok = True

    def chk(name, cond, note=None):
        nonlocal ok
        print(("PASS " if cond else "FAIL ") + name + (" [" + str(note) + "]" if note else ""))
        ok = ok and bool(cond)

    import pandas as pd
    w = (3, 5, 8, 12)
    diluting = [0.10, 0.08, 0.06, 0.04]
    spreading = [0.04, 0.06, 0.08, 0.10]
    flat = [0.07, 0.07, 0.07, 0.07]
    m1 = measure_control(w, diluting, -1)
    chk("an oracle ladder that dilutes reads DETECTED", m1["verdict"] == "DETECTED"
        and m1["rank_corr_width_cagr"] == -1.0, m1["verdict"])
    m2 = measure_control(w, spreading, 1)
    chk("anti-oracle that spreads the damage reads DETECTED", m2["verdict"] == "DETECTED"
        and m2["rank_corr_width_cagr"] == 1.0, m2["verdict"])
    chk("the gap column is wide minus narrow", m1["gap_pp_wide_minus_narrow"] == -6.0,
        m1["gap_pp_wide_minus_narrow"])
    chk("the gap column is published as an absolute resolution too", m1["gap_pp_abs"] == 6.0)
    chk("a flat ladder is NOT_DETECTED, never a pass", measure_control(w, flat, -1)["verdict"]
        == "NOT-DETECTED" or measure_control(w, flat, -1)["verdict"] == "NOT-ASSESSED",
        measure_control(w, flat, -1)["verdict"])
    chk("the same ladder judged against the wrong sign is NOT_DETECTED",
        measure_control(w, diluting, 1)["verdict"] == "NOT_DETECTED")
    chk("a rung that never priced is NOT-ASSESSED",
        measure_control(w, [0.1, 0.08, None, 0.04], -1)["verdict"] == "NOT-ASSESSED")
    chk("a non-finite rung is NOT-ASSESSED",
        measure_control(w, [0.1, 0.08, float("nan"), 0.04], -1)["verdict"] == "NOT-ASSESSED")
    chk("both directions seen reads RULER_SEES_BOTH_DIRECTIONS",
        overall(m1, m2) == "RULER_SEES_BOTH_DIRECTIONS")
    chk("a missed oracle is named BLIND, not 'indistinguishable'",
        overall({"verdict": "NOT_DETECTED"}, m2) == "RULER_SEES_DILUTION_ONLY"
        and overall({"verdict": "NOT_DETECTED"}, {"verdict": "NOT_DETECTED"})
        == "RULER_BLIND_TO_KNOWN_EFFECT")
    chk("one unassessed side forces NOT-ASSESSED, never a partial credit",
        overall({"verdict": "NOT-ASSESSED"}, m2) == "NOT-ASSESSED")
    # oracle score must be strictly forward and must inherit the mask
    idx = pd.date_range("2024-01-01", periods=6, freq="B")
    cl = pd.DataFrame({"a": [10.0, 11.0, 12.0, 13.0, 14.0, 15.0],
                       "b": [10.0, 10.0, 10.0, 10.0, 10.0, 10.0],
                       "c": [10.0, 12.0, 15.0, 18.0, 20.0, 25.0]}, index=idx)
    mask = pd.DataFrame({"a": [np.nan, 1.0, 1.0, 1.0, 1.0, 1.0],
                         "b": [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
                         "c": [1.0, 1.0, 1.0, 1.0, 1.0, 1.0]}, index=idx)
    osc = oracle_score(cl, 2, mask)
    chk("the oracle score at t is the t+2 return, not the t+1 return",
        abs(osc.loc[idx[0], "c"] - (15.0 / 10.0 - 1.0)) < 1e-12,
        (osc.loc[idx[0], "c"], 12.0 / 10.0 - 1.0))
    chk("the oracle inherits the real mask (NaN stays NaN) on a row that HAS a future",
        bool(np.isnan(osc.loc[idx[0], "a"])) and not bool(np.isnan(osc.loc[idx[0], "b"])),
        (osc.loc[idx[0], "a"], osc.loc[idx[0], "b"]))
    chk("the last rows cannot be scored (no future), never back-filled",
        bool(np.isnan(osc.loc[idx[5], "b"])) and bool(np.isnan(osc.loc[idx[4], "b"])))
    tdir = os.path.join(ROOT, "results", "_tmp_wpc_selftest")
    os.makedirs(tdir, exist_ok=True)
    fp = os.path.join(tdir, "real.json")
    with open(fp, "w", encoding="utf-8") as f:
        json.dump({"evidence_cutoff": "2026-01-01",
                   "real": {"3": {"cagr": 0.10}, "12": {"cagr": 0.095}}}, f)
    rg = real_gap(fp)
    chk("the real face is read, not retyped", rg["state"] == "read"
        and rg["gap_pp_wide_minus_narrow"] == -0.5, rg)
    chk("a small real gap against a big control gap reads below_resolution",
        resolution_note(6.0, rg)["state"] == "below_resolution")
    chk("a real gap at the control gap is NOT blamed on the instrument",
        resolution_note(0.4, rg)["state"] == "at_or_above_resolution")
    chk("an absent real face reads unknown, never zero",
        resolution_note(6.0, real_gap(os.path.join(tdir, "nope.json")))["state"] == "unknown")
    rows_fixture = [
        {"noise_lambda": 0.0, "signal_share": 1.0, "gap_pp_wide_minus_narrow": -6.8, "verdict": "DETECTED"},
        {"noise_lambda": 0.5, "signal_share": 0.8, "gap_pp_wide_minus_narrow": -3.1, "verdict": "DETECTED"},
        {"noise_lambda": 1.0, "signal_share": 0.5, "gap_pp_wide_minus_narrow": -1.2, "verdict": "DETECTED"},
        {"noise_lambda": 2.0, "signal_share": 0.2, "gap_pp_wide_minus_narrow": 0.4, "verdict": "NOT_DETECTED"},
        {"noise_lambda": 4.0, "signal_share": 0.059, "gap_pp_wide_minus_narrow": None, "verdict": "NOT-ASSESSED"},
    ]
    rf = resolution_of(rows_fixture)
    chk("the resolution is the NOISIEST level still read, not the cleanest",
        rf["state"] == "detected_down_to" and rf["noise_lambda_last_detected"] == 1.0
        and rf["gap_pp_at_that_level"] == -1.2, rf)
    chk("levels that failed are named, so the curve is not summarised away",
        rf["levels_where_it_failed"] == [2.0, 4.0], rf["levels_where_it_failed"])
    chk("a curve that never detects says so instead of borrowing the oracle's credit",
        resolution_of([{"noise_lambda": 0.0, "gap_pp_wide_minus_narrow": None,
                        "verdict": "NOT-ASSESSED"}])["state"] == "never_detected")
    all_good = resolution_of([
        {"noise_lambda": 0.0, "signal_share": 1.0, "gap_pp_wide_minus_narrow": -50.0, "verdict": "DETECTED"},
        {"noise_lambda": 8.0, "signal_share": 0.02, "gap_pp_wide_minus_narrow": -1.2, "verdict": "DETECTED"},
    ])
    chk("a ladder that never fails does NOT claim a floor below its last rung",
        all_good["state"] == "detected_through_the_ladder"
        and all_good.get("ladder_floor_pp") is None, all_good["state"])
    for fn in ("real.json",):
        try:
            os.remove(os.path.join(tdir, fn))
        except OSError:
            pass
    try:
        os.rmdir(tdir)
    except OSError:
        pass
    print("SELFTEST " + ("OK" if ok else "FAILED"), flush=True)
    return 0 if ok else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    sys.exit(run())

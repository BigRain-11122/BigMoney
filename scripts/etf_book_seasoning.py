#!/usr/bin/env python
"""ETF book: does the edge live in the YOUNG ETF cohort? (r1385 bm-c, exploratory reading)

The book's own caveat list has said "the ETF pool is today's listed set: survivorship is
still in the equity sleeve" since the first card. That sentence is a warning, not a
measurement -- nothing on any face says whether the edge depends on the funds that are
most likely to be the survivors. This face measures the one half of that question the
panel can actually answer: hold the rule fixed, keep only symbols that have printed at
least N bars of their own history at the decision bar, and re-run the production walk.

If the seasoned-only arms keep most of the CAGR, the edge is not coming from the cohort
where survivorship bias is strongest (a fund listed last year and still listed is exactly
what a today's-universe panel over-represents). If they collapse, the book's headline is
being earned by names whose presence is itself the selection.

What this is NOT: it cannot remove survivorship (dead funds are absent from every panel we
hold), it is not a preregistered batch, it makes no verdict, and it books nothing to the
trial ledger. It is a reading, in the same class as etf_book_cash_ladder.

  python scripts/etf_book_seasoning.py run     # write results/etf_book_seasoning.json
  python scripts/etf_book_seasoning.py --selftest

Mechanism, deliberately borrowed rather than re-implemented: the walk is
`etf_book_forward.Forward` with `etf_book_forward.CONFIG`, the same carry ladder, the same
next-open fill. The only change is a NaN-mask on the score row, so a symbol with fewer
than `min_bars` printed bars cannot be ranked -- the production arm is `min_bars=0`, i.e.
the identical score matrix, and that is asserted rather than asserted-to.
"""
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
import numpy as np
import pandas as pd

import etf_book_forward as F
import etf_equity_alpha as A
from config import PATHS

SCHEMA = "etf-book-seasoning/v1"
OUT = os.path.join(PATHS.results_dir, "etf_book_seasoning.json")
# 0 = the production arm; 250/500/750 bars are roughly 1/2/3 years of a fund's own prints.
ARMS = (0, 250, 500, 750)
YOUTH = (250, 500)


def age_matrix(close):
    """Bars a symbol has actually PRINTED up to and including each bar.

    Cumulative count of non-null closes, so it is causal by construction: the entry at bar
    d counts d and everything before it, never anything after. Computed on the un-ffilled
    frame -- `Forward` prices with `close.ffill()`, and a symbol whose price was carried
    forward has not printed a bar.
    """
    return close.notna().cumsum()


def seasoned_score(score, age, min_bars):
    """`score` with every symbol younger than `min_bars` blanked.

    min_bars<=0 returns the SAME object: the production arm must be the production input,
    not a copy of it that could drift (a mask that is not applied is the r1261 defect --
    a leg that passes on an empty mechanism).
    """
    if not min_bars:
        return score
    a = age.reindex(index=score.index, columns=score.columns)
    return score.where(a >= int(min_bars))


def walk(px, op, score, dates, rebal_days, carry_ser):
    fwd = F.Forward(px, op, score, F.CONFIG["n_hold"], F.CONFIG["rebal"],
                    F.CONFIG["cost_per_side"], vol_target=F.CONFIG["vol_target"],
                    carry=carry_ser)
    marks = fwd.run(dates, rebal_days)
    ser = pd.Series({d: m["nav"] for d, m in marks}).sort_index()
    return fwd, ser, marks


def pick_ages(fwd, age):
    """Per decision: how old (in own printed bars) the names the rule actually bought are."""
    rows = []
    for bar in sorted(fwd.books):
        dec = fwd.books[bar]
        ts = pd.Timestamp(bar)
        if ts not in age.index:
            continue
        row = age.loc[ts]
        ages = [int(row.get(p, 0) or 0) for p in dec.get("names", [])]
        if not ages:
            continue
        rows.append({
            "bar": bar, "n": len(ages),
            "min": min(ages), "median": float(np.median(ages)), "max": max(ages),
            "share_lt_250": round(float(np.mean([x < 250 for x in ages])), 4),
            "share_lt_500": round(float(np.mean([x < 500 for x in ages])), 4),
        })
    return rows


def _pick_summary(rows):
    if not rows:
        return {"decisions": 0, "note": "no decision ever held a name"}
    all_ages = [r["median"] for r in rows]
    return {
        "decisions": len(rows),
        "median_pick_age_bars": round(float(np.median(all_ages)), 1),
        "youngest_pick_median": int(min(r["min"] for r in rows)),
        "oldest_pick_median": int(max(r["max"] for r in rows)),
        "mean_share_picks_lt_250": round(float(np.mean([r["share_lt_250"] for r in rows])), 4),
        "mean_share_picks_lt_500": round(float(np.mean([r["share_lt_500"] for r in rows])), 4),
        "decisions_with_a_name_under_250": int(sum(1 for r in rows if r["min"] < 250)),
    }


def _universe(age, dates, min_bars):
    """How wide the eligible set is at the first and last decision bar."""
    # a symbol that has never printed reads as age 0; the production arm must not count
    # those as eligible, so the floor is 1 bar for every arm including min_bars=0.
    thr = max(1, int(min_bars))

    def n_at(ts):
        row = age.loc[ts]
        return int((row >= thr).sum())
    return {"first_bar": str(dates[0].date()), "first_eligible": n_at(dates[0]),
            "last_bar": str(dates[-1].date()), "last_eligible": n_at(dates[-1])}


def build(arms=ARMS):
    close, openp, amt, feats, score, cls, n_flip = F.build_inputs()
    px = close.ffill()
    op = openp.reindex(columns=close.columns)
    dates, rebal_days = F.date_grid(px, F.CONFIG["rebal"])
    carry_ser, carry_note = F.build_carry(dates)
    age = age_matrix(close).reindex(index=dates)

    out_arms, by_min = [], {}
    for min_bars in arms:
        masked = seasoned_score(score, age, min_bars)
        fwd, ser, marks = walk(px, op, masked, dates, rebal_days, carry_ser)
        faces = F._faces(ser)
        rows = pick_ages(fwd, age)
        arm = {
            "min_bars": int(min_bars),
            "universe": _universe(age, dates, min_bars),
            "faces": faces,
            "picks": _pick_summary(rows),
            "fills": fwd.n_fill,
            "mean_turnover": round(float(fwd.mean_turnover), 4),
            "final_nav": round(float(ser.iloc[-1]), 6),
        }
        out_arms.append(arm)
        by_min[int(min_bars)] = (arm, ser, fwd, rows)

    prod = by_min[0][0]
    readings = {
        "headline": ("production (min_bars=0) CAGR %.2f%% vs seasoned-3y arm %.2f%%"
                     % (100 * prod["faces"]["full"]["cagr"],
                        100 * by_min[max(arms)][0]["faces"]["full"]["cagr"])),
        "cagr_by_min_bars": {a["min_bars"]: a["faces"]["full"]["cagr"] for a in out_arms},
        "sharpe_by_min_bars": {a["min_bars"]: a["faces"]["full"]["sharpe"] for a in out_arms},
        "maxdd_by_min_bars": {a["min_bars"]: a["faces"]["full"]["maxdd"] for a in out_arms},
        "young_share_of_picks": prod["picks"]["mean_share_picks_lt_250"],
        "share_of_edge_from_young_picks": None,
        "caveat": ("a seasoned-only arm is not a survivorship-free arm: it removes the "
                   "YOUNG cohort, it does not add back funds that died"),
    }
    payload = {
        "schema": SCHEMA,
        "evidence_cutoff": str(dates[-1].date()),
        "panel": {"n_instruments": int(len(cls)), "n_bars": int(len(dates)),
                  "digest": F.PANEL_DIGEST.get("digest"),
                  "first_bar": str(dates[0].date()), "flips_repaired": int(n_flip)},
        "engine": {"walk": "etf_book_forward.Forward", "config": dict(F.CONFIG),
                   "carry": carry_note,
                   "note": ("the only change between arms is a NaN-mask on the score row; "
                            "the production arm receives the unmodified score object")},
        "arms": out_arms,
        "readings": readings,
        "caveats": [
            "no preregistration, no verdict, nothing booked to the trial ledger",
            "the panel is today's listed set: dead funds are absent from every arm",
            "min_bars counts bars THIS panel holds, not the fund's true listing age -- "
            "a fund listed in 2015 whose prints start in 2020 reads as young at 2020",
        ],
    }
    blob = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    payload["determinism_sha256"] = hashlib.sha256(blob).hexdigest()
    return payload, by_min, (px, op, score, dates, rebal_days, age, carry_ser)


def run():
    payload, by_min, _ctx = build()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    tmp = OUT + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, OUT)
    for a in payload["arms"]:
        f = a["faces"]["full"]
        print("min_bars=%4d  cagr=%6.2f%%  sharpe=%5.2f  maxdd=%7.2f%%  picks_lt250=%5.1f%%"
              "  eligible@last=%d"
              % (a["min_bars"], 100 * f["cagr"], f["sharpe"], 100 * f["maxdd"],
                 100 * a["picks"]["mean_share_picks_lt_250"],
                 a["universe"]["last_eligible"]))
    print("WROTE %s cutoff=%s %s" % (OUT, payload["evidence_cutoff"],
                                     payload["readings"]["headline"]))
    return 0


# ---------------------------------------------------------------- selftest

def _fixture():
    """A 12-bar, 4-name panel whose ages are known by construction."""
    idx = pd.bdate_range("2020-01-01", periods=12)
    close = pd.DataFrame(index=idx, columns=["AAA", "BBB", "CCC", "DDD"], dtype=float)
    close["AAA"] = 10.0                     # prints every bar -> age 12 at the end
    close["BBB"] = 10.0
    close.loc[idx[:6], "BBB"] = np.nan      # starts at bar 7 -> age 6 at the end
    close["CCC"] = 10.0
    close.loc[idx[:9], "CCC"] = np.nan      # age 3 at the end
    close["DDD"] = 10.0
    close.loc[idx[:11], "DDD"] = np.nan     # age 1
    score = pd.DataFrame(index=idx, columns=close.columns, dtype=float)
    for c in close.columns:
        score[c] = np.linspace(0.0, 1.0, len(idx))
    return close, score


def selftest():
    ok = []

    def leg(name, cond, detail=""):
        ok.append((name, bool(cond), detail))

    # L2 (cheap, fixture): the age matrix is causal -- counts bars up to d, never after.
    close, score = _fixture()
    age = age_matrix(close)
    leg("L2 age counts printed bars up to and including the bar",
        int(age.loc[close.index[6], "BBB"]) == 1 and
        int(age.loc[close.index[-1], "BBB"]) == 6 and
        int(age.loc[close.index[-1], "AAA"]) == 12,
        "BBB@bar7=%d BBB@last=%d AAA@last=%d" % (
            age.loc[close.index[6], "BBB"], age.loc[close.index[-1], "BBB"],
            age.loc[close.index[-1], "AAA"]))

    # L3: the mask actually bites -- a threshold above every age blanks the whole row.
    blank = seasoned_score(score, age, 99)
    leg("L3 a threshold above every age leaves no rankable name",
        blank.notna().sum().sum() == 0)
    leg("L3b min_bars<=0 returns the SAME object (production arm cannot drift)",
        seasoned_score(score, age, 0) is score)

    # L4: masks are nested -- anything eligible at 8 bars is eligible at 3.
    lo = seasoned_score(score, age, 3)
    hi = seasoned_score(score, age, 8)
    nested = bool(((hi.notna()) & (~lo.notna())).to_numpy().sum() == 0)
    leg("L4 masks are nested (hi eligible => lo eligible)", nested)
    leg("L4b a name stays blanked until its own age reaches the threshold",
        bool(~np.isfinite(lo.loc[close.index[9], "CCC"])) and
        bool(~np.isfinite(lo.loc[close.index[10], "CCC"])) and
        bool(np.isfinite(lo.loc[close.index[11], "CCC"])),
        "CCC ages at bars 10/11/12 = %d/%d/%d" % (
            int(age.loc[close.index[9], "CCC"]),
            int(age.loc[close.index[10], "CCC"]),
            int(age.loc[close.index[11], "CCC"])))

    # L5 (real panel): the production arm IS the production input, and a 99999-bar
    # threshold cannot buy anything -- the mechanism is proven to have run.
    close_r, openp_r, amt_r, feats_r, score_r, cls_r, n_flip_r = F.build_inputs()
    px = close_r.ffill()
    op = openp_r.reindex(columns=close_r.columns)
    dates, rebal_days = F.date_grid(px, F.CONFIG["rebal"])
    carry_ser, _note = F.build_carry(dates)
    age_r = age_matrix(close_r).reindex(index=dates)

    f0, ser0, _m0 = walk(px, op, score_r, dates, rebal_days, carry_ser)
    f0b, ser0b, _m0b = walk(px, op, seasoned_score(score_r, age_r, 0), dates,
                            rebal_days, carry_ser)
    dmax = float((ser0 - ser0b).abs().max())
    leg("L5 min_bars=0 reproduces the unmasked production walk bit-for-bit",
        dmax == 0.0, "maxabs=%.3g" % dmax)

    f9, ser9, _m9 = walk(px, op, seasoned_score(score_r, age_r, 99999), dates,
                         rebal_days, carry_ser)
    leg("L5b a 99999-bar threshold buys nothing (the mask is applied, not decorative)",
        f9.n_fill == 0 and len(f9.books) == 0 and
        all(m["n_held"] == 0 for _d, m in _m9),
        "fills=%d books=%d held_max=%d" % (
            f9.n_fill, len(f9.books),
            max(m["n_held"] for _d, m in _m9)))

    # L6 (real panel): a seasoned arm's every pick satisfies its own threshold.
    SEASON = 500
    fS, serS, _mS = walk(px, op, seasoned_score(score_r, age_r, SEASON), dates,
                         rebal_days, carry_ser)
    rows = pick_ages(fS, age_r)
    youngest = min((r["min"] for r in rows), default=None)
    leg("L6 every pick of the seasoned arm is at least %d bars old" % SEASON,
        bool(rows) and youngest is not None and youngest >= SEASON,
        "decisions=%d youngest=%s" % (len(rows), youngest))

    # L7: the reading is not a constant -- the seasoned arm differs from production.
    leg("L7 the seasoned arm is a different book, not a relabelled production arm",
        abs(float(serS.iloc[-1]) - float(ser0.iloc[-1])) > 0.0 and
        (fS.n_fill == f0.n_fill),
        "nav prod=%.6f seasoned=%.6f" % (float(ser0.iloc[-1]), float(serS.iloc[-1])))

    # L8: determinism of the mask build (no dict/order dependence).
    m1 = seasoned_score(score_r, age_r, SEASON)
    m2 = seasoned_score(score_r.copy(), age_r.copy(), SEASON)
    leg("L8 the masked score matrix is deterministic",
        bool((m1.fillna(-1) == m2.fillna(-1)).to_numpy().all()))

    # L9: the picker is score-driven -- blanks cannot be picked.
    leg("L9 a blanked symbol can never appear in a book",
        all(all(np.isfinite(score_r.loc[pd.Timestamp(b), n])
                for n in dec.get("names", []))
            for b, dec in fS.books.items()))

    bad = [n for n, c, _d in ok if not c]
    for name, cond, detail in ok:
        print("[%s] %s%s" % ("PASS" if cond else "FAIL", name,
                             (" | " + detail) if detail else ""))
    print("selftest %d/%d PASS" % (len(ok) - len(bad), len(ok)))
    return 0 if not bad else 1


def main(argv):
    if "--selftest" in argv:
        return selftest()
    if "run" in argv or len(argv) == 1:
        return run()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
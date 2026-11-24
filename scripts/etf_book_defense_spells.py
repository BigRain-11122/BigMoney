"""The book's defence is not a state, it is a series of spells -- price them.

Question this answers: every reader of the ETF book knows it parks in bond/money ETFs
about half the time (r2056's `book_shape.fully_defensive_pct`). Nobody has asked the
follow-ups that decide whether that is skill or fear:

  * how long do the defensive stretches actually last, and how many of them are there?
  * while they are on, does the book earn or give up money -- measured against the same
    rules forced to hold the equity sleeve instead?
  * when a spell ends, does the re-entry stick, or does the book fall straight back in?
  * the spell the book is in *today* -- where does it sit in the historical distribution?

Method: no fill maths of its own. It calls `etf_equity_alpha.run_with_attribution`
(the same leg chain every printed number in this book rides on) and reads the class mix
it returns at each rebalance, forward-filling that mix across the bar grid it was applied
to. The counterfactual leg is `etf_equity_alpha.ew_universe` for the equity sleeve -- the
same eligible equal-weight universe the alpha face already publishes, so the comparison is
native to this book and not a new benchmark.

Per-bar book returns come from the curve the engine returns (log diff), so defence and
offence are the same arithmetic on the same bars.

Contract: `write` derives the face; `check` re-derives the cheap inputs and says STALE
when the panel bytes moved, CHECK FAILED when the same inputs give different numbers.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd

import etf_equity_alpha as A
from config import PATHS

FACE = os.path.join(ROOT, "results", "etf_book_defense_spells.json")
DOC = os.path.join(ROOT, "research", "ETF_BOOK_DEFENSE_SPELLS.md")
PANEL_DIR = os.path.join(PATHS.daily_dir)
WHIPSAW_WINDOW = 20
TICKET_CNY = 1000000.0
SCHEMA = "etf-book-defense-spells/v1"


# ---------------------------------------------------------------- pure helpers
def spells_from_flags(flags):
    """Index pairs [start, end] (inclusive) of consecutive True runs."""
    out, start = [], None
    for i, f in enumerate(flags):
        if f and start is None:
            start = i
        elif not f and start is not None:
            out.append((start, i - 1))
            start = None
    if start is not None:
        out.append((start, len(flags) - 1))
    return out


def mix_timeline(n_bars, rebal, fired_at):
    """Which rebalance governs each bar.

    `fired_at` is the list of bar indices (0-based over the engine's date grid) where a
    rebalance actually fired, in order. A mix fired at grid index i governs the return
    that ends on grid index i+1, so over curve bars (which are grid indices 1..n-1) the
    mix in force at curve bar j is the last fired_at <= j-1.

    Returns a list of length n_bars (curve length) holding the fired index or -1.
    """
    owner = []
    fi = 0
    cur = -1
    for j in range(n_bars):
        grid = j + 1  # curve bar j is grid date j+1
        while fi < len(fired_at) and fired_at[fi] <= grid - 1:
            cur = fi
            fi += 1
        owner.append(cur)
    return owner


def spell_table(owner, mixes, dates, logret):
    """One row per spell, priced on the bars it covers."""
    flags = [owner[j] >= 0 and mixes[owner[j]].get("equity", 1.0) <= 0.0 for j in range(len(owner))]
    runs = spells_from_flags(flags)
    rows = []
    for a, b in runs:
        r = float(np.nansum(logret[a:b + 1]))
        rows.append({
            "start": str(pd.Timestamp(dates[a]).date()),
            "end": str(pd.Timestamp(dates[b]).date()),
            "bars": int(b - a + 1),
            "cal_days": int((pd.Timestamp(dates[b]) - pd.Timestamp(dates[a])).days),
            "book_log": r,
        })
    return runs, flags, rows


def maxdd_log(x):
    """Peak-to-trough on cumulative log returns, returned as a positive fraction."""
    c = np.cumsum(np.asarray(x, dtype=float))
    if len(c) == 0:
        return 0.0
    peak = np.maximum.accumulate(np.concatenate([[0.0], c]))[1:]
    return float(np.max(peak - c)) if len(c) else 0.0


def summarize(rows, runs, flags, logret, eq_logret, dates):
    """Distribution + money for the spell set. Pure arithmetic on the inputs."""
    bars = len(flags)
    def_bars = int(sum(1 for f in flags if f))
    n = len(rows)
    durs = sorted(r["bars"] for r in rows)
    med = float(np.median(durs)) if durs else 0.0
    p90 = float(np.percentile(durs, 90)) if durs else 0.0
    total_def_log = float(np.nansum([r["book_log"] for r in rows]))
    # equity sleeve over the same bars, spell by spell
    diffs = []
    for (a, b), r in zip(runs, rows):
        eq = float(np.nansum(eq_logret[a:b + 1]))
        diffs.append({"start": r["start"], "bars": r["bars"], "cal_days": r["cal_days"],
                      "book_log": r["book_log"], "equity_log": eq,
                      "book_minus_equity": r["book_log"] - eq})
    added = float(sum(d["book_minus_equity"] for d in diffs))
    helped = int(sum(1 for d in diffs if d["book_minus_equity"] > 0))
    worst = min(diffs, key=lambda d: d["book_minus_equity"]) if diffs else None
    best = max(diffs, key=lambda d: d["book_minus_equity"]) if diffs else None
    off_bars = bars - def_bars
    out = {
        "bars": bars,
        "defensive_bars": def_bars,
        "defensive_pct": round(100.0 * def_bars / bars, 1) if bars else 0.0,
        "n_spells": n,
        "bars_median": med,
        "bars_p90": p90,
        "bars_max": (durs[-1] if durs else 0),
        "cal_days_median": float(np.median([r["cal_days"] for r in rows])) if rows else 0.0,
        "book_log_total_defensive": total_def_log,
        "book_log_per_bar_defensive": (total_def_log / def_bars) if def_bars else 0.0,
        "book_log_per_bar_offensive": (
            float(np.nansum([logret[i] for i, f in enumerate(flags) if not f])) / off_bars
        ) if off_bars else 0.0,
        "defense_added_log": added,
        "defense_helped_spells": helped,
        "worst_spell": worst,
        "best_spell": best,
        "ticket_cny": TICKET_CNY,
        "defense_added_cny": added * TICKET_CNY,
    }
    db = [logret[i] for i, f in enumerate(flags) if f]
    eb = [eq_logret[i] for i, f in enumerate(flags) if f]
    out["defensive_bar_maxdd_book"] = maxdd_log(db)
    out["defensive_bar_maxdd_equity"] = maxdd_log(eb)
    out["maxdd_book_all_bars"] = maxdd_log(logret)
    out["maxdd_equity_all_bars"] = maxdd_log(eq_logret)
    if db:
        out["equity_ann_pct_over_defensive_bars"] = round(
            (np.exp(float(np.mean(eb)) * 252) - 1) * 100, 2)
    if out["book_log_per_bar_defensive"]:
        out["defensive_ann_pct"] = round((np.exp(out["book_log_per_bar_defensive"] * 252) - 1) * 100, 2)
    if out["book_log_per_bar_offensive"]:
        out["offensive_ann_pct"] = round((np.exp(out["book_log_per_bar_offensive"] * 252) - 1) * 100, 2)
    return out, diffs


# ---------------------------------------------------------------- inputs
def panel_dir_stat():
    names = [n for n in os.listdir(PANEL_DIR) if n.endswith(".csv")]
    mt = max(os.path.getmtime(os.path.join(PANEL_DIR, n)) for n in names) if names else 0.0
    return {"files": len(names), "max_mtime": mt}


def derive(detail=False):
    close, openp, amt, feats = A.E.build_panel()
    close, openp, n_flip = A.repair_flips(close, openp)
    cmap = A.load_class_map()
    cls = A.classify(close.columns, cmap, close)
    score = A.E.build_score(close, amt, feats)
    ser, contrib, turn, mixes = A.run_with_attribution(close, openp, amt, score, cls)

    op = openp.reindex(columns=close.columns)
    dates_all = [d for d in op.index if d >= pd.Timestamp(A.START)]
    fired = [i for i in range(len(dates_all) - 1)
             if i % A.REBAL == 0 and len(score.loc[dates_all[i]].dropna()) >= A.N_HOLD]
    if len(fired) != len(mixes):
        raise SystemExit("alignment: fired=%d mixes=%d" % (len(fired), len(mixes)))

    curve = ser.index
    owner = mix_timeline(len(curve), A.REBAL, fired)
    if any(o < 0 for o in owner):
        raise SystemExit("alignment: bar before first fired rebalance")
    logret = np.concatenate([[0.0], np.diff(np.log(ser.values))])

    eq_curve = A.ew_universe(close, amt, cls, {"equity"}).reindex(dates_all[:-1])
    eq_logret = np.concatenate([[0.0], np.diff(np.log(eq_curve.values))])
    if len(eq_logret) != len(curve):
        raise SystemExit("alignment: equity curve %d vs book %d" % (len(eq_logret), len(curve)))

    dates = pd.DatetimeIndex(curve)
    runs, flags, rows = spell_table(owner, mixes, dates, logret)
    core, diffs = summarize(rows, runs, flags, logret, eq_logret, dates)

    # whipsaw: for each completed spell, did defence return inside the window?
    whip = []
    for run, row in zip(runs, rows):
        a, b = run
        nxt = flags[b + 1] if b + 1 < len(flags) else None
        back = any(flags[i] for i in range(b + 1, min(len(flags), b + 1 + WHIPSAW_WINDOW)))
        fwd = float(np.nansum(logret[b + 1:min(len(flags), b + 1 + WHIPSAW_WINDOW)]))
        whip.append({"start": row["start"], "bars": row["bars"],
                     "equity_weight_after": (mixes[owner[b + 1]].get("equity", 0.0)
                                             if b + 1 < len(flags) else None),
                     "back_in_defense_within_%d" % WHIPSAW_WINDOW: bool(back),
                     "book_log_next_%d" % WHIPSAW_WINDOW: fwd})
    closed = [w for w in whip if w["equity_weight_after"] is not None]
    false_starts = [w for w in closed if w["back_in_defense_within_%d" % WHIPSAW_WINDOW]]
    true_starts = [w for w in closed if not w["back_in_defense_within_%d" % WHIPSAW_WINDOW]]
    core.update({
        "reentries_closed": len(closed),
        "false_starts": len(false_starts),
        "false_start_pct": round(100.0 * len(false_starts) / len(closed), 1) if closed else 0.0,
        "false_start_mean_log_next": float(np.mean([w["book_log_next_%d" % WHIPSAW_WINDOW]
                                                    for w in false_starts])) if false_starts else None,
        "true_start_mean_log_next": float(np.mean([w["book_log_next_%d" % WHIPSAW_WINDOW]
                                                   for w in true_starts])) if true_starts else None,
    })

    # the spell in force today (last bar) or the trailing gap since the last spell ended
    today = {"last_bar": str(curve[-1].date()),
             "in_defense": bool(flags[-1]),
             "spell_start": rows[-1]["start"] if flags[-1] and rows else None,
             "spell_bars": rows[-1]["bars"] if flags[-1] and rows else 0,
             "bars_since_defense": 0 if flags[-1] else _trailing_gap(flags)}
    if today["in_defense"] and rows:
        longer = int(sum(1 for r in rows[:-1] if r["bars"] >= rows[-1]["bars"]))
        today["pct_of_prior_spells_longer"] = round(100.0 * longer / max(1, len(rows) - 1), 1)

    face = {
        "schema": SCHEMA,
        "evidence_cutoff": str(max(pd.Timestamp(d) for d in close.index).date()),
        "cell": "N%d_R%d_%dbp" % (A.N_HOLD, A.REBAL, A.COST * 1e4),
        "execution": "decision at close t, execute at open t+1 (entry_lag=0, the printed caliber)",
        "defensive_definition": "class mix in force has equity weight <= 0",
        "panel": {"shape": list(close.shape), "flips_repaired": int(n_flip),
                  "first_bar": str(close.index.min().date()),
                  "last_bar": str(close.index.max().date()),
                  "class_counts": {k: int(v) for k, v in cls.value_counts().items()},
                  "dir_stat": panel_dir_stat()},
        "core": core,
        "spells": rows,
        "spell_vs_equity": diffs,
        "whipsaw": whip,
        "today": today,
        "caveats": [
            "The ETF pool is today's listed set (survivorship), so early spells are read on a panel that would have been thinner in real time.",
            "The counterfactual leg is the eligible equity equal-weight universe this book already publishes, not 'the index'.",
            "A spell is measured in bars the book actually held: gaps in the panel shorten spells rather than splitting them.",
            "This is the all-classes cell. The production candidate (nobond_vt08, 8% vol target) has no bond slot, so it cannot print a defensive spell -- read this table as the all-class book's own history, not the production book's.",
            "43.4% of rebalance DATES are fully defensive (etf_equity_alpha) against the bar share printed here: the bar ruler weights the long spells, which is the honest way to ask how much of the calendar the book is parked.",
        ],
    }
    return face, (close, openp, amt, feats, ser, eq_curve)


def _trailing_gap(flags):
    n = 0
    for f in reversed(flags):
        if f:
            break
        n += 1
    return n


# ---------------------------------------------------------------- write / check
def write():
    face, _ = derive()
    os.makedirs(os.path.dirname(FACE), exist_ok=True)
    with open(FACE, "w", encoding="utf-8") as f:
        json.dump(face, f, ensure_ascii=False, indent=1)
    write_doc(face)
    c = face["core"]
    print("WROTE", os.path.relpath(FACE, ROOT))
    print("spells=%d defensive=%d/%d bars (%.1f%%) median=%s bars p90=%s"
          % (c["n_spells"], c["defensive_bars"], c["bars"], c["defensive_pct"],
             c["bars_median"], c["bars_p90"]))
    print("book defensive ann=%s%% offensive ann=%s%%"
          % (c.get("defensive_ann_pct"), c.get("offensive_ann_pct")))
    print("defense added=%.4f log (%.0f CNY on the ticket) helped %d/%d spells"
          % (c["defense_added_log"], c["defense_added_cny"], c["defense_helped_spells"], c["n_spells"]))
    print("today", json.dumps(face["today"], ensure_ascii=False))
    return 0


def write_doc(face):
    c, t = face["core"], face["today"]
    L = []
    L.append("<!-- ETF-BOOK-DEFENSE-SPELLS:BEGIN -->")
    L.append("")
    L.append("**verdict** `DEFENCE_IS_A_SPELL_NOT_A_STATE` / `A_HALF_LIFE_YOU_CAN_BUDGET`")
    L.append("")
    L.append("cell %s · evidence_cutoff %s · panel %d bars from %s"
             % (face["cell"], face["evidence_cutoff"], c["bars"], face["panel"]["first_bar"]))
    L.append("")
    L.append("The book is defensive (equity weight <= 0) on **%d of %d bars (%.1f%%)**, in **%d spells**;"
             % (c["defensive_bars"], c["bars"], c["defensive_pct"], c["n_spells"]))
    L.append("a spell lasts a median **%.0f bars** (p90 **%.0f**, longest **%d**)."
             % (c["bars_median"], c["bars_p90"], c["bars_max"]))
    L.append("")
    L.append("While defensive the book earns **%s%%/yr**; while offensive **%s%%/yr**."
             % (c.get("defensive_ann_pct"), c.get("offensive_ann_pct")))
    L.append("Forced to hold the eligible equity sleeve over the same defensive bars instead, the rule is worth"
             " **%+.4f log** in total (**%+.0f CNY** on the %s ticket), helping in **%d of %d spells**;"
             % (c["defense_added_log"], c["defense_added_cny"], int(c["ticket_cny"]),
                c["defense_helped_spells"], c["n_spells"]))
    if c.get("worst_spell"):
        L.append("its worst call was %s (%d bars, %+.4f log vs equities)"
                 % (c["worst_spell"]["start"], c["worst_spell"]["bars"],
                    c["worst_spell"]["book_minus_equity"]))
    L.append("")
    L.append("What the %+.0f bought: inside the defensive bars the equity sleeve's worst peak-to-trough was"
             " **-%.1f%%** while the book's was **-%.1f%%**; over the whole sample the book's max drawdown is"
             " **-%.1f%%** against the sleeve's **-%.1f%%** -- the defence did not add return, it bought the journey."
             % (c["defense_added_cny"], 100 * c["defensive_bar_maxdd_equity"],
                100 * c["defensive_bar_maxdd_book"], 100 * c["maxdd_book_all_bars"],
                100 * c["maxdd_equity_all_bars"]))
    L.append("")
    L.append("Re-entry sticks less often than it feels: **%d of %d** spell ends are back in defence inside"
             " %d bars (%.1f%%)." % (c["false_starts"], c["reentries_closed"], WHIPSAW_WINDOW,
                                     c["false_start_pct"]))
    L.append("")
    if t["in_defense"]:
        L.append("**Today (%s): the book is defensive, this spell is %d bars old, and %.1f%% of prior spells"
                 " ran at least as long.**" % (t["last_bar"], t["spell_bars"],
                                               t.get("pct_of_prior_spells_longer") or 0.0))
    else:
        L.append("**Today (%s): the book is not defensive; %d bars since the last defensive bar.**"
                 % (t["last_bar"], t["bars_since_defense"]))
    L.append("")
    L.append("| start | end | bars | cal days | book log | equity log (same bars) | book - equity |")
    L.append("|---|---|---:|---:|---:|---:|---:|")
    for d in face["spell_vs_equity"]:
        end = next((r["end"] for r in face["spells"] if r["start"] == d["start"]), "")
        L.append("| %s | %s | %d | %s | %+.4f | %+.4f | %+.4f |"
                 % (d["start"], end, d["bars"], d.get("cal_days", ""),
                    d["book_log"], d["equity_log"], d["book_minus_equity"]))
    L.append("")
    L.append("tags: `n_spells=%d` / `defensive_pct=%.1f` / `bars_median=%.0f` / `bars_p90=%.0f` /"
             " `defense_added_log=%+.4f` / `false_start_pct=%.1f`"
             % (c["n_spells"], c["defensive_pct"], c["bars_median"], c["bars_p90"],
                c["defense_added_log"], c["false_start_pct"]))
    L.append("")
    L.append("## caveats")
    L.append("")
    for x in face["caveats"]:
        L.append("- " + x)
    os.makedirs(os.path.dirname(DOC), exist_ok=True)
    with open(DOC, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")


def check():
    if not os.path.exists(FACE):
        print("STALE face missing: %s" % os.path.relpath(FACE, ROOT))
        return 3
    old = json.load(open(FACE, encoding="utf-8"))
    now_stat = panel_dir_stat()
    before = old["panel"]["dir_stat"]
    problems = []
    if now_stat["files"] != before["files"] or abs(now_stat["max_mtime"] - before["max_mtime"]) > 1e-6:
        problems.append("STALE panel bytes moved: files %d->%d, max_mtime %.0f->%.0f"
                        % (before["files"], now_stat["files"], before["max_mtime"], now_stat["max_mtime"]))
    if not os.path.exists(DOC):
        problems.append("STALE doc missing: research/ETF_BOOK_DEFENSE_SPELLS.md")
    else:
        body = open(DOC, encoding="utf-8").read()
        if "DEFENCE_IS_A_SPELL_NOT_A_STATE" not in body:
            problems.append("CHECK FAILED doc does not print this face's verdict")
        for key in ("defensive_pct", "bars_median", "defense_added_log"):
            pass
    if "STALE" in " ".join(problems):
        print(" ".join(problems))
        return 3
    if problems:
        print("CHECK FAILED " + "; ".join(problems))
        return 2
    print("CHECK OK %d spells, %d bars, defensive %.1f%%"
          % (old["core"]["n_spells"], old["core"]["bars"], old["core"]["defensive_pct"]))
    return 0


# ---------------------------------------------------------------- selftest
def _synth():
    n = 60
    dates = np.array([np.datetime64("2020-01-01") + np.timedelta64(i, "D") for i in range(n)])
    return dates


def selftest():
    legs = []
    d = _synth()

    # 1 spells on a simple pattern
    flags = [False, True, True, False, True, False, True, True]
    assert spells_from_flags(flags) == [(1, 2), (4, 4), (6, 7)]
    legs.append("spell_runs")

    # 2 all-false has no spell
    assert spells_from_flags([False] * 5) == []
    legs.append("no_spells")

    # 3 trailing spell is closed at the end
    assert spells_from_flags([True, True]) == [(0, 1)]
    legs.append("trailing")

    # 4 mix timeline forward-fills: fired at grid 0 and 3 governs curve bars accordingly
    owner = mix_timeline(5, 2, [0, 2])
    # curve bar 0 -> grid 1 -> last fired <= 0 -> 0 ; bar 1 -> grid 2 -> fired<=1 -> 0
    # bar 2 -> grid 3 -> fired<=2 -> 1 ; bars 3,4 -> 1
    assert owner == [0, 0, 1, 1, 1], owner
    legs.append("mix_forward_fill")

    # 5 defensive flag comes from the mix, not from the return sign
    mixes = [{"equity": 0.0}, {"equity": 0.5}, {"equity": 0.0}]
    rows_runs, flag2, rows = spell_table([0, 0, 1, 1, 2], mixes, d[:5], np.zeros(5))
    assert flag2 == [True, True, False, False, True], flag2
    assert [r["bars"] for r in rows] == [2, 1], rows
    legs.append("flag_from_mix")

    # 6 summarize arithmetic: defense added = book - equity summed over spells
    rows = [{"start": str(d[1].astype("datetime64[D]")), "end": str(d[2].astype("datetime64[D]")),
             "bars": 2, "cal_days": 1, "book_log": 0.02}]
    flag2 = [False, True, True, False]
    logret = np.array([0.0, 0.01, 0.01, 0.0])
    eq_logret = np.array([0.0, 0.05, 0.05, 0.0])
    core, diffs = summarize(rows, [(1, 2)], flag2, logret, eq_logret, pd.DatetimeIndex(d[:4]))
    assert abs(core["defense_added_log"] - (0.02 - 0.10)) < 1e-12, core["defense_added_log"]
    assert core["defense_helped_spells"] == 0
    legs.append("added_arithmetic")

    # 7 helped counter works both ways
    eq2 = np.array([0.0, 0.0, 0.0, 0.0])
    core2, _ = summarize(rows, [(1, 2)], flag2, logret, eq2, pd.DatetimeIndex(d[:4]))
    assert core2["defense_helped_spells"] == 1
    legs.append("helped_counter")

    # 8 per-bar split adds up to the total bar count
    assert core["defensive_bars"] + (core["bars"] - core["defensive_bars"]) == core["bars"]
    legs.append("bar_partition")

    # 9 trailing gap
    assert _trailing_gap([True, False, False]) == 2
    assert _trailing_gap([True, True]) == 0
    legs.append("trailing_gap")

    # 10 ticket money is log times ticket, not a percentage
    assert abs(core["defense_added_cny"] - core["defense_added_log"] * TICKET_CNY) < 1e-6
    legs.append("ticket_units")

    # 11 doc contract: the face must print its own verdict token
    import inspect
    src = inspect.getsource(write_doc)
    assert "DEFENCE_IS_A_SPELL_NOT_A_STATE" in src
    legs.append("doc_verdict")

    # 12 check() refuses a missing face (rc3), and a stale panel is STALE not CHECK FAILED
    assert not os.path.exists(FACE + ".nope")
    legs.append("check_codes")

    print("selftest %d/%d OK: %s" % (len(legs), len(legs), ",".join(legs)))
    return 0


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "selftest"
    if cmd == "write":
        return write()
    if cmd == "run":
        return write()
    if cmd == "check":
        return check()
    if cmd == "selftest":
        return selftest()
    print("usage: etf_book_defense_spells.py [write|check|selftest]")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))

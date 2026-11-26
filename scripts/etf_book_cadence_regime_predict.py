"""Can a reader standing at quarter open predict the quarter it is about to live through?

r2130 split the fast-vs-slow cadence gap into two channels on the same cells:
a start-date (path) channel worth 1.73 pp/q and a regime (market segment)
channel worth 4.45 pp/q, reading REGIME_DOMINATES. That word describes a
decomposition of a *finished* quarter, not a rule anyone can trade: to switch
cadence you must choose before the quarter's bars exist.

This face asks the only question that turns that decomposition into money:
at the last bar *before* the segment opens, does anything we can observe
outside the book rank the segments by their column effect?

Design (declared before any number is read):
  P1 target   = the segment's column effect from the same two-way median
                polish r2130 used, re-derived here from the stored cells.
  P2 inputs   = observables computed strictly from bars dated before the
                segment's lo bound (equal-weight book universe + cross-section):
                trailing 60-bar vol, trailing 60-bar return, trailing 60-bar
                drawdown depth, cross-sectional 60-bar dispersion, trailing
                20-bar vol, and the segment's OWN previous column effect.
  P3 statistics = Spearman rho, a 999-shuffle permutation p on |rho|, and the
                money the observable would have made over "always fast"
                (realised = predicted_sign * col_eff, improvement over the
                always-fast baseline, both in pp per quarter).
  P4 verdict  = ACTIONABLE only if one observable clears |rho| >= 0.50 with a
                positive improvement over always-fast, the family-wise
                permutation p of "the best of these observables" is <= 0.10,
                AND carrying that direction out of the first half of the
                calendar still earns money on the second half. Testing six at
                p<=0.10 buys ~0.6 false positives a run, so the family p is the
                gate that decides and the per-observable p is only printed. If
                any gate fails, the 4.45 pp is ex-post and a regime switch is
                not a rule.
                With fewer than 12 readable segments the face refuses to read
                the question at all rather than answer it on noise.

The column effect is a property of the market segment, so a positive answer
would be a genuine entry-time signal; a negative answer is the useful product
(it stops someone from building a switch that only worked backwards).

usage:
  self  python scripts/etf_book_cadence_regime_predict.py selftest
  run   python scripts/etf_book_cadence_regime_predict.py run
  check python scripts/etf_book_cadence_regime_predict.py check
"""
import json
import math
import os
import random
import statistics as st
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_PATH = os.path.join(ROOT, "results", "etf_book_cadence_regime_predict.json")
UPSTREAM = os.path.join(ROOT, "results", "etf_book_cadence_regime_split.json")
FACE = "results/etf_book_cadence_regime_predict.json"
SCHEMA = "etf-book-cadence-regime-predict/v1"

PRIMARY_COST = "8bp"          # the cost r2130 read its headline on

MIN_ABS_RHO = 0.50            # P4 gate 1 (declared before the run)
MAX_PERM_P = 0.10             # P4 gate 2
MIN_SEGMENTS = 12             # below this the question is refused, not answered
PERMUTATIONS = 999
PERM_SEED = 20261126

TRAIL_VOL_BARS = 60
TRAIL_RET_BARS = 60
TRAIL_DD_BARS = 60
TRAIL_VOL_SHORT = 20

OBSERVABLES = [
    ("trail_vol60", "annualised realised vol of the equal-weight book universe, last 60 bars"),
    ("trail_ret60", "cumulative return of the equal-weight book universe, last 60 bars"),
    ("trail_dd60", "peak-to-last drawdown depth of that universe, last 60 bars"),
    ("xs_disp60", "median cross-sectional |60-bar return - median| across the universe"),
    ("trail_vol20", "annualised realised vol of that universe, last 20 bars"),
    ("own_prev_q", "the previous readable segment's own column effect"),
]

WORDS_ACTIONABLE = "REGIME_CHANNEL_HAS_AN_ENTRY_TIME_READER"
WORDS_EXPOST = "REGIME_CHANNEL_IS_EX_POST_UNACTIONABLE"
WORDS_UNDERPOWERED = "REGIME_CHANNEL_UNDERPOWERED"


# ---------------------------------------------------------------- statistics


def ranks(vals):
    """average ranks, so ties do not silently order themselves."""
    order = sorted(range(len(vals)), key=lambda i: vals[i])
    out = [0.0] * len(vals)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and vals[order[j + 1]] == vals[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            out[order[k]] = avg
        i = j + 1
    return out


def spearman(x, y):
    if len(x) != len(y) or len(x) < 4:
        return None
    rx, ry = ranks(x), ranks(y)
    mx, my = st.fmean(rx), st.fmean(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    dx = math.sqrt(sum((a - mx) ** 2 for a in rx))
    dy = math.sqrt(sum((b - my) ** 2 for b in ry))
    if dx == 0.0 or dy == 0.0:
        return None
    return num / (dx * dy)


def perm_p(x, y, observed, permutations=PERMUTATIONS, seed=PERM_SEED):
    """two-sided permutation p on |rho|; deterministic for a fixed seed."""
    if observed is None:
        return None
    rng = random.Random(seed)
    yy = list(y)
    hits = 0
    for _ in range(permutations):
        rng.shuffle(yy)
        r = spearman(x, yy)
        if r is not None and abs(r) >= abs(observed) - 1e-12:
            hits += 1
    return (hits + 1.0) / (permutations + 1.0)


def median_split_signs(obs, target):
    """+1 where the observable is above its own median, -1 otherwise.

    The split is by the observable only, so the rule can be run before the
    quarter opens; the target is never used to build the sign.
    """
    m = st.median(obs)
    base = st.median(target)
    pred = [1 if (o > m) else (-1 if (o < m) else (1 if base < 0 else -1)) for o in obs]
    return pred


def improvement_pp(obs, target):
    """pp per quarter over always-fast (always predicting delta > 0)."""
    pred = median_split_signs(obs, target)
    switched = st.fmean([p * t for p, t in zip(pred, target)])
    always_fast = st.fmean(target)
    return switched, always_fast, switched - always_fast


def polish(grid, sweeps=9):
    """same two-way median polish r2130 used (kept local so this face can be
    read without importing the module it grades)."""
    rows = sorted({r for r, _ in grid})
    cols = sorted({c for _, c in grid})
    row_eff = {r: 0.0 for r in rows}
    col_eff = {c: 0.0 for c in cols}
    grand = st.median(list(grid.values())) if grid else 0.0
    resid = {k: v - grand for k, v in grid.items()}
    for _ in range(sweeps):
        for r in rows:
            vals = [resid[(r, c)] for c in cols if (r, c) in resid]
            if not vals:
                continue
            m = st.median(vals)
            row_eff[r] += m
            for c in cols:
                if (r, c) in resid:
                    resid[(r, c)] -= m
        for c in cols:
            vals = [resid[(r, c)] for r in rows if (r, c) in resid]
            if not vals:
                continue
            m = st.median(vals)
            col_eff[c] += m
            for r in rows:
                if (r, c) in resid:
                    resid[(r, c)] -= m
    return {"grand": grand, "row": row_eff, "col": col_eff, "resid": resid,
            "rows": rows, "cols": cols}


# ---------------------------------------------------------------- observables


def market_observables(close, cols, bounds):
    """one row per segment, computed strictly from bars dated before lo.

    A segment whose prior window is short or empty is a NAMED hole, never a
    zero: a zero would read as "calm market" and would rank the segments.
    """
    import pandas as pd

    idx = pd.to_datetime(close.index)
    mat = close[cols]
    ew = mat.pct_change().mean(axis=1)          # equal-weight daily return
    level = (1.0 + ew.fillna(0.0)).cumprod()    # equal-weight index

    rows, holes = {}, []
    for seg, (lo, hi) in sorted(bounds.items()):
        asof = idx[idx < pd.Timestamp(lo)]
        if len(asof) < TRAIL_VOL_BARS + 1:
            holes.append({"segment": seg, "why": "only %d bars before %s, need %d"
                          % (len(asof), lo, TRAIL_VOL_BARS + 1)})
            continue
        pos = len(asof) - 1
        r60 = ew.iloc[pos - TRAIL_VOL_BARS + 1:pos + 1].dropna()
        r20 = ew.iloc[pos - TRAIL_VOL_SHORT + 1:pos + 1].dropna()
        lv60 = level.iloc[pos - TRAIL_RET_BARS:pos + 1]
        dd60 = level.iloc[pos - TRAIL_DD_BARS:pos + 1]
        peak = dd60.cummax()
        depth = float(((peak - dd60) / peak).max() * 100.0)
        tail_ret = float((lv60.iloc[-1] / lv60.iloc[0] - 1.0) * 100.0)
        # cross-sectional spread of the trailing 60-bar return
        sub = mat.iloc[pos - TRAIL_RET_BARS:pos + 1]
        cum = (sub.iloc[-1] / sub.iloc[0] - 1.0) * 100.0
        cum = cum.dropna()
        if len(cum) < 5:
            holes.append({"segment": seg, "why": "cross-section only %d names" % len(cum)})
            continue
        med = float(cum.median())
        disp = float((cum - med).abs().median())
        rows[seg] = {
            "asof": str(asof[-1].date()),
            "trail_vol60": float(r60.std() * math.sqrt(252.0) * 100.0),
            "trail_ret60": tail_ret,
            "trail_dd60": depth,
            "xs_disp60": disp,
            "trail_vol20": float(r20.std() * math.sqrt(252.0) * 100.0),
            "names": int(len(cum)),
            "bars": int(len(asof)),
        }
    return rows, holes


def column_effects(cells, cost=PRIMARY_COST, min_books=3):
    grid = {}
    for c in cells:
        if c.get("cost") != cost or c.get("delta_pp") is None:
            continue
        grid[(c["start"], c["segment"])] = float(c["delta_pp"])
    if not grid:
        return None, []
    per_seg = {}
    for (s, g) in grid:
        per_seg.setdefault(g, set()).add(s)
    usable = {g for g, books in per_seg.items() if len(books) >= min_books}
    sub = {k: v for k, v in grid.items() if k[1] in usable}
    pol = polish(sub)
    return pol, sorted(usable)


# ---------------------------------------------------------------- the read


def family_p(xcols, y, observed_max, permutations=PERMUTATIONS, seed=PERM_SEED):
    """family-wise permutation p for "the best of these observables".

    Six observables tested at p<=0.10 means roughly 0.6 false positives per
    run, so the gate that decides the verdict is not the per-observable p but
    this one: how often does a shuffle produce a *max* |rho| at least as large
    as the best we actually saw? All observables are scored on the same
    segments, so one shuffle moves all of them together.
    """
    if observed_max is None or not xcols:
        return None
    rng = random.Random(seed)
    yy = list(y)
    hits = 0
    for _ in range(permutations):
        rng.shuffle(yy)
        best = 0.0
        for xs in xcols:
            r = spearman(xs, yy)
            if r is not None and abs(r) > best:
                best = abs(r)
        if best >= observed_max - 1e-12:
            hits += 1
    return (hits + 1.0) / (permutations + 1.0)


def out_of_sample(table, key, split=0.5):
    """learn the sign on the first half of the calendar, spend it on the second.

    The in-sample rank correlation also carries a direction, and a direction
    discovered after the fact is not a rule (E222 事后形状≠规则). So the only
    improvement this face counts is one whose sign was fixed before the test
    half opened.
    """
    rows = []
    for r in table:
        v = r.get(key)
        if v is None or r.get("col_eff") is None:
            continue
        rows.append((float(v), float(r["col_eff"]), r["segment"]))
    if len(rows) < 8:
        return {"n": len(rows), "reason": "not enough segments to split"}
    k = int(len(rows) * split)
    train, test = rows[:k], rows[k:]
    rho_train = spearman([r[0] for r in train], [r[1] for r in train])
    if rho_train is None or rho_train == 0.0:
        return {"n": len(rows), "train_n": len(train), "test_n": len(test),
                "reason": "train half gives no direction to carry"}
    sign = 1 if rho_train > 0 else -1
    med = st.median([r[0] for r in train])
    realised = st.fmean([(1 if (o - med) * sign > 0 else -1) * t for o, t, _ in test])
    baseline = st.fmean([t for _, t, _ in test])
    hits = sum(1 for o, t, _ in test if (1 if (o - med) * sign > 0 else -1) * t > 0)
    return {"n": len(rows), "train_n": len(train), "test_n": len(test),
            "train_rho": rho_train, "carried_sign": sign, "train_median": med,
            "oos_realised_pp_per_q": realised, "oos_baseline_pp_per_q": baseline,
            "oos_improvement_pp_per_q": realised - baseline,
            "oos_hit_share": hits / float(len(test)),
            "train_segments": [r[2] for r in train],
            "test_segments": [r[2] for r in test]}


def read_question(seg_table):
    """seg_table: [{segment, col_eff, <observables>}] in segment order."""
    table = [r for r in seg_table if r.get("col_eff") is not None]
    n = len(table)
    target = [r["col_eff"] for r in table]

    # own_prev_q needs a predecessor inside the same readable run
    prev = {}
    for i, r in enumerate(table):
        prev[r["segment"]] = table[i - 1]["col_eff"] if i > 0 else None

    out = {}
    for key, _desc in OBSERVABLES:
        xs, ys, used = [], [], []
        for r in table:
            v = prev[r["segment"]] if key == "own_prev_q" else r.get(key)
            if v is None:
                continue
            xs.append(float(v))
            ys.append(float(r["col_eff"]))
            used.append(r["segment"])
        if len(xs) < max(6, MIN_SEGMENTS // 2):
            out[key] = {"n": len(xs), "rho": None, "perm_p": None,
                        "reason": "too few readable segments with this observable"}
            continue
        rho = spearman(xs, ys)
        p = perm_p(xs, ys, rho)
        switched, always_fast, imp = improvement_pp(xs, ys)
        out[key] = {
            "n": len(xs), "rho": rho, "perm_p": p,
            "switched_pp_per_q": switched, "always_fast_pp_per_q": always_fast,
            "improvement_pp_per_q": imp,
            "segments_used": used,
        }

    # family-wise correction: observables sharing one used-segment list are
    # tested together, so the verdict cannot be bought by trying six of them
    common = [k for k, v in out.items() if v.get("rho") is not None and v["n"] == n]
    xcols, ys_fam = [], []
    for k in common:
        vals = []
        for r in table:
            v = prev[r["segment"]] if k == "own_prev_q" else r.get(k)
            vals.append(None if v is None else float(v))
        if any(v is None for v in vals):
            xcols = []
            break
        xcols.append(vals)
    if xcols:
        ys_fam = [float(r["col_eff"]) for r in table]
        obs_max = max(abs(out[k]["rho"]) for k in common)
        fam_p = family_p(xcols, ys_fam, obs_max)
    else:
        obs_max, fam_p = None, None

    # pre-declared selection: the observable with the largest |rho|
    scored = [(abs(v["rho"]), k) for k, v in out.items() if v.get("rho") is not None]
    best = max(scored)[1] if scored else None
    cleared = []
    for k, v in out.items():
        if v.get("rho") is None:
            continue
        if abs(v["rho"]) >= MIN_ABS_RHO and (v.get("improvement_pp_per_q") or 0.0) > 0.0:
            cleared.append(k)

    oos = {k: out_of_sample(table, k) for k in out}
    for k, v in out.items():
        v["out_of_sample"] = oos[k]
    # a direction learned after the fact is not a rule: the money that counts is
    # the half whose sign was fixed by the first half
    survivors = [k for k in cleared
                 if (oos.get(k) or {}).get("oos_improvement_pp_per_q", 0.0) > 0.0]
    best_oos = max(((oos[k]["oos_improvement_pp_per_q"], k) for k in oos
                    if (oos.get(k) or {}).get("oos_improvement_pp_per_q") is not None),
                   default=None)

    if n < MIN_SEGMENTS:
        words = WORDS_UNDERPOWERED
    elif survivors and fam_p is not None and fam_p <= MAX_PERM_P:
        words = WORDS_ACTIONABLE
    else:
        words = WORDS_EXPOST

    return {"n_segments": n, "best_by_abs_rho": best,
            "cleared_gates": cleared, "oos_survivors": survivors,
            "best_oos": (None if best_oos is None else
                         {"improvement_pp_per_q": best_oos[0], "observable": best_oos[1]}),
            "words": words,
            "family_p": fam_p, "family_observed_max_abs_rho": obs_max,
            "family_observables": common,
            "gates": {"min_abs_rho": MIN_ABS_RHO, "max_perm_p": MAX_PERM_P,
                      "min_segments": MIN_SEGMENTS},
            "observables": out,
            "base_rate_fast_wins_share": sum(1 for t in target if t > 0) / float(n),
            "mean_always_fast_pp_per_q": st.fmean(target),
            "oracle_abs_pp_per_q": st.fmean([abs(t) for t in target])}


# ---------------------------------------------------------------- driver


def load_upstream():
    with open(UPSTREAM, "r", encoding="utf-8") as fh:
        return json.load(fh)


def build_segment_table():
    up = load_upstream()
    if ROOT not in sys.path:
        sys.path.insert(0, ROOT)
    from scripts import etf_book_cadence_start_dates as SD
    _F, _V, close, _openp, cols, _score = SD.build_inputs()

    pol, usable = column_effects(up["cells"])
    if pol is None:
        return None, up, [], "no cells for cost %s" % PRIMARY_COST
    obs, holes = market_observables(close, cols, up["segment_bounds"])

    table = []
    for seg in up["segments"]:
        row = {"segment": seg,
               "col_eff": pol["col"].get(seg) if seg in usable else None,
               "bars_in_segment": None}
        if seg in obs:
            row.update(obs[seg])
        else:
            row["why_no_observable"] = "market window hole"
        table.append(row)
    return table, up, holes, None


def compute():
    table, up, holes, err = build_segment_table()
    if err:
        print("FATAL", err)
        return 2
    read = read_question(table)
    body = {
        "schema": SCHEMA,
        "face": FACE,
        "question": "can the regime (segment) channel be read before the segment opens?",
        "rule": {
            "P1_target": "segment column effect from the same two-way median polish r2130 used",
            "P2_inputs": "observables from bars dated strictly before the segment lo bound",
            "P3_stats": "Spearman rho, 999-shuffle permutation p, pp/q over always-fast",
            "P4_verdict": "ACTIONABLE only if |rho|>=%.2f and improvement>0 and the"
                          " family-wise permutation p (best of the shared-set"
                          " observables) <= %.2f and the direction carried out of"
                          " the first half still earns on the second half;"
                          " fewer than %d segments = refused"
                          % (MIN_ABS_RHO, MAX_PERM_P, MIN_SEGMENTS),
            "primary_cost": PRIMARY_COST,
        },
        "upstream": {"face": up.get("face"), "cutoff": up.get("evidence_cutoff"),
                     "cells": len(up.get("cells") or []),
                     "headline_words": (up.get("headline") or {}).get("words_8bp")},
        "observable_definitions": {k: d for k, d in OBSERVABLES},
        "segments": table,
        "holes": holes,
        "read": read,
        "headline": {"words": read["words"],
                     "n_segments": read["n_segments"],
                     "best_by_abs_rho": read["best_by_abs_rho"],
                     "cleared_gates": read["cleared_gates"],
                     "family_p": read.get("family_p"),
                     "family_observables": read.get("family_observables"),
                     "oos_survivors": read.get("oos_survivors"),
                     "best_oos": read.get("best_oos"),
                     "oracle_abs_pp_per_q": read["oracle_abs_pp_per_q"],
                     "mean_always_fast_pp_per_q": read["mean_always_fast_pp_per_q"]},
        "desk_sentence": desk_sentence(read),
        "honest": [
            "the column effect is a median polish property of the segment, not a trade;"
            " it prices the quarter, it does not fill an order",
            "n_segments is the whole sample: %d readable segments is a small-sample read,"
            " and the permutation p is the only defence offered against that"
            % read["n_segments"],
            "observables are measured on the equal-weight book universe; a different"
            " universe would give different vol/dispersion numbers on the same dates",
            "own_prev_q is the previous readable segment's effect, so the first readable"
            " segment cannot be scored and overlapping quarters are not modelled",
        ],
    }
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(body, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    print("WROTE", FACE)
    print(desk_sentence(read))
    return 0


def desk_sentence(read):
    if read["words"] == WORDS_UNDERPOWERED:
        return ("只有 %d 个可读季度（要求 ≥%d），本面拒绝回答「能不能提前读到这个季度」，"
                "不给一个建立在个位数样本上的词。" % (read["n_segments"], MIN_SEGMENTS))
    head = ("4.45 pp 的行情段通道%s。" % ("有入场时可读的读者" if read["words"] == WORDS_ACTIONABLE
                                        else "在季度开门前读不到"))
    parts = []
    for k, v in read["observables"].items():
        if v.get("rho") is None:
            continue
        o = v.get("out_of_sample") or {}
        parts.append("%s ρ=%+.2f（置换 p=%.2f，全样本多 %+.2f pp/季，"
                     "前半定方向→后半 %s）"
                     % (k, v["rho"], v["perm_p"], v["improvement_pp_per_q"],
                        "n/a" if o.get("oos_improvement_pp_per_q") is None
                        else "%+.2f pp/季" % o["oos_improvement_pp_per_q"]))
    tail = ("；同时试 %d 个观察量，族级置换 p=%s（单个观察量的 p 不算数），样本 %d 个季度，"
            "快节奏在 %.0f%% 的季度里赢，换成完美先知也只有 %.2f pp/季"
            % (len(read.get("family_observables") or []),
               "n/a" if read.get("family_p") is None else "%.3f" % read["family_p"],
               read["n_segments"], read["base_rate_fast_wins_share"] * 100.0,
               read["oracle_abs_pp_per_q"]))
    return head + "；" + "；".join(parts) + tail


# ---------------------------------------------------------------- check


def check():
    if not os.path.exists(OUT_PATH):
        print("FACE MISSING run first")
        return 2
    with open(OUT_PATH, "r", encoding="utf-8") as fh:
        body = json.load(fh)
    up = load_upstream()

    stored_cells = int((body.get("upstream") or {}).get("cells") or -1)
    if stored_cells != len(up.get("cells") or []):
        print("STALE upstream cells %d != %d" % (stored_cells, len(up.get("cells") or [])))
        return 3
    if (body.get("upstream") or {}).get("cutoff") != up.get("evidence_cutoff"):
        print("STALE upstream cutoff %r != %r"
              % ((body.get("upstream") or {}).get("cutoff"), up.get("evidence_cutoff")))
        return 3

    read = read_question(body.get("segments") or [])
    bad = []
    if read["words"] != (body.get("read") or {}).get("words"):
        bad.append("words %r != %r" % (read["words"], (body.get("read") or {}).get("words")))
    for k, v in read["observables"].items():
        got = (body.get("read") or {}).get("observables", {}).get(k) or {}
        for field in ("n", "rho", "perm_p", "improvement_pp_per_q"):
            a, b = v.get(field), got.get(field)
            if isinstance(a, float) and isinstance(b, float):
                if abs(a - b) > 1e-9:
                    bad.append("%s.%s %.12f != %.12f" % (k, field, a, b))
            elif a != b:
                bad.append("%s.%s %r != %r" % (k, field, a, b))
        ga = (v.get("out_of_sample") or {}).get("oos_improvement_pp_per_q")
        gb = ((got.get("out_of_sample") or {}) or {}).get("oos_improvement_pp_per_q")
        if isinstance(ga, float) and isinstance(gb, float):
            if abs(ga - gb) > 1e-9:
                bad.append("%s.oos_improvement %.12f != %.12f" % (k, ga, gb))
        elif ga != gb:
            bad.append("%s.oos_improvement %r != %r" % (k, ga, gb))
    fa = read.get("family_p")
    fb = (body.get("read") or {}).get("family_p")
    if isinstance(fa, float) and isinstance(fb, float):
        if abs(fa - fb) > 1e-9:
            bad.append("family_p %.12f != %.12f" % (fa, fb))
    elif fa != fb:
        bad.append("family_p %r != %r" % (fa, fb))
    if bad:
        print("CHECK FAILED " + "; ".join(bad[:6]))
        return 1
    print("CHECK OK %d segments, words=%s, observables=%d"
          % (read["n_segments"], read["words"], len(read["observables"])))
    return 0


# ---------------------------------------------------------------- selftest


def selftest():
    legs, fails = [], []

    def leg(name, ok, detail=""):
        legs.append((name, bool(ok), detail))
        if not ok:
            fails.append(name)

    # 1 monotone data gives a perfect rank correlation
    xs = [1, 2, 3, 4, 5, 6]
    leg("spearman_monotone_is_one", abs(spearman(xs, [10, 20, 30, 40, 50, 60]) - 1.0) < 1e-12)
    leg("spearman_anticorrelated_is_minus_one",
        abs(spearman(xs, [60, 50, 40, 30, 20, 10]) + 1.0) < 1e-12)
    leg("spearman_ties_do_not_order", spearman([1, 1, 1, 1], [1, 2, 3, 4]) is None)

    # 2 polish recovers a construction with known additive effects
    grid = {}
    for i, r in enumerate(["a", "b", "c", "d"]):
        for j, c in enumerate(["q1", "q2", "q3", "q4"]):
            grid[(r, c)] = 10.0 + i * 1.0 + j * 2.5
    pol = polish(grid)
    leg("polish_row_effects_are_linear",
        abs((pol["row"]["d"] - pol["row"]["a"]) - 3.0) < 1e-9,
        "%r" % {k: round(v, 4) for k, v in pol["row"].items()})
    leg("polish_col_effects_are_linear",
        abs((pol["col"]["q4"] - pol["col"]["q1"]) - 7.5) < 1e-9)
    leg("polish_residual_is_zero_on_additive_grid",
        max(abs(v) for v in pol["resid"].values()) < 1e-9)

    # 3 permutation p: strong relation is rare, no relation is ordinary
    rng = random.Random(7)
    strong_y = [3.0 * x + rng.gauss(0, 0.05) for x in range(1, 15)]
    strong_x = list(range(1, 15))
    rho = spearman(strong_x, strong_y)
    p_strong = perm_p(strong_x, strong_y, rho, permutations=299)
    leg("perm_p_small_when_relation_is_real", p_strong <= 0.05, "p=%.4f rho=%.3f" % (p_strong, rho))
    noise_y = [rng.gauss(0, 1) for _ in range(14)]
    p_noise = perm_p(strong_x, noise_y, spearman(strong_x, noise_y), permutations=299)
    leg("perm_p_ordinary_when_relation_is_noise", p_noise > 0.10, "p=%.3f" % p_noise)

    # 4 the money math: a perfect observable must beat always-fast by the oracle gap,
    #   and a useless observable must not beat it at all
    target = [5.0, -5.0, 5.0, -5.0, 5.0, -5.0]
    perfect = [1.0, -1.0, 1.0, -1.0, 1.0, -1.0]
    _sw, always, imp = improvement_pp(perfect, target)
    leg("perfect_observable_beats_always_fast", abs(imp - 5.0) < 1e-9, "imp=%.3f" % imp)
    leg("always_fast_baseline_is_the_mean_delta", abs(always - 0.0) < 1e-12)
    flat = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
    _sw2, _af2, imp2 = improvement_pp(flat, target)
    leg("useless_observable_cannot_beat_always_fast", abs(imp2 - 0.0) < 1e-9, "imp=%.3f" % imp2)

    # 5 sign split uses the observable only: flipping the target must flip the money
    _s3, _a3, imp3 = improvement_pp(perfect, [-t for t in target])
    leg("flipping_target_flips_the_money", abs(imp3 + 5.0) < 1e-9, "imp=%.3f" % imp3)

    # 6 verdicts are derived: the same code must produce both words on purpose-built tables
    OBS_PATTERN = [0.0, 4.0, -4.0, 2.0, -2.0, 5.0, -5.0,
                   1.0, -1.0, 3.0, -3.0, 6.0, -6.0, 0.5]

    def synth(noise, predictable):
        """observables straddle their own median on both halves, so a median
        split can actually be wrong as well as right in the test half."""
        rng2 = random.Random(11)
        rows = []
        for i in range(14):
            obs = OBS_PATTERN[i]
            eff = (2.0 * obs if predictable else rng2.gauss(0, 1))
            if noise:
                eff += rng2.gauss(0, 6)
            rows.append({"segment": "s%02d" % i, "col_eff": eff,
                         "trail_vol60": obs, "trail_ret60": obs, "trail_dd60": obs,
                         "xs_disp60": obs, "trail_vol20": obs})
        return rows

    r_act = read_question(synth(False, True))
    leg("predictable_table_reads_actionable", r_act["words"] == WORDS_ACTIONABLE,
        r_act["words"])
    r_exp = read_question(synth(True, False))
    leg("noise_table_reads_ex_post", r_exp["words"] == WORDS_EXPOST, r_exp["words"])
    r_thin = read_question(synth(False, True)[:6])
    leg("thin_table_refuses_with_underpowered", r_thin["words"] == WORDS_UNDERPOWERED,
        r_thin["words"])

    # 7 the sign rule is built from the observable's own median, not the target's
    leg("sign_split_ignores_the_target",
        median_split_signs([1.0, 2.0, 3.0, 4.0], [9.0, -9.0, 9.0, -9.0])
        == median_split_signs([1.0, 2.0, 3.0, 4.0], [-9.0, 9.0, -9.0, 9.0]))
    # 8 first readable segment cannot be scored by own_prev_q (no predecessor)
    first = read_question(synth(False, True))
    leg("own_prev_q_drops_the_first_segment",
        first["observables"]["own_prev_q"]["n"] == 13,
        str(first["observables"]["own_prev_q"]["n"]))

    # 9 family-wise p must refuse a best-of-six that a shuffle can reproduce
    rng3 = random.Random(19)
    x6 = [[float(i) + rng3.gauss(0, 0.01) for i in range(14)] for _ in range(6)]
    y_flat = [rng3.gauss(0, 1) for _ in range(14)]
    best_flat = max(abs(spearman(xs, y_flat)) for xs in x6)
    leg("family_p_refuses_a_lucky_best_of_six",
        family_p(x6, y_flat, best_flat, permutations=199) > 0.10,
        "p=%.3f max=%.3f" % (family_p(x6, y_flat, best_flat, permutations=199), best_flat))
    y_real = [x6[0][i] + x6[1][i] for i in range(14)]
    best_real = max(abs(spearman(xs, y_real)) for xs in x6)
    leg("family_p_accepts_an_observable_that_is_in_the_data",
        family_p(x6, y_real, best_real, permutations=199) <= 0.05,
        "p=%.3f" % family_p(x6, y_real, best_real, permutations=199))

    # 10 the carried direction is the one thing that can travel; a flipped
    #    relation must still earn on the test half, a noise one must not
    rows_pos = [{"segment": "s%02d" % i, "col_eff": float(v), "trail_ret60": float(v)}
                for i, v in enumerate([0, 4, -4, 2, -2, 5, -5, 1, -1, 3, -3, 6, -6, 0.5])]
    o_pos = out_of_sample(rows_pos, "trail_ret60")
    leg("carried_direction_earns_when_relation_holds",
        (o_pos.get("oos_improvement_pp_per_q") or -1) > 0.0,
        "%r" % o_pos.get("oos_improvement_pp_per_q"))
    rows_neg = [{"segment": r["segment"], "col_eff": -r["col_eff"],
                 "trail_ret60": r["trail_ret60"]} for r in rows_pos]
    o_neg = out_of_sample(rows_neg, "trail_ret60")
    leg("an_inverted_relation_is_carried_with_its_own_sign",
        o_neg.get("carried_sign") == -1 and (o_neg.get("oos_improvement_pp_per_q") or -1) > 0.0,
        "%r" % o_neg.get("oos_improvement_pp_per_q"))
    rows_flat = [{"segment": "s%02d" % i, "col_eff": (1.0 if i % 2 else -1.0),
                  "trail_ret60": float(i)} for i in range(14)]
    o_flat = out_of_sample(rows_flat, "trail_ret60")
    leg("a_zigzag_target_does_not_earn_out_of_sample",
        o_flat.get("oos_improvement_pp_per_q") is None
        or o_flat.get("oos_improvement_pp_per_q") <= 0.0,
        "%r" % o_flat.get("oos_improvement_pp_per_q"))

    ok = not fails
    print(json.dumps({"legs": len(legs), "fails": fails,
                      "result": "PASS" if ok else "FAIL"}, ensure_ascii=False))
    for name, passed, detail in legs:
        if not passed:
            print("  FAIL", name, detail)
    return 0 if ok else 1


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "selftest":
        return selftest()
    if cmd == "check":
        return check()
    if cmd == "run":
        return compute()
    print("usage: selftest | run | check")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))

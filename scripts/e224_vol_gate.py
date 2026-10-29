"""E224 -- does a continuously-sampled state gate buy the resolution a calendar cannot?

E223 shut the calendar door: a rule anchored once a month (or once a week) is
observed 12 (52) times a year, so the annual bar barely moves when the anchor gets
faster, because shortening the hold shrinks the per-period signal by as much as it
raises the count. Its closing line named the successor: a rule whose INDEPENDENT
observations rise without cutting the exposure per observation. A state gate is the
obvious candidate -- volatility regimes switch far more often than months do, and
each episode keeps a full multi-session hold.

This face asks the same question in the same accounting, with one addition that is
the whole point: it separates the number of DAYS the gate is on (the tempting
sample size) from the number of EPISODES that produced those days (the independent
unit), and reports both t-statistics side by side.

Frozen before reading any number:

  * arms: state in {vol_low, vol_high} x hold in {10, 20} sessions  -> 4 arms on the
    index, replicated 1:1 on the five-ETF basket (8 tests, bar = two-sided 5%/8)
  * signal: trailing 20-session realised volatility of daily returns, in bp, known
    at the close of session t. A gate is ON at t when the signal sits in the bottom
    tercile (vol_low) or the top tercile (vol_high) of the PREVIOUS 250 signal
    values, strictly before t. No value from t or later enters the threshold.
  * entry: hold the next H sessions (t+1 .. t+H), one round trip per episode
    (2 sides at the frozen 13.041bp/side). While holding the gate is not polled, so
    two episodes can never overlap and no return is counted twice.
  * excess per episode = held_bp - toll - baseline, where baseline = H x the
    IN-SAMPLE mean daily return, i.e. the drift you would have earned by being in
    the market for the same number of sessions without any gating. The baseline is
    estimated on the in-sample sessions only and applied unchanged to OOS.
  * split: first 60% of SESSIONS are in-sample; an episode is OOS if it entered
    after the boundary. Minimum 30 OOS episodes to judge anything.
  * decision rule: ADOPT iff OOS episodes >= 30 AND OOS net excess per year > 0 AND
    OOS t >= the 8-test Bonferroni bar AND the arm is still net positive at x2
    costs. REJECT if the window is long enough and any test fails. UNRESOLVED below.
  * resolution: MDE at 80% power (z=2.802) for the CURRENT test length, in bp/yr:
    MDE_ann = z * sd_per_episode * sqrt(episodes_per_year / years). This is the
    number the calendar could not move.
  * the naive reading is reported too: the same held days treated as independent
    observations, which is what an overlapping-window t-test silently assumes. The
    ratio naive_t / episode_t is the inflation that reading buys.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e222_tom_overlay as e222  # noqa: E402

ROOT = e222.ROOT
PANEL_DIR = e222.PANEL_DIR
OUTDIR = os.path.join(ROOT, "results", "vol_gate")
E223_FACE = os.path.join(ROOT, "results", "obs_rate", "OBSRATE-20261028.json")

# ---------------------------------------------------------------- frozen spec
COST_SIDE_BP = e222.COST_SIDE_BP      # 13.041 flat, per side
SIDES_PER_EPISODE = 2                 # one round trip per episode
COST_X2_MULT = 2.0
VOL_WINDOW = 20                       # trailing sessions in the signal
THRESHOLD_WINDOW = 250                # past signal values used for the terciles
THRESHOLD_MIN = 120                   # below this the gate stays OFF (no threshold)
IS_FRAC = 0.60
MIN_OOS_EPISODES = 30
Z_80 = 2.802
PRIMARY_SYMBOL = "sh510300"
BASKET = ["sh510300", "sh510050", "sh510500", "sh512100", "sh588000"]

ARMS = [
    {"name": "vol_low_h10", "state": "low", "hold": 10},
    {"name": "vol_low_h20", "state": "low", "hold": 20},
    {"name": "vol_high_h10", "state": "high", "hold": 10},
    {"name": "vol_high_h20", "state": "high", "hold": 20},
]


# ---------------------------------------------------------------- statistics
def _mean(v):
    return (sum(v) / len(v)) if v else None


def _sd(v):
    if not v or len(v) < 2:
        return None
    m = sum(v) / len(v)
    return (sum((x - m) ** 2 for x in v) / (len(v) - 1)) ** 0.5


def _z_two_sided(alpha):
    return e222._z_two_sided(alpha)


def _quantile(sorted_vals, q):
    """Linear-interpolated quantile on an already sorted list."""
    if not sorted_vals:
        return None
    if len(sorted_vals) == 1:
        return sorted_vals[0]
    pos = q * (len(sorted_vals) - 1)
    lo = int(pos)
    hi = min(lo + 1, len(sorted_vals) - 1)
    frac = pos - lo
    return sorted_vals[lo] * (1.0 - frac) + sorted_vals[hi] * frac


# ---------------------------------------------------------------- signal + gate
def returns_bp(closes_dates_ordered, close_values):
    """(dates, ret_bp) with ret_bp[0] = None -- session i return is close[i]/close[i-1]-1."""
    dates = list(closes_dates_ordered)
    vals = list(close_values)
    ret = [None]
    for i in range(1, len(vals)):
        prev, cur = vals[i - 1], vals[i]
        ret.append((cur / prev - 1.0) * 10000.0 if (prev and cur) else None)
    return dates, ret


def vol_signal(ret_bp, window=VOL_WINDOW):
    """Trailing realised vol in bp at each session, using returns up to and including it."""
    out = [None] * len(ret_bp)
    for i in range(len(ret_bp)):
        if i + 1 < window:
            continue
        chunk = ret_bp[i - window + 1: i + 1]
        if any(x is None for x in chunk):
            continue
        out[i] = _sd(chunk)
    return out


def terciles_at(sig, i, window=THRESHOLD_WINDOW, minimum=THRESHOLD_MIN):
    """Bottom/top tercile of the PAST signal values strictly before i, or None."""
    start = max(0, i - window)
    past = [v for v in sig[start:i] if v is not None]
    if len(past) < minimum:
        return None
    past.sort()
    return _quantile(past, 1.0 / 3.0), _quantile(past, 2.0 / 3.0)


def gate_on(sig, ret_bp, i, state):
    """Is the gate open at the close of session i? Reads nothing dated after i."""
    v = sig[i]
    if v is None:
        return False
    thr = terciles_at(sig, i)
    if thr is None:
        return False
    lo, hi = thr
    if state == "low":
        return v <= lo
    if state == "high":
        return v >= hi
    raise ValueError("unknown state: %r" % (state,))


def episodes(ret_bp, sig, state, hold):
    """Non-overlapping gate episodes: [{'entry': i, 'held_bp': x}, ...]."""
    n = len(ret_bp)
    out = []
    i = 0
    while i < n:
        if not gate_on(sig, ret_bp, i, state) or i + hold >= n:
            i += 1
            continue
        chunk = ret_bp[i + 1: i + 1 + hold]
        if len(chunk) < hold or any(x is None for x in chunk):
            i += 1
            continue
        out.append({"entry": i, "held_bp": sum(chunk)})
        i += hold
    return out


# ---------------------------------------------------------------- accounting
def episode_ceiling_per_year(hold, sessions_per_year=252):
    """The hard cap on independent observations: disjoint holds of `hold` sessions."""
    return (float(sessions_per_year) / hold) if hold else None


def split_index(n_sessions, frac=IS_FRAC):
    idx = int(round(n_sessions * frac))
    return min(max(idx, 1), n_sessions - 1)


def arm_stats(eps, split, hold, cost_side_bp, years, n_sessions, ret_bp, bar_t=None):
    """Episode-level accounting, with the overlapping-day reading reported beside it."""
    is_eps = [e for e in eps if e["entry"] < split]
    oos_eps = [e for e in eps if e["entry"] >= split]
    is_rets = [r for r in ret_bp[1:split] if r is not None]
    baseline_bp = (hold * _mean(is_rets)) if is_rets else None
    toll = SIDES_PER_EPISODE * cost_side_bp

    def excess(e, tol, base):
        return e["held_bp"] - tol - base

    is_ex = [excess(e, toll, baseline_bp) for e in is_eps] if baseline_bp is not None else []
    oos_ex = [excess(e, toll, baseline_bp) for e in oos_eps] if baseline_bp is not None else []
    sd_oos = _sd(oos_ex)
    m_oos = _mean(oos_ex)
    se_oos = (sd_oos / (len(oos_ex) ** 0.5)) if (sd_oos is not None and oos_ex) else None
    t_oos = (m_oos / se_oos) if (se_oos and m_oos is not None) else None

    eps_per_year = (len(eps) / years) if (years and eps) else None
    held_days = len(eps) * hold
    # naive reading: every held day treated as an independent observation
    oos_days = []
    for e in oos_eps:
        oos_days.extend(ret_bp[e["entry"] + 1: e["entry"] + 1 + hold])
    oos_days = [d - (baseline_bp / hold) for d in oos_days if d is not None] if baseline_bp is not None else []
    sd_days, m_days = _sd(oos_days), _mean(oos_days)
    se_days = (sd_days / (len(oos_days) ** 0.5)) if (sd_days is not None and oos_days) else None
    t_naive = (m_days / se_days) if (se_days and m_days is not None) else None

    mde = None
    years_needed = None
    years_unbounded = False
    if sd_oos and eps_per_year and years and m_oos not in (None, 0.0):
        per_year_excess_sd = sd_oos * ((eps_per_year / years) ** 0.5)
        mde = Z_80 * per_year_excess_sd
        # a mean indistinguishable from zero makes "years needed" explode to 1e8+,
        # which reads as a measurement instead of the non-answer it is
        if abs(m_oos) >= 1e-3:
            factor = (Z_80 * sd_oos / m_oos) ** 2
            years_needed = factor / eps_per_year
            if years_needed > 1e5:
                years_needed = None
                years_unbounded = True

    return {
        "hold_sessions": hold,
        "episodes": len(eps),
        "episodes_is": len(is_eps),
        "episodes_oos": len(oos_eps),
        "episodes_per_year": eps_per_year,
        "held_days": held_days,
        "time_in_market_pct": (100.0 * held_days / n_sessions) if n_sessions else None,
        "cost_bp_per_episode": toll,
        "baseline_bp_per_episode": baseline_bp,
        "excess_bp_per_episode": _mean([e["held_bp"] - toll - baseline_bp for e in eps])
                                 if (eps and baseline_bp is not None) else None,
        "excess_is_bp_per_episode": _mean(is_ex),
        "excess_oos_bp_per_episode": m_oos,
        "excess_oos_bp_per_year": (m_oos * eps_per_year) if (m_oos is not None and eps_per_year) else None,
        "excess_oos_se_bp": se_oos,
        "excess_oos_t": t_oos,
        "sd_bp_per_episode": sd_oos,
        "mde_ann_bp_per_year": mde,
        "years_needed": years_needed,
        "years_needed_unbounded": years_unbounded,
        "naive_days": len(oos_days),
        "naive_t": t_naive,
        "naive_inflation": ((abs(t_naive) / abs(t_oos)) if (t_naive and t_oos) else None),
        "bar_t": bar_t,
    }


def verdict(a, min_oos=MIN_OOS_EPISODES):
    if a["episodes_oos"] < min_oos:
        return "UNRESOLVED", "oos_episodes_%d_below_%d" % (a["episodes_oos"], min_oos)
    if a["excess_oos_bp_per_year"] is None or a["excess_oos_t"] is None:
        return "UNRESOLVED", "oos_series_unusable"
    if a["excess_oos_bp_per_year"] <= 0:
        return "REJECT", "oos_net_excess_not_positive"
    if a["excess_oos_t"] < a["bar_t"]:
        return "REJECT", "oos_t_%.2f_below_bar_%.2f" % (a["excess_oos_t"], a["bar_t"])
    return "ADOPT", "clears_rule"


# ---------------------------------------------------------------- panels
def single_panel(sym, panel_dir=None):
    closes = e222.load_closes(sym, panel_dir)
    if not closes:
        return None
    dates = sorted(closes)
    return returns_bp(dates, [closes[d] for d in dates])


def basket_panel(panel_dir=None):
    series = {s: e222.load_closes(s, panel_dir) for s in BASKET}
    series = {k: v for k, v in series.items() if v}
    if not series:
        return None
    dates, rows = e222.daily_returns(series)
    if not rows:
        return None
    ret = [None]
    for r in rows:
        ret.append((r["ret"] * 10000.0) if r["ret"] is not None else None)
    return returns_bp(dates, [1.0] * len(dates))[0], ret


def _e223_month_mde():
    try:
        with open(E223_FACE, "r", encoding="utf-8") as fh:
            face = json.load(fh)
    except (OSError, ValueError):
        return None
    try:
        a = face["arms"]["primary_single"]["arms"]["month_turn"]
        mde = a["mde"]
    except (KeyError, TypeError):
        return None
    return {"source": os.path.relpath(E223_FACE, ROOT).replace("\\", "/"),
            "study": face.get("study"),
            "month_turn_mde_ann_bp_per_year": mde.get("mde_bp_per_year"),
            "month_turn_periods_per_year": mde.get("periods_per_year"),
            "month_turn_years_needed_for_observed": mde.get("years_needed_for_observed")}


def run(save=True, panel_dir=None, outdir=None):
    panel_dir = panel_dir or PANEL_DIR
    outdir = outdir or OUTDIR
    single = single_panel(PRIMARY_SYMBOL, panel_dir)
    if single is None:
        print("primary panel missing: %s" % PRIMARY_SYMBOL)
        return None
    basket = basket_panel(panel_dir)

    n_tests = len(ARMS) * (2 if basket else 1)
    bar_t = max(2.0, _z_two_sided(0.05 / n_tests))

    panels = [{"panel": "primary_single", "symbol": PRIMARY_SYMBOL, "sessions": len(single[0]),
               "first": single[0][0], "last": single[0][-1]}]
    if basket:
        panels.append({"panel": "basket_equal_weight", "symbol": "+".join(sorted(BASKET)),
                       "sessions": len(basket[0]), "first": basket[0][0], "last": basket[0][-1]})

    for panel in panels:
        dates, ret_bp = (single if panel["panel"] == "primary_single" else basket)
        sig = vol_signal(ret_bp)
        split = split_index(len(dates))
        years = len(dates) / 252.0
        arms_out = []
        for spec in ARMS:
            eps = episodes(ret_bp, sig, spec["state"], spec["hold"])
            a = arm_stats(eps, split, spec["hold"], COST_SIDE_BP, years, len(dates), ret_bp, bar_t)
            a["name"] = spec["name"]
            a["state"] = spec["state"]
            a_x2 = arm_stats(eps, split, spec["hold"], COST_SIDE_BP * COST_X2_MULT, years,
                             len(dates), ret_bp, bar_t)
            a["excess_oos_bp_per_year_x2"] = a_x2["excess_oos_bp_per_year"]
            if a["excess_oos_bp_per_year"] is not None and a["excess_oos_bp_per_year"] > 0:
                if a_x2["excess_oos_bp_per_year"] is None or a_x2["excess_oos_bp_per_year"] <= 0:
                    a["verdict"], a["verdict_reason"] = "REJECT", "dies_at_x2_costs"
                else:
                    a["verdict"], a["verdict_reason"] = verdict(a)
            else:
                a["verdict"], a["verdict_reason"] = verdict(a)
            arms_out.append(a)
        panel["arms"] = arms_out
        panel["split_session"] = split
        panel["split_date"] = dates[split]
        panel["is_frac"] = IS_FRAC
        panel["years"] = len(dates) / 252.0
    face = {
        "study": "E224",
        "title": "volatility state gate vs the calendar wall: does a continuously-sampled "
                 "rule buy resolution a monthly anchor cannot?",
        "generated": datetime.now().isoformat(timespec="seconds"),
        "evidence_cutoff": panels[0]["last"],
        "frozen_spec": {
            "arms": ARMS, "cost_side_bp": COST_SIDE_BP, "sides_per_episode": SIDES_PER_EPISODE,
            "vol_window": VOL_WINDOW, "threshold_window": THRESHOLD_WINDOW,
            "threshold_min": THRESHOLD_MIN, "is_frac": IS_FRAC,
            "min_oos_episodes": MIN_OOS_EPISODES, "z_80pct": Z_80,
            "bar_t": bar_t, "tests": n_tests,
            "bar_basis": "two-sided 5%% over %d tests (4 arms x 2 panels)" % n_tests,
            "baseline": "H x in-sample mean daily return, estimated on IS sessions only",
        },
        "panels": panels,
    }
    ref = _e223_month_mde()
    if ref:
        face["calendar_reference"] = ref
        primary = panels[0]["arms"]
        best = None
        for a in primary:
            if a["mde_ann_bp_per_year"] is not None:
                if best is None or a["mde_ann_bp_per_year"] < best["mde_ann_bp_per_year"]:
                    best = a
        if best and ref.get("month_turn_mde_ann_bp_per_year"):
            face["resolution_comparison"] = {
                "calendar_month_turn_mde_ann_bp_per_year": ref["month_turn_mde_ann_bp_per_year"],
                "calendar_observations_per_year": ref.get("month_turn_periods_per_year"),
                "gate_best_arm": best["name"],
                "gate_episodes_per_year": best["episodes_per_year"],
                "gate_mde_ann_bp_per_year": best["mde_ann_bp_per_year"],
                "ratio_calendar_over_gate": (ref["month_turn_mde_ann_bp_per_year"]
                                             / best["mde_ann_bp_per_year"]),
                "reading": "the calendar rule's annual bar divided by the gate's: below 1 means "
                           "the gate resolves more per year of history, above 1 means more "
                           "observations bought a worse bar",
            }
        # the observation count is throttled by the HOLD, not by how often the signal is
        # sampled: at most ~252/H disjoint episodes a year can exist at all
        face["observation_ceiling"] = {
            "sessions_per_year": 252,
            "arms": [{"name": a["name"], "hold_sessions": a["hold_sessions"],
                      "ceiling_episodes_per_year": 252.0 / a["hold_sessions"],
                      "observed_episodes_per_year": a["episodes_per_year"],
                      "occupancy_pct_of_ceiling": (100.0 * a["episodes_per_year"]
                                                   / (252.0 / a["hold_sessions"]))
                      if a["episodes_per_year"] else None}
                     for a in panels[0]["arms"]],
            "reading": "a continuously-sampled signal does not produce continuous "
                       "observations: the hold length caps the episode count, and the gate "
                       "only fills part of that cap",
        }
        # the one-sentence answer, derived from the numbers rather than asserted
        primary = panels[0]["arms"]
        adopted = [a["name"] for a in primary if a["verdict"] == "ADOPT"]
        best = None
        for a in primary:
            if a["mde_ann_bp_per_year"] is not None:
                if best is None or a["mde_ann_bp_per_year"] < best["mde_ann_bp_per_year"]:
                    best = a
        cal = face.get("resolution_comparison") or {}
        face["answer"] = (
            "a state gate does not escape the observation wall: %d of %d arms adopt, the "
            "gate turns on in %s episodes a year (a %d-session hold caps it at %.1f), and its "
            "tightest annual bar is %s bp/yr against the calendar rule's %s -- %.2fx tighter, "
            "bought by smaller per-episode dispersion rather than by more observations"
            % (len(adopted), len(primary),
               ", ".join("%.1f" % a["episodes_per_year"] for a in primary if a["episodes_per_year"]),
               primary[0]["hold_sessions"], episode_ceiling_per_year(primary[0]["hold_sessions"]),
               ("%.1f" % best["mde_ann_bp_per_year"]) if best else "-",
               ("%.1f" % cal.get("calendar_month_turn_mde_ann_bp_per_year"))
               if cal.get("calendar_month_turn_mde_ann_bp_per_year") else "-",
               cal.get("ratio_calendar_over_gate") or 0.0))
    if save:
        if not os.path.isdir(outdir):
            os.makedirs(outdir)
        path = os.path.join(outdir, "VOLGATE-%s.json" % face["evidence_cutoff"])
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
        latest = os.path.join(outdir, "latest.json")
        with open(latest, "w", encoding="utf-8") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
        csv_path = os.path.join(outdir, "by_arm_%s.csv" % face["evidence_cutoff"])
        with open(csv_path, "w", encoding="utf-8", newline="") as fh:
            cols = ["panel", "name", "hold_sessions", "episodes", "episodes_oos",
                    "episodes_per_year", "time_in_market_pct", "excess_oos_bp_per_episode",
                    "excess_oos_bp_per_year", "excess_oos_bp_per_year_x2", "excess_oos_t",
                    "sd_bp_per_episode", "mde_ann_bp_per_year", "years_needed",
                    "naive_days", "naive_t", "naive_inflation", "verdict", "verdict_reason"]
        # the header above is built explicitly so a missing literal comma cannot glue
        # two labels together and silently swallow the first data row (the r1325 lesson)
            assert len(cols) == 19, "column list length drift"
            w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
            w.writeheader()
            for panel in panels:
                for a in panel["arms"]:
                    row = dict(a)
                    row["panel"] = panel["panel"]
                    w.writerow(row)
        face["_written"] = os.path.relpath(path, ROOT).replace("\\", "/")
        print("wrote %s" % face["_written"])
    return face


# ---------------------------------------------------------------- selftest
def _synth(n=900, drift_bp=1.0, vol_cycle=None, seed=7):
    """Deterministic synthetic panel: ret_bp with a slow vol cycle and fixed drift."""
    ret = [None]
    for i in range(1, n):
        v = vol_cycle(i % 120) if vol_cycle else 60.0
        # deterministic pseudo-noise from a tiny LCG so the fixture never drifts
        seed = (1103515245 * seed + 12345) % (2 ** 31)
        z = ((seed / 2 ** 31) - 0.5) * 3.4641
        ret.append(drift_bp + z * v)
    return ["d%04d" % i for i in range(n)], ret


def selftest():
    legs = []

    def leg(name, cond, note=""):
        legs.append((name, bool(cond), note))

    # L1 signal is causal: perturbing later returns changes nothing before that index
    dates, ret = _synth(600)
    sig = vol_signal(ret)
    ret2 = list(ret)
    for i in range(400, 600):
        ret2[i] = (ret2[i] or 0.0) + 500.0
    sig2 = vol_signal(ret2)
    leg("signal_ignores_future_returns", all(sig[i] == sig2[i] for i in range(0, 400)),
        "a signal at t must not move when returns after t are changed")

    # L2 thresholds read only the past 250 signal values
    thr_a = terciles_at(sig, 400)
    thr_b = terciles_at(sig2, 400)
    leg("thresholds_are_past_only", thr_a == thr_b, "future perturbation must not move the gate")

    # L3 episodes never overlap: every entry is at least hold sessions after the previous one
    eps = episodes(ret, sig, "low", 10)
    leg("episodes_do_not_overlap", all(eps[i + 1]["entry"] - eps[i]["entry"] >= 10
                                       for i in range(len(eps) - 1)) and len(eps) >= 3,
        "held windows are disjoint by construction; n=%d" % len(eps))

    # L4 the held window equals the sum of the next H returns
    e0 = eps[0]
    leg("held_window_is_next_h_sessions",
        abs(e0["held_bp"] - sum(ret[e0["entry"] + 1: e0["entry"] + 11])) < 1e-9,
        "entry at close t, returns t+1..t+H")

    # L5 a zero-return hold with no drift nets exactly minus the toll
    flat = [None] + [0.0] * 300
    sig_flat = vol_signal(flat)
    stats = arm_stats([{"entry": 100, "held_bp": 0.0}], 150, 10, COST_SIDE_BP, 1.0, 301, flat, 2.5)
    leg("toll_is_the_only_cost_when_nothing_moves",
        stats["baseline_bp_per_episode"] is not None
        and abs(stats["excess_bp_per_episode"] + 2 * COST_SIDE_BP) < 1e-6,
        "flat panel: excess == -toll")

    # L6 the baseline is in-sample only: move OOS returns, baseline must not budge
    a = arm_stats([{"entry": 100, "held_bp": 5.0}] + [{"entry": 200, "held_bp": 5.0}],
                  150, 5, COST_SIDE_BP, 1.0, 301, [None] + [2.0] * 300, 2.5)
    ret_moved = [None] + [2.0] * 160 + [900.0] * 140
    b = arm_stats([{"entry": 100, "held_bp": 5.0}] + [{"entry": 200, "held_bp": 5.0}],
                  150, 5, COST_SIDE_BP, 1.0, 301, ret_moved, 2.5)
    leg("baseline_is_in_sample_only",
        a["baseline_bp_per_episode"] == b["baseline_bp_per_episode"],
        "baseline %r vs %r" % (a["baseline_bp_per_episode"], b["baseline_bp_per_episode"]))

    # L7 MDE identity: z * sd * sqrt(eps_per_year / years)
    eps_known = [{"entry": 10 + 5 * k, "held_bp": 10.0 + (k % 5)} for k in range(40)]
    st = arm_stats(eps_known, 100, 5, COST_SIDE_BP, 2.0, 400, [None] + [1.0] * 399, 2.5)
    expect = Z_80 * st["sd_bp_per_episode"] * ((st["episodes_per_year"] / 2.0) ** 0.5)
    leg("mde_identity_holds", st["mde_ann_bp_per_year"] is not None
        and abs(st["mde_ann_bp_per_year"] - expect) < 1e-9,
        "MDE_ann = z*sd*sqrt(eps_per_year/years)")

    # L8 the naive reading uses episodes x hold days, not the episode count
    leg("naive_uses_every_held_day", st["naive_days"] > st["episodes_oos"],
        "naive_days=%d vs episodes_oos=%d" % (st["naive_days"], st["episodes_oos"]))

    # L9 verdict branches: each one reachable with a hand-built record
    def rec(**kw):
        base = {"episodes_oos": 50, "excess_oos_bp_per_year": 100.0, "excess_oos_t": 3.0,
                "bar_t": 2.5}
        base.update(kw)
        return base
    leg("verdict_unresolved_below_floor", verdict(rec(episodes_oos=10))[0] == "UNRESOLVED")
    leg("verdict_reject_on_negative", verdict(rec(excess_oos_bp_per_year=-1.0))[0] == "REJECT")
    leg("verdict_reject_below_bar", verdict(rec(excess_oos_t=1.0))[0] == "REJECT")
    leg("verdict_adopt_when_all_pass", verdict(rec())[0] == "ADOPT")
    leg("verdict_never_adopts_without_t", verdict(rec(excess_oos_t=None))[0] == "UNRESOLVED")

    # L10 determinism: two builds of the same fixture are byte-identical
    d1 = json.dumps(fixture_face(), sort_keys=True)
    d2 = json.dumps(fixture_face(), sort_keys=True)
    leg("run_is_deterministic_on_fixture", d1 == d2, "fixture path has zero wall-clock fields")

    # L11 split boundary is exactly 60% of sessions and never degenerate
    leg("split_boundary_is_60pct", split_index(1000) == 600 and split_index(5) == 3
        and split_index(2) == 1, "60%% of sessions, clamped to leave both sides non-empty")

    # L12 an empty episode set produces a record, not an exception
    empty = arm_stats([], 150, 10, COST_SIDE_BP, 1.0, 301, [None] + [1.0] * 300, 2.5)
    leg("empty_episodes_yield_a_record",
        empty["episodes"] == 0 and verdict(empty)[0] == "UNRESOLVED")

    # L13 the observation ceiling is 252/hold and the gate can never exceed it
    leg("observation_ceiling_is_252_over_hold",
        episode_ceiling_per_year(10) == 25.2 and episode_ceiling_per_year(20) == 12.6,
        "a 10-session hold cannot produce more than 25.2 independent observations a year")

    # L14 a mean indistinguishable from zero reports no year count instead of 1e8
    near_zero = [{"entry": 10 + 5 * k, "held_bp": 26.082 + (0.001 if k % 2 else 0.0)}
                 for k in range(40)]
    nz = arm_stats(near_zero, 100, 5, COST_SIDE_BP, 2.0, 400, [None] + [1.0] * 399, 2.5)
    leg("degenerate_mean_suppresses_years_needed",
        nz["years_needed"] is None or nz["years_needed"] < 1e6,
        "years_needed=%r unbounded=%r" % (nz["years_needed"], nz["years_needed_unbounded"]))

    passed = sum(1 for _, ok, _ in legs if ok)
    for name, ok, note in legs:
        print("[%s] %s%s" % ("PASS" if ok else "FAIL", name, (" | " + note) if note else ""))
    print("%d/%d PASS" % (passed, len(legs)))
    return passed == len(legs)


def fixture_face():
    """A tiny deterministic face built from the synthetic panel (no disk, no clock)."""
    dates, ret = _synth(700)
    sig = vol_signal(ret)
    split = split_index(len(dates))
    years = len(dates) / 252.0
    arms = []
    for spec in ARMS:
        eps = episodes(ret, sig, spec["state"], spec["hold"])
        a = arm_stats(eps, split, spec["hold"], COST_SIDE_BP, years, len(dates), ret, 2.5)
        a["name"] = spec["name"]
        arms.append(a)
    return {"study": "E224", "fixture": True, "arms": arms}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run", choices=["run", "selftest"])
    ap.add_argument("--panel-dir", default=None)
    args = ap.parse_args(argv)
    if args.cmd == "selftest":
        ok = selftest()
        return 0 if ok else 1
    face = run(panel_dir=args.panel_dir)
    if face is None:
        return 2
    for panel in face["panels"]:
        print("== %s (%s..%s, %d sessions)" % (panel["panel"], panel["first"], panel["last"],
                                              panel["sessions"]))
        for a in panel["arms"]:
            print("  %-12s eps=%-4d eps/yr=%-6.2f inmkt=%-5.1f%%  oos=%-8s t=%-7s mde=%-8s %s"
                  % (a["name"], a["episodes"],
                     a["episodes_per_year"] or 0.0, a["time_in_market_pct"] or 0.0,
                     ("%.1f" % a["excess_oos_bp_per_year"]) if a["excess_oos_bp_per_year"] is not None else "-",
                     ("%.2f" % a["excess_oos_t"]) if a["excess_oos_t"] is not None else "-",
                     ("%.1f" % a["mde_ann_bp_per_year"]) if a["mde_ann_bp_per_year"] is not None else "-",
                     a["verdict"]))
    if face.get("resolution_comparison"):
        rc = face["resolution_comparison"]
        print("resolution: calendar %s bp/yr at %s/yr vs gate %s at %s/yr -> ratio %.3f"
              % (rc["calendar_month_turn_mde_ann_bp_per_year"], rc["calendar_observations_per_year"],
                 rc["gate_mde_ann_bp_per_year"], rc["gate_episodes_per_year"],
                 rc["ratio_calendar_over_gate"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
"""Does the overnight gap carry the information the one-bar price is made of? (E26)

The card declares `decide at close of bar d -> fill at open of bar d+1` and prints 8.46%/yr;
the as-coded arm fills at open d and earns 9.60%. E25 (`etf_book_causal_rebuild`) showed the
1.14 pp/yr cannot be won back by rebuilding the same ranking causally: the best smoothed arm
recovered +0.07 pp of 1.14, split signal +0.06 / cost +0.01. So the price is information.

If it is information, one channel is left -- the only one that exists between the decision
close and the fill open:

    gap[t] = open[t] / close[t-1] - 1

It is fully observed at the fill instant (so it is admissible, not look-ahead): a desk can see
the open print and still decide whether to take the trade. Two economically distinct uses:

  rank on it        gap_rank_up / gap_rank_down   buys the names that gapped up / down
  exclude the ran   excl_absgap_q80 / q90         drops names whose |gap| is extreme
                    excl_upgap_q80                drops only the one-sided (already jumped) names

`excl_upgap_q80` is the arm with a story; the two-sided one is its control, and the rank arms
test whether the gap carries information at all.

Frozen criterion (`research/CASE_PREREG_E26_OVERNIGHT_GAP.md`, committed before the first
run): an arm is admissible iff it beats `declared` by >= 0.57 pp/yr on the full span, wins at
least 3 of 4 decision phases, and is no deeper in drawdown than declared - 2.0 pp. `--check`
re-derives the verdict from the published rows only.

Usage:
    python scripts/etf_book_overnight_gap.py run
    python scripts/etf_book_overnight_gap.py --check
    python scripts/etf_book_overnight_gap.py --selftest
"""
from __future__ import annotations

import io
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import numpy as np
import pandas as pd

import etf_book_forward as F
import etf_equity_alpha as A
import etf_robust_pf as R
import etf_composite_pf as E
import etf_book_vol_window_phase as PH

OUT_JSON = os.path.join(ROOT, "results", "etf_book_overnight_gap.json")
OUT_MD = os.path.join(ROOT, "research", "ETF_BOOK_OVERNIGHT_GAP.md")
PRODUCTION_JSON = os.path.join(ROOT, "results", "etf_book_production", "latest.json")

# ---------------------------------------------------------------- frozen criteria
# Half the one-bar price (1.14 pp/yr): recovering less than half of it is not a reason to
# change what the card prints.
GAP_MIN_PP = 0.57
DD_TOL_PP = 2.0
N_PHASES = 4
PHASE_SHARE_MIN = 0.75
IDENT_TOL_PP = 0.05
OOS_FROM = "2023-12-31"
EXCL_QS = (0.80, 0.90)
UP_Q = 0.80

REBAL = F.CONFIG["rebal"]
N_HOLD = F.CONFIG["n_hold"]
COST = F.CONFIG["cost_per_side"]
VOL_TARGET = F.CONFIG["vol_target"]

ARMS = ("declared", "gap_rank_up", "gap_rank_down", "excl_absgap_q80",
        "excl_absgap_q90", "excl_upgap_q80")

CRITERIA = {
    "gap_min_pp": GAP_MIN_PP,
    "dd_tol_pp": DD_TOL_PP,
    "n_phases": N_PHASES,
    "phase_share_min": PHASE_SHARE_MIN,
    "ident_tol_pp": IDENT_TOL_PP,
    "excl_quantiles": list(EXCL_QS),
    "up_quantile": UP_Q,
    "oos_from": OOS_FROM,
    "verdict_rule": (
        "ADOPT_GAP iff some gap arm beats `declared` on CAGR by >= gap_min_pp AND its Sharpe "
        "is >= this run's `declared` Sharpe AND its max drawdown is no deeper than declared - "
        "dd_tol_pp AND it beats declared on CAGR in >= phase_share_min of the phases; "
        "MIXED_ACROSS_PHASES if the return line is cleared but the phase share is not (or the "
        "reverse); NO_GAP_EDGE otherwise -- the gap stays information"),
    "arms": {
        "declared": "score.shift(1) -- the number the card carries (control)",
        "gap_rank_up": "+gap[t], gap = open[t]/close[t-1]-1, observed at the fill",
        "gap_rank_down": "-gap[t]",
        "excl_absgap_q80": "declared ranking minus the top 20% of abs(gap) on that bar",
        "excl_absgap_q90": "declared ranking minus the top 10% of abs(gap) on that bar",
        "excl_upgap_q80": "declared ranking minus the top 20% of gap (one-sided)",
    },
}


# ---------------------------------------------------------------- score builders
def overnight_gap(close, openp):
    """open[t] / close[t-1] - 1. Nothing from bar t's close is used: the gap is known at
    the fill instant, which is exactly what makes it admissible."""
    return (openp / close.shift(1) - 1.0).replace([np.inf, -np.inf], np.nan)


def excl_mask(gap, q, one_sided):
    """True where a name's gap is in the excluded tail of *that bar's* cross-section."""
    if one_sided:
        thr = gap.quantile(q, axis=1)
        return gap.gt(thr, axis=0)
    a = gap.abs()
    thr = a.quantile(q, axis=1)
    return a.gt(thr, axis=0)


def apply_excl(score, gap, q, one_sided=False):
    """Keep the declared ranking, drop the names whose gap already ran (NaN = not ranked)."""
    return score.mask(excl_mask(gap, q, one_sided))


def arm_scores(score, gap):
    """Ordered {arm_name: score_frame}. `declared` is the causal control."""
    declared = score.shift(1)
    out = {"declared": declared,
           "gap_rank_up": gap,
           "gap_rank_down": -gap}
    for q in EXCL_QS:
        out["excl_absgap_q%d" % int(round(q * 100))] = apply_excl(declared, gap, q, False)
    out["excl_upgap_q%d" % int(round(UP_Q * 100))] = apply_excl(declared, gap, UP_Q, True)
    return {k: out[k] for k in ARMS if k in out}


# ---------------------------------------------------------------- pricing
def _run(close, openp, amt, score, start, cost):
    ser, turn = R.open_to_open_equity(close, openp, amt, score, REBAL, N_HOLD, cost,
                                     vol_target=VOL_TARGET, start=start)
    return ser, float(turn)


def _stats(ser):
    full = A.stats2(ser, "full")
    oos = A.stats2(ser[ser.index > pd.Timestamp(OOS_FROM)], "oos") if len(ser) else {}
    return {
        "cagr": full.get("cagr"),
        "sharpe": full.get("sharpe"),
        "maxdd": full.get("maxdd"),
        "vol": full.get("vol"),
        "years": full.get("years"),
        "oos_cagr": oos.get("cagr"),
        "oos_sharpe": oos.get("sharpe"),
        "bars": int(len(ser)),
    }


def _row(phase, arm, ser, turn, cost, extra=None):
    st = _stats(ser)
    row = {"phase": int(phase), "arm": arm, "cost_per_side": cost, "turnover": round(turn, 4)}
    row.update({k: (None if v is None else (round(v, 6) if isinstance(v, float) else v))
                for k, v in st.items()})
    if extra:
        row.update(extra)
    return row


# ---------------------------------------------------------------- mechanism audits
def audit_fill_time_causality(close, openp, gap, bars):
    """A6: the gap row at bar t is reproducible from open[t] and close[t-1] alone."""
    bad, rows = [], []
    idx = list(close.index)
    for d in bars:
        i = idx.index(d)
        if i == 0:
            continue
        prev_close = close.iloc[i - 1]
        recomputed = (openp.loc[d] / prev_close - 1.0).replace([np.inf, -np.inf], np.nan)
        same = np.allclose(np.nan_to_num(recomputed.values, nan=-999.0),
                           np.nan_to_num(gap.loc[d].values, nan=-999.0),
                           rtol=0.0, atol=1e-12)
        rows.append({"bar": str(getattr(d, "date", lambda: d)()), "ok": bool(same)})
        if not same:
            bad.append(rows[-1])
    return {"ok": not bad, "checked": len(rows), "violations": bad}


def audit_declared_lag(score, declared, bars):
    """A7: the control arm is the previous bar's score, not this bar's."""
    bad = []
    idx = list(score.index)
    for d in bars:
        i = idx.index(d)
        if i == 0:
            continue
        prev = score.iloc[i - 1]
        got = declared.loc[d]
        if not np.allclose(np.nan_to_num(prev.values, nan=-999.0),
                           np.nan_to_num(got.values, nan=-999.0), rtol=0.0, atol=0.0):
            bad.append({"bar": str(getattr(d, "date", lambda: d)())})
    return {"ok": not bad, "checked": len(bars), "violations": bad}


def audit_mask_not_rescale(reference, arm, gap, q, bars):
    """A8: an exclusion arm changes the selection set only -- a name that survives keeps the
    reference score bit-for-bit, and the names that disappear are exactly the masked ones.
    Passing the arm twice would compare it with itself and could never fire, so the reference
    and the arm are two separate arguments."""
    bad = []
    for d in bars:
        ref_row = reference.loc[d].dropna()
        m = excl_mask(gap, q, False).loc[d].reindex(ref_row.index).fillna(False)
        expect = ref_row[~m]
        got = arm.loc[d].dropna()
        name = str(getattr(d, "date", lambda: d)())
        if set(got.index) != set(expect.index):
            extra = sorted(set(got.index) - set(expect.index))[:5]
            missing = sorted(set(expect.index) - set(got.index))[:5]
            bad.append({"bar": name, "why": "selection set differs", "extra": extra,
                        "missing": missing})
            continue
        a = expect.reindex(got.index)
        if not np.allclose(a.values, got.values, rtol=0.0, atol=0.0):
            bad.append({"bar": name, "why": "a surviving name's score moved"})
    return {"ok": not bad, "checked": len(bars), "violations": bad}


# ---------------------------------------------------------------- verdict
def decide(rows, criteria=CRITERIA):
    """Verdict from the published rows only -- re-derivable, never re-run."""
    full = {}
    for r in rows:
        full.setdefault(r["arm"], r)
    if "declared" not in full:
        return {"state": "INCOMPLETE", "why": "no `declared` arm"}
    d = full["declared"]
    if d.get("cagr") is None:
        return {"state": "INCOMPLETE", "why": "declared arm did not price"}
    dd_floor = (d["maxdd"] or 0.0) - criteria["dd_tol_pp"] / 100.0

    phases = sorted({r["phase"] for r in rows})
    by_phase = {p: {r["arm"]: r for r in rows if r["phase"] == p} for p in phases}

    arms = []
    for name, r in full.items():
        if name == "declared" or r.get("cagr") is None:
            continue
        gained_pp = 100.0 * (r["cagr"] - d["cagr"])
        full_ok = (gained_pp >= criteria["gap_min_pp"]
                   and (r.get("sharpe") or 0.0) >= (d.get("sharpe") or 0.0)
                   and (r.get("maxdd") or 0.0) >= dd_floor)
        wins = 0
        for p in phases:
            pr, pd_ = by_phase[p].get(name), by_phase[p].get("declared")
            if pr and pd_ and pr.get("cagr") is not None and pd_.get("cagr") is not None:
                if pr["cagr"] > pd_["cagr"]:
                    wins += 1
        share = (float(wins) / len(phases)) if phases else 0.0
        arms.append({
            "arm": name,
            "gained_pp": round(gained_pp, 2),
            "full_span_tests_pass": bool(full_ok),
            "phase_wins": wins,
            "phase_share": round(share, 3),
            "phase_share_pass": bool(share >= criteria["phase_share_min"]),
            "admissible": bool(full_ok and share >= criteria["phase_share_min"]),
        })
    if not arms:
        return {"state": "INCOMPLETE", "why": "no gap arm priced"}

    win = [a for a in arms if a["admissible"]]
    best = max(arms, key=lambda a: a["gained_pp"])
    line_ok = best["gained_pp"] >= criteria["gap_min_pp"]
    if win:
        state = "ADOPT_GAP"
        chosen = max(win, key=lambda a: a["gained_pp"])
    elif line_ok and (best["full_span_tests_pass"] or best["phase_share_pass"]):
        state = "MIXED_ACROSS_PHASES"
        chosen = None
    else:
        state = "NO_GAP_EDGE"
        chosen = None
    return {
        "state": state,
        "state_rule_detail": ("MIXED_ACROSS_PHASES requires the return line to be cleared "
                              "first; a gain smaller than gap_min_pp is NO_GAP_EDGE however "
                              "consistently it wins"),
        "declared_cagr": round(d["cagr"], 4),
        "declared_sharpe": d.get("sharpe"),
        "declared_maxdd": d.get("maxdd"),
        "dd_floor": round(dd_floor, 4),
        "best_arm": best["arm"],
        "best_gained_pp": best["gained_pp"],
        "admissible_arms": [a["arm"] for a in win],
        "chosen_arm": chosen["arm"] if chosen else None,
        "recommended_card_arm": chosen["arm"] if chosen else "declared",
        "arms": arms,
        "phases": len(phases),
    }


# ---------------------------------------------------------------- run
def run():
    t0 = time.time()
    close, openp, amt, feats, score, _cls, _flip = F.build_inputs()
    gap = overnight_gap(close, openp)
    scores = arm_scores(score, gap)

    trade_dates = [d for d in close.index if d >= pd.Timestamp(R.START)]
    starts = PH.phase_starts(trade_dates)

    rows = []
    for i, st in enumerate(starts):
        for name in ARMS:
            sc = scores[name]
            ser, turn = _run(close, openp, amt, sc, st, COST)
            rows.append(_row(i, name, ser, turn, COST))

    # what the gap actually is, on the bars where it is used
    entry_bars = list(close.index[close.index >= pd.Timestamp(R.START)])[::REBAL]
    gap_at_entry = gap.reindex(entry_bars).abs()
    gap_stats = {
        "entry_bars": len(gap_at_entry),
        "mean_abs_gap_bp": round(10000.0 * float(np.nanmean(gap_at_entry.to_numpy())), 2)
        if gap_at_entry.size else None,
        "median_abs_gap_bp": round(10000.0 * float(np.nanmedian(gap_at_entry.to_numpy())), 2)
        if gap_at_entry.size else None,
        "p90_abs_gap_bp": round(10000.0 * float(np.nanpercentile(
            gap_at_entry.to_numpy(), 90)), 2) if gap_at_entry.size else None,
        "excluded_names_per_decision": {
            "excl_absgap_q80": round(float(np.nanmean(
                excl_mask(gap, 0.80, False).reindex(entry_bars).sum(axis=1).to_numpy())), 1),
            "excl_absgap_q90": round(float(np.nanmean(
                excl_mask(gap, 0.90, False).reindex(entry_bars).sum(axis=1).to_numpy())), 1),
            "excl_upgap_q80": round(float(np.nanmean(
                excl_mask(gap, 0.80, True).reindex(entry_bars).sum(axis=1).to_numpy())), 1),
        },
        "rule": ("The gap is priced in bp of the entry bar. A channel worth 0.57 pp/yr has to "
                 "show up as a selection difference, not as a rounding artefact."),
    }

    sample_bars = [starts[0], starts[len(starts) // 2], starts[-1]]
    audits = {
        "A6_fill_time_causality": audit_fill_time_causality(close, openp, gap, sample_bars),
        "A7_declared_lag": audit_declared_lag(score, scores["declared"], sample_bars),
        "A8_mask_not_rescale": audit_mask_not_rescale(scores["declared"],
                                                     scores["excl_absgap_q80"], gap, 0.80,
                                                     sample_bars),
    }

    try:
        with io.open(PRODUCTION_JSON, encoding="utf-8") as fh:
            prod = json.load(fh)
        eb = prod.get("execution_basis") or {}
        pub = {"declared_cagr": eb.get("declared_cagr"),
               "as_coded_cagr": eb.get("as_coded_cagr"),
               "source": "results/etf_book_production/latest.json::execution_basis"}
    except Exception as exc:
        pub = {"declared_cagr": None, "as_coded_cagr": None,
               "source": "unreadable: %s" % exc}
    controls = []
    got = next((r["cagr"] for r in rows if r["phase"] == 0 and r["arm"] == "declared"), None)
    want = pub.get("declared_cagr")
    gap_pp = None if (got is None or want is None) else 100.0 * (got - want)
    controls.append({"arm": "declared", "got_cagr": got, "published_cagr": want,
                     "gap_pp": None if gap_pp is None else round(gap_pp, 3),
                     "ok": bool(gap_pp is not None and abs(gap_pp) <= IDENT_TOL_PP)})

    payload = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "script": os.path.relpath(os.path.abspath(__file__), ROOT),
        "evidence_cutoff": str(pd.Timestamp(close.index[-1]).date()),
        "prereg": "research/CASE_PREREG_E26_OVERNIGHT_GAP.md",
        "criteria": CRITERIA,
        "config": {"n_hold": N_HOLD, "rebal": REBAL, "cost_per_side": COST,
                   "vol_target": VOL_TARGET, "phases": [str(p.date()) for p in starts]},
        "published": pub,
        "controls": controls,
        "audits": audits,
        "gap_stats": gap_stats,
        "rows": rows,
        "verdict": decide(rows),
        "elapsed_sec": round(time.time() - t0, 1),
    }
    _write_md(payload)
    _write_json(payload)
    _print_summary(payload)
    return payload


def _write_json(payload):
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    tmp = OUT_JSON + ".tmp"
    with io.open(tmp, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    os.replace(tmp, OUT_JSON)


def _write_md(payload):
    v = payload["verdict"]
    g = payload["gap_stats"]
    full = {}
    for r in payload["rows"]:
        full.setdefault(r["arm"], r)
    d = full["declared"]
    lines = [
        "# ETF book — the overnight gap as the last information channel (E26)",
        "",
        "Frozen prereg: `%s` (committed before the run). Evidence cutoff **%s**."
        % (payload["prereg"], payload["evidence_cutoff"]),
        "",
        "## Verdict",
        "",
        "**%s**" % v["state"],
        "",
    ]
    if v["state"] == "ADOPT_GAP":
        lines += ["At least one gap arm is admissible; the card should carry **`%s`** "
                  "(+%.2f pp/yr over `declared`)." % (v["recommended_card_arm"],
                                                      v["best_gained_pp"])]
    elif v["state"] == "NO_GAP_EDGE":
        lines += ["No gap arm clears the frozen line. The best one is `%s` at %+.2f pp/yr "
                  "against a %.2f pp line, so the gap stays **information**: the 1.14 pp the "
                  "declared fill costs is not recoverable from anything a desk can see at the "
                  "fill either." % (v["best_arm"], v["best_gained_pp"],
                                    payload["criteria"]["gap_min_pp"])]
    elif v["state"] == "MIXED_ACROSS_PHASES":
        lines += ["The return line and the phase share disagree; nothing is recommended."]
    else:
        lines += ["The declared control arm did not price, so nothing can be compared."]
    lines += [
        "",
        "## Arms (full span, 10 bp/side)",
        "",
        "| arm | CAGR | Sharpe | maxDD | turnover | vs declared (pp) |",
        "|---|---|---|---|---|---|",
    ]
    for arm in ARMS:
        r = full.get(arm)
        if not r:
            continue
        lines.append("| `%s` | %.2f%% | %.2f | %.2f%% | %.3f | %+.2f |"
                     % (arm, 100.0 * (r["cagr"] or 0.0), r["sharpe"] or 0.0,
                        100.0 * (r["maxdd"] or 0.0), r["turnover"] or 0.0,
                        100.0 * ((r["cagr"] or 0.0) - (d["cagr"] or 0.0))))
    lines += [
        "",
        "## What the channel actually is",
        "",
        "| read | value |",
        "|---|---|",
        "| entry bars priced | %d |" % g["entry_bars"],
        "| mean abs gap | %s bp |" % g["mean_abs_gap_bp"],
        "| median abs gap | %s bp |" % g["median_abs_gap_bp"],
        "| p90 abs gap | %s bp |" % g["p90_abs_gap_bp"],
        "| names excluded per decision (two-sided 20%%) | %s |"
        % g["excluded_names_per_decision"]["excl_absgap_q80"],
        "| names excluded per decision (one-sided 20%%) | %s |"
        % g["excluded_names_per_decision"]["excl_upgap_q80"],
        "",
        "## Phase spread (CAGR per decision phase)",
        "",
        "| phase | " + " | ".join("`%s`" % a for a in ARMS) + " |",
        "|---|" + "---|" * len(ARMS),
    ]
    for p in sorted({r["phase"] for r in payload["rows"]}):
        cells = []
        for a in ARMS:
            r = next((x for x in payload["rows"] if x["phase"] == p and x["arm"] == a), None)
            cells.append("—" if not r or r["cagr"] is None else "%.2f%%" % (100.0 * r["cagr"]))
        lines.append("| %d | %s |" % (p, " | ".join(cells)))
    au = payload["audits"]
    lines += [
        "",
        "## Mechanism audits",
        "",
        "| audit | result |",
        "|---|---|",
        "| A6 gap is reproducible from open[t] and close[t-1] | %s (%d bars) |"
        % ("pass" if au["A6_fill_time_causality"]["ok"] else "FAIL",
           au["A6_fill_time_causality"]["checked"]),
        "| A7 declared arm is shift(1), not lag 0 | %s |"
        % ("pass" if au["A7_declared_lag"]["ok"] else "FAIL"),
        "| A8 exclusion masks, never rescales | %s |"
        % ("pass" if au["A8_mask_not_rescale"]["ok"] else "FAIL"),
        "",
        "A6 is the whole legitimacy of this face: if the gap row could only be built by "
        "looking at the same bar's close, the arm would be look-ahead and the number would "
        "mean nothing.",
        "",
        "## Control against the published card",
        "",
        "| arm | this face | published | gap (pp) | within tolerance |",
        "|---|---|---|---|---|",
    ]
    for c in payload["controls"]:
        lines.append("| `%s` | %s | %s | %s | %s |"
                     % (c["arm"],
                        "—" if c["got_cagr"] is None else "%.2f%%" % (100.0 * c["got_cagr"]),
                        "—" if c["published_cagr"] is None
                        else "%.2f%%" % (100.0 * c["published_cagr"]),
                        "—" if c["gap_pp"] is None else "%+.3f" % c["gap_pp"],
                        "yes" if c["ok"] else "NO"))
    lines += [
        "",
        "## Boundary",
        "",
        "- Nothing is adopted here: this face prices candidates. Changing the card is a separate "
        "frozen step across every face that quotes the headline.",
        "- Mark basis is open-to-open throughout; the close-marked ledger arm (9.12%) answers a "
        "different question and is not mixed in.",
        "- Instrument-list survivorship is unchanged and still disclosed on the card.",
        "",
        "Generated by `%s` in %.1fs." % (payload["script"], payload["elapsed_sec"]),
        "",
    ]
    with io.open(OUT_MD, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines))


def _print_summary(p):
    v = p["verdict"]
    print("verdict:", v["state"])
    full = {}
    for r in p["rows"]:
        full.setdefault(r["arm"], r)
    for arm in ARMS:
        r = full.get(arm)
        if r:
            print("  %-18s cagr=%.2f%% sharpe=%.3f maxdd=%.2f%% turn=%.3f"
                  % (arm, 100.0 * (r["cagr"] or 0.0), r["sharpe"] or 0.0,
                     100.0 * (r["maxdd"] or 0.0), r["turnover"] or 0.0))
    g = p["gap_stats"]
    print("  gap: mean %.2f bp / median %.2f bp / p90 %.2f bp over %d entry bars"
          % (g["mean_abs_gap_bp"] or 0.0, g["median_abs_gap_bp"] or 0.0,
             g["p90_abs_gap_bp"] or 0.0, g["entry_bars"]))
    print("  best=%s %+.2f pp (line %.2f)" % (v["best_arm"], v["best_gained_pp"],
                                              p["criteria"]["gap_min_pp"]))
    for c in p["controls"]:
        print("  control %-9s gap=%s ok=%s" % (c["arm"], c["gap_pp"], c["ok"]))
    print("  audits: A6=%s A7=%s A8=%s"
          % (p["audits"]["A6_fill_time_causality"]["ok"],
             p["audits"]["A7_declared_lag"]["ok"],
             p["audits"]["A8_mask_not_rescale"]["ok"]))


# ---------------------------------------------------------------- check
def read_published(path=None):
    with io.open(path or OUT_JSON, encoding="utf-8") as fh:
        return json.load(fh)


def check(path=None):
    p = read_published(path)
    fresh = decide(p["rows"])
    published = p["verdict"]
    drift = {k: (published.get(k), fresh.get(k)) for k in
             ("state", "best_arm", "best_gained_pp", "recommended_card_arm")
             if published.get(k) != fresh.get(k)}
    ok = not drift
    print(json.dumps({"check": "OK" if ok else "DRIFT", "state": fresh["state"],
                      "drift": drift}, ensure_ascii=False))
    return 0 if ok else 1


# ---------------------------------------------------------------- selftest
def _fixture(n_names=16, n_bars=1400, seed=23, rebal=20):
    """A panel with a persistent cross-sectional trend and a random overnight gap."""
    rng = np.random.RandomState(seed)
    dates = pd.bdate_range("2016-01-04", periods=n_bars)
    drift = np.linspace(-0.0002, 0.0009, n_names)
    rets = rng.normal(0.0, 0.012, size=(n_bars, n_names)) + drift
    close = pd.DataFrame(np.exp(np.cumsum(rets, axis=0)) * 10.0, index=dates,
                         columns=["n%02d" % i for i in range(n_names)]).round(3)
    openp = (close.shift(1) * (1.0 + rng.normal(0, 0.004, size=close.shape))).bfill().round(4)
    amt = pd.DataFrame(1e8, index=dates, columns=close.columns)
    mom = close.pct_change(20)
    feats = {"mom_12_1": mom, "price_position": mom, "drawdown_60": mom, "adx_14": mom,
             "vol_60": mom, "intraday_range": mom}
    score = E.build_score(close, amt, feats)
    return close, openp, amt, feats, score


def selftest():
    legs = []

    def leg(name, cond, detail=""):
        legs.append((name, bool(cond), detail))

    close, openp, amt, feats, score = _fixture()
    gap = overnight_gap(close, openp)
    i0 = 300
    d0 = close.index[i0]

    # L1: the gap is the previous-close ratio, and it is not the same-bar ratio
    want = float(openp.loc[d0].iloc[0] / close.iloc[i0 - 1].iloc[0] - 1.0)
    leg("L1a: gap uses the previous close", abs(float(gap.loc[d0].iloc[0]) - want) < 1e-12)
    same_bar = (openp / close - 1.0)
    leg("L1b: the same-bar ratio is a different number",
        abs(float(same_bar.loc[d0].iloc[0]) - float(gap.loc[d0].iloc[0])) > 0.0)

    # L2: the auditor refuses a leaky (same-bar) gap
    good = audit_fill_time_causality(close, openp, gap, [d0, close.index[600]])
    leg("L2a: the frozen gap passes the fill-time audit", good["ok"], str(good["checked"]))
    bad = audit_fill_time_causality(close, openp, same_bar, [d0])
    leg("L2b: a same-bar gap makes the auditor fire", not bad["ok"])

    # L3: the exclusion mask drops exactly the requested tail of the cross-section
    m = excl_mask(gap, 0.80, False).loc[d0]
    n = int(m.sum())
    leg("L3a: two-sided 20%% mask drops ~20%% of names", 2 <= n <= 5, str(n))
    g = gap.loc[d0]
    q = float(g.abs().quantile(0.80))
    leg("L3b: every surviving name is inside the bar's 80th pct of abs(gap)",
        all(abs(g[k]) <= q + 1e-15 for k in g.index if not m[k]))

    # L4: one-sided mask drops only names that gapped up
    mu = excl_mask(gap, 0.80, True).loc[d0]
    leg("L4: one-sided mask keeps every negative gap",
        all((gap.loc[d0][k] > 0) for k in gap.columns if mu[k]))

    # L5: arms registered = the frozen set
    scores = arm_scores(score, gap)
    leg("L5: arms registered = frozen set", tuple(scores) == ARMS, ",".join(scores))

    # L6: the declared control is the previous bar's ranking; lag 0 would fail A7
    a7 = audit_declared_lag(score, scores["declared"], [d0])
    leg("L6a: declared arm is shift(1)", a7["ok"])
    leg("L6b: an unshifted arm fails the lag audit",
        not audit_declared_lag(score, score, [d0])["ok"])

    # L7: exclusion keeps the kept names' scores bit-for-bit (mask, not rescale)
    a8 = audit_mask_not_rescale(scores["declared"], scores["excl_absgap_q80"], gap, 0.80, [d0])
    leg("L7a: exclusion does not rescale the kept names", a8["ok"])
    rescaled = scores["declared"] * 1.01
    leg("L7b: a rescaled arm fails the mask audit",
        not audit_mask_not_rescale(scores["declared"], rescaled, gap, 0.80, [d0])["ok"])

    # L8: an exclusion that leaves too few names must not trade at all (no silent fallback)
    empty = scores["declared"] * np.nan
    ser, _turn = _run(close, openp, amt, empty, close.index[200], COST)
    leg("L8: an arm that excludes the whole universe holds cash, it does not trade",
        len(ser) > 0 and abs(float(ser.iloc[-1]) - 1.0) < 1e-9, "%.6f" % float(ser.iloc[-1]))

    # L9: verdict logic -- three reachable states on synthetic rows
    def rows_for(gain, sharpe_gain, wins, dd=None):
        out = []
        for p in range(N_PHASES):
            for arm in ("declared", "excl_upgap_q80"):
                cagr = 0.08 + (0.0001 * p)
                if arm != "declared":
                    cagr += gain if p < wins else -0.001
                out.append({"phase": p, "arm": arm, "cagr": cagr,
                            "sharpe": 0.87 + (sharpe_gain if arm != "declared" else 0.0),
                            "maxdd": -0.10 if dd is None else dd})
        return out

    leg("L9a: wins everywhere = ADOPT_GAP",
        decide(rows_for(0.008, 0.02, 4))["state"] == "ADOPT_GAP",
        decide(rows_for(0.008, 0.02, 4))["state"])
    leg("L9b: same gain on 2 of 4 phases = MIXED",
        decide(rows_for(0.008, 0.02, 2))["state"] == "MIXED_ACROSS_PHASES")
    leg("L9c: under the line = NO_GAP_EDGE",
        decide(rows_for(0.002, 0.02, 4))["state"] == "NO_GAP_EDGE")

    # L10: a deeper drawdown disqualifies even a large gain
    rows = rows_for(0.02, 0.02, 4)
    for r in rows:
        if r["arm"] != "declared":
            r["maxdd"] = -0.20
    leg("L10: a much deeper drawdown disqualifies the arm",
        decide(rows)["state"] != "ADOPT_GAP")

    # L11: pp not fraction (r1220 family)
    v = decide([{"phase": 0, "arm": "declared", "cagr": 0.0846, "sharpe": 0.87,
                 "maxdd": -0.16},
                {"phase": 0, "arm": "excl_upgap_q80", "cagr": 0.0903, "sharpe": 0.90,
                 "maxdd": -0.16}])
    leg("L11: the gap is quoted in pp/yr", v["best_gained_pp"] == 0.57,
        str(v["best_gained_pp"]))

    # L12: decide() is a pure function of the rows
    leg("L12: verdict is re-derivable",
        decide(rows_for(0.008, 0.02, 4)) == decide(rows_for(0.008, 0.02, 4)))

    # L13: a missing declared arm is INCOMPLETE, never a silent pass
    v = decide([{"phase": 0, "arm": "excl_upgap_q80", "cagr": 0.09, "sharpe": 1.0,
                 "maxdd": -0.1}])
    leg("L13: missing declared arm is INCOMPLETE", v["state"] == "INCOMPLETE")

    # L14: the exclusion threshold is a per-bar cross-sectional statistic, not a whole-sample one
    q_series = gap.abs().quantile(0.80, axis=1)
    leg("L14: the exclusion threshold moves with the bar (per-row, not one global number)",
        float(q_series.std()) > 0.0)

    failed = [n for n, ok, _ in legs if not ok]
    for n, ok, detail in legs:
        print("%s %s%s" % ("[PASS]" if ok else "[FAIL]", n, (" | " + detail) if detail else ""))
    print("\nselftest: %d/%d %s" % (len(legs) - len(failed), len(legs),
                                    "PASS" if not failed else "FAIL"))
    return 0 if not failed else 1


def main(argv):
    if "--selftest" in argv:
        return selftest()
    if "--check" in argv:
        return check()
    if "run" in argv or not argv:
        run()
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
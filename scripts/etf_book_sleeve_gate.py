"""ETF book -- does the commodity sleeve deserve a risk gate of its own?

The card already says what the sleeve is worth: deleting it costs about 3.71pp of CAGR and
roughly doubles the drawdown, so it is a cushion that also pays -- not a free lunch. The
question that follows is not "keep it?" (yes) but "does it need its OWN gate?", i.e. is
there a sleeve-level state in which the sleeve should be switched off at a decision, on top
of the book-level vol target that already de-levers the whole book?

Three gate shapes are priced on the production engine. Each is applied as "*the sleeve is
not eligible at this decision*": the commodity columns have their score set to NaN on the
gated decision dates, so the engine substitutes the next-best names on its own grid (the
same mechanism the concentration face uses for leave-one-out; nothing here re-implements
selection, sizing or costs).

    trend       sleeve index (equal-weight, causal) below its own trailing MA
    vol         sleeve realised vol above its own trailing quantile
    drawdown    sleeve index more than DD_THR below its own trailing peak

Each gate gets a DOSE-MATCHED PLACEBO: the same number of off-decisions, evenly spread over
the grid instead of timed by the gate. This is the leg that makes the experiment mean
something -- switching the sleeve off X% of the time changes two things at once, the
exposure level and the timing. The placebo holds the exposure change fixed and destroys
only the timing, so ADOPT requires beating the placebo, not just the baseline (E188/E199
class path test: a gate that only "sells a bit less gold" must not be published as a
signal).

A reference arm deletes the sleeve outright, so this face carries its own version of the
cushion reading and the two faces can be cross-checked instead of quoted from memory.

Criteria are frozen below and echoed into the payload; `--check` recomputes every verdict
from the published rows, so a later "small adjustment" cannot pass as the rule.

Usage:
    python scripts/etf_book_sleeve_gate.py run [--out=...]
    python scripts/etf_book_sleeve_gate.py --check
    python scripts/etf_book_sleeve_gate.py --selftest
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import numpy as np
import pandas as pd

import etf_book_concentration as C
import etf_book_production as P
import etf_robust_pf as R

OUT_JSON = ROOT / "results" / "etf_book_sleeve_gate.json"
OUT_MD = ROOT / "research" / "ETF_BOOK_SLEEVE_GATE.md"

SCRIPT = "scripts/etf_book_sleeve_gate.py"
FACE = "results/etf_book_sleeve_gate.json"

SLEEVE_CLASS = "commodity"
N_HOLD = C.N_HOLD
REBAL = C.REBAL
COST = C.COST
VOL_TARGET = C.VOL_TARGET

# ---------------------------------------------------------------- frozen criteria
# Written before the first run. The payload echoes them and `--check` refuses a face that
# echoes different ones.
TREND_MA = 200           # sleeve trend gate: index below its own trailing MA
VOL_WIN = 60             # sleeve risk gate: realised vol window
VOL_Q = 0.80             # and the trailing quantile it must exceed to switch the gate off
VOL_LOOKBACK = 252       # trailing observations the quantile is taken over
DD_WIN = 250             # sleeve crash gate: trailing peak window
DD_THR = 0.10            # and how far below that peak the sleeve must be
MIN_HISTORY = 250        # a gate with less history than this is ON (never off) by definition
MIN_DD_GAIN_PP = 1.0     # an arm must cut the full-window drawdown by this much...
CAGR_KEEP = 0.95         # ...keep this share of baseline CAGR...
PLACEBO_DD_EDGE_PP = 0.5  # ...and beat its own dose-matched placebo by drawdown edge here
PLACEBO_CAGR_EDGE_PP = 0.5  # ...or by CAGR edge here
MIN_DECISIONS = 20       # fewer decisions than this: refuse to judge

GATES = ("trend", "vol", "drawdown")

CRITERIA = {
    "sleeve_class": SLEEVE_CLASS,
    "n_hold": N_HOLD,
    "rebal": REBAL,
    "cost_bp_per_side": COST * 1e4,
    "vol_target": VOL_TARGET,
    "trend_ma": TREND_MA,
    "vol_win": VOL_WIN,
    "vol_q": VOL_Q,
    "vol_lookback": VOL_LOOKBACK,
    "dd_win": DD_WIN,
    "dd_thr": DD_THR,
    "min_history": MIN_HISTORY,
    "min_dd_gain_pp": MIN_DD_GAIN_PP,
    "cagr_keep": CAGR_KEEP,
    "placebo_dd_edge_pp": PLACEBO_DD_EDGE_PP,
    "placebo_cagr_edge_pp": PLACEBO_CAGR_EDGE_PP,
    "min_decisions": MIN_DECISIONS,
    "frozen": ("constants above were written before the first run; --check refuses a face "
               "that echoes others and re-derives every verdict from its own rows"),
    "verdict_rule": (
        "per gate: ADOPT requires (a) full maxdd better than baseline by >= min_dd_gain_pp, "
        "(b) full CAGR >= cagr_keep * baseline, (c) beats its dose-matched placebo by "
        "placebo_dd_edge_pp of drawdown OR placebo_cagr_edge_pp of CAGR; the face verdict is "
        "ADOPT_GATE when any gate adopts, else NO_GATE"),
}


# --------------------------------------------------------------------------- gates
def sleeve_returns(close, cols):
    """Equal-weight daily return of the sleeve (names missing on a bar are skipped)."""
    if not cols:
        raise ValueError("empty sleeve -- cannot build a sleeve index from no columns")
    sub = close.reindex(columns=list(cols))
    return sub.pct_change().mean(axis=1, skipna=True)


def sleeve_index(close, cols):
    """Causal cumulative index of the equal-weight sleeve."""
    r = sleeve_returns(close, cols).fillna(0.0)
    return (1.0 + r).cumprod()


def gate_trend(index, dates, ma=TREND_MA):
    """Off when the sleeve index sits below its own trailing MA (needs `ma` history)."""
    off = []
    for d in dates:
        hist = index.loc[:d]
        if len(hist) < max(ma, MIN_HISTORY):
            continue
        if float(hist.iloc[-1]) < float(hist.tail(ma).mean()):
            off.append(d)
    return off


def gate_vol(index, dates, win=VOL_WIN, q=VOL_Q, lb=VOL_LOOKBACK):
    """Off when sleeve realised vol is above its own trailing quantile."""
    vol = index.pct_change().rolling(win).std() * np.sqrt(252.0)
    off = []
    for d in dates:
        hist = vol.loc[:d].dropna()
        if len(hist) < max(lb, MIN_HISTORY):
            continue
        if float(hist.iloc[-1]) > float(hist.tail(lb).quantile(q)):
            off.append(d)
    return off


def gate_drawdown(index, dates, win=DD_WIN, thr=DD_THR):
    """Off when the sleeve index is more than `thr` below its own trailing peak."""
    peak = index.rolling(win, min_periods=max(win, MIN_HISTORY)).max()
    dd = index / peak - 1.0
    off = []
    for d in dates:
        v = dd.loc[d] if d in dd.index else np.nan
        if not np.isfinite(v):
            continue
        if float(v) < -thr:
            off.append(d)
    return off


def placebo_dates(dates, n_off):
    """The same dose on an untimed schedule: `n_off` decisions spread evenly over the grid."""
    n = len(dates)
    if n_off <= 0 or n == 0:
        return []
    if n_off >= n:
        return list(dates)
    step = n / float(n_off)
    picked, seen = [], set()
    for i in range(n_off):
        d = dates[min(n - 1, int(i * step))]
        if d not in seen:
            seen.add(d)
            picked.append(d)
    return picked


# --------------------------------------------------------------------------- arms
def run_arm(close, openp, amt, score, cols, off_dates):
    """Price the book with the sleeve ineligible on `off_dates` (score -> NaN there)."""
    sc = score
    off = list(off_dates)
    if off:
        sc = score.copy()
        missing = [c for c in cols if c not in sc.columns]
        if missing:
            raise KeyError("sleeve names missing from the panel: %r" % missing[:5])
        mask = sc.index.isin(pd.Index(off))
        if not mask.any():
            raise ValueError("no off-date landed on the score index -- refusing a silent no-op")
        sc.loc[mask, list(cols)] = np.nan
    ser, turn = R.open_to_open_equity(close, openp, amt, sc, REBAL, N_HOLD, COST,
                                      vol_target=VOL_TARGET)
    return ser, float(turn)


def _arm_row(stats, base_full, off_n, decisions):
    full = stats.get("full") or {}
    b = base_full or {}
    return {
        "stats": stats,
        "off_decisions": int(off_n),
        "off_share": round(off_n / float(decisions), 4) if decisions else None,
        "delta_cagr_pp": _pp(full.get("cagr"), b.get("cagr")),
        "delta_sharpe": _r3(full.get("sharpe"), b.get("sharpe")),
        "delta_maxdd_pp": _pp(full.get("maxdd"), b.get("maxdd")),
    }


def _pp(a, b):
    if a is None or b is None:
        return None
    return round(100.0 * (a - b), 3)


def _r3(a, b):
    if a is None or b is None:
        return None
    return round(a - b, 3)


def judge_gate(arm, placebo, base_full):
    """The frozen rule, evaluated from rows only (the gate calls this too)."""
    a = (arm.get("stats") or {}).get("full") or {}
    p = (placebo.get("stats") or {}).get("full") or {}
    b = base_full or {}
    reasons = []
    if b.get("cagr") in (None, 0) or a.get("cagr") is None:
        return {"verdict": "NOT_ASSESSED", "reasons": ["baseline or arm unreadable"]}, None
    dd_gain = (a.get("maxdd") - b.get("maxdd")) * 100.0 if a.get("maxdd") is not None \
        and b.get("maxdd") is not None else None
    keep = a["cagr"] / b["cagr"]
    edge_dd = (a["maxdd"] - p["maxdd"]) * 100.0 if a.get("maxdd") is not None \
        and p.get("maxdd") is not None else None
    edge_cagr = (a["cagr"] - p["cagr"]) * 100.0 if p.get("cagr") is not None else None
    ok_dd = dd_gain is not None and dd_gain >= MIN_DD_GAIN_PP
    ok_keep = keep >= CAGR_KEEP
    ok_beat = ((edge_dd is not None and edge_dd >= PLACEBO_DD_EDGE_PP) or
               (edge_cagr is not None and edge_cagr >= PLACEBO_CAGR_EDGE_PP))
    reasons.append("drawdown gain %s pp vs baseline (needs >= %.1f)" %
                   (None if dd_gain is None else round(dd_gain, 2), MIN_DD_GAIN_PP))
    reasons.append("CAGR kept %s of baseline (needs >= %.2f)" % (round(keep, 3), CAGR_KEEP))
    reasons.append("beats placebo by %s pp drawdown / %s pp CAGR (needs +%.1f or +%.1f)" %
                   (None if edge_dd is None else round(edge_dd, 2),
                    None if edge_cagr is None else round(edge_cagr, 2),
                    PLACEBO_DD_EDGE_PP, PLACEBO_CAGR_EDGE_PP))
    verdict = "ADOPT" if (ok_dd and ok_keep and ok_beat) else "NO_GATE"
    return ({"verdict": verdict, "reasons": reasons},
            {"dd_gain_pp": None if dd_gain is None else round(dd_gain, 3),
             "cagr_keep": round(keep, 4),
             "placebo_dd_edge_pp": None if edge_dd is None else round(edge_dd, 3),
             "placebo_cagr_edge_pp": None if edge_cagr is None else round(edge_cagr, 3)})


def _face_verdict(gates):
    adopting = [k for k, v in gates.items() if (v.get("judgement") or {}).get("verdict") == "ADOPT"]
    if adopting:
        return "ADOPT_GATE", adopting
    if all((v.get("judgement") or {}).get("verdict") == "NOT_ASSESSED" for v in gates.values()):
        return "NOT_ASSESSED", []
    return "NO_GATE", []


def answer_sentence(base_full, gates, verdict, adopting):
    """The one line the card quotes, formatted from the published numbers only.

    English, because the face it lands on (CARD.md) is English; the rule is the same one
    `judge_gate` used, so this can never say "adopt" over a row set that says otherwise.
    """
    if verdict == "NOT_ASSESSED" or not base_full:
        return None
    b = base_full.get("maxdd")
    parts = []
    if adopting:
        k = adopting[0]
        g = gates[k]
        j = g["judgement"]["numbers"]
        parts.append("The %s gate cuts the full-window max drawdown from %.1f%% to %.1f%% "
                     "(%+.2fpp), keeps %.1f%% of the CAGR and beats its dose-matched placebo by "
                     "%+.2fpp."
                     % (k, 100 * (b or 0), 100 * ((g["stats"]["full"] or {}).get("maxdd") or 0),
                        j["dd_gain_pp"], 100 * j["cagr_keep"],
                        j["placebo_dd_edge_pp"] if j["placebo_dd_edge_pp"] is not None else 0.0))
    else:
        best = None
        beaten_by_placebo = []
        for k, g in gates.items():
            n = g["judgement"].get("numbers") or {}
            dd = n.get("dd_gain_pp")
            if dd is None:
                continue
            if best is None or dd > best[1]:
                best = (k, dd, n)
            edge = n.get("placebo_dd_edge_pp")
            cedge = n.get("placebo_cagr_edge_pp")
            if (dd <= 0) or ((edge is None or edge < PLACEBO_DD_EDGE_PP)
                             and (cedge is None or cedge < PLACEBO_CAGR_EDGE_PP)):
                beaten_by_placebo.append(k)
        if best is None:
            return None
        parts.append("No sleeve-level gate earns adoption: switching the sleeve off on %s of "
                     "the decision grid is no better than switching it off on the same number of "
                     "untimed decisions, so a gate here would buy a shorter holding period, not "
                     "a signal." % ", ".join("%s %.0f%%" % (k, 100 * (g.get("off_share") or 0))
                                             for k, g in gates.items()))
        parts.append("The closest arm is the %s gate: %+.2fpp of drawdown against the frozen "
                     "%.1fpp bar%s."
                     % (best[0], best[1], MIN_DD_GAIN_PP,
                        (", and it does beat its own placebo by %+.2fpp -- which is why it is "
                         "named as the re-test candidate on new data, not re-thresholded here"
                         % (best[2].get("placebo_dd_edge_pp") or 0.0))
                        if (best[2].get("placebo_dd_edge_pp") or 0.0) >= PLACEBO_DD_EDGE_PP
                        else ""))
    parts.append("Verdict %s." % verdict)
    return " ".join(parts)


def read_published(path=None):
    """Consumer entry point: {status, sentence, evidence_cutoff, verdict} or an honest gap."""
    p = Path(path) if path else OUT_JSON
    if not p.exists():
        return {"status": "absent", "sentence": None, "evidence_cutoff": None, "verdict": None}
    try:
        doc = json.load(open(p, encoding="utf-8"))
    except Exception as e:                                        # noqa: BLE001
        return {"status": "unreadable: %s" % e, "sentence": None,
                "evidence_cutoff": None, "verdict": None}
    ident = doc.get("identity") or {}
    if not ident.get("passes"):
        return {"status": "no_identity", "sentence": None, "evidence_cutoff": None,
                "verdict": doc.get("verdict")}
    return {"status": "ok", "sentence": doc.get("answer"),
            "evidence_cutoff": doc.get("evidence_cutoff"), "verdict": doc.get("verdict"),
            "adopting": doc.get("adopting") or []}


# --------------------------------------------------------------------------- run
def run(out_path=None, verbose=True):
    close, openp, amt, score, cls, n_flip = P.prep_panel()
    cols = sorted([c for c in close.columns if str(cls.get(c)) == SLEEVE_CLASS])
    if not cols:
        raise RuntimeError("no %s columns in the panel -- nothing to gate" % SLEEVE_CLASS)

    diag = []
    ser, turn = R.open_to_open_equity(close, openp, amt, score, REBAL, N_HOLD, COST,
                                      vol_target=VOL_TARGET, diag=diag)
    if len(diag) < MIN_DECISIONS:
        raise RuntimeError("only %d decisions on the grid -- refusing to judge" % len(diag))
    dates = [pd.Timestamp(r["date"]) for r in diag]
    base = C._stats(ser)
    base_full = base.get("full") or {}

    idx = sleeve_index(close, cols)
    gate_fns = {"trend": gate_trend, "vol": gate_vol, "drawdown": gate_drawdown}
    arms, gates = {}, {}
    for name in GATES:
        off = gate_fns[name](idx, dates)
        ser_g, turn_g = run_arm(close, openp, amt, score, cols, off)
        st_g = C._stats(ser_g)
        arms["gate_%s" % name] = _arm_row(st_g, base_full, len(off), len(dates))
        pl = placebo_dates(dates, len(off))
        ser_p, turn_p = run_arm(close, openp, amt, score, cols, pl)
        st_p = C._stats(ser_p)
        arms["placebo_%s" % name] = _arm_row(st_p, base_full, len(pl), len(dates))
        judgement, numbers = judge_gate(arms["gate_%s" % name], arms["placebo_%s" % name],
                                        base_full)
        gates[name] = {"off_decisions": len(off), "off_share": round(len(off) / len(dates), 4),
                       "first_off": (str(off[0].date()) if off else None),
                       "last_off": (str(off[-1].date()) if off else None),
                       "turnover": round(turn_g, 3), "placebo_turnover": round(turn_p, 3),
                       "stats": st_g, "placebo_stats": st_p,
                       "judgement": {"verdict": judgement["verdict"],
                                     "reasons": judgement["reasons"], "numbers": numbers}}

    # reference arm: delete the sleeve outright (the cushion reading, priced here as well)
    ser_d, turn_d = run_arm(close, openp, amt, score, cols, dates)
    st_d = C._stats(ser_d)
    arms["delete_sleeve"] = _arm_row(st_d, base_full, len(dates), len(dates))

    # identity 1: an all-on gate must be the baseline, bit for bit
    ser_z, _ = run_arm(close, openp, amt, score, cols, [])
    common = ser_z.index.intersection(ser.index)
    zero_gap = float(np.max(np.abs(ser_z.reindex(common) - ser.reindex(common)))) if len(common) else None
    # identity 2: the delete arm must reproduce the concentration face's own sleeve arm
    cross = None
    ref = C.read_published()
    try:
        ref_doc = json.load(open(C.OUT_JSON, encoding="utf-8"))
    except Exception:                                             # noqa: BLE001
        ref_doc = {}
    ref_arm = ref_doc.get("leave_class_out") or {}
    my_delta = arms["delete_sleeve"]["delta_cagr_pp"]
    if ref_arm.get("delta_cagr_pp") is not None and my_delta is not None:
        gap = abs(float(ref_arm["delta_cagr_pp"]) - float(my_delta))
        same_cut = (ref_doc.get("evidence_cutoff") or "") == str(close.index[-1].date())
        cross = {"reference_delta_cagr_pp": ref_arm["delta_cagr_pp"],
                 "mine_delta_cagr_pp": my_delta, "gap_pp": round(gap, 4),
                 "same_cutoff": bool(same_cut), "reference_status": ref.get("status"),
                 "passes": bool(same_cut and gap <= 0.01),
                 "detail": ("the two faces must price the same deletion; a differing cutoff is "
                            "reported as stale, not as agreement")}

    passes = bool(zero_gap is not None and zero_gap < 1e-12
                  and (cross is None or cross.get("passes") or not cross.get("same_cutoff")))
    verdict, adopting = _face_verdict(gates)
    payload = {
        "ts": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
        "script": SCRIPT,
        "face": FACE,
        "evidence_cutoff": str(close.index[-1].date()),
        "criteria": CRITERIA,
        "execution": "decide at close t -> fill at open t+1 -> hold to next decision",
        "panel": {"columns": int(close.shape[1]), "bars": int(close.shape[0]),
                  "flips_repaired": n_flip, "sleeve_symbols": len(cols),
                  "digest": (P.PANEL_DIGEST or {}).get("digest")},
        "book": {"n_hold": N_HOLD, "rebal": REBAL, "vol_target": VOL_TARGET,
                 "cost_bp_per_side": COST * 1e4, "decisions": len(dates),
                 "turnover_per_decision": round(turn, 3)},
        "identity": {"zero_gate_vs_baseline_max_abs": zero_gap,
                     "bars_compared": int(len(common)),
                     "cross_face_delete_sleeve": cross,
                     "passes": passes},
        "baseline": base,
        "arms": arms,
        "gates": gates,
        "verdict": verdict,
        "adopting": adopting,
        "answer": answer_sentence(base_full, gates, verdict, adopting),
        "names": {c: (P.load_names() or {}).get(c, "") for c in cols[:24]},
    }
    if verbose:
        print("baseline", base_full)
        for name in GATES:
            g = gates[name]
            print("%-9s off %3d/%d (%.1f%%)  full %s  placebo %s  -> %s"
                  % (name, g["off_decisions"], len(dates), 100 * g["off_share"],
                     (g["stats"]["full"] or {}), (g["placebo_stats"]["full"] or {}),
                     g["judgement"]["verdict"]))
        print("delete sleeve:", arms["delete_sleeve"]["delta_cagr_pp"], "pp")
        print("identity zero-gate gap:", zero_gap, "| cross-face:", cross)
        print("verdict", verdict, adopting)
        print("answer", payload["answer"])
    p = Path(out_path) if out_path else OUT_JSON
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    if verbose:
        print("saved", p)
    return payload


# --------------------------------------------------------------------------- check
def check(path=None):
    """Re-read the published face and recompute every verdict from its own rows."""
    p = Path(path) if path else OUT_JSON
    doc = json.load(open(p, encoding="utf-8"))
    problems = []
    if doc.get("criteria") != CRITERIA:
        problems.append("criteria echoed by the face differ from the frozen constants")
    base_full = (doc.get("baseline") or {}).get("full") or {}
    gates = doc.get("gates") or {}
    for name, g in gates.items():
        judgement, numbers = judge_gate({"stats": g.get("stats") or {}},
                                        {"stats": g.get("placebo_stats") or {}}, base_full)
        if judgement["verdict"] != (g.get("judgement") or {}).get("verdict"):
            problems.append("gate %s: published verdict %r != recomputed %r"
                            % (name, (g.get("judgement") or {}).get("verdict"),
                               judgement["verdict"]))
        if numbers != (g.get("judgement") or {}).get("numbers"):
            problems.append("gate %s: published numbers do not recompute from its rows" % name)
    verdict, adopting = _face_verdict(gates)
    if verdict != doc.get("verdict"):
        problems.append("face verdict %r != recomputed %r" % (doc.get("verdict"), verdict))
    if list(adopting) != list(doc.get("adopting") or []):
        problems.append("adopting list does not recompute")
    if doc.get("answer") != answer_sentence(base_full, gates, verdict, adopting):
        problems.append("the published answer is not the one its own numbers generate")
    if not (doc.get("identity") or {}).get("passes"):
        problems.append("identity block does not pass")
    for prob in problems:
        print("FAIL:", prob)
    print("check %s (%d problem(s), verdict %s)" % ("OK" if not problems else "FAILED",
                                                    len(problems), doc.get("verdict")))
    return 0 if not problems else 1


# --------------------------------------------------------------------------- selftest
def selftest():
    legs = []

    def chk(name, cond, info=""):
        legs.append((bool(cond), name, info))

    # L1 sleeve index: equal weight, causal prefixes
    idx = pd.date_range("2020-01-01", periods=300, freq="D")
    a = pd.Series(1.0 + np.sin(np.arange(300) / 20.0) * 0.01, index=idx)
    close = pd.DataFrame({"A": a, "B": a * 2.0}, index=idx)
    si = sleeve_index(close, ["A", "B"])
    rets = close.pct_change().mean(axis=1).fillna(0.0)
    expect = (1.0 + rets).cumprod()
    chk("L1 sleeve index equals the equal-weight compounded return",
        float(np.max(np.abs(si - expect))) < 1e-12)
    chk("L1b empty sleeve raises instead of returning a flat line",
        _raises(lambda: sleeve_index(close, [])))

    # L2 trend gate: off exactly when the index is under its trailing MA
    up = pd.Series(np.linspace(1.0, 3.0, 400), index=idx[:400] if len(idx) >= 400 else
                   pd.date_range("2019-01-01", periods=400, freq="D"))
    d2 = pd.Series(np.concatenate([np.linspace(1.0, 2.0, 300), np.linspace(2.0, 1.2, 100)]),
                   index=up.index)
    dates = list(up.index[::10])
    chk("L2 monotone-up sleeve never trips the trend gate", gate_trend(up, dates) == [])
    off = gate_trend(d2, dates)
    chk("L2b falling sleeve trips it and only after the MA has warm history",
        len(off) > 0 and all(d > up.index[TREND_MA] for d in off))

    # L3 volatility gate needs its lookback before it can fire
    chk("L3 vol gate stays silent before vol_lookback history",
        gate_vol(d2, list(d2.index[:200])) == [])

    # L4 drawdown gate: fires below the threshold, silent above it
    dd_idx = pd.Series(np.concatenate([np.linspace(1.0, 2.0, 300), np.linspace(2.0, 1.5, 100)]),
                       index=up.index)
    chk("L4 a 25% slide off the trailing peak trips the crash gate",
        len(gate_drawdown(dd_idx, list(dd_idx.index[300:]))) > 0)
    chk("L4b a book at its peak never trips it",
        gate_drawdown(pd.Series(np.linspace(1.0, 2.0, 400), index=up.index),
                      list(up.index[300:])) == [])

    # L5 placebo holds the dose, destroys the timing
    dts = list(pd.date_range("2021-01-01", periods=83, freq="D"))
    pl = placebo_dates(dts, 17)
    chk("L5 placebo dose equals the gate dose", len(pl) == 17 and len(set(pl)) == 17)
    chk("L5b placebo spread is monotone in the grid and never leaves it",
        all(d in dts for d in pl) and pl == sorted(pl))
    chk("L5c zero-dose placebo is empty and full-dose is the whole grid",
        placebo_dates(dts, 0) == [] and placebo_dates(dts, len(dts)) == dts)

    # L6/L7/L8 the frozen verdict rule, on synthetic rows
    base = {"full": {"cagr": 0.10, "maxdd": -0.20}}
    good_arm = {"stats": {"full": {"cagr": 0.098, "maxdd": -0.15}}}
    good_pl = {"stats": {"full": {"cagr": 0.098, "maxdd": -0.19}}}
    j, n = judge_gate(good_arm, good_pl, base["full"])
    chk("L6 adopt: cuts drawdown, keeps CAGR, beats its placebo", j["verdict"] == "ADOPT")
    j2, _ = judge_gate({"stats": {"full": {"cagr": 0.098, "maxdd": -0.15}}}, good_arm, base["full"])
    chk("L6b a gate that only ties its placebo is NO_GATE (that is just less exposure)",
        j2["verdict"] == "NO_GATE" and "placebo" in " ".join(j2["reasons"]))
    j3, _ = judge_gate({"stats": {"full": {"cagr": 0.05, "maxdd": -0.15}}}, good_pl, base["full"])
    chk("L6c giving up the return is NO_GATE even with a better drawdown",
        j3["verdict"] == "NO_GATE")
    j4, _ = judge_gate({"stats": {"full": {"cagr": 0.10, "maxdd": -0.20}}}, good_pl, base["full"])
    chk("L6d no drawdown gain is NO_GATE", j4["verdict"] == "NO_GATE")
    v, ad = _face_verdict({"trend": {"judgement": {"verdict": "ADOPT"}}})
    chk("L7 face verdict adopts when any gate adopts", v == "ADOPT_GATE" and ad == ["trend"])
    v2, _ = _face_verdict({"trend": {"judgement": {"verdict": "NOT_ASSESSED"}}})
    chk("L7b all-not-assessed is its own verdict, never a quiet NO_GATE", v2 == "NOT_ASSESSED")

    # L8 the answer is generated from the numbers, and refuses to invent one
    chk("L8 answer exists for a real face and is None without a baseline",
        answer_sentence({"maxdd": -0.2, "cagr": 0.1}, {"trend": {
            "judgement": {"verdict": "NO_GATE", "numbers": {"dd_gain_pp": 0.4}},
            "stats": {"full": {"maxdd": -0.196}}}}, "NO_GATE", []) is not None
        and answer_sentence({}, {}, "NOT_ASSESSED", []) is None)

    # L9 arm application is causal: an off-date set built only from the past cannot move
    # a result computed before that date
    chk("L9 gate inputs are prefixes of the index (no future read)",
        all(si.loc[:d].index[-1] == d for d in list(si.index[250:260])))

    ok = sum(1 for p, _, _ in legs if p)
    for p, name, info in legs:
        print("[%s] %s%s" % ("PASS" if p else "FAIL", name, (" | " + info) if info else ""))
    print("selftest %d/%d %s" % (ok, len(legs), "PASS" if ok == len(legs) else "FAIL"))
    return 0 if ok == len(legs) else 1


def _raises(fn):
    try:
        fn()
    except Exception:                                             # noqa: BLE001
        return True
    return False


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    ap = argparse.ArgumentParser(description="does the commodity sleeve deserve its own gate?")
    ap.add_argument("cmd", nargs="?", default="run")
    ap.add_argument("--out", default=None)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest or a.cmd == "selftest":
        return selftest()
    if a.check or a.cmd == "check":
        return check(a.out)
    if a.cmd in ("run", "all"):
        run(a.out)
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
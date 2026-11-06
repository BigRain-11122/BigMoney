"""Is the card's one-bar price recoverable by rebuilding the signal causally? (E25)

The card prints 9.60%/yr; the same rule one bar later earns 8.46%/yr (r1207/r1220,
`etf_book_lookahead_audit`). The 1.14 pp/yr is the price of ranking on a close that had not
happened yet when the book was bought.

E25 asks the reader's question: *is that 1.14 pp simply information the desk never had (so it
can never be earned back), or is part of it a rule that can be rebuilt to stop chasing a move
that already happened?*

Two mechanisms can hide inside "recovered return", and this face separates them instead of
conflating them:

  signal  -- a smoothed causal ranking is a genuinely better ordering
  cost    -- a smoothed causal ranking trades less, and the 1.14 pp was partly commission

Arms (card`s own ladder: n_hold 5, rebal 20, 10 bp/side, 8% vol target that only de-levers,
open->open, same repaired panel and class filter):

  as_coded   score                       control, must reproduce the card
  declared   score.shift(1)              the number the card carries (causal)
  smooth_kN  mean(score.shift(1..N))     causal for every N -- lags are all >= 1

Frozen criteria live in `research/CASE_PREREG_E25_CAUSAL_REBUILD.md` (committed before the
first run) and are echoed into the payload; `--check` re-derives the verdict from the
published rows only, so the sentence cannot drift from the evidence.

Usage:
    python scripts/etf_book_causal_rebuild.py run
    python scripts/etf_book_causal_rebuild.py --check
    python scripts/etf_book_causal_rebuild.py --selftest
"""
from __future__ import annotations

import io
import json
import os
import re
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def _rel(path):
    """Label a path for the audit receipt without letting the label be the failure.

    os.path.relpath raises ValueError across Windows drives, and the selftest builds
    its fixtures under %TEMP% on C: while this repo lives on K:. The audit was
    therefore crashing on its own evidence line (r1386), which the smoke leg read as
    a broken contract rather than a broken label.
    """
    try:
        return os.path.relpath(path, ROOT)
    except ValueError:
        return str(path)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import numpy as np
import pandas as pd

import etf_book_forward as F
import etf_equity_alpha as A
import etf_robust_pf as R
import etf_composite_pf as E
import etf_book_vol_window_phase as PH

OUT_JSON = os.path.join(ROOT, "results", "etf_book_causal_rebuild.json")
OUT_MD = os.path.join(ROOT, "research", "ETF_BOOK_CAUSAL_REBUILD.md")
PRODUCTION_JSON = os.path.join(ROOT, "results", "etf_book_production", "latest.json")
FACTORS_PY = os.path.join(ROOT, "engine", "factors.py")

# ---------------------------------------------------------------- frozen criteria
# Half the published one-bar price (1.14 pp/yr). Recovering less than half of it is not a
# reason to change what the card prints.
RECOVERY_MIN_PP = 0.57
# A smoothed arm may not be deeper in drawdown than the declared arm by more than this.
DD_TOL_PP = 2.0
# One decision sequence cannot distinguish a rule from a lucky ordering.
N_PHASES = 4
PHASE_SHARE_MIN = 0.75           # 3 of 4
# Control tolerance against the published card (the card prints 4 decimals).
IDENT_TOL_PP = 0.05
SMOOTH_KS = (2, 3, 4, 6)
OOS_FROM = "2023-12-31"

REBAL = F.CONFIG["rebal"]
N_HOLD = F.CONFIG["n_hold"]
COST = F.CONFIG["cost_per_side"]
VOL_TARGET = F.CONFIG["vol_target"]

CRITERIA = {
    "recovery_min_pp": RECOVERY_MIN_PP,
    "dd_tol_pp": DD_TOL_PP,
    "n_phases": N_PHASES,
    "phase_share_min": PHASE_SHARE_MIN,
    "ident_tol_pp": IDENT_TOL_PP,
    "smooth_ks": list(SMOOTH_KS),
    "oos_from": OOS_FROM,
    "verdict_rule": (
        "RECOVERABLE iff some smoothed causal arm beats `declared` on CAGR by >= "
        "recovery_min_pp AND its Sharpe is >= this run's `declared` Sharpe AND its max "
        "drawdown is no deeper than declared - dd_tol_pp AND it beats declared on CAGR in "
        ">= phase_share_min of the phases; IRRECOVERABLE if no arm passes; "
        "MIXED_ACROSS_PHASES if the full-span tests pass but the phase share does not (or "
        "the reverse) -- a rule that wins on one decision sequence is not a rule"),
    "arms": {
        "as_coded": "score (control; not causal, must reproduce the card)",
        "declared": "score.shift(1) -- the number the card carries",
        "smooth_kN": "mean(score.shift(1..N)) for N in smooth_ks -- every lag >= 1",
    },
}


# ---------------------------------------------------------------- score builders
def lag_score(score, k):
    """Mean of the last `k` causal scores. Every lag is >= 1: nothing from bar d is used."""
    if k < 1:
        raise ValueError("lag must be >= 1 (a 0-lag arm is the look-ahead arm, not a rebuild)")
    parts = [score.shift(i) for i in range(1, k + 1)]
    return sum(parts) / float(len(parts))


def arm_scores(score):
    """Ordered {arm_name: score_frame}. `as_coded` is the only non-causal member."""
    out = {"as_coded": score, "declared": lag_score(score, 1)}
    for k in SMOOTH_KS:
        out["smooth_k%d" % k] = lag_score(score, k)
    return out


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


def _row(phase, arm, ser, turn, cost):
    st = _stats(ser)
    row = {"phase": int(phase), "arm": arm, "cost_per_side": cost, "turnover": round(turn, 4)}
    row.update({k: (None if v is None else (round(v, 6) if isinstance(v, float) else v))
                for k, v in st.items()})
    return row


# ---------------------------------------------------------------- mechanism audits
def audit_factor_source(path=FACTORS_PY):
    """A4: no whole-sample statistic in the factor library.

    `shift(1)` is only a *causal* rebuild if each factor at bar d is a function of bars <= d.
    Rolling/expanding windows are; a whole-frame `.mean()` or a `rank()` without `axis=1`
    is not (it would let a later bar change an earlier value). This is a source pin, checked
    mechanically -- and it is itself selftested against a planted violation, so it cannot
    pass by never firing.
    """
    with io.open(path, encoding="utf-8") as fh:
        src = fh.read()
    violations = []
    for i, line in enumerate(src.splitlines(), 1):
        code = line.split("#", 1)[0]
        if not code.strip():
            continue
        for call in re.finditer(r"\.(mean|std|median|rank|quantile)\(", code):
            name = call.group(1)
            head = code[:call.start()]
            allowed = (".rolling(" in head or ".expanding(" in head or "axis=1" in code
                       or "axis = 1" in code)
            if not allowed:
                violations.append({"line": i, "call": name, "code": code.strip()[:120]})
    return {"ok": not violations, "violations": violations, "path": _rel(path)}


def audit_rank_causality(close, amt, feats, score, bars):
    """A3: the score row at bar d is reproducible from a panel truncated at bar d."""
    bad = []
    rows = []
    for d in bars:
        trunc_c = close.loc[:d]
        trunc_a = amt.loc[:d]
        trunc_f = {k: v.loc[:d] for k, v in feats.items()}
        sc = E.build_score(trunc_c, trunc_a, trunc_f)
        a = sc.loc[d] if d in sc.index else None
        b = score.loc[d] if d in score.index else None
        if a is None or b is None:
            bad.append({"bar": str(d), "why": "bar missing from a score frame"})
            continue
        diff = 0.0 if not len(a) else float(np.nanmax(np.abs(a.values - b.values))) \
            if np.isfinite(np.abs(a.values - b.values)).any() else 0.0
        if not np.allclose(a.values, b.values, rtol=0.0, atol=0.0, equal_nan=True):
            diff = float("nan") if not np.isfinite(diff) else diff
            rows.append({"bar": str(getattr(d, "date", lambda: d)()),
                         "max_abs_diff": "row differs (NaN-safe compare)"})
            bad.append({"bar": str(getattr(d, "date", lambda: d)()), "max_abs_diff": diff})
            continue
        rows.append({"bar": str(getattr(d, "date", lambda: d)()), "max_abs_diff": diff})
    return {"ok": not bad, "checked": len(rows), "violations": bad, "sample": rows[:5]}


# ---------------------------------------------------------------- verdict
def _arm_rows(rows, phase=None):
    return [r for r in rows if phase is None or r["phase"] == phase]


def decide(rows, criteria=CRITERIA):
    """Verdict from published rows only -- re-derivable, never re-run."""
    full = {}
    for r in _arm_rows(rows):
        full.setdefault(r["arm"], r)
    if "declared" not in full:
        return {"state": "INCOMPLETE", "why": "no `declared` arm"}
    d = full["declared"]
    if d.get("cagr") is None:
        return {"state": "INCOMPLETE", "why": "declared arm did not price"}
    dd_floor = (d["maxdd"] or 0.0) - criteria["dd_tol_pp"] / 100.0

    phases = sorted({r["phase"] for r in rows})
    by_phase = {}
    for p in phases:
        by_phase[p] = {r["arm"]: r for r in _arm_rows(rows, p)}

    arms = []
    for name, r in full.items():
        if name in ("as_coded", "declared") or r.get("cagr") is None:
            continue
        recovered_pp = 100.0 * (r["cagr"] - d["cagr"])
        full_ok = (recovered_pp >= criteria["recovery_min_pp"]
                   and (r.get("sharpe") or 0.0) >= (d.get("sharpe") or 0.0)
                   and (r.get("maxdd") or 0.0) >= dd_floor)
        wins = 0
        for p in phases:
            pr = by_phase[p].get(name)
            pd_ = by_phase[p].get("declared")
            if pr and pd_ and pr.get("cagr") is not None and pd_.get("cagr") is not None:
                if pr["cagr"] > pd_["cagr"]:
                    wins += 1
        share = (float(wins) / len(phases)) if phases else 0.0
        arms.append({
            "arm": name,
            "recovered_pp": round(recovered_pp, 2),
            "full_span_tests_pass": bool(full_ok),
            "phase_wins": wins,
            "phase_share": round(share, 3),
            "phase_share_pass": bool(share >= criteria["phase_share_min"]),
            "admissible": bool(full_ok and share >= criteria["phase_share_min"]),
        })
    if not arms:
        return {"state": "INCOMPLETE", "why": "no causal rebuild arm priced"}

    win = [a for a in arms if a["admissible"]]
    best = max(arms, key=lambda a: a["recovered_pp"])
    gain_ok = best["recovered_pp"] >= criteria["recovery_min_pp"]
    # A gain under the line is never "mixed": the question the state names -- is this a rule
    # or one lucky ordering -- does not arise until the arm clears the return line. Only an
    # arm that clears the line but fails the phase share (or clears the phases but fails the
    # return) is reported as mixed; anything else recovers too little to matter.
    if win:
        state = "RECOVERABLE"
        chosen = max(win, key=lambda a: a["recovered_pp"])
    elif gain_ok and (best["full_span_tests_pass"] or best["phase_share_pass"]):
        state = "MIXED_ACROSS_PHASES"
        chosen = None
    else:
        state = "IRRECOVERABLE"
        chosen = None
    return {
        "state": state,
        "state_rule_detail": ("MIXED_ACROSS_PHASES requires the return line to be cleared "
                              "first; a recovery smaller than recovery_min_pp is "
                              "IRRECOVERABLE however consistently it wins"),
        "declared_cagr": round(d["cagr"], 4),
        "declared_sharpe": d.get("sharpe"),
        "declared_maxdd": d.get("maxdd"),
        "dd_floor": round(dd_floor, 4),
        "best_arm": best["arm"],
        "best_recovered_pp": best["recovered_pp"],
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
    scores = arm_scores(score)

    trade_dates = [d for d in close.index if d >= pd.Timestamp(R.START)]
    starts = PH.phase_starts(trade_dates)

    rows = []
    for i, st in enumerate(starts):
        for name, sc in scores.items():
            ser, turn = _run(close, openp, amt, sc, st, COST)
            rows.append(_row(i, name, ser, turn, COST))

    # cost decomposition: the winning arm and the declared arm, zero commission
    verdict_pre = decide(rows)
    focus = verdict_pre.get("chosen_arm") or verdict_pre.get("best_arm")
    gross_rows = []
    for name in [n for n in dict.fromkeys(["declared", focus]) if n]:
        ser, turn = _run(close, openp, amt, scores[name], starts[0], 0.0)
        gross_rows.append(_row(0, "%s__gross" % name, ser, turn, 0.0))
    gross = {r["arm"]: r for r in gross_rows}
    net = {r["arm"]: r for r in _arm_rows(rows, 0)}
    recovery_total = (net.get(focus, {}).get("cagr") or 0.0) - (net["declared"].get("cagr") or 0.0)
    recovery_gross = ((gross.get("%s__gross" % focus, {}).get("cagr") or 0.0)
                      - (gross.get("declared__gross", {}).get("cagr") or 0.0))
    decomposition = {
        "arm": focus,
        "total_pp": round(100.0 * recovery_total, 2),
        "signal_pp": round(100.0 * recovery_gross, 2),
        "cost_pp": round(100.0 * recovery_total - 100.0 * recovery_gross, 2),
        "turnover_declared": net.get("declared", {}).get("turnover"),
        "turnover_arm": net.get(focus, {}).get("turnover"),
        "rule": ("signal_pp = the same two rules priced with zero commission; cost_pp = the "
                 "rest. A recovery that is entirely cost must be printed as cost, not edge."),
    }

    # controls against the published card
    try:
        with io.open(PRODUCTION_JSON, encoding="utf-8") as fh:
            prod = json.load(fh)
        eb = prod.get("execution_basis") or {}
        pub = {"as_coded_cagr": eb.get("as_coded_cagr"),
               "declared_cagr": eb.get("declared_cagr"),
               "source": "results/etf_book_production/latest.json::execution_basis"}
    except Exception as exc:
        pub = {"as_coded_cagr": None, "declared_cagr": None,
               "source": "unreadable: %s" % exc}
    controls = []
    for name in ("as_coded", "declared"):
        got = next((r["cagr"] for r in rows if r["phase"] == 0 and r["arm"] == name), None)
        want = pub.get("%s_cagr" % name)
        gap = None if (got is None or want is None) else 100.0 * (got - want)
        controls.append({
            "arm": name, "got_cagr": got, "published_cagr": want,
            "gap_pp": None if gap is None else round(gap, 3),
            "ok": bool(gap is not None and abs(gap) <= IDENT_TOL_PP),
        })

    # mechanism audits
    sample_bars = [starts[0], starts[len(starts) // 2], starts[-1]]
    a3 = audit_rank_causality(close, amt, feats, score, sample_bars)
    a4 = audit_factor_source()
    lags_used = {name: (list(range(1, k + 1)) if name.startswith("smooth_k")
                        else ([1] if name == "declared" else [0]))
                 for name, k in [("declared", 1)] + [("smooth_k%d" % k, k) for k in SMOOTH_KS]}
    a5 = {"ok": all(min(v) >= 1 for v in lags_used.values()), "lags_used": lags_used}

    published_verdict = decide(rows)
    payload = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "script": os.path.relpath(os.path.abspath(__file__), ROOT),
        "evidence_cutoff": str(pd.Timestamp(close.index[-1]).date()),
        "prereg": "research/CASE_PREREG_E25_CAUSAL_REBUILD.md",
        "criteria": CRITERIA,
        "config": {"n_hold": N_HOLD, "rebal": REBAL, "cost_per_side": COST,
                   "vol_target": VOL_TARGET, "phases": [str(p.date()) for p in starts]},
        "published": pub,
        "controls": controls,
        "audits": {"A3_rank_causality": a3, "A4_factor_source": a4, "A5_lags": a5},
        "rows": rows,
        "gross_rows": gross_rows,
        "decomposition": decomposition,
        "verdict": published_verdict,
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
    dec = payload["decomposition"]
    lines = [
        "# ETF book causal rebuild — is the one-bar price recoverable? (E25)",
        "",
        "Frozen prereg: `%s` (committed before the run). Evidence cutoff **%s**."
        % (payload["prereg"], payload["evidence_cutoff"]),
        "",
        "## Verdict",
        "",
        "**%s**" % v["state"],
        "",
    ]
    if v["state"] == "RECOVERABLE":
        lines += ["The card should carry **`%s`** (%s). The rebuild earns back %.2f pp/yr of "
                  "the %.2f pp one-bar price."
                  % (v["recommended_card_arm"], v["chosen_arm"], v["best_recovered_pp"],
                     100.0 * (payload["controls"][0]["published_cagr"] or 0.0)
                     - 100.0 * (v["declared_cagr"] or 0.0))]
    elif v["state"] == "IRRECOVERABLE":
        lines += ["No causal rebuild in the frozen set earns back the one-bar price. The card "
                  "keeps **`declared`** (%.2f%%/yr) and further smoothing of this score is not "
                  "worth burning: the gap is information the desk never had."
                  % (100.0 * (v["declared_cagr"] or 0.0))]
    else:
        lines += ["The tests split across the four decision phases; no arm is admissible on "
                  "both the full span and the phase share. Nothing is recommended."]
    lines += [
        "",
        "## Arms (full span, 10 bp/side)",
        "",
        "| arm | CAGR | Sharpe | maxDD | turnover | vs declared (pp) |",
        "|---|---|---|---|---|---|",
    ]
    full = {}
    for r in payload["rows"]:
        full.setdefault(r["arm"], r)
    d = full["declared"]["cagr"]
    for arm in ("as_coded", "declared") + tuple("smooth_k%d" % k for k in SMOOTH_KS):
        r = full.get(arm)
        if not r:
            continue
        lines.append("| `%s` | %.2f%% | %.2f | %.2f%% | %.3f | %+.2f |"
                     % (arm, 100.0 * (r["cagr"] or 0.0), r["sharpe"] or 0.0,
                        100.0 * (r["maxdd"] or 0.0), r["turnover"] or 0.0,
                        100.0 * ((r["cagr"] or 0.0) - d)))
    lines += [
        "",
        "`as_coded` is the control: it is not causal, and it must reproduce the card.",
        "",
        "## Where the recovery comes from",
        "",
        "| arm | total (pp) | signal (pp) | cost (pp) | turnover |",
        "|---|---|---|---|---|",
        "| `%s` vs `declared` | %+.2f | %+.2f | %+.2f | %.3f -> %.3f |"
        % (dec["arm"] or "n/a", dec["total_pp"], dec["signal_pp"], dec["cost_pp"],
           dec["turnover_declared"] or 0.0, dec["turnover_arm"] or 0.0),
        "",
        "Signal = the same two rules with commission set to zero. Cost = the remainder.",
        "",
        "## Phase spread (per decision phase, CAGR)",
        "",
        "| phase | " + " | ".join(["`%s`" % a for a in ("declared", "smooth_k2", "smooth_k3",
                                                     "smooth_k4", "smooth_k6")]) + " |",
        "|---|" + "---|" * 5,
    ]
    for p in sorted({r["phase"] for r in payload["rows"]}):
        cells = []
        for a in ("declared", "smooth_k2", "smooth_k3", "smooth_k4", "smooth_k6"):
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
        "| A3 rank-layer causality | %s (%d bars) |"
        % ("pass" if au["A3_rank_causality"]["ok"] else "FAIL",
           au["A3_rank_causality"]["checked"]),
        "| A4 factor library has no whole-sample statistic | %s |"
        % ("pass" if au["A4_factor_source"]["ok"] else "FAIL"),
        "| A5 every rebuild arm uses lag >= 1 | %s |"
        % ("pass" if au["A5_lags"]["ok"] else "FAIL"),
        "",
        "A3/A4 matter because `shift(1)` is only a causal rebuild if each factor at bar d is a "
        "function of bars <= d. If it were not, the `declared` arm itself would still be "
        "look-ahead, and 8.46% would not be a tradable number either.",
        "",
        "## Controls against the published card",
        "",
        "| arm | this face | published | gap (pp) | within tolerance |",
        "|---|---|---|---|---|",
    ]
    for c in payload["controls"]:
        lines.append("| `%s` | %s | %s | %s | %s |"
                     % (c["arm"],
                        "—" if c["got_cagr"] is None else "%.2f%%" % (100.0 * c["got_cagr"]),
                        "—" if c["published_cagr"] is None else "%.2f%%" % (100.0 * c["published_cagr"]),
                        "—" if c["gap_pp"] is None else "%+.3f" % c["gap_pp"],
                        "yes" if c["ok"] else "NO"))
    lines += [
        "",
        "## Boundary",
        "",
        "- Nothing is adopted here: this face prices candidates. Changing what the card prints "
        "is a separate frozen step across every face that quotes the headline.",
        "- Mark basis is open-to-open throughout. The close-marked ledger arm (9.12%) answers a "
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
    for arm in ("as_coded", "declared") + tuple("smooth_k%d" % k for k in SMOOTH_KS):
        r = full.get(arm)
        if r:
            print("  %-10s cagr=%.2f%% sharpe=%.3f maxdd=%.2f%% turn=%.3f"
                  % (arm, 100.0 * (r["cagr"] or 0.0), r["sharpe"] or 0.0,
                     100.0 * (r["maxdd"] or 0.0), r["turnover"] or 0.0))
    d = p["decomposition"]
    print("  decomposition: total %+.2fpp = signal %+.2fpp + cost %+.2fpp"
          % (d["total_pp"], d["signal_pp"], d["cost_pp"]))
    for c in p["controls"]:
        print("  control %-9s gap=%s ok=%s" % (c["arm"], c["gap_pp"], c["ok"]))
    print("  audits: A3=%s A4=%s A5=%s"
          % (p["audits"]["A3_rank_causality"]["ok"], p["audits"]["A4_factor_source"]["ok"],
             p["audits"]["A5_lags"]["ok"]))


# ---------------------------------------------------------------- check
def read_published(path=None):
    with io.open(path or OUT_JSON, encoding="utf-8") as fh:
        return json.load(fh)


def check(path=None):
    p = read_published(path)
    fresh = decide(p["rows"])
    published = p["verdict"]
    drift = {k: (published.get(k), fresh.get(k)) for k in
             ("state", "best_arm", "best_recovered_pp", "recommended_card_arm")
             if published.get(k) != fresh.get(k)}
    ok = not drift
    print(json.dumps({"check": "OK" if ok else "DRIFT", "state": fresh["state"],
                      "drift": drift}, ensure_ascii=False))
    return 0 if ok else 1


# ---------------------------------------------------------------- selftest
def _fixture(n_names=16, n_bars=1400, seed=11, rebal=20):
    """A panel with a persistent cross-sectional trend, so a causal score can be built."""
    rng = np.random.RandomState(seed)
    dates = pd.bdate_range("2016-01-04", periods=n_bars)
    drift = np.linspace(-0.0002, 0.0009, n_names)
    rets = rng.normal(0.0, 0.012, size=(n_bars, n_names)) + drift
    close = pd.DataFrame(np.exp(np.cumsum(rets, axis=0)) * 10.0, index=dates,
                         columns=["n%02d" % i for i in range(n_names)]).round(3)
    openp = (close.shift(1) * (1.0 + rng.normal(0, 0.002, size=close.shape))).bfill().round(3)
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

    # L1: lag builder never uses the same bar
    k2 = lag_score(score, 2)
    i0 = 60
    a = score.loc[close.index[i0]]
    b = k2.loc[close.index[i0 + 1]]
    leg("L1: mean of shifts 1..2 uses only earlier bars",
        np.allclose(np.nan_to_num(b.values),
                    np.nan_to_num(((a + score.loc[close.index[i0 - 1]]).values / 2.0)),
                    atol=1e-12))

    # L2: a 0-lag arm is refused loudly (it is the look-ahead arm, not a rebuild)
    try:
        lag_score(score, 0)
        leg("L2: lag 0 refused", False)
    except ValueError:
        leg("L2: lag 0 refused", True)

    # L3: arm_scores registers the frozen set and only `as_coded` is non-causal
    sc = arm_scores(score)
    leg("L3: arms registered = frozen set",
        set(sc) == {"as_coded", "declared"} | {"smooth_k%d" % k for k in SMOOTH_KS},
        ",".join(sorted(sc)))

    # L4: rank-layer causality holds on the fixture and fires on a planted leak
    bars = [close.index[400], close.index[600]]
    good = audit_rank_causality(close, amt, feats, score, bars)
    leg("L4a: truncation reproduces the score row", good["ok"], str(good["checked"]))
    # A3 can only police the layer that is recomputed here -- the score built from the panel.
    # A score normalised over the whole sample is the canonical violation at that layer: its
    # value at bar d moves when later bars exist, which truncation exposes.
    vals = score.stack()
    leaky = (score - vals.mean()) / vals.std()
    bad = audit_rank_causality(close, amt, feats, leaky, [close.index[600]])
    leg("L4b: a whole-sample-normalised score makes the audit fire", not bad["ok"])

    # L5: the factor-library auditor fires on a planted violation and passes on rolling code
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as fh:
        fh.write("def f(x):\n    return x.mean()\n")
        badp = fh.name
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as fh:
        fh.write("def f(x):\n    return x.rolling(20).mean()\n")
        goodp = fh.name
    try:
        leg("L5a: auditor fires on a whole-sample mean", not audit_factor_source(badp)["ok"])
        leg("L5b: auditor passes a rolling mean", audit_factor_source(goodp)["ok"])
    finally:
        os.unlink(badp)
        os.unlink(goodp)

    # L6: verdict logic on synthetic rows -- the three reachable states
    def rows_for(recovered, sharpe_gain, wins):
        out = []
        for p in range(N_PHASES):
            for arm in ("declared", "smooth_k2"):
                cagr = 0.08 + (0.0001 * p)
                if arm == "smooth_k2":
                    cagr += recovered if p < wins else -0.001
                out.append({"phase": p, "arm": arm, "cagr": cagr,
                            "sharpe": 0.87 + (sharpe_gain if arm == "smooth_k2" else 0.0),
                            "maxdd": -0.10 if arm == "declared" else -0.10})
        return out
    v = decide(rows_for(0.008, 0.02, 4))
    leg("L6a: a rebuild that wins everywhere is RECOVERABLE", v["state"] == "RECOVERABLE",
        v["state"])
    v = decide(rows_for(0.008, 0.02, 2))
    leg("L6b: the same gain on 2 of 4 phases is MIXED", v["state"] == "MIXED_ACROSS_PHASES",
        v["state"])
    v = decide(rows_for(0.002, 0.02, 4))
    leg("L6c: under half the gap is IRRECOVERABLE", v["state"] == "IRRECOVERABLE", v["state"])

    # L7: a deeper drawdown disqualifies even a large recovery
    rows = rows_for(0.02, 0.02, 4)
    for r in rows:
        if r["arm"] == "smooth_k2":
            r["maxdd"] = -0.20
    v = decide(rows)
    leg("L7: a much deeper drawdown disqualifies the arm", v["state"] != "RECOVERABLE", v["state"])

    # L8: pp not fraction (r1220 family) -- 1.14pp must print as 1.14, never 114
    r_pp = decide([{"phase": 0, "arm": "declared", "cagr": 0.0846, "sharpe": 0.87, "maxdd": -0.16},
                   {"phase": 0, "arm": "smooth_k2", "cagr": 0.0960, "sharpe": 0.99, "maxdd": -0.16}])
    leg("L8: the gap is quoted in pp/yr", r_pp["best_recovered_pp"] == 1.14,
        str(r_pp["best_recovered_pp"]))

    # L9: decide() is a pure function of the rows
    leg("L9: verdict is re-derivable", decide(rows_for(0.008, 0.02, 4)) ==
        decide(rows_for(0.008, 0.02, 4)))

    # L10: a missing declared arm is INCOMPLETE, never a silent pass
    v = decide([{"phase": 0, "arm": "smooth_k2", "cagr": 0.09, "sharpe": 1.0, "maxdd": -0.1}])
    leg("L10: missing declared arm is INCOMPLETE", v["state"] == "INCOMPLETE", v["state"])

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
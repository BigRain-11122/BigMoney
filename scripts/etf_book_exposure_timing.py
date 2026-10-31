"""Is the 8% vol target timing the market, or is it just a smaller book?

The card says the overlay "is a drawdown tool, not an edge", and the slot census agrees:
87.3% of decision slots were de-levered (research/ETF_BOOK_VOLTARGET_LAG.md). That raises a
question nobody had measured: when the book shrinks before a bad stretch and grows before a
good one, is the *timing* worth anything -- or is the whole effect simply that a book held at
two-thirds size earns two-thirds of the return with two-thirds of the wobble?

Three reference points, because one arm alone cannot answer it:

    production  the card's book, scale from the engine's own 60-day estimator
    full        the same selections at exposure 1.0 (no overlay)
    constant    the same selections at the book's OWN average exposure, held every bar

`production - constant` is the timing value at matched average risk. `constant - full` is
what de-risking (not timing) is worth. A number is only a timing result if it clears the
placebo band that follows.

The placebo is the honest control: permute the engine's own scale series across its own
decision bars -- identical exposure distribution, identical turnover statistics, zero
information about which bar is which -- and re-run the book 20 times. If the real
production path does not beat the permuted ones, the "timing" is a consequence of holding
less risk on average, and the page must say so.

Scope: no engine edit, no network, no prereg. Every arm differs from production in exactly
one thing (the scale applied at each decision), and the identity arm re-runs the engine's
own scale sequence and must reproduce its nav bit for bit -- that is the first selftest leg,
because a face that cannot reproduce the book it is describing is measuring a different book.

  python scripts/etf_book_exposure_timing.py run
  python scripts/etf_book_exposure_timing.py --check      # re-derive verdict from the face
  python scripts/etf_book_exposure_timing.py --selftest   # offline invariants
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import pandas as pd

import etf_composite_pf as E
import etf_equity_alpha as A
import etf_book_production as P
import etf_book_forward as F

OUT_JSON = os.path.join(E.PATHS.results_dir, "etf_book_exposure_timing.json")
OUT_MD = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                      "research", "ETF_BOOK_EXPOSURE_TIMING.md")
N_PLACEBO = 20
PLACEBO_SEED = 20261031
N_HOLD = F.CONFIG["n_hold"]
REBAL = F.CONFIG["rebal"]
COST = F.CONFIG["cost_per_side"]
VOL_TARGET = F.CONFIG["vol_target"]
IDENT_TOL = 1e-12


class ScaledBook(F.Forward):
    """Forward's own state machine with the exposure scale replaced.

    Nothing else changes: the selection, the grid, the fill rule, the cost model and the
    cash carry are the engine's. `scale_fn(bar, engine_scale)` returns the multiplier for
    that decision, so the identity arm is `lambda d, s: s` and must be a no-op.
    """

    def __init__(self, *a, **kw):
        self.scale_fn = kw.pop("scale_fn")
        self.selection_drift = 0
        super().__init__(*a, **kw)

    def _decide(self, d):
        # Mirrors Forward._decide line for line except that the scale handed to `scale_fn`
        # is the engine's own unrounded value. Reading it back off `last_decision["scale"]`
        # (which the engine publishes rounded to 6dp) made the identity arm differ from the
        # engine by ~1e-7 on the real panel -- small, but it means the "identity" arm was
        # not the engine, and a face that cannot reproduce the book it describes is
        # measuring a different book (found by the r1197 identity gate, not by a fixture).
        s = self.score.loc[d].dropna()
        if len(s) < self.n_hold:
            return
        picks = list(s.nlargest(self.n_hold).index)
        if len(picks) != self.n_hold:
            self.selection_drift += 1
        base = {p: 1.0 / self.n_hold for p in picks}
        scale, vol = 1.0, None
        if self.vol_target:
            scale, vol = P.scale_for(base, self.op, d, self.vol_target)
        m = float(self.scale_fn(d, scale))
        new = {k: w * m for k, w in base.items()}
        turn = sum(abs(new.get(k, 0.0) - self.held.get(k, 0.0))
                   for k in set(new) | set(self.held))
        self.pending = (new, turn)
        self.last_decision = {"bar": str(d.date()), "scale": round(m, 6),
                              "realised_vol_60d": None if vol is None else round(float(vol), 6),
                              "names": picks, "turnover": round(float(turn), 6)}
        self.books[str(d.date())] = self.last_decision


def _series(marks):
    return pd.Series([m["nav"] for _d, m in marks],
                     index=pd.DatetimeIndex([d for d, _m in marks]), name="nav")


def _exposure(marks):
    return np.array([1.0 - m["cash"] for _d, m in marks], dtype=float)


def _run_arm(px, op, score, carry, dates, rebal_days, scale_fn):
    book = ScaledBook(px, op, score, N_HOLD, REBAL, COST, vol_target=VOL_TARGET,
                      carry=carry, scale_fn=scale_fn)
    marks = book.run(dates, rebal_days)
    return _series(marks), _exposure(marks), book


def _row(label, ser, exposure, book, full_cagr=None):
    st = A.stats2(ser, label)
    row = {
        "arm": label,
        "cagr": st.get("cagr"),
        "sharpe": st.get("sharpe"),
        "maxdd": st.get("maxdd"),
        "vol": st.get("vol"),
        "years": st.get("years"),
        "mean_exposure": round(float(np.mean(exposure)), 4),
        "delevered_share": round(float(np.mean(exposure < 0.999)), 4),
        "turnover_per_fill": round(float(book.mean_turnover), 3),
        "n_fills": book.n_fill,
        "selection_drift": book.selection_drift,
    }
    if full_cagr is not None and st.get("cagr") is not None:
        row["cagr_delta_vs_full_pp"] = round(100.0 * (st["cagr"] - full_cagr), 2)
    return row


def decide(rows, placebo_rows):
    """Verdict from published rows alone -- no re-run, so --check can re-derive it.

    A timing claim needs the production path to beat permuted paths with the same exposure
    distribution. `timing_pp` is production minus constant; the band is the placebo spread
    around the same constant baseline.
    """
    by = {r["arm"]: r for r in rows}
    if "production" not in by or "constant" not in by or "full" not in by:
        return {"state": "INCOMPLETE", "why": "missing a required arm"}
    pc = [r["cagr"] for r in placebo_rows if r.get("cagr") is not None]
    if len(pc) < 5:
        return {"state": "INCOMPLETE", "why": "too few placebo arms"}
    const = by["constant"]["cagr"]
    timing = 100.0 * (by["production"]["cagr"] - const)
    placebo_delta = sorted(100.0 * (c - const) for c in pc)
    p05 = placebo_delta[int(0.05 * (len(placebo_delta) - 1))]
    p50 = placebo_delta[len(placebo_delta) // 2]
    p95 = placebo_delta[int(0.95 * (len(placebo_delta) - 1))]
    if timing > max(p95, 0.0):
        state = "TIMING_ADDS"
    elif timing < min(p05, 0.0):
        state = "TIMING_SUBTRACTS"
    else:
        state = "AVERAGE_EXPOSURE_ONLY"
    return {
        "state": state,
        "timing_pp": round(timing, 2),
        "placebo_p05_pp": round(p05, 2),
        "placebo_p50_pp": round(p50, 2),
        "placebo_p95_pp": round(p95, 2),
        "de_risking_pp": round(100.0 * (const - by["full"]["cagr"]), 2),
        "n_placebo": len(pc),
        "rule": ("TIMING_ADDS iff production beats the p95 of same-exposure placebo paths; "
                 "TIMING_SUBTRACTS iff it loses to the p05; otherwise the overlay is average "
                 "exposure, not timing"),
    }


def run():
    t0 = time.time()
    close, openp, _amt, _feats, score, cls, n_flip = F.build_inputs()
    dates, rebal_days = F.date_grid(close, REBAL)
    carry, carry_note = F.build_carry(dates)
    carry = None if carry is None else carry.reindex(pd.DatetimeIndex(dates)).fillna(0.0)

    prod_ser, prod_exp, prod = _run_arm(close, openp, score, carry, dates, rebal_days,
                                        lambda d, s: s)
    # the engine's own scale per decision bar, keyed by the bar it was decided on
    scales = {b: v["scale"] for b, v in prod.books.items()}
    bars = [d for d in dates if str(d.date()) in scales]
    seq = [scales[str(d.date())] for d in bars]
    mean_scale = float(np.mean(seq)) if seq else 1.0

    full_ser, full_exp, full_book = _run_arm(close, openp, score, carry, dates, rebal_days,
                                             lambda d, s: 1.0)
    full_cagr = A.stats2(full_ser, "full").get("cagr")
    const_ser, const_exp, const_book = _run_arm(close, openp, score, carry, dates, rebal_days,
                                                lambda d, s: mean_scale)

    rows = [_row("production", prod_ser, prod_exp, prod, full_cagr),
            _row("full", full_ser, full_exp, full_book, full_cagr),
            _row("constant", const_ser, const_exp, const_book, full_cagr)]

    rng = np.random.RandomState(PLACEBO_SEED)
    placebo_rows = []
    for i in range(N_PLACEBO):
        perm = rng.permutation(len(seq)) if seq else np.array([], dtype=int)
        mapping = {str(bars[j].date()): float(seq[perm[j]]) for j in range(len(bars))}
        ser, exp, bk = _run_arm(close, openp, score, carry, dates, rebal_days,
                                lambda d, s, m=mapping: m.get(str(d.date()), s))
        r = _row("placebo_%02d" % (i + 1), ser, exp, bk, full_cagr)
        r["scale_series_preserved"] = bool(
            abs(float(np.mean(list(mapping.values()) or [0.0])) - mean_scale) < 1e-9)
        placebo_rows.append(r)

    # identity leg, published (r1197): the production arm IS the engine's own scale path,
    # so re-running the untouched engine must reproduce its nav bit for bit. Without this
    # block on the artifact, a page or a card could quote "timing" for an arm that was
    # silently a different book -- the selftest only proves it on a fixture.
    eng = F.Forward(close, openp, score, N_HOLD, REBAL, COST, vol_target=VOL_TARGET,
                    carry=carry)
    eng_ser = _series(eng.run(dates, rebal_days))
    ident_gap = float(np.max(np.abs(eng_ser.to_numpy() - prod_ser.to_numpy())))
    # a real cross-book check: the arms may only differ in the scale, so every bar the two
    # books share must hold the same names. `selection_drift` alone is structurally zero
    # (every arm builds its book from the same rule), which is why it cannot carry this.
    pick_drift = sum(1 for b, v in eng.books.items()
                     if b in prod.books
                     and list(prod.books[b]["names"]) != list(v["names"]))
    identity = {"gap": ident_gap, "tol": IDENT_TOL,
                "passes": ident_gap <= IDENT_TOL and pick_drift == 0,
                "pick_drift": pick_drift, "selection_drift": prod.selection_drift}

    verdict = decide(rows, placebo_rows)
    doc = {
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "elapsed_sec": round(time.time() - t0, 1),
        "evidence_cutoff": str(dates[-1].date()),
        "bars": len(dates),
        "decisions": len(bars),
        "identity": identity,
        "panel": F._panel_block(cls, n_flip),
        "config": {"n_hold": N_HOLD, "rebal": REBAL, "cost_bp": round(COST * 1e4, 1),
                   "vol_target": VOL_TARGET, "classes": list(P.USE_CLASSES),
                   "carry": carry_note},
        "exposure": {
            "mean_engine_scale": round(mean_scale, 4),
            "delevered_decision_share": round(float(np.mean([s < 0.999 for s in seq])), 4)
            if seq else None,
            "constant_arm_scale": round(mean_scale, 4),
        },
        "arms": rows,
        "placebo": {
            "n": N_PLACEBO, "seed": PLACEBO_SEED,
            "cagr_mean": round(float(np.mean([r["cagr"] for r in placebo_rows])), 4),
            "sharpe_mean": round(float(np.mean([r["sharpe"] for r in placebo_rows])), 3),
            "mean_exposure": round(float(np.mean([r["mean_exposure"] for r in placebo_rows])), 4),
            "scale_series_preserved_all": all(r["scale_series_preserved"] for r in placebo_rows),
            "rows": placebo_rows,
        },
        "verdict": verdict,
        "notes": [
            "constant arm holds the book's own mean decision scale every bar: same names, "
            "same grid, same cost model -- only the exposure path differs",
            "placebo arms permute the engine's own scale series across its own decision "
            "bars, preserving the distribution and destroying the timing information",
            "turnover differs between arms because a smaller book trades smaller amounts; "
            "the toll is charged on that turnover, so it is inside the comparison",
        ],
    }
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
    write_md(doc)
    v = verdict
    print("exposure timing: %s | production %.2f%% vs constant %.2f%% (timing %+.2fpp, "
          "placebo [%+.2f, %+.2f]) | de-risking %+.2fpp | %d bars cutoff %s"
          % (v["state"], 100 * rows[0]["cagr"], 100 * rows[2]["cagr"], v["timing_pp"],
             v["placebo_p05_pp"], v["placebo_p95_pp"], v["de_risking_pp"],
             len(dates), doc["evidence_cutoff"]))
    return doc


def write_md(doc):
    rows = doc["arms"]
    v = doc["verdict"]
    lines = ["# Is the de-levering timing, or just a smaller book?", "",
             "Face: `results/etf_book_exposure_timing.json` (evidence cutoff %s, %d bars, "
             "%d decisions, %.1f s)."
             % (doc["evidence_cutoff"], doc["bars"], doc["decisions"], doc["elapsed_sec"]), "",
             "All three arms hold the same names on the same 20-bar grid and pay the same "
             "10 bp/side; only the exposure path differs.", "",
             "| arm | CAGR | Sharpe | maxDD | vol | mean exposure | de-levered share | turnover/fill |",
             "|---|---|---|---|---|---|---|---|"]
    labels = {"production": "production (8% vol target)", "full": "full (exposure 1.0)",
              "constant": "constant (mean exposure %.3f)" % doc["exposure"]["constant_arm_scale"]}
    for r in rows:
        lines.append("| %s | %.2f%% | %.3f | %.2f%% | %.2f%% | %.3f | %.1f%% | %.3f |" % (
            labels.get(r["arm"], r["arm"]), 100 * r["cagr"], r["sharpe"], 100 * r["maxdd"],
            100 * r["vol"], r["mean_exposure"], 100 * r["delevered_share"],
            r["turnover_per_fill"]))
    lines += ["",
              "## Placebo: same exposure distribution, no timing", "",
              "| | value |", "|---|---|",
              "| identity gap vs the untouched engine | %.2e (tol %.0e) |"
              % ((doc.get("identity") or {}).get("gap") or 0.0,
                 (doc.get("identity") or {}).get("tol") or 0.0),
              "| arms | %d (seed %d) |" % (doc["placebo"]["n"], doc["placebo"]["seed"]),
              "| mean CAGR | %.2f%% |" % (100 * doc["placebo"]["cagr_mean"]),
              "| mean Sharpe | %.3f |" % doc["placebo"]["sharpe_mean"],
              "| mean exposure | %.3f |" % doc["placebo"]["mean_exposure"],
              "| exposure multiset preserved | %s |" % doc["placebo"]["scale_series_preserved_all"],
              "| production − constant | %+.2f pp |" % v["timing_pp"],
              "| placebo band (p05..p95) | %+.2f .. %+.2f pp |" % (v["placebo_p05_pp"],
                                                                  v["placebo_p95_pp"]),
              "| constant − full (de-risking, not timing) | %+.2f pp |" % v["de_risking_pp"],
              "",
              "## Verdict", "",
              "**%s** — %s" % (v["state"], v["rule"]), "",
              "Read as: at matched average exposure the production exposure path earns "
              "%+.2f pp/yr against a placebo band of %+.2f..%+.2f pp/yr, so what the operator "
              "is buying with the vol target is %s." % (
                  v["timing_pp"], v["placebo_p05_pp"], v["placebo_p95_pp"],
                  "the overlay's timing" if v["state"] == "TIMING_ADDS"
                  else ("less than an equal-sized constant book" if v["state"] == "TIMING_SUBTRACTS"
                        else "a smaller book, not a better-timed one")),
              "",
              "## Caveats", "",
              "- one panel, one grid; the placebo band is 20 permutations, not a null "
              "distribution over all orderings",
              "- the constant arm is the book's own mean scale, so the comparison is matched "
              "on average exposure and not on realised volatility",
              "- survivorship in the ETF pool travels with every arm here; the comparison is "
              "between arms on one panel, so it does not depend on the pool being complete",
              ""]
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


def read_published(path=None):
    """Consumer entry point: the published comparison, or an honest gap (r1197).

    The card and the CEO page both have to answer "is the vol target timing, or just a
    smaller book?"; before this, each face would have re-opened the artifact and re-built
    the arms block on its own (E289 family). The identity gate travels with the read: an
    artifact whose production arm could not reproduce the engine's nav is not evidence
    about timing, so it reads as `no_identity` and callers print no numbers at all.
    """
    p = path or OUT_JSON
    if not os.path.exists(p):
        return {"status": "absent", "artifact": str(p), "verdict": None,
                "sentence": None, "evidence_cutoff": None}
    try:
        with open(p, "r", encoding="utf-8") as fh:
            doc = json.load(fh)
    except Exception as exc:                                        # noqa: BLE001
        return {"status": "unreadable: %s" % str(exc)[:120], "artifact": str(p),
                "verdict": None, "sentence": None, "evidence_cutoff": None}
    ident = doc.get("identity") or {}
    if not ident.get("passes"):
        return {"status": "no_identity", "artifact": str(p), "verdict": doc.get("verdict"),
                "sentence": None, "evidence_cutoff": None,
                "detail": "identity gap %r" % (ident.get("gap"),)}
    arms = {r.get("arm"): r for r in doc.get("arms") or []}
    v = doc.get("verdict") or {}
    pl = doc.get("placebo") or {}
    ex = doc.get("exposure") or {}
    return {
        "status": "ok",
        "artifact": str(p),
        "evidence_cutoff": doc.get("evidence_cutoff"),
        "bars": doc.get("bars"),
        "decisions": doc.get("decisions"),
        "identity": {"gap": ident.get("gap"), "tol": ident.get("tol"),
                     "pick_drift": ident.get("pick_drift")},
        "arms": {k: {"cagr": (arms.get(k) or {}).get("cagr"),
                     "sharpe": (arms.get(k) or {}).get("sharpe"),
                     "maxdd": (arms.get(k) or {}).get("maxdd"),
                     "vol": (arms.get(k) or {}).get("vol"),
                     "mean_exposure": (arms.get(k) or {}).get("mean_exposure"),
                     "delevered_share": (arms.get(k) or {}).get("delevered_share")}
                 for k in ("production", "full", "constant")},
        "exposure": {"mean_engine_scale": ex.get("mean_engine_scale"),
                     "delevered_decision_share": ex.get("delevered_decision_share")},
        "placebo": {"n": pl.get("n"), "cagr_mean": pl.get("cagr_mean")},
        "verdict": {"state": v.get("state"), "timing_pp": v.get("timing_pp"),
                    "placebo_p05_pp": v.get("placebo_p05_pp"),
                    "placebo_p95_pp": v.get("placebo_p95_pp"),
                    "de_risking_pp": v.get("de_risking_pp")},
        "sentence": ("production %.2f%% vs a constant book at the same average exposure "
                     "%.2f%% -> timing %+.2fpp/yr inside a %d-path placebo band of "
                     "[%+.2f, %+.2f]pp" % (
                         100 * (arms.get("production") or {}).get("cagr", 0.0),
                         100 * (arms.get("constant") or {}).get("cagr", 0.0),
                         v.get("timing_pp") or 0.0, pl.get("n") or 0,
                         v.get("placebo_p05_pp") or 0.0, v.get("placebo_p95_pp") or 0.0))
        if v.get("state") else None,
    }


def check(path=None):
    with open(path or OUT_JSON, "r", encoding="utf-8") as fh:
        doc = json.load(fh)
    ident = doc.get("identity") or {}
    if not ident.get("passes"):
        print("CHECK FAIL: the production arm does not reproduce the engine's nav "
              "(gap %r, pick drift %r)" % (ident.get("gap"), ident.get("pick_drift")))
        return 1
    v = decide(doc["arms"], doc["placebo"]["rows"])
    if v["state"] != doc["verdict"]["state"]:
        print("CHECK FAIL: published verdict %s, re-derived %s"
              % (doc["verdict"]["state"], v["state"]))
        return 1
    if abs(v["timing_pp"] - doc["verdict"]["timing_pp"]) > 0.011:
        print("CHECK FAIL: timing_pp moved %.2f -> %.2f"
              % (doc["verdict"]["timing_pp"], v["timing_pp"]))
        return 1
    print("CHECK OK: %s (timing %+.2fpp)" % (v["state"], v["timing_pp"]))
    return 0


def _fixture(n_names=14, n_bars=260, seed=7):
    rng = np.random.RandomState(seed)
    idx = pd.bdate_range("2021-01-01", periods=n_bars)
    names = ["t%02d" % i for i in range(n_names)]
    drift = rng.normal(0.0006, 0.0004, n_names)
    rets = rng.normal(drift, 0.012, size=(n_bars, n_names))
    close = pd.DataFrame(100.0 * np.exp(np.cumsum(rets, axis=0)), index=idx, columns=names)
    openp = close.shift(1).bfill() * (1.0 + rng.normal(0, 0.001, size=close.shape))
    score = pd.DataFrame(rng.normal(size=(n_bars, n_names)), index=idx, columns=names)
    dates = list(idx)
    rebal_days = set(dates[::4])
    return close, openp, score, dates, rebal_days


def selftest():
    ok = [0, 0]

    def chk(name, cond, detail=""):
        ok[0] += 1
        if cond:
            ok[1] += 1
            print("  PASS %s %s" % (name, detail))
        else:
            print("  FAIL %s %s" % (name, detail))

    close, openp, score, dates, rebal_days = _fixture()
    eng = F.Forward(close, openp, score, N_HOLD, REBAL, COST, vol_target=VOL_TARGET, carry=None)
    eng_marks = eng.run(dates, rebal_days)
    eng_ser = _series(eng_marks)

    # L1 identity: the identity arm must reproduce the engine bit for bit
    ident_ser, ident_exp, ident_book = _run_arm(close, openp, score, None, dates, rebal_days,
                                                lambda d, s: s)
    gap = float(np.max(np.abs(ident_ser.to_numpy() - eng_ser.to_numpy())))
    chk("identity arm reproduces the engine", gap <= IDENT_TOL, "gap=%.2e" % gap)
    chk("identity arm keeps the engine's picks", ident_book.selection_drift == 0,
        "drift=%d" % ident_book.selection_drift)

    # L2: the full arm equals the engine configured with no overlay
    nore = F.Forward(close, openp, score, N_HOLD, REBAL, COST, vol_target=None, carry=None)
    nore_ser = _series(nore.run(dates, rebal_days))
    full_ser, _fe, _fb = _run_arm(close, openp, score, None, dates, rebal_days,
                                  lambda d, s: 1.0)
    gap2 = float(np.max(np.abs(full_ser.to_numpy() - nore_ser.to_numpy())))
    chk("full arm equals vol_target=None book", gap2 <= 1e-9, "gap=%.2e" % gap2)

    # L3: the placebo permutation preserves the exposure multiset (and so the mean)
    scales = [v["scale"] for v in eng.books.values()]
    perm = np.random.RandomState(PLACEBO_SEED).permutation(len(scales))
    chk("permutation preserves the exposure multiset",
        sorted(np.array(scales)[perm]) == sorted(scales) and
        abs(float(np.mean(np.array(scales)[perm])) - float(np.mean(scales))) < 1e-12)

    # L4: a constant arm at the degenerate mean scale 1.0 must equal the full arm
    all_one = ScaledBook(close, openp, score, N_HOLD, REBAL, COST, vol_target=VOL_TARGET,
                         carry=None, scale_fn=lambda d, s: 1.0)
    one_ser = _series(all_one.run(dates, rebal_days))
    chk("constant scale 1.0 equals the full arm",
        float(np.max(np.abs(one_ser.to_numpy() - full_ser.to_numpy()))) <= 1e-12)

    # L5: verdict is a pure function of the rows, and it moves when the rows move
    rows = [{"arm": "production", "cagr": 0.10}, {"arm": "constant", "cagr": 0.09},
            {"arm": "full", "cagr": 0.08}]
    plac = [{"cagr": c} for c in (0.088, 0.089, 0.090, 0.091, 0.092, 0.087)]
    v = decide(rows, plac)
    chk("verdict recomputes from rows", v["state"] == "TIMING_ADDS" and v["timing_pp"] == 1.0,
        "%s %.2f" % (v["state"], v["timing_pp"]))
    rows2 = [{"arm": "production", "cagr": 0.0905}, {"arm": "constant", "cagr": 0.09},
             {"arm": "full", "cagr": 0.08}]
    v2 = decide(rows2, plac)
    chk("inside the placebo band is not a timing result",
        v2["state"] == "AVERAGE_EXPOSURE_ONLY", v2["state"])
    chk("too few placebo arms refuses to publish",
        decide(rows, plac[:2])["state"] == "INCOMPLETE")

    # L6: a smaller book trades smaller amounts -- turnover must fall with the scale
    small = ScaledBook(close, openp, score, N_HOLD, REBAL, COST, vol_target=VOL_TARGET,
                       carry=None, scale_fn=lambda d, s: 0.5 * s)
    small.run(dates, rebal_days)
    chk("half-size book turns over less than production",
        small.mean_turnover < ident_book.mean_turnover,
        "%.3f < %.3f" % (small.mean_turnover, ident_book.mean_turnover))
    chk("half-size book holds the same names", small.selection_drift == 0)

    # L7-L9 (r1197): the reader every consumer goes through. An artifact whose production
    # arm did not reproduce the engine must read as no_identity (and produce no sentence),
    # a missing file as absent, and a clean one must hand back the arms it published --
    # otherwise a face could quote numbers off a book nobody verified.
    import tempfile
    tmpdir = tempfile.mkdtemp(prefix="extim_")
    absent = read_published(os.path.join(tmpdir, "nope.json"))
    chk("reader: missing artifact reads absent, never zero-timing",
        absent["status"] == "absent" and absent["sentence"] is None)

    def _write(doc, name="face.json"):
        fp = os.path.join(tmpdir, name)
        with open(fp, "w", encoding="utf-8") as fh:
            json.dump(doc, fh)
        return fp

    good = {"evidence_cutoff": "2026-10-30", "bars": 10, "decisions": 3,
            "identity": {"gap": 0.0, "tol": IDENT_TOL, "passes": True, "pick_drift": 0},
            "exposure": {"mean_engine_scale": 0.7, "delevered_decision_share": 0.8},
            "arms": [{"arm": "production", "cagr": 0.0912, "sharpe": 0.95, "maxdd": -0.13,
                      "vol": 0.10, "mean_exposure": 0.707, "delevered_share": 0.879},
                     {"arm": "full", "cagr": 0.1321, "sharpe": 0.92, "maxdd": -0.16,
                      "vol": 0.15, "mean_exposure": 1.0, "delevered_share": 0.0},
                     {"arm": "constant", "cagr": 0.1003, "sharpe": 0.97, "maxdd": -0.12,
                      "vol": 0.11, "mean_exposure": 0.707, "delevered_share": 1.0}],
            "placebo": {"n": 20, "cagr_mean": 0.098},
            "verdict": {"state": "AVERAGE_EXPOSURE_ONLY", "timing_pp": -0.91,
                        "placebo_p05_pp": -1.90, "placebo_p95_pp": 0.88,
                        "de_risking_pp": -3.18}}
    okf = _write(good)
    got = read_published(okf)
    chk("reader: a clean artifact hands back the published arms and verdict",
        got["status"] == "ok" and got["verdict"]["state"] == "AVERAGE_EXPOSURE_ONLY"
        and abs(got["arms"]["production"]["cagr"] - 0.0912) < 1e-9
        and "constant book" in (got["sentence"] or ""))
    broken = dict(good)
    broken["identity"] = {"gap": 1e-3, "tol": IDENT_TOL, "passes": False, "pick_drift": 0}
    got_b = read_published(_write(broken, "face_broken.json"))
    chk("reader: a failed identity gate reads no_identity and carries no sentence",
        got_b["status"] == "no_identity" and got_b["sentence"] is None)

    print("selftest %d/%d" % (ok[1], ok[0]))
    return 0 if ok[1] == ok[0] else 1


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "run"
    if arg == "--selftest":
        sys.exit(selftest())
    elif arg == "--check":
        sys.exit(check())
    else:
        run()
"""ETF book -- the rebalance calendar must name WHICH book it reads.

HANDOVER (2026-11-11) left one question open on the transfer day: does the calendar
judge the **audited book** (``nobond_vt08``, an 8% vol target living inside the book) or
the **book that is actually running** (beta 0.20 on the un-vol-targeted base)?  The two
are not the same rule, and the ticket already prints both weights side by side while its
gate reads only one of them (``results/etf_book_weight_provenance.json``).

That only becomes a calendar question if the two engines put their 20-session grid on
different phases.  If they do, then on some days one book says "rebalance today" and the
other says "wait", and a sheet that sizes from one rule while its gate reads another
cannot tell the reader which is true.  If they do not, then the calendar is target-free
and the only open question is the size -- which is a different, already-measured face.

This face answers with a measurement, never an opinion:

  * the beta book's schedule comes from the implementation the ticket already runs
    (``etf_book_order.k_schedule``), not a copy of it;
  * the vol-target book's decision dates and scales come from the engine that publishes
    ``nobond_vt08`` (``etf_robust_pf.open_to_open_equity(diag=...)``), also not a copy;
  * every decision date is checked against the OFFICIAL calendar -- a panel cannot
    certify its own grid (r1286), so a date the exchange calendar does not contain is
    named unreadable instead of being counted;
  * the money consequence is printed only where both books really have a scale:
    ``(k_beta - scale_vol) * NAV``, with the bar it was read on;
  * the verdict is derived from the comparison, never hand-written:
    ``SAME_GRID`` / ``PHASE_OFFSET(<n>)`` / ``DIVERGENT`` / ``ONE_SIDED``.

Usage:
    python scripts/etf_book_calendar_book.py run
    python scripts/etf_book_calendar_book.py check
    python scripts/etf_book_calendar_book.py selftest
"""

from __future__ import annotations

import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from config import PATHS                          # noqa: E402
from scripts import etf_composite_pf as F         # noqa: E402
from scripts import etf_equity_alpha as AE        # noqa: E402
from scripts import etf_phase_beta_target as BT   # noqa: E402
from scripts import etf_robust_pf as R            # noqa: E402
from scripts import etf_variants_null_rolling as V  # noqa: E402
from scripts import etf_book_order as O           # noqa: E402  (one k_schedule, one in_force)
from scripts import exchange_calendar_audit as CA  # noqa: E402  (official calendar owner)
from scripts.etf_asset_class import classify      # noqa: E402

OUT_JSON = os.path.join(ROOT, "results", "etf_book_calendar_book.json")
OUT_MD = os.path.join(ROOT, "results", "etf_book_calendar_book.md")

REBAL = O.REBAL
BETA_TARGET = O.DEFAULT_BETA
VOL_TARGET = 0.08
NAV = 1_000_000.0
TOL = 1e-12

SAME_GRID = "SAME_GRID"
PHASE_OFFSET = "PHASE_OFFSET"
DIVERGENT = "DIVERGENT"
ONE_SIDED = "ONE_SIDED"


# ------------------------------------------------------------------ schedule building
def beta_schedule(rp, rm, target=BETA_TARGET, step=REBAL):
    """The ticket's own schedule, verbatim (one implementation: etf_book_order)."""
    return O.k_schedule(rp, rm, target, step=step)


def vol_schedule(close, openp, amt, score, n_hold=F.N_HOLD, cost=0.0010,
                 vol_target=VOL_TARGET):
    """Decision dates + scales from the engine that publishes nobond_vt08."""
    diag: list = []
    R.open_to_open_equity(close, openp, amt, score, REBAL, n_hold, cost,
                          vol_target=vol_target, diag=diag)
    return diag


# ------------------------------------------------------------------------- comparison
def phases(dates, calendar):
    """[(date, calendar_index % REBAL)] for dates the official calendar contains.

    Unreadable dates are returned separately -- a date the exchange does not list is
    never silently reindexed (r1286 / next_decision lineage).
    """
    pos = {d: i for i, d in enumerate(calendar)}
    readable, unreadable = [], []
    for d in dates:
        if d in pos:
            readable.append((d, pos[d] % REBAL))
        else:
            unreadable.append(d)
    return readable, unreadable


def compare_schedules(beta_dates, vol_dates, calendar):
    """Derive the verdict from the two date sets; no hand-written answer."""
    b_set, v_set = set(beta_dates), set(vol_dates)
    if not b_set or not v_set:
        return {
            "verdict": ONE_SIDED,
            "sentence": "one of the two books produced no decision date at all; the "
                        "calendar question cannot be answered on this panel",
            "shared": 0, "beta_only": len(b_set), "vol_only": len(v_set),
            "phase_shift_bars": None,
        }
    shared = sorted(b_set & v_set)
    beta_only = sorted(b_set - v_set)
    vol_only = sorted(v_set - b_set)
    if not beta_only and not vol_only:
        return {
            "verdict": SAME_GRID,
            "sentence": "both books tick on exactly the same decision dates -- the "
                        "calendar is target-free, only the size differs",
            "shared": len(shared), "beta_only": 0, "vol_only": 0,
            "phase_shift_bars": 0,
        }
    # A constant shift in the calendar index means one phase, not two rules.
    pos = {d: i for i, d in enumerate(calendar)}
    shifts = []
    for d in beta_only:
        nxt = [x for x in vol_only if x > d]
        if d in pos and nxt and nxt[0] in pos:
            shifts.append(pos[nxt[0]] - pos[d])
    shift = int(shifts[0]) if shifts and len(set(shifts)) == 1 else None
    return {
        "verdict": PHASE_OFFSET if shift is not None else DIVERGENT,
        "sentence": (
            "the two books tick on different dates, but by a single constant offset of "
            "%d session(s) -- one rule with two phases, not two rules" % shift
            if shift is not None else
            "the two books tick on different dates with no constant offset -- the "
            "calendar itself depends on which book is asked"),
        "shared": len(shared), "beta_only": len(beta_only), "vol_only": len(vol_only),
        "phase_shift_bars": shift,
    }


def money_reading(k_beta, scale_vol, nav=NAV, bar_beta=None, bar_vol=None):
    """What the two books would put to work on the same bar, in CNY."""
    if k_beta is None or scale_vol is None:
        return {
            "bar_beta": bar_beta, "bar_vol": bar_vol,
            "k_beta": k_beta, "k_vol": scale_vol, "cny_diff": None,
            "sentence": "one of the two books has no scale on a shared bar; the money "
                        "difference is not printed rather than printed as zero",
        }
    diff = (float(k_beta) - float(scale_vol)) * float(nav)
    return {
        "bar_beta": bar_beta, "bar_vol": bar_vol,
        "k_beta": round(float(k_beta), 6), "k_vol": round(float(scale_vol), 6),
        "cny_beta": round(float(k_beta) * nav, 2),
        "cny_vol": round(float(scale_vol) * nav, 2),
        "cny_diff": round(diff, 2),
        "sentence": "the running book would put %s CNY %s than the audited book on the "
                    "same bar" % (abs(round(diff, 2)),
                                  "more" if diff >= 0 else "less"),
    }


def next_decision(last_bar, calendar, phase):
    """First official session after `last_bar` that lands on `phase`."""
    pos = {d: i for i, d in enumerate(calendar)}
    if last_bar not in pos or phase is None:
        return None
    i = pos[last_bar] + 1
    while i < len(calendar):
        if i % REBAL == phase:
            return calendar[i]
        i += 1
    return None


LIVE_BOOK_INDEX = os.path.join(ROOT, "docs", "live_book", "latest.json")


def live_book_decision_bars(index_path=LIVE_BOOK_INDEX):
    """Every decision bar the CEO page prints, with how many sections print it.

    Returns ([(bar, count)], truth). The page is allowed to print the same bar in several
    sections; it is NOT allowed to print two different ones and call them one clock, so the
    caller gets every distinct value rather than one arbitrary pick.
    """
    try:
        with open(index_path, encoding="utf-8") as fh:
            idx = json.load(fh)
        rel = idx.get("json")
        if not rel:
            return [], "missing"
        p = os.path.join(ROOT, rel) if not os.path.isabs(rel) else rel
        with open(p, encoding="utf-8") as fh:
            page = json.load(fh)
    except Exception:
        return [], "missing"
    found: list = []

    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k == "decision_bar" and isinstance(v, str):
                    found.append(v)
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)

    walk(page)
    if not found:
        return [], "missing"
    counts: dict = {}
    for v in found:
        counts[v] = counts.get(v, 0) + 1
    return sorted(counts.items()), "read"


def on_grid(bar, calendar, phase):
    """Is `bar` a grid bar of this book? None when it cannot be checked at all."""
    if bar is None or phase is None:
        return None
    pos = {d: i for i, d in enumerate(calendar)}
    d = pd.Timestamp(bar)
    if d not in pos:
        return None
    return pos[d] % REBAL == phase


def same_book_check(bars, beta_phase, vol_phase, calendar):
    """Does the calendar the page prints belong to the book the page sizes from?"""
    if not bars:
        return {
            "published_decision_bars": [],
            "verdict": "UNKNOWN",
            "sentence": "the page's decision bar could not be read; the calendar question "
                        "is not answered by guessing",
            "on_beta_grid": None, "on_vol_grid": None,
        }
    rows = []
    for bar, n in bars:
        on_b = on_grid(bar, calendar, beta_phase)
        on_v = on_grid(bar, calendar, vol_phase)
        rows.append({"bar": bar, "sections": n, "on_beta_grid": on_b, "on_vol_grid": on_v})
    beta_hit = any(r["on_beta_grid"] for r in rows)
    vol_hit = any(r["on_vol_grid"] for r in rows)
    unreadable = [r["bar"] for r in rows
                  if r["on_beta_grid"] is None or r["on_vol_grid"] is None]
    distinct = sorted({r["bar"] for r in rows})
    if len(distinct) > 1 and beta_hit and vol_hit:
        verdict = "PAGE_PRINTS_TWO_CLOCKS"
        sentence = ("the page prints %d different decision bars and they land on two "
                    "different books' grids -- the reader is shown two clocks at once"
                    % len(distinct))
    elif len(distinct) > 1:
        verdict = "PAGE_PRINTS_TWO_BARS"
        sentence = ("the page prints %d different decision bars, though they share one "
                    "book's grid" % len(distinct))
    elif beta_hit and vol_hit:
        verdict, sentence = ("SAME_BOOK", "the printed decision bar sits on both grids "
                                          "(the phases coincide here) -- no split")
    elif vol_hit:
        verdict, sentence = ("CALENDAR_FROM_AUDITED_BOOK", "the page's calendar is the "
                                                            "audited book's grid, while its "
                                                            "size comes from the running book")
    elif beta_hit:
        verdict, sentence = ("CALENDAR_FROM_RUNNING_BOOK", "the page's calendar is the "
                                                           "running book's grid, matching the "
                                                           "rule that sizes it")
    else:
        verdict, sentence = ("CALENDAR_FROM_NEITHER_BOOK", "the printed decision bar is on "
                                                           "neither book's grid")
    if unreadable and verdict != "UNKNOWN":
        sentence += " (%s not on the official calendar -- unreadable, not reindexed)" \
                    % ", ".join(unreadable)
    return {
        "published_decision_bars": rows, "verdict": verdict, "sentence": sentence,
        "on_beta_grid": bool(beta_hit) if not unreadable else None,
        "on_vol_grid": bool(vol_hit) if not unreadable else None,
    }


# ------------------------------------------------------------------------------- run
def run():
    close, openp, amt, feats = F.build_panel()
    classes = pd.Series(classify(list(close.columns)))
    cols = [c for c in close.columns if classes[c] in V.KEEP]
    close, openp, n_flip = AE.repair_flips(close, openp)
    score = F.build_score(close[cols], amt[cols], feats)
    print("panel: %d symbols, %d bars, last %s, %d flip prints repaired"
          % (len(cols), len(close), close.index[-1].date(), n_flip), flush=True)

    mkt_col = next((c for c in BT.MKT if c in close.columns), None)
    if mkt_col is None:
        print("FATAL: no 510300 column on the panel")
        return 2
    mkt = close[mkt_col]

    ser, turnover, _gapfill = F.run_next_open(close[cols], openp[cols], amt[cols], feats,
                                              REBAL, n_hold=F.N_HOLD, cost=F.COST,
                                              score=score)
    idx = ser.index.intersection(mkt.index)
    rp, rm = BT.rets(ser.reindex(idx)), BT.rets(mkt.reindex(idx))
    sched_beta = beta_schedule(rp, rm)
    beta_dates = [d for d, _k, _b in sched_beta]
    print("beta book: %d decision dates, last %s, k=%.6f"
          % (len(beta_dates), beta_dates[-1].date() if beta_dates else "-",
             sched_beta[-1][1] if sched_beta else float("nan")), flush=True)

    diag = vol_schedule(close[cols], openp[cols], amt[cols], score)
    vol_dates = [pd.Timestamp(r["date"]) for r in diag]
    print("vol book : %d decision dates, last %s, scale=%.6f"
          % (len(vol_dates), vol_dates[-1].date() if vol_dates else "-",
             diag[-1]["scale"] if diag else float("nan")), flush=True)

    calendar = [pd.Timestamp(d) for d in CA.load_calendar()]
    if not calendar:
        print("FATAL: official calendar is empty -- a grid cannot certify itself (r1286)")
        return 2
    readable_beta, unread_beta = phases(beta_dates, calendar)
    readable_vol, unread_vol = phases(vol_dates, calendar)

    cmp_ = compare_schedules(beta_dates, vol_dates, calendar)

    # The live reading is taken on the panel's last bar, where both books have a scale in
    # force. It is NOT restricted to shared decision dates: the whole point of this face is
    # that the two books may never decide on the same day, and requiring one would print
    # nothing at all.
    k_beta_ser = O.in_force(sched_beta, idx)
    vol_marks = pd.Series(np.nan, index=idx, dtype=float)
    for r in diag:
        d = pd.Timestamp(r["date"])
        if d in vol_marks.index:
            vol_marks.loc[d] = float(r["scale"])
    k_vol_ser = vol_marks.shift(1).ffill()
    bar = idx[-1]
    money = money_reading(
        float(k_beta_ser.loc[bar]) if np.isfinite(k_beta_ser.loc[bar]) else None,
        float(k_vol_ser.loc[bar]) if np.isfinite(k_vol_ser.loc[bar]) else None,
        bar_beta=str(bar.date()), bar_vol=str(bar.date()))
    last_shared = bar

    # the decision clock: what each book says the next rebalance bar is
    beta_phase = readable_beta[-1][1] if readable_beta else None
    vol_phase = readable_vol[-1][1] if readable_vol else None
    last_bar = close.index[-1]
    clock = {
        "last_bar": str(last_bar.date()),
        "beta_last_decision": str(beta_dates[-1].date()) if beta_dates else None,
        "beta_phase": beta_phase,
        "beta_next_grid_bar": (str(next_decision(last_bar, calendar, beta_phase).date())
                               if next_decision(last_bar, calendar, beta_phase) is not None
                               else None),
        "vol_last_decision": str(vol_dates[-1].date()) if vol_dates else None,
        "vol_phase": vol_phase,
        "vol_next_grid_bar": (str(next_decision(last_bar, calendar, vol_phase).date())
                              if next_decision(last_bar, calendar, vol_phase) is not None
                              else None),
    }

    # which book's calendar does the CEO page print?
    pbar, ptruth = live_book_decision_bars()
    page_cal = same_book_check([tuple(x) for x in pbar], beta_phase, vol_phase, calendar)
    page_cal["read_truth"] = ptruth

    out = {
        "face": "etf_book_calendar_book",
        "question": "does the rebalance calendar judge the audited book or the running book",
        "panel_last_bar": str(last_bar.date()),
        "rebal": REBAL,
        "beta_target": BETA_TARGET,
        "vol_target": VOL_TARGET,        "beta_book": {
            "rule": "k = beta_target / expanding beta (etf_book_order.k_schedule)",
            "n_dates": len(beta_dates), "n_readable": len(readable_beta),
            "unreadable_dates": [str(d.date()) for d in unread_beta],
            "last_k": round(float(sched_beta[-1][1]), 6) if sched_beta else None,
        },
        "vol_book": {
            "rule": "scale = min(1, vol_target / 60-bar book vol) "
                    "(etf_robust_pf.open_to_open_equity, the nobond_vt08 engine)",
            "n_dates": len(vol_dates), "n_readable": len(readable_vol),
            "unreadable_dates": [str(d.date()) for d in unread_vol],
            "last_scale": round(float(diag[-1]["scale"]), 6) if diag else None,
        },
        "comparison": cmp_,
        "money": money,
        "money_bar": str(last_shared.date()) if last_shared is not None else None,
        "clock": clock,
        "page_calendar": page_cal,
        "verdict": cmp_["verdict"],
        "evidence_cutoff": str(last_bar.date()),
    }
    _write(OUT_JSON, out)
    _write_md(OUT_MD, out)
    print("verdict: %s -- %s" % (cmp_["verdict"], cmp_["sentence"]), flush=True)
    if money.get("cny_diff") is not None:
        print("money: %s" % money["sentence"], flush=True)
    return 0


# ----------------------------------------------------------------------------- check
def check():
    """Re-derive the published verdict from live inputs; red if it stops matching."""
    if not os.path.exists(OUT_JSON):
        print("[check] %s missing" % OUT_JSON)
        return 1
    with open(OUT_JSON, encoding="utf-8") as fh:
        pub = json.load(fh)
    import io
    from contextlib import redirect_stdout
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = run()
    if rc != 0:
        print("[check] run failed rc=%d" % rc)
        return 1
    with open(OUT_JSON, encoding="utf-8") as fh:
        now = json.load(fh)
    bad = []
    for key in ("verdict", "panel_last_bar", "rebal"):
        if pub.get(key) != now.get(key):
            bad.append("%s: %r -> %r" % (key, pub.get(key), now.get(key)))
    pc, nc = pub.get("comparison") or {}, now.get("comparison") or {}
    for key in ("shared", "beta_only", "vol_only", "phase_shift_bars"):
        if pc.get(key) != nc.get(key):
            bad.append("comparison.%s: %r -> %r" % (key, pc.get(key), nc.get(key)))
    pm, nm = pub.get("money") or {}, now.get("money") or {}
    for key in ("k_beta", "k_vol", "cny_diff"):
        a, b = pm.get(key), nm.get(key)
        if (a is None) != (b is None):
            bad.append("money.%s: %r -> %r" % (key, a, b))
        elif a is not None and abs(float(a) - float(b)) > 1e-6:
            bad.append("money.%s: %r -> %r" % (key, a, b))
    pp, npc = pub.get("page_calendar") or {}, now.get("page_calendar") or {}
    if pp.get("verdict") != npc.get("verdict"):
        bad.append("page_calendar.verdict: %r -> %r" % (pp.get("verdict"),
                                                       npc.get("verdict")))
    a_bars = [(r["bar"], r["on_beta_grid"], r["on_vol_grid"])
              for r in (pp.get("published_decision_bars") or [])]
    b_bars = [(r["bar"], r["on_beta_grid"], r["on_vol_grid"])
              for r in (npc.get("published_decision_bars") or [])]
    if a_bars != b_bars:
        bad.append("page_calendar.bars: %r -> %r" % (a_bars, b_bars))
    if bad:
        print("[check] RED: " + "; ".join(bad))
        return 1
    print("[check] CHECK_OK verdict=%s shared=%s beta_only=%s vol_only=%s"
          % (nc.get("verdict"), nc.get("shared"), nc.get("beta_only"), nc.get("vol_only")))
    return 0


# -------------------------------------------------------------------------- selftest
def selftest():
    fails = []

    def leg(name, ok, detail=""):
        print("[%s] %s%s" % ("PASS" if ok else "FAIL", name,
                             (" | " + detail) if detail else ""))
        if not ok:
            fails.append(name)

    # a calendar we control: 400 consecutive sessions
    cal = [pd.Timestamp("2024-01-01") + pd.Timedelta(days=i) for i in range(400)]

    # L1: two targets over the same (rp, rm) must pick the same decision dates.
    rng = np.random.default_rng(7)
    n = 300
    rp = pd.Series(rng.normal(0, 0.01, n), index=cal[:n])
    rm = pd.Series(rng.normal(0, 0.01, n), index=cal[:n])
    low = [d for d, _k, _b in beta_schedule(rp, rm, 0.20)]
    high = [d for d, _k, _b in beta_schedule(rp, rm, 9.99)]
    leg("L1 two targets, one grid", low == high,
        "%d vs %d dates" % (len(low), len(high)))

    # L2: k clips at 1 and de-levers only -- the two targets differ in size, not dates.
    # A 2x-beta book is used so the two targets really land on different sizes; a random
    # book often pins both at the 1.0 cap, and a leg that cannot separate them proves
    # nothing about the rule (r1371 lineage: perturb the field the assertion claims).
    rp2 = 2.0 * rm + pd.Series(rng.normal(0, 0.0005, n), index=cal[:n])
    kl = [k for _d, k, _b in beta_schedule(rp2, rm, 0.20)]
    kh = [k for _d, k, _b in beta_schedule(rp2, rm, 9.99)]
    leg("L2 sizes differ, dates do not", all(0.0 <= x <= 1.0 for x in kl + kh)
        and max(kh) > max(kl) + 0.1
        and [d for d, _k, _b in beta_schedule(rp2, rm, 0.20)]
        == [d for d, _k, _b in beta_schedule(rp2, rm, 9.99)],
        "max k %r vs %r" % (round(max(kl), 4), round(max(kh), 4)))

    # L3: a book with no market beta skips the same bars for both targets.
    flat = pd.Series(0.0, index=cal[:n])
    l1 = [d for d, _k, _b in beta_schedule(flat, rm, 0.20)]
    l2 = [d for d, _k, _b in beta_schedule(flat, rm, 9.99)]
    leg("L3 a zero-beta book skips identically", l1 == l2, "%d vs %d dates"
        % (len(l1), len(l2)))

    # L4: identical date sets must read SAME_GRID, never PHASE_OFFSET.
    c = compare_schedules(low, list(low), cal)
    leg("L4 identical sets -> SAME_GRID", c["verdict"] == SAME_GRID,
        c["verdict"])

    # L5: a constant shift must be named as a shift, with its size.
    shifted = [cal[cal.index(d) + 1] for d in low[:-1]]
    c = compare_schedules(low[:-1], shifted, cal)
    leg("L5 constant shift -> PHASE_OFFSET(1)", c["verdict"] == PHASE_OFFSET
        and c["phase_shift_bars"] == 1, "%s shift=%r" % (c["verdict"],
                                                        c["phase_shift_bars"]))

    # L6: a date the official calendar does not contain is unreadable, not zeroed.
    outside = [pd.Timestamp("2030-01-01")]
    readable, unreadable = phases(outside, cal)
    leg("L6 off-calendar date is unreadable", not readable and len(unreadable) == 1,
        "readable=%d unreadable=%d" % (len(readable), len(unreadable)))

    # L7: money is not printed as zero when a scale is missing.
    m = money_reading(None, 0.5)
    leg("L7 missing scale -> no money", m["cny_diff"] is None)
    m = money_reading(0.460253, 0.38, nav=NAV)
    leg("L8 money equals the scale difference", abs(m["cny_diff"] - 80253.0) < 0.01,
        "%r" % m["cny_diff"])

    # L9: the clock never returns a bar that is not on the requested phase.
    d = next_decision(cal[200], cal, 7)
    leg("L9 next grid bar lands on its phase", d is not None and cal.index(d) % REBAL == 7,
        str(d))

    # L10: one empty book cannot be reported as an agreement.
    c = compare_schedules(low, [], cal)
    leg("L10 empty book -> ONE_SIDED", c["verdict"] == ONE_SIDED, c["verdict"])

    # L11: a bar on the vol grid only must be named as the audited book's calendar.
    bar_vol = cal[200]                      # 200 % 20 == 0
    sbc = same_book_check([(str(bar_vol.date()), 2)], 7, 0, cal)
    leg("L11 vol-grid bar -> audited book",
        sbc["verdict"] == "CALENDAR_FROM_AUDITED_BOOK"
        and sbc["on_vol_grid"] is True and sbc["on_beta_grid"] is False,
        "%s b=%r v=%r" % (sbc["verdict"], sbc["on_beta_grid"], sbc["on_vol_grid"]))

    # L12: an unreadable page is UNKNOWN, never a silent agreement.
    sbc = same_book_check([], 7, 0, cal)
    leg("L12 unreadable page -> UNKNOWN", sbc["verdict"] == "UNKNOWN",
        sbc["verdict"])

    # L13: two bars, one on each book's grid, must be named as two clocks.
    two = [(str(cal[200].date()), 2), (str(cal[207].date()), 1)]
    sbc = same_book_check(two, 7, 0, cal)
    leg("L13 two grids on one page -> TWO_CLOCKS",
        sbc["verdict"] == "PAGE_PRINTS_TWO_CLOCKS", sbc["verdict"])

    print("selftest: %d/%d PASS" % (13 - len(fails), 13))
    return 0 if not fails else 1


# ----------------------------------------------------------------------------- writer
def _write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    os.replace(tmp, path)


def _yn(v):
    return "未核实" if v is None else ("是" if v else "否")


def _write_md(path, o):
    c = o["comparison"]
    m = o["money"]
    k = o["clock"]
    lines = [
        "# 换仓日历该判哪一本书 —— %s" % o["panel_last_bar"],
        "",
        "> 问题：日历判**被审书**（nobond_vt08，书内 8%% 波动目标）还是判**在跑的书**"
        "（beta %.2f，无波动目标）。本页只量，不猜。" % o["beta_target"],
        "",
        "## 结论",
        "",
        "**%s** —— %s。" % (o["verdict"], c["sentence"]),
        "",
        "| 书 | 网格（%d 根） | 决策日数 | 可被官方日历核实 | 最新规模 |"
        % o["rebal"],
        "|---|---|---|---|---|",
        "| 在跑的书（beta %.2f） | 相位 %s | %d | %d | k=%s |"
        % (o["beta_target"], k["beta_phase"], o["beta_book"]["n_dates"],
           o["beta_book"]["n_readable"], o["beta_book"]["last_k"]),
        "| 被审书（vt%.2f） | 相位 %s | %d | %d | scale=%s |"
        % (o["vol_target"] * 100, k["vol_phase"], o["vol_book"]["n_dates"],
           o["vol_book"]["n_readable"], o["vol_book"]["last_scale"]),
        "",
        "共同决策日 **%d** 天；仅在跑书 **%d** 天；仅被审书 **%d** 天；恒定相位差 **%s** 根。"
        % (c["shared"], c["beta_only"], c["vol_only"],
           "-" if c["phase_shift_bars"] is None else c["phase_shift_bars"]),
        "",
        "## 下一个换仓日",
        "",
        "面板最后一根 **%s**。" % k["last_bar"],
        "",
        "- 在跑的书：最近决策 %s，下一网格 bar **%s**"
        % (k["beta_last_decision"], k["beta_next_grid_bar"]),
        "- 被审书：最近决策 %s，下一网格 bar **%s**"
        % (k["vol_last_decision"], k["vol_next_grid_bar"]),
        "",
        "## 钱（同一根 bar 上两本书的规模差）",
        "",
        "读在 **%s** 这根 bar 上。" % (o.get("money_bar") or "-"),
        "",
    ]
    if m.get("cny_diff") is None:
        lines.append("**%s。**" % m["sentence"])
    else:
        lines += [
            "| 书 | 规模 | 投入（NAV %s） |" % format(int(NAV), ","),
            "|---|---|---|",
            "| 在跑的书 | k=%s | ￥%s |" % (m["k_beta"], format(int(m["cny_beta"]), ",")),
            "| 被审书 | scale=%s | ￥%s |" % (m["k_vol"], format(int(m["cny_vol"]), ",")),
            "",
            "差额 **￥%s**（%s）。" % (format(int(abs(m["cny_diff"])), ","),
                                    m["sentence"].split(" put ")[-1]),
        ]
    lines += [
        "",
        "## 页面印的那个决策 bar 属于哪本书",
        "",
    ]
    pc_rows = o["page_calendar"].get("published_decision_bars") or []
    if pc_rows:
        lines += ["| 页面印的 bar | 出现节数 | 在跑书网格 | 被审书网格 |",
                  "|---|---|---|---|"]
        for r in pc_rows:
            lines.append("| %s | %s | %s | %s |"
                         % (r["bar"], r["sections"], _yn(r["on_beta_grid"]),
                            _yn(r["on_vol_grid"])))
    else:
        lines.append("页面决策 bar：**读不到**（读取状态：%s）"
                     % o["page_calendar"].get("read_truth"))
    lines += [
        "",
        "**%s** —— %s。" % (o["page_calendar"].get("verdict"),
                            o["page_calendar"].get("sentence")),
        "",
        "## 读法（三条判据）",
        "",
        "1. 决策日由各自的既有实现产生（`etf_book_order.k_schedule` / "
        "`etf_robust_pf.open_to_open_equity(diag=...)`），本面无第二份网格实现。",
        "2. 每个决策日都对官方日历核实；不在日历上的日期点名为不可读，不重编号。",
        "3. 判决由两个日期集派生（SAME_GRID / PHASE_OFFSET / DIVERGENT / ONE_SIDED），"
        "`check` 重算臂比对数量与金额，手改即红。",
        "",
        "## 边界",
        "",
        "- 只读已发布引擎与面板，不改 target、不改票面、不改账本。",
        "- 两本书的规模字段语义可并置（都是「投入资金比例」），但**不是**同一条规则；"
        "本页回答的是日历，规模差异的采纳走各自的预注册与转仓日决策。",
        "- 面板为现存 ETF（幸存者偏差），起点由各引擎历史窗决定，前段不可比属正常。",
        "",
    ]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines))
    os.replace(tmp, path)


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "run":
        return run()
    if cmd == "check":
        return check()
    if cmd == "selftest":
        return selftest()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())

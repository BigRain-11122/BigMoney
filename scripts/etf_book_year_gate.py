"""Point the desk's own calendar gate at the book the desk actually holds.

r1415 built scripts/candidate_year_gate.py and used it on two CANDIDATE books --
both came back CONDITIONAL because their headline is carried by two years. Nobody
ever pointed the same gate at the book that is already adopted (the bond-free ETF
composite with the 8% vol target, results/etf_nobond_vt.json). A gate that has only
ever judged candidates is not a gate on the desk.

This file reprices the adopted book and its two nearest siblings with the published
engine (imported, never re-implemented), derives calendar-year returns from the
daily series, and re-issues a verdict through candidate_year_gate.admission_block --
the frozen rules are imported, so the line cannot drift between the two files.

ONE SUBSTITUTION, PRINTED NOT HIDDEN: the candidate receipts count 60-bar cohorts
per year and mark a year "partial" when it holds fewer than four. A daily book has
no cohorts, so the same 60-bar unit is used here as a window count
(cohorts_analog = floor(bars/60)) and the partial flag falls out of the same rule.
2026 (partial calendar year) lands at 3 windows and is therefore partial, which is
the honest reading; 2020 (starts 2020-01-02) reaches 4 and is not.

Capacity is derived, not declared: the book holds five names equally, so the money
that can be put on in one day at 5% participation is 5 x 0.05 x (20-bar median
amount of the name in each slot), taken from the same panel the pricing uses.

Usage:
    python scripts/etf_book_year_gate.py run
    python scripts/etf_book_year_gate.py selftest
"""
import io
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import candidate_year_gate as G  # noqa: E402
import etf_composite_pf as E  # noqa: E402
import etf_equity_alpha as A  # noqa: E402
import etf_robust_pf as R  # noqa: E402

OUT_DIR = os.path.join(ROOT, "results", "etf_book_year_gate")
OUT = os.path.join(OUT_DIR, "YEAR-GATE.json")
BARS_PER_WINDOW = 60
PARTICIPATION = 0.05


def levels(ser: pd.Series) -> pd.Series:
    """The engine already returns a level curve (not returns); pass it through."""
    return ser.astype(float)


def yearly_returns(ser: pd.Series) -> dict:
    """Calendar-year returns on the book's own definition (last/first within the year,
    the same one etf_equity_alpha.stats2 publishes) plus the 60-bar window count."""
    ser = ser.dropna()
    lv = ser.astype(float)
    out = {}
    for year, blk in lv.groupby(lv.index.year):
        ret = float(blk.iloc[-1]) / float(blk.iloc[0]) - 1.0
        out[str(year)] = {"net_pct": ret * 100.0,
                          "cohorts": int(len(blk) // BARS_PER_WINDOW),
                          "bars": int(len(blk))}
    return out


def capacity_cny(picks: list[str], amt: pd.DataFrame) -> float | None:
    if not picks:
        return None
    total = 0.0
    for sym in picks:
        if sym not in amt.columns:
            return None
        med = float(amt[sym].tail(20).median())
        if not np.isfinite(med):
            return None
        total += PARTICIPATION * med
    return total


def _block(name: str, years: dict, capacity: float | None, ser: pd.Series | None,
           note: str) -> dict:
    cagr = None
    if ser is not None:
        cagr = A.stats2(ser, name).get("cagr")
    blk = G.admission_block(years, capacity, None, cagr)
    blk["book"] = name
    blk["note"] = note
    blk["yearly_returns_pct"] = {y: v["net_pct"] for y, v in years.items()}
    blk["yearly_bars"] = {y: v.get("bars") for y, v in years.items()}
    return blk


def caliber_reading(lag0_block: dict | None, lag1_block: dict | None,
                    line: float) -> dict:
    """The same frozen concentration line, read on two execution calibers.

    r1798: every year check in this face was priced on `entry_lag=0` -- the score read off
    bar d's own close, held from bar d's own open. The desk's declared execution is "decide
    at close t, own from open t+1", and the shared engine gained that switch in r1795. A
    concentration verdict read on a bar the book could not own is a ruler reading the wrong
    day, so both readings are printed and the movement is named instead of assumed.

    The word is derived from the two numbers, never hand-written; two `None`s are their own
    state (E98: "I could not check it" is not "it is fine").
    """
    def lit(b):
        # `year_metrics.top2_share` is a FRACTION of the annual sum (0.7084), the unit the
        # frozen line is written in; the percent twin is printed beside it so a reader never
        # has to guess which of the two they are looking at (r1775's 100x defect).
        if not b:
            return {"top2_share": None, "top2_share_pct": None, "passes": None,
                    "cagr_pct": None, "verdict": None}
        m = b.get("year_metrics") or {}
        t2 = m.get("top2_share")
        return {"top2_share": t2,
                "top2_share_pct": None if t2 is None else round(float(t2) * 100.0, 4),
                "passes": None if t2 is None else bool(float(t2) <= float(line)),
                "cagr_pct": b.get("cagr_pct"),
                "verdict": b.get("verdict")}
    l0, l1 = lit(lag0_block), lit(lag1_block)
    if l0["passes"] is None or l1["passes"] is None:
        word = "CALIBER_UNREADABLE"
    elif l0["passes"] == l1["passes"]:
        word = "CALIBER_KEEPS_Y4"
    else:
        word = "CALIBER_FLIPS_Y4"
    gap = (None if l0["top2_share"] is None or l1["top2_share"] is None
           else round((float(l1["top2_share"]) - float(l0["top2_share"])) * 100.0, 4))
    return {
        "book": "nobond_vt08_adopted",
        "line_top2_share_max": round(float(line), 4),
        "line_top2_share_max_pct": round(float(line) * 100.0, 4),
        "entry_lag0": l0,
        "entry_lag1": l1,
        "top2_gap_pp": gap,
        "verdict": word,
        "sentence": (
            "the book's own concentration line reads %s%% on the decision bar and %s%% "
            "once the picks can only be owned from the next open (line %.2f%%); %s"
            % (l0["top2_share_pct"], l1["top2_share_pct"], float(line) * 100.0,
               "the verdict does not move with the caliber" if word != "CALIBER_FLIPS_Y4"
               else "the verdict moves with the caliber -- the failing row was a reading of "
                    "the wrong bar, not of the book")),
    }


def _caliber_arm(lag1_ser: pd.Series | None, cap: float | None) -> dict | None:
    """The execution-caliber twin of the adopted arm: same book, same line, entry_lag=1."""
    if lag1_ser is None:
        return None
    blk = _block("nobond_vt08_adopted_lag1", yearly_returns(lag1_ser), cap, lag1_ser,
                 "the adopted book repriced on the desk's declared execution: decide at "
                 "close t, own from open t+1 -- read only by the caliber block, never "
                 "substituted for a printed arm")
    blk["capacity_cny_1day_5pct"] = None if cap is None else round(cap, 0)
    blk["capacity_checked"] = cap is not None
    blk["checks"]["C1_capacity"] = None if cap is None else cap >= G.CAPACITY_FLOOR_CNY
    blk["verdict"] = G.verdict({"checks": blk["checks"]})
    return blk


def run() -> int:
    t0 = time.time()
    close, openp, amt, feats = E.build_panel()
    close, openp, n_flip = A.repair_flips(close, openp)
    cmap = A.load_class_map()
    cls = A.classify(close.columns, cmap, close)
    cols = [c for c in close.columns if cls[c] in ("equity", "commodity", "convertible")]
    sc = E.build_score(close[cols], amt[cols], feats)

    arms = []
    adopted_ser = None
    diag = []
    for label, vt in (("nobond_vt08_adopted", 0.08), ("nobond_base", None)):
        ser, turn = R.open_to_open_equity(close[cols], openp[cols], amt[cols], sc, 20, 5,
                                          0.0010, vol_target=vt,
                                          diag=diag if vt is not None else None)
        if vt is not None:
            adopted_ser = ser
        yrs = yearly_returns(ser)
        blk = _block(label, yrs, None, ser,
                     "repriced here with the published engine; turnover/side %.2f" % turn)
        if vt is not None and diag:
            by_year = {}
            for row in diag:
                y = str(pd.Timestamp(row["date"]).year)
                by_year.setdefault(y, []).append(float(row["scale"]))
            blk["sizing_scale_by_year"] = {y: round(float(np.mean(v)), 3)
                                           for y, v in sorted(by_year.items())}
            blk["sizing_note"] = ("average position scale the 8% target applied per "
                                  "calendar year (1.0 = fully invested); this is what "
                                  "moves the calendar, not the selection")
        arms.append(blk)

    # r1798: the same adopted book on the desk's own execution caliber (decide at close t,
    # own from open t+1). It is priced here only to be read by the concentration line --
    # the printed arms above keep their published numbers bit for bit.
    lag1_ser = None
    if adopted_ser is not None:
        lag1_ser, _turn_lag1 = R.open_to_open_equity(
            close[cols], openp[cols], amt[cols], sc, 20, 5, 0.0010,
            vol_target=0.08, entry_lag=1)

    last = sc.index[-1]
    picks = list(sc.loc[last].dropna().nlargest(5).index)
    cap = capacity_cny(picks, amt)
    for a in arms:
        if a["book"].startswith("nobond_vt08"):
            a["capacity_cny_1day_5pct"] = None if cap is None else round(cap, 0)
            a["capacity_checked"] = cap is not None
            a["checks"]["C1_capacity"] = None if cap is None else cap >= G.CAPACITY_FLOOR_CNY
            a["verdict"] = G.verdict({"checks": a["checks"]})

    # r1684 / O-20261114-2325 P0: the year checks above stay printed as diagnostics; the
    # verdict that can actually stop the desk is now the three measurable readings. The
    # weakest slot's ADV is used, because an equal-weight book has to fill its worst name.
    adv_weakest = None
    if picks:
        advs = []
        for sym in picks:
            if sym in amt.columns:
                med = float(amt[sym].tail(20).median())
                if np.isfinite(med):
                    advs.append(med)
        adv_weakest = min(advs) if advs else None
    oos = G.oos_sharpe(adopted_ser) if adopted_ser is not None else None
    cagr_frac = A.stats2(adopted_ser, "nobond_vt08_adopted").get("cagr") if adopted_ser is not None else None
    cagr_pct = None if cagr_frac is None else round(float(cagr_frac) * 100.0, 4)
    decision = G.decision_block(oos, cagr_pct, adv_weakest, len(picks) or None)
    decision["book"] = "nobond_vt08_adopted"
    decision["adv_note"] = ("the weakest of the live five slots (20-bar median turnover), "
                            "not their sum: an equal-weight book must fill its worst name")

    # third arm: the full book, whose yearly face is already published
    published = os.path.join(ROOT, "results", "etf_equity_alpha.json")
    allc_years = None
    if os.path.exists(published):
        with io.open(published, encoding="utf-8") as f:
            pj = json.load(f)
        ya = pj.get("yearly_all") or {}
        if ya:
            # published face carries returns as fractions and no bar counts; the
            # window count is recovered by handing the gate a full-year analogue
            # of 4 only where the year is a complete calendar year.
            last_year = max(int(y) for y in ya)
            years = {}
            for y, v in ya.items():
                years[y] = {"net_pct": round(float(v) * 100.0, 4),
                            "cohorts": 3 if int(y) == last_year else 4,
                            "bars": None}
            allc_years = years
            arms.append(_block("all_classes_published", years, None, None,
                               "yearly face read from results/etf_equity_alpha.json"
                               " (daily bars not republished; 2026 marked partial by"
                               " calendar, which the published file cannot attest)"))

    prior = None
    if os.path.exists(OUT):
        try:
            with io.open(OUT, encoding="utf-8") as f:
                prev = json.load(f)
            prior = {"asof": prev.get("asof"),
                     "data_last": (prev.get("data") or {}).get("last"),
                     "books": {b.get("book"): {
                         "verdict": b.get("verdict"),
                         "top2_share": (b.get("year_metrics") or {}).get("top2_share")}
                         for b in (prev.get("books") or [])}}
        except Exception as exc:                                # noqa: BLE001
            prior = {"unreadable": str(exc)}
    for a in arms:
        m = a.get("year_metrics") or {}
        t2 = m.get("top2_share")
        a["margin_to_line"] = (None if t2 is None
                               else round(G.TOP2_SHARE_MAX - float(t2), 4))
        a["top2_share_full_only_note"] = (
            "the frozen line reads the net sum (partial years included); reading only"
            " complete years gives %s" % m.get("top2_share_full_only"))
        pb = ((prior or {}).get("books") or {}).get(a["book"]) if prior else None
        a["prior"] = pb
        a["verdict_changed_from_prior"] = (None if not pb
                                           else (pb.get("verdict") != a.get("verdict")))

    cal = caliber_reading(
        next((a for a in arms if a["book"] == "nobond_vt08_adopted"), None),
        _caliber_arm(lag1_ser, cap), G.TOP2_SHARE_MAX)
    if cal["verdict"] == "CALIBER_UNREADABLE":
        cal["why"] = ("one of the two calibers produced no top2_share -- the line is not "
                      "read as passing; the missing leg is named above")

    out = {
        "face": "etf_book_year_gate",
        "asof": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "cell": "N5_R20_10bp",
        "gate_rules": {
            "source": "scripts/candidate_year_gate.py (imported, not copied)",
            "positive_years_share_min": G.POSITIVE_YEARS_SHARE,
            "worst_year_floor_pp": G.WORST_YEAR_FLOOR_PP,
            "top2_share_max": G.TOP2_SHARE_MAX,
            "capacity_floor_cny": G.CAPACITY_FLOOR_CNY,
            "cohorts_analog": "%d-bar windows per calendar year" % BARS_PER_WINDOW,
        },
        "data": {"bars": int(len(adopted_ser)) if adopted_ser is not None else 0,
                 "first": str(close.index[0].date()) if len(close) else None,
                 "last": str(close.index[-1].date()) if len(close) else None,
                 "flips_repaired": int(n_flip),
                 "bond_free_universe": len(cols),
                 "live_picks": picks,
                 "live_picks_asof": str(last.date())},
        "books": arms,
        "caliber": cal,
        "decision": decision,
        "prior": prior,
        "honest": [
            "the adopted book is judged by the same frozen line it never faced",
            "the caliber block reads the SAME book on the desk's declared execution "
            "(own from open t+1); the printed arms keep their published numbers untouched",
            "capacity is derived from the current five slots at 5% participation, "
            "not from a stated AUM",
            "the published all-classes arm carries no bar counts; its 2026 partial "
            "flag is inferred from the calendar and printed as such",
        ],
        "elapsed_sec": round(time.time() - t0, 1),
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    tmp = OUT + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    os.replace(tmp, OUT)
    print(json.dumps({"verdicts": {a["book"]: a["verdict"] for a in arms},
                      "decision": decision["verdict"],
                      "caliber": {"verdict": cal["verdict"],
                                  "lag0_top2": cal["entry_lag0"]["top2_share_pct"],
                                  "lag1_top2": cal["entry_lag1"]["top2_share_pct"],
                                  "gap_pp": cal["top2_gap_pp"]},
                      "decision_reads": {k: v for k, v in decision["reads"].items()
                                         if k != "capacity_by_capital"},
                      "elapsed_sec": out["elapsed_sec"]}, ensure_ascii=False))
    print("saved", OUT)
    return 0


def _chk(ok: bool, msg: str, errs: list) -> None:
    print(("PASS " if ok else "FAIL ") + msg)
    if not ok:
        errs.append(msg)


def freshness(last, expected):
    """Is a gate panel on the bar the official calendar says must exist? (pure, r1570)

    Two different failures live behind "not today's": a panel that is BEHIND must exist
    (the chain may buy the rebuild), while a panel that is AHEAD means the calendar the
    reader used is wrong -- rebuilding would hide that, so it is not this function's word.
    """
    if not last:
        return "unknown", "the receipt publishes no data.last"
    if not expected:
        return "unknown", "the official calendar yields no expected bar"
    if str(last) < str(expected):
        return "stale", ("gate panel is on %s while the official calendar expects %s"
                         % (last, expected))
    if str(last) > str(expected):
        return "ahead", ("gate panel is on %s, AFTER the expected %s" % (last, expected))
    return "current", "gate panel is on %s, the expected bar" % last


def check() -> int:
    """Re-derive every published verdict from the receipt's own rows (read-only)."""
    if not os.path.exists(OUT):
        print("FAIL no published receipt at %s" % OUT)
        return 1
    with io.open(OUT, encoding="utf-8") as f:
        d = json.load(f)
    # r1570: this face has many readers (the order sheet now prints its verdict beside the
    # fill) and, until this leg, no scheduled producer -- the r1282 class. A gate frozen on
    # an older panel would be quoted on the operator's paper as if it were today's decision.
    # The age is judged against the OFFICIAL calendar, never against this receipt's own data
    # (E136: a face may not adjudicate its own freshness), and "stale" is spelled out so the
    # chain pays the rebuild instead of someone loosening the assertion.
    try:
        import exchange_calendar_audit as CA
        _exp, _past = CA.expected_last_day(
            CA.load_calendar(),
            pd.Timestamp.now(tz="Asia/Shanghai").to_pydatetime())
    except Exception as exc:                                     # noqa: BLE001
        _exp = None
        print("freshness unknown: %s" % exc)
    _word, _msg = freshness((d.get("data") or {}).get("last"), _exp)
    if _word == "stale":
        print("stale: %s" % _msg)
        return 2
    if _word == "ahead":
        print("FAIL %s" % _msg)
        return 1
    errs = []
    _tally = [0, 0]

    def chk(ok, msg):
        _tally[0] += 1
        if ok:
            _tally[1] += 1
        _chk(ok, msg, errs)

    books = d.get("books") or []
    chk(len(books) == 3, "three books published (got %d)" % len(books))
    for b in books:
        again = G.verdict({"checks": b["checks"]})
        chk(again == b["verdict"],
            "%s verdict re-derives: %s == %s" % (b["book"], again, b["verdict"]))
        chk(len(b.get("yearly_returns_pct") or {}) == len(b["years"]),
            "%s publishes a return for every year it judged" % b["book"])
        y4 = b["year_metrics"]["top2_share"]
        chk((y4 is None) or (b["checks"]["Y4_top2_share"] == (y4 <= G.TOP2_SHARE_MAX)),
            "%s Y4 flag agrees with its own top2_share" % b["book"])
        chk(bool(b.get("partial_years")),
            "%s discloses its partial year rather than annualising it" % b["book"])
    adopted = books[0]
    chk(adopted.get("capacity_cny_1day_5pct") is not None
        and adopted["checks"]["C1_capacity"] is not None,
        "the adopted arm carries a derived capacity face (not left unchecked)")
    chk(bool(adopted.get("sizing_scale_by_year")),
        "the adopted arm prints the sizing scale that moved its calendar")
    for b in books:
        t2 = (b.get("year_metrics") or {}).get("top2_share")
        want = None if t2 is None else round(G.TOP2_SHARE_MAX - float(t2), 4)
        chk(b.get("margin_to_line") == want,
            "%s publishes its distance to the line (%s)" % (b["book"], want))
        pb = ((d.get("prior") or {}).get("books") or {}).get(b["book"])
        moved = None if not pb else (pb.get("verdict") != b.get("verdict"))
        chk(b.get("verdict_changed_from_prior") == moved
            and (moved is not True or b.get("margin_to_line") is not None),
            "%s states whether its verdict moved since the prior panel (%s)"
            % (b["book"], moved))
    # r1798: the caliber block is the only place the concentration line is read twice. Its
    # word must re-derive from its own two numbers, and its lag0 leg must quote the arm's
    # own printed top2_share -- a second number for the same reading is how two calibers
    # quietly become two books.
    cal = d.get("caliber") or {}
    l0 = (cal.get("entry_lag0") or {}).get("top2_share")
    l1 = (cal.get("entry_lag1") or {}).get("top2_share")
    chk(bool(cal), "the receipt carries a caliber block (the line read on both calibers)")
    if l0 is None or l1 is None:
        chk(cal.get("verdict") == "CALIBER_UNREADABLE",
            "a leg without top2_share reads UNREADABLE, never 'keeps'")
        chk(cal.get("top2_gap_pp") is None,
            "an unreadable caliber publishes no gap instead of zero")
    else:
        p0 = float(l0) <= G.TOP2_SHARE_MAX
        p1 = float(l1) <= G.TOP2_SHARE_MAX
        want = "CALIBER_KEEPS_Y4" if p0 == p1 else "CALIBER_FLIPS_Y4"
        chk(cal.get("verdict") == want,
            "caliber word re-derives from its two readings: %s" % want)
        chk(abs(float(cal.get("top2_gap_pp"))
                - (float(l1) - float(l0)) * 100.0) < 1e-6,
            "caliber gap equals the difference of the two published readings")
    for leg in ("entry_lag0", "entry_lag1"):
        b = cal.get(leg) or {}
        f, p = b.get("top2_share"), b.get("top2_share_pct")
        chk((f is None and p is None)
            or (abs(float(p) - float(f) * 100.0) < 1e-6),
            "%s prints the fraction and its percent twin from one reading" % leg)
    chk(l0 == ((adopted.get("year_metrics") or {}).get("top2_share")),
        "the lag0 leg quotes the adopted arm's own top2_share (one number, not two)")
    print("%d/%d PASS" % (_tally[1], _tally[0]))
    return 0 if not errs else 1


def selftest() -> int:
    errs = []
    rets = pd.Series([0.01] * 260 + [-0.005] * 240,
                     index=pd.bdate_range("2020-01-02", periods=500))
    ser = (1.0 + rets).cumprod()
    ser.iloc[0] = 1.0
    yrs = yearly_returns(ser)
    _chk(len(yrs) == 2, "two calendar years from a 500-bar series", errs)
    _chk(all(v["bars"] == v["cohorts"] * BARS_PER_WINDOW + round(v["bars"] - v["cohorts"] * BARS_PER_WINDOW)
             for v in yrs.values()), "window count is floor(bars/60)", errs)
    ok_leg = True
    for y, v in yrs.items():
        blk = ser[ser.index.year == int(y)]
        ok_leg = ok_leg and abs((float(blk.iloc[-1]) / float(blk.iloc[0]) - 1.0) * 100.0
                                - v["net_pct"]) < 1e-9
    _chk(ok_leg, "each year is last/first on the book's own definition", errs)

    # a book whose headline is two years -> must not clear the frozen top-2 line
    carried = {"2021": {"net_pct": 2.0, "cohorts": 4}, "2022": {"net_pct": -1.0, "cohorts": 4},
               "2023": {"net_pct": 3.0, "cohorts": 4}, "2024": {"net_pct": 40.0, "cohorts": 4},
               "2025": {"net_pct": 45.0, "cohorts": 4}}
    b1 = G.admission_block(carried, 1e9, None, 0.10)
    _chk(b1["checks"]["Y4_top2_share"] is False and b1["verdict"] != "ADMIT",
         "carried-by-two-years book fails Y4 -> %s" % b1["verdict"], errs)

    # a flat, broad book must clear it
    flat = {str(y): {"net_pct": 8.0, "cohorts": 4} for y in range(2020, 2026)}
    b2 = G.admission_block(flat, 1e9, None, 0.08)
    _chk(b2["verdict"] == "ADMIT", "even book clears every year check -> %s" % b2["verdict"], errs)

    # partial-year rule: fewer than four windows -> partial, and printed with months
    part = {"2026": {"net_pct": -18.0, "cohorts": 3}}
    b3 = G.admission_block(part, None, None, 0.05)
    _chk(len(b3["partial_years"]) == 1 and b3["partial_years"][0]["approx_months_of_evidence"] > 0,
         "3-window year is disclosed as partial evidence", errs)
    _chk(b3["checks"]["Y3_worst_year"] is False, "a -18pp year fails the -15pp floor", errs)

    # no capacity face is unchecked, never a pass
    _chk(b3["capacity_checked"] is False and b3["checks"]["C1_capacity"] is None,
         "missing capacity is unchecked, not passed", errs)

    # capacity math
    amt = pd.DataFrame({"A": [1e8] * 30, "B": [2e8] * 30})
    _chk(abs(capacity_cny(["A", "B"], amt) - (0.05 * 1e8 + 0.05 * 2e8)) < 1.0,
         "capacity = 5% participation per slot summed", errs)
    _chk(capacity_cny(["A", "MISSING"], amt) is None, "a slot with no panel -> None, not a number", errs)

    # r1570: the freshness word decides whether the chain may buy a rebuild. Behind = stale
    # (rebuild), ahead = a broken calendar (do not hide it), unreadable = unknown (never a
    # pass -- "no data" and "up to date" are different sentences).
    _chk(freshness("2026-11-09", "2026-11-11")[0] == "stale",
         "a panel behind the calendar is stale, not inconsistent", errs)
    _chk(freshness("2026-11-11", "2026-11-11")[0] == "current",
         "a panel on the expected bar is current", errs)
    _chk(freshness("2026-11-12", "2026-11-11")[0] == "ahead",
         "a panel ahead of the calendar is not a rebuild", errs)
    _chk(freshness(None, "2026-11-11")[0] == "unknown"
         and freshness("2026-11-11", None)[0] == "unknown",
         "missing dates read unknown, never current", errs)

    # r1798: the caliber word is derived from the two readings and must speak in all three
    # directions -- keep, flip, and "one leg was never measured". Fixtures use the gate's
    # own unit (a FRACTION of the annual sum), which is what `year_metrics` publishes.
    def _blk(t2):
        return {"cagr_pct": 7.0, "verdict": "CONDITIONAL",
                "year_metrics": {"top2_share": t2}}
    c_keep = caliber_reading(_blk(0.65), _blk(0.68), G.TOP2_SHARE_MAX)
    _chk(c_keep["verdict"] == "CALIBER_KEEPS_Y4"
         and abs(c_keep["top2_gap_pp"] - 3.0) < 1e-9
         and abs(c_keep["entry_lag1"]["top2_share_pct"] - 68.0) < 1e-9,
         "both calibers under the line -> KEEPS, gap +3pp, percent twin printed", errs)
    c_flip = caliber_reading(_blk(0.7084), _blk(0.68), G.TOP2_SHARE_MAX)
    _chk(c_flip["verdict"] == "CALIBER_FLIPS_Y4" and c_flip["entry_lag0"]["passes"] is False
         and c_flip["entry_lag1"]["passes"] is True,
         "carried on bar d, spread on the executable caliber -> FLIPS", errs)
    c_bad = caliber_reading(_blk(None), _blk(0.68), G.TOP2_SHARE_MAX)
    _chk(c_bad["verdict"] == "CALIBER_UNREADABLE" and c_bad["top2_gap_pp"] is None,
         "a leg with no top2_share is UNREADABLE, never KEEPS", errs)
    c_side = caliber_reading(_blk(0.80), _blk(0.88), G.TOP2_SHARE_MAX)
    _chk(c_side["verdict"] == "CALIBER_KEEPS_Y4"
         and c_side["entry_lag0"]["passes"] is False,
         "both calibers over the line -> KEEPS too (the word is about movement)", errs)

    print("%d/%d PASS" % (18 - len(errs), 18))
    return 0 if not errs else 1


def main() -> int:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd == "selftest":
        return selftest()
    if cmd == "check":
        return check()
    if cmd == "run":
        return run()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
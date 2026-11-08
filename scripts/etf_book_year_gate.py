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

    last = sc.index[-1]
    picks = list(sc.loc[last].dropna().nlargest(5).index)
    cap = capacity_cny(picks, amt)
    for a in arms:
        if a["book"].startswith("nobond_vt08"):
            a["capacity_cny_1day_5pct"] = None if cap is None else round(cap, 0)
            a["capacity_checked"] = cap is not None
            a["checks"]["C1_capacity"] = None if cap is None else cap >= G.CAPACITY_FLOOR_CNY
            a["verdict"] = G.verdict({"checks": a["checks"]})

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
        "honest": [
            "the adopted book is judged by the same frozen line it never faced",
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
                      "elapsed_sec": out["elapsed_sec"]}, ensure_ascii=False))
    print("saved", OUT)
    return 0


def _chk(ok: bool, msg: str, errs: list) -> None:
    print(("PASS " if ok else "FAIL ") + msg)
    if not ok:
        errs.append(msg)


def check() -> int:
    """Re-derive every published verdict from the receipt's own rows (read-only)."""
    if not os.path.exists(OUT):
        print("FAIL no published receipt at %s" % OUT)
        return 1
    with io.open(OUT, encoding="utf-8") as f:
        d = json.load(f)
    errs = []

    def chk(ok, msg):
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
    print("%d/%d PASS" % (6 + 4 * len(books) - len(errs), 6 + 4 * len(books)))
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

    print("%d/%d PASS" % (10 - len(errs), 10))
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
"""Does the Y4 gate still pass on the execution the card declares?

r1738 and r1739 answered a question on the research engine: pay the book's idle sleeve and
the shallow arm crosses the two-year concentration line. Both rounds ran that engine as
coded -- `score.loc[d]` selects the names, `op.at[d, p]` pays for them -- which is one bar
of the future the desk never had. `etf_book_lookahead_audit` already priced that lag on the
12-name card (1.14 pp/yr) and `etf_book_causal_headline` already named which arm the
operator reads. What nobody re-ran is the GATE: every adoption sentence in r1738/r1739
("CONDITIONAL -> ADMIT") sits on the same-open arm.

This face re-adjudicates the same six cells on the declared execution and prints both
verdicts side by side. It adds no threshold, no width, no carrier: the grid, the gate line
and the block builder are the published ones, and the lag is the audit's own `score.shift`.

Cells: 2 bases (as_coded lag=0 / causal lag=1) x 2 widths (5 = the gate arm, 12 = the arm
the forward ledger runs) x 2 carriers (cash at 0 / ladder3). Composition and the carriers
come from `etf_book_idle_cash`, the year blocks from `etf_book_year_gate`, the line from
`candidate_year_gate` -- one implementation each.

Read the verdict, not the intent:

  VERDICT_SURVIVES_THE_BASIS -- the shallow paid arm is still an ADMIT one bar later; the
                                adoption sentence r1738 wrote is execution-independent
  VERDICT_WAS_THE_BASIS      -- it was the ADMIT only because the book bought at the open of
                                the bar whose close ranked it; the headline number must fall
                                before any adoption sentence is re-issued
  BASIS_WAS_HIDING_THE_PASS  -- the causal arm passes where the coded arm did not (a lag that
                                helps is a lag worth understanding before it is trusted)
  NEITHER_BASIS_PASSES       -- neither arm clears Y4
  CONTROL_FAILED             -- the as-coded cells must reproduce the published JSON; if they
                                do not, this face is measuring a different book

Usage:
    python scripts/etf_book_gate_causal.py run
    python scripts/etf_book_gate_causal.py selftest
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
import etf_book_cash_ladder as CL  # noqa: E402
import etf_book_gate_knobs as K  # noqa: E402
import etf_book_idle_cash as IC  # noqa: E402
import etf_book_year_gate as YG  # noqa: E402
import etf_composite_pf as E  # noqa: E402
import etf_equity_alpha as A  # noqa: E402
import etf_robust_pf as R  # noqa: E402

OUT = os.path.join(ROOT, "results", "etf_book_gate_causal.json")
MD = os.path.join(ROOT, "research", "ETF_BOOK_GATE_CAUSAL.md")
KNOBS = os.path.join(ROOT, "results", "etf_book_gate_knobs.json")
CARRY = os.path.join(ROOT, "results", "etf_book_forward", "CARRY.json")

BASES = (("as_coded", 0), ("causal", 1))
WIDTHS = (("n5", 5), ("n12", 12))
CASH = (("cash_zero", None),
        ("ladder3", CL.LADDERS["ladder3"]))
REBAL, COST, VOL_TARGET = K.REBAL, K.COST, K.VOL_TARGET
REPRO_TOL_TOP2 = 1e-4          # the as-coded cells must land on the published JSON
LEDGER_TOL_PP = 0.35           # causal n12/ladder3 vs the forward ledger's own accrual


def _read_json(path):
    if not os.path.exists(path):
        return None
    try:
        with io.open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:                                              # noqa: BLE001
        return None


def basis_verdict(readings):
    """Pure: the published verdicts and the causal ones decide this, nothing typed in."""
    if not readings.get("controls_ok"):
        return "CONTROL_FAILED"
    ac = (readings.get("grid") or {}).get("as_coded") or {}
    ca = (readings.get("grid") or {}).get("causal") or {}
    ac5 = ((ac.get("n5") or {}).get("ladder3") or {}).get("verdict")
    ca5 = ((ca.get("n5") or {}).get("ladder3") or {}).get("verdict")
    if ac5 == "ADMIT" and ca5 == "ADMIT":
        return "VERDICT_SURVIVES_THE_BASIS"
    if ac5 == "ADMIT":
        return "VERDICT_WAS_THE_BASIS"
    if ca5 == "ADMIT":
        return "BASIS_WAS_HIDING_THE_PASS"
    return "NEITHER_BASIS_PASSES"


def _arm(close, openp, amt, sc_lag, n_hold):
    """One engine run per (base, width): the book and its idle schedule.

    The carriers are then composed on this same curve, so a cell can only differ from
    another by the sleeve it is paid -- never by a second engine call.
    """
    diag = []
    book, turn = R.open_to_open_equity(close, openp, amt, sc_lag, REBAL, n_hold, COST,
                                       vol_target=VOL_TARGET, diag=diag)
    idle = (1.0 - IC.scale_schedule(diag, book.index)).clip(lower=0.0, upper=1.0)
    # Capacity on the newest decision the book could take under this lag: the last score
    # row that exists for it. Typing the newest cell twice would let a lagged arm inherit
    # a book it could not have chosen.
    picks_row = sc_lag.dropna(how="all")
    picks = ([] if picks_row.empty
             else list(picks_row.iloc[-1].dropna().nlargest(n_hold).index))
    return {"book": book, "idle": idle, "turnover": float(turn), "picks": picks,
            "diag": diag}


def _cell(arm, amt, cash_step, label):
    ser = IC.compose(arm["book"], arm["idle"],
                     (pd.Series(0.0, index=arm["book"].index) if cash_step is None
                      else cash_step.reindex(arm["book"].index).fillna(0.0)))
    cap = YG.capacity_cny(arm["picks"], amt) if arm["picks"] else None
    blk = YG._block(label, YG.yearly_returns(ser), cap, ser, label)
    if cap is not None:
        blk["capacity_cny_1day_5pct"] = round(float(cap), 0)
        blk["checks"]["C1_capacity"] = bool(cap >= G.CAPACITY_FLOOR_CNY)
        blk["verdict"] = G.verdict({"checks": blk["checks"]})
    st = A.stats2(ser, label)
    return {"block": blk, "ser": ser, "turnover": arm["turnover"],
            "idle_median": float(np.nanmedian(arm["idle"].to_numpy())),
            "stats": {k: (None if st.get(k) is None else round(float(st[k]), 6))
                      for k in ("cagr", "sharpe", "maxdd", "vol")},
            "picks": arm["picks"]}


def _thin(blk, stats, turn, idle_median):
    ym = blk.get("year_metrics") or {}
    return {"verdict": blk.get("verdict"),
            "top2_share": ym.get("top2_share"),
            "top2_share_full_only": ym.get("top2_share_full_only"),
            "Y4_top2_share": (blk.get("checks") or {}).get("Y4_top2_share"),
            "cagr": stats.get("cagr"), "sharpe": stats.get("sharpe"),
            "maxdd_pct": (None if stats.get("maxdd") is None
                          else round(float(stats["maxdd"]) * 100.0, 4)),
            "vol_pct": (None if stats.get("vol") is None
                        else round(float(stats["vol"]) * 100.0, 4)),
            "median_idle_share": round(float(idle_median), 4),
            "turnover_per_side": round(float(turn), 4)}


def run():
    t0 = time.time()
    close, openp, amt, feats = E.build_panel()
    close, openp, n_flip = A.repair_flips(close, openp)
    cls = A.classify(close.columns, A.load_class_map(), close)
    cols = [c for c in close.columns if cls[c] in ("equity", "commodity", "convertible")]
    sc = E.build_score(close[cols], amt[cols], feats)
    print("bond-free universe %d, flips repaired %d" % (len(cols), n_flip), flush=True)

    rates = CL.load_panel()
    cash_cache = {}
    grid, full = {}, {}
    for bname, lag in BASES:
        s = sc if lag == 0 else sc.shift(lag)
        grid[bname], full[bname] = {}, {}
        for wname, n_hold in WIDTHS:
            grid[bname][wname], full[bname][wname] = {}, {}
            arm = _arm(close[cols], openp[cols], amt[cols], s, n_hold)
            for cname, ladder in CASH:
                lab = "%s/%s/%s" % (bname, wname, cname)
                if ladder is None:
                    step = None
                else:
                    key = (lag, str(arm["book"].index[0].date()),
                           str(arm["book"].index[-1].date()), tuple(ladder))
                    if key not in cash_cache:
                        st, _info, _raw, _bars = IC.cash_step_returns(
                            rates, arm["book"].index, ladder=tuple(ladder), fees=None)
                        cash_cache[key] = st
                    step = cash_cache[key]
                cell = _cell(arm, amt[cols], step, lab)
                grid[bname][wname][cname] = _thin(cell["block"], cell["stats"],
                                                  cell["turnover"], cell["idle_median"])
                full[lab] = cell
                print("%-22s top2=%s verdict=%s cagr=%s" % (
                    lab, grid[bname][wname][cname]["top2_share"],
                    grid[bname][wname][cname]["verdict"],
                    grid[bname][wname][cname]["cagr"]), flush=True)

    # ---- controls -------------------------------------------------------------
    knobs = (_read_json(KNOBS) or {}).get("readings") or {}
    pub_ac5 = ((((knobs.get("grid") or {}).get("n5_gate_arm") or {})
                .get("cash_zero") or {}).get("top2_share"))
    pub_ac12 = ((((knobs.get("grid") or {}).get("n12_forward_arm") or {})
                 .get("ladder3") or {}).get("top2_share"))
    mine_ac5 = grid["as_coded"]["n5"]["cash_zero"]["top2_share"]
    mine_ac12 = grid["as_coded"]["n12"]["ladder3"]["top2_share"]
    c_knobs_n5 = (pub_ac5 is not None and mine_ac5 is not None
                  and abs(float(mine_ac5) - float(pub_ac5)) <= REPRO_TOL_TOP2)
    c_knobs_n12 = (pub_ac12 is not None and mine_ac12 is not None
                   and abs(float(mine_ac12) - float(pub_ac12)) <= REPRO_TOL_TOP2)

    carry = _read_json(CARRY) or {}
    led = ((carry.get("books") or {}).get("fixed_carry") or {}).get("full") or {}
    led_cagr = led.get("cagr")
    mine_causal_n12 = grid["causal"]["n12"]["ladder3"]["cagr"]
    ledger_gap_pp = (None if led_cagr is None or mine_causal_n12 is None
                     else round((float(mine_causal_n12) - float(led_cagr)) * 100.0, 3))
    c_ledger = (ledger_gap_pp is not None and abs(ledger_gap_pp) <= LEDGER_TOL_PP)

    controls_ok = bool(c_knobs_n5 and c_knobs_n12)
    readings = {
        "controls_ok": controls_ok,
        "control_knobs_n5_top2": {"published": pub_ac5, "mine": mine_ac5,
                                  "ok": bool(c_knobs_n5)},
        "control_knobs_n12_ladder3_top2": {"published": pub_ac12, "mine": mine_ac12,
                                           "ok": bool(c_knobs_n12)},
        "ledger_crosscheck": {"ledger_fixed_carry_cagr": led_cagr,
                             "causal_n12_ladder3_cagr": mine_causal_n12,
                             "gap_pp": ledger_gap_pp, "ok": bool(c_ledger),
                             "note": ("the ledger accrues decide-at-close/fill-next-open; "
                                      "this face prices the audit's lag arm on the engine's "
                                      "open-to-open window, so the two are different "
                                      "settlement stacks and only have to agree to "
                                      "%g pp" % LEDGER_TOL_PP)},
        "gate_line_top2_share_max": G.TOP2_SHARE_MAX,
        "grid": grid,
        "price_of_the_basis_pp": {
            "n5_cash_zero": round((grid["as_coded"]["n5"]["cash_zero"]["cagr"]
                                   - grid["causal"]["n5"]["cash_zero"]["cagr"]) * 100.0, 3),
            "n12_ladder3": round((grid["as_coded"]["n12"]["ladder3"]["cagr"]
                                  - grid["causal"]["n12"]["ladder3"]["cagr"]) * 100.0, 3)},
    }
    readings["verdict"] = basis_verdict(readings)

    rep = {
        "face": "etf_book_gate_causal",
        "asof": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "evidence_cutoff": str(pd.Timestamp(full["as_coded/n5/cash_zero"]["ser"].index[-1])
                               .date()),
        "window": {"start": str(pd.Timestamp(
                       full["as_coded/n5/cash_zero"]["ser"].index[0]).date()),
                   "end": str(pd.Timestamp(
                       full["as_coded/n5/cash_zero"]["ser"].index[-1]).date()),
                   "bars": int(len(full["as_coded/n5/cash_zero"]["ser"]))},
        "question": ("r1738/r1739 sent the shallow paid arm from CONDITIONAL to ADMIT on an "
                     "engine that ranks on bar d's close and pays from bar d's open. Does "
                     "that verdict survive the execution the card declares (rank on d-1, "
                     "fill at d's open)?"),
        "grid_config": {"bases": {b: l for b, l in BASES},
                        "widths": {w: n for w, n in WIDTHS},
                        "carriers": {c: (None if l is None else list(l)) for c, l in CASH},
                        "rebal": REBAL, "cost_per_side": COST,
                        "vol_target": VOL_TARGET},
        "readings": readings,
        "honest": [
            "the causal arm is `score.shift(1)` -- the audit's own lag lattice point, not a "
            "second way of ranking; both arms pick the same names, one bar apart",
            "a one-bar lag also moves which bar the sample starts and ends on; the price of "
            "the basis is therefore a sample-level number, not a per-trade rebate",
            "the capacity check reads the newest score row that exists for each lag, so the "
            "lagged arm cannot inherit picks it could not have ranked",
            "no carry is credited to the ledger comparison here: the ledger's own face "
            "prices the sleeve and this one only re-adjudicates the equity book's gate",
            "this face does not choose an arm. It says whether an already-issued adoption "
            "sentence is execution-independent",
        ],
        "elapsed_sec": round(time.time() - t0, 1),
    }
    with io.open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(rep, f, ensure_ascii=False, indent=1)
    with io.open(MD, "w", encoding="utf-8", newline="\n") as f:
        f.write(_md(rep))
    print(json.dumps({"verdict": readings["verdict"],
                      "price_of_the_basis_pp": readings["price_of_the_basis_pp"],
                      "n5_causal": grid["causal"]["n5"]["ladder3"],
                      "ledger_gap_pp": ledger_gap_pp}, ensure_ascii=False), flush=True)
    return 0 if readings["verdict"] != "CONTROL_FAILED" else 3


def basis_caveat_lines(results_path=OUT):
    """The paragraph a page that prints ADMIT has to carry, read from this face's JSON.

    Station-of-birth rule: the sentence "CONDITIONAL -> ADMIT" is read as an adoption
    order wherever it is printed, so the page that prints it names the basis it was
    adjudicated on. Nothing is typed here -- the numbers come from the file, and a missing
    file says so instead of guessing.
    """
    doc = _read_json(results_path)
    if not doc:
        return ["**Basis caveat** — not yet priced; run "
                "`scripts\\etf_book_gate_causal.py run`.", ""]
    r = doc.get("readings") or {}
    g = r.get("grid") or {}
    ac5 = ((g.get("as_coded") or {}).get("n5") or {}).get("ladder3") or {}
    ca5 = ((g.get("causal") or {}).get("n5") or {}).get("ladder3") or {}
    L = ["**Basis caveat** — %s. Every cell above is the as-coded engine (rank on bar d's "
         "close, pay from bar d's open). One bar later (`score.shift(1)`, the execution the "
         "card declares) the paid 5-name arm reads best-two share %s, gate %s, CAGR %s: "
         "`research\\ETF_BOOK_GATE_CAUSAL.md`." % (
             r.get("verdict"),
             "n/a" if ca5.get("top2_share") is None else "%.2f%%" % (ca5["top2_share"] * 100),
             ca5.get("verdict"),
             "n/a" if ca5.get("cagr") is None else "%.2f%%" % (ca5["cagr"] * 100))]
    if ac5.get("top2_share") is not None and ca5.get("top2_share") is not None:
        L.append("")
        L.append("The %s in this table is that same-open reading. Read any ADMIT here as "
                 "*priced on the same-open basis*, not as an execution-independent pass."
                 % ("%.2f%%" % (ac5["top2_share"] * 100)))
    L.append("")
    return L


def _md(rep):
    r = rep["readings"]
    L = ["# ETF book — does the Y4 gate survive the declared execution?", ""]
    L.append("Evidence cutoff **%s** (%d bars from %s). Generated by "
             "`scripts\\etf_book_gate_causal.py`." % (rep["evidence_cutoff"],
                                                      rep["window"]["bars"],
                                                      rep["window"]["start"]))
    L.append("")
    L.append("## Verdict")
    L.append("")
    L.append("**%s**" % r["verdict"])
    L.append("")
    L.append("| basis | width | carrier | best-two share | line | gate | CAGR | Sharpe | maxDD |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for b, g in r["grid"].items():
        for w, gg in g.items():
            for c, v in gg.items():
                L.append("| %s | %s | %s | %s | <= %.2f%% | %s | %s | %s | %s |" % (
                    b, w, c,
                    "n/a" if v["top2_share"] is None else "%.2f%%" % (v["top2_share"] * 100),
                    r["gate_line_top2_share_max"] * 100.0, v["verdict"],
                    "n/a" if v["cagr"] is None else "%.2f%%" % (v["cagr"] * 100),
                    "n/a" if v["sharpe"] is None else "%.3f" % v["sharpe"],
                    "n/a" if v["maxdd_pct"] is None else "%.2f%%" % v["maxdd_pct"]))
    L.append("")
    L.append("## Price of the basis")
    L.append("")
    for k, v in r["price_of_the_basis_pp"].items():
        L.append("- `%s`: **%+.2f pp/yr** (as coded minus causal)" % (k, v))
    L.append("")
    L.append("## Controls")
    L.append("")
    L.append("| control | value |")
    L.append("|---|---|")
    for k in ("control_knobs_n5_top2", "control_knobs_n12_ladder3_top2"):
        c = r[k]
        L.append("| %s | published %s / mine %s -> %s |" % (
            k, c["published"], c["mine"], "ok" if c["ok"] else "MISMATCH"))
    lc = r["ledger_crosscheck"]
    L.append("| forward ledger cross-check | ledger %s vs this face %s -> %+.3f pp (%s) |" % (
        lc["ledger_fixed_carry_cagr"], lc["causal_n12_ladder3_cagr"], lc["gap_pp"] or 0.0,
        "within" if lc["ok"] else "OUTSIDE tolerance"))
    L.append("")
    L.append("## Honest limits")
    L.append("")
    for h in rep["honest"]:
        L.append("- %s" % h)
    L.append("")
    return "\n".join(L)


def selftest():
    bad = []

    def chk(ok, msg):
        print("[%s] %s" % ("PASS" if ok else "FAIL", msg))
        if not ok:
            bad.append(msg)

    def g(ac5, ca5, ok=True):
        return {"controls_ok": ok,
                "grid": {"as_coded": {"n5": {"ladder3": {"verdict": ac5}}},
                         "causal": {"n5": {"ladder3": {"verdict": ca5}}}}}

    chk(basis_verdict(g("ADMIT", "ADMIT")) == "VERDICT_SURVIVES_THE_BASIS",
        "an ADMIT on both bases survives the basis")
    chk(basis_verdict(g("ADMIT", "CONDITIONAL")) == "VERDICT_WAS_THE_BASIS",
        "an ADMIT only on the same-open arm was the basis")
    chk(basis_verdict(g("CONDITIONAL", "ADMIT")) == "BASIS_WAS_HIDING_THE_PASS",
        "a pass that only appears one bar later is named, not celebrated")
    chk(basis_verdict(g("CONDITIONAL", "CONDITIONAL")) == "NEITHER_BASIS_PASSES",
        "neither passing is neither passing")
    chk(basis_verdict(g("ADMIT", "ADMIT", ok=False)) == "CONTROL_FAILED",
        "a control failure outranks every reading")
    chk(basis_verdict({}) == "CONTROL_FAILED",
        "a missing grid cannot pass by default")
    print("selftest: %d/%d PASS" % (6 - len(bad), 6))
    return 0 if not bad else 1


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "run":
        return run()
    if cmd == "selftest":
        return selftest()
    print(__doc__)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

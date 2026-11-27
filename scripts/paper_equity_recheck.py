"""Paper book equity recheck: the ledger's own arithmetic, its marks against the
daily panel, and every reader face against the ledger.

Why this face exists: four reader faces (results/paper_export, strategy_scorecard,
daily_scorecard and the CEO live page) all copy the same `capital` block, so they
agree with each other even when the block itself is wrong -- agreement between
copies is not evidence about the book. This face recomputes from the raw position
fields (`quantity x last_close`, `(last_close - cost_price) x quantity`) and
anchors every mark on `data/daily`, so a stale or mis-scaled price cannot hide
behind four faces that agree.

Readings (per trader):
  L1  sum(quantity x last_close) == capital.positions_value_cny
  L2  sum(market_value_cny)      == capital.positions_value_cny
  L3  sum(unrealized_pnl_cny)    == sum((last_close - cost_price) x quantity)
  L4  cash_cny + positions_value_cny == equity_cny
  L5  every last_close           == the daily panel's latest close for that code
  L6  every position mark's bar  is not newer than the ledger's own cutoff

Reader reconciliation:
  R1  results/paper_export equity/positions_value == the ledger
  R2  export summary.total_equity_cny == sum of its own per-trader equity
  R3  strategy_scorecard trader_cards[*].live_paper.capital.equity_cny == the ledger
      -- unless the scorecard was generated before the ledger bar's close (15:30):
      then the copy cannot carry that bar, and it is accepted only if it reproduces
      the PREVIOUS bar (else it matches neither bar, and that is still a breach).

Subcommands:
  run       -> results/paper_equity_recheck.json + one-line verdict
  selftest  offline fixtures (no live data, no network)

exit 0 = every identity holds / 1 = at least one breach / 2 = a face cannot be read
"""
from __future__ import annotations

import datetime as _dt
import glob
import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Money identities are stated to the cent, so a cent's worth of rounding per
# position is the widest a difference may be and still be the same number.
AMOUNT_TOL = 0.02
PRICE_REL_TOL = 1e-4
PRICE_ABS_TOL = 1e-6

# The repo's own completeness convention: a bar dated D is only complete (hence
# only copyable by a reader face) after 15:30 on D. A scorecard written before
# that moment cannot carry D's marks, so one bar's move is not a breach (R3).
BAR_CLOSE_HOUR = 15
BAR_CLOSE_MINUTE = 30

# How close a stale copy must sit to the *previous* bar's marks to be accepted as
# "one bar behind". A bar's move is 1e-3..1e-2 of equity, so 1e-4 separates "same
# bar" from "a different number" without pretending to explain the residual.
STALE_COPY_REL_TOL = 1e-4


def _tol(value: float) -> float:
    return AMOUNT_TOL + 1e-9 * abs(value)


def _load(path: str):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def panel_closes(root: str, code: str) -> dict:
    """Latest bar per file family for one code.

    Two families live in data/daily (bare `510300.csv` and `sh510300.csv`);
    they are separate writers and may disagree, so both are returned and the
    caller decides -- picking the newer one silently would hide a split panel.
    """
    out = {}
    for name in (f"{code}.csv", f"sh{code}.csv", f"sz{code}.csv"):
        path = os.path.join(root, "data", "daily", name)
        if not os.path.exists(path):
            continue
        last = None
        with open(path, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.lower().startswith("date"):
                    continue
                last = line
        if not last:
            continue
        parts = last.split(",")
        if len(parts) < 5:
            continue
        try:
            out[name] = {"date": parts[0], "close": float(parts[4])}
        except ValueError:
            continue
    return out


def resolve_mark(panel: dict):
    """(date, close, source, conflict) for one code's mark, or (None, None, None, why)."""
    if not panel:
        return None, None, None, "no panel file"
    dates = {v["date"] for v in panel.values()}
    closes = {round(v["close"], 4) for v in panel.values()}
    if len(dates) == 1 and len(closes) > 1:
        return None, None, None, "two families, same bar, different close"
    newest = max(panel.items(), key=lambda kv: kv[1]["date"])
    return newest[1]["date"], newest[1]["close"], newest[0], None


def _parse_iso(value):
    """datetime for an ISO-ish stamp, or None. Tolerates a trailing timezone/offset."""
    if not isinstance(value, str) or len(value) < 10:
        return None
    text = value.strip().replace("Z", "").replace("T", " ")
    text = text.split("+")[0].strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return _dt.datetime.strptime(text[:19], fmt)
        except ValueError:
            continue
    return None


def bar_copyable(generated, cutoff):
    """True/False/None: could a face written at `generated` have copied the bar `cutoff`?

    None means the question cannot be asked (a stamp or a cutoff is missing), and the
    caller keeps the strict reading rather than inventing staleness.
    """
    gen = _parse_iso(generated)
    cut = _parse_iso(cutoff)
    if gen is None or cut is None:
        return None
    return gen >= cut.replace(hour=BAR_CLOSE_HOUR, minute=BAR_CLOSE_MINUTE)


def prior_bar_close(root: str, code: str):
    """Close of the bar before the one that priced the ledger's mark, or None.

    The family is the one whose newest bar is the latest (the same family
    resolve_mark() would price today), so the prior row is that family's own
    previous bar -- mixing families would compare two different series.
    """
    tails = {}
    for name in (f"{code}.csv", f"sh{code}.csv", f"sz{code}.csv"):
        path = os.path.join(root, "data", "daily", name)
        if not os.path.exists(path):
            continue
        tail = []
        with open(path, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.lower().startswith("date"):
                    continue
                parts = line.split(",")
                if len(parts) < 5:
                    continue
                tail.append(parts)
                tail = tail[-2:]
        if tail:
            tails[name] = tail
    if not tails:
        return None
    _, tail = max(tails.items(), key=lambda kv: kv[1][-1][0])
    if len(tail) < 2:
        return None
    try:
        return float(tail[0][4])
    except ValueError:
        return None


def prior_bar_equity(root: str, book: dict):
    """Equity rebuilt from the previous bar's closes and the ledger's own cash, or None."""
    try:
        cash = float((book.get("capital") or {})["cash_cny"])
    except (KeyError, TypeError, ValueError):
        return None
    total = 0.0
    for row in book.get("open_positions") or []:
        close = prior_bar_close(root, str(row.get("symbol")))
        if close is None:
            return None
        total += float(row.get("quantity") or 0.0) * close
    return total + cash


def check_trader(root: str, ledger: dict) -> dict:
    tid = ledger.get("trader")
    cap = ledger.get("capital") or {}
    pos = ledger.get("open_positions") or []
    cutoff = ledger.get("cutoff")

    res = {
        "trader": tid,
        "cutoff": cutoff,
        "n_positions": len(pos),
        "equity_cny": cap.get("equity_cny"),
        "problems": [],
        "price_lags": [],
        "prices_unverified": [],
    }
    if not cap:
        res["problems"].append("L0 capital block missing")
        return res

    try:
        pv = float(cap.get("positions_value_cny") or 0.0)
        cash = float(cap.get("cash_cny") or 0.0)
        equity = float(cap.get("equity_cny") or 0.0)
    except (TypeError, ValueError):
        res["problems"].append("L0 capital fields are not numeric")
        return res

    mv_recalc = 0.0
    mv_field = 0.0
    pnl_recalc = 0.0
    pnl_field = 0.0
    for p in pos:
        try:
            qty = float(p["quantity"])
            close = float(p["last_close"])
            cost = float(p["cost_price"])
        except (KeyError, TypeError, ValueError):
            res["problems"].append(f"L0 position row unreadable: {p.get('symbol')}")
            continue
        mv_recalc += qty * close
        mv_field += float(p.get("market_value_cny") or qty * close)
        pnl_recalc += (close - cost) * qty
        pnl_field += float(p.get("unrealized_pnl_cny") or 0.0)

        panel = panel_closes(root, str(p["symbol"]))
        bar, panel_close, source, why = resolve_mark(panel)
        row = {"symbol": str(p["symbol"]), "last_close": close,
               "panel_close": panel_close, "panel_bar": bar, "panel_source": source}
        if why:
            res["prices_unverified"].append(dict(row, why=why))
        else:
            if abs(panel_close - close) > max(PRICE_ABS_TOL, PRICE_REL_TOL * abs(panel_close)):
                res["problems"].append(
                    "L5 mark %s: ledger %.4f vs panel %s %.4f (%s)"
                    % (row["symbol"], close, source, panel_close, bar))
            if cutoff and bar > cutoff:
                # The mark is newer than the ledger's own cutoff: the ledger is
                # pricing a bar it did not claim to have seen.
                res["problems"].append(
                    "L6 mark %s priced on %s beyond cutoff %s" % (row["symbol"], bar, cutoff))
            elif cutoff and bar < cutoff:
                res["price_lags"].append({"symbol": row["symbol"], "panel_bar": bar,
                                          "cutoff": cutoff})

    res["positions_value_recalc"] = round(mv_recalc, 2)
    res["positions_value_field"] = round(mv_field, 2)
    res["unrealized_recalc"] = round(pnl_recalc, 2)
    res["unrealized_field"] = round(pnl_field, 2)

    if abs(mv_recalc - pv) > _tol(pv):
        res["problems"].append(
            "L1 positions_value: recalc %.2f vs ledger %.2f (d %+.2f)"
            % (mv_recalc, pv, mv_recalc - pv))
    if abs(mv_field - pv) > _tol(pv):
        res["problems"].append(
            "L2 market_value fields: %.2f vs positions_value %.2f (d %+.2f)"
            % (mv_field, pv, mv_field - pv))
    if abs(pnl_recalc - pnl_field) > _tol(pnl_field):
        res["problems"].append(
            "L3 unrealized: recalc %.2f vs fields %.2f (d %+.2f)"
            % (pnl_recalc, pnl_field, pnl_recalc - pnl_field))
    if abs(cash + pv - equity) > _tol(equity):
        res["problems"].append(
            "L4 cash+pv: %.2f vs equity %.2f (d %+.2f)"
            % (cash + pv, equity, cash + pv - equity))
    return res


def check_readers(root: str, books: dict) -> tuple[dict, list]:
    readers = {}
    problems = []

    export_path = os.path.join(root, "results", "paper_export", "latest.json")
    if os.path.exists(export_path):
        exp = _load(export_path)
        per = {}
        total = 0.0
        for row in exp.get("traders") or []:
            tid = row.get("trader")
            cap = row.get("capital_cny") or {}
            try:
                equity = float(cap.get("equity"))
                pv = float(cap.get("positions_value"))
            except (TypeError, ValueError):
                problems.append(f"R0 export row unreadable: {tid}")
                continue
            per[tid] = {"equity": equity, "positions_value": pv,
                        "export_date": exp.get("export_date")}
            total += equity
            book = books.get(tid)
            if not book:
                problems.append(f"R1 export names {tid} with no ledger face")
                continue
            bcap = book.get("capital") or {}
            try:
                b_eq = float(bcap.get("equity_cny"))
                b_pv = float(bcap.get("positions_value_cny"))
            except (TypeError, ValueError):
                problems.append(f"R1 ledger capital unreadable: {tid}")
                continue
            if abs(equity - b_eq) > _tol(b_eq):
                problems.append(
                    "R1 %s equity: export %.2f vs ledger %.2f (d %+.2f)"
                    % (tid, equity, b_eq, equity - b_eq))
            if abs(pv - b_pv) > _tol(b_pv):
                problems.append(
                    "R1 %s positions_value: export %.2f vs ledger %.2f (d %+.2f)"
                    % (tid, pv, b_pv, pv - b_pv))
        summ = exp.get("summary") or {}
        try:
            stated = float(summ.get("total_equity_cny"))
        except (TypeError, ValueError):
            stated = None
        if stated is None:
            problems.append("R2 export summary.total_equity_cny missing")
        elif abs(total - stated) > _tol(stated):
            problems.append(
                "R2 export total: rows sum %.2f vs summary %.2f (d %+.2f)"
                % (total, stated, total - stated))
        readers["paper_export"] = {"n_traders": len(per), "per_trader": per,
                                   "rows_sum": round(total, 2), "summary": stated}
    else:
        problems.append("R0 results/paper_export/latest.json missing")

    sc_path = os.path.join(root, "results", "strategy_scorecard.json")
    if os.path.exists(sc_path):
        sc = _load(sc_path)
        cards = sc.get("trader_cards") or {}
        seen = 0
        stale_rows = []
        fresh_mismatch = 0
        for tid, card in cards.items():
            book = books.get(tid)
            if not book:
                continue
            try:
                stated = float(((card.get("live_paper") or {}).get("capital") or {})
                               .get("equity_cny"))
                actual = float((book.get("capital") or {}).get("equity_cny"))
            except (TypeError, ValueError):
                problems.append(f"R3 scorecard capital unreadable: {tid}")
                continue
            seen += 1
            if abs(stated - actual) <= _tol(actual):
                continue
            # A copy written before this bar's close cannot carry it. Ask the cheap
            # question first: is the copy simply yesterday's marks?
            if bar_copyable(sc.get("generated"), book.get("cutoff")) is False:
                prev_eq = prior_bar_equity(root, book)
                if prev_eq is not None:
                    rel = abs(stated - prev_eq) / max(1.0, abs(prev_eq))
                    row = {"trader": tid, "scorecard_cny": round(stated, 2),
                           "ledger_cny": round(actual, 2),
                           "delta_vs_ledger_cny": round(stated - actual, 2),
                           "prior_bar_equity_cny": round(prev_eq, 2),
                           "delta_vs_prior_bar_cny": round(stated - prev_eq, 2),
                           "rel_vs_prior_bar": round(rel, 10),
                           "scorecard_generated": sc.get("generated"),
                           "ledger_cutoff": book.get("cutoff")}
                    if rel <= STALE_COPY_REL_TOL:
                        row["state"] = "STALE_BY_GENERATION"
                        stale_rows.append(row)
                        continue
                    problems.append(
                        "R3 %s is older than the bar (%s < cutoff %s %02d:%02d) but does "
                        "not reproduce the prior bar either: %.2f vs %.2f (rel %.2e)"
                        % (tid, sc.get("generated"), book.get("cutoff"), BAR_CLOSE_HOUR,
                           BAR_CLOSE_MINUTE, stated, prev_eq, rel))
                    continue
            fresh_mismatch += 1
            problems.append(
                "R3 %s scorecard equity: %.2f vs ledger %.2f (d %+.2f)"
                % (tid, stated, actual, stated - actual))
        latest = max((b.get("cutoff") or "" for b in books.values()), default="")
        readers["strategy_scorecard"] = {
            "n_cards_checked": seen,
            "generated": sc.get("generated"),
            "latest_cutoff": latest,
            "bar_close_local": "%02d:%02d" % (BAR_CLOSE_HOUR, BAR_CLOSE_MINUTE),
            "state": ("STALE_BY_GENERATION" if stale_rows and not fresh_mismatch
                      else "BREACH" if fresh_mismatch else "AGREES"),
            "n_stale": len(stale_rows),
            "stale": stale_rows,
        }
    else:
        problems.append("R0 results/strategy_scorecard.json missing")

    return readers, problems


def run(root: str = ROOT) -> dict:
    books = {}
    per_trader = []
    problems = []
    for path in sorted(glob.glob(os.path.join(root, "results", "paper", "*_paper.json"))):
        try:
            ledger = _load(path)
        except Exception as exc:  # noqa: BLE001 - a face that cannot be read is a finding
            problems.append(f"L0 {os.path.basename(path)} unreadable: {exc}")
            continue
        tid = ledger.get("trader") or os.path.basename(path).split("_paper")[0]
        books[tid] = ledger
        per_trader.append(check_trader(root, ledger))

    if not books:
        return {"verdict": "NO_LEDGERS", "problems": problems or ["no results/paper/*_paper.json"],
                "traders": [], "readers": {}}

    readers, rproblems = check_readers(root, books)
    for row in per_trader:
        problems.extend(f"{row['trader']}: {p}" for p in row["problems"])
    problems.extend(rproblems)

    total_equity = 0.0
    for row in per_trader:
        if row.get("equity_cny"):
            total_equity += float(row["equity_cny"])

    lags = [{"trader": r["trader"], **m} for r in per_trader for m in r["price_lags"]]
    unverified = [{"trader": r["trader"], **m} for r in per_trader for m in r["prices_unverified"]]

    out = {
        "face": "paper_equity_recheck",
        "why": ("four reader faces copy one capital block; this face recomputes from the "
                "raw position fields and anchors every mark on data/daily"),
        "evidence_cutoff": max((b.get("cutoff") or "" for b in books.values()), default=None),
        "n_traders": len(per_trader),
        "total_equity_cny": round(total_equity, 2),
        "identities": ["L1 positions_value", "L2 market_value fields", "L3 unrealized",
                       "L4 cash+positions", "L5 mark vs panel", "L6 mark within cutoff",
                       "R1 export vs ledger", "R2 export total", "R3 scorecard vs ledger"],
        "traders": per_trader,
        "readers": readers,
        "price_lags": lags,
        "prices_unverified": unverified,
        "problems": problems,
        "verdict": "PASS" if not problems else "BREACH",
        "zeros": {"engine_runs": 0, "ledger_trials_added": 0, "network": "zero"},
    }
    return out


def main(argv: list) -> int:
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd in ("selftest", "--selftest", "-t"):
        return selftest()
    if cmd not in ("run", "--check", "check"):
        print(__doc__)
        return 2
    try:
        out = run(ROOT)
    except Exception as exc:  # noqa: BLE001
        print(f"paper_equity_recheck: rc2 cannot read a face: {exc}")
        return 2
    path = os.path.join(ROOT, "results", "paper_equity_recheck.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print("paper_equity_recheck: verdict=%s traders=%d total_equity=%.2f problems=%d "
          "price_lags=%d unverified=%d reader_stale=%d -> results/paper_equity_recheck.json"
          % (out["verdict"], out["n_traders"], out["total_equity_cny"],
             len(out["problems"]), len(out["price_lags"]), len(out["prices_unverified"]),
             int((out["readers"].get("strategy_scorecard") or {}).get("n_stale") or 0)))
    for row in (out["readers"].get("strategy_scorecard") or {}).get("stale") or []:
        print("  STALE-COPY %s: scorecard %.2f = prior bar %.2f (ledger %.2f, d %+.2f)"
              % (row["trader"], row["scorecard_cny"], row["prior_bar_equity_cny"],
                 row["ledger_cny"], row["delta_vs_ledger_cny"]))
    for p in out["problems"][:10]:
        print("  PROBLEM", p)
    return 0 if out["verdict"] == "PASS" else 1


# --------------------------------------------------------------------------
# selftest: offline fixtures, one defect per leg
# --------------------------------------------------------------------------

def _fixture(tmp: str, skip_panel: str | None = None) -> dict:
    """One two-position book that satisfies every identity, plus the reader faces."""
    os.makedirs(os.path.join(tmp, "results", "paper"), exist_ok=True)
    os.makedirs(os.path.join(tmp, "results", "paper_export"), exist_ok=True)
    os.makedirs(os.path.join(tmp, "data", "daily"), exist_ok=True)

    def write_panel(code: str, bar: str, close: float, prefix: str = "") -> None:
        if skip_panel == code:
            return
        with open(os.path.join(tmp, "data", "daily", f"{prefix}{code}.csv"), "w",
                  encoding="utf-8") as fh:
            fh.write("date,open,high,low,close,volume,amount\n")
            fh.write("2026-11-13,1.0,1.0,1.0,1.0,1,1\n")
            fh.write(f"{bar},1.0,1.0,1.0,{close},1,1\n")

    # 159996: 1000 x 1.368 = 1368.00 ; 511010: 10 x 141.2 = 1412.00
    write_panel("159996", "2026-11-16", 1.3680)
    write_panel("511010", "2026-11-16", 141.2000)
    pv = 1368.0 + 1412.0
    cash = 1000000.0 - pv
    ledger = {
        "trader": "FIX-01",
        "cutoff": "2026-11-16",
        "capital": {"initial_cash_cny": 1000000.0, "equity_cny": 1000000.0,
                    "positions_value_cny": pv, "cash_cny": cash},
        "open_positions": [
            {"symbol": "159996", "quantity": 1000.0, "cost_price": 1.2000,
             "last_close": 1.3680, "market_value_cny": 1368.0,
             "unrealized_pnl_cny": 168.0},
            {"symbol": "511010", "quantity": 10.0, "cost_price": 141.4400,
             "last_close": 141.2000, "market_value_cny": 1412.0,
             "unrealized_pnl_cny": -2.4},
        ],
    }
    with open(os.path.join(tmp, "results", "paper", "FIX-01_paper.json"), "w",
              encoding="utf-8") as fh:
        json.dump(ledger, fh, ensure_ascii=False)
    export = {
        "export_date": "2026-11-16",
        "traders": [{"trader": "FIX-01",
                     "capital_cny": {"initial": 1000000.0, "equity": 1000000.0,
                                     "positions_value": pv, "cash": cash}}],
        "summary": {"total_equity_cny": 1000000.0},
    }
    with open(os.path.join(tmp, "results", "paper_export", "latest.json"), "w",
              encoding="utf-8") as fh:
        json.dump(export, fh, ensure_ascii=False)
    scorecard = {"trader_cards": {"FIX-01": {"live_paper": {"capital": {"equity_cny": 1000000.0}}}}}
    with open(os.path.join(tmp, "results", "strategy_scorecard.json"), "w",
              encoding="utf-8") as fh:
        json.dump(scorecard, fh, ensure_ascii=False)
    return ledger


def _rewrite(tmp: str, ledger: dict) -> None:
    with open(os.path.join(tmp, "results", "paper", "FIX-01_paper.json"), "w",
              encoding="utf-8") as fh:
        json.dump(ledger, fh, ensure_ascii=False)


def _rewrite_json(tmp: str, rel: str, obj: dict) -> None:
    with open(os.path.join(tmp, rel), "w", encoding="utf-8") as fh:
        json.dump(obj, fh, ensure_ascii=False)


def selftest() -> int:
    legs = []

    def leg(name: str, ok: bool, detail: str = "") -> None:
        legs.append((name, bool(ok), detail))

    def case(mutate) -> dict:
        tmp = tempfile.mkdtemp(prefix="per_")
        try:
            _fixture(tmp)
            mutate(tmp)
            return run(tmp)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    base = case(lambda t: None)
    leg("L1 the clean fixture passes every identity", base["verdict"] == "PASS", base["verdict"])
    leg("L1b the fixture books two positions", base["n_traders"] == 1
        and base["traders"][0]["n_positions"] == 2)

    def bump_pv(tmp):
        led = _load(os.path.join(tmp, "results", "paper", "FIX-01_paper.json"))
        led["capital"]["positions_value_cny"] += 1.0
        _rewrite(tmp, led)
    out = case(bump_pv)
    leg("L2 a positions_value that is one yuan off is a breach",
        out["verdict"] == "BREACH" and any("L1 positions_value" in p for p in out["problems"]),
        out["problems"][:1])

    def bump_mv_field(tmp):
        led = _load(os.path.join(tmp, "results", "paper", "FIX-01_paper.json"))
        led["open_positions"][0]["market_value_cny"] += 5.0
        _rewrite(tmp, led)
    out = case(bump_mv_field)
    leg("L3 a market_value field that disagrees with the same row's qty x close is caught",
        any("L2 market_value" in p for p in out["problems"]), out["problems"][:1])

    def bump_pnl(tmp):
        led = _load(os.path.join(tmp, "results", "paper", "FIX-01_paper.json"))
        led["open_positions"][1]["unrealized_pnl_cny"] = 100.0
        _rewrite(tmp, led)
    out = case(bump_pnl)
    leg("L4 a hand-typed unrealized pnl is caught",
        any("L3 unrealized" in p for p in out["problems"]), out["problems"][:1])

    def break_cash(tmp):
        led = _load(os.path.join(tmp, "results", "paper", "FIX-01_paper.json"))
        led["capital"]["cash_cny"] += 100.0
        _rewrite(tmp, led)
    out = case(break_cash)
    leg("L5 cash + positions that does not rebuild equity is caught",
        any("L4 cash+pv" in p for p in out["problems"]), out["problems"][:1])

    def wrong_mark(tmp):
        led = _load(os.path.join(tmp, "results", "paper", "FIX-01_paper.json"))
        led["open_positions"][0]["last_close"] = 1.5000
        led["open_positions"][0]["market_value_cny"] = 1500.0
        led["capital"]["positions_value_cny"] = 1500.0 + 1412.0
        _rewrite(tmp, led)
    out = case(wrong_mark)
    leg("L6 a mark that is not the panel's close is a breach, even when the book is self-consistent",
        any("L5 mark 159996" in p for p in out["problems"]), out["problems"][:1])

    def newer_mark(tmp):
        led = _load(os.path.join(tmp, "results", "paper", "FIX-01_paper.json"))
        led["cutoff"] = "2026-11-13"
        _rewrite(tmp, led)
    out = case(newer_mark)
    leg("L7 a mark priced on a bar newer than the ledger's cutoff is a breach",
        any("L6 mark" in p for p in out["problems"]), out["problems"][:1])

    def lagging_panel(tmp):
        base_dir = os.path.join(tmp, "data", "daily")
        with open(os.path.join(base_dir, "159996.csv"), "w", encoding="utf-8") as fh:
            fh.write("date,open,high,low,close,volume,amount\n2026-11-13,1,1,1,1.3680,1,1\n")
    out = case(lagging_panel)
    leg("L8 a panel bar behind the cutoff is disclosed as a lag, not called a wrong price",
        out["verdict"] == "PASS" and any(x["symbol"] == "159996" for x in out["price_lags"]),
        out["price_lags"][:1])

    def two_families(tmp):
        with open(os.path.join(tmp, "data", "daily", "sh159996.csv"), "w", encoding="utf-8") as fh:
            fh.write("date,open,high,low,close,volume,amount\n2026-11-16,1,1,1,1.2900,1,1\n")
    out = case(two_families)
    leg("L9 two panel families disagreeing on the same bar is reported, never silently resolved",
        out["verdict"] == "PASS"
        and any(x["symbol"] == "159996" for x in out["prices_unverified"]),
        out["prices_unverified"][:1])

    def no_panel(tmp):
        os.remove(os.path.join(tmp, "data", "daily", "511010.csv"))
    out = case(no_panel)
    leg("L10 a mark with no panel file is unverified, not a breach",
        out["verdict"] == "PASS"
        and any(x["symbol"] == "511010" for x in out["prices_unverified"]),
        out["prices_unverified"][:1])

    def export_drift(tmp):
        exp = _load(os.path.join(tmp, "results", "paper_export", "latest.json"))
        exp["traders"][0]["capital_cny"]["equity"] += 50.0
        exp["summary"]["total_equity_cny"] += 50.0
        _rewrite_json(tmp, os.path.join("results", "paper_export", "latest.json"), exp)
    out = case(export_drift)
    leg("R1 an export that drifted from the ledger is caught",
        any(p.startswith("R1 FIX-01 equity") for p in out["problems"]), out["problems"][:1])

    def total_drift(tmp):
        exp = _load(os.path.join(tmp, "results", "paper_export", "latest.json"))
        exp["summary"]["total_equity_cny"] += 7.0
        _rewrite_json(tmp, os.path.join("results", "paper_export", "latest.json"), exp)
    out = case(total_drift)
    leg("R2 an export total that is not its own rows' sum is caught",
        any(p.startswith("R2 export total") for p in out["problems"]), out["problems"][:1])

    def scorecard_drift(tmp):
        sc = _load(os.path.join(tmp, "results", "strategy_scorecard.json"))
        sc["trader_cards"]["FIX-01"]["live_paper"]["capital"]["equity_cny"] += 3.0
        _rewrite_json(tmp, os.path.join("results", "strategy_scorecard.json"), sc)
    out = case(scorecard_drift)
    leg("R3 a scorecard card that drifted from the ledger is caught",
        any(p.startswith("R3 FIX-01") for p in out["problems"]), out["problems"][:1])

    def _sc(tmp, generated, equity):
        sc = _load(os.path.join(tmp, "results", "strategy_scorecard.json"))
        if generated is not None:
            sc["generated"] = generated
        sc["trader_cards"]["FIX-01"]["live_paper"]["capital"]["equity_cny"] = equity
        _rewrite_json(tmp, os.path.join("results", "strategy_scorecard.json"), sc)

    # The fixture's prior bar prices both codes at 1.0: 1000 x 1.0 + 10 x 1.0 + cash.
    prior_eq = 1000.0 * 1.0 + 10.0 * 1.0 + (1000000.0 - 1368.0 - 1412.0)

    out = case(lambda t: _sc(t, "2026-11-16T02:00:00", prior_eq))
    leg("R3b a scorecard written before the bar's 15:30 close is disclosed as one bar "
        "behind, not called a breach",
        out["verdict"] == "PASS"
        and (out["readers"].get("strategy_scorecard") or {}).get("state") == "STALE_BY_GENERATION"
        and (out["readers"]["strategy_scorecard"]["stale"] or [{}])[0].get("trader") == "FIX-01",
        out["problems"][:1])

    out = case(lambda t: _sc(t, "2026-11-16T02:00:00", prior_eq + 270.0))
    leg("R3c a copy that is older than the bar but matches neither bar is still a breach",
        any("does not reproduce the prior bar" in p for p in out["problems"]),
        out["problems"][:1])

    out = case(lambda t: _sc(t, "2026-11-16T16:00:00", prior_eq))
    leg("R3d a copy written after the close is held to the current bar",
        any(p.startswith("R3 FIX-01 scorecard equity") for p in out["problems"]),
        out["problems"][:1])

    def rounding_ok(tmp):
        led = _load(os.path.join(tmp, "results", "paper", "FIX-01_paper.json"))
        led["capital"]["positions_value_cny"] += 0.0149
        led["capital"]["cash_cny"] -= 0.0149
        _rewrite(tmp, led)
    out = case(rounding_ok)
    leg("T1 a sub-cent rounding difference is not a breach", out["verdict"] == "PASS",
        out["problems"][:1])

    tmp = tempfile.mkdtemp(prefix="per_empty_")
    try:
        out = run(tmp)
        leg("T2 no ledger faces at all reads NO_LEDGERS instead of a pass",
            out["verdict"] == "NO_LEDGERS", out["verdict"])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    fails = [f"{n}: {d}" for n, ok, d in legs if not ok]
    for name, ok, _ in legs:
        print(("PASS " if ok else "FAIL ") + name)
    print("paper_equity_recheck selftest %d/%d" % (len(legs) - len(fails), len(legs)))
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))

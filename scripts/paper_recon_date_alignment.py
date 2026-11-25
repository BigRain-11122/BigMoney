"""Paper book recon: is an export-vs-ledger gap a drift, or just a different bar?

Why this face exists: `paper_equity_recheck.py` R1 compares
`results/paper_export/latest.json` against each ledger's `capital` block with no
date guard. The export face is a snapshot of the book at its own `export_date`,
while the ledger is repriced every time a new daily bar lands, so the morning
after a bar the two faces describe two different closes. R1 then reports every
held name as a breach. On 2026-11-25 that produced eight R1 lines totalling
+20,616.79 CNY across four traders -- and every one of them is one bar of price
movement, not a bookkeeping error:

    COMPOSITE-CE-01  159996  export 1.376 (11-24 close)  ledger 1.350 (11-25 close)

That is the r1880 shape ("A is behind B" is not "B is wrong"), so the fix is to
verify the export at its *own* bar instead of excusing it: repricing the ledger's
quantities on the export date must reproduce the export. A gap that survives
that reprice is a real drift and is named.

Readings (per trader), in the order they are decided:
  D0  the export row and the ledger share one as-of bar   -> direct compare (same as R1)
  D1  the ledger's quantities, priced at the export date, reproduce the export
  D2  cash is unchanged between the two dates (no trade in the gap)
  D3  every held symbol has a bar on the export date (else the gap is unreadable)
  D4  residual after D1 is stated in money and in pp of equity; the raw R1 gap is
      decomposed per symbol (qty x price change) so nothing is left unattributed

Subcommands:
  run       -> results/paper_recon_date_alignment.json + one-line verdict
  selftest  offline fixtures (no live data, no network)

exit 0 = every export row is explained at its own bar (or matches directly)
exit 1 = at least one real drift / a gap that cannot be attributed
exit 2 = a face cannot be read
"""
from __future__ import annotations

import glob
import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Money is stated to the cent; rounding per name is the widest a difference may
# be and still be the same number (same convention as paper_equity_recheck).
AMOUNT_TOL = 0.02


def _tol(value: float) -> float:
    return AMOUNT_TOL + 1e-9 * abs(value)


def _load(path: str):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _dump(obj, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1, sort_keys=False)
        fh.write("\n")


def closes_by_date(root: str, code: str) -> tuple[dict, list]:
    """{date: close} for one code across every daily family, plus conflicts.

    Two families live in data/daily (bare `510300.csv` and `sh510300.csv`); they
    are separate writers and may disagree. A date on which they disagree is
    reported, not silently resolved by picking the newer file.
    """
    per_family: dict[str, dict] = {}
    for name in (f"{code}.csv", f"sh{code}.csv", f"sz{code}.csv"):
        path = os.path.join(root, "data", "daily", name)
        if not os.path.exists(path):
            continue
        rows = {}
        with open(path, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if not line or line[:4].lower() == "date":
                    continue
                parts = line.split(",")
                if len(parts) < 5:
                    continue
                try:
                    rows[parts[0]] = float(parts[4])
                except ValueError:
                    continue
        if rows:
            per_family[name] = rows

    out: dict[str, float] = {}
    conflicts = []
    dates = sorted({d for rows in per_family.values() for d in rows})
    for d in dates:
        seen = {name: rows[d] for name, rows in per_family.items() if d in rows}
        values = {round(v, 4) for v in seen.values()}
        if len(values) > 1:
            conflicts.append({"date": d, "families": seen})
            continue
        out[d] = next(iter(seen.values()))
    return out, conflicts


def align_one(export_row: dict, ledger: dict, root: str, export_date: str) -> dict:
    """Decide one trader's export-vs-ledger gap against the export's own bar."""
    tid = ledger.get("trader") or export_row.get("trader")
    cutoff = ledger.get("cutoff")
    cap = ledger.get("capital") or {}
    exp_cap = export_row.get("capital_cny") or {}

    res = {
        "trader": tid,
        "export_date": export_date,
        "ledger_cutoff": cutoff,
        "export_equity": exp_cap.get("equity"),
        "ledger_equity": cap.get("equity_cny"),
        "export_positions_value": exp_cap.get("positions_value"),
        "ledger_positions_value": cap.get("positions_value_cny"),
        "cash_export": exp_cap.get("cash"),
        "cash_ledger": cap.get("cash_cny"),
        "problems": [],
        "unattributed_cny": None,
    }
    try:
        exp_eq = float(exp_cap.get("equity"))
        exp_pv = float(exp_cap.get("positions_value"))
        led_eq = float(cap.get("equity_cny"))
        led_pv = float(cap.get("positions_value_cny"))
        led_cash = float(cap.get("cash_cny") or 0.0)
    except (TypeError, ValueError):
        res["problems"].append("D0 capital fields are not numeric on one side")
        res["verdict"] = "UNREADABLE"
        return res

    raw_gap = exp_eq - led_eq
    res["raw_gap_cny"] = round(raw_gap, 2)

    if export_date and cutoff and export_date == cutoff:
        res["verdict"] = "SAME_BAR"
        if abs(raw_gap) > _tol(led_eq):
            res["problems"].append(
                "D0 same bar but equity differs by %+.2f" % raw_gap)
            res["verdict"] = "REAL_DRIFT"
        return res

    if not export_date or not cutoff:
        res["problems"].append("D0 one side has no as-of date")
        res["verdict"] = "UNREADABLE"
        return res

    if export_date > cutoff:
        # The export is ahead of the ledger: the ledger has not priced a bar the
        # export claims to have seen. Never align forward -- that would be a
        # future mark (see no_future_data on every ledger face).
        res["problems"].append(
            "D0 export date %s is newer than ledger cutoff %s" % (export_date, cutoff))
        res["verdict"] = "EXPORT_AHEAD"
        return res

    # D2: a trade between the two dates moves cash *and* the position set, so the
    # ledger's quantities are not the export's quantities and no reprice can
    # reconcile them.
    cash_exp = exp_cap.get("cash")
    try:
        cash_exp = float(cash_exp)
    except (TypeError, ValueError):
        res["problems"].append("D2 export cash unreadable")
        res["verdict"] = "UNREADABLE"
        return res
    cash_gap = cash_exp - led_cash
    res["cash_gap_cny"] = round(cash_gap, 2)
    if abs(cash_gap) > _tol(led_cash):
        res["verdict"] = "TRADES_BETWEEN"
        res["problems"].append(
            "D2 cash moved %+.2f between %s and %s: the position sets differ, so "
            "the gap is not a repricing question" % (cash_gap, export_date, cutoff))
        return res

    # D1/D3: reprice the ledger's quantities on the export date.
    mv = 0.0
    decomposition = []
    for p in ledger.get("open_positions") or []:
        code = str(p.get("symbol"))
        try:
            qty = float(p["quantity"])
            led_close = float(p["last_close"])
        except (KeyError, TypeError, ValueError):
            res["problems"].append(f"D3 position row unreadable: {code}")
            continue
        bars, conflicts = closes_by_date(root, code)
        if conflicts:
            res["problems"].append(
                "D3 %s has two families disagreeing on a bar (%d date(s))"
                % (code, len(conflicts)))
        if export_date not in bars:
            res["problems"].append(
                "D3 %s has no bar on %s (families read from data/daily)"
                % (code, export_date))
            continue
        exp_close = bars[export_date]
        mv += qty * exp_close
        decomposition.append({
            "symbol": code,
            "quantity": qty,
            "close_export_bar": exp_close,
            "close_ledger_bar": led_close,
            "value_export_bar": round(qty * exp_close, 2),
            "value_ledger_bar": round(qty * led_close, 2),
            "attributable_cny": round(qty * (led_close - exp_close), 2),
        })

    if res["problems"]:
        res["verdict"] = "INCOMPARABLE"
        res["decomposition"] = decomposition
        return res

    res["positions_value_at_export_bar"] = round(mv, 2)
    res["decomposition"] = decomposition
    residual = exp_pv - mv
    res["residual_cny"] = round(residual, 2)
    res["residual_bp_of_equity"] = round(1e4 * residual / led_eq, 2)
    res["unattributed_cny"] = round(raw_gap - (mv - led_pv), 2)
    res["verdict"] = "ALIGNED_AT_EXPORT_BAR" if abs(residual) <= _tol(exp_pv) else "REAL_DRIFT"
    if res["verdict"] == "REAL_DRIFT":
        res["problems"].append(
            "D1 repriced at %s the export still differs by %+.2f (%.1f bp of equity)"
            % (export_date, residual, res["residual_bp_of_equity"]))
    elif abs(res["unattributed_cny"]) > _tol(exp_eq):
        res["problems"].append(
            "D4 %+.2f of the %+.2f gap is not explained by held-name repricing"
            % (res["unattributed_cny"], raw_gap))
        res["verdict"] = "PARTIALLY_ATTRIBUTED"
    return res


def run(root: str = ROOT) -> dict:
    export_path = os.path.join(root, "results", "paper_export", "latest.json")
    out = {
        "face": "paper_recon_date_alignment",
        "why": ("an export-vs-ledger gap is read at the export's own bar; a gap that "
                "survives repricing is a drift, one that disappears is a bar lag"),
        "inputs": ["results/paper_export/latest.json", "results/paper/*_paper.json",
                   "data/daily"],
        "rows": [],
        "problems": [],
        "zeros": {"engine_runs": 0, "ledger_trials_added": 0, "network": "zero"},
    }
    if not os.path.exists(export_path):
        out["verdict"] = "UNREADABLE"
        out["problems"].append("results/paper_export/latest.json missing")
        _dump(out, os.path.join(root, "results", "paper_recon_date_alignment.json"))
        return out

    export = _load(export_path)
    export_date = export.get("export_date")
    rows = {r.get("trader"): r for r in export.get("traders") or []}
    out["export_date"] = export_date

    ledgers = {}
    for path in sorted(glob.glob(os.path.join(root, "results", "paper", "*_paper.json"))):
        try:
            led = _load(path)
        except Exception as exc:  # noqa: BLE001 - an unreadable face is a finding
            out["problems"].append("ledger unreadable: %s (%s)" % (path, exc))
            continue
        ledgers[led.get("trader")] = led
    out["n_ledgers"] = len(ledgers)

    for tid, led in ledgers.items():
        if tid not in rows:
            out["problems"].append("D0 ledger %s has no export row" % tid)
            continue
        out["rows"].append(align_one(rows[tid], led, root, export_date))

    for tid in rows:
        if tid not in ledgers:
            out["problems"].append("D0 export names %s with no ledger face" % tid)

    verdicts = [r.get("verdict") for r in out["rows"]]
    bad = [r for r in out["rows"]
           if r.get("verdict") not in ("SAME_BAR", "ALIGNED_AT_EXPORT_BAR")]
    out["n_rows"] = len(out["rows"])
    out["n_explained"] = sum(1 for v in verdicts if v == "ALIGNED_AT_EXPORT_BAR")
    out["n_same_bar"] = sum(1 for v in verdicts if v == "SAME_BAR")
    out["raw_gap_total_cny"] = round(sum(r.get("raw_gap_cny") or 0.0 for r in out["rows"]), 2)
    out["residual_total_cny"] = round(
        sum(abs(r.get("residual_cny") or 0.0) for r in out["rows"]), 2)

    if out["problems"] or bad:
        out["verdict"] = "FAIL"
    else:
        out["verdict"] = "PASS"
    out["readings"] = {
        "PASS": ("every export row is reproduced at its own bar, or shares the "
                 "ledger's bar"),
        "FAIL": "at least one export row is a real drift or a gap that cannot be attributed",
    }[out["verdict"]]
    out["by_verdict"] = {v: verdicts.count(v) for v in sorted(set(verdicts))}

    _dump(out, os.path.join(root, "results", "paper_recon_date_alignment.json"))
    return out


# ---------------------------------------------------------------- selftest ---

def _write_ledger(root: str, tid: str, cutoff: str, rows: list, cash: float,
                  equity: float, pv: float) -> None:
    _dump({
        "trader": tid,
        "cutoff": cutoff,
        "capital": {"equity_cny": equity, "positions_value_cny": pv,
                    "cash_cny": cash, "initial_cash_cny": 1000000.0},
        "open_positions": [
            {"symbol": s, "quantity": q, "cost_price": c, "last_close": lc,
             "market_value_cny": round(q * lc, 2)}
            for s, q, c, lc in rows
        ],
    }, os.path.join(root, "results", "paper", "%s_paper.json" % tid))


def _write_export(root: str, date: str, per: dict) -> None:
    traders = []
    total = 0.0
    for tid, cap in per.items():
        traders.append({"trader": tid, "capital_cny": {
            "equity": cap["equity"], "positions_value": cap["pv"],
            "cash": cap["cash"], "initial": 1000000.0, "denomination": "CNY"}})
        total += cap["equity"]
    _dump({"export_date": date, "traders": traders,
           "summary": {"traders": len(traders), "total_equity_cny": total}},
          os.path.join(root, "results", "paper_export", "latest.json"))


def _panel(root: str, code: str, bars: dict) -> None:
    path = os.path.join(root, "data", "daily", "%s.csv" % code)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write("date,open,high,low,close,volume\n")
        for d, c in sorted(bars.items()):
            fh.write("%s,%.4f,%.4f,%.4f,%.4f,0\n" % (d, c, c, c, c))


def selftest() -> int:
    legs = []

    def leg(name, cond, detail=""):
        legs.append({"leg": name, "ok": bool(cond), "detail": detail})

    tmp = tempfile.mkdtemp(prefix="recon_align_")
    try:
        # --- fixture: one name, two bars ---------------------------------
        # ledger priced on 11-25 (close 1.350) at qty 100,000 => pv 135,000
        # export snapshot on 11-24 (close 1.376) => pv 137,600, equity 147,600
        case = os.path.join(tmp, "case")
        _panel(case, "159996", {"2026-11-24": 1.376, "2026-11-25": 1.350})
        _write_ledger(case, "T-01", "2026-11-25", [("159996", 100000, 1.356, 1.350)],
                      cash=10000.0, equity=145000.0, pv=135000.0)
        _write_export(case, "2026-11-24",
                      {"T-01": {"equity": 147600.0, "pv": 137600.0, "cash": 10000.0}})
        out = run(case)
        row = out["rows"][0]
        leg("one-bar lag is aligned, not a breach",
            row["verdict"] == "ALIGNED_AT_EXPORT_BAR" and out["verdict"] == "PASS",
            row["verdict"])
        leg("the raw gap is the price change on the held name",
            abs(row["raw_gap_cny"] - 2600.0) < 0.02, row.get("raw_gap_cny"))
        leg("residual after repricing is zero",
            row.get("residual_cny") is not None
            and abs(row["residual_cny"]) < 0.02, row.get("residual_cny"))

        # --- real drift: export price is not any bar's close --------------
        _write_export(case, "2026-11-24",
                      {"T-01": {"equity": 148600.0, "pv": 138600.0, "cash": 10000.0}})
        out = run(case)
        row = out["rows"][0]
        leg("a phantom export price is a real drift",
            row["verdict"] == "REAL_DRIFT" and out["verdict"] == "FAIL", row["verdict"])
        leg("the drift is priced in money and bp",
            row.get("residual_cny") == 1000.0 and row.get("residual_bp_of_equity") is not None,
            (row.get("residual_cny"), row.get("residual_bp_of_equity")))

        # --- same bar: falls back to a direct compare --------------------
        _write_export(case, "2026-11-25",
                      {"T-01": {"equity": 145000.0, "pv": 135000.0, "cash": 10000.0}})
        out = run(case)
        leg("same bar compares directly",
            out["rows"][0]["verdict"] == "SAME_BAR" and out["verdict"] == "PASS",
            out["rows"][0]["verdict"])

        # --- a trade in the gap makes the quantity basis differ -----------
        _write_export(case, "2026-11-24",
                      {"T-01": {"equity": 147600.0, "pv": 137600.0, "cash": 12000.0}})
        out = run(case)
        leg("cash moved => not a repricing question",
            out["rows"][0]["verdict"] == "TRADES_BETWEEN", out["rows"][0]["verdict"])

        # --- no bar on the export date: refuse rather than guess ----------
        case2 = os.path.join(tmp, "case2")
        _panel(case2, "511010", {"2026-11-25": 141.416})
        _write_ledger(case2, "T-02", "2026-11-25",
                      [("511010", 1000, 141.44, 141.416)],
                      cash=5000.0, equity=146416.0, pv=141416.0)
        _write_export(case2, "2026-11-24",
                      {"T-02": {"equity": 146500.0, "pv": 141500.0, "cash": 5000.0}})
        out = run(case2)
        leg("a missing bar is incomparable, not a pass",
            out["rows"][0]["verdict"] == "INCOMPARABLE" and out["verdict"] == "FAIL",
            out["rows"][0]["verdict"])

        # --- export ahead of the ledger: never align forward -------------
        _write_export(case2, "2026-11-26",
                      {"T-02": {"equity": 146500.0, "pv": 141500.0, "cash": 5000.0}})
        out = run(case2)
        leg("an export ahead of the ledger is refused",
            out["rows"][0]["verdict"] == "EXPORT_AHEAD", out["rows"][0]["verdict"])

        # --- two families disagreeing on the same bar -------------------
        case3 = os.path.join(tmp, "case3")
        _panel(case3, "511010", {"2026-11-24": 141.438, "2026-11-25": 141.416})
        with open(os.path.join(case3, "data", "daily", "sh511010.csv"), "w",
                  encoding="utf-8", newline="") as fh:
            fh.write("date,open,high,low,close,volume\n")
            fh.write("2026-11-24,1,1,1,141.0000,0\n")
            fh.write("2026-11-25,1,1,1,141.4160,0\n")
        _write_ledger(case3, "T-03", "2026-11-25", [("511010", 1000, 141.44, 141.416)],
                      cash=5000.0, equity=146416.0, pv=141416.0)
        _write_export(case3, "2026-11-24",
                      {"T-03": {"equity": 146438.0, "pv": 141438.0, "cash": 5000.0}})
        out = run(case3)
        leg("a split panel is named, not silently resolved",
            out["rows"][0]["verdict"] == "INCOMPARABLE"
            and any("disagreeing" in p for p in out["rows"][0]["problems"]),
            out["rows"][0].get("problems"))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    ok = sum(1 for l in legs if l["ok"])
    for l in legs:
        print(("PASS " if l["ok"] else "FAIL ") + l["leg"] + (
            "" if l["ok"] else "  <- %r" % (l["detail"],)))
    print("%d/%d legs" % (ok, len(legs)))
    return 0 if ok == len(legs) else 1


def main(argv: list[str]) -> int:
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "selftest":
        return selftest()
    if cmd == "run":
        out = run()
        if out["verdict"] == "PASS":
            print("PAPER-RECON-DATE-ALIGNMENT PASS rows=%d explained_at_own_bar=%d "
                  "same_bar=%d raw_gap=%+.2f"
                  % (out.get("n_rows", 0), out.get("n_explained", 0),
                     out.get("n_same_bar", 0), out.get("raw_gap_total_cny") or 0.0))
            for r in out["rows"]:
                if r["verdict"] == "ALIGNED_AT_EXPORT_BAR":
                    print("  %s: %+.2f gap == one bar of price (residual %+.2f, %s -> %s)"
                          % (r["trader"], r["raw_gap_cny"], r.get("residual_cny") or 0.0,
                             r["export_date"], r["ledger_cutoff"]))
            return 0
        print("PAPER-RECON-DATE-ALIGNMENT %s" % out["verdict"])
        for p in out.get("problems") or []:
            print("  " + p)
        for r in out["rows"]:
            if r["verdict"] not in ("SAME_BAR", "ALIGNED_AT_EXPORT_BAR"):
                print("  %s %s: %s" % (r["trader"], r["verdict"],
                                       "; ".join(r.get("problems") or [])[:200]))
        return 1
    if cmd in ("-h", "--help", "help"):
        print(__doc__)
        return 0
    print("unknown subcommand: %s (use run|selftest)" % cmd)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))

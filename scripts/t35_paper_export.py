"""T-35 d3: daily paper-plane export face (CEO order O-20260924-2045 s3).

"每天让我看到他们的持仓和操作" -- this script materializes the daily
read-only export consumed by the city-side probe (results/paper_export/,
FluxVerse face per F-20260924-16) and any T-29 scorecard consumer.

Scope (deliverable 3 of ticket T-2026-09-24-35): positions + operations
+ capital per registered paper trader. PROSPECT members are excluded by
construction (results/prospect_paper/ is a separate dir; O-2045 keeps
their observation capital at zero).

Operations derivation (deterministic, three-tier honest):
  tier 1  prior daily export in results/paper_export/ (export-<D>.json
          with D < today) -> per-symbol position diff = entries/exits
          (canonical chain from the second export day onward)
  tier 2  day-1 fallback: entries from engine hold_days<=1 (entered on
          the current bar day); exits NOT derivable without a prior
          face -> honest "exits_not_derivable_first_snapshot": true
  T+1 contract makes same-day roundtrips impossible (engine law), so
  a position present yesterday and absent today = exit today.

Idempotency: output bytes are data-driven (no wall-clock field) --
rerunning on unchanged inputs rewrites identical files, so the S6 chain
can carry this step every round without git churn.

Display law: CEO 2026-09-23 sensitivity law (no price-change %/K-line/
FX on the city face) is a RENDER-side constraint; this data face carries
amounts per O-2045 (CEO one-word toggle to direct display, city side).

Usage:
    python scripts/t35_paper_export.py              # export -> results/paper_export/
    python scripts/t35_paper_export.py --selftest   # offline fixtures
Exit codes: 0 = exported (or honest partial with missing faces),
            2 = mechanism fault (no readable trader state at all).
"""
import datetime as dt
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import PATHS

PAPER_DIR = os.path.join(PATHS.results_dir, "paper")
MARKS_DIR = os.path.join(PAPER_DIR, "marks")
EXPORT_DIR = os.path.join(PATHS.results_dir, "paper_export")
EVIDENCE = "O-20260924-2045 s3 (T-35 d3); capital/open_positions faces = R93 "
"additive engine export; marks lane = Bigmoney-IntradayMarks (R93)"
QTY_EPS = 1e-9


def _read_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _write_json_atomic(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    os.replace(tmp, path)


def _derive_operations(current_positions, prior_positions, prior_available):
    """Per-trader operations today. Returns (ops, source, first_snapshot)."""
    if prior_available:
        cur = {p["symbol"]: p for p in current_positions}
        pri = {p["symbol"]: p for p in prior_positions}
        ops = []
        for sym, p in sorted(cur.items()):
            if sym not in pri:
                ops.append({"action": "entry", "symbol": sym,
                            "quantity": p["quantity"],
                            "cost_price": p["cost_price"]})
            elif abs(float(p["quantity"]) - float(pri[sym]["quantity"])) > QTY_EPS:
                ops.append({"action": "qty_change", "symbol": sym,
                            "quantity_prior": pri[sym]["quantity"],
                            "quantity": p["quantity"]})
        for sym, p in sorted(pri.items()):
            if sym not in cur:
                ops.append({"action": "exit", "symbol": sym,
                            "quantity_prior": p["quantity"]})
        return ops, "prior_export_diff", False
    # day-1: engine hold_days<=1 == entered on the current bar day
    ops = []
    for p in current_positions:
        if int(p.get("hold_days", 0)) <= 1:
            ops.append({"action": "entry", "symbol": p["symbol"],
                        "quantity": p["quantity"],
                        "cost_price": p["cost_price"]})
    return ops, "hold_days_derivation_first_snapshot", True


def _prior_export(export_dir, today):
    """Latest export file strictly older than today (tier-1 diff source)."""
    best_date, best_path = None, None
    for path in glob.glob(os.path.join(export_dir, "export-*.json")):
        d = os.path.basename(path)[len("export-"):-len(".json")]
        if len(d) == 10 and d < today and (best_date is None or d > best_date):
            best_date, best_path = d, path
    return best_date, best_path


def _marks_face(marks_dir, date):
    """Last tick of the day's marks jsonl (intraday marking evidence).

    R93 lane filenames are compact-date (marks-YYYYMMDD.jsonl); the export
    date is ISO -- normalize before joining.
    """
    compact = str(date).replace("-", "")
    path = os.path.join(marks_dir, f"marks-{compact}.jsonl")
    if not os.path.exists(path):
        return None
    last = None
    n = 0
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                last = json.loads(line)
            except json.JSONDecodeError:
                continue  # torn tail line: skip, last good tick stands
            n += 1
    if last is None:
        return None
    traders = last.get("traders", {})
    return {
        "file": os.path.basename(path),
        "ticks": n,
        "last_tick_ts": last.get("ts"),
        "last_tick_kind": last.get("kind"),
        "source": last.get("source"),
        "per_trader_equity_mark_cny": {
            tid: face.get("equity_mark_cny")
            for tid, face in sorted(traders.items())
        },
    }


def build_export(paper_dir, marks_dir, export_dir):
    """Pure worker: dirs in, export dict out (selftest-friendly)."""
    state_paths = sorted(glob.glob(os.path.join(paper_dir, "*_paper.json")))
    if not state_paths:
        raise FileNotFoundError("no *_paper.json states under " + paper_dir)

    states = {}
    missing_faces = []
    for path in state_paths:
        st = _read_json(path)
        tid = os.path.basename(path)[: -len("_paper.json")]
        states[tid] = st
        if "capital" not in st:
            missing_faces.append(f"{tid}:capital")
        if "open_positions" not in st:
            missing_faces.append(f"{tid}:open_positions")

    cutoffs = [st.get("cutoff") or "" for st in states.values()]
    today = max(cutoffs) if cutoffs else ""
    if not today:
        raise ValueError("no state cutoff readable (export date unknown)")

    prior_date, prior_path = _prior_export(export_dir, today)
    prior = _read_json(prior_path) if prior_path else None
    exits_not_derivable = prior is None

    traders_out = []
    tot_equity = tot_pos = tot_entries = tot_exits = 0
    for tid, st in sorted(states.items()):
        positions = st.get("open_positions", [])
        capital = st.get("capital", {})
        prior_positions = []
        if prior is not None:
            for pt in prior.get("traders", []):
                if pt.get("trader") == tid:
                    prior_positions = pt.get("open_positions", [])
        ops, source, _first = _derive_operations(
            positions, prior_positions, prior is not None)
        entries = sum(1 for o in ops if o["action"] == "entry")
        exits = sum(1 for o in ops if o["action"] == "exit")
        tot_equity += float(capital.get("equity_cny", 0.0) or 0.0)
        tot_pos += len(positions)
        tot_entries += entries
        tot_exits += exits
        w = st.get("window_metrics", {})
        traders_out.append({
            "trader": tid,
            "capital_cny": {
                "initial": capital.get("initial_cash_cny"),
                "equity": capital.get("equity_cny"),
                "positions_value": capital.get("positions_value_cny"),
                "cash": capital.get("cash_cny"),
                "denomination": capital.get("denomination", "CNY"),
            },
            "open_positions": [
                {"symbol": p["symbol"], "quantity": p["quantity"],
                 "cost_price": p["cost_price"],
                 "last_close": p.get("last_close"),
                 "hold_days": p.get("hold_days"),
                 "market_value_cny": p.get("market_value_cny"),
                 "unrealized_pnl_cny": p.get("unrealized_pnl_cny")}
                for p in positions
            ],
            "positions_count": len(positions),
            "operations_today": ops,
            "operations_source": source,
            "metrics": {
                "paper_start": st.get("paper_start"),
                "bars": st.get("bars"),
                "months_tracked": st.get("months_tracked"),
                "current_dd": st.get("current_dd"),
                "num_trades_window": w.get("num_trades"),
                "win_rate": w.get("win_rate"),
            },
            "regime_guard": {
                "mode": (st.get("regime_guard") or {}).get("mode"),
                "active_from": (st.get("regime_guard") or {}).get("active_from"),
            },
            "state_cutoff": st.get("cutoff"),
            "state_updated": st.get("updated"),
        })

    state_updated_max = max((st.get("updated") or "") for st in states.values())
    out = {
        "schema": "t35_paper_export_v1",
        "ticket": "T-2026-09-24-35",
        "deliverable": "d3-daily-export-face",
        "law_ref": EVIDENCE,
        "export_date": today,
        "evidence_cutoff": today,
        "generated_from_state_updated": state_updated_max,
        "traders": traders_out,
        "marks_face": _marks_face(marks_dir, today),
        "summary": {
            "traders": len(traders_out),
            "total_equity_cny": round(tot_equity, 2),
            "total_positions": tot_pos,
            "entries_today": tot_entries,
            "exits_today": tot_exits,
            "exits_not_derivable_first_snapshot": exits_not_derivable,
        },
        "prior_diff_source": {"date": prior_date,
                              "file": os.path.basename(prior_path)
                              if prior_path else None},
        "prospect_note": "PROSPECT members live in results/prospect_paper/ "
                         "(allocation_pct==0, O-2045 observation-capital "
                         "zero) -- excluded from this export by construction",
        "display_law": "CEO 2026-09-23 sensitivity law is render-side (city "
                       "face: no price-change %/K-line/FX); this data face "
                       "carries amounts per O-2045 (CEO one-word toggle)",
        "no_future_data": "closed bars only; marks are spot quotes for "
                          "marking only, never signal input",
        "missing_faces": missing_faces,
        "audit": {"engine_runs": 0, "ledger_trials_added": 0,
                  "network": "zero (pure local state read)"},
    }
    return out


def run() -> int:
    try:
        out = build_export(PAPER_DIR, MARKS_DIR, EXPORT_DIR)
    except (FileNotFoundError, ValueError, json.JSONDecodeError,
            OSError) as exc:
        print(f"t35_paper_export mechanism fault: {exc}")
        return 2
    daily = os.path.join(EXPORT_DIR, f"export-{out['export_date']}.json")
    latest = os.path.join(EXPORT_DIR, "latest.json")
    _write_json_atomic(daily, out)
    _write_json_atomic(latest, out)
    s = out["summary"]
    print(f"export {out['export_date']}: traders={s['traders']} "
          f"positions={s['total_positions']} equity={s['total_equity_cny']:.0f} "
          f"ops(entry/exit)={s['entries_today']}/{s['exits_today']} "
          f"source={out['prior_diff_source']['date'] or 'first-snapshot'}")
    print(f"-> {daily} + latest.json")
    if out["missing_faces"]:
        print("missing_faces (honest):", ",".join(out["missing_faces"]))
    return 0


def selftest() -> bool:
    """Offline: synthetic dirs, no network, no real-state dependency."""
    import shutil
    import tempfile
    root = tempfile.mkdtemp(prefix="t35_export_st_")
    ok = True
    try:
        paper = os.path.join(root, "paper")
        marks = os.path.join(paper, "marks")
        exdir = os.path.join(root, "paper_export")
        os.makedirs(marks)

        def state(tid, positions, capital, cutoff="2026-09-24", updated="x"):
            st = {"trader": tid, "cutoff": cutoff, "updated": updated,
                  "open_positions": positions, "capital": capital,
                  "window_metrics": {"num_trades": 0, "win_rate": 0.0},
                  "paper_start": "2026-09-23", "bars": 2,
                  "months_tracked": 0, "current_dd": 0.0}
            with open(os.path.join(paper, f"{tid}_paper.json"), "w",
                      encoding="utf-8") as fh:
                json.dump(st, fh)

        cap = {"initial_cash_cny": 1_000_000.0, "equity_cny": 1_000_000.0,
               "positions_value_cny": 0.0, "cash_cny": 1_000_000.0,
               "denomination": "CNY"}
        # S1: day-1 hold_days derivation + first-snapshot honesty
        state("T-A", [{"symbol": "159980", "quantity": 100.0,
                       "cost_price": 2.0, "hold_days": 1,
                       "last_close": 2.0, "market_value_cny": 200.0,
                       "unrealized_pnl_cny": 0.0},
                      {"symbol": "510300", "quantity": 10.0,
                       "cost_price": 4.0, "hold_days": 5,
                       "last_close": 4.0, "market_value_cny": 40.0,
                       "unrealized_pnl_cny": 0.0}],
              {**cap, "equity_cny": 1_000_240.0,
               "positions_value_cny": 240.0, "cash_cny": 999_760.0})
        state("T-B", [], cap)
        out = build_export(paper, marks, exdir)
        ops_a = out["traders"][0]["operations_today"]
        ok &= ([o["symbol"] for o in ops_a] == ["159980"] and
               ops_a[0]["action"] == "entry" and
               out["traders"][0]["operations_source"] ==
               "hold_days_derivation_first_snapshot" and
               out["summary"]["exits_not_derivable_first_snapshot"] is True)
        # S2: idempotency -- second build is byte-identical (no wall clock)
        out2 = build_export(paper, marks, exdir)
        ok &= json.dumps(out, sort_keys=True) == json.dumps(out2, sort_keys=True)
        # S3: write daily + prior-chain diff on the next day
        _write_json_atomic(
            os.path.join(exdir, f"export-{out['export_date']}.json"), out)
        # next day: T-A exited 159980, kept 510300; T-B entered 511010
        state("T-A", [{"symbol": "510300", "quantity": 10.0,
                       "cost_price": 4.0, "hold_days": 6,
                       "last_close": 4.0, "market_value_cny": 40.0,
                       "unrealized_pnl_cny": 0.0}],
              cap, cutoff="2026-09-25", updated="y")
        state("T-B", [{"symbol": "511010", "quantity": 20.0,
                       "cost_price": 140.0, "hold_days": 1,
                       "last_close": 140.0, "market_value_cny": 2800.0,
                       "unrealized_pnl_cny": 0.0}],
              cap, cutoff="2026-09-25", updated="y")
        out3 = build_export(paper, marks, exdir)
        ops3 = {t["trader"]: t["operations_today"] for t in out3["traders"]}
        ok &= (out3["export_date"] == "2026-09-25" and
               out3["prior_diff_source"]["date"] == "2026-09-24" and
               [o["action"] for o in ops3["T-A"]] == ["exit"] and
               ops3["T-A"][0]["symbol"] == "159980" and
               [o["action"] for o in ops3["T-B"]] == ["entry"] and
               out3["summary"]["exits_not_derivable_first_snapshot"] is False)
        # S4: marks face capture + torn-tail tolerance
        with open(os.path.join(marks, "marks-20260925.jsonl"), "w",
                  encoding="utf-8") as fh:
            fh.write(json.dumps({"ts": "t1", "kind": "intraday",
                                 "source": "sina", "traders": {
                                     "T-A": {"equity_mark_cny": 1.0}}}) + "\n")
            fh.write('{"ts": "t2", "traders": {')  # torn tail line
        out4 = build_export(paper, marks, exdir)
        mf = out4["marks_face"]
        ok &= (mf is not None and mf["ticks"] == 1 and
               mf["last_tick_ts"] == "t1" and
               mf["per_trader_equity_mark_cny"] == {"T-A": 1.0})
        # S5: marks absent -> honest null
        os.remove(os.path.join(marks, "marks-20260925.jsonl"))
        out5 = build_export(paper, marks, exdir)
        ok &= out5["marks_face"] is None
        # S6: missing capital face recorded honestly, export still lands
        st_path = os.path.join(paper, "T-B_paper.json")
        stb = _read_json(st_path)
        stb.pop("capital")
        _write_json_atomic(st_path, stb)
        out6 = build_export(paper, marks, exdir)
        ok &= ("T-B:capital" in out6["missing_faces"] and
               out6["traders"][1]["capital_cny"]["equity"] is None)
        # S7: PROSPECT isolation -- prospect dir files never picked
        os.makedirs(os.path.join(root, "prospect_paper"), exist_ok=True)
        with open(os.path.join(root, "prospect_paper",
                               "PROS-X_paper.json"), "w",
                  encoding="utf-8") as fh:
            json.dump({"trader": "PROS-X"}, fh)
        out7 = build_export(paper, marks, exdir)
        ok &= all("PROS" not in t["trader"] for t in out7["traders"])
    finally:
        shutil.rmtree(root, ignore_errors=True)
    return bool(ok)


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if "--selftest" in argv:
        ok = selftest()
        print("t35_paper_export selftest:", "PASS" if ok else "FAIL")
        return 0 if ok else 1
    return run()


if __name__ == "__main__":
    sys.exit(main())

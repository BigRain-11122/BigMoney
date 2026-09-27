"""T-2026-09-24-19 stage-2a: consolidation forward-protection guard
(paper plane, O-1325 art.2 option-a guard-style; prereg =
research/T19_STAGE2A_PAPER_FPGUARD.md, frozen pre-implementation).

Contract (prereg §2, verbatim semantics):
  C1 buy mask: registry (sym, date) cells -> False on the prices_full
     union index (P4-B2 drop semantics downstream); all-True default;
     event dates absent from the member panel index are SKIPPED and
     counted in diag (never blind-written).
  C2 sell face: UNTOUCHED (frozen negative decision -- P4-B2 sell
     deferral cannot remove the break-day jump; option-b adjusted
     panel is the eventual fix, deferred per O-1325 art.2 b).
  C3 boundary-inclusive crossing disclosure (s5 correction rides
     along: break-day close exits carried 8/10 phantom rows):
     entry_date <= event_date <= mark/exit date, BOTH ends included.
     Entry-date derivation law: price_index[-(hold_days + 1)]
     (hold_days increments once per bar iteration from first fill,
     deferral days included -- zero engine changes).
  C4 composition: buy = T-20 buy AND T-19 buy (commutes with the
     T-21 regime AND inside paper_run); sell = the SAME T-20 object.
  C5 iron laws inherited: registry is READ-ONLY (D2 lock box); fresh
     per run, no cache (T-20 build_guard idiom); anchor gate never
     receives any mask; marks/ledger/criteria untouched.

Selftest: hermetic G1-G4 (synthetic + real registry zero-drift);
wiring G5/G6 are proven by live.paper selftest + the S6 live run.
"""

import json
import os
import sys

import pandas as pd

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY_PATH = os.path.join(_REPO, "data", "consolidation", "registry.json")
SOURCE_LABEL = "t19_paper_guard (registry 21ev/19sym bit-exact, read-only)"

# Prereg-frozen synthetic fixtures (G1/G3) -- NOT registry writes.


def load_registry(path: str = REGISTRY_PATH) -> dict:
    """Fresh read each call (C5: no cache); fail-closed honest raise."""
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def build_consol_buy_mask(prices_full: dict,
                          registry: dict | None = None,
                          diag_out: dict | None = None) -> pd.DataFrame:
    """C1: boolean buy mask on the union raw index (build_guard shape).

    All True except registry event cells that exist in the member's
    panel index. Members absent from the universe are skipped (counted
    in diag); event dates absent from the member index are skipped the
    same way (never blind-written onto non-trading rows).
    """
    reg = registry if registry is not None else load_registry()
    union = sorted(set().union(*[df.index for df in prices_full.values()]))
    buy = pd.DataFrame(True, index=pd.DatetimeIndex(union),
                       columns=list(prices_full))
    events = reg.get("events", [])
    blocked = skipped_non_panel = in_universe = 0
    for ev in events:
        sym, d = ev.get("sym"), pd.Timestamp(ev.get("date"))
        if sym not in buy.columns:
            skipped_non_panel += 1
            continue
        in_universe += 1
        if d in prices_full[sym].index:
            buy.loc[d, sym] = False
            blocked += 1
        else:
            skipped_non_panel += 1
    if diag_out is not None:
        diag_out.update({
            "source": SOURCE_LABEL,
            "events_total": len(events),
            "events_in_universe": in_universe,
            "buy_blocked_days": blocked,
            "skipped_non_panel": skipped_non_panel,
        })
    return buy


def compose_fill_guard(fill_guard: tuple | dict, prices_full: dict,
                       registry: dict | None = None) -> tuple[dict, dict]:
    """C4: compose the T-19 buy face into a built T-20 guard.

    Accepts either the (guard, diag) tuple from build_guard or the
    guard dict itself. Returns (composed_guard, diag). sell is passed
    through as the SAME object (untouched, prereg C2/C4).
    """
    if isinstance(fill_guard, tuple):
        guard, t20_diag = fill_guard
    else:
        guard, t20_diag = fill_guard, {}
    diag: dict = {}
    cons = build_consol_buy_mask(prices_full, registry, diag_out=diag)
    diag["t20_totals"] = t20_diag.get("totals", {})
    composed = {"buy": guard["buy"] & cons.reindex(
        index=guard["buy"].index, columns=guard["buy"].columns).fillna(True),
        "sell": guard["sell"]}
    return composed, diag


def _entry_date(hold_days: int, price_index: pd.DatetimeIndex):
    """Prereg C3 entry-derivation law: index[-(hold_days+1)]."""
    if hold_days is None or hold_days < 0:
        return None
    pos = len(price_index) - 1 - int(hold_days)
    if pos < 0:
        return None
    return price_index[pos]


def crossing_rows(open_positions: list, price_index: pd.DatetimeIndex,
                  trades: list | None = None,
                  registry: dict | None = None) -> dict:
    """C3: boundary-inclusive crossing disclosure block (reporting-only).

    Open positions: entry <= event <= last bar (both ends in). Closed
    trades: entry <= event <= exit (the s5 8/10 break-day-exit shape
    included via the exit-side boundary day).
    """
    reg = registry if registry is not None else load_registry()
    by_sym: dict = {}
    for ev in reg.get("events", []):
        by_sym.setdefault(ev["sym"], []).append(ev)
    idx = pd.DatetimeIndex(price_index)
    rows, open_n, trade_n = [], 0, 0
    for p in open_positions or []:
        sym = p.get("symbol")
        if sym not in by_sym:
            continue
        entry = _entry_date(p.get("hold_days"), idx)
        if entry is None:
            continue
        mark = idx[-1] if len(idx) else None
        for ev in by_sym[sym]:
            d = pd.Timestamp(ev["date"])
            if entry <= d and (mark is None or d <= mark):
                open_n += 1
                rows.append({
                    "face": "open_position",
                    "symbol": sym, "event_date": ev["date"],
                    "implied_ratio_approx": ev.get("implied_ratio_approx"),
                    "pct_observed": ev.get("pct_observed"),
                    "amplitude_class": ev.get("amplitude_class"),
                    "position_entry_date": str(entry.date()),
                    "entry_to_event_bars": int(idx.get_loc(d) - idx.get_loc(entry))
                    if d in idx else None,
                })
    for tr in trades or []:
        sym = tr.get("symbol")
        if sym not in by_sym or "date" not in tr:
            continue
        exit_d = pd.Timestamp(tr["date"])
        if exit_d not in idx:
            continue
        exit_pos = idx.get_loc(exit_d)
        entry = _entry_date(tr.get("hold_days"), idx[:exit_pos + 1])
        if entry is None:
            continue
        for ev in by_sym[sym]:
            d = pd.Timestamp(ev["date"])
            if entry <= d <= exit_d:
                trade_n += 1
                rows.append({
                    "face": "closed_trade",
                    "symbol": sym, "event_date": ev["date"],
                    "implied_ratio_approx": ev.get("implied_ratio_approx"),
                    "pct_observed": ev.get("pct_observed"),
                    "amplitude_class": ev.get("amplitude_class"),
                    "position_entry_date": str(entry.date()),
                    "exit_date": str(exit_d.date()),
                })
    events_total = len(reg.get("events", []))
    return {
        "enabled": True,
        "source": SOURCE_LABEL,
        "events_total": events_total,
        "events_in_universe_n": len({p.get("symbol") for p in open_positions or []}
                                    & set(by_sym)) if open_positions else 0,
        "crossing_rows_n": len(rows),
        "crossing_rows": rows,
        "open_position_hits": open_n,
        "closed_trade_hits": trade_n,
        "semantics": "boundary-inclusive (s5): entry<=event<=mark/exit, "
                     "both ends in; buy mask no-trade per C1; sell face "
                     "untouched per C2 (option-b adjusted panel deferred "
                     "per O-1325 art.2 b)",
        "reporting_only": "marks +0, ledger +0, adjudication criteria "
                          "unchanged (T-20 deliverable-4 lineage)",
        "note": "buy_rejected_n in forward_guard may include consolidation "
                "drops when composed (C4 AND composition)",
    }


# ------------------------------------------------------------------ selftest

def _synth_panel():
    days = pd.bdate_range("2026-09-01", periods=10)
    return {"510300": pd.DataFrame({"close": [1.0] * 10}, index=days),
            "512480": pd.DataFrame({"close": [1.0] * 10}, index=days),
            "159901": pd.DataFrame({"close": [1.0] * 9}, index=days[:9])}


def _synth_registry():
    days = pd.bdate_range("2026-09-01", periods=10)
    return {"events": [
        {"sym": "512480", "date": str(days[3].date()),
         "pct_observed": -0.51, "implied_ratio_approx": 2.04,
         "amplitude_class": "consolidation_scale"},
        {"sym": "159901", "date": str(days[5].date()),
         "pct_observed": -0.50, "implied_ratio_approx": 2.01,
         "amplitude_class": "consolidation_scale"},
        {"sym": "999999", "date": str(days[3].date()),
         "pct_observed": -0.5, "implied_ratio_approx": 2.0,
         "amplitude_class": "consolidation_scale"},
        {"sym": "510300", "date": "2026-09-06",   # a Sunday: not a panel row
         "pct_observed": -0.5, "implied_ratio_approx": 2.0,
         "amplitude_class": "consolidation_scale"},
    ]}


def selftest() -> bool:
    print("  [t19fp] G1 synthetic mask exactness...", end=" ")
    panel = _synth_panel()
    reg = _synth_registry()
    diag: dict = {}
    buy = build_consol_buy_mask(panel, reg, diag_out=diag)
    days = pd.bdate_range("2026-09-01", periods=10)
    ok = (diag["events_total"] == 4 and diag["events_in_universe"] == 3
          and diag["buy_blocked_days"] == 2
          and diag["skipped_non_panel"] == 2
          and not buy.loc[days[3], "512480"]           # event cell blocked
          and not buy.loc[days[5], "159901"]
          and buy.loc[days[3], "510300"]               # non-event member
          and bool(buy["510300"].all())                # Sunday skip: no write
          and bool(buy.loc[days[:4], "512480"].iloc[:3].all()))
    print("PASS" if ok else "FAIL")
    if not ok:
        return False

    print("  [t19fp] G3 boundary-inclusive four shapes...", end=" ")
    pos_held_through = [{"symbol": "512480", "hold_days": 6}]   # entry=day3-? -> derived
    idx = pd.bdate_range("2026-09-01", periods=10)
    # entry law: index[-(h+1)]: h=6 -> days[3]; event at days[3] == entry day
    blk = crossing_rows(pos_held_through, idx, trades=[], registry=reg)
    shape1 = blk["crossing_rows_n"] == 1 and blk["crossing_rows"][0][
        "position_entry_date"] == str(days[3].date())
    # s5 8/10 shape: exit ON the break day (closed trade, hold_days 0)
    tr_exit_on_break = [{"symbol": "512480", "date": str(days[3].date()),
                         "hold_days": 0}]
    blk2 = crossing_rows([], idx, trades=tr_exit_on_break, registry=reg)
    shape2 = (blk2["crossing_rows_n"] == 1
              and blk2["crossing_rows"][0]["face"] == "closed_trade")
    # exit BEFORE the break day -> NOT flagged
    tr_exit_before = [{"symbol": "512480", "date": str(days[2].date()),
                       "hold_days": 5}]
    shape3 = crossing_rows([], idx, trades=tr_exit_before,
                          registry=reg)["crossing_rows_n"] == 0
    # entry AFTER the break day -> NOT flagged
    pos_after = [{"symbol": "512480", "hold_days": 2}]   # entry=days[7]
    shape4 = crossing_rows(pos_after, idx, trades=[],
                           registry=reg)["crossing_rows_n"] == 0
    ok = shape1 and shape2 and shape3 and shape4
    print("PASS" if ok else "FAIL")
    if not ok:
        return False

    print("  [t19fp] G2 real-registry zero-drift on paper windows...", end=" ")
    reg_real = load_registry()
    last_ev = max(pd.Timestamp(ev["date"]) for ev in reg_real["events"])
    starts = []
    tdir = os.path.join(_REPO, "firm", "traders")   # firm.hr TRADERS_DIR
    for fn in sorted(os.listdir(tdir)) if os.path.isdir(tdir) else []:
        if not fn.endswith(".json") or fn.startswith("_"):
            continue
        with open(os.path.join(tdir, fn), encoding="utf-8") as fh:
            created = json.load(fh).get("created")
        if created:
            starts.append(pd.Timestamp(created))
    ok = bool(starts) and last_ev < min(starts)
    print(f"PASS (last event {last_ev.date()} < earliest paper window "
          f"{min(starts).date() if starts else '-'})" if ok else "FAIL")
    if not ok:
        return False

    print("  [t19fp] G4 composition identity...", end=" ")
    t20_buy = pd.DataFrame(True, index=idx, columns=["510300", "512480"])
    t20_sell = pd.DataFrame(True, index=idx, columns=["510300", "512480"])
    composed, cd = compose_fill_guard(
        ({"buy": t20_buy, "sell": t20_sell}, {"totals": {"x": 1}}),
        panel, registry=reg)
    ok = (composed["sell"] is t20_sell
          and not bool(composed["buy"].loc[days[3], "512480"])
          and bool(composed["buy"].loc[days[3], "510300"])
          and cd["events_total"] == 4)
    print("PASS" if ok else "FAIL")
    return ok


if __name__ == "__main__":
    sys.exit(0 if selftest() else 1)

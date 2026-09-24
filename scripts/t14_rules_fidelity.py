"""T-2026-09-24-14 ETF rules-fidelity batch (measurement, zero registration claims).

Prereg (frozen before any run): research/ETF_RULES_FIDELITY.md (sha256 of the
frozen file is embedded in the batch JSON). Rails per prereg s4:
  A   = anchor repro at evidence_cutoff (recorded-cell reproduction, g25
        family-matrix precedent: NOT accounted) -- hard gate via
        live.paper.anchor_gate 6/6 plus byte-equality with this harness.
  B1  = fill_guard only (board-seal buy rejection / limit-down sell deferral /
        suspension double-block), runtime input, engine file untouched.
  B2  = T0 runtime patch only (159985 commodity-futures ETF treated T+0).
  B   = B1 + B2 combined.
  Bx2 = B under CostPatch(2) stressed-cost face.
  Control (unaccounted): Ax2 and B2x2 -- required by the frozen B2 landing
  gate ("B2 all 6 traders x both cost faces bit-identical to A").
Accounted runs = 6 x {B1, B2, B, Bx2} = 24 (append_ledger, prereg s4).

Guard construction rules are FROZEN in prereg s3 (P4-B2 semantics + ETF wiring):
  pct = close/prev-row close - 1 on the RAW per-symbol series (dividend
  phantom amplitudes are far below board windows for normal days; the huge
  share-consolidation artifacts are excluded BY the board-window membership
  itself -- artifact-exclusion law).
  buy=False  <=> open==high AND pct in [tier-0.5pp, tier+1.5pp]
  sell=False <=> close==low AND pct in [-tier-1.5pp, -tier+0.5pp]
  suspension: calendar day (510300 dates) inside [first,last] with no raw row
               -> buy=False AND sell=False
  missing symbol/date -> True (engine fill_guard semantics). Pre-listing
               (before first bar) -> True.
Output guard = {"buy": DF, "sell": DF} on the union panel index.

Zero-touch discipline: live/paper.py semantics, registered evidence,
scorecard, paper state, engine files -- all untouched. New outputs only:
results/rules_fidelity_t14.json + market_rules.md s11.5 disclosure row +
(optional, gated) knowledge/rules.py T0_ETF_CODES additive line.
"""
from __future__ import annotations

import contextlib
import hashlib
import json
import os
import sys

import pandas as pd

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import engine.backtester as _eb
from engine import run_backtest
from scripts.science_gates import CostPatch, append_ledger, cutoff_meta
import live.paper as LP

SCAN_PATH = os.path.join(_REPO, "results", "rules_fidelity_t14_scan.json")
OUT_PATH = os.path.join(_REPO, "results", "rules_fidelity_t14.json")
PREREG_PATH = os.path.join(_REPO, "research", "ETF_RULES_FIDELITY.md")
RULES_PATH = os.path.join(_REPO, "knowledge", "rules.py")

TIER_20 = frozenset({"159915", "159949", "588000", "588080"})  # frozen scan s2
CAL_SYM = "510300"                                            # prereg s3 calendar
TOL_LO, TOL_HI = 0.005, 0.015          # board window [tier-0.5pp, tier+1.5pp]
BREAK_MAG = 0.30                       # |pct| >= 30% = consolidation-scale day
T0_NEW = "159985"                      # Rail B2 patch target (prereg s2.3)
BATCH_TRIALS = 24                      # prereg s4 accounted grid


def _tier(sym: str) -> float:
    return 0.20 if sym in TIER_20 else 0.10


def build_guard(prices_full: dict) -> tuple[dict, dict]:
    """Frozen prereg s3 guard construction + diagnostics.

    Returns ({"buy": DF, "sell": DF}, diag). Guard DFs are indexed on the
    union raw index (== build_panels pre-ffill index), all True by default.
    """
    cal = prices_full[CAL_SYM].index
    union = sorted(set().union(*[df.index for df in prices_full.values()]))
    union_idx = pd.DatetimeIndex(union)
    buy = pd.DataFrame(True, index=union_idx, columns=list(prices_full))
    sell = pd.DataFrame(True, index=union_idx, columns=list(prices_full))
    diag = {"per_symbol": {}, "break_days": [], "totals": {}}

    for sym, df in prices_full.items():
        t = _tier(sym)
        cl, op, hi, lo = df["close"], df["open"], df["high"], df["low"]
        pct = cl / cl.shift(1) - 1.0
        first, last = df.index[0], df.index[-1]
        # board-seal masks on real rows (NaN comparisons yield False; masks
        # are fillna(False)-ed below, so NaN rows are never blocked)
        up_seal = (op == hi) & (pct >= t - TOL_LO) & (pct <= t + TOL_HI)
        dn_seal = (cl == lo) & (pct <= -(t - TOL_LO)) & (pct >= -(t + TOL_HI))
        up_days, dn_days = list(df.index[up_seal.fillna(False)]), \
            list(df.index[dn_seal.fillna(False)])
        # suspension: calendar days inside [first,last] with no raw row
        susp_days = [d for d in cal if (first <= d <= last) and d not in df.index]
        # consolidation-scale artifact days (disclosure, excluded by window)
        art = ((pct.abs() >= BREAK_MAG)).fillna(False)
        art_days = list(df.index[art])
        for d in up_days:
            buy.at[d, sym] = False
        for d in dn_days:
            sell.at[d, sym] = False
        for d in susp_days:
            buy.at[d, sym] = False
            sell.at[d, sym] = False
        diag["per_symbol"][sym] = {
            "tier": t, "bars": int(len(df)),
            "first": str(first.date()), "last": str(last.date()),
            "buy_blocked_days": len(up_days), "sell_blocked_days": len(dn_days),
            "susp_days": len(susp_days),
            "up_days": [str(d.date()) for d in up_days],
            "dn_days": [str(d.date()) for d in dn_days],
            "susp_dates": [str(d.date()) for d in susp_days],
        }
        for d in art_days:
            diag["break_days"].append({
                "sym": sym, "date": str(d.date()),
                "pct": round(float(pct.loc[d]), 4),
            })
    diag["totals"] = {
        "buy_blocked": sum(v["buy_blocked_days"] for v in diag["per_symbol"].values()),
        "sell_blocked": sum(v["sell_blocked_days"] for v in diag["per_symbol"].values()),
        "susp": sum(v["susp_days"] for v in diag["per_symbol"].values()),
        "break_days": len(diag["break_days"]),
    }
    return {"buy": buy, "sell": sell}, diag


class T0Patch:
    """Rail B2 runtime patch: treat T0_NEW as T+0 (CostPatch family pattern).

    Patches the is_t0 NAME inside engine.backtester only; knowledge/rules.py
    and engine files are untouched; name always restored on exit.
    """
    CODE = T0_NEW

    def __init__(self):
        self.orig = None

    def __enter__(self):
        self.orig = _eb.is_t0
        orig, code = self.orig, self.CODE
        _eb.is_t0 = lambda c: (c == code) or orig(c)
        return self

    def __exit__(self, *exc):
        _eb.is_t0 = self.orig
        return False


def run_rail(t: dict, prices: dict, P: dict, guard: dict | None = None,
             use_t0: bool = False, x2: bool = False) -> dict:
    """One measurement run at the anchor-repro site (prereg s4).

    Mirrors live.paper.anchor_gate's truncation/panels/patch chain exactly;
    guard/T0/x2 are the only deltas. Returns seg metrics + trades + equity.
    """
    entry = LP.SIGNAL_BUILDERS[t["params"]["entry"]](P)
    params = {k: v for k, v in t["params"].items() if k != "entry"}
    with contextlib.ExitStack() as st:
        if x2:
            st.enter_context(CostPatch(2))
        st.enter_context(LP.ExitPatch(t.get("exit_overrides")))
        if use_t0:
            st.enter_context(T0Patch())
        res = run_backtest(prices, params, entry_signal=entry,
                           exit_signal=(entry <= 0), fill_guard=guard)
    idx = P["close"].index
    eq = pd.Series(res["equity_curve"], index=idx[:len(res["equity_curve"])])
    oos = sum(1 for tr in res["trades"] if str(tr["date"]) >= LP.OOS_START)
    got = {"in_sample": {**LP.seg_metrics(eq[eq.index < LP.OOS_START]),
                         "trades": len(res["trades"]) - oos},
           "out_sample": {**LP.seg_metrics(eq, LP.OOS_START), "trades": oos}}
    return {"got": got, "trades": res["trades"], "equity": eq, "idx": idx,
            "n_entries": res["metrics"].get("num_entries")}


def _seg_clean(seg: dict) -> dict:
    """Comparable seg-metrics view (order-stable)."""
    return {k: seg[k] for k in sorted(seg)}


def _rails_equal(a: dict, b: dict) -> bool:
    return (_seg_clean(a["got"]["in_sample"]) == _seg_clean(b["got"]["in_sample"])
            and _seg_clean(a["got"]["out_sample"]) == _seg_clean(b["got"]["out_sample"])
            and a["trades"] == b["trades"])


def _break_intersections(rail: dict, break_by_sym: dict) -> list[dict]:
    """Holding-path x consolidation-break-day intersections (prereg s5).

    Uses A-rail anchor-repro trades only (zero new runs). hold_days counts
    every engine trading day a position was open, so entry_pos =
    exit_pos - hold_days on the run's own dates index (exact, incl. NaN
    suspension days which also increment hold_days).
    """
    pos_of = {d: i for i, d in enumerate(rail["idx"])}
    out = []
    for tr in rail["trades"]:
        sym, ex = tr["symbol"], tr["date"]
        if sym not in break_by_sym or ex not in pos_of:
            continue
        e_pos = pos_of[ex] - int(tr["hold_days"])
        for bd in break_by_sym[sym]:
            if bd in pos_of and e_pos <= pos_of[bd] < pos_of[ex]:
                out.append({"sym": sym, "break_date": bd, "exit_date": ex})
    return out


# ---------------------------------------------------------------- selftest

def _fixture_guard() -> tuple[dict, dict]:
    """Synthetic 2-symbol panel with frozen-prereg edge cases."""
    d = pd.bdate_range("2020-01-01", periods=6)
    cal_df = pd.DataFrame(
        {"open": [10, 10, 10, 10, 10, 10], "high": [10, 10, 10, 10, 10, 10],
         "low": [10, 10, 10, 10, 10, 10], "close": [10, 10, 10, 10, 10, 10],
         "volume": [1, 1, 1, 1, 1, 1], "amount": [10, 10, 10, 10, 10, 10]},
        index=d)
    # AAA: d0 close 100 (base); d1 +10% one-word limit-up (open==high);
    # d2 -10% one-word limit-down (close==low); d3 = missing (suspension);
    # d4 -59.6% consolidation artifact (close==low, far outside window).
    a = pd.DataFrame(
        {"open": [100.0, 110.0, 100.0, 99.0, 40.0],
         "high": [100.0, 110.0, 101.0, 99.0, 40.0],
         "low": [100.0, 110.0, 99.0, 99.0, 40.0],
         "close": [100.0, 110.0, 99.0, 99.0, 40.0],
         "volume": [1.0] * 5, "amount": [1.0] * 5},
        index=[d[0], d[1], d[2], d[4], d[5]])  # d3 intentionally absent
    b = pd.DataFrame(
        {"open": [5.0, 5.0], "high": [5.0, 5.0], "low": [5.0, 5.0],
         "close": [5.0, 5.0], "volume": [1.0, 1.0], "amount": [5.0, 5.0]},
        index=[d[3], d[4]])  # BBB lists only from d3
    return {CAL_SYM: cal_df, "AAA": a, "BBB": b}


def selftest() -> bool:
    ok = True

    def _chk(name, cond):
        nonlocal ok
        print(f"  [t14] {name}: {'PASS' if cond else 'FAIL'}")
        ok = ok and bool(cond)

    # G1 fixture: frozen s3 semantics cell-by-cell
    fx = _fixture_guard()
    g, dg = build_guard(fx)
    _chk("fixture up-seal buy-blocked d1", not g["buy"].at[fx["AAA"].index[1], "AAA"])
    _chk("fixture up-seal sell unrestricted d1", bool(g["sell"].at[fx["AAA"].index[1], "AAA"]))
    _chk("fixture dn-seal sell-blocked d2", not g["sell"].at[fx["AAA"].index[2], "AAA"])
    _chk("fixture dn-seal buy unrestricted d2", bool(g["buy"].at[fx["AAA"].index[2], "AAA"]))
    susp = fx[CAL_SYM].index[3]
    _chk("fixture suspension double-block d3", (not g["buy"].at[susp, "AAA"])
         and (not g["sell"].at[susp, "AAA"]))
    art = fx["AAA"].index[4]  # d5 row: close 40 vs prev 99 -> -0.596
    _chk("artifact day NOT sell-blocked (window law)", bool(g["sell"].at[art, "AAA"]))
    _chk("artifact day disclosed in break_days", dg["totals"]["break_days"] == 1
         and dg["break_days"][0]["sym"] == "AAA")
    pre = fx[CAL_SYM].index[0]
    _chk("pre-listing BBB cell True", bool(g["buy"].at[pre, "BBB"])
         and bool(g["sell"].at[pre, "BBB"]))
    # G2 determinism
    g2, _ = build_guard(fx)
    _chk("guard determinism (two builds identical)",
         g["buy"].equals(g2["buy"]) and g["sell"].equals(g2["sell"]))
    # G4 T0 patch in/out semantics
    with T0Patch():
        _chk("T0Patch active: 159985 T+0", _eb.is_t0("159985"))
        _chk("T0Patch active: existing T0 member intact", _eb.is_t0("511010"))
        _chk("T0Patch active: non-T0 intact", not _eb.is_t0("510300"))
    _chk("T0Patch restored: 159985 back to T+1", not _eb.is_t0("159985"))
    print(f"  [t14] selftest {'PASS' if ok else 'FAIL'}")
    return ok


# ---------------------------------------------------------------- batch run

def _load_traders() -> list[dict]:
    out = []
    tdir = LP.TRADERS_DIR
    for path in sorted(tdir.glob("*.json")):
        with open(path, encoding="utf-8-sig") as fh:
            t = json.load(fh)
        if t.get("level") != "INTERN":
            continue
        out.append(t)
    return out


def run_batch() -> int:
    print("[t14] loading core-48 + traders + frozen scan ...")
    scan = json.load(open(SCAN_PATH, encoding="utf-8"))
    traders = _load_traders()
    assert len(traders) == 6, f"expected 6 traders, got {len(traders)}"
    prices_full = LP.load_core()
    guard, diag = build_guard(prices_full)
    g2, _ = build_guard(prices_full)
    assert guard["buy"].equals(g2["buy"]) and guard["sell"].equals(g2["sell"]), \
        "guard nondeterministic"

    # counts gate (s3): board-window-filtered counts must not exceed the
    # frozen scan's loose aggregates (24 up / 42 dn incl. artifacts; susp exact)
    tot = diag["totals"]
    scan_up = sum(r["limit_up_seal_days"] for r in scan["rows"])
    scan_dn = sum(r["limit_dn_seal_days"] for r in scan["rows"])
    scan_susp = sum(r["susp_days"] for r in scan["rows"])
    assert tot["buy_blocked"] <= scan_up, (tot["buy_blocked"], scan_up)
    assert tot["sell_blocked"] <= scan_dn, (tot["sell_blocked"], scan_dn)
    assert tot["susp"] == scan_susp, (tot["susp"], scan_susp)
    print(f"[t14] guard totals: up={tot['buy_blocked']} dn={tot['sell_blocked']} "
          f"susp={tot['susp']} break_days={tot['break_days']} "
          f"(scan loose: up={scan_up} dn={scan_dn})")

    break_by_sym: dict[str, list[str]] = {}
    for b in diag["break_days"]:
        break_by_sym.setdefault(b["sym"], []).append(b["date"])

    rails = ["A", "B1", "B2", "B", "Bx2", "Ax2", "B2x2"]
    table = []
    landing_ok = True
    for t in traders:
        tid = t["id"]
        cutoff = LP.evidence_cutoff(t, prices_full)
        ps = pd.Timestamp(cutoff)
        prices = {s: df[df.index <= ps] for s, df in prices_full.items()}
        P = LP.build_panels(prices)
        res = {}
        for rail in rails:
            res[rail] = run_rail(
                t, prices, P,
                guard=(guard if rail in ("B1", "B", "Bx2") else None),
                use_t0=(rail in ("B2", "B", "Bx2", "B2x2")),
                x2=(rail in ("Bx2", "Ax2", "B2x2")))
        # hard gate: A must match registered evidence via live.paper.anchor_gate
        ag = LP.anchor_gate(t, prices_full)
        assert ag["ok"], f"anchor gate FAIL {tid}: {ag.get('error')}"
        assert _seg_clean(ag["got"]["in_sample"]) == _seg_clean(res["A"]["got"]["in_sample"]) \
            and _seg_clean(ag["got"]["out_sample"]) == _seg_clean(res["A"]["got"]["out_sample"]), \
            f"harness drift vs anchor_gate: {tid}"
        # B2 landing gate: bit-identical on both cost faces (prereg s4)
        b2_ok = (_rails_equal(res["B2"], res["A"])
                 and _rails_equal(res["B2x2"], res["Ax2"]))
        landing_ok = landing_ok and b2_ok
        # holding-path x break-day intersections from A trades (zero new runs)
        inter = _break_intersections(res["A"], break_by_sym)
        row = {"trader": tid, "cutoff": cutoff, "b2_landing_bit_identical": b2_ok,
               "break_intersections": len(inter), "break_detail": inter[:20]}
        for rail in ("A", "B1", "B2", "B", "Bx2", "Ax2", "B2x2"):
            got = res[rail]["got"]
            row[rail] = {
                "is": got["in_sample"], "oos": got["out_sample"],
                "delta_is_sharpe": round(got["in_sample"]["sharpe"]
                    - res["A"]["got"]["in_sample"]["sharpe"], 4),
                "delta_oos_sharpe": round(got["out_sample"]["sharpe"]
                    - res["A"]["got"]["out_sample"]["sharpe"], 4),
            }
        table.append(row)
        dmax = max(abs(row[r]["delta_is_sharpe"]) + abs(row[r]["delta_oos_sharpe"])
                   for r in ("B1", "B2", "B"))
        print(f"[t14] {tid}: B2_identical={b2_ok} break_x={len(inter)} "
              f"max|dSharpe|(B1/B2/B)={dmax:.4f}")

    # T0 constant landing decision (frozen gate, prereg s4)
    landed = False
    if landing_ok:
        src = open(RULES_PATH, encoding="utf-8").read()
        if f'"{T0_NEW}"' not in src:
            anchor = '    # 货币 ETF (not in our universe but listed for completeness)\n'
            assert anchor in src, "rules.py T0 block anchor not found"
            add = f'    # 商品期货 ETF (T+0, knowledge/market_rules.md s4; T-14 landed)\n    "{T0_NEW}",\n'
            src = src.replace(anchor, add + anchor)
            open(RULES_PATH, "w", encoding="utf-8", newline="\n").write(src)
        from knowledge.rules import is_t0 as _is_t0_now
        assert _is_t0_now(T0_NEW), "is_t0('159985') must be True after landing"
        landed = True
        print("[t14] T0 constant LANDED (bit-identical gate passed 6/6 x2 faces)")
    else:
        print("[t14] T0 constant NOT landed (drift found -> GM adjudication)")

    prereg_sha = hashlib.sha256(open(PREREG_PATH, "rb").read()).hexdigest()
    led = append_ledger("etf_rules_fidelity_t14", BATCH_TRIALS,
                        file_name=os.path.basename(OUT_PATH),
                        evidence_cutoff="2026-09-23",
                        note="T-14 ETF rules-fidelity measurement batch: "
                             "6x{B1,B2,B,Bx2}=24 accounted; A/Ax2/B2x2 control "
                             "runs unaccounted (recorded-cell repro + landing gate)")
    out = {
        **cutoff_meta("2026-09-23"),
        "batch": "etf_rules_fidelity_t14",
        "ticket": "T-2026-09-24-14",
        "prereg": "research/ETF_RULES_FIDELITY.md",
        "prereg_sha256": prereg_sha,
        "rails": rails,
        "accounted_runs": BATCH_TRIALS,
        "control_runs_unaccounted": 12,
        "guard_totals": tot,
        "scan_loose_totals": {"up": scan_up, "dn": scan_dn, "susp": scan_susp},
        "trials_ledger": led,
        "t0_landing": {"decision": "land" if landing_ok else "do_not_land",
                       "landed": landed,
                       "gate": "B2 bit-identical to A on both cost faces, 6/6"},
        "traders": table,
        "instruments": [
            {"sym": r["sym"], "tier": r["tier"], "t0_scan": r["t0"],
             "bars": r["bars"], "first": r["first"], "last": r["last"],
             "guard_buy_blocked": diag["per_symbol"][r["sym"]]["buy_blocked_days"],
             "guard_sell_blocked": diag["per_symbol"][r["sym"]]["sell_blocked_days"],
             "guard_susp": diag["per_symbol"][r["sym"]]["susp_days"]}
            for r in scan["rows"]],
        "break_days": diag["break_days"],
        "disclosures": {
            "F_A_board_seal": "sell-leg limit-down deferral was omitted in the "
                "unguarded default path -> registered evidence is directionally "
                "optimistic on exit liquidity; impact measured in rails B1/B.",
            "F_D_cost_v2_floor": "cost v2 (ADV-tier slippage) lacks the 5-yuan "
                "commission floor; low-value orders are undercharged under v2 "
                "faces -- disclosure only, no code change in this batch.",
            "share_consolidation": "raw sina series carries structural "
                "share-consolidation breaks (see break_days); engine keeps "
                "no consolidation adjustment -> cross-break holds embed phantom "
                "jumps; anchor-frozen evidence NOT recomputed (D2 lockbox); "
                "panel-integrity governance = new-ticket candidate; paper "
                "forward pollution risk disclosed to GM.",
            "paper_dual_rail_recommendation": "recommendation only (GM "
                "adjudication domain): wire the same guard into live/paper "
                "window runs behind an additive default-off flag so forward "
                "paper fills respect board-seal/suspension un-fillability.",
        },
    }
    with open(OUT_PATH, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print(f"[t14] batch JSON written: {OUT_PATH}")
    print(f"[t14] ledger: prev={led['prev_total']} +{led['batch_trials']} "
          f"= {led['total']}")
    return 0


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] == "selftest":
        return 0 if selftest() else 1
    if argv and argv[0] == "run":
        return run_batch()
    print("usage: t14_rules_fidelity.py [selftest|run]")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

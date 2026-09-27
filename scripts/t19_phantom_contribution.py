"""T-19 stage-2c phantom contribution quantification (T19_PHANTOM_P1 v1.0).

Prereg: research/T19_PHANTOM_P1.md (FROZEN r74a commit 79e8b1a7; seed base
68_500 registered in science_gates.SEED_REGISTRY same commit).
Ticket: fleet/tasks/T-2026-09-24-19-P1.json (bm-c lane since r48).
Deliverable: GM option-a/b adjudication EVIDENCE batch -- measurement only,
zero new members, zero ledger trials (stage-1 audit law).

  run      -> results/t19_phantom_contribution.json (+ .csv twin)
              6 baseline A-rail repros (G-REPRO bit-exact vs frozen T-14
              batch), 3 counterfactuals (buy-guard entry suppression on the
              8 disposal tranche families, engine-native fill_guard face,
              zero engine edits), 150 placebo rails (K=50 per affected
              trader, family-unit uniform sampling), row-level attribution
              (PnL + d0 gap + official-ratio true-return + h10 forward).
  selftest -> offline synthetic checks (mask construction / family-window
              union / G-SET closure / placebo determinism / disposal census
              gate) -- all green before any real run (prereg s6 law).

Honest disclosure (prereg s3): equity_fraction sizing means suppressed legs
shift the equity path -> retained trades may differ in qty/pnl while their
(symbol, date, hold_days) identity is invariant -- G-SET keys on identity and
the size-drift face is disclosed per trader, never silently swallowed.
"""
from __future__ import annotations

import json
import os
import sys
from collections import Counter

import numpy as np
import pandas as pd

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from scripts.science_gates import SEED_REGISTRY, cutoff_meta
from scripts.t14_rules_fidelity import _load_traders, _seg_clean, run_rail
import live.paper as LP

CUTOFF = "2026-09-23"
T14_BATCH = os.path.join(_REPO, "results", "rules_fidelity_t14.json")
AUDIT_PATH = os.path.join(_REPO, "results", "t19_exposure_audit.json")
REGISTRY_PATH = os.path.join(_REPO, "data", "consolidation", "registry.json")
PROBE_PATH = os.path.join(_REPO, "results", "t19_official_ratio_probe.json")
OUT_JSON = os.path.join(_REPO, "results", "t19_phantom_contribution.json")
OUT_CSV = os.path.join(_REPO, "results", "t19_phantom_contribution.csv")

K_PLACEBO = 50
# Frozen disposal census (prereg s3): 10 rows / 8 families; per-trader
# family counts CE-02=5 / CE-01=2 / DROUGHT=1 (= placebo n_k per trader).
CENSUS_ROWS, CENSUS_FAMILIES = 10, 8
N_K_BY_SUBSTR = {"CE-02": 5, "CE-01": 2, "DROUGHT": 1}


def _dk(d) -> str:
    return d.strftime("%Y-%m-%d") if hasattr(d, "strftime") else str(d)[:10]


def _trade_key(tr) -> tuple:
    """G-SET identity key: which trades happened (size drift disclosed)."""
    return (tr["symbol"], str(tr["date"])[:10], int(tr["hold_days"]))


# ------------------------------------------------------------- disposal set

def load_disposal_set() -> dict:
    """All phantom_accrued rows from the frozen stage-1 exposure audit,
    grouped into tranche families (same symbol x same entry date)."""
    audit = json.load(open(AUDIT_PATH, encoding="utf-8-sig"))
    rows = []
    for tr in audit["traders"]:
        tid = tr["trader"]
        for h in tr["break_detail"]:
            if h.get("phantom_accrued"):
                rows.append(dict(h, trader=tid, face="frozen"))
        for b in tr.get("boundary_detail", []):
            if b.get("phantom_accrued"):
                rows.append(dict(b, trader=tid, face="boundary"))
    fams: dict[tuple, list[dict]] = {}
    for r in rows:
        fams.setdefault((r["trader"], r["sym"], r["entry_date"]), []).append(r)
    assert len(rows) == CENSUS_ROWS, f"disposal census drift: {len(rows)} rows"
    assert len(fams) == CENSUS_FAMILIES, \
        f"disposal census drift: {len(fams)} families"
    n_k = {}
    for (tid, _sym, _e), _legs in fams.items():
        subs = [s for s in N_K_BY_SUBSTR if s in tid]
        assert subs, f"trader outside census substr map: {tid}"
        # longest substrate wins so DROUGHT-CE-01 maps to DROUGHT (n=1)
        # instead of its CE-01 substring, independent of dict order
        n_k[tid] = N_K_BY_SUBSTR[max(subs, key=len)]
    # exact per-trader family-count gate (5/2/1 frozen)
    by_trader = Counter(f[0] for f in fams)
    for tid, n in n_k.items():
        assert by_trader[tid] == n, \
            f"family-count drift {tid}: {by_trader[tid]} != {n}"
    return {"rows": rows, "families": fams, "n_k": n_k}


# ------------------------------------------------------- mask / family faces

def _union_index(prices: dict) -> pd.DatetimeIndex:
    return pd.DatetimeIndex(sorted(set().union(
        *[df.index for df in prices.values()])))


def buy_drop_mask(prices: dict, sym_windows: dict) -> dict:
    """Engine-native fill_guard dict: buy=False on [entry, exit) family
    windows (union per family), sell never blocked, missing -> True."""
    idx = _union_index(prices)
    buy = pd.DataFrame(True, index=idx, columns=list(prices))
    for sym, windows in sym_windows.items():
        for lo, hi in windows:
            for d in idx[(idx >= pd.Timestamp(lo)) & (idx < pd.Timestamp(hi))]:
                buy.at[d, sym] = False
    sell = pd.DataFrame(True, index=idx, columns=list(prices))
    return {"buy": buy, "sell": sell}


def _entry_dates(rail: dict) -> dict:
    """Derived entry date per trade key (audit semantics: exit_pos -
    hold_days on the run's own index, suspension-inclusive)."""
    pos_of = {_dk(d): i for i, d in enumerate(rail["idx"])}
    out = {}
    for tr in rail["trades"]:
        ex = str(tr["date"])[:10]
        out[_trade_key(tr)] = _dk(rail["idx"][pos_of[ex] - int(tr["hold_days"])])
    return out


def family_windows(rail: dict, fams: dict, trader: str) -> dict:
    """symbol -> [(lo, hi), ...] window union over the family's legs."""
    ent = _entry_dates(rail)
    sym_windows: dict[str, list] = {}
    for (tid, sym, entry), legs in fams.items():
        if tid != trader:
            continue
        for r in legs:
            sym_windows.setdefault(sym, []).append((r["entry_date"],
                                                    r["exit_date"]))
    return sym_windows


def _legs_of(rail: dict, trader_fams: list) -> list[dict]:
    """All baseline trade records belonging to the given families."""
    ent = _entry_dates(rail)
    legs = []
    for tr in rail["trades"]:
        if (tr["symbol"], ent[_trade_key(tr)]) in trader_fams:
            legs.append(tr)
    return legs


def g_set_check(base_rail: dict, cf_rail: dict, removed_legs: list[dict]) -> dict:
    """Hard gate: counterfactual trade LIST == baseline LIST - family closure
    (multiset on identity keys, no extra, no missing)."""
    cb = Counter(_trade_key(t) for t in base_rail["trades"])
    cc = Counter(_trade_key(t) for t in cf_rail["trades"])
    expect = Counter(_trade_key(t) for t in removed_legs)
    diff, extra = cb - cc, cc - cb
    ok = (diff == expect) and not extra
    # size-drift face (equity_fraction compounding): retained trades whose
    # qty/pnl differ while identity matches -- disclosed, never a gate input
    bmap = {}
    for t in base_rail["trades"]:
        bmap.setdefault(_trade_key(t), []).append(t)
    cmap = {}
    for t in cf_rail["trades"]:
        cmap.setdefault(_trade_key(t), []).append(t)
    drift = sum(1 for k, ts in bmap.items()
                for a, b in zip(ts, cmap.get(k, []))
                if a.get("qty") != b.get("qty") or a.get("pnl") != b.get("pnl"))
    return {"ok": ok, "missing_beyond_expected": list(diff - expect)
            if ok is False else [], "extra": list(extra),
            "size_drift_rows": drift}


def _delta(base: dict, cf: dict) -> dict:
    d = {}
    for seg in ("in_sample", "out_sample"):
        b, c = base[seg], cf[seg]
        d[seg] = {"d_sharpe": round(c["sharpe"] - b["sharpe"], 4),
                  "d_annual_return": round(c["annual_return"]
                                           - b["annual_return"], 4),
                  "d_max_drawdown": round(c["max_drawdown"] - b["max_drawdown"],
                                          4),
                  "d_trades": c["trades"] - b["trades"]}
    return d


# --------------------------------------------------------------- main faces

def _affected_traders(disposal: dict) -> list[str]:
    return sorted(disposal["n_k"])


def _baseline(t, prices_full, frozen_rows) -> dict:
    cutoff = LP.evidence_cutoff(t, prices_full)
    ps = pd.Timestamp(cutoff)
    prices = {s: df[df.index <= ps] for s, df in prices_full.items()}
    P = LP.build_panels(prices)
    rail = run_rail(t, prices, P)
    ag = LP.anchor_gate(t, prices_full)
    assert ag["ok"], f"anchor gate FAIL {t['id']}: {ag.get('error')}"
    a_ok = (_seg_clean(rail["got"]["in_sample"])
            == _seg_clean(frozen_rows[t["id"]]["A"]["is"])
            and _seg_clean(rail["got"]["out_sample"])
            == _seg_clean(frozen_rows[t["id"]]["A"]["oos"]))
    assert a_ok, f"G-REPRO drift vs frozen T-14 A face: {t['id']}"
    return {"cutoff": cutoff, "prices": prices, "P": P, "rail": rail}


def _null_band(vals: np.ndarray, actual: float) -> dict:
    p5, p95 = (round(float(np.percentile(vals, 5)), 4),
               round(float(np.percentile(vals, 95)), 4))
    pct = round(100.0 * float(np.mean(vals <= actual)), 2)
    outside = bool(actual < p5 or actual > p95)
    return {"mu": round(float(np.mean(vals)), 4),
            "sigma": round(float(np.std(vals, ddof=1)), 4) if len(vals) > 1
            else None,
            "p5": p5, "p95": p95, "actual_percentile": pct,
            "readout": "phantom_beyond_family_removal_noise" if outside
            else "within_family_removal_noise"}


def run() -> int:
    seed = SEED_REGISTRY["t19_phantom_p1"]
    assert isinstance(seed, int), "seed must be int (SEED_REGISTRY)"
    disposal = load_disposal_set()
    reg = json.load(open(REGISTRY_PATH, encoding="utf-8-sig"))
    reg_ev = {e["sym"] + "@" + e["date"]: e for e in reg["events"]}
    probe = json.load(open(PROBE_PATH, encoding="utf-8-sig"))
    pr_ev = {r["sym"] + "@" + r["date"]: r for r in probe["results"]}
    frozen = json.load(open(T14_BATCH, encoding="utf-8-sig"))
    rows_f = {r["trader"]: r for r in frozen["traders"]}
    prices_full = LP.load_core()

    affected = _affected_traders(disposal)
    out_traders, out_rows, rails = [], [], 0
    ss = np.random.SeedSequence(seed)

    for t in _load_traders():
        tid = t["id"]
        base = _baseline(t, prices_full, rows_f)
        rail = base["rail"]
        rails += 1
        block = {"trader": tid, "cutoff": base["cutoff"],
                 "baseline": {"in_sample": rail["got"]["in_sample"],
                              "out_sample": rail["got"]["out_sample"]},
                 "g_repro": "PASS (bit-exact vs frozen T-14 A face)",
                 "families_disposed": 0, "counterfactual": None,
                 "delta": None, "placebo": None, "size_drift_rows": None}
        if tid in affected:
            n_k = disposal["n_k"][tid]
            trader_fams = [k for k in disposal["families"] if k[0] == tid]
            fam_keys = [(sym, entry) for (_t, sym, entry) in trader_fams]
            legs = _legs_of(rail, fam_keys)
            mask = buy_drop_mask(base["prices"],
                                 family_windows(rail, disposal["families"],
                                                tid))
            cf = run_rail(t, base["prices"], base["P"], guard=mask)
            rails += 1
            gs = g_set_check(rail, cf, legs)
            assert gs["ok"], f"G-SET FAIL {tid}: {gs}"
            block["families_disposed"] = len(trader_fams)
            block["counterfactual"] = {"in_sample": cf["got"]["in_sample"],
                                       "out_sample": cf["got"]["out_sample"]}
            block["delta"] = _delta(rail["got"], cf["got"])
            block["size_drift_rows"] = gs["size_drift_rows"]

            # placebo: family-unit uniform sampling from non-disposal
            # families of this trader's reproduced trade list (prereg s3)
            ent = _entry_dates(rail)
            pool_fams = sorted({(tr["symbol"], ent[_trade_key(tr)])
                                for tr in rail["trades"]
                                if (tr["symbol"], ent[_trade_key(tr)])
                                not in fam_keys})
            assert len(pool_fams) >= n_k, \
                f"placebo pool too small {tid}: {len(pool_fams)} < {n_k}"
            rng = np.random.default_rng(ss.spawn(1)[0])
            draws = [rng.choice(len(pool_fams), size=n_k, replace=False)
                     for _ in range(K_PLACEBO)]
            pl_is, pl_oos = [], []
            for draw in draws:
                sampled = [pool_fams[i] for i in draw]
                sym_w: dict[str, list] = {}
                for tr in rail["trades"]:
                    if (tr["symbol"], ent[_trade_key(tr)]) in sampled:
                        sym_w.setdefault(tr["symbol"], []).append(
                            (ent[_trade_key(tr)], str(tr["date"])[:10]))
                mask_p = buy_drop_mask(base["prices"], sym_w)
                cf_p = run_rail(t, base["prices"], base["P"], guard=mask_p)
                rails += 1
                gsp = g_set_check(rail, cf_p, _legs_of(rail, sampled))
                assert gsp["ok"], f"G-SET FAIL placebo {tid}: {gsp}"
                d = _delta(rail["got"], cf_p["got"])
                pl_is.append(d["in_sample"]["d_sharpe"])
                pl_oos.append(d["out_sample"]["d_sharpe"])
            block["placebo"] = {
                "k": K_PLACEBO, "n_k": n_k, "pool_families": len(pool_fams),
                "is_sharpe": _null_band(np.array(pl_is),
                                        block["delta"]["in_sample"]
                                        ["d_sharpe"]),
                "oos_sharpe": _null_band(np.array(pl_oos),
                                         block["delta"]["out_sample"]
                                         ["d_sharpe"]),
                "asymmetry_note": ("placebo families are mostly single-leg; "
                                   "the real disposal set contains a 3-leg "
                                   "family -> placebo row count <= actual "
                                   "(conservative face, prereg s3)"),
            }
            for r in [x for x in disposal["rows"] if x["trader"] == tid]:
                legs_r = [x for x in legs
                         if x["symbol"] == r["sym"]
                         and str(x["date"])[:10] == r["exit_date"]]
                leg = legs_r[0] if legs_r else None
                ev = reg_ev.get(r["sym"] + "@" + r["break_date"], {})
                pr = pr_ev.get(r["sym"] + "@" + r["break_date"], {})
                prev_close = ev.get("prev_close")
                pct = ev.get("pct_observed")
                d0_y = (round(leg["qty"] * prev_close * pct, 2)
                        if leg and prev_close and pct is not None else None)
                nav = (pr.get("nav_leg") or {})
                true_ret = (round(pr["price_implied_ratio"]
                                  * nav["nav_step_ratio"] - 1.0, 6)
                            if pr and nav.get("status") == "ok" else None)
                true_y = (round(leg["qty"] * prev_close * true_ret, 2)
                          if leg and prev_close and true_ret is not None
                          else None)
                close_s = base["prices"][r["sym"]]["close"]
                pos = close_s.index.get_loc(pd.Timestamp(r["break_date"])) \
                    if r["break_date"] in close_s.index else None
                h10 = (round(float(close_s.iloc[pos + 10]
                                   / close_s.iloc[pos]) - 1.0, 6)
                       if pos is not None and pos + 10 < len(close_s)
                       else None)
                out_rows.append({
                    "trader": tid, "sym": r["sym"], "face": r["face"],
                    "entry_date": r["entry_date"], "exit_date":
                        r["exit_date"], "break_date": r["break_date"],
                    "leg_pnl": leg.get("pnl") if leg else None,
                    "leg_pnl_rate": leg.get("pnl_rate") if leg else None,
                    "leg_qty": leg.get("qty") if leg else None,
                    "raw_d0_pct": pct, "d0_gap_component_yuan": d0_y,
                    "official_true_d0_ret": true_ret,
                    "true_return_component_yuan": true_y,
                    "reconciliation_ratio_space":
                        pr.get("reconciliation"),
                    "official_verdict": pr.get("verdict"),
                    "h10_forward_ret_raw": h10,
                })
        else:
            block["delta"] = {"in_sample": {"d_sharpe": 0.0,
                                            "d_annual_return": 0.0,
                                            "d_max_drawdown": 0.0,
                                            "d_trades": 0},
                              "out_sample": {"d_sharpe": 0.0,
                                             "d_annual_return": 0.0,
                                             "d_max_drawdown": 0.0,
                                             "d_trades": 0}}
            block["g_repro"] += " | structural-zero delta (zero exposure)"
        out_traders.append(block)
        print(f"[t19c] {tid}: G-REPRO PASS, families="
              f"{block['families_disposed']}, rails={rails}")

    out = {
        **cutoff_meta(CUTOFF),
        "batch": "t19_phantom_contribution",
        "prereg": "research/T19_PHANTOM_P1.md v1.0 (frozen r74a 79e8b1a7)",
        "ticket": "T-2026-09-24-19", "stage": "2c",
        "seed": {"base": seed, "registry_key": "t19_phantom_p1",
                 "law": "SEED_REGISTRY same-commit registration (s3)"},
        "disposal_set": {"rows": CENSUS_ROWS, "families": CENSUS_FAMILIES,
                         "per_trader_families": disposal["n_k"]},
        "cost_face": "V1 legacy 13bp x2 (registered-anchor repro law)",
        "counterfactual_semantics": (
            "option-a operationalized as engine-native buy-guard entry "
            "suppression over family-window unions (fill_guard face, zero "
            "engine edits); NOT ledger row surgery -- equity_fraction "
            "compounding makes post-hoc row removal ill-defined (s3)"),
        "gates": {"G_REPRO": "PASS 6/6 (bit-exact frozen T-14 A faces)",
                  "G_SET": "PASS (actual 3 + placebo 150 closures exact)",
                  "null_band_readout": "descriptive two-state, no "
                                       "pass/fail strategy narrative"},
        "traders": out_traders,
        "rows": out_rows,
        "audit": {"ledger_trials_added": 0, "rails_run": rails,
                  "k_placebo": K_PLACEBO},
    }
    with open(OUT_JSON, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    _write_csv(out)
    print(f"[t19c] written: {OUT_JSON} (rails={rails}, rows={len(out_rows)})")
    return 0


def _write_csv(out: dict) -> None:
    lines = ["trader,seg,d_sharpe,d_annual_return,d_max_drawdown,d_trades,"
             "placebo_readout_is,placebo_readout_oos"]
    for b in out["traders"]:
        for seg in ("in_sample", "out_sample"):
            d = b["delta"][seg]
            pl = b.get("placebo") or {}
            lines.append(",".join(str(x) for x in (
                b["trader"], seg, d["d_sharpe"], d["d_annual_return"],
                d["d_max_drawdown"], d["d_trades"],
                (pl.get("is_sharpe") or {}).get("readout", "")
                if seg == "in_sample" else "",
                (pl.get("oos_sharpe") or {}).get("readout", "")
                if seg == "out_sample" else "")))
    lines.append("")
    lines.append("trader,sym,face,entry_date,exit_date,break_date,leg_pnl,"
                 "leg_pnl_rate,leg_qty,raw_d0_pct,d0_gap_component_yuan,"
                 "official_true_d0_ret,true_return_component_yuan,"
                 "reconciliation_ratio_space,official_verdict,"
                 "h10_forward_ret_raw")
    for r in out["rows"]:
        lines.append(",".join(str(r.get(k)) for k in (
            "trader", "sym", "face", "entry_date", "exit_date", "break_date",
            "leg_pnl", "leg_pnl_rate", "leg_qty", "raw_d0_pct",
            "d0_gap_component_yuan", "official_true_d0_ret",
            "true_return_component_yuan", "reconciliation_ratio_space",
            "official_verdict", "h10_forward_ret_raw")))
    with open(OUT_CSV, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")


# ---------------------------------------------------------------- selftest

def selftest() -> bool:
    ok = True

    def _chk(name, cond):
        nonlocal ok
        print(f"  [t19c] {name}: {'PASS' if cond else 'FAIL'}")
        ok = ok and bool(cond)

    days = pd.bdate_range("2026-01-01", periods=8)
    px = {"AAA": pd.DataFrame({"close": [10.0] * 8}, index=days),
          "BBB": pd.DataFrame({"close": [5.0] * 8}, index=days)}
    # S1 mask construction: buy blocked exactly on [entry, exit) window
    m = buy_drop_mask(px, {"AAA": [("2026-01-05", "2026-01-08")]})
    blocked = [str(d.date()) for d in m["buy"].index
               if not m["buy"].at[d, "AAA"]]
    _chk("mask blocks [entry, exit) exactly",
         blocked == ["2026-01-05", "2026-01-06", "2026-01-07"])
    _chk("sell never blocked", bool(m["sell"].all().all()))
    _chk("other symbol untouched", bool(m["buy"]["BBB"].all()))
    # S2 family-window union: two legs overlapping
    m2 = buy_drop_mask(px, {"AAA": [("2026-01-05", "2026-01-07"),
                                    ("2026-01-06", "2026-01-09")]})
    blocked2 = {str(d.date()) for d in m2["buy"].index
                if not m2["buy"].at[d, "AAA"]}
    _chk("window union over legs",
         blocked2 == {"2026-01-05", "2026-01-06", "2026-01-07",
                      "2026-01-08"})
    # S3 G-SET closure: counterfactual == baseline - family legs
    rail_b = {"idx": days, "trades": [
        {"symbol": "AAA", "date": "2026-01-07", "hold_days": 2, "qty": 1.0,
         "pnl": 1.0},
        {"symbol": "AAA", "date": "2026-01-08", "hold_days": 3, "qty": 1.0,
         "pnl": 2.0},
        {"symbol": "BBB", "date": "2026-01-08", "hold_days": 1, "qty": 1.0,
         "pnl": 0.5}]}
    rail_c = {"idx": days, "trades": [
        {"symbol": "AAA", "date": "2026-01-08", "hold_days": 3, "qty": 1.0,
         "pnl": 2.0},
        {"symbol": "BBB", "date": "2026-01-08", "hold_days": 1, "qty": 1.0,
         "pnl": 0.5}]}
    gs = g_set_check(rail_b, rail_c, [rail_b["trades"][0]])
    _chk("G-SET passes exact closure", gs["ok"])
    gs_bad = g_set_check(rail_b, rail_c, [])
    _chk("G-SET catches unexplained removal", not gs_bad["ok"])
    gs_extra = g_set_check(rail_b, {"idx": days, "trades":
                                    rail_c["trades"]
                                    + [{"symbol": "CCC", "date": "2026-01-08",
                                        "hold_days": 1, "qty": 1, "pnl": 0}]},
                            [rail_b["trades"][0]])
    _chk("G-SET catches extra trades", not gs_extra["ok"])
    _chk("size drift counted, not gated",
         g_set_check(rail_b, {"idx": days, "trades": [
             {"symbol": "AAA", "date": "2026-01-08", "hold_days": 3,
              "qty": 9.0, "pnl": 9.0},
             {"symbol": "BBB", "date": "2026-01-08", "hold_days": 1,
              "qty": 1.0, "pnl": 0.5}]},
             [rail_b["trades"][0]])["ok"])
    # S4 placebo determinism: same seed -> same draws; disposal excluded
    rng = np.random.default_rng(np.random.SeedSequence(68500).spawn(1)[0])
    pool = [("A", "e1"), ("B", "e2"), ("C", "e3"), ("D", "e4"), ("E", "e5")]
    d1 = [tuple(rng.choice(len(pool), size=2, replace=False))
          for _ in range(3)]
    rng2 = np.random.default_rng(np.random.SeedSequence(68500).spawn(1)[0])
    d2 = [tuple(rng2.choice(len(pool), size=2, replace=False))
          for _ in range(3)]
    _chk("placebo draws deterministic", d1 == d2)
    _chk("placebo draw = distinct-family subset",
         all(len(set(d)) == 2 for d in d1))
    # S5 derived-entry semantics mirrors audit (exit_pos - hold_days)
    ent = _entry_dates(rail_b)
    _chk("entry derivation: hold 2 exit 01-07 -> 01-05",
         ent[("AAA", "2026-01-07", 2)] == "2026-01-05")
    # S6 disposal census gate fires on drift (synthetic audit)
    import tempfile
    fake = {"traders": [{"trader": "X-CE-02", "break_detail": [
        {"sym": "A", "break_date": "2026-01-06", "exit_date": "2026-01-07",
         "entry_date": "2026-01-05", "phantom_accrued": True}],
        "boundary_detail": []}]}
    global AUDIT_PATH
    with tempfile.NamedTemporaryFile("w", suffix=".json",
                                     delete=False, encoding="utf-8") as fh:
        json.dump(fake, fh)
        tmp = fh.name
    orig, AUDIT_PATH = AUDIT_PATH, tmp
    try:
        try:
            load_disposal_set()
            fired = False
        except AssertionError:
            fired = True
        _chk("disposal census gate fires on drift", fired)
    finally:
        AUDIT_PATH = orig
        os.unlink(tmp)
    # S6b happy path: census-shaped fixture (10 rows / 8 families / 5-2-1)
    # must load and yield the frozen n_k map (regression for assignment bug
    # r76: n_k was never assigned n, gate failed on correct real data)
    ce02 = [{"sym": "S1", "entry_date": "2026-01-05",
             "exit_date": f"2026-01-1{d}", "phantom_accrued": True}
            for d in (2, 3, 4)]
    ce02 += [{"sym": f"S{k}", "entry_date": "2026-01-05",
              "exit_date": "2026-01-20", "phantom_accrued": True}
             for k in (2, 3, 4, 5)]
    fake_ok = {"traders": [
        {"trader": "COMPOSITE-CE-02", "break_detail": ce02,
         "boundary_detail": []},
        {"trader": "COMPOSITE-CE-01", "break_detail": [
            {"sym": "S6", "entry_date": "2026-01-05",
             "exit_date": "2026-01-20", "phantom_accrued": True},
            {"sym": "S7", "entry_date": "2026-01-05",
             "exit_date": "2026-01-20", "phantom_accrued": True}],
         "boundary_detail": []},
        {"trader": "DROUGHT-CE-01", "break_detail": [], "boundary_detail": [
            {"sym": "S8", "entry_date": "2026-01-05",
             "exit_date": "2026-01-20", "phantom_accrued": True}]}]}
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False,
                                     encoding="utf-8") as fh:
        json.dump(fake_ok, fh)
        tmp_ok = fh.name
    orig, AUDIT_PATH = AUDIT_PATH, tmp_ok
    try:
        d = load_disposal_set()
        _chk("census happy path yields frozen n_k 5/2/1",
             d["n_k"] == {"COMPOSITE-CE-02": 5, "COMPOSITE-CE-01": 2,
                          "DROUGHT-CE-01": 1})
    finally:
        AUDIT_PATH = orig
        os.unlink(tmp_ok)
    print(f"  [t19c] selftest {'PASS' if ok else 'FAIL'}")
    return ok


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] == "selftest":
        return 0 if selftest() else 1
    if argv and argv[0] == "run":
        return run()
    print("usage: t19_phantom_contribution.py [run|selftest]")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

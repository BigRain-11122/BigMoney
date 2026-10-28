"""One book, four published annualised numbers -- which one does the executable ticket earn?

The ETF composite book has been published at, over the same 2020-01..cutoff window:

    9.62%  results/etf_book_spanning.json        (card config: 12 names, 8% vol target, 10bp)
    7.80%  results/etf_book_capacity_rule.json   (rule arm, no size limit: 5 names, beta 0.20, 8bp)
    7.38%  same face, NAV = 1e6                  (5 names, beta 0.20, 8bp + impact at 1M)
    7.28%  same face, CAGR at the 1%-ADV ceiling (NAV 1.53M, the worst tier of that ladder)

r1319 called the 9.62 -> 7.28 distance an UNATTRIBUTED "run diff" and, worse, priced the
book at 7.28 in every capital tier -- including tiers far below the ceiling, where impact
barely binds. That charges a capacity cost that does not exist yet AND credits the book
with a rule it does not trade: the executable order sheet (ORDER-<asof>.md) is 5 names
with a 0.20 beta cover, while the card headline is the 12-name 8%-vol-target book.

This face answers the decision-relevant question instead: run CARD and TICKET on ONE
stack (same panel, same fill engine, same window) so the distance between the published
numbers becomes knobs rather than mystery. It builds a 2 (width) x 3 (risk rule) x
2 (cost) grid = 12 cells on the production stack, and the same grid on the capacity
face's own stack (raw panel + next_open engine) as a reproduction control.

Knob semantics, so a term can never be read as something else:
  width  n_hold 12 -> 5           fewer names, same rule
  rule   vol 0.08 -> beta 0.20    scale by realised book vol vs scale to a market beta
  cost   10bp -> 8bp              per-side, no impact term (impact is a size question and
                                  it lives in etf_book_capacity_rule, not here)

Decomposition is published as a forward path, a reverse path, AND per-knob marginals
measured from each endpoint, because r1291 already proved the order matters: when the
two ends disagree the honest reading is the interaction term, not one path.

Evidence: results/etf_book_cagr_reconcile.json. Selftest runs on fixtures (no engine).
"""
import argparse
import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import etf_book_production as P          # noqa: E402
import etf_composite_pf as F             # noqa: E402
import etf_equity_alpha as A             # noqa: E402
import etf_phase_beta_target as BT       # noqa: E402
import etf_phase_beta_window as BW       # noqa: E402
import etf_robust_pf as R                # noqa: E402
import etf_book_capacity_rule as CR      # noqa: E402

RESULT = os.path.join(ROOT, "results", "etf_book_cagr_reconcile.json")
SPANNING = os.path.join(ROOT, "results", "etf_book_spanning.json")
CAPACITY = os.path.join(ROOT, "results", "etf_book_capacity_rule.json")

REBAL = 20
WIDTHS = (12, 5)
RULES = ("flat", "vol08", "beta020")
COSTS = (10.0, 8.0)
VOL_TARGET = 0.08
TARGET_BETA = 0.20
CARD = (12, "vol08", 10.0)
TICKET = (5, "beta020", 8.0)


# ---------------------------------------------------------------------------- fixtures
def _cell_key(stack, n, rule, cost):
    return "%s|n%d|%s|%gbp" % (stack, n, rule, cost)


def decompose(cells, start, end, order):
    """Waterfall over `order` from `start` to `end`; returns per-step pp and the total.

    `cells` is keyed by (n, rule, cost). Pure arithmetic -- fixtures pin it.
    """
    state = tuple(start)
    path = []
    for ax, target in order:
        nxt = list(state)
        idx = {"width": 0, "rule": 1, "cost": 2}[ax]
        nxt[idx] = target[idx]
        nxt = tuple(nxt)
        path.append({"knob": ax, "from": _fmt_cfg(state), "to": _fmt_cfg(nxt),
                     "delta_pp": round(100.0 * (cells[nxt] - cells[state]), 4)})
        state = nxt
    if state != tuple(end):
        raise ValueError("path does not land on the end cell")
    total = 100.0 * (cells[tuple(end)] - cells[tuple(start)])
    return {"order": [ax for ax, _ in order], "steps": path,
            "total_pp": round(total, 4),
            "sum_pp": round(sum(s["delta_pp"] for s in path), 4)}


def marginals(cells, origin, target):
    """One-knob-at-a-time move from `origin` TOWARD the other endpoint.

    Each axis is stepped to the target cell's value with the other two held at `origin`,
    keyed by knob name. This is the move actually taken on that axis, so the sum over
    axes is comparable to the total and the difference is the interaction.
    """
    out = {}
    base = cells[tuple(origin)]
    for ax, idx in (("width", 0), ("rule", 1), ("cost", 2)):
        nxt = list(origin)
        nxt[idx] = target[idx]
        if tuple(nxt) == tuple(origin):
            continue
        out[ax] = round(100.0 * (cells[tuple(nxt)] - base), 4)
    return out


def _alts(cfg, idx):
    vals = {0: WIDTHS, 1: RULES, 2: COSTS}[idx]
    return [v for v in vals if v != cfg[idx]]


def _val_label(v):
    if isinstance(v, float):
        return "%gbp" % v
    return str(v)


def _fmt_cfg(cfg):
    return "n%d/%s/%gbp" % (cfg[0], cfg[1], cfg[2])


def knob_means(marg):
    """Kept as a named helper so a knob count of one delta each is explicit."""
    return {ax: round(float(v), 4) for ax, v in marg.items()}


def interaction(total_pp, marg_from_start, marg_from_end):
    """What the single-knob readings do NOT explain.

    interaction_from_start = total - sum(one-at-a-time moves off the start cell);
    interaction_from_end   = -total - sum(moves off the end cell back toward the start),
    because that reverse trip sums to -total in an additive grid, not to +total. Both are
    printed; `interaction_pp` is their mean, which equals -mean(sum_start, sum_end).
    """
    ks, ke = knob_means(marg_from_start), knob_means(marg_from_end)
    s, e = sum(ks.values()), sum(ke.values())
    return {"knob_marginals_from_start_pp": ks, "knob_marginals_from_end_pp": ke,
            "sum_knob_marginals_from_start_pp": round(s, 4),
            "sum_knob_marginals_from_end_pp": round(e, 4),
            "interaction_from_start_pp": round(total_pp - s, 4),
            "interaction_from_end_pp": round(-total_pp - e, 4),
            "interaction_pp": round(-0.5 * (s + e), 4)}


# ------------------------------------------------------------------------------- engines
def _stats(ser, label):
    m = A.stats2(ser.dropna(), label)
    return {k: m.get(k) for k in ("cagr", "sharpe", "maxdd", "vol", "years")}


def open_open(close, openp, amt, score, n, cost_bp, vol_target=None):
    ser, _turn = R.open_to_open_equity(close, openp, amt, score, REBAL, n,
                                       cost_bp / 1e4, vol_target=vol_target)
    return ser.dropna()


def _raw_face(n_hold, start="2020-01-01"):
    """Capacity-face stack: raw panel + next-open engine, gross, fills recorded.

    Mirrors etf_book_capacity_rule.build_face line for line except that `n_hold` is a
    parameter -- that face hardcodes the engine default so it can only ever price 5
    names, which is exactly why the width knob could not be measured before. The n=5
    cell is asserted against the published face in `run()` so the mirror cannot drift.
    """
    close, openp, amt, feats = F.build_panel()
    score = F.build_score(close, amt, feats)
    rec = CR.Recorder()
    gross, turn, gapfill = F.run_next_open(close, openp, amt, feats, REBAL,
                                           n_hold=n_hold, cost=rec, start=start,
                                           score=score)
    mkt_col = next((c for c in BT.MKT if c in close.columns), None)
    if mkt_col is None:
        raise SystemExit("FATAL: no 510300 column on the panel")
    mkt = close[mkt_col]
    idx = gross.index.intersection(mkt.index)
    rp = gross.reindex(idx).pct_change().fillna(0.0)
    rm = mkt.reindex(idx).pct_change().fillna(0.0)
    sched = BT.k_schedule(rp, rm, TARGET_BETA)
    k_ser = CR._applied_k(sched, rp.index).reindex(rp.index)
    rf, rf_missing = BW.repo_daily_cash(rp.index, BW.load_repo_rates())
    rf = rf.reindex(rp.index).fillna(0.0)
    return {"close": close, "amt": amt, "idx": idx, "rp": rp, "rm": rm,
            "sched": sched, "k": k_ser, "rf": rf, "rf_missing": rf_missing,
            "fills": rec.fills, "rebal_turnover": turn, "gapfill": gapfill,
            "market": mkt, "mkt_col": mkt_col}


def raw_cell(face, n, rule, cost_bp):
    if rule == "flat":
        ser, _rows, _cnt = CR.curve(face, 1e9, k_bp=0.0, base_bp=cost_bp, k_override=1.0)
    elif rule == "beta020":
        ser, _rows, _cnt = CR.curve(face, 1e9, k_bp=0.0, base_bp=cost_bp)
    else:
        raise ValueError("raw stack has no %s rule" % rule)
    return ser.dropna()


def beta_on_prod(ser_flat, mkt, cost_bp, target=TARGET_BETA):
    """Apply the beta cover to a production-stack flat series (the capacity face's own
    mechanism: causal expanding beta, cash leg at observed repo, cost on each de-lever)."""
    rp = ser_flat.pct_change().fillna(0.0)
    idx = rp.index.intersection(mkt.index)
    rp, rm = rp.reindex(idx), mkt.reindex(idx).pct_change().fillna(0.0)
    sched = BT.k_schedule(rp, rm, target)
    rf, _missing = BW.repo_daily_cash(rp.index, BW.load_repo_rates())
    rf = rf.reindex(rp.index).fillna(0.0)
    out, _bench, _k = BT.apply_overlay(rp, rm, sched, cash_ann=0.0, cost_bp=cost_bp, rf=rf)
    if out is None:
        raise SystemExit("FATAL: beta overlay produced no series")
    return out.dropna()


# ---------------------------------------------------------------------------------- run
def run(write=True):
    out = {"schema": "etf_book_cagr_reconcile/v1", "ts": _now(),
           "script": "scripts/etf_book_cagr_reconcile.py"}
    close, openp, amt, score, cls, n_flip = P.prep_panel()
    out["panel"] = {"stack": "production (repair_flips + class filter)",
                    "universe": int(len(close.columns)), "flips_repaired": int(n_flip),
                    "last_bar": str(close.index[-1].date())}
    mkt_col = next((c for c in BT.MKT if c in close.columns), None)
    if mkt_col is None:
        raise SystemExit("FATAL: no 510300 column on the production panel")
    mkt = close[mkt_col]

    print("grid: production stack (%d cells) ..." % (len(WIDTHS) * 2 * 2), flush=True)
    prod = {}
    for n in WIDTHS:
        for cost in COSTS:
            flat = open_open(close, openp, amt, score, n, cost, None)
            vol = open_open(close, openp, amt, score, n, cost, VOL_TARGET)
            beta = beta_on_prod(flat, mkt, cost)
            for rule, ser in (("flat", flat), ("vol08", vol), ("beta020", beta)):
                prod[(n, rule, cost)] = ser
                print("  " + _cell_key("prod", n, rule, cost), flush=True)

    print("grid: capacity-face stack (raw panel + next-open engine) ...", flush=True)
    raw = {}
    raw_faces = {}
    for n in WIDTHS:
        face = _raw_face(n)
        raw_faces[n] = face
        for cost in COSTS:
            for rule in ("flat", "beta020"):
                raw[(n, rule, cost)] = raw_cell(face, n, rule, cost)
                print("  " + _cell_key("raw", n, rule, cost), flush=True)

    def table(cells):
        row = {}
        for (n, rule, cost), ser in cells.items():
            stats = _stats(ser, _cell_key("", n, rule, cost).lstrip("|"))
            row[repr((n, rule, cost))] = dict(stats, n_hold=n, rule=rule, cost_bp=cost)
        return row

    out["stacks"] = {
        "production": {"note": "same panel/engine/window for every cell; the only "
                               "differences between cells are the three knobs",
                       "cells": table(prod)},
        "capacity_face": {"note": "the stack the 7.80% / 7.28% numbers were printed on "
                                  "(raw un-repaired panel, no class filter, next-open "
                                  "engine); 12-name cells here exist only because this "
                                  "script parametrises n_hold",
                          "cells": table(raw),
                          "rebal_turnover": {str(n): round(float(raw_faces[n]["rebal_turnover"]), 3)
                                             for n in WIDTHS},
                          "repo_missing_days": {str(n): int(raw_faces[n]["rf_missing"])
                                                for n in WIDTHS}},
    }

    # --- controls: does this script reproduce the two published endpoints?
    published = _published()
    out["published"] = published
    controls = {}
    card = round(100.0 * _stats(prod[CARD], "card")["cagr"], 4)
    controls["card_cell_reproduces_spanning"] = _cmp(card, published.get("spanning_card_pp"),
                                                    "prod n12/vol08/10bp vs results/etf_book_spanning.json")
    no_size = 100.0 * _stats(raw[(5, "beta020", 8.0)], "x")["cagr"]
    controls["nosize_cell_reproduces_capacity"] = _cmp(round(no_size, 4),
                                                       published.get("capacity_nosize_pp"),
                                                       "raw n5/beta020/8bp vs results/etf_book_capacity_rule.json")
    out["controls"] = controls

    # --- the bridge: card cell -> ticket cell, same stack, two orders
    prod_cagr = {k: _stats(v, "x")["cagr"] for k, v in prod.items()}
    forward = decompose(prod_cagr, CARD, TICKET,
                        [("width", TICKET), ("rule", TICKET), ("cost", TICKET)])
    reverse = decompose(prod_cagr, CARD, TICKET,
                        [("cost", TICKET), ("rule", TICKET), ("width", TICKET)])
    m_start = marginals(prod_cagr, CARD, TICKET)
    m_end = marginals(prod_cagr, TICKET, CARD)
    out["bridge"] = {
        "stack": "production (one stack for every cell)",
        "from": {"label": "card headline (what the card prints)", "cfg": _fmt_cfg(CARD),
                 "cagr_pp": round(100.0 * prod_cagr[CARD], 4)},
        "to": {"label": "executable ticket (what ORDER-<asof>.md trades)",
               "cfg": _fmt_cfg(TICKET), "cagr_pp": round(100.0 * prod_cagr[TICKET], 4)},
        "total_pp": round(100.0 * (prod_cagr[TICKET] - prod_cagr[CARD]), 4),
        "forward_path": forward,
        "reverse_path": reverse,
        "marginals_from_card": m_start,
        "marginals_from_ticket": m_end,
        "interaction": interaction(100.0 * (prod_cagr[TICKET] - prod_cagr[CARD]),
                                   m_start, m_end),
        "note": "every term is a CAGR difference between two cells of the SAME grid, so "
                "no term can hide a panel, engine or window change. The panel/engine "
                "difference between the two published faces is measured separately in "
                "stacks.capacity_face vs stacks.production, not charged to a knob.",
    }
    out["stack_effect"] = _stack_effect(prod, raw)
    out["verdict"] = _verdict(out)
    out["evidence_cutoff"] = str(close.index[-1].date())
    if write:
        os.makedirs(os.path.dirname(RESULT), exist_ok=True)
        with open(RESULT, "w", encoding="utf-8", newline="\n") as f:
            json.dump(out, f, indent=1, ensure_ascii=False)
    print(json.dumps({"verdict": out["verdict"], "bridge": {
        "from_pp": out["bridge"]["from"]["cagr_pp"], "to_pp": out["bridge"]["to"]["cagr_pp"],
        "total_pp": out["bridge"]["total_pp"],
        "forward": [(s["knob"], s["delta_pp"]) for s in forward["steps"]],
        "reverse": [(s["knob"], s["delta_pp"]) for s in reverse["steps"]],
        "interaction_pp": out["bridge"]["interaction"]["interaction_pp"]},
        "controls": controls}, ensure_ascii=False, indent=1), flush=True)
    return out


def _repo_missing(cells):
    return None


def _stack_effect(prod, raw):
    """Same knobs, two stacks: the part of the published gap that is panel+engine."""
    rows = {}
    for n in WIDTHS:
        for rule in ("flat", "beta020"):
            for cost in COSTS:
                a = _stats(prod[(n, rule, cost)], "p")["cagr"]
                b = _stats(raw[(n, rule, cost)], "r")["cagr"]
                rows[_cell_key("", n, rule, cost).lstrip("|")] = {
                    "production_pp": round(100 * a, 4), "capacity_face_pp": round(100 * b, 4),
                    "delta_pp": round(100 * (a - b), 4)}
    vals = [v["delta_pp"] for v in rows.values()]
    return {"cells": rows,
            "spread_pp": round(max(vals) - min(vals), 4) if vals else None,
            "note": "production stack minus capacity-face stack, knob held fixed. A "
                    "non-zero, variable delta here is panel/engine, NOT a rule effect."}


def _published():
    out = {"spanning_card_pp": None, "capacity_nosize_pp": None,
           "capacity_ceiling_pp": None, "capacity_at_1M_pp": None}
    try:
        d = json.load(open(SPANNING, encoding="utf-8"))
        out["spanning_card_pp"] = round(100 * float(d["book"]["cagr"]), 4)
        out["spanning_config"] = d.get("config")
    except Exception as e:                                        # noqa: BLE001
        out["spanning_error"] = type(e).__name__
    try:
        d = json.load(open(CAPACITY, encoding="utf-8"))
        out["capacity_nosize_pp"] = round(100 * float(d["rule_at_8bp_no_size"]["cagr"]), 4)
        out["capacity_at_1M_pp"] = round(100 * float(d["ladder"]["rule"][0]["cagr"]), 4)
        out["capacity_ceiling_pp"] = round(
            100 * float(d["capacity_frontier_by_cap"]["rule"][0]["cagr"]), 4)
        out["capacity_nosize_config"] = d.get("config")
    except Exception as e:                                        # noqa: BLE001
        out["capacity_error"] = type(e).__name__
    return out


def _cmp(mine_pp, published_pp, label):
    if mine_pp is None or published_pp is None:
        return {"status": "unavailable", "label": label}
    d = abs(float(mine_pp) - float(published_pp))
    return {"mine_pp": round(float(mine_pp), 4), "published_pp": round(float(published_pp), 4),
            "delta_pp": round(d, 4), "within_0p5pp": bool(d <= 0.5), "label": label}


def _verdict(out):
    b = out.get("bridge") or {}
    if not b:
        return "no bridge"
    return ("card %s at %.2f%% vs executable ticket %s at %.2f%% on one stack: %.2fpp apart, "
            "interaction %.2fpp" % (b["from"]["cfg"], b["from"]["cagr_pp"],
                                    b["to"]["cfg"], b["to"]["cagr_pp"],
                                    b["total_pp"], b["interaction"]["interaction_pp"]))


def _now():
    import datetime as dt
    return dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ------------------------------------------------------------------------------ selftest
def selftest():
    n = 0

    def ok(cond, msg):
        nonlocal n
        n += 1
        if not cond:
            raise AssertionError("L%d FAIL: %s" % (n, msg))
        print("  L%-2d PASS %s" % (n, msg))

    # synthetic grid: card 9.6, ticket 7.6, honest 2.0pp total spread over the knobs
    cells = {}
    for w in WIDTHS:
        for r in RULES:
            for c in COSTS:
                v = 0.096
                v += 0.010 if w == 5 else 0.0
                v += 0.004 if c == 8.0 else 0.0
                v += {"flat": 0.006, "vol08": 0.0, "beta020": -0.008}[r]
                cells[(w, r, c)] = v
    fwd = decompose(cells, CARD, TICKET, [("width", TICKET), ("rule", TICKET), ("cost", TICKET)])
    rev = decompose(cells, CARD, TICKET, [("cost", TICKET), ("rule", TICKET), ("width", TICKET)])
    ok(abs(fwd["sum_pp"] - fwd["total_pp"]) < 1e-9, "forward path sums to the total")
    ok(abs(rev["sum_pp"] - rev["total_pp"]) < 1e-9, "reverse path sums to the same total")
    ok(fwd["steps"][0]["knob"] == "width" and rev["steps"][0]["knob"] == "cost",
       "order is honoured, not assumed")
    ok(abs(fwd["total_pp"] - (100 * (cells[TICKET] - cells[CARD]))) < 1e-9,
       "total equals endpoint difference")
    ms, me = marginals(cells, CARD, TICKET), marginals(cells, TICKET, CARD)
    # 1 alternative for each binary knob (width, cost) + 2 for the 3-valued rule axis
    ok(len(ms) == 3 and len(me) == 3, "one marginal per knob toward the other endpoint")
    inter = interaction(fwd["total_pp"], ms, me)
    ok(abs(inter["interaction_from_start_pp"]) < 1e-9
       and abs(inter["interaction_from_end_pp"]) < 1e-9,
       "an additive grid has zero interaction from BOTH ends (so a non-zero term is real)")
    # a genuinely interactive grid: the 12-name book only pays the beta bonus off
    inter_cells = {}
    for w in WIDTHS:
        for r in RULES:
            for c in COSTS:
                v = 0.05 + (0.01 if w == 5 else 0.0) + (0.004 if c == 8.0 else 0.0)
                v += {"flat": 0.006, "vol08": 0.0,
                      "beta020": (-0.008 if w == 12 else 0.004)}[r]
                inter_cells[(w, r, c)] = v
    i_ms, i_me = marginals(inter_cells, CARD, TICKET), marginals(inter_cells, TICKET, CARD)
    i_total = 100 * (inter_cells[TICKET] - inter_cells[CARD])
    i_int = interaction(i_total, i_ms, i_me)
    ok(abs(i_int["interaction_pp"]) > 1e-6,
       "a width x rule interaction shows up instead of being charged to one knob")
    ok(abs(decompose(inter_cells, CARD, TICKET, [("width", TICKET), ("rule", TICKET),
                                                ("cost", TICKET)])["sum_pp"] - i_total) < 1e-9,
       "the waterfall still sums on an interactive grid (sum is exact, split is not)")
    # a path that does not land on the end must be refused, not silently reported
    try:
        decompose(cells, CARD, TICKET, [("width", (5, "flat", 8.0))])
        ok(False, "bad path must raise")
    except ValueError:
        ok(True, "incomplete path raises instead of printing a partial waterfall")
    # cost monotonicity helper: 10bp must never beat 8bp on the same (width, rule)
    ok(all(cells[(w, r, 8.0)] >= cells[(w, r, 10.0)] for w in WIDTHS for r in RULES),
       "fixture cost ordering is the one the live grid is checked against")
    print("selftest %d/%d PASS" % (n, n))
    return 0


def check():
    """Cheap, engine-free audit of the published face (this is the S6 chain leg).

    The grid costs ~5 minutes (panel build dominates), so the chain cannot re-derive it
    every round. What it CAN do every round is refuse to let the published face drift
    away from the faces it reconciles and from its own arithmetic:
      rc 1 = internally inconsistent (grid incomplete, bridge does not sum, control red)
      rc 2 = a source face moved (spanning/capacity headline no longer matches what this
             face recorded) -- re-run the grid, do not quote the old bridge
    """
    if not os.path.exists(RESULT):
        print("reconcile face MISSING: %s" % RESULT)
        return 2
    d = json.load(open(RESULT, encoding="utf-8"))
    problems = []
    want = {n for n in WIDTHS}
    prod = ((d.get("stacks") or {}).get("production") or {}).get("cells") or {}
    if len(prod) != len(want) * len(RULES) * len(COSTS):
        problems.append("production grid has %d cells, expected %d"
                        % (len(prod), len(want) * len(RULES) * len(COSTS)))
    rawc = ((d.get("stacks") or {}).get("capacity_face") or {}).get("cells") or {}
    if len(rawc) != len(want) * 2 * len(COSTS):
        problems.append("capacity-face grid has %d cells, expected %d"
                        % (len(rawc), len(want) * 2 * len(COSTS)))
    b = d.get("bridge") or {}
    if b:
        total = float(b["total_pp"])
        f = float(b["forward_path"]["sum_pp"])
        r = float(b["reverse_path"]["sum_pp"])
        if abs(f - total) > 1e-6 or abs(r - total) > 1e-6:
            problems.append("bridge does not sum: total %.4f fwd %.4f rev %.4f"
                            % (total, f, r))
        endpoints = round(float(b["to"]["cagr_pp"]) - float(b["from"]["cagr_pp"]), 4)
        if abs(endpoints - total) > 1e-6:
            problems.append("bridge total %.4f != endpoint difference %.4f"
                            % (total, endpoints))
    else:
        problems.append("no bridge block")
    for k, v in (d.get("controls") or {}).items():
        if isinstance(v, dict) and v.get("within_0p5pp") is False:
            problems.append("control red: %s (mine %.4f vs published %.4f)"
                            % (k, v.get("mine_pp") or 0.0, v.get("published_pp") or 0.0))
    live = _published()
    rec = d.get("published") or {}
    moved = [k for k in ("spanning_card_pp", "capacity_nosize_pp", "capacity_ceiling_pp",
                         "capacity_at_1M_pp")
             if rec.get(k) is not None and live.get(k) is not None
             and abs(float(rec[k]) - float(live[k])) > 0.01]
    if moved:
        msg = ("source faces moved: %s recorded %s vs live %s"
               % (", ".join(moved), {k: rec.get(k) for k in moved},
                  {k: live.get(k) for k in moved}))
        print("reconcile STALE " + msg)
        return 2
    if problems:
        print("reconcile INCONSISTENT: " + "; ".join(problems))
        return 1
    print("reconcile OK cutoff=%s card=%.2f%% ticket=%.2f%% total=%.2fpp interaction=%.2fpp"
          % (d.get("evidence_cutoff"), float(b["from"]["cagr_pp"]),
             float(b["to"]["cagr_pp"]), float(b["total_pp"]),
             float(b["interaction"]["interaction_pp"])))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--check", action="store_true",
                    help="audit the published face without re-running the grid")
    ap.add_argument("--no-write", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.check:
        return check()
    run(write=not a.no_write)
    return 0


if __name__ == "__main__":
    sys.exit(main())
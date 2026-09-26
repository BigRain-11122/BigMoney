# -*- coding: utf-8 -*-
"""Market-clock current call -- T-74 s1 (O-20260926-0932).

Generates the CURRENT market-clock one-pager per research/MARKET_CLOCK_COMBO.md (s0 v1.2):
  L1 = REGIME_GUARD v3 state (results/regime_state.json, produced by S6 chain) x heat composite
       (HOT if LHB last-day rows >= rolling-250d p80 of daily row counts AND net buy sum > 0);
  L2 = core48 ETF momentum board (r5/r20/r60) on files fresh at the daily panel cutoff;
  L3 = sleeve activation -- EVIDENCE-DRIVEN since v1.2 (O-20260926-1342 sec.3, T-81 slice-2):
       activated = design nomination (SLEEVE_TABLE) INTERSECT evidence gate (profile_cards
       heat-cell PASS, prereg research/L3_ACTIVATION_EVIDENCE.md); no-evidence state = NOT
       activated (fail-closed); structural sleeves (cash leg / falsified / in-flight) carry
       their structural labels verbatim. Full 8-cell table -> results/market_clock/l3_activation_table.json.
  L4/L5 = selection faces / position ladder per the frozen table (v1.0 lines unchanged).

Deterministic, read-only on inputs, zero network. Output:
  results/market_clock/CALL-<asof>.md + results/market_clock/call_latest.json
  results/market_clock/l3_activation_table.json (8 cells x 6 sleeves evidence matrix)
Idempotent per asof (rerun same-day = byte-identical; no wall-clock fields).

Usage:
  python scripts/market_clock_call.py run        (normal; no-op-safe, regenerates current call)
  python scripts/market_clock_call.py selftest  (offline hermetic: synthetic regime+lhb+daily+cards)

Exit codes: 0 = call written (or selftest pass); 2 = mechanism failure (honest, report as-is).
"""
import hashlib
import json
import os
import sys

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "results", "market_clock")
LHB_PATH = os.path.join(ROOT, "Money02", "data", "lhb", "lhb_detail.parquet")
SCORECARD_PATH = os.path.join(ROOT, "results", "strategy_scorecard.json")
L3_PREREG = os.path.join(ROOT, "research", "L3_ACTIVATION_EVIDENCE.md")
L3_TABLE_PATH = os.path.join(OUT_DIR, "l3_activation_table.json")

# Sleeve activation table -- design baseline frozen verbatim from research/MARKET_CLOCK_COMBO.md
# s0 v1.0 (L3/L5). Since v1.2 activation is EVIDENCE-GATED (O-20260926-1342 sec.3): a design-
# nominated sleeve activates in a cell only with profile_cards heat-cell PASS evidence.
SLEEVE_TABLE = {
    "GREEN_COOL": ["offense-corps trend/momentum sleeve (full)", "grid sleeve aux"],
    "GREEN_HOT": ["offense-corps momentum sleeve (full)", "wild-theme micro-satellite (<=5%, T-57 survivor gate)"],
    "YELLOW_COOL": ["chop-corps grid sleeve (half)", "mean-reversion range sleeve (half)"],
    "YELLOW_HOT": ["chop-corps grid sleeve (half)", "mean-reversion range sleeve (half)"],
    "ORANGE_COOL": ["chop-corps on duty (grid/mean-reversion half)", "dividend-lowvol base position"],
    "ORANGE_HOT": ["chop-corps on duty (half)", "wild-theme micro-satellite (<=5%, T-57 survivor gate)"],
    "RED_COOL": ["air-defense cash leg (>=80% cash/bond), no theme satellite"],
    "RED_HOT": ["air-defense cash leg (>=80% cash/bond), no theme satellite"],
}
POSITION_LADDER = {"RED": 0.20, "ORANGE": 0.50, "YELLOW": 0.65, "GREEN": 0.80}
HOT_LADDER_BONUS = 0.15  # GREEN x HOT -> 0.95 per canon L5

# --- L3 evidence-driven faces (T-81 slice-2, prereg research/L3_ACTIVATION_EVIDENCE.md sec.1) ---
# Sleeve -> member evidence cards (declared mapping, all citations in prereg sec.1). Structural
# sleeves without members carry a structural label and never activate on cell evidence.
SLEEVE_REGISTRY = {
    "offense": {
        "label": "offense-corps trend/momentum sleeve",
        "members": ["AGGR-OFFENSE", "AGGR-CONC-TOP2", "AGGR-REGIME"],
        "structural": None,
    },
    "grid": {
        "label": "grid sleeve",
        "members": [],
        "structural": "FALSIFIED (T-78 grid_sleeve_p1 0/5 survivors judged negative)",
    },
    "mean_reversion": {
        "label": "mean-reversion range sleeve",
        "members": ["VOLATILITY-CE-01"],
        "structural": None,
    },
    "satellite": {
        "label": "wild-theme micro-satellite",
        "members": [],
        "structural": "NO_SURVIVORS (T-57 wild-route 0 survivors)",
    },
    "divlowvol": {
        "label": "dividend-lowvol base position",
        "members": [],
        "structural": "JUDGED_NEGATIVE (CN-DIV-LOWVOL-ROT 0/4 G1'v2, bm-a R252; state face = results/strategy_scorecard.json landing_hooks, LANDING_HOOKS_P1 sec.2.2)",
    },
    "airdefense_cash": {
        "label": "air-defense cash leg",
        "members": ["COMPOSITE-CE-01", "COMPOSITE-CE-02", "DROUGHT-CE-01", "ENGULF-CE-01", "NEEDLE-DE-01"],
        "structural": "CASH_LEG_STRUCTURAL (cash floor by construction in RED rows; member evidence gates only the <=20% strategy risk-leg)",
    },
}
# Design nomination per cell (traceability to SLEEVE_TABLE lines; the design ROUTES, evidence GATES).
# Keys = L3_CELLS format STATExHEAT.
CELL_NOMINATION = {
    "GREENxCOOL": ["offense", "grid"],
    "GREENxHOT": ["offense", "satellite"],
    "YELLOWxCOOL": ["mean_reversion", "grid"],
    "YELLOWxHOT": ["mean_reversion", "grid"],
    "ORANGExCOOL": ["grid", "mean_reversion", "divlowvol"],
    "ORANGExHOT": ["grid", "mean_reversion", "satellite"],
    "REDxCOOL": ["airdefense_cash"],
    "REDxHOT": ["airdefense_cash"],
}
L3_CELLS = [f"{s}x{h}" for s in ("GREEN", "YELLOW", "ORANGE", "RED") for h in ("COOL", "HOT")]


def _profile_cards_face():
    """Load the profile_cards evidence face (T-81 slice-1). Honest label on failure."""
    try:
        d = json.load(open(SCORECARD_PATH, encoding="utf-8-sig"))
        pc = d.get("profile_cards") or {}
        cards = pc.get("cards")
        if not isinstance(cards, dict) or not cards:
            return {"face": "FACE_ERROR", "error": "profile_cards.cards missing/empty"}
        return {"face": "OK", "pc": pc, "cards": cards}
    except Exception as e:
        return {"face": "FACE_ERROR", "error": repr(e)[:200]}


def _sleeve_cell_record(skey, sleeve, cellkey, cards, nominated, face_ok):
    """Per-sleeve per-cell record per prereg sec.2 (evidence gate x nomination intersection)."""
    rec = {
        "label": sleeve["label"],
        "nominated": nominated,
        "members": sleeve["members"],
        "cell_verdicts": {},
        "n_pass": 0,
        "evidence_activated": False,
        "status": None,
        "activated": False,
        "note": None,
    }
    if not face_ok:
        if skey == "airdefense_cash" and cellkey and cellkey.startswith("RED") and nominated:
            rec["status"] = "STRUCTURAL_CASH"
            rec["activated"] = True
            rec["note"] = "cash floor by construction (prereg sec.2 rule 4); strategy risk-leg NOT activated: evidence face missing"
        else:
            rec["status"] = "NOT_ACTIVATED_EVIDENCE_FACE_MISSING"
            rec["note"] = "profile_cards face unreadable -> fail-closed (prereg sec.2 rule 3)"
        return rec
    for m in sleeve["members"]:
        v = None
        hc = (cards.get(m) or {}).get("heat_cells") or {}
        cell = hc.get(cellkey)
        if isinstance(cell, dict):
            v = cell.get("verdict")
        rec["cell_verdicts"][m] = v
        if v == "PASS":
            rec["n_pass"] += 1
    rec["evidence_activated"] = rec["n_pass"] > 0
    if sleeve["structural"]:
        tag = sleeve["structural"].split(" ")[0]
        if skey == "airdefense_cash":
            # prereg sec.2 rule 4: cash leg structural in RED rows; strategy risk-leg gated by members.
            cash_row = cellkey.startswith("RED")
            rec["status"] = "STRUCTURAL_CASH" if cash_row else (
                "ACTIVATED" if rec["evidence_activated"] else (
                    "NOT_ACTIVATED_DEAD" if rec["cell_verdicts"] and all(
                        v == "DEAD_ZONE" for v in rec["cell_verdicts"].values()) else "NOT_ACTIVATED_NO_EVIDENCE"))
            rec["activated"] = bool(cash_row and nominated) or (nominated and rec["evidence_activated"] and not cash_row)
            rec["note"] = sleeve["structural"] + (
                "; strategy risk-leg NOT activated: zero RED days in evidence window" if cash_row and not rec["evidence_activated"] else "")
        else:
            rec["status"] = "NOT_ACTIVATED_" + tag
            rec["note"] = sleeve["structural"]
    else:
        if rec["evidence_activated"]:
            rec["status"] = "ACTIVATED"
        elif rec["cell_verdicts"] and all(v == "DEAD_ZONE" for v in rec["cell_verdicts"].values()):
            rec["status"] = "NOT_ACTIVATED_DEAD"
        else:
            rec["status"] = "NOT_ACTIVATED_NO_EVIDENCE"
        rec["activated"] = bool(nominated and rec["evidence_activated"])
    return rec


def _l3_evidence_table(cards_face):
    """8-cell x 6-sleeve evidence matrix (prereg sec.2). Readout-only, +0 ledger face."""
    face_ok = cards_face.get("face") == "OK"
    cards = cards_face.get("cards") or {}
    table = {}
    for cellkey in L3_CELLS:
        design = SLEEVE_TABLE.get(cellkey, [])
        nominated_keys = CELL_NOMINATION.get(cellkey, [])
        sleeves = {}
        activated_keys = []
        for skey, sleeve in SLEEVE_REGISTRY.items():
            rec = _sleeve_cell_record(skey, sleeve, cellkey, cards, skey in nominated_keys, face_ok)
            sleeves[skey] = rec
            if rec["activated"]:
                activated_keys.append(skey)
        table[cellkey] = {
            "design_sleeves": design,
            "nominated": nominated_keys,
            "sleeves": sleeves,
            "activated": activated_keys,
        }
    meta = {"prereg": "research/L3_ACTIVATION_EVIDENCE.md"}
    if face_ok:
        pc = cards_face["pc"]
        meta.update({
            "source_face": "results/strategy_scorecard.json profile_cards",
            "batch": pc.get("batch"), "ticket": pc.get("ticket"),
            "evidence_cutoff": pc.get("evidence_cutoff"),
            "source_prereg_sha256_16": pc.get("prereg_sha256_16"),
        })
    else:
        meta["source_face"] = "EVIDENCE_FACE_MISSING: " + str(cards_face.get("error"))
    try:
        with open(L3_PREREG, "rb") as f:
            meta["prereg_sha256_16"] = hashlib.sha256(f.read()).hexdigest()[:16]
    except Exception:
        meta["prereg_sha256_16"] = None
    return {"version": 1, "canon": "MARKET_CLOCK_COMBO s0 v1.2 L3 evidence-driven (O-20260926-1342 sec.3)",
            "meta": meta, "cells": table}


def _sleeve_strings(cellkey, ev_table):
    """Evidence-driven active_sleeves strings for one cell (honest, machine-stable)."""
    if cellkey not in ev_table["cells"]:
        return ["UNDETERMINED -- face error, no instruction issued (honest)"]
    cell = ev_table["cells"][cellkey]
    out = []
    for skey in cell["nominated"]:
        rec = cell["sleeves"][skey]
        if rec["activated"]:
            if rec["status"] == "STRUCTURAL_CASH":
                out.append(f"{rec['label']} ACTIVATED (structural cash >=80%; strategy risk-leg NOT activated -- no RED-state evidence)"
                           if "risk-leg" in (rec["note"] or "") else f"{rec['label']} ACTIVATED ({rec['status']})")
            else:
                ev = [m for m, v in rec["cell_verdicts"].items() if v == "PASS"]
                out.append(f"{rec['label']} ({skey}) ACTIVATED (evidence: {', '.join(ev)})")
        else:
            out.append(f"{rec['label']} ({skey}) NOT activated ({rec['status']}"
                       + (f"; {rec['note']}" if rec["note"] else "") + ")")
    if not cell["activated"]:
        out.append("zero evidence-backed sleeves activate in this cell (fail-closed, O-20260926-1342 sec.1.4)")
    # disclosure: evidence-PASS sleeves NOT nominated by design in this cell (prereg sec.2 rule 2)
    for skey, rec in cell["sleeves"].items():
        if not rec["nominated"] and rec["evidence_activated"]:
            out.append(f"disclosure: {rec['label']} ({skey}) has PASS evidence in cell but is not design-nominated here (routing frozen)")
    return out



def _heat_face():
    """LHB heat composite. Returns dict with honest face-state labels on failure."""
    try:
        df = pd.read_parquet(LHB_PATH, columns=["上榜日", "龙虎榜净买额"])
    except Exception as e:
        return {"state": "FACE_ERROR", "error": repr(e)[:200]}
    df["上榜日"] = pd.to_datetime(df["上榜日"])
    daily_rows = df.groupby("上榜日").size()
    daily_net = df.groupby("上榜日")["龙虎榜净买额"].sum()
    asof = daily_rows.index.max()
    # rolling 250-trading-day p80 of daily row counts, evaluated strictly BEFORE asof (causality)
    hist = daily_rows[daily_rows.index < asof].tail(250)
    p80 = float(hist.quantile(0.80)) if len(hist) >= 60 else None
    rows_last = int(daily_rows.loc[asof])
    net_last = float(daily_net.loc[asof])
    if p80 is None:
        heat = "UNDETERMINED"
    else:
        heat = "HOT" if (rows_last >= p80 and net_last > 0) else "COOL"
    return {
        "asof": str(asof.date()),
        "rows_last_day": rows_last,
        "net_buy_sum_yuan": net_last,
        "rolling250_p80_rows": p80,
        "hist_days": int(len(hist)),
        "heat": heat,
    }


def _momentum_board(asof):
    """core48 ETF momentum board on files whose last bar == asof (fresh only, honest)."""
    import glob

    recs = []
    for f in glob.glob(os.path.join(ROOT, "data", "daily", "*.csv")):
        sym = os.path.splitext(os.path.basename(f))[0]
        try:
            px = pd.read_csv(f, usecols=[0, 4])
        except Exception:
            continue
        px.columns = ["date", "close"]
        px["date"] = pd.to_datetime(px["date"])
        px = px.sort_values("date").dropna()
        if str(px["date"].iloc[-1].date()) != asof or len(px) < 61:
            continue
        c = px["close"].values
        recs.append({
            "symbol": sym,
            "r5": round(float(c[-1] / c[-6] - 1), 4),
            "r20": round(float(c[-1] / c[-21] - 1), 4),
            "r60": round(float(c[-1] / c[-61] - 1), 4),
        })
    recs.sort(key=lambda r: r["r20"], reverse=True)
    return recs


def _regime_face():
    try:
        d = json.load(open(os.path.join(ROOT, "results", "regime_state.json"), encoding="utf-8"))
        return {"state": d.get("state"), "asof": d.get("asof"), "days_in_state": d.get("days_in_state"),
                "triggers": d.get("triggers", [])}
    except Exception as e:
        return {"state": "FACE_ERROR", "error": repr(e)[:200]}


def build_call():
    regime = _regime_face()
    heat = _heat_face()
    asof = heat.get("asof") if heat.get("asof") else regime.get("asof")
    board = _momentum_board(asof) if asof else []
    state = regime.get("state", "UNDETERMINED")
    heatv = heat.get("heat", "UNDETERMINED")
    cell = f"{state}_{heatv}" if (state and heatv) else "UNDETERMINED"
    cards_face = _profile_cards_face()
    ev_table = _l3_evidence_table(cards_face)
    cellkey = f"{state}x{heatv}" if (state and heatv) else None
    sleeves = _sleeve_strings(cellkey, ev_table)
    ladder = POSITION_LADDER.get(state)
    if ladder is not None and cell == "GREEN_HOT":
        ladder = round(ladder + HOT_LADDER_BONUS, 2)
    breadth = round(sum(1 for r in board if r["r20"] > 0) / len(board), 3) if board else None
    ev_meta = ev_table.get("meta", {})
    call = {
        "asof": asof,
        "clock_cell": cell,
        "regime_v3": regime,
        "heat_composite": {k: heat.get(k) for k in
                           ("rows_last_day", "net_buy_sum_yuan", "rolling250_p80_rows", "heat")},
        "sector_board_top8": board[:8],
        "sector_board_bottom5": board[-5:],
        "fresh_universe_n": len(board),
        "breadth_r20_pos": breadth,
        "active_sleeves": sleeves,
        "l3_evidence": {
            "activated": ev_table["cells"].get(cellkey, {}).get("activated", []),
            "evidence_face": ev_meta.get("source_face"),
            "evidence_cutoff": ev_meta.get("evidence_cutoff"),
            "prereg": "research/L3_ACTIVATION_EVIDENCE.md",
            "prereg_sha256_16": ev_meta.get("prereg_sha256_16"),
        },
        "position_cap_ladder": ladder,
        "canon": "research/MARKET_CLOCK_COMBO.md s0 v1.2 (L3 evidence-driven per O-20260926-1342 sec.3; L1/L2/L5 v1.0 lines)",
    }
    call["_ev_table"] = ev_table
    return call


def render_md(call):
    h = call["heat_composite"]
    L = []
    L.append(f"# 市场时钟 · 当日系统指令 — {call['asof']}")
    L.append("")
    L.append(f"- **时钟格**：`{call['clock_cell']}`（v3 政体 × 热度复合，正典=MARKET_CLOCK_COMBO.md s0 v1.0）")
    r = call["regime_v3"]
    L.append(f"- **L1 政体（v3）**：{r.get('state')} · 在态 {r.get('days_in_state')} 日 · 触发：{'；'.join(r.get('triggers', []) or [])}")
    net_yi = h.get("net_buy_sum_yuan")
    rows_lh, p80 = h.get("rows_last_day"), h.get("rolling250_p80_rows")
    cmp_rows = ">=" if (rows_lh is not None and p80 is not None and rows_lh >= p80) else "<"
    cmp_net = ">" if (net_yi or 0) > 0 else "<="
    L.append(f"- **L1 热度复合**：{h.get('heat')}（LHB 当日 {rows_lh} 行 {cmp_rows} 滚动250日p80 {p80} 且 净买 "
             f"{round(net_yi / 1e8, 2) if net_yi is not None else 'N/A'} 亿 {cmp_net} 0）")
    L.append(f"- **L2 板块面**（core48 新鲜 {call['fresh_universe_n']} 件，r20 强势榜）：")
    for r0 in call["sector_board_top8"][:8]:
        L.append(f"  - {r0['symbol']}: r5 {r0['r5']:+.1%} · r20 {r0['r20']:+.1%} · r60 {r0['r60']:+.1%}")
    bottom = "；".join("{} r20 {:+.1%}".format(r0["symbol"], r0["r20"]) for r0 in call["sector_board_bottom5"])
    L.append(f"  - 弱势榜尾：{bottom}")
    L.append(f"  - 宽度（r20>0 占比）：{call['breadth_r20_pos']}")
    L.append(f"- **L3/L4 激活袖与选股面**（证据驱动 v1.2：激活=设计提名∩画像证据，无证=不激活）：")
    for s in call["active_sleeves"]:
        L.append(f"  - {s}")
    ev = call.get("l3_evidence") or {}
    L.append(f"  - 证据面：{ev.get('evidence_face')} · evidence_cutoff {ev.get('evidence_cutoff')} · "
             f"prereg {ev.get('prereg')} sha16 {ev.get('prereg_sha256_16')} · 全表 results/market_clock/l3_activation_table.json")
    L.append(f"- **L5 仓位阶梯帽**：{call['position_cap_ladder'] if call['position_cap_ladder'] is not None else 'N/A'}"
             f"（RED 20% → ORANGE 50% → GREEN 80% → GREEN×HOT 95%；T0 刹车不破）")
    L.append("")
    L.append("> 面态只读判定（收盘因果），零未来数据；缺面与代理披露见正典 §1/§2。")
    return "\n".join(L)


def run():
    os.makedirs(OUT_DIR, exist_ok=True)
    call = build_call()
    ev_table = call.pop("_ev_table")
    asof = call.get("asof") or "undetermined"
    md_path = os.path.join(OUT_DIR, f"CALL-{asof}.md")
    with open(md_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(render_md(call))
    latest = os.path.join(OUT_DIR, "call_latest.json")
    with open(latest, "w", encoding="utf-8", newline="\n") as f:
        json.dump(call, f, ensure_ascii=False, indent=1, default=str)
    with open(L3_TABLE_PATH, "w", encoding="utf-8", newline="\n") as f:
        json.dump(ev_table, f, ensure_ascii=False, indent=1, default=str)
    print(f"call written: {md_path} cell={call['clock_cell']} sleeves={len(call['active_sleeves'])} "
          f"activated={len(call['l3_evidence']['activated'])}")
    return 0


def _synthetic_cards_face():
    """Hermetic profile_cards fixture mirroring the slice-1 face shape (family-1 microcosm)."""
    def card(hc):
        return {"account": "x", "family": "A", "heat_cells": hc, "activation_set": [], "states": {}}
    cards = {
        "AGGR-OFFENSE": card({"GREENxCOOL": {"verdict": "PASS"}, "GREENxHOT": {"verdict": "PASS"}}),
        "AGGR-CONC-TOP2": card({"GREENxCOOL": {"verdict": "PASS"}, "GREENxHOT": {"verdict": "DEAD_ZONE"}}),
        "AGGR-REGIME": card({"GREENxCOOL": {"verdict": "PASS"}, "GREENxHOT": {"verdict": "PASS"}}),
        "VOLATILITY-CE-01": card({"YELLOWxCOOL": {"verdict": "PASS"}, "YELLOWxHOT": {"verdict": "PASS"},
                                  "GREENxCOOL": {"verdict": "PASS"}}),
        "COMPOSITE-CE-01": card({}),
    }
    pc = {"batch": "SYNTH", "ticket": "T-81", "evidence_cutoff": "2026-09-24", "prereg_sha256_16": "synthetic0000000"}
    return {"face": "OK", "pc": pc, "cards": cards}


def selftest():
    """Hermetic: monkeypatch face readers with synthetic minimal data, assert clock + L3 evidence logic."""
    global _heat_face, _momentum_board, _regime_face, _profile_cards_face
    heat = {"asof": "2026-09-24", "rows_last_day": 90, "net_buy_sum_yuan": 1.0e9, "rolling250_p80_rows": 70.0, "heat": "HOT"}
    board = [{"symbol": "X1", "r5": 0.01, "r20": 0.02, "r60": 0.03}, {"symbol": "X2", "r5": -0.01, "r20": -0.02, "r60": -0.03}]
    regime = {"state": "ORANGE", "asof": "2026-09-24", "days_in_state": 2, "triggers": ["t1"]}
    _heat_face, _momentum_board, _regime_face = (lambda: heat), (lambda a: board), (lambda: regime)
    _profile_cards_face = _synthetic_cards_face
    c = build_call()
    # [1] current cell ORANGE_HOT: zero evidence (no ORANGE cells in fixture) -> fail-closed zero activation
    assert c["clock_cell"] == "ORANGE_HOT", c["clock_cell"]
    assert any("micro-satellite" in s and "NOT activated" in s for s in c["active_sleeves"]), c["active_sleeves"]
    assert c["l3_evidence"]["activated"] == [], c["l3_evidence"]
    assert any("zero evidence-backed sleeves" in s for s in c["active_sleeves"]), c["active_sleeves"]
    assert c["position_cap_ladder"] == 0.50, c["position_cap_ladder"]
    assert c["breadth_r20_pos"] == 0.5
    ev = c.pop("_ev_table")
    # [2] evidence gate: GREENxHOT offense activates on OFFENSE+REGIME PASS despite CONC-TOP2 DEAD; satellite NO_SURVIVORS
    gh = ev["cells"]["GREENxHOT"]
    assert gh["activated"] == ["offense"], gh["activated"]
    assert gh["sleeves"]["offense"]["cell_verdicts"] == {"AGGR-OFFENSE": "PASS", "AGGR-CONC-TOP2": "DEAD_ZONE", "AGGR-REGIME": "PASS"}
    assert gh["sleeves"]["satellite"]["status"].startswith("NOT_ACTIVATED_NO_SURVIVORS")
    assert gh["sleeves"]["grid"]["status"].startswith("NOT_ACTIVATED_FALSIFIED")
    # [3] nomination intersection: mean_reversion has PASS evidence in GREENxCOOL but is NOT nominated there -> disclosed, not activated
    gc = ev["cells"]["GREENxCOOL"]
    assert gc["activated"] == ["offense"] and "mean_reversion" not in gc["activated"], gc["activated"]
    assert gc["sleeves"]["mean_reversion"]["nominated"] is False and gc["sleeves"]["mean_reversion"]["evidence_activated"] is True
    # [4] YELLOW cells: mean_reversion nominated + PASS -> activated; grid falsified stays out
    yc = ev["cells"]["YELLOWxCOOL"]
    assert yc["activated"] == ["mean_reversion"], yc["activated"]
    # [5] RED rows: cash leg structural activation, strategy members NO_EVIDENCE, satellite ban intact
    rc = ev["cells"]["REDxCOOL"]
    assert rc["activated"] == ["airdefense_cash"], rc["activated"]
    assert rc["sleeves"]["airdefense_cash"]["status"] == "STRUCTURAL_CASH"
    assert rc["sleeves"]["airdefense_cash"]["cell_verdicts"]["COMPOSITE-CE-01"] is None
    assert "satellite" not in rc["nominated"]
    # [6] GREEN_HOT ladder bonus + render
    regime2 = dict(regime, state="GREEN")
    _regime_face = lambda: regime2
    c2 = build_call()
    assert c2["clock_cell"] == "GREEN_HOT" and c2["position_cap_ladder"] == 0.95, (c2["clock_cell"], c2["position_cap_ladder"])
    assert c2["l3_evidence"]["activated"] == ["offense"], c2["l3_evidence"]
    md = render_md(c2)
    assert "GREEN_HOT" in md and "L5 仓位阶梯帽" in md and "证据驱动" in md
    # [7] face-missing fail-closed: all sleeves NOT_ACTIVATED_EVIDENCE_FACE_MISSING
    _profile_cards_face = lambda: {"face": "FACE_ERROR", "error": "synthetic missing"}
    regime3 = dict(regime, state="RED")
    _regime_face = lambda: regime3
    c4 = build_call()
    assert c4["position_cap_ladder"] == 0.20
    assert any("air-defense cash leg" in s and "ACTIVATED" in s for s in c4["active_sleeves"]), c4["active_sleeves"]
    ev4 = c4.pop("_ev_table")
    assert ev4["cells"]["REDxHOT"]["sleeves"]["offense"]["status"] == "NOT_ACTIVATED_EVIDENCE_FACE_MISSING"
    # [8] face-error cell (non-L3) -> honest no-instruction passthrough
    _regime_face = lambda: {"state": "FACE_ERROR", "error": "x"}
    c5 = build_call()
    assert c5["clock_cell"] == "FACE_ERROR_HOT", c5["clock_cell"]
    assert c5["active_sleeves"] == ["UNDETERMINED -- face error, no instruction issued (honest)"]
    print("market_clock_call selftest: PASS (8 evidence-driven L3 legs + ladder + render + fail-closed)")
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd == "selftest":
        sys.exit(selftest())
    if cmd == "run":
        sys.exit(run())
    print("usage: run | selftest", file=sys.stderr)
    sys.exit(2)

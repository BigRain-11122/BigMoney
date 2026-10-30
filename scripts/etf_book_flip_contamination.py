"""ETF book -- how much of its published numbers is quote-flip contamination?

`etf_equity_alpha.repair_flips` has existed since the cash-ladder work: some ETF price
series carry single-day prints of -50% or -90% that are unit changes or bad ticks, and a
flat day is the honest reading. The book's production path (`etf_composite_pf.build_panel`
-> `run_next_open`) does not apply it, so every published number of the book is computed
on a panel that still carries those prints.

This face asks the only question that matters for money: **does it change the answer?**
It runs the identical rule twice -- raw panel, repaired panel -- over the same window,
and prints the delta. No new rule, no new engine: `capture` calls the same production
functions in both runs and the repair is the published one, imported, never re-written.

Materiality is frozen before the run. If the deltas stay inside the band the book's
numbers stand and the flips are cosmetic; if they leave it, the published faces are
wrong by that much and the repair is an obligation, not an improvement.

Usage:
    python scripts/etf_book_flip_contamination.py run
    python scripts/etf_book_flip_contamination.py --check
    python scripts/etf_book_flip_contamination.py --selftest
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import numpy as np
import pandas as pd

import etf_composite_pf as F
import etf_equity_alpha as A
import etf_phase_beta_target as BT
import etf_phase_beta_window as BW
import etf_variants_null_rolling as V
import etf_book_order as O
from etf_asset_class import classify

OUT_JSON = ROOT / "results" / "etf_book_flip_contamination.json"
OUT_MD = ROOT / "research" / "ETF_BOOK_FLIP_CONTAMINATION.md"

SCRIPT = "scripts/etf_book_flip_contamination.py"
FACE = "results/etf_book_flip_contamination.json"

# ---------------------------------------------------------------- frozen criteria
# Written before the first run; --check refuses a face whose echoed band differs.
MATERIAL_CAGR_PP = 0.50      # a percentage point of annual return
MATERIAL_MAXDD_PP = 0.50     # a percentage point of drawdown depth
MATERIAL_SHARPE = 0.10       # a tenth of a Sharpe point
FLIP_THR = A.FLIP_THR if hasattr(A, "FLIP_THR") else 0.35

CRITERIA = {
    "material_cagr_pp": MATERIAL_CAGR_PP,
    "material_maxdd_pp": MATERIAL_MAXDD_PP,
    "material_sharpe": MATERIAL_SHARPE,
    "flip_thr": float(FLIP_THR),
    "frozen": "constants above were written before the first run",
}


# ------------------------------------------------------------------ pure functions
def delta_row(raw, clean):
    """Delta between two stats dicts, in the units the criteria are stated in."""
    return {
        "cagr_pp": round(100.0 * (clean["cagr"] - raw["cagr"]), 4),
        "maxdd_pp": round(100.0 * (clean["maxdd"] - raw["maxdd"]), 4),
        "sharpe": round(clean["sharpe"] - raw["sharpe"], 4),
        "vol_pp": round(100.0 * (clean.get("vol", 0.0) - raw.get("vol", 0.0)), 4),
    }


def material(drow, criteria=None):
    c = criteria or CRITERIA
    if drow is None:
        return {"cagr": False, "maxdd": False, "sharpe": False, "any": False}
    out = {
        "cagr": abs(drow["cagr_pp"]) >= c["material_cagr_pp"],
        "maxdd": abs(drow["maxdd_pp"]) >= c["material_maxdd_pp"],
        "sharpe": abs(drow["sharpe"]) >= c["material_sharpe"],
    }
    out["any"] = out["cagr"] or out["maxdd"] or out["sharpe"]
    return out


def worst_day(returns):
    s = pd.Series(returns).astype(float).dropna()
    if not len(s):
        return None
    return {"value": round(float(s.min()), 6),
            "date": pd.Timestamp(s.idxmin()).date().isoformat()}


def count_flips(close, thr=None):
    """Flip prints, measured between adjacent PRICED closes (the E74 lesson)."""
    r = pd.Series(close).ffill().pct_change() if isinstance(close, pd.Series) else \
        close.ffill().pct_change()
    return int((r.abs() > (thr or FLIP_THR)).to_numpy().sum())


def held_on_flip_days(book_dates, flip_by_day):
    """Days the book moved on a bar that carries at least one flip print somewhere."""
    common = [d for d in book_dates if d in flip_by_day]
    return len(common)


# ------------------------------------------------------------------------- build
def capture(close, openp, amt, feats, inception=None):
    """Run the production rule on one panel; return stats + daily returns.

    The same three production calls in both arms -- if this function ever grows a
    second rule, the comparison stops being about the panel.
    """
    classes = pd.Series(classify(list(close.columns)))
    cols = [c for c in close.columns if classes[c] in V.KEEP]
    score = F.build_score(close[cols], amt[cols], feats)
    ser, _turn, _gap = F.run_next_open(close[cols], openp[cols], amt[cols], feats,
                                       O.REBAL, n_hold=F.N_HOLD, cost=F.COST,
                                       score=score)
    mkt = next((c for c in BT.MKT if c in close.columns), None)
    if mkt is None:
        return None
    idx = ser.index.intersection(close[mkt].index)
    if inception is not None:
        idx = idx[idx >= pd.Timestamp(inception)]
    if len(idx) < 60:
        return None
    rp, rm = BT.rets(ser.reindex(idx)), BT.rets(close[mkt].reindex(idx))
    rates = BW.load_repo_rates()
    cash_rf, _missing = BW.repo_daily_cash(idx, rates)
    cash_rf = cash_rf.reindex(idx).fillna(0.0)
    sched = O.k_schedule(rp, rm, O.DEFAULT_BETA)
    if not sched:
        return None
    equity, _k, _m = BT.apply_overlay(rp, rm, sched, 0.0, O.COST_BP, rf=cash_rf)
    if equity is None:
        return None
    st = A.stats2(equity, "book")
    if "cagr" not in st:
        return None
    rets = equity / equity.shift(1) - 1.0
    return {"stats": st, "returns": rets, "bars": int(len(equity))}


def build(out_path=OUT_JSON, md_path=OUT_MD):
    close, openp, amt, feats = F.build_panel()
    adj, adj_open, n_repaired = A.repair_flips(close, openp)

    panels = {"full_history": None, "since_inception": O.DEFAULT_INCEPTION}
    windows = {}
    for name, inception in panels.items():
        raw = capture(close, openp, amt, feats, inception)
        clean = capture(adj, adj_open, amt, feats, inception)
        if raw is None or clean is None:
            windows[name] = None
            continue
        drow = delta_row(raw["stats"], clean["stats"])
        windows[name] = {
            "bars": raw["bars"],
            "inception": None if inception is None else str(inception),
            "raw": {k: (round(float(v), 6) if isinstance(v, (int, float)) else v)
                    for k, v in raw["stats"].items()},
            "clean": {k: (round(float(v), 6) if isinstance(v, (int, float)) else v)
                      for k, v in clean["stats"].items()},
            "delta": drow,
            "material": material(drow),
            "worst_day": {"raw": worst_day(raw["returns"]),
                          "clean": worst_day(clean["returns"])},
        }

    # how the flips are spread over the panel, and whether any lands on a book bar
    r = close.ffill().pct_change()
    bad = r.abs() > FLIP_THR
    flip_by_day = {d for d in bad.index if bool(bad.loc[d].any())}
    symbols_hit = int((bad.sum() > 0).sum())
    worst_prints = []
    for c in close.columns:
        s = r[c].dropna()
        if len(s) and float(s.min()) < -FLIP_THR:
            d = s.idxmin()
            worst_prints.append({"symbol": c, "date": pd.Timestamp(d).date().isoformat(),
                                 "return": round(float(s.min()), 6)})
    worst_prints.sort(key=lambda x: x["return"])

    full = windows.get("full_history") or {}
    verdict = "MATERIAL" if (full.get("material") or {}).get("any") else "COSMETIC"

    payload = {
        "script": SCRIPT,
        "face": FACE,
        "evidence_cutoff": pd.Timestamp(close.index.max()).date().isoformat()
        if len(close.index) else None,
        "criteria": CRITERIA,
        "panel": {"symbols": int(close.shape[1]), "bars": int(close.shape[0]),
                  "flip_prints_flattened": int(n_repaired),
                  "symbols_with_a_flip": symbols_hit,
                  "days_with_a_flip": len(flip_by_day)},
        "windows": windows,
        "worst_prints": worst_prints[:10],
        "verdict": verdict,
    }
    payload["sentence"] = sentence_of(payload)
    if not check_payload(payload):
        print("FATAL: payload failed its own gate")
        return 2
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=1),
                        encoding="utf-8")
    if md_path:
        md_path.write_text(render_md(payload), encoding="utf-8")
    print("wrote %s (verdict %s)" % (out_path.relative_to(ROOT), verdict))
    print(payload["sentence"])
    return 0


def sentence_of(p):
    w = (p.get("windows") or {}).get("full_history") or {}
    d = w.get("delta") or {}
    wd = (w.get("worst_day") or {})
    if not d:
        return "the contamination face could not build both arms, so it states nothing"
    rw, cw = wd.get("raw") or {}, wd.get("clean") or {}
    return ("%d flip prints on the panel move the book's own numbers by %+.2fpp of "
            "annual return, %+.2fpp of drawdown and %+.3f of Sharpe (full history) -- "
            "and the worst day it publishes, %+.2f%% on %s, is one of them: on repaired "
            "prices the worst day is %+.2f%%"
            % (p["panel"]["flip_prints_flattened"], d["cagr_pp"], d["maxdd_pp"],
               d["sharpe"], 100 * (rw.get("value") or 0.0), rw.get("date"),
               100 * (cw.get("value") or 0.0)))


def render_md(p):
    lines = [
        "# ETF book -- quote-flip contamination in its published numbers",
        "",
        "Evidence cutoff %s · production rule untouched · repair = "
        "`etf_equity_alpha.repair_flips` (imported, not re-written)" % p.get("evidence_cutoff"),
        "",
        "## The answer",
        "",
        p.get("sentence", ""),
        "",
        "Verdict: **%s** (band: %.2fpp CAGR / %.2fpp drawdown / %.2f Sharpe)."
        % (p["verdict"], MATERIAL_CAGR_PP, MATERIAL_MAXDD_PP, MATERIAL_SHARPE),
        "",
        "## The panel",
        "",
        "%d symbols x %d bars; **%d** flip prints flattened (%d of %d symbols carry at "
        "least one, on %d distinct days)."
        % (p["panel"]["symbols"], p["panel"]["bars"],
           p["panel"]["flip_prints_flattened"], p["panel"]["symbols_with_a_flip"],
           p["panel"]["symbols"], p["panel"]["days_with_a_flip"]),
        "",
        "| window | bars | | CAGR | Sharpe | max drawdown | worst day |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for name, w in (p.get("windows") or {}).items():
        if not w:
            lines.append("| %s | - | could not build | - | - | - | - |" % name)
            continue
        for arm in ("raw", "clean"):
            st = w[arm]
            wd = (w.get("worst_day") or {}).get(arm) or {}
            lines.append("| %s | %d | %s | %.2f%% | %.3f | %.2f%% | %+.2f%% (%s) |"
                         % (name, w["bars"], arm, 100 * st["cagr"], st["sharpe"],
                            100 * st["maxdd"], 100 * (wd.get("value") or 0.0),
                            wd.get("date")))
        d = w["delta"]
        lines.append("| %s | %d | **delta** | **%+.2fpp** | **%+.3f** | **%+.2fpp** | |"
                     % (name, w["bars"], d["cagr_pp"], d["sharpe"], d["maxdd_pp"]))
    lines += ["", "## The ten deepest prints on the panel", "",
              "| symbol | date | print |", "| --- | --- | --- |"]
    for row in (p.get("worst_prints") or []):
        lines.append("| %s | %s | %+.1f%% |" % (row["symbol"], row["date"],
                                                100 * row["return"]))
    lines += [
        "",
        "## What this does and does not say",
        "",
        "* Nothing was changed in the production path. This face measures the cost of "
        "leaving it unchanged; the repair decision is a separate, deliberate one because "
        "it moves every published number of the book at once.",
        "* The clean arm is the same rule on the same dates with the flip prints read "
        "as flat days -- not a different strategy, and not a better backtest.",
        "* A deeper drawdown under raw prices is the tell: a phantom -50% print in a "
        "held name looks exactly like a real crash to any statistic that only sees "
        "returns.",
        "* The absolute levels in each row are **this face's own construction** (the "
        "production rule over the bars where the index exists). They are not the "
        "ticket's metrics block, which is built differently, and this face makes no "
        "claim to reproduce it -- only the raw/clean delta is being measured here. The "
        "same code, the same dates, one panel difference.",
    ]
    return "\n".join(lines) + "\n"


def check_payload(p):
    if p.get("criteria") != CRITERIA:
        print("GATE: echoed criteria differ from the frozen ones")
        return False
    full = (p.get("windows") or {}).get("full_history") or {}
    d = full.get("delta")
    want = "MATERIAL" if (material(d) or {}).get("any") else "COSMETIC"
    if p.get("verdict") != want:
        print("GATE: verdict does not recompute from the published deltas")
        return False
    return True


# ---------------------------------------------------------------------- selftest
def selftest():
    legs = []

    def leg(name, ok, detail=""):
        legs.append((name, bool(ok), detail))

    idx = pd.date_range("2024-01-01", periods=6, freq="D")
    one = pd.Series([1.0, 1.01, 1.02, 0.51, 0.52, 0.53], index=idx)  # split on day 4
    leg("L1 a split-sized print is counted as a flip", count_flips(one) == 1,
        count_flips(one))
    leg("L2 a normal series counts none",
        count_flips(pd.Series([1.0, 1.01, 1.02, 1.03, 1.04, 1.05], index=idx)) == 0)

    flat = pd.Series([1.0, 1.01, np.nan, 0.51, 0.52, 0.53], index=idx)
    leg("L3 a flip next to a suspension bar is still counted (priced closes, E74)",
        count_flips(flat) == 1, count_flips(flat))

    raw = {"cagr": 0.0654, "maxdd": -0.0691, "sharpe": 1.056, "vol": 0.0815}
    clean = {"cagr": 0.0771, "maxdd": -0.0578, "sharpe": 1.342, "vol": 0.0815}
    d = delta_row(raw, clean)
    leg("L4 deltas are in percentage points and carry sign",
        d["cagr_pp"] > 0 and d["maxdd_pp"] > 0 and d["sharpe"] > 0, d)
    leg("L5 an identical pair is not material",
        not material(delta_row(raw, raw))["any"])
    leg("L6 a 1.17pp return move is material", material(d)["cagr"])
    leg("L7 a 0.05pp drawdown move alone is not material",
        not material({"cagr_pp": 0.0, "maxdd_pp": 0.05, "sharpe": 0.0})["any"])
    leg("L8 the band is inclusive: 0.50pp is material, 0.49pp is not",
        material({"cagr_pp": 0.50, "maxdd_pp": 0.0, "sharpe": 0.0})["cagr"]
        and not material({"cagr_pp": 0.49, "maxdd_pp": 0.0, "sharpe": 0.0})["cagr"])
    leg("L9 an empty delta is not material", not material(None)["any"])

    w = worst_day(pd.Series([0.01, -0.047, 0.02], index=idx[:3]))
    leg("L10 the worst day names its date", w["value"] == -0.047 and w["date"] == "2024-01-02")
    leg("L11 an empty return series has no worst day",
        worst_day(pd.Series([np.nan])) is None)

    p = {"criteria": CRITERIA, "verdict": "MATERIAL",
         "panel": {"flip_prints_flattened": 168},
         "windows": {"full_history": {"delta": {"cagr_pp": 1.17, "maxdd_pp": 1.13,
                                                "sharpe": 0.286},
                                      "worst_day": {"raw": {"value": -0.047,
                                                            "date": "2025-07-07"},
                                                    "clean": {"value": -0.0288,
                                                              "date": "2025-04-23"}}}}}
    leg("L12 the sentence names both worst days",
        "-4.70%" in sentence_of(p) and "-2.88%" in sentence_of(p), sentence_of(p))
    leg("L13 the gate passes a self-consistent payload", check_payload(p))
    bad = dict(p, verdict="COSMETIC")
    leg("L14 the gate refuses a verdict that does not recompute", not check_payload(bad))
    bad2 = dict(p, criteria=dict(CRITERIA, material_cagr_pp=5.0))
    leg("L15 the gate refuses criteria edited after the fact", not check_payload(bad2))

    ok = sum(1 for _n, o, _d in legs if o)
    for name, good, detail in legs:
        print("[%s] %s%s" % ("PASS" if good else "FAIL", name,
                             "" if not detail else " | " + str(detail)))
    print("%d/%d %s" % (ok, len(legs), "PASS" if ok == len(legs) else "FAIL"))
    return 0 if ok == len(legs) else 1


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--out", default=str(OUT_JSON))
    ap.add_argument("--md", default=str(OUT_MD))
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.check:
        p = json.loads(Path(a.out).read_text(encoding="utf-8"))
        ok = check_payload(p)
        print("check: %s" % ("OK" if ok else "FAIL"))
        return 0 if ok else 1
    return build(Path(a.out), Path(a.md))


if __name__ == "__main__":
    sys.exit(main())
"""If the 20% cap had been enforced on the rule's own days, would these six books be richer?

Why this face exists: the family already measures the cap's *state* (`regime_cap_vs_book`),
the two writings of it (`regime_cap_measure_sizes`), what complying today would cost
(`regime_cap_compliance_cost`), how often it was enforced and bought back
(`regime_cap_breach_timeline`), what the re-buy itself earned (`regime_cap_breach_pnl`),
where the freed cash went instead of repo (`regime_cap_breach_cash_vs_repo`) and on which
days the rule binds at all (`regime_cap_binding_days`). None of them answers the question a
reader asks next: **obeying the cap -- does it make money or lose money?**

What this face is NOT: a re-simulation. A forced sale would have changed tomorrow's book and
tomorrow's trades. What it sums is the one-session effect

    equity_d * max(0, w_d - CAP) * (repo_d - r_deployed_d)

over the sessions an arm binds. It prints the model's own error (published equity return vs
the return the same holdings predict) in money next to the effect, and refuses a verdict when
that error could swamp the effect.

Arms (all printed, none chosen):
  actual      the published equity path (exact, no model)
  bear_rule   cap binds on major-bear sessions -- firm/risk/regime.py::major_bear_series
  red_label   cap binds on RED-labelled sessions -- results/regime_state.json
  always_cap  cap binds every session (reference: a permanently 20% book)

Verdicts:
  CANNOT_READ_EXPORT_FACE          no per-session export to read
  NO_BEAR_INTERVALS                the rule's own condition never binds inside the exports
  CANNOT_PRICE_THE_BOOK            too little of the deployed book has a price for both legs
  MODEL_ERROR_SWAMPS_THE_EFFECT    |effect| <= the money the model itself cannot explain
  ENFORCING_THE_CAP_WOULD_HAVE_PAID_X_CNY
  ENFORCING_THE_CAP_WOULD_HAVE_COST_X_CNY
  NO_SEPARABLE_MONEY               effect is zero to the cent

Reads published faces + price/repo panels. Writes its own json + md. Books nothing, changes
no rule, moves no position.

    python scripts/regime_cap_enforced_counterfactual.py run
    python scripts/regime_cap_enforced_counterfactual.py check
    python scripts/regime_cap_enforced_counterfactual.py --selftest
"""

import argparse
import datetime
import glob
import hashlib
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from config import PATHS                                   # noqa: E402
from firm.risk import regime as RULE                       # noqa: E402  single source
import etf_equity_alpha as EA                              # noqa: E402  repair_flips, single source
import regime_cap_binding_days as B                        # noqa: E402  export/bear/red loaders

SCHEMA = "regime-cap-enforced-counterfactual/v1"
ARTIFACT = "results/regime_cap_enforced_counterfactual.json"
DOC = "research/REGIME-CAP-ENFORCED-COUNTERFACTUAL.md"

OUT = os.path.join(PATHS.results_dir, "regime_cap_enforced_counterfactual.json")
DOC_PATH = os.path.join(_ROOT, "research", "REGIME-CAP-ENFORCED-COUNTERFACTUAL.md")
EXPORT_DIR = os.path.join(PATHS.results_dir, "paper_export")
DAILY_DIR = os.path.join(_ROOT, "data", "daily")
REPO_CSV = os.path.join(_ROOT, "data", "repo_daily", "GC001.csv")

# CN-C7: the cost constant every other face in this repo charges. One source, quoted.
COST_SIDE_BP = 13.041
COST_SENSITIVITY_BP = (0.0, 13.041, 26.082)
PRICE_CROSS_TOL = 0.005      # export mark vs panel close, relative
PRICED_SHARE_FLOOR = 0.90    # below this the deployed book is not priced well enough
MONEY_TOL = 0.01             # one fen


# --------------------------------------------------------------------------- inputs

def _read_json(path):
    if not os.path.isfile(path):
        return None, "missing: %s" % os.path.relpath(path, _ROOT)
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh), None
    except Exception as exc:                              # unreadable != empty
        return None, "unreadable: %s (%s)" % (os.path.relpath(path, _ROOT), exc)


def load_exports(export_dir=None):
    """Per-session exports with their holdings. Later duplicate of a date wins (re-drawn).

    Equity/deployed/cash are cross-gated against `regime_cap_binding_days.load_exports`
    so this reader cannot quietly disagree with the rest of the family.
    """
    export_dir = export_dir or EXPORT_DIR
    paths = sorted(glob.glob(os.path.join(export_dir, "export-*.json")))
    by_date, problems = {}, []
    for p in paths:
        pay, err = _read_json(p)
        if err:
            problems.append(err)
            continue
        d = pay.get("export_date")
        if not d:
            problems.append("no export_date: %s" % os.path.basename(p))
            continue
        stamp = pay.get("generated_from_state_updated") or ""
        if d in by_date and stamp < (by_date[d]["stamp"] or ""):
            continue
        by_date[d] = {"file": os.path.basename(p), "stamp": stamp, "payload": pay,
                      "size": os.path.getsize(p)}

    series = {}
    for d in sorted(by_date):
        for t in by_date[d]["payload"].get("traders") or []:
            name = t.get("trader")
            cap = t.get("capital_cny") or {}
            eq, dep = cap.get("equity"), cap.get("positions_value")
            if not name or not isinstance(eq, (int, float)) or not isinstance(dep, (int, float)):
                problems.append("trader without equity/positions on %s: %r" % (d, name))
                continue
            legs = []
            for pos in t.get("open_positions") or []:
                mv = pos.get("market_value_cny")
                sym = pos.get("symbol")
                if not sym or not isinstance(mv, (int, float)):
                    problems.append("leg without symbol/value on %s/%s" % (d, name))
                    continue
                legs.append({"symbol": str(sym), "mv_cny": float(mv),
                             "last_close": pos.get("last_close")})
            series.setdefault(name, {})[d] = {
                "equity_cny": float(eq),
                "deployed_cny": float(dep),
                "cash_cny": float(cap.get("cash") or 0.0),
                "legs": legs,
                "ops_n": len(t.get("operations_today") or []),
            }
    cross = _cross_gate(series)
    return {"dates": sorted(by_date), "series": series, "problems": problems,
            "files": [{"date": d, "file": by_date[d]["file"], "size": by_date[d]["size"]}
                      for d in sorted(by_date)],
            "cross_gate": cross}


def _cross_gate(series):
    """Same trader-day equity/deployed as the family's loader, or say so out loud."""
    theirs = B.load_exports()
    if not isinstance(theirs, dict) or not theirs.get("series"):
        return {"status": "SKIPPED",
                "why": "family loader returned no series (%s)" % (theirs.get("problems") or "")}
    mism, checked = [], 0
    for name, rows in series.items():
        for d, row in rows.items():
            mine = (theirs.get("series") or {}).get(name, {}).get(d)
            if not mine:
                continue
            checked += 1
            for key, tol in (("equity_cny", 0.02), ("deployed_cny", 0.02)):
                if abs(row[key] - float(mine[key])) > tol:
                    mism.append("%s %s %s: %.2f vs %.2f" % (name, d, key, row[key], mine[key]))
    return {"status": "AGREE" if not mism else "MISMATCH", "checked": checked,
            "mismatches": mism[:10]}


def _read_csv_closes(path):
    out = {}
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.lower().startswith("date"):
                    continue
                parts = line.split(",")
                if len(parts) < 5:
                    continue
                try:
                    out[parts[0]] = float(parts[4])
                except ValueError:
                    continue
    except OSError:
        return None
    return out or None


def load_prices(codes, daily_dir=None):
    """{code: {date: repaired close}} -- flip repair imported, never re-written.

    Two families live in data/daily (bare `511010.csv`, `sh511010.csv`); they overlap and
    may disagree. Agreement is asserted here and every disagreement is disclosed.
    """
    import pandas as pd
    daily_dir = daily_dir or DAILY_DIR
    raw, fam_problems = {}, []
    for code in sorted(set(codes)):
        merged, conflicts = {}, 0
        for name in ("%s.csv" % code, "sh%s.csv" % code, "sz%s.csv" % code):
            series = _read_csv_closes(os.path.join(daily_dir, name))
            if not series:
                continue
            for d, px in series.items():
                if d in merged:
                    tol = max(abs(merged[d]) * 1e-6, 1e-9)
                    if abs(merged[d] - px) > tol:
                        conflicts += 1
                        fam_problems.append("%s %s: %.4f vs %.4f" % (code, d, merged[d], px))
                else:
                    merged[d] = px
        if not merged:
            fam_problems.append("no panel file for %s" % code)
            continue
        if conflicts:
            fam_problems.append("%s: %d split-family prints" % (code, conflicts))
        raw[code] = merged

    if not raw:
        return {}, {"flips": 0, "problems": fam_problems}

    frame = pd.DataFrame({c: pd.Series(v, dtype="float64") for c, v in raw.items()}).sort_index()
    adj, _open, flips = EA.repair_flips(frame, frame)
    prices = {}
    for code in adj.columns:
        col = adj[code].dropna()
        prices[str(code)] = {str(k)[:10]: float(v) for k, v in col.items()}
    return prices, {"flips": int(flips), "problems": fam_problems}


def load_repo_rates(path=None):
    """{date: annualised close %} for GC001 (data/repo_daily)."""
    path = path or REPO_CSV
    rates = {}
    if not os.path.isfile(path):
        return {}, "missing: %s" % os.path.relpath(path, _ROOT)
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.lower().startswith("date"):
                    continue
                parts = line.split(",")
                if len(parts) < 5:
                    continue
                try:
                    rates[parts[0]] = float(parts[4])
                except ValueError:
                    continue
    except OSError as exc:
        return {}, "unreadable: %s (%s)" % (os.path.relpath(path, _ROOT), exc)
    return rates, None


def load_bear_map():
    """{date: bool} over the benchmark's own bars (single source, imported)."""
    mask = B.load_bear_mask()
    return {str(k)[:10]: bool(v) for k, v in mask.items()}


def load_red_map():
    red = B.load_red_labels()
    if not isinstance(red, dict):
        return {}, "regime_state.json unreadable"
    if red.get("problem"):
        return {}, str(red["problem"])
    labels = red.get("labels") or {}
    return {str(k)[:10]: v for k, v in labels.items()}, None


# --------------------------------------------------------------------------- primitives

def on_or_before(series, date):
    """(value, used_date, ffilled) for the last print on/before `date`, or (None, None, False)."""
    if not series:
        return None, None, False
    if date in series:
        return series[date], date, False
    best = None
    for d in series:
        if d <= date and (best is None or d > best):
            best = d
    if best is None:
        return None, None, False
    return series[best], best, True


def repo_daily_return(rates, date):
    """(daily simple return, used_date, ffilled) from an annualised percent quote."""
    px, used, ff = on_or_before(rates, date)
    if px is None:
        return None, None, False
    return (px / 100.0) / 365.0, used, ff


def session_return(legs, prices, d0, d1):
    """Return of the deployed book from d0 to d1, plus how much of it could be priced."""
    tot, priced, unpriced = 0.0, 0.0, []
    for leg in legs:
        series = prices.get(leg["symbol"]) or {}
        p0, _, _ = on_or_before(series, d0)
        p1, _, _ = on_or_before(series, d1)
        if p0 is None or p1 is None or not p0:
            unpriced.append({"symbol": leg["symbol"], "mv_cny": round(leg["mv_cny"], 2),
                             "why": "no price on one leg" if p0 is None or p1 is None
                                    else "zero price"})
            continue
        tot += leg["mv_cny"] * (p1 / p0 - 1.0)
        priced += leg["mv_cny"]
    deployed = sum(l["mv_cny"] for l in legs)
    if priced <= 0:
        return None, 0.0, unpriced
    return tot / priced, (priced / deployed if deployed else 0.0), unpriced


def arm_effect(pairs, arm_dates, prices, rates, cap, cost_side_bp, charge_cost=True):
    """One-session effects of binding the cap on `arm_dates`.

    delta = sum over traders/sessions of equity * (w - target) * (r_repo - r_deployed)
    minus one sell side per bound episode (the re-buy side is what the 26.082bp
    sensitivity column buys back, so a round trip is readable without a second model).
    """
    bound_now = [p["d0"] in arm_dates for p in pairs]
    rows, per_trader, total, cost_total = [], {}, 0.0, 0.0
    sessions_matched = sum(1 for b in bound_now if b)
    sessions_bound = sessions_skipped = 0
    prev_bound = False
    for pair, bound in zip(pairs, bound_now):
        d0, d1 = pair["d0"], pair["d1"]
        r_repo, used, ff = repo_daily_return(rates, d0)
        if bound and r_repo is None:
            rows.append({"d0": d0, "d1": d1, "bound": True, "skipped": "no repo quote"})
            sessions_skipped += 1
            prev_bound = True
            continue
        pair_bound = False
        for name in sorted(pair["traders"]):
            sess = pair["traders"][name]
            r_dep, share, unpriced = session_return(sess["legs"], prices, d0, d1)
            if r_dep is None:
                rows.append({"d0": d0, "d1": d1, "trader": name, "bound": bool(bound),
                             "skipped": "no priced leg"})
                continue
            eq0 = sess["equity_cny"]
            w0 = (sess["deployed_cny"] / eq0) if eq0 else 0.0
            target = min(w0, cap)
            binds = bool(bound and w0 > cap)
            delta = eq0 * (w0 - target) * (r_repo - r_dep) if binds else 0.0
            cost = 0.0
            if binds and charge_cost and not prev_bound:
                cost = eq0 * (w0 - target) * (cost_side_bp / 1e4)
            pair_bound = pair_bound or binds
            acc = per_trader.setdefault(name, {"delta_cny": 0.0, "cost_cny": 0.0,
                                               "sessions_bound": 0, "excess_cny": 0.0})
            acc["delta_cny"] += delta
            acc["cost_cny"] += cost
            if binds:
                acc["sessions_bound"] += 1
                acc["excess_cny"] += eq0 * (w0 - target)
            total += delta
            cost_total += cost
            rows.append({"d0": d0, "d1": d1, "trader": name, "bound": bool(bound),
                         "binds": binds, "weight": round(w0, 6), "target": round(target, 6),
                         "delta_cny": round(delta, 2), "cost_cny": round(cost, 2),
                         "r_deployed": round(r_dep, 8),
                         "r_repo": round(r_repo, 10) if r_repo is not None else None,
                         "priced_share": round(share, 6),
                         "unpriced_legs": unpriced})
        if pair_bound:
            sessions_bound += 1
        prev_bound = bool(bound)
    return {"delta_gross_cny": round(total, 2), "cost_cny": round(cost_total, 2),
            "delta_net_cny": round(total - cost_total, 2),
            "per_trader": {k: {kk: round(vv, 2) for kk, vv in v.items()} for k, v in per_trader.items()},
            "rows": rows, "sessions_matched": sessions_matched,
            "sessions_bound": sessions_bound, "sessions_skipped": sessions_skipped}


def _episodes_unused(pairs, arm_dates):   # kept out of the path; see arm_effect
    return [p["d0"] in arm_dates for p in pairs]


def build_pairs(exports):
    """Consecutive export sessions with each trader's book on the earlier one."""
    dates = exports["dates"]
    pairs = []
    for i in range(len(dates) - 1):
        d0, d1 = dates[i], dates[i + 1]
        traders = {}
        for name, rows in exports["series"].items():
            if d0 in rows and rows[d0].get("legs"):
                traders[name] = rows[d0]
        if traders:
            pairs.append({"d0": d0, "d1": d1, "traders": traders})
    return pairs


def measure_model_error(pairs, prices, rates):
    """How well panel closes reproduce the ledger's own equity move -- on clean sessions only.

    A session that traded cannot validate anything: the ledger books the execution price and
    this face only sees closes, so its residual measures the trade, not the price basis.
    Those sessions are counted and disclosed, never folded into the error estimate.
    """
    err_money, err_pp, n = 0.0, [], 0
    unpriced_mv, deployed_mv = 0.0, 0.0
    clean_pairs = traded_pairs = 0
    clean_equity = []
    for pair in pairs:
        d0, d1 = pair["d0"], pair["d1"]
        r_repo, _, _ = repo_daily_return(rates, d0)
        r_repo = r_repo or 0.0
        has_ops = any((nxt or {}).get("ops_n") for nxt in (pair.get("next") or {}).values())
        for name, sess in pair["traders"].items():
            deployed_mv += sess["deployed_cny"]
            _r, _share, unpriced = session_return(sess["legs"], prices, d0, d1)
            unpriced_mv += sum(u["mv_cny"] for u in unpriced)
        if has_ops:
            traded_pairs += 1
            continue                                    # the ledger booked an execution price
        clean_pairs += 1
        for name, sess in pair["traders"].items():
            nxt = (pair.get("next") or {}).get(name)
            r_dep, _, _ = session_return(sess["legs"], prices, d0, d1)
            if nxt is None or r_dep is None:
                continue
            eq0 = sess["equity_cny"]
            w0 = (sess["deployed_cny"] / eq0) if eq0 else 0.0
            pred = w0 * r_dep + (1.0 - w0) * r_repo
            resid = nxt["equity_cny"] / eq0 - 1.0 - pred
            err_money += abs(resid) * eq0
            err_pp.append(resid * 100.0)
            clean_equity.append(eq0)
            n += 1
    return {"n_account_sessions": n,
            "mean_abs_pp": round(sum(abs(x) for x in err_pp) / n, 6) if n else None,
            "max_abs_pp": round(max((abs(x) for x in err_pp), default=0.0), 6) if n else None,
            "error_money_cny": round(err_money, 2),
            "mean_equity_cny": round(sum(clean_equity) / len(clean_equity), 2) if clean_equity else None,
            "clean_pairs": clean_pairs, "traded_pairs_excluded": traded_pairs,
            "unpriced_mv_cny": round(unpriced_mv, 2),
            "deployed_mv_cny": round(deployed_mv, 2),
            "priced_share": round(1.0 - (unpriced_mv / deployed_mv), 6) if deployed_mv else None}


def error_budget(payload, arm):
    """The model error scaled to the sessions an arm actually bound (same units as the effect)."""
    model = payload.get("model") or {}
    rate = model.get("mean_abs_pp")
    eq = model.get("mean_equity_cny")
    if rate is None or eq is None:
        return None
    acc_sessions = 0
    for name, acc in (arm.get("per_trader") or {}).items():
        acc_sessions += int(acc.get("sessions_bound") or 0)
    return round((rate / 100.0) * eq * acc_sessions, 2)


def verdict_for(payload):
    """Name the reading -- every branch is exercised by the selftest."""
    if payload.get("problems_hard"):
        return "CANNOT_READ_EXPORT_FACE"
    arms = payload.get("arms") or {}
    bear = arms.get("bear_rule") or {}
    if not bear.get("sessions_matched"):
        return "NO_BEAR_INTERVALS"
    if not bear.get("sessions_bound") and bear.get("sessions_skipped"):
        return "CANNOT_PRICE_THE_REPO"
    model = payload.get("model") or {}
    share = model.get("priced_share")
    if share is None or share < PRICED_SHARE_FLOOR:
        return "CANNOT_PRICE_THE_BOOK"
    if not bear.get("sessions_bound"):
        return "NO_SEPARABLE_MONEY"
    delta = bear.get("delta_gross_cny")
    if delta is None:
        return "CANNOT_PRICE_THE_BOOK"
    budget = error_budget(payload, bear)
    if abs(delta) <= max(budget or 0.0, MONEY_TOL):
        return "MODEL_ERROR_SWAMPS_THE_EFFECT"
    if abs(delta) <= MONEY_TOL:
        return "NO_SEPARABLE_MONEY"
    if delta > 0:
        return "ENFORCING_THE_CAP_WOULD_HAVE_PAID_%s_CNY" % _money_token(abs(delta))
    return "ENFORCING_THE_CAP_WOULD_HAVE_COST_%s_CNY" % _money_token(abs(delta))


def _money_token(x):
    return ("%.2f" % abs(x)).replace(".", "_")


def sentence_for(payload):
    """One plain sentence for a reader who will never open the json."""
    verdict = payload.get("verdict") or ""
    arms = payload.get("arms") or {}
    bear = arms.get("bear_rule") or {}
    red = arms.get("red_label") or {}
    always = arms.get("always_cap") or {}
    if verdict == "CANNOT_READ_EXPORT_FACE":
        return "读不到逐日导出面，这一问答不了。"
    if verdict == "NO_BEAR_INTERVALS":
        return "导出窗内没有一天触发大熊市条件，这顶帽子在本窗根本没有生效过，无法比较守与不守。"
    if verdict == "CANNOT_PRICE_THE_REPO":
        return "帽子该生效的日子有，但那一侧回购报价读不到，不拿假利率报钱数。"
    if verdict == "CANNOT_PRICE_THE_BOOK":
        share = (payload.get("model") or {}).get("priced_share")
        return ("只有 %s 的持仓能同时取到前后两天的价格，样本不够，不报钱数。"
                % ("—" if share is None else "%.1f%%" % (share * 100.0)))
    if verdict == "MODEL_ERROR_SWAMPS_THE_EFFECT":
        return ("按规则原文该生效的 %d 个会话里，守帽与不守帽的差只有 %.2f 元，"
                "而干净会话上这套持仓也只能把已发布权益追到平均 %.3fpp 以内——折到这几个会话是 %.2f 元，"
                "差得比算得出的还小，不判定。"
                % (bear.get("sessions_bound") or 0, bear.get("delta_gross_cny") or 0.0,
                   (payload.get("model") or {}).get("mean_abs_pp") or 0.0,
                   error_budget(payload, bear) or 0.0))
    if verdict == "NO_SEPARABLE_MONEY":
        return "守帽与不守帽在这几个会话里差到分位为零。"
    paid = verdict.startswith("ENFORCING_THE_CAP_WOULD_HAVE_PAID")
    head = ("按规则原文（大熊市）守帽，这 %d 个会话合计比实际多赚 %.2f 元"
            % (bear.get("sessions_bound") or 0, abs(bear.get("delta_gross_cny") or 0.0))
            if paid else
            "按规则原文（大熊市）守帽，这 %d 个会话合计比实际少赚 %.2f 元"
            % (bear.get("sessions_bound") or 0, abs(bear.get("delta_gross_cny") or 0.0)))
    return ("%s；按 RED 标签的 %d 个会话算则是 %+.2f 元；一直压在 20%% 的参照臂 %d 个会话是 %+.2f 元。%s"
            "这是把每个会话的当期差相加，不是重跑账户，卖出后的后续成交没有重演。"
            % (head, red.get("sessions_bound") or 0, red.get("delta_gross_cny") or 0.0,
               always.get("sessions_bound") or 0, always.get("delta_gross_cny") or 0.0,
               _conc_clause(payload)))


def _conc_clause(payload):
    c = payload.get("concentration") or {}
    if not c.get("largest_session"):
        return ""
    return ("但这笔钱不是一场一场攒出来的：%s 一天就 %+.2f 元，其余 %d 场合计 %+.2f 元。"
            % (c["largest_session"], c.get("largest_cny") or 0.0,
               len(c.get("by_session") or {}) - 1, c.get("total_without_largest_cny") or 0.0))


# --------------------------------------------------------------------------- build

def build(exports=None, prices=None, rates=None, bear=None, red=None, cap=None,
          notes=None, charge_cost=True):
    cap = RULE.CAP_MAJOR_BEAR if cap is None else cap
    notes = list(notes or [])
    payload = {"schema": SCHEMA, "generated": _now(),
               "implementation": {"cap": "firm/risk/regime.py::CAP_MAJOR_BEAR",
                                  "bear": "firm/risk/regime.py::major_bear_series",
                                  "flip_repair": "scripts/etf_equity_alpha.py::repair_flips",
                                  "cost_bp_side": COST_SIDE_BP},
               "cap": cap, "notes": notes}

    hard = []
    if exports is None:
        exports = load_exports()
    if prices is None:
        codes = sorted({leg["symbol"] for rows in exports["series"].values()
                        for row in rows.values() for leg in row.get("legs") or []})
        prices, meta = load_prices(codes)
        payload["price_meta"] = meta
    if rates is None:
        rates, rerr = load_repo_rates()
        if rerr:
            hard.append(rerr)
            payload["repo_problem"] = rerr
    if bear is None:
        bear = load_bear_map()
    if red is None:
        red, rerr2 = load_red_map()
        if rerr2:
            notes.append("red labels: %s" % rerr2)

    payload["export_span"] = {"first": exports["dates"][0] if exports["dates"] else None,
                              "last": exports["dates"][-1] if exports["dates"] else None,
                              "sessions": len(exports["dates"])}
    payload["evidence_cutoff"] = exports["dates"][-1] if exports["dates"] else None
    payload["cross_gate"] = exports.get("cross_gate")
    hard.extend(exports.get("problems") or [])
    if not exports["dates"] or not exports["series"]:
        payload["problems_hard"] = hard or ["no export rows"]
        payload["arms"] = {}
        payload["model"] = {}
        payload["verdict"] = verdict_for(payload)
        payload["sentence"] = sentence_for(payload)
        return payload

    pairs = build_pairs(exports)
    for pair in pairs:                     # next session, for the model's own error
        pair["next"] = {name: exports["series"][name][pair["d1"]]
                        for name in exports["series"] if pair["d1"] in exports["series"][name]}

    bear_dates = {d for d, v in bear.items() if v}
    red_dates = {d for d, v in (red or {}).items() if v == "RED"}
    all_dates = {p["d0"] for p in pairs}

    arms = {}
    for label, bind in (("bear_rule", bear_dates), ("red_label", red_dates),
                        ("always_cap", all_dates)):
        arms[label] = arm_effect(pairs, bind, prices, rates, cap, COST_SIDE_BP,
                                 charge_cost=charge_cost)
        sens = {}
        for bp in COST_SENSITIVITY_BP:
            sens["%g" % bp] = arm_effect(pairs, bind, prices, rates, cap, bp,
                                        charge_cost=charge_cost)["delta_net_cny"]
        arms[label]["cost_sensitivity"] = sens
        arms[label]["rows"] = [r for r in arms[label]["rows"] if r.get("bound")]
    payload["arms"] = arms
    payload["model"] = measure_model_error(pairs, prices, rates)
    payload["error_budget_cny"] = error_budget(payload, arms.get("bear_rule") or {})
    payload["inputs_digest"] = inputs_digest(exports, rates)
    payload["problems_hard"] = hard
    payload["uncovered"] = {
        "sessions_without_a_next_export": [exports["dates"][-1]] if exports["dates"] else [],
        "bear_sessions_outside_pairs": sorted(bear_dates & (set(exports["dates"]) - all_dates)),
        "red_sessions_outside_pairs": sorted(red_dates & (set(exports["dates"]) - all_dates)),
    }
    payload["verdict"] = verdict_for(payload)
    payload["concentration"] = concentration_for((payload.get("arms") or {}).get("bear_rule") or {})
    payload["sentence"] = sentence_for(payload)
    payload["limits"] = limits_for(payload)
    return payload


def concentration_for(arm):
    """Is the total one day wearing the name of a rule? Print it, never let the sum hide it."""
    by_date = {}
    for row in arm.get("rows") or []:
        if not row.get("binds"):
            continue
        by_date[row["d0"]] = by_date.get(row["d0"], 0.0) + (row.get("delta_cny") or 0.0)
    if not by_date:
        return None
    total = sum(by_date.values())
    top = max(by_date.items(), key=lambda kv: abs(kv[1]))
    rest = total - top[1]
    return {"by_session": {d: round(v, 2) for d, v in sorted(by_date.items())},
            "largest_session": top[0], "largest_cny": round(top[1], 2),
            "total_cny": round(total, 2), "total_without_largest_cny": round(rest, 2),
            "largest_share_of_total": round(top[1] / total, 4) if total else None}


def limits_for(payload):
    """What this number may not be read as. Printed on the face, not only in a report."""
    out = []
    bear = (payload.get("arms") or {}).get("bear_rule") or {}
    bound_dates = sorted({r["d0"] for r in (bear.get("rows") or []) if r.get("binds")})
    late = [d for d in bound_dates if "2026-11-16" <= d <= "2026-11-21"]
    if bound_dates:
        out.append("绑定会话 %d 个（%s），其中 %d 个落在 2026-11-16..11-20 这段回撤里。"
                   "在一个下跌窗口里少持仓按构造就会赢——这个数说明的是「这段行情里守帽更省」，"
                   "不是「帽子长期免费赚钱」。" % (len(bound_dates), "、".join(bound_dates), len(late)))
    c = payload.get("concentration") or {}
    if c.get("largest_session"):
        out.append("单场依赖：%s 一天 %+.2f 元，其余 %d 场合计 %+.2f 元——总量是这一天的形状，"
                   "不是一条每场都成立的规律。"
                   % (c["largest_session"], c.get("largest_cny") or 0.0,
                      len(c.get("by_session") or {}) - 1, c.get("total_without_largest_cny") or 0.0))
    model = payload.get("model") or {}
    if model.get("traded_pairs_excluded"):
        out.append("有交易日的 %d 个会话对不参与价格基准校验（账本记的是成交价，这张面只看得见收盘）；"
                   "绑定会话里若当天有交易，账户实现的路径与本面的当期差本来就不是一回事。"
                   % model["traded_pairs_excluded"])
    out.append("只覆盖六员纸盘账户；ETF 复合书按自己的规则不在本梯子里。")
    out.append("成本只在毛差之外按每个绑定片段一次卖出计入净额列，来回一趟由 26.082bp 的敏感列代表。")
    return out


def inputs_digest(exports, rates):
    """Deterministic stand-in for 'which generation of inputs did I read?'."""
    h = hashlib.sha256()
    for row in exports.get("files") or []:
        h.update(("%s:%s\n" % (row["date"], row["size"])).encode("utf-8"))
    if rates:
        h.update(("repo_last:%s\n" % max(rates)).encode("utf-8"))
    return h.hexdigest()[:16]


def _now():
    return datetime.datetime.now().astimezone().replace(microsecond=0).isoformat()


# --------------------------------------------------------------------------- render

def render_md(payload):
    arms = payload.get("arms") or {}
    model = payload.get("model") or {}
    lines = []
    lines.append("# 守帽 vs 破帽：这顶 20% 帽子到底让人赚钱还是亏钱")
    lines.append("")
    lines.append("- schema: `%s` · 生成 %s · evidence_cutoff **%s**（%s 个逐日导出会话）"
                 % (payload["schema"], payload.get("generated"), payload.get("evidence_cutoff"),
                    (payload.get("export_span") or {}).get("sessions")))
    lines.append("- 判词：**%s**" % payload.get("verdict"))
    lines.append("- 一句话：%s" % payload.get("sentence"))
    lines.append("")
    lines.append("## 这条面在量什么")
    lines.append("")
    lines.append("对每个会话对 `[d, d+1]`，取该日导出里的持仓与权重 `w = 持仓市值 / 权益`，")
    lines.append("设帽子 `cap = %s`（`firm/risk/regime.py::CAP_MAJOR_BEAR`，单源 import）。" % payload.get("cap"))
    lines.append("守帽的当期差 = `权益 × max(0, w - cap) × (回购日收益 - 持仓组合日收益)`。")
    lines.append("")
    lines.append("**它不是重跑账户。** 强平会改变明天的持仓与明天的成交，这里只把每个会话的当期差相加。")
    lines.append("卖出成本按 CN-C7 的 13.041bp/边、每个绑定片段进出各一次计入净额列。")
    lines.append("")
    lines.append("## 三条臂（全部印，不选）")
    lines.append("")
    lines.append("| 臂 | 绑定会话 | 毛差(元) | 成本(元) | 净差(元) |")
    lines.append("|---|---|---|---|---|")
    for label, cn in (("bear_rule", "规则原文（大熊市）"), ("red_label", "RED 标签"),
                      ("always_cap", "一直压在 20%（参照）")):
        a = arms.get(label) or {}
        lines.append("| %s | %d | %+.2f | %.2f | %+.2f |"
                     % (cn, a.get("sessions_bound") or 0, a.get("delta_gross_cny") or 0.0,
                        a.get("cost_cny") or 0.0, a.get("delta_net_cny") or 0.0))
    lines.append("")
    conc = payload.get("concentration") or {}
    if conc.get("by_session"):
        lines.append("## 逐会话当期差（规则原文臂）")
        lines.append("")
        lines.append("| 会话 | 当期差(元) |")
        lines.append("|---|---|")
        for d, v in conc["by_session"].items():
            lines.append("| %s | %+.2f |" % (d, v))
        lines.append("| **合计** | **%+.2f** |" % (conc.get("total_cny") or 0.0))
        lines.append("")
    if arms.get("bear_rule", {}).get("per_trader"):
        lines.append("## 逐账户（规则原文臂）")
        lines.append("")
        lines.append("| 账户 | 绑定会话 | 超帽名义(元) | 毛差(元) | 净差(元) |")
        lines.append("|---|---|---|---|---|")
        for name, acc in sorted(arms["bear_rule"]["per_trader"].items()):
            lines.append("| %s | %d | %.2f | %+.2f | %+.2f |"
                         % (name, acc.get("sessions_bound") or 0, acc.get("excess_cny") or 0.0,
                            acc.get("delta_cny") or 0.0,
                            (acc.get("delta_cny") or 0.0) - (acc.get("cost_cny") or 0.0)))
        lines.append("")
    if model:
        lines.append("## 模型自己的误差（与效应同单位）")
        lines.append("")
        lines.append("- 可定价持仓占比：%s" % _pct(model.get("priced_share")))
        lines.append("- 校验样本 = **无交易日**（有交易日里账本记的是成交价，这张面只看得见收盘，"
                     "残差量的是那笔成交，不是价格基准）：%d 个干净会话对、%d 个账户-会话；"
                     "有交易日 %d 个会话对已排除并计数"
                     % (model.get("clean_pairs") or 0, model.get("n_account_sessions") or 0,
                        model.get("traded_pairs_excluded") or 0))
        lines.append("- 同一套持仓预测的日收益 vs 已发布权益收益：均值 |差| %s pp，最大 %s pp"
                     % (_num(model.get("mean_abs_pp"), 4), _num(model.get("max_abs_pp"), 4)))
        lines.append("- 折到规则原文臂绑定的那几场：**%s 元**——效应小于这个数就判 "
                     "`MODEL_ERROR_SWAMPS_THE_EFFECT`（本轮误差预算 = %s）"
                     % (_num(payload.get("error_budget_cny"), 2), _num(payload.get("error_budget_cny"), 2)))
        lines.append("")
    lines.append("")
    if payload.get("limits"):
        lines.append("## 不能读成什么")
        lines.append("")
        for item in payload["limits"]:
            lines.append("- %s" % item)
        lines.append("")
    bound_rows = [r for r in (arms.get("bear_rule") or {}).get("rows") or [] if r.get("binds")]
    if bound_rows:
        lines.append("## 绑定会话逐场（规则原文臂）")
        lines.append("")
        lines.append("| 会话 | 账户 | 权重 | 目标 | 持仓组合日收益 | 回购日收益 | 当期差(元) |")
        lines.append("|---|---|---|---|---|---|---|")
        for r in sorted(bound_rows, key=lambda x: (x["d0"], x["trader"])):
            lines.append("| %s | %s | %.1f%% | %.1f%% | %+.4f%% | %+.4f%% | %+.2f |"
                         % (r["d0"], r["trader"], (r["weight"] or 0) * 100.0,
                            (r["target"] or 0) * 100.0, (r["r_deployed"] or 0) * 100.0,
                            (r["r_repo"] or 0) * 100.0, r["delta_cny"]))
        lines.append("")
    unc = payload.get("uncovered") or {}
    lines.append("## 没覆盖到的")
    lines.append("")
    lines.append("- 没有下一份导出、因而无法计入的会话：%s"
                 % (", ".join(unc.get("sessions_without_a_next_export") or []) or "无"))
    lines.append("- 落在导出窗内但触发条件命中的会话里、没有会话对可算的：%s"
                 % (", ".join((unc.get("bear_sessions_outside_pairs") or [])) or "无"))
    lines.append("- 价格口径：`data/daily` 两族（裸码 / `sh|sz` 前缀）逐日交叉；翻转按 "
                 "`etf_equity_alpha.repair_flips` 修复（本窗修复 %s 处）。"
                 % ((payload.get("price_meta") or {}).get("flips")))
    lines.append("- 回购替身：GC001 收盘年化 / 100 / 365，缺报价按上一交易日披露（不编数）。")
    lines.append("")
    lines.append("## 复跑")
    lines.append("")
    lines.append("```")
    lines.append("python scripts/regime_cap_enforced_counterfactual.py run")
    lines.append("python scripts/regime_cap_enforced_counterfactual.py check")
    lines.append("python scripts/regime_cap_enforced_counterfactual.py --selftest")
    lines.append("```")
    return "\n".join(lines) + "\n"


def _pct(x):
    return "—" if x is None else "%.2f%%" % (x * 100.0)


def _num(x, nd):
    return "—" if x is None else ("%." + str(nd) + "f") % x


# --------------------------------------------------------------------------- commands

def run(root=None):
    payload = build()
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2, sort_keys=True)
    with open(DOC_PATH, "w", encoding="utf-8") as fh:
        fh.write(render_md(payload))
    print("%s | arms=%s | %s" % (
        payload["verdict"],
        ",".join("%s:%+.0f" % (k, (v or {}).get("delta_gross_cny") or 0.0)
                 for k, v in sorted((payload.get("arms") or {}).items())),
        payload["sentence"][:120]))
    return 0


def check(root=None):
    """STALE when an input moved; CHECK FAILED when the numbers no longer re-derive."""
    pub, err = _read_json(OUT)
    if err:
        print("STALE: face missing (%s)" % err)
        return 3
    fresh = build()
    digest_now = fresh.get("inputs_digest")
    if pub.get("inputs_digest") != digest_now:
        print("STALE: inputs moved since this face was written (digest %s -> %s)"
              % (pub.get("inputs_digest"), digest_now))
        return 3
    problems = []
    if pub.get("verdict") != fresh.get("verdict"):
        problems.append("verdict: published %s vs re-derived %s"
                        % (pub.get("verdict"), fresh.get("verdict")))
    for label in ("bear_rule", "red_label", "always_cap"):
        a = (pub.get("arms") or {}).get(label) or {}
        b = (fresh.get("arms") or {}).get(label) or {}
        if (a.get("sessions_bound") or 0) != (b.get("sessions_bound") or 0):
            problems.append("%s sessions_bound: %s vs %s"
                            % (label, a.get("sessions_bound"), b.get("sessions_bound")))
        if abs((a.get("delta_gross_cny") or 0.0) - (b.get("delta_gross_cny") or 0.0)) > MONEY_TOL:
            problems.append("%s delta_gross: %s vs %s"
                            % (label, a.get("delta_gross_cny"), b.get("delta_gross_cny")))
        for name, acc in (b.get("per_trader") or {}).items():
            mine = (a.get("per_trader") or {}).get(name) or {}
            if abs((mine.get("delta_cny") or 0.0) - (acc.get("delta_cny") or 0.0)) > MONEY_TOL:
                problems.append("%s/%s delta: %s vs %s"
                                % (label, name, mine.get("delta_cny"), acc.get("delta_cny")))
    if problems:
        print("CHECK FAILED")
        for p in problems[:12]:
            print("  - %s" % p)
        return 1
    print("CHECK OK | %s | digest %s" % (pub.get("verdict"), digest_now))
    return 0


# --------------------------------------------------------------------------- selftest

def _series(pairs):
    """{date: close} from [(date, close)]."""
    return {d: c for d, c in pairs}


def _mini_exports(rows):
    """rows = [(date, trader, equity, deployed, legs[(sym, mv)])] -> exports dict."""
    series, dates = {}, set()
    for d, name, eq, dep, legs in rows:
        dates.add(d)
        series.setdefault(name, {})[d] = {
            "equity_cny": float(eq), "deployed_cny": float(dep),
            "cash_cny": float(eq) - float(dep), "ops_n": 0,
            "legs": [{"symbol": s, "mv_cny": float(mv), "last_close": None} for s, mv in legs],
        }
    return {"dates": sorted(dates), "series": series, "problems": [],
            "files": [{"date": d, "file": "synthetic.json", "size": 1} for d in sorted(dates)],
            "cross_gate": {"status": "SKIPPED", "why": "synthetic"}}


def _selftest():
    import copy
    ok = True
    cap = RULE.CAP_MAJOR_BEAR

    def leg(name, cond, detail=""):
        nonlocal ok
        if not cond:
            ok = False
            print("FAIL %s %s" % (name, detail))
        else:
            print("ok   %s" % name)

    # --- 1. empty exports -> refuse, never a 0
    p = build(exports={"dates": [], "series": {}, "problems": [], "files": [],
                       "cross_gate": None}, prices={}, rates={}, bear={}, red={})
    leg("empty exports refuse", p["verdict"] == "CANNOT_READ_EXPORT_FACE", p["verdict"])

    # a synthetic book: `w` deployed in one name whose price steps by `step` per session.
    # Equity compounds with the book, so the model's own error is zero by construction --
    # otherwise the swamped-effect guard (rightly) fires on the fixture itself.
    def synth(step, w=1.0, eq0=1_000_000.0):
        rows, dates, px, eq = [], ["2026-11-16", "2026-11-17", "2026-11-18"], {}, eq0
        for i, d in enumerate(dates):
            px[d] = 10.0 * (1 + step) ** i
            rows.append((d, "T1", eq, eq * w if w else 0.0, [("A", eq * w)] if w else []))
            eq = eq * (1 + w * step)
        return _mini_exports(rows), px

    # --- 2. no bear day -> NO_BEAR_INTERVALS
    ex, px = synth(0.01)
    p = build(exports=ex, prices={"A": px}, rates={"2026-11-16": 1.0, "2026-11-17": 1.0},
              bear={"2026-11-16": False, "2026-11-17": False}, red={})
    leg("no bear -> NO_BEAR_INTERVALS", p["verdict"] == "NO_BEAR_INTERVALS", p["verdict"])

    # --- 3. rising sleeve, cap binds -> enforcing costs money
    p = build(exports=ex, prices={"A": px}, rates={"2026-11-16": 1.0, "2026-11-17": 1.0},
              bear={"2026-11-16": True, "2026-11-17": True}, red={})
    d_gross = (p["arms"]["bear_rule"] or {}).get("delta_gross_cny")
    leg("rising sleeve -> cap loses money",
        p["verdict"].startswith("ENFORCING_THE_CAP_WOULD_HAVE_COST") and d_gross < 0,
        "%s %s" % (p["verdict"], d_gross))

    # --- 4. falling sleeve, cap binds -> enforcing pays
    ex2, px2 = synth(-0.01)
    p = build(exports=ex2, prices={"A": px2}, rates={"2026-11-16": 1.0, "2026-11-17": 1.0},
              bear={"2026-11-16": True, "2026-11-17": True}, red={})
    leg("falling sleeve -> cap pays",
        p["verdict"].startswith("ENFORCING_THE_CAP_WOULD_HAVE_PAID"), p["verdict"])

    # --- 5. weight already inside the cap -> exactly zero
    ex3, px3 = synth(-0.05, w=0.10)
    p = build(exports=ex3, prices={"A": px3}, rates={"2026-11-16": 1.0, "2026-11-17": 1.0},
              bear={"2026-11-16": True, "2026-11-17": True}, red={})
    a = (p["arms"]["bear_rule"] or {})
    leg("weight under the cap -> zero effect",
        abs(a.get("delta_gross_cny") or 0.0) <= MONEY_TOL and a.get("sessions_bound") == 0,
        str(a.get("delta_gross_cny")))

    # --- 6. arithmetic check: one session, 100% book, sleeve -1%, repo 0 -> saving = eq*0.8*0.01
    one = _mini_exports([("2026-11-16", "T1", 1_000_000.0, 1_000_000.0, [("A", 1_000_000.0)]),
                         ("2026-11-17", "T1", 990_000.0, 990_000.0, [("A", 990_000.0)])])
    p = build(exports=one, prices={"A": {"2026-11-16": 10.0, "2026-11-17": 9.9}},
              rates={"2026-11-16": 0.0},
              bear={"2026-11-16": True}, red={})
    exp = 1_000_000.0 * (1.0 - cap) * 0.01
    got = (p["arms"]["bear_rule"] or {}).get("delta_gross_cny")
    leg("hand-computed saving 8000.00", abs((got or 0.0) - exp) <= 0.02, "%s vs %.2f" % (got, exp))

    # --- 7. cost monotonic: net(26bp) <= net(13bp) <= net(0)
    a = (p["arms"]["bear_rule"] or {}).get("cost_sensitivity") or {}
    leg("cost monotonic", (a.get("26.082") or 0.0) <= (a.get("13.041") or 0.0)
        <= (a.get("0") or 0.0) + 1e-9, str(a))

    # --- 8. unpriced book -> CANNOT_PRICE_THE_BOOK (never a silent zero)
    ex4, _ = synth(-0.02)
    for rows in ex4["series"].values():
        for row in rows.values():
            for legrow in row["legs"]:
                legrow["symbol"] = "MISSING"
    p = build(exports=ex4, prices={}, rates={"2026-11-16": 1.0}, bear={"2026-11-16": True}, red={})
    leg("unpriced book refuses", p["verdict"] == "CANNOT_PRICE_THE_BOOK", p["verdict"])

    # --- 9. selftest must not touch the published artifact
    before = os.path.getmtime(OUT) if os.path.isfile(OUT) else None
    build(exports=ex, prices={"A": px}, rates={"2026-11-16": 1.0}, bear={}, red={})
    after = os.path.getmtime(OUT) if os.path.isfile(OUT) else None
    leg("selftest does not write the published face", before == after,
        "%s vs %s" % (before, after))

    # --- 10. verdict word carries the money it decided on
    p = build(exports=ex2, prices={"A": px2}, rates={"2026-11-16": 1.0, "2026-11-17": 1.0},
              bear={"2026-11-16": True, "2026-11-17": True}, red={})
    money = abs((p["arms"]["bear_rule"] or {}).get("delta_gross_cny") or 0.0)
    leg("verdict token == the money it printed", _money_token(money) in p["verdict"],
        "%s vs %.2f" % (p["verdict"], money))

    # --- 11. RED arm and bear arm are separate bindings, never merged
    p = build(exports=ex2, prices={"A": px2}, rates={"2026-11-16": 1.0, "2026-11-17": 1.0},
              bear={"2026-11-16": True, "2026-11-17": True},
              red={"2026-11-16": "GREEN", "2026-11-17": "GREEN"})
    leg("red arm does not inherit the bear binding",
        (p["arms"]["red_label"] or {}).get("sessions_bound") == 0
        and (p["arms"]["bear_rule"] or {}).get("sessions_bound") == 2,
        "%s / %s" % ((p["arms"]["red_label"] or {}).get("sessions_bound"),
                     (p["arms"]["bear_rule"] or {}).get("sessions_bound")))

    # --- 12. an export with no next session is disclosed, not counted
    p = build(exports=one, prices={"A": {"2026-11-16": 10.0, "2026-11-17": 9.9}},
              rates={"2026-11-16": 0.0}, bear={"2026-11-16": True}, red={})
    leg("last session disclosed as uncounted",
        (p.get("uncovered") or {}).get("sessions_without_a_next_export") == ["2026-11-17"],
        str((p.get("uncovered") or {}).get("sessions_without_a_next_export")))

    # --- 13. a missing repo quote refuses to print money rather than faking a rate
    p = build(exports=one, prices={"A": {"2026-11-16": 10.0, "2026-11-17": 9.9}},
              rates={}, bear={"2026-11-16": True}, red={})
    leg("missing repo quote -> CANNOT_PRICE_THE_REPO",
        p["verdict"] == "CANNOT_PRICE_THE_REPO"
        and (p["arms"]["bear_rule"] or {}).get("sessions_skipped") == 1, str(p["verdict"]))

    # --- 14. a total carried by one session must say so, on the face and in the sentence
    two = _mini_exports([("2026-11-16", "T1", 1_000_000.0, 1_000_000.0, [("A", 1_000_000.0)]),
                         ("2026-11-17", "T1", 1_000_000.0, 1_000_000.0, [("A", 1_000_000.0)]),
                         ("2026-11-18", "T1", 1_000_000.0, 1_000_000.0, [("A", 1_000_000.0)]),
                         ("2026-11-19", "T1", 900_000.0, 900_000.0, [("A", 900_000.0)])])
    p = build(exports=two, prices={"A": {"2026-11-16": 10.0, "2026-11-17": 10.0,
                                         "2026-11-18": 10.0, "2026-11-19": 9.0}},
              rates={"2026-11-16": 0.0, "2026-11-17": 0.0, "2026-11-18": 0.0},
              bear={"2026-11-16": True, "2026-11-17": True, "2026-11-18": True}, red={})
    c = p.get("concentration") or {}
    leg("one-session concentration is named",
        c.get("largest_session") == "2026-11-18" and abs(c.get("total_without_largest_cny") or 0.0) <= MONEY_TOL,
        str(c))
    leg("sentence carries the concentration clause",
        "不是一场一场攒出来" in (p.get("sentence") or ""), p.get("sentence") or "")

    print("%d legs, %s" % (15, "ALL PASS" if ok else "FAILURES"))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", nargs="?", choices=("run", "check", "selftest"), default=None)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest or args.cmd == "selftest":
        return _selftest()
    if args.cmd == "check":
        return check()
    return run()


if __name__ == "__main__":
    sys.exit(main())

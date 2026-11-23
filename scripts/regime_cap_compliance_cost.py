"""Selling down to the RED cap is not a compliance formality -- it is a naked bet, and this face prices both sides.

The live page says two things on the same day: the market clock is RED and the ladder caps
equity exposure at 20%, and three of the six governed paper accounts are far above it
(COMPOSITE-CE-01 at 95.9%, COMPOSITE-CE-02 at 85.2%, VOLATILITY-CE-01 at 35.4%).  The
published face (`scripts/regime_cap_vs_book.py`) answers *whether* they are above and by how
much in CNY, and it says the honest thing about the rule: the cap gates new entries and does
not force a sale.  What it does not do is price the action.

So the reader is left holding "1,527,342 元 above the cap" with no way to tell whether
complying is expensive, free, or a bet.  This face answers in cash:

  1. what would have to be sold, per account and in total (re-derived here and gated against
     the published face: the numbers must be the same, not merely similar);
  2. what the sale costs -- the unrealized P&L it crystallises (pro-rata across the account's
     own published holdings) and the one-way sell cost at the desk's single-source fee
     schedule (`knowledge.cost_spec`, 13.041 bp; never re-typed here);
  3. what the sale buys -- loss avoided at -5 / -10 / -20 / -30% on the equity sleeve, and the
     break-even drop (which is exactly the one-way rate: a sale of X pays for itself once the
     sleeve falls further than the fee);
  4. what it gives up -- the expected return on the excess, printed as a labelled assumption
     and never folded into a "net" number as if it were measured;
  5. what the accounts' own published history says about the cap ever binding: the daily
     export series is read day by day and each account's deployed weight is compared with
     TODAY's 20% ladder, and the face says out loud that this is today's ruler applied to
     past days, because the historical ladder is not on any face.

Verdicts (frozen before the first run):

  NOTHING_ABOVE_CAP_TODAY                         no governed account is above the ladder
  CANNOT_PRICE_EVERY_ABOVE_CAP_ACCOUNT            an above-cap account has no export row or no
                                                  holdings -- printed as unpriced, never as zero
  FACES_ARE_ONE_GENERATION_APART                  the cap face and the holdings face are dated
                                                  differently; the sale is not priced at all
  FEE_IS_SMALLER_THAN_A_DAY_THESE_ACCOUNTS_HAVE_ALREADY_HAD
  FEE_IS_LARGER_THAN_A_DAY_THESE_ACCOUNTS_HAVE_ALREADY_HAD
  NO_HISTORY_TO_COMPARE_THE_FEE_WITH

  history: ABOVE_TODAYS_CAP_ON_EVERY_PUBLISHED_DAY / ABOVE_TODAYS_CAP_ON_MOST_PUBLISHED_DAYS
           / ABOVE_TODAYS_CAP_ON_A_MINORITY_OF_PUBLISHED_DAYS / NO_HISTORY

Reads published faces only (cap face, daily export series, cost single source).  Writes its own
new json + md.  Books nothing, changes no rule, makes no recommendation: the verdict says what
the trade costs and what it buys, and names the direction as a bet instead of a duty (r98 family:
an absent input is "cannot answer", never a zero).

  python scripts/regime_cap_compliance_cost.py            # build + write json/md
  python scripts/regime_cap_compliance_cost.py check      # re-derive and compare (STALE if inputs moved)
  python scripts/regime_cap_compliance_cost.py selftest   # hermetic legs
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
import shutil
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (ROOT, os.path.join(ROOT, "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from knowledge import cost_spec                              # noqa: E402  single-source fee schedule

SCHEMA = "regime_cap_compliance_cost_v1"
REL_CAP_FACE = "results/regime_cap_vs_book.json"
REL_EXPORT_LATEST = "results/paper_export/latest.json"
REL_EXPORT_GLOB = "results/paper_export/export-*.json"
REL_JSON = "results/regime_cap_compliance_cost.json"
REL_MD = "research/CAP-COMPLIANCE-COST.md"

OUT_JSON = os.path.join(ROOT, *REL_JSON.split("/"))
OUT_MD = os.path.join(ROOT, *REL_MD.split("/"))

SHOCKS = (0.05, 0.10, 0.20, 0.30)
# A return the desk has NOT measured on this excess; printed as an assumption, never mixed
# into a "net" line.  10%/yr is the book's own long-run equity sleeve order of magnitude.
ASSUMED_EXCESS_RETURN = 0.10
SELL_RATE = float(cost_spec.X1_SELL_RATE)          # 13.041 bp, one way
CASH_EPS = 0.01


# ---------------------------------------------------------------- helpers

def _load(path):
    import io
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _money(x):
    return None if x is None else round(float(x), 2)


def _pct(x):
    return None if x is None else round(float(x) * 100.0, 4)


def price_sale(deployed, equity, excess, positions, sell_rate, shocks=SHOCKS):
    """What the sale costs and what it buys.  Pure arithmetic, no reads (selftest drives this)."""
    out = {
        "deployed_cny": _money(deployed),
        "equity_cny": _money(equity),
        "excess_cny": _money(excess),
        "sell_cost_cny": _money(excess * sell_rate),
        "sell_cost_bp_of_excess": round(sell_rate * 1e4, 3),
        "breakeven_drop_pct": round(sell_rate * 100.0, 6),
        "loss_avoided_cny": {"-%g%%" % (s * 100.0): _money(excess * s) for s in shocks},
        "excess_foregone_cny_per_year": _money(excess * ASSUMED_EXCESS_RETURN),
        "assumed_excess_return_used": ASSUMED_EXCESS_RETURN,
    }
    if deployed and deployed > 0:
        share = excess / deployed
        out["share_of_positions_sold"] = round(share, 6)
        out["crystallized_pnl_cny"] = _money(
            sum(float(p.get("unrealized_pnl_cny") or 0.0) for p in positions) * share)
    else:
        # no positions means the excess cannot be located in a holding: answer "cannot price",
        # never 0 (r98 family).
        out["share_of_positions_sold"] = None
        out["crystallized_pnl_cny"] = None
    return out


def decide(accounts_above, unpriceable, own_range_pct, sell_rate):
    if not accounts_above and not unpriceable:
        return "NOTHING_ABOVE_CAP_TODAY"
    if unpriceable:
        return "CANNOT_PRICE_EVERY_ABOVE_CAP_ACCOUNT"
    if own_range_pct is None:
        return "NO_HISTORY_TO_COMPARE_THE_FEE_WITH"
    if sell_rate * 100.0 < own_range_pct:
        return "FEE_IS_SMALLER_THAN_A_DAY_THESE_ACCOUNTS_HAVE_ALREADY_HAD"
    return "FEE_IS_LARGER_THAN_A_DAY_THESE_ACCOUNTS_HAVE_ALREADY_HAD"


def decide_history(rows):
    """rows = [(days_above_todays_cap, days_published)] -- was the cap ever the binding ruler?"""
    rows = [r for r in rows if r]
    if not rows or any(d <= 0 for _, d in rows):
        return "NO_HISTORY"
    if all(a == d for a, d in rows):
        return "ABOVE_TODAYS_CAP_ON_EVERY_PUBLISHED_DAY"
    if any(a * 2 >= d for a, d in rows):
        return "ABOVE_TODAYS_CAP_ON_MOST_PUBLISHED_DAYS"
    return "ABOVE_TODAYS_CAP_ON_A_MINORITY_OF_PUBLISHED_DAYS"


def _export_history():
    """[(date, traders_by_name)] from the daily export series, deduped by export_date."""
    by_date = {}
    for p in sorted(glob.glob(os.path.join(ROOT, *REL_EXPORT_GLOB.split("/")))):
        try:
            d = _load(p)
        except Exception:
            continue
        day = d.get("export_date") or d.get("evidence_cutoff")
        if not day:
            continue
        by_date[day] = d
    return [(day, {t.get("trader"): t for t in (by_date[day].get("traders") or [])})
            for day in sorted(by_date)]


def _fee_components():
    """The parts of the single-source sell rate, in bp -- printed so the reader sees what it is."""
    try:
        f = cost_spec.FeeSchedule()
    except Exception:
        return None
    def bp(name):
        v = getattr(f, name, None)
        return None if v is None else round(float(v) * 1e4, 3)
    return {"commission_bp": bp("commission_rate"), "handling_bp": bp("handling_fee"),
            "supervision_bp": bp("supervision_fee"), "slippage_bp": bp("slippage_a")}


def _history_digest(history):
    """A digest of the daily export series: date + bytes, so a new or rewritten day is STALE."""
    pairs = []
    for day, _ in history:
        p = os.path.join(ROOT, "results", "paper_export", "export-%s.json" % day)
        pairs.append([day, _sha(p) if os.path.exists(p) else None])
    return hashlib.sha256(json.dumps(pairs, sort_keys=True).encode("utf-8")).hexdigest()


def _deployed_weight(trader):
    cap = (trader or {}).get("capital_cny") or {}
    equity = cap.get("equity")
    pv = cap.get("positions_value")
    if equity in (None, 0):
        return None
    return float(pv or 0.0) / float(equity)


# ---------------------------------------------------------------- build

def build(write=False, quiet=False):
    t0 = time.time()
    cap_path = os.path.join(ROOT, *REL_CAP_FACE.split("/"))
    exp_path = os.path.join(ROOT, *REL_EXPORT_LATEST.split("/"))
    cap_face = _load(cap_path)
    export = _load(exp_path)

    cap = cap_face.get("ladder_cap")
    cap_date = cap_face.get("evidence_cutoff")
    exp_date = export.get("export_date") or export.get("evidence_cutoff")
    cap_rule = cap_face.get("ladder_rule")

    inputs = [{"path": REL_CAP_FACE, "sha256": _sha(cap_path)},
              {"path": REL_EXPORT_LATEST, "sha256": _sha(exp_path)}]
    history = _export_history()
    hist_digest = _history_digest(history)
    inputs.append({"path": "results/paper_export/export-*.json", "sha256": hist_digest,
                   "files": len(history)})

    traders = {t.get("trader"): t for t in (export.get("traders") or [])}
    above = [a for a in (cap_face.get("accounts") or [])
             if a.get("kind") == "ladder" and a.get("status") == "above_cap"]

    face = {
        "artifact": REL_JSON,
        "schema": SCHEMA,
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "evidence_cutoff": cap_date,
        "cap": {"ladder_cap": cap, "date": cap_date, "rule": cap_rule,
                "source": REL_CAP_FACE},
        "holdings": {"date": exp_date, "source": REL_EXPORT_LATEST},
        "sell_rate": {"rate": SELL_RATE, "bp": round(SELL_RATE * 1e4, 3),
                      "components_bp": _fee_components(),
                      "single_source": "knowledge.cost_spec.X1_SELL_RATE",
                      "note": "one way; a sale only. The schedule is the desk's stock cost "
                              "(commission+handling+supervision+slippage_a); an ETF-only sleeve "
                              "would cost less, so this is a ceiling."},
        "assumption": {"excess_expected_return_per_year": ASSUMED_EXCESS_RETURN,
                       "why": "printed as a labelled assumption; never measured on this excess"},
        "shocks": list(SHOCKS),
        "accounts_above_cap": len(above),
        "accounts": [],
        "unpriceable": [],
        "history": {"days_published": len(history),
                    "rows": [],
                    "below_days": [],
                    "ruler_warning": "过去各日的仓位一律用今天的 20% 帽子上限去读——任何面上都没有逐日的"
                                     "历史帽子，所以过去某一天是否超帽，不是按那一天的帽子判的"},
        "inputs": inputs,
    }

    if cap in (None, 0):
        face["verdict"] = "CANNOT_PRICE_EVERY_ABOVE_CAP_ACCOUNT"
        face["sentence"] = "这张帽子面没有给出阶梯上限，本面不知道该拿什么宽度去比，所以一笔也不定价。"
        face["elapsed_sec"] = round(time.time() - t0, 1)
        if write:
            _write(face)
        return face

    if cap_date and exp_date and cap_date != exp_date:
        face["verdict"] = "FACES_ARE_ONE_GENERATION_APART"
        face["sentence"] = ("帽子面读的是 %s 的账户，持仓面读的是 %s 的持仓——两代之间卖哪一笔都是拿"
                            "昨天的持仓去抵今天的帽子，所以本面一笔都不定价。" % (cap_date, exp_date))
        face["elapsed_sec"] = round(time.time() - t0, 1)
        if write:
            _write(face)
        return face

    total_excess = 0.0
    total_cost = 0.0
    total_crystal = 0.0
    total_avoided = {s: 0.0 for s in SHOCKS}
    own_range_max = 0.0
    have_range = False

    for a in sorted(above, key=lambda r: -float(r.get("excess_cny") or 0.0)):
        name = a.get("name")
        t = traders.get(name)
        cap_cny = (t or {}).get("capital_cny") or {}
        positions = (t or {}).get("open_positions") or []
        deployed = cap_cny.get("positions_value")
        equity = cap_cny.get("equity")
        if t is None or deployed in (None, 0):
            face["unpriceable"].append({"name": name, "why": "no holdings row on the export face"})
            continue
        excess = max(0.0, float(deployed) - float(cap) * float(equity))
        published = float(a.get("excess_cny") or 0.0)
        row = price_sale(float(deployed), float(equity), excess, positions, SELL_RATE)
        row["name"] = name
        row["published_excess_cny"] = _money(published)
        row["matches_published"] = abs(excess - published) <= CASH_EPS
        row["deployed_weight"] = round(float(deployed) / float(equity), 6) if equity else None
        row["deployed_weight_pct"] = _pct(row["deployed_weight"])
        # where the sale lands: the largest holdings carry the sale pro-rata
        top = sorted(positions, key=lambda p: -float(p.get("market_value_cny") or 0.0))[:3]
        row["largest_holdings"] = [
            {"symbol": p.get("symbol"),
             "market_value_cny": _money(p.get("market_value_cny")),
             "sold_in_this_plan_cny": _money(
                 float(p.get("market_value_cny") or 0.0) * (row["share_of_positions_sold"] or 0.0))}
            for p in top]
        face["accounts"].append(row)
        total_excess += excess
        total_cost += float(row["sell_cost_cny"] or 0.0)
        total_crystal += float(row["crystallized_pnl_cny"] or 0.0)
        for s in SHOCKS:
            total_avoided[s] += excess * s

    # the accounts' own published path, measured against today's ruler (labelled as such)
    for a in sorted(above, key=lambda r: -float(r.get("excess_cny") or 0.0)):
        name = a.get("name")
        days_above = days_pub = 0
        weights = []
        for day, by_name in history:
            w = _deployed_weight(by_name.get(name))
            if w is None:
                continue
            days_pub += 1
            weights.append((day, w))
            if w > float(cap) + 1e-12:
                days_above += 1
        if not weights:
            face["history"]["rows"].append({"name": name, "days_published": 0,
                                            "days_above_todays_cap": None,
                                            "first_day": None, "last_day": None,
                                            "first_weight_pct": None, "last_weight_pct": None})
            continue
        lo = min(weights, key=lambda t: t[1])
        below = [d for d, w in weights if w <= float(cap) + 1e-12]
        swing = {"pp": None, "from_day": None, "to_day": None}
        for (d0, w0), (d1, w1) in zip(weights, weights[1:]):
            if w0 and abs(w1 - w0) > abs((swing["pp"] or 0.0) / 100.0):
                swing = {"pp": round((w1 - w0) * 100.0, 4), "from_day": d0, "to_day": d1}
        face["history"]["rows"].append({
            "name": name,
            "days_published": days_pub,
            "days_above_todays_cap": days_above,
            "days_below_todays_cap": len(below),
            "below_days": below,
            "first_day": history[0][0] if history else None,
            "last_day": history[-1][0] if history else None,
            "first_weight_pct": _pct(weights[0][1]),
            "last_weight_pct": _pct(weights[-1][1]),
            "min_weight_pct": _pct(lo[1]),
            "min_weight_day": lo[0],
            "max_weight_pct": _pct(max(w for _, w in weights)),
            "largest_single_session_weight_swing_pp": swing["pp"],
            "swing_from_day": swing["from_day"],
            "swing_to_day": swing["to_day"],
        })
        # this account's own largest one-day equity move, from its published daily exports
        eqs = []
        for day, by_name in history:
            t = by_name.get(name)
            e = ((t or {}).get("capital_cny") or {}).get("equity")
            if e:
                eqs.append(float(e))
        for prev, cur in zip(eqs, eqs[1:]):
            if prev:
                own_range_max = max(own_range_max, abs(cur - prev) / prev * 100.0)
                have_range = True

    face["control"] = {
        "total_excess_cny": _money(total_excess),
        "published_total_excess_cny": _money(
            (cap_face.get("under_engine") or {}).get("total_excess_cny")),
        "per_account_matches": all(r["matches_published"] for r in face["accounts"]),
        "sum_matches_published": (
            abs(total_excess - float((cap_face.get("under_engine") or {}).get(
                "total_excess_cny") or 0.0)) <= CASH_EPS),
        "n_compared": len(face["accounts"]),
        "n_above_published": len(above),
    }
    face["totals"] = {
        "excess_cny": _money(total_excess),
        "sell_cost_cny": _money(total_cost),
        "crystallized_pnl_cny": _money(total_crystal),
        "loss_avoided_cny": {"-%g%%" % (s * 100.0): _money(v) for s, v in total_avoided.items()},
        "own_biggest_one_day_equity_move_pct": round(own_range_max, 4) if have_range else None,
    }
    # a control failure is a refusal to publish, never a number with a footnote
    if not (face["control"]["per_account_matches"] and face["control"]["sum_matches_published"]):
        raise SystemExit("FATAL: control arms failed against the published cap face: %s"
                         % json.dumps(face["control"], ensure_ascii=False))

    own_range = face["totals"]["own_biggest_one_day_equity_move_pct"]
    below_union = sorted({d for r in face["history"]["rows"] for d in (r.get("below_days") or [])})
    face["history"]["below_days"] = below_union
    face["history"]["below_days_count"] = len(below_union)
    face["verdict"] = decide(face["accounts"], face["unpriceable"], own_range, SELL_RATE)
    face["history"]["verdict"] = decide_history(
        [(r.get("days_above_todays_cap"), r.get("days_published"))
         for r in face["history"]["rows"]])

    face["sentence"] = _sentence(face)
    face["elapsed_sec"] = round(time.time() - t0, 1)
    if write:
        _write(face)
    if not quiet:
        print("verdict %s | history %s" % (face["verdict"], face["history"]["verdict"]))
        print(" excess %s CNY on %s account(s); fee %s CNY (%.3f bp); breakeven drop %.4f%%"
              % (face["totals"]["excess_cny"], len(face["accounts"]),
                 face["totals"]["sell_cost_cny"], SELL_RATE * 1e4, SELL_RATE * 100.0))
        print(" crystallized P&L %s CNY; the accounts' own biggest one-day equity move so far %s%%"
              % (face["totals"]["crystallized_pnl_cny"],
                 face["totals"]["own_biggest_one_day_equity_move_pct"]))
        for s, v in face["totals"]["loss_avoided_cny"].items():
            print("  a %s move on the sleeve: loss avoided %s CNY" % (s, v))
        print(" cap face %s vs holdings face %s -> %s"
              % (cap_date, exp_date, face["verdict"]))
    return face


def _sentence(face):
    tot = face.get("totals") or {}
    if face["verdict"] == "NOTHING_ABOVE_CAP_TODAY":
        return "今天没有一户站在 20% 帽子上方，这张面没有可卖的东西。"
    if face["verdict"] == "CANNOT_PRICE_EVERY_ABOVE_CAP_ACCOUNT":
        names = "、".join(u["name"] for u in face["unpriceable"])
        return ("站在帽子上方的账户里，%s 在持仓面上找不到可定价的持仓，所以这些户各卖多少元这笔账"
                "今天算不出来——不拿 0 顶替。" % names)
    n = len(face["accounts"])
    fee = tot["sell_cost_cny"]
    cry = tot["crystallized_pnl_cny"]
    be = face["accounts"][0]["breakeven_drop_pct"] if face["accounts"] else None
    own = tot["own_biggest_one_day_equity_move_pct"]
    days = (face.get("history") or {}).get("days_published")
    return ("把 %d 户卖回 20%% 帽子要动 %s 元：手续费 %s 元（%.3f bp），同时把账上 %s 元的%s落成实%s"
            "（这笔钱卖不卖都已经%s了，只是从账面变成实账）；它买到的是跌 %.4f%% 以上的保护——"
            "而同一批账户在自己 %s 个发布日里最大的一天净值波动就有 %s%%。所以这不是「手续费」问题，"
            "而是一个方向判断：跌超过 %.4f%% 就赚，涨回去就白让出那份仓位（按 %d%%/年假设，那份仓位一年 %s 元）。"
            % (n, f"{tot['excess_cny']:,.2f}", f"{fee:,.2f}", SELL_RATE * 1e4,
               f"{abs(float(cry or 0.0)):,.2f}", "浮亏" if (cry or 0) < 0 else "浮盈",
               "亏" if (cry or 0) < 0 else "盈", "亏" if (cry or 0) < 0 else "赚",
               be, days, own if own is not None else "（无历史）", be,
               int(ASSUMED_EXCESS_RETURN * 100),
               f"{tot['excess_cny'] * ASSUMED_EXCESS_RETURN:,.2f}"))


def _write(face):
    with open(OUT_JSON, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    write_md(face, OUT_MD)


def write_md(face, path):
    L = []
    A = L.append
    comp = (face.get("sell_rate") or {}).get("components_bp") or {}
    A("# 卖回 20% 帽子：要花多少钱，买到什么")
    A("")
    A("> 判词 **%s**（历史面 **%s**）· 证据截止 %s · 持仓面 %s"
      % (face["verdict"], face.get("history", {}).get("verdict"),
         face.get("evidence_cutoff"), (face.get("holdings") or {}).get("date")))
    A("")
    A(face.get("sentence") or "")
    A("")
    if face.get("accounts"):
        A("## 逐户账")
        A("")
        A("| 账户 | 仓位 | 超出帽子 | 卖出占比 | 落袋的浮盈/浮亏 | 手续费 |")
        A("| --- | --- | --- | --- | --- | --- |")
        for r in face["accounts"]:
            A("| %s | %s%% | %s | %s%% | %s | %s |"
              % (r["name"], r["deployed_weight_pct"], f"{r['excess_cny']:,.2f}",
                 round((r["share_of_positions_sold"] or 0) * 100, 2),
                 f"{r['crystallized_pnl_cny']:,.2f}", f"{r['sell_cost_cny']:,.2f}"))
        A("")
        A("## 两边价钱（合计）")
        A("")
        tot = face["totals"]
        A("- 卖出金额：**%s 元**（%.3f bp 手续费 = %s 元）"
          % (f"{tot['excess_cny']:,.2f}", SELL_RATE * 1e4, f"{tot['sell_cost_cny']:,.2f}"))
        A("- 顺手把未实现盈亏变成已实现：**%s 元**（不是新增亏损，是把账上的浮盈浮亏落袋）"
          % f"{tot['crystallized_pnl_cny']:,.2f}")
        for s, v in sorted(tot["loss_avoided_cny"].items(),
                           key=lambda kv: float(kv[0].strip("%"))):
            A("- 权益档跌 %s：少亏 **%s 元**" % (s, f"{v:,.2f}"))
        A("- 按 %d%%/年假设，让出的这份仓位一年值 **%s 元**（假设，不是本面测出来的数）"
          % (int(ASSUMED_EXCESS_RETURN * 100), f"{tot['excess_cny'] * ASSUMED_EXCESS_RETURN:,.2f}"))
        A("")
        A("## 为什么这不是一个「手续费」问题")
        A("")
        A("一次卖出的手续费是卖出金额的 %.3f bp，也就是 %.4f%%——所以卖出的**盈亏平衡点就是一次 %.4f%% 的下跌**："
          "只要权益档跌得比这个多，卖出在现金上就赚了。费用小到决定不了这件事，决定它的是方向。"
          % (SELL_RATE * 1e4, SELL_RATE * 100.0, SELL_RATE * 100.0))
        A("")
        A("费用里最大的那块不是佣金：佣金 %s bp、过户费 %s bp、监管 %s bp，真正拿大头的滑点 %s bp——"
          "滑点是成本表给的保守假设，不是本面实测出来的成交价差。"
          % (comp.get("commission_bp"), comp.get("handling_bp"),
             comp.get("supervision_bp"), comp.get("slippage_bp")))
        A("")
    if face.get("history", {}).get("rows"):
        A("## 这些账户自己有没有被帽子管住过")
        A("")
        A("| 账户 | 发布日 | 站在今日 20% 帽子上方的天数 | 首日仓位 | 末日仓位 | 区间最低（日） | 区间最高 |")
        A("| --- | --- | --- | --- | --- | --- | --- |")
        for r in face["history"]["rows"]:
            A("| %s | %s | %s | %s%% | %s%% | %s%%（%s） | %s%% |"
              % (r["name"], r["days_published"], r["days_above_todays_cap"],
                 r["first_weight_pct"], r["last_weight_pct"],
                 r.get("min_weight_pct"), r.get("min_weight_day"), r.get("max_weight_pct")))
        A("")
        A("> 口径警告：%s。" % face["history"]["ruler_warning"])
        swings = [r for r in face["history"]["rows"]
                  if r.get("largest_single_session_weight_swing_pp") is not None]
        if swings:
            big = max(swings, key=lambda r: abs(r["largest_single_session_weight_swing_pp"]))
            A(">")
            A("> 自有换手能力：%s 在一个交易日里把仓位挪过 %s pp（%s → %s）。"
              "所以「卖了就买不回来」不是这些账户的问题——它们自己的规则一个交易日就能把仓位搬这么远；"
              "帽子不强制卖出，是因为规则写的是「只挡新开仓」，不是因为这些户卖不动。"
              % (big["name"], big["largest_single_session_weight_swing_pp"],
                 big.get("swing_from_day"), big.get("swing_to_day")))
        if face["history"].get("below_days"):
            A(">")
            A("> 唯一低于帽子的发布日：%s（%d 户同日低于 20%%）。那天是真空仓还是快照读数，本面不知道，"
              "如实印出来而不是抹掉——上表「区间最低」就是那一天。"
              % ("、".join(face["history"]["below_days"]),
                 len([r for r in face["history"]["rows"] if r.get("below_days")])))
        A("")
    if face.get("unpriceable"):
        A("## 算不出来的")
        A("")
        for u in face["unpriceable"]:
            A("- %s：%s" % (u["name"], u["why"]))
        A("")
    A("## 诚实边界")
    A("")
    A("1. 帽子只挡新开仓、不强制卖出（已发布面 `results/regime_cap_vs_book.json` 的原话）；"
      "所以「卖回帽子」是一个**选择**，本面只给它标价，不说该不该做。")
    A("2. 卖出是**按仓位比例**摊到这户自己的持仓上；真要卖哪一只，取决于账户自己的规则，本面不替它选。")
    A("3. 手续费是桌上这套股票成本表（含滑点 %.0f bp 的保守值）；纯 ETF 的袖子实际更低，所以本面是上限口径。"
      % ((comp.get("slippage_bp") or 0.0)))
    A("4. 让出仓位的机会成本用的是 %d%%/年**假设**，没有在本账户上测过；真实期望收益本面不知道。"
      % int(ASSUMED_EXCESS_RETURN * 100))
    A("5. 历史段只用今天这把 20% 的尺子去读过去，因为任何面上都没有逐日的历史帽子；"
      "「过去某天该不该算超帽」本面不回答。")
    A("6. 这些是纸盘账户（观察账本），不是实盘持仓；本面不产生任何委托。")
    A("")
    A("## 复跑")
    A("")
    A("```")
    A("python scripts/regime_cap_compliance_cost.py            # 生成 json/md")
    A("python scripts/regime_cap_compliance_cost.py check      # 输入动=STALE、数字不符=CHECK FAILED")
    A("python scripts/regime_cap_compliance_cost.py selftest   # 离线腿")
    A("```")
    A("")
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(L).rstrip() + "\n")


# ---------------------------------------------------------------- check

def check(path=None, quiet=False):
    path = path or OUT_JSON
    if not os.path.exists(path):
        print("STALE: %s missing" % path)
        return 3
    pub = _load(path)
    stale = []
    for it in pub.get("inputs") or []:
        p = os.path.join(ROOT, *str(it.get("path") or "").split("/"))
        if not it.get("path"):
            stale.append("input path missing")
        elif "*" in str(it.get("path")):
            if _history_digest(_export_history()) != it.get("sha256"):
                stale.append("source bytes moved: %s" % it.get("path"))
        elif not os.path.exists(p):
            stale.append("source face missing: %s" % it.get("path"))
        elif _sha(p) != it.get("sha256"):
            stale.append("source bytes moved: %s" % it.get("path"))
    if stale:
        for s in stale:
            print("STALE: " + s)
        return 3
    fresh = build(write=False, quiet=True)
    diffs = _compare({k: v for k, v in pub.items() if k not in ("generated", "elapsed_sec")},
                     {k: v for k, v in fresh.items() if k not in ("generated", "elapsed_sec")})
    if diffs:
        for d in diffs[:25]:
            print("CHECK FAILED: " + d)
        return 1
    if not quiet:
        print("check ok: %d account(s) re-priced against %s, every printed number matches"
              % (len(pub.get("accounts") or []), pub.get("evidence_cutoff")))
    return 0


def _compare(a, b, prefix=""):
    out = []
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a:
                out.append("%s%s only in fresh" % (prefix, k))
            elif k not in b:
                out.append("%s%s only in published" % (prefix, k))
            else:
                out.extend(_compare(a[k], b[k], prefix + k + "."))
        return out
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append("%s length %d vs %d" % (prefix or "list", len(a), len(b)))
            return out
        for i, (x, y) in enumerate(zip(a, b)):
            out.extend(_compare(x, y, "%s[%d]." % (prefix, i)))
        return out
    if isinstance(a, float) or isinstance(b, float):
        if a is None or b is None:
            if a != b:
                out.append("%s %r vs %r" % (prefix or "value", a, b))
            return out
        try:
            if abs(float(a) - float(b)) > 5e-4:
                out.append("%s %r vs %r" % (prefix or "value", a, b))
        except (TypeError, ValueError):
            if a != b:
                out.append("%s %r vs %r" % (prefix or "value", a, b))
        return out
    if a != b:
        out.append("%s %r vs %r" % (prefix or "value", a, b))
    return out


# ---------------------------------------------------------------- selftest

def selftest():
    fails, ok = [], []

    def want(cond, leg, msg):
        (ok if cond else fails).append(leg if cond else "%s %s" % (leg, msg))

    # L1 pro-rata crystallisation
    pos = [{"unrealized_pnl_cny": 100.0}, {"unrealized_pnl_cny": -40.0}]
    r = price_sale(1000.0, 1200.0, 760.0, pos, 0.0013041)
    want(abs(r["crystallized_pnl_cny"] - 45.6) < 1e-9, "L1 pro-rata crystallisation",
         "got %r" % (r["crystallized_pnl_cny"],))

    # L2 excess arithmetic: at the cap there is nothing to sell; above it the excess is linear
    want(price_sale(200.0, 1000.0, 0.0, pos, 0.0013041)["excess_cny"] == 0.0,
         "L2 zero at the cap", "")
    r2 = price_sale(500.0, 1000.0, 300.0, [], 0.0013041)
    want(r2["excess_cny"] == 300.0 and r2["share_of_positions_sold"] == 0.6,
         "L2b linear excess and share", "got %r" % (r2,))

    # L3 break-even equals the one-way rate; two-sided
    a = price_sale(500.0, 1000.0, 300.0, [], 0.0013041)
    b = price_sale(500.0, 1000.0, 300.0, [], 0.0)
    want(abs(a["breakeven_drop_pct"] - 0.13041) < 1e-9 and b["breakeven_drop_pct"] == 0.0,
         "L3 break-even = one-way rate", "%r %r" % (a["breakeven_drop_pct"], b["breakeven_drop_pct"]))

    # L4 no positions is "cannot price", never zero (r98 family)
    r4 = price_sale(0.0, 1000.0, 0.0, [], 0.0013041)
    want(r4["crystallized_pnl_cny"] is None and r4["share_of_positions_sold"] is None,
         "L4 no holdings -> cannot price", "got %r" % (r4,))

    # L5 loss avoided scales with the shock and with the excess
    r5 = price_sale(500.0, 1000.0, 300.0, [], 0.0013041)
    want(abs(r5["loss_avoided_cny"]["-10%"] - 30.0) < 1e-9
         and abs(r5["loss_avoided_cny"]["-20%"] - 60.0) < 1e-9,
         "L5 shock table linear", "got %r" % (r5["loss_avoided_cny"],))

    # L6 verdict matrix
    want(decide([], [], 1.0, 0.0013041) == "NOTHING_ABOVE_CAP_TODAY", "L6 nothing above", "")
    want(decide([{"name": "X"}], [{"name": "X"}], 1.0, 0.0013041)
         == "CANNOT_PRICE_EVERY_ABOVE_CAP_ACCOUNT", "L6b unpriceable wins", "")
    want(decide([{"name": "X"}], [], 1.0, 0.0013041)
         == "FEE_IS_SMALLER_THAN_A_DAY_THESE_ACCOUNTS_HAVE_ALREADY_HAD", "L6c fee below own range", "")
    want(decide([{"name": "X"}], [], 0.01, 0.0013041)
         == "FEE_IS_LARGER_THAN_A_DAY_THESE_ACCOUNTS_HAVE_ALREADY_HAD", "L6d fee above own range", "")
    want(decide([{"name": "X"}], [], None, 0.0013041)
         == "NO_HISTORY_TO_COMPARE_THE_FEE_WITH", "L6e no history", "")

    # L7 history verdict
    want(decide_history([(5, 5)]) == "ABOVE_TODAYS_CAP_ON_EVERY_PUBLISHED_DAY",
         "L7 above on every day", "")
    want(decide_history([(5, 6)]) == "ABOVE_TODAYS_CAP_ON_MOST_PUBLISHED_DAYS",
         "L7b above on most days", "")
    want(decide_history([(1, 6)]) == "ABOVE_TODAYS_CAP_ON_A_MINORITY_OF_PUBLISHED_DAYS",
         "L7c above on a minority", "")
    want(decide_history([(None, 0)]) == "NO_HISTORY", "L7d no days", "")

    # L8 the cap is read from the face, not typed in: a different ladder changes the excess
    r8a = price_sale(500.0, 1000.0, 500.0 - 0.20 * 1000.0, [], 0.0013041)
    r8b = price_sale(500.0, 1000.0, 500.0 - 0.50 * 1000.0, [], 0.0013041)
    want(abs(r8a["excess_cny"] - 300.0) < 1e-9 and r8b["excess_cny"] == 0.0,
         "L8 cap comes from the face", "%r %r" % (r8a["excess_cny"], r8b["excess_cny"]))

    # L9 determinism: same inputs -> byte-identical payload
    f1 = build(write=False, quiet=True)
    f2 = build(write=False, quiet=True)
    k = ("generated", "elapsed_sec")
    d1 = json.dumps({x: y for x, y in f1.items() if x not in k}, sort_keys=True, ensure_ascii=False)
    d2 = json.dumps({x: y for x, y in f2.items() if x not in k}, sort_keys=True, ensure_ascii=False)
    want(d1 == d2, "L9 deterministic build", "payloads differ")

    # L10 behaviour of check on a doctored copy: a changed number is CHECK FAILED (no STALE),
    # a changed input digest is STALE.  Drives the real check() on a real file.
    tmpd = tempfile.mkdtemp(prefix="capcost_")
    try:
        built = os.path.join(tmpd, "face.json")
        if os.path.exists(OUT_JSON):
            shutil.copy2(OUT_JSON, built)
        else:
            build(write=True, quiet=True)
            shutil.copy2(OUT_JSON, built)
        pub = _load(built)
        pub["totals"]["excess_cny"] = float(pub["totals"]["excess_cny"]) + 1.0
        with open(built, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(pub, fh, ensure_ascii=False, indent=1, sort_keys=True)
        import io as _io
        import contextlib
        buf = _io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc_bad = check(path=built, quiet=False)
        txt = buf.getvalue()
        want(rc_bad == 1 and "CHECK FAILED" in txt and "STALE" not in txt,
             "L10 a changed number is CHECK FAILED", "rc=%r txt=%r" % (rc_bad, txt[:200]))

        pub = _load(built)
        pub["totals"]["excess_cny"] = float(pub["totals"]["excess_cny"]) - 1.0
        for it in pub.get("inputs") or []:
            if it.get("sha256"):
                it["sha256"] = "0" * 64
                break
        with open(built, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(pub, fh, ensure_ascii=False, indent=1, sort_keys=True)
        buf = _io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc_stale = check(path=built, quiet=False)
        want(rc_stale == 3 and "STALE" in buf.getvalue(),
             "L10b a moved input is STALE", "rc=%r txt=%r" % (rc_stale, buf.getvalue()[:200]))
    finally:
        shutil.rmtree(tmpd, ignore_errors=True)

    print("selftest: %d/%d PASS" % (len(ok), len(ok) + len(fails)))
    for f in fails:
        print("  FAIL " + f)
    return 0 if not fails else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", nargs="?", default="run",
                    choices=("run", "check", "selftest"))
    a = ap.parse_args(argv)
    if a.cmd == "run":
        build(write=True)
        return 0
    if a.cmd == "check":
        return check()
    return selftest()


if __name__ == "__main__":
    raise SystemExit(main())

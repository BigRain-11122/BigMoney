"""Can the 12-name card actually be placed at 1,000,000 CNY?  Whole lots, a 5 CNY ticket floor.

The card (`scripts/etf_book_production.py`) publishes twelve weights and a yuan/share order
sheet.  The ticket (`scripts/etf_book_order.py`) prices it.  Both quote a capital, and until
this face existed nothing took the last step: for every one of the twelve names, is the slice
big enough to be a legal order at all?

That is a different question from the small-account ladder (`etf_book_lot_ladder.py`, which
asks how small an account can be before friction bites).  Here the account is fixed at the
capital the sheet states and the question is per name:

  * one lot is 100 shares; a name whose ONE-LOT price exceeds its slice cannot be bought,
    and that slice stays in cash -- so the executed book is not the published book
  * commission has a 5 CNY floor per ticket, which at a 75,000 CNY slice is negligible but
    at a 3,000 CNY slice is not

Frozen judgement (written before the reading, not tuned to it):

  FLOOR_CAPITAL      min over legs is not the question -- the binding name is the one with
                     the largest (one_lot / weight): at that capital every name can buy at
                     least one lot.  Reported as `floor.min_capital_cny` with the name.
  TRADABLE_AT_<C>    at the stated capital (a) every leg gets at least one lot, (b) nobody
                     is unfilled, and (c) the whole-lot residual is <= 0.5% of NAV.  The
                     residual bound is the point: a book that fits but strands 8% in cash
                     is not the published book either.
  BELOW_FLOOR_AT_<C> at least one leg cannot buy a single lot -- the sheet is not placeable
                     at that capital, and the face names the legs.
  TICKET_MISSING     no ticket on disk: the face refuses rather than inventing one.

The capital multiple (stated / floor) is printed so a reader can see how much headroom there
is, and the residual is printed in yuan, not only in percent.

The second block is the path question, and it is deliberately labelled as a DIFFERENT book:
`etf_book_lot_ladder.lot_equity` run at n_hold=12 on the full panel (no class filter, no 8%
vol target) once with whole lots + fee floor and once with 1-share lots and no floor.  The
gap between the two is what lots cost at 1M for a twelve-name book; it bounds the card's own
friction but does not restate the card (the card's configuration differs and is named).

Usage:
    python scripts/etf_book_ticket_floor.py run [--capital=1000000]
    python scripts/etf_book_ticket_floor.py --selftest
    python scripts/etf_book_ticket_floor.py --check
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import etf_book_lot_ladder as L

OUT_JSON = os.path.join(ROOT, "results", "etf_book_ticket_floor.json")
OUT_MD = os.path.join(ROOT, "research", "ETF_BOOK_TICKET_FLOOR.md")
TICKET_GLOB = os.path.join(ROOT, "results", "etf_book_order", "TICKET-*-card.json")

LOT = 100
FEE_FLOOR = 5.0
COST = 0.0010
RESIDUAL_MAX_PCT = 0.50      # frozen: whole-lot residue as % of NAV


def newest_ticket(pattern=TICKET_GLOB):
    files = sorted(glob.glob(pattern), key=os.path.getmtime)
    return files[-1] if files else None


def load_ticket(path):
    if not path or not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def leg_rows(ticket, capital):
    """One row per leg: what the sheet asks for, what one lot costs, what fits."""
    rows = []
    for leg in ticket.get("order") or []:
        px = leg.get("price")
        w = float(leg.get("weight") or 0.0)
        budget = capital * w
        one_lot = LOT * float(px) if px else None
        lots = int(budget // one_lot) if one_lot and one_lot > 0 else 0
        shares = lots * LOT
        amount = shares * float(px) if px else 0.0
        fee = max(FEE_FLOOR, amount * COST) if amount > 0 else 0.0
        rows.append({
            "symbol": leg.get("symbol"), "name": leg.get("name"),
            "class": leg.get("class"), "weight": round(w, 6),
            "price": round(float(px), 4) if px else None,
            "budget_cny": round(budget, 2),
            "one_lot_cny": round(one_lot, 2) if one_lot else None,
            "lots": lots, "shares": shares,
            "amount_cny": round(amount, 2),
            "fee_cny": round(fee, 2),
            "residual_cny": round(budget - amount, 2),
            "fits": lots >= 1,
        })
    return rows


def floor_capital(rows):
    """Smallest capital at which every leg can buy at least one lot.

    For a leg, capital * weight >= one_lot  =>  capital >= one_lot / weight.  The binding name
    is the maximum of that ratio over the legs.  A weight of zero cannot buy anything and is
    reported as unbuyable-by-weight rather than silently dropped.
    """
    ratios = []
    for r in rows:
        if not r.get("one_lot_cny") or not r.get("weight"):
            ratios.append({"symbol": r["symbol"], "needed_cny": None,
                           "why": "no price or zero weight"})
            continue
        ratios.append({"symbol": r["symbol"],
                       "needed_cny": round(r["one_lot_cny"] / r["weight"], 2)})
    usable = [x for x in ratios if x.get("needed_cny")]
    binding = max(usable, key=lambda x: x["needed_cny"]) if usable else None
    return {
        "min_capital_cny": binding["needed_cny"] if binding else None,
        "binding_symbol": binding["symbol"] if binding else None,
        "per_leg_needed_cny": ratios,
        "fee_floor_needs_cny": {"note": "5 CNY per ticket is inside the residual bound at any "
                                        "capital above the one-lot floor",
                                "max_extra_cny": round(FEE_FLOOR, 2)},
    }


def resolve(ticket, capital):
    """Derive the verdict from the ticket's own rows.  Pure: no file reads."""
    if ticket is None:
        return {"verdict": "TICKET_MISSING", "capital_cny": capital, "legs": []}
    rows = leg_rows(ticket, capital)
    fl = floor_capital(rows)
    unfilled = [r["symbol"] for r in rows if not r["fits"]]
    executable = sum(r["amount_cny"] for r in rows)
    cash_leg = float(ticket.get("cash_weight") or 0.0)
    book_amount = round(capital * (1.0 - cash_leg), 2)
    # the residual is the whole-lot rounding INSIDE the sleeves, not the cash slot: the
    # sheet's own cash weight is a design choice (the 8% vol target), and counting it as
    # rounding would read a full-size book as if it were a stranded one
    residual = round(sum(r["budget_cny"] - r["amount_cny"] for r in rows), 2)
    residual_pct = round(residual / capital * 100, 4) if capital else None
    if unfilled:
        verdict = "BELOW_FLOOR_AT_%d" % capital
    elif residual_pct is not None and residual_pct <= RESIDUAL_MAX_PCT:
        verdict = "TRADABLE_AT_%d" % capital
    else:
        verdict = "RESIDUAL_TOO_BIG_AT_%d" % capital
    return {
        "verdict": verdict,
        "capital_cny": capital,
        "asof_bar": ticket.get("asof_bar"),
        "n_legs": len(rows),
        "cash_weight": cash_leg,
        "book_amount_cny": book_amount,
        "traded_amount_cny": round(executable, 2),
        "cash_slot_cny": round(capital * cash_leg, 2),
        "residual_cny": residual,
        "residual_pct_nav": residual_pct,
        "unfilled_names": unfilled,
        "floor": fl,
        "capital_multiple_vs_floor": (round(capital / fl["min_capital_cny"], 1)
                                      if fl.get("min_capital_cny") else None),
        "legs": rows,
        "thresholds": {"residual_max_pct_nav": RESIDUAL_MAX_PCT, "lot": LOT,
                       "fee_floor_cny": FEE_FLOOR},
    }


def path_gap():
    """What whole lots cost at 1M for a twelve-name book -- a DIFFERENT configuration.

    No class filter, no 8% vol target: this is `lot_equity` on the full panel at n_hold=12.
    It bounds the card's lot friction; it does not restate the card's number.
    """
    close, openp, amt, score, n_flip = L._panel()
    lot_ser, lot_info = L.lot_equity(close, openp, amt, score, 1_000_000, n_hold=12)
    ref_ser, ref_info = L.lot_equity(close, openp, amt, score, 1_000_000, n_hold=12,
                                     lot=1, fee_floor=0.0)
    a = L.stats(lot_ser / 1e6, "n12_lot")
    b = L.stats(ref_ser / 1e6, "n12_ref")
    return {
        "config": {"n_hold": 12, "rebal": L.REBAL, "cost_bp_per_side": L.COST * 1e4,
                   "vol_target": None, "universe_classes": "all (no filter)",
                   "capital_cny": 1_000_000},
        "note": "same rule family, NOT the card's configuration (the card runs a class "
                "filter and an 8% vol target); reported to bound lot friction, not to "
                "restate the card",
        "cagr_lot": a.get("cagr"), "sharpe_lot": a.get("sharpe"),
        "maxdd_lot": a.get("maxdd"),
        "cagr_ref": b.get("cagr"), "sharpe_ref": b.get("sharpe"),
        "friction_cost_pp": round((a.get("cagr", 0.0) - b.get("cagr", 0.0)) * 100, 3),
        "cash_avg_pct": lot_info.get("cash_avg_pct"),
        "unfilled_tickets": lot_info.get("unfilled_tickets"),
        "tickets": lot_info.get("tickets"),
        "flips_repaired": n_flip,
    }


def run(capital=1_000_000):
    path = newest_ticket()
    ticket = load_ticket(path)
    out = resolve(ticket, capital)
    out["ticket_file"] = os.path.relpath(path, ROOT).replace("\\", "/") if path else None
    out["evidence_cutoff"] = out.get("asof_bar") or _panel_cutoff()
    out["path_check"] = path_gap()
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print(json.dumps({k: out[k] for k in ("evidence_cutoff", "verdict", "capital_cny",
                                          "residual_pct_nav", "unfilled_names")},
                     ensure_ascii=False))
    print(json.dumps(out["path_check"], ensure_ascii=False))
    return out


def _panel_cutoff():
    """Bar date of the panel -- used only when no ticket is on disk."""
    try:
        close, _openp, _amt, _score, _n = L._panel()
        return str(close.index[-1].date())
    except Exception:
        return None


def _md(out):
    L_ = []
    L_.append("# ETF 卡：12 名的单，在这个资本上到底能不能下\n")
    L_.append("> evidence_cutoff=%s；票面= `%s`\n" % (out.get("evidence_cutoff"),
                                                  out.get("ticket_file")))
    L_.append("## 这一面回答什么\n")
    L_.append("卡片印权重，票面印金额，可**下单是整手**——100 份一手。"
              "一个名字的切片如果小于它一手的价格，这个名字根本买不进，那份钱只能躺在现金里；"
              "于是「按权重执行的书」和「按整手执行的书」是两本书。"
              "小账户阶梯面（`etf_book_lot_ladder.py`）回答的是「小到什么程度摩擦开始咬」，"
              "这一面回答的是反向的那一半：**在这个资本上，12 个名字是不是都下得进去。**\n")
    fl = out.get("floor") or {}
    L_.append("## 一手门槛\n")
    L_.append("每一名至少要一手，所以最小资本 = max(一手金额 / 权重)。"
              "本面读出：**%s 元**，由 `%s` 顶着；当前资本 %s 元 = 它的 **%s 倍**。\n"
              % ("{:,}".format(fl.get("min_capital_cny") or 0), fl.get("binding_symbol"),
                 "{:,}".format(out.get("capital_cny") or 0),
                 out.get("capital_multiple_vs_floor")))
    L_.append("## 逐名读数\n")
    L_.append("| 代码 | 名称 | 类 | 权重 | 目标金额 | 一手金额 | 手数 | 实际金额 | 残差 |")
    L_.append("|---|---|---|---:|---:|---:|---:|---:|---:|")
    for r in out.get("legs") or []:
        L_.append("| %s | %s | %s | %.2f%% | %s | %s | %d | %s | %s |" % (
            r["symbol"], r["name"], r["class"], r["weight"] * 100,
            "{:,.0f}".format(r["budget_cny"]),
            "{:,.2f}".format(r["one_lot_cny"] or 0), r["lots"],
            "{:,.0f}".format(r["amount_cny"]), "{:,.2f}".format(r["residual_cny"])))
    L_.append("\n合计成交 %s 元，残差 %s 元 = 净值的 **%s%%**（冻结门 %.2f%%）。\n"
              % ("{:,.0f}".format(out["traded_amount_cny"]),
                 "{:,.0f}".format(out["residual_cny"]), out["residual_pct_nav"],
                 out["thresholds"]["residual_max_pct_nav"]))
    L_.append("## 判决\n")
    v = out["verdict"]
    if v.startswith("TRADABLE_AT_"):
        L_.append("**下得进去。** 12 个名字在 %s 元上都至少买到一手，没有一个落在「预算不足一手」，"
                  "整手取整只把 %s 元（%.3f%% 净值）留在现金里——远低于冻结的 0.5%% 门。"
                  "换句话说：这张单在这个资本上是**可执行的**，权重书与整手书在这个规模上几乎是同一本书。\n"
                  % ("{:,}".format(out["capital_cny"]), "{:,.0f}".format(out["residual_cny"]),
                     out["residual_pct_nav"]))
    elif v.startswith("BELOW_FLOOR_AT_"):
        L_.append("**下不进去。** 资本低于一手门槛，这些名字一手都买不到：%s。"
                  "这个资本上的票面只是一张权重的愿望，不是订单。\n"
                  % "、".join(out["unfilled_names"]))
    else:
        L_.append("**能下但不够像这本书。** 每个名字都买到了一手，可整手取整留下的现金"
                  "（%.3f%% 净值）超过了冻结的 0.5%% 门：能下单，但下的不是按权重那本书。\n"
                  % (out["residual_pct_nav"] or 0))
    p = out.get("path_check") or {}
    L_.append("## 路径上的量级（另一本书，如实标注）\n")
    L_.append("同一个规则、n=12、全池（**没有**类别过滤、**没有** 8%% 波动目标）在 100 万档跑两遍："
              "整手+5 元佣金底 年化 **%.2f%%**，1 份整手+零佣金底 年化 **%.2f%%**，差 **%+.2fpp**；"
              "平均现金占比 %s%%、没买成的票数 %s（现金或一手不足，累计在 %s 张票里）。\n"
              % ((p.get("cagr_lot") or 0) * 100, (p.get("cagr_ref") or 0) * 100,
                 p.get("friction_cost_pp") or 0, p.get("cash_avg_pct"),
                 p.get("unfilled_tickets"), p.get("tickets")))
    L_.append("这是**同族不同配置**，用来说明「12 名在 100 万上整手摩擦有多小」，"
              "不能拿来替代卡片自己的读数（卡片带类别过滤与 8% 波动目标，两个数不是一回事）。\n")
    L_.append("## 这张面没有回答的\n")
    L_.append("- 没有回答「下得进去」之外的执行风险：当日深度、涨跌停、停牌都不在这里。\n")
    L_.append("- 路径面用的是全池，不是卡片的池，见上。\n")
    L_.append("- ETF 票池是现存标的（幸存者偏差照旧）。\n")
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L_) + "\n")
    return OUT_MD


# --------------------------------------------------------------------- selftest
def _ticket(prices, weights, cash=0.0):
    return {"asof_bar": "2026-01-02", "cash_weight": cash,
            "order": [{"symbol": "S%d" % i, "name": "n%d" % i, "class": "equity",
                       "weight": w, "price": p}
                      for i, (p, w) in enumerate(zip(prices, weights))]}


def selftest():
    fails = []

    # L1 twelve cheap names at 1M: every leg fits and the residual is tiny
    t = _ticket([1.2] * 12, [1 / 12] * 12)
    r = resolve(t, 1_000_000)
    if not r["verdict"].startswith("TRADABLE_AT_"):
        fails.append("L1 twelve cheap names should be tradable at 1M, got %r" % r["verdict"])
    if r["unfilled_names"]:
        fails.append("L1b unfilled names on a cheap book: %r" % r["unfilled_names"])
    if not (0 <= r["residual_pct_nav"] <= RESIDUAL_MAX_PCT):
        fails.append("L1c residual out of band: %r" % r["residual_pct_nav"])

    # L2 one expensive name: at 100,000 the slice cannot buy one lot -> BELOW_FLOOR
    t2 = _ticket([200.0] + [1.0] * 11, [1 / 12] * 12)
    r2 = resolve(t2, 100_000)          # slice 8,333 < one lot 20,000
    if not r2["verdict"].startswith("BELOW_FLOOR_AT_"):
        fails.append("L2 expected BELOW_FLOOR, got %r" % r2["verdict"])
    if r2["unfilled_names"] != ["S0"]:
        fails.append("L2b wrong unfilled set: %r" % r2["unfilled_names"])

    # L3 the floor is set by the same expensive name, and it is the ratio not the price
    fl = r2["floor"]
    if fl["binding_symbol"] != "S0":
        fails.append("L3 floor not bound by the expensive name: %r" % fl["binding_symbol"])
    expect = 200.0 * LOT / (1 / 12)
    if abs(fl["min_capital_cny"] - expect) > 1.0:
        fails.append("L3b floor arithmetic wrong: %r vs %r" % (fl["min_capital_cny"], expect))

    # L4 raising the capital to the floor makes exactly that name fit
    r4 = resolve(t2, int(expect))
    if not r4["verdict"].startswith("TRADABLE_AT_"):
        fails.append("L4 at the floor the book should be tradable, got %r" % r4["verdict"])

    # L5 a book that fits but strands too much cash is named, not silently passed
    #    1 lot 10,000 per name at 12 names = 120,000 traded of 200,000 => 40% residual
    t5 = _ticket([100.0] * 12, [1 / 12] * 12)
    r5 = resolve(t5, 200_000)
    if not r5["verdict"].startswith("RESIDUAL_TOO_BIG_AT_"):
        fails.append("L5 expected RESIDUAL_TOO_BIG, got %r (residual %r)"
                     % (r5["verdict"], r5["residual_pct_nav"]))

    # L6 no ticket is a refusal, never an invented one
    r6 = resolve(None, 1_000_000)
    if r6["verdict"] != "TICKET_MISSING":
        fails.append("L6 missing ticket should refuse, got %r" % r6["verdict"])

    # L7 commission floor is per ticket and never charged on a zero ticket
    t7 = _ticket([1.0] * 12, [1 / 12] * 12)
    r7 = resolve(t7, 60_000)           # 5,000 slice -> 50 lots -> 5,000 traded, fee 5
    legs = r7["legs"]
    if abs(legs[0]["fee_cny"] - FEE_FLOOR) > 1e-9:
        fails.append("L7 fee floor not applied: %r" % legs[0]["fee_cny"])
    t8 = _ticket([1000.0] * 12, [1 / 12] * 12)
    r8 = resolve(t8, 60_000)
    if any(l["fee_cny"] != 0.0 for l in r8["legs"]):
        fails.append("L7b a zero-notional ticket was charged a fee")

    # L9 the published face must carry its cutoff and a verdict re-derivable from its legs
    if os.path.exists(OUT_JSON):
        face = json.load(open(OUT_JSON, encoding="utf-8"))
        if not face.get("evidence_cutoff"):
            fails.append("L9 published face has no evidence_cutoff")
        again = resolve({"asof_bar": face.get("asof_bar"), "cash_weight": face.get("cash_weight"),
                         "order": [{"symbol": l["symbol"], "name": l["name"], "class": l["class"],
                                    "weight": l["weight"], "price": l["price"]}
                                   for l in face["legs"]]}, face["capital_cny"])
        if again["verdict"] != face["verdict"]:
            fails.append("L9b published verdict does not re-derive: %r vs %r"
                         % (face["verdict"], again["verdict"]))

    print("selftest %d/%d PASS" % (9 - len(fails), 9))
    for f in fails:
        print("FAIL", f)
    return 0 if not fails else 1


def check():
    """Re-derive the verdict from the published legs and the ticket it names."""
    if not os.path.exists(OUT_JSON):
        print("check: no face on disk")
        return 2
    face = json.load(open(OUT_JSON, encoding="utf-8"))
    problems = []
    if not face.get("evidence_cutoff"):
        problems.append("missing evidence_cutoff")
    legs = face.get("legs") or []
    if not legs:
        problems.append("no legs on the face")
    # every leg must re-derive from weight+price at the stated capital
    for l in legs:
        budget = face["capital_cny"] * l["weight"]
        if abs(budget - l["budget_cny"]) > 0.01:
            problems.append("%s budget does not re-derive" % l["symbol"])
        one_lot = LOT * (l["price"] or 0)
        if l["one_lot_cny"] is not None and abs(one_lot - l["one_lot_cny"]) > 0.01:
            problems.append("%s one-lot does not re-derive" % l["symbol"])
        lots = int(budget // one_lot) if one_lot > 0 else 0
        if lots != l["lots"]:
            problems.append("%s lots do not re-derive (%r vs %r)"
                            % (l["symbol"], l["lots"], lots))
        if (lots >= 1) != l["fits"]:
            problems.append("%s fits-flag disagrees with its own lots" % l["symbol"])
    unfilled = sorted(l["symbol"] for l in legs if not l["fits"])
    if unfilled != sorted(face.get("unfilled_names") or []):
        problems.append("unfilled set differs from its own legs")
    if abs(sum(l["amount_cny"] for l in legs) - face["traded_amount_cny"]) > 0.05:
        problems.append("traded amount does not re-derive from the legs")
    again = resolve({"asof_bar": face.get("asof_bar"), "cash_weight": face.get("cash_weight"),
                     "order": [{"symbol": l["symbol"], "name": l["name"], "class": l["class"],
                                "weight": l["weight"], "price": l["price"]} for l in legs]},
                    face["capital_cny"])
    if again["verdict"] != face["verdict"]:
        problems.append("verdict %r re-derives to %r" % (face.get("verdict"),
                                                         again["verdict"]))
    if again["floor"]["binding_symbol"] != (face.get("floor") or {}).get("binding_symbol"):
        problems.append("binding name does not re-derive")
    # the named ticket must still exist: a face that points at nothing is not evidence
    tf = face.get("ticket_file")
    if tf and not os.path.exists(os.path.join(ROOT, tf)):
        problems.append("named ticket is gone: %s" % tf)
    out = {"ok": not problems, "verdict": face.get("verdict"),
           "capital_cny": face.get("capital_cny"), "problems": problems[:10]}
    print(json.dumps(out, ensure_ascii=False))
    return 0 if out["ok"] else 1


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run", choices=["run", "check", "selftest"])
    ap.add_argument("--capital", type=int, default=1_000_000)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest or args.cmd == "selftest":
        return selftest()
    if args.check or args.cmd == "check":
        return check()
    out = run(args.capital)
    print("md ->", _md(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())

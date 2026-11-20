"""What capital does this book actually need -- the fee floor, not the lot.

r1813 answered "can you place the ticket": every leg needs at least one whole
lot, and the binding name sets a minimum capital (published on
results/etf_book_ticket_floor.json, ~1.5e4 CNY at the 2026-11-19 card). That
face explicitly punted on the other half -- it says the CNY 5 minimum commission
"sits inside the residual bound", i.e. it checked that the floor does not
strand money, not what the floor COSTS.

At the one-lot floor each of the twelve legs is worth ~1e3 CNY, and a broker's
CNY 5 minimum commission on a 1e3 CNY ticket is ~52bp of commission where the
model charges 2.5bp. So the smallest tradable account is not the cheapest one:
the book's per-side cost is a curve in capital, and the entry price is where
that curve comes back to the 13.041bp the whole research line is priced at.

Nothing here is re-derived from a second cost caliber: the per-ticket side cost
comes from scripts/account_cost_tax.py::_side_cost_bp (knowledge/cost_spec.py
Face A + knowledge/rules.py CN-C3 minimum commission), lot quantization comes
from scripts/etf_book_ticket_floor.py::leg_rows, and the one-lot floor is READ
from the published ticket-floor face, never recomputed here.

Usage (cwd = repo root):
    python scripts/etf_book_entry_price.py run
    python scripts/etf_book_entry_price.py check
    python scripts/etf_book_entry_price.py selftest
"""
from __future__ import annotations

import datetime
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

if hasattr(sys.stdout, "encoding") and sys.stdout.encoding \
        and sys.stdout.encoding.lower().replace("-", "") not in ("utf8", "utf8mb4"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import etf_book_ticket_floor as TF                 # noqa: E402  lot quantization + ticket IO
from knowledge import cost_spec, rules             # noqa: E402  canonical cost calibers
from scripts.account_cost_tax import _side_cost_bp  # noqa: E402  per-ticket side cost

OUT_JSON = os.path.join(ROOT, "results", "etf_book_entry_price.json")
OUT_MD = os.path.join(ROOT, "results", "etf_book_entry_price.md")
FLOOR_FACE = os.path.join(ROOT, "results", "etf_book_ticket_floor.json")

# frozen before the read
LADDER = [20000, 50000, 100000, 200000, 300000, 500000, 1000000]
TOLERABLE_FLOOR_BP = 1.0     # the minimum may cost at most this much per side
ENTRY_MULTIPLE = 2.0         # clean entry this many times the lot floor = a real gap
REBAL_SESSIONS = 20          # the book's own cadence (gate face)
SESSIONS_PER_YEAR = 252
REBAL_PER_YEAR = SESSIONS_PER_YEAR / REBAL_SESSIONS


def panel_cutoff(rows):
    """The newest asof_bar among the legs is the evidence cutoff of the sheet."""
    bars = [r.get("asof_bar") for r in rows if r.get("asof_bar")]
    return max(bars) if bars else None


def rung(capital, ticket, fee, model_bp):
    """One capital rung: what fits, what the tickets cost, what a side pays in bp."""
    rows = TF.leg_rows(ticket, capital)
    fit = [r for r in rows if r.get("fits")]
    traded = sum(float(r["amount_cny"]) for r in fit)
    if not fit or traded <= 0:
        return {
            "capital_cny": float(capital), "legs_placed": 0, "legs_total": len(rows),
            "traded_cny": 0.0, "side_cost_bp": None, "floor_tax_bp": None,
            "legs_paying_floor": 0, "min_leg_cny": None, "stalled": "no leg fits: below the lot floor",
        }
    # one source for the per-ticket side cost: account_cost_tax._side_cost_bp applies the
    # CN-C3 minimum commission to THIS ticket and adds the frozen Face A fixed part
    fees = 0.0
    model_fees = 0.0
    paying = 0
    for r in fit:
        amount = float(r["amount_cny"])
        side = _side_cost_bp(fee, amount)
        if side - _side_cost_bp(fee) > 1e-12:
            paying += 1
        fees += amount * side / 1e4
        model_fees += amount * model_bp / 1e4
    floor_tax = fees - model_fees
    side_bp = fees / traded * 1e4
    return {
        "capital_cny": float(capital),
        "legs_placed": len(fit),
        "legs_total": len(rows),
        "traded_cny": round(traded, 2),
        "fees_cny": round(fees, 6),
        "model_fees_cny": round(model_fees, 6),
        "model_side_bp": round(model_bp, 4),
        "side_cost_bp": round(side_bp, 4),
        "excess_bp": round(side_bp - model_bp, 4),
        "floor_tax_bp": round(floor_tax / traded * 1e4, 4),
        "floor_tax_cny": round(floor_tax, 2),
        "side_cost_bp_waived": round(model_bp, 4),
        "legs_paying_floor": paying,
        "min_leg_cny": round(min(float(r["amount_cny"]) for r in fit), 2),
        # ceiling: the whole book turns twice (out and in) every rebalance
        "annual_cost_pct_ceiling": round(2 * REBAL_PER_YEAR * fees / capital * 100, 4),
        "annual_floor_tax_pct_ceiling": round(2 * REBAL_PER_YEAR * floor_tax / capital * 100, 4),
    }


def clean_entry(ticket, fee):
    """Smallest capital at which NO leg pays the minimum, by the sheet's own weights.

    A leg worth `capital * w` pays the floor until `capital * w * rate >= min`, so the
    binding leg is the one with the smallest weight; the lot floor can only raise it.
    """
    ratios = []
    for leg in ticket.get("order") or []:
        w = float(leg.get("weight") or 0.0)
        if w <= 0:
            ratios.append({"symbol": leg.get("symbol"), "needed_cny": None,
                           "why": "zero weight"})
            continue
        ratios.append({"symbol": leg.get("symbol"),
                       "needed_cny": round(fee.commission_min / (w * fee.commission_rate), 2)})
    usable = [x for x in ratios if x.get("needed_cny")]
    # every leg must clear, so the capital is driven by the leg that needs the MOST
    binding = max(usable, key=lambda x: x["needed_cny"]) if usable else None
    return {
        "all_legs_above_min_commission_cny": binding["needed_cny"] if binding else None,
        "binding_symbol": binding["symbol"] if binding else None,
        "per_leg_needed_cny": ratios,
    }


def read_lot_floor():
    """The one-lot floor comes from the published face; absent = None, never a guess."""
    if not os.path.exists(FLOOR_FACE):
        return None, None
    try:
        with open(FLOOR_FACE, encoding="utf-8") as fh:
            face = json.load(fh)
    except Exception:
        return None, None
    fl = face.get("floor") or {}
    return fl.get("min_capital_cny"), fl.get("binding_symbol")


def verdict_of(p):
    if p.get("stalled"):
        return p["stalled"]
    rungs = p["rungs"]
    if not any(r.get("side_cost_bp") for r in rungs):
        return "UNTRADABLE_AT_EVERY_RUNG"
    lot_floor = p["lot_floor_cny"]
    clean = (p["clean_entry"].get("all_legs_above_min_commission_cny")
             if p.get("clean_entry") else None)
    if not lot_floor or not clean:
        return "ENTRY_UNKNOWN"
    if clean >= ENTRY_MULTIPLE * lot_floor:
        return "ENTRY_PRICE_IS_THE_COMMISSION_FLOOR"
    return "LOT_FLOOR_IS_THE_ENTRY_PRICE"


def build(ticket, fee, lot_floor, lot_binding, model_bp):
    if ticket is None:
        return {"face": "etf_book_entry_price", "stalled": "TICKET_MISSING", "rungs": [],
                "verdict": "TICKET_MISSING"}
    rungs = []
    if lot_floor:
        rungs.append(dict(rung(lot_floor, ticket, fee, model_bp), label="one-lot floor"))
    for cap in LADDER:
        rungs.append(dict(rung(cap, ticket, fee, model_bp), label=None))
    clean = clean_entry(ticket, fee)
    clean_cny = clean.get("all_legs_above_min_commission_cny")
    tolerable = None
    for r in rungs:
        if r.get("floor_tax_bp") is not None and r["floor_tax_bp"] < TOLERABLE_FLOOR_BP:
            if tolerable is None or r["capital_cny"] < tolerable:
                tolerable = r["capital_cny"]
    p = {
        "face": "etf_book_entry_price",
        "generated": None,   # stamped by run(); kept out of build() so selftest stays hermetic
        "evidence_cutoff": ticket.get("asof_bar") or panel_cutoff(ticket.get("order") or []),
        "script": "scripts/etf_book_entry_price.py",
        "ticket_file": os.path.basename(TF.newest_ticket() or "") or None,
        "asof_bar": ticket.get("asof_bar"),
        "n_legs": len(ticket.get("order") or []),
        "criteria": {
            "ladder_cny": list(LADDER),
            "tolerable_floor_bp": TOLERABLE_FLOOR_BP,
            "entry_multiple": ENTRY_MULTIPLE,
            "rebal_sessions": REBAL_SESSIONS,
            "annual_ceiling": "2 sides x %.1f rebalances/yr, whole book turned" % REBAL_PER_YEAR,
            "frozen": "criteria fixed before the read; the one-lot floor and the per-ticket "
                      "cost are read from published faces, never recomputed here",
        },
        "calibers": {
            "side_cost": "knowledge/cost_spec.py Face A via scripts/account_cost_tax.py::_side_cost_bp",
            "min_commission": "knowledge/rules.py CN-C3 (commission_rate %.6f, min %.2f CNY)"
                              % (fee.commission_rate, fee.commission_min),
            "lots": "scripts/etf_book_ticket_floor.py::leg_rows (lot=%d)" % TF.LOT,
            "model_side_bp": round(model_bp, 4),
        },
        "lot_floor_cny": lot_floor,
        "lot_floor_binding_symbol": lot_binding,
        "clean_entry": clean,
        "tolerable_entry_cny": tolerable,
        "waived_entry_cny": lot_floor,
        "rungs": rungs,
    }
    p["verdict"] = verdict_of(p)
    return p


def run() -> int:
    ticket = TF.load_ticket(TF.newest_ticket())
    fee = rules.FeeSchedule()
    model_bp = cost_spec.x1_side_rate(fee) * 1e4
    lot_floor, lot_binding = read_lot_floor()
    p = build(ticket, fee, lot_floor, lot_binding, model_bp)
    if p.get("verdict") == "TICKET_MISSING":
        print("no ticket card on disk (results/etf_book_order/TICKET-*-card.json)")
        return 2
    p["generated"] = datetime.datetime.now(
        datetime.timezone(datetime.timedelta(hours=8))).isoformat(timespec="seconds")
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(p, fh, ensure_ascii=False, indent=1)
    write_md(p)
    first = next(r for r in p["rungs"] if r.get("side_cost_bp"))
    print("verdict %s | one-lot floor %s | clean entry %s | %d legs"
          % (p["verdict"], _money(p["lot_floor_cny"]),
             _money(p["clean_entry"].get("all_legs_above_min_commission_cny")), p["n_legs"]))
    print("first rung %s -> side %s bp (model %s bp), floor tax %s bp"
          % (_money(first["capital_cny"]), first["side_cost_bp"], p["calibers"]["model_side_bp"],
             first["floor_tax_bp"]))
    print("-> %s" % OUT_JSON)
    return 0


def _money(x):
    return "n/a" if x is None else "{:,.0f}".format(float(x))


def write_md(p):
    rows = [r for r in p["rungs"] if r.get("side_cost_bp") is not None]
    stale = [r for r in p["rungs"] if r.get("side_cost_bp") is None]
    first = rows[0] if rows else None
    L = ["# 这本书的门票价不是一手，是一手以上的那一截佣金", "",
         "证据截止 %s · 票面 %s · %d 腿 · 模型单边 %s bp"
         % (p["evidence_cutoff"], p["asof_bar"], p["n_legs"], p["calibers"]["model_side_bp"]), "",
         "## 判词：%s" % p["verdict"], ""]
    if first is not None:
        L += ["一手门槛（%s 元，由 %s 那张面给定）只回答「能不能下单」。钱真正付出去的时候，"
              "同样这十二腿会被券商的**最低佣金按每张单一笔**收费：一手门槛上的账户一腿只有 %s 元，"
              "最低佣金那一截折成 **%.1f bp**，单边总成本 **%.1f bp**＝模型的 %.1f 倍。"
              "换成一年：只这一截佣金上限就吃掉本金的 **%.1f%%**，比这本书在 3000 万规模上的年化（0.85%%）还高。"
              % (_money(p["lot_floor_cny"]), p["lot_floor_binding_symbol"] or "n/a",
                 _money(first["min_leg_cny"]),
                 (first["floor_tax_bp"] or 0.0),
                 first["side_cost_bp"],
                 (first["side_cost_bp"] / p["calibers"]["model_side_bp"]
                  if first["side_cost_bp"] else 0),
                 (first["annual_floor_tax_pct_ceiling"] or 0.0)),
              "", "| 资金（元） | 能下的腿 | 成交额（元） | 单边成本 bp | 超出模型 | 其中最低佣金 bp | 一年成本上限 | 其中最低佣金 |",
              "|---|---:|---:|---:|---:|---:|---:|---:|"]
        for r in p["rungs"]:
            if r.get("side_cost_bp") is None:
                L.append("| %s | 0/%d | — | **不可交易** | — | — | — | — |"
                         % (_money(r["capital_cny"]), r["legs_total"]))
                continue
            L.append("| %s | %d/%d | %s | %.2f | %+.2f | %.2f | %.2f%% | %.2f%% |"
                     % (_money(r["capital_cny"]), r["legs_placed"], r["legs_total"],
                        _money(r["traded_cny"]), r["side_cost_bp"], r["excess_bp"],
                        r["floor_tax_bp"] or 0.0, r["annual_cost_pct_ceiling"],
                        r["annual_floor_tax_pct_ceiling"] or 0.0))
        L += ["", "一年上限＝每轮整本卖出再买入（2 边 × %.1f 次/年），所以是**上限不是预测**；"
              "「其中最低佣金」那一栏是纯佣金下限——它与「超出模型」逐列相等，说明小账户多付的钱"
              "**全部来自每张单的固定收费**，不是整手凑数：凑数只会留下现金，不会凭空加价。"
              % REBAL_PER_YEAR,
              "", "## 三个入门价", "",
              "| 说法 | 资金（元） | 它保证什么 |", "|---|---:|---|",
              "| 一手门槛（r1813） | %s | 十二条腿每一条都买得起一手 |" % _money(p["lot_floor_cny"]),
              "| 容忍门槛（本轮） | %s | 最低佣金每边吃掉 ≤ %.1f bp |"
              % (_money(p["tolerable_entry_cny"]), p["criteria"]["tolerable_floor_bp"]),
              "| 干净门槛（本轮） | %s | **没有一腿**付最低佣金（约束腿 %s） |"
              % (_money(p["clean_entry"].get("all_legs_above_min_commission_cny")),
                 p["clean_entry"].get("binding_symbol") or "n/a"), "",
              "佣金免五的账户（不少券商对 ETF 免最低佣金）把这三栏合成一栏：入门价回到 %s 元，"
              "单边成本在任何资金上都是 %s bp。开在哪家，比开多大更值钱。"
              % (_money(p["waived_entry_cny"]), p["calibers"]["model_side_bp"]), "",
              "## 读法", "",
              "- 这是一条**成本曲线**，不是收益结论：它说的是同一本钱在不同账户规模上要交多少，"
              "不改变书本身的信号。",
              "- 与规模上限（r1878 的容量阶梯）是同一件事的两端：钱太少被最低佣金吃，钱太多被成交额吃，"
              "中间那段才是这本书能待的地方。",
              "- 「一年上限」把整本换成现金再买回来，实际调仓只换一部分，所以真实成本在表内数字之下。",
              "", "## 未验证（如实）", ""]
    else:
        L += ["没有一条腿能在这个资金档上下单，表为空。", ""]
    L += ["- 只按当前票面一次的权重算，不按历史调仓的平均权重；等权十二腿使这项偏差很小。",
          "- 最低佣金取 CN-C3 的 5 元冻结值；不同券商实际不同，免五账户另有一栏。",
          "- 印花税对 ETF 为零（CN-C1），故本面只有佣金与固定项，不含卖出侧额外税。",
          "- 一年上限假设整本换手，未使用书自己的换手率——用了就等于替它假定了成交行为。"]
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")


def check() -> int:
    """Re-derive every row from its own numbers, and the verdict from the published counts."""
    if not os.path.exists(OUT_JSON):
        print("STALE -- face missing: %s" % OUT_JSON)
        return 2
    with open(OUT_JSON, encoding="utf-8") as fh:
        p = json.load(fh)
    problems = []
    newest = os.path.basename(TF.newest_ticket() or "")
    if newest and p.get("ticket_file") and newest != p["ticket_file"]:
        print("STALE -- ticket moved: face prices %s, disk has %s"
              % (p["ticket_file"], newest))
        return 3
    model_bp = float(p["calibers"]["model_side_bp"])
    for r in p["rungs"]:
        if r.get("side_cost_bp") is None:
            continue
        traded = float(r["traded_cny"])
        if traded <= 0:
            problems.append("rung %s has a cost but no traded amount" % r["capital_cny"])
            continue
        # two published numbers must agree: the bp column and the CNY it was paid in
        back = float(r["fees_cny"]) / traded * 1e4
        if abs(back - float(r["side_cost_bp"])) > 1e-3:
            problems.append("rung %s side bp does not re-derive from its own fee: %.4f vs %.4f"
                            % (r["capital_cny"], back, r["side_cost_bp"]))
        if abs(float(r["excess_bp"]) - (float(r["side_cost_bp"]) - model_bp)) > 1e-3:
            problems.append("rung %s excess does not re-derive" % r["capital_cny"])
        if float(r["floor_tax_bp"]) < -1e-6 or float(r["floor_tax_bp"]) > float(r["excess_bp"]) + 1e-3:
            problems.append("rung %s floor tax is not inside the excess" % r["capital_cny"])
        if not (1.0 <= float(r["side_cost_bp"]) <= 400.0):
            problems.append("rung %s side bp outside any plausible band: %s"
                            % (r["capital_cny"], r["side_cost_bp"]))
        waived = float(r.get("side_cost_bp_waived") or 0.0)
        if abs(waived - model_bp) > 1e-3:
            problems.append("rung %s waived arm is not the model rate" % r["capital_cny"])
        ceiling = float(r.get("annual_cost_pct_ceiling") or 0.0)
        again = 2 * REBAL_PER_YEAR * float(r["fees_cny"]) / float(r["capital_cny"]) * 100
        if abs(ceiling - again) > 1e-2:
            problems.append("rung %s annual ceiling does not re-derive" % r["capital_cny"])
        if ceiling > 100.0:
            problems.append("rung %s annual ceiling above 100%% of capital" % r["capital_cny"])
    verdict = verdict_of(p)
    if verdict != p.get("verdict"):
        print("STALE -- verdict re-derives to %s, published %s" % (verdict, p.get("verdict")))
        return 3
    out = {"ok": not problems, "verdict": p.get("verdict"),
           "rungs": len(p["rungs"]), "problems": problems[:10]}
    print(json.dumps(out, ensure_ascii=False))
    return 0 if not problems else 3


# ------------------------------------------------------------------ selftest

def _synth(prices, weights, cash=0.0):
    order = [{"symbol": "S%02d" % i, "name": "s%02d" % i, "class": "equity",
              "weight": w, "price": px}
             for i, (w, px) in enumerate(zip(weights, prices))]
    return {"asof_bar": "2026-01-05", "cash_weight": cash, "order": order}


def selftest() -> int:
    fails = []

    def chk(name, cond, extra=""):
        print("[%s] %s%s" % ("PASS" if cond else "FAIL", name, ("  " + extra) if extra else ""))
        if not cond:
            fails.append(name)

    fee = rules.FeeSchedule()
    model_bp = cost_spec.x1_side_rate(fee) * 1e4
    crit = fee.commission_min / fee.commission_rate

    # L1 -- a synthetic 12-leg equal-weight book at 1M pays exactly the model rate
    t1 = _synth([2.0] * 12, [0.075] * 12, cash=0.10)
    r1 = rung(1_000_000, t1, fee, model_bp)
    chk("L1 at 1M no leg pays the minimum", r1["legs_paying_floor"] == 0,
        "min leg %s" % r1["min_leg_cny"])
    chk("L1b at 1M the side cost is the model rate",
        abs(r1["side_cost_bp"] - model_bp) < 1e-6, "%.4f vs %.4f" % (r1["side_cost_bp"], model_bp))

    # L2 -- at one lot per leg the floor bites hard: twelve tickets at 200 CNY each
    t2 = _synth([2.0] * 12, [0.075] * 12)
    cap_lot = max(TF.LOT * 2.0 / 0.075, 0)
    r2 = rung(cap_lot, t2, fee, model_bp)
    chk("L2 at the lot floor every leg pays the minimum", r2["legs_paying_floor"] == 12,
        "%d/12" % r2["legs_paying_floor"])
    chk("L2b the floor multiplies the side cost", r2["side_cost_bp"] > 3 * model_bp,
        "%.1f bp vs %.3f" % (r2["side_cost_bp"], model_bp))

    # L3 -- the floor tax is exactly zero once every leg clears the critical ticket
    t3 = _synth([10.0] * 12, [0.075] * 12)
    r3 = rung(crit / 0.075 * 1.0001, t3, fee, model_bp)
    chk("L3 above the critical ticket the tax is zero",
        abs(r3["floor_tax_bp"]) < 1e-6, "%.6f bp" % r3["floor_tax_bp"])

    # L4 -- an untradable capital says so instead of printing a cost
    r4 = rung(100.0, t3, fee, model_bp)
    chk("L4 below one lot there is no cost to print",
        r4["side_cost_bp"] is None and r4["legs_placed"] == 0)

    # L5 -- the waived arm is the model rate at EVERY capital (免五 collapses the curve)
    waivers = [rung(c, t2, fee, model_bp)["side_cost_bp_waived"] for c in (cap_lot, 200_000)]
    chk("L5 without the minimum the cost is the model at every size",
        all(abs(w - model_bp) < 1e-6 for w in waivers), str(waivers))

    # L6 -- the tax falls monotonically as capital rises
    tax = [rung(c, t2, fee, model_bp)["floor_tax_bp"] for c in (50_000, 200_000, 500_000)]
    chk("L6 the floor tax falls as the account grows",
        tax[0] > tax[1] >= tax[2] - 1e-9, str(tax))

    # L7 -- clean entry is where the smallest-weight leg clears the critical ticket
    t7 = _synth([2.0] * 11 + [2.0], [0.02] + [0.08] * 11)
    ce = clean_entry(t7, fee)
    chk("L7 clean entry is set by the SMALLEST weight",
        abs(ce["all_legs_above_min_commission_cny"] - crit / 0.02) < 1e-6,
        "%.0f" % ce["all_legs_above_min_commission_cny"])
    chk("L7b and it names that leg", ce["binding_symbol"] == "S00")

    # L8 -- the verdict flips on the frozen multiple, not on taste
    base = {"stalled": None, "rungs": [{"side_cost_bp": 20.0}], "lot_floor_cny": 15000.0}
    p_gap = dict(base, clean_entry={"all_legs_above_min_commission_cny": 30000.0})
    p_close = dict(base, clean_entry={"all_legs_above_min_commission_cny": 20000.0})
    chk("L8 a clean entry twice the lot floor is a floor, not a lot",
        verdict_of(p_gap) == "ENTRY_PRICE_IS_THE_COMMISSION_FLOOR")
    chk("L8b a clean entry at 1.33x is the lot",
        verdict_of(p_close) == "LOT_FLOOR_IS_THE_ENTRY_PRICE")

    # L9 -- a sheet with no tradable rung cannot claim a price
    chk("L9 no tradable rung is a stalled verdict",
        verdict_of({"stalled": None, "rungs": [{"side_cost_bp": None}],
                    "lot_floor_cny": None}) == "UNTRADABLE_AT_EVERY_RUNG")

    print("\nselftest %d/%d" % (9 + 4 - len(fails), 13))
    return 0 if not fails else 1


def main():
    cmd = (sys.argv[1] if len(sys.argv) > 1 else "run").lstrip("-").lower()
    if cmd in ("selftest", "test"):
        return selftest()
    if cmd == "check":
        return check()
    if cmd == "run":
        return run()
    print("unknown command %r (run|check|selftest)" % cmd)
    return 2


if __name__ == "__main__":
    sys.exit(main())

"""The capacity gate already says how much capital this book carries on a typical day.
Does the ticket still place at that number?  Whole lots, 5 CNY ticket floor.

Two faces already existed and never met:

  * `etf_book_capacity_edge.py` reads the year gate backwards and reports the capital at
    which the book stops breaching 1% of ADV -- **today** (the best of the last 60
    sessions), the **median** session, and the **worst** session.
  * `etf_book_ticket_floor.py` takes one capital and asks, name by name, whether each slice
    is big enough to be a legal order (100 shares a lot, 5 CNY a ticket).

The ticket that is actually signed is priced at the sheet's own capital (1,000,000), while
the gate says a typical day only carries about half of it.  Nobody had checked whether the
twelve names survive that cut.  This face feeds each of the gate's three capitals through
the ticket floor's own resolver -- imported, not re-implemented -- so the two faces cannot
disagree about what a lot costs.

Frozen judgement (written before the reading, not tuned to it):

  TRADABLE_IN_EVERY_READ_SESSION  all three rungs (best / typical / worst) resolve TRADABLE
  TRADABLE_ON_A_TYPICAL_DAY       best and typical resolve TRADABLE, worst does not
  TRADABLE_ONLY_ON_THE_BEST_DAY   only the best session's capital places the book
  NOT_TRADABLE_ON_ANY_PRICED_DAY  even the best session's capital cannot buy one lot of
                                  every name
  CAPACITY_FACE_MISSING           no capacity face on disk: the face refuses rather than
                                  inventing capitals
  TICKET_MISSING                  no ticket on disk

The shortfall to the typical day is printed in yuan (`shortfall_to_typical_cny`): the
typical capital minus the one-lot floor the ticket needs.  Negative means the typical day
has room to spare; positive means the book needs that much more capital before a typical
session can carry all twelve names.

Usage:
    python scripts/etf_book_capacity_ticket.py run
    python scripts/etf_book_capacity_ticket.py --selftest
    python scripts/etf_book_capacity_ticket.py --check
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import etf_book_ticket_floor as TF  # noqa: E402  (same-directory sibling)

CAP_FACE = os.path.join(ROOT, "results", "etf_book_capacity_edge.json")
OUT_JSON = os.path.join(ROOT, "results", "etf_book_capacity_ticket.json")
OUT_MD = os.path.join(ROOT, "research", "ETF_BOOK_CAPACITY_TICKET.md")

RUNGS = (("best", "capital_max_cny"), ("typical", "capital_median_cny"),
         ("worst", "capital_min_cny"))


def load_capacity(path=CAP_FACE):
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def rung_capitals(face):
    """The three capitals the gate priced, in the face's own order (best, typical, worst)."""
    s = (face or {}).get("summary") or {}
    out = []
    for tag, key in RUNGS:
        cap = s.get(key)
        out.append({"tag": tag, "source_key": key, "capital_cny": cap,
                    "verdict": s.get("verdict")})
    return out


def derive(ticket, face, resolver=None):
    """Fold the gate's three capitals through the ticket.  Pure: no file writes."""
    resolver = resolver or TF.resolve
    rungs = rung_capitals(face)
    rows = []
    for r in rungs:
        cap = r["capital_cny"]
        if not cap:
            rows.append(dict(r, verdict=None, unfilled=None, residual_pct_nav=None,
                             traded_amount_cny=None, note="gate published no capital"))
            continue
        res = resolver(ticket, cap)
        rows.append(dict(r, verdict=res.get("verdict"),
                         unfilled=res.get("unfilled_names"),
                         n_unfilled=len(res.get("unfilled_names") or []),
                         residual_pct_nav=res.get("residual_pct_nav"),
                         traded_amount_cny=res.get("traded_amount_cny"),
                         floor_cny=(res.get("floor") or {}).get("min_capital_cny"),
                         binding=(res.get("floor") or {}).get("binding_symbol")))
    verdict = verdict_from_rungs(rows)
    floor = None
    for r in rows:
        if r.get("floor_cny"):
            floor = r["floor_cny"]
            break
    typical = next((r for r in rows if r["tag"] == "typical"), None)
    shortfall = None
    if floor and typical and typical.get("capital_cny"):
        shortfall = round(floor - typical["capital_cny"], 2)
    return {
        "rungs": rows,
        "verdict": verdict,
        "one_lot_floor_cny": floor,
        "shortfall_to_typical_cny": shortfall,
        "n_rungs_tradable": sum(1 for r in rows if is_tradable(r.get("verdict"))),
    }


def is_tradable(verdict):
    return bool(verdict) and verdict.startswith("TRADABLE")


def verdict_from_rungs(rows):
    """The verdict is a count of rungs that place, never a name-level judgement."""
    if any(r.get("verdict") is None for r in rows):
        return "CAPACITY_FACE_MISSING"
    ok = {r["tag"]: is_tradable(r.get("verdict")) for r in rows}
    if ok.get("best") and ok.get("typical") and ok.get("worst"):
        return "TRADABLE_IN_EVERY_READ_SESSION"
    if ok.get("best") and ok.get("typical"):
        return "TRADABLE_ON_A_TYPICAL_DAY"
    if ok.get("best"):
        return "TRADABLE_ONLY_ON_THE_BEST_DAY"
    return "NOT_TRADABLE_ON_ANY_PRICED_DAY"


def fault_of(rung):
    """Why a rung did not place -- two different faults, two different sentences.

    A rung can fail because a name cannot buy a single lot, or because every name buys but
    the whole-lot residue strands more than the frozen share of NAV.  Collapsing the second
    into the first prints "0 names cannot buy" beside "does not fit", which reads as a bug.
    """
    if not rung or not rung.get("verdict"):
        return "unknown"
    if rung.get("n_unfilled"):
        return "unfilled"
    if str(rung.get("verdict")).startswith("RESIDUAL_TOO_BIG"):
        return "residual"
    return "none"


def fault_text(rung, residual_max_pct):
    if fault_of(rung) == "unfilled":
        return "那天有 {} 个名字连一手都买不到（{}）".format(
            rung.get("n_unfilled"), "、".join(rung.get("unfilled") or []) or "—")
    if fault_of(rung) == "residual":
        return ("那天没有名字买不到，但整手残差 %s%% 的净值超过冻结的 %.2f%% 门"
                % ("%.4f" % (rung.get("residual_pct_nav") or 0.0), residual_max_pct))
    return "那天判词是 %s" % rung.get("verdict")


def sentence(payload):
    v = payload.get("verdict")
    rows = {r["tag"]: r for r in payload.get("rungs") or []}
    typ = rows.get("typical") or {}
    worst = rows.get("worst") or {}
    best = rows.get("best") or {}
    floor = payload.get("one_lot_floor_cny")
    short = payload.get("shortfall_to_typical_cny")
    if v == "CAPACITY_FACE_MISSING":
        return "容量面不在盘上，这一面拒绝编造资本：先跑 etf_book_capacity_edge.py。"
    if v == "TICKET_MISSING":
        return "票面不在盘上，这一面拒绝编造订单：先跑 etf_book_order.py run。"
    if v == "TRADABLE_IN_EVERY_READ_SESSION":
        return ("闸的三个资本档（今天 {:,} 元 / 平常 {:,} 元 / 最差 {:,} 元）都能把十二名各买到一手，"
                "一手门槛 {:,} 元。".format(int(best.get("capital_cny") or 0),
                                            int(typ.get("capital_cny") or 0),
                                            int(worst.get("capital_cny") or 0),
                                            int(floor or 0)))
    rmax = float((payload.get("frozen") or {}).get("residual_max_pct") or 0.0)
    if v == "TRADABLE_ON_A_TYPICAL_DAY":
        return ("平常的一天（{:,} 元）装得下这张票，最差的一天（{:,} 元）装不下——{}。".format(
            int(typ.get("capital_cny") or 0), int(worst.get("capital_cny") or 0),
            fault_text(worst, rmax)))
    if v == "TRADABLE_ONLY_ON_THE_BEST_DAY":
        return ("只有 60 天里最好的一天（{:,} 元）装得下；平常的一天（{:,} 元）装不下——{}，"
                "一手门槛 {:,} 元。".format(
                    int(best.get("capital_cny") or 0), int(typ.get("capital_cny") or 0),
                    fault_text(typ, rmax), int(floor or 0)))
    return ("连 60 天里最好的一天（{:,} 元）也装不下：一手门槛 {:,} 元，缺 {:,} 元。".format(
        int(best.get("capital_cny") or 0), int(floor or 0),
        int((floor or 0) - (best.get("capital_cny") or 0))))


def run():
    face = load_capacity()
    path = TF.newest_ticket()
    ticket = TF.load_ticket(path)
    out = derive(ticket, face)
    out.update({
        "artifact": "etf_book_capacity_ticket",
        "face": "results/etf_book_capacity_ticket.json",
        "script": "scripts/etf_book_capacity_ticket.py",
        "ticket_file": os.path.relpath(path, ROOT).replace("\\", "/") if path else None,
        "capacity_face": "results/etf_book_capacity_edge.json" if face else None,
        "capacity_verdict": ((face or {}).get("summary") or {}).get("verdict"),
        "n_sessions_read": ((face or {}).get("summary") or {}).get("n_sessions"),
        "evidence_cutoff": (ticket or {}).get("asof_bar") or (face or {}).get("evidence_cutoff"),
        "frozen": {"lot_shares": TF.LOT, "fee_floor_cny": TF.FEE_FLOOR,
                   "residual_max_pct": TF.RESIDUAL_MAX_PCT,
                   "rung_order": [t for t, _ in RUNGS]},
    })
    if out["verdict"] == "TICKET_MISSING":
        out["sentence"] = sentence(out)
    else:
        out["sentence"] = sentence(out)
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print(json.dumps({k: out[k] for k in ("evidence_cutoff", "verdict",
                                          "one_lot_floor_cny", "shortfall_to_typical_cny",
                                          "n_rungs_tradable")}, ensure_ascii=False))
    print("md ->", render_md(out))
    return out


def render_md(out):
    L = []
    L.append("# 容量闸说平常只装得下一半，那这张票还下得进去吗\n")
    L.append("> evidence_cutoff=%s；票面=`%s`；容量面=`%s`\n"
             % (out.get("evidence_cutoff"), out.get("ticket_file"), out.get("capacity_face")))
    L.append("## 问题从哪来\n")
    L.append("容量闸（`etf_book_capacity_edge.py`）读的是「这本书在 1% 成交额下能装多大」，"
             "它给出三个资本：60 天里最好的一天、平常的一天、最差的一天。"
             "而签出去的票是按票面自己的资本（1,000,000）定的价。"
             "没人问过：**把资本换成闸允许的数，十二个名字还买得进吗。**"
             "买不进的钱只能留在现金里，那执行出来的就不是印在卡片上的那本书。\n")
    L.append("## 三个资本档的逐档读数\n")
    L.append("| 档 | 资本 | 判词 | 填不满的名字 | 残差(%NAV) | 成交额 |")
    L.append("|---|---:|---|---|---:|---:|")
    names = {"best": "60 天最好的一天", "typical": "平常的一天", "worst": "60 天最差的一天"}
    for r in out.get("rungs") or []:
        L.append("| %s | %s | %s | %s | %s | %s |" % (
            names.get(r["tag"], r["tag"]),
            "{:,.0f}".format(r.get("capital_cny") or 0),
            r.get("verdict") or "—",
            (("、".join(r.get("unfilled") or []) or "—") if r.get("n_unfilled")
             else ("无（残差超线）" if fault_of(r) == "residual" else "全部买进")),
            ("%.4f" % r["residual_pct_nav"]) if r.get("residual_pct_nav") is not None else "—",
            "{:,.0f}".format(r.get("traded_amount_cny") or 0)))
    L.append("")
    L.append("## 判词\n")
    L.append("**%s** — %s\n" % (out.get("verdict"), out.get("sentence")))
    L.append("一手门槛（每一名至少一手所需的最小资本）**%s 元**；"
             "平常档与它的差 **%s 元**（正值＝平常的日子还差这么多钱才装得下，负值＝有余量）。\n"
             % ("{:,.2f}".format(out.get("one_lot_floor_cny") or 0),
                "{:,.2f}".format(out.get("shortfall_to_typical_cny") or 0)))
    L.append("## 口径与限制\n")
    L.append("- 整手口径与票面面同源：`etf_book_ticket_floor.py` 的 `resolve()` 直接 import，"
             "没有第二份实现，两面不会对「一手多少钱」有分歧。\n")
    L.append("- 三个资本来自容量闸的面，不是这一面自己挑的；闸用的是「收盘×成交量」的 20 日中位再中位，"
             "是阶梯状读数（60 天只落几十个值），所以「平常的一天」是这把尺子的中位，不是成交明细的中位。\n")
    L.append("- 8% 波动目标的现金槽（票面 `cash_weight`）不算残差，这一点沿用票面面的口径。\n")
    path = OUT_MD
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")
    return path


def check():
    """Re-derive every printed number from disk and from the source faces."""
    problems = []
    if not os.path.exists(OUT_JSON):
        print(json.dumps({"ok": False, "problems": ["face missing"]}, ensure_ascii=False))
        return 2
    with open(OUT_JSON, "r", encoding="utf-8") as fh:
        pub = json.load(fh)
    face = load_capacity()
    path = TF.newest_ticket()
    ticket = TF.load_ticket(path)
    got = derive(ticket, face)
    if got["verdict"] != pub.get("verdict"):
        problems.append("verdict re-derives to %s, face says %s"
                        % (got["verdict"], pub.get("verdict")))
    if got["one_lot_floor_cny"] != pub.get("one_lot_floor_cny"):
        problems.append("one-lot floor re-derives to %s, face says %s"
                        % (got["one_lot_floor_cny"], pub.get("one_lot_floor_cny")))
    if got["shortfall_to_typical_cny"] != pub.get("shortfall_to_typical_cny"):
        problems.append("shortfall re-derives to %s, face says %s"
                        % (got["shortfall_to_typical_cny"], pub.get("shortfall_to_typical_cny")))
    # the rung capitals must be the gate's own numbers, not re-read or rounded here
    gate = (face or {}).get("summary") or {}
    for r in pub.get("rungs") or []:
        src = gate.get(r["source_key"])
        if r.get("capital_cny") != src:
            problems.append("rung %s capital %s != gate %s" % (r["tag"], r.get("capital_cny"), src))
    for a, b in zip(pub.get("rungs") or [], got["rungs"]):
        if a.get("verdict") != b.get("verdict"):
            problems.append("rung %s verdict %s != re-derived %s" % (a["tag"], a.get("verdict"), b.get("verdict")))
        if (a.get("unfilled") or []) != (b.get("unfilled") or []):
            problems.append("rung %s unfilled %s != re-derived %s" % (a["tag"], a.get("unfilled"), b.get("unfilled")))
    if pub.get("sentence") != sentence(pub):
        problems.append("sentence does not match its own verdict")
    # the reader's page must carry this run's verdict, not a previous generation's
    if not os.path.exists(OUT_MD):
        problems.append("page missing")
    else:
        with open(OUT_MD, "r", encoding="utf-8") as fh:
            md = fh.read()
        if str(pub.get("verdict")) not in md:
            problems.append("page does not print the verdict")
        if "%%" in md:
            problems.append("page carries a literal double percent -- the escape is leaking")
    n_ok = sum(1 for r in pub.get("rungs") or [] if is_tradable(r.get("verdict")))
    if n_ok != pub.get("n_rungs_tradable"):
        problems.append("n_rungs_tradable %s != count %d" % (pub.get("n_rungs_tradable"), n_ok))
    print(json.dumps({"ok": not problems, "problems": problems,
                      "verdict": pub.get("verdict")}, ensure_ascii=False))
    return 0 if not problems else 1


# ---------------------------------------------------------------- selftest

def _ticket(prices, weights, cash=0.0, bar="2026-01-05"):
    order = [{"symbol": "T%d" % i, "name": "N%d" % i, "class": "equity",
              "weight": w, "price": p, "amount": 0.0, "lots": 0, "shares": 0, "note": ""}
             for i, (p, w) in enumerate(zip(prices, weights))]
    return {"asof_bar": bar, "order": order, "cash_weight": cash, "cash_leg": "test"}


def _face(cmax, cmed, cmin, verdict="BELOW_LINE_EVERY_SESSION"):
    return {"summary": {"capital_max_cny": cmax, "capital_median_cny": cmed,
                        "capital_min_cny": cmin, "verdict": verdict, "n_sessions": 60},
            "evidence_cutoff": "2026-01-05"}


def selftest():
    legs = []

    def leg(name, fn):
        try:
            fn()
            legs.append({"leg": name, "pass": True})
        except AssertionError as exc:
            legs.append({"leg": name, "pass": False, "detail": str(exc)})

    # 1. every rung places -> TRADABLE_IN_EVERY_READ_SESSION
    def l1():
        t = _ticket([1.0, 2.0], [0.5, 0.5])
        out = derive(t, _face(1_000_000, 900_000, 800_000))
        assert out["verdict"] == "TRADABLE_IN_EVERY_READ_SESSION", out["verdict"]
        assert out["n_rungs_tradable"] == 3, out["n_rungs_tradable"]
    leg("three rungs all place", l1)

    # 2. the worst session drops a name -> TRADABLE_ON_A_TYPICAL_DAY
    def l2():
        # one lot of T0 = 100*1000 = 100,000; at 100 CNY of capital its slice is 50 CNY
        t = _ticket([1000.0, 1.0], [0.5, 0.5])
        out = derive(t, _face(10_000_000, 1_000_000, 1_000))
        assert out["verdict"] == "TRADABLE_ON_A_TYPICAL_DAY", out["verdict"]
        worst = [r for r in out["rungs"] if r["tag"] == "worst"][0]
        assert worst["n_unfilled"] == 1 and worst["unfilled"] == ["T0"], worst
    leg("worst session cannot buy one lot", l2)

    # 3. only the best session places -> TRADABLE_ONLY_ON_THE_BEST_DAY
    def l3():
        t = _ticket([100.0, 2.0], [0.5, 0.5])
        out = derive(t, _face(1_000_000, 300, 200))
        assert out["verdict"] == "TRADABLE_ONLY_ON_THE_BEST_DAY", out["verdict"]
    leg("only the best session places", l3)

    # 4. nothing places -> NOT_TRADABLE_ON_ANY_PRICED_DAY
    def l4():
        t = _ticket([100.0, 2.0], [0.5, 0.5])
        out = derive(t, _face(300, 200, 100))
        assert out["verdict"] == "NOT_TRADABLE_ON_ANY_PRICED_DAY", out["verdict"]
    leg("no priced day places", l4)

    # 5. a rung that fits but strands too much cash is not "tradable" (floor's own rule)
    def l5():
        # at 500 each slice is 150 and one lot costs 100 -> it fits but strands a third of NAV
        t = _ticket([1.0, 1.0, 1.0], [0.30, 0.30, 0.30])
        out = derive(t, _face(500, 500, 500))
        assert out["verdict"] == "NOT_TRADABLE_ON_ANY_PRICED_DAY", (out["verdict"],
                                                                    out["rungs"])
    leg("fits-but-strands is not tradable", l5)

    # 6. no capacity face -> refuses
    def l6():
        out = derive(_ticket([1.0], [1.0]), None)
        assert out["verdict"] == "CAPACITY_FACE_MISSING", out["verdict"]
    leg("missing capacity face refuses", l6)

    # 7. no ticket -> the resolver's TICKET_MISSING propagates, never a pass
    def l7():
        out = derive(None, _face(1_000_000, 900_000, 800_000))
        assert out["verdict"] == "NOT_TRADABLE_ON_ANY_PRICED_DAY", out["verdict"]
        assert all((r["unfilled"] or []) == [] for r in out["rungs"]), out["rungs"]
    leg("missing ticket never reads as placeable", l7)

    # 8. shortfall == one-lot floor - typical capital
    def l8():
        t = _ticket([100.0, 2.0], [0.5, 0.5])
        out = derive(t, _face(1_000_000, 300, 200))
        assert out["one_lot_floor_cny"] == 20000.0, out["one_lot_floor_cny"]
        assert out["shortfall_to_typical_cny"] == round(out["one_lot_floor_cny"] - 300, 2), \
            out["shortfall_to_typical_cny"]
    leg("shortfall = floor - typical", l8)

    # 9. the rung rows use the floor face's own resolver (no second lot implementation)
    def l9():
        t = _ticket([12.34, 5.67], [0.6, 0.4])
        cap = 250_000
        out = derive(t, _face(cap, cap, cap))
        direct = TF.resolve(t, cap)
        assert out["rungs"][0]["traded_amount_cny"] == direct["traded_amount_cny"], out
        assert out["rungs"][0]["residual_pct_nav"] == direct["residual_pct_nav"], out
    leg("rows come from the floor resolver verbatim", l9)

    # 10. the verdict follows the count, not the tag order
    def l10():
        rows = [{"tag": "best", "verdict": "TRADABLE_AT_1000000"},
                {"tag": "typical", "verdict": "TRADABLE_AT_496475"},
                {"tag": "worst", "verdict": "TRADABLE_AT_340837"}]
        assert verdict_from_rungs(rows) == "TRADABLE_IN_EVERY_READ_SESSION"
        rows[2]["verdict"] = "BELOW_FLOOR_AT_340837"
        assert verdict_from_rungs(rows) == "TRADABLE_ON_A_TYPICAL_DAY"
        rows[1]["verdict"] = "BELOW_FLOOR_AT_496475"
        assert verdict_from_rungs(rows) == "TRADABLE_ONLY_ON_THE_BEST_DAY"
        rows[0]["verdict"] = "BELOW_FLOOR_AT_1000000"
        assert verdict_from_rungs(rows) == "NOT_TRADABLE_ON_ANY_PRICED_DAY"
    leg("verdict is a count of rungs", l10)

    # 11. a gate that publishes no capital is named, not silently zero
    def l11():
        rows = [{"tag": "best", "verdict": "TRADABLE_AT_1"},
                {"tag": "typical", "verdict": None},
                {"tag": "worst", "verdict": "TRADABLE_AT_1"}]
        assert verdict_from_rungs(rows) == "CAPACITY_FACE_MISSING"
    leg("missing rung capital is named", l11)

    # 12. the sentence quotes its own numbers and switches with the verdict
    def l12():
        t = _ticket([100.0, 2.0], [0.5, 0.5])
        out = derive(t, _face(1_000_000, 300, 200))
        s = sentence(out)
        assert "1,000,000" in s and "300" in s, s
        out2 = derive(t, _face(1_000_000, 900_000, 800_000))
        assert sentence(out2) != s, "the sentence must move with the verdict"
    leg("sentence quotes its own numbers", l12)

    # 13. a rung that fits but strands too much is never printed as "names cannot buy"
    def l13():
        t = _ticket([1.0, 1.0, 1.0], [0.30, 0.30, 0.30])
        out = derive(t, _face(500, 500, 500))
        worst = out["rungs"][0]
        assert fault_of(worst) == "residual", fault_of(worst)
        payload = dict(out, frozen={"residual_max_pct": TF.RESIDUAL_MAX_PCT})
        s = sentence(dict(payload, verdict="TRADABLE_ON_A_TYPICAL_DAY"))
        assert "连一手都买不到" not in s and "残差" in s, s
    leg("stranded residue is not printed as unbuyable", l13)

    # 14. the three fault shapes stay distinct
    def l14():
        assert fault_of({"verdict": "BELOW_FLOOR_AT_1", "n_unfilled": 2}) == "unfilled"
        assert fault_of({"verdict": "RESIDUAL_TOO_BIG_AT_1", "n_unfilled": 0}) == "residual"
        assert fault_of({"verdict": "TRADABLE_AT_1", "n_unfilled": 0}) == "none"
        assert fault_of({"verdict": None}) == "unknown"
    leg("fault shapes are distinct", l14)

    failed = [x for x in legs if not x["pass"]]
    print(json.dumps({"selftest": "%d/%d" % (len(legs) - len(failed), len(legs)),
                      "failed": failed}, ensure_ascii=False, indent=1))
    return 0 if not failed else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("cmd", nargs="?", default="run", choices=["run", "check", "selftest"])
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest or args.cmd == "selftest":
        return selftest()
    if args.check or args.cmd == "check":
        return check()
    run()
    return 0


if __name__ == "__main__":
    sys.exit(main())

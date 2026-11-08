"""Is the size the permission refuses actually the size the desk orders?

r1450 turned five readings of one sizing rule into a permission and printed one
subtraction: the 2026-11-11 rebalance must size at k=0.393073 (CNY 392,616), a cut of
CNY 67,180 (6.72pp) from the weight in force.

That is a statement about what is ALLOWED.  It is not a statement about what will be
ORDERED.  The order path (`scripts/etf_book_order.py`) derives its own k from an
expanding beta (`k = beta_target / beta_hat`, clipped to [0,1]) and has no notion of a
permission.  So the two published surfaces can disagree, and a reader of the permission
face has no way to tell whether the CNY 67,180 is a decision or a decoration.

This face answers that one question from published receipts and the source tree only
(no panel, no repricing, no engine import):

  * ordered_k   -- machine-read from the newest TICKET-*.json (the size in force);
  * permitted_k -- machine-read from results/etf_book_rebalance_permission.json;
  * binding     -- does ANY other program read the permission receipt's numbers?
                   A receipt nobody reads cannot bind an order, no matter how true it is;
  * the trim    -- per-leg lots to sell on the decision bar, floored (an integer-lot trim
                   must never round the book back UP over the permission), plus what the
                   trim actually costs: 8bp one side on the sold amount and the repo
                   carry the freed cash earns.

The pick set is re-derived at the 11-11 decision bar, so the per-leg rows are marked
illustrative on the 11-06 names while the sleeve total is exact.

Read-only.  Deterministic.  No network.
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import os
import sys
import time

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PERMISSION_RECEIPT = "results/etf_book_rebalance_permission.json"
TICKET_DIR = os.path.join(BASE, "results", "etf_book_order")
OUT = os.path.join(BASE, "results", "etf_book_cut_order_gap.json")
MD = os.path.join(BASE, "research", "ETF_BOOK_CUT_ORDER_GAP.md")

SIZE_TOL = 0.005              # 0.5pp: the same "same size" tolerance the rulers table uses
COST_BP_PER_SIDE = 8.0        # paper convention; the ticket publishes its own value
IDENT_TOL = 1e-6

# keys whose presence in another module means someone consumes the permission
PERMISSION_KEYS = ("permitted_k", "permitted_book_cny", "cut_cny", "etf_book_rebalance_permission.json")
# reading a number is not the same as acting on it (E206: a name must say what it measures).
# A module counts as an ENFORCER only if it calls the shared trim that lands the book at or
# below the floor -- otherwise it is a printer, and a printer cannot bind an order.
ENFORCER_KEYS = ("trim_legs(", "permission_block(")
SELF_NAME = "etf_book_cut_order_gap"

VERDICT_UNBOUND = "ORDER_EXCEEDS_PERMISSION_NOBODY_READS_IT"
VERDICT_BOUND = "ORDER_EXCEEDS_PERMISSION_BUT_WIRED"
VERDICT_WITHIN = "ORDER_WITHIN_PERMISSION"
VERDICT_UNREADABLE = "UNREADABLE"


def _read_json(rel):
    p = rel if os.path.isabs(rel) else os.path.join(BASE, rel)
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def latest_ticket():
    files = sorted(glob.glob(os.path.join(TICKET_DIR, "TICKET-*.json")))
    files = [f for f in files if "-card" not in os.path.basename(f)]
    if not files:
        return None, None
    with open(files[-1], encoding="utf-8") as f:
        d = json.load(f)
    d["_file"] = os.path.basename(files[-1])
    return os.path.basename(files[-1]), d


def latest_repo_rate():
    """GC001 observed close (annualised %) -- machine-read, never typed in."""
    try:
        sys.path.insert(0, BASE)
        from scripts import etf_phase_beta_window as BW
        s = BW.load_repo_rates()
    except Exception:
        return None, None
    if s is None or not len(s):
        return None, None
    return float(s.iloc[-1]), str(s.index[-1].date())


def source_corpus():
    """{module_name: text} over the two code roots, for the consumer scan."""
    out = {}
    for root in ("scripts", "Tools"):
        d = os.path.join(BASE, root)
        if not os.path.isdir(d):
            continue
        for p in glob.glob(os.path.join(d, "*.py")):
            try:
                with open(p, encoding="utf-8", errors="replace") as f:
                    out["%s/%s" % (root, os.path.basename(p))] = f.read()
            except OSError:
                continue
    return out


def readers_of(corpus, producer="scripts/etf_book_rebalance_permission.py"):
    """Modules that consume the permission's NUMBERS (not the ones that merely run it)."""
    hits = []
    for name, text in corpus.items():
        if name == producer or SELF_NAME in name:
            continue
        if any(k in text for k in PERMISSION_KEYS):
            hits.append(name)
    return sorted(hits)


def enforcers_of(corpus, readers):
    """Readers that actually apply the trim. A printer is not an enforcer (E206)."""
    return sorted(r for r in readers
                  if any(k in (corpus.get(r) or "") for k in ENFORCER_KEYS))


def trim_legs(legs, permitted, nav, und):
    """Integer-lot trim that lands the sleeve at or below `permitted` k.

    Shared by this face and the order sheet itself (r1455): the sheet a desk executes and
    the receipt that audits it must be the same arithmetic, or obeying the permission
    depends on which file someone happened to open.

    Floored, never rounded: an integer-lot trim that rounded could put the book back over
    the permission it is trying to obey.
    """
    legs = legs or []
    n_hold = len(legs)
    out = []
    sold = 0.0
    kept = 0.0
    target_w = (permitted / float(n_hold)) if n_hold else None
    for row in legs:
        px = float(row.get("price") or 0.0)
        cur_lots = int(row.get("lots") or 0)
        if px <= 0 or target_w is None:
            out.append({"symbol": row.get("symbol"), "price": row.get("price"),
                        "lots_now": cur_lots, "lots_target": None,
                        "priced": False, "why": "no price on the ticket row"})
            continue
        target_lots = int(math.floor((target_w * nav) / (px * 100.0)))  # floor: never round up
        sell = max(cur_lots - target_lots, 0)
        sold += sell * px * 100.0
        kept += target_lots * px * 100.0
        out.append({"symbol": row.get("symbol"), "price": px, "lots_now": cur_lots,
                    "lots_target": target_lots, "lots_sell": sell,
                    "sell_cny": round(sell * px * 100.0, 2), "priced": True})
    k_after = ((kept + nav * und / 100.0) / nav) if n_hold else None
    return {
        "n_legs": n_hold,
        "target_weight_per_leg": None if target_w is None else round(target_w, 6),
        "legs": out,
        "lots_sell_total": sum(int(r.get("lots_sell") or 0) for r in out if r.get("priced")),
        "sold": sold,
        "sold_cny": round(sold, 2),
        "k_after": k_after,
    }


def plan_cut(perm, ticket, repo_rate, repo_date, readers, cost_bp=COST_BP_PER_SIDE,
             enforcers=None):
    """Pure function of published receipts + the consumer list."""
    if perm is None:
        return {"verdict": VERDICT_UNREADABLE, "reason": "missing_permission_receipt",
                "sentence": "no permission receipt on disk: nothing forbids the order, and "
                            "this face will not invent a cut"}
    if ticket is None:
        return {"verdict": VERDICT_UNREADABLE, "reason": "missing_ticket",
                "sentence": "no ticket on disk: there is no ordered size to compare"}
    k_now = ticket.get("k_now")
    permitted = perm.get("permitted_k")
    tk = ticket.get("ticket") or {}
    nav = tk.get("nav")
    if k_now is None or permitted is None or nav is None:
        return {"verdict": VERDICT_UNREADABLE, "reason": "incomplete_receipts",
                "sentence": "the ticket or the permission is missing k_now/permitted_k/nav"}

    k_now = float(k_now)
    permitted = float(permitted)
    nav = float(nav)
    und = float(tk.get("underspend_pct") or 0.0)
    ordered_book = k_now * nav - nav * und / 100.0
    permitted_book = permitted * nav - nav * und / 100.0
    cut_cny = ordered_book - permitted_book
    exceeds = k_now > permitted + SIZE_TOL

    t = trim_legs(tk.get("order") or [], permitted, nav, und)
    n_hold = t["n_legs"]
    trim = t["legs"]
    sold = t["sold"]
    k_after = t["k_after"]

    tx = sold * cost_bp / 10000.0
    carry = None if repo_rate is None else cut_cny * float(repo_rate) / 100.0
    realized = ((ticket.get("metrics") or {}).get("book") or {}).get("cagr")
    shadow = ((ticket.get("metrics") or {}).get("same_beta_benchmark") or {}).get("cagr")
    giveup = {}
    if repo_rate is not None:
        for label, cagr in (("book_realized", realized), ("same_beta_benchmark", shadow)):
            if cagr is not None:
                giveup[label] = round(cut_cny * (float(cagr) - float(repo_rate) / 100.0), 2)

    if not exceeds:
        verdict = VERDICT_WITHIN
    else:
        verdict = VERDICT_BOUND if readers else VERDICT_UNBOUND

    if not exceeds:
        sentence = ("the ticket orders k=%.6f (CNY %s) and the permission allows %.6f "
                    "(CNY %s): no cut is owed on %s"
                    % (k_now, format(ordered_book, ",.0f"), permitted,
                       format(permitted_book, ",.0f"), perm.get("decision_date")))
    elif readers:
        enforcers = list(enforcers or [])
        if enforcers:
            sentence = ("the ticket orders k=%.6f (CNY %s) against a permission of %.6f "
                        "(CNY %s) -- CNY %s over -- and %d module(s) read the permission, "
                        "%d of which apply the trim: %s"
                        % (k_now, format(ordered_book, ",.0f"), permitted,
                           format(permitted_book, ",.0f"), format(cut_cny, ",.0f"),
                           len(readers), len(enforcers), ", ".join(sorted(enforcers))))
        else:
            sentence = ("the ticket orders k=%.6f (CNY %s) against a permission of %.6f "
                        "(CNY %s) -- CNY %s over -- and %d module(s) read the permission, "
                        "but none applies the trim, so reading it does not bind the order"
                        % (k_now, format(ordered_book, ",.0f"), permitted,
                           format(permitted_book, ",.0f"), format(cut_cny, ",.0f"),
                           len(readers)))
    else:
        sentence = ("the ticket path will order k=%.6f (CNY %s) on %s while the permission "
                    "allows %.6f (CNY %s): CNY %s (%.2fpp) is refused on paper and NO module "
                    "reads the permission receipt, so nothing in the order path will trim it"
                    % (k_now, format(ordered_book, ",.0f"), perm.get("decision_date"),
                       permitted, format(permitted_book, ",.0f"),
                       format(cut_cny, ",.0f"), 100.0 * (k_now - permitted)))

    return {
        "face": "etf_book_cut_order_gap",
        "decision_date": perm.get("decision_date"),
        "ticket_file": ticket.get("_file"),
        "evidence_cutoff": ticket.get("evidence_cutoff") or ticket.get("ticket", {}).get("evidence_cutoff"),
        "k_now": round(k_now, 6),
        "permitted_k": round(permitted, 6),
        "gap_k": round(k_now - permitted, 6),
        "gap_pp": round(100.0 * (k_now - permitted), 2),
        "nav_cny": nav,
        "ordered_book_cny": round(ordered_book, 2),
        "permitted_book_cny": round(permitted_book, 2),
        "cut_cny": round(cut_cny, 2),
        "order_exceeds_permission": bool(exceeds),
        "permission_readers": readers,
        "permission_enforcers": sorted(enforcers or []),
        "permission_is_binding": bool(enforcers or []) or not exceeds,
        "verdict": verdict,
        "sentence": sentence,
        "trim": {
            "basis": "the 11-06 pick set; the 11-11 decision bar re-derives the names, so "
                     "these rows are illustrative while the sleeve total is exact",
            "n_legs": n_hold,
            "target_weight_per_leg": None if not n_hold else round(permitted / n_hold, 6),
            "legs": trim,
            "lots_sell_total": sum(int(r.get("lots_sell") or 0) for r in trim if r.get("priced")),
            "sold_cny": round(sold, 2),
            "k_after_integer_lots": None if k_after is None else round(k_after, 6),
            "trim_within_permission": None if k_after is None else bool(k_after <= permitted + IDENT_TOL),
        },
        "cost": {
            "cost_bp_per_side": cost_bp,
            "tx_cny_one_side": round(tx, 2),
            "repo_rate_pct": None if repo_rate is None else round(float(repo_rate), 4),
            "repo_rate_date": repo_date,
            "carry_cny_per_year": None if carry is None else round(carry, 2),
            "giveup_cny_per_year_ex_post": giveup,
            "note": "give-up is the sleeve's own realized CAGR minus the observed repo rate on "
                    "the trimmed amount: an ex-post reading, not a forecast, and it is the "
                    "price of obeying a gate that failed on concentration, not a return estimate",
        },
        "not_measured": [
            "the year gate on the trimmed book: a smaller k is not automatically a passing "
            "book (r1438/r1450: the wrapper's yearly shape has never been through it)",
            "whether the 11-11 pick set changes names: the trim ratio holds at the sleeve "
            "level, the per-leg rows do not survive a re-pick",
            "the carry accrual path: one observed GC001 close is used for the annualised "
            "figure; a holiday gap accrues more days than the rate implies",
        ],
    }


def run():
    perm = _read_json(PERMISSION_RECEIPT)
    _, ticket = latest_ticket()
    rate, rdate = latest_repo_rate()
    corpus = source_corpus()
    readers = readers_of(corpus)
    d = plan_cut(perm, ticket, rate, rdate, readers,
                 enforcers=enforcers_of(corpus, readers))
    d["repo_source"] = "data/repo_daily/GC001.csv (observed close)"
    return d


def published_face():
    p = OUT if os.path.isabs(OUT) else os.path.join(BASE, OUT)
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def md_lines(d):
    L = ["# The size the permission refuses vs the size the desk orders", ""]
    L += ["- 判定：**%s**" % d.get("verdict"),
          "- 决策日：%s ｜ 票据：%s ｜ 证据截止：%s"
          % (d.get("decision_date"), d.get("ticket_file"), d.get("evidence_cutoff")), ""]
    L += ["## 一句话", "", d.get("sentence") or "", ""]
    L += ["## 两侧的数", "",
          "| 读数 | k | 风险腿金额 CNY |", "|---|---|---|",
          "| 票据将下单 | %.6f | %s |" % (d.get("k_now") or 0, format(d.get("ordered_book_cny") or 0, ",.0f")),
          "| 权限允许 | %.6f | %s |" % (d.get("permitted_k") or 0, format(d.get("permitted_book_cny") or 0, ",.0f")),
          "| 差额 | %.6f（%.2fpp） | %s |"
          % (d.get("gap_k") or 0, d.get("gap_pp") or 0, format(d.get("cut_cny") or 0, ",.0f")), ""]
    t = d.get("trim") or {}
    L += ["## 逐腿削减（%s）" % t.get("basis", ""), "",
          "| 代码 | 价 | 现手数 | 目标手数 | 卖出手数 | 卖出 CNY |", "|---|---|---|---|---|---|"]
    for r in t.get("legs") or []:
        if not r.get("priced"):
            L += ["| %s | %s | %s | — | — | 未定价 |"
                  % (r.get("symbol"), r.get("price"), r.get("lots_now"))]
            continue
        L += ["| %s | %s | %d | %d | %d | %s |"
              % (r.get("symbol"), r.get("price"), r.get("lots_now"), r.get("lots_target"),
                 r.get("lots_sell"), format(r.get("sell_cny") or 0, ",.0f"))]
    L += ["", "- 卖出手数合计 %s 手，金额 CNY %s；整手取整后 k=%.6f（%s）"
          % (t.get("lots_sell_total"), format(t.get("sold_cny") or 0, ",.0f"),
             t.get("k_after_integer_lots") or 0,
             "不超过权限" if t.get("trim_within_permission") else "**超出权限**"), ""]
    c = d.get("cost") or {}
    L += ["## 削减的代价", "",
          "- 交易成本（%.0fbp 单边 × 卖出额）：CNY %s"
          % (c.get("cost_bp_per_side") or 0, format(c.get("tx_cny_one_side") or 0, ",.2f")),
          "- 释放现金的回购收益：年化 CNY %s（GC001 %s%%，%s 收盘）"
          % (format(c.get("carry_cny_per_year") or 0, ",.2f"),
             c.get("repo_rate_pct"), c.get("repo_rate_date"))]
    for k, v in (c.get("giveup_cny_per_year_ex_post") or {}).items():
        L += ["- 若风险腿维持 %s 的已实现年化：少赚 CNY %s/年" % (k, format(v, ",.0f"))]
    L += ["- %s" % (c.get("note") or ""), ""]
    nm = d.get("not_measured") or []
    if nm:
        L += ["## 未测", ""] + ["- " + x for x in nm] + [""]
    return L


def check():
    """Re-derive the published receipt from its own sources; refuse a stale face."""
    d = published_face()
    if not d:
        print("MISSING %s" % OUT)
        return 1
    fresh = run()
    fails = []

    def leg(ok, msg):
        if not ok:
            fails.append(msg)

    for k in ("verdict", "k_now", "permitted_k", "order_exceeds_permission",
              "permission_is_binding", "cut_cny"):
        leg(fresh.get(k) == d.get(k), "field %s: disk=%r fresh=%r" % (k, d.get(k), fresh.get(k)))
    leg(abs((fresh.get("trim") or {}).get("k_after_integer_lots", 0)
            - (d.get("trim") or {}).get("k_after_integer_lots", 0)) <= 1e-6,
        "trimmed k drifted: disk=%r fresh=%r"
        % ((d.get("trim") or {}).get("k_after_integer_lots"),
           (fresh.get("trim") or {}).get("k_after_integer_lots")))
    leg(fresh.get("permission_readers") == d.get("permission_readers"),
        "consumer list drifted: disk=%r fresh=%r"
        % (d.get("permission_readers"), fresh.get("permission_readers")))
    leg(fresh.get("permission_enforcers") == d.get("permission_enforcers"),
        "enforcer list drifted: disk=%r fresh=%r"
        % (d.get("permission_enforcers"), fresh.get("permission_enforcers")))
    leg(fresh.get("ticket_file") == d.get("ticket_file"),
        "a newer ticket landed since this receipt was written (disk=%r fresh=%r): re-run"
        % (d.get("ticket_file"), fresh.get("ticket_file")))
    for f in fails:
        print("  FAIL " + f)
    print("[check] %d/%d OK" % (7 - len(fails), 7))
    return 0 if not fails else 1


LIVE_PRICES = [("159501", 2.069), ("513100", 2.158), ("513690", 1.158),
               ("159577", 1.612), ("159263", 1.143)]


def _tk(k_now, legs=None, nav=1000000.0, und=0.0457, cagr=0.1246, bench=0.0287):
    """A ticket whose lots are DERIVED from k_now -- a fixture that states one book in the
    header and another in the legs cannot be used to prove anything about either."""
    if legs is None:
        w = k_now / float(len(LIVE_PRICES)) * nav
        legs = [{"symbol": s, "price": p,
                 "lots": int(math.floor(w / (p * 100.0)))} for s, p in LIVE_PRICES]
    for L in legs:
        L["amount"] = round(int(L["lots"]) * float(L["price"]) * 100.0, 2)
    return {"k_now": k_now, "evidence_cutoff": "2026-11-06", "_file": "TICKET-fixture.json",
            "ticket": {"nav": nav, "underspend_pct": und, "order": legs,
                       "book_amount": round(k_now * nav - nav * und / 100.0, 2)},
            "metrics": {"book": {"cagr": cagr}, "same_beta_benchmark": {"cagr": bench}}}


def _perm(k=0.393073, date="2026-11-11"):
    return {"permitted_k": k, "decision_date": date}


def selftest():
    fails = []

    def leg(ok, msg):
        if not ok:
            fails.append(msg)

    rate, rdate = 1.185, "2026-11-06"

    # L1 the live pair: the order path is 6.72pp over and nobody reads the permission
    d = plan_cut(_perm(), _tk(0.460253), rate, rdate, readers=[])
    leg(d["verdict"] == VERDICT_UNBOUND, "L1 verdict=%r" % d["verdict"])
    leg(abs(d["cut_cny"] - 67180.0) <= 1.0, "L1 cut_cny=%r" % d.get("cut_cny"))
    leg(abs(d["permitted_book_cny"] - 392616.3) <= 1.0, "L1 permitted_book=%r" % d.get("permitted_book_cny"))
    leg(d["permission_is_binding"] is False, "L1 binding=%r" % d.get("permission_is_binding"))

    # L2 a reader flips the verdict -- a leg that can only say "unbound" is not evidence
    d = plan_cut(_perm(), _tk(0.460253), rate, rdate, readers=["scripts/etf_book_order.py"],
                 enforcers=["scripts/etf_book_order.py"])
    leg(d["verdict"] == VERDICT_BOUND and d["permission_is_binding"] is True,
        "L2 verdict=%r binding=%r" % (d["verdict"], d.get("permission_is_binding")))

    # L3 a ticket already inside the permission owes no trim
    d = plan_cut(_perm(), _tk(0.393000), rate, rdate, readers=[])
    leg(d["verdict"] == VERDICT_WITHIN, "L3 verdict=%r" % d["verdict"])
    leg(all(not r.get("lots_sell") for r in d["trim"]["legs"]), "L3 sold=%r" % d["trim"]["legs"])

    # L4 missing receipts never become a default trim
    leg(plan_cut(None, _tk(0.46), rate, rdate, [])["verdict"] == VERDICT_UNREADABLE, "L4 no perm")
    leg(plan_cut(_perm(), None, rate, rdate, [])["verdict"] == VERDICT_UNREADABLE, "L4 no ticket")

    # L5 integer lots must floor, never round the book back over the permission
    d = plan_cut(_perm(), _tk(0.460253), rate, rdate, readers=[])
    leg(d["trim"]["k_after_integer_lots"] <= d["permitted_k"] + IDENT_TOL,
        "L5 k_after=%r > permitted=%r" % (d["trim"]["k_after_integer_lots"], d["permitted_k"]))
    leg(d["trim"]["trim_within_permission"] is True, "L5 flag=%r" % d["trim"]["trim_within_permission"])

    # L6 the lot boundary: exact division takes every lot it can, one fen more per lot
    # takes one fewer -- a floor that rounds up would pass the first and fail the second
    legs = [{"symbol": "X", "price": 78.6146, "lots": 60}]
    d = plan_cut(_perm(), _tk(0.460253, legs=legs, und=0.0), rate, rdate, readers=[])
    leg(d["trim"]["legs"][0]["lots_target"] == 50, "L6 exact target=%r" % d["trim"]["legs"][0]["lots_target"])
    legs = [{"symbol": "X", "price": 78.6147, "lots": 60}]
    d = plan_cut(_perm(), _tk(0.460253, legs=legs, und=0.0), rate, rdate, readers=[])
    leg(d["trim"]["legs"][0]["lots_target"] == 49, "L6 over-boundary target=%r"
        % d["trim"]["legs"][0]["lots_target"])

    # L7 costs use the rate passed in, not a constant, and the bp is on the sold amount
    d = plan_cut(_perm(), _tk(0.460253), 2.0, "2026-11-06", readers=[])
    leg(abs(d["cost"]["carry_cny_per_year"] - d["cut_cny"] * 0.02) <= 0.5,
        "L7 carry=%r" % d["cost"]["carry_cny_per_year"])
    leg(abs(d["cost"]["tx_cny_one_side"] - d["trim"]["sold_cny"] * 0.0008) <= 0.5,
        "L7 tx=%r sold=%r" % (d["cost"]["tx_cny_one_side"], d["trim"]["sold_cny"]))

    # L8 the consumer scan must find a real reader and ignore producers/schedulers
    corpus = {"scripts/etf_book_rebalance_permission.py": "permitted_k = min(paths)",
              "scripts/etf_book_cut_order_gap.py": "PERMISSION_KEYS = ('permitted_k',)",
              "Tools/s6_chain_bmc.py": "python scripts/etf_book_rebalance_permission.py check",
              "scripts/consumer.py": "p = json.load(open('results/etf_book_rebalance_permission.json'))"}
    leg(readers_of(corpus) == ["scripts/consumer.py"], "L8 readers=%r" % readers_of(corpus))

    # L8b reading a permission is not the same as enforcing it (E206). A printer that only
    # loads the receipt must never be counted as the thing that binds the order.
    corpus_ro = dict(corpus, **{"scripts/printer.py":
                                "p = json.load(open('results/etf_book_rebalance_permission.json'))"
                                "\nprint(p['permitted_k'])"})
    leg(enforcers_of(corpus_ro, readers_of(corpus_ro)) == [],
        "L8b printer counted as enforcer=%r" % enforcers_of(corpus_ro, readers_of(corpus_ro)))
    corpus_en = dict(corpus, **{"scripts/applier.py":
                                "p = json.load(open('results/etf_book_rebalance_permission.json'))"
                                "\nfrom scripts.etf_book_cut_order_gap import trim_legs"
                                "\nprint(trim_legs([], p['permitted_k'], 1e6, 0))"})
    leg(enforcers_of(corpus_en, readers_of(corpus_en)) == ["scripts/applier.py"],
        "L8b applier missed=%r" % enforcers_of(corpus_en, readers_of(corpus_en)))

    # L9 the two book sides must add back to the ticket's own amount
    d = plan_cut(_perm(), _tk(0.460253), rate, rdate, readers=[])
    leg(abs((d["permitted_book_cny"] + d["cut_cny"]) - d["ordered_book_cny"]) <= 1.0,
        "L9 sum=%r vs %r" % (d["permitted_book_cny"] + d["cut_cny"], d["ordered_book_cny"]))

    # L10 the sentence must carry the numbers the flags say
    leg(("%.6f" % d["k_now"]) in (d.get("sentence") or ""), "L10 sentence=%r" % d.get("sentence"))
    leg(format(d["cut_cny"], ",.0f") in (d.get("sentence") or ""), "L10 cut in sentence")

    # L11 the sentence must not call a printer an enforcer
    _s_ro = plan_cut(_perm(), _tk(0.460253), rate, rdate, readers=["scripts/printer.py"],
                     enforcers=[])["sentence"]
    _s_en = plan_cut(_perm(), _tk(0.460253), rate, rdate, readers=["scripts/applier.py"],
                     enforcers=["scripts/applier.py"])["sentence"]
    leg("none applies the trim" in _s_ro and "apply the trim" in _s_en,
        "L11 ro=%r en=%r" % (_s_ro[:70], _s_en[:70]))

    for f in fails:
        print("  FAIL " + f)
    print("[selftest] %d/%d PASS" % (12 - len(fails), 12))
    return 0 if not fails else 1


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    argv = ["check" if a == "--check" else "selftest" if a == "--selftest" else a for a in argv]
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", nargs="?", default="run", choices=["run", "check", "selftest"])
    a = ap.parse_args(argv)
    if a.mode == "selftest":
        return selftest()
    if a.mode == "check":
        return check()
    t0 = time.time()
    d = run()
    d["elapsed_sec"] = round(time.time() - t0, 2)
    d["generated"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    with open(MD, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines(d)) + "\n")
    print(json.dumps({k: d.get(k) for k in ("verdict", "sentence", "k_now", "permitted_k",
                                            "cut_cny", "permission_readers",
                                            "permission_is_binding")},
                     ensure_ascii=False, indent=1))
    return 0 if d.get("verdict") != VERDICT_UNREADABLE else 1


if __name__ == "__main__":
    sys.exit(main())
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""etf_book_k_gap -- the money the permission floor never spent, name by name.

WHY THIS FILE EXISTS
--------------------
`results/etf_book_order/TICKET-<bar>.json` carries two sizes in one sheet: `k_rule`
(0.460253, what the sizing rule alone says) and `k_now` (0.393073, what the permission
floor lets this bar write). The ticket prints the difference as one number -- 63,652 CNY
on 2026-11-10 -- and the operator reading it can do nothing with it: a single total does
not say which holding was cut, nor what it would cost to buy one of the missing lots back.

This face answers those two questions from the ticket's own rows and prices, using the
same whole-lot rule the sheet used (floor(want / (price * lot))), so it cannot disagree
with the order it explains.

WHAT IT IS NOT
--------------
Not a signal, not a recommendation, and not a claim that the rule's size is the right
size. The floor exists because the permission face measured a narrower k; this face only
says what that measurement cost on this sheet.

TWO BASES, NAMED
----------------
The ticket sizes on the sizing NAV (1,000,000 on 2026-11-10) while the account face
reports the accrued NAV (1,007,436). The per-name gap here is priced on the ticket's own
sizing NAV -- the base the order was written from -- and the account-base total is
carried alongside, labelled, never mixed.

MODES
-----
  run       write results/etf_book_k_gap.json (+ .md) for the newest ticket.
  check     re-derive every published number from the ticket and refuse a drift.
  selftest  offline legs over a synthetic ticket (the face's own contract).

Exit codes: 0 ok / 2 cannot build (no ticket, unreadable ticket) /
            3 refused (ticket has no rule size to compare against).
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TICKET_DIR = os.path.join(ROOT, "results", "etf_book_order")
OUT_JSON = os.path.join(ROOT, "results", "etf_book_k_gap.json")
OUT_MD = os.path.join(ROOT, "results", "etf_book_k_gap.md")

LOT = 100


def _ticket_path(path=None):
    if path:
        return path
    hits = sorted(glob.glob(os.path.join(TICKET_DIR, "TICKET-*.json")))
    return hits[-1] if hits else None


def _load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _lots(want, price, lot=LOT):
    if not price or price <= 0:
        return None
    return int(want // (price * lot))


def compute(ticket):
    """Per-name decomposition of k_rule - k_now on this sheet's own base."""
    tk = ticket.get("ticket") or {}
    rows = tk.get("order") or []
    nav = float(tk.get("nav") or 0.0)
    k_now = ticket.get("k_now")
    k_rule = ticket.get("k_rule")
    if not rows or not nav or k_now is None or k_rule is None:
        return None
    k_now, k_rule = float(k_now), float(k_rule)
    n = len(rows)
    w_now, w_rule = k_now / n, k_rule / n

    out, total, unpriced = [], 0.0, []
    for r in rows:
        px = r.get("price")
        if not px:
            unpriced.append(r.get("symbol"))
            continue
        px = float(px)
        lots_now = r.get("lots")
        if lots_now is None:
            lots_now = _lots(nav * w_now, px)
        lots_rule = _lots(nav * w_rule, px)
        short = lots_rule - lots_now
        cny = round(short * LOT * px, 2)
        total += cny
        # smallest increase in k that buys exactly one more lot of this name
        nxt = int(lots_now) + 1
        dk_pp = round(100.0 * ((nxt * LOT * px * n) / nav - k_now), 4)
        out.append({
            "symbol": r.get("symbol"),
            "price": px,
            "lots_ordered": lots_now,
            "lots_at_rule": lots_rule,
            "short_lots": short,
            "short_shares": short * LOT,
            "short_cny": cny,
            "next_lot_dk_pp": dk_pp,
        })

    base = ticket.get("base") or {}
    account_gap = base.get("notional_gap_cny")
    total_cny = round(total, 2)
    if total_cny > 1.0:
        verdict = "FLOOR_CUT_THIS_SHEET"
    elif total_cny < -1.0:
        verdict = "SHEET_ABOVE_RULE"
    else:
        verdict = "FLOOR_DID_NOT_BIND"

    return {
        "face": "etf_book_k_gap",
        "bar": ticket.get("as_of") or tk.get("asof"),
        "decision_bar": base.get("bar"),
        "k_now": k_now,
        "k_rule": k_rule,
        "dk_pp": round(100.0 * (k_rule - k_now), 4),
        "nav_sizing_cny": nav,
        "nav_account_cny": base.get("nav_cny"),
        "permission_floor": (ticket.get("sizing_floor") or {}).get("floor"),
        "permission_source": (ticket.get("sizing_floor") or {}).get("source"),
        "rows": out,
        "short_total_cny": total_cny,
        "short_share_of_book_pct": round(100.0 * total_cny / (nav * k_rule), 4) if k_rule else None,
        "account_base_gap_cny": account_gap,
        "unpriced_rows": unpriced,
        "cheapest_next_lot": min(out, key=lambda r: r["next_lot_dk_pp"]) if out else None,
        "verdict": verdict,
    }


def verify(face, bar=None, ticket_file=None):
    """Is this table usable on the page about to print it? (r1515)

    Two readers now print this face: the CEO page reads the published file, and the ORDER
    sheet prints the object it just computed from its own ticket. Both have to answer the
    same two questions -- do the rows add up to the total the face claims, and is this the
    table for THIS sheet -- so the answer is derived here once instead of twice (E289).
    Returns (bad, mism); empty bad = the arithmetic holds, empty mism = this is the sheet.
    """
    if not face:
        return ["面不存在"], []
    rows = face.get("rows") or []
    if not rows or face.get("short_total_cny") is None \
            or face.get("k_rule") is None or face.get("k_now") is None:
        return ["面里没有逐名行，或没有规则/额度这一对 k"], []
    bad, tot = [], 0.0
    for r in rows:
        px, lots, cny = r.get("price"), r.get("short_lots"), r.get("short_cny")
        if px is None or lots is None or cny is None or float(px) <= 0:
            bad.append("%s 缺价或缺手" % r.get("symbol"))
            continue
        if abs(float(cny) - int(lots) * LOT * float(px)) > 1.0:
            bad.append("%s 手数×价 ≠ 金额" % r.get("symbol"))
        tot += float(cny)
    if abs(tot - float(face["short_total_cny"])) > 1.0:
        bad.append("逐名合计 %.2f ≠ 面自己 %.2f" % (tot, float(face["short_total_cny"])))
    mism = []
    if bar and face.get("bar") and str(face["bar"]) != str(bar):
        mism.append("面是 %s 的、这一张是 %s 的" % (face["bar"], bar))
    if ticket_file and face.get("ticket_file") and face["ticket_file"] != ticket_file:
        mism.append("面来自 %s、这一张是 %s" % (face["ticket_file"], ticket_file))
    return bad, mism


def sentence(face):
    if not face:
        return "这张票面没有可比的规则尺寸，本面不出数。"
    cheap = face["cheapest_next_lot"]
    head = ("规则要 **%.6f**、额度只给 **%.6f**（差 %.2fpp）：这张单因此少买 **%s**，按各自的价折成 **%s 元**。"
            % (face["k_rule"], face["k_now"], face["dk_pp"],
               " + ".join("%d 手" % r["short_lots"] for r in face["rows"]),
               format(face["short_total_cny"], ",.2f")))
    if face["verdict"] == "FLOOR_DID_NOT_BIND":
        head = ("规则要 %.6f、额度给 %.6f，两者在整手上没有差别：这张单没有被额度裁掉任何一手。"
                % (face["k_rule"], face["k_now"]))
    tail = ""
    if cheap and face["verdict"] == "FLOOR_CUT_THIS_SHEET":
        others = [r for r in face["rows"] if r.get("symbol") != cheap["symbol"]]
        # "其余" must mean the rest: including the cheapest name in the range prints
        # "others need 0.0110~..." which is the cheapest one's own number.
        rest = ("，其余每名各要 %.4f~%.4fpp"
                % (min(r["next_lot_dk_pp"] for r in others),
                   max(r["next_lot_dk_pp"] for r in others))) if others else ""
        tail = (" 想先补回**一手**，最便宜的是 **%s**：%s 的额度上调 **%.4fpp** 就够买它那一手%s。"
                % (cheap["symbol"], cheap["symbol"], cheap["next_lot_dk_pp"], rest))
    return head + tail


def render_md(face):
    if not face:
        return "# k 差分解\n\n这张票面没有可比的规则尺寸。\n"
    lines = ["# 额度裁掉的那一段（%s）" % face["bar"], "", sentence(face), "",
             "| 代码 | 价 | 本单手数 | 规则手数 | 少买手数 | 少买金额 | 再买一手要上调 k |",
             "|---|---|---|---|---|---|---|"]
    for r in face["rows"]:
        lines.append("| %s | %.3f | %d | %d | %d | %s | %.4fpp |" % (
            r["symbol"], r["price"], r["lots_ordered"], r["lots_at_rule"],
            r["short_lots"], format(r["short_cny"], ",.2f"), r["next_lot_dk_pp"]))
    lines += ["",
              "口径：逐名差额按票面自己的 sizing NAV（%s 元）与票面自己的价算，取整规则与票面一致"
              "（floor(目标金额 / (价×100))）。账本基座差 %s 元是另一个基（accrued NAV %s 元），两个数不混。"
              % (format(face["nav_sizing_cny"], ",.0f"),
                 face.get("account_base_gap_cny"), face.get("nav_account_cny")),
              ""]
    return "\n".join(lines)


def run(path=None):
    tp = _ticket_path(path if isinstance(path, str) else None)
    if not tp or not os.path.exists(tp):
        print("no ticket to explain")
        return 2
    tk = _load(tp)
    face = compute(tk)
    if not face:
        print("ticket carries no rule size (k_rule) -- nothing to decompose")
        return 3
    face["ticket_file"] = os.path.basename(tp)
    face["evidence_cutoff"] = face.get("bar")
    with open(OUT_JSON, "w", encoding="utf-8", newline="\n") as f:
        json.dump(face, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")
    with open(OUT_MD, "w", encoding="utf-8", newline="\n") as f:
        f.write(render_md(face))
    print(sentence(face))
    print("wrote %s" % os.path.relpath(OUT_JSON, ROOT))
    return 0


def check(path=None):
    tp = _ticket_path(path if isinstance(path, str) else None)
    if not tp:
        print("CHECK_FAIL no ticket")
        return 2
    fresh = compute(_load(tp))
    if not os.path.exists(OUT_JSON):
        print("CHECK_FAIL no face on disk")
        return 2
    old = _load(OUT_JSON)
    bad = []
    for k in ("k_now", "k_rule", "dk_pp", "short_total_cny", "verdict"):
        if fresh.get(k) != old.get(k):
            bad.append("%s %r != %r" % (k, fresh.get(k), old.get(k)))
    if (fresh.get("rows") or []) != (old.get("rows") or []):
        bad.append("rows differ")
    if bad:
        print("CHECK_FAIL " + "; ".join(bad))
        return 3
    print("CHECK_OK rows=%d total=%.2f" % (len(fresh["rows"]), fresh["short_total_cny"]))
    return 0


def _fixture(k_now=0.40, k_rule=0.50, rows=None, nav=100000.0):
    rows = rows or [{"symbol": "A", "price": 2.0, "lots": 20},
                    {"symbol": "B", "price": 10.0, "lots": 0},
                    {"symbol": "C", "price": 1.0, "lots": 40}]
    return {"as_of": "2026-01-01", "k_now": k_now, "k_rule": k_rule,
            "ticket": {"nav": nav,
                       "order": [{"symbol": r["symbol"], "price": r["price"],
                                  "lots": r["lots"], "weight": k_now / len(rows)}
                                 for r in rows]},
            "base": {"bar": "2026-01-01", "nav_cny": nav * 1.01, "notional_gap_cny": 1000.0},
            "sizing_floor": {"floor": k_now, "source": "fixture"}}


def _fixture_consistent(k_now=0.40, k_rule=0.50, nav=100000.0):
    """A sheet whose ordered lots are exactly what the formula produces at k_now."""
    rows = [("A", 2.0), ("B", 10.0), ("C", 1.0)]
    order = [{"symbol": s, "price": p, "weight": k_now / len(rows),
              "lots": _lots(nav * k_now / len(rows), p)} for s, p in rows]
    return {"as_of": "2026-01-01", "k_now": k_now, "k_rule": k_rule,
            "ticket": {"nav": nav, "order": order},
            "base": {"bar": "2026-01-01", "nav_cny": nav * 1.01, "notional_gap_cny": 1000.0},
            "sizing_floor": {"floor": k_now, "source": "fixture"}}


def selftest():
    ok = []

    def leg(name, cond):
        ok.append((name, bool(cond)))

    f = compute(_fixture())
    by = {r["symbol"]: r for r in f["rows"]}
    # A: nav*k/n = 100000*0.5/3 = 16666.67 -> 83 lots; sheet says it holds 20
    leg("L1 rule lots use the sheet's own floor rule", by["A"]["lots_at_rule"] == 83)
    leg("L2 short_lots = rule - ordered", by["A"]["short_lots"] == 83 - 20)
    leg("L3 short_cny priced at name's own price",
        abs(by["A"]["short_cny"] - (83 - 20) * 100 * 2.0) < 1e-6)
    leg("L4 total is the sum of the names", abs(f["short_total_cny"] - sum(r["short_cny"] for r in f["rows"])) < 1e-6)
    leg("L5 verdict derived from the signed total", f["verdict"] == "FLOOR_CUT_THIS_SHEET")
    fc = compute(_fixture_consistent())
    leg("L6 next-lot dk is positive and smallest for the cheapest name",
        all(r["next_lot_dk_pp"] > 0 for r in fc["rows"])
        and fc["cheapest_next_lot"]["symbol"] == min(fc["rows"], key=lambda r: r["next_lot_dk_pp"])["symbol"])
    # next-lot dk must actually buy exactly one more lot, on a sheet whose lots are the formula's
    rc_ = {r["symbol"]: r for r in fc["rows"]}["A"]
    k2 = fc["k_now"] + rc_["next_lot_dk_pp"] / 100.0
    leg("L7 applying next_lot_dk buys exactly one more lot of that name",
        _lots(100000.0 * k2 / 3, 2.0) == rc_["lots_ordered"] + 1)
    leg("L8 k_rule == k_now is not a cut",
        compute(_fixture_consistent(k_now=0.4, k_rule=0.4))["verdict"] == "FLOOR_DID_NOT_BIND")
    leg("L9 below-rule sheet is named, not silently floored",
        compute(_fixture_consistent(k_now=0.45, k_rule=0.40))["verdict"] == "SHEET_ABOVE_RULE")
    leg("L10 unpriced row is counted, not treated as zero",
        compute(_fixture(rows=[{"symbol": "Z", "price": None, "lots": 0}]))["unpriced_rows"] == ["Z"])
    leg("L11 no k_rule -> no face", compute({"ticket": {"nav": 1.0, "order": [{"symbol": "A", "price": 1.0}]}}) is None)
    leg("L12 sentence names the per-name shortfall and the cheapest top-up",
        "少买" in sentence(f) and f["cheapest_next_lot"]["symbol"] in sentence(f))
    leg("L13 zero-gap sentence does not claim a cut",
        "没有被额度裁掉" in sentence(compute(_fixture_consistent(k_now=0.4, k_rule=0.4))))
    # r1514: "其余" has to mean the rest -- the first live sentence said "其余每名各要
    # 0.0110~0.0442pp", where 0.0110 was the cheapest name's own number.
    _s_txt = sentence(f)
    _cheap = f["cheapest_next_lot"]
    _rest = [r["next_lot_dk_pp"] for r in f["rows"] if r["symbol"] != _cheap["symbol"]]
    leg("L14 the 'rest of the names' range excludes the cheapest top-up itself",
        ("其余每名各要 %.4f" % min(_rest)) in _s_txt
        and ("其余每名各要 %.4f" % _cheap["next_lot_dk_pp"]) not in _s_txt)
    # r1515: one check shared by the CEO page and the ORDER sheet.
    leg("L15 verify passes a table that adds up on its own sheet",
        verify(f) == ([], []) and verify(f, bar="2026-01-01")[0] == [])
    _bad_row = json.loads(json.dumps(f))
    _bad_row["rows"][0]["short_cny"] = _bad_row["rows"][0]["short_cny"] + 50.0
    leg("L16 verify refuses a row whose lots x price is not its money",
        any("手数×价" in b for b in verify(_bad_row)[0]))
    leg("L17 verify refuses another bar's table, and does not confuse it with a broken one",
        verify(f, bar="2026-01-02")[0] == []
        and any("这一张是 2026-01-02 的" in m for m in verify(f, bar="2026-01-02")[1]))
    bad = [n for n, v in ok if not v]
    for n, v in ok:
        print("%s %s" % ("[ok]" if v else "[FAIL]", n))
    print("selftest %d/%d" % (len(ok) - len(bad), len(ok)))
    return 0 if not bad else 1


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", nargs="?", default="run", choices=["run", "check", "selftest"])
    ap.add_argument("--ticket", default=None)
    a = ap.parse_args(argv)
    if a.mode == "selftest":
        return selftest()
    if a.mode == "check":
        return check(a.ticket)
    return run(a.ticket)


if __name__ == "__main__":
    sys.exit(main())
"""etf_book_base_basis_audit -- the same bar, two k's for the same account.

Why this exists (r1283 bm-a, judged on the published rows of 2026-11-10):
`results/etf_book_positions.json` carries two books that both call themselves the
account on bar `2026-11-10`:

  accrual.last  -> holdings 690/925/487/674 lots, risk 400,023.30, cash 607,432.09,
                   nav 1,007,455.39   (the PRE-trade book marked at this bar's closes)
  ledger_row    -> holdings 693/891/473/677 lots, risk 392,404.90, cash 607,595.10,
                   nav 1,000,000.00   (the POST-trade book, same closes, policy capital)

They differ by CNY 7,618.40 of risk and CNY 7,455.39 of NAV, and they do not agree on
k either: 0.397063 vs 0.392405. The order sheet reads the first one and prints its k
under the words "执行账 k" (`base_k_executed`), i.e. the account that exists after the
trade is reported with the k of the account that existed before it. A reader who follows
the sheet by hand sizes against a book that no longer exists.

This face does not pick a winner by opinion. It re-derives both totals from
lots x price x 100, decomposes the risk gap per symbol (lots vs prices) and per cause,
names which of the two k's the ticket consumed, and states in one sentence which total
is the account after the trade. Verification only: it writes no book.

CLI:
  python scripts/etf_book_base_basis_audit.py run|--check|--selftest
"""

from __future__ import annotations

import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSITIONS = os.path.join(ROOT, "results", "etf_book_positions.json")
ORDER_DIR = os.path.join(ROOT, "results", "etf_book_order")
OUT_JSON = os.path.join(ROOT, "results", "etf_book_base_basis_audit.json")
OUT_MD = os.path.join(ROOT, "docs", "live_book", "BASE-BASIS.md")

LOT_SHARES = 100
LOT_TOL = 0.02      # declared amounts are printed to 2dp per row
K_TOL = 5e-7        # k is printed to 6dp


def _load(path):
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _value(holdings):
    """Re-derive the risk leg from lots x price x LOT_SHARES; None if a price is unusable."""
    total, unpriced = 0.0, []
    for h in holdings or []:
        lots, px = h.get("lots"), h.get("price")
        if lots is None or px is None:
            unpriced.append(h.get("symbol"))
            continue
        total += float(lots) * float(px) * LOT_SHARES
    return round(total, 2), unpriced


def _k(risk, cash):
    nav = float(risk) + float(cash)
    return (None, None) if nav <= 0 else (round(float(risk) / nav, 6), round(nav, 2))


def _prices(holdings):
    return {str(h.get("symbol")): float(h["price"]) for h in holdings or [] if h.get("price") is not None}


def audit(positions, ticket):
    """Judge the two bases. Pure function: same inputs -> same verdict."""
    if not positions:
        return {"artifact": "etf_book_base_basis_audit", "status": "absent",
                "sentence": "没有持仓面（%s 缺失）：这一问答不了。" % POSITIONS}
    ledger = positions.get("ledger_row") or {}
    accrued = ((positions.get("accrual") or {}).get("last")) or {}
    if not ledger or not accrued:
        return {"artifact": "etf_book_base_basis_audit", "status": "unreadable",
                "sentence": "两道账有一道缺席（ledger_row / accrual.last）：缺面不等于零仓。"}

    sides = {}
    for name, row in (("accrued_pre_trade", accrued), ("ledger_post_trade", ledger)):
        risk, cash = row.get("risk_book_cny"), row.get("cash_cny")
        derived, unpriced = _value(row.get("holdings"))
        k, nav = _k(risk, cash)
        sides[name] = {
            "bar": row.get("bar"),
            "from_bar": row.get("from_bar"),
            "risk_book_cny": None if risk is None else round(float(risk), 2),
            "cash_cny": None if cash is None else round(float(cash), 2),
            "nav_cny": nav,
            "k": k,
            "derived_risk_cny": derived,
            "declared_matches_derived": (None if (derived is None or risk is None)
                                         else abs(derived - float(risk)) <= LOT_TOL),
            "unpriced_symbols": unpriced,
            "holdings_n": len(row.get("holdings") or []),
        }

    pre, post = sides["accrued_pre_trade"], sides["ledger_post_trade"]
    prices_same = _prices(accrued.get("holdings")) == _prices(ledger.get("holdings"))

    # per-symbol decomposition: a trade moves lots, this bar's closes are shared
    def _lots(row):
        return {str(h.get("symbol")): int(h.get("lots") or 0) for h in row.get("holdings") or []}

    lp, lq = _lots(accrued), _lots(ledger)
    px = _prices(accrued.get("holdings"))
    px.update(_prices(ledger.get("holdings")))
    rows = []
    for sym in sorted(set(lp) | set(lq)):
        a, b = lp.get(sym, 0), lq.get(sym, 0)
        if a == b:
            continue
        price = px.get(sym)
        rows.append({
            "symbol": sym,
            "pre_lots": a,
            "post_lots": b,
            "lot_delta": b - a,
            "price": price,
            "delta_cny": None if price is None else round((b - a) * price * LOT_SHARES, 2),
        })
    decomposed = round(sum(r["delta_cny"] or 0.0 for r in rows), 2)
    risk_gap = (None if (pre["risk_book_cny"] is None or post["risk_book_cny"] is None)
                else round(post["risk_book_cny"] - pre["risk_book_cny"], 2))
    cash_gap = (None if (pre["cash_cny"] is None or post["cash_cny"] is None)
                else round(post["cash_cny"] - pre["cash_cny"], 2))
    nav_gap = (None if (pre["nav_cny"] is None or post["nav_cny"] is None)
               else round(post["nav_cny"] - pre["nav_cny"], 2))

    # which k did the sheet consume?
    consumed, matches = None, {}
    if ticket:
        bk = ticket.get("base_k_executed")
        for name, side in sides.items():
            if bk is None or side["k"] is None:
                matches[name] = None
            else:
                matches[name] = abs(float(bk) - side["k"]) <= K_TOL
        if any(matches[k] for k in matches):
            consumed = [k for k, v in matches.items() if v][0]

    verdict, sentence = "UNRESOLVED", ""
    if prices_same and decomposed == risk_gap:
        verdict = "SAME_CLOSES_TWO_LOTS" if not (consumed == "ledger_post_trade") else "SHEET_READS_POST_TRADE"
        if verdict == "SAME_CLOSES_TWO_LOTS":
            sentence = ("同一组收盘价下两本账只差手数（换手前 %d 只 ¥%s / 换手后 %d 只 ¥%s，差 ¥%s）；"
                        "但两边的 NAV 不是同一个量：前账 NAV ¥%s 含当日收益，后账 NAV ¥%s 被钉在政策本金上，"
                        "所以票面引用的 k=%.6f 与账户实际持有比例的 k=%.6f 差 %+.6f。"
                        % (pre["holdings_n"], format(pre["risk_book_cny"], ",.0f"),
                           post["holdings_n"], format(post["risk_book_cny"], ",.0f"),
                           format(abs(risk_gap), ",.0f"),
                           format(pre["nav_cny"], ",.2f"), format(post["nav_cny"], ",.2f"),
                           pre["k"] or 0.0, post["k"] or 0.0,
                           (pre["k"] or 0.0) - (post["k"] or 0.0)))
    elif not prices_same:
        verdict, sentence = "DIFFERENT_CLOSES", "两本账用的收盘价不同：差额里既有估值差也有换手，不能只责怪换手。"

    k_gap = (None if (pre["k"] is None or post["k"] is None) else round(pre["k"] - post["k"], 6))
    out = {
        "artifact": "etf_book_base_basis_audit",
        "bar": ledger.get("bar"),
        "evidence_cutoff": ledger.get("bar"),
        "sides": sides,
        "prices_same": prices_same,
        "risk_gap_cny": risk_gap,
        "cash_gap_cny": cash_gap,
        "nav_gap_cny": nav_gap,
        "k_gap_pre_minus_post": k_gap,
        "notional_gap_cny": (None if (k_gap is None or pre["nav_cny"] is None)
                             else round(k_gap * pre["nav_cny"], 2)),
        "lot_moves": rows,
        "lot_moves_total_cny": decomposed,
        "decomposition_closes": (decomposed == risk_gap),
        "ticket_base_k_executed": None if not ticket else ticket.get("base_k_executed"),
        "ticket_k_matches": matches,
        "ticket_sized_from": consumed,
        "verdict": verdict,
        "sentence": sentence,
        "reading": [
            "两本账都是同一个账户的同一根 bar，只是处在换手的两侧：前账=上一根 bar 的持仓按本 bar 收盘价估值（NAV 随当日收益滚动），后账=本 bar 换手后的持仓按同一收盘价估值（NAV 钉在政策本金 1,000,000，现金是残差）。",
            "净值差 ¥%s = 风险腿差 ¥%s + 现金腿差 ¥%s：其中手数解释风险腿、现金腿补上剩余，两本账合起来才说得清这一天。"
            % (format(nav_gap or 0.0, ",.0f"), format(risk_gap or 0.0, ",.0f"),
               format(cash_gap or 0.0, ",.0f")),
            "所以「k 差」不是仓位不同，是分母不同：同一个风险腿，除滚动的 NAV 得 %.6f，除钉住的本金得 %.6f。"
            % (pre["k"] or 0.0, post["k"] or 0.0),
            "任何只印其中一个 k 的句子都要说清除的是什么——CEO 手动跟单时按哪个数下单，差的就是这一格。",
        ],
    }
    return out


def check():
    out = _load(OUT_JSON)
    if out is None:
        print("CHECK FAIL: %s missing" % OUT_JSON)
        return 1
    pos, tkt = _load(POSITIONS), _load(os.path.join(ORDER_DIR, "TICKET-%s.json" % (out.get("bar") or "")))
    fresh = audit(pos, tkt)
    drift = {k: (out.get(k), fresh.get(k)) for k in ("verdict", "risk_gap_cny", "k_gap_pre_minus_post",
                                                     "ticket_sized_from", "decomposition_closes")
             if out.get(k) != fresh.get(k)}
    if drift:
        print("CHECK FAIL: published rows no longer reproduce -> %s" % drift)
        return 1
    print("CHECK OK: %s | risk_gap %s | k_gap %s | ticket sized from %s"
          % (out["verdict"], out["risk_gap_cny"], out["k_gap_pre_minus_post"], out["ticket_sized_from"]))
    return 0


def render_md(out):
    L = ["# 同一根 bar，两本账（%s）" % (out.get("bar") or "?"), ""]
    if out.get("status") in ("absent", "unreadable", "UNRESOLVED"):
        L += [out.get("sentence") or "", ""]
        return "\n".join(L)
    L += ["- 判定：**%s**" % out["verdict"], "- %s" % out["sentence"], "",
          "| 账 | bar | 只数 | 风险腿 ¥ | 现金 ¥ | NAV ¥ | k |", "|---|---|---|---|---|---|---|"]
    for name, s in out["sides"].items():
        L.append("| %s | %s | %d | %s | %s | %s | %.6f |"
                 % (name, s["bar"], s["holdings_n"], format(s["risk_book_cny"], ",.2f"),
                    format(s["cash_cny"], ",.2f"), format(s["nav_cny"], ",.2f"), s["k"] or 0.0))
    L += ["", "## 差额落在哪几只上（手数 × 收盘价 × 100）", "",
          "| 代码 | 换手前手数 | 换手后手数 | 手数差 | 价格 | 金额 CNY |", "|---|---|---|---|---|---|"]
    for r in out["lot_moves"]:
        L.append("| %s | %d | %d | %+d | %s | %s |"
                 % (r["symbol"], r["pre_lots"], r["post_lots"], r["lot_delta"],
                    r["price"], format(r["delta_cny"], ",.2f")))
    L += ["| **合计** | | | | | **%s** |" % format(out["lot_moves_total_cny"], ",.2f"), "",
          "口径：%s" % ("两本账用同一组收盘价，差额全部由手数解释（分解和 = 风险腿差）"
                        if out["decomposition_closes"] else "两本账收盘价不同，差额含估值成分"),
          "", "## 票面读的是哪一本", "",
          "- 票面 `base_k_executed` = %s，与 %s 相符（容差 %.1e）。"
          % (out["ticket_base_k_executed"], out["ticket_sized_from"] or "两边都不符", K_TOL),
          "- 两本账的 k 相差 **%+.6f**，按前账 NAV 折 ¥%s 名义额。"
          % (out["k_gap_pre_minus_post"] or 0.0, format(out["notional_gap_cny"] or 0.0, ",.0f")),
          ""] + ["- " + r for r in out["reading"]] + [""]
    return "\n".join(L)


def run():
    # Lane guard (R31): this face publishes docs/live_book/BASE-BASIS.md, and docs/live_book/
    # is bm-a's single-writer face. Another host prints its no-op and writes nothing.
    machine = ""
    try:
        with open(os.path.join(ROOT, "fleet", "machine.json"), "r", encoding="utf-8") as fh:
            machine = (json.load(fh) or {}).get("machine_id") or ""
    except Exception:
        machine = ""
    if machine and machine != "bm-a":
        print("lane guard: docs/live_book is bm-a's face; this machine (%s) stdout-only, zero writes"
              % machine)
        return 0
    pos = _load(POSITIONS)
    bar = ((pos or {}).get("ledger_row") or {}).get("bar")
    tkt = _load(os.path.join(ORDER_DIR, "TICKET-%s.json" % bar)) if bar else None
    out = audit(pos, tkt)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    os.makedirs(os.path.dirname(OUT_MD), exist_ok=True)
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write(render_md(out))
    print("%s | %s | risk_gap %s | k_gap %s | -> %s"
          % (out.get("verdict"), out.get("bar"), out.get("risk_gap_cny"),
             out.get("k_gap_pre_minus_post"), OUT_JSON))
    return 0


def _fixture(pre_lots=(0, 0), post_lots=(3, -4), prices=(1.0, 2.0), nav_pin=True):
    hold_pre = [{"symbol": "A", "lots": pre_lots[0], "price": prices[0]},
                {"symbol": "B", "lots": pre_lots[1], "price": prices[1]}]
    hold_post = [{"symbol": "A", "lots": post_lots[0], "price": prices[0]},
                 {"symbol": "B", "lots": post_lots[1], "price": prices[1]}]
    vp = sum(h["lots"] * h["price"] * LOT_SHARES for h in hold_pre)
    vq = sum(h["lots"] * h["price"] * LOT_SHARES for h in hold_post)
    cash = 100000.0 - vp if nav_pin else 50000.0
    cash_post = 100000.0 - vq if nav_pin else cash
    pos = {"ledger_row": {"bar": "2026-01-02", "risk_book_cny": round(vq, 2),
                          "cash_cny": round(cash_post, 2), "holdings": hold_post},
           "accrual": {"last": {"bar": "2026-01-02", "from_bar": "2026-01-01",
                                "risk_book_cny": round(vp, 2), "cash_cny": round(cash, 2),
                                "holdings": hold_pre}}}
    ks = vp / (vp + cash)
    tkt = {"base_k_executed": round(ks, 6)}
    return pos, tkt


def selftest():
    legs = []

    def leg(name, cond):
        legs.append((name, bool(cond)))

    pos, tkt = _fixture()
    out = audit(pos, tkt)
    leg("fixture: gap is the trade", out["risk_gap_cny"] == round((3 * 1.0 - 4 * 2.0) * 100, 2))
    leg("fixture: decomposition closes",
        out["decomposition_closes"] and out["lot_moves_total_cny"] == out["risk_gap_cny"])
    leg("fixture: sheet read the pre-trade k", out["ticket_sized_from"] == "accrued_pre_trade")
    leg("fixture: verdict names the pre-trade read", out["verdict"] == "SAME_CLOSES_TWO_LOTS")
    leg("fixture: k gap is k_pre - k_post",
        abs(out["k_gap_pre_minus_post"] - round(out["sides"]["accrued_pre_trade"]["k"]
                                               - out["sides"]["ledger_post_trade"]["k"], 6)) < 1e-12)
    leg("fixture: holdings identity holds on both sides",
        all(s["declared_matches_derived"] for s in out["sides"].values()))
    leg("fixture: nav gap decomposes into risk + cash",
        abs(out["nav_gap_cny"] - (out["risk_gap_cny"] + out["cash_gap_cny"])) <= 0.011)

    # a sheet that sized from the POST-trade k must not be accused
    pos2, _ = _fixture()
    k_post = pos2["ledger_row"]["risk_book_cny"] / (pos2["ledger_row"]["risk_book_cny"]
                                                    + pos2["ledger_row"]["cash_cny"])
    out2 = audit(pos2, {"base_k_executed": round(k_post, 6)})
    leg("post-trade k is recognised", out2["ticket_sized_from"] == "ledger_post_trade")
    leg("post-trade k clears the accusation", out2["verdict"] == "SHEET_READS_POST_TRADE")

    # no trade at all -> no gap, and no accusation
    pos3, tkt3 = _fixture(post_lots=(0, 0))
    out3 = audit(pos3, tkt3)
    leg("no trade -> zero gap", out3["risk_gap_cny"] == 0.0 and out3["lot_moves"] == [])

    # missing face must not read as an empty account
    leg("absent positions face is unreadable, not zero", audit(None, None)["status"] == "absent")
    leg("accrual missing is unreadable", audit({"ledger_row": {"bar": "x"}}, None)["status"] == "unreadable")

    # different closes must not be blamed on lots alone
    pos4, tkt4 = _fixture()
    pos4["accrual"]["last"]["holdings"][0]["price"] = 1.5
    pos4["accrual"]["last"]["risk_book_cny"] = round(1.5 * 0 * 100, 2)
    out4 = audit(pos4, tkt4)
    leg("different closes are named", out4["verdict"] in ("DIFFERENT_CLOSES", "UNRESOLVED"))

    # the renderer must survive an unreadable verdict without inventing a table
    md = render_md(audit(None, None))
    leg("unreadable verdict renders no table", "|---" not in md and "这一问答不了" in md)

    ok = sum(1 for _, v in legs if v)
    for name, v in legs:
        print("%s %s" % ("PASS" if v else "FAIL", name))
    print("selftest %d/%d" % (ok, len(legs)))
    return 0 if ok == len(legs) else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="two books on one bar: which k did the sheet use")
    ap.add_argument("mode", nargs="?", default="run", choices=["run", "check", "selftest"])
    a = ap.parse_args(argv)
    if a.mode == "selftest":
        return selftest()
    if a.mode == "check":
        return check()
    return run()


if __name__ == "__main__":
    sys.exit(main())

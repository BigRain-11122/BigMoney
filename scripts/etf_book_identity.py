"""r1580: which book is each face talking about?

Two books live under the same name on the same 1,000,000 CNY:

  * the FORWARD LEDGER (`results/etf_book_forward/LEDGER.json`) -- 12 names
    on the 8% vol target, k~0.91, the research candidate being tracked;
  * the EXECUTABLE SHEET (`results/etf_book_order/latest.json` ->
    `TICKET-<bar>.json`) -- 5 names on the beta target 0.2, k~0.43, the
    portfolio the desk is actually handed.

The CEO page printed the first as "⑥ ETF 复合书", the daily report printed
the second as "十二、ETF 那本账", and the report's own section put the 5-name
holdings line directly above the 12-name ledger's NAV -- so a reader who
followed either face bought a portfolio the other face never described
(47.7pp of exposure, twice the position).

This module is the ONE implementation both faces import.  Rules:

  * each side prints ITS OWN published numbers -- nothing is re-derived;
  * two sides decided on different bars are NOT comparable (a date is not an
    identity); both dates are printed instead of one being borrowed;
  * a side that cannot be read is UNKNOWN, never "same book" (r98).

Usage:
    python scripts/etf_book_identity.py            # print the face
    python scripts/etf_book_identity.py selftest   # hermetic fixtures
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEDGER_PATH = os.path.join(ROOT, "results", "etf_book_forward", "LEDGER.json")
TICKET_LATEST = os.path.join(ROOT, "results", "etf_book_order", "latest.json")
REL_LEDGER = "results/etf_book_forward/LEDGER.json"
REL_TICKET = "results/etf_book_order/latest.json"
BOOK_ID_TOL = 1e-3     # two published ks this close are the same leverage


def _read_json(path):
    with open(path, encoding="utf-8-sig") as fh:
        return json.load(fh)


def face(ledger=None, latest_path=None):
    """Compare the book in force against the book the desk executes."""
    out = {
        "path_ledger": REL_LEDGER,
        "path_ticket": REL_TICKET,
        "ledger": {"present": False},
        "ticket": {"present": False},
        "comparable": False,
        "same_book": None,
        "verdict": "UNKNOWN",
        "names_overlap": None,
        "scale_gap_pp": None,
        "scale_gap_cny": None,
        "capital_cny": None,
        "note": "",
    }

    led = ledger
    if led is None:
        led = _read_json(LEDGER_PATH) if os.path.exists(LEDGER_PATH) else None
    if led:
        cfg = led.get("config") or {}
        bars = led.get("bars") or []
        bif = led.get("book_in_force") or {}
        pf = led.get("pending_fill") or {}
        scale = bif.get("scale")
        names = bif.get("names") or []
        bar = bif.get("bar")
        if scale is None and bars:
            scale = 1.0 - float(bars[-1].get("cash") or 0.0)
            bar = bar or bars[-1].get("bar")
        vt = cfg.get("vol_target")
        out["ledger"] = {
            "present": scale is not None,
            "bar": bar,
            "n_hold": cfg.get("n_hold"),
            "scale": None if scale is None else round(float(scale), 6),
            "names": [str(s) for s in names],
            "rule": (None if vt is None
                     else "vol_target %.1f%%" % (float(vt) * 100.0)),
            "capital_cny": pf.get("capital_cny"),
        }
        if pf.get("capital_cny") is not None:
            out["capital_cny"] = pf.get("capital_cny")

    latest = latest_path or TICKET_LATEST
    tick = _read_json(latest) if os.path.exists(latest) else None
    if tick:
        sheet = tick
        rel = tick.get("file")
        if rel:
            full = os.path.join(os.path.dirname(latest), rel)
            if os.path.exists(full):
                sheet = _read_json(full)
                out["path_ticket"] = "results/etf_book_order/" + str(rel)
            else:
                out["note"] = ("执行单本体缺失（latest 指向的 %s 不在盘上）"
                               % rel)
        tk = sheet.get("ticket") or {}
        order = tk.get("order") or []
        scale_t = tk.get("book_weight", sheet.get("k_now"))
        out["ticket"] = {
            "present": bool(order) and scale_t is not None,
            "bar": (sheet.get("as_of")
                    or (sheet.get("permission") or {}).get("decision_date")),
            "n_hold": sheet.get("n_hold", len(order)),
            "scale": None if scale_t is None else round(float(scale_t), 6),
            "names": [str(r.get("symbol")) for r in order],
            "rule": (None if sheet.get("beta_target") is None
                     else "beta_target %.2f" % float(sheet["beta_target"])),
            "book_amount_cny": tk.get("book_amount"),
            "cash_amount_cny": tk.get("cash_amount"),
        }
        if out["capital_cny"] is None:
            out["capital_cny"] = tk.get("nav")

    ls, ts = out["ledger"], out["ticket"]
    if not (ls.get("present") and ts.get("present")):
        out["verdict"] = "UNKNOWN"
        out["note"] = out["note"] or (
            "一侧读不出来（账本 %s / 执行单 %s）——不能据此判断两者是不是同一本书"
            % ("可读" if ls.get("present") else "不可读",
               "可读" if ts.get("present") else "不可读"))
        return out

    a, b = set(ls["names"]), set(ts["names"])
    out["names_overlap"] = len(a & b)
    gap = float(ls["scale"]) - float(ts["scale"])
    out["scale_gap_pp"] = round(gap * 100.0, 2)
    if out["capital_cny"] is not None:
        out["scale_gap_cny"] = round(gap * float(out["capital_cny"]), 2)
    if ls.get("bar") and ts.get("bar") and ls["bar"] != ts["bar"]:
        out["verdict"] = "NOT_COMPARABLE"
        out["note"] = ("两侧不在同一决策 bar（账本 %s / 执行单 %s）——只并排印，"
                       "不做比较" % (ls["bar"], ts["bar"]))
        return out
    out["comparable"] = True
    if a == b and abs(gap) <= BOOK_ID_TOL:
        out["same_book"] = True
        out["verdict"] = "SAME_BOOK"
        out["note"] = "两册同本：同一决策 bar、同一名册、同一杠杆"
    else:
        out["same_book"] = False
        out["verdict"] = "DIFFERENT_BOOKS"
        out["note"] = ("两册不同本：账本 %s 名 %s 与执行单 %s 名 %s 是两条规则，"
                       "敞口差 %.2fpp"
                       % (ls.get("n_hold") or len(a), ls.get("rule"),
                          ts.get("n_hold") or len(b), ts.get("rule"),
                          out["scale_gap_pp"]))
    return out


def lines(bi):
    """Human-readable rendering.  Every number comes from `face`."""
    if not bi:
        return []
    ls = bi.get("ledger") or {}
    ts = bi.get("ticket") or {}
    if not (ls.get("present") or ts.get("present")):
        return ["- **这一页写的是哪本书（r1580）**：两侧都读不出来（"
                f"{bi.get('path_ledger')} / {bi.get('path_ticket')}）"
                "——本页不给书名"]
    v = bi.get("verdict")
    side_l = ("%s 名 · k %.6f · %s · 决策 bar %s"
              % (ls.get("n_hold"), ls.get("scale") or 0.0, ls.get("rule"),
                 ls.get("bar"))) if ls.get("present") else "不可读"
    side_t = ("%s 名 · k %.6f · %s · 决策 bar %s"
              % (ts.get("n_hold"), ts.get("scale") or 0.0, ts.get("rule"),
                 ts.get("bar"))) if ts.get("present") else "不可读"
    if v == "SAME_BOOK":
        return ["- **这一页写的是哪本书（r1580）**：同一本——账本 " + side_l
                + "（`" + str(bi.get("path_ledger")) + "` 与 `"
                + str(bi.get("path_ticket")) + "` 逐项相等）"]
    if v == "NOT_COMPARABLE":
        return ["- **这一页写的是哪本书（r1580）**：**不比较**——账本 "
                + side_l + "｜执行单 " + side_t + "。两侧不在同一决策 bar，"
                "并排列出即止（借用一侧的日期会把两个世界的数印成一本书）"]
    if v == "UNKNOWN":
        return ["- **这一页写的是哪本书（r1580）**：账本 " + side_l
                + "｜执行单 " + side_t + f"。{bi.get('note')}"]
    out = ["- **这一页写的是哪本书（r1580）**：账本 = " + side_l
           + "（`" + str(bi.get("path_ledger")) + "`）｜执行单 = " + side_t
           + "（`" + str(bi.get("path_ticket")) + "`）"]
    gap_pp = bi.get("scale_gap_pp")
    gap_cny = bi.get("scale_gap_cny")
    extra = ""
    if gap_cny is not None:
        extra = "，按 %s 本金 = CNY %s" % (
            f"{float(bi['capital_cny']):,.0f}" if bi.get("capital_cny")
            else "1,000,000", f"{float(gap_cny):,.0f}")
    out.append("  - **两册不是同一本**：名册 %s vs %s（重叠 %s 名）｜"
               "敞口 %.2f%% vs %.2f%%（差 %spp%s）"
               % (ls.get("n_hold"), ts.get("n_hold"), bi.get("names_overlap"),
                  float(ls.get("scale") or 0.0) * 100.0,
                  float(ts.get("scale") or 0.0) * 100.0,
                  f"{float(gap_pp):.2f}" if gap_pp is not None else "?",
                  extra))
    if ts.get("book_amount_cny") is not None:
        out.append("  - 读法：按账本那本跟买 ≠ 按执行单下单——执行单只有 %s 名、"
                   "仓位 CNY %s（现金 CNY %s）。两个面各自都是真的，"
                   "问题只在没人说过它们不是同一本书"
                   % (ts.get("n_hold"),
                      f"{float(ts['book_amount_cny']):,.0f}",
                      f"{float(ts.get('cash_amount_cny') or 0.0):,.0f}"))
    return out


def selftest():
    import tempfile
    fails = []

    def check(name, cond):
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}")
        if not cond:
            fails.append(name)

    real = face()
    check("real faces produce a named verdict",
          real["verdict"] in {"SAME_BOOK", "DIFFERENT_BOOKS",
                              "NOT_COMPARABLE", "UNKNOWN"})
    check("real faces carry both side paths",
          real["path_ledger"].endswith("LEDGER.json")
          and real["path_ticket"].startswith("results/etf_book_order/"))

    led = {"config": {"n_hold": 12, "vol_target": 0.08},
           "book_in_force": {"bar": "2026-11-11", "scale": 0.909384,
                             "names": ["a", "b", "c"]},
           "pending_fill": {"capital_cny": 1000000.0}}
    tmp = tempfile.mkdtemp(prefix="bi1580_")
    sheet = {"as_of": "2026-11-11", "n_hold": 4, "beta_target": 0.2,
             "ticket": {"book_weight": 0.432195,
                        "order": [{"symbol": s} for s in ("a", "b", "c", "d")],
                        "book_amount": 431696.8, "cash_amount": 568303.2}}
    with open(os.path.join(tmp, "TICKET-2026-11-11.json"), "w",
              encoding="utf-8") as fh:
        json.dump(sheet, fh)
    latest = os.path.join(tmp, "latest.json")
    with open(latest, "w", encoding="utf-8") as fh:
        json.dump({"as_of": "2026-11-11", "file": "TICKET-2026-11-11.json",
                   "k_now": 0.432195}, fh)

    two = face(ledger=led, latest_path=latest)
    check("two different books are named, not merged",
          two["verdict"] == "DIFFERENT_BOOKS" and two["same_book"] is False
          and two["names_overlap"] == 3
          and abs(two["scale_gap_pp"] - 47.72) < 0.01
          and abs(two["scale_gap_cny"] - 477189.0) < 1.0)
    md2 = "\n".join(lines(two))
    check("both books print their own ks and the gap",
          "0.909384" in md2 and "0.432195" in md2
          and "不是同一本" in md2 and "47.72" in md2)

    miss = face(ledger=led, latest_path=os.path.join(tmp, "nope.json"))
    md4 = "\n".join(lines(miss))
    check("a missing ticket is UNKNOWN, never 'same book'",
          miss["verdict"] == "UNKNOWN" and miss["same_book"] is None
          and "同一本——" not in md4 and "不可读" in md4)

    led2 = json.loads(json.dumps(led))
    led2["book_in_force"]["bar"] = "2026-11-10"
    nc = face(ledger=led2, latest_path=latest)
    md3 = "\n".join(lines(nc))
    check("different decision bars are not compared",
          nc["verdict"] == "NOT_COMPARABLE" and nc["comparable"] is False
          and "2026-11-10" in md3 and "2026-11-11" in md3)

    sheet2 = json.loads(json.dumps(sheet))
    sheet2["n_hold"] = 2
    sheet2["ticket"]["order"] = [{"symbol": s} for s in ("a", "b")]
    with open(os.path.join(tmp, "TICKET-2026-11-11.json"), "w",
              encoding="utf-8") as fh:
        json.dump(sheet2, fh)
    same = face(ledger={"config": {"n_hold": 2, "vol_target": None},
                        "book_in_force": {"bar": "2026-11-11",
                                          "scale": 0.432195,
                                          "names": ["a", "b"]}},
                latest_path=latest)
    check("one book on both sides says so",
          same["verdict"] == "SAME_BOOK" and same["same_book"] is True
          and same["names_overlap"] == 2)
    print("selftest: %s" % ("ALL PASS" if not fails else f"FAIL {fails}"))
    return 0 if not fails else 1


def main(argv):
    if len(argv) > 1 and argv[1] == "selftest":
        print("=== etf_book_identity selftest (hermetic fixtures) ===")
        return selftest()
    bi = face()
    for line in lines(bi):
        print(line)
    print("verdict=%s" % bi["verdict"])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

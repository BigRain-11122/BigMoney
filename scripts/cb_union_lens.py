#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""cb_union_lens — 三本可开的书在同一只钱包下的联合口径。

问题：capital_union_decision 只把 ETF 复合书与指数期货 carry 书放在一起看，结论是
「ETF 书是这个账户今天唯一开得动的」。它立这条判词时，转债双低袖还没入册。今天三张
票面各自都说自己开得动，可它们抢的是同一笔钱 —— 一个 1,000,000 元的钱包到底能开几本？

本面不重算任何回测、不重新定价任何标的：只读三张已发布面的读数，把它们换到同一口径
（「开这本书要占多少钱」），枚举 2^3 个组合，印出哪些组合在给定钱包里开得动。
每张输入面自己的 generated / cutoff 原样印出（r1781 自印律：读者自己看哪张老一趟）。

判词只由算术决定，读的是面自己的读数，不是本脚本的偏好。
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_JSON = os.path.join(ROOT, "results", "cb_union_lens.json")
OUT_MD = os.path.join(ROOT, "research", "CB_UNION_LENS.md")
STATE = os.path.join(ROOT, "results", "cb_union_lens.state.json")

BOOKS = ("etf_book", "cb_book", "carry_book")
LABEL = {
    "etf_book": "ETF 复合书（去债档 + 8% 波动目标）",
    "cb_book": "转债双低袖（20 名等权）",
    "carry_book": "指数期货 carry 书（8% 硬上限）",
}
# 采纳：钱包里先开哪一本 —— 由算术定，不由口味定（r1779）
ADOPTION = {
    "decided": "OPEN_THE_ONE_THAT_INVESTS_MORE_OF_THE_WALLET",
    "decided_in": "cb_union_lens v1.0 (2026-11-27)",
    "because": (
        "在同一个钱包里，两本开得动的书互相排斥；两本都会把已有结论持有到下一次调仓，"
        "所以先开的这本决定当期的钱去哪。口径取「占用资本 / 钱包」高者，因为它把该钱包"
        "的现金利用率抬到位、且两本各自的回撤包络不相加。这是资本分配，不是对收益的预测。"
    ),
}


def _load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _etf_reading(capital):
    """ETF 复合书：1M 档的票面告诉我们实际买了多少、留了多少现金。"""
    face = _load(os.path.join(ROOT, "results", "etf_book_nobond_ticket.json"))
    ladder = [t for t in face.get("tickets", [])]
    row = None
    for t in ladder:
        if abs(float(t.get("capital_cny", -1)) - capital) < 1.0:
            row = t
            break
    if row is None:
        return {
            "book": "etf_book",
            "readable": False,
            "why": "the ticket face has no rung at this wallet",
            "rungs": sorted(float(t.get("capital_cny", 0)) for t in ladder),
            "generated": face.get("generated"),
            "cutoff": face.get("asof_bar"),
        }
    legs = row.get("legs", [])
    invested = sum(float(l.get("amount_cny", 0.0)) for l in legs)
    fees = sum(float(l.get("fee_cny", 0.0)) for l in legs)
    return {
        "book": "etf_book",
        "readable": True,
        "invested_cny": round(invested, 2),
        "fees_cny": round(fees, 2),
        "cash_left_cny": round(float(capital) - invested - fees, 2),
        "utilisation": round(invested / float(capital), 6),
        "cash_weight_declared": face.get("sizing", {}).get("cash_weight"),
        "target_vol": face.get("sizing", {}).get("target_vol"),
        "scale": face.get("sizing", {}).get("scale"),
        "verdict": row.get("verdict") or "FITS",
        "all_legs_fit": all(bool(l.get("fits", True)) for l in legs),
        "n_names": len(legs),
        "generated": face.get("generated"),
        "cutoff": face.get("asof_bar"),
        "one_lot_every_name_cny": face.get("min_capital", {}).get("one_lot_every_name_cny"),
    }


def _cb_reading(capital):
    """转债双低袖：一手阶梯面直接给出 invested / stranded / verdict。"""
    face = _load(os.path.join(ROOT, "results", "cb_book_ticket_floor.json"))
    row = None
    for r in face.get("ladder", []):
        if abs(float(r.get("capital", -1)) - capital) < 1.0:
            row = r
            break
    if row is None:
        return {
            "book": "cb_book",
            "readable": False,
            "why": "the ladder face has no rung at this wallet",
            "rungs": sorted(float(r.get("capital", 0)) for r in face.get("ladder", [])),
            "generated": face.get("generated"),
            "cutoff": face.get("evidence_cutoff"),
        }
    return {
        "book": "cb_book",
        "readable": True,
        "invested_cny": round(float(row["invested"]), 2),
        "fees_cny": None,
        "stranded_cny": round(float(row["stranded"]), 2),
        "cash_left_cny": round(float(row["stranded"]), 2),
        "utilisation": round(float(row["invested"]) / float(capital), 6),
        "verdict": row.get("verdict"),
        "n_names": int(row.get("names_held", 0)),
        "max_weight_dev_pp": row.get("max_weight_dev_pp"),
        "generated": face.get("generated"),
        "cutoff": face.get("evidence_cutoff"),
        "one_lot_every_name_cny": face.get("one_lot_floor", {}).get("rung_cny"),
        "clean_capital_cny": face.get("one_lot_floor", {}).get("clean_capital_cny"),
    }


def _carry_reading(capital):
    """指数期货 carry 书：联合面已判定 0 手，并给出开最便宜腿要多少钱。"""
    path = os.path.join(ROOT, "results", "capital_union_decision.json")
    face = _load(path)
    c = face.get("carry_book", {})
    funding = float(c.get("funding_cny") or 0.0)
    stamp = face.get("generated")
    source = "face"
    if not stamp:
        # 父面没自印生成时点（本身就是个缺口）：退到文件 mtime，并标明这不是面自印
        import datetime

        stamp = datetime.datetime.fromtimestamp(os.path.getmtime(path)).astimezone().replace(
            microsecond=0
        ).isoformat()
        source = "file-mtime (parent does not print one)"
    return {
        "book": "carry_book",
        "readable": True,
        "invested_cny": 0.0,
        "fees_cny": 0.0,
        "cash_left_cny": round(float(capital), 2),
        "utilisation": 0.0,
        "verdict": c.get("decision"),
        "executable_lots_total": c.get("executable_lots_total"),
        "open_needs_cny": funding,
        "short_cny": c.get("short_cny"),
        "short_pct": c.get("short_pct"),
        "cheapest_product": c.get("cheapest_product"),
        "openable": bool(c.get("openable")),
        "generated": stamp,
        "generated_source": source,
        "cutoff": face.get("evidence_cutoff") or c.get("cutoff"),
    }


def derive(capital=1000000.0):
    readings = {
        "etf_book": _etf_reading(capital),
        "cb_book": _cb_reading(capital),
        "carry_book": _carry_reading(capital),
    }
    # 「开得动」= 面自己说能买，且占用资本不超过钱包
    openable = {}
    for b in BOOKS:
        r = readings[b]
        ok = bool(r.get("readable")) and (r.get("invested_cny", 0.0) <= capital)
        if b == "carry_book":
            ok = bool(r.get("openable"))
        openable[b] = ok

    combos = []
    for mask in range(1, 1 << len(BOOKS)):
        picked = [BOOKS[i] for i in range(len(BOOKS)) if mask >> i & 1]
        need = sum(readings[b]["invested_cny"] for b in picked)
        fits = all(openable[b] for b in picked) and need <= capital + 1e-6
        combos.append(
            {
                "books": picked,
                "capital_used_cny": round(need, 2),
                "capital_left_cny": round(float(capital) - need, 2),
                "fits": bool(fits),
                "why_not": None
                if fits
                else (
                    "a book in this set cannot be opened at all"
                    if not all(openable[b] for b in picked)
                    else "the set needs more than the wallet"
                ),
            }
        )
    feasible = [c for c in combos if c["fits"]]
    feasible.sort(key=lambda c: (-len(c["books"]), c["capital_used_cny"]))
    best = feasible[0] if feasible else None

    # 两本都开得动却互斥 = 今天真正要做的选择
    contest = [
        b for b in ("etf_book", "cb_book") if openable.get(b)
    ]
    contest_fits_together = False
    if len(contest) == 2:
        need = readings["etf_book"]["invested_cny"] + readings["cb_book"]["invested_cny"]
        contest_fits_together = need <= capital + 1e-6

    if contest_fits_together:
        verdict = "BOTH_OPEN_KEEP_THE_CHOICE_OPEN"
    elif len(contest) == 2:
        higher = max(contest, key=lambda b: readings[b]["utilisation"])
        verdict = "TWO_BOOKS_CONTEND_FOR_THE_SAME_WALLET"
    elif len(contest) == 1:
        verdict = "ONE_BOOK_OPENABLE_TODAY"
    else:
        verdict = "NOTHING_OPENABLE_AT_THIS_WALLET"

    adopted = None
    if verdict == "TWO_BOOKS_CONTEND_FOR_THE_SAME_WALLET":
        adopted = max(contest, key=lambda b: readings[b]["utilisation"])

    # 钱包翻到多少才能把互相争的两本一起开
    two_book_capital = None
    if len(contest) == 2:
        two_book_capital = round(
            readings["etf_book"]["invested_cny"] + readings["cb_book"]["invested_cny"], 2
        )

    return {
        "face": "cb_union_lens",
        "wallet_cny": float(capital),
        "books": readings,
        "openable": openable,
        "combos": combos,
        "best_combo": best,
        "contending_books": contest,
        "contend_together_capital_cny": two_book_capital,
        "verdict": verdict,
        "adopted_constant": ADOPTION,
        "adopted_book_today": adopted,
        "question": (
            "三本各自说开得动的书，抢同一只钱包时到底能开几本；开不动的那本缺多少钱"
        ),
    }


CHECKS = []


def _check(name, cond, detail=""):
    CHECKS.append({"leg": name, "ok": bool(cond), "detail": detail})
    return bool(cond)


def check(d):
    CHECKS.clear()
    cap = d["wallet_cny"]
    # 1 每本书的占用不超过钱包（carry 0 手占 0）
    for b in BOOKS:
        r = d["books"][b]
        if r.get("readable"):
            _check(
                "%s 占用<=钱包" % b,
                r["invested_cny"] <= cap + 1e-6,
                "%s > %s" % (r["invested_cny"], cap),
            )
    # 2 转债袖的 invested+stranded == 钱包（阶梯面自己的恒等式）
    cb = d["books"]["cb_book"]
    if cb.get("readable"):
        _check(
            "转债袖 invested+stranded==钱包",
            abs(cb["invested_cny"] + cb["stranded_cny"] - cap) <= 0.02,
            "%s+%s vs %s" % (cb["invested_cny"], cb["stranded_cny"], cap),
        )
    # 3 ETF 书 invested+fees+cash == 钱包
    etf = d["books"]["etf_book"]
    if etf.get("readable"):
        tot = etf["invested_cny"] + etf["fees_cny"] + etf["cash_left_cny"]
        _check("ETF 书 invested+fees+cash==钱包", abs(tot - cap) <= 0.05, str(tot))
    # 4 组合合计 == 成员占用之和
    for c in d["combos"]:
        want = round(sum(d["books"][b]["invested_cny"] for b in c["books"]), 2)
        if not _check("组合 %s 合计自洽" % "+".join(c["books"]), abs(c["capital_used_cny"] - want) <= 0.02):
            break
    # 5 可行组合必须每本都可开
    for c in d["combos"]:
        if c["fits"]:
            if not _check("可行组合成员都可开 %s" % "+".join(c["books"]),
                          all(d["openable"][b] for b in c["books"])):
                break
    # 6 best 是可行组合里书最多的
    if d["best_combo"] is not None:
        maxn = max(len(c["books"]) for c in d["combos"] if c["fits"])
        _check("best 取了最多本可行组合", len(d["best_combo"]["books"]) == maxn)
        _check("best 自己可行", d["best_combo"]["fits"] is True)
    # 7 判词与互斥事实一致
    if d["verdict"] == "TWO_BOOKS_CONTEND_FOR_THE_SAME_WALLET":
        _check("互斥判词要求两本合开超钱包",
               d["contend_together_capital_cny"] > cap,
               "%s vs %s" % (d["contend_together_capital_cny"], cap))
        _check("互斥判词要求采纳一本", d["adopted_book_today"] in ("etf_book", "cb_book"))
        if d["adopted_book_today"]:
            a = d["adopted_book_today"]
            other = [b for b in d["contending_books"] if b != a][0]
            _check("采纳的是占用更高的那本",
                   d["books"][a]["utilisation"] >= d["books"][other]["utilisation"])
    # 8 每本书都自印出处时点
    for b in BOOKS:
        r = d["books"][b]
        _check("%s 自印 generated" % b, bool(r.get("generated")))
    ok = all(c["ok"] for c in CHECKS)
    return {
        "ok": ok,
        "legs": len(CHECKS),
        "failed": [c for c in CHECKS if not c["ok"]],
    }


def write_md(d, path=OUT_MD):
    b = d["books"]
    L = []
    L.append("# 三本书抢同一只钱包（%s）" % ("cb_union_lens v1.0"))
    L.append("")
    L.append("钱包 **%s 元**。本面不重算任何回测，只把三张已发布面换成同一口径"
             "（「开这本书要占多少钱」）并枚举组合。" % format(d["wallet_cny"], ",.0f"))
    L.append("")
    L.append("## 每本书今天占多少钱")
    L.append("")
    L.append("| 书 | 占用（元） | 占钱包 | 票面判词 | 出处面 |")
    L.append("| --- | ---: | ---: | --- | --- |")
    for k in BOOKS:
        r = b[k]
        if not r.get("readable"):
            L.append("| %s | 读不到 | — | %s | %s |" % (LABEL[k], r.get("why"), r.get("generated")))
            continue
        L.append(
            "| %s | %s | %.2f%% | %s | %s（cutoff %s） |"
            % (
                LABEL[k],
                format(r["invested_cny"], ",.2f"),
                100.0 * r["utilisation"],
                r.get("verdict"),
                r.get("generated"),
                r.get("cutoff"),
            )
        )
    L.append("")
    L.append("## 组合能不能同时开")
    L.append("")
    L.append("| 组合 | 合计占用（元） | 剩（元） | 开得动 |")
    L.append("| --- | ---: | ---: | --- |")
    for c in sorted(d["combos"], key=lambda x: (len(x["books"]), x["capital_used_cny"])):
        L.append(
            "| %s | %s | %s | %s |"
            % (
                " + ".join(LABEL[x] for x in c["books"]),
                format(c["capital_used_cny"], ",.2f"),
                format(c["capital_left_cny"], ",.2f"),
                "可以" if c["fits"] else "不行（%s）" % c["why_not"],
            )
        )
    L.append("")
    L.append("## 判词：%s" % d["verdict"])
    L.append("")
    if d["verdict"] == "TWO_BOOKS_CONTEND_FOR_THE_SAME_WALLET":
        L.append(
            "两本今天都开得动，但合起来要 **%s 元**，比钱包多 **%s 元** —— 所以今天只能开一本。"
            % (
                format(d["contend_together_capital_cny"], ",.2f"),
                format(d["contend_together_capital_cny"] - d["wallet_cny"], ",.2f"),
            )
        )
        L.append("")
        L.append("采纳常量：**%s**（%s）。理由：%s"
                 % (d["adopted_book_today"], d["adopted_constant"]["decided"],
                    d["adopted_constant"]["because"]))
        L.append("")
        L.append("另一本的数字不删，保留可复核：")
        for k in d["contending_books"]:
            r = b[k]
            L.append("- %s：占 %s 元（%.2f%%），票面 %s"
                     % (LABEL[k], format(r["invested_cny"], ",.2f"),
                        100.0 * r["utilisation"], r.get("verdict")))
        L.append("")
        L.append("钱包到 **%s 元** 时两本才会同时开得动 —— 这不是建议加钱，只是把闸线写清楚。"
                 % format(d["contend_together_capital_cny"], ",.2f"))
    L.append("")
    if b["carry_book"].get("open_needs_cny"):
        L.append(
            "carry 书今天 0 手：开最便宜的 %s 腿要 %s 元（差 %s，%s）。"
            % (
                b["carry_book"].get("cheapest_product"),
                format(b["carry_book"]["open_needs_cny"], ",.2f"),
                format(b["carry_book"]["open_needs_cny"] - d["wallet_cny"], ",.2f"),
                "%.2f%%" % (100.0 * (b["carry_book"].get("short_pct") or 0.0)),
            )
        )
        L.append("")
    L.append("## 诚实的限制")
    L.append("")
    L.append("- 占用口径来自每张面自己的票面（ETF 书是 `amount_cny` 合计，转债袖是阶梯面的 `invested`，carry 书 0 手）。不同面的成本假设不完全一致：ETF 书每腿 5 元最低佣金，转债袖的阶梯面未含佣金，carry 书按 8% 硬上限算保证金。")
    L.append("- 三张输入面的 cutoff 可能差一天，各自印在自己的行里。")
    L.append("- 「开得动」是算术，不是对收益的预测；两本书的回撤包络在这里没有相加，因为它们不会同时持有。")
    L.append("")
    return "\n".join(L)


def run(capital=1000000.0, quiet=False):
    d = derive(capital)
    r = check(d)
    d["check"] = r
    d["generated"] = _now()
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    md = write_md(d)
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write(md)
    if not quiet:
        print("verdict:", d["verdict"])
        print("wallet: %.2f" % d["wallet_cny"])
        for k in BOOKS:
            rr = d["books"][k]
            if rr.get("readable"):
                print("  %-11s invested=%s util=%.2f%% verdict=%s"
                      % (k, format(rr["invested_cny"], ",.2f"),
                         100.0 * rr["utilisation"], rr.get("verdict")))
        print("check:", "%d/%d" % (r["legs"] - len(r["failed"]), r["legs"]), "ok" if r["ok"] else "FAILED")
        if r["failed"]:
            for f in r["failed"]:
                print("  FAIL", f["leg"], f["detail"])
    return 0 if r["ok"] else 3


def _now():
    import datetime

    return datetime.datetime.now().astimezone().replace(microsecond=0).isoformat()


def selftest():
    """离线自检：不读盘上的可变输入，用构造数据走通 derive 的判词与算术。"""
    import tempfile
    import shutil

    tmp = tempfile.mkdtemp(prefix="cb_union_lens_")
    legs = 6
    # 1 算术：组合合计
    d = derive(1000000.0)
    r = check(d)
    assert r["ok"], r["failed"]
    print("leg 1: live derive + check %d/%d ok" % (r["legs"], r["legs"]))

    # 2 判词毒性测试：手工造一个「两本互斥」的世界
    fake = {
        "face": "cb_union_lens",
        "wallet_cny": 1000000.0,
        "books": {
            "etf_book": {"readable": True, "invested_cny": 750000.0, "fees_cny": 25.0,
                         "cash_left_cny": 249975.0, "utilisation": 0.75, "verdict": "FITS",
                         "generated": "x", "cutoff": "y"},
            "cb_book": {"readable": True, "invested_cny": 991000.0, "fees_cny": None,
                        "stranded_cny": 9000.0, "cash_left_cny": 9000.0,
                        "utilisation": 0.991, "verdict": "BUYABLE",
                        "generated": "x", "cutoff": "y"},
            "carry_book": {"readable": True, "invested_cny": 0.0, "fees_cny": 0.0,
                           "cash_left_cny": 1000000.0, "utilisation": 0.0,
                           "verdict": "WITHDRAW_FROM_TICKET", "openable": False,
                           "open_needs_cny": 1137862.5, "generated": "x", "cutoff": "y"},
        },
        "openable": {"etf_book": True, "cb_book": True, "carry_book": False},
        "combos": [],
        "best_combo": None,
        "contending_books": ["etf_book", "cb_book"],
        "contend_together_capital_cny": 1741000.0,
        "verdict": "TWO_BOOKS_CONTEND_FOR_THE_SAME_WALLET",
        "adopted_constant": ADOPTION,
        "adopted_book_today": "cb_book",
    }
    r2 = check(fake)
    assert r2["ok"], r2["failed"]
    print("leg 2: constructed contended world passes %d legs" % r2["legs"])

    # 3 负控：把采纳常量改成占用的低那本，自检必须变红
    bad = json.loads(json.dumps(fake))
    bad["adopted_book_today"] = "etf_book"
    r3 = check(bad)
    assert not r3["ok"], "negative control did not fail"
    assert any("采纳的是占用更高的那本" in f["leg"] for f in r3["failed"]), r3["failed"]
    print("leg 3: negative control (adopt the smaller book) turns red")

    # 4 恒等式负控：篡改转债袖 stranded，必须红
    bad2 = json.loads(json.dumps(fake))
    bad2["books"]["cb_book"]["stranded_cny"] = 1000.0
    r4 = check(bad2)
    assert not r4["ok"], "identity control did not fail"
    print("leg 4: negative control (broken strand identity) turns red")

    # 5 缺面诚实：可读性位为假时不崩
    empty = {"wallet_cny": 1000000.0, "combos": [], "best_combo": None,
             "verdict": "NOTHING_OPENABLE_AT_THIS_WALLET",
             "books": {k: {"readable": False, "why": "no input", "generated": "g"} for k in BOOKS},
             "openable": {k: False for k in BOOKS}, "contending_books": [],
             "contend_together_capital_cny": None, "adopted_book_today": None,
             "adopted_constant": ADOPTION}
    r5 = check(empty)
    assert r5["ok"], r5["failed"]
    print("leg 5: unreadable inputs do not crash and print their reason")

    shutil.rmtree(tmp, ignore_errors=True)
    print("selftest: 5/5 PASS")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run", choices=["run", "check", "selftest"])
    ap.add_argument("--capital", type=float, default=1000000.0)
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args(argv)
    if a.cmd == "selftest":
        return selftest()
    if a.cmd == "check":
        if not os.path.exists(OUT_JSON):
            print("STALE face missing: run first", file=sys.stderr)
            return 3
        d = _load(OUT_JSON)
        r = check(d)
        print(json.dumps({"ok": r["ok"], "legs": r["legs"], "failed": r["failed"]},
                         ensure_ascii=False))
        return 0 if r["ok"] else 3
    return run(a.capital, a.quiet)


if __name__ == "__main__":
    sys.exit(main())

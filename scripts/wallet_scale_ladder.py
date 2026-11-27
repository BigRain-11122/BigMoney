#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""wallet_scale_ladder — 同一笔钱在不同规模下能开哪本书，以及多出来的钱该去哪。

问题：cb_union_lens（r2187）只回答了「1,000,000 元能不能同开两本」——答案是不能，差
741,528.50。可读者手里未必是 100 万。150 万怎么办？174 万呢？多出来的钱放现金还是推进
第二本书？这三问一直没人算，因为每本书只印自己的年化，从没按「账户规模」印过。

本面不重算任何回测、不重新定价任何标的：只读已发布面的读数
  results/cb_union_lens.json           — 两本书在 1M 书上的实际占用（need）
  results/etf_nobond_vt.json           — ETF 复合书 nobond_vt08 的年化/夏普/回撤/波动
  results/cb_dual_low.json             — 转债双低袖主配置（20 名 / 20 日 / 10bp）读数
  results/capital_union_decision.json  — ETF 书的容量线（资本在 1% ADV 线上）
  results/etf_book_cash_roll_today.json— 今天现金袖能拿到的净利率（连费用）

口径（写死在代码里，自检逐条钉住）：
  * 每本书的部署额 = 它在 1M 书上的实际占用（need），**不随钱包等比放大**：
    ETF 书的容量线今天印 1,082,283.94 元、60 个交易日只有 6 天过线，把同一批标的按更大
    资金打进去的冲击成本本面没有定价，所以不做「放大」这种无证据的假设。
  * 剩余资本按现金腿利率计息（取自今天那张滚动面，连费用后的净年化）。
  * 组合年化 = 各臂年收益之和 / 钱包。**这不是组合回测**：两本书的共动、调仓日撞车、
    以及同一天抢同一只标的的成本，本面都没定价，页面上逐条印出来。

判词只由算术决定，读的是面自己的读数，不是本脚本的偏好。
"""
import argparse
import datetime as dt
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_JSON = os.path.join(ROOT, "results", "wallet_scale_ladder.json")
OUT_MD = os.path.join(ROOT, "results", "wallet_scale_ladder.md")
OUT_RESEARCH = os.path.join(ROOT, "research", "WALLET_SCALE_LADDER.md")
STATE = os.path.join(ROOT, "results", "wallet_scale_ladder.state.json")

CB_MAIN = dict(n_hold=20, rebal=20, cost_bp=10.0)
ETF_ARM = "nobond_vt08"
LADDER_CNY = (500000, 1000000, 1200000, 1500000, 1741529, 2000000, 2300000)


def _load(rel):
    path = os.path.join(ROOT, rel)
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _src():
    """每张输入面：读数 + 自己的 generated / cutoff（r1781 自印律）。"""
    union = _load("results/cb_union_lens.json")
    etf = union["books"]["etf_book"]
    cb = union["books"]["cb_book"]

    vt = _load("results/etf_nobond_vt.json")
    run = None
    for r in vt.get("runs", []):
        if r.get("label") == ETF_ARM:
            run = r
    if run is None:
        raise SystemExit("face missing: results/etf_nobond_vt.json has no arm %r" % ETF_ARM)

    cbface = _load("results/cb_dual_low.json")
    cell = None
    for g in cbface.get("grid", []):
        if (
            g.get("n_hold") == CB_MAIN["n_hold"]
            and g.get("rebal") == CB_MAIN["rebal"]
            and abs(float(g.get("cost_bp", -1)) - CB_MAIN["cost_bp"]) < 1e-9
        ):
            cell = g
    if cell is None:
        raise SystemExit("face missing: results/cb_dual_low.json has no main cell %r" % (CB_MAIN,))

    cap = _load("results/capital_union_decision.json")["etf_book"]
    roll = _load("results/etf_book_cash_roll_today.json")
    best_cash = None
    for c in roll.get("eligible", []):
        if c.get("net_ann_pct") is None:
            continue
        if best_cash is None or float(c["net_ann_pct"]) > float(best_cash["net_ann_pct"]):
            best_cash = c
    if best_cash is None:
        raise SystemExit("face missing: results/etf_book_cash_roll_today.json has no priced eligible repo")

    return {
        "inputs": {
            "cb_union_lens": {
                "path": "results/cb_union_lens.json",
                "generated": union.get("generated"),
                "cutoff": union.get("evidence_cutoff") or union.get("cutoff"),
            },
            "etf_nobond_vt": {
                "path": "results/etf_nobond_vt.json",
                "generated": vt.get("generated"),
                "cutoff": vt.get("evidence_cutoff"),
            },
            "cb_dual_low": {
                "path": "results/cb_dual_low.json",
                "generated": cbface.get("generated_at"),
                "cutoff": cbface.get("evidence_cutoff"),
            },
            "capital_union_decision": {
                "path": "results/capital_union_decision.json",
                "generated": cap.get("generated"),
                "cutoff": None,  # 父面不印，下面按面自己的 evidence_cutoff 兜底
            },
            "etf_book_cash_roll_today": {
                "path": "results/etf_book_cash_roll_today.json",
                "generated": roll.get("generated"),
                "cutoff": roll.get("as_of"),
            },
        },
        "cutoffs": sorted(
            {v for v in [
                union.get("evidence_cutoff") or union.get("cutoff"),
                vt.get("evidence_cutoff"),
                cbface.get("evidence_cutoff"),
                cap.get("evidence_cutoff"),
                roll.get("as_of"),
            ] if v}
        ),
        "etf": {
            "label": "ETF 复合书（去债档 + 8 个点波动目标，%s）" % ETF_ARM,
            "need_cny": float(etf["invested_cny"]),
            "cagr": float(run["cagr"]),
            "vol": float(run["vol"]),
            "sharpe": float(run["sharpe"]),
            "maxdd": float(run["maxdd"]),
            "years": float(run["years"]),
            "scale_ceiling_cny": float(cap["capital_at_line_today_cny"]),
            "sessions_passing": int(cap.get("sessions_passing", -1)),
            "sessions_measured": int(cap.get("sessions_measured", -1)),
            "warn_stale": etf.get("verdict"),
        },
        "cb": {
            "label": "转债双低袖（20 名等权 / 20 日 / 10bp）",
            "need_cny": float(cb["invested_cny"]),
            "cagr": float(cell["cagr"]),
            "vol": float(cell["vol"]),
            "sharpe": float(cell["sharpe"]),
            "maxdd": float(cell["maxdd"]),
            "years": float(cell["years"]),
            "bars": int(cell["bars"]),
        },
        "cash": {
            "contract": best_cash.get("contract"),
            "net_ann_pct": float(best_cash["net_ann_pct"]),
            "rate": float(best_cash["net_ann_pct"]) / 100.0,
            "quoted_pct": best_cash.get("quoted_pct"),
            "window_days": roll.get("window_days"),
        },
    }


def _year(src, key, amount):
    return amount * float(src[key]["cagr"])


def allocate(src, wallet):
    """给一个钱包规模，按算术选配置。返回 dict（含被否掉的备选，不删）。"""
    etf, cb, cash = src["etf"], src["cb"], src["cash"]
    need_e, need_c = etf["need_cny"], cb["need_cny"]
    both_need = need_e + need_c
    rate = cash["rate"]

    def pack(names, used):
        cash_left = wallet - used
        y_etf = need_e * etf["cagr"] if "etf_book" in names else 0.0
        y_cb = need_c * cb["cagr"] if "cb_book" in names else 0.0
        y_cash = max(cash_left, 0.0) * rate
        total = y_etf + y_cb + y_cash
        return {
            "books": list(names),
            "invested_cny": round(used, 2),
            "cash_cny": round(cash_left, 2),
            "cash_weight": round(max(cash_left, 0.0) / wallet, 6),
            "year_cny": round(total, 2),
            "year_pct": round(total / wallet, 6),
            "year_from": {"etf_book": round(y_etf, 2), "cb_book": round(y_cb, 2), "cash": round(y_cash, 2)},
            "fits": used <= wallet + 1e-9,
        }

    options = [pack(("etf_book",), need_e), pack(("cb_book",), need_c)]
    if both_need <= wallet + 1e-9:
        options.append(pack(("etf_book", "cb_book"), both_need))
    else:
        options.append(
            dict(
                pack(("etf_book", "cb_book"), both_need),
                fits=False,
                why_not="needs %.2f more than the wallet" % (both_need - wallet),
            )
        )
    options.append(pack((), 0.0))  # 什么都不开 = 全现金，始终是合法备选

    feasible = [o for o in options if o["fits"]]
    best = sorted(feasible, key=lambda o: (-o["year_cny"], len(o["books"])))[0]
    rejected = [o for o in options if o is not best]
    return {
        "wallet_cny": round(float(wallet), 2),
        "chosen": best,
        "rejected": rejected,
        "both_need_cny": round(both_need, 2),
        "short_for_both_cny": round(max(both_need - wallet, 0.0), 2),
        "etf_scale_ok": wallet <= etf["scale_ceiling_cny"] + 1e-9,
    }


def verdict_of(rows, src, wallet=1000000, tol_cny=1.0):
    """判词纯函数：只吃 rows（已算好的档位表），不吃调用者的偏好。"""
    at = [r for r in rows if abs(r["wallet_cny"] - wallet) < 1.0]
    if not at:
        return "NO_RUNG_AT_THIS_WALLET"
    at = at[0]
    ch = at["chosen"]
    etf_only = [r for r in at["rejected"] if r["books"] == ["etf_book"]]
    cb_only = [r for r in at["rejected"] if r["books"] == ["cb_book"]]
    if ch["books"] == ["etf_book"] and cb_only and ch["year_cny"] - cb_only[0]["year_cny"] > tol_cny:
        pick = "AT_%d_CNY_THE_ETF_BOOK_PAYS_MORE_THAN_THE_CONVERTIBLE_BOOK" % int(wallet)
    elif ch["books"] == ["cb_book"] and etf_only and ch["year_cny"] - etf_only[0]["year_cny"] > tol_cny:
        pick = "AT_%d_CNY_THE_CONVERTIBLE_BOOK_PAYS_MORE_THAN_THE_ETF_BOOK" % int(wallet)
    elif len(ch["books"]) == 2:
        pick = "AT_%d_CNY_BOTH_BOOKS_FIT_AND_PAY_MORE_THAN_EITHER_ALONE" % int(wallet)
    else:
        pick = "AT_%d_CNY_NO_SINGLE_BOOK_COMES_OUT_AHEAD" % int(wallet)

    extra = ""
    if ch["cash_weight"] > 0 and ch["books"]:
        extra = "_AND_THE_REST_ROLLS_AT_THE_CASH_LEG"
    scale = "ETF_BOOK_SCALE_CEILING_IS_%d_CNY_ON_THE_CAPACITY_RULER" % int(round(src["etf"]["scale_ceiling_cny"]))
    return pick + extra, scale


def _names(books):
    if not books:
        return "全现金"
    return "+".join({"etf_book": "ETF 书", "cb_book": "转债书"}.get(b, b) for b in books)


def build(src, today=None):
    today = today or dt.date.today().isoformat()
    future = [c for c in src["cutoffs"] if c > today]
    if future:
        raise SystemExit("refusing to publish: inputs carry a cutoff in the future (%r)" % future)

    rows = [allocate(src, w) for w in LADDER_CNY]
    # 额外一档：两本恰好同开的门槛
    reach = round(src["etf"]["need_cny"] + src["cb"]["need_cny"], 2)
    if not any(abs(r["wallet_cny"] - reach) < 1.0 for r in rows):
        rows.append(allocate(src, reach))
    rows.sort(key=lambda r: r["wallet_cny"])

    pick, scale = verdict_of(rows, src)
    both = [r for r in rows if len(r["chosen"]["books"]) == 2]
    one_m = [r for r in rows if abs(r["wallet_cny"] - 1000000) < 1.0][0]
    # 100 万那档「改开转债书」的反事实：直接按同一把尺手算，不依赖 rejected 的排列
    _need_c, _need_e = src["cb"]["need_cny"], src["etf"]["need_cny"]
    cb_only_year = _need_c * src["cb"]["cagr"] + (1000000.0 - _need_c) * src["cash"]["rate"]
    cb_only = {
        "books": ["cb_book"],
        "year_cny": cb_only_year,
        "year_pct": cb_only_year / 1000000.0,
    }
    margin_cny = one_m["chosen"]["year_cny"] - cb_only_year

    sentence = (
        "100 万时开 %s 年赚 %.0f 元（收益率 %.2f%%，其中现金腿 %.0f 元）；"
        "改开 %s 是 %.0f 元（%.2f%%），差 %.0f 元/年。"
        "两本同开要 %.0f 元——到那一档年赚 %.0f 元（%.2f%%），也就是多掏 %.0f 元换来每年多 %.0f 元，"
        "收益率只抬 %.2f 个百分点，因为新钱全进了年化 %.2f%% 的转债书。"
        "ETF 书今天按容量尺只能撑到 %.0f 元（60 个交易日 %d 天过线），所以钱包再大也不该往它里面加钱，"
        "多出来的部分只能进转债书或现金腿（今天 %.4f%% 净年化）。"
        % (
            _names(one_m["chosen"]["books"]),
            one_m["chosen"]["year_cny"],
            one_m["chosen"]["year_pct"] * 100,
            one_m["chosen"]["year_from"]["cash"],
            _names(cb_only["books"]),
            cb_only["year_cny"],
            cb_only["year_pct"] * 100,
            margin_cny or 0.0,
            reach,
            both[0]["chosen"]["year_cny"] if both else 0.0,
            both[0]["chosen"]["year_pct"] * 100 if both else 0.0,
            reach - 1000000,
            (both[0]["chosen"]["year_cny"] - one_m["chosen"]["year_cny"]) if both else 0.0,
            ((both[0]["chosen"]["year_pct"] - one_m["chosen"]["year_pct"]) * 100) if both else 0.0,
            src["cb"]["cagr"] * 100,
            src["etf"]["scale_ceiling_cny"],
            src["etf"]["sessions_passing"],
            src["cash"]["net_ann_pct"],
        )
    )

    # 现金拖累区间：100 万（含）到两本门槛之间，收益率最低的那一档
    _mid = [r for r in rows if 1000000.0 <= r["wallet_cny"] <= reach + 1e-9]
    _drag = min(_mid, key=lambda r: r["chosen"]["year_pct"])["chosen"] | {
        "wallet_cny": min(_mid, key=lambda r: r["chosen"]["year_pct"])["wallet_cny"]
    }

    out = {
        "face": "wallet_scale_ladder",
        "question": "同一笔钱在 50 万到 230 万之间能开哪本书，多出来的钱该去哪",
        "verdict": pick,
        "scale_verdict": scale,
        "sentence": sentence,
        "evidence_cutoff": min(src["cutoffs"]),
        "cutoffs": src["cutoffs"],
        "inputs": src["inputs"],
        "readings": {"etf_book": src["etf"], "cb_book": src["cb"], "cash_leg": src["cash"]},
        "ladder": rows,
        "ruler": {
            "deployed_per_book": "each book's own invested amount on the 1M book, never scaled up with the wallet",
            "cash": "the rest earns the cash leg's net annual rate taken from today's roll face",
            "not_priced": [
                "joint drawdown / correlation between the two books",
                "two books competing for the same underlying on the same rebalance day",
                "the cost of pushing the ETF book past its capacity line (so it is never pushed)",
            ],
        },
        "caveats": [
            "两本书的收益读数来自不同窗口（ETF 6.9 年 / 转债 %.1f 年）与不同成本模型，本面没有做同窗对账——它比的是「已发布的这两张票面各自说能赚多少」，不是同一段历史的重赛。" % src["cb"]["years"],
            "组合年化是各臂年收益之和除以钱包，不是组合回测：共动、撞车成本、以及同时短缺时的处置都没定价。",
            "转债书的容量上限本面没有测（没有已发布面），所以「钱包更大就多进转债」只是算术上可行，不是已验证可执行。",
            "现金拖累区间：钱包在 100 万到 %.0f 元之间时，多出来的钱只能躺现金（%.4f%%），收益率一路下滑（到 %.0f 元那档只剩 %.2f%%），跨过这个门槛才回到 %.2f%%——所以「190 万比 174 万更差」不是笔误，是阶梯的形状。" % (
                reach,
                src["cash"]["rate"] * 100,
                _drag["wallet_cny"],
                _drag["year_pct"] * 100,
                both[0]["chosen"]["year_pct"] * 100 if both else 0.0,
            ),
        ],
    }
    return out


def _write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)


def render_md(face):
    e, c, k = face["readings"]["etf_book"], face["readings"]["cb_book"], face["readings"]["cash_leg"]
    L = []
    L.append("# 钱包规模阶梯：同一笔钱，从 50 万到 230 万各能开哪本\n")
    L.append("> 生成 %s · 输入 cutoff `%s` · 判词 `%s`\n" % (
        face.get("generated", ""), face["evidence_cutoff"], face["verdict"]))
    L.append("## 结论\n")
    L.append(face["sentence"] + "\n")
    L.append("## 两本书各自的读数（原样来自各自票面）\n")
    L.append("| 书 | 占用（元） | 年化 | 夏普 | 最大回撤 | 波动 | 窗口 |")
    L.append("|---|---|---|---|---|---|---|")
    L.append("| %s | %s | %.2f%% | %.3f | %.2f%% | %.2f%% | %.1f 年 |" % (
        e["label"], format(e["need_cny"], ",.2f"), e["cagr"] * 100, e["sharpe"], e["maxdd"] * 100, e["vol"] * 100, e["years"]))
    L.append("| %s | %s | %.2f%% | %.3f | %.2f%% | %.2f%% | %.1f 年 |" % (
        c["label"], format(c["need_cny"], ",.2f"), c["cagr"] * 100, c["sharpe"], c["maxdd"] * 100, c["vol"] * 100, c["years"]))
    L.append("")
    L.append("现金腿：`%s` 净年化 **%.4f%%**（报价 %s%%，窗口 %s 天）。\n" % (
        k["contract"], k["net_ann_pct"], k["quoted_pct"], k["window_days"]))
    L.append("## 阶梯表\n")
    L.append("| 钱包 | 开哪本 | 占用 | 现金 | 年收益（元） | 收益率 | 被否掉的更优备选 |")
    L.append("|---|---|---|---|---|---|---|")
    for r in face["ladder"]:
        ch = r["chosen"]
        books = "+".join({"etf_book": "ETF", "cb_book": "转债"}.get(b, b) for b in ch["books"]) or "全现金"
        alt = max(r["rejected"], key=lambda o: o["year_cny"])
        alt_books = "+".join({"etf_book": "ETF", "cb_book": "转债"}.get(b, b) for b in alt["books"]) or "全现金"
        L.append("| %s | %s | %s | %s | %s | %.2f%% | %s（%s 元%s） |" % (
            format(r["wallet_cny"], ",.0f"), books, format(ch["invested_cny"], ",.2f"),
            format(ch["cash_cny"], ",.2f"), format(ch["year_cny"], ",.0f"), ch["year_pct"] * 100,
            alt_books, format(alt["year_cny"], ",.0f"), "" if alt["fits"] else "·装不下"))
    L.append("")
    L.append("## 这把尺子没量什么\n")
    for k2 in face["ruler"]["not_priced"]:
        L.append("- %s" % k2)
    L.append("")
    L.append("## 诚实的一半\n")
    for cav in face["caveats"]:
        L.append("- %s" % cav)
    L.append("")
    L.append("## 输入面（每张自印时刻，读者自己看谁老一趟）\n")
    for name, meta in sorted(face["inputs"].items()):
        L.append("- `%s` — generated `%s` · cutoff `%s`" % (meta["path"], meta.get("generated"), meta.get("cutoff")))
    return "\n".join(L) + "\n"


def _verify(face):
    """把已发布面与它的输入重算一遍；漂移说 STALE，自相矛盾说 CHECK FAILED。"""
    src = _src()
    rows = [allocate(src, r["wallet_cny"]) for r in face["ladder"]]
    for got, want in zip(face["ladder"], rows):
        if abs(got["chosen"]["year_cny"] - want["chosen"]["year_cny"]) > 0.05:
            return 3, "STALE: the ladder no longer recomputes from its inputs at wallet %.0f (%.2f vs %.2f)" % (
                want["wallet_cny"], got["chosen"]["year_cny"], want["chosen"]["year_cny"])
    v = verdict_of(face["ladder"], src)
    if (face["verdict"], face["scale_verdict"]) != v:
        return 3, "STALE: verdict no longer recomputes (%r vs %r)" % ((face["verdict"], face["scale_verdict"]), v)
    if min(src["cutoffs"]) != face["evidence_cutoff"]:
        return 3, "STALE: evidence_cutoff moved (%s vs %s)" % (face["evidence_cutoff"], min(src["cutoffs"]))
    return 0, "CHECK OK"


def selftest():
    src = _src()
    ok, fail = [], []

    def leg(name, cond):
        (ok if cond else fail).append(name)

    face = build(src, today="2099-01-01")
    e, c, k = src["etf"], src["cb"], src["cash"]

    leg("1 两本书占用等于已发布票面（ETF）", abs(e["need_cny"] - _load("results/cb_union_lens.json")["books"]["etf_book"]["invested_cny"]) < 1e-9)
    leg("2 两本书占用等于已发布票面（转债）", abs(c["need_cny"] - _load("results/cb_union_lens.json")["books"]["cb_book"]["invested_cny"]) < 1e-9)
    leg("3 ETF 年化逐位等于 nobond_vt08", abs(e["cagr"] - [r for r in _load("results/etf_nobond_vt.json")["runs"] if r["label"] == ETF_ARM][0]["cagr"]) < 1e-12)
    leg("4 转债年化逐位等于主配置格", abs(c["cagr"] - [g for g in _load("results/cb_dual_low.json")["grid"] if g["n_hold"] == 20 and g["rebal"] == 20 and abs(g["cost_bp"] - 10) < 1e-9][0]["cagr"]) < 1e-12)
    leg("5 现金利率不是硬编码（等于滚动面净年化/100）", abs(k["rate"] - k["net_ann_pct"] / 100.0) < 1e-15)

    one_m = [r for r in face["ladder"] if abs(r["wallet_cny"] - 1000000) < 1.0][0]
    cb_only = [r for r in one_m["rejected"] if r["books"] == ["cb_book"]][0]
    leg("6 100 万时 ETF 年收益高于转债（判词与算术一致）", one_m["chosen"]["books"] == ["etf_book"] and one_m["chosen"]["year_cny"] > cb_only["year_cny"])
    leg("7 100 万时两本同开装不下，且缺口 = need 之和 - 钱包", (not [r for r in one_m["rejected"] if r["books"] == ["etf_book", "cb_book"]][0]["fits"]) and abs(one_m["short_for_both_cny"] - (e["need_cny"] + c["need_cny"] - 1000000)) < 0.01)
    leg("8 每个配置的占用+现金=钱包（恒等式）", all(abs(r["chosen"]["invested_cny"] + r["chosen"]["cash_cny"] - r["wallet_cny"]) < 0.01 for r in face["ladder"]))
    leg("9 年收益 = 各臂之和（恒等式）", all(abs(sum(r["chosen"]["year_from"].values()) - r["chosen"]["year_cny"]) < 0.05 for r in face["ladder"]))
    leg("10 钱包变大时年收益（元）不减", all(face["ladder"][i]["chosen"]["year_cny"] <= face["ladder"][i + 1]["chosen"]["year_cny"] + 0.01 for i in range(len(face["ladder"]) - 1)))
    both = [r for r in face["ladder"] if len(r["chosen"]["books"]) == 2][0]
    leg("11 两本同开档位的现金 = 钱包 - 两本 need", abs(both["chosen"]["cash_cny"] - (both["wallet_cny"] - e["need_cny"] - c["need_cny"])) < 0.01)
    leg("12 两本同开的收益率高于只开转债、低于只开 ETF（混合必然夹在中间）", both["chosen"]["year_pct"] < e["cagr"] and both["chosen"]["year_pct"] > c["cagr"])

    # 负控 1：把转债年化抬到 20%，100 万那档必须改选转债
    src2 = json.loads(json.dumps(src))
    src2["cb"]["cagr"] = 0.20
    one_m2 = allocate(src2, 1000000)
    leg("13 负控·转债年化抬到 20% 时 100 万改选转债", one_m2["chosen"]["books"] == ["cb_book"])
    # 负控 2：钱包低于 ETF need，必须落到全现金或转债
    small = allocate(src, e["need_cny"] - 1.0)
    leg("14 负控·钱包低于 ETF 整手门槛时不开 ETF", "etf_book" not in small["chosen"]["books"])
    # 负控 3：篡改一档年收益必须让 check 说 STALE
    bad = json.loads(json.dumps(face))
    bad["ladder"][0]["chosen"]["year_cny"] += 1000.0
    rc, msg = _verify(bad)
    leg("15 负控·篡改一档年收益后 check 说 STALE 且 rc=3", rc == 3 and "STALE" in msg)
    # 负控 4：未来 cutoff 必须拒绝发布
    fut_rejected = False
    try:
        build(src, today="2020-01-01")
    except SystemExit:
        fut_rejected = True
    leg("16 负控·输入 cutoff 在「今天」之后时拒绝发布", fut_rejected)
    # 负控 5：判词必须随算术翻面，不能钉死
    leg("17 负控·判词随算术翻面（负控 1 的判词与主判词不同）", verdict_of([{**one_m2, "wallet_cny": 1000000.0}], src2)[0] != face["verdict"])

    print("selftest: %d/%d PASS" % (len(ok), len(ok) + len(fail)))
    for f in fail:
        print("  FAIL %s" % f)
    return 0 if not fail else 1


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run", choices=("run", "check", "selftest", "status"))
    ap.add_argument("--today", default=None)
    a = ap.parse_args(argv)

    if a.cmd == "selftest":
        return selftest()
    if a.cmd == "status":
        if not os.path.exists(OUT_JSON):
            print("face missing: results/wallet_scale_ladder.json")
            return 2
        face = _load("results/wallet_scale_ladder.json")
        print("verdict=%s\n%s" % (face["verdict"], face["sentence"]))
        return 0
    if a.cmd == "check":
        if not os.path.exists(OUT_JSON):
            print("face missing: results/wallet_scale_ladder.json")
            return 2
        rc, msg = _verify(_load("results/wallet_scale_ladder.json"))
        print(msg)
        return rc

    src = _src()
    face = build(src, today=a.today)
    face["generated"] = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    _write(OUT_JSON, json.dumps(face, ensure_ascii=False, indent=2) + "\n")
    md = render_md(face)
    _write(OUT_MD, md)
    _write(OUT_RESEARCH, md)
    _write(STATE, json.dumps({"last_run": face["generated"], "verdict": face["verdict"]}, ensure_ascii=False) + "\n")
    print(face["verdict"])
    print(face["scale_verdict"])
    print(face["sentence"])
    for r in face["ladder"]:
        ch = r["chosen"]
        print("  %12s  %-14s  year=%12.0f  pct=%6.2f%%  cash=%12.2f" % (
            format(r["wallet_cny"], ",.0f"),
            "+".join(ch["books"]) or "cash_only",
            ch["year_cny"], ch["year_pct"] * 100, ch["cash_cny"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())

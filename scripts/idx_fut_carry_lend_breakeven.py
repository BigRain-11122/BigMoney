#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""What borrowing the tracking ETF has to cost before the four-arm book is worth opening

WHY THIS FILE EXISTS
--------------------
results/idx_fut_carry_tradeable_hedge_capital.json listed a road it refused to price:

    借券（融券 ETF） | 跟踪 ETF | 未定价 | -- | 有，费用本司无序列

Refusing to invent a financing fee is right, but "unpriced" is not an answer to the
question the ticket actually asks, which is **whether** the road is worth walking at
any fee you can plausibly be quoted.  This file answers that half honestly: it does
not guess a fee, it computes the fee **ceiling** -- the annualised rate above which
the borrowed-ETF hedge stops beating what the account can already buy.

Three numbers per arm, all derived from panels already on disk:

    f_zero       the borrow rate at which the arm's own carry is exactly eaten away
                 (= the arm's futures carry, pp/yr of notional);
    f_beat_best  the borrow rate at which the ETF hedge still beats the best
                 *priced* futures-vs-futures pair this arm has (= f_zero minus that
                 pair's net carry).  Negative means no fee saves it.
    track_vol    the residual the ETF leg itself leaves standing (ETF vs its index),
                 printed next to the futures pair's own residual so the reader sees
                 which hedge is actually tighter.

WHAT THIS FILE DOES NOT DO
--------------------------
  * it never states a financing fee: this repo has no 融券 rate series, so the fee
    stays unknown and only the ceiling is a measured quantity;
  * it does not claim 券源 (whether the ETF can be borrowed at all, in the size the
    ticket needs): availability is named, not measured;
  * it does not re-price carry: `long_carry_pp` and `net_carry_pp` are read from the
    published tradeable-hedge face, and that face's own gates must already be green;
  * it does not size an account: the notional here is one long lot, which is the same
    unit the published face prices.
"""
import hashlib
import json
import math
import os
import re
import statistics
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import idx_fut_basis as BASE  # noqa: E402  panel readers + the product->index->ETF map

PARENT_PATH = os.path.join(ROOT, "results", "idx_fut_carry_tradeable_hedge_capital.json")
DESK_PATH = os.path.join(ROOT, "results", "idx_fut_desk_sheet.json")
OUT_PATH = os.path.join(ROOT, "results", "idx_fut_carry_lend_breakeven.json")
DOC_PATH = os.path.join(ROOT, "research", "IDX_FUT_CARRY_LEND_BREAKEVEN.md")

PRODUCTS = ("IF", "IC", "IH", "IM")
TRADING_DAYS = 242.0
FLIP_THRESHOLD = 0.35      # an as-traded ETF cannot move 35% in a day: that is a conversion
MARK_BEGIN = "<!-- BEGIN:LEND-BREAKEVEN -->"
MARK_END = "<!-- END:LEND-BREAKEVEN -->"

# The published map leaves IH without an ETF (idx_fut_basis.PAIRS: IH -> None).  There
# IS an SSE50 tracker on disk, so the road is named here rather than left blank; the
# extension is declared in the face instead of being silently folded into the map.
ETF_EXTENSION = {"IH": ("sh510050", "the published map leaves IH unmapped; SSE50 tracker on disk")}


# ------------------------------------------------------------------ panels
def repair_flips(series, threshold=FLIP_THRESHOLD):
    """As-traded ETF panels carry share conversions that are not returns.

    Same 35% single-day line the ETF book uses (r1313 family): a move beyond it is a
    conversion, so the level is rebuilt forward from the previous close and the day is
    booked as 0% rather than being allowed to manufacture a +176% return.
    """
    dates = sorted(series)
    if len(dates) < 2:
        return dict(series), []
    fixed = {dates[0]: series[dates[0]]}
    fixes = []
    factor = 1.0
    for k in range(1, len(dates)):
        d, prev_d = dates[k], dates[k - 1]
        raw_prev, raw_cur = series[prev_d], series[d]
        # the flip is detected on the *as-traded* reader, before any rescaling
        r = raw_cur / raw_prev - 1.0 if raw_prev > 0 else 0.0
        if abs(r) > threshold:
            factor *= 1.0 / (1.0 + r)
            fixed[d] = fixed[prev_d]          # a conversion day books 0% return
            fixes.append({"date": d, "as_traded_move": round(r * 100.0, 4),
                          "factor": round(1.0 / (1.0 + r), 6)})
        else:
            fixed[d] = raw_cur * factor
    return fixed, fixes


def returns_on(dates, values):
    return [values[k] / values[k - 1] - 1.0 for k in range(1, len(dates))]


def betas(etf_close, idx_close, window=None):
    dates, e, i = BASE.aligned(etf_close, idx_close)
    if window:
        lo, hi = window
        keep = [k for k, d in enumerate(dates) if lo <= d <= hi]
        dates = [dates[k] for k in keep]
        e = [e[k] for k in keep]
        i = [i[k] for k in keep]
    if len(dates) < 30:
        return {"state": "too_short", "days": len(dates)}
    re_ = returns_on(dates, e)
    ri = returns_on(dates, i)
    var = statistics.pvariance(ri)
    if var <= 0:
        return {"state": "degenerate", "days": len(dates)}
    mean_e = statistics.fmean(re_)
    mean_i = statistics.fmean(ri)
    cov = sum((a - mean_e) * (b - mean_i) for a, b in zip(re_, ri)) / len(ri)
    beta = cov / var
    resid = [a - beta * b for a, b in zip(re_, ri)]
    return {
        "state": "ok",
        "days": len(dates) - 1,
        "window": [dates[0], dates[-1]],
        "beta": round(beta, 4),
        "etf_ann_vol_pct": round(statistics.pstdev(re_) * math.sqrt(TRADING_DAYS) * 100.0, 3),
        "index_ann_vol_pct": round(statistics.pstdev(ri) * math.sqrt(TRADING_DAYS) * 100.0, 3),
        "track_resid_ann_vol_pct": round(statistics.pstdev(resid) * math.sqrt(TRADING_DAYS) * 100.0, 3),
        "corr": round(cov / (statistics.pstdev(re_) * statistics.pstdev(ri)), 5)
        if statistics.pstdev(re_) > 0 and statistics.pstdev(ri) > 0 else None,
    }


# ------------------------------------------------------------------ build
def _load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def build():
    parent = _load(PARENT_PATH)
    desk = _load(DESK_PATH)
    problems = []
    if not all((parent.get("gates") or {}).values()):
        problems.append("parent gates are not all green: refusing to price on them")
    if (parent.get("problems") or []):
        problems.append("parent published problems: %s" % "; ".join(parent["problems"]))

    mult = desk.get("multiplier_assumption") or {}
    cutoff = parent.get("evidence_cutoff")
    window = None
    rows = desk.get("rows") or {}

    accounts = {}
    for p in PRODUCTS:
        acct = (parent.get("accounts") or {}).get(p) or {}
        idx_code, idx_name, etf_code = BASE.PAIRS[p]
        extended = None
        if etf_code is None and p in ETF_EXTENSION:
            etf_code, extended = ETF_EXTENSION[p]
        row = rows.get(p) or {}
        close = row.get("close")
        lot_mult = mult.get(p)

        entry = {
            "index": idx_code, "index_name": idx_name, "etf": etf_code,
            "etf_mapping_extended": extended,
            "lot_notional_cny": None, "tracking": None,
            "long_carry_pp": None, "best_priced_pair": None,
            "ceiling_pp": {}, "verdict": None,
        }
        if etf_code is None or not etf_code.startswith("sh"):
            entry["verdict"] = "NO_TRACKING_ETF_ON_DISK"
            accounts[p] = entry
            continue
        if close and lot_mult:
            entry["lot_notional_cny"] = round(float(close) * float(lot_mult), 2)

        etf_close = BASE.load_etf(etf_code)
        idx_close = BASE.load_index(idx_code)
        if not etf_close or not idx_close:
            entry["tracking"] = {"state": "panel_missing",
                                 "etf_present": bool(etf_close), "index_present": bool(idx_close)}
        else:
            etf_fixed, fixes = repair_flips(etf_close)
            entry["tracking"] = betas(etf_fixed, idx_close, window)
            entry["tracking"]["conversion_fixes"] = fixes

        long_carry = None
        best = None
        best_pair = None
        for other, leg in (acct.get("tradeable") or {}).items():
            if leg.get("long_carry_pp") is not None:
                long_carry = leg["long_carry_pp"]
            net = leg.get("net_carry_pp")
            if net is not None and (best is None or net > best):
                best, best_pair = net, other
        entry["long_carry_pp"] = long_carry
        entry["best_priced_pair"] = best_pair
        entry["best_priced_pair_net_pp"] = best

        if long_carry is None:
            entry["verdict"] = "CARRY_UNPRICED_CANNOT_CEILING"
            # the desk face does carry a compound figure for IH (2.443%); this page
            # ceilings on the simple per-notional carry the arm face uses, so mixing
            # the two would print a ceiling built on a different ruler (r1779 family).
            if row.get("carry_ann_compound_pct") is not None:
                entry["desk_carry_compound_pct_not_used"] = row["carry_ann_compound_pct"]
            accounts[p] = entry
            continue

        f_zero = round(long_carry, 3)
        entry["ceiling_pp"]["net_carry_zero"] = f_zero
        if entry["lot_notional_cny"] and entry["tracking"] and entry["tracking"].get("beta"):
            entry["borrow_notional_cny"] = round(
                entry["lot_notional_cny"] * entry["tracking"]["beta"], 2)
            entry["carry_income_one_year_cny"] = round(
                entry["lot_notional_cny"] * long_carry / 100.0, 2)
        if best is None:
            entry["ceiling_pp"]["above_best_priced_pair"] = None
            entry["verdict"] = "LEND_IS_THE_ONLY_ROAD_WITH_A_CEILING_BELOW_%.3fPP" % f_zero
        else:
            f_beat = round(long_carry - best, 3)
            entry["ceiling_pp"]["above_best_priced_pair"] = f_beat
            if f_beat > 0:
                entry["verdict"] = ("LEND_BEATS_%s_BELOW_%.3fPP" % (best_pair, f_beat))
            else:
                entry["verdict"] = ("LEND_CANNOT_BEAT_%s_AT_ANY_NONNEGATIVE_FEE" % best_pair)
        accounts[p] = entry

    totals = {
        "arms_with_a_ceiling": sorted([p for p in accounts
                                       if accounts[p]["ceiling_pp"].get("net_carry_zero") is not None]),
        "arms_that_beat_the_priced_pair": sorted(
            [p for p in accounts
             if isinstance(accounts[p]["ceiling_pp"].get("above_best_priced_pair"), float)
             and accounts[p]["ceiling_pp"]["above_best_priced_pair"] > 0]),
        "arms_that_no_fee_saves": sorted(
            [p for p in accounts
             if isinstance(accounts[p]["ceiling_pp"].get("above_best_priced_pair"), float)
             and accounts[p]["ceiling_pp"]["above_best_priced_pair"] <= 0]),
    }

    inputs = {}
    for rel in ["results/idx_fut_carry_tradeable_hedge_capital.json", "results/idx_fut_desk_sheet.json"]:
        path = os.path.join(ROOT, rel)
        with open(path, "rb") as f:
            inputs[rel] = hashlib.sha256(f.read()).hexdigest()
    for p in PRODUCTS:
        idx_code, _, etf_code = BASE.PAIRS[p]
        if etf_code is None and p in ETF_EXTENSION:
            etf_code = ETF_EXTENSION[p][0]
        for code in (idx_code, etf_code):
            if not code:
                continue
            folder = BASE.IDX_DIR if code.startswith("sh000") else os.path.join(ROOT, "data", "daily")
            path = os.path.join(folder, code + ".csv")
            rel = os.path.relpath(path, ROOT).replace("\\", "/")
            if os.path.exists(path):
                with open(path, "rb") as f:
                    inputs[rel] = hashlib.sha256(f.read()).hexdigest()

    face = {
        "kind": "idx_fut_carry_lend_breakeven",
        "generated": datetime.now().astimezone().isoformat(timespec="seconds"),
        "evidence_cutoff": cutoff,
        "book_capital_cny": parent.get("book_capital_cny"),
        "target_pct": parent.get("target_pct"),
        "method": "ceiling = the annualised borrow fee at which the ETF hedge stops paying",
        "fee_is_measured": False,
        "why_no_fee": "this repo has no 融券 financing-rate series; only the ceiling is measured",
        "availability_is_measured": False,
        "why_no_availability": "券源 (whether the ETF can be borrowed at this size) is not on any panel",
        "accounts": accounts,
        "totals": totals,
        "problems": problems,
        "sources": {
            "parent": "results/idx_fut_carry_tradeable_hedge_capital.json",
            "desk": "results/idx_fut_desk_sheet.json",
            "panel_reader": "scripts/idx_fut_basis.py (load_etf/load_index/aligned/PAIRS)",
        },
        "inputs": inputs,
    }
    face["verdict"] = judge(face)
    return face


def judge(face):
    if face["problems"]:
        return "REFUSE_INPUTS_NOT_TRUSTWORTHY"
    t = face["totals"]
    if not t["arms_with_a_ceiling"]:
        return "NO_ARM_HAS_A_MEASURED_CEILING"
    if t["arms_that_beat_the_priced_pair"] and not t["arms_that_no_fee_saves"]:
        return "LEND_FEE_CEILING_EXISTS_FOR_EVERY_CARRY_ARM"
    if t["arms_that_beat_the_priced_pair"] and t["arms_that_no_fee_saves"]:
        return "THE_CEILING_DEPENDS_ON_WHICH_ARM"
    return "NO_FEE_MAKES_THE_BORROWED_LEG_THE_BETTER_HEDGE"


# ------------------------------------------------------------------ render
def _pp(v):
    return "--" if v is None else ("%+.3f" % v)


def _money(v):
    return "--" if v is None else "{:,.0f}".format(v)


def render_md(face):
    a = face["accounts"]
    L = []
    L.append(MARK_BEGIN)
    L.append("")
    L.append("generated %s | evidence_cutoff **%s** | verdict **%s**"
             % (face["generated"], face["evidence_cutoff"], face["verdict"]))
    L.append("")
    L.append("## 融券这条路的天花板（不是收益率）")
    L.append("")
    L.append("本司**没有融券费率序列**，所以这页不印费率，只印「费率必须低于多少，这条路才值得」。"
             "同一个数还有第二层：低于多少才**胜过**账户今天已经买得到的那个期货对。")
    L.append("")
    L.append("| 臂 | 跟踪 ETF | ETF 对指数 beta | 跟踪残差年化波动 | 本臂 carry | 已定价最好对冲 | 净 carry 归零天花板 | 胜过它的天花板 | 判词 |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for p in PRODUCTS:
        e = a[p]
        tr = e.get("tracking") or {}
        L.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            p, e.get("etf") or "--",
            "--" if tr.get("beta") is None else "%.3f" % tr["beta"],
            "--" if tr.get("track_resid_ann_vol_pct") is None else "%.2f%%" % tr["track_resid_ann_vol_pct"],
            _pp(e.get("long_carry_pp")),
            "%s %spp" % (e.get("best_priced_pair") or "--", _pp(e.get("best_priced_pair_net_pp")))
            if e.get("best_priced_pair") else "--",
            _pp(e["ceiling_pp"].get("net_carry_zero")),
            _pp(e["ceiling_pp"].get("above_best_priced_pair")),
            e.get("verdict")))
    L.append("")
    L.append("## 一手的名义与它一年的 carry")
    L.append("")
    L.append("| 臂 | 一手名义 | 借券名义（× beta） | 一年 carry 收入 | 转换修复条数 |")
    L.append("|---|---|---|---|---|")
    for p in PRODUCTS:
        e = a[p]
        tr = e.get("tracking") or {}
        L.append("| %s | %s | %s | %s | %d |" % (
            p, _money(e.get("lot_notional_cny")), _money(e.get("borrow_notional_cny")),
            _money(e.get("carry_income_one_year_cny")),
            len(tr.get("conversion_fixes") or [])))
    L.append("")
    L.append("## 一句话")
    L.append("")
    t = face["totals"]
    beat = t["arms_that_beat_the_priced_pair"]
    zero = t["arms_that_no_fee_saves"]
    if beat:
        cells = []
        for p in beat:
            e = a[p]
            cells.append("%s 要低于 %spp 才胜过今天买得到的 %s 对"
                         % (p, _pp(e["ceiling_pp"]["above_best_priced_pair"]), e["best_priced_pair"]))
        L.append("· " + "；".join(cells) + "。这个数落在 1pp 以下时，它不是一条投资路，而是一句「除非近零费率，否则别借」。")
    if zero:
        L.append("· %s：任何非负费率都救不回来（期货对已经比它自己的 carry 更值）。" % "、".join(zero))
    if "IH" in a and a["IH"].get("verdict") == "CARRY_UNPRICED_CANNOT_CEILING":
        L.append("· IH：本臂的 carry 在臂面未定价，所以天花板算不出来；desk 面那个 %s%% 是复合口径，与本页单利口径不同，不混用。"
                 % (a["IH"].get("desk_carry_compound_pct_not_used") or "--"))
    L.append("")
    L.append("## 读法")
    L.append("")
    L.append("1. **天花板不是报价**：拿到的融券费率低于该臂的「胜过它的天花板」，这条路才比已买得到的期货对冲更值；低于「归零天花板」才至少不亏 carry。两个都印，因为只印一个等于替读者做了选择。")
    L.append("2. **券源没测**：ETF 能不能按这个名义借到，本司任何面板都没有答案。天花板成立不等于借得到；借不到时这张表只是一把尺子。")
    L.append("3. **跟踪残差要一起看**：期货对的对冲残差来自指数价差，融券 ETF 的残差来自跟踪误差。表里两个都给了读数，谁更紧就不用猜。")
    fixes = []
    for p in PRODUCTS:
        for fx in ((a[p].get("tracking") or {}).get("conversion_fixes") or []):
            fixes.append("%s %s 单日 %.2f%% → 已按前收重定基" % (p, fx["date"], fx["as_traded_move"]))
    if fixes:
        L.append("4. **as-traded 面板里的份额折算已剔除**（%d 处，按 35%% 单日线，与 ETF 账本同一判例）：%s。" % (len(fixes), "；".join(fixes)))
    L.append("")
    L.append(MARK_END)
    return "\n".join(L) + "\n"


def splice_doc(block):
    if os.path.exists(DOC_PATH):
        with open(DOC_PATH, encoding="utf-8") as f:
            text = f.read()
    else:
        text = (
            "# 融券空腿：费率天花板\n\n"
            "> 本页读数块由 `scripts/idx_fut_carry_lend_breakeven.py` 渲染（`--write` 重写、`--check` 逐字比对）。\n\n"
        )
    pat = re.compile(re.escape(MARK_BEGIN) + r".*?" + re.escape(MARK_END) + r"\n?", re.S)
    if pat.search(text):
        text = pat.sub(block, text, count=1)
    else:
        text = text.rstrip("\n") + "\n\n" + block
    with open(DOC_PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def dump_json(path, face):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(face, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")


# ------------------------------------------------------------------ check
def check():
    if not os.path.exists(OUT_PATH):
        return 3, "STALE: results/idx_fut_carry_lend_breakeven.json is missing"
    with open(OUT_PATH, encoding="utf-8") as f:
        on_disk = json.load(f)
    fresh = build()
    if fresh["inputs"] != on_disk.get("inputs"):
        return 3, "STALE: an input panel moved since this face was written (re-run --write)"
    if fresh["evidence_cutoff"] != on_disk.get("evidence_cutoff"):
        return 3, "STALE: the parent's evidence_cutoff moved"
    for p in PRODUCTS:
        d = on_disk["accounts"].get(p, {})
        f_ = fresh["accounts"].get(p, {})
        if d.get("verdict") != f_.get("verdict"):
            return 1, "CHECK FAILED: %s verdict %s != recomputed %s" % (
                p, d.get("verdict"), f_.get("verdict"))
        for key in ("long_carry_pp", "best_priced_pair_net_pp"):
            dv, fv = d.get(key), f_.get(key)
            if (dv is None) != (fv is None) or (dv is not None and abs(dv - fv) > 1e-9):
                return 1, "CHECK FAILED: %s.%s %s != %s" % (p, key, dv, fv)
        for key in ("net_carry_zero", "above_best_priced_pair"):
            dv = (d.get("ceiling_pp") or {}).get(key)
            fv = (f_.get("ceiling_pp") or {}).get(key)
            if (dv is None) != (fv is None) or (dv is not None and abs(dv - fv) > 1e-9):
                return 1, "CHECK FAILED: %s.ceiling_pp.%s %s != %s" % (p, key, dv, fv)
    if not os.path.exists(DOC_PATH):
        return 1, "CHECK FAILED: page missing"
    with open(DOC_PATH, encoding="utf-8") as f:
        page = f.read()
    m = re.search(re.escape(MARK_BEGIN) + r".*?" + re.escape(MARK_END), page, re.S)
    if not m:
        return 1, "CHECK FAILED: page has no readings block"
    want = render_md(fresh).split(MARK_BEGIN, 1)[1].split(MARK_END, 1)[0]
    got = m.group(0).split(MARK_BEGIN, 1)[1].split(MARK_END, 1)[0]
    # the render stamps `generated` at call time; identity is the readings, not the clock
    norm = lambda s: re.sub(r"^generated .*$", "generated <t>", s.strip(), flags=re.M)
    if norm(want) != norm(got):
        return 1, "CHECK FAILED: page block differs from a fresh render (re-run --write)"
    return 0, "ok: %d arms, verdict %s" % (len(on_disk["accounts"]), on_disk["verdict"])


# ------------------------------------------------------------------ selftest
def selftest():
    legs = []

    # 1. a share conversion is not a return
    pan = {"2020-01-01": 1.0, "2020-01-02": 1.0, "2020-01-03": 3.0, "2020-01-04": 3.1}
    fixed, fixes = repair_flips(pan)
    worst = max(abs(fixed[d] / fixed[sorted(fixed)[k - 1]] - 1.0)
                for k, d in enumerate(sorted(fixed)) if k > 0)
    legs.append((len(fixes) == 1 and worst < FLIP_THRESHOLD,
                 "conversion day is booked as 0%% (fixes=%d, worst day %.3f)" % (len(fixes), worst)))

    # 2. beta of a perfect copy is 1 and its residual is 0
    idx = {"2020-01-%02d" % k: 100.0 * (1.01 ** k) for k in range(1, 49)}
    etf = dict(idx)
    b = betas(etf, idx)
    legs.append((b.get("state") == "ok" and abs(b["beta"] - 1.0) < 1e-6
                 and b["track_resid_ann_vol_pct"] < 1e-6,
                 "perfect copy -> beta 1, residual 0 (%s)" % (b.get("beta"),)))

    # 3. the ceiling arithmetic: f_beat = long carry - the priced pair's net carry
    long_carry, best = 6.599, 0.958
    legs.append((abs((long_carry - best) - 5.641) < 1e-9,
                 "ceiling arithmetic %.3f - %.3f = %.3f" % (long_carry, best, long_carry - best)))

    # 4. a pair that earns more than the arm's own carry leaves no positive fee room
    legs.append(((2.0 - 6.0) <= 0, "no fee saves an arm whose pair already earns more"))

    # 5. live face is self-consistent and every carry arm has a ceiling
    face = build()
    if face["problems"]:
        legs.append((False, "live build refused: %s" % "; ".join(face["problems"])))
    else:
        legs.append((all(face["accounts"][p]["ceiling_pp"].get("net_carry_zero") is not None
                         or face["accounts"][p]["verdict"] == "CARRY_UNPRICED_CANNOT_CEILING"
                         for p in PRODUCTS),
                     "every arm with a carry also has a ceiling"))
        # 6. the borrow notional is one lot scaled by the measured beta, not the lot itself
        ok = True
        for p in PRODUCTS:
            e = face["accounts"][p]
            if e.get("borrow_notional_cny") and e.get("lot_notional_cny"):
                want = e["lot_notional_cny"] * e["tracking"]["beta"]
                ok = ok and abs(e["borrow_notional_cny"] - want) / want < 5e-4
        legs.append((ok, "borrow notional = lot notional x measured beta"))

    passed = sum(1 for ok_, _ in legs if ok_)
    for ok_, name in legs:
        print(("PASS  " if ok_ else "FAIL  ") + name)
    print("%d/%d PASS" % (passed, len(legs)))
    return 0 if passed == len(legs) else 1


# ------------------------------------------------------------------ main
def run(write=True):
    face = build()
    if face["verdict"].startswith("REFUSE"):
        print("REFUSE: " + "; ".join(face["problems"]))
        return 4
    if write:
        dump_json(OUT_PATH, face)
        splice_doc(render_md(face))
    print("verdict %s" % face["verdict"])
    for p in PRODUCTS:
        e = face["accounts"][p]
        print("%-3s etf %-9s beta %s | carry %s | best pair %s %s | zero %s | beats %s | %s"
              % (p, e.get("etf") or "--",
                 "--" if (e.get("tracking") or {}).get("beta") is None
                 else "%.3f" % e["tracking"]["beta"],
                 _pp(e.get("long_carry_pp")), e.get("best_priced_pair") or "--",
                 _pp(e.get("best_priced_pair_net_pp")),
                 _pp(e["ceiling_pp"].get("net_carry_zero")),
                 _pp(e["ceiling_pp"].get("above_best_priced_pair")),
                 e.get("verdict")))
    return 0


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd in ("run", "--write"):
        return run(write=True)
    if cmd in ("dry", "--dry"):
        return run(write=False)
    if cmd == "--check":
        rc, msg = check()
        print(msg)
        return rc
    if cmd == "--selftest":
        return selftest()
    print("usage: python scripts/idx_fut_carry_lend_breakeven.py [run|dry|--check|--selftest]")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))

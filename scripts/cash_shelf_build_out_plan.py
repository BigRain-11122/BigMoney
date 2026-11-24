#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""cash_shelf_build_out_plan -- a THIN capacity verdict is a schedule, not a wall.

WHY THIS FACE EXISTS
--------------------
`cb_parking_shelf_at_size` (r2041) put the five cash vehicles on the 1%/10% capacity
ruler and published, for the ticket's cash of 565,246 CNY:

  * 511380 convertible   1.13% of the bad day  -> THIN   (four days of extra per year)
  * 511180 convertible   2.57%                 -> THIN
  * 511360 short-financing 4.32%               -> THIN   (+3,088 CNY/yr over repo)
  * 511010 treasury       0.83%                -> OPEN   (+3,199 CNY/yr over repo)
  * 511880 money          0.006%               -> OPEN

It stopped at the arrow.  A treasurer reading "THIN" has exactly two moves: don't buy,
or buy over several sessions.  Nobody had priced the second move, so the shelf that
pays the most (511360, +0.546pp over repo) looked unusable for a reason that is really
a calendar question.

THE QUESTION (frozen before the first run)
------------------------------------------
If we spread the ticket across the sessions the capacity ruler allows, what does that
cost -- measured on history, not modelled?

MODEL
-----
* **Day ceiling** = 1% of the bad-day turnover, read from r2041's published face
  (`max_open_order_cny`).  Never retyped: the face is loaded and a selftest leg
  asserts the bands still agree with `repo_capacity_at_size`.
* **Sessions to fill** = ceil(size / ceiling), at least 1.  Integer lots are not
  re-derived here -- r2041 already priced the lot residue; this face prices *time*.
* **Fill price** = the session's own close on the adjusted price index.  The index is
  the same return series r2040/r2041 used: money vehicles go through
  `etf_book_cash_vehicle.consolidation_returns` (share resets booked as zero), the rest
  use the flip-repaired panel close.
* **Equal cash per session** means the achieved average price is the *harmonic* mean of
  the n session prices, not the arithmetic mean: buying the same yuan amount each day
  buys more shares on the cheap days.  Using the arithmetic mean would overstate the
  cost of batching, so the harmonic mean is the only honest one and a selftest leg
  pins it (a 2-day 10/20 tape gives 13.333, not 15).
* **Slippage** = (harmonic mean over the window) / (first session's price) - 1, in bp.
  Positive = batching paid up.  Every overlapping window on the panel is evaluated, so
  the published distribution is what actually happened, not a normal approximation.
* **Money** = size x slippage.  Compared against r2041's own `cny_per_year_vs_repo` for
  the same row and tier, so "one bad batch of sessions costs more than a year of the
  extra" is a subtraction of two published numbers.

VERDICTS (mechanical, no taste)
-------------------------------
* ONE_SESSION_IS_ENOUGH              -- the ceiling clears the tier in a single session.
* SCHEDULING_REPLACES_CAPACITY       -- >1 session, and the 95th-percentile slippage in
                                        money is no larger than the year's extra.
* THE_SCHEDULE_COSTS_MORE_THAN_THE_YEAR -- the 95th-percentile slippage in money exceeds
                                        the year's extra: the shelf's capacity is a wall
                                        after all.
* BATCHING_IS_A_CARRY_LOSS           -- every window's slippage is >= 0: batching can only
                                        ever pay up, by a known amount (a price series that
                                        only walks up).  The amount is on the page.
* BATCHING_IS_TWO_SIDED              -- some window lets batching come out cheaper: the sign
                                        is not known in advance.  Whether that is affordable
                                        is the SCHEDULING verdict's question, not this one --
                                        the two verdicts are read together.
* FILLS_TAKE_LONGER_THAN_A_MONTH     -- more than 21 sessions to fill at the ceiling.
* FILLS_TAKE_LONGER_THAN_A_MONTH     -- more than 21 sessions to fill at the ceiling.
* UNIT_SUSPECT                       -- a ceiling outside the published magnitude; no
                                        schedule is printed for that row.

Usage:
    python scripts/cash_shelf_build_out_plan.py run
    python scripts/cash_shelf_build_out_plan.py --check
    python scripts/cash_shelf_build_out_plan.py --selftest
"""

from __future__ import annotations

import datetime as dt
import hashlib
import io
import json
import math
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import cb_parking_shelf_at_size as S  # noqa: E402  (the shelf face: rows, tiers, bands)
import etf_book_cash_vehicle as CV  # noqa: E402  (money ETF share-reset consolidation)
import etf_composite_pf as E  # noqa: E402  (ETF panel)
import etf_equity_alpha as A  # noqa: E402  (flip repair)

R2041_JSON = os.path.join(ROOT, "results", "cb_parking_shelf_at_size.json")
OUT_JSON = os.path.join(ROOT, "results", "cash_shelf_build_out_plan.json")
OUT_MD = os.path.join(ROOT, "research", "CASH_SHELF_BUILD_OUT_PLAN.md")

SCHEMA = "cash-shelf-build-out-plan/v1"
MAX_SESSIONS_A_MONTH = 21
TICK_CNY = 0.001          # the exchange minimum price increment for an ETF (yuan):
                          # 0.88bp on a 114.19 money ETF, 0.86bp on an 11.59 convertible
P95 = 95.0
P05 = 5.0


# --------------------------------------------------------------------------- helpers
def _sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _now():
    return dt.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")


def log(*a):
    print(*a, flush=True)


def sessions_to_fill(size_cny, ceiling_cny):
    """How many capacity-ruler sessions the tier needs.  Never zero, never fractional."""
    if not (np.isfinite(ceiling_cny) and ceiling_cny > 0):
        return None
    return max(1, int(math.ceil(float(size_cny) / float(ceiling_cny))))


def harmonic_mean(values):
    """Equal-cash-per-session average price.  Zero/NaN prices would divide by zero, so a
    window containing one is refused rather than silently distorted."""
    v = np.asarray([float(x) for x in values], dtype=float)
    if not len(v) or not np.all(np.isfinite(v)) or np.any(v <= 0):
        return float("nan")
    return float(len(v) / np.sum(1.0 / v))


def batch_slippage_bp(index_vals, days):
    """Every overlapping window on the index: batching vs buying it all on day one, in bp.

    A window is only usable if it has `days` finite positive prices."""
    p = np.asarray([float(x) for x in index_vals], dtype=float)
    if days < 1 or len(p) < days:
        return np.array([], dtype=float)
    out = []
    for i in range(0, len(p) - days + 1):
        win = p[i:i + days]
        if not np.all(np.isfinite(win)) or np.any(win <= 0):
            continue
        ref = win[0]
        hm = harmonic_mean(win)
        if not np.isfinite(hm):
            continue
        out.append((hm / ref - 1.0) * 1e4)
    return np.asarray(out, dtype=float)


def adjusted_index(code, klass, close_all):
    """A cumulative price index on the panel's own calendar.

    Money vehicles are share-consolidating: their traded line resets ~yearly (~101 -> ~100)
    which is a -1% day that is not a loss.  The consolidation helper books those days as
    zero return; everything else uses the flip-repaired close.  Returns (index, note)."""
    panel_idx = close_all.index
    if klass == "money":
        try:
            rets, jumps = CV.consolidation_returns(CV.load_etf(code))
            if len(rets) >= 40:
                rets = rets.reindex(panel_idx).fillna(0.0)
                idx = (1.0 + rets).cumprod()
                idx = idx / float(idx.iloc[0])
                return idx, {"source": "consolidation_returns",
                             "share_resets_removed": int(len(jumps))}
        except Exception as exc:  # noqa: BLE001 -- fall back and say so
            log("  %s: consolidation unavailable (%s) -> flip-repaired close" % (code, exc))
    px = close_all[code].astype(float)
    rets = px.pct_change().fillna(0.0)
    idx = (1.0 + rets).cumprod()
    idx = idx / float(idx.iloc[0])
    return idx, {"source": "panel_close_pct_change", "share_resets_removed": 0}


# --------------------------------------------------------------------------- build
def build(write=True, verbose=True):
    t0 = time.time()
    global log
    _log = log
    if not verbose:
        log = lambda *a: None

    if not os.path.exists(R2041_JSON):
        print("MISSING FACE: %s" % R2041_JSON)
        return 2
    with io.open(R2041_JSON, encoding="utf-8") as f:
        pub = json.load(f)
    repo_pct = float(pub["comparator"]["repo_net_pct"])
    tiers = [int(x) for x in pub["tiers_cny"]]
    ticket_cash = float(pub["ticket_cash_cny"])
    ticket_tier = min(tiers, key=lambda t: abs(t - ticket_cash))

    close_all, open_all, amt_all, _feats = E.build_panel()
    close_all, _o2, n_flip = A.repair_flips(close_all, open_all)
    log("  panel: %d cols x %d bars, %d flips repaired"
        % (close_all.shape[1], close_all.shape[0], n_flip))

    rows = []
    for prow in pub["rows"]:
        code = prow["code"]
        if code not in close_all.columns:
            print("MISSING INSTRUMENT: %s" % code)
            return 2
        idx, src = adjusted_index(code, prow["class"], close_all)
        idx = idx[idx.index >= pd.Timestamp(S.START)].dropna()
        vals = idx.values

        ceiling = prow.get("max_open_order_cny")
        unit_ok = bool(prow.get("unit_check", {}).get("ok", False))
        by_tier = {}
        for tier in tiers:
            cap = prow["capacity"][str(tier)]
            days = sessions_to_fill(tier, ceiling) if unit_ok else None
            year_extra = cap.get("cny_per_year_vs_repo")
            rec = {"class_of_tier": cap.get("class"),
                   "sessions_to_fill": days,
                   "bad_day_participation_pct": cap.get("participation_pct_of_bad_day"),
                   "year_extra_cny": year_extra}
            if days is None:
                rec["windows"] = 0
                by_tier[str(tier)] = rec
                continue
            slip = batch_slippage_bp(vals, days)
            rec["windows"] = int(len(slip))
            if len(slip):
                med = float(np.median(slip))
                p05 = float(np.percentile(slip, P05))
                p95 = float(np.percentile(slip, P95))
                worst = float(slip.max())
                rec.update({
                    "slip_median_bp": round(med, 4),
                    "slip_p05_bp": round(p05, 4),
                    "slip_p95_bp": round(p95, 4),
                    "slip_worst_bp": round(worst, 4),
                    "slip_never_negative": bool(p05 >= 0.0),
                    "median_cny": round(med / 1e4 * tier, 2),
                    "p95_cny": round(p95 / 1e4 * tier, 2),
                    "worst_cny": round(worst / 1e4 * tier, 2),
                    "p95_over_year_extra": (round(p95 / 1e4 * tier / year_extra, 4)
                                            if year_extra not in (None, 0) else None),
                    "worst_over_year_extra": (round(worst / 1e4 * tier / year_extra, 4)
                                              if year_extra not in (None, 0) else None),
                })
            by_tier[str(tier)] = rec

        row_verdicts = verdicts_for(by_tier, tiers, prow.get("price"))
        rows.append({
            "code": code,
            "label": prow["label"],
            "class": prow["class"],
            "price": prow.get("price"),
            "lot_value_cny": prow.get("lot_value_cny"),
            "one_defence_day_cny_at_ticket": prow["capacity"][str(ticket_tier)]
            .get("one_defence_day_cny"),
            "bad_day_turnover_yuan": prow.get("turnover_bad_day_yuan"),
            "open_order_ceiling_cny": ceiling,
            "unit_check_ok": unit_ok,
            "tick_size_bp": (round(TICK_CNY / float(prow["price"]) * 1e4, 4)
                             if prow.get("price") else None),
            "index_source": src,
            "index_bars": int(len(vals)),
            "index_first": str(idx.index[0].date()),
            "index_last": str(idx.index[-1].date()),
            "tiers": by_tier,
            "verdict": row_verdicts,
        })
        log("  %s %-14s ceiling=%swan  %s" % (
            code, prow["label"],
            ("%.1f" % (ceiling / 1e4)) if ceiling else "n/a",
            " ".join("%dd" % by_tier[str(t)]["sessions_to_fill"]
                     if by_tier[str(t)]["sessions_to_fill"] else "n/a" for t in tiers)))

    # ---- the comparison this face exists for: which shelf is slow AND free?
    ticket_key = str(tiers[1]) if len(tiers) > 1 else str(tiers[0])
    cheap_slow, cheap_slow_p95 = [], []
    for r in rows:
        t = r["tiers"].get(ticket_key, {})
        if t.get("sessions_to_fill") and t["sessions_to_fill"] > 1 and t.get("p95_cny") is not None:
            cheap_slow.append((r["code"], r["class"], t["sessions_to_fill"],
                               t["year_extra_cny"], t["p95_cny"]))
            cheap_slow_p95.append(t["p95_cny"])

    headline = {
        "ticket_cash_cny": ticket_cash,
        "tier_used_for_headline": int(ticket_key),
        "shelves_needing_more_than_one_session": [
            {"code": c, "class": k, "sessions": d, "year_extra_cny": y, "p95_batching_cny": p}
            for c, k, d, y, p in cheap_slow],
        "the_slowest_shelf": max(cheap_slow, key=lambda x: x[2])[0] if cheap_slow else None,
        "the_cheapest_slow_shelf": (max([x for x in cheap_slow if x[3] and x[3] > 0],
                                        key=lambda x: x[3])[0] if cheap_slow else None),
    }

    payload = {
        "schema": SCHEMA,
        "artifact": "cash_shelf_build_out_plan",
        "generated": _now(),
        "evidence_cutoff": str(close_all.index[-1].date()),
        "window": {"start": S.START, "end": str(close_all.index[-1].date())},
        "question": ("if we spread the ticket across the sessions the capacity ruler allows, "
                     "what does that cost -- measured on history, not modelled?"),
        "upstream": {"face": os.path.relpath(R2041_JSON, ROOT).replace("\\", "/"),
                     "sha256": _sha(R2041_JSON),
                     "tiers_cny": tiers,
                     "repo_net_pct": repo_pct},
        "ruler": {"day_ceiling": "1% of the bad-day turnover (r2041 max_open_order_cny), imported not retyped",
                  "fill_price": "adjusted close index; money vehicles via consolidation_returns"
                                " (share resets booked as zero), others via flip-repaired panel close",
                  "average_price": "harmonic mean over equal-cash sessions (a selftest leg pins it)",
                  "slippage": "(harmonic mean / first-session price - 1) in bp, all overlapping windows",
                  "money": "size x slippage; compared to r2041's cny_per_year_vs_repo for the same row+tier"},
        "rows": rows,
        "headline": headline,
        "verdict": verdicts_overall(rows, ticket_key),
    }
    log("  headline: %s" % json.dumps(headline, ensure_ascii=False)[:300])

    if write:
        os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
        with io.open(OUT_JSON, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2, sort_keys=False)
            f.write("\n")
        with io.open(OUT_MD, "w", encoding="utf-8") as f:
            f.write(render_md(payload))
        log("  wrote %s" % os.path.relpath(OUT_JSON, ROOT))
        log("  wrote %s" % os.path.relpath(OUT_MD, ROOT))
    log("  done in %.1fs" % (time.time() - t0))
    return 0


def verdicts_for(by_tier, tiers, price=None):
    out = []
    days = [by_tier[str(t)]["sessions_to_fill"] for t in tiers
            if by_tier[str(t)]["sessions_to_fill"] is not None]
    slips = [by_tier[str(t)] for t in tiers if by_tier[str(t)].get("windows")]
    if days and all(d == 1 for d in days):
        out.append("ONE_SESSION_IS_ENOUGH")
    if days and max(days) > MAX_SESSIONS_A_MONTH:
        out.append("FILLS_TAKE_LONGER_THAN_A_MONTH")
    multi = [s for s in slips if s["sessions_to_fill"] > 1]
    if multi:
        # only a shelf that would otherwise earn MORE than repo has anything to lose by
        # waiting; comparing a negative year's extra against a batching cost is not a
        # comparison, so those rows are judged on price risk alone
        earning = [s for s in multi if s.get("year_extra_cny") and s["year_extra_cny"] > 0]
        if earning:
            tail_ok = all(abs(s["p95_cny"]) <= abs(s["year_extra_cny"]) for s in earning)
            out.append("SCHEDULING_REPLACES_CAPACITY" if tail_ok
                       else "THE_SCHEDULE_COSTS_MORE_THAN_THE_YEAR")
        p05_min = min(s["slip_p05_bp"] for s in multi)
        out.append("BATCHING_IS_A_CARRY_LOSS" if p05_min >= 0.0 else "BATCHING_IS_TWO_SIDED")
    return out


def verdicts_overall(rows, ticket_key):
    out = []
    slow = [r for r in rows
            if (r["tiers"].get(ticket_key, {}).get("sessions_to_fill") or 1) > 1]
    if not slow:
        out.append("EVERY_SHELF_FILLS_IN_ONE_SESSION")
        return out
    free = [r["code"] for r in slow
            if "SCHEDULING_REPLACES_CAPACITY" in r["verdict"]]
    costly = [r["code"] for r in slow
              if "THE_SCHEDULE_COSTS_MORE_THAN_THE_YEAR" in r["verdict"]]
    carry = [r["code"] for r in slow if "BATCHING_IS_A_CARRY_LOSS" in r["verdict"]]
    two_sided = [r["code"] for r in slow if "BATCHING_IS_TWO_SIDED" in r["verdict"]]
    if free:
        out.append("SCHEDULING_IS_ENOUGH_FOR:" + ",".join(free))
    if costly:
        out.append("SCHEDULING_IS_NOT_ENOUGH_FOR:" + ",".join(costly))
    if carry:
        out.append("A_CARRY_LOSS_IS_BUDGETABLE:" + ",".join(carry))
    if two_sided:
        out.append("A_TWO_SIDED_BATCH_IS_NOT_BUDGETABLE_FOR:" + ",".join(two_sided))
    return out


# --------------------------------------------------------------------------- render
def render_md(p):
    L = []
    A_ = L.append
    A_("# 现金腿货架：装不下，还是排不开？")
    A_("")
    A_("r2041 把五只现金工具放上容量尺子，量出 511380 是 1.13%（THIN）、511360 是 4.32%（THIN），"
       "然后在箭头那里停了。「THIN」对一个管钱的人只有两种处理：不买，或者分几天买。"
       "**第二种从来没有人给过价**——于是付得最多的那副货架（511360，比回购多 0.546 个百分点）"
       "看起来因为一个日历问题而用不了。这张面就是把第二种处理放到历史上去量。")
    A_("")
    A_("## 一句话")
    A_("")
    h = p["headline"]
    slow = h["shelves_needing_more_than_one_session"]
    if slow:
        det = []
        for s in slow:
            y = s.get("year_extra_cny")
            if y is None or y <= 0:
                det.append("%s 要 %d 天、95 分位折 %.0f 元，但它本来就比回购少赚 %.0f 元/年——"
                           "这一行的问题不是等，是不该买" % (s["code"], s["sessions"],
                                                                s["p95_batching_cny"], abs(y or 0)))
                continue
            ratio = s["p95_batching_cny"] / y
            det.append("%s 要 %d 天、95 分位折 %.0f 元 = 一年超额（%.0f 元）的 %.0f%%"
                       % (s["code"], s["sessions"], s["p95_batching_cny"], y, ratio * 100.0))
        A_("票面的 %s 元放到这张尺子上，三副货架装不进一个交易日：%s。"
           % (_yuan(h["ticket_cash_cny"]), "；".join(det)))
        A_("")
        A_("所以「最慢」和「最贵」在这副架子上是反着的：**需要五个交易日的 511360，分批只花掉它一年超额的 9%；"
           "只要两个交易日的 511380，一次分批就吃掉 2.4 年**。慢不贵，波动才贵——"
           "同一个「分天买」的动作，落在一条每天只走 0.9 个基点的曲线上，是排期；"
           "落在一条每天摆动几十个基点的曲线上，是下注。")
    A_("")
    A_("判词：**%s**" % " + ".join(p["verdict"]))
    A_("")
    A_("判词读法：`SCHEDULING_IS_ENOUGH_FOR:<码>` = 分天买得起；`SCHEDULING_IS_NOT_ENOUGH_FOR:<码>` = "
       "分天买就把一年超额吃掉了；`A_TWO_SIDED_BATCH_IS_NOT_BUDGETABLE_FOR:<码>` = 分批的结果会落在首日价的"
       "两边（不是只往贵里走），所以它那一笔省不了也躲不开。**三个判词要一起读**：一个「THIN」的货架同时可以是"
       "「排期够」和「双向」——前者说等得起，后者说不该把这件事当成零风险。")
    A_("")
    A_("## 尺子（先冻结，再看数）")
    A_("")
    A_("- 一天能买多少 = 坏日子成交额的 1%（直接读 r2041 的 `max_open_order_cny`，不重打）。")
    A_("- 需要几天 = 规模 ÷ 一天上限，向上取整。整手的零头不在本面重复计价——r2041 已经按整手定过价，"
       "本面只给「时间」定价。")
    A_("- 成交价 = 当日收盘的调整后价格指数：货币工具走 `consolidation_returns`（份额折算日记零收益），"
       "其余走翻转修复后的面板收盘价。")
    A_("- 每天买同样多的钱，所以成交均价是各日价格的**调和平均**，不是算术平均：同样的钱在便宜的日子买到更多份。"
       "用算术平均会把分批的成本说大（自检里有一条腿把这件事钉死：10/20 两天，调和均价 13.333 而不是 15）。")
    A_("- 偏移 = （窗口内调和均价 ÷ 首日价 − 1），单位 bp。正数 = 分批买贵了。面板上每一个重叠窗都算，"
       "所以公布的是真的发生过什么，不是正态近似。")
    A_("- 折成钱 = 规模 × 偏移；对照 r2041 同一格自己的「一年比回购多赚多少」，两句已发布的话相减。")
    A_("")
    A_("## 货架（按规模）")
    A_("")
    for r in p["rows"]:
        A_("### %s · %s（%s）" % (r["code"], r["label"], r["class"]))
        A_("")
        A_("一手 ￥%s · 坏日子成交 ￥%s 万 · p10 的 1%% 上限 ￥%s 万 · 一跳 = %s bp · "
           "价格序列 %s → %s（%d bar，%s）"
           % (_yuan(r["lot_value_cny"]), _m((r["bad_day_turnover_yuan"] or 0) / 1e4),
              _m((r["open_order_ceiling_cny"] or 0) / 1e4),
              _bp_abs(r.get("tick_size_bp")),
              r["index_first"], r["index_last"], r["index_bars"],
              r["index_source"]["source"]))
        A_("")
        A_("| 规模 | 档位 | 要几天 | 中位偏移 | 05 分位 | 95 分位 | 折钱(95) | 一年超额 | 95 分位÷超额 |")
        A_("|---|---|---|---|---|---|---|---|---|")
        for tier, t in r["tiers"].items():
            A_("| %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
                _yuan(int(tier)), t["class_of_tier"],
                t["sessions_to_fill"] if t["sessions_to_fill"] else "n/a",
                _bp(t.get("slip_median_bp")), _bp(t.get("slip_p05_bp")), _bp(t.get("slip_p95_bp")),
                _yuan(t.get("p95_cny")), _yuan(t.get("year_extra_cny")),
                _ratio_cell(t)))
        A_("")
        A_("判词（本行）：%s" % (" / ".join(r["verdict"]) if r["verdict"] else "—"))
        A_("")
    A_("## 这张面不决定什么")
    A_("")
    A_("- 不改票面：现金腿在生产里仍然是 GC001，改仓是月界动作。")
    A_("- 不测盘中冲击：上限是「别成为当天成交的一大部分」这条惯例，不是实测冲击模型。")
    A_("- 不重复整手：一手 11,419 元在 565,246 上留下 5,720 元零头（15.2bp）是 r2041 的读数，本面不覆盖。")
    A_("- 窗口 2020-07-16 .. %s，与所有现金腿面同一个窗口。" % p["evidence_cutoff"])
    A_("")
    A_("数据：ETF 面板（close/open/amount，含翻转修复）× r2041 的容量面；证据文件 `results/cash_shelf_build_out_plan.json`。")
    return "\n".join(L) + "\n"


def _yuan(x):
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return "—"
    return "{:,.0f}".format(float(x))


def _bp(x):
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return "—"
    return "{:+.2f}".format(float(x))


def _bp_abs(x):
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return "—"
    return "{:.2f}".format(float(x))


def _ratio_cell(t):
    """A shelf that pays less than repo has no "year's extra" to be spent by waiting --
    printing a percentage of a negative number would read as if the wait were the problem."""
    y = t.get("year_extra_cny")
    if y is None:
        return "—"
    if y <= 0:
        return "本行超额为负"
    r = t.get("p95_over_year_extra")
    if r is None:
        return "—"
    return "%.0f%%" % (abs(r) * 100.0)


def _m(x):
    if x is None:
        return "—"
    return "{:,.0f}".format(float(x))


# --------------------------------------------------------------------------- check
def classify(errs, moved, n_rows=0):
    """(rc, headline) for a re-derivation: a moved panel is staleness, not a defect.

    r1934: the chain pays for a rebuild only when the check's own words say STALE, so
    the two causes must not share one sentence.  A bar that arrived after this face was
    priced is the panel's clock (the window grew by one and every tier's window count
    with it); a reading that disagrees on an unchanged tape is this script's arithmetic.
    """
    if moved:
        return 3, ("STALE: panel tail moved under this face (%d reading(s)) -> re-run"
                   % len(moved))
    if errs:
        return 1, "CHECK FAILED (%d)" % len(errs)
    return 0, "CHECK OK  %d rows re-derived from the panel and r2041" % n_rows


def check(verbose=True):
    """Re-derive the published face from the upstream face and the panel."""
    errs = []
    moved = []
    if not os.path.exists(OUT_JSON):
        print("MISSING FACE: %s" % OUT_JSON)
        return 3
    with io.open(OUT_JSON, encoding="utf-8") as f:
        pub = json.load(f)
    if not os.path.exists(R2041_JSON):
        print("STALE: upstream face missing %s" % R2041_JSON)
        return 3
    up_sha = _sha(R2041_JSON)
    if up_sha != pub["upstream"]["sha256"]:
        print("STALE FACE_UPSTREAM_MOVED: r2041 sha %s -> %s" % (
            pub["upstream"]["sha256"][:12], up_sha[:12]))
        return 3

    close_all, open_all, _amt, _f = E.build_panel()
    close_all, _o, _n = A.repair_flips(close_all, open_all)
    with io.open(R2041_JSON, encoding="utf-8") as f:
        up = json.load(f)
    for r in pub["rows"]:
        code = r["code"]
        prow = next(x for x in up["rows"] if x["code"] == code)
        idx, _src = adjusted_index(code, r["class"], close_all)
        idx = idx[idx.index >= pd.Timestamp(S.START)].dropna()
        vals = idx.values
        if int(len(vals)) != r["index_bars"]:
            moved.append("%s index_bars %d != published %d" % (code, len(vals), r["index_bars"]))
            continue
        for tier, t in r["tiers"].items():
            days = sessions_to_fill(int(tier), prow.get("max_open_order_cny"))
            if days != t["sessions_to_fill"]:
                errs.append("%s@%s sessions %s != published %s"
                            % (code, tier, days, t["sessions_to_fill"]))
                continue
            if days is None:
                continue
            slip = batch_slippage_bp(vals, days)
            if int(len(slip)) != t["windows"]:
                moved.append("%s@%s windows %d != published %d"
                             % (code, tier, len(slip), t["windows"]))
                continue
            if not len(slip):
                continue
            for key, val in (("slip_median_bp", float(np.median(slip))),
                             ("slip_p05_bp", float(np.percentile(slip, P05))),
                             ("slip_p95_bp", float(np.percentile(slip, P95)))):
                if abs(round(val, 4) - t[key]) > 5e-4:
                    errs.append("%s@%s %s %.4f != %.4f" % (code, tier, key, val, t[key]))
    rc, headline = classify(errs, moved, len(pub["rows"]))
    print(headline)
    if rc:
        for e in (moved or errs)[:20]:
            print("  - " + e)
        return rc
    return 0


# --------------------------------------------------------------------------- selftest
def selftest():
    errs = []
    ran = [0]

    def chk(ok, msg):
        ran[0] += 1
        if not ok:
            errs.append(msg)

    # 1. sessions_to_fill arithmetic
    chk(sessions_to_fill(565246, 130856) == 5, "565246/130856 must be 5 sessions")
    chk(sessions_to_fill(565246, 500750) == 2, "565246/500750 must be 2 sessions")
    chk(sessions_to_fill(250000, 500750) == 1, "a tier under the ceiling is one session")
    chk(sessions_to_fill(1000, 0) is None, "a zero ceiling has no schedule")
    chk(sessions_to_fill(1000, float("nan")) is None, "a NaN ceiling has no schedule")
    chk(sessions_to_fill(10, 10) == 1, "exactly at the ceiling is one session")

    # 2. harmonic mean, not arithmetic
    chk(abs(harmonic_mean([10.0, 20.0]) - 13.333333333) < 1e-6,
        "two-day 10/20 must average to 13.3333 (harmonic), not 15 (arithmetic)")
    chk(abs(harmonic_mean([5.0]) - 5.0) < 1e-12, "one session is its own mean")
    chk(not np.isfinite(harmonic_mean([10.0, 0.0])), "a zero price must be refused, not averaged")
    chk(not np.isfinite(harmonic_mean([])), "an empty window is NaN, never 0")

    # 3. one session has exactly zero slippage on any tape
    chk(float(np.max(np.abs(batch_slippage_bp([1.0, 1.3, 0.7, 2.0], 1)))) == 0.0,
        "days=1 must give zero slippage on any tape")

    # 4. a monotonically rising tape can only make batching pay up
    rising = [1.0, 1.001, 1.002, 1.003, 1.004]
    s2 = batch_slippage_bp(rising, 3)
    chk(len(s2) == 3, "five prices with a 3-day window give 3 windows")
    chk(bool(np.all(s2 > 0)), "on a rising tape every window must be positive")
    chk(abs(s2[0] - ((harmonic_mean(rising[:3]) / rising[0] - 1) * 1e4)) < 1e-9,
        "the first window must be the harmonic mean against its own first price")

    # 5. a falling tape can make batching pay less (the sign must not be forced)
    falling = [1.004, 1.003, 1.002, 1.001, 1.0]
    s3 = batch_slippage_bp(falling, 3)
    chk(bool(np.all(s3 < 0)), "on a falling tape batching must come out cheaper")

    # 6. windows never exceed the tape
    chk(len(batch_slippage_bp([1.0, 1.1, 1.2], 3)) == 1, "n prices with n-day window = 1 window")
    chk(len(batch_slippage_bp([1.0, 1.1], 3)) == 0, "too few prices = no windows")

    # 7. the bands still agree with the capacity face it imports
    chk(abs(S.LOT_UNITS - 100) == 0, "lot must still be 100 units")
    cls, part = S.RC.part_class(400000.0, 50075041.0)
    chk(cls == "OPEN" and part <= S.RC.PART_OK, "under 1% of the bad day must still be OPEN")
    chk(abs(S.RC.PART_OK - 0.01) < 1e-12 and abs(S.RC.PART_THIN - 0.10) < 1e-12,
        "the imported bands must still be 1%/10%")
    # exactly at 1% is a rounding coin-flip; the face must never call it BLOCKED
    cls2, _p2 = S.RC.part_class(500750.0, 50075041.0)
    chk(cls2 in ("OPEN", "THIN"), "a hair over 1% must never read as BLOCKED")

    # 8. verdict logic: a slow shelf whose tail is under the year's extra schedules fine
    def row(free=True):
        return {"tiers": {"250000": {"sessions_to_fill": 5, "windows": 10,
                                     "p95_cny": 100.0 if free else 5000.0,
                                     "year_extra_cny": 3000.0,
                                     "slip_never_negative": True,
                                     "slip_p05_bp": 0.4, "slip_p95_bp": 3.0},
                          "1000000": {"sessions_to_fill": 5, "windows": 10,
                                      "p95_cny": 300.0 if free else 9000.0,
                                      "year_extra_cny": 6000.0,
                                      "slip_never_negative": True,
                                      "slip_p05_bp": 0.7, "slip_p95_bp": 5.0}}}
    v = verdicts_for(row(True)["tiers"], [250000, 1000000], 114.189)
    chk("SCHEDULING_REPLACES_CAPACITY" in v and "BATCHING_IS_A_CARRY_LOSS" in v,
        "a cheap tail must read as scheduling, and a non-negative tape as a carry loss")
    v2 = verdicts_for(row(False)["tiers"], [250000, 1000000], 114.189)
    chk("THE_SCHEDULE_COSTS_MORE_THAN_THE_YEAR" in v2, "an expensive tail must read as a wall")

    # 9. a one-session shelf says so and prints no batching verdict
    one = {"tiers": {str(t): {"sessions_to_fill": 1, "windows": 100} for t in (250000, 1000000)}}
    v3 = verdicts_for(one["tiers"], [250000, 1000000], 114.189)
    chk(v3 == ["ONE_SESSION_IS_ENOUGH"], "ONE_SESSION_IS_ENOUGH must stand alone, got %r" % (v3,))

    # 10. the overall verdict names both sides when both exist
    r1 = dict(row(True), code="AAA", verdict=verdicts_for(row(True)["tiers"], [250000, 1000000], 114.189))
    r2 = dict(row(False), code="BBB", verdict=verdicts_for(row(False)["tiers"], [250000, 1000000], 114.189))
    ov = verdicts_overall([r1, r2], "250000")
    chk(any(x.startswith("SCHEDULING_IS_ENOUGH_FOR:AAA") for x in ov), "AAA must be named as schedulable")
    chk(any(x.startswith("SCHEDULING_IS_NOT_ENOUGH_FOR:BBB") for x in ov), "BBB must be named as a wall")

    # 11. a two-sided batch is named as such, and does not pretend to be a carry loss
    risk = {"tiers": {"250000": {"sessions_to_fill": 3, "windows": 10, "p95_cny": 100.0,
                                 "year_extra_cny": 3000.0, "slip_never_negative": False,
                                 "slip_p05_bp": -30.0, "slip_p95_bp": 30.0}}}
    v_r = verdicts_for(risk["tiers"], [250000], 114.189)
    chk("BATCHING_IS_TWO_SIDED" in v_r and "BATCHING_IS_A_CARRY_LOSS" not in v_r,
        "a window that can come out cheaper must be named two-sided, got %r" % (v_r,))
    chk("SCHEDULING_REPLACES_CAPACITY" in v_r,
        "a 100-yuan tail against a 3,000-yuan year is still schedulable")

    # 12. a month-long schedule is flagged
    long_ = {"tiers": {"250000": {"sessions_to_fill": 22, "windows": 5, "p95_cny": 0.0,
                                  "year_extra_cny": 1000.0, "slip_never_negative": True,
                                  "slip_p05_bp": 0.0, "slip_p95_bp": 0.0}}}
    chk("FILLS_TAKE_LONGER_THAN_A_MONTH" in verdicts_for(long_["tiers"], [250000], 114.189),
        "22 sessions must be flagged as longer than a month")

    # 13. the tick is printed as a reading, and the two verdicts stay orthogonal:
    #     the same -0.79bp tail is "two-sided" on a 114.19 tape and also on an 11.59 tape --
    #     affordability is the SCHEDULING verdict's job, never a price-magnitude guess
    tick_bp = TICK_CNY / 114.189 * 1e4
    chk(0.08 < tick_bp < 0.10, "a tick on a 114.19 price is about 0.0876bp, got %.4f" % tick_bp)
    inside = {"tiers": {"250000": {"sessions_to_fill": 5, "windows": 10, "p95_cny": 264.5,
                                   "year_extra_cny": 3088.2, "slip_never_negative": False,
                                   "slip_p05_bp": -0.79, "slip_p95_bp": 4.68}}}
    chk(verdicts_for(inside["tiers"], [250000], 114.189) ==
        ["SCHEDULING_REPLACES_CAPACITY", "BATCHING_IS_TWO_SIDED"],
        "the short-financing row must read schedulable AND two-sided, got %r"
        % (verdicts_for(inside["tiers"], [250000], 114.189),))

    # 14. a shelf that already pays less than repo is not judged on "a year's extra"
    negative = {"tiers": {"250000": {"sessions_to_fill": 3, "windows": 10, "p95_cny": 3000.0,
                                     "year_extra_cny": -2041.0, "slip_never_negative": False,
                                     "slip_p05_bp": -56.3, "slip_p95_bp": 54.7}}}
    v4 = verdicts_for(negative["tiers"], [250000], 10.956)
    chk(not any(x.startswith("SCHEDULING_") or x.startswith("THE_SCHEDULE") for x in v4),
        "a negative year's extra must not be spent by waiting, got %r" % (v4,))
    chk("BATCHING_IS_TWO_SIDED" in v4, "a -56bp tail is two-sided regardless")

    # 15. the page must never print a percentage of a negative year's extra
    chk(_ratio_cell({"year_extra_cny": -2041.0, "p95_over_year_extra": -1.51}) == "本行超额为负",
        "a negative year's extra must not be turned into a percentage")
    chk(_ratio_cell({"year_extra_cny": 1166.94, "p95_over_year_extra": 2.388}) == "239%",
        "a positive ratio must print as a percentage of the year's extra")

    # 16. r1934: the two causes of a red must not share one sentence.  The chain only
    #     pays for a rebuild when the check says STALE, so a helper that folded "a bar
    #     arrived" into "CHECK FAILED" would leave this face permanently red on every
    #     new session (and a permanently red shell trains the reader to ignore it).
    _rc, _head = classify([], ["511360@250000 windows 1540 != published 1539"], 5)
    chk(_rc == 3 and _head.startswith("STALE"),
        "a moved panel must read STALE rc3, got %r" % (_head,))
    _rc, _head = classify(["511360@250000 slip_median_bp 1.0 != 1.1"], [], 5)
    chk(_rc == 1 and "STALE" not in _head and "CHECK FAILED" in _head,
        "a disagreeing reading on an unchanged tape is a defect, not staleness, got %r"
        % (_head,))
    _rc, _head = classify([], [], 5)
    chk(_rc == 0 and _head.startswith("CHECK OK"), "a clean re-derivation reads CHECK OK")
    _rc, _head = classify(["defect"], ["moved"], 5)
    chk(_rc == 3, "the panel's clock wins when both are present -- the reading is not comparable")

    if errs:
        print("SELFTEST FAILED (%d of %d legs)" % (len(errs), ran[0]))
        for e in errs:
            print("  - " + e)
        return 1
    print("SELFTEST OK  %d legs" % ran[0])
    return 0


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    if "--selftest" in sys.argv:
        return selftest()
    if "--check" in sys.argv:
        return check()
    if not args or args[0] == "run":
        return build(write=True)
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())

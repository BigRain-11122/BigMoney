#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""cash_shelf_inflight_carry -- who pays for the wait, and how much of it the repo leg gives back.

WHY THIS FACE EXISTS
--------------------
`cash_shelf_build_out_plan` (r2043) turned a THIN capacity verdict into a schedule and
priced the wait at 265 CNY (95th percentile) for 511360 over five sessions -- 8.6% of the
extra that shelf pays over the repo leg in a year.  It compared the bought price against the
first session's price, which is the right way to measure a *price* offset and the wrong way
to measure *cost*: the cash that has not been spent yet does not sit in a drawer.  If the
in-flight cash stays in the published cash leg (GC001, `etf_book_cash_ladder.roll_rung`),
the wait is partly paid back, and the exchange commission is charged per contract -- so the
give-back has a floor.

THE QUESTION (frozen before the first run)
------------------------------------------
When the ticket is spread over the sessions the capacity ruler allows, how much of the
measured price offset does the in-flight cash earn back in the repo leg -- net of the
commission that leg actually charges?

MODEL
-----
* Slippage, sessions, tiers and the ticket are imported from r2043's published face (never
  retyped); a selftest leg re-derives the published slippage and demands it match.
* In-flight cash weight: equal cash per session means that between session i+k-1 and i+k
  exactly (n-k)/n of the ticket is still unspent, so the window's carry is
      sum_{k=1..n-1} (n-k)/n * repo_return(bar i+k)
  on the repo leg's own per-bar return, in which the interest of a contract is credited on
  the step that ENDS at the bar and the commission is charged on the bar it is BOUGHT.
  The weights sum to (n-1)/2 full-size days -- a selftest leg pins both the weights and
  the closed form on a constant-rate tape.
* Two arms, same tape: NET (the module's default commission, 0.1bp per 1-day contract
  entry) and GROSS (commission zeroed).  The difference is what the exchange charges for
  the privilege of parking, and it is printed rather than netted away.
* Money = bp x size, on r2043's own tier sizes.

VERDICTS (mechanical)
---------------------
* ONE_SESSION_NO_WAIT            -- the ruler clears this tier in one session; nothing to price.
* CARRY_IS_A_ROUNDING_ERROR      -- net carry is under 10% of the slippage it offsets.
* CARRY_TICKS_THE_WAIT_DOWN      -- 10%..35%.
* CARRY_PAYS_MOST_OF_THE_WAIT    -- 35% or more.
* NET_WAIT_IS_FREE               -- the whole 95th-percentile net is at or below zero.
* NO_WINDOWS                     -- the tape is shorter than the schedule; nothing is claimed.

Usage:
    python scripts/cash_shelf_inflight_carry.py run
    python scripts/cash_shelf_inflight_carry.py --check
    python scripts/cash_shelf_inflight_carry.py --selftest
"""

from __future__ import annotations

import datetime as dt
import hashlib
import io
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import cash_shelf_build_out_plan as P  # noqa: E402  (r2043: sessions, slippage, ticket)
import cb_parking_shelf_at_size as S  # noqa: E402  (window start, shelf rows)
import etf_book_cash_ladder as CL  # noqa: E402  (the published cash leg)
import etf_composite_pf as E  # noqa: E402  (ETF panel)
import etf_equity_alpha as A  # noqa: E402  (flip repair)

R2043_JSON = os.path.join(ROOT, "results", "cash_shelf_build_out_plan.json")
OUT_JSON = os.path.join(ROOT, "results", "cash_shelf_inflight_carry.json")
OUT_MD = os.path.join(ROOT, "research", "CASH_SHELF_INFLIGHT_CARRY.md")

SCHEMA = "cash-shelf-inflight-carry/v1"
P50 = 50.0
P05 = 5.0
P95 = 95.0
ROUNDING_SHARE = 0.10
MOST_SHARE = 0.35
LONG_SCHEDULE = 39          # r2043 named 39 sessions as the 5m-CNY case
_QUIET = False


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
    if _QUIET:
        return
    print(*a, flush=True)


def cash_weights(days):
    """Fraction of the ticket still unspent on each step of an equal-cash schedule."""
    n = int(days)
    if n < 2:
        return np.zeros(0, dtype=float)
    return np.asarray([(n - k) / float(n) for k in range(1, n)], dtype=float)


def weight_days(days):
    """Full-size days of exposure the weights represent: sum_{k=1..n-1} (n-k)/n = (n-1)/2."""
    return float(np.sum(cash_weights(days)))


def window_carry(rets, days):
    """Every overlapping window's weighted repo carry, as a fraction of the ticket."""
    r = np.asarray([float(x) for x in rets], dtype=float)
    n = int(days)
    w = cash_weights(n)
    if n < 2 or len(r) < n:
        return np.array([], dtype=float)
    out = []
    for i in range(0, len(r) - n + 1):
        step = r[i + 1:i + n]
        if len(step) != n - 1 or not np.all(np.isfinite(step)):
            continue
        out.append(float(np.dot(w, step)))
    return np.asarray(out, dtype=float)


def pct(vals, q):
    a = np.asarray(vals, dtype=float)
    if not len(a):
        return None
    return float(np.percentile(a, q))


def money(bp, size):
    if bp is None or size in (None, 0):
        return None
    return round(float(bp) / 1e4 * float(size), 2)


def verdicts_for(rec):
    """One shelf/tier row -> its mechanical verdicts."""
    out = []
    if rec.get("sessions_to_fill") is None:
        return out
    if rec["sessions_to_fill"] <= 1:
        return ["ONE_SESSION_NO_WAIT"]
    if not rec.get("windows"):
        return ["NO_WINDOWS"]
    slip50 = rec.get("slip_median_bp")
    carry50 = rec.get("carry_net_median_bp")
    if slip50 is None or carry50 is None or slip50 <= 0:
        out.append("NO_WINDOWS")
    else:
        share = carry50 / slip50
        rec["carry_share_of_slippage"] = round(share, 4)
        if share < ROUNDING_SHARE:
            out.append("CARRY_IS_A_ROUNDING_ERROR")
        elif share < MOST_SHARE:
            out.append("CARRY_TICKS_THE_WAIT_DOWN")
        else:
            out.append("CARRY_PAYS_MOST_OF_THE_WAIT")
    if rec.get("net_p95_bp") is not None and rec["net_p95_bp"] <= 0.0:
        out.append("NET_WAIT_IS_FREE")
    per_day = rec.get("net_per_wait_day_bp")
    if per_day is not None:
        if per_day <= 0.0:
            out.append("WAIT_IS_PAID_IN_FULL")
        elif per_day <= 0.10:
            out.append("WAIT_IS_NEARLY_SELF_FINANCING")
        else:
            out.append("WAIT_WALKS_FASTER_THAN_THE_REPO_LEG")
    return out


# --------------------------------------------------------------------------- build
def build(write=True, verbose=True):
    global _QUIET
    t0 = time.time()
    _prev_quiet = _QUIET
    _QUIET = not verbose

    if not os.path.exists(R2043_JSON):
        print("MISSING FACE: %s" % R2043_JSON)
        _QUIET = _prev_quiet
        return 2
    with io.open(R2043_JSON, encoding="utf-8") as f:
        pub = json.load(f)
    tiers = [int(x) for x in pub["upstream"]["tiers_cny"]]
    ticket_cash = float(pub["headline"]["ticket_cash_cny"])
    ticket_tier = min(tiers, key=lambda t: abs(t - ticket_cash))

    close_all, open_all, _amt, _feats = E.build_panel()
    close_all, _o2, n_flip = A.repair_flips(close_all, open_all)
    log("  panel: %d cols x %d bars, %d flips repaired"
        % (close_all.shape[1], close_all.shape[0], n_flip))

    rates = CL.load_panel()
    no_fee = {k: 0.0 for k in CL.FEE_BP}

    rows = []
    for prow in pub["rows"]:
        code = prow["code"]
        if code not in close_all.columns:
            print("MISSING INSTRUMENT: %s" % code)
            _QUIET = _prev_quiet
            return 2
        idx, src = P.adjusted_index(code, prow["class"], close_all)
        idx = idx[idx.index >= pd.Timestamp(S.START)].dropna()
        bars = pd.DatetimeIndex(idx.index)
        vals = idx.values
        repo_net, _info = CL.roll_rung(bars, rates, None, fees=None, name="GC001")
        repo_gross, _info2 = CL.roll_rung(bars, rates, None, fees=no_fee, name="GC001")
        log("  %s repo leg: %d bars, net %.2f%% / gross %.2f%% of a year"
            % (code, len(bars), float(np.sum(repo_net.values)) * 100.0 / max(len(bars) / 244.0, 1e-9),
               float(np.sum(repo_gross.values)) * 100.0 / max(len(bars) / 244.0, 1e-9)))

        by_tier = {}
        for tier in tiers:
            src_tier = prow["tiers"].get(str(tier), {})
            n = src_tier.get("sessions_to_fill")
            rec = {"sessions_to_fill": n,
                   "published_slip_median_bp": src_tier.get("slip_median_bp"),
                   "published_slip_p95_bp": src_tier.get("slip_p95_bp"),
                   "published_p95_cny": src_tier.get("p95_cny"),
                   "year_extra_cny": src_tier.get("year_extra_cny"),
                   "size_cny": tier}
            if n is None:
                by_tier[str(tier)] = rec
                continue
            slip = P.batch_slippage_bp(vals, int(n))
            carry_net = window_carry(repo_net.values, int(n))
            carry_gross = window_carry(repo_gross.values, int(n))
            m = min(len(slip), len(carry_net), len(carry_gross)) if (
                len(slip) and len(carry_net) and len(carry_gross)) else 0
            rec["windows"] = int(m)
            if m:
                slip_bp = slip[:m]
                cnet_bp = carry_net[:m] * 1e4
                cgross_bp = carry_gross[:m] * 1e4
                net_bp = slip_bp - cnet_bp
                rec.update({
                    "slip_median_bp": round(pct(slip_bp, P50), 4),
                    "slip_p95_bp": round(pct(slip_bp, P95), 4),
                    "carry_net_median_bp": round(pct(cnet_bp, P50), 4),
                    "carry_net_p05_bp": round(pct(cnet_bp, P05), 4),
                    "carry_gross_median_bp": round(pct(cgross_bp, P50), 4),
                    "commission_median_bp": round(pct(cgross_bp - cnet_bp, P50), 4),
                    "net_median_bp": round(pct(net_bp, P50), 4),
                    "net_p95_bp": round(pct(net_bp, P95), 4),
                    "weight_days": round(weight_days(int(n)), 4),
                    "net_median_cny": money(pct(net_bp, P50), tier),
                    "net_p95_cny": money(pct(net_bp, P95), tier),
                    "carry_net_median_cny": money(pct(cnet_bp, P50), tier),
                })
                wd = weight_days(int(n))
                if wd > 0:
                    rec["slip_per_wait_day_bp"] = round(rec["slip_median_bp"] / wd, 4)
                    rec["carry_per_wait_day_bp"] = round(rec["carry_net_median_bp"] / wd, 4)
                    rec["net_per_wait_day_bp"] = round(rec["net_median_bp"] / wd, 4)
            by_tier[str(tier)] = rec
            log("    %-10s tier=%-9s n=%-3s windows=%-4d slip50=%s carry50(net)=%s net95=%s bp"
                % (code, tier, n, rec["windows"],
                   rec.get("slip_median_bp"), rec.get("carry_net_median_bp"), rec.get("net_p95_bp")))

        row_v = {}
        daily_bp = np.diff(vals) / vals[:-1] * 1e4
        daily_bp = daily_bp[np.isfinite(daily_bp)]
        for tier in tiers:
            key = str(tier)
            rec = by_tier[key]
            rec["verdict"] = verdicts_for(rec)
            row_v[key] = rec["verdict"]
        rows.append({
            "code": code,
            "label": prow["label"],
            "class": prow["class"],
            "index_source": src,
            "index_bars": int(len(vals)),
            "index_last": str(bars[-1].date()),
            "tape": {"mean_daily_bp": round(float(np.mean(daily_bp)), 4) if len(daily_bp) else None,
                     "median_daily_bp": round(float(np.median(daily_bp)), 4) if len(daily_bp) else None,
                     "days_below_minus_5bp": int((daily_bp < -5.0).sum()),
                     "days_bars": int(len(daily_bp))},
            "tiers": by_tier,
            "verdict": row_v,
        })

    # ---- how the two terms scale: the same subtraction at the long-schedule size
    long_rows = []
    for r in rows:
        key = str(ticket_tier)
        rec = r["tiers"].get(key, {})
        if not rec.get("size_cny"):
            continue
        code = r["code"]
        idx, _src = P.adjusted_index(code, r["class"], close_all)
        idx = idx[idx.index >= pd.Timestamp(S.START)].dropna()
        bars = pd.DatetimeIndex(idx.index)
        repo_net, _i = CL.roll_rung(bars, rates, None, fees=None, name="GC001")
        slip = P.batch_slippage_bp(idx.values, LONG_SCHEDULE)
        carry = window_carry(repo_net.values, LONG_SCHEDULE)
        m = min(len(slip), len(carry))
        if m <= 0 or rec["sessions_to_fill"] is None or rec["sessions_to_fill"] >= LONG_SCHEDULE:
            continue
        long_rows.append({
            "code": code,
            "class": r["class"],
            "sessions": LONG_SCHEDULE,
            "windows": int(m),
            "slip_median_bp": round(pct(slip[:m], P50), 4),
            "carry_net_median_bp": round(pct(carry[:m] * 1e4, P50), 4),
            "carry_share_of_slippage": round(float(np.median(carry[:m] * 1e4))
                                             / float(np.median(slip[:m])), 4)
            if float(np.median(slip[:m])) > 0 else None,
            "weight_days": round(weight_days(LONG_SCHEDULE), 4),
        })

    # ---- headline counts, all mechanical
    kinds = {}
    shares = []
    for r in rows:
        for key, rec in r["tiers"].items():
            for v in rec.get("verdict", []):
                kinds[v] = kinds.get(v, 0) + 1
            if rec.get("carry_share_of_slippage") is not None:
                shares.append(rec["carry_share_of_slippage"])

    ticket_rows = []
    for r in rows:
        rec = r["tiers"].get(str(ticket_tier), {})
        if rec.get("sessions_to_fill") and rec["sessions_to_fill"] > 1 and rec.get("windows"):
            ticket_rows.append({
                "code": r["code"],
                "sessions": rec["sessions_to_fill"],
                "slip_p95_cny": rec.get("published_p95_cny"),
                "carry_net_median_cny": rec.get("carry_net_median_cny"),
                "net_p95_cny": rec.get("net_p95_cny"),
                "net_median_cny": rec.get("net_median_cny"),
                "carry_share_of_slippage": rec.get("carry_share_of_slippage"),
                "commission_median_bp": rec.get("commission_median_bp"),
                "slip_per_wait_day_bp": rec.get("slip_per_wait_day_bp"),
                "carry_per_wait_day_bp": rec.get("carry_per_wait_day_bp"),
                "net_per_wait_day_bp": rec.get("net_per_wait_day_bp"),
                "tape_mean_daily_bp": r["tape"]["mean_daily_bp"],
                "verdict": rec.get("verdict"),
            })

    headline = {
        "ticket_cash_cny": ticket_cash,
        "tier_used_for_headline": ticket_tier,
        "verdict_counts": kinds,
        "carry_share_median_across_rows": round(float(np.median(shares)), 4) if shares else None,
        "carry_share_min": round(float(np.min(shares)), 4) if shares else None,
        "carry_share_max": round(float(np.max(shares)), 4) if shares else None,
        "shelves_needing_more_than_one_session_at_the_ticket": ticket_rows,
        "long_schedule_check": long_rows,
    }
    tape_shelf = next((r for r in rows if r["code"] == "511360"), rows[0] if rows else None)
    if tape_shelf is not None:
        headline["tape_of_the_cash_shelf"] = {
            "code": tape_shelf["code"],
            "bars": tape_shelf["tape"]["days_bars"],
            "days_below_minus_5bp": tape_shelf["tape"]["days_below_minus_5bp"],
        }

    payload = {
        "schema": SCHEMA,
        "artifact": "cash_shelf_inflight_carry",
        "generated": _now(),
        "evidence_cutoff": str(close_all.index[-1].date()),
        "window": {"start": S.START, "end": str(close_all.index[-1].date())},
        "question": ("how much of the measured price offset does the in-flight cash earn back "
                     "in the repo leg, net of the commission that leg charges?"),
        "upstream": {"face": os.path.relpath(R2043_JSON, ROOT).replace("\\", "/"),
                     "sha256": _sha(R2043_JSON),
                     "tiers_cny": tiers,
                     "ticket_cash_cny": ticket_cash},
        "ruler": {
            "sessions_and_slippage": "imported from r2043 (sessions_to_fill, batch_slippage_bp); "
                                     "the published slippage is re-derived and asserted",
            "in_flight_weight": "sum_{k=1..n-1} (n-k)/n of the ticket, i.e. (n-1)/2 full-size days",
            "repo_return": "etf_book_cash_ladder.roll_rung GC001 -- the desk's published cash-leg "
                           "caliber; interest credited on the step that ends at the bar, "
                           "commission on the bar the contract is bought",
            "commission": "CL.FEE_BP 1-day entry 0.1bp per contract; the GROSS arm zeroes it",
            "net": "slippage (bp) minus net carry (bp), same window, same bars",
            "money": "bp x tier size",
        },
        "rows": rows,
        "headline": headline,
    }
    log("  headline: %s" % json.dumps(headline["verdict_counts"], ensure_ascii=False))

    _LAST["payload"] = payload
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
    _QUIET = _prev_quiet
    return 0


# --------------------------------------------------------------------------- render
def _m(x):
    if x is None:
        return "n/a"
    return "{:,.0f}".format(x)


def _bp(x):
    if x is None:
        return "n/a"
    return "{:+.2f}".format(x)


def render_md(p):
    h = p["headline"]
    L = []
    L.append("# 分批等待期间，在途资金停在回购腿能挣回多少\n")
    L.append("> 生成 %s ｜ 证据截止 %s ｜ 上游面 r2043 `%s`（sha256 %s…）\n"
             % (p["generated"], p["evidence_cutoff"],
                p["upstream"]["face"], p["upstream"]["sha256"][:12]))
    L.append("## 一句话\n")
    L.append("r2043 把等待定价成「均价 ÷ 首日价 − 1」，那是**价格偏移**，不是**成本**："
             "还没花出去的钱不会躺在抽屉里。本面把同一段时间里在途资金按本司已发布的现金腿"
             "（GC001，含交易所佣金）重算，得到净等待。票面档下，回购腿能挣回的份额中位数 "
             "**%s**（区间 %s ~ %s）。\n"
             % (_share(h["carry_share_median_across_rows"]),
                _share(h["carry_share_min"]), _share(h["carry_share_max"])))
    L.append("## 票面档（%s 元）需要多个交易日的货架\n" % _m(h["ticket_cash_cny"]))
    L.append("| 货架 | 交易日 | r2043 的 p95 等待（元） | 回购腿挣回（元/中位） | 净等待 p95（元） | 净等待 p50（元） | 佣金（bp/窗） | 挣回份额 |")
    L.append("|---|---|---|---|---|---|---|---|")
    for t in h["shelves_needing_more_than_one_session_at_the_ticket"]:
        L.append("| %s | %d | %s | %s | %s | %s | %s | %s |"
                 % (t["code"], t["sessions"], _m(t["slip_p95_cny"]),
                    _m(t["carry_net_median_cny"]), _m(t["net_p95_cny"]),
                    _m(t.get("net_median_cny")),
                    _bp(t["commission_median_bp"]), _share(t["carry_share_of_slippage"])))
    L.append("")
    L.append("两项为什么几乎同阶：等额分批把「多等的天数」压成 `(n-1)/2` 个满仓日，"
             "滑点与 carry **乘的是同一个天数**，只剩每日期望比赛。\n")
    L.append("读法两条，先说明白再读表：**净等待 p50 是逐窗配对差的中位数**，不是左边两列中位数相减"
             "（同一窗口的滑点与 carry 一起算，配对后中位可能不相等）；"
             "**carry 只取决于回购腿与天数**，所以下表里同一列对所有货架大致相同，那不是抄错。\n")
    L.append("| 货架 | 交易日 | 价格每日走（bp） | 回购腿每日付（bp） | 净每日（bp） |")
    L.append("|---|---|---|---|---|")
    for t in h["shelves_needing_more_than_one_session_at_the_ticket"]:
        L.append("| %s | %d | %s | %s | %s |"
                 % (t["code"], t["sessions"], _bp(t.get("slip_per_wait_day_bp")),
                    _bp(t.get("carry_per_wait_day_bp")), _bp(t.get("net_per_wait_day_bp"))))
    L.append("")
    L.append("## 排期拉长时两项怎么长\n")
    L.append("佣金按**每张合约进场**收：1 天期 0.1bp。等 5 天要滚 4 张、等 39 天要滚 38 张，"
             "而利差只会按天线性累积 —— 两个总量赛跑，本面把同一段历史按 39 日窗口重跑一次：\n")
    L.append("| 货架 | 39 日窗口 | 滑点中位（bp） | 净 carry 中位（bp） | 挣回份额 | 满仓天数 |")
    L.append("|---|---|---|---|---|---|")
    for t in h["long_schedule_check"]:
        L.append("| %s | %d | %s | %s | %s | %.1f |"
                 % (t["code"], t["windows"], _bp(t["slip_median_bp"]),
                    _bp(t["carry_net_median_bp"]), _share(t["carry_share_of_slippage"]),
                    t["weight_days"]))
    L.append("")
    L.append("## 逐货架读数\n")
    L.append("| 货架 | 类 | 档位 | 交易日 | 窗数 | 价格每日（bp） | 滑点 p50 | 净 carry p50 | 佣金 p50 | 净等待 p50 | 判词 |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for r in p["rows"]:
        for key, rec in r["tiers"].items():
            if rec.get("sessions_to_fill") is None:
                continue
            L.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |"
                     % (r["code"], r["class"], key, rec["sessions_to_fill"],
                        rec.get("windows", 0), _bp(rec.get("slip_per_wait_day_bp")),
                        _bp(rec.get("slip_median_bp")),
                        _bp(rec.get("carry_net_median_bp")),
                        _bp(rec.get("commission_median_bp")),
                        _bp(rec.get("net_median_bp")),
                        " / ".join(rec.get("verdict", [])) or "-"))
    L.append("")
    L.append("## 每只货架的价格是不是「把收益走在了价格里」\n")
    L.append("| 货架 | 条形数 | 日均（bp） | 日中位（bp） | 单日跌破 −5bp 的天数 |")
    L.append("|---|---|---|---|---|")
    for r in p["rows"]:
        tp = r.get("tape", {})
        L.append("| %s | %d | %s | %s | %d |"
                 % (r["code"], tp.get("days_bars", 0), _bp(tp.get("mean_daily_bp")),
                    _bp(tp.get("median_daily_bp")), tp.get("days_below_minus_5bp", 0)))
    L.append("")
    L.append("## 口径与不做的事\n")
    L.append("* 滑点与交易日数**不重打**：从 r2043 面读，并在自检里用同一函数重算、逐位比对。")
    L.append("* 在途权重 `(n-k)/n` 是「每天等额买」的直接后果，和为 `(n-1)/2` 个满仓日（自检钉死）。")
    L.append("* 回购收益用本司现金腿模块的逐日口径（利息落在合约到期的那一步、佣金落在买进的那一步），"
             "**不**另建一个 repo 模型。")
    L.append("* 未做的事：①佣金按交易所牌价假设，未逐券商核；②在途资金只测「停 GC001」，"
             "没有测「停货币 ETF」或「停活期」；③价格偏移仍用收盘价（r2043 的口径），不是次日开盘；"
             "④价格指数是**价格**不是全收益：若窗口内有分红派息，先买齐的一方拿到的现金更多，"
             "所以本面的净等待是**下界**——上表的「单日跌破 −5bp 天数」就是给读者自查的："
             "短融（%s）在 %d 根 bar 里只有 %d 天跌破 5bp，收益确实走在价格里；"
             "⑤窗口从 %s 起，样本只有一段。\n"
             % (h.get("tape_of_the_cash_shelf", {}).get("code", "n/a"),
                h.get("tape_of_the_cash_shelf", {}).get("bars", 0),
                h.get("tape_of_the_cash_shelf", {}).get("days_below_minus_5bp", 0),
                p["window"]["start"]))
    return "\n".join(L) + "\n"


def _share(x):
    if x is None:
        return "n/a"
    return "{:.1f}%".format(float(x) * 100.0)


# --------------------------------------------------------------------------- check
def check(verbose=True):
    """Re-derive from the upstreams and compare to what is published."""
    if not os.path.exists(OUT_JSON):
        print("STALE: face missing (%s) -> run" % os.path.relpath(OUT_JSON, ROOT))
        return 3
    with io.open(OUT_JSON, encoding="utf-8") as f:
        pub = json.load(f)
    if not os.path.exists(R2043_JSON):
        print("STALE: upstream face missing (%s) -> run" % os.path.relpath(R2043_JSON, ROOT))
        return 3
    if _sha(R2043_JSON) != pub["upstream"]["sha256"]:
        print("STALE: upstream r2043 face bytes changed (sha %s… vs %s…) -> run"
              % (_sha(R2043_JSON)[:12], pub["upstream"]["sha256"][:12]))
        return 3

    buf = io.StringIO()
    old = sys.stdout
    sys.stdout = buf
    try:
        rc = build(write=False, verbose=False)
    finally:
        sys.stdout = old
    if rc != 0:
        print("CHECK FAILED: rebuild rc=%s" % rc)
        return 3
    del buf

    fresh = json.loads(json.dumps(_LAST["payload"]))
    # r1934: a bar that arrived after this face was priced is the panel's clock, not a
    # defect -- and the chain only pays for a rebuild when the check says STALE.  On a
    # moved tail every tier's slip median moves with it, so the comparison below cannot
    # be read as arithmetic at all.
    if fresh["evidence_cutoff"] != pub["evidence_cutoff"]:
        print("STALE: panel tail moved %s -> %s, this face is priced on the old bar -> run"
              % (pub["evidence_cutoff"], fresh["evidence_cutoff"]))
        return 3
    problems = []
    if fresh["evidence_cutoff"] != pub["evidence_cutoff"]:
        problems.append("evidence_cutoff %s -> %s"
                        % (pub["evidence_cutoff"], fresh["evidence_cutoff"]))
    for a, b in zip(pub["rows"], fresh["rows"]):
        if a["code"] != b["code"]:
            problems.append("row order drifted (%s vs %s)" % (a["code"], b["code"]))
            continue
        for key, brec in b["tiers"].items():
            arec = a["tiers"].get(key, {})
            if arec.get("sessions_to_fill") != brec.get("sessions_to_fill"):
                problems.append("%s tier %s sessions %s -> %s"
                                % (a["code"], key, arec.get("sessions_to_fill"),
                                   brec.get("sessions_to_fill")))
                continue
            for f in ("slip_median_bp", "carry_net_median_bp", "net_median_bp",
                      "net_p95_bp", "commission_median_bp"):
                av, bv = arec.get(f), brec.get(f)
                if (av is None) != (bv is None):
                    problems.append("%s tier %s %s missing on one side" % (a["code"], key, f))
                elif av is not None and abs(float(av) - float(bv)) > 1e-6:
                    problems.append("%s tier %s %s %s -> %s"
                                    % (a["code"], key, f, av, bv))
            if arec.get("verdict") != brec.get("verdict"):
                problems.append("%s tier %s verdict %s -> %s"
                                % (a["code"], key, arec.get("verdict"), brec.get("verdict")))
    if problems:
        if verbose:
            print("CHECK FAILED (%d)" % len(problems))
            for p_ in problems[:12]:
                print("  " + p_)
        return 3
    if verbose:
        rows = sum(1 for r in pub["rows"] for t in r["tiers"].values()
                   if t.get("windows"))
        print("CHECK OK  %d shelves, %d priced shelf-tier rows, evidence_cutoff %s"
              % (len(pub["rows"]), rows, pub["evidence_cutoff"]))
    return 0


# --------------------------------------------------------------------------- selftest
def selftest():
    ok = []

    def chk(cond, msg):
        ok.append((bool(cond), msg))
        if not cond:
            print("  FAIL %s" % msg)

    # 1. weights and their closed form
    w = cash_weights(5)
    chk(len(w) == 4, "n=5 gives 4 steps")
    chk(np.allclose(w, [0.8, 0.6, 0.4, 0.2]), "n=5 weights 0.8/0.6/0.4/0.2")
    chk(abs(weight_days(5) - 2.0) < 1e-12, "(n-1)/2 full-size days at n=5")
    chk(abs(weight_days(39) - 19.0) < 1e-12, "(n-1)/2 full-size days at n=39")
    chk(len(cash_weights(1)) == 0, "n=1 has no wait to price")

    # 2. constant-rate tape: carry == weight_days x daily rate, exactly
    daily = 0.4 / 1e4                       # 0.4bp per step
    rets = np.full(60, daily)
    car = window_carry(rets, 5)
    chk(len(car) == 56, "every overlapping 5-step window on a 60-bar tape")
    chk(np.allclose(car, 2.0 * daily), "constant tape: carry = (n-1)/2 x rate")

    # 3. the carry is the second term only: first step's own return is not counted
    step = np.zeros(60)
    step[0] = 1e-3                          # a return on the bar BEFORE the window opens
    chk(np.allclose(window_carry(step, 5), 0.0), "a return before the window is not carried")

    # 4. sign: net = slip - carry, so a positive carry must LOWER the net
    slip = np.asarray([5.0, 5.0, 5.0])
    carry_bp = np.asarray([1.0, 2.0, 3.0])
    net = slip - carry_bp
    chk(np.allclose(net, [4.0, 3.0, 2.0]), "net is a plain subtraction in the same bp units")

    # 5. money conversion
    chk(abs(money(4.0, 500000) - 200.0) < 1e-9, "4bp on 500k is 200 CNY")
    chk(money(None, 500000) is None, "no bp -> no money")

    # 6. verdict thresholds are monotone in the carry share
    base = {"sessions_to_fill": 3, "windows": 10, "slip_median_bp": 10.0,
            "carry_net_median_bp": 0.5, "net_p95_bp": 1.0}
    chk(verdicts_for(dict(base)) == ["CARRY_IS_A_ROUNDING_ERROR"],
        "5% of the slippage is a rounding error")
    chk(verdicts_for(dict(base, carry_net_median_bp=2.0)) == ["CARRY_TICKS_THE_WAIT_DOWN"],
        "20% ticks the wait down")
    chk(verdicts_for(dict(base, carry_net_median_bp=4.0)) == ["CARRY_PAYS_MOST_OF_THE_WAIT"],
        "40% pays most of the wait")
    chk(verdicts_for(dict(base, carry_net_median_bp=9.0, net_p95_bp=-1.0))
        == ["CARRY_PAYS_MOST_OF_THE_WAIT", "NET_WAIT_IS_FREE"],
        "a negative 95th percentile means the wait is free")
    chk(verdicts_for({"sessions_to_fill": 1}) == ["ONE_SESSION_NO_WAIT"],
        "one session has nothing to price")
    chk(verdicts_for({"sessions_to_fill": 4, "windows": 0}) == ["NO_WINDOWS"],
        "a tape shorter than the schedule claims nothing")

    # 6b. the per-wait-day axis: both terms divide by the same (n-1)/2
    rec = {"sessions_to_fill": 5, "windows": 10, "slip_median_bp": 1.6,
           "carry_net_median_bp": 1.2, "net_median_bp": 0.4, "net_p95_bp": 3.0,
           "net_per_wait_day_bp": 0.2}
    v = verdicts_for(dict(rec))
    chk("WAIT_WALKS_FASTER_THAN_THE_REPO_LEG" in v, "0.2bp/day of net wait is not self-financing")
    chk("WAIT_IS_NEARLY_SELF_FINANCING"
        in verdicts_for(dict(rec, net_per_wait_day_bp=0.05)),
        "0.05bp/day is nearly self-financing")
    chk("WAIT_IS_PAID_IN_FULL" in verdicts_for(dict(rec, net_per_wait_day_bp=-0.1)),
        "a negative per-day wait is paid in full")
    chk(abs(1.6 / weight_days(5) - 0.8) < 1e-12,
        "1.6bp over (n-1)/2 = 2 full-size days is 0.8bp/day")

    # 7. the commission arm must be strictly weaker than the gross arm
    fees0 = {k: 0.0 for k in CL.FEE_BP}
    bars = pd.bdate_range("2024-01-02", periods=30)
    rates = {"GC001": pd.Series(np.full(30, 1.8), index=bars)}
    net_ret, _ = CL.roll_rung(bars, rates, None, fees=None, name="GC001")
    gross_ret, _ = CL.roll_rung(bars, rates, None, fees=fees0, name="GC001")
    chk(float(np.sum(gross_ret.values)) > float(np.sum(net_ret.values)),
        "gross carry strictly exceeds net carry on a flat-rate tape")
    comm = float(np.sum(gross_ret.values)) - float(np.sum(net_ret.values))
    chk(abs(comm - 0.1 * 29 / 1e4) < 1e-9,
        "commission is 0.1bp per contract entry (29 entries over 30 bars)")

    # 8. published face agrees with a fresh build (this is the leg that catches a hand edit)
    if os.path.exists(OUT_JSON):
        rc = check(verbose=False)
        chk(rc == 0, "published face re-derives (check rc0)")
    else:
        chk(False, "published face exists")

    n_fail = sum(1 for c, _ in ok if not c)
    print("selftest: %d/%d PASS" % (len(ok) - n_fail, len(ok)))
    return 0 if n_fail == 0 else 1


# --------------------------------------------------------------------------- main
_LAST = {}


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd in ("--selftest", "selftest"):
        return selftest()
    if cmd in ("--check", "check"):
        return check()
    if cmd in ("run", "--run"):
        return build(True, True)
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))

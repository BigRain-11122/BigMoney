#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""money_accrual_level_decomposition -- how much of a money ETF's printed return is accrual?

WHY THIS FACE EXISTS
--------------------
r2050 (`money_premium_carry_audit`) printed a carry number for every money/bond shelf leg
and r2051 (`money_band_blind_spot`) showed that below the 1% band the elevation is still
partly paid back.  Both closed with the same debt:

    "要看到它，必须把 accrual 与价格水平分开建模（例如对同一只标的做「收益率对时间」的
     结构拟合），那是下一面的事。"

Every ruler so far measured a *deviation* from a level.  A deviation ruler cannot say what
share of the printed return is accrual -- it can only say the price is far from a level.
This face splits the printed return into two parts that add up to it:

    printed return  =  accrual (the typical bar)  +  price level (everything the typical bar is not)

and then asks the one follow-up that decides what the level part is: **is it a real price
path, a premium bleeding back, or the reset convention printing a number that is not there?**

THE QUESTION (frozen before the first run)
------------------------------------------
For every instrument in the r2048 money set and every book leg r2050 named as control:

1. What is the accrual rate (pp/yr) and what is the level part (pp/yr)?  Do they add up to
   the printed return?
2. Does the level part survive a trimmed average (i.e. is it made of a handful of bars)?
3. Does the deviation from the accrual line mean-revert, and at what half-life?

RULER (nothing re-decided here)
-------------------------------
* panel, window, reader -- r2050's own: `etf_book_cash_vehicle.load_etf` +
  `consolidation_returns` (share resets booked at exactly zero), window 2020-07-16 ..
  the panel tail.  Universe = `cash_shelf_flip_census.json` money set + the five book legs
  from `money_premium_carry_audit.json`.
* **ACCRUAL = median daily log return x 252.**  A money ETF's price sits at face value on
  most bars and moves in jumps on the rest; the median is the bar-level accrual estimate
  that ignores how many jump bars there are.  Printed beside it is the mean, so a reader
  can see how far the average bar is from the typical one.
* **PRINTED RETURN = mean daily log return x 252** (the series' own growth).  Deliberately
  NOT first-to-last: a price-accumulating ticker is a sawtooth, so endpoints can sit at the
  same level while the holder earned 2.4%/yr (r2050's own note).
* **LEVEL PART = printed return - accrual** (signed, pp/yr).  This is the share of the
  printed return that is not the typical bar.  It is not a claim that the price is "high".
* **TRIMMED LEVEL = 10% trimmed mean daily log return x 252 - accrual** (signed, pp/yr).
  If the level part is made of a handful of bars, the trimmed version collapses; if it is a
  real path, it survives.  This is the falsifier for "the number is a reset artifact".
* **DEVIATION d_t = cumsum(r_t - accrual_bar)**, bp.  Distance of the price path from its
  accrual line: excursion = std(d) / max|d|, today = last bar.
* **AR(1) = sum(d_t d_{t+1}) / sum(d_t^2)** (no intercept).  **HALF-LIFE = ln(0.5)/ln(phi)**
  when 0 < phi < 1; phi >= 1 means the deviation does not revert inside the window (a level
  shift, not a bleed).
* **BARS_PER_YEAR = 252** everywhere, so both parts sit on the published carry's clock.
* gates -- the census face must still be the face this reader priced (cutoff and row count
  re-read, not trusted), `printed = accrual + level` must hold to 1e-9pp, and every printed
  row must re-derive from the panel within 0.01pp / 0.05bp / 0.01 bar.

VERDICTS (mechanical, frozen on the worst |level part| across the measured set)
-------------------------------------------------------------------------------
* ACCRUAL_EXPLAINS_THE_RETURN      -- every instrument's |level part| < 0.50pp/yr.
* ACCRUAL_IS_MOST_OF_THE_RETURN    -- worst |level part| < 2.00pp/yr.
* THE_PRINTED_RETURN_IS_MOSTLY_PRICE -- worst |level part| >= 2.00pp/yr.

TAGS (printed beside the verdict, never folded into it)
------------------------------------------------------
* LEVEL_PART_IS_A_RESET_ARTIFACT -- some instrument's |level| >= 2.00pp while its
                                    |trimmed level| < 0.50pp: the printed return is a few
                                    jump bars, not a price path.
* LEVEL_PART_SURVIVES_TRIMMING   -- no instrument shows that gap: the level part is real.
* PREMIUMS_BLEED_BACK / PREMIUMS_ARE_LEVEL_SHIFTS
                                 -- median half-life over reversion-flagged instruments
                                    < / >= 60 bars.
* TODAY_SITS_ABOVE_THE_PATH / TODAY_SITS_BELOW_THE_PATH / TODAY_SITS_ON_THE_PATH
                                 -- median last-bar deviation vs +-5bp.
* BOOK_LEGS_ARE_ACCRUAL          -- every book leg has |trimmed level| < 0.50pp/yr:
                                    r2050's clean tag survives a decomposition that uses no
                                    band at all.
* BOOK_LEGS_NEED_THE_SPLIT       -- at least one book leg does not.

WHAT THIS RULER CANNOT DO (printed, not folded)
-----------------------------------------------
* A reset is booked at zero by the published reader; the *snap-back* bars after it are not
  repaired, so they land in the mean as a gain.  The trimmed level is what separates that
  convention from a real path -- it is a convention test, not a return estimate.
* Accrual is one number for six years: a policy-rate change shows up as level, exactly like
  a premium does.  Only the reversion tag can tell them apart, and only if the reversion is
  visible inside the window.
* Dividend-paying share vehicles (fixed face, return paid in shares) have no accrual in
  their close at all; the face prints the band and says so rather than a zero.

Usage:
    python scripts/money_accrual_level_decomposition.py run
    python scripts/money_accrual_level_decomposition.py --check
    python scripts/money_accrual_level_decomposition.py --write
    python scripts/money_accrual_level_decomposition.py --selftest
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import etf_book_cash_vehicle as CV  # noqa: E402  (the published money reader)

CENSUS_FACE = "results/cash_shelf_flip_census.json"
PREMIUM_FACE = "results/money_premium_carry_audit.json"
FACE = "results/money_accrual_level_decomposition.json"
DOC = "research/MONEY_ACCRUAL_LEVEL_DECOMPOSITION.md"

# Frozen before the first run.  See the docstring for why each number is what it is.
BARS_PER_YEAR = 252
WINDOW_START = "2020-07-16"   # r2050's census window
MATERIAL_PP = 2.00            # at or above this the level part deserves its own ruler
MILD_PP = 0.50                # below this the printed return is accrual for a carry caliber
REVERT_BARS = 60.0            # half-life at or above this is not a bleed, it is a level shift
MIN_PHI = 0.10                # below this the residual is one-bar noise (float noise, not decay)
ON_PATH_BP = 5.00             # today "sits on the path" inside this
TRIM_PCT = 10.0               # two-sided trim for the robustness read
BIG_BAR_BP = 50.0             # |bar return| at or above this counts as a jump bar
BOOK_LEG_TOL_PP = 0.50        # r2050's own clean threshold, re-used (not re-decided)

_QUIET = False


def log(msg: str) -> None:
    if not _QUIET:
        print(msg)


# ----------------------------------------------------------------------------- io helpers
def _load(path):
    with open(os.path.join(ROOT, path), "r", encoding="utf-8") as fh:
        return json.load(fh)


def _content_sha(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()[:12]


# ----------------------------------------------------------------------------- the ruler
def decompose(px: pd.Series) -> dict:
    """Split the printed return into accrual + level and measure the level's persistence."""
    px = px.dropna().astype(float)
    ret, jumps = CV.consolidation_returns(px)
    ret = ret.iloc[1:]                          # the first bar has no return
    r = np.log1p(ret.to_numpy())
    n = len(r)
    if n < 120:
        raise ValueError("too few bars: %d" % n)

    accrual_bar = float(np.median(r))
    mean_bar = float(np.mean(r))
    lo, hi = np.percentile(r, [TRIM_PCT, 100.0 - TRIM_PCT])
    trimmed_bar = float(np.mean(r[(r >= lo) & (r <= hi)]))

    accrual_pp = math.expm1(accrual_bar * BARS_PER_YEAR) * 100.0
    printed_pp = math.expm1(mean_bar * BARS_PER_YEAR) * 100.0
    trimmed_pp = math.expm1(trimmed_bar * BARS_PER_YEAR) * 100.0

    dev = np.cumsum(r - accrual_bar) * 1e4        # bp away from the accrual line
    sigma_bp = float(np.std(dev, ddof=1))
    max_abs_bp = float(np.max(np.abs(dev)))
    today_bp = float(dev[-1])

    # Persistence is a property of the RESIDUAL bar (r - accrual), not of the cumulative
    # level: a cumulative deviation is a random walk under constant accrual and would report
    # a half-life for a series that never reverts.  phi in (0,1) = a premium bar decays;
    # phi >= 1 = the excess persists (a path); phi <= 0 = one-bar noise (nothing to decay).
    resid = r - accrual_bar
    x, y = resid[:-1], resid[1:]
    denom = float(np.dot(x, x))
    phi = float(np.dot(x, y) / denom) if denom > 0 else float("nan")
    half_life = (math.log(0.5) / math.log(phi)
                 if (math.isfinite(phi) and MIN_PHI <= phi < 1.0) else None)

    return {
        "bars": int(n),
        "accrual_pp": accrual_pp,
        "printed_pp": printed_pp,
        "level_pp": printed_pp - accrual_pp,
        "trimmed_pp": trimmed_pp,
        "trimmed_level_pp": trimmed_pp - accrual_pp,
        "accrual_bar_bp": accrual_bar * 1e4,
        "mean_bar_bp": mean_bar * 1e4,
        "median_minus_mean_bp": (accrual_bar - mean_bar) * 1e4,
        "jump_bars": int(len(jumps)),
        "big_bars": int(np.sum(np.abs(r) * 1e4 >= BIG_BAR_BP)),
        "dev_sigma_bp": sigma_bp,
        "dev_max_abs_bp": max_abs_bp,
        "today_bp": today_bp,
        "ar1_phi": phi,
        "half_life_bars": half_life,
        "reverts": bool(half_life is not None and half_life < REVERT_BARS),
    }


def verdict_of(level_pps) -> str:
    worst = max((abs(v) for v in level_pps), default=0.0)
    if worst < MILD_PP:
        return "ACCRUAL_EXPLAINS_THE_RETURN"
    if worst < MATERIAL_PP:
        return "ACCRUAL_IS_MOST_OF_THE_RETURN"
    return "THE_PRINTED_RETURN_IS_MOSTLY_PRICE"


def tags_of(rows, book_codes) -> list:
    tags = []
    artifact = [r for r in rows
                if abs(r["level_pp"]) >= MATERIAL_PP and abs(r["trimmed_level_pp"]) < MILD_PP]
    tags.append("LEVEL_PART_IS_A_RESET_ARTIFACT" if artifact else "LEVEL_PART_SURVIVES_TRIMMING")
    if artifact:
        tags.append("artifact_codes=" + ",".join(sorted(str(r.get("code", "?")) for r in artifact)))

    hl = [r["half_life_bars"] for r in rows if r.get("reverts")]
    pers = [r["ar1_phi"] for r in rows if math.isfinite(r.get("ar1_phi", float("nan")))]
    if hl:
        med = float(np.median(hl))
        tags.append("PREMIUMS_BLEED_BACK" if med < REVERT_BARS else "PREMIUMS_ARE_PERSISTENT_PATHS")
        tags.append("median_half_life_bars=%.2f" % med)
    elif pers and float(np.median(pers)) >= 0.995:
        tags.append("PREMIUMS_ARE_PERSISTENT_PATHS")
        tags.append("median_half_life_bars=none")
    else:
        tags.append("PREMIUMS_HAVE_NO_PERSISTENCE")
        tags.append("median_half_life_bars=none")
    tags.append("reversion_flagged=%d/%d" % (len(hl), len(rows)))

    med_today = float(np.median([r["today_bp"] for r in rows])) if rows else 0.0
    if abs(med_today) < ON_PATH_BP:
        tags.append("TODAY_SITS_ON_THE_PATH")
    elif med_today > 0:
        tags.append("TODAY_SITS_ABOVE_THE_PATH")
    else:
        tags.append("TODAY_SITS_BELOW_THE_PATH")
    tags.append("median_today_bp=%.2f" % med_today)

    legs = [r for r in rows if r.get("code") in book_codes]
    if legs and all(abs(r["trimmed_level_pp"]) < BOOK_LEG_TOL_PP for r in legs):
        tags.append("BOOK_LEGS_ARE_ACCRUAL")
    elif legs:
        tags.append("BOOK_LEGS_NEED_THE_SPLIT")
    return tags


# ----------------------------------------------------------------------------- build
def _universe():
    census = _load(CENSUS_FACE)
    premium = _load(PREMIUM_FACE)
    named = {r["code"]: r.get("name") for r in census["rows"]}
    money = [r["code"] for r in census["universe"].get("money_sigma_over_25bp", [])]
    book_codes = {r["code"] for r in premium.get("book_legs") or [] if r.get("code")}
    if not book_codes:
        book_codes = {"511880", "511360", "511010"}
    return census, named, money, book_codes


def build() -> dict:
    census, named, money, book_codes = _universe()
    rows = []
    for code in sorted(set(money) | book_codes):
        try:
            px = CV.load_etf(code)
        except FileNotFoundError:
            rows.append({"code": code, "name": named.get(code), "priced": False,
                         "why_unpriced": "no daily panel"})
            continue
        px = px[px.index >= pd.Timestamp(WINDOW_START)]
        span_bp = float((px.max() / px.min() - 1.0) * 1e4) if len(px) > 1 else 0.0
        if len(px) < 120:
            rows.append({"code": code, "name": named.get(code), "priced": False,
                         "why_unpriced": "fewer than 120 bars in the census window",
                         "price_band_bp": round(span_bp, 1)})
            continue
        m = decompose(px)
        m.update({"code": code, "name": named.get(code), "priced": True,
                  "is_money_named": code in money, "is_book_leg": code in book_codes,
                  "price_band_bp": round(span_bp, 1),
                  "panel_first": str(px.index[0].date()), "panel_last": str(px.index[-1].date())})
        rows.append(m)

    priced = [r for r in rows if r.get("priced")]
    verdict = verdict_of([r["level_pp"] for r in priced])
    tags = tags_of(priced, book_codes)
    worst = max(priced, key=lambda r: abs(r["level_pp"])) if priced else None
    top = max(priced, key=lambda r: r["level_pp"]) if priced else None

    payload = {
        "schema": "money-accrual-level-decomposition/v1",
        "artifact": "money_accrual_level_decomposition",
        "generated": pd.Timestamp.now(tz="Asia/Shanghai").isoformat(timespec="seconds"),
        "evidence_cutoff": max(r["panel_last"] for r in priced) if priced else None,
        "window": {"start": WINDOW_START, "end": max(r["panel_last"] for r in priced) if priced else None},
        "question": ("what share of a money ETF's printed return is accrual, and is the level "
                     "part a real path or the reset convention?"),
        "ruler": {
            "accrual": "median daily log return x 252",
            "printed": "mean daily log return x 252 (series growth, not endpoints)",
            "level_part": "printed - accrual (signed, pp/yr)",
            "trimmed_level": "%g%% trimmed mean x 252 - accrual (signed, pp/yr)" % TRIM_PCT,
            "deviation": "cumsum(ret - accrual_bar), bp",
            "persistence": "AR(1) without intercept; half-life = ln0.5/ln(phi)",
            "bars_per_year": BARS_PER_YEAR,
            "material_pp": MATERIAL_PP, "mild_pp": MILD_PP, "revert_bars": REVERT_BARS,
            "on_path_bp": ON_PATH_BP, "trim_pct": TRIM_PCT, "big_bar_bp": BIG_BAR_BP,
            "book_leg_tol_pp": BOOK_LEG_TOL_PP,
        },
        "upstream": {"census_face": CENSUS_FACE, "premium_face": PREMIUM_FACE,
                     "census_cutoff": census.get("evidence_cutoff"),
                     "census_rows": len(census.get("rows") or [])},
        "universe": {"named_money": sorted(money), "book_legs": sorted(book_codes),
                     "priced": len(priced), "unpriced": len(rows) - len(priced)},
        "verdict": verdict,
        "tags": tags,
        "headline": ({
            "worst_level_pp": round(worst["level_pp"], 2), "worst_code": worst["code"],
            "worst_name": worst["name"], "worst_accrual_pp": round(worst["accrual_pp"], 2),
            "worst_trimmed_level_pp": round(worst["trimmed_level_pp"], 2),
            "highest_level_pp": round(top["level_pp"], 2), "highest_code": top["code"],
        } if worst else None),
        "rows": rows,
    }
    payload["content_sha256"] = _content_sha({k: v for k, v in payload.items() if k != "content_sha256"})
    return payload


# ----------------------------------------------------------------------------- rendering
def _f(v, nd=2, dash="-"):
    if v is None:
        return dash
    if isinstance(v, float) and not math.isfinite(v):
        return dash
    return ("%." + str(nd) + "f") % v


def render_table(payload) -> str:
    head = ("| code | class | accrual pp/yr | printed pp/yr | level pp/yr | trimmed level pp/yr | "
            "jump bars | big bars | dev sigma bp | today bp | half-life bars | reverts |\n"
            "|---|---|---|---|---|---|---|---|---|---|---|---|")
    lines = [head]
    for r in payload["rows"]:
        if not r.get("priced"):
            lines.append("| %s | %s | unpriced | - | - | - | - | - | - | - | - | %s |"
                         % (r["code"], "money" if r.get("is_money_named") else "book",
                            r.get("why_unpriced") or "-"))
            continue
        lines.append("| %s | %s | %s | %s | %s | %s | %d | %d | %s | %s | %s | %s |" % (
            r["code"], "money" if r["is_money_named"] else ("book" if r["is_book_leg"] else "other"),
            _f(r["accrual_pp"]), _f(r["printed_pp"]), _f(r["level_pp"]), _f(r["trimmed_level_pp"]),
            r["jump_bars"], r["big_bars"], _f(r["dev_sigma_bp"], 1), _f(r["today_bp"], 1),
            _f(r["half_life_bars"], 2), "yes" if r["reverts"] else "no"))
    return "\n".join(lines)


def write_doc(payload) -> None:
    priced = [r for r in payload["rows"] if r.get("priced")]
    money = [r for r in priced if r["is_money_named"]]
    legs = [r for r in priced if r["is_book_leg"]]
    worst = max(priced, key=lambda r: abs(r["level_pp"])) if priced else None
    artifacts = [r for r in priced
                 if abs(r["level_pp"]) >= MATERIAL_PP and abs(r["trimmed_level_pp"]) < MILD_PP]
    by_level = sorted(money, key=lambda r: -abs(r["level_pp"]))

    body = []
    body.append("# 一只货币 ETF 印出来的收益里，有多少是真 accrual\n")
    body.append("> 本面把「印出来的收益率」拆成两半，两半相加等于它本身：\n"
                "> **印出来的收益 = accrual（典型那根 bar）+ 价格水平（典型 bar 解释不了的部分）**。\n"
                "> 然后追问决定性的第二问：价格水平那半是真实路径，还是复权规则印出来的假数字？\n")
    body.append("## 一、判词与标签\n")
    body.append("- **判词：`%s`**" % payload["verdict"])
    for t in payload["tags"]:
        body.append("- `%s`" % t)
    body.append("")
    body.append("## 二、口径（跑之前就冻结，见脚本头注）\n")
    body.append("- accrual = 日对数收益率的**中位数** × 252。货币 ETF 大多数 bar 停在面值附近、"
                "少数 bar 才动，中位数是忽略「动了几次」的 bar 层估计；平均值同时印出，"
                "让你看见平均 bar 离典型 bar 有多远。")
    body.append("- 印出来的收益 = **日对数收益率的平均值** × 252（序列自己的增长），"
                "**故意不用首尾价差**——价格累计型标的的锯齿会让首尾同高而持有人每年赚 2.4%。")
    body.append("- 价格水平 = 印出来的收益 − accrual（**带符号**）。这不是在说价格「高」。")
    body.append("- **截尾水平** = 两侧各截 10% 后的平均 × 252 − accrual："
                "如果价格水平是少数几根 bar 撑起来的，这一列会塌；是真路径则留得住。"
                "这是「这个数字是不是复权规则印出来的」的证伪尺。")
    body.append("- 偏离 d_t = cumsum(r_t − accrual_bar)，单位 bp；持续性 = 无截距 AR(1)，"
                "半衰期 = ln0.5/ln(φ)，φ ≥ 1 表示窗口内不回归（水平位移，不是溢价）。\n")
    body.append("## 三、逐只读数\n")
    body.append("<!-- ACCRUAL-LEVEL-TABLE:START -->")
    body.append(render_table(payload))
    body.append("<!-- ACCRUAL-LEVEL-TABLE:END -->\n")
    body.append("## 四、读数怎么读\n")
    body.append("三句真话，按重要性排：\n")
    if worst is not None:
        body.append("1. **最极端的 %s（%s）印出 %s pp/yr，其中 accrual 只有 %s pp/yr、"
                    "价格水平 %s pp/yr。** 换成截尾口径后水平剩 %s pp/yr——%s"
                    % (worst["code"], worst["name"], _f(worst["printed_pp"]),
                       _f(worst["accrual_pp"]), _f(worst["level_pp"]),
                       _f(worst["trimmed_level_pp"]),
                       "它塌了，说明这个收益率是少数几根跳变 bar 印出来的，不是路径。"
                       if abs(worst["trimmed_level_pp"]) < MILD_PP else "它留住了，说明这是真实价格路径。"))
    if artifacts:
        body.append("2. **%d 只标的的「价格水平」在截尾口径下塌掉：%s。** 它们的均价被少数几根大 bar "
                    "（跳变 bar 数见上表）抬起来；对 carry 口径而言那不是溢价，是复权规则的记账。"
                    % (len(artifacts), "、".join("%s（%s pp→%s pp）"
                                               % (r["code"], _f(r["level_pp"]), _f(r["trimmed_level_pp"]))
                                               for r in sorted(artifacts, key=lambda r: -abs(r["level_pp"])))))
    if by_level:
        body.append("3. **同一把尺下，%s 的价格水平最小（%s pp/yr）。** 它们的印出收益几乎全是 accrual——"
                    "这正是「干净」这个词能成立的地方：不是偏差小，而是典型 bar 就解释了它。"
                    % (by_level[-1]["code"], _f(by_level[-1]["level_pp"])))
    body.append("")
    if legs:
        body.append("**这本书自己的腿：** %s。"
                    % "；".join("%s accrual %s / 水平 %s / 截尾水平 %s pp/yr"
                                % (r["code"], _f(r["accrual_pp"]), _f(r["level_pp"]),
                                   _f(r["trimmed_level_pp"])) for r in legs))
        body.append("")
    body.append("## 五、局限（印出来，不当结论用）\n")
    body.append("- 复权把重置 bar 记成零，但**复位后的回弹 bar 没有修**，它会以「收益」身份进平均值。"
                "截尾水平就是为这件事准备的：它是**规则检验**，不是收益估计。")
    body.append("- accrual 在六年里是一个数：政策利率变了会整段显示为价格水平，与真溢价同形。"
                "能分开它们的只有回归标签，而回归必须在窗口内看得见。")
    body.append("- 分红型份额标的的收盘价里根本没有 accrual（面值固定、收益按份额发），"
                "本面对这类标的只印出价格带宽并明说，不印一个零。")
    body.append("- 不计成本、不改动任何已发布货架数字、不重开 r2050/r2051 的判词。\n")
    body.append("---\n")
    body.append("生成：`%s` · 内容哈希 `%s` · 上游 `%s`（cutoff %s，%s 行）"
                % (payload["generated"], payload["content_sha256"], CENSUS_FACE,
                   payload["upstream"]["census_cutoff"], payload["upstream"]["census_rows"]))
    text = "\n".join(body) + "\n"

    with open(os.path.join(ROOT, DOC), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    log("[write] %s (%d chars)" % (DOC, len(text)))


def _block_of(text: str) -> str:
    a = text.index("<!-- ACCRUAL-LEVEL-TABLE:START -->")
    b = text.index("<!-- ACCRUAL-LEVEL-TABLE:END -->")
    return text[a:b]


# ----------------------------------------------------------------------------- check
def check(payload=None) -> tuple:
    """Re-derive every printed row.  STALE = the panel moved; CHECK FAILED = the face's
    arithmetic is not the arithmetic on disk (r1934: the words are a contract, not a mood)."""
    problems, stale = [], []
    face = payload if payload is not None else _load(FACE)
    fresh = build()

    if face.get("evidence_cutoff") != fresh.get("evidence_cutoff"):
        stale.append("panel tail %s -> %s" % (face.get("evidence_cutoff"), fresh.get("evidence_cutoff")))
    if (face.get("upstream") or {}).get("census_rows") != (fresh.get("upstream") or {}).get("census_rows"):
        stale.append("census rows %s -> %s" % ((face.get("upstream") or {}).get("census_rows"),
                                               (fresh.get("upstream") or {}).get("census_rows")))

    old = {r["code"]: r for r in face.get("rows") or []}
    new = {r["code"]: r for r in fresh.get("rows") or []}
    for code, nrow in new.items():
        orow = old.get(code)
        if orow is None:
            stale.append("%s added" % code)
            continue
        if not nrow.get("priced") or not orow.get("priced"):
            continue
        for key, tol in (("accrual_pp", 0.01), ("printed_pp", 0.01), ("level_pp", 0.01),
                         ("trimmed_pp", 0.01), ("trimmed_level_pp", 0.01),
                         ("dev_sigma_bp", 0.05), ("today_bp", 0.05)):
            if abs(float(orow.get(key, 0.0)) - float(nrow[key])) > tol:
                problems.append("%s %s printed=%s now=%s" % (code, key, _f(orow.get(key), 4), _f(nrow[key], 4)))
        oh, nh = orow.get("half_life_bars"), nrow.get("half_life_bars")
        if (oh is None) != (nh is None):
            problems.append("%s half_life printed=%s now=%s" % (code, oh, nh))
        elif oh is not None and abs(float(oh) - float(nh)) > 0.01:
            problems.append("%s half_life printed=%.4f now=%.4f" % (code, float(oh), float(nh)))
        if abs((nrow["accrual_pp"] + nrow["level_pp"]) - nrow["printed_pp"]) > 1e-9:
            problems.append("%s identity broken" % code)
    for code in old:
        if code not in new:
            stale.append("%s dropped" % code)

    if face.get("verdict") != fresh.get("verdict"):
        problems.append("verdict printed=%s now=%s" % (face.get("verdict"), fresh.get("verdict")))
    if list(face.get("tags") or []) != list(fresh.get("tags") or []):
        problems.append("tags printed=%s now=%s" % (face.get("tags"), fresh.get("tags")))

    doc_path = os.path.join(ROOT, DOC)
    if not os.path.exists(doc_path):
        problems.append("page missing: %s" % DOC)
    else:
        with open(doc_path, "r", encoding="utf-8") as fh:
            text = fh.read()
        if face.get("verdict") not in text:
            problems.append("page does not carry the verdict %s" % face.get("verdict"))
        if render_table(face) not in _block_of(text):
            problems.append("page table != face table")

    if problems:
        return 1, "CHECK FAILED: " + "; ".join(problems[:6])
    if stale:
        return 3, "STALE: " + "; ".join(stale[:6])
    return 0, "CHECK OK %d rows re-derived from the panel (cutoff %s)" % (
        len([r for r in fresh["rows"] if r.get("priced")]), fresh.get("evidence_cutoff"))


# ----------------------------------------------------------------------------- selftest
def _series(bars=700, accrual_bp=0.5, seed=7, mode="clean", phi=0.8, bump_bp=50.0,
            resets=7, reset_pct=-0.09):
    """Synthetic close series whose accrual and jumps are both known."""
    rng = np.random.default_rng(seed)
    r = np.full(bars, accrual_bp / 1e4)
    if mode == "step":
        r[bars // 2] += bump_bp / 1e4
    elif mode == "ar1":
        d = np.zeros(bars)
        for t in range(1, bars):
            d[t] = phi * d[t - 1] + rng.normal(0.0, bump_bp / 1e4)
        r = r + d
    elif mode == "noise":
        r = r + rng.normal(0.0, bump_bp / 1e4, bars)
    elif mode == "dividends":
        drop = rng.random(bars) < 0.20
        r = r - np.where(drop, 0.0030, 0.0)
    elif mode == "reset":
        # `resets` share resets (deep negative bar, booked at zero by the reader) plus the
        # snap-back bar that the reader does NOT repair -- this is the artifact under test.
        idx = np.linspace(bars // 8, bars - bars // 8, resets).astype(int)
        r[idx] = reset_pct
        r[idx + 1] = -reset_pct
    elif mode == "skewed":
        # 40% of the bars print +1.5bp on top of accrual: the median stays at accrual, both
        # the mean and the trimmed mean are lifted -- a level part that is not a few bars.
        pick = rng.random(bars) < 0.40
        r = r + np.where(pick, 1.5e-4, 0.0)
    lp = np.log(100.0) + np.cumsum(r)
    return pd.Series(np.exp(lp), index=pd.bdate_range("2021-01-04", periods=bars))


def selftest() -> int:
    legs = 0
    fails = []

    def chk(ok, msg):
        nonlocal legs
        legs += 1
        if not ok:
            fails.append(msg)

    # 1. pure accrual: the typical bar explains the printed return, no excursion
    m = decompose(_series(mode="clean"))
    chk(abs(m["level_pp"]) < 0.02, "pure accrual must have ~0 level part, got %.4f" % m["level_pp"])
    chk(m["dev_sigma_bp"] < 0.01, "pure accrual must have ~0 excursion, got %.4f" % m["dev_sigma_bp"])
    chk(verdict_of([m["level_pp"]]) == "ACCRUAL_EXPLAINS_THE_RETURN", "pure accrual must read as accrual")

    # 2. identity: accrual + level == printed, always
    chk(abs(m["accrual_pp"] + m["level_pp"] - m["printed_pp"]) < 1e-9, "identity must hold to 1e-9")

    # 3. a permanent step is a level shift: positive level part, no reversion
    s = decompose(_series(mode="step"))
    chk(s["level_pp"] > 0.10, "a +50bp permanent step must show a positive level part, got %.3f" % s["level_pp"])
    chk(not s["reverts"], "a permanent step must not be tagged as reversion (phi=%.3f)" % s["ar1_phi"])
    chk(s["dev_max_abs_bp"] > 40.0, "step must show a 40bp+ excursion, got %.1f" % s["dev_max_abs_bp"])

    # 4. AR(1) half-life is recovered
    a = decompose(_series(mode="ar1", phi=0.8, bump_bp=30.0))
    chk(a["half_life_bars"] is not None, "AR(1) series must have a finite half-life")
    if a["half_life_bars"] is not None:
        true_hl = math.log(0.5) / math.log(0.8)
        chk(abs(a["half_life_bars"] - true_hl) < 1.5,
            "half-life %.2f must be near %.2f (0.8 phi)" % (a["half_life_bars"], true_hl))
        chk(a["reverts"], "a 3.1-bar half-life must be tagged as reversion")

    # 5. a dividend tail separates median from mean; the median stays at the true accrual
    dv = decompose(_series(mode="dividends"))
    chk(abs(dv["median_minus_mean_bp"]) > 5.0,
        "dividend tail must separate median from mean, got %.2f" % dv["median_minus_mean_bp"])
    chk(abs(dv["accrual_bar_bp"] - 0.5) < 0.02,
        "median must stay at the true accrual 0.5bp, got %.4f" % dv["accrual_bar_bp"])

    # 6. the reset artifact: raw level is large, the trimmed level collapses
    rs = decompose(_series(mode="reset"))
    chk(abs(rs["level_pp"]) >= MATERIAL_PP,
        "reset series must print a material level part, got %.2f" % rs["level_pp"])
    chk(abs(rs["trimmed_level_pp"]) < MILD_PP,
        "reset series' trimmed level must collapse, got %.2f" % rs["trimmed_level_pp"])
    chk("LEVEL_PART_IS_A_RESET_ARTIFACT" in tags_of([rs], set()),
        "reset artifact must be tagged")
    sk = decompose(_series(mode="skewed"))
    chk(abs(sk["trimmed_level_pp"]) >= MILD_PP,
        "a level part built from many bars must survive trimming, got %.2f" % sk["trimmed_level_pp"])
    chk("LEVEL_PART_SURVIVES_TRIMMING" in tags_of([sk], set()),
        "a many-bar level part must be tagged as surviving trimming")

    # 7. verdict thresholds are the frozen ones
    chk(verdict_of([0.1, 0.3]) == "ACCRUAL_EXPLAINS_THE_RETURN", "mild verdict band")
    chk(verdict_of([0.1, 1.0]) == "ACCRUAL_IS_MOST_OF_THE_RETURN", "middle verdict band")
    chk(verdict_of([0.1, -2.5]) == "THE_PRINTED_RETURN_IS_MOSTLY_PRICE", "material verdict band (signed)")

    # 8. tags follow their inputs
    rows = [{"code": "A", "half_life_bars": 3.0, "reverts": True, "today_bp": 1.0,
             "level_pp": 0.1, "trimmed_level_pp": 0.1},
            {"code": "B", "half_life_bars": 4.0, "reverts": True, "today_bp": -2.0,
             "level_pp": 0.2, "trimmed_level_pp": 0.2}]
    tg = tags_of(rows, {"A"})
    chk("PREMIUMS_BLEED_BACK" in tg, "fast reversion tag")
    chk("TODAY_SITS_ON_THE_PATH" in tg, "on-path tag")
    chk("BOOK_LEGS_ARE_ACCRUAL" in tg, "clean book legs tag")

    # 9. STALE and CHECK FAILED are different words (r1934 contract)
    face = build()
    write_doc(face)     # the page is part of this face; the legs below must see a fresh one
    moved = dict(face, evidence_cutoff="1999-01-01")
    rc, msg = check(moved)
    chk(rc == 3 and "STALE" in msg, "moved panel must be rc3 with STALE, got rc%d %s" % (rc, msg[:50]))

    dirty = json.loads(json.dumps(face))
    dirty["rows"][0]["accrual_pp"] = float(dirty["rows"][0].get("accrual_pp") or 0.0) + 1.0
    rc2, msg2 = check(dirty)
    chk(rc2 == 1 and "CHECK FAILED" in msg2 and "STALE" not in msg2.split(":")[0],
        "tampered row must be rc1 CHECK FAILED, got rc%d %s" % (rc2, msg2[:50]))

    print("selftest: %d legs, %d failed" % (legs, len(fails)))
    for f in fails:
        print("  FAIL " + f)
    return 0 if not fails else 1


# ----------------------------------------------------------------------------- entry points
def run() -> int:
    payload = build()
    with open(os.path.join(ROOT, FACE), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    log("[write] %s" % FACE)
    write_doc(payload)
    log("[run] %s | %s | %s" % (payload["verdict"],
                                " ".join(t for t in payload["tags"] if "=" in t),
                                payload["headline"]))
    return 0


def main(argv) -> int:
    global _QUIET
    cmd = (argv[1] if len(argv) > 1 else "run").lstrip("-")
    if cmd == "run":
        return run()
    if cmd == "write":
        write_doc(_load(FACE))
        return 0
    if cmd == "check":
        rc, msg = check()
        print(msg)
        return rc
    if cmd == "selftest":
        _QUIET = True
        return selftest()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))

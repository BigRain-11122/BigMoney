"""Deploy now, or wait for a narrower beta band?  Priced on the exposure each choice carries.

r2033 put both carriers of this hedge on one ruler; r2036 charged the collateral and the
lender; r2037 cut the same 52 periods five ways and found the sign stable while the size
was shrinking.  Every one of those faces ends at the same sentence -- the beta's own 95%
band spans 924 lots, and a narrower band is available by fitting on more periods, at the
price of fitting on data the reader cannot see yet.  None of them chose that trade.

This face chooses it, and it does so by pricing the one thing the family has never put a
number on: what does the wait cost while you are waiting?

  deploy   the point estimate, 0.9013, is 3,919 lots.  Residual annualised volatility is
           10.763% (band face `risk.rows[point]`).  The cost of running the hedge is
           r2036's -0.354pp carrier gap, both legs funded.
  wait     the band halves when the standard error halves, which needs four times the
           periods -- 172 instead of 43, i.e. 10.238 more years at 12.6 periods a year.
           During those years the book is NOT hedged: it carries its own 27.343% vol.
           What the wait buys at the end is the residual of a perfect beta, 10.639%
           (`risk.rows[one_unit]`), a ceiling of 0.124pp.
  wrong    deploy and be wrong: hold 0.9013 while the true beta is the held-back 1.0263.
           Residual is 10.709% -- the deployment's risk ceiling is 0.054pp of vol, which
           is 307x cheaper per year than the wait it avoids.

No panel read, no re-fitting, no new claim about whether the hedge works.  Every number
below is a published cell of results/astock_veto_hedge_band.json,
results/astock_veto_hedge_funding.json and results/astock_veto_hedgeable_beta.json,
carried into one subtraction.  It would rather say STALE than price a parent that moved.

Modes: run (default) | --check | --selftest
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BAND_FACE = os.path.join(ROOT, "results", "astock_veto_hedge_band.json")
FUNDING_FACE = os.path.join(ROOT, "results", "astock_veto_hedge_funding.json")
BETA_FACE = os.path.join(ROOT, "results", "astock_veto_hedgeable_beta.json")
OUT_JSON = os.path.join(ROOT, "results", "astock_veto_hedge_deploy_wait.json")
OUT_MD = os.path.join(ROOT, "research", "ASTOCK_VETO_HEDGE_DEPLOY_WAIT.md")

PPY = 12.6                 # periods per year, frozen by the band face's spec
LENS_CNY = 1_000_000.0     # the family's per-million lens (r1912/r1913)
TARGET_BAND_SHRINK = 0.5   # the wait is priced for "halve the band", not "make it zero"
CHEAP_RATIO = 1.0          # below this the wait buys cheaper insurance than it costs
TOL = 1e-9

PREREG = {
    "question": ("the beta family publishes a 924-lot band and then declines to choose "
                 "between deploying on the point estimate and waiting for a narrower "
                 "one.  What does the wait cost per year while it is running, and how "
                 "does that price compare with the residual volatility it removes?"),
    "answered_from": "results/astock_veto_hedge_band.json (risk rows, fit, ladder, spec), "
                     "results/astock_veto_hedge_funding.json (carrier gap), "
                     "results/astock_veto_hedgeable_beta.json (book vol identity)",
    "not_done_here": ("no new data, no re-fitting of beta, no re-pricing of the hedge's "
                      "own edge, no claim that either carrier is worth committing "
                      "capital to -- the sizing decision is priced, not decided"),
    "error_model": ("the band face's classical OLS standard error is carried as "
                    "se(n) = se(n0) * sqrt(n0/n); a band that halves therefore needs "
                    "four times the periods.  The residual volatility of a beta is read "
                    "from the band face's own published risk rows, never re-derived from "
                    "the panel"),
    "wait_definition": ("'wait' means the position is NOT on until the band reaches the "
                        "target.  The book therefore carries its own annualised "
                        "volatility during the wait, and the wait's yearly cost is the "
                        "difference between that and the hedged residual.  A reader who "
                        "runs a partial hedge while waiting pays less than this face "
                        "prices -- the face prices the fully-unhedged wait"),
    "verdicts": [
        "wait price / wait benefit >= %.1f -> WAITING_IS_THE_EXPENSIVE_INSURANCE"
        % CHEAP_RATIO,
        "wait price / wait benefit < %.1f -> WAITING_IS_THE_CHEAPER_INSURANCE"
        % CHEAP_RATIO,
        "the band face is missing or unreadable -> CANNOT_PRICE (a missing face is not a "
        "zero)",
    ],
    "risk_ceiling_verdicts": [
        "deploying on a beta that is wrong by the whole held-back shift costs < 1.0pp of "
        "annualised residual vol -> THE_BETA_ERROR_IS_CHEAPER_THAN_THE_WAIT_IT_AVOIDS",
        "it costs >= 1.0pp -> THE_BETA_ERROR_IS_EXPENSIVE",
    ],
    "use_rule": ("a sizing block that prints a band and then declines to price the wait "
                 "is handing the reader back the only decision the band was meant to "
                 "inform"),
}


# ------------------------------------------------------------------ small helpers
def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def _rel(path: str) -> str:
    try:
        return os.path.relpath(path, ROOT).replace("\\", "/")
    except ValueError:
        return path


def _read_json(path: str):
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _sha_file(path: str) -> str:
    if not os.path.exists(path):
        return ""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def content_sha(face: dict) -> str:
    """Digest of a face's own content, with volatile envelope fields removed."""
    if not isinstance(face, dict):
        return ""
    body = {k: v for k, v in face.items()
            if k not in ("generated", "content_sha256", "elapsed_sec")}
    blob = json.dumps(body, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def fingerprint(path: str) -> dict:
    face = _read_json(path)
    return {
        "face": _rel(path),
        "file_sha256": _sha_file(path),
        "content_sha256": content_sha(face) if face else "",
        "generated": (face or {}).get("generated"),
        "evidence_cutoff": (face or {}).get("evidence_cutoff"),
    }


def risk_row(band: dict, label: str):
    for r in (band or {}).get("risk", {}).get("rows") or []:
        if r.get("label") == label:
            return r
    return None


def lots_row(band: dict):
    for r in (band or {}).get("ladder") or []:
        if r.get("arm") == "etf" and float(r.get("capital") or 0) == LENS_CNY:
            return r
    return None


# ------------------------------------------------------------------ the arithmetic
def periods_needed(n0: float, shrink: float) -> float:
    """se(n) = se(n0)*sqrt(n0/n); se/shrink -> n = n0/shrink**2."""
    if not n0 or not shrink or shrink <= 0:
        return float("nan")
    return float(n0) / (float(shrink) ** 2)


def years_to_band(n0: float, ppy: float, shrink: float) -> tuple:
    n_target = periods_needed(n0, shrink)
    return (n_target - float(n0)) / float(ppy), n_target


def wait_price_pp(book_vol: float, hedged_vol: float) -> float:
    """Yearly volatility carried for nothing while the position is off."""
    return (float(book_vol) - float(hedged_vol)) * 100.0


def decide_wait(ratio) -> tuple:
    if ratio is None:
        return ("CANNOT_PRICE", "the wait cannot be priced without both an exposure "
                                "and the band it is waiting on")
    if ratio >= CHEAP_RATIO:
        return ("WAITING_IS_THE_EXPENSIVE_INSURANCE",
                "the wait pays back less risk per year than the exposure it keeps on "
                "the book")
    return ("WAITING_IS_THE_CHEAPER_INSURANCE",
            "the wait removes more risk per year than the exposure it keeps")


def decide_risk_ceiling(ceiling_pp, line_pp: float = 1.0) -> tuple:
    if ceiling_pp is None:
        return ("CANNOT_PRICE", "the deployment's risk ceiling is not readable")
    if ceiling_pp < line_pp:
        return ("THE_BETA_ERROR_IS_CHEAPER_THAN_THE_WAIT_IT_AVOIDS",
                "being wrong about the beta by the whole held-back shift costs less "
                "than one year of not being hedged")
    return ("THE_BETA_ERROR_IS_EXPENSIVE",
            "the beta error alone costs more than the line the family calls cheap")


def build_face() -> dict:
    band = _read_json(BAND_FACE)
    funding = _read_json(FUNDING_FACE)
    beta = _read_json(BETA_FACE)

    parents = {
        "band": fingerprint(BAND_FACE),
        "funding": fingerprint(FUNDING_FACE),
        "beta": fingerprint(BETA_FACE),
    }

    if not band or not band.get("risk") or not band.get("fit"):
        return {
            "kind": "hedge_deploy_wait",
            "machine": "bm-c",
            "evidence_cutoff": (band or {}).get("evidence_cutoff"),
            "generated": _now(),
            "parents": parents,
            "prereg": PREREG,
            "verdict": "CANNOT_PRICE",
            "verdict_why": "band face missing or unreadable",
            "sentence": "band 面缺或读不出，等待价格无从计算（缺面不等于免费）。",
            "inputs_ok": False,
        }

    risk = band.get("risk") or {}
    fit = (band.get("fit") or {}).get("etf_in_sample") or {}
    spec = band.get("spec") or {}
    ppy = float(spec.get("periods_per_year") or PPY)

    book_vol = float(risk.get("book_annual_vol") or 0.0)
    r_point = risk_row(band, "point") or {}
    r_one = risk_row(band, "one_unit") or {}
    r_oos = risk_row(band, "oos_beta") or {}
    r_low = risk_row(band, "ci_low") or {}
    r_high = risk_row(band, "ci_high") or {}

    resid_point = float(r_point.get("residual_annual_vol") or 0.0)
    resid_one = float(r_one.get("residual_annual_vol") or 0.0)
    resid_oos = float(r_oos.get("residual_annual_vol") or 0.0)

    n0 = float(fit.get("n") or 0)
    se0 = float(fit.get("se_beta") or 0.0)
    beta_point = float(fit.get("beta") or 0.0)
    beta_oos = float((band.get("fit") or {}).get("etf_out_of_sample", {}).get("beta")
                     or 0.0)
    ci_width = float(fit.get("ci_width") or 0.0)

    lots = lots_row(band) or {}
    lots_needed = float(lots.get("lots_needed") or 0.0)
    band_low = float(lots.get("lots_band_low") or 0.0)
    band_high = float(lots.get("lots_band_high") or 0.0)

    gap_pp = None
    if funding:
        g = funding.get("carrier_leg_gap_pp")
        if g is not None:
            gap_pp = float(g)

    # ---- the wait: how long, and what it costs while it runs
    wait_years, n_target = years_to_band(n0, ppy, TARGET_BAND_SHRINK)
    target_band_lots = band_high - band_low
    target_band_lots = target_band_lots * TARGET_BAND_SHRINK

    # yearly cost of being unhedged = book vol - hedged residual (point estimate)
    yearly_cost_pp = wait_price_pp(book_vol, resid_point)
    # the wait's own ceiling benefit: residual of a perfect beta minus the point estimate
    wait_ceiling_pp = (resid_point - resid_one) * 100.0

    total_cost_pp = yearly_cost_pp * wait_years
    total_benefit_pp = wait_ceiling_pp
    ratio = None
    if total_benefit_pp > TOL:
        ratio = total_cost_pp / total_benefit_pp
    elif total_cost_pp <= TOL:
        ratio = 1.0  # free wait with no benefit is a tie, not a division by zero

    verdict, verdict_why = decide_wait(ratio)

    # ---- deploy and be wrong: the held-back beta is the family's own printed error
    wrong_shift_pp = (resid_oos - resid_point) * 100.0
    wrong_shift_abs = abs(wrong_shift_pp)
    risk_ceiling_verdict, risk_ceiling_why = decide_risk_ceiling(wrong_shift_abs)
    ratio_ceiling = (yearly_cost_pp / wrong_shift_abs
                     if wrong_shift_abs > TOL else None)

    # ---- money lens (per 1,000,000)
    yearly_cost_cny = yearly_cost_pp / 100.0 * LENS_CNY
    wait_ceiling_cny = wait_ceiling_pp / 100.0 * LENS_CNY
    total_cost_cny = total_cost_pp / 100.0 * LENS_CNY
    wrong_shift_cny = wrong_shift_abs / 100.0 * LENS_CNY

    arms = [
        {
            "name": "deploy_now",
            "beta": round(beta_point, 4),
            "lots": round(lots_needed, 2),
            "band_lots": [round(band_low, 2), round(band_high, 2)],
            "residual_vol_pct": round(resid_point * 100.0, 3),
            "carrier_gap_pp": None if gap_pp is None else round(gap_pp, 4),
            "what_it_keeps": "no time unhedged",
        },
        {
            "name": "wait_for_half_band",
            "target_band_lots": round(target_band_lots, 2),
            "years": round(wait_years, 3),
            "periods_added": round(n_target - n0, 2),
            "residual_vol_pct_if_perfect": round(resid_one * 100.0, 3),
            "residual_vol_pct_at_point": round(resid_point * 100.0, 3),
            "unhedged_vol_pct": round(book_vol * 100.0, 3),
            "yearly_cost_pp": round(yearly_cost_pp, 4),
            "yearly_cost_cny": round(yearly_cost_cny, 1),
            "total_cost_pp": round(total_cost_pp, 3),
            "total_cost_cny": round(total_cost_cny, 1),
            "benefit_ceiling_pp": round(total_benefit_pp, 4),
            "benefit_ceiling_cny": round(wait_ceiling_cny, 1),
            "ratio_cost_over_benefit": None if ratio is None else round(ratio, 2),
        },
        {
            "name": "deploy_and_be_wrong",
            "beta_used": round(beta_point, 4),
            "true_beta": round(beta_oos, 4),
            "beta_error": round(abs(beta_oos - beta_point), 4),
            "beta_error_pct_of_point": (round(abs(beta_oos - beta_point)
                                              / beta_point * 100.0, 2)
                                        if beta_point else None),
            "residual_vol_at_used_pct": round(resid_point * 100.0, 3),
            "residual_vol_at_true_pct": round(resid_oos * 100.0, 3),
            "risk_ceiling_pp": round(wrong_shift_abs, 4),
            "risk_ceiling_cny": round(wrong_shift_cny, 1),
            "one_year_of_wait_pp": round(yearly_cost_pp, 4),
            "ratio_wait_over_ceiling": (None if ratio_ceiling is None
                                        else round(ratio_ceiling, 2)),
        },
    ]

    sentence = (
        "现在按 beta=%.4f 部署 %s 手（90.13%% 账本），残差年化波动 %.3f%%；"
        "要等到 95%% 带宽减半需再采 %.2f 期（%.2f 年，按 %.1f 期/年），"
        "而等待期账本是裸的、每年多扛 %.3fpp 波动（每百万 %s 元），"
        "等满 %.2f 年共付 %.1fpp（%s 元），换来的是残差从 %.3f%% 降到 %.3f%%，"
        "天花板只有 %.3fpp（%s 元）——等待的价签是它买到保险的 %.0f 倍。"
        "反过来，就算 beta 一直错着（用点估计 %.4f 而真值 %.4f，差 %.2f%%），"
        "残差也只多 %.3fpp（%s 元），是等一年要付的 %.3fpp 的 1/%.0f。"
        % (beta_point, _cny_cell(lots_needed), resid_point * 100.0,
           n_target - n0, wait_years, ppy,
           yearly_cost_pp, _cny_cell(yearly_cost_cny),
           wait_years, total_cost_pp, _cny_cell(total_cost_cny),
           resid_point * 100.0, resid_one * 100.0,
           total_benefit_pp, _cny_cell(wait_ceiling_cny),
           ratio if ratio is not None else float("nan"),
           beta_point, beta_oos,
           (abs(beta_oos - beta_point) / beta_point * 100.0) if beta_point else 0.0,
           wrong_shift_abs, _cny_cell(wrong_shift_cny), yearly_cost_pp,
           ratio_ceiling if ratio_ceiling else float("nan")))

    return {
        "kind": "hedge_deploy_wait",
        "machine": "bm-c",
        "evidence_cutoff": (band or {}).get("evidence_cutoff"),
        "generated": _now(),
        "parents": parents,
        "prereg": PREREG,
        "inputs_ok": True,
        "spec": {
            "periods_per_year": ppy,
            "lens_cny": LENS_CNY,
            "target_band_shrink": TARGET_BAND_SHRINK,
            "n0_periods": n0,
            "se_beta": round(se0, 6),
            "ci_width_beta": round(ci_width, 6),
            "beta_point": round(beta_point, 6),
            "beta_oos": round(beta_oos, 6),
            "book_annual_vol": round(book_vol, 6),
        },
        "arms": arms,
        "wait": {
            "years": round(wait_years, 3),
            "periods_added": round(n_target - n0, 2),
            "target_band_lots": round(target_band_lots, 2),
            "yearly_cost_pp": round(yearly_cost_pp, 4),
            "yearly_cost_cny": round(yearly_cost_cny, 1),
            "total_cost_pp": round(total_cost_pp, 3),
            "total_cost_cny": round(total_cost_cny, 1),
            "benefit_ceiling_pp": round(total_benefit_pp, 4),
            "benefit_ceiling_cny": round(wait_ceiling_cny, 1),
            "ratio_cost_over_benefit": None if ratio is None else round(ratio, 2),
            "verdict": verdict,
            "verdict_why": verdict_why,
        },
        "risk_ceiling": {
            "beta_used": round(beta_point, 6),
            "true_beta": round(beta_oos, 6),
            "beta_error": round(abs(beta_oos - beta_point), 6),
            "risk_ceiling_pp": round(wrong_shift_abs, 4),
            "risk_ceiling_cny": round(wrong_shift_cny, 1),
            "one_year_of_wait_pp": round(yearly_cost_pp, 4),
            "ratio_wait_over_ceiling": (None if ratio_ceiling is None
                                        else round(ratio_ceiling, 2)),
            "verdict": risk_ceiling_verdict,
            "verdict_why": risk_ceiling_why,
        },
        "verdict": verdict,
        "verdict_why": verdict_why,
        "risk_ceiling_verdict": risk_ceiling_verdict,
        "sentence": sentence,
        "reads": [
            "deploy_now: the point estimate is on the ticket, nothing is waiting",
            "wait_for_half_band: the band halves only after four times the periods; "
            "every year of it is a year the book is not hedged",
            "deploy_and_be_wrong: the held-back beta is this family's own printed "
            "estimate of how wrong the point estimate can be, so its residual "
            "difference is the deployment's risk ceiling",
        ],
    }


def _cny_cell(x) -> str:
    try:
        return "{:,.0f}".format(float(x))
    except (TypeError, ValueError):
        return "?"


def _f(x, digits: int = 3) -> str:
    try:
        return ("%%.%df" % digits) % float(x)
    except (TypeError, ValueError):
        return "?"


def _pct(x, digits: int = 2) -> str:
    try:
        return ("%%.%df%%%%" % digits) % (float(x) * 100.0)
    except (TypeError, ValueError):
        return "?"


def render_md(face: dict) -> str:
    L = []
    L.append("<!-- BEGIN:ASTOCK-VETO-HEDGE-DEPLOY-WAIT -->")
    L.append("# 现在部署，还是等带宽变窄？")
    L.append("")
    L.append("`%s` · `%s`" % (face.get("verdict"), face.get("risk_ceiling_verdict")))
    L.append("")
    L.append("generated %s | evidence_cutoff **%s** | machine `%s`"
             % (face.get("generated"), face.get("evidence_cutoff"),
                face.get("machine")))
    L.append("")
    if not face.get("inputs_ok"):
        L.append("## 无法定价")
        L.append("")
        L.append("- %s" % face.get("verdict_why"))
        L.append("- 缺一张父面不等于等待是免费的：本面的所有读数都来自已发布的父面。")
        L.append("")
        L.append("Machine `bm-c`, generated %s." % face.get("generated"))
        L.append("<!-- END:ASTOCK-VETO-HEDGE-DEPLOY-WAIT -->")
        return "\n".join(L) + "\n"

    spec = face.get("spec") or {}
    wait = face.get("wait") or {}
    rc = face.get("risk_ceiling") or {}
    a0, a1, a2 = face.get("arms")[0], face.get("arms")[1], face.get("arms")[2]

    L.append("## 1. 一句话")
    L.append("")
    L.append("- %s" % face.get("sentence"))
    L.append("")

    L.append("## 2. 为什么这一面存在")
    L.append("")
    L.append("r2033 把两条载体放上同一把尺，r2036 给它付了抵押与租金，r2037 把同样 52 期切五刀，"
             "发现**符号稳、幅度在缩**（最新一季只剩 0.61pp，中位块 3.05pp）。三面都在同一句上收口：")
    L.append("")
    L.append("> beta 自己的 95%% 带宽跨 %s 手，更窄的带子可以用更多期数据换，"
             "代价是用读者还看不到的数据去拟合。**本面不选这个交易**。"
             % _cny_cell(a0["band_lots"][1] - a0["band_lots"][0]))
    L.append("")
    L.append("这句话把一个决定留在桌上了：**现在下单，还是等带子变窄再下单？** 本面选它，"
             "而且选的方式是给这个家族从没标过价的东西开一张价签——**等待期你在付什么**。")
    L.append("")

    L.append("## 3. 三个口径，一张价签")
    L.append("")
    L.append("| 臂 | beta | 手数 | 95% 带（手） | 残差年化波动 | 等待期暴露 |")
    L.append("|---|---|---|---|---|---|")
    L.append("| **deploy_now** | %.4f | %s | %s .. %s | **%.3f%%** | 无（一开始就对冲） |"
             % (a0["beta"], _cny_cell(a0["lots"]),
                _cny_cell(a0["band_lots"][0]), _cny_cell(a0["band_lots"][1]),
                a0["residual_vol_pct"]))
    L.append("| **wait_for_half_band** | 完美 beta | — | 目标 %s（半宽） | %.3f%%（天花板） | **%.3f%% 裸账本** |"
             % (_cny_cell(a1["target_band_lots"]),
                a1["residual_vol_pct_if_perfect"], a1["unhedged_vol_pct"]))
    L.append("| **deploy_and_be_wrong** | %.4f（真值 %.4f） | — | — | %.3f%% | 无 |"
             % (a2["beta_used"], a2["true_beta"], a2["residual_vol_at_true_pct"]))
    L.append("")

    L.append("## 4. 等待的价格：一年多少钱")
    L.append("")
    L.append("带宽减半 = 标准误减半 = **四倍期数**（se ∝ 1/√n）。当前 %s 期，"
             "目标 %s 期，按 %.1f 期/年算要**再等 %.2f 年**。"
             % (_cny_cell(spec.get("n0_periods")), _cny_cell(wait.get("periods_added")
                                                              and spec.get("n0_periods", 0)
                                                              + wait.get("periods_added", 0)),
                spec.get("periods_per_year", PPY), wait.get("years")))
    L.append("")
    L.append("- **等待期每年多扛的波动** = 账本自带的 %.3f%% 减去对冲后的 %.3f%% = **%.3fpp**"
             "（每百万 **%s 元/年**）"
             % (a1["unhedged_vol_pct"], a1["residual_vol_pct_at_point"],
                wait.get("yearly_cost_pp"), _cny_cell(wait.get("yearly_cost_cny"))))
    L.append("- **等满 %.2f 年的总价** = %.3fpp × %.2f 年 = **%.1fpp**（每百万 **%s 元**）"
             % (wait.get("years"), wait.get("yearly_cost_pp"), wait.get("years"),
                wait.get("total_cost_pp"), _cny_cell(wait.get("total_cost_cny"))))
    L.append("- **等到的天花板收益** = 残差从 %.3f%% 降到 %.3f%% = **%.3fpp**（每百万 **%s 元**）"
             % (a1["residual_vol_pct_at_point"], a1["residual_vol_pct_if_perfect"],
                wait.get("benefit_ceiling_pp"), _cny_cell(wait.get("benefit_ceiling_cny"))))
    L.append("- **倍率** = %.1fpp ÷ %.3fpp = **%.0f 倍** → `%s`"
             % (wait.get("total_cost_pp"), wait.get("benefit_ceiling_pp"),
                wait.get("ratio_cost_over_benefit") or float("nan"),
                wait.get("verdict")))
    L.append("")
    L.append("> 判词的理由：%s。" % wait.get("verdict_why"))
    L.append("")

    L.append("## 5. 反过来：部署错了要付多少")
    L.append("")
    L.append("band 面自己印了样本外 beta = **%.4f**，与点估计 **%.4f** 差 **%.4f**"
             "（点估计的 %.2f%%）。这是这个家族自己给出的「beta 能错多少」的估计，"
             "所以用它算出来的残差差就是**部署的风险上界**。"
             % (rc.get("true_beta"), rc.get("beta_used"), rc.get("beta_error"),
                a2.get("beta_error_pct_of_point") or 0.0))
    L.append("")
    L.append("| 用什么 beta | 残差年化波动 | 相对点估计 |")
    L.append("|---|---|---|")
    L.append("| %.4f（点估计，部署） | %.3f%% | +0.000pp |"
             % (rc.get("beta_used"), a2["residual_vol_at_used_pct"]))
    L.append("| %.4f（样本外真值） | %.3f%% | %+.4fpp（部署多付） |"
             % (rc.get("true_beta"), a2["residual_vol_at_true_pct"],
                float(rc.get("risk_ceiling_pp") or 0.0)))
    L.append("")
    L.append("- **部署的风险上界** = **%.3fpp** 波动（每百万 **%s 元/年**）"
             % (rc.get("risk_ceiling_pp"), _cny_cell(rc.get("risk_ceiling_cny"))))
    L.append("- **等一年要付** = **%.3fpp**（每百万 %s 元）"
             % (rc.get("one_year_of_wait_pp"),
                _cny_cell(float(rc.get("one_year_of_wait_pp") or 0) / 100.0 * LENS_CNY)))
    L.append("- **倍率** = %.3f ÷ %.3f = **%.0f 倍** → `%s`"
             % (rc.get("one_year_of_wait_pp"), rc.get("risk_ceiling_pp"),
                rc.get("ratio_wait_over_ceiling") or float("nan"),
                rc.get("verdict")))
    L.append("")
    L.append("> %s。" % rc.get("verdict_why"))
    L.append("")

    L.append("## 6. 判词与它的边界")
    L.append("")
    L.append("**主判词** `%s`：等待是一份昂贵的保险——它每年付出去的波动，"
             "是它买回来的风险降低的 %.0f 倍。"
             % (face.get("verdict"), wait.get("ratio_cost_over_benefit") or float("nan")))
    L.append("")
    L.append("**副判词** `%s`：就算 beta 错到底（用点估计而真值是样本外的 %.4f），"
             "部署的风险上界也只有 %.3fpp，是等一年要付的 1/%.0f。"
             % (face.get("risk_ceiling_verdict"), rc.get("true_beta"),
                rc.get("risk_ceiling_pp"), rc.get("ratio_wait_over_ceiling") or 0.0))
    L.append("")
    L.append("**本面不说的**：")
    L.append("")
    L.append("- 不说这个对冲值不值得做——那是 BUDGET 面的价签，本面只给「现在 vs 等」定级。")
    L.append("- 不说等待期一定要完全裸奔：一个跑部分对冲（比如 BUDGET 面规则 A 的 k=0.65）"
             "的读者付的等待费比这里少，本面价的是**完全不对冲**的等待。")
    L.append("- 不说 beta 在等待期是常数：band 面的滚动拟合范围 0.885..1.280，"
             "这 0.395 的移动比任何采样带宽都大，本面只把「带宽」当等待的理由，"
             "不把「beta 会动」当成等待的理由。")
    L.append("- 不说 52 期代表未来 regime——r2037 已明说符号稳不等于样本公平，本面沿用。")
    L.append("- 口径是每 %s 元的镜头，票面自己的成本腿（每边 13.041bp × 换手）不是同一个量，"
             "两者不相加。" % _cny_cell(LENS_CNY))
    L.append("")

    L.append("## 7. 复现")
    L.append("")
    L.append("```")
    L.append("python scripts/astock_veto_hedge_deploy_wait.py selftest")
    L.append("python scripts/astock_veto_hedge_deploy_wait.py run")
    L.append("python scripts/astock_veto_hedge_deploy_wait.py check")
    L.append("```")
    L.append("")
    L.append("Machine `bm-c`, generated %s." % face.get("generated"))
    L.append("<!-- END:ASTOCK-VETO-HEDGE-DEPLOY-WAIT -->")
    return "\n".join(L) + "\n"


# ------------------------------------------------------------------ modes
def run(write: bool = True) -> int:
    face = build_face()
    if not face.get("inputs_ok"):
        print("CANNOT_PRICE: %s" % face.get("verdict_why"))
        return 2
    t0 = time.time()
    if write:
        os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
        os.makedirs(os.path.dirname(OUT_MD), exist_ok=True)
        with open(OUT_JSON, "w", encoding="utf-8") as f:
            json.dump(face, f, ensure_ascii=False, indent=1, sort_keys=True)
        with open(OUT_MD, "w", encoding="utf-8") as f:
            f.write(render_md(face))
    print("verdict=%s" % face.get("verdict"))
    print("risk_ceiling=%s" % face.get("risk_ceiling_verdict"))
    print("wait_years=%.3f  yearly_cost_pp=%.4f  ratio=%.2f"
          % (face["wait"]["years"], face["wait"]["yearly_cost_pp"],
             face["wait"]["ratio_cost_over_benefit"] or float("nan")))
    print("elapsed=%.3fs" % (time.time() - t0))
    return 0


def check() -> int:
    """Re-derive from parents and name what moved.

    Two kinds of red kept apart (r1934): an upstream that moved one step is STALE and is
    repaired by `run`; a number that disagrees with its own inputs is CHECK FAILED.

    Reads the module-level paths (not default arguments) so a control can point them at a
    throwaway copy -- r2037's negative control depends on the same property.
    """
    json_path, md_path = OUT_JSON, OUT_MD
    problems = []
    if not os.path.exists(json_path):
        print("STALE: face missing (%s)" % _rel(json_path))
        return 3
    face = _read_json(json_path)
    fresh = build_face()

    for key in ("band", "funding", "beta"):
        a = (face.get("parents") or {}).get(key) or {}
        b = (fresh.get("parents") or {}).get(key) or {}
        if a.get("content_sha256") != b.get("content_sha256"):
            problems.append("STALE: parent %s content moved (%s -> %s)"
                            % (key, str(a.get("content_sha256"))[:12],
                               str(b.get("content_sha256"))[:12]))
        elif a.get("file_sha256") != b.get("file_sha256"):
            # same parsed body, different bytes: a re-write that added no information is
            # still a moved parent (r1934: the byte face is the contract, not the dict)
            problems.append("STALE: parent %s bytes moved (%s -> %s)"
                            % (key, str(a.get("file_sha256"))[:12],
                               str(b.get("file_sha256"))[:12]))

    stale = [p for p in problems if p.startswith("STALE")]
    if stale:
        for p in problems:
            print(p)
        return 3

    # every published number must re-derive from the parents
    try:
        for key in ("verdict", "risk_ceiling_verdict", "evidence_cutoff", "machine"):
            if face.get(key) != fresh.get(key):
                problems.append("CHECK FAILED: %s moved (%r -> %r)"
                                % (key, face.get(key), fresh.get(key)))
        for key in ("yearly_cost_pp", "total_cost_pp", "benefit_ceiling_pp", "years"):
            a = (face.get("wait") or {}).get(key)
            b = (fresh.get("wait") or {}).get(key)
            if a is None or b is None or abs(float(a) - float(b)) > 1e-6:
                problems.append("CHECK FAILED: wait.%s moved (%r -> %r)" % (key, a, b))
        for key in ("risk_ceiling_pp", "beta_error"):
            a = (face.get("risk_ceiling") or {}).get(key)
            b = (fresh.get("risk_ceiling") or {}).get(key)
            if a is None or b is None or abs(float(a) - float(b)) > 1e-6:
                problems.append("CHECK FAILED: risk_ceiling.%s moved (%r -> %r)"
                                % (key, a, b))
        # the ratio must equal its own two operands
        w = face.get("wait") or {}
        if w.get("ratio_cost_over_benefit") is not None and w.get("benefit_ceiling_pp"):
            calc = float(w["total_cost_pp"]) / float(w["benefit_ceiling_pp"])
            # the stored operands are rounded, so the ratio re-derives to ~1e-3 relative
            if abs(calc - float(w["ratio_cost_over_benefit"])) > 1e-3 * max(1.0, abs(calc)):
                problems.append("CHECK FAILED: wait ratio != total/benefit (%.4f vs %.4f)"
                                % (calc, float(w["ratio_cost_over_benefit"])))
    except (TypeError, ValueError) as exc:
        problems.append("CHECK FAILED: unreadable number (%s)" % exc)

    # the page must carry both tokens
    if not os.path.exists(md_path):
        problems.append("STALE: page missing (%s)" % _rel(md_path))
    else:
        with open(md_path, "r", encoding="utf-8") as f:
            page = f.read()
        for token in (face.get("verdict"), face.get("risk_ceiling_verdict")):
            if token and token not in page:
                problems.append("CHECK FAILED: page missing token %s" % token)

    # content hash must describe the face
    body = {k: v for k, v in face.items()
            if k not in ("generated", "content_sha256", "elapsed_sec")}
    digest = content_sha(face)
    if face.get("content_sha256") and face["content_sha256"] != digest:
        problems.append("CHECK FAILED: content_sha256 does not describe the face")
    if not face.get("content_sha256"):
        face["content_sha256"] = digest
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(face, f, ensure_ascii=False, indent=1, sort_keys=True)

    if problems:
        for p in problems:
            print(p)
        return 3
    print("CHECK_OK: %d parents, %d arms, 0 problems"
          % (len(face.get("parents") or {}), len(face.get("arms") or [])))
    return 0


def selftest() -> int:
    ok = 0
    fail = 0

    def chk(name, cond):
        nonlocal ok, fail
        if cond:
            ok += 1
        else:
            fail += 1
            print("FAIL: %s" % name)

    # ---- pure arithmetic legs
    chk("se halves when periods quadruple",
        abs(periods_needed(43, 0.5) - 172.0) < 1e-9)
    chk("periods_needed of a full band is n0",
        abs(periods_needed(43, 1.0) - 43.0) < 1e-9)
    y, n = years_to_band(43, 12.6, 0.5)
    chk("years to half band is (172-43)/12.6", abs(y - 129.0 / 12.6) < 1e-9)
    chk("target periods is 172", abs(n - 172.0) < 1e-9)
    chk("wait price is book minus hedged",
        abs(wait_price_pp(0.27343, 0.10763) - 16.58) < 1e-6)
    chk("wait price is zero when nothing is removed",
        abs(wait_price_pp(0.10, 0.10)) < 1e-12)

    # ---- verdict legs
    v, _ = decide_wait(100.0)
    chk("ratio above 1 is expensive insurance",
        v == "WAITING_IS_THE_EXPENSIVE_INSURANCE")
    v, _ = decide_wait(0.5)
    chk("ratio below 1 is cheaper insurance", v == "WAITING_IS_THE_CHEAPER_INSURANCE")
    v, _ = decide_wait(None)
    chk("no ratio cannot be priced", v == "CANNOT_PRICE")
    v, _ = decide_risk_ceiling(0.054)
    chk("a small beta error is cheap",
        v == "THE_BETA_ERROR_IS_CHEAPER_THAN_THE_WAIT_IT_AVOIDS")
    v, _ = decide_risk_ceiling(2.5)
    chk("a large beta error is expensive", v == "THE_BETA_ERROR_IS_EXPENSIVE")

    # ---- the face itself, from the real parents
    face = build_face()
    chk("face has inputs", bool(face.get("inputs_ok")))
    chk("face has three arms", len(face.get("arms") or []) == 3)
    chk("face names a wait verdict", bool(face.get("verdict")))
    chk("face names a risk verdict", bool(face.get("risk_ceiling_verdict")))
    chk("face has three parents", len(face.get("parents") or {}) == 3)
    chk("deploy arm keeps its band", (face["arms"][0].get("band_lots") or []) and
        face["arms"][0]["band_lots"][1] > face["arms"][0]["band_lots"][0])
    chk("wait arm reports a positive cost", float(face["wait"]["total_cost_pp"]) > 0)
    chk("wait arm reports a positive ceiling",
        float(face["wait"]["benefit_ceiling_pp"]) > 0)
    chk("wait ratio equals total over ceiling",
        abs(float(face["wait"]["ratio_cost_over_benefit"])
            - float(face["wait"]["total_cost_pp"])
            / float(face["wait"]["benefit_ceiling_pp"]))
        <= 1e-3 * max(1.0, float(face["wait"]["ratio_cost_over_benefit"])))
    chk("risk ceiling is the held-back shift",
        abs(float(face["risk_ceiling"]["risk_ceiling_pp"])
            - abs(face["arms"][2]["residual_vol_at_true_pct"]
                  - face["arms"][2]["residual_vol_at_used_pct"])) < 1e-3)
    chk("wait is expensive by this face's own arithmetic",
        float(face["wait"]["ratio_cost_over_benefit"]) > 1.0)
    chk("beta error is cheap by this face's own arithmetic",
        float(face["risk_ceiling"]["risk_ceiling_pp"]) < 1.0)

    # ---- the page renders and carries both tokens
    page = render_md(face)
    chk("page carries the wait verdict", face["verdict"] in page)
    chk("page carries the risk verdict", face["risk_ceiling_verdict"] in page)
    chk("page has a begin marker", "BEGIN:ASTOCK-VETO-HEDGE-DEPLOY-WAIT" in page)
    chk("page has an end marker", "END:ASTOCK-VETO-HEDGE-DEPLOY-WAIT" in page)
    chk("page prints the wait years", "%.2f" % face["wait"]["years"] in page)

    print("%d/%d PASS" % (ok, ok + fail))
    return 0 if fail == 0 else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("mode", nargs="?", default="run",
                    choices=["run", "check", "selftest"])
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args(argv)
    if args.mode == "selftest":
        return selftest()
    if args.mode == "check":
        return check()
    return run(write=not args.no_write)


if __name__ == "__main__":
    sys.exit(main())

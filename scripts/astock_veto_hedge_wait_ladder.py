"""The wait, priced as a function of the hedge you keep on while you wait (r2039, bm-c).

r2038 priced the wait as one number: if you keep nothing hedged while the beta band
narrows, you carry 16.580pp of annualised volatility for 10.24 years, against a ceiling
of 0.124pp of residual volatility removed -- 1367x.  It said, in its own boundaries,
that a reader running a partial hedge (e.g. the budget face's rule-A k=0.65) pays less
than that price.  This face prices that sentence.

The lever is not new data.  The band face publishes five residual-volatility rows at
five betas, and those five rows are not five independent measurements: the residual of
`book - k*hedge` is a three-parameter quadratic in k,

    R(k)**2 = Var(book) - 2k*Cov(book, hedge) + k**2*Var(hedge),

so five rows over-determine three parameters and two rows are a check.  Fitting them
recovers the book's own annual volatility to the digit the band face prints it, and
recovers the residual-minimising ratio -- which is the full-window OLS slope the band
face also prints.  Two published faces therefore agree through an identity, and the
same identity turns any hedge ratio between 0 and 1.1 into a wait price.

What it finds:
  * the wait is cheap only above k=0.8986 (3,522 lots) -- the hedge has to be almost
    entirely on before holding the rest back stops costing more than the band is worth;
  * at the budget face's rule-A k=0.65 (2,547 lots) the wait still costs 2.724pp a year,
    224x its ceiling;
  * the ceiling the wait is chasing (0.124pp) is what unit beta already earns today
    (10.639% vs 10.763%) -- the drop is available by moving the ratio, not by waiting;
  * and the deployed point estimate is the worst of the three betas the face publishes
    on the window it evaluates them on.

No new data, no re-fitting of the strategy, no re-pricing of the hedge's own edge, no
claim that any ratio should be chosen.  The wait is priced across hedges, not decided.

Modes:
    python scripts/astock_veto_hedge_wait_ladder.py selftest
    python scripts/astock_veto_hedge_wait_ladder.py run
    python scripts/astock_veto_hedge_wait_ladder.py check
"""

import argparse
import hashlib
import json
import math
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_JSON = os.path.join(ROOT, "results", "astock_veto_hedge_wait_ladder.json")
OUT_MD = os.path.join(ROOT, "research", "ASTOCK_VETO_HEDGE_WAIT_LADDER.md")
BAND_FACE = os.path.join(ROOT, "results", "astock_veto_hedge_band.json")
WAIT_FACE = os.path.join(ROOT, "results", "astock_veto_hedge_deploy_wait.json")

LENS_CNY = 1000000.0
TARGET_BAND_SHRINK = 0.5
TOL = 1e-12
# the ratio the budget face's rule A uses; this face prices the wait at that hedge
RULE_A_HEDGE = 0.65
# the ladder printed on the page; 1.0263 is the face's own out-of-sample beta
LADDER_K = (0.0, 0.25, 0.50, 0.65, 0.75, 0.85, 0.90, 0.95, 1.00, 1.0263)

PREREG = {
    "question": "the deploy-or-wait face priced the wait with the hedge entirely off.  "
                "What does the same wait cost a reader who keeps some of the hedge on "
                "while the band narrows, and how much of the hedge has to be on before "
                "waiting stops being more expensive than the band it waits for?",
    "error_model": "residual(k)**2 = Var(book) - 2k*Cov + k**2*Var(hedge) is an identity, "
                   "not a model: the band face's five published residual rows are fitted "
                   "to its three parameters by least squares, and the two rows not needed "
                   "for the fit are carried as the check.  The wait's length and ceiling "
                   "are read from the deploy-or-wait face and the band face, never "
                   "re-derived from the panel.",
    "wait_definition": "'wait' still means the rest of the hedge is not on until the band "
                       "reaches its target.  k is the hedge ratio actually carried during "
                       "the wait, in units of the book; k=1.0 is 3,919 lots at the face's "
                       "own lot step.  The reference the wait is priced against is the "
                       "full point-estimate hedge, so cost(k) = R(k) - R(k_ref).",
    "verdicts": [
        "R(1.0) removes as much residual volatility as the wait's own ceiling -> "
        "THE_CEILING_IS_A_RATIO_NOT_A_WAIT",
        "ratio at the rule-A hedge >= 1.0 -> PARTIAL_HEDGING_DOES_NOT_MAKE_THE_WAIT_CHEAP",
        "ratio at the rule-A hedge < 1.0 -> A_PARTIAL_HEDGE_MAKES_THE_WAIT_CHEAP",
        "the point estimate's residual is above both the unit-beta and the out-of-sample "
        "residuals -> THE_POINT_ESTIMATE_IS_THE_WORST_OF_THREE_BETAS",
        "the break-even hedge is at least half the deployed hedge -> "
        "YOU_MUST_ALREADY_HOLD_MOST_OF_THE_HEDGE",
        "the break-even hedge is below half the deployed hedge -> "
        "THE_WAIT_SURVIVES_A_THIN_HEDGE",
        "the band face is missing or unreadable -> CANNOT_PRICE (a missing face is not a zero)",
    ],
    "not_done_here": "no new data, no re-fitting of beta, no re-pricing of the hedge's own "
                     "edge, no choice of hedge ratio -- this face prices the wait across "
                     "hedges; it does not recommend one",
}


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


# ------------------------------------------------------------------ the identity
def solve_quadratic(rows) -> dict:
    """Recover Var(book), Cov, Var(hedge) from the published residual rows.

    R(beta)**2 is linear in (1, -2*beta, beta**2), so three rows determine the three
    parameters and any further rows are the check.  Solved with a normal-equation
    least squares: five rows, three unknowns, exact to machine precision when the
    rows are internally consistent.
    """
    pts = [(float(r["beta"]), float(r["residual_annual_vol"]))
           for r in rows if r.get("beta") is not None
           and r.get("residual_annual_vol") is not None]
    if len(pts) < 3:
        return {}
    # normal equations for y = a + b*(-2k) + c*k**2
    ata = [[0.0] * 3 for _ in range(3)]
    aty = [0.0] * 3
    for beta, resid in pts:
        row = (1.0, -2.0 * beta, beta * beta)
        y = resid * resid
        for i in range(3):
            aty[i] += row[i] * y
            for j in range(3):
                ata[i][j] += row[i] * row[j]
    coef = _solve3(ata, aty)
    if coef is None:
        return {}
    var_book, cov, var_hedge = coef
    worst = 0.0
    for beta, resid in pts:
        pred = var_book - 2.0 * cov * beta + var_hedge * beta * beta
        worst = max(worst, abs(math.sqrt(max(0.0, pred)) - resid))
    return {
        "var_book": var_book,
        "cov": cov,
        "var_hedge": var_hedge,
        "rows_used": len(pts),
        "max_row_error": worst,
        "vertex": (cov / var_hedge) if var_hedge > 0 else None,
    }


def _solve3(a, b):
    """Tiny 3x3 Gaussian elimination with partial pivoting; no numpy dependency."""
    m = [list(a[i]) + [b[i]] for i in range(3)]
    for col in range(3):
        piv = max(range(col, 3), key=lambda r: abs(m[r][col]))
        if abs(m[piv][col]) < 1e-18:
            return None
        if piv != col:
            m[col], m[piv] = m[piv], m[col]
        pv = m[col][col]
        for j in range(col, 4):
            m[col][j] /= pv
        for r in range(3):
            if r == col:
                continue
            f = m[r][col]
            if f == 0.0:
                continue
            for j in range(col, 4):
                m[r][j] -= f * m[col][j]
    return (m[0][3], m[1][3], m[2][3])


def resid_at(k: float, quad: dict) -> float:
    """Annualised residual volatility of `book - k*hedge`, from the identity."""
    if not quad:
        return float("nan")
    r2 = (quad["var_book"] - 2.0 * float(k) * quad["cov"]
          + float(k) * float(k) * quad["var_hedge"])
    if r2 <= 0:
        return 0.0
    return math.sqrt(r2)


def wait_years(n0: float, ppy: float, shrink: float) -> float:
    """se(n) = se(n0)*sqrt(n0/n); halving the band needs four times the periods."""
    if not n0 or not ppy or not shrink or shrink <= 0:
        return float("nan")
    return (float(n0) / (float(shrink) ** 2) - float(n0)) / float(ppy)


def break_even_hedge(quad: dict, k_ref: float, target_pp: float,
                     k_hi: float = 1.4) -> dict:
    """Both ratios where the yearly wait cost equals ceiling/years.

    The residual is a parabola, so the break-even set is an interval.  Returns the
    low and high crossing; a crossing outside [0, k_hi] is reported as absent rather
    than clamped (r98 family: a missing answer is not a zero).
    """
    out = {"k_low": None, "k_high": None, "target_yearly_pp": target_pp}
    if not quad or target_pp is None or target_pp <= 0:
        return out
    base = resid_at(k_ref, quad)

    def over(k):
        return (resid_at(k, quad) - base) * 100.0 - target_pp > 0.0

    if over(0.0):
        lo, hi = 0.0, k_ref
        for _ in range(200):
            mid = 0.5 * (lo + hi)
            if over(mid):
                lo = mid
            else:
                hi = mid
        out["k_low"] = hi
    if over(k_hi):
        lo, hi = k_ref, k_hi
        for _ in range(200):
            mid = 0.5 * (lo + hi)
            if over(mid):
                hi = mid
            else:
                lo = mid
        out["k_high"] = lo
    return out


def decide_ceiling(gap_pp, ceiling_pp) -> tuple:
    if gap_pp is None or ceiling_pp is None or ceiling_pp <= TOL:
        return ("CANNOT_PRICE", "the ceiling or the ratio gap is missing")
    if gap_pp >= 0.99 * ceiling_pp:
        return ("THE_CEILING_IS_A_RATIO_NOT_A_WAIT",
                "moving the hedge to unit beta removes as much residual volatility as "
                "the wait is waiting for")
    return ("THE_CEILING_NEEDS_THE_WAIT",
            "unit beta does not reproduce the ceiling, so the wait buys something the "
            "ratio cannot")


def decide_ladder(ratio) -> tuple:
    if ratio is None:
        return ("CANNOT_PRICE", "the rule-A hedge could not be priced")
    if ratio >= 1.0:
        return ("PARTIAL_HEDGING_DOES_NOT_MAKE_THE_WAIT_CHEAP",
                "a hedge at the budget face's rule-A ratio still pays back less risk "
                "than the exposure it keeps on the book")
    return ("A_PARTIAL_HEDGE_MAKES_THE_WAIT_CHEAP",
            "at the budget face's rule-A ratio the wait already costs less than its "
            "ceiling")


def decide_point(resid_point, resid_one, resid_oos) -> tuple:
    if None in (resid_point, resid_one, resid_oos):
        return ("CANNOT_PRICE", "the published betas could not all be read")
    if resid_point > resid_one and resid_point > resid_oos:
        return ("THE_POINT_ESTIMATE_IS_THE_WORST_OF_THREE_BETAS",
                "on the window the face evaluates them on, both the unit-beta and the "
                "out-of-sample beta leave less residual volatility than the deployed one")
    return ("THE_POINT_ESTIMATE_IS_NOT_THE_WORST",
            "the deployed point estimate is not beaten by both of the other published "
            "betas")


def decide_holding(k_low, k_ref) -> tuple:
    if k_low is None or not k_ref:
        return ("CANNOT_PRICE", "the break-even hedge could not be bracketed")
    if k_low >= 0.5 * k_ref:
        return ("YOU_MUST_ALREADY_HOLD_MOST_OF_THE_HEDGE",
                "the hedge has to be at least %.1f%% of the deployed one before the wait "
                "stops costing more than it buys" % (100.0 * k_low / k_ref))
    return ("THE_WAIT_SURVIVES_A_THIN_HEDGE",
            "a hedge below half of the deployed one still leaves the wait cheap")


def rows_by_label(band: dict) -> dict:
    return {r.get("label"): r for r in ((band or {}).get("risk") or {}).get("rows") or []}


def etf_ladder_row(band: dict) -> dict:
    for r in (band or {}).get("ladder") or []:
        if r.get("arm") == "etf" and abs(float(r.get("capital") or 0) - LENS_CNY) < 1.0:
            return r
    return {}


# ------------------------------------------------------------------ the face
def build_face() -> dict:
    band = _read_json(BAND_FACE)
    wait = _read_json(WAIT_FACE)

    parents = {"band": fingerprint(BAND_FACE), "wait": fingerprint(WAIT_FACE)}

    if not band or not band.get("risk") or not band.get("fit"):
        return {
            "kind": "hedge_wait_ladder",
            "machine": "bm-c",
            "evidence_cutoff": (band or {}).get("evidence_cutoff"),
            "generated": _now(),
            "parents": parents,
            "prereg": PREREG,
            "verdict": "CANNOT_PRICE",
            "verdict_why": "band face missing or unreadable",
            "sentence": "band 面缺或读不出，对冲比例阶梯无从计算（缺面不等于免费）。",
            "inputs_ok": False,
        }

    rows = rows_by_label(band)
    quad = solve_quadratic(list(rows.values()))
    fit_in = (band.get("fit") or {}).get("etf_in_sample") or {}
    fit_full = (band.get("fit") or {}).get("etf_full_window") or {}
    spec = band.get("spec") or {}
    lot = etf_ladder_row(band)

    ppy = float(spec.get("periods_per_year") or 12.6)
    n0 = float(fit_in.get("n") or 0.0)
    k_ref = float(fit_in.get("beta") or 0.0)
    beta_one = 1.0
    beta_oos = float((band.get("fit") or {}).get("etf_out_of_sample", {}).get("beta")
                     or 0.0)
    beta_full = float(fit_full.get("beta") or 0.0)

    resid_point = float((rows.get("point") or {}).get("residual_annual_vol") or 0.0)
    resid_one = float((rows.get("one_unit") or {}).get("residual_annual_vol") or 0.0)
    resid_oos = float((rows.get("oos_beta") or {}).get("residual_annual_vol") or 0.0)

    lots_needed = float(lot.get("lots_needed") or 0.0)
    lots_per_unit = (lots_needed / k_ref) if k_ref else 0.0

    years = wait_years(n0, ppy, TARGET_BAND_SHRINK)
    ceiling_pp = (resid_point - resid_one) * 100.0
    target_yearly_pp = (ceiling_pp / years) if years > 0 else None

    # ---- the ladder: what the wait costs at each hedge ratio actually carried
    ladder = []
    for k in LADDER_K:
        r = resid_at(k, quad)
        yearly_pp = (r - resid_point) * 100.0
        total_pp = yearly_pp * years
        ratio = (total_pp / ceiling_pp) if ceiling_pp > TOL else None
        ladder.append({
            "hedge_ratio": round(float(k), 4),
            "lots": round(float(k) * lots_per_unit, 1),
            "residual_vol_pct": round(r * 100.0, 3),
            "yearly_cost_pp": round(yearly_pp, 4),
            "yearly_cost_cny": round(yearly_pp / 100.0 * LENS_CNY, 1),
            "total_cost_pp": round(total_pp, 3),
            "ratio_cost_over_ceiling": None if ratio is None else round(ratio, 2),
        })

    be = break_even_hedge(quad, k_ref, target_yearly_pp)
    be["lots_low"] = None if be.get("k_low") is None else round(be["k_low"] * lots_per_unit, 1)
    be["lots_high"] = None if be.get("k_high") is None else round(be["k_high"] * lots_per_unit, 1)

    rule_a = next((row for row in ladder
                   if abs(row["hedge_ratio"] - RULE_A_HEDGE) < 1e-9), {})
    unit = next((row for row in ladder if abs(row["hedge_ratio"] - 1.0) < 1e-9), {})
    r_at_point = resid_at(k_ref, quad)
    at_point = {
        "hedge_ratio": round(k_ref, 4),
        "lots": round(lots_needed, 1),
        "residual_vol_pct": round(r_at_point * 100.0, 3),
        "yearly_cost_pp": 0.0,
        "total_cost_pp": 0.0,
        "ratio_cost_over_ceiling": 0.0,
        "note": "the reference rung: the hedge the deploy arm books, so its wait cost is "
                "zero by construction",
    }

    gap_one_pp = (resid_point - resid_one) * 100.0
    ratio_rule_a = rule_a.get("ratio_cost_over_ceiling")

    v_ceiling, why_ceiling = decide_ceiling(gap_one_pp, ceiling_pp)
    v_ladder, why_ladder = decide_ladder(ratio_rule_a)
    v_point, why_point = decide_point(resid_point, resid_one, resid_oos)
    v_hold, why_hold = decide_holding(be.get("k_low"), k_ref)

    verdict = v_ceiling
    verdict_why = why_ceiling

    # ---- consistency between the two faces' published identities
    rebuilt_book = math.sqrt(quad["var_book"]) if quad else float("nan")
    published_book = float((band.get("risk") or {}).get("book_annual_vol") or 0.0)
    vertex = quad.get("vertex")
    vertex_gap = None if (vertex is None or not beta_full) else abs(vertex - beta_full)

    sentence = (
        "把等待按「等待期保留多少对冲」重新定价：r2038 的裸等价格（k=0）复现为每年 "
        "%.3fpp；k=0.65（BUDGET 规则 A）仍要每年 %.3fpp（%.0f 元/百万），是它买到的东西的 "
        "%.0f 倍；要对冲比例到 k=%.4f（%.0f 手）等待才不再比带宽本身更贵。而等待追的那个 "
        "0.124pp 天花板，其实今天把比例挪到 1.0 就已经拿到（10.639%% 对 10.763%%）——"
        "掉下来的这部分是一个比例，不是一段等待；顺带，部署用的点估计在这三个 beta 里残差最差。"
        % (ladder[0]["yearly_cost_pp"], rule_a.get("yearly_cost_pp") or float("nan"),
           rule_a.get("yearly_cost_cny") or float("nan"),
           rule_a.get("ratio_cost_over_ceiling") or float("nan"),
           be.get("k_low") or float("nan"), be.get("lots_low") or float("nan")))

    face = {
        "kind": "hedge_wait_ladder",
        "machine": "bm-c",
        "evidence_cutoff": band.get("evidence_cutoff"),
        "generated": _now(),
        "parents": parents,
        "prereg": PREREG,
        "inputs_ok": True,
        "verdict": verdict,
        "verdict_why": verdict_why,
        "ladder_verdict": v_ladder,
        "ladder_verdict_why": why_ladder,
        "point_verdict": v_point,
        "point_verdict_why": why_point,
        "holding_verdict": v_hold,
        "holding_verdict_why": why_hold,
        "sentence": sentence,
        "quadratic": {
            "var_book": quad.get("var_book"),
            "cov": quad.get("cov"),
            "var_hedge": quad.get("var_hedge"),
            "rows_used": quad.get("rows_used"),
            "max_row_error": quad.get("max_row_error"),
            "vertex": vertex,
            "beta_full_window": beta_full,
            "vertex_gap_vs_full_window": vertex_gap,
            "book_vol_rebuilt_pct": rebuilt_book * 100.0,
            "book_vol_published_pct": published_book * 100.0,
        },
        "spec": {
            "hedge_ref": k_ref,
            "beta_point": k_ref,
            "beta_one_unit": beta_one,
            "beta_oos": beta_oos,
            "beta_full_window": beta_full,
            "hedge_ref_lots": lots_needed,
            "lots_per_unit_hedge": lots_per_unit,
            "rule_a_hedge": RULE_A_HEDGE,
            "periods_in_sample": n0,
            "periods_per_year": ppy,
            "target_band_shrink": TARGET_BAND_SHRINK,
            "wait_years": years,
            "ceiling_pp": ceiling_pp,
            "target_yearly_pp": target_yearly_pp,
            "lens_cny": LENS_CNY,
            "residual_point_pct": resid_point * 100.0,
            "residual_one_unit_pct": resid_one * 100.0,
            "residual_oos_pct": resid_oos * 100.0,
        },
        "ladder": ladder,
        "break_even": be,
        "at_the_point_estimate": at_point,
        "at_unit_beta": unit,
        "anchor": {
            "wait_face_ratio": (wait or {}).get("wait", {}).get("ratio_cost_over_benefit"),
            "wait_face_yearly_cost_pp": (wait or {}).get("wait", {}).get("yearly_cost_pp"),
            "wait_face_total_cost_pp": (wait or {}).get("wait", {}).get("total_cost_pp"),
            "wait_face_ceiling_pp": (wait or {}).get("wait", {}).get("benefit_ceiling_pp"),
            "wait_face_years": (wait or {}).get("wait", {}).get("years"),
            "reproduced_yearly_cost_pp": ladder[0]["yearly_cost_pp"],
            "reproduced_total_cost_pp": ladder[0]["total_cost_pp"],
            "reproduced_ratio": ladder[0]["ratio_cost_over_ceiling"],
        },
        "reads": [
            "k = 0.0 is r2038's own price, recomputed here from the band face rather than "
            "copied; if the two disagree the ladder is not the same ladder",
            "the ladder's hinge is not the ratio you would like to hold but the ratio at "
            "which holding the rest back stops costing more than the band is worth",
            "the wait's ceiling equals the gap between the deployed beta's residual and "
            "unit beta's residual, so the ceiling is reachable without more periods",
            "the point estimate is the in-sample OLS slope; the residual rows are "
            "evaluated on the paired window, which is why the full-window slope wins on "
            "that window",
        ],
    }

    face["content_sha256"] = content_sha(face)
    return face


def _f(x, digits: int = 3) -> str:
    try:
        return ("%." + str(digits) + "f") % float(x)
    except (TypeError, ValueError):
        return "-"


def _pct(x, digits: int = 2) -> str:
    try:
        return ("%." + str(digits) + "f%%") % (float(x) * 100.0)
    except (TypeError, ValueError):
        return "-"


def _pp(x, digits: int = 2) -> str:
    """Format a value that is ALREADY in percent points (27.343 -> '27.343%')."""
    try:
        return ("%." + str(digits) + "f%%") % float(x)
    except (TypeError, ValueError):
        return "-"


def _cny(x) -> str:
    try:
        return "{:,}".format(int(round(float(x))))
    except (TypeError, ValueError):
        return "-"


def render_md(face: dict) -> str:
    if not face.get("inputs_ok"):
        return ("<!-- BEGIN:ASTOCK-VETO-HEDGE-WAIT-LADDER -->\n# 等待的价格取决于你留多少对冲\n\n"
                "`CANNOT_PRICE`\n\nband 面缺或读不出，本面不编数。\n"
                "<!-- END:ASTOCK-VETO-HEDGE-WAIT-LADDER -->\n")

    L = []
    a = L.append
    a("<!-- BEGIN:ASTOCK-VETO-HEDGE-WAIT-LADDER -->")
    a("# 等待的价格取决于你留多少对冲")
    a("")
    a("`%s` · `%s` · `%s` · `%s`" % (face.get("verdict"), face.get("ladder_verdict"),
                                     face.get("point_verdict"), face.get("holding_verdict")))
    a("")
    a("generated %s | evidence_cutoff **%s** | machine `%s`"
      % (face.get("generated"), face.get("evidence_cutoff"), face.get("machine")))
    a("")
    a("## 1. 一句话")
    a("")
    a("- %s" % face.get("sentence"))
    a("")
    a("## 2. 为什么这一面存在")
    a("")
    a("r2038 给等待开了一张价签：如果等带宽收窄的这 10.24 年里账本裸着，每年多扛 16.580pp，"
      "而等到的东西只有 0.124pp——1367 倍。它自己在边界里写明：")
    a("")
    a("> 一个跑部分对冲（比如 BUDGET 面规则 A 的 k=0.65）的读者付的等待费比这里少，"
      "本面价的是**完全不对冲**的等待。")
    a("")
    a("本面把这句话做成一张阶梯表。用的不是新数据，是 band 面自己印的五条残差行——")
    a("它们不是五个独立测量，而是同一个二次型的五个点：")
    a("")
    a("```")
    a("R(k)^2 = Var(book) - 2k*Cov(book, hedge) + k^2*Var(hedge)")
    a("```")
    a("")
    a("五个点、三个参数，多出来的两行就是检查。")
    a("")
    a("## 3. 先把身份核对上")
    a("")
    q = face.get("quadratic") or {}
    a("| 项目 | 本面从五条残差行反解 | band 面自己印的 | 差 |")
    a("|---|---|---|---|")
    a("| 账本年化波动 | %s | %s | %s pp |"
      % (_pp(q.get("book_vol_rebuilt_pct"), 4), _pp(q.get("book_vol_published_pct"), 4),
         _f((q.get("book_vol_rebuilt_pct") or 0) - (q.get("book_vol_published_pct") or 0), 6)))
    a("| 残差最小点 k | %s | 全窗 beta %s | %s |"
      % (_f(q.get("vertex"), 6), _f(q.get("beta_full_window"), 6),
         ("%.2e" % q["vertex_gap_vs_full_window"]) if q.get("vertex_gap_vs_full_window") is not None else "-"))
    a("")
    a("五条行逐点复现的最大误差 **%s**（波动 pp）。也就是说：面里的「残差行」和"
      "「全窗 beta」不是两套数，是同一个二次型的两张脸。" % ("%.2e" % (q.get("max_row_error") or 0.0)))
    a("")
    a("## 4. 阶梯：等待期留多少对冲，每年付多少")
    a("")
    a("参考臂是 r2038 的**部署**（k=%.4f，%s 手），成本 = R(k) − R(参考)。"
      % (face["spec"]["hedge_ref"], _f(face["spec"]["hedge_ref_lots"], 0)))
    a("")
    a("| 等待期对冲 k | 手数 | 残差年化波动 | 每年多扛 | 元/百万/年 | 10.24 年总价 | 倍率 |")
    a("|---|---|---|---|---|---|---|")
    for row in face.get("ladder") or []:
        a("| %s | %s | %s | %s pp | %s | %s pp | %s |"
          % (_f(row.get("hedge_ratio"), 4), _f(row.get("lots"), 0),
             _pp(row.get("residual_vol_pct"), 3), _f(row.get("yearly_cost_pp"), 3),
             _cny(row.get("yearly_cost_cny")), _f(row.get("total_cost_pp"), 2),
             _f(row.get("ratio_cost_over_ceiling"), 1)))
    a("")
    be = face.get("break_even") or {}
    a("- **打平带**：k ∈ [%s, %s]（%s .. %s 手）——在这个带内，等待每年多扛的波动不到它买到的东西。"
      % (_f(be.get("k_low"), 4), _f(be.get("k_high"), 4),
         _f(be.get("lots_low"), 0), _f(be.get("lots_high"), 0)))
    a("- **低边界 %s** 就是这道题的答案：对冲至少要上到部署量的 %s%%，把剩下的留到带宽变窄之后才不亏。"
      % (_f(be.get("k_low"), 4),
         _f(100.0 * (be["k_low"] / face["spec"]["hedge_ref"]) if be.get("k_low") else float("nan"), 1)))
    a("- 规则 A 的 k=0.65 落在带外很远：每年 %s pp（%s 元/百万），是天花板 %s 倍。"
      % (_f((face.get("ladder") or [{}] * 4)[3].get("yearly_cost_pp"), 3),
         _cny((face.get("ladder") or [{}] * 4)[3].get("yearly_cost_cny")),
         _f((face.get("ladder") or [{}] * 4)[3].get("ratio_cost_over_ceiling"), 0)))
    a("")
    a("> 判词 `%s` 的理由：%s。" % (face.get("holding_verdict"), face.get("holding_verdict_why")))
    a("")
    a("## 5. 天花板是一个比例，不是一段等待")
    a("")
    a("r2038 把残差从 10.763% 降到 10.639% 记作「等待的收益」。但 10.639% 正是 **k=1.0** 那一行——"
      "也就是今天就能拿到的残差。等带宽收窄并没有创造出这个数，它只是让一个估计收敛到它；")
    a("而比例是你现在就能选的。")
    a("")
    a("| 用什么 beta | k | 残差年化波动 | 相对部署 |")
    a("|---|---|---|---|")
    a("| 点估计（部署） | %s | %s | +0.000 pp |"
      % (_f(face["spec"]["hedge_ref"], 4), _pp(face["spec"]["residual_point_pct"], 3)))
    a("| 单位 beta | %s | %s | %s pp |"
      % (_f(face["spec"].get("beta_one_unit"), 4),
         _pp(face["spec"]["residual_one_unit_pct"], 3),
         _f((face["spec"]["residual_one_unit_pct"] or 0) - (face["spec"]["residual_point_pct"] or 0), 3)))
    a("| 样本外 beta | %s | %s | %s pp |"
      % (_f(face["spec"].get("beta_oos"), 4),
         _pp(face["spec"]["residual_oos_pct"], 3),
         _f((face["spec"]["residual_oos_pct"] or 0) - (face["spec"]["residual_point_pct"] or 0), 3)))
    a("")
    a("> 判词 `%s`：%s。" % (face.get("verdict"), face.get("verdict_why")))
    a("")
    a("> 判词 `%s`：%s。" % (face.get("point_verdict"), face.get("point_verdict_why")))
    a("")
    a("## 6. 本面不说的")
    a("")
    a("- 不说该选哪个 k。本面只给「等」定价，不定「对冲多少」。")
    a("- 不说 k=1.0 比点估计「更对」——单位 beta 只是在这张残差表自己的窗口上更好；"
      "换窗口重选比例就是又在窗口上挑数。")
    a("- 不说这 52/77 期代表未来 regime（r2037 已明说不等于样本公平）。")
    a("- 台阶假设等待期内 k 恒定、不随波动调整；运行中调比例会产生换手成本，本面没算。")
    a("- 口径是每 1,000,000 元的镜头，与票面 13.041bp/边的成本腿不是同一个量，两者不相加。")
    a("")
    a("## 7. 复现")
    a("")
    a("```")
    a("python scripts/astock_veto_hedge_wait_ladder.py selftest")
    a("python scripts/astock_veto_hedge_wait_ladder.py run")
    a("python scripts/astock_veto_hedge_wait_ladder.py check")
    a("```")
    a("")
    a("Machine `%s`, generated %s." % (face.get("machine"), face.get("generated")))
    a("<!-- END:ASTOCK-VETO-HEDGE-WAIT-LADDER -->")
    return "\n".join(L) + "\n"


def run(write: bool = True) -> int:
    t0 = time.time()
    face = build_face()
    if not face.get("inputs_ok"):
        print("CANNOT_PRICE: %s" % face.get("verdict_why"))
        return 2
    if write:
        os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
        os.makedirs(os.path.dirname(OUT_MD), exist_ok=True)
        with open(OUT_JSON, "w", encoding="utf-8") as f:
            json.dump(face, f, ensure_ascii=False, indent=1, sort_keys=True)
        with open(OUT_MD, "w", encoding="utf-8") as f:
            f.write(render_md(face))
    print("verdict=%s" % face.get("verdict"))
    print("ladder=%s | point=%s | holding=%s" % (face.get("ladder_verdict"),
                                                face.get("point_verdict"),
                                                face.get("holding_verdict")))
    be = face.get("break_even") or {}
    print("break_even k in [%s, %s] | rule_a_ratio=%s"
          % (_f(be.get("k_low"), 4), _f(be.get("k_high"), 4),
             _f((face.get("ladder") or [{}] * 4)[3].get("ratio_cost_over_ceiling"), 1)))
    print("elapsed=%.3fs" % (time.time() - t0))
    return 0


def check() -> int:
    """Re-derive from parents and name what moved.

    Two kinds of red kept apart (r1934): an upstream that moved one step is STALE and is
    repaired by `run`; a number that disagrees with its own inputs is CHECK FAILED.
    Reads the module-level paths inside the body, never as default arguments, so a
    control can point them at a throwaway copy (r2038's trap).
    """
    json_path, md_path = OUT_JSON, OUT_MD
    problems = []
    if not os.path.exists(json_path):
        print("STALE: face missing (%s)" % _rel(json_path))
        return 3
    face = _read_json(json_path)
    fresh = build_face()

    for key in ("band", "wait"):
        a = (face.get("parents") or {}).get(key) or {}
        b = (fresh.get("parents") or {}).get(key) or {}
        if a.get("content_sha256") != b.get("content_sha256"):
            problems.append("STALE: parent %s content moved (%s -> %s)"
                            % (key, str(a.get("content_sha256"))[:12],
                               str(b.get("content_sha256"))[:12]))
        elif a.get("file_sha256") != b.get("file_sha256"):
            problems.append("STALE: parent %s bytes moved (%s -> %s)"
                            % (key, str(a.get("file_sha256"))[:12],
                               str(b.get("file_sha256"))[:12]))

    if [p for p in problems if p.startswith("STALE")]:
        for p in problems:
            print(p)
        return 3

    try:
        for key in ("verdict", "ladder_verdict", "point_verdict", "holding_verdict",
                    "evidence_cutoff", "machine"):
            if face.get(key) != fresh.get(key):
                problems.append("CHECK FAILED: %s moved (%r -> %r)"
                                % (key, face.get(key), fresh.get(key)))

        # every ladder cell must re-derive from the identity
        old_rows = face.get("ladder") or []
        new_rows = fresh.get("ladder") or []
        if len(old_rows) != len(new_rows):
            problems.append("CHECK FAILED: ladder length moved (%d -> %d)"
                            % (len(old_rows), len(new_rows)))
        for a_row, b_row in zip(old_rows, new_rows):
            for key in ("hedge_ratio", "residual_vol_pct", "yearly_cost_pp",
                        "total_cost_pp", "ratio_cost_over_ceiling"):
                a, b = a_row.get(key), b_row.get(key)
                if a is None or b is None:
                    if a != b:
                        problems.append("CHECK FAILED: ladder[%s].%s moved (%r -> %r)"
                                        % (a_row.get("hedge_ratio"), key, a, b))
                elif abs(float(a) - float(b)) > 1e-6:
                    problems.append("CHECK FAILED: ladder[%s].%s moved (%r -> %r)"
                                    % (a_row.get("hedge_ratio"), key, a, b))

        for key in ("k_low", "k_high", "lots_low", "lots_high"):
            a = (face.get("break_even") or {}).get(key)
            b = (fresh.get("break_even") or {}).get(key)
            if a is None or b is None:
                if a != b:
                    problems.append("CHECK FAILED: break_even.%s moved (%r -> %r)"
                                    % (key, a, b))
            elif abs(float(a) - float(b)) > 1e-6:
                problems.append("CHECK FAILED: break_even.%s moved (%r -> %r)"
                                % (key, a, b))

        q_old = (face.get("quadratic") or {})
        q_new = (fresh.get("quadratic") or {})
        for key in ("var_book", "cov", "var_hedge", "vertex"):
            a, b = q_old.get(key), q_new.get(key)
            if a is None or b is None:
                if a != b:
                    problems.append("CHECK FAILED: quadratic.%s moved (%r -> %r)"
                                    % (key, a, b))
            elif abs(float(a) - float(b)) > 1e-9:
                problems.append("CHECK FAILED: quadratic.%s moved (%r -> %r)"
                                % (key, a, b))

        # the identity must hold on the face's own rows
        worst = float((face.get("quadratic") or {}).get("max_row_error") or 0.0)
        if worst > 1e-9:
            problems.append("CHECK FAILED: published residual rows are not a quadratic "
                            "(max error %.3e)" % worst)

        # the k=0 rung is r2038's own price, not a different ladder
        anchor = face.get("anchor") or {}
        for key in ("yearly_cost_pp", "total_cost_pp", "ratio_cost_over_benefit"):
            src = anchor.get("wait_face_" + ("ratio" if key == "ratio_cost_over_benefit"
                                             else key))
            mine = anchor.get("reproduced_" + ("ratio" if key == "ratio_cost_over_benefit"
                                               else key))
            if src is None or mine is None:
                continue
            tol = 0.02 if "pp" in key else 1.0
            if abs(float(src) - float(mine)) > tol:
                problems.append("CHECK FAILED: k=0 does not reproduce %s (%r vs %r)"
                                % (key, src, mine))
    except (TypeError, ValueError) as exc:
        problems.append("CHECK FAILED: unreadable number (%s)" % exc)

    if not os.path.exists(md_path):
        problems.append("STALE: page missing (%s)" % _rel(md_path))
    else:
        with open(md_path, "r", encoding="utf-8") as f:
            page = f.read()
        for token in ("verdict", "ladder_verdict", "point_verdict", "holding_verdict"):
            tok = face.get(token)
            if tok and tok not in page:
                problems.append("CHECK FAILED: page missing token %s" % tok)

    digest = content_sha(face)
    if face.get("content_sha256") and face["content_sha256"] != digest:
        problems.append("CHECK FAILED: content_sha256 does not describe the face")

    if problems:
        for p in problems:
            print(p)
        return 3
    print("CHECK_OK: %d parents, %d rungs, 0 problems"
          % (len(face.get("parents") or {}), len(face.get("ladder") or [])))
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

    # ---- the solver on a known parabola
    quad = {"var_book": 0.04, "cov": 0.03, "var_hedge": 0.06}
    rows = [{"beta": b, "residual_annual_vol": resid_at(b, quad)}
            for b in (0.5, 1.0, 1.2, 0.7, 1.1)]
    solved = solve_quadratic(rows)
    chk("solver recovers var_book", abs(solved["var_book"] - 0.04) < 1e-12)
    chk("solver recovers cov", abs(solved["cov"] - 0.03) < 1e-12)
    chk("solver recovers var_hedge", abs(solved["var_hedge"] - 0.06) < 1e-12)
    chk("solver vertex is cov/var_hedge", abs(solved["vertex"] - 0.5) < 1e-12)
    chk("solver reports zero row error on a true parabola", solved["max_row_error"] < 1e-12)
    chk("solver refuses fewer than three rows", solve_quadratic(rows[:2]) == {})

    # ---- residual and break-even arithmetic
    chk("residual at the vertex is the minimum",
        resid_at(solved["vertex"], solved) <= resid_at(0.2, solved) + 1e-15)
    chk("residual at zero hedge is the book", abs(resid_at(0.0, solved) - 0.2) < 1e-12)
    be = break_even_hedge(solved, 0.9, 0.01)
    chk("break-even brackets the reference", (be["k_low"] or 0) < 0.9)
    chk("break-even high side is above the reference", (be["k_high"] or 0) > 0.9)
    tight = break_even_hedge(solved, 0.9, 1e9)
    chk("an impossible target has no break-even at all",
        tight["k_low"] is None and tight["k_high"] is None)
    chk("a missing quadratic has no break-even",
        break_even_hedge({}, 0.9, 0.01)["k_low"] is None)
    chk("wait years halves with four times the periods",
        abs(wait_years(43, 12.6, 0.5) - 129.0 / 12.6) < 1e-12)
    chk("wait years of a full band is zero", abs(wait_years(43, 12.6, 1.0)) < 1e-12)

    # ---- verdict legs
    v, _ = decide_ceiling(0.1242, 0.1242)
    chk("a ceiling reached by the ratio is named", v == "THE_CEILING_IS_A_RATIO_NOT_A_WAIT")
    v, _ = decide_ceiling(0.02, 0.1242)
    chk("a ceiling not reached by the ratio is named", v == "THE_CEILING_NEEDS_THE_WAIT")
    v, _ = decide_ladder(224.0)
    chk("a rule-A hedge that is still dear is named",
        v == "PARTIAL_HEDGING_DOES_NOT_MAKE_THE_WAIT_CHEAP")
    v, _ = decide_ladder(0.4)
    chk("a rule-A hedge that is cheap is named", v == "A_PARTIAL_HEDGE_MAKES_THE_WAIT_CHEAP")
    v, _ = decide_point(0.1076, 0.1064, 0.1071)
    chk("the worst of three betas is named",
        v == "THE_POINT_ESTIMATE_IS_THE_WORST_OF_THREE_BETAS")
    v, _ = decide_point(0.10, 0.1064, 0.1071)
    chk("a point estimate that is not worst is named",
        v == "THE_POINT_ESTIMATE_IS_NOT_THE_WORST")
    v, _ = decide_holding(0.9, 0.9)
    chk("a hinge near the deployed hedge is named",
        v == "YOU_MUST_ALREADY_HOLD_MOST_OF_THE_HEDGE")
    v, _ = decide_holding(0.2, 0.9)
    chk("a hinge far below the deployed hedge is named",
        v == "THE_WAIT_SURVIVES_A_THIN_HEDGE")
    v, _ = decide_holding(None, 0.9)
    chk("no hinge cannot be priced", v == "CANNOT_PRICE")

    # ---- the real face, from the real parents
    face = build_face()
    chk("face has inputs", bool(face.get("inputs_ok")))
    chk("face names four verdicts", all(face.get(k) for k in
                                        ("verdict", "ladder_verdict", "point_verdict",
                                         "holding_verdict")))
    chk("face has two parents", len(face.get("parents") or {}) == 2)
    q = face.get("quadratic") or {}
    chk("published residual rows are a quadratic", (q.get("max_row_error") or 1) < 1e-9)
    chk("the quadratic's vertex is the full-window beta",
        q.get("vertex_gap_vs_full_window") is not None
        and q["vertex_gap_vs_full_window"] < 1e-9)
    chk("the quadratic rebuilds the published book vol",
        abs((q.get("book_vol_rebuilt_pct") or 0) - (q.get("book_vol_published_pct") or 0))
        < 1e-9)
    ladder = face.get("ladder") or []
    chk("ladder has ten rungs", len(ladder) == 10)
    chk("ladder starts at zero hedge", ladder[0].get("hedge_ratio") == 0.0)
    chk("ladder's zero-hedge rung carries the whole book",
        abs(ladder[0]["residual_vol_pct"] - q["book_vol_published_pct"]) < 1e-3)
    chk("ladder is monotone falling below the vertex",
        ladder[0]["residual_vol_pct"] > ladder[1]["residual_vol_pct"] > ladder[2]["residual_vol_pct"])
    chk("ladder's zero-hedge cost is the anchor",
        abs(ladder[0]["yearly_cost_pp"]
            - float((face.get("anchor") or {}).get("wait_face_yearly_cost_pp") or 0)) < 0.01)
    chk("the wait is expensive with nothing hedged",
        (ladder[0].get("ratio_cost_over_ceiling") or 0) > 100.0)
    chk("the rule-A rung is still expensive by this face's own arithmetic",
        face.get("ladder_verdict") == "PARTIAL_HEDGING_DOES_NOT_MAKE_THE_WAIT_CHEAP")
    be = face.get("break_even") or {}
    chk("break-even is bracketed", be.get("k_low") is not None and be.get("k_high") is not None)
    chk("break-even low side sits below the deployed hedge",
        be.get("k_low") is not None and be["k_low"] < face["spec"]["hedge_ref"])
    chk("break-even low side sits above the rule-A hedge",
        be.get("k_low") is not None and be["k_low"] > RULE_A_HEDGE)
    chk("unit beta earns the ceiling",
        abs((face["spec"]["residual_point_pct"] - face["spec"]["residual_one_unit_pct"])
            - face["spec"]["ceiling_pp"]) < 1e-9)
    chk("the ceiling verdict is the ratio one",
        face.get("verdict") == "THE_CEILING_IS_A_RATIO_NOT_A_WAIT")

    # ---- the page renders and carries every token
    page = render_md(face)
    for key in ("verdict", "ladder_verdict", "point_verdict", "holding_verdict"):
        chk("page carries %s" % key, face[key] in page)
    chk("page has begin marker", "BEGIN:ASTOCK-VETO-HEDGE-WAIT-LADDER" in page)
    chk("page has end marker", "END:ASTOCK-VETO-HEDGE-WAIT-LADDER" in page)
    chk("page prints the break-even hedge", _f(be.get("k_low"), 4) in page)
    chk("page prints the rule-A ratio", _f(ladder[3]["ratio_cost_over_ceiling"], 1) in page)
    # a percent field formatted with the fraction helper prints 2734.3286% -- the page is
    # the only place that defect shows up, so the page is where it is caught
    chk("page does not print a percent of a percent", "2734." not in page)
    chk("page prints the book volatility as a percent", "27.3433%" in page)
    chk("page prints the point-estimate residual as a percent", "10.763%" in page)

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

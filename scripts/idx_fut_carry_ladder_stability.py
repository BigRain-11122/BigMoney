#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""the ladder prices its futures block with ONE volatility and ONE correlation; are they constants?

WHY THIS FILE EXISTS
--------------------
`scripts/policy_return_lattice.py` builds every whole-lot rung's risk from two declarations:

    l2 = (futures notional / nav) * L2_CARRY_VOL       <- 4.0 %/yr per unit notional
    ...  one block, one number, RHO applied as a constant

r2105 measured those two numbers on the whole sample (sigma_IC 5.92, sigma_IM 6.82, rho 0.833
against a declared 0.10) and r2106/r2107 carried the consequences into drawdown and years.
Every one of those faces still answers "what was the average risk over eight years", and a
constant fitted on eight years of average is exactly what a risk budget must not be built
on: the question a position holder actually asks is *how much does this number move*, and
whether it moves in the direction that hurts.

This face answers that one question for the futures block only -- no sleeve, no costs, no
margin, all of which stay where they already are published:

  * rolling rho and rolling sigma for windows of 60 / 120 / 250 trading days on the days
    both legs quote (the same `idx_fut_carry_risk.product_spread` series every sibling face
    prices, imported, never rebuilt);
  * the block's own vol at the instruction rung (1 lot IC + 1 lot IM) recomputed in every
    window with the ladder's own formula and the ladder's own per-lot notionals;
  * calendar-year rho and block vol, because "the correlation in 2024 was X" is a sentence a
    reader can check against their own memory of that year;
  * the declared number the ladder prints, so the gap is never a subtraction the reader has
    to do in their head.

WHAT IS DELIBERATELY OUT OF SCOPE (printed on the face, not implied away)
------------------------------------------------------------------------
the equity sleeve, financing, margin and transaction costs.  Those live in
`results/idx_fut_carry_ladder_risk.json` (sleeve included, rung by rung) and are not
recomputed here; a reader who wants the whole rung's risk reads that face.

verdict tokens (frozen before the first run):
  RHO_RANGE_WIDE / RHO_TIGHT
       120-day rolling rho spans >= 0.20 / < 0.20 between its 5th and 95th percentile
  DIVERSIFICATION_DISAPPEARS_IN_STRESS / STRESS_NOT_CONCENTRATED
       block vol at the 95th percentile is >= 1.25x its median AND rho at that percentile is
       at least 0.10 above the median -- the two legs converge exactly when both move
  BLOCK_VOL_ALWAYS_ABOVE_DECLARATION    (>= 90 % of 120-day windows exceed the declared number)
  BLOCK_VOL_SOMETIMES_ABOVE_DECLARATION (some windows are inside the declared number)
  DATA_BLOCKED                          a leg or the ladder is missing; refuse, never default

Usage:
    python scripts/idx_fut_carry_ladder_stability.py run
    python scripts/idx_fut_carry_ladder_stability.py check
    python scripts/idx_fut_carry_ladder_stability.py --selftest
"""
from __future__ import annotations

import argparse
import io
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
for _p in (ROOT, HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

SCHEMA = "idx-fut-carry-ladder-stability/v1"
KIND = "carry_ladder_parameter_stability"
OUT = os.path.join(ROOT, "results", "idx_fut_carry_ladder_stability.json")
DOC = os.path.join(ROOT, "research", "IDX_FUT_CARRY_LADDER_STABILITY.md")
LATTICE = os.path.join(ROOT, "results", "policy_return_lattice.json")
SIBLING = os.path.join(ROOT, "results", "idx_fut_carry_ladder_risk.json")

WINDOWS = (60, 120, 250)
DECLARED_L2_VOL_PCT = 4.0      # scripts/policy_return_lattice.py L2_CARRY_VOL
DECLARED_RHO = 0.10            # scripts/policy_return_lattice.py RHO
MIN_DAYS = 400                 # below this a refusal is a short sample, not a verdict
NUM_TOL = 0.002                # face publishes 3 dp; half an ulp is 0.0005
RHO_RANGE_PP = 0.20
STRESS_RATIO = 1.25
STRESS_RHO_GAP = 0.10
ALWAYS_SHARE = 0.90

V_RHO_WIDE = "RHO_RANGE_WIDE"
V_RHO_TIGHT = "RHO_TIGHT"
V_STRESS_CONC = "DIVERSIFICATION_DISAPPEARS_IN_STRESS"
V_STRESS_FLAT = "STRESS_NOT_CONCENTRATED"
V_ALWAYS_ABOVE = "BLOCK_VOL_ALWAYS_ABOVE_DECLARATION"
V_SOMETIMES_ABOVE = "BLOCK_VOL_SOMETIMES_ABOVE_DECLARATION"
V_BLOCK = "DATA_BLOCKED"


# ------------------------------------------------------------------ arithmetic (pure)
def td():
    """Bars per year from the authority, never re-declared."""
    import idx_fut_basis as B
    return float(B.TRADING_DAYS)


def ann_vol(daily):
    n = len(daily)
    if n < 2:
        return None
    m = sum(daily) / n
    v = sum((x - m) ** 2 for x in daily) / (n - 1)
    return math.sqrt(v) * math.sqrt(td()) * 100.0


def corr(a, b):
    n = min(len(a), len(b))
    if n < 3:
        return None
    a, b = a[:n], b[:n]
    ma, mb = sum(a) / n, sum(b) / n
    va = sum((x - ma) ** 2 for x in a)
    vb = sum((y - mb) ** 2 for y in b)
    if va <= 0 or vb <= 0:
        return None
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / math.sqrt(va * vb)


def block_vol_pct(w_ic, s_ic, w_im, s_im, rho):
    """The ladder's own two-asset formula, in pp of nav per year."""
    if s_ic is None or s_im is None or rho is None:
        return None
    var = (w_ic * s_ic) ** 2 + (w_im * s_im) ** 2 + 2.0 * rho * (w_ic * s_ic) * (w_im * s_im)
    return math.sqrt(max(var, 0.0))


def pctl(xs, q):
    """Nearest-rank percentile on a sorted copy (q in [0,1]); pure, selftest pins it."""
    ys = sorted(x for x in xs if x is not None)
    if not ys:
        return None
    i = int(round(q * (len(ys) - 1)))
    i = max(0, min(len(ys) - 1, i))
    return ys[i]


def align(dates_a, series_a, dates_b, series_b):
    ma, mb = dict(zip(dates_a, series_a)), dict(zip(dates_b, series_b))
    common = sorted(set(ma) & set(mb))
    return common, [ma[d] for d in common], [mb[d] for d in common]


# ------------------------------------------------------------------ rolling measurement
def rolling(dates, a, b, window):
    """Every window's rho / sigmas / block vol.  `dates` aligns 1:1 with a and b."""
    out = []
    n = min(len(a), len(b), len(dates))
    for i in range(window - 1, n):
        wa = a[i - window + 1:i + 1]
        wb = b[i - window + 1:i + 1]
        rho = corr(wa, wb)
        if rho is None:
            continue
        out.append({"end": dates[i],
                    "rho": rho,
                    "sig_ic_pct": ann_vol(wa),
                    "sig_im_pct": ann_vol(wb)})
    return out


def with_block(rows, w_ic, w_im):
    for r in rows:
        r["block_vol_pct"] = block_vol_pct(w_ic, r["sig_ic_pct"], w_im, r["sig_im_pct"], r["rho"])
    return [r for r in rows if r.get("block_vol_pct") is not None]


def summarize(rows, declared_pct):
    vols = [r["block_vol_pct"] for r in rows]
    rhos = [r["rho"] for r in rows]
    if not vols:
        return None
    above = sum(1 for v in vols if v > declared_pct)
    worst = max(rows, key=lambda r: r["block_vol_pct"])
    most_corr = max(rows, key=lambda r: r["rho"])
    least_corr = min(rows, key=lambda r: r["rho"])
    return {
        "windows": len(rows),
        "rho_min": round(pctl(rhos, 0.0), 4),
        "rho_p05": round(pctl(rhos, 0.05), 4),
        "rho_median": round(pctl(rhos, 0.5), 4),
        "rho_p95": round(pctl(rhos, 0.95), 4),
        "rho_max": round(pctl(rhos, 1.0), 4),
        "block_vol_min_pct": round(pctl(vols, 0.0), 3),
        "block_vol_median_pct": round(pctl(vols, 0.5), 3),
        "block_vol_p95_pct": round(pctl(vols, 0.95), 3),
        "block_vol_max_pct": round(pctl(vols, 1.0), 3),
        "share_windows_above_declared": round(above / float(len(vols)), 4),
        "worst_window": {"end": worst["end"],
                         "block_vol_pct": round(worst["block_vol_pct"], 3),
                         "rho": round(worst["rho"], 4)},
        "most_correlated_window": {"end": most_corr["end"], "rho": round(most_corr["rho"], 4),
                                   "block_vol_pct": round(most_corr["block_vol_pct"], 3)},
        "least_correlated_window": {"end": least_corr["end"], "rho": round(least_corr["rho"], 4),
                                    "block_vol_pct": round(least_corr["block_vol_pct"], 3)},
    }


def by_year(dates, a, b, w_ic, w_im):
    """Calendar-year rho and block vol -- the sentence a reader can test from memory."""
    buckets = {}
    for d, x, y in zip(dates, a, b):
        buckets.setdefault(d[:4], ([], []))
        buckets[d[:4]][0].append(x)
        buckets[d[:4]][1].append(y)
    out = {}
    for yr in sorted(buckets):
        xa, ya = buckets[yr]
        if len(xa) < 20:
            continue
        rho = corr(xa, ya)
        sic, sim = ann_vol(xa), ann_vol(ya)
        out[yr] = {"days": len(xa),
                   "rho": round(rho, 4) if rho is not None else None,
                   "sig_ic_pct": round(sic, 3) if sic is not None else None,
                   "sig_im_pct": round(sim, 3) if sim is not None else None,
                   "block_vol_pct": (round(block_vol_pct(w_ic, sic, w_im, sim, rho), 3)
                                     if rho is not None else None)}
    return out


def judge(summary, declared_pct):
    """The frozen tokens, derived from the 120-day summary only (pure)."""
    s = summary["120"]
    rho_range = s["rho_p95"] - s["rho_p05"]
    ratio = (s["block_vol_p95_pct"] / s["block_vol_median_pct"]
             if s["block_vol_median_pct"] else None)
    rho_gap = s["rho_p95"] - s["rho_median"]
    tokens = {
        "rho_stability": V_RHO_WIDE if rho_range >= RHO_RANGE_PP else V_RHO_TIGHT,
        "rho_range_120d": round(rho_range, 4),
        "stress_concentration": (V_STRESS_CONC
                                 if (ratio is not None and ratio >= STRESS_RATIO
                                     and rho_gap >= STRESS_RHO_GAP)
                                 else V_STRESS_FLAT),
        "stress_vol_ratio": round(ratio, 4) if ratio is not None else None,
        "declaration_coverage": (V_ALWAYS_ABOVE
                                 if s["share_windows_above_declared"] >= ALWAYS_SHARE
                                 else V_SOMETIMES_ABOVE),
        "declared_block_vol_pct": round(declared_pct, 3),
        "median_block_vol_pct": s["block_vol_median_pct"],
        "p95_block_vol_pct": s["block_vol_p95_pct"],
        "understatement_at_p95_pp": round(s["block_vol_p95_pct"] - declared_pct, 3),
        "understatement_at_median_pp": round(s["block_vol_median_pct"] - declared_pct, 3),
    }
    return tokens


# ------------------------------------------------------------------ io
def read_json(path):
    with io.open(path, encoding="utf-8") as f:
        return json.load(f)


def digest(path):
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path, payload):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
        f.write("\n")
    os.replace(tmp, path)


def spread_leg(prod):
    """The leg's daily spread from the authority module by import (never rebuilt here)."""
    import idx_fut_carry_risk as R
    sp = R.product_spread(prod)
    if not sp or "spread" not in sp:
        return {"_refused": "no_spread_series", "product": prod}
    dates = [str(d)[:10] for d in sp["dates"]]
    if len(dates) != len(sp["spread"]) + 1:
        return {"_refused": "date_return_misaligned", "product": prod,
                "dates": len(dates), "returns": len(sp["spread"])}
    return {"product": prod, "dates": dates[1:], "spread": [float(x) for x in sp["spread"]],
            "span": [dates[1], dates[-1]], "days": len(sp["spread"]), "index": sp.get("index")}


def per_lot_notional(lattice):
    n = {"IC": None, "IM": None}
    for r in lattice.get("lattice") or []:
        if r.get("ic_lots") == 1 and r.get("im_lots") == 0:
            n["IC"] = float(r["notional_cny"])
        if r.get("ic_lots") == 0 and r.get("im_lots") == 1:
            n["IM"] = float(r["notional_cny"])
    return n


# ------------------------------------------------------------------ measurement
def measure(legs, lattice, nav):
    """Everything this face publishes, from two leg series + the ladder's notionals."""
    ic, im = legs["IC"], legs["IM"]
    dates, s_ic, s_im = align(ic["dates"], ic["spread"], im["dates"], im["spread"])
    if len(dates) < MIN_DAYS:
        return None, {"verdict": V_BLOCK,
                      "why": "common history %d days, need %d" % (len(dates), MIN_DAYS)}
    n_lot = per_lot_notional(lattice)
    if not n_lot.get("IC") or not n_lot.get("IM"):
        return None, {"verdict": V_BLOCK, "why": "ladder does not publish per-lot notionals"}
    w_ic = n_lot["IC"] / nav
    w_im = n_lot["IM"] / nav
    declared_pct = (w_ic + w_im) * DECLARED_L2_VOL_PCT

    rho_fs = corr(s_ic, s_im)
    sig_ic, sig_im = ann_vol(s_ic), ann_vol(s_im)
    summary = {}
    for wnd in WINDOWS:
        rows = with_block(rolling(dates, s_ic, s_im, wnd), w_ic, w_im)
        summary[str(wnd)] = summarize(rows, declared_pct)
        if summary[str(wnd)] is None:
            return None, {"verdict": V_BLOCK, "why": "window %d produced no rows" % wnd}

    return {
        "headline": {
            "rho_full": round(rho_fs, 4),
            "sigma_ic_pct": round(sig_ic, 3),
            "sigma_im_pct": round(sig_im, 3),
            "block_vol_full_pct": round(block_vol_pct(w_ic, sig_ic, w_im, sig_im, rho_fs), 3),
            "declared_block_vol_pct": round(declared_pct, 3),
            "declared_rho": DECLARED_RHO,
            "declared_l2_vol_pct": DECLARED_L2_VOL_PCT,
            "common_days": len(dates),
            "span": [dates[0], dates[-1]],
        },
        "weights": {"w_ic": round(w_ic, 6), "w_im": round(w_im, 6),
                    "notional_per_lot_cny": {k: round(v, 2) for k, v in n_lot.items()},
                    "nav_cny": nav},
        "rolling": summary,
        "by_year": by_year(dates, s_ic, s_im, w_ic, w_im),
        "judgment": judge(summary, declared_pct),
    }, None


def cross_face(body):
    """Reconcile the futures block against the sibling face's own measurement.

    The sibling publishes `l2_vol_measured_pct` for the same 1/1 rung from the same two
    series, so the two numbers must be bit-identical; if they are not, one of the faces has
    drifted and a reader must not be told both.  A missing sibling is named, never scored 0.
    """
    path = SIBLING
    if not os.path.exists(path):
        return {"status": "SIBLING_FACE_MISSING", "sibling_face": path}
    rung = (((read_json(path).get("measured") or {}).get("rungs") or {}).get("1/1") or {})
    theirs = rung.get("l2_vol_measured_pct")
    if theirs is None:
        return {"status": "SIBLING_RUNG_MISSING", "sibling_face": path}
    mine = body["headline"]["block_vol_full_pct"]
    delta = mine - float(theirs)
    return {
        "status": "CROSS_FACE_MATCHES" if abs(delta) <= NUM_TOL else "CROSS_FACE_DIVERGES",
        "sibling_face": "results/idx_fut_carry_ladder_risk.json",
        "sibling_l2_vol_measured_pct": round(float(theirs), 3),
        "this_face_block_vol_full_pct": mine,
        "delta_pp": round(delta, 3),
        "why_the_declared_labels_differ":
            "the sibling's rung declares 10.46% because that column already includes the "
            "equity sleeve; this face's 8.96% is the futures block alone, so the two "
            "declared numbers are not two answers to one question",
    }


def build():
    if not os.path.exists(LATTICE):
        return None, {"verdict": V_BLOCK, "why": "ladder face missing: %s" % LATTICE}
    lattice = read_json(LATTICE)
    nav = float(lattice.get("nav_cny") or 0.0)
    if nav <= 0:
        return None, {"verdict": V_BLOCK, "why": "ladder publishes no nav_cny"}
    legs = {p: spread_leg(p) for p in ("IC", "IM")}
    for p, leg in legs.items():
        if "_refused" in leg:
            return None, {"verdict": V_BLOCK,
                          "why": "leg %s refused: %s" % (p, leg["_refused"])}
        if leg["days"] < MIN_DAYS:
            return None, {"verdict": V_BLOCK,
                          "why": "leg %s has %d days, need %d" % (p, leg["days"], MIN_DAYS)}
    body, refusal = measure(legs, lattice, nav)
    if refusal:
        return None, refusal
    face = {
        "schema": SCHEMA,
        "kind": KIND,
        "evidence_cutoff": body["headline"]["span"][1],
        "inputs": {
            "lattice": {"path": "results/policy_return_lattice.json",
                        "sha256": digest(LATTICE)},
            "sibling": {"path": "results/idx_fut_carry_ladder_risk.json",
                        "sha256": (digest(SIBLING) if os.path.exists(SIBLING) else None)},
            "legs": {p: {"index": legs[p].get("index"), "span": legs[p]["span"],
                         "days": legs[p]["days"]} for p in ("IC", "IM")},
        },
        "params": {"windows": list(WINDOWS),
                   "declared_l2_vol_pct": DECLARED_L2_VOL_PCT,
                   "declared_rho": DECLARED_RHO,
                   "instruction_rung": [1, 1],
                   "nav_cny": nav},
        "scope_limits": [
            "futures block only (1 lot IC + 1 lot IM); the equity sleeve, financing,",
            "margin and costs stay in results/idx_fut_carry_ladder_risk.json",
        ],
        "generated": None,
    }
    face.update(body)
    face["cross_face"] = cross_face(body)
    return face, None


# ------------------------------------------------------------------ check (pure classifier)
def classify(face, lattice_sha, leg_meta, recomputed, sibling_sha=None):
    """Return (rc, word, detail).  A drift in *inputs* says STALE; a disagreement on the
    same inputs says CHECK FAILED and never carries the STALE word (r1934 word contract)."""
    inp = (face or {}).get("inputs") or {}
    if ((inp.get("lattice") or {}).get("sha256") or "") != (lattice_sha or ""):
        return 3, "STALE", "ladder face changed since this one was priced"
    sib_old = (inp.get("sibling") or {}).get("sha256")
    if sibling_sha is not None and (sib_old or "") != (sibling_sha or ""):
        return 3, "STALE", "sibling risk face changed since this one was priced"
    for p, m in (leg_meta or {}).items():
        old = ((inp.get("legs") or {}).get(p) or {})
        if list(old.get("span") or []) != list((m or {}).get("span") or []) \
                or old.get("days") != (m or {}).get("days"):
            return 3, "STALE", "leg %s moved since this one was priced" % p
    if recomputed is None:
        return 3, "STALE", "recompute unavailable"
    pub = (face or {}).get("headline") or {}
    for key in ("rho_full", "block_vol_full_pct", "declared_block_vol_pct", "common_days"):
        a, b = pub.get(key), recomputed.get("headline", {}).get(key)
        if a is None or b is None:
            return 3, "CHECK FAILED", "headline field %s missing" % key
        if abs(float(a) - float(b)) > NUM_TOL:
            return 3, "CHECK FAILED", "headline %s printed %s recomputes %s" % (key, a, b)
    if (face or {}).get("judgment") != recomputed.get("judgment"):
        return 3, "CHECK FAILED", "verdict tokens differ from a fresh derivation"
    if ((face.get("cross_face") or {}).get("status")
            != (recomputed.get("cross_face") or {}).get("status")):
        return 3, "CHECK FAILED", "cross-face reconciliation differs from a fresh derivation"
    return 0, "CHECK_OK", "face matches its inputs"


def cmd_check(_args=None):
    if not os.path.exists(OUT):
        print("STALE face missing: %s" % OUT)
        return 3
    face = read_json(OUT)
    if not os.path.exists(LATTICE):
        print("STALE ladder missing: %s" % LATTICE)
        return 3
    lattice = read_json(LATTICE)
    nav = float(lattice.get("nav_cny") or 0.0)
    legs = {p: spread_leg(p) for p in ("IC", "IM")}
    leg_meta = {p: {"span": legs[p].get("span"), "days": legs[p].get("days")}
                for p in legs if "_refused" not in legs[p]}
    recomputed = None
    if not any("_refused" in v for v in legs.values()) and nav > 0:
        recomputed, _refusal = measure(legs, lattice, nav)
        if recomputed is not None:
            recomputed["cross_face"] = cross_face(recomputed)
    rc, word, detail = classify(face, digest(LATTICE), leg_meta, recomputed,
                                digest(SIBLING) if os.path.exists(SIBLING) else None)
    print("%s: %s" % (word, detail))
    return rc


# ------------------------------------------------------------------ page
def render_page(face):
    j = face["judgment"]
    hl = face["headline"]
    w = face["weights"]
    lines = []
    add = lines.append
    add("# 梯子的两个风险常数是不是常数")
    add("")
    add("generated %s | 证据截止 %s | 面 `results/idx_fut_carry_ladder_stability.json`"
        % (face["generated"], face["evidence_cutoff"]))
    add("")
    add("`policy_return_lattice.py` 用**一个波动率、一个相关系数**给整块期货定价："
        "`l2 = 名义/nav × %.1f%%`，相关系数写死 %.2f。r2105 已经在全样本上量过这两个数"
        "（IC %.2f%%、IM %.2f%%、相关 %.3f），但八年平均正是风险预算最不该建在上面的东西。"
        "这一页只回答一个问题：**这两个数会动吗，动起来是不是往痛的方向动。**"
        % (hl["declared_l2_vol_pct"], hl["declared_rho"], hl["sigma_ic_pct"],
           hl["sigma_im_pct"], hl["rho_full"]))
    add("")
    add("## 一、先看今天梯子上印的那个数与量出来的那个数")
    add("")
    add("| 项目 | 数值 |")
    add("|---|---|")
    add("| 每手名义（IC / IM） | %s / %s 元 |"
        % (format(w["notional_per_lot_cny"]["IC"], ",.0f"),
           format(w["notional_per_lot_cny"]["IM"], ",.0f")))
    add("| 权重（各一手 / 100 万） | %.3f / %.3f |" % (w["w_ic"], w["w_im"]))
    add("| 梯子声明的期货块波动 | **%.2f%%**（= (%.3f+%.3f) × %.1f%%） |"
        % (hl["declared_block_vol_pct"], w["w_ic"], w["w_im"], hl["declared_l2_vol_pct"]))
    add("| 全样本实测期货块波动 | **%.2f%%** |" % hl["block_vol_full_pct"])
    add("| 少报 | **%.2f pp** |" % (hl["block_vol_full_pct"] - hl["declared_block_vol_pct"]))
    add("| 共同交易日 | %d（%s → %s） |"
        % (hl["common_days"], hl["span"][0], hl["span"][1]))
    add("")
    cf = face.get("cross_face") or {}
    add("跨面对照：`idx_fut_carry_ladder_risk` 同一档量出的期货块波动 **%s%%**，本页 **%.3f%%**，"
        "差 %s pp → **%s**。（兄弟面那一档印的 10.46%% 已经把权益袖算进去，"
        "本页的 %.2f%% 只是期货块，两个声明数不是同一个问题的两个答案。）"
        % (cf.get("sibling_l2_vol_measured_pct"), hl["block_vol_full_pct"],
           cf.get("delta_pp"), cf.get("status"), hl["declared_block_vol_pct"]))
    add("")
    add("## 二、把这两个数沿时间展开（滚动窗）")
    add("")
    add("| 窗长 | 相关 5% | 中位 | 95% | 最大 | 块波动 最小 | 中位 | 95% | 最大 | 超过声明数的窗口占比 |")
    add("|---|---|---|---|---|---|---|---|---|---|")
    for wnd in [str(x) for x in WINDOWS]:
        s = face["rolling"][wnd]
        add("| %s 日 | %.3f | %.3f | %.3f | %.3f | %.2f%% | %.2f%% | %.2f%% | %.2f%% | %.1f%% |"
            % (wnd, s["rho_p05"], s["rho_median"], s["rho_p95"], s["rho_max"],
               s["block_vol_min_pct"], s["block_vol_median_pct"], s["block_vol_p95_pct"],
               s["block_vol_max_pct"], 100.0 * s["share_windows_above_declared"]))
    add("")
    s120 = face["rolling"]["120"]
    add("* 最惨的一个 120 日窗收在 **%s**：块波动 **%.2f%%**（相关 %.3f）。"
        % (s120["worst_window"]["end"], s120["worst_window"]["block_vol_pct"],
           s120["worst_window"]["rho"]))
    add("* 两条腿最同向的窗收在 **%s**：相关 **%.3f**，块波动 %.2f%%。"
        % (s120["most_correlated_window"]["end"], s120["most_correlated_window"]["rho"],
           s120["most_correlated_window"]["block_vol_pct"]))
    add("* 最分散的窗收在 **%s**：相关 %.3f，块波动 %.2f%%。"
        % (s120["least_correlated_window"]["end"], s120["least_correlated_window"]["rho"],
           s120["least_correlated_window"]["block_vol_pct"]))
    add("")
    add("## 三、逐年（读者可以拿自己记得的那一年来对）")
    add("")
    add("| 年 | 交易日 | 相关 | IC 波动 | IM 波动 | 块波动 |")
    add("|---|---|---|---|---|---|")
    for yr, r in sorted(face["by_year"].items()):
        add("| %s | %d | %.3f | %.2f%% | %.2f%% | %.2f%% |"
            % (yr, r["days"], r["rho"], r["sig_ic_pct"], r["sig_im_pct"], r["block_vol_pct"]))
    add("")
    add("## 四、判词（冻结于首跑之前）")
    add("")
    add("| 判词 | 读数 |")
    add("|---|---|")
    add("| 相关稳不稳 | **%s**（120 日 5%%→95%% 跨 %.3f） |"
        % (j["rho_stability"], j["rho_range_120d"]))
    add("| 压力下分散还在不在 | **%s**（95%% 块波动 / 中位 = %s 倍，95%% 相关 − 中位 = %s） |"
        % (j["stress_concentration"], j["stress_vol_ratio"],
           round(face["rolling"]["120"]["rho_p95"] - face["rolling"]["120"]["rho_median"], 4)))
    add("| 声明数覆盖面 | **%s**（%.1f%% 的 120 日窗高于声明数） |"
        % (j["declaration_coverage"],
           100.0 * face["rolling"]["120"]["share_windows_above_declared"]))
    add("| 少报多少 | 中位窗 **%.2f pp** / 95%% 窗 **%.2f pp** |"
        % (j["understatement_at_median_pp"], j["understatement_at_p95_pp"]))
    add("")
    add("## 五、这一页**没有**覆盖什么")
    add("")
    add("* 权益袖、融资成本、保证金、交易成本：全部留在 "
        "`results/idx_fut_carry_ladder_risk.json`（含袖子的逐档风险），本页不重算、不合并。")
    add("* 本页所有腿序列来自 `idx_fut_carry_risk.product_spread` 的 import，"
        "与 risk / pause-price / ladder_risk 三面同源；每手名义读自梯子自己的 rung，未在此声明。")
    add("")
    add("## 六、可执行结论")
    add("")
    add("**把 `L2_CARRY_VOL = 4.0` 留在原处，等于告诉读者这块期货的风险是 %.2f%%，"
        "而它过去 %d 个共同交易日里有 %.1f%% 的 120 日窗比这个数高，中位 %.2f%%、"
        "最坏 %.2f%%。** 若要把 8–12%% 的带子当风险预算用，期货块的输入必须换成滚动读数，"
        "并且按 **95%% 窗（%.2f%%）** 定手数，而不是按中位窗。"
        % (hl["declared_block_vol_pct"], hl["common_days"],
           100.0 * face["rolling"]["120"]["share_windows_above_declared"],
           s120["block_vol_median_pct"], s120["block_vol_max_pct"],
           s120["block_vol_p95_pct"]))
    add("")
    return "\n".join(lines)


def cmd_run(_args=None):
    import datetime
    face, refusal = build()
    if refusal:
        print(refusal["verdict"] + ": " + refusal["why"])
        return 2
    face["generated"] = datetime.datetime.now().astimezone().replace(microsecond=0).isoformat()
    write_json(OUT, face)
    os.makedirs(os.path.dirname(DOC), exist_ok=True)
    with io.open(DOC, "w", encoding="utf-8", newline="\n") as f:
        f.write(render_page(face))
        f.write("\n")
    hl = face["headline"]
    print("OK rho_full=%.4f block_vol=%.3f declared=%.3f median120=%.3f p95_120=%.3f tokens=%s/%s/%s"
          % (hl["rho_full"], hl["block_vol_full_pct"], hl["declared_block_vol_pct"],
             face["rolling"]["120"]["block_vol_median_pct"],
             face["rolling"]["120"]["block_vol_p95_pct"],
             face["judgment"]["rho_stability"],
             face["judgment"]["stress_concentration"],
             face["judgment"]["declaration_coverage"]))
    return 0


# ------------------------------------------------------------------ selftest
def cmd_selftest(_args=None):
    legs = []
    fails = []

    def ok(cond, name):
        legs.append((name, bool(cond)))
        if not cond:
            fails.append(name)

    ok(abs(ann_vol([0.01] * 50) or 0.0) < 1e-9, "constant series has zero vol")
    ok(abs((corr([1, 2, 3, 4], [2, 4, 6, 8]) or 0) - 1.0) < 1e-9, "identical shape corr = 1")
    ok(abs(block_vol_pct(1.0, 10.0, 1.0, 10.0, 1.0) - 20.0) < 1e-9, "rho=1 sums the vols")
    ok(abs(block_vol_pct(1.0, 10.0, 1.0, 10.0, 0.0) - math.sqrt(200.0)) < 1e-9,
       "rho=0 quadrature")

    # regime switch: perfectly anti-correlated then perfectly correlated -> rho range ~2
    n = 500
    dates = ["2020-%03d" % i for i in range(n)]
    a, b = [], []
    for i in range(n):
        x = 0.01 if i % 2 else -0.01
        y = x if i < n // 2 else -x
        a.append(x + (i * 1e-6))
        b.append(y)
    rows = with_block(rolling(dates, a, b, 120), 1.0, 1.0)
    s = summarize(rows, 15.0)
    ok(len(rows) > 0, "rolling produced rows")
    ok(s["rho_min"] < -0.5 and s["rho_max"] > 0.5, "regime switch spans the rho range")
    ok(judge({"120": s}, 15.0)["rho_stability"] == V_RHO_WIDE,
       "wide rho range flips RHO_RANGE_WIDE")

    # same series twice -> rho pinned at 1 -> tight, and always above declaration
    rows2 = with_block(rolling(dates, a, a, 120), 1.0, 1.0)
    s2 = summarize(rows2, 0.5)
    ok(s2["rho_min"] > 0.999 and s2["rho_max"] > 0.999, "rho pinned at 1 for identical legs")
    ok(judge({"120": s2}, 0.5)["rho_stability"] == V_RHO_TIGHT, "tight range flips RHO_TIGHT")
    ok(judge({"120": summarize(rows2, 1e6)}, 1e6)["declaration_coverage"] == V_SOMETIMES_ABOVE,
       "an absurd declaration is sometimes exceeded")
    ok(judge({"120": summarize(rows2, 0.5)}, 0.5)["declaration_coverage"] == V_ALWAYS_ABOVE,
       "a tiny declaration is always exceeded")

    ok(pctl([5, 1, 3], 0.5) == 3 and pctl([1, 2, 3, 4], 0.0) == 1 and pctl([], 0.5) is None,
       "percentile nearest-rank")

    # free money: the two legs converge -> block vol must rise with rho at fixed sigmas
    v_lo = block_vol_pct(1.0, 6.0, 1.0, 7.0, 0.0)
    v_hi = block_vol_pct(1.0, 6.0, 1.0, 7.0, 0.9)
    ok(v_hi > v_lo, "higher rho raises the block vol")

    # classifier: input drift says STALE, same-input disagreement says CHECK FAILED
    face = {"inputs": {"lattice": {"sha256": "aaa"}, "legs": {"IC": {"span": ["d1", "d2"], "days": 2}}},
            "headline": {"rho_full": 0.8333, "block_vol_full_pct": 14.28,
                         "declared_block_vol_pct": 9.36, "common_days": 1052},
            "judgment": {"rho_stability": V_RHO_WIDE}}
    good = {"headline": dict(face["headline"]), "judgment": dict(face["judgment"])}
    rc, word, _d = classify(face, "aaa", {"IC": {"span": ["d1", "d2"], "days": 2}}, good)
    ok(rc == 0 and word == "CHECK_OK", "identical inputs and numbers pass")
    rc, word, _d = classify(face, "bbb", {"IC": {"span": ["d1", "d2"], "days": 2}}, good)
    ok(rc == 3 and word == "STALE", "ladder drift says STALE")
    rc, word, _d = classify(face, "aaa", {"IC": {"span": ["d1", "d3"], "days": 3}}, good)
    ok(rc == 3 and word == "STALE", "leg drift says STALE")
    bad = {"headline": dict(face["headline"], block_vol_full_pct=13.0),
           "judgment": dict(face["judgment"])}
    rc, word, _d = classify(face, "aaa", {"IC": {"span": ["d1", "d2"], "days": 2}}, bad)
    ok(rc == 3 and word == "CHECK FAILED" and "STALE" not in word,
       "tampered number says CHECK FAILED without the STALE word")
    bad2 = {"headline": dict(face["headline"]), "judgment": {"rho_stability": V_RHO_TIGHT}}
    rc, word, _d = classify(face, "aaa", {"IC": {"span": ["d1", "d2"], "days": 2}}, bad2)
    ok(rc == 3 and word == "CHECK FAILED", "token drift says CHECK FAILED")
    rc, word, _d = classify(face, "aaa", {"IC": {"span": ["d1", "d2"], "days": 2}}, None)
    ok(rc == 3 and word == "STALE", "unavailable recompute is STALE not a silent pass")
    face_s = {"inputs": dict(face["inputs"], sibling={"sha256": "s0"}),
              "headline": face["headline"], "judgment": face["judgment"]}
    rc, word, _d = classify(face_s, "aaa", {"IC": {"span": ["d1", "d2"], "days": 2}}, good, "s1")
    ok(rc == 3 and word == "STALE", "sibling drift says STALE")
    good_x = dict(good, cross_face={"status": "CROSS_FACE_MATCHES"})
    face_x = dict(face, cross_face={"status": "CROSS_FACE_DIVERGES"})
    rc, word, _d = classify(face_x, "aaa", {"IC": {"span": ["d1", "d2"], "days": 2}}, good_x)
    ok(rc == 3 and word == "CHECK FAILED", "cross-face token drift says CHECK FAILED")

    passed = sum(1 for _n, c in legs if c)
    for name, cond in legs:
        if not cond:
            print("FAIL " + name)
    print("selftest %d/%d %s" % (passed, len(legs), "PASS" if not fails else "FAIL"))
    return 0 if not fails else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("run", help="measure and publish the face + page")
    sub.add_parser("check", help="re-probe inputs; STALE vs CHECK FAILED")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return cmd_selftest()
    if args.cmd == "check":
        return cmd_check()
    return cmd_run()


if __name__ == "__main__":
    raise SystemExit(main())

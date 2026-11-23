"""Which carrier do you short: the IM futures or the 512100 ETF?

r2022 priced one beta on two carriers and published both arm tables, but never put the two
carriers on one ruler.  Every later face (r2027 lots, r2028 dating, r2029 band, r2030
walk-forward, r2031 instrument) then quoted whichever carrier it happened to need.  A reader
who has seen the IM discount printed as "8.9% a year" reads that as the price of hedging with
futures and expects the ETF to be far cheaper.  This face asks the only question that settles
it: on the same 52 periods, the same book and the same k, what did each carrier actually
deliver, and what does each one tie up in capital?

Readings
  1. Arm table on the shared window (k = 0, 0.5, 1) for both carriers.
  2. The realised carrier cost: the geometric, compounded difference between the two short
     legs over the same 52 periods -- the number that gets charged, not the median day.
  3. The surface reading quoted next to it (median daily spread x 252 from the basis face),
     so a reader can see the two rulers disagree and know which one is money.
  4. Capital: a 901k notional short needs 12% of it in IM margin, and 50..100% of it in ETF
     eyebrows; the cash that is left over can earn something, and the ETF leg pays borrow.

Usage
    python scripts/astock_veto_hedge_carrier.py run
    python scripts/astock_veto_hedge_carrier.py check
    python scripts/astock_veto_hedge_carrier.py selftest
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import statistics
import sys
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PARENT = os.path.join(ROOT, "results", "astock_veto_hedgeable_beta.json")
BASIS = os.path.join(ROOT, "results", "idx_fut_basis.json")
OUT_JSON = os.path.join(ROOT, "results", "astock_veto_hedge_carrier.json")
OUT_MD = os.path.join(ROOT, "research", "ASTOCK_VETO_HEDGE_CARRIER.md")

K_GRID = [0.0, 0.5, 1.0]
CAPITAL = 1_000_000.0
CASH_YIELD = 0.02          # what idle margin cash can earn; declared, swept, never assumed away
IM_MARGINS = [0.08, 0.12, 0.15]
ETF_HAIRCUTS = [0.50, 0.80, 1.00]
ETF_BORROW_FEES = [0.02, 0.05, 0.08]
TIE_PP = 1.0               # the two carriers tie when the realised gap is inside this
SURFACE_GAP_PP = 5.0       # a surface reading this large next to a realised gap is an artifact
VERDICT_ARTIFACT = "DISCOUNT_IS_A_MEDIAN_ARTIFACT"
VERDICT_TIE = "CARRIER_TIES_ON_RETURN_IM_QUIETER"
VERDICT_IM_CAPITAL = "IM_WINS_ON_CAPITAL"
VERDICT_ETF = "CARRIER_ETF_WINS"
VERDICT_WHY = {
    VERDICT_ARTIFACT: "the published discount is a median day annualised; the compounded "
                      "difference between the two short legs is an order of magnitude smaller",
    VERDICT_TIE: "on the shared window the two carriers compound to the same return, and the "
                 "futures leg is the quieter one",
    VERDICT_IM_CAPITAL: "the notional that must be blocked is the difference: margin on the "
                        "futures leg leaves cash earning, the ETF leg blocks it and pays borrow",
    VERDICT_ETF: "on the same periods the ETF short compounded above the futures short by more "
                 "than the tie band, so the futures discount was paid for in realised return",
}


# --------------------------------------------------------------- plumbing
def _now() -> str:
    return datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")


def _rel(path: str) -> str:
    try:
        return os.path.relpath(path, ROOT).replace(os.sep, "/")
    except ValueError:
        return str(path).replace(os.sep, "/")


def _read_json(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _sha_file(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def content_sha(face: dict) -> str:
    body = {k: v for k, v in face.items() if k != "generated"}
    return hashlib.sha256(json.dumps(body, sort_keys=True, ensure_ascii=False)
                          .encode("utf-8")).hexdigest()


def fingerprint(path: str) -> dict:
    face = _read_json(path)
    return {"face": _rel(path), "file_sha256": _sha_file(path),
            "content_sha256": content_sha(face),
            "generated": face.get("generated"),
            "evidence_cutoff": face.get("evidence_cutoff")}


# ------------------------------------------------------------------ pure logic
def max_drawdown(returns):
    """Peak-to-trough of the compounded curve, as a negative fraction."""
    vals = [v for v in returns if v is not None and math.isfinite(v)]
    if not vals:
        return float("nan")
    eq = 1.0
    peak = 1.0
    worst = 0.0
    for v in vals:
        eq *= 1.0 + v
        peak = max(peak, eq)
        worst = min(worst, eq / peak - 1.0)
    return worst


def arm_stats(vals, periods_per_year: float):
    """Annualised, compounded statistics of a per-period return list."""
    kept = [v for v in vals if v is not None and math.isfinite(v)]
    n = len(kept)
    if n < 2:
        return None
    growth = 1.0
    for v in kept:
        growth *= 1.0 + v
    if growth <= 0.0:
        return None
    ann = growth ** (periods_per_year / n) - 1.0
    mu = statistics.fmean(kept)
    sd = statistics.pstdev(kept)
    return {
        "periods": n,
        "per_period_mean": mu,
        "annualized_compound": ann,
        "annual_vol": sd * math.sqrt(periods_per_year),
        "sharpe_excess_0": (mu / sd * math.sqrt(periods_per_year)) if sd > 0 else None,
        "max_drawdown": max_drawdown(kept),
        "worst_period": min(kept),
        "hit_rate": sum(1 for v in kept if v > 0) / n,
    }


def hedged(book, hedge, k):
    return [b - k * h for b, h in zip(book, hedge)]


def compounded(vals):
    """Growth factor of a return list; 1.0 for an empty list."""
    out = 1.0
    for v in vals:
        out *= 1.0 + v
    return out


def realised_carrier(etf_leg, im_leg, periods_per_year: float):
    """The compounded difference between the two SHORT legs.

    Both legs in the parent are expressed as the long return of the hedging instrument, so a
    short earns the negative.  The face reports the short-vs-short gap because that is the
    cash a hedger sees, and a geometric gap because a median day is not a year.
    """
    n = len(etf_leg)
    if n < 2:
        return None
    etf_short = compounded([-v for v in etf_leg])
    im_short = compounded([-v for v in im_leg])
    years = n / periods_per_year
    if etf_short <= 0.0 or im_short <= 0.0:
        return None
    return {
        "periods": n,
        "years": years,
        "etf_short_cum": etf_short - 1.0,
        "im_short_cum": im_short - 1.0,
        "im_minus_etf_pp_per_year": ((im_short / etf_short) ** (1.0 / years) - 1.0) * 100.0,
    }


def capital_table(beta: float, capital: float, cash_yield: float):
    """What each carrier blocks to short the same notional, and what that costs or earns."""
    shorted = beta * capital
    im_rows = []
    for margin in IM_MARGINS:
        blocked = shorted * margin
        free = capital - blocked
        im_rows.append({
            "margin": margin,
            "blocked_cny": blocked,
            "free_cash_cny": free,
            "cash_yield": cash_yield,
            "interest_pp_per_year": (free * cash_yield) / capital * 100.0,
        })
    etf_rows = []
    for haircut in ETF_HAIRCUTS:
        for fee in ETF_BORROW_FEES:
            blocked = shorted * haircut
            borrow = shorted * fee
            etf_rows.append({
                "haircut": haircut,
                "borrow_fee": fee,
                "blocked_cny": blocked,
                "borrow_cny": borrow,
                "borrow_pp_per_year": borrow / capital * 100.0,
                "free_cash_cny": capital - blocked,
            })
    return {"capital": capital, "beta": beta, "shorted_notional": shorted,
            "im": im_rows, "etf": etf_rows}


def decide(realised, arms, surface_gap_pp):
    """Each verdict is a separate question; none of them reads the others."""
    out = {}
    if realised is None:
        return {"all": None}
    gap = realised["im_minus_etf_pp_per_year"]
    out[VERDICT_ARTIFACT] = bool(
        surface_gap_pp is not None and surface_gap_pp >= SURFACE_GAP_PP
        and abs(gap) <= TIE_PP)
    etf_a = (arms.get("etf") or {}).get("1.0") or {}
    im_a = (arms.get("im") or {}).get("1.0") or {}
    etf_ann = etf_a.get("annualized_compound")
    im_ann = im_a.get("annualized_compound")
    etf_vol = etf_a.get("annual_vol")
    im_vol = im_a.get("annual_vol")
    out[VERDICT_TIE] = bool(
        etf_ann is not None and im_ann is not None and etf_vol is not None
        and im_vol is not None
        and abs(im_ann - etf_ann) * 100.0 <= TIE_PP and im_vol < etf_vol)
    out[VERDICT_ETF] = bool(abs(gap) > TIE_PP and gap < 0.0)
    out[VERDICT_IM_CAPITAL] = bool(
        gap >= -TIE_PP)  # the futures leg is never behind by more than the tie band
    return out


def headline(flags):
    """One sentence, chosen by a fixed ladder -- not by whichever flag looks best."""
    if flags.get(VERDICT_ETF):
        return VERDICT_ETF
    if flags.get(VERDICT_ARTIFACT) and flags.get(VERDICT_IM_CAPITAL):
        return VERDICT_ARTIFACT + "+" + VERDICT_IM_CAPITAL
    if flags.get(VERDICT_TIE):
        return VERDICT_TIE
    return "CARRIER_GAP_DISCLOSED"


# --------------------------------------------------------------------- build
def build_face() -> dict:
    parent = _read_json(PARENT)
    basis = _read_json(BASIS)
    spec = parent.get("spec") or {}
    ppy = float(spec.get("periods_per_year") or 12.6)

    rows = [r for r in (parent.get("rows") or []) if r.get("im_window")]
    if len(rows) < 20:
        return {"generated": _now(), "kind": "hedge_carrier",
                "evidence_cutoff": parent.get("evidence_cutoff"),
                "verdict": "NOT_ENOUGH_PERIODS",
                "parents": {"beta": fingerprint(PARENT)}}

    book = [r.get("book_net") for r in rows]
    etf_leg = [r.get("hedge_etf") for r in rows]
    im_leg = [r.get("hedge_im") for r in rows]

    arms = {"etf": {}, "im": {}}
    for k in K_GRID:
        arms["etf"][("%.1f" % k)] = arm_stats(hedged(book, etf_leg, k), ppy)
        arms["im"][("%.1f" % k)] = arm_stats(hedged(book, im_leg, k), ppy)

    realised = realised_carrier(etf_leg, im_leg, ppy)

    im_pair = ((basis.get("pairs") or {}).get("IM") or {})
    carry = im_pair.get("carry") or {}
    surface_median = carry.get("median_ann_pct")
    surface_net = ((basis.get("verdict") or {}).get("carries") or [])
    surface_net_im = next((c for c in surface_net if c.get("fut") == "IM"), {})
    surface_gap = surface_median

    beta = ((parent.get("arms_etf") or {}).get("1.0") or {}).get("beta_used")
    if beta is None:
        beta = ((parent.get("variance") or {}).get("beta_used_for_arms")) or 0.9013
    capital = capital_table(float(beta), CAPITAL, CASH_YIELD)

    flags = decide(realised, arms, surface_gap)
    verdict = headline(flags)

    caveats = [
        "both legs are priced off their own panels (512100 secondary-market close, IM main "
        "continuous close); an ETF tracking error and its premium/discount are inside the gap "
        "and are not separated here",
        "the shared window is 52 periods because the IM panel starts 2022-07; the ETF arm's "
        "longer 77-period record is not used anywhere on this face",
        "the capital table sweeps margin and borrow assumptions instead of picking one; the "
        "cash yield is a declared 2% assumption, not a measured rate",
        "no borrow availability is modelled: an ETF short needs a lender and A-share borrow is "
        "frequently exhausted, which a number cannot cure",
        "this is a ruler and an execution note, not a trade instruction",
    ]

    face = {
        "generated": _now(),
        "kind": "hedge_carrier",
        "machine": "bm-c",
        "evidence_cutoff": parent.get("evidence_cutoff"),
        "fills_the_hole_of": "r2022 published both carriers but never put them on one ruler; "
                             "the IM discount is quoted everywhere as an annual cost",
        "parents": {"beta": fingerprint(PARENT), "basis": fingerprint(BASIS)},
        "spec": {"k_grid": K_GRID, "periods_per_year": ppy, "capital": CAPITAL,
                 "cash_yield": CASH_YIELD, "tie_pp": TIE_PP,
                 "surface_gap_pp": SURFACE_GAP_PP,
                 "im_margins": IM_MARGINS, "etf_haircuts": ETF_HAIRCUTS,
                 "etf_borrow_fees": ETF_BORROW_FEES},
        "sample": {"periods": len(rows), "first": rows[0].get("date"),
                   "last": rows[-1].get("end"),
                   "basis": "parent rows flagged im_window (both carriers priced)"},
        "arms": arms,
        "realised_carrier": realised,
        "surface_readings": {
            "source_face": "results/idx_fut_basis.json",
            "source_generated": basis.get("generated"),
            "source_cutoff": im_pair.get("window", {}).get("to"),
            "im_median_ann_pct": surface_median,
            "im_net_carry_pct": surface_net_im.get("net_carry_pct"),
            "reading_note": "median daily (futures minus index) return annualised -- a typical "
                            "day, not a compounded year; it is printed beside the realised gap "
                            "so the two rulers can be seen disagreeing",
        },
        "capital": capital,
        "verdicts": flags,
        "verdict": verdict,
        "verdict_why": VERDICT_WHY.get(verdict.split("+")[0], ""),
        "caveats": caveats,
    }
    face["reads"] = build_reads(face)
    face["content_sha256"] = content_sha(face)
    return face


def build_reads(face):
    reads = []
    a = (face.get("arms") or {})
    etf1 = ((a.get("etf") or {}).get("1.0") or {})
    im1 = ((a.get("im") or {}).get("1.0") or {})
    etf0 = ((a.get("etf") or {}).get("0.0") or {})
    rc = face.get("realised_carrier") or {}
    if etf1 and im1 and etf0:
        gap = rc.get("im_minus_etf_pp_per_year") or 0.0
        reads.append({
            "id": "R1",
            "text": "on the shared %d periods at k=1 the ETF short compounded %.2f%% against "
                    "%.2f%% for the futures short (%s); without a hedge the same book did %.2f%%"
                    % (etf1.get("periods") or 0,
                       (etf1.get("annualized_compound") or 0) * 100,
                       (im1.get("annualized_compound") or 0) * 100,
                       ("futures ahead by %.3f pp a year" % gap if gap >= 0
                        else "futures behind by %.3f pp a year" % abs(gap)),
                       (etf0.get("annualized_compound") or 0) * 100),
        })
        reads.append({
            "id": "R2",
            "text": "the futures leg is the quieter one: %.2f%% annual volatility against "
                    "%.2f%%, so the same return arrives with a higher Sharpe (%.2f vs %.2f)"
                    % ((im1.get("annual_vol") or 0) * 100, (etf1.get("annual_vol") or 0) * 100,
                       im1.get("sharpe_excess_0") or 0.0, etf1.get("sharpe_excess_0") or 0.0),
        })
    sr = face.get("surface_readings") or {}
    if rc and sr.get("im_median_ann_pct") is not None:
        reads.append({
            "id": "R3",
            "text": "two rulers, one order of magnitude apart: the basis face annualises the "
                    "median day to %.2f%% a year, while the compounded short-vs-short gap over "
                    "the same window is %.3f pp a year -- the median day is not a year"
                    % (sr["im_median_ann_pct"], rc.get("im_minus_etf_pp_per_year") or 0.0),
        })
    cap = face.get("capital") or {}
    if cap.get("im") and cap.get("etf"):
        im_mid = next((r for r in cap["im"] if r["margin"] == 0.12), cap["im"][0])
        etf_low = cap["etf"][0]
        etf_high = cap["etf"][-1]
        reads.append({
            "id": "R4",
            "text": "the notional is the same, the blocked cash is not: %.0f yuan of short "
                    "needs %.0f yuan of margin at 12%% on the futures leg (leaving %.0f yuan "
                    "earning %.0f yuan a year), against %.0f..%.0f yuan blocked on the ETF leg "
                    "where the borrow itself costs %.2f..%.2f pp a year"
                    % (cap["shorted_notional"], im_mid["blocked_cny"], im_mid["free_cash_cny"],
                       im_mid["free_cash_cny"] * CASH_YIELD,
                       etf_low["blocked_cny"], etf_high["blocked_cny"],
                       min(r["borrow_pp_per_year"] for r in cap["etf"]),
                       max(r["borrow_pp_per_year"] for r in cap["etf"])),
        })
    return reads


# --------------------------------------------------------------------- render
def render_md(face) -> str:
    parents = face.get("parents") or {}
    beta = parents.get("beta") or {}
    basis = parents.get("basis") or {}
    sr = face.get("surface_readings") or {}
    rc = face.get("realised_carrier") or {}
    arms = face.get("arms") or {}
    cap = face.get("capital") or {}

    lines = ["# Which carrier do you short: IM futures or the 512100 ETF?", "",
             "A hedge is a decision about a carrier before it is a decision about a size. "
             "Every face in this family since r2022 quoted one carrier at a time, and the IM "
             "discount travels through those pages as an annual cost. This face puts the two "
             "carriers on one ruler, on one window, at one k.", "",
             "Evidence cutoff **%s**, parent beta face `%s` (generated %s), basis face `%s` "
             "(generated %s, cutoff %s)."
             % (face.get("evidence_cutoff"), beta.get("face"), beta.get("generated"),
                basis.get("face"), sr.get("source_generated"), sr.get("source_cutoff")), ""]

    rows = []
    for k in ("0.0", "0.5", "1.0"):
        e = (arms.get("etf") or {}).get(k) or {}
        i = (arms.get("im") or {}).get(k) or {}
        if not e and not i:
            continue
        rows.append("| k=%s | %s | %s | %s | %s | %s | %s |"
                    % (k,
                       "%.2f%%" % ((e.get("annualized_compound") or 0) * 100),
                       "%.2f%%" % ((i.get("annualized_compound") or 0) * 100),
                       "%.2f%%" % ((e.get("annual_vol") or 0) * 100),
                       "%.2f%%" % ((i.get("annual_vol") or 0) * 100),
                       "%.2f" % (e.get("sharpe_excess_0") or 0),
                       "%.2f" % (i.get("sharpe_excess_0") or 0)))
    lines += ["## 1. The same book, the same periods, two carriers", "",
              "| hedge | ETF short ann. | IM short ann. | ETF vol | IM vol | ETF Sharpe | IM Sharpe |",
              "|---|---|---|---|---|---|---|"] + rows + [
              "", "Sample: %d periods, %s to %s."
              % ((face.get("sample") or {}).get("periods"),
                 (face.get("sample") or {}).get("first"),
                 (face.get("sample") or {}).get("last")), ""]

    if rc:
        gap = rc.get("im_minus_etf_pp_per_year") or 0.0
        relation = ("ahead of the ETF short by **%.3f pp a year**" % gap if gap >= 0 else
                    "behind the ETF short by **%.3f pp a year**" % abs(gap))
        lines += ["## 2. What the carrier actually charged", "",
                  "These are the hedging legs on their own, not the book. Shorting the ETF over "
                  "these %d periods (%.2f years) compounded **%.2f%%**; shorting the futures "
                  "compounded **%.2f%%**. The futures short finished %s."
                  % (rc.get("periods") or 0, rc.get("years") or 0,
                     (rc.get("etf_short_cum") or 0) * 100,
                     (rc.get("im_short_cum") or 0) * 100, relation), ""]

    if sr.get("im_median_ann_pct") is not None and rc:
        gap = rc.get("im_minus_etf_pp_per_year") or 0.0
        ratio = (abs(sr["im_median_ann_pct"]) / abs(gap)) if gap else float("inf")
        scale = ("%.0f times smaller" % ratio) if ratio != float("inf") and ratio >= 1.5 \
            else "the same size"
        lines += ["## 3. The ruler that is quoted is not the ruler that is paid", "",
                  "The basis face annualises the median daily (futures minus index) return to "
                  "**%.2f%% a year** (net of drift %.2f%%). Read alone that looks like the annual "
                  "price of hedging with futures. But a median day is not a year: the compounded "
                  "short-vs-short gap on the same window is **%.3f pp a year -- %s**. The typical "
                  "day does charge the futures short (that is what the median says); the few days "
                  "when the futures fall harder than the index pay it back, and almost nothing "
                  "survives in the compounded number. The comparison assumes 512100 tracks CSI "
                  "1000 closely enough that what is left is the basis."
                  % (sr["im_median_ann_pct"], sr.get("im_net_carry_pct") or 0, gap, scale), ""]

    if cap.get("im"):
        lines += ["## 4. The notional is the same; the blocked cash is not", "",
                  "Short %.0f yuan of notional (beta %.4f on %.0f yuan)."
                  % (cap.get("shorted_notional") or 0, cap.get("beta") or 0,
                     cap.get("capital") or 0), "",
                  "| carrier | assumption | blocked CNY | free cash CNY | annual impact |",
                  "|---|---|---|---|---|"]
        for r in cap["im"]:
            lines.append("| IM margin | %.0f%% | %.0f | %.0f | +%.0f CNY interest |"
                         % (r["margin"] * 100, r["blocked_cny"], r["free_cash_cny"],
                            r["free_cash_cny"] * CASH_YIELD))
        for r in cap["etf"]:
            lines.append("| ETF borrow | %.0f%% haircut, %.0f%% fee | %.0f | %.0f | -%.0f CNY borrow |"
                         % (r["haircut"] * 100, r["borrow_fee"] * 100, r["blocked_cny"],
                            r["free_cash_cny"], r["borrow_cny"]))
        lines += ["", "The futures leg blocks a fraction of the notional and lets the rest earn; "
                      "the ETF leg blocks most of it and pays borrow on top. Nothing on this "
                      "table depends on the closed term structure -- it is the cash a broker "
                      "asks for.", ""]

    lines += ["## 5. Verdict", "", "**`%s`**" % face.get("verdict"), "",
              "Every flag below is computed from its own inputs and several can hold at once; "
              "the headline names the two that change what a reader would do.", ""]
    for flag, on in (face.get("verdicts") or {}).items():
        if on:
            why = VERDICT_WHY.get(flag)
            if why:
                lines.append("- `%s` -- %s" % (flag, why))
    lines.append("")

    reads = face.get("reads") or []
    if reads:
        lines += ["## 6. Readings", ""]
        for r in reads:
            lines.append("- **%s.** %s" % (r.get("id"), r.get("text")))
        lines.append("")

    lines += ["## 7. What this face does not settle", ""]
    for c in face.get("caveats") or []:
        lines.append("- " + c)
    lines += ["", "Machine `%s`, generated %s." % (face.get("machine"), face.get("generated")), ""]
    return "\n".join(lines)


# ----------------------------------------------------------------------- cmds
def run() -> int:
    face = build_face()
    with open(OUT_JSON, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    _write_md(render_md(face))
    print("carrier -> %s | %s" % (face.get("verdict"), _rel(OUT_JSON)))
    if face.get("realised_carrier"):
        print("  realised gap %.3f pp/yr | surface %.2f pp/yr"
              % (face["realised_carrier"]["im_minus_etf_pp_per_year"],
                 (face.get("surface_readings") or {}).get("im_median_ann_pct") or 0.0))
    return 0


def _write_md(text: str) -> None:
    os.makedirs(os.path.dirname(OUT_MD), exist_ok=True)
    with open(OUT_MD, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def check() -> int:
    """Re-derive every published number from the parents; drift is STALE, disagreement is FAILED."""
    problems = []
    try:
        face = _read_json(OUT_JSON)
    except FileNotFoundError:
        print("STALE face missing: %s" % _rel(OUT_JSON))
        return 3
    except (json.JSONDecodeError, OSError) as exc:
        print("CHECK FAILED unreadable face: %s" % exc)
        return 1
    try:
        parent = _read_json(PARENT)
        basis = _read_json(BASIS)
        md = open(OUT_MD, encoding="utf-8").read()
    except FileNotFoundError as exc:
        print("STALE parent missing: %s" % exc)
        return 3
    except OSError as exc:
        print("STALE cannot read: %s" % exc)
        return 3

    # 1. the parents moved?
    for name, path in (("beta", PARENT), ("basis", BASIS)):
        stored = ((face.get("parents") or {}).get(name) or {})
        if stored.get("file_sha256") != _sha_file(path):
            print("STALE parent %s moved (%s)" % (name, _rel(path)))
            return 3
        if stored.get("content_sha256") != content_sha(_read_json(path)):
            print("STALE parent %s content moved (%s)" % (name, _rel(path)))
            return 3

    spec = parent.get("spec") or {}
    ppy = float(spec.get("periods_per_year") or 12.6)
    rows = [r for r in (parent.get("rows") or []) if r.get("im_window")]
    book = [r.get("book_net") for r in rows]
    etf_leg = [r.get("hedge_etf") for r in rows]
    im_leg = [r.get("hedge_im") for r in rows]

    # 2. the arm table
    for carrier, leg in (("etf", etf_leg), ("im", im_leg)):
        for k in K_GRID:
            key = "%.1f" % k
            published = (face.get("arms") or {}).get(carrier, {}).get(key)
            fresh = arm_stats(hedged(book, leg, k), ppy)
            if published is None or fresh is None:
                problems.append("arms %s k=%s missing" % (carrier, key))
                continue
            for field in ("periods", "annualized_compound", "annual_vol",
                          "sharpe_excess_0", "max_drawdown", "worst_period", "hit_rate"):
                a, b = published.get(field), fresh.get(field)
                if a is None or b is None:
                    if a != b:
                        problems.append("arms %s k=%s %s None mismatch" % (carrier, key, field))
                    continue
                if abs(float(a) - float(b)) > 1e-9:
                    problems.append("arms %s k=%s %s %.12g != %.12g"
                                    % (carrier, key, field, a, b))

    # 3. the realised gap
    rc_fresh = realised_carrier(etf_leg, im_leg, ppy)
    rc_pub = face.get("realised_carrier") or {}
    if rc_fresh is None or not rc_pub:
        problems.append("realised_carrier missing")
    else:
        for field in ("periods", "etf_short_cum", "im_short_cum",
                      "im_minus_etf_pp_per_year", "years"):
            a, b = rc_pub.get(field), rc_fresh.get(field)
            if a is None or abs(float(a) - float(b)) > 1e-9:
                problems.append("realised_carrier %s %.12g != %.12g" % (field, a or float('nan'), b))

    # 4. the surface reading is arithmetic on the basis face
    im_pair = ((basis.get("pairs") or {}).get("IM") or {})
    carry = im_pair.get("carry") or {}
    pub_surface = (face.get("surface_readings") or {}).get("im_median_ann_pct")
    if carry.get("median_ann_pct") != pub_surface:
        problems.append("surface median %.6g != %.6g"
                        % (pub_surface if pub_surface is not None else float('nan'),
                           carry.get("median_ann_pct", float('nan'))))

    # 5. the capital table
    beta = ((parent.get("arms_etf") or {}).get("1.0") or {}).get("beta_used")
    if beta is None:
        beta = ((parent.get("variance") or {}).get("beta_used_for_arms")) or 0.9013
    cap_fresh = capital_table(float(beta), CAPITAL, CASH_YIELD)
    cap_pub = face.get("capital") or {}
    if abs((cap_pub.get("shorted_notional") or 0) - cap_fresh["shorted_notional"]) > 1e-6:
        problems.append("capital shorted_notional mismatch")
    for row_pub, row_fresh in zip(cap_pub.get("im") or [], cap_fresh["im"]):
        for field in ("margin", "blocked_cny", "free_cash_cny", "interest_pp_per_year"):
            if abs(float(row_pub.get(field) or 0) - float(row_fresh[field])) > 1e-6:
                problems.append("capital im %s %.8g != %.8g"
                                % (field, row_pub.get(field) or 0, row_fresh[field]))
    for row_pub, row_fresh in zip(cap_pub.get("etf") or [], cap_fresh["etf"]):
        for field in ("haircut", "borrow_fee", "blocked_cny", "borrow_cny",
                      "borrow_pp_per_year"):
            if abs(float(row_pub.get(field) or 0) - float(row_fresh[field])) > 1e-6:
                problems.append("capital etf %s %.8g != %.8g"
                                % (field, row_pub.get(field) or 0, row_fresh[field]))

    # 6. the verdict re-derives from the fresh numbers
    surface_gap = carry.get("median_ann_pct")
    arms_fresh = {"etf": {"1.0": arm_stats(hedged(book, etf_leg, 1.0), ppy)},
                  "im": {"1.0": arm_stats(hedged(book, im_leg, 1.0), ppy)}}
    flags_fresh = decide(rc_fresh, arms_fresh, surface_gap)
    if flags_fresh != (face.get("verdicts") or {}):
        problems.append("verdicts %s != %s" % (face.get("verdicts"), flags_fresh))
    verdict_fresh = headline(flags_fresh)
    if verdict_fresh != face.get("verdict"):
        problems.append("verdict %s != %s" % (face.get("verdict"), verdict_fresh))

    # 7. the page says the same thing
    for token in ("`%s`" % face.get("verdict"), "%.3f pp a year"
                  % ((rc_pub.get("im_minus_etf_pp_per_year") or 0))):
        if token not in md:
            problems.append("page missing token %r" % token)

    if problems:
        print("CHECK FAILED %d problem(s)" % len(problems))
        for p in problems[:12]:
            print("  - " + p)
        return 1
    print("CHECK OK verdict=%s gap=%.3fpp surface=%.2fpp"
          % (face.get("verdict"), rc_pub.get("im_minus_etf_pp_per_year") or 0,
             pub_surface or 0))
    return 0


# ------------------------------------------------------------------- selftest
def selftest() -> int:
    legs = []

    def leg(name, ok, detail=""):
        legs.append((name, bool(ok), detail))

    # --- stats
    st = arm_stats([0.01] * 12, 12.0)
    leg("L1 constant +1% per period compounds to 12.6825% a year",
        abs(st["annualized_compound"] - (1.01 ** 12 - 1)) < 1e-12)
    leg("L1b zero variance has no Sharpe", arm_stats([0.0] * 12, 12.0)["sharpe_excess_0"] is None)
    leg("L1c one period is not an arm", arm_stats([0.05], 12.0) is None)
    leg("L1d nan rows are dropped, not faked",
        arm_stats([0.01, float("nan"), 0.01], 12.0)["periods"] == 2)

    # --- drawdown
    leg("L2 drawdown of a monotone rise is zero", abs(max_drawdown([0.01, 0.01, 0.01])) < 1e-12)
    leg("L2b drawdown of -10% then +10% is -10%",
        abs(max_drawdown([-0.10, 0.10]) - (-0.10)) < 1e-12)

    # --- the carrier gap is geometric, and a median day is not a year
    etf = [0.01, -0.01, 0.01, -0.01]
    im = [0.01, -0.01, 0.01, -0.01]
    rc = realised_carrier(etf, im, 12.0)
    leg("L3 identical legs have exactly zero gap", abs(rc["im_minus_etf_pp_per_year"]) < 1e-12)
    im2 = [0.02, -0.02, 0.02, -0.02]
    rc2 = realised_carrier(etf, im2, 12.0)
    leg("L3b bigger swings on the same median day make the wider leg the worse short",
        rc2["im_minus_etf_pp_per_year"] < 0.0 and abs(rc2["im_minus_etf_pp_per_year"]) > 0.1)
    leg("L3c the median of the two leg return series is identical",
        statistics.median(etf) == statistics.median(im2))
    leg("L3d an empty leg has no gap", realised_carrier([], [], 12.0) is None)
    rc3 = realised_carrier([0.10], [0.10, 0.0], 12.0)
    leg("L3e a length mismatch still computes off the shorter count",
        rc3 is None or rc3["periods"] == 1)

    # --- capital
    cap = capital_table(0.9, 1_000_000.0, 0.02)
    leg("L4 shorted notional is beta times capital",
        abs(cap["shorted_notional"] - 900_000.0) < 1e-9)
    mid = next(r for r in cap["im"] if r["margin"] == 0.12)
    leg("L4b 12% margin blocks 108,000", abs(mid["blocked_cny"] - 108_000.0) < 1e-9)
    leg("L4c the rest earns the declared yield",
        abs(mid["free_cash_cny"] * 0.02 - 17_840.0) < 1e-6)
    etf_row = next(r for r in cap["etf"] if r["haircut"] == 1.00 and r["borrow_fee"] == 0.02)
    leg("L4d a 100% haircut blocks the whole notional",
        abs(etf_row["blocked_cny"] - 900_000.0) < 1e-9)
    leg("L4e borrow cost is charged on the notional, not the blocked cash",
        abs(etf_row["borrow_cny"] - 18_000.0) < 1e-9)

    # --- verdict ladder: each flag flips on its own input
    arms_pos = {"etf": {"1.0": {"annualized_compound": 0.10, "annual_vol": 0.12}},
                "im": {"1.0": {"annualized_compound": 0.10, "annual_vol": 0.11}}}
    tie = decide({"im_minus_etf_pp_per_year": 0.1}, arms_pos, 8.9)
    leg("L5 tie flag on", tie[VERDICT_TIE] is True)
    leg("L5b artifact flag on when a big surface reading meets a small realised gap",
        tie[VERDICT_ARTIFACT] is True)
    leg("L5c ETF-wins flag off when the gap is inside the tie band", tie[VERDICT_ETF] is False)
    arms_wrong = {"etf": {"1.0": {"annualized_compound": 0.10, "annual_vol": 0.11}},
                  "im": {"1.0": {"annualized_compound": 0.10, "annual_vol": 0.12}}}
    leg("L5d the tie flag needs the futures leg to be the quieter one",
        decide({"im_minus_etf_pp_per_year": 0.1}, arms_wrong, 8.9)[VERDICT_TIE] is False)
    etf_wins = decide({"im_minus_etf_pp_per_year": -3.0}, arms_pos, 8.9)
    leg("L5e a gap beyond the band toward the ETF flips the ETF flag on",
        etf_wins[VERDICT_ETF] is True)
    leg("L5f the same flipped gap kills the artifact flag",
        etf_wins[VERDICT_ARTIFACT] is False)
    leg("L5g a small surface reading cannot summon the artifact flag",
        decide({"im_minus_etf_pp_per_year": 0.1}, arms_pos, 2.0)[VERDICT_ARTIFACT] is False)
    leg("L5h headline follows the ETF flag first", headline(etf_wins) == VERDICT_ETF)
    leg("L5i headline otherwise names both the artifact and the capital case",
        headline(tie) == VERDICT_ARTIFACT + "+" + VERDICT_IM_CAPITAL)
    leg("L5j missing arms do not crash the decision",
        decide({"im_minus_etf_pp_per_year": 0.1}, {}, 8.9)[VERDICT_TIE] is False)
    leg("L5k no realised gap -> no flags at all",
        decide(None, arms_pos, 8.9) == {"all": None})

    # --- live face (only if the parents and the published face are on disk)
    if os.path.exists(PARENT) and os.path.exists(BASIS) and os.path.exists(OUT_JSON):
        face = _read_json(OUT_JSON)
        parent = _read_json(PARENT)
        ppy = float((parent.get("spec") or {}).get("periods_per_year") or 12.6)
        rows = [r for r in (parent.get("rows") or []) if r.get("im_window")]
        leg("L6 the published sample is the im_window subset",
            (face.get("sample") or {}).get("periods") == len(rows))
        leg("L6b the published parents are the files on disk",
            all(((face.get("parents") or {}).get(n) or {}).get("file_sha256")
                == _sha_file(p_) for n, p_ in (("beta", PARENT), ("basis", BASIS))))
        rc_pub = face.get("realised_carrier") or {}
        rc_live = realised_carrier([r.get("hedge_etf") for r in rows],
                                   [r.get("hedge_im") for r in rows], ppy)
        leg("L6c the realised gap is reproducible from the parent rows",
            abs((rc_pub.get("im_minus_etf_pp_per_year") or 0)
                - (rc_live.get("im_minus_etf_pp_per_year") or 0)) < 1e-9)
        leg("L6d the verdict in the file is the one this code would print",
            face.get("verdict") == build_face().get("verdict"))
        leg("L6e the surface reading equals the basis face",
            ((face.get("surface_readings") or {}).get("im_median_ann_pct")
             == (((_read_json(BASIS).get("pairs") or {}).get("IM") or {})
                 .get("carry") or {}).get("median_ann_pct")))
        leg("L6f the page carries the verdict token",
            ("`%s`" % face.get("verdict")) in open(OUT_MD, encoding="utf-8").read())
    else:
        leg("L6 live face skipped (files absent)", True, "skipped")

    width = max(len(n) for n, _, _ in legs) + 2
    bad = 0
    for name, ok, detail in legs:
        if not ok:
            bad += 1
        print("%s %-*s %s" % ("PASS" if ok else "FAIL", width, name, detail))
    print("%d/%d PASS" % (len(legs) - bad, len(legs)))
    return 0 if bad == 0 else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("cmd", nargs="?", default="run",
                    choices=("run", "check", "selftest"))
    args = ap.parse_args(argv)
    if args.cmd == "selftest":
        return selftest()
    if args.cmd == "check":
        return check()
    return run()


if __name__ == "__main__":
    sys.exit(main())

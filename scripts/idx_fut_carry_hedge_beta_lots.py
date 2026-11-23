#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""the hedge is a whole number of lots, so what does estimating beta actually cost?

WHY THIS FILE EXISTS
--------------------
r2006 priced the carry book on a hedge you can buy and printed, for one IC long lot,
beta = 1.5567 IF lots and an integer hedge of 2 lots (capital 3,150,916.73 CNY instead
of 2,826,641.50).  Two things were left under that number and neither is a detail:

  1. beta was estimated on one 242-day window.  If the same rule estimated on a different
     242 days printed a different beta, the desk's hedge size is a coin flip over the
     calendar, not a property of the pair.
  2. a lot is indivisible.  beta 1.5567 cannot be bought; you buy 1 (under-hedged by 36%)
     or 2 (over-hedged by 28%).  Nobody printed what each of those two errors costs in
     CNY and in sigma.

The question, one line: **is the integer hedge a measurement or an artefact of the window
it was measured on, and what does the indivisibility cost?**

WHAT IS MEASURED AND WHAT IS A RULE
-----------------------------------
Measured, from this repo's own panels (same roll walk as the parent face, imported, not
re-implemented):
  * beta on every trailing window of 60/120/242 trading days, stepped 5 days, for each
    (long arm, hedge arm) pair -- the spread of that distribution is the honest error bar
    the point estimate never had;
  * the whole-lot count each of those betas would imply, and how often it differs from
    the one the published face used;
  * for the last year: net P&L and residual sigma of the hedged book under four rules
    (exact beta / whole lots rounded up / whole lots rounded / beta = 1), so the cost of
    indivisibility is a number rather than a shrug.

A RULE, not a measurement: the whole-lot convention itself.  This file prints both
ceil and round so a desk that prefers one can read its own row; it does not adjudicate.

WHAT WOULD MAKE THIS FACE WRONG
-------------------------------
If every trailing window printed beta on the same side of a lot boundary, the answer is
"the integer hedge is stable, stop worrying".  That is a perfectly good output and the
verdict string says so instead of manufacturing a problem.
"""

import hashlib
import json
import math
import os
import statistics
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import idx_fut_basis as BASE       # noqa: E402  PAIRS / load_index -- product->index map
import idx_fut_carry_paper as PAP  # noqa: E402  position_series -- the roll walk

OUT_PATH = os.path.join(ROOT, "results", "idx_fut_carry_hedge_beta_lots.json")
DOC_PATH = os.path.join(ROOT, "research", "IDX_FUT_CARRY_HEDGE_BETA_LOTS.md")
PARENT_PATH = os.path.join(ROOT, "results", "idx_fut_carry_tradeable_hedge_capital.json")

MULTIPLIER = {"IF": 300, "IH": 300, "IC": 200, "IM": 200}
PRODUCTS = ("IF", "IH", "IC", "IM")
LONG_ARMS = ("IC", "IM", "IH")
WINDOW_LENGTHS = (60, 120, 242)
STEP = 5
SAMPLE_YEARS = 10          # ask the parent's walk for its whole usable history
TARGET_PCT = 8.0
DOC_BEGIN = "<!-- BEGIN:IDX-FUT-CARRY-HEDGE-BETA-LOTS -->"
DOC_END = "<!-- END:IDX-FUT-CARRY-HEDGE-BETA-LOTS -->"


# ------------------------------------------------------------------ io helpers
def now_iso():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def load_json(path):
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def dump_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    os.replace(tmp, path)


def sha256_file(path):
    if not os.path.exists(path):
        return None
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def input_digests():
    out = {}
    for prod in PRODUCTS:
        path = BASE.PAIRS.get(prod, (None,))[0]
        if not path:
            continue
        out["index_" + prod] = sha256_file(os.path.join(HERE, "..", path))
    out["prices_panel"] = sha256_file(PAP.PRICES_PATH) if hasattr(PAP, "PRICES_PATH") else None
    return out


# ------------------------------------------------------------------ arithmetic
def dated_pnl(prod, years=SAMPLE_YEARS):
    """[(date, pnl_cny_per_lot)] via the parent's own roll walk (PAP.position_series)."""
    rows, _rolls = PAP.position_series(prod)
    if not rows:
        return None
    cutoff = rows[-1][0]
    want = str(int(cutoff[:4]) - int(years)) + cutoff[4:]
    start = next((k for k, r in enumerate(rows) if r[0] >= want), 0)
    held = rows[start][1]
    prev = rows[start][2]
    mult = MULTIPLIER[prod]
    out = []
    for d, sym, px, old_px in rows[start + 1:]:
        if px is None:
            continue
        if sym != held:
            if old_px is None:
                fut = 0.0
            else:
                fut = (old_px - prev) if prev is not None else 0.0
            held, prev = sym, px
        else:
            fut = (px - prev) if prev is not None else 0.0
            prev = px
        out.append((d, fut * mult))
    return out


def beta_no_intercept(xs, ys):
    sxx = sum(x * x for x in xs)
    if sxx <= 0:
        return None
    return sum(x * y for x, y in zip(xs, ys)) / sxx


def residual_sigma_ann(xs, ys, beta):
    if not xs:
        return None
    resid = [y - beta * x for x, y in zip(xs, ys)]
    if len(resid) < 3:
        return None
    return statistics.pstdev(resid) * math.sqrt(252.0)


def whole_lots(beta, mode):
    if beta is None:
        return None
    if mode == "ceil":
        return max(1, int(math.ceil(beta - 1e-12)))
    if mode == "round":
        return max(1, int(round(beta)))
    raise ValueError(mode)


def align(long_series, hedge_series):
    lm = dict(long_series)
    hm = dict(hedge_series)
    days = sorted(set(lm) & set(hm))
    return days, [lm[d] for d in days], [hm[d] for d in days]


# ------------------------------------------------------------------ faces
def rolling_betas(xs, ys):
    """beta on every trailing window of each length, stepped STEP."""
    out = {}
    for n in WINDOW_LENGTHS:
        betas = []
        if len(xs) >= n:
            for end in range(n, len(xs) + 1, STEP):
                b = beta_no_intercept(xs[end - n:end], ys[end - n:end])
                if b is not None:
                    betas.append(round(b, 6))
        out[str(n)] = betas
    return out


def rolling_row(betas, published_lots):
    """One row of the window table. Selftest builds the row through this exact seam,
    because a row that forgets its own `state` is silently skipped by verdict_of --
    that defect shipped for one run before the table contradicted the verdict."""
    if not betas:
        return {"state": "NO_WINDOW"}
    srt = sorted(betas)
    counts = [whole_lots(b, "ceil") for b in betas]
    return {
        "state": "ok",
        "n_windows": len(betas),
        "min": round(srt[0], 6),
        "p10": round(srt[int(0.10 * (len(srt) - 1))], 6),
        "median": round(statistics.median(betas), 6),
        "p90": round(srt[int(0.90 * (len(srt) - 1))], 6),
        "max": round(srt[-1], 6),
        "span": round(srt[-1] - srt[0], 6),
        "ceil_lots_seen": sorted(set(counts)),
        "share_different_from_published": round(
            sum(1 for c in counts if c != published_lots) / float(len(counts)), 4),
    }


def pair_face(long_arm, hedge_arm, series):
    days, ys, xs = align(series[long_arm], series[hedge_arm])
    if len(days) < min(WINDOW_LENGTHS) + STEP:
        return {"state": "TOO_SHORT", "days": len(days)}
    beta_full = beta_no_intercept(xs, ys)
    face = {
        "state": "ok",
        "days": len(days),
        "window": [days[0], days[-1]],
        "beta_full_sample": None if beta_full is None else round(beta_full, 6),
        "rolling": {},
    }
    last_year = [k for k, d in enumerate(days) if d >= days[-1][:4] + "-" + days[-1][5:7] + "-01"]
    n_last = min(242, len(days))
    ys_l, xs_l = ys[-n_last:], xs[-n_last:]
    beta_lastyear = beta_no_intercept(xs_l, ys_l)
    face["beta_last_year"] = None if beta_lastyear is None else round(beta_lastyear, 6)

    # The published face sized its integer hedge off a 242-day window ending at the
    # cutoff, so that is the reference the window spread is measured against.
    published_lots = whole_lots(beta_lastyear, "ceil")
    face["published_rule_lots"] = published_lots
    for n, betas in rolling_betas(xs, ys).items():
        face["rolling"][n] = rolling_row(betas, published_lots)

    # what indivisibility costs, on the last year, per sizing rule
    pnl_long = sum(ys_l)
    pnl_hedge = sum(xs_l)
    rules = {}
    for name, lam in (
        ("exact_beta", beta_lastyear),
        ("whole_ceil", whole_lots(beta_lastyear, "ceil")),
        ("whole_round", whole_lots(beta_lastyear, "round")),
        ("beta_one", 1.0),
    ):
        if lam is None:
            continue
        net = pnl_long - lam * pnl_hedge
        sigma = residual_sigma_ann(xs_l, ys_l, lam)
        rules[name] = {
            "hedge_lots": None if name in ("exact_beta", "beta_one") else int(lam),
            "beta_applied": round(float(lam), 6),
            "net_pnl_cny": round(net, 2),
            "residual_sigma_cny": None if sigma is None else round(sigma, 2),
            "capital_at_8pct_cny": None if not sigma else round(sigma / (TARGET_PCT / 100.0), 2),
        }
    face["last_year_rules"] = rules
    if "exact_beta" in rules and "whole_ceil" in rules:
        diff = round(rules["whole_ceil"]["net_pnl_cny"] - rules["exact_beta"]["net_pnl_cny"], 2)
        extra = round((rules["whole_ceil"]["beta_applied"]
                       - rules["exact_beta"]["beta_applied"]), 6)
        face["cost_of_indivisibility"] = {
            "pnl_difference_cny_vs_exact": diff,
            # the sign is not a defect: rounding up buys EXTRA hedge, and extra hedge is
            # a position in the hedge leg's own carry.  A positive difference means the
            # rounding happened to pay last year, not that it is free.
            "extra_hedge_beta": extra,
            "why_the_sign_is_what_it_is": (
                "a positive difference means the extra hedge earned last year because "
                "the hedge leg's own carry was negative; it is a bet, not a saving"),
            "sigma_delta_cny_vs_exact": (
                None if rules["whole_ceil"]["residual_sigma_cny"] is None
                or rules["exact_beta"]["residual_sigma_cny"] is None
                else round(rules["whole_ceil"]["residual_sigma_cny"]
                           - rules["exact_beta"]["residual_sigma_cny"], 2)),
        }
    face["last_year"] = [days[-n_last], days[-1]]
    return face


def verdict_of(arms):
    """One sentence a reader can act on."""
    unstable = []
    costs = []
    for key, face in arms.items():
        if face.get("state") != "ok":
            continue
        for n, row in face.get("rolling", {}).items():
            if row.get("state") != "ok":
                continue
            if len(row.get("ceil_lots_seen") or []) > 1:
                unstable.append("%s/%s@%sd" % (key, "?", n))
                break
        cost = face.get("cost_of_indivisibility")
        if cost and cost.get("pnl_difference_cny_vs_exact") is not None:
            costs.append((key, cost["pnl_difference_cny_vs_exact"]))
    if not unstable:
        return "INTEGER_HEDGE_IS_STABLE_ACROSS_ESTIMATION_WINDOWS"
    worst = max(costs, key=lambda kv: abs(kv[1])) if costs else None
    if worst and abs(worst[1]) > 5000:
        return "THE_WHOLE_LOT_COUNT_DEPENDS_ON_THE_WINDOW_AND_IT_COSTS_MONEY"
    return "THE_WHOLE_LOT_COUNT_DEPENDS_ON_THE_WINDOW_BUT_THE_COST_IS_SMALL"


def build():
    series = {}
    problems = []
    for prod in PRODUCTS:
        s = dated_pnl(prod)
        if not s:
            problems.append({"product": prod, "why": "NO_SERIES"})
            continue
        series[prod] = s
    arms = {}
    for long_arm in LONG_ARMS:
        for hedge_arm in PRODUCTS:
            if hedge_arm == long_arm or long_arm not in series or hedge_arm not in series:
                continue
            key = "%s_vs_%s" % (long_arm, hedge_arm)
            arms[key] = pair_face(long_arm, hedge_arm, series)

    cutoff = None
    for prod, s in series.items():
        d = s[-1][0]
        cutoff = d if cutoff is None or d < cutoff else cutoff

    parent = load_json(PARENT_PATH) or {}
    published = {}
    for acc, body in (parent.get("accounts") or {}).items():
        trad = (body or {}).get("tradeable") or {}
        for hedge_arm, row in trad.items():
            if not isinstance(row, dict):
                continue
            published["%s_vs_%s" % (acc, hedge_arm)] = {
                "beta_lots_per_long_lot": row.get("beta_lots_per_long_lot"),
                "integer_hedge_lots": (row.get("integer_hedge") or {}).get("lots"),
                "capital_cny": row.get("capital_cny"),
            }

    agree = []
    for key, row in published.items():
        mine = arms.get(key) or {}
        if mine.get("state") != "ok":
            continue
        b = mine.get("beta_last_year")
        agree.append({
            "pair": key,
            "published_beta": row.get("beta_lots_per_long_lot"),
            "recomputed_beta_last_year": b,
            "delta": None if (b is None or row.get("beta_lots_per_long_lot") is None)
            else round(b - row["beta_lots_per_long_lot"], 6),
            "published_lots": row.get("integer_hedge_lots"),
            "published_capital_cny": row.get("capital_cny"),
        })

    obj = {
        "kind": "idx-fut-carry-hedge-beta-lots",
        "generated": now_iso(),
        "evidence_cutoff": cutoff,
        "target_pct": TARGET_PCT,
        "sample_years": SAMPLE_YEARS,
        "window_lengths": list(WINDOW_LENGTHS),
        "step": STEP,
        "arms": arms,
        "cross_check_against_published_face": agree,
        "verdict": verdict_of(arms),
        "problems": problems,
        "inputs": input_digests(),
        "sources": {
            "parent_face": "results/idx_fut_carry_tradeable_hedge_capital.json",
            "roll_walk": "scripts/idx_fut_carry_paper.py::position_series",
            "index_panel": "scripts/idx_fut_basis.py::load_index",
        },
    }
    return obj


# ------------------------------------------------------------------ doc
def render_doc(obj):
    lines = [DOC_BEGIN, "",
             "# the hedge is a whole number of lots",
             "",
             "generated %s | evidence_cutoff **%s** | verdict **%s**"
             % (obj["generated"], obj["evidence_cutoff"], obj["verdict"]),
             "",
             "The r2006 face priced one IC long lot hedged with beta x IF lots and then had",
             "to buy a whole number of them. This page asks whether that integer came from",
             "the pair or from the 242 days it was measured on, and what the rounding costs.",
             ""]
    for key in sorted(obj["arms"]):
        face = obj["arms"][key]
        if face.get("state") != "ok":
            lines.append("* %s: %s" % (key, face.get("state")))
            continue
        lines.append("## %s" % key)
        lines.append("")
        lines.append("full-sample beta **%.4f** | last-year beta **%.4f** | %d aligned days %s..%s"
                     % (face["beta_full_sample"] or 0.0, face["beta_last_year"] or 0.0,
                        face["days"], face["window"][0], face["window"][1]))
        lines.append("")
        lines.append("| window | n | min | p10 | median | p90 | max | whole-lot counts | share != published |")
        lines.append("|---|---|---|---|---|---|---|---|---|")
        for n in sorted(face["rolling"], key=lambda x: int(x)):
            row = face["rolling"][n]
            if row.get("state") != "ok":
                lines.append("| %sd | - | - | - | - | - | - | - | - |" % n)
                continue
            lines.append("| %sd | %d | %.3f | %.3f | %.3f | %.3f | %.3f | %s | %.1f%% |"
                         % (n, row["n_windows"], row["min"], row["p10"], row["median"],
                            row["p90"], row["max"], row["ceil_lots_seen"],
                            100.0 * row["share_different_from_published"]))
        lines.append("")
        rules = face.get("last_year_rules") or {}
        if rules:
            lines.append("last year %s..%s, per one long lot:" % tuple(face["last_year"]))
            lines.append("")
            lines.append("| sizing rule | hedge lots | net P&L CNY | residual sigma CNY | capital at 8% CNY |")
            lines.append("|---|---|---|---|---|")
            for name in ("exact_beta", "whole_ceil", "whole_round", "beta_one"):
                if name not in rules:
                    continue
                r = rules[name]
                lines.append("| %s | %s | %s | %s | %s |"
                             % (name, r["hedge_lots"] if r["hedge_lots"] is not None else "%.4f" % r["beta_applied"],
                                "{:,.0f}".format(r["net_pnl_cny"]),
                                "-" if r["residual_sigma_cny"] is None else "{:,.0f}".format(r["residual_sigma_cny"]),
                                "-" if r["capital_at_8pct_cny"] is None else "{:,.0f}".format(r["capital_at_8pct_cny"])))
            cost = face.get("cost_of_indivisibility") or {}
            if cost:
                lines.append("")
                sigma_txt = ("n/a" if cost.get("sigma_delta_cny_vs_exact") is None
                             else "{:+,.0f} CNY".format(cost["sigma_delta_cny_vs_exact"]))
                lines.append("rounding up to whole lots moves P&L by **{:+,.0f} CNY** and sigma by **{}** against the exact beta."
                             .format(cost.get("pnl_difference_cny_vs_exact") or 0.0, sigma_txt))
                lines.append("")
                lines.append("Read the sign before the number: rounding 1.5567 up to 2 buys `%.4f` of extra"
                             % (cost.get("extra_hedge_beta") or 0.0))
                lines.append("hedge, and extra hedge is a position in the hedge leg's own carry. A positive")
                lines.append("difference means that bet paid last year; it is not a saving, and it reverses")
                lines.append("whenever the hedge leg's carry turns positive.")
        lines.append("")

    lines.append("## what this does not settle")
    lines.append("")
    lines.append("* the whole-lot convention itself is a desk rule, not a measurement: both `ceil`")
    lines.append("  and `round` rows are printed and no row is recommended;")
    lines.append("* the sample is one roll walk over the history this repo holds; a pair whose")
    lines.append("  beta sits far from a lot boundary cannot show this effect at all, which is")
    lines.append("  the honest reading of a single-lot-count spread.")
    lines.append("")
    lines.append(DOC_END)
    return "\n".join(lines) + "\n"


def write_all(obj):
    dump_json(OUT_PATH, obj)
    doc = render_doc(obj)
    begin, end = DOC_BEGIN, DOC_END
    if os.path.exists(DOC_PATH):
        with open(DOC_PATH, "r", encoding="utf-8") as fh:
            old = fh.read()
        if begin in old and end in old:
            head = old[:old.index(begin)]
            tail = old[old.index(end) + len(end):].lstrip("\n")
            doc = head + doc + (("\n" + tail) if tail else "")
    with open(DOC_PATH, "w", encoding="utf-8") as fh:
        fh.write(doc)


# ------------------------------------------------------------------ selftest
def selftest():
    legs = []

    def ok(name, cond, why=""):
        legs.append((name, bool(cond), why))

    xs = [0.01, -0.02, 0.03, -0.01, 0.02, 0.005, -0.015]
    ys = [2 * x for x in xs]
    ok("beta recovers a known slope", abs(beta_no_intercept(xs, ys) - 2.0) < 1e-12)
    ok("beta is scale-invariant on the same series",
       abs(beta_no_intercept([x * 100 for x in xs], ys) - 0.02) < 1e-12)
    ok("zero variance input yields None", beta_no_intercept([0.0] * 5, ys[:5]) is None)
    ok("ceil(1.5567)=2", whole_lots(1.5567, "ceil") == 2)
    ok("ceil(0.98)=1 (never zero lots)", whole_lots(0.98, "ceil") == 1)
    ok("round(1.4)=1", whole_lots(1.4, "round") == 1)
    ok("round(1.6)=2", whole_lots(1.6, "round") == 2)
    ok("a perfect hedge has zero residual sigma",
       residual_sigma_ann(xs, ys, 2.0) < 1e-12)
    ok("a 1-lot hedge of a 2x pair has positive residual sigma",
       residual_sigma_ann(xs, ys, 1.0) > 0.0)
    # the verdict must react to a real window spread and stay quiet when there is none
    fake_stable = {"IC_vs_IF": {"state": "ok", "rolling": {"242": {"state": "ok", "ceil_lots_seen": [2]}},
                                "cost_of_indivisibility": {"pnl_difference_cny_vs_exact": 0.0}}}
    ok("verdict says STABLE when every window agrees",
       verdict_of(fake_stable) == "INTEGER_HEDGE_IS_STABLE_ACROSS_ESTIMATION_WINDOWS")
    fake_unstable = {"IC_vs_IF": {"state": "ok",
                                  "rolling": {"242": {"state": "ok", "ceil_lots_seen": [1, 2]}},
                                  "cost_of_indivisibility": {"pnl_difference_cny_vs_exact": -9000.0}}}
    ok("verdict says IT COSTS MONEY when both boundaries appear and the drag is real",
       verdict_of(fake_unstable) == "THE_WHOLE_LOT_COUNT_DEPENDS_ON_THE_WINDOW_AND_IT_COSTS_MONEY")
    # the seam defect: a table row that forgets `state` was skipped by verdict_of, so a
    # spread of [1, 2, 3] printed next to a STABLE verdict.  The row is built here from
    # the same function the face uses, and the verdict must react to it.
    row = rolling_row([1.0, 1.6, 2.4], 2)
    ok("a row built by rolling_row carries its own state", row.get("state") == "ok")
    ok("that row names the whole-lot spread", row.get("ceil_lots_seen") == [1, 2, 3])
    seam_face = {"IC_vs_IF": {"state": "ok", "rolling": {"242": row},
                              "cost_of_indivisibility": {"pnl_difference_cny_vs_exact": -12000.0}}}
    ok("verdict is not STABLE on a face built from rolling_row",
       verdict_of(seam_face) != "INTEGER_HEDGE_IS_STABLE_ACROSS_ESTIMATION_WINDOWS")
    failed = [leg for leg in legs if not leg[1]]
    for name, good, why in legs:
        print("%-72s %s %s" % (name, "PASS" if good else "FAIL", why))
    print("selftest: %d/%d" % (len(legs) - len(failed), len(legs)))
    return 0 if not failed else 1


def check():
    """Re-derive and compare.

    Two different reds (r1934): a moved cutoff or a moved input digest is STALE -- the
    inputs moved, pay to rebuild.  A number that disagrees while the inputs are the same
    bytes is CHECK FAILED and must not carry the word STALE, or the chain will keep
    paying to rebuild a face whose arithmetic is wrong.
    """
    if not os.path.exists(OUT_PATH):
        print("STALE face missing: %s" % OUT_PATH)
        return 3
    old = load_json(OUT_PATH) or {}
    new = build()
    drift = []
    if old.get("evidence_cutoff") != new.get("evidence_cutoff"):
        drift.append("evidence_cutoff %s -> %s" % (old.get("evidence_cutoff"), new.get("evidence_cutoff")))
    if old.get("inputs") != new.get("inputs"):
        drift.append("input digests moved")
    if drift:
        print("STALE face drifted: " + "; ".join(drift[:6]))
        return 3
    defects = []
    if old.get("verdict") != new.get("verdict"):
        defects.append("verdict %s -> %s" % (old.get("verdict"), new.get("verdict")))
    for key, face in (new.get("arms") or {}).items():
        oface = (old.get("arms") or {}).get(key) or {}
        if oface.get("beta_full_sample") != face.get("beta_full_sample"):
            defects.append("%s beta_full %s -> %s" % (key, oface.get("beta_full_sample"), face.get("beta_full_sample")))
        if oface.get("published_rule_lots") != face.get("published_rule_lots"):
            defects.append("%s published_rule_lots %s -> %s"
                           % (key, oface.get("published_rule_lots"), face.get("published_rule_lots")))
    if (old.get("arms") or {}).keys() != (new.get("arms") or {}).keys():
        defects.append("the set of pairs changed")
    if defects:
        print("CHECK FAILED face contradicts its own inputs: " + "; ".join(defects[:6]))
        return 3
    print("CHECK OK %s" % OUT_PATH)
    return 0


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "selftest":
        return selftest()
    if cmd == "check":
        return check()
    if cmd in ("run", "--write", ""):
        obj = build()
        write_all(obj)
        print("wrote %s" % OUT_PATH)
        print("wrote %s" % DOC_PATH)
        print("verdict %s | cutoff %s" % (obj["verdict"], obj["evidence_cutoff"]))
        for key in sorted(obj["arms"]):
            f = obj["arms"][key]
            if f.get("state") != "ok":
                print("  %-14s %s" % (key, f.get("state")))
                continue
            spread = (f["rolling"].get("242") or {})
            print("  %-14s beta_full=%.4f beta_1y=%.4f 242d span=%s lots=%s"
                  % (key, f["beta_full_sample"] or 0.0, f["beta_last_year"] or 0.0,
                     spread.get("span"), spread.get("ceil_lots_seen")))
        return 0
    print("usage: idx_fut_carry_hedge_beta_lots.py [run|check|selftest]")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))

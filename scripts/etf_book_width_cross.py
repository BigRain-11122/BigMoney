"""Does the width sign survive off the grid that produced it? (r1362 / card E276)

E275 (r1361) read the atlas ordering as a toll ladder and found exactly one sign-stable
direction: a WIDER book earns more (+0.69 -> +1.56pp median CAGR, rank corr +1.000 with the
toll), while the 12-cell ordering itself only clears its own phase noise below 1.045bp/side.
That width sign was measured inside one grid (3/5/8 x 10/20/40 fixed phases) on ONE panel
(the full ETF pool). A sign that only exists there is this family's naming, not a mechanism.

This face re-asks the same question on a panel the atlas never touched: the 17-ETF cross
declared in E198 (plus its 510300 benchmark). Declared before any number is read:

  * PANEL       -- the 18 usable names of the E198 basket; 510880 and 510180 have no local
                   file and are PUBLISHED as missing, never substituted (a panel re-picked
                   after the answer is not a panel).
  * WIDTHS      -- 3/5/8/12 (the atlas stopped at 8; 12 reaches the no-selectivity corner of
                   an 18-name panel, which is where a "wider is better" sign should die first
                   if it is a rank artifact).
  * CADENCE     -- 20 bars, fixed (the production cadence). Only width moves.
  * COSTS       -- 0.0 (the atlas's cost-zero arm, the arm the family sign was read at) and
                   8bp/side (the toll the production card is actually charged).
  * PHASES      -- decision-grid offsets 0/4/8/12/16 bars. One decision sequence is one draw
                   (E188), so every rung is published as a phase range, never a single number.
  * The score is recomputed WITHIN this panel, so it is a different instrument: a top-5 name
    here is not a top-5 name there. That is the point of the test, and also why a "no" here
    cannot unseat the family reading -- it can only show the sign is not portable.

CAGR alone is confounded with volatility: an equal-weight book of fewer names is more
volatile, so in a rising market the narrow book earns more for the same edge. Every rung
therefore prints vol and Sharpe beside CAGR, and the verdict rests on the CAGR sign only
when the paired phase count agrees (declared share floor below).

Verdict rule (frozen; --check re-derives it from the stored summariser output):
  arm replicates  : rank corr(width, median CAGR) >= 0.70 AND
                    share of phases with cagr(widest) > cagr(narrowest) >= 0.60
  arm flips       : rank corr <= -0.70 OR that share <= 0.40
  WIDTH_SIGN_REPLICATES      -- every cost arm replicates
  WIDTH_SIGN_IS_FAMILY_NAMING-- at least one cost arm flips
  WIDTH_SIGN_ARM_DEPENDENT   -- otherwise (reportable, not adoptable)

Usage:
  python scripts/etf_book_width_cross.py run
  python scripts/etf_book_width_cross.py --check
  python scripts/etf_book_width_cross.py --selftest

Outputs: results/etf_book_width_cross.json (+ .md)
Exploratory measurement: no ledger booking, no admission change, no engine run.
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import numpy as np
import pandas as pd

RES = os.path.join(ROOT, "results")
OUT = os.path.join(RES, "etf_book_width_cross.json")
OUT_MD = os.path.join(RES, "etf_book_width_cross.md")
FAMILY_FACE = os.path.join(RES, "etf_book_atlas_toll_ladder.json")

# ---- frozen constants (declared before any number is read; the gate refuses an edit) ----
BASKET = ["510300", "510050", "510500", "512100", "588000", "159915", "159919",
          "512880", "518880", "511010", "159928", "159920", "512170", "512480",
          "515000", "510310", "513100", "159949"]
MISSING_DECLARED = ["510880", "510180"]
WIDTHS = (3, 5, 8, 12)
CADENCE = 20
COSTS = (0.0, 0.0008)
PHASES = (0, 4, 8, 12, 16)
START = "2020-01-01"
RHO_MIN = 0.70
PHASE_SHARE_MIN = 0.60
PHASE_SHARE_FLIP = 0.40
# Random-signal baseline (research/BACKTEST_PLAN.md three iron laws: every batch carries a
# null arm and a trial count). Seeded, so the null is reproducible rather than rhetoric.
NULL_SEEDS = 20
NULL_PHASES = (0, 8)
NULL_COST = 0.0008


# ----------------------------------------------------------------------------- primitives
def _median(a):
    a = [x for x in a if x is not None]
    if not a:
        return None
    a = sorted(a)
    n = len(a)
    return a[n // 2] if n % 2 else 0.5 * (a[n // 2 - 1] + a[n // 2])


def _rank(a):
    """Average ranks (1-based), so a tie does not get an arbitrary order."""
    idx = sorted(range(len(a)), key=lambda i: a[i])
    out = [0.0] * len(a)
    i = 0
    while i < len(idx):
        j = i
        while j + 1 < len(idx) and a[idx[j + 1]] == a[idx[i]]:
            j += 1
        r = 0.5 * (i + j) + 1.0
        for k in range(i, j + 1):
            out[idx[k]] = r
        i = j + 1
    return out


def spearman(x, y):
    if len(x) != len(y) or len(x) < 2:
        return None
    rx, ry = _rank(list(x)), _rank(list(y))
    mx, my = np.mean(rx), np.mean(ry)
    sx = float(np.sqrt(sum((v - mx) ** 2 for v in rx)))
    sy = float(np.sqrt(sum((v - my) ** 2 for v in ry)))
    if sx == 0.0 or sy == 0.0:
        return None
    return float(sum((a - mx) * (b - my) for a, b in zip(rx, ry)) / (sx * sy))


# ------------------------------------------------------------------------------ panel io
def _panel_path(code):
    for cand in (("sh" if code[0] == "5" else "sz") + code + ".csv", code + ".csv"):
        p = os.path.join(ROOT, "data", "daily", cand)
        if os.path.exists(p):
            return p
    return None


def load_panel(codes=BASKET):
    """Load the declared panel only. Nothing outside BASKET is read, so the ranks computed
    downstream live inside this cross-section and nowhere else."""
    prices, missing = {}, []
    for code in codes:
        p = _panel_path(code)
        if p is None:
            missing.append(code)
            continue
        df = pd.read_csv(p, parse_dates=["date"]).set_index("date").sort_index()
        df = df[~df.index.duplicated(keep="last")]
        if "amount" not in df.columns:
            df["amount"] = df["close"] * df.get("volume", 0.0)
        prices[code] = df
    return prices, missing


def bench_series():
    p = os.path.join(ROOT, "data", "basic", "csi300.csv")
    if not os.path.exists(p):
        return None
    return pd.read_csv(p, parse_dates=["date"]).set_index("date")["close"]


# -------------------------------------------------------------------------------- rollout
def run_rung(close, openp, amt, score, n_hold, cost, phase):
    """One rung of the width ladder at one decision phase. The phase is a shift of the
    decision grid's first bar, nothing else: same panel, same score, same cost."""
    import etf_robust_pf as R
    dates = [d for d in openp.index if d >= pd.Timestamp(START)]
    if phase >= len(dates) - 2:
        return None
    start = dates[phase]
    ser, turn = R.open_to_open_equity(close, openp, amt, score, CADENCE, n_hold, cost,
                                      start=start)
    m = R.stats(ser, "w%d_c%gbp_p%d" % (n_hold, cost * 1e4, phase))
    if m.get("note") == "short":
        return None
    m["turnover"] = round(turn, 3)
    m["phase"] = phase
    m["n_hold"] = n_hold
    m["cost"] = cost
    m["bars"] = int(ser.dropna().shape[0])
    return m


def width_summary(rows):
    """Collapse the phase draws for one width into the median rung, keeping the range."""
    by_w = {}
    for r in rows:
        by_w.setdefault(r["n_hold"], []).append(r)
    out = {}
    for w, rs in by_w.items():
        out[w] = {
            "phases": len(rs),
            "cagr_median": round(_median([r["cagr"] for r in rs]), 4),
            "cagr_min": round(min(r["cagr"] for r in rs), 4),
            "cagr_max": round(max(r["cagr"] for r in rs), 4),
            "vol_median": round(_median([r["vol"] for r in rs]), 4),
            "sharpe_median": round(_median([r["sharpe"] for r in rs]), 3),
            "maxdd_median": round(_median([r["maxdd"] for r in rs]), 4),
            "turnover_median": round(_median([r["turnover"] for r in rs]), 3),
            "bars_median": int(_median([r["bars"] for r in rs])),
        }
    return out


def paired_share(rows, key, hi=None, lo=None):
    """Share of phases where width `hi` beats width `lo` on `key`, paired by phase.
    Unpaired phases (one side short) are dropped and counted, never silently zeroed."""
    hi = WIDTHS[-1] if hi is None else hi
    lo = WIDTHS[0] if lo is None else lo
    a = {r["phase"]: r[key] for r in rows if r["n_hold"] == hi}
    b = {r["phase"]: r[key] for r in rows if r["n_hold"] == lo}
    common = sorted(set(a) & set(b))
    if not common:
        return {"share_up": None, "n_paired": 0, "deltas": []}
    d = [a[p] - b[p] for p in common]
    return {"share_up": round(sum(1 for x in d if x > 0) / float(len(d)), 4),
            "n_paired": len(d),
            "deltas": [round(x, 4) for x in d],
            "median_delta": round(_median(d), 4)}


def run_null(close, openp, amt, score, seeds=NULL_SEEDS, phases=NULL_PHASES,
             cost=NULL_COST):
    """Same engine, same panel, same widths -- but the score is pure noise. This separates
    "wider books earn more" as an arithmetic of diversification from "wider books earn more
    because the signal is better spread". Without this, a width sign and a volatility sign
    are the same number."""
    rng = np.random.default_rng(20261030)
    rows = []
    trials = 0
    for seed in range(seeds):
        noise = pd.DataFrame(rng.standard_normal(score.shape), index=score.index,
                             columns=score.columns)
        # keep the eligibility mask identical: the null must be able to hold whatever the
        # real book could hold, otherwise breadth is compared across different universes.
        noise = noise.where(score.notna())
        for n_hold in WIDTHS:
            for phase in phases:
                r = run_rung(close, openp, amt, noise, n_hold, cost, phase)
                trials += 1
                if r is not None:
                    rows.append(r)
    by_w = width_summary(rows) if rows else {}
    return {
        "seeds": seeds,
        "phases": list(phases),
        "cost": cost,
        "trials": trials,
        "rungs_read": len(rows),
        "by_width": {str(w): by_w.get(w) for w in WIDTHS},
        "cagr_by_width_pp": [round(by_w[w]["cagr_median"] * 100, 3) for w in WIDTHS
                             if w in by_w],
        "rho_cagr_width": (lambda vals: None if len(vals) != len(WIDTHS)
                           else (None if spearman(list(WIDTHS), vals) is None
                                 else round(spearman(list(WIDTHS), vals), 4)))(
            [by_w[w]["cagr_median"] for w in WIDTHS if w in by_w]),
    }


def attribute(real_arm, null):
    """Real minus null, width by width. If the null shows the same width direction, the sign
    is diversification arithmetic; if it does not, the sign belongs to the signal."""
    if not real_arm or not null or not null.get("by_width"):
        return {"status": "unreadable"}
    deltas, real_c, null_c = [], [], []
    for w in WIDTHS:
        r = (real_arm.get("per_width") or {}).get(str(w))
        q = (null.get("by_width") or {}).get(str(w))
        if not r or not q:
            continue
        real_c.append(round(r["cagr_median"] * 100, 3))
        null_c.append(round(q["cagr_median"] * 100, 3))
        deltas.append(round((r["cagr_median"] - q["cagr_median"]) * 100, 3))
    if len(deltas) != len(WIDTHS):
        return {"status": "unreadable", "deltas_pp": deltas}
    widths = list(WIDTHS)
    rho_r = spearman(widths, real_c)
    rho_n = spearman(widths, null_c)
    rho_d = spearman(widths, deltas)
    same = (rho_r is not None and rho_n is not None
            and (rho_r * rho_n) > 0 and abs(rho_n) >= RHO_MIN)
    return {
        "status": "read",
        "real_cagr_pp": real_c,
        "null_cagr_pp": null_c,
        "deltas_pp": deltas,
        "rho_real_width": None if rho_r is None else round(rho_r, 4),
        "rho_null_width": None if rho_n is None else round(rho_n, 4),
        "rho_delta_width": None if rho_d is None else round(rho_d, 4),
        "null_shares_the_width_sign": bool(same),
        "reading": ("the width sign is diversification arithmetic, not a property of the score"
                    if same else
                    "the width sign is not reproduced by noise, so it belongs to the score"),
    }


def null_vs_family(attr, ref):
    """The sharpest thing this face can say. If the quoted family width sign points the same
    way as the NOISE arm on this panel, then that direction is what diversification arithmetic
    produces, and the family's own width sign cannot be credited to its signal without running
    the null on the family panel (which this face does not do and must not pretend to)."""
    fam_rho = (ref or {}).get("width_effect_rank_corr_with_toll")
    null_rho = (attr or {}).get("rho_null_width")
    if fam_rho is None or null_rho is None:
        return {"status": "unreadable"}
    fam_pos = float(fam_rho) > 0
    null_pos = float(null_rho) > 0
    aligned = fam_pos == null_pos
    return {
        "status": "read",
        "family_rho": round(float(fam_rho), 4),
        "null_rho_on_this_panel": round(float(null_rho), 4),
        "aligned": bool(aligned),
        "reading": ("the family's width direction is the direction noise produces -- it cannot be"
                    " credited to the family signal until the null runs on the family panel"
                    if aligned else
                    "the family's width direction is the opposite of what noise produces on this"
                    " panel, so it is not simple diversification arithmetic"),
    }


def classify_arm(arm):
    """Frozen rule: one arm is one cost. Never looks at another arm's numbers."""
    rho = arm.get("rho_cagr_width")
    share = (arm.get("paired_cagr") or {}).get("share_up")
    if rho is None or share is None:
        return "unreadable"
    if rho >= RHO_MIN and share >= PHASE_SHARE_MIN:
        return "replicates"
    if rho <= -RHO_MIN or share <= PHASE_SHARE_FLIP:
        return "flips"
    return "undecided"


def verdict_of(arms):
    states = [a["state"] for a in arms]
    if states and all(s == "replicates" for s in states):
        return "WIDTH_SIGN_REPLICATES"
    if any(s == "flips" for s in states):
        return "WIDTH_SIGN_IS_FAMILY_NAMING"
    if all(s == "unreadable" for s in states) or not states:
        return "UNREADABLE"
    return "WIDTH_SIGN_ARM_DEPENDENT"


def family_reference():
    """The number this face is testing, read from the face that published it -- quoted, not
    recomputed, so a move on either side is visible instead of silently agreeing."""
    if not os.path.exists(FAMILY_FACE):
        return {"face": None, "note": "family ladder face absent"}
    try:
        payload = json.load(open(FAMILY_FACE, encoding="utf-8"))
    except Exception as e:
        return {"face": FAMILY_FACE, "note": "unreadable: %s" % e}
    t = payload.get("toll_ladder") or {}
    return {
        "face": os.path.relpath(FAMILY_FACE, ROOT).replace("\\", "/"),
        "width_effect_median_pp": t.get("width_effect_median_pp"),
        "width_effect_rank_corr_with_toll": t.get("width_effect_rank_corr_with_toll"),
        "width_pair": ((payload.get("spec") or {}).get("width_pair")),
        "panel": "full ETF pool (1653 names), 12 cells, 10 phases each",
    }


# ---------------------------------------------------------------------------------- build
def build():
    prices, missing = load_panel()
    missing = sorted(set(missing) | set(MISSING_DECLARED))
    if len(prices) < max(WIDTHS) + 1:
        raise SystemExit("panel too thin: %d names for widths up to %d"
                         % (len(prices), max(WIDTHS)))
    import etf_composite_pf as E
    from engine.factors import compute_all

    close = pd.DataFrame({s: p["close"] for s, p in prices.items()}).sort_index()
    openp = pd.DataFrame({s: p["open"] for s, p in prices.items()}).sort_index()
    vol = pd.DataFrame({s: p["volume"] for s, p in prices.items()}).sort_index()
    close = close.replace(0.0, np.nan)
    openp = openp.replace(0.0, np.nan)
    amt = (close * vol).rolling(20, min_periods=10).median()
    feats = compute_all(prices, bench_series())
    score = E.build_score(close, amt, feats)

    idx = [d for d in openp.index if d >= pd.Timestamp(START)]
    elig = score.loc[idx].notna().sum(axis=1)
    coverage = {
        "names_loaded": int(close.shape[1]),
        "missing_declared": missing,
        "eligible_names_min": int(elig.min()),
        "eligible_names_median": int(_median(list(elig.values))),
        "eligible_names_max": int(elig.max()),
        "decision_days": len(idx),
    }

    arms = []
    for cost in COSTS:
        rows = []
        for n_hold in WIDTHS:
            for phase in PHASES:
                r = run_rung(close, openp, amt, score, n_hold, cost, phase)
                if r is not None:
                    rows.append(r)
        summ = width_summary(rows)
        meds = [summ[w]["cagr_median"] for w in WIDTHS if w in summ]
        rho = spearman(list(WIDTHS[:len(meds)]), meds) if len(meds) == len(WIDTHS) else None
        paired = paired_share(rows, "cagr")
        paired_sharpe = paired_share(rows, "sharpe")
        paired_vol = paired_share(rows, "vol")
        arm = {
            "cost": cost,
            "cost_bp": round(cost * 1e4, 1),
            "rungs": len(rows),
            "per_width": {str(w): summ[w] for w in WIDTHS if w in summ},
            "cagr_by_width_pp": [round(summ[w]["cagr_median"] * 100, 3)
                                 for w in WIDTHS if w in summ],
            "rho_cagr_width": None if rho is None else round(rho, 4),
            "rho_sharpe_width": _rho_sharpe(summ, "sharpe_median"),
            "paired_cagr": paired,
            "paired_sharpe": paired_sharpe,
            "paired_vol": paired_vol,
            "turnover_by_width": {str(w): summ[w]["turnover_median"]
                                  for w in WIDTHS if w in summ},
        }
        arm["state"] = classify_arm(arm)
        arms.append(arm)

    null = run_null(close, openp, amt, score)

    verdict = verdict_of(arms)
    payload = {
        "study": "E276 width sign, read on a panel the atlas never touched",
        "evidence_cutoff": _cutoff(close),
        "script": "scripts/etf_book_width_cross.py",
        "spec": {
            "panel": "E198 declared 17-ETF cross + its 510300 benchmark (18 usable names)",
            "basket": BASKET,
            "missing_declared": MISSING_DECLARED,
            "widths": list(WIDTHS),
            "cadence": CADENCE,
            "costs": list(COSTS),
            "phases": list(PHASES),
            "start": START,
            "null_seeds": NULL_SEEDS,
            "null_phases": list(NULL_PHASES),
            "null_cost": NULL_COST,
            "rho_min": RHO_MIN,
            "phase_share_min": PHASE_SHARE_MIN,
            "phase_share_flip": PHASE_SHARE_FLIP,
            "score": "composite of the six E-composite factors, ranks computed INSIDE this panel",
            "execution": "decide at close t, fill at open t+1, hold to the next rebalance open",
            "verdict_rule": ("arm replicates if rho_cagr_width>=rho_min and paired share_up"
                             ">=phase_share_min; flips if rho<=-rho_min or share<=phase_share_flip;"
                             " full replicate needs every arm; any flip = family naming"),
        },
        "coverage": coverage,
        "arms": arms,
        "null": null,
        "attribution": attribute(arms[0] if arms else None, null)
        if len(COSTS) == 1 else attribute(_arm_at(arms, NULL_COST), null),
        "null_vs_family": null_vs_family(
            attribute(_arm_at(arms, NULL_COST), null) if len(COSTS) > 1
            else attribute(arms[0] if arms else None, null), family_reference()),
        "verdict": verdict,
        "family_reference": family_reference(),
        "trials": {
            "real_rungs": sum(a.get("rungs") or 0 for a in arms),
            "null_runs": (null or {}).get("trials") or 0,
            "note": ("N counts engine runs, not independent draws: the phase shifts reuse the"
                     " same bars, so N is a workload record and not a multiple-testing denominator"),
        },
        "honest": [
            "The score is re-ranked inside 18 names, so this is a different instrument, not the"
            " same book on new data: a null here says the sign does not travel, not that the"
            " family reading was wrong.",
            "CAGR is confounded with volatility -- fewer names means a more volatile book. Vol"
            " and Sharpe are published per rung for that reason; the paired Sharpe/vol shares"
            " are printed beside the CAGR share and can disagree with it.",
            "80 monthly bars per name is thin for a CAGR claim; the phase draws are the same data"
            " shifted, not new data, so the phase range is a stability read and not a p-value.",
            "510880 and 510180 have no local file and were declared missing, not replaced.",
            "Zero-cost arm is a diagnostic rung (the arm the family sign was read at), not a"
            " tradeable configuration.",
            "The null runs on THIS panel only. It can show that the family's direction is the"
            " direction noise produces, but only a null on the family panel can price the family's"
            " own width effect (that is the next round, not a claim made here).",
        ],
    }
    payload["statement"] = statement(payload)
    return payload


def _arm_at(arms, cost):
    for a in arms or []:
        if abs(float(a.get("cost") or 0.0) - float(cost)) < 1e-12:
            return a
    return None


def _rho_sharpe(summ, key):
    vals = [summ[w][key] for w in WIDTHS if w in summ]
    if len(vals) != len(WIDTHS):
        return None
    r = spearman(list(WIDTHS), vals)
    return None if r is None else round(r, 4)


def _cutoff(close):
    try:
        return str(pd.to_datetime(close.index.max()).date())
    except Exception:
        return None


def statement(p):
    v = p["verdict"]
    attr = p.get("attribution") or {}
    tail = ""
    if attr.get("status") == "read":
        tail = (" Random-score control (N=%d runs): real-minus-null %spp across widths"
                " (rank corr %s), so %s."
                % ((p.get("trials") or {}).get("null_runs") or 0,
                   attr.get("deltas_pp"), attr.get("rho_delta_width"),
                   "the width sign is diversification arithmetic, not the score"
                   if attr.get("null_shares_the_width_sign")
                   else "the width sign belongs to the score, not to noise"))
    nvf = p.get("null_vs_family") or {}
    if nvf.get("status") == "read" and nvf.get("aligned"):
        tail += (" The quoted family direction (%s) is the same direction the noise arm takes on"
                 " this panel (%s), so the family width sign is not yet evidence about the"
                 " signal: it needs its own null." % (nvf.get("family_rho"),
                                                      nvf.get("null_rho_on_this_panel")))
    ref = p.get("family_reference") or {}
    fam = ref.get("width_effect_median_pp")
    a0 = p["arms"][0] if p["arms"] else {}
    a1 = p["arms"][1] if len(p["arms"]) > 1 else {}
    head = ("Family reading (quoted): wider books earned %spp more per rung at rank corr %s "
            "inside a 1653-name pool. On the 18-name cross: " % (fam,
                                                                 ref.get("width_effect_rank_corr_with_toll")))
    if v == "WIDTH_SIGN_REPLICATES":
        return head + ("the sign travels -- cagr rank corr %s at %sbp and %s at %sbp."
                       % (a0.get("rho_cagr_width"), a0.get("cost_bp"),
                          a1.get("rho_cagr_width"), a1.get("cost_bp"))) + tail
    if v == "WIDTH_SIGN_IS_FAMILY_NAMING":
        return head + ("the sign does not travel -- it flips on this panel (cagr rank corr %s at"
                       " %sbp, %s at %sbp), so the width direction is that family's naming, not a"
                       " portable mechanism."
                       % (a0.get("rho_cagr_width"), a0.get("cost_bp"),
                          a1.get("rho_cagr_width"), a1.get("cost_bp"))) + tail
    if v == "UNREADABLE":
        return head + ("the cross could not be read (see coverage), so nothing is claimed."
                       + tail)
    return head + ("the answer depends on the cost: rank corr %s at %sbp vs %s at %sbp --"
                   " reportable, not adoptable."
                   % (a0.get("rho_cagr_width"), a0.get("cost_bp"),
                      a1.get("rho_cagr_width"), a1.get("cost_bp"))) + tail


# --------------------------------------------------------------------------------- render
def render_md(p):
    L = ["# E276 -- does the width sign survive off its own grid? (r1362 bm-c)", "",
         "Panel: %s" % p["spec"]["panel"],
         "Cutoff: %s" % p["evidence_cutoff"],
         "", "## Verdict: `%s`" % p["verdict"], "", p["statement"], "",
         "| cost | width | CAGR med | CAGR range | vol | Sharpe | MaxDD | turnover | phases |",
         "|---|---|---|---|---|---|---|---|---|"]
    for arm in p["arms"]:
        for w in p["spec"]["widths"]:
            row = arm["per_width"].get(str(w))
            if not row:
                continue
            L.append("| %sbp | %d | %.2f%% | %.2f..%.2f%% | %.1f%% | %.3f | %.1f%% | %.2f | %d |"
                     % (arm["cost_bp"], w, row["cagr_median"] * 100,
                        row["cagr_min"] * 100, row["cagr_max"] * 100,
                        row["vol_median"] * 100, row["sharpe_median"],
                        row["maxdd_median"] * 100, row["turnover_median"], row["phases"]))
    L += ["", "## Paired phase reads (widest vs narrowest, same phase)", "",
          "| cost | arm state | rank corr(width, CAGR) | CAGR share up | Sharpe share up | vol share up |",
          "|---|---|---|---|---|---|"]
    for arm in p["arms"]:
        L.append("| %sbp | %s | %s | %s (%d paired) | %s | %s |"
                 % (arm["cost_bp"], arm["state"], arm["rho_cagr_width"],
                    (arm["paired_cagr"] or {}).get("share_up"),
                    (arm["paired_cagr"] or {}).get("n_paired"),
                    (arm["paired_sharpe"] or {}).get("share_up"),
                    (arm["paired_vol"] or {}).get("share_up")))
    null = p.get("null") or {}
    attr = p.get("attribution") or {}
    if null.get("by_width"):
        L += ["", "## Random-score baseline (seeded, same panel/engine/widths)", "",
              "cost %.1fbp, %d seeds x %d phases = %d trials"
              % ((null.get("cost") or 0) * 1e4, null.get("seeds") or 0,
                 len(null.get("phases") or []), null.get("trials") or 0), "",
              "| width | real CAGR | null CAGR | real - null |", "|---|---|---|---|"]
        for i, w in enumerate(p["spec"]["widths"]):
            row = (null["by_width"] or {}).get(str(w)) or {}
            L.append("| %d | %s | %s | %s |"
                     % (w,
                        (attr.get("real_cagr_pp") or [None] * 4)[i],
                        (attr.get("null_cagr_pp") or [None] * 4)[i],
                        (attr.get("deltas_pp") or [None] * 4)[i]))
        if attr.get("status") == "read":
            L += ["", "rank corr with width: real %s / null %s / delta %s -> %s"
                  % (attr.get("rho_real_width"), attr.get("rho_null_width"),
                     attr.get("rho_delta_width"), attr.get("reading"))]
        nvf = p.get("null_vs_family") or {}
        if nvf.get("status") == "read":
            L += ["", "family direction %s vs noise direction %s -> %s"
                  % (nvf.get("family_rho"), nvf.get("null_rho_on_this_panel"),
                     nvf.get("reading"))]
    L += ["", "## Coverage", "",
          "* names loaded: %d (missing declared: %s)"
          % (p["coverage"]["names_loaded"], ", ".join(p["coverage"]["missing_declared"]) or "none"),
          "* eligible names per decision: min %d / median %d / max %d"
          % (p["coverage"]["eligible_names_min"], p["coverage"]["eligible_names_median"],
             p["coverage"]["eligible_names_max"]),
          "* decision days: %d" % p["coverage"]["decision_days"], "",
          "## Honest limits", ""]
    L += ["* " + h for h in p["honest"]]
    L.append("")
    return "\n".join(L)


def write(payload):
    os.makedirs(RES, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write(render_md(payload))
    print("saved", OUT)
    print("saved", OUT_MD)
    print(payload["verdict"], "|", payload["statement"])


# ---------------------------------------------------------------------------------- gates
def check():
    """Recompute the verdict from the stored summariser output. A hand-edited verdict, or a
    verdict whose arm states no longer follow from the numbers, is red."""
    payload = json.load(open(OUT, encoding="utf-8"))
    arms = payload.get("arms") or []
    bad = []
    for arm in arms:
        st = classify_arm(arm)
        if st != arm.get("state"):
            bad.append("cost=%s stored=%s recomputed=%s" % (arm.get("cost_bp"),
                                                            arm.get("state"), st))
    v = verdict_of(arms)
    if v != payload.get("verdict"):
        bad.append("verdict stored=%s recomputed=%s" % (payload.get("verdict"), v))
    spec = payload.get("spec") or {}
    if list(spec.get("widths") or []) != list(WIDTHS):
        bad.append("widths moved: %s" % (spec.get("widths"),))
    if float(spec.get("costs")[0]) != COSTS[0] or len(spec.get("costs") or []) != len(COSTS):
        bad.append("costs moved: %s" % (spec.get("costs"),))
    # a rung that never traded is not a measurement
    for arm in arms:
        for w, row in (arm.get("per_width") or {}).items():
            if not row.get("turnover_median") or row["turnover_median"] <= 0:
                bad.append("cost=%s width=%s never traded" % (arm.get("cost_bp"), w))
    if bad:
        print("CHECK FAILED:")
        for b in bad:
            print("  -", b)
        return 1
    print("CHECK OK: verdict=%s arms=%d widths=%s" % (payload["verdict"], len(arms), list(WIDTHS)))
    return 0


# ------------------------------------------------------------------------------- selftest
def selftest():
    fails = []
    LEGS = [0]

    def leg(name, cond, detail=""):
        LEGS[0] += 1
        if cond:
            print("  PASS", name)
        else:
            print("  FAIL", name, detail)
            fails.append(name)

    def _close(a, b, tol=1e-9):
        return a is not None and abs(a - b) <= tol

    leg("spearman on a monotone ramp is +1", _close(spearman([1, 2, 3, 4], [10, 20, 30, 40]), 1.0))
    leg("spearman inverts with the ramp", _close(spearman([1, 2, 3, 4], [40, 30, 20, 10]), -1.0))
    leg("spearman follows the tie structure, not the values",
        _close(spearman([1, 2, 2, 3], [5, 7, 7, 9]), 1.0))
    leg("a partially tied pair is neither +1 nor -1",
        0.0 < (spearman([1, 2, 2, 3], [1, 2, 3, 4]) or 0.0) < 1.0)
    leg("a flat arm is not a sign", spearman([1, 2, 3], [5, 5, 5]) is None)

    # verdict classifier: each branch reachable
    rep = {"rho_cagr_width": 0.9, "paired_cagr": {"share_up": 0.8}}
    flp = {"rho_cagr_width": -0.9, "paired_cagr": {"share_up": 0.2}}
    mid = {"rho_cagr_width": 0.1, "paired_cagr": {"share_up": 0.6}}
    leg("classifier: replicate", classify_arm(rep) == "replicates")
    leg("classifier: flip", classify_arm(flp) == "flips")
    leg("classifier: undecided", classify_arm(mid) == "undecided")
    leg("classifier: unreadable when a term is missing",
        classify_arm({"rho_cagr_width": None, "paired_cagr": {}}) == "unreadable")

    def arm(st):
        return {"state": st}

    leg("verdict: every arm replicates", verdict_of([arm("replicates"), arm("replicates")])
        == "WIDTH_SIGN_REPLICATES")
    leg("verdict: one flip is enough to name it",
        verdict_of([arm("replicates"), arm("flips")]) == "WIDTH_SIGN_IS_FAMILY_NAMING")
    leg("verdict: mixed is arm dependent",
        verdict_of([arm("replicates"), arm("undecided")]) == "WIDTH_SIGN_ARM_DEPENDENT")
    leg("verdict: nothing readable is UNREADABLE",
        verdict_of([arm("unreadable"), arm("unreadable")]) == "UNREADABLE")

    # attribution: only a null that reproduces the real width direction can absorb the sign
    def _arm(cagrs):
        return {"per_width": {str(w): {"cagr_median": c / 100.0}
                              for w, c in zip(WIDTHS, cagrs)}}

    def _null(cagrs):
        return {"by_width": {str(w): {"cagr_median": c / 100.0}
                             for w, c in zip(WIDTHS, cagrs)}}

    a_same = attribute(_arm([6.0, 5.0, 4.0, 3.0]), _null([6.0, 5.0, 4.0, 3.0]))
    leg("attribution: a null with the same ramp absorbs the sign",
        a_same["status"] == "read" and a_same["null_shares_the_width_sign"] is True, str(a_same))
    a_flat = attribute(_arm([6.0, 5.0, 4.0, 3.0]), _null([3.0, 3.1, 2.9, 3.0]))
    leg("attribution: a flat null leaves the sign with the score",
        a_flat["status"] == "read" and a_flat["null_shares_the_width_sign"] is False)
    leg("attribution: missing rungs are unreadable, not quietly zero",
        attribute(_arm([6.0, 5.0, 4.0, 3.0]), {"by_width": {}})["status"] == "unreadable")
    leg("attribution: deltas are real minus null, per width",
        a_flat["deltas_pp"] == [3.0, 1.9, 1.1, 0.0], str(a_flat["deltas_pp"]))

    # family-vs-noise alignment
    leg("null_vs_family: same direction is flagged as not-yet-evidence",
        null_vs_family({"rho_null_width": 1.0},
                       {"width_effect_rank_corr_with_toll": 1.0}).get("aligned") is True)
    leg("null_vs_family: opposite direction is not arithmetic",
        null_vs_family({"rho_null_width": -1.0},
                       {"width_effect_rank_corr_with_toll": 1.0}).get("aligned") is False)
    leg("null_vs_family: no quoted rho is unreadable",
        null_vs_family({"rho_null_width": 1.0}, {}).get("status") == "unreadable")

    # paired share must pair by phase, not by row order
    rows = [{"n_hold": 3, "phase": 0, "cagr": 0.10}, {"n_hold": 3, "phase": 4, "cagr": 0.20},
            {"n_hold": 12, "phase": 4, "cagr": 0.25}, {"n_hold": 12, "phase": 0, "cagr": 0.05}]
    ps = paired_share(rows, "cagr")
    leg("paired share pairs by phase", ps["n_paired"] == 2 and ps["share_up"] == 0.5, str(ps))

    # integration: the engine actually trades, and diversification lowers volatility.
    # (E126: an equivalence read is worthless without proving something happened.)
    try:
        import etf_robust_pf as R
        rng = np.random.default_rng(20261030)
        n_names, n_bars = 24, 420
        idx = pd.bdate_range("2020-01-01", periods=n_bars)
        rets = rng.normal(0.0003, 0.012, size=(n_bars, n_names))
        close = pd.DataFrame(100 * np.cumprod(1 + rets, axis=0), index=idx,
                             columns=[str(i) for i in range(n_names)])
        openp = close.shift(1).fillna(close.iloc[0])
        amt = pd.DataFrame(5e8, index=idx, columns=close.columns)
        # a score that is constant in time but differs across names, so selection is stable
        score = pd.DataFrame(np.tile(np.linspace(1.0, -1.0, n_names), (n_bars, 1)),
                             index=idx, columns=close.columns)
        narrow, tn = R.open_to_open_equity(close, openp, amt, score, 20, 3, 0.0)
        wide, tw = R.open_to_open_equity(close, openp, amt, score, 20, 12, 0.0)
        sn, sw = R.stats(narrow, "n3"), R.stats(wide, "n12")
        leg("fixture: the engine really traded (narrow)", tn > 0 and sn["vol"] > 0,
            "turn=%s vol=%s" % (tn, sn.get("vol")))
        leg("fixture: the engine really traded (wide)", tw > 0 and sw["vol"] > 0,
            "turn=%s vol=%s" % (tw, sw.get("vol")))
        leg("fixture: diversification lowers volatility (3 names > 12 names)",
            sn["vol"] > sw["vol"], "n3=%s n12=%s" % (sn["vol"], sw["vol"]))
        leg("fixture: both books cover the same window",
            narrow.dropna().shape[0] == wide.dropna().shape[0],
            "bars n3=%d n12=%d" % (narrow.dropna().shape[0], wide.dropna().shape[0]))
    except Exception as e:  # pragma: no cover
        leg("fixture: engine runs", False, str(e))

    print("selftest: %d/%d pass, %d fail" % (LEGS[0] - len(fails), LEGS[0], len(fails)))
    return 1 if fails else 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run", choices=["run", "check", "selftest"])
    ap.add_argument("--check", dest="check_flag", action="store_true")
    ap.add_argument("--selftest", dest="selftest_flag", action="store_true")
    a = ap.parse_args(argv)
    if a.check_flag or a.cmd == "check":
        return check()
    if a.selftest_flag or a.cmd == "selftest":
        return selftest()
    write(build())
    return 0


if __name__ == "__main__":
    sys.exit(main())
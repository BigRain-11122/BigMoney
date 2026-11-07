"""Is the A-share size ladder a size effect, or a listing-cohort effect?

WHY THIS EXISTS (r1413)
-----------------------
r1412 priced the equal-weight breadth premium against cap weights and read a ladder:
EW_ALL +10.11%/yr, CW_ALL +2.01%, terciles small/mid/large +14.98/+9.97/+0.55, and the
small-minus-large spread held in all 12 decision phases where the EW level did not. That
is the first decomposed structure this desk can hold, so the next question is not "how
big" but "what is it".

The archive cannot answer it by holding the dead: of 5,199 names, 5,198 trade to the last
bar and 1,671 start inside the window -- the panel is a snapshot of currently listed
names, so a delisting-aware reading is impossible from inside. What IS measurable is the
other structural confound: 1,671 of those names did not exist in 2020, and the small end
of a cap-sorted pool is where new listings land first. A-share new listings also carry
their own return pattern. So "small" and "young" are two names for the same cohort in
this panel unless it is tested.

CONSTRUCTION (frozen; changing any line changes the answer)
-----------------------------------------------------------
  panel       data/astock_daily/per/<sym>.csv via zoo93.load_panel(with_shares=True)
              -- single loader, imported, never re-implemented
  eligible    at decision bar t: bb.eligibility (20-bar median amount >= 20M CNY,
              finite close) -- imported from the r1411 control, same rule
  cohorts     bb.cohorts, R = 60 bars, non-overlapping, next-open entry, sell R bars
              later (r = open[t+1+R]/open[t+1]-1) -- imported, same rule
  cap         close[t] * outstanding_share[t] (total-market-cap proxy, not float)
  age         t - first_bar(sym), where first_bar = first finite close index in the
              panel. first_bar == 0 means LISTED BEFORE THE PANEL: the age is censored
              and that name is never claimed to be old, only "pre-panel".
  tiers       PREPANEL  first_bar == 0                       (age unknowable, >= t+1)
              YOUNG     0 < first_bar, age <= 250 bars        (about one year)
              MID       250 < age <= 750 bars
              OLD       age > 750 bars (all in-panel ages past 3 years)
  arms        pooled_sml / pooled_lrg = cap terciles on the whole member set (the r1412
                       arms, re-run here and required to reproduce its reading)
              <tier>_sml / <tier>_lrg = cap terciles computed INSIDE that tier only
                       (smallest third vs largest third of the tier's own members), equal
                       weight inside each tercile, 2 x 13.041bp per cohort per arm
  annualise   bb.chained over cohorts (252/60 periods per year)
  phases      decision offsets 0, 5, ..., 55 (12 readings) on the pooled arms AND on
              the pre-panel spread; the phase set is the error bar r1411 established

READ THE SPREAD, NOT THE LEVEL
------------------------------
Every arm here is an equal-weighted tercile, so its LEVEL carries the breadth premium
that r1411 already showed cannot be separated from the calendar on 26 cohorts. The
quantity under test is small-minus-large inside one tier. Within-tier levels are
reported because they are free, and they are not the verdict.

VERDICT RULE (frozen BEFORE the numbers were seen; re-emitted in the receipt)
  Let P = pooled_sml - pooled_lrg (the r1412 size spread)
      S = prepanel_sml - prepanel_lrg (the spread among names already listed in 2020,
          the only tier whose members cannot be new listings)
  SIZE_SURVIVES_AGE_CONTROL iff S > 0 and S >= 0.60 * P and S > 0 in >= 8 of 12 phases
  AGE_IS_THE_PREMIUM      iff S <= 0 or S <= 0.25 * P
  MIXED                   otherwise
  No arm is proposed for registration in either case. The output is an attribution of
  the r1412 ladder; a candidate still needs its own frozen prereg.

USAGE
  selftest  python scripts/astock_size_age_control.py selftest   # synthetic, seconds
  run       python scripts/astock_size_age_control.py run        # full panel, ~4 min
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import astock_breadth_book as bb          # eligibility/cohorts/chained/cost, one copy
import zoo93_disposition_cgo_probe as z93  # panel loader, one copy
import astock_size_decomp as z80          # caps_at/tercile_bounds, one copy

OUT = os.path.join(ROOT, "results", "size_decomp", "astock_size_age_control.json")
COST = bb.COST_PER_SIDE
R = bb.R
PHASE_STEP = 5
TERCILES = z80.TERCILES

TIERS = ("prepanel", "young", "mid", "old")
YOUNG_MAX = 250
MID_MAX = 750


def first_bar(panel: dict) -> np.ndarray:
    """First finite close index per symbol; -1 for a symbol that never trades."""
    cl = np.asarray(panel["close"], dtype=np.float64)
    fin = np.isfinite(cl)
    has = fin.any(axis=0)
    idx = np.where(has, fin.argmax(axis=0), -1)
    return idx.astype(np.int64)


def tier_of(first: np.ndarray, t: int) -> np.ndarray:
    """Tier label per symbol at decision bar t, as an index into TIERS (-1 = unknown)."""
    out = np.full(first.size, -1, dtype=np.int64)
    live = first >= 0
    pre = live & (first == 0)
    age = np.where(live, t - first, -1)
    out[pre] = 0
    out[live & (first > 0) & (age <= YOUNG_MAX)] = 1
    out[live & (first > 0) & (age > YOUNG_MAX) & (age <= MID_MAX)] = 2
    out[live & (first > 0) & (age > MID_MAX)] = 3
    return out


def tercile_pair(cap: np.ndarray, rs: np.ndarray) -> dict:
    """Smallest-third vs largest-third equal-weight readings inside one subset."""
    ok = np.isfinite(cap) & (cap > 0) & np.isfinite(rs)
    n = int(ok.sum())
    out = {"n": n, "sml": float("nan"), "lrg": float("nan")}
    if n < TERCILES * 2:
        return out
    sub_cap = cap[ok]
    sub_rs = rs[ok]
    order = np.argsort(sub_cap, kind="mergesort")
    sorted_rs = sub_rs[order]
    bounds = z80.tercile_bounds(sub_cap[order])
    lo0, hi0 = bounds[0]
    lo2, hi2 = bounds[-1]
    if hi0 > lo0:
        out["sml"] = float(sorted_rs[lo0:hi0].mean()) - 2.0 * COST
    if hi2 > lo2:
        out["lrg"] = float(sorted_rs[lo2:hi2].mean()) - 2.0 * COST
    return out


def cohort_row(panel: dict, t: int, members: np.ndarray, rs: np.ndarray,
               first: np.ndarray) -> dict:
    """Every arm's NET reading for one cohort; unreadable arms stay NaN, never filled."""
    cap_all = z80.caps_at(panel, t, members)
    pooled = tercile_pair(cap_all, rs)
    row = {
        "date": panel["dates"][t],
        "n_members": int(members.size),
        "pooled_sml": pooled["sml"],
        "pooled_lrg": pooled["lrg"],
        "pooled_n": pooled["n"],
        "tiers": {},
    }
    tiers = tier_of(first, t)[members]
    for k, name in enumerate(TIERS):
        m = tiers == k
        cell = tercile_pair(cap_all[m], rs[m])
        row["tiers"][name] = cell
    return row


def cohort_rows(panel: dict, first: np.ndarray, r: int = R, offset: int = 0) -> list[dict]:
    cs, _skipped = bb.cohorts(panel, r=r, offset=offset)
    return [cohort_row(panel, t, members, rs, first) for t, members, rs in cs]


ARMS = ("pooled_sml", "pooled_lrg") + tuple(
    f"{t}_{s}" for t in TIERS for s in ("sml", "lrg"))


def _arm_seq(rows: list[dict], arm: str) -> list[float]:
    if arm in ("pooled_sml", "pooled_lrg"):
        seq = [row[arm] for row in rows]
    else:
        tier, side = arm.rsplit("_", 1)
        seq = [row["tiers"][tier][side] for row in rows]
    return [x for x in seq if np.isfinite(x)]


def chain_arms(rows: list[dict]) -> dict:
    out = {}
    for arm in ARMS:
        seq = _arm_seq(rows, arm)
        cagr, dd, _curve = bb.chained(seq, r=R)
        out[arm] = {"cagr": cagr, "maxdd": dd, "cohorts": len(seq),
                    "skipped": len(rows) - len(seq)}
    return out


def verdict_block(chained: dict, phase_stats: dict) -> dict:
    def c(a):
        return chained[a]["cagr"]

    fails = []
    P = S = None
    if np.isfinite(c("pooled_sml")) and np.isfinite(c("pooled_lrg")):
        P = c("pooled_sml") - c("pooled_lrg")
    if np.isfinite(c("prepanel_sml")) and np.isfinite(c("prepanel_lrg")):
        S = c("prepanel_sml") - c("prepanel_lrg")
    pos_phases = phase_stats.get("prepanel_positive_phases")
    n_phases = phase_stats.get("phases_read")
    if P is None or S is None or not pos_phases or not n_phases:
        v = "UNDECISIVE"
        if P is None:
            fails.append("pooled terciles unreadable")
        if S is None:
            fails.append("pre-panel terciles unreadable")
        if not pos_phases or not n_phases:
            fails.append("phase sweep unreadable")
    elif S > 0 and S >= 0.60 * P and pos_phases * 12 >= 8 * n_phases:
        v = "SIZE_SURVIVES_AGE_CONTROL"
    elif S <= 0 or S <= 0.25 * P:
        v = "AGE_IS_THE_PREMIUM"
    else:
        v = "MIXED"
    if v == "AGE_IS_THE_PREMIUM" and S > 0:
        fails.append("pre-panel spread is positive but small against the pooled spread")
    return {
        "verdict": v,
        "pooled_spread_pp": None if P is None else round(P * 100.0, 3),
        "prepanel_spread_pp": None if S is None else round(S * 100.0, 3),
        "prepanel_share_of_pooled": (None if (P is None or S is None or P == 0)
                                     else round(S / P, 3)),
        "prepanel_positive_phases": pos_phases,
        "phases_read": n_phases,
        "failing_conditions": fails,
        "rule": "SIZE_SURVIVES_AGE_CONTROL iff prepanel_spread>0 and "
                ">=0.60*pooled_spread and positive in >=8/12 phases; "
                "AGE_IS_THE_PREMIUM iff prepanel_spread<=0 or <=0.25*pooled; "
                "MIXED otherwise",
        "candidate": False,
        "note": "attribution of the r1412 size ladder; nothing is proposed for "
                "registration -- a candidate still needs its own frozen prereg",
    }


def phase_readings(panel: dict, first: np.ndarray, r: int = R) -> dict:
    phases = []
    for off in range(0, r, PHASE_STEP):
        ch = chain_arms(cohort_rows(panel, first, r=r, offset=off))
        def rd(a):
            v = ch[a]["cagr"]
            return None if v is None else round(v * 100.0, 3)
        sp = None
        if ch["prepanel_sml"]["cagr"] is not None and ch["prepanel_lrg"]["cagr"] is not None:
            sp = round((ch["prepanel_sml"]["cagr"] - ch["prepanel_lrg"]["cagr"]) * 100.0, 3)
        phases.append({
            "offset": off,
            "pooled_sml": rd("pooled_sml"),
            "pooled_lrg": rd("pooled_lrg"),
            "prepanel_sml": rd("prepanel_sml"),
            "prepanel_lrg": rd("prepanel_lrg"),
            "pooled_spread_pp": None if (rd("pooled_sml") is None or rd("pooled_lrg") is None)
                                else round(rd("pooled_sml") - rd("pooled_lrg"), 3),
            "prepanel_spread_pp": sp,
        })
    read = [p for p in phases if p["prepanel_spread_pp"] is not None]
    pos = [p for p in read if p["prepanel_spread_pp"] > 0]
    pooled_read = [p for p in phases if p["pooled_spread_pp"] is not None]
    pooled_pos = [p for p in pooled_read if p["pooled_spread_pp"] > 0]
    vals = np.array([p["prepanel_spread_pp"] for p in read], dtype=np.float64)
    return {
        "phases": phases,
        "phases_read": len(read),
        "prepanel_positive_phases": len(pos),
        "prepanel_spread_range_pp": (None if not vals.size
                                     else [float(vals.min()), float(vals.max())]),
        "pooled_positive_phases": len(pooled_pos),
        "pooled_phases_read": len(pooled_read),
    }


def age_share(rows: list[dict]) -> dict:
    """How much of the pooled small tercile is young -- the confound in name counts."""
    tot = {t: 0 for t in TIERS}
    for row in rows:
        for t in TIERS:
            tot[t] += row["tiers"][t]["n"]
    grand = sum(tot.values())
    return {
        "member_cohort_slots": tot,
        "share": {t: (None if not grand else round(tot[t] / grand, 4)) for t in TIERS},
    }


def run() -> dict:
    t0 = time.time()
    panel = z93.load_panel(with_shares=True)
    if "shares" not in panel:
        raise SystemExit("panel loader did not return shares")
    first = first_bar(panel)
    rows = cohort_rows(panel, first)
    chained = chain_arms(rows)
    ph = phase_readings(panel, first)
    vb = verdict_block(chained, ph)
    receipt = {
        "face": "astock_size_age_control",
        "asof": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "evidence_cutoff": panel["dates"][-1] if panel["dates"] else None,
        "construct": {
            "panel": "data/astock_daily/per (qfq, with outstanding_share)",
            "names": len(panel["symbols"]),
            "bars": len(panel["dates"]),
            "first_date": panel["dates"][0], "last_date": panel["dates"][-1],
            "hold_bars": int(R), "cost_per_side": COST,
            "cohort_count": len(rows),
            "terciles": TERCILES,
            "tier_rules": {"prepanel": "first_bar == 0 (listed before panel start)",
                           "young": f"0 < first_bar, age <= {YOUNG_MAX}",
                           "mid": f"{YOUNG_MAX} < age <= {MID_MAX}",
                           "old": f"age > {MID_MAX}"},
            "names_listed_inside_panel": int((first > 0).sum()),
            "names_listed_before_panel": int((first == 0).sum()),
            "names_never_priced": int((first < 0).sum()),
        },
        "chained": chained,
        "verdict_block": vb,
        "age_share": age_share(rows),
        "phases": ph,
        "series": [
            {"date": r["date"], "n_members": r["n_members"],
             "pooled_sml": r["pooled_sml"], "pooled_lrg": r["pooled_lrg"],
             "tiers": {k: r["tiers"][k] for k in TIERS}}
            for r in rows
        ],
        "elapsed_sec": round(time.time() - t0, 1),
        "honest": [
            "the archive is a snapshot of currently listed names: 5,199 symbols and 5,198 "
            "carry a bar at the last date, so a delisting-aware reading is impossible "
            "from inside this panel and no such claim is made",
            "pre-panel listed names have a CENSORED age (>= t+1 bars); they are the "
            "cleanest tier only in the sense that none of them is a new listing",
            "pool = names liquid enough for a 20M CNY 20-bar median amount; small caps "
            "near that gate are not investable at scale, and equal weight across a "
            "tercile of ~1,400 names is not a book",
            "cap = close x outstanding_share is total market cap, not free float",
            "cohort drawdown is 60-bar granularity, coarser than a daily curve",
            "26 quarterly cohorts over six years: a level difference this short a "
            "sample cannot separate from the calendar, which is why only the SPREAD is "
            "under test here",
        ],
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(receipt, fh, ensure_ascii=False, indent=1)
    return receipt


# --------------------------------------------------------------------------- #
def _synth(nT=400, nS=150, seed=11, size_link=0.0, age_link=0.0,
           young_from=0, young_until=0, young_starts=250):
    """Synthetic panel: `young_from..young_until` symbols list late (bars are NaN
    before `young_starts`). size_link ties returns to 1/sqrt(cap rank), age_link
    adds a drift to the late listers, so the two confounds can be turned on
    independently.
    """
    p = z80._synth(nT=nT, nS=nS, seed=seed, size_link=size_link)
    if young_until > young_from:
        p["open"][:young_starts, young_from:young_until] = float("nan")
        p["close"][:young_starts, young_from:young_until] = float("nan")
        p["amount"][:young_starts, young_from:young_until] = float("nan")
    if age_link:
        # the extra drift starts at the listing bar, so the age axis carries it
        for j in range(young_from, young_until):
            base = p["close"][young_starts, j]
            p["close"][young_starts:, j] = base * np.cumprod(
                np.full(nT - young_starts, 1.0 + age_link))
            p["open"][young_starts:, j] = p["close"][young_starts:, j] * 1.001
    return p


def selftest() -> int:
    fails = []
    # L1 first_bar: a symbol that never prices reads -1; a late lister reads its
    #    first real index, never 0 (0 would silently file it as pre-panel).
    p1 = _synth(young_from=0, young_until=30, young_starts=100)
    f1 = first_bar(p1)
    if f1[0] != 100:
        fails.append(f"L1 a late lister reads first_bar={f1[0]}, expected 100")
    if f1[60] != 0:
        fails.append(f"L1 a full-history name reads first_bar={f1[0]}, expected 0")
    p1["close"][:, 70] = np.nan
    if first_bar(p1)[70] != -1:
        fails.append("L1 a never-priced symbol did not read -1")
    # L2 tiers: disjoint, cover every live member, and the pre-panel label is
    #    reserved for first_bar == 0 only.
    f2 = first_bar(_synth(young_from=0, young_until=30, young_starts=100))
    tw = tier_of(f2, 200)
    if not ((tw[0] >= 1) and (tw[60] == 0)):
        fails.append(f"L2 tier split wrong: late={tw[0]} early={tw[60]}")
    if set(np.unique(tw[f2 >= 0]).tolist()) - set(range(len(TIERS))):
        fails.append("L2 tier split produced an out-of-range label")
    # L3 flat tape: every tercile reading is exactly minus the round trip.
    flat = tercile_pair(np.arange(1, 61, dtype=np.float64) * 1e8, np.zeros(60))
    for side in ("sml", "lrg"):
        if abs(flat[side] + 2.0 * COST) > 1e-12:
            fails.append(f"L3 flat tape {side} != -2*cost ({flat[side]})")
    # L4 too few names: refused, not averaged over a shorter tercile.
    tiny = tercile_pair(np.array([1e8, 2e8, 3e8]), np.array([0.01, 0.02, 0.03]))
    if np.isfinite(tiny["sml"]) or np.isfinite(tiny["lrg"]):
        fails.append("L4 a three-name subset produced a tercile reading")
    # L5 size-only tape (every name pre-panel): the within-tier spread must be
    #    positive, and the verdict must not blame age.
    p5 = _synth(size_link=0.004)
    f5 = first_bar(p5)
    ch5 = chain_arms(cohort_rows(p5, f5))
    sp5 = ch5["prepanel_sml"]["cagr"] - ch5["prepanel_lrg"]["cagr"]
    if not (sp5 > 0):
        fails.append(f"L5 a size-only tape produced a pre-panel spread of {sp5:.4f}")
    # L6 age-only tape: late listers carry the drift and start small, so the pooled
    #    spread is positive while the pre-panel spread is not. The verdict must read
    #    AGE_IS_THE_PREMIUM -- this is the whole point of the face.
    p6 = _synth(size_link=0.0, age_link=0.0025, young_from=0, young_until=40,
                young_starts=200)
    p6["shares"] = np.repeat((np.arange(1, 151, dtype=np.float64) * 2e8)[None, :],
                             p6["close"].shape[0], axis=0)
    f6 = first_bar(p6)
    rows6 = cohort_rows(p6, f6)
    ch6 = chain_arms(rows6)
    ph6 = phase_readings(p6, f6)
    vb6 = verdict_block(ch6, ph6)
    if vb6["verdict"] != "AGE_IS_THE_PREMIUM":
        fails.append(f"L6 an age-only tape read {vb6['verdict']} "
                     f"(pooled {vb6['pooled_spread_pp']}, pre-panel "
                     f"{vb6['prepanel_spread_pp']})")
    if not (vb6["pooled_spread_pp"] is not None and vb6["pooled_spread_pp"] > 0):
        fails.append("L6 the age-only tape did not show up in the pooled spread, so the "
                     "leg proves nothing about telling the two confounds apart")
    if not (vb6["prepanel_spread_pp"] is not None
            and vb6["prepanel_spread_pp"] <= 0.25 * vb6["pooled_spread_pp"]):
        fails.append("L6 the pre-panel spread did not collapse against the pooled one "
                     f"({vb6['prepanel_spread_pp']} vs {vb6['pooled_spread_pp']})")
    # L7 chain reproducibility against bb.chained on the same sequence
    seq = [0.01, -0.02, 0.03]
    cagr_a, _dd, _c = bb.chained(seq, r=R)
    curve = np.concatenate(([1.0], np.cumprod(1.0 + np.asarray(seq))))
    cagr_b = curve[-1] ** (1.0 / (len(seq) * R / 252.0)) - 1.0
    if abs(cagr_a - cagr_b) > 1e-12:
        fails.append("L7 chained disagrees with its own closed form")
    # L8 an unreadable tier must be skipped, not counted as a zero return
    rows8 = [{"date": "d0", "n_members": 2, "pooled_sml": 0.01, "pooled_lrg": 0.01,
              "tiers": {t: {"n": 0, "sml": float("nan"), "lrg": float("nan")}
                        for t in TIERS}}]
    ch8 = chain_arms(rows8)
    if ch8["prepanel_sml"]["cohorts"] != 0:
        fails.append("L8 a NaN tier reading entered the chain")
    if fails:
        for f in fails:
            print("FAIL", f)
        return 1
    print("selftest 8/8 OK")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", nargs="?", default="run", choices=["run", "selftest"])
    a = ap.parse_args()
    if a.mode == "selftest":
        return selftest()
    r = run()
    ch = r["chained"]
    print("names", r["construct"]["names"], "bars", r["construct"]["bars"],
          "cohorts", r["construct"]["cohort_count"], "elapsed", r["elapsed_sec"])
    for arm in ARMS:
        print(f"  {arm:14s} cagr={ch[arm]['cagr']} maxdd={ch[arm]['maxdd']} "
              f"cohorts={ch[arm]['cohorts']}")
    vb = r["verdict_block"]
    print("verdict", vb["verdict"], "pooled_pp", vb["pooled_spread_pp"],
          "prepanel_pp", vb["prepanel_spread_pp"],
          "phases", vb["prepanel_positive_phases"], "/", vb["phases_read"])
    print("age share", r["age_share"]["share"])
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
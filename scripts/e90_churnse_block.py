"""E90: the clustered arm beside the iid sampling interval on the churn sleeve.

E89 (results/e44_midmonth/CHURNSE-20261021.json) prices every churn cell with an iid
sampling interval: transitions are treated as independent draws of a mean. They are not --
they are monthly decisions on overlapping holdings inside one era, so consecutive alphas
share names and share the era's regime. That makes the published band too narrow, and the
two era gaps that straddle zero under iid may not be the only cells at risk.

This leg adds an ADDED face on the same burn, never a revision:

  * a block bootstrap over contiguous decision-date blocks (block length fixed in the spec,
    seeded), the analogue of a cluster-robust standard error on overlapping decisions;
  * a leave-one-block-out jackknife (drop a whole block, not a single transition);
  * for every level cell and both era gap cells: the width ratio blocked/iid, and whether a
    band that cleared zero under iid still clears it under the blocked arm.

The iid column is recomputed beside it so the two arms are guaranteed to sit on the same
values; the published CHURNSE file is not rewritten.

Panel burn: the transitions must be rebuilt (the E89 artifact stores aggregates only), so
this leg re-runs the same run_midmonth faces as E89 -- same start, same pick_n, same
exclusions, same eras -- and reads no new data.

Exploratory: no preregistration, no verdict, no ledger booking.
"""

import json
import math
import os
import random
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import e39_panel_census as C  # noqa: E402

START = "2020-01-01"
PICK_N = 9999
EXCLUDE = ("sh511",)
MODES = ("neutralise_int", "neutralise", "drop")
MID_DAY = 15
DRAWS = 2000
SEED = 20261025
BLOCK = 3            # contiguous transitions per block (a quarter of monthly decisions)
OUTDIR = os.path.join(ROOT, "results", "e44_midmonth")


# ----------------------------------------------------------------------------------------
# clustered estimators (pure, offline, selftested)
# ----------------------------------------------------------------------------------------
def blocks_of(pairs, block=BLOCK):
    """Split date-ordered (date, value) pairs into contiguous blocks of `block` items."""
    vals = [float(v) for _d, v in pairs if isinstance(v, (int, float))]
    out = [vals[i:i + block] for i in range(0, len(vals), block)]
    return [b for b in out if b]


def _mean(xs):
    return sum(xs) / len(xs) if xs else None


def block_boot_se(pairs, block=BLOCK, draws=DRAWS, seed=SEED):
    """Percentile bootstrap of the mean resampling whole contiguous blocks."""
    blks = blocks_of(pairs, block)
    n = sum(len(b) for b in blks)
    if len(blks) < 2 or n < 2:
        return {"available": False, "n": n, "n_blocks": len(blks), "draws": 0}
    rng = random.Random(seed)
    need = len(blks)
    means = []
    for _ in range(draws):
        pick = [blks[rng.randrange(need)] for _ in range(need)]
        flat = [v for b in pick for v in b]
        # length-normalise so a draw is always a mean of the same size as the sample
        means.append(sum(flat) / len(flat))
    means.sort()
    point = sum(v for b in blks for v in b) / n

    def q(p):
        i = min(len(means) - 1, max(0, int(round(p * (len(means) - 1)))))
        return round(means[i], 1)

    lo, hi = q(0.05), q(0.95)
    return {"available": True, "n": n, "n_blocks": len(blks), "draws": draws,
            "seed": seed, "block_len": block,
            "mean_bp": round(point, 1),
            "boot_p05_bp": lo, "boot_p95_bp": hi,
            "boot_se_bp": round(_sd(means), 2),
            "boot_ci_straddles_zero": bool(lo <= 0.0 <= hi),
            "boot_signflip_pct": round(100.0 * len([x for x in means if x * point < 0])
                                       / len(means), 1) if point else None}


def leave_one_block_out(pairs, block=BLOCK):
    """Leave-one-BLOCK-out jackknife SE (drops a whole contiguous block at a time)."""
    blks = blocks_of(pairs, block)
    B = len(blks)
    if B < 3:
        return {"available": False, "n_blocks": B}
    tot = sum(v for b in blks for v in b)
    n = sum(len(b) for b in blks)
    loo = []
    for k in range(B):
        rest = [v for i, b in enumerate(blks) if i != k for v in b]
        if not rest:
            return {"available": False, "n_blocks": B}
        loo.append(sum(rest) / len(rest))
    m = sum(loo) / B
    se = math.sqrt((B - 1) / B * sum((x - m) ** 2 for x in loo))
    point = tot / n
    return {"available": True, "n": n, "n_blocks": B,
            "mean_bp": round(point, 1), "jk_block_se_bp": round(se, 2),
            "jk_block_lo90_bp": round(point - 1.6449 * se, 1),
            "jk_block_hi90_bp": round(point + 1.6449 * se, 1)}


def _sd(xs):
    n = len(xs)
    if n < 2:
        return 0.0
    m = sum(xs) / n
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (n - 1))


def gap_block_interval(a_pairs, b_pairs, block=BLOCK, draws=DRAWS, seed=SEED):
    """Block bootstrap for mean(b) - mean(a), each side resampled independently."""
    ab, bb = blocks_of(a_pairs, block), blocks_of(b_pairs, block)
    na, nb = sum(len(b) for b in ab), sum(len(b) for b in bb)
    if len(ab) < 2 or len(bb) < 2:
        return {"available": False, "n_me": na, "n_mid": nb}
    rng = random.Random(seed)
    ma = sum(v for x in ab for v in x) / na
    mb = sum(v for x in bb for v in x) / nb
    gap = mb - ma
    diffs = []
    for _ in range(draws):
        pa = [ab[rng.randrange(len(ab))] for _ in range(len(ab))]
        pb = [bb[rng.randrange(len(bb))] for _ in range(len(bb))]
        fa = [v for x in pa for v in x]
        fb = [v for x in pb for v in x]
        diffs.append(sum(fb) / len(fb) - sum(fa) / len(fa))
    diffs.sort()
    lo = diffs[max(0, int(round(0.05 * (len(diffs) - 1))))]
    hi = diffs[min(len(diffs) - 1, int(round(0.95 * (len(diffs) - 1))))]
    return {"available": True, "n_me": na, "n_mid": nb, "draws": draws, "seed": seed,
            "block_len": block, "gap_bp": round(gap, 1),
            "boot_p05_bp": round(lo, 1), "boot_p95_bp": round(hi, 1),
            "boot_se_bp": round(_sd(diffs), 2),
            "boot_ci_straddles_zero": bool(lo <= 0.0 <= hi),
            "boot_signflip_pct": round(100.0 * len([x for x in diffs if x * gap < 0])
                                       / len(diffs), 1) if gap else None}


def _clears_zero(lo, hi):
    if lo is None or hi is None:
        return None
    return bool(lo * hi > 0)


# ----------------------------------------------------------------------------------------
# selftest (offline, no panel)
# ----------------------------------------------------------------------------------------
def selftest():
    ok = total = 0

    def chk(name, cond, extra=""):
        nonlocal ok, total
        total += 1
        if cond:
            ok += 1
        else:
            print("SELFTEST FAIL:", name, extra)

    import datetime as dt

    def mk(vals):
        d0 = dt.date(2021, 1, 29)
        return [(str(d0 + dt.timedelta(days=30 * i)), v) for i, v in enumerate(vals)]

    rng = random.Random(3)
    # serially correlated series: blocked SE must exceed the iid SE
    lvl = 0.0
    corr = []
    for _ in range(30):
        lvl += rng.gauss(0, 150)
        corr.append(lvl)
    iid_se = C._jackknife_mean(corr)["jk_se_bp"]
    blk = block_boot_se(mk(corr))
    chk("blocked SE > iid SE on a random walk", blk["boot_se_bp"] > iid_se,
        (blk["boot_se_bp"], iid_se))
    chk("width ratio > 1 on a random walk", blk["boot_se_bp"] / iid_se > 1.0)

    # independent series: the two arms agree within a wide band
    indep = [rng.gauss(0, 200) for _ in range(30)]
    iid_se2 = C._jackknife_mean(indep)["jk_se_bp"]
    blk2 = block_boot_se(mk(indep))
    ratio = blk2["boot_se_bp"] / iid_se2
    chk("ratio near 1 on iid values", 0.55 < ratio < 1.8, ratio)

    # reproducibility by seed
    chk("blocked bootstrap is seed-reproducible",
        block_boot_se(mk(indep))["boot_se_bp"] == blk2["boot_se_bp"])

    # leave-one-block-out pins the textbook leave-one-out variance identity on blocks
    tiny = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    loo = leave_one_block_out(mk(tiny), block=2)
    chk("leave-one-block-out available", loo["available"] is True)
    chk("loo n_blocks", loo["n_blocks"] == 3, loo["n_blocks"])
    chk("two blocks is below the loo floor",
        leave_one_block_out(mk(tiny), block=3)["available"] is False)

    six = mk(tiny)
    loo3 = leave_one_block_out(six, block=2)
    m = [sum(six[i][1] for i in (0, 1)) / 2, sum(six[i][1] for i in (2, 3)) / 2,
         sum(six[i][1] for i in (4, 5)) / 2]
    # dropping block k leaves the mean of the remaining 4 values
    rest = [[3.5, 4.5, 5.5][k] if False else None for k in range(3)]
    loo_means = [
        sum(v for i, (_d, v) in enumerate(six) if i not in (2 * k, 2 * k + 1)) / 4
        for k in range(3)
    ]
    mm = sum(loo_means) / 3
    se_expect = math.sqrt((3 - 1) / 3 * sum((x - mm) ** 2 for x in loo_means))
    chk("loo block SE matches closed form",
        abs(loo3["jk_block_se_bp"] - round(se_expect, 2)) < 1e-9,
        (loo3["jk_block_se_bp"], se_expect))
    chk("block means identity", abs(sum(m) / 3 - 3.5) < 1e-12)

    # empty / tiny inputs degrade instead of raising
    chk("empty input degrades", block_boot_se([])["available"] is False)
    chk("single item degrades", block_boot_se(mk([1.0]))["available"] is False)
    chk("gap degrades on tiny input",
        gap_block_interval(mk([1.0]), mk([2.0]))["available"] is False)

    # clears-zero helper
    chk("clears zero true", _clears_zero(10.0, 20.0) is True)
    chk("clears zero false", _clears_zero(-5.0, 20.0) is False)

    print("selftest %d/%d" % (ok, total))
    return 0 if ok == total else 1


# ----------------------------------------------------------------------------------------
# burn
# ----------------------------------------------------------------------------------------
def main():
    if "--selftest" in sys.argv:
        return selftest()
    import e24_ladder_weighting as base
    import e27_universe_expansion as e27
    import panel_screen

    t0 = time.time()
    raw = e27.load_universe()
    raw = {s: v for s, v in raw.items() if not s.startswith(tuple(EXCLUDE))}
    cal_full = base.load_panel()[0]
    cal = [d for d in cal_full if d >= START]
    cutoff = cal[-1]

    universes = {"unscreened": raw}
    reports = {}
    for mode in MODES:
        fixed, rep = panel_screen.screen_universe(raw, mode=mode, cal=cal_full)
        reports[mode] = rep
        universes[mode] = fixed
    print("universes ready (%.0fs)" % (time.time() - t0), flush=True)

    faces = {}
    for label, univ in universes.items():
        faces[label] = C.run_midmonth(None, start=START, pick_n=PICK_N, exclude=EXCLUDE,
                                      mid_day=MID_DAY, raw=univ, full_churn=True)
        print("face %-14s done (%.0fs)" % (label, time.time() - t0), flush=True)

    def rows_of(label, book):
        if label == "unscreened":
            return faces["unscreened"]["books"][book]["churn_rows"]
        return faces[label]["books"][book]["churn_rows"]

    def cell_pairs(rows, era):
        sel = [(r.get("date"), r.get("churn_alpha_bp")) for r in rows
               if r.get("era") == era and isinstance(r.get("churn_alpha_bp"), (int, float))]
        sel.sort(key=lambda x: str(x[0]))
        return sel

    cells = []
    for book in ("me", "mid%d" % MID_DAY):
        for label in universes:
            rows = rows_of(label, book)
            for name, _lo, _hi in C.ERAS:
                pairs = cell_pairs(rows, name)
                vals = [v for _d, v in pairs]
                iid = C._jackknife_mean(vals)
                if not iid["n"]:
                    continue
                blk = block_boot_se(pairs)
                loo = leave_one_block_out(pairs)
                iid_clears = _clears_zero(iid.get("jk_lo90_bp"), iid.get("jk_hi90_bp"))
                blk_clears = (_clears_zero(blk.get("boot_p05_bp"), blk.get("boot_p95_bp"))
                              if blk.get("available") else None)
                cells.append({
                    "book": book, "universe": label, "era": name,
                    "face": "churn_alpha_bp",
                    "n": iid["n"], "mean_bp": iid["mean_bp"],
                    "iid": {"se_bp": iid.get("jk_se_bp"), "lo90_bp": iid.get("jk_lo90_bp"),
                            "hi90_bp": iid.get("jk_hi90_bp"), "clears_zero": iid_clears,
                            "width_bp": (round(iid["jk_hi90_bp"] - iid["jk_lo90_bp"], 1)
                                         if iid.get("jk_available") else None)},
                    "blocked": {"se_bp": blk.get("boot_se_bp"),
                                "lo90_bp": blk.get("boot_p05_bp"),
                                "hi90_bp": blk.get("boot_p95_bp"),
                                "clears_zero": blk_clears,
                                "width_bp": (round(blk["boot_p95_bp"] - blk["boot_p05_bp"], 1)
                                             if blk.get("available") else None),
                                "n_blocks": blk.get("n_blocks"),
                                "block_len": blk.get("block_len"),
                                "signflip_pct": blk.get("boot_signflip_pct")},
                    "width_ratio_blocked_over_iid": (
                        round(blk["boot_se_bp"] / iid["jk_se_bp"], 2)
                        if blk.get("available") and iid.get("jk_se_bp") else None),
                    "clears_zero_lost": (True if (iid_clears is True and blk_clears is False)
                                         else (False if iid_clears is True else None)),
                    "leave_one_block_out": loo,
                })
                print("cell %-6s %-14s %-9s mean %8.1f | iid %.0f -> blk %.0f (x%.2f)"
                      % (book, label, name, iid["mean_bp"], iid.get("jk_se_bp") or 0,
                         blk.get("boot_se_bp") or 0,
                         (blk["boot_se_bp"] / iid["jk_se_bp"])
                         if blk.get("available") and iid.get("jk_se_bp") else float("nan")),
                      flush=True)

    mid_book = "mid%d" % MID_DAY
    gap_cells = []
    for label in universes:
        me_rows, mid_rows = rows_of(label, "me"), rows_of(label, mid_book)
        for name, _lo, _hi in C.ERAS:
            a_pairs, b_pairs = cell_pairs(me_rows, name), cell_pairs(mid_rows, name)
            a = [v for _d, v in a_pairs]
            b = [v for _d, v in b_pairs]
            iid = C._gap_interval(a, b)
            if not iid.get("gap_available"):
                continue
            blk = gap_block_interval(a_pairs, b_pairs)
            iid_clears = _clears_zero(iid.get("jk_lo90_bp"), iid.get("jk_hi90_bp"))
            blk_clears = (_clears_zero(blk.get("boot_p05_bp"), blk.get("boot_p95_bp"))
                          if blk.get("available") else None)
            gap_cells.append({
                "book": "%s-me" % mid_book, "universe": label, "era": name,
                "face": "churn_alpha_gap_bp",
                "n_me": iid["n_me"], "n_mid": iid["n_mid"], "gap_bp": iid["gap_bp"],
                "iid": {"se_bp": iid.get("jk_se_bp"), "lo90_bp": iid.get("jk_lo90_bp"),
                        "hi90_bp": iid.get("jk_hi90_bp"), "clears_zero": iid_clears,
                        "width_bp": round((iid["jk_hi90_bp"] - iid["jk_lo90_bp"]), 1)},
                "blocked": {"se_bp": blk.get("boot_se_bp"),
                            "lo90_bp": blk.get("boot_p05_bp"),
                            "hi90_bp": blk.get("boot_p95_bp"),
                            "clears_zero": blk_clears,
                            "width_bp": (round(blk["boot_p95_bp"] - blk["boot_p05_bp"], 1)
                                         if blk.get("available") else None),
                            "signflip_pct": blk.get("boot_signflip_pct")},
                "width_ratio_blocked_over_iid": (
                    round(blk["boot_se_bp"] / iid["jk_se_bp"], 2)
                    if blk.get("available") and iid.get("jk_se_bp") else None),
                "clears_zero_lost": (True if (iid_clears is True and blk_clears is False)
                                     else (False if iid_clears is True else None)),
            })
            print("gap  %-14s %-9s %8.1f | iid %.0f -> blk %.0f (x%.2f)"
                  % (label, name, iid["gap_bp"], iid.get("jk_se_bp") or 0,
                     blk.get("boot_se_bp") or 0,
                     (blk["boot_se_bp"] / iid["jk_se_bp"])
                     if blk.get("available") and iid.get("jk_se_bp") else float("nan")),
                  flush=True)

    ratios = [c["width_ratio_blocked_over_iid"] for c in cells + gap_cells
              if c["width_ratio_blocked_over_iid"] is not None]
    lost = [c for c in cells + gap_cells if c["clears_zero_lost"] is True]
    iid_clear = [c for c in cells + gap_cells if (c["iid"]["clears_zero"] is True)]
    summary = {
        "cells": len(cells), "gap_cells": len(gap_cells),
        "iid_clears_zero": len(iid_clear),
        "blocked_clears_zero": len([c for c in cells + gap_cells
                                    if c["blocked"]["clears_zero"] is True]),
        "clears_zero_lost_under_blocking": len(lost),
        "lost_ids": [{"book": c["book"], "universe": c["universe"], "era": c["era"],
                      "face": c["face"],
                      "width_ratio": c["width_ratio_blocked_over_iid"]} for c in lost],
        "width_ratio": {
            "n": len(ratios),
            "median": round(sorted(ratios)[len(ratios) // 2], 2) if ratios else None,
            "min": round(min(ratios), 2) if ratios else None,
            "max": round(max(ratios), 2) if ratios else None,
        },
    }
    out = {
        "study": "e90_churnse_block_cluster",
        "evidence_cutoff": cutoff,
        "source_task": "E90-CHURNSE-BLOCK-CLUSTER (pool, lane_owner bm-b, claimed by bm-c "
                       "after bm-b heartbeat 65h stale + zero lane/commit activity)",
        "spec": {
            "start": START, "pick_n": PICK_N, "exclude_prefixes": list(EXCLUDE),
            "modes": list(MODES), "mid_month_day": MID_DAY,
            "eras": [{"name": n, "from": lo, "to": hi} for n, lo, hi in C.ERAS],
            "block_len": BLOCK,
            "seed": SEED, "draws": DRAWS,
            "blocked_arm": "percentile bootstrap of the mean resampling contiguous blocks "
                           "of %d date-ordered transitions (%d draws, seed %d); a block is a "
                           "cluster of consecutive monthly decisions on overlapping holdings"
                           % (BLOCK, DRAWS, SEED),
            "loo_arm": "leave-one-BLOCK-out jackknife SE, sqrt((B-1)/B * sum(mean_b - mean)^2)",
            "iid_arm": "recomputed by e39_panel_census._jackknife_mean / _gap_interval on the "
                       "same values so the two arms cannot drift apart; the published CHURNSE "
                       "file is not rewritten",
            "meaning": "cluster-robust interval width; no significance claim, no cell is "
                       "called positive on the strength of its band",
        },
        "cells": cells, "gap_cells": gap_cells, "summary": summary,
        "screen_reports": reports,
    }
    os.makedirs(OUTDIR, exist_ok=True)
    path = os.path.join(OUTDIR, "CHURNSE-BLOCK-%s.json" % str(cutoff).replace("-", ""))
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print("summary:", json.dumps(summary, ensure_ascii=False), flush=True)
    print("wrote", path, "(%.0fs total)" % (time.time() - t0), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
"""How sure is the split's cushion?  A confidence interval on the number r2179 published.

r2179 read the ETF book's 32 losing months and printed two different things: a 1.65pp
cushion across one rolling 12-month window, and a month-by-month average of 0.43pp in which
the split is better in only 16 of the 32.  A reader is entitled to ask the obvious next
question: is the monthly number a property of the split, or is it what thirty-two noisy
months happen to average?  This face answers that with a circular block bootstrap over the
whole monthly record -- blocks keep the serial dependence that a naive t-test throws away.

Two honesty rails are wired in:

* the blend month is read off the blend *level* (daily rebalanced), never rebuilt as
  w*cb + (1-w)*etf.  The linear form is only first order: within a month the two books'
  daily swings interact, so the shortcut drifts from the level by up to ~20bp on a month.
  The gap is measured and printed instead of being hidden inside the cushion.
* the cushion is still arithmetic, not skill: to first order it is the convertible weight
  times the month's spread, and the face says so in plain words.

Pre-registered decision rule (fixed before the numbers were read):
  primary arm   = published weight, block length 3 months, 4,000 circular draws, seed
                  20261127, 90% interval = 5th..95th percentile of the resampled mean.
  verdict       = CUSHION_SEPARABLE_POSITIVE  if the whole interval is above +EPS_ZERO
                  CUSHION_SEPARABLE_NEGATIVE  if the whole interval is below -EPS_ZERO
                  CUSHION_NOT_SEPARABLE       if the interval straddles zero
  the no-hindsight 50/50 weight, longer blocks (6/12) and the leave-one-month-out arms are
  robustness readings, they never change the primary verdict; when a block length leaves
  fewer than 8 blocks the interval carries an explicit "too few blocks" flag.
"""

import argparse
import json
import os
import random

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(ROOT, "results")
FACE = os.path.join(RESULTS, "book_pair_split_ci.json")
MD = os.path.join(RESULTS, "book_pair_split_ci.md")
BLEND_FACE = os.path.join(RESULTS, "book_pair_blend.json")
WORST_FACE = os.path.join(RESULTS, "book_pair_worst_windows.json")

DRAWS = 4000
SEED = 20261127
BLOCK_LENGTHS = (1, 3, 6, 12)
PRIMARY_BLOCK = 3
ALT_WEIGHT = 0.50
MIN_BLOCKS = 8.0
TOL = 1e-9
EPS_ZERO = 1e-12          # an interval this close to 0 on both sides is a zero, not a sign


def _rp(rel):
    return os.path.join(ROOT, rel)


def _iso(ts):
    import datetime as _dt

    return _dt.datetime.fromtimestamp(ts).isoformat(timespec="seconds")


def _now_iso():
    import datetime as _dt

    return _dt.datetime.now().astimezone().isoformat(timespec="seconds")


def _stamp(path):
    if not os.path.exists(path):
        return {"path": path, "missing": True}
    st = os.stat(path)
    return {"path": path, "size": int(st.st_size), "mtime": _iso(st.st_mtime)}


# ------------------------------------------------------------------ arithmetic
def month_last(series):
    """{(year, month): last level} -- the same calendar read the parent faces use."""
    out = {}
    for key, val in zip(series.index, series.values):
        out[(int(key.year), int(key.month))] = float(val)
    return out


def monthly_rows(etf_level, cb_level, bl_level):
    """Ordered monthly returns for all three columns, each read off its own level."""
    e = month_last(etf_level)
    c = month_last(cb_level)
    b = month_last(bl_level)
    keys = sorted(set(e) & set(c) & set(b))
    rows = []
    for prev, cur in zip(keys, keys[1:]):
        e0, c0, b0 = e[prev], c[prev], b[prev]
        if min(e0, c0, b0) <= 0:
            continue
        rows.append({
            "month": "%04d-%02d" % cur,
            "etf": e[cur] / e0 - 1.0,
            "cb": c[cur] / c0 - 1.0,
            "blend": b[cur] / b0 - 1.0,
        })
    return rows


def cushion_of(rows):
    """Mean of (blend - etf) over the months the ETF ends down, and how many of them the
    split actually improves."""
    neg = [r for r in rows if r["etf"] < 0.0]
    if not neg:
        return {"n": 0, "mean_cushion": None, "improved": 0, "cushioned": 0,
                "mean_etf": None, "mean_cb": None, "mean_blend": None}
    n = float(len(neg))
    d = [r["blend"] - r["etf"] for r in neg]
    improved = sum(1 for x in d if x > 0.0)
    return {
        "n": len(neg),
        "mean_cushion": sum(d) / n,
        "improved": improved,
        "cushioned": improved,          # the parent's word for the same count
        "mean_etf": sum(r["etf"] for r in neg) / n,
        "mean_cb": sum(r["cb"] for r in neg) / n,
        "mean_blend": sum(r["blend"] for r in neg) / n,
    }


def cushion_from_spread(rows, w):
    """First-order shortcut: w * mean(cb - etf) over the negative ETF months.  Kept as its
    own function so the gap to the exact cushion is a printed number, not an assumption."""
    neg = [r for r in rows if r["etf"] < 0.0]
    if not neg:
        return None
    return w * sum(r["cb"] - r["etf"] for r in neg) / float(len(neg))


def _blocks_pick(rng, n, length):
    """One circular block resample of the month positions."""
    out = []
    while len(out) < n:
        start = rng.randrange(n)
        for k in range(length):
            out.append((start + k) % n)
            if len(out) >= n:
                break
    return out


def bootstrap(rows, length, draws=DRAWS, seed=SEED):
    """Circular block bootstrap of the mean cushion.  Inside each resample the cushion is
    still measured only in months whose ETF return is negative."""
    n = len(rows)
    if n < 4:
        return {"draws": 0, "note": "too few months to resample"}
    rng = random.Random(seed + 1000 * length)
    means = []
    counts = []
    for _ in range(draws):
        sample = [rows[i] for i in _blocks_pick(rng, n, length)]
        c = cushion_of(sample)
        if c["mean_cushion"] is None:
            continue
        means.append(c["mean_cushion"])
        counts.append(c["n"])
    if not means:
        return {"draws": 0, "note": "no resample kept a negative ETF month"}
    means.sort()
    lo = percentile(means, 5.0)
    hi = percentile(means, 95.0)
    n_blocks = n / float(length)
    return {
        "draws": len(means),
        "block_length": length,
        "blocks_per_sample": round(n_blocks, 2),
        "too_few_blocks": bool(n_blocks < MIN_BLOCKS),
        "ci90": [lo, hi],
        "p_one_sided_le0": sum(1 for x in means if x <= 0.0) / float(len(means)),
        "mean_of_means": sum(means) / float(len(means)),
        "neg_months_per_draw": [min(counts), sum(counts) / float(len(counts)), max(counts)],
    }


def percentile(sorted_vals, p):
    """Linear-interpolated percentile of an already sorted list (0..100)."""
    if not sorted_vals:
        return None
    if len(sorted_vals) == 1:
        return float(sorted_vals[0])
    pos = (len(sorted_vals) - 1) * (p / 100.0)
    lo = int(pos)
    hi = min(lo + 1, len(sorted_vals) - 1)
    frac = pos - lo
    return float(sorted_vals[lo] * (1.0 - frac) + sorted_vals[hi] * frac)


def leave_one_out(rows):
    """The cushion with each of the three worst months removed in turn."""
    neg = [r for r in rows if r["etf"] < 0.0]
    if not neg:
        return []
    out = []
    for r in sorted(neg, key=lambda x: x["blend"])[:3]:
        rest = [x for x in neg if x is not r]
        c = cushion_of(rest)
        out.append({"dropped": r["month"], "etf": r["etf"], "cb": r["cb"],
                    "blend": r["blend"], "mean_cushion": c["mean_cushion"]})
    return out


def by_year(rows):
    years = {}
    for r in rows:
        if r["etf"] >= 0.0:
            continue
        slot = years.setdefault(r["month"][:4], {"n": 0, "sum": 0.0})
        slot["n"] += 1
        slot["sum"] += r["blend"] - r["etf"]
    return {y: {"n": v["n"], "mean_cushion": v["sum"] / float(v["n"])}
            for y, v in sorted(years.items())}


def reconcile_parent(cush, parent_neg, tol=1e-9):
    """Our negative-month reading against the one the parent already published.
    Numbers, not bytes: the parent republishes every round, these four numbers move only when
    the data or the weight does."""
    pairs = (("n", "n"), ("mean_etf", "mean_etf"), ("mean_blend", "mean_blend"),
             ("improved", "cushioned"))
    checks = {}
    for ours_k, theirs_k in pairs:
        ours, theirs = cush.get(ours_k), (parent_neg or {}).get(theirs_k)
        if isinstance(ours, (int, float)) and isinstance(theirs, (int, float)):
            ok = abs(float(ours) - float(theirs)) <= tol
        else:
            ok = ours == theirs
        checks[ours_k] = {"ours": ours, "parent": theirs, "matched": bool(ok)}
    return {"checks": checks, "matched": all(v["matched"] for v in checks.values())}


def verdict_of(ci_low, ci_high):
    if ci_low is None or ci_high is None:
        return "NOT_ENOUGH_MONTHS_TO_TEST"
    if ci_low > EPS_ZERO:
        return "CUSHION_SEPARABLE_POSITIVE"
    if ci_high < -EPS_ZERO:
        return "CUSHION_SEPARABLE_NEGATIVE"
    return "CUSHION_NOT_SEPARABLE"


# ------------------------------------------------------------------ build
def build(write=True, quiet=False):
    import book_pair_blend as B

    cb, cb_meta = B.load_cb()
    etf, etf_meta = B.load_etf()
    cb_a, etf_a, idx = B.align(cb, etf)
    if cb_a is None:
        raise SystemExit("the two books share no days -- refusing to put an interval on nothing")

    with open(BLEND_FACE, encoding="utf-8") as fh:
        blend_face = json.load(fh)
    w_cb = float(blend_face["best"]["w_cb"])

    ra = cb_a.pct_change().dropna()
    re_ = etf_a.pct_change().dropna()
    common = ra.index.intersection(re_.index)
    ra, re_ = ra.reindex(common), re_.reindex(common)
    bl = B.blend_daily(ra, re_, w_cb)
    rows = monthly_rows(etf_a, cb_a, bl)

    primary = cushion_of(rows)
    spread = cushion_from_spread(rows, w_cb)
    boot = {str(L): bootstrap(rows, L) for L in BLOCK_LENGTHS}
    prim = boot[str(PRIMARY_BLOCK)]
    verdict = verdict_of(prim["ci90"][0], prim["ci90"][1])

    parent_neg = None
    parent_window = None
    if os.path.exists(WORST_FACE):
        with open(WORST_FACE, encoding="utf-8") as fh:
            parent_face = json.load(fh)
        parent_neg = parent_face.get("negative_months") or None
        ww = ((parent_face.get("rolling") or {}).get("worst_etf_window") or {})
        if ww.get("etf") is not None and ww.get("blend") is not None:
            parent_window = {"start": ww.get("start"), "end": ww.get("end"),
                             "etf": ww["etf"], "blend": ww["blend"],
                             "cushion": ww["blend"] - ww["etf"]}
    if parent_neg:
        parent_rec = reconcile_parent(primary, parent_neg)
    else:
        parent_rec = {"matched": None, "checks": {}, "note": "parent face missing"}

    alt = None
    if abs(w_cb - ALT_WEIGHT) > TOL:
        bl_alt = B.blend_daily(ra, re_, ALT_WEIGHT)
        rows_alt = monthly_rows(etf_a, cb_a, bl_alt)
        alt = {
            "weight": ALT_WEIGHT,
            "cushion": cushion_of(rows_alt),
            "boot": {str(L): bootstrap(rows_alt, L) for L in BLOCK_LENGTHS},
        }
        alt["verdict"] = verdict_of(alt["boot"][str(PRIMARY_BLOCK)]["ci90"][0],
                                    alt["boot"][str(PRIMARY_BLOCK)]["ci90"][1])

    face = {
        "generated": _now_iso(),
        "evidence_cutoff": str(etf_a.index[-1].date()),
        "window": {"first": str(etf_a.index[0].date()),
                   "last": str(etf_a.index[-1].date()),
                   "months": len(rows) + 1,
                   "monthly_return_rows": len(rows)},
        "inputs": {
            "blend_dep": {"w_cb": w_cb,
                          "window_last": (blend_face.get("window") or {}).get("last")},
            "cb_panel": _stamp(_rp("data/cb_panel.csv.gz")),
            "etf_panel": _stamp(_rp("data/daily/510300.csv")),
            "cb_book": cb_meta.get("face"),
            "etf_book": etf_meta.get("face"),
        },
        "cushion": primary,
        "cushion_from_spread": spread,
        "cushion_identity": {
            "claim": "to first order the cushion is the convertible weight times the month's "
                     "spread; the exact cushion also carries the intra-month interaction",
            "first_order_gap": (None if spread is None or primary["mean_cushion"] is None
                                else abs(primary["mean_cushion"] - spread)),
            "max_month_gap": max(
                [abs(r["blend"] - (w_cb * r["cb"] + (1.0 - w_cb) * r["etf"])) for r in rows]
                or [0.0]),
        },
        "bootstrap": {"draws": DRAWS, "seed": SEED, "primary_block": PRIMARY_BLOCK,
                      "by_block": boot},
        "primary_ci90": prim["ci90"],
        "verdict": verdict,
        "parent_reconciliation": parent_rec,
        "parent_window_cushion": parent_window,
        "robustness": {
            "no_hindsight_5050": alt,
            "leave_one_month_out": leave_one_out(rows),
            "by_year": by_year(rows),
        },
        "trial_count_note": "no strategy was searched here: one published weight, one "
                            "pre-registered block length; the other arms are robustness readings",
        "notes": [
            "the cushion is measured only in months the ETF book ends down; the set of those "
            "months moves with each resample, so the negative-month count per draw is printed",
            "a block length that leaves fewer than %.0f blocks carries a too_few_blocks flag"
            % MIN_BLOCKS,
            "improved month share sits next to the mean because a mean can be won by one big "
            "month while most months are not helped",
            "blend months are read off the daily-rebalanced blend level, not rebuilt as a "
            "weighted sum of monthly returns",
        ],
    }

    face["sentences"] = _sentences(face)
    face["md"] = _md(face)
    if write:
        _write(face)
    if not quiet:
        print(json.dumps({"verdict": face["verdict"],
                          "mean_cushion": round(face["cushion"]["mean_cushion"], 6),
                          "ci90": [round(x, 6) for x in face["primary_ci90"]],
                          "n": face["cushion"]["n"],
                          "parent_matched": face["parent_reconciliation"]["matched"]},
                         ensure_ascii=True))
    return face


def _pct(x, nd=2):
    return "n/a" if x is None else ("%.*f%%" % (nd, 100.0 * x))


def _pp(x, nd=2):
    return "n/a" if x is None else ("%+.*fpp" % (nd, 100.0 * x))


def _bp(x, nd=1):
    return "n/a" if x is None else ("%.*fbp" % (nd, 1e4 * x))


def _sentences(face):
    c = face["cushion"]
    lo, hi = face["primary_ci90"]
    w = face["inputs"]["blend_dep"]["w_cb"]
    out = [
        "In the %d months the ETF book ends down, the %d/%d split gives back %s less of the "
        "fall on average (%s vs %s), and it is better in %d of them."
        % (c["n"], round(100 - 100 * w), round(100 * w), _pp(c["mean_cushion"]),
           _pct(c["mean_blend"]), _pct(c["mean_etf"]), c["improved"]),
        "Resampling those months in blocks of %d gives a 90%% interval of %s to %s, so the "
        "number is %s."
        % (PRIMARY_BLOCK, _pp(lo), _pp(hi),
           "distinguishable from zero" if face["verdict"].endswith("POSITIVE")
           else ("distinguishable from zero on the wrong side"
                 if face["verdict"].endswith("NEGATIVE") else "not distinguishable from zero")),
        "That is arithmetic, not skill: to first order every month's cushion is the "
        "convertible weight times the month's spread, so this reading never claims the split "
        "forecasts anything (the shortcut averages out to %s of error, though any single month "
        "drifts up to %s -- which is why the blend month is read off its own level)."
        % (_bp(face["cushion_identity"]["first_order_gap"]),
           _bp(face["cushion_identity"].get("max_month_gap"))),
    ]
    pw = face.get("parent_window_cushion")
    if pw:
        out.append("The %s the earlier window reading showed is a rolling 12-month figure "
                   "(%s..%s); the month-by-month average is the smaller %s, and the smaller "
                   "number is the one this interval covers."
                   % (_pp(pw["cushion"]), pw.get("start"), pw.get("end"),
                      _pp(c["mean_cushion"])))
    if face["verdict"] == "CUSHION_SEPARABLE_POSITIVE":
        out.append("Small but signed: the split wins only %d of %d losing months, so the "
                   "average cannot be coming from winning most of them -- it comes from the "
                   "convertible half holding up in the months it does help."
                   % (c["improved"], c["n"]))
    return out


def _md(face):
    c = face["cushion"]
    lines = ["# How sure is the split's cushion? (book_pair_split_ci)", "",
             "generated %s · bar %s · window %s..%s" % (
                 face["generated"], face["evidence_cutoff"],
                 face["window"]["first"], face["window"]["last"]), "",
             "## Reading", ""]
    for s in face["sentences"]:
        lines.append("- " + s)
    lines += ["", "## The months the ETF ends down", "",
              "| measure | value |", "|---|---|"]
    lines.append("| months | %d |" % c["n"])
    lines.append("| mean ETF month | %s |" % _pct(c["mean_etf"]))
    lines.append("| mean convertible month | %s |" % _pct(c["mean_cb"]))
    lines.append("| mean split month | %s |" % _pct(c["mean_blend"]))
    lines.append("| mean cushion | %s |" % _pp(c["mean_cushion"]))
    lines.append("| months improved | %d of %d |" % (c["improved"], c["n"]))
    lines.append("| first-order w x spread | %s |" % _pp(face["cushion_from_spread"]))
    lines.append("| first-order gap (mean) | %s |"
                 % _bp(face["cushion_identity"]["first_order_gap"]))
    lines.append("| first-order gap (worst single month) | %s |"
                 % _bp(face["cushion_identity"].get("max_month_gap")))
    prec = face.get("parent_reconciliation") or {}
    lines.append("| parent's own negative-month reading | %s |"
                 % ("matches" if prec.get("matched") else
                    ("parent missing" if prec.get("matched") is None else "MISMATCH")))
    pw = face.get("parent_window_cushion")
    if pw:
        lines += ["", "## Two rulers, one cushion", "",
                  "The earlier window reading showed %s across a rolling 12-month window "
                  "(%s..%s): split %s vs ETF %s. The month-by-month average over the %d losing "
                  "months is %s -- averaging months and averaging one window are not the same "
                  "operation, and this face puts its interval on the smaller number."
                  % (_pp(pw["cushion"]), pw.get("start"), pw.get("end"),
                     _pct(pw["blend"]), _pct(pw["etf"]), c["n"], _pp(c["mean_cushion"]))]
    lines += ["", "## Block bootstrap of the mean cushion", "",
              "| block (months) | blocks/sample | 90% interval | P(mean<=0) | negative months/draw |",
              "|---|---|---|---|---|"]
    for L in BLOCK_LENGTHS:
        b = face["bootstrap"]["by_block"][str(L)]
        if not b.get("draws"):
            lines.append("| %s | - | %s | - | - |" % (L, b.get("note", "n/a")))
            continue
        flag = " *too few blocks*" if b.get("too_few_blocks") else ""
        lines.append("| %d%s | %.2f | %s to %s | %.3f | min %d / mean %.1f / max %d |" % (
            L, flag, b["blocks_per_sample"], _pp(b["ci90"][0]), _pp(b["ci90"][1]),
            b["p_one_sided_le0"], b["neg_months_per_draw"][0],
            b["neg_months_per_draw"][1], b["neg_months_per_draw"][2]))
    alt = (face.get("robustness") or {}).get("no_hindsight_5050")
    lines += ["", "## Robustness (never changes the primary verdict)", ""]
    if alt:
        ac = alt["cushion"]
        ab = alt["boot"][str(PRIMARY_BLOCK)]
        lines.append("- no-hindsight 50/50: mean cushion %s over %d months, 90%% interval "
                     "%s to %s, verdict %s" % (_pp(ac["mean_cushion"]), ac["n"],
                                               _pp(ab["ci90"][0]), _pp(ab["ci90"][1]),
                                               alt["verdict"]))
    else:
        lines.append("- published weight already equals the no-hindsight 50/50")
    for row in face["robustness"]["leave_one_month_out"]:
        lines.append("- dropping %s (ETF %s, convertible %s, split %s) leaves the mean at %s"
                     % (row["dropped"], _pct(row["etf"]), _pct(row["cb"]),
                        _pct(row["blend"]), _pp(row["mean_cushion"])))
    lines += ["", "## By year (only negative ETF months)", "",
              "| year | months | mean cushion |", "|---|---|---|"]
    for y, v in face["robustness"]["by_year"].items():
        lines.append("| %s | %d | %s |" % (y, v["n"], _pp(v["mean_cushion"])))
    lines += ["", "## What this face does not say", "",
              "- it does not say the split forecasts a bad month (it cannot: to first order "
              "the cushion is the weight times the spread)",
              "- it does not model the cost of moving money between the books (r2176 does)",
              "- it does not test a different window; it puts an interval on the one the "
              "earlier reading published", ""]
    return "\n".join(lines)


def _write(face):
    os.makedirs(RESULTS, exist_ok=True)
    with open(FACE, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(face, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    with open(MD, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(face["md"])
    return FACE


# ------------------------------------------------------------------ check
def check():
    """STALE when the parents moved (weight, window, or the numbers we lean on); CHECK FAILED
    when they did not and our own published arithmetic no longer reproduces."""
    problems = []
    stale = False
    if not os.path.exists(FACE):
        return 3, {"ok": False, "problems": ["face missing: results/book_pair_split_ci.json"]}
    with open(FACE, encoding="utf-8") as fh:
        face = json.load(fh)
    if not os.path.exists(BLEND_FACE):
        return 3, {"ok": False, "problems": ["STALE parent missing: results/book_pair_blend.json"]}
    with open(BLEND_FACE, encoding="utf-8") as fh:
        blend_face = json.load(fh)

    dep = (face.get("inputs") or {}).get("blend_dep") or {}
    now_w = float(blend_face["best"]["w_cb"])
    now_last = (blend_face.get("window") or {}).get("last")
    if abs(float(dep.get("w_cb", -1)) - now_w) > 1e-12:
        problems.append("STALE sleeve weight moved: %s -> %s" % (dep.get("w_cb"), now_w))
        stale = True
    if dep.get("window_last") != now_last:
        problems.append("STALE blend window moved: %s -> %s" % (dep.get("window_last"), now_last))
        stale = True
    if str(face.get("evidence_cutoff")) != str(now_last):
        problems.append("STALE evidence cutoff %s != blend window %s"
                        % (face.get("evidence_cutoff"), now_last))
        stale = True

    if not stale:
        c = face.get("cushion") or {}
        lo, hi = face.get("primary_ci90") or [None, None]
        if c.get("improved", 0) > c.get("n", 0):
            problems.append("CHECK FAILED improved %s > n %s" % (c.get("improved"), c.get("n")))
        if c.get("mean_cushion") is not None and not (lo <= c["mean_cushion"] <= hi):
            problems.append("CHECK FAILED the point estimate sits outside its own interval")
        gap = (face.get("cushion_identity") or {}).get("first_order_gap")
        if gap is None or gap > 5e-4:
            problems.append("CHECK FAILED first-order shortcut drifted from the exact "
                            "cushion by %s (> 5bp)" % gap)
        want = verdict_of(lo, hi)
        if face.get("verdict") != want:
            problems.append("CHECK FAILED verdict %s but the interval says %s"
                            % (face.get("verdict"), want))
        if face.get("verdict") == "CUSHION_SEPARABLE_POSITIVE" and not (c.get("mean_cushion") or 0) > 0:
            problems.append("CHECK FAILED positive verdict with a non-positive mean")

        stored = face.get("parent_reconciliation") or {}
        if stored.get("matched") is False:
            problems.append("CHECK FAILED our own negative-month reading never matched the parent")
        if os.path.exists(WORST_FACE):
            with open(WORST_FACE, encoding="utf-8") as fh:
                parent_neg = (json.load(fh).get("negative_months") or None)
            if parent_neg:
                now = reconcile_parent(c, parent_neg)
                if stored.get("matched") is True and not now["matched"]:
                    moved = [k for k, v in now["checks"].items() if not v["matched"]]
                    problems.append("STALE parent's negative months moved: %s" % ", ".join(moved))
                    stale = True

    return (3 if problems else 0), {"ok": not problems, "problems": problems,
                                    "verdict": face.get("verdict")}


# ------------------------------------------------------------------ selftest
def selftest():
    import datetime as _dt

    legs = []

    def leg(name, cond):
        legs.append({"leg": name, "ok": bool(cond)})

    class Ser:
        def __init__(self, values, index):
            self.values = values
            self.index = index

    def day(y, m, d=28):
        return _dt.date(y, m, d)

    def rows_of(n, etf_fn, cb_fn, w=0.30):
        """Monthly rows whose blend is the exact weighted daily path within the month
        (constant weights inside the month is the same thing as daily rebalance here)."""
        rows = []
        for i in range(n):
            e = etf_fn(i)
            c = cb_fn(i)
            rows.append({"month": "%04d-%02d" % (2020 + i // 12, 1 + i % 12),
                         "etf": e, "cb": c, "blend": w * c + (1 - w) * e})
        return rows

    # L1 month_last keeps the month's last level
    s = Ser([1.0, 1.1, 1.2], [day(2020, 1, 2), day(2020, 1, 20), day(2020, 2, 3)])
    ml = month_last(s)
    leg("L1 month_last keeps the month's last level",
        ml[(2020, 1)] == 1.1 and ml[(2020, 2)] == 1.2)

    # L2 monthly_rows reads each column off its own level
    etf = Ser([1.0, 0.90, 0.99], [day(2020, 1, 31), day(2020, 2, 29), day(2020, 3, 31)])
    cb = Ser([1.0, 1.02, 1.04], [day(2020, 1, 31), day(2020, 2, 29), day(2020, 3, 31)])
    bl = Ser([1.0, 0.9378, 1.00435], [day(2020, 1, 31), day(2020, 2, 29), day(2020, 3, 31)])
    rr = monthly_rows(etf, cb, bl)
    leg("L2 two month rows from three levels", len(rr) == 2)
    leg("L3 each column is its own level ratio",
        abs(rr[0]["etf"] + 0.10) < 1e-12 and abs(rr[0]["cb"] - 0.02) < 1e-12
        and abs(rr[0]["blend"] + 0.0622) < 1e-12)

    # L4 only negative ETF months enter the cushion
    probe = [{"month": "2020-01", "etf": -0.05, "cb": 0.01, "blend": -0.032},
             {"month": "2020-02", "etf": 0.04, "cb": -0.9, "blend": -0.242},
             {"month": "2020-03", "etf": -0.01, "cb": 0.03, "blend": 0.002}]
    c = cushion_of(probe)
    leg("L4 positive ETF months are excluded", c["n"] == 2)
    leg("L5 cushion is the exact blend-minus-etf mean",
        abs(c["mean_cushion"] - ((0.018 + 0.012) / 2.0)) < 1e-12)
    leg("L6 the count of cushioned months is printed under both names",
        c["improved"] == 2 and c["cushioned"] == c["improved"])

    # L7 the first-order shortcut is close to but not identical with the exact number
    half = cushion_from_spread(probe, 0.30)
    leg("L7 first-order w x spread", abs(half - 0.30 * ((0.06) + (0.04)) / 2.0) < 1e-12)
    conv = [{"month": "2020-01", "etf": -0.05, "cb": 0.01, "blend": -0.0321}]
    gap = abs(cushion_of(conv)["mean_cushion"] - cushion_from_spread(conv, 0.30))
    leg("L8 a level that carries intra-month interaction makes the shortcut differ",
        gap > 1e-5)

    # L9 percentile interpolation
    leg("L9 percentile interpolates", abs(percentile([0.0, 1.0, 2.0, 3.0], 50.0) - 1.5) < 1e-12)
    leg("L10 percentile endpoints", percentile([5.0], 5.0) == 5.0)

    # L11 a block as long as the sample is the sample
    steady = rows_of(12, lambda i: -0.02, lambda i: 0.001 * i)
    b_all = bootstrap(steady, 12, draws=200)
    point = cushion_of(steady)["mean_cushion"]
    leg("L11 whole-sample block reproduces the mean",
        abs(b_all["mean_of_means"] - point) < 1e-12 and abs(b_all["ci90"][0] - point) < 1e-12)
    leg("L12 few blocks flagged", b_all["too_few_blocks"] is True)

    # L13 one sign cannot be resampled into a straddling interval
    one_way = rows_of(24, lambda i: -0.02, lambda i: 0.02)
    b_one = bootstrap(one_way, 3, draws=400)
    leg("L13 a same-sign cushion stays separable",
        verdict_of(b_one["ci90"][0], b_one["ci90"][1]) == "CUSHION_SEPARABLE_POSITIVE")

    # L14 zero spread sits on zero
    zero = rows_of(24, lambda i: -0.02, lambda i: -0.02)
    b_zero = bootstrap(zero, 3, draws=400)
    leg("L14 no spread reads as not separable",
        verdict_of(b_zero["ci90"][0], b_zero["ci90"][1]) == "CUSHION_NOT_SEPARABLE")

    # L15 mixed signs straddle
    mixed = rows_of(24, lambda i: -0.02, lambda i: 0.04 if i % 2 == 0 else -0.08)
    b_mix = bootstrap(mixed, 3, draws=600)
    leg("L15 a mixed spread straddles zero",
        verdict_of(b_mix["ci90"][0], b_mix["ci90"][1]) == "CUSHION_NOT_SEPARABLE")

    # L16 seeds are reproducible
    leg("L16 same seed, same interval",
        bootstrap(mixed, 3, draws=200)["ci90"] == bootstrap(mixed, 3, draws=200)["ci90"])

    # L17 leave-one-out removes exactly one month
    lo = leave_one_out(probe)
    leg("L17 leave-one-out drops one month and keeps the rest",
        len(lo) == 2 and abs(lo[0]["mean_cushion"] - 0.012) < 1e-12)

    # L18 by_year splits on the month tag
    yr = by_year(probe)
    leg("L18 by_year counts only negative ETF months",
        yr["2020"]["n"] == 2 and abs(yr["2020"]["mean_cushion"] - 0.015) < 1e-12)

    # L19 verdict signs
    leg("L19 verdict on signs", verdict_of(0.001, 0.004) == "CUSHION_SEPARABLE_POSITIVE"
        and verdict_of(-0.004, -0.001) == "CUSHION_SEPARABLE_NEGATIVE"
        and verdict_of(-0.001, 0.004) == "CUSHION_NOT_SEPARABLE")

    # L20 the parent reconciliation is a number check, not a bytes check
    same = {"n": 32, "mean_etf": -0.014120556, "mean_blend": -0.009832538, "improved": 16}
    parent_same = {"n": 32, "mean_etf": -0.014120556, "mean_blend": -0.009832538,
                   "cushioned": 16}
    leg("L20 identical reads match", reconcile_parent(same, parent_same)["matched"] is True)
    moved = dict(parent_same)
    moved["mean_etf"] = -0.015
    rec = reconcile_parent(same, moved)
    leg("L21 one moved number breaks the match and names itself",
        rec["matched"] is False and rec["checks"]["mean_etf"]["matched"] is False
        and rec["checks"]["n"]["matched"] is True)

    # L22 a stale face says STALE, not CHECK FAILED (behavioural leg, restores itself)
    tmp = None
    if os.path.exists(FACE):
        with open(FACE, encoding="utf-8") as fh:
            tmp = json.load(fh)
        try:
            poison = json.loads(json.dumps(tmp))
            poison["inputs"]["blend_dep"]["w_cb"] = 0.99
            with open(FACE, "w", encoding="utf-8", newline="\n") as fh:
                json.dump(poison, fh, ensure_ascii=False, indent=1)
            rc, out = check()
            leg("L22 stale parent says STALE",
                rc == 3 and any("STALE" in p for p in out["problems"])
                and not any("CHECK FAILED" in p for p in out["problems"]))
        finally:
            with open(FACE, "w", encoding="utf-8", newline="\n") as fh:
                json.dump(tmp, fh, ensure_ascii=False, indent=1)
    else:
        leg("L22 stale parent says STALE (face absent: skipped)", True)

    ok = all(x["ok"] for x in legs)
    print(json.dumps({"selftest": "PASS" if ok else "FAIL",
                      "legs": len(legs), "failed": [x["leg"] for x in legs if not x["ok"]]},
                     ensure_ascii=True))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="confidence interval on the book pair's cushion")
    ap.add_argument("cmd", nargs="?", default="run",
                    choices=["run", "check", "selftest", "build"])
    ap.add_argument("--no-write", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)
    if args.cmd == "selftest":
        return selftest()
    if args.cmd == "check":
        rc, out = check()
        print(json.dumps(out, ensure_ascii=True))
        return rc
    build(write=not args.no_write, quiet=args.quiet)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

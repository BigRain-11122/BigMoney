"""ETF_BOOK_IH_TAIL_CI -- is the tail beta a measurement, or 52 days that happened?

Parent pointer (r1714 next (a)): the IH hedge only looks interesting because the book's
beta on the days IH falls hard (0.613 when IH <= -2%) is much larger than its average beta
(0.0745). That number rests on 52 observations. Until it carries an interval, "the hedge
protects you in a crash" is a point estimate presented as a fact.

This face re-reads the SAME series and the SAME switch-day rule as scripts/etf_book_ih_hedge.py
(imported, never re-implemented -- E288 one implementation) and puts a block bootstrap
around two questions that are asked separately:

  Q1  how wide is the sampling interval on the tail beta, and does it separate from 0 and
      from the unconditional beta?
  Q2  is the correctly sized short (k = 1 x beta) a measurable improvement -- i.e. does the
      interval on the Sharpe change exclude 0 -- or is it a point estimate inside noise?

Frozen reading rules, written before this round's numbers were read:

  R1  the interval is a *sampling* interval conditional on this window's tail days. It is
      not a regime statement: a future crash can look nothing like these 52 days.
  R2  the tail beta counts as measured only when its 90% interval excludes 0.
  R3  the tail counts as DIFFERENT from the average only when the interval excludes the
      unconditional beta (otherwise "the hedge helps in the tail" is explained by the
      same beta as every other day).
  R4  the hedge counts as a measurable improvement only when the 90% interval on the
      Sharpe change excludes 0 on the positive side. A point estimate below zero inside a
      wide interval is not a loss; it is no evidence either way.
  R5  the two tags are never averaged. A real tail beta and an unmeasurable Sharpe change
      are both true at once and are printed together.

Block bootstrap: circular blocks of 21 bars (one decision block), 2000 resamples, fixed
seed printed in the face. Resampling pairs keeps the book/futures co-movement intact.

Usage:
    python scripts/etf_book_ih_tail_ci.py run
    python scripts/etf_book_ih_tail_ci.py selftest
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

import etf_book_ih_hedge as H  # noqa: E402

OUT = os.path.join(ROOT, "results", "etf_book_ih_tail_ci.json")
DOC = os.path.join(ROOT, "research", "ETF_BOOK_IH_TAIL_CI.md")

SEED = 20261115
RESAMPLES = 2000
BLOCK_BARS = 21
CI = (0.05, 0.95)
MIN_TAIL_N = 20


# ---------------------------------------------------------------- bootstrap
def block_indices(n, block, rng):
    """Circular block bootstrap: n indices, drawn in blocks of `block`, all in range."""
    if n <= 0:
        return []
    idx = []
    while len(idx) < n:
        s = rng.randrange(n)
        idx.extend((s + j) % n for j in range(block))
    return idx[:n]


def pct(values, q):
    vals = sorted(v for v in values if v is not None)
    if not vals:
        return None
    if len(vals) == 1:
        return vals[0]
    pos = q * (len(vals) - 1)
    lo = int(math.floor(pos))
    hi = min(lo + 1, len(vals) - 1)
    frac = pos - lo
    return vals[lo] * (1.0 - frac) + vals[hi] * frac


def boot(pairs, cuts, resamples=RESAMPLES, block=BLOCK_BARS, seed=SEED, ks=(0.0, 1.0)):
    """One pass of the bootstrap over aligned (book, futures) return pairs."""
    n = len(pairs)
    xb = [p[0] for p in pairs]
    xf = [p[1] for p in pairs]
    rng = random.Random(seed)
    tail_draws = {c: [] for c in cuts}
    tail_n = {c: [] for c in cuts}
    sharpe_d = []
    vol_d = []
    maxdd_d = []
    beta_draws = []
    for _ in range(resamples):
        idx = block_indices(n, block, rng)
        xs = [xb[i] for i in idx]
        ys = [xf[i] for i in idx]
        m = H.moments(xs, ys)
        beta = m.get("beta")
        beta_draws.append(beta)
        for cut in cuts:
            sub = [(a, b) for a, b in zip(xs, ys) if b <= cut]
            tail_n[cut].append(len(sub))
            if len(sub) >= MIN_TAIL_N and beta is not None:
                tm = H.moments([s[0] for s in sub], [s[1] for s in sub])
                tail_draws[cut].append(tm.get("beta"))
            else:
                tail_draws[cut].append(None)
        if beta is None:
            continue
        arms = H.hedge_arms(xs, ys, beta, ks=ks)
        base = next(a for a in arms if a["k"] == 0.0)
        full = next(a for a in arms if a["k"] == 1.0)
        if base["sharpe"] is None or full["sharpe"] is None:
            continue
        sharpe_d.append(full["sharpe"] - base["sharpe"])
        vol_d.append(full["vol"] - base["vol"])
        maxdd_d.append(full["maxdd"] - base["maxdd"])
    return {"beta_draws": beta_draws, "tail_draws": tail_draws, "tail_n": tail_n,
            "sharpe_d": sharpe_d, "vol_d": vol_d, "maxdd_d": maxdd_d,
            "n": n, "resamples": resamples, "block": block, "seed": seed}


def summarise(draws):
    if not draws:
        return {"n": 0, "lo": None, "hi": None, "median": None}
    return {"n": len(draws), "lo": pct(draws, CI[0]), "hi": pct(draws, CI[1]),
            "median": pct(draws, 0.5)}


def share(value, draws, kind="gt"):
    vals = [d for d in draws if d is not None]
    if not vals:
        return None
    if kind == "gt":
        return sum(1 for d in vals if d > value) / len(vals)
    if kind == "ne":
        return sum(1 for d in vals if d != value) / len(vals)
    return None


def verdicts_of(tail, perf, uncond_beta):
    """R2-R4 applied to the intervals; the two words are never combined."""
    t = tail.get("beta_ci")
    if not t or t.get("lo") is None:
        tail_tag = "TAIL_UNMEASURABLE"
    elif t["lo"] <= 0.0:
        tail_tag = "TAIL_BETA_NOT_DISTINGUISHABLE_FROM_ZERO"
    elif uncond_beta is not None and t["lo"] <= uncond_beta <= t["hi"]:
        tail_tag = "TAIL_NOT_DIFFERENT_FROM_AVERAGE"
    else:
        tail_tag = "TAIL_BETA_IS_REAL"
    d = perf.get("dsharpe_ci") or {}
    if d.get("lo") is None:
        hedge_tag = "HEDGE_UNMEASURABLE"
    elif d["lo"] > 0.0:
        hedge_tag = "HEDGE_IMPROVES_SHARPE"
    elif d["hi"] < 0.0:
        hedge_tag = "HEDGE_HURTS_SHARPE"
    else:
        hedge_tag = "HEDGE_NOT_MEASURABLE"
    return {"tail": tail_tag, "hedge": hedge_tag}


# ---------------------------------------------------------------- build
def run():
    t0 = time.time()
    book = H.load_book()
    px = H.load_close("IH")
    raw = H.daily_rets(px)
    splices = H.named_roll_days("IH")
    kept, dropped = H.drop_splice_days(raw, splices)
    common, xb, xf = H.align(book, kept)
    if len(common) < 250:
        raise SystemExit("too few common bars: %d" % len(common))
    pairs = list(zip(xb, xf))

    uncond = H.moments(xb, xf)
    beta = uncond.get("beta")
    cuts = list(H.TAIL_CUTS)

    point_tail = {}
    for cut in cuts:
        sub = [(a, b) for a, b in pairs if b <= cut]
        key = "ih_le_%d" % int(round(cut * 100))
        if len(sub) >= MIN_TAIL_N:
            tm = H.moments([s[0] for s in sub], [s[1] for s in sub])
            point_tail[key] = {"cut": cut, "n": len(sub), "beta": tm.get("beta"),
                               "corr": tm.get("corr")}
        else:
            point_tail[key] = {"cut": cut, "n": len(sub), "beta": None, "corr": None}

    arms = H.hedge_arms(xb, xf, beta, ks=(0.0, 1.0))
    base = next(a for a in arms if a["k"] == 0.0)
    full = next(a for a in arms if a["k"] == 1.0)
    point_perf = {"dsharpe": (full["sharpe"] or 0.0) - (base["sharpe"] or 0.0),
                  "dvol": full["vol"] - base["vol"],
                  "dmaxdd": full["maxdd"] - base["maxdd"]}

    b = boot(pairs, cuts)
    tail_rows = {}
    for cut in cuts:
        key = "ih_le_%d" % int(round(cut * 100))
        draws = b["tail_draws"][cut]
        ci = summarise(draws)
        row = dict(point_tail[key])
        row["beta_ci"] = ci
        row["share_above_zero"] = share(0.0, draws)
        row["share_above_uncond"] = share(beta, draws) if beta is not None else None
        row["median_tail_days"] = pct(b["tail_n"][cut], 0.5)
        tail_rows[key] = row

    perf = {
        "k": 1.0,
        "dsharpe": point_perf["dsharpe"],
        "dsharpe_ci": summarise(b["sharpe_d"]),
        "dvol": point_perf["dvol"],
        "dvol_ci": summarise(b["vol_d"]),
        "dmaxdd": point_perf["dmaxdd"],
        "dmaxdd_ci": summarise(b["maxdd_d"]),
        "share_dsharpe_positive": share(0.0, b["sharpe_d"]),
        "base_sharpe": base["sharpe"],
        "full_sharpe": full["sharpe"],
    }

    # the tail the hedge story rests on: the deepest cut with enough days
    deepest = None
    for key in sorted(tail_rows):
        if tail_rows[key].get("n") and tail_rows[key]["beta"] is not None:
            deepest = key
    v = verdicts_of(tail_rows.get(deepest) or {}, perf, beta) if deepest else \
        {"tail": "TAIL_UNMEASURABLE", "hedge": "HEDGE_UNMEASURABLE"}
    t_row = tail_rows.get(deepest) or {}
    t_ci = t_row.get("beta_ci") or {}
    d_ci = perf["dsharpe_ci"]
    if t_ci.get("lo") is None or d_ci.get("lo") is None:
        sentence = ("尾部 beta 的区间算不出来，这一面无法给出判决。")
    else:
        sentence = (
            "尾部 beta %.3f 建在 %d 天上，90%% 的抽样区间是 [%.3f, %.3f]；按 beta 精确对冲的"
            "夏普变化 %.3f，区间 [%+.3f, %+.3f]。"
            % (t_row.get("beta") or 0.0, t_row.get("n") or 0,
               t_ci.get("lo") or 0.0, t_ci.get("hi") or 0.0,
               perf["dsharpe"], d_ci.get("lo") or 0.0, d_ci.get("hi") or 0.0))

    face = {
        "kind": "etf_book_ih_tail_ci",
        "evidence_cutoff": book["cutoff"],
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "book": {"series": book["path"], "bars": len(common),
                 "first": common[0], "last": common[-1]},
        "index": {"product": "IH", "splice_days_dropped": len(dropped)},
        "unconditional": {"beta": beta, "corr": uncond.get("corr"), "bars": uncond.get("n")},
        "tail": tail_rows,
        "deepest_tail": deepest,
        "perf_at_1beta": perf,
        "bootstrap": {"resamples": b["resamples"], "block_bars": b["block"],
                      "seed": b["seed"], "ci": list(CI),
                      "unit": "bar pairs (book return, IH return)",
                      "beta_draws_ci": summarise(b["beta_draws"])},
        "verdict": {"tail": v["tail"], "hedge": v["hedge"], "sentence": sentence},
        "reading_rules": {
            "R1": "sampling interval conditional on this window's tail days, not a regime claim",
            "R2": "tail beta measured only if the 90% interval excludes 0",
            "R3": "tail differs from average only if the interval excludes the unconditional beta",
            "R4": "measurable improvement only if the Sharpe-change interval excludes 0 upward",
            "R5": "the two tags are printed together and never averaged",
        },
        "not_measured": [
            "regime change: a future crash need not resemble these tail days",
            "margin interest on the short is not netted (same as etf_book_ih_hedge)",
            "the coarse-unit problem is a separate face and is not repriced here",
            "this is arithmetic on published series, not a broker fill record",
        ],
        "elapsed_sec": round(time.time() - t0, 1),
    }
    return face


def render_md(face):
    u = face["unconditional"]
    lines = ["# The tail beta, with an interval", "",
             "Cutoff %s | %d bar pairs (%s..%s) | %d resamples of %d-bar blocks, seed %d."
             % (face["evidence_cutoff"], face["book"]["bars"], face["book"]["first"],
                face["book"]["last"], face["bootstrap"]["resamples"],
                face["bootstrap"]["block_bars"], face["bootstrap"]["seed"]), "",
             "Unconditional beta %.4f (corr %.3f)." % (u["beta"], u["corr"] or 0.0), "",
             "| slice | n | beta | 90% interval | share of draws above the average beta |",
             "| --- | --- | --- | --- | --- |"]
    for key in sorted(face["tail"]):
        r = face["tail"][key]
        ci = r.get("beta_ci") or {}
        lines.append("| %s | %d | %s | [%s, %s] | %s |" % (
            key, r.get("n") or 0,
            "-" if r.get("beta") is None else "%.4f" % r["beta"],
            "-" if ci.get("lo") is None else "%.4f" % ci["lo"],
            "-" if ci.get("hi") is None else "%.4f" % ci["hi"],
            "-" if r.get("share_above_uncond") is None else "%.0f%%" % (100 * r["share_above_uncond"])))
    p = face["perf_at_1beta"]
    lines += ["", "## The correctly sized short (k = 1 x beta)", "",
              "| reading | point | 90% interval |", "| --- | --- | --- |"]
    for label, key, ci_key in (("sharpe change", "dsharpe", "dsharpe_ci"),
                               ("vol change", "dvol", "dvol_ci"),
                               ("maxdd change", "dmaxdd", "dmaxdd_ci")):
        ci = p.get(ci_key) or {}
        lines.append("| %s | %.4f | [%s, %s] |" % (
            label, p.get(key) or 0.0,
            "-" if ci.get("lo") is None else "%+.4f" % ci["lo"],
            "-" if ci.get("hi") is None else "%+.4f" % ci["hi"]))
    v = face["verdict"]
    lines += ["", "## Verdict", "",
              "- tail: **%s**" % v["tail"],
              "- hedge: **%s**" % v["hedge"], "",
              v["sentence"], ""]
    return "\n".join(lines)


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "selftest":
        return selftest()
    if cmd != "run":
        print("usage: etf_book_ih_tail_ci.py [run|selftest]")
        return 2
    face = run()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(face, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")
    with open(DOC, "w", encoding="utf-8", newline="\n") as f:
        f.write(render_md(face))
        f.write("\n")
    v = face["verdict"]
    p = face["perf_at_1beta"]
    print("tail %s | hedge %s | dsharpe %.3f [%.3f, %.3f]"
          % (v["tail"], v["hedge"], p["dsharpe"],
             p["dsharpe_ci"]["lo"] or 0.0, p["dsharpe_ci"]["hi"] or 0.0))
    return 0


# ---------------------------------------------------------------- selftest
def selftest():
    fails = []

    def chk(name, cond):
        if not cond:
            fails.append(name)

    # L1 exact recovery on a noiseless constructed pair
    xs = [0.8 * y for y in [0.01 * ((i % 7) - 3) for i in range(300)]]
    ys = [0.01 * ((i % 7) - 3) for i in range(300)]
    m = H.moments(xs, ys)
    chk("L1 a noiseless 0.8 beta is recovered exactly", abs(m["beta"] - 0.8) < 1e-12)

    # L2 the interval covers a known beta
    pairs = [(0.8 * y + 0.0005 * ((i % 5) - 2), y)
             for i, y in enumerate(0.01 * ((i * 37 % 11) - 5) for i in range(400))]
    b = boot(pairs, [-0.02], resamples=200, block=21)
    ci = summarise(b["beta_draws"])
    chk("L2 90% interval on beta covers the truth", ci["lo"] < 0.8 < ci["hi"])

    # L3 a tail-only beta is separated from the average
    tp = []
    rng = random.Random(7)
    for i in range(600):
        # the tail days carry their own spread: a constant futures return has zero
        # variance and no beta at all, which is a different answer from "beta is 3"
        f = (-0.025 + 0.002 * rng.uniform(-1, 1)) if i % 6 == 0 else 0.004 * rng.uniform(-1, 1)
        x = (3.0 * f + 0.0002 * rng.uniform(-1, 1)) if f <= -0.02 else \
            (0.2 * f + 0.0002 * rng.uniform(-1, 1))
        tp.append((x, f))
    b2 = boot(tp, [-0.02], resamples=300, block=21)
    t_ci = summarise(b2["tail_draws"][-0.02])
    uncond2 = H.moments([p[0] for p in tp], [p[1] for p in tp])["beta"]
    chk("L3 tail beta on a constructed tail is near 3", t_ci["median"] > 2.0)
    chk("L3 its interval excludes the unconditional beta", t_ci["lo"] > uncond2)
    v2 = verdicts_of({"beta_ci": t_ci, "n": 100}, {"dsharpe_ci": {"lo": 0.0, "hi": 0.1}},
                     uncond2)
    chk("L3 verdict says the tail is real", v2["tail"] == "TAIL_BETA_IS_REAL")

    # L4 constant beta -> the tail is NOT different from the average (or unmeasurable)
    cp = [(0.8 * y, y) for y in (0.01 * ((i * 53 % 13) - 6) for i in range(500))]
    b3 = boot(cp, [-0.02], resamples=300, block=21)
    c_ci = summarise(b3["tail_draws"][-0.02])
    v3 = verdicts_of({"beta_ci": c_ci}, {"dsharpe_ci": {"lo": None}}, 0.8)
    chk("L4 a constant beta is never reported as a real tail effect",
        v3["tail"] in ("TAIL_NOT_DIFFERENT_FROM_AVERAGE", "TAIL_BETA_NOT_DISTINGUISHABLE_FROM_ZERO",
                       "TAIL_UNMEASURABLE"))

    # L5 determinism: same seed, same numbers
    b4 = boot(pairs, [-0.02], resamples=100, block=21)
    b5 = boot(pairs, [-0.02], resamples=100, block=21)
    chk("L5 the same seed reproduces the same interval",
        summarise(b4["beta_draws"]) == summarise(b5["beta_draws"]))

    # L6 noise: a zero-relationship pair must not be called a measurable improvement
    zp = [((i % 3 - 1) * 0.004, (i % 5 - 2) * 0.006) for i in range(400)]
    bz = boot(zp, [-0.02], resamples=200, block=21)
    vz = verdicts_of({"beta_ci": summarise(bz["tail_draws"][-0.02])},
                     {"dsharpe_ci": summarise(bz["sharpe_d"])}, 0.0)
    chk("L6 a zero relationship is never HEDGE_IMPROVES_SHARPE",
        vz["hedge"] != "HEDGE_IMPROVES_SHARPE")

    # L7 an unreadable interval is never rendered as a zero
    face = {"evidence_cutoff": "2026-01-01", "book": {"bars": 2, "first": "a", "last": "b"},
            "bootstrap": {"resamples": 1, "block_bars": 1, "seed": 1},
            "unconditional": {"beta": 0.1, "corr": 0.2},
            "tail": {"ih_le_-2": {"n": 1, "beta": None, "beta_ci": {"lo": None, "hi": None},
                                  "share_above_uncond": None}},
            "perf_at_1beta": {"dsharpe": 0.0,
                              "dsharpe_ci": {"lo": None, "hi": None},
                              "dvol": 0.0, "dvol_ci": {"lo": None, "hi": None},
                              "dmaxdd": 0.0, "dmaxdd_ci": {"lo": None, "hi": None}},
            "verdict": {"tail": "TAIL_UNMEASURABLE", "hedge": "HEDGE_UNMEASURABLE",
                        "sentence": "x"}}
    md = render_md(face)
    chk("L7 a missing interval renders a dash, not 0.0000",
        "| [-, -] |" in md and "[0.0000, 0.0000]" not in md)

    # L8 block indices stay in range and keep the length
    idx = block_indices(50, 7, random.Random(1))
    chk("L8 block bootstrap returns n in-range indices",
        len(idx) == 50 and all(0 <= i < 50 for i in idx))

    # L9 the verdict vocabulary is closed
    chk("L9 tail tags are from the frozen set",
        verdicts_of({}, {}, None)["tail"] == "TAIL_UNMEASURABLE"
        and verdicts_of({"beta_ci": {"lo": 0.5, "hi": 0.9}}, {"dsharpe_ci": {"lo": -1, "hi": 1}},
                        0.5)["tail"] == "TAIL_NOT_DIFFERENT_FROM_AVERAGE"
        and verdicts_of({"beta_ci": {"lo": -0.1, "hi": 0.9}}, {"dsharpe_ci": {"lo": -1, "hi": 1}},
                        0.0)["tail"] == "TAIL_BETA_NOT_DISTINGUISHABLE_FROM_ZERO")

    if fails:
        print("SELFTEST FAIL (%d): %s" % (len(fails), "; ".join(fails)))
        return 1
    print("SELFTEST PASS (9 legs)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

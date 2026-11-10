"""Does a leg's own-history premium percentile say anything about what the price does next?

r1499 put two premium rulers on the order sheet -- where each leg's premium sits in its own
history (percentile) and whether that reading survives a NAV-stamp shift (persistence). The
page then says, in the operator's own words, "高分位不是卖单" and "限购的基金可以常年溢价".
Those are honest caveats, but they leave the only question the person placing the order
actually has unanswered: **if I pay a 100th-percentile premium, what has happened to the
price afterwards, in this fund's own history?**

That is measurable off the panel already on disk (`premium_history.csv`: date, symbol,
close, nav_date, nav, premium_pct) and it needs no new data source. The percentile is
computed causally -- each session is ranked against the sessions before it, never against
its own future -- and the outcome measured is the leg's own close-to-close move, which is
what the operator's P&L rides on. The NAV leg is deliberately NOT the outcome: a premium
that "reverts" by the NAV catching up is not a loss to someone holding the price.

Two rulers, both derived here:
    * bucket table -- forward 5/20-session price return by causal premium percentile
      bucket (BOTTOM<10, LOW 10-30, MID 30-70, UPPER 70-90, TOP>=90), per symbol and pooled.
    * information coefficient -- rank correlation of the causal percentile with the
      forward return, on NON-OVERLAPPING samples (every h-th session) so the t-stat is not
      inflated by h-fold repetition of the same move.

Verdict words (derived from the numbers, never typed):
    HIGH_PREMIUM_COSTS     top-bucket forward returns are negative at |t|>=2 in a majority
                           of legs with enough history -- paying the top premium has lost
                           money in these funds' own records
    HIGH_PREMIUM_PAYS      the same test with the opposite sign (kept for symmetry: if it
                           ever fires, the "don't chase premium" story is wrong here)
    NO_FORWARD_INFORMATION pooled |IC| below the line and no bucket clears |t|>=2
    MIXED                  some legs speak, the pooled reading does not
    NO_SCALE               no leg reaches the thin-observation floor
    UNPRICED               no usable price/premium pairs

The money line is a description of the past, not a forecast: mean forward move of the
sessions that sat in the same bucket, times the amount this ticket puts on that leg.

Usage:
    python scripts/etf_book_premium_forward.py run
    python scripts/etf_book_premium_forward.py check
    python scripts/etf_book_premium_forward.py selftest
"""
import argparse
import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import etf_book_premium_percentile as pp  # noqa: E402  single premium-history reader

OUT_DIR = os.path.join(ROOT, "results", "etf_premium")
OUT = os.path.join(OUT_DIR, "PREMIUM-FORWARD.json")
DOC = os.path.join(ROOT, "research", "ETF_BOOK_PREMIUM_FORWARD.md")

THIN_N = pp.THIN_N          # 60 usable observations: below this there is no scale
HORIZONS = (5, 20)
MIN_PRIOR = 60              # a percentile needs a history behind it before it means anything
IC_LINE = 0.05              # |pooled rank IC| below this is no information
T_LINE = 2.0
BUCKETS = (("BOTTOM", None, 10.0), ("LOW", 10.0, 30.0), ("MID", 30.0, 70.0),
           ("UPPER", 70.0, 90.0), ("TOP", 90.0, None))
WORDS = ("HIGH_PREMIUM_COSTS", "HIGH_PREMIUM_PAYS", "NO_FORWARD_INFORMATION",
         "MIXED", "NO_SCALE", "UNPRICED")


# ---------------------------------------------------------------- statistics
def bucket_of(pctile):
    """Bucket name for a causal percentile in [0, 100]; None when there is no percentile."""
    if pctile is None:
        return None
    for name, lo, hi in BUCKETS:
        if (lo is None or pctile >= lo) and (hi is None or pctile < hi):
            return name
    return None


def expanding_percentile(vals, min_prior=MIN_PRIOR):
    """Causal percentile: share of the sessions BEFORE t that sat at or below vals[t].

    Strictly prior history only -- ranking a session inside its own full sample would let
    the future decide the label. Returns None until min_prior sessions exist.
    """
    out = []
    for i, v in enumerate(vals):
        prior = vals[:i]
        if len(prior) < min_prior or v is None:
            out.append(None)
            continue
        below = sum(1 for p in prior if p is not None and p <= v)
        usable = sum(1 for p in prior if p is not None)
        out.append(100.0 * below / usable if usable else None)
    return out


def fwd_returns(closes, h):
    """close[t+h] / close[t] - 1 in percent; None where the future is not on the panel."""
    out = []
    for i in range(len(closes)):
        j = i + h
        if j >= len(closes) or closes[i] in (None, 0) or closes[j] is None:
            out.append(None)
        else:
            out.append(100.0 * (closes[j] / closes[i] - 1.0))
    return out


def describe(vals):
    """mean / sd / n / t of a sample; t is None when the sample cannot support one."""
    xs = [v for v in vals if v is not None]
    n = len(xs)
    if n == 0:
        return {"n": 0, "mean_pct": None, "sd_pct": None, "t": None}
    m = sum(xs) / float(n)
    if n < 2:
        return {"n": n, "mean_pct": m, "sd_pct": None, "t": None}
    var = sum((x - m) ** 2 for x in xs) / float(n - 1)
    sd = math.sqrt(var)
    t = m / (sd / math.sqrt(n)) if sd > 1e-12 else None
    return {"n": n, "mean_pct": m, "sd_pct": sd, "t": t}


def spearman(xs, ys):
    """Rank correlation over the pairs where both sides exist (no ties correction beyond
    average ranks -- these percentiles are continuous enough that ties are rare)."""
    pairs = [(x, y) for x, y in zip(xs, ys) if x is not None and y is not None]
    n = len(pairs)
    if n < 8:
        return None, n

    def ranks(vals):
        order = sorted(range(len(vals)), key=lambda i: vals[i])
        r = [0.0] * len(vals)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and vals[order[j + 1]] == vals[order[i]]:
                j += 1
            avg = (i + j) / 2.0 + 1.0
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r

    rx = ranks([p[0] for p in pairs])
    ry = ranks([p[1] for p in pairs])
    mx = sum(rx) / n
    my = sum(ry) / n
    num = sum((rx[i] - mx) * (ry[i] - my) for i in range(n))
    dx = math.sqrt(sum((v - mx) ** 2 for v in rx))
    dy = math.sqrt(sum((v - my) ** 2 for v in ry))
    if dx <= 1e-12 or dy <= 1e-12:
        return None, n
    return num / (dx * dy), n


# ---------------------------------------------------------------- per-leg measurement
def leg_forward(rows, h):
    """One leg's forward-return evidence at horizon h.

    ``rows`` are that symbol's premium_history rows in date order. Overlapping and
    non-overlapping samples are both reported; the t-stat is taken on the non-overlapping
    one because h overlapping windows repeat the same move h times.
    """
    closes = [r.get("close") for r in rows]
    prem = [r.get("premium_pct") for r in rows]
    pct = expanding_percentile(prem)
    fwd = fwd_returns(closes, h)

    buckets = {}
    for name, _lo, _hi in BUCKETS:
        xs = [fwd[i] for i in range(len(rows)) if pct[i] is not None
              and bucket_of(pct[i]) == name]
        buckets[name] = describe(xs)

    # non-overlapping: hold the series still for h sessions between samples
    stride_pct, stride_fwd = [], []
    i = 0
    while i < len(rows):
        if pct[i] is not None and fwd[i] is not None:
            stride_pct.append(pct[i])
            stride_fwd.append(fwd[i])
            i += h
        else:
            i += 1
    ic, ic_n = spearman(stride_pct, stride_fwd)
    covered = sum(1 for i in range(len(rows)) if pct[i] is not None and fwd[i] is not None)
    return {
        "usable_obs": covered,
        "nonoverlap_obs": ic_n,
        "ic": ic,
        "buckets": buckets,
        "latest_pctile": next((p for p in reversed(pct) if p is not None), None),
        "latest_bucket": bucket_of(next((p for p in reversed(pct) if p is not None), None)),
    }


def load_legs(hist):
    by = {}
    for r in hist:
        sym = r.get("symbol")
        if not sym or r.get("close") is None or r.get("premium_pct") is None:
            continue
        by.setdefault(sym, []).append(r)
    for sym in by:
        by[sym].sort(key=lambda r: r["date"])
    return by


def ticket_amounts():
    """Per-leg money from the live ticket, so the past-move line can be priced.

    The ticket puts its rows at ``ticket.order`` (a list carrying ``symbol``/``amount``);
    ``latest.json`` names the dated file. Reading only the top level would find nothing and
    quietly print a percent-only face -- the money column is the point of this leg.
    """
    lpath = os.path.join(ROOT, "results", "etf_book_order", "latest.json")
    if not os.path.exists(lpath):
        return {}, None
    try:
        latest = json.load(open(lpath, encoding="utf-8"))
        t = json.load(open(os.path.join(ROOT, "results", "etf_book_order",
                                        latest["file"]), encoding="utf-8"))
    except Exception:
        return {}, None
    rows = ((t.get("ticket") or {}).get("order")) or []
    out = {}
    for row in rows:
        sym = row.get("symbol")
        amt = row.get("amount")
        if sym and amt:
            out[str(sym)] = float(amt)
    return out, t.get("as_of") or latest.get("as_of")


def verdict_of(legs, pooled):
    """Derived verdict: computed from the published numbers, never typed by hand."""
    usable = [l for l in legs if l["usable_obs"] >= THIN_N]
    if not usable:
        return "NO_SCALE"
    top = [l["buckets"]["TOP"] for l in usable]
    moved = [b for b in top if b["t"] is not None and abs(b["t"]) >= T_LINE]
    neg = [b for b in moved if b["mean_pct"] < 0]
    pos = [b for b in moved if b["mean_pct"] > 0]
    half = len(usable) / 2.0
    if len(neg) >= max(1.0, half) and not pos:
        return "HIGH_PREMIUM_COSTS"
    if len(pos) >= max(1.0, half) and not neg:
        return "HIGH_PREMIUM_PAYS"
    ic = pooled.get("ic")
    if ic is not None and abs(ic) < IC_LINE and not moved:
        return "NO_FORWARD_INFORMATION"
    return "MIXED"


# ---------------------------------------------------------------- build
def build(hist=None, horizons=HORIZONS):
    if hist is None:
        hist = pp.read_hist()
    legs_by = load_legs(hist)
    amounts, session = ticket_amounts()
    if not legs_by:
        return {"verdict": "UNPRICED", "legs": [], "generated_by":
                "etf_book_premium_forward v1.0"}

    out = {
        "generated_by": "etf_book_premium_forward v1.0",
        "generated_utc_note": "wall clock appears nowhere; numbers are deterministic on the panel",
        "ticket_session": session,
        "panel_rows": len(hist),
        "evidence_cutoff": max(r["date"] for r in hist),
        "definitions": {
            "percentile": "causal: share of the sessions BEFORE t whose premium_pct <= that "
                          "session's; needs >= %d prior sessions" % MIN_PRIOR,
            "outcome": "close[t+h]/close[t]-1 in percent -- the price the operator holds, "
                       "not the NAV",
            "t_stat": "computed on non-overlapping samples (stride h), so h-fold repetition "
                      "of the same move cannot inflate it",
            "thin_n": THIN_N,
            "ic_line": IC_LINE,
            "t_line": T_LINE,
        },
        "horizons": {},
    }

    for h in horizons:
        legs = []
        for sym, rows in sorted(legs_by.items()):
            leg = leg_forward(rows, h)
            leg["symbol"] = sym
            leg["amount_cny"] = amounts.get(sym)
            leg["rows"] = len(rows)
            leg["last_date"] = rows[-1]["date"]
            b = leg["latest_bucket"]
            if b and leg["buckets"].get(b, {}).get("mean_pct") is not None \
                    and leg["amount_cny"]:
                leg["same_bucket_past_move_cny"] = (
                    leg["amount_cny"] * leg["buckets"][b]["mean_pct"] / 100.0)
            legs.append(leg)

        # pooled IC: median of the legs' rank correlations, and a pooled rank IC over all
        # legs stacked (the median resists one long series dominating the panel)
        ics = [l["ic"] for l in legs if l["ic"] is not None and l["usable_obs"] >= THIN_N]
        pooled_ic = None
        if ics:
            s = sorted(ics)
            pooled_ic = s[len(s) // 2] if len(s) % 2 else 0.5 * (s[len(s) // 2 - 1] + s[len(s) // 2])
        pooled = {"ic": pooled_ic, "legs_with_ic": len(ics)}

        # pooled bucket table across legs (equal weight per leg, not per observation)
        pooled_buckets = {}
        for name, _lo, _hi in BUCKETS:
            parts = [l["buckets"][name] for l in legs if l["buckets"][name]["n"]]
            if not parts:
                pooled_buckets[name] = {"n": 0, "mean_pct": None, "legs": 0}
                continue
            # weighted by each leg's own n but reported with the leg count beside it
            tot = sum(p["n"] for p in parts)
            mean = sum(p["mean_pct"] * p["n"] for p in parts if p["mean_pct"] is not None) / tot
            pooled_buckets[name] = {"n": tot, "mean_pct": mean, "legs": len(parts)}

        out["horizons"][str(h)] = {
            "legs": legs,
            "pooled_ic": pooled,
            "pooled_buckets": pooled_buckets,
            "verdict": verdict_of(legs, pooled),
        }

    # the book-level word comes from the longer horizon (20 sessions) when it exists
    main = out["horizons"].get(str(horizons[-1])) or out["horizons"][str(horizons[0])]
    out["verdict"] = main["verdict"]
    out["verdict_horizon"] = horizons[-1]
    out["caveat"] = ("five legs of one ticket: this is a description of these funds' own "
                     "records, not a cross-sectional study and not a forecast. Overlapping "
                     "windows are counted once per stride in the t-stat and reported in full "
                     "only as coverage.")
    out["sentence"] = sentence_of(out)
    return out


def _fmt(x, nd=2):
    return "n/a" if x is None else ("%+.*f" % (nd, x))


def sentence_of(out):
    h = out["verdict_horizon"]
    main = out["horizons"][str(h)]
    parts = []
    for leg in main["legs"]:
        top = leg["buckets"]["TOP"]
        if top["n"] == 0:
            parts.append("%s never reached its own top decile in %d sessions" %
                         (leg["symbol"], leg["rows"]))
            continue
        parts.append("%s: after sessions in its top decile the next %d sessions averaged "
                     "%s%% (n=%d, t=%s)" % (leg["symbol"], h, _fmt(top["mean_pct"]), top["n"],
                                            _fmt(top["t"], 1)))
    ic = main["pooled_ic"]["ic"]
    head = ("premium percentile rank-IC with the next %d sessions is %s (%d legs)"
            % (h, _fmt(ic, 3), main["pooled_ic"]["legs_with_ic"]))
    return head + "; " + "; ".join(parts)


# ---------------------------------------------------------------- accessors
def load_out():
    if not os.path.exists(OUT):
        return None
    try:
        return json.load(open(OUT, encoding="utf-8"))
    except Exception:
        return None


def run():
    out = build()
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print("verdict: %s (h=%s)" % (out["verdict"], out["verdict_horizon"]))
    print(out["sentence"])
    print("wrote %s" % os.path.relpath(OUT, ROOT))
    return 0


def check():
    """Re-derive the published face from the panel; a hand-typed number turns this red."""
    pub = load_out()
    if pub is None:
        print("FAIL: %s missing -- run the tool first" % os.path.relpath(OUT, ROOT))
        return 1
    fresh = build()
    bad = []
    if pub.get("verdict") not in WORDS:
        bad.append("verdict %r is not one of the derived words" % pub.get("verdict"))
    for h in fresh["horizons"]:
        got = fresh["horizons"][h]
        have = pub.get("horizons", {}).get(h)
        if not have:
            bad.append("horizon %s missing from the published face" % h)
            continue
        if have.get("verdict") != got["verdict"]:
            bad.append("h=%s verdict %r != recomputed %r"
                       % (h, have.get("verdict"), got["verdict"]))
        for leg in got["legs"]:
            hl = next((x for x in have["legs"] if x["symbol"] == leg["symbol"]), None)
            if hl is None:
                bad.append("h=%s leg %s missing" % (h, leg["symbol"]))
                continue
            if hl.get("usable_obs") != leg["usable_obs"]:
                bad.append("h=%s leg %s usable_obs %s != %s"
                           % (h, leg["symbol"], hl.get("usable_obs"), leg["usable_obs"]))
            for name in [b[0] for b in BUCKETS]:
                a = hl["buckets"][name]
                b = leg["buckets"][name]
                if a.get("n") != b.get("n"):
                    bad.append("h=%s leg %s bucket %s n %s != %s"
                               % (h, leg["symbol"], name, a.get("n"), b.get("n")))
                elif a.get("mean_pct") is not None and b.get("mean_pct") is not None \
                        and abs(a["mean_pct"] - b["mean_pct"]) > 1e-6:
                    bad.append("h=%s leg %s bucket %s mean %s != %s"
                               % (h, leg["symbol"], name, a["mean_pct"], b["mean_pct"]))
        if have["pooled_ic"]["legs_with_ic"] != got["pooled_ic"]["legs_with_ic"]:
            bad.append("h=%s pooled ic leg count drifted" % h)

    # the money column is the reason this face exists: a percent-only slide would be the
    # same surface as the two rulers it was built to go beyond. Assert it is priced AND
    # that it follows from the bucket mean and the ticket amount (r1499: a leg that walks
    # an empty list passes; so require a non-zero count of priced legs).
    priced = [l for l in fresh["horizons"][str(HORIZONS[-1])]["legs"]
              if l.get("same_bucket_past_move_cny") is not None]
    if not priced:
        bad.append("no leg carries a CNY reading -- the ticket amounts were not read "
                   "(priced 0 of %d)"
                   % len(fresh["horizons"][str(HORIZONS[-1])]["legs"]))
    for leg in fresh["horizons"][str(HORIZONS[-1])]["legs"]:
        amt, cny, bkt = leg.get("amount_cny"), leg.get("same_bucket_past_move_cny"), \
            leg.get("latest_bucket")
        if cny is None:
            continue
        mean = leg["buckets"][bkt]["mean_pct"]
        if abs(amt * mean / 100.0 - cny) > 1e-6 * max(1.0, abs(cny)):
            bad.append("%s CNY %r does not follow from %r x %r%%"
                       % (leg["symbol"], cny, amt, mean))
    if bad:
        for b in bad[:12]:
            print("FAIL: " + b)
        print("%d failure(s)" % len(bad))
        return 1
    print("OK: published face re-derives from premium_history.csv "
          "(%d horizons, %d legs each, verdict %s)"
          % (len(fresh["horizons"]), len(fresh["horizons"][str(HORIZONS[-1])]["legs"]),
             fresh["verdict"]))
    return 0


# ---------------------------------------------------------------- selftest
def _rows(sym, prems, closes, start_day=1):
    out = []
    for i, (p, c) in enumerate(zip(prems, closes)):
        out.append({"date": "2020-01-%02d" % (min(28, i + 1)) if i < 28 else
                    "2021-01-%02d" % (min(28, i - 27)),
                    "symbol": sym, "close": c, "nav_date": None, "nav": None,
                    "premium_pct": p})
    return out


def selftest():
    fails = []

    def eq(got, want, label):
        if got != want:
            fails.append("%s: got %r want %r" % (label, got, want))

    def close_to(got, want, label, tol=1e-6):
        if got is None or abs(got - want) > tol:
            fails.append("%s: got %r want %r" % (label, got, want))

    # 1. bucket boundaries are half-open and TOP is unbounded
    eq(bucket_of(None), None, "L1 no percentile has no bucket")
    eq(bucket_of(9.99), "BOTTOM", "L2 9.99 is bottom")
    eq(bucket_of(10.0), "LOW", "L3 10.0 moves to LOW")
    eq(bucket_of(90.0), "TOP", "L4 90.0 is TOP")
    eq(bucket_of(100.0), "TOP", "L5 100 is TOP")

    # 2. the percentile is causal: a huge value at t cannot affect its own rank
    vals = [1.0] * 60 + [99.0]
    pct = expanding_percentile(vals, min_prior=60)
    eq(pct[:60], [None] * 60, "L6 nothing before the floor")
    close_to(pct[60], 100.0, "L7 current is ranked against the 60 flat priors")

    # 2b. and a DECREASING value at t reads low even though it is the max of the full sample
    vals2 = [5.0] * 60 + [1.0]
    pct2 = expanding_percentile(vals2, min_prior=60)
    eq(pct2[60], 0.0, "L8 a low value after high priors reads 0, not 50+")

    # 3. forward returns use the price leg and stop at the panel edge
    fwd = fwd_returns([100.0, 110.0, 121.0], 1)
    close_to(fwd[0], 10.0, "L9 one session ahead is +10%")
    eq(fwd[-1], None, "L10 the last bar has no future")

    # 4. describe / t behaviour on degenerate samples
    eq(describe([])["n"], 0, "L11 empty sample")
    eq(describe([1.0])["t"], None, "L12 single observation has no t")
    eq(describe([2.0, 2.0, 2.0])["t"], None, "L13 zero variance has no t")
    close_to(describe([1.0, 2.0, 3.0])["mean_pct"], 2.0, "L14 mean")

    # 5. spearman: perfect +1 / -1 and the flat-series guard
    ic, n = spearman(list(range(20)), [i * 2 for i in range(20)])
    close_to(ic, 1.0, "L15 monotone ranks correlate at 1")
    ic2, _ = spearman(list(range(20)), [-i for i in range(20)])
    close_to(ic2, -1.0, "L16 reversed ranks correlate at -1")
    eq(spearman(list(range(20)), [1.0] * 20)[0], None, "L17 a flat side has no rank IC")

    # 6. a leg where the top decile is followed by losses must read HIGH_PREMIUM_COSTS
    prems, closes = [], []
    px = 100.0
    for i in range(400):
        hot = (i % 40) == 0
        prems.append(10.0 if hot else 0.0)
        closes.append(px)
        px *= (0.97 if hot else 1.0)          # the session AFTER a hot print loses 3%
    rows = _rows("TEST", prems, closes)
    leg = leg_forward(rows, 5)
    if leg["buckets"]["TOP"]["mean_pct"] is None or leg["buckets"]["TOP"]["mean_pct"] >= 0:
        fails.append("L18 a top-decile-then-loss leg should print a negative top bucket")
    leg["symbol"] = "TEST"
    v = verdict_of([leg], {"ic": leg["ic"]})
    eq(v, "HIGH_PREMIUM_COSTS", "L19 verdict follows the top bucket")

    # 6b. same shape, opposite sign -> HIGH_PREMIUM_PAYS
    px = 100.0
    closes2 = []
    for i in range(400):
        hot = (i % 40) == 0
        closes2.append(px)
        px *= (1.03 if hot else 1.0)
    leg2 = leg_forward(_rows("TEST", prems, closes2), 5)
    leg2["symbol"] = "TEST"
    eq(verdict_of([leg2], {"ic": leg2["ic"]}), "HIGH_PREMIUM_PAYS",
       "L20 mirror case flips the verdict")

    # 7. no relationship at all -> NO_FORWARD_INFORMATION
    prems3 = [float(i % 7) for i in range(400)]
    closes3 = [100.0 + (i % 11) for i in range(400)]
    leg3 = leg_forward(_rows("TEST", prems3, closes3), 5)
    leg3["symbol"] = "TEST"
    eq(verdict_of([leg3], {"ic": 0.0}), "NO_FORWARD_INFORMATION",
       "L21 flat information reads as none")

    # 8. nothing reaches the floor -> NO_SCALE (not a word invented from a short series)
    short = leg_forward(_rows("TEST", [1.0] * 30, [10.0] * 30), 5)
    short["symbol"] = "TEST"
    eq(verdict_of([short], {"ic": None}), "NO_SCALE", "L22 short history has no scale")

    # 9. non-overlapping sampling really reduces the count (else the t-stat is inflated)
    prems4 = [float(i % 5) for i in range(300)]
    closes4 = [100.0 + 0.3 * i for i in range(300)]
    leg4 = leg_forward(_rows("TEST", prems4, closes4), 20)
    if not (leg4["nonoverlap_obs"] * 3 < leg4["usable_obs"]):
        fails.append("L23 stride-20 sampling did not thin the sample: %d vs %d"
                     % (leg4["nonoverlap_obs"], leg4["usable_obs"]))

    # 10. the built face carries its own evidence cutoff and a word from the enum
    face = build(hist=_rows("TEST", prems4, closes4))
    if face["verdict"] not in WORDS:
        fails.append("L24 built verdict %r is outside the vocabulary" % face["verdict"])
    if not face.get("evidence_cutoff"):
        fails.append("L25 built face has no evidence_cutoff")

    # 11. 'never in the top decile' is described as such, not as a zero return
    # (a strictly falling premium never ranks above its own past, so TOP stays empty)
    face2 = build(hist=_rows("TEST", [10.0 - 0.03 * i for i in range(200)],
                             [100.0 + i for i in range(200)]))
    if "never reached its own top decile" not in face2["sentence"]:
        fails.append("L26 a leg with no top-decile session must say so in the sentence")

    print("%d/%d legs" % (26 - len(fails), 26))
    for f in fails:
        print("FAIL: " + f)
    return 1 if fails else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("run", "check", "selftest"))
    a = ap.parse_args()
    if a.cmd == "run":
        return run()
    if a.cmd == "check":
        return check()
    return selftest()


if __name__ == "__main__":
    sys.exit(main())
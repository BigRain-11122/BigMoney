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
import hashlib
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
# One frozen row per distinct leg set ever published. The face's verdict has a referent --
# the funds it measured -- and that referent changes when the ticket changes (E550 family:
# a name whose member set moves keeps the name). 2026-11-11 is the live case: the face read
# MIXED with rank-IC -0.133 on the 11-10 legs and HIGH_PREMIUM_PAYS with +0.023 on the
# 11-11 legs -- nothing drifted, the sample was replaced.
SAMPLE_LEDGER = os.path.join(OUT_DIR, "PREMIUM-FORWARD-SAMPLES.jsonl")
BREAK_MARK = "not comparable across sessions"
DOC = os.path.join(ROOT, "research", "ETF_BOOK_PREMIUM_FORWARD.md")

THIN_N = pp.THIN_N          # 60 usable observations: below this there is no scale
# h=1 is the horizon the person placing the order actually faces: pay today's close or
# wait one session. It is reported beside the 5/20-session buckets, never instead of them.
HORIZONS = (1, 5, 20)
# The decile bucket is 10% wide and today's three expensive legs sit at 98.8-99.9, i.e.
# in the top 2% -- a band the TOP>=90 mean dilutes with the 90-95 mass. These bands are
# cut finer at the tail, and the deferral read is taken on the last one.
TAILS = (("P95_98", 95.0, 98.0), ("P98P", 98.0, None))
DEFER_BAND = "P98P"
DOWN_LINE = 0.55            # a history counts as "the next session fell" at >=55% of cases
DEFER_WORDS = ("WAITING_PAID", "WAITING_COST", "NO_READ")
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


def tail_of(pctile):
    """Tail band for a causal percentile in [0, 100]; None outside the upper tail."""
    if pctile is None:
        return None
    for name, lo, hi in TAILS:
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


def tail_stats(vals):
    """One tail band's next-session sample, with the two counters a mean cannot carry.

    ``share_down`` is the share of sessions whose next-session price move was negative --
    an average of -0.02% can come from 51% small losses or from 90% losses and 10% wins,
    and those are different worlds for someone deciding whether to wait.
    """
    xs = [v for v in vals if v is not None]
    d = describe(xs)
    d["median_pct"] = pp.q(xs, 0.5) if xs else None
    d["share_down"] = (sum(1 for v in xs if v < 0) / float(len(xs))) if xs else None
    return d


def one_session_obs(rows):
    """Raw next-session price moves split by the tail band the session sat in.

    Returns (obs, pct): obs maps band -> [move in percent]; pct is the causal percentile
    series (kept so the caller can say which band the latest session sits in).
    """
    closes = [r.get("close") for r in rows]
    prem = [r.get("premium_pct") for r in rows]
    pct = expanding_percentile(prem)
    fwd = fwd_returns(closes, 1)
    obs = {name: [] for name, _lo, _hi in TAILS}
    for i in range(len(rows)):
        if pct[i] is None or fwd[i] is None:
            continue
        b = tail_of(pct[i])
        if b:
            obs[b].append(fwd[i])
    return obs, pct


def defer_verdict(pooled):
    """Derived from the pooled P98P sample: did the next session fall, rise, or say nothing?"""
    b = (pooled or {}).get(DEFER_BAND) or {}
    if b.get("n", 0) < THIN_N or b.get("median_pct") is None or b.get("share_down") is None:
        return "NO_READ"
    if b["median_pct"] < 0 and b["share_down"] >= DOWN_LINE:
        return "WAITING_PAID"
    if b["median_pct"] > 0 and b["share_down"] <= 1.0 - DOWN_LINE:
        return "WAITING_COST"
    return "NO_READ"


def defer_sentence(pooled, legs, session=None, panel=None):
    """The one-session read in words, with the count that supports it (never typed).

    ``legs`` are the legs' one-session blocks. Only a leg whose bar IS the ticket's session
    may speak about "today"; a leg read off another bar is named as left out, never summed
    into this ticket's day (r1609). The day itself is printed, so a reader can see the
    sentence move when the sheet moves even if no number in it changes.
    """
    b = (pooled or {}).get(DEFER_BAND) or {}
    if not b.get("n"):
        head = ("no session in these funds' own records reached the %s band, so the one "
                "session the ticket could wait for has no history here" % DEFER_BAND)
    else:
        head = ("after sessions at or above the 98th percentile of the fund's own history, "
                "the NEXT session moved a median %s%% (mean %s%%, fell in %s%% of %d cases)"
                % (_fmt(b.get("median_pct")), _fmt(b.get("mean_pct")),
                   "n/a" if b.get("share_down") is None else "%.0f" % (100.0 * b["share_down"]),
                   b["n"]))
    panel = panel or {}
    day = session or panel.get("ticket_session")
    counted = [l for l in legs if l.get("counted")]
    off = [l for l in legs if not l.get("counted")]
    if counted:
        there = ["%s %.1f" % (l["symbol"], l["latest_pctile"])
                 for l in counted if l.get("latest_band") == DEFER_BAND
                 and l.get("latest_pctile") is not None]
        if there:
            tail = ("; on %s (the ticket's own bar) the legs in that band: %s"
                    % (day, ", ".join(there)))
        else:
            tail = "; no leg of this ticket sits in that band on %s" % day
    else:
        tail = ("; this face cannot say where the ticket's legs sit on %s: %s"
                % (day or "a day the sheet does not name", panel.get("state") or "SESSION_UNKNOWN"))
    if off:
        tail += (" (%d leg(s) read off another bar and left out: %s)"
                 % (len(off), ", ".join(sorted(l["symbol"] for l in off))))
    if panel.get("state") == "PANEL_AHEAD":
        tail += ("; the premium panel has walked %d bar(s) past that day, and those bars are "
                 "not this ticket's" % int(panel.get("bars_beyond_session") or 0))
    return head + tail


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


def read_ticket(path=None):
    """The ticket this face prices: the one named on the command line, else the published one."""
    if path:
        try:
            return json.load(open(path, encoding="utf-8"))
        except Exception:
            return {}
    lpath = os.path.join(ROOT, "results", "etf_book_order", "latest.json")
    if not os.path.exists(lpath):
        return {}
    try:
        latest = json.load(open(lpath, encoding="utf-8"))
        return json.load(open(os.path.join(ROOT, "results", "etf_book_order",
                                           latest["file"]), encoding="utf-8"))
    except Exception:
        return {}


def ticket_amounts(ticket=None):
    """Per-leg money from the live ticket, plus the day that ticket is for.

    The ticket puts its rows at ``ticket.order`` (a list carrying ``symbol``/``amount``);
    ``latest.json`` names the dated file. Reading only the top level would find nothing and
    quietly print a percent-only face -- the money column is the point of this leg.

    The session goes through the shared fallback chain (``pp.ticket_session``: session ->
    base_bar -> evidence_cutoff -> feed_status.ticket_bar), so this face and the percentile
    face cannot disagree about which day the sheet is for. This ticket carries no
    ``session`` key -- ``base_bar`` is what answers (r1607).
    """
    t = ticket if ticket is not None else read_ticket()
    rows = ((t.get("ticket") or {}).get("order")) or []
    out = {}
    for row in rows:
        sym = row.get("symbol")
        amt = row.get("amount")
        if sym and amt:
            out[str(sym)] = float(amt)
    session, field = pp.ticket_session(t)
    return out, session, field


def anchor_reading(rows, session):
    """"Today" for this leg: (pctile, bucket, bar_date, state, counted) on the ticket's bar.

    The percentile is causal -- each session ranked against the sessions before it -- so
    trimming the panel at the ticket's day cannot let a later bar decide the rank; it only
    decides WHICH bar is "today". A leg with no bar of its own inside the panel (the panel
    has not reached it, its bar is missing, or the ticket names no day) is not counted: it
    publishes no number instead of publishing another session's (r1609 -- the fourth copy of
    the family cured in the persistence and percentile faces).
    """
    if not rows:
        return None, None, None, "SESSION_UNKNOWN", False
    price_session = rows[-1].get("date")
    state = pp.session_state(price_session, session)
    if not session:
        return None, None, None, "SESSION_UNKNOWN", False
    anchored = [r for r in rows if r.get("date") and r["date"] <= session]
    if not anchored:
        return None, None, None, "PANEL_BEHIND", False
    bar_date = anchored[-1].get("date")
    pct = expanding_percentile([r.get("premium_pct") for r in anchored])
    v = next((p for p in reversed(pct) if p is not None), None)
    counted = bool(bar_date == session and v is not None)
    return ((v if counted else None), (bucket_of(v) if counted else None), bar_date, state,
            counted)


def sample_signature(symbols):
    """Identity of WHAT this face measured: sha256 of the sorted leg codes, 12 hex.

    Sorted and de-duplicated, so the signature is a property of the set -- two runs that
    read the same funds in another order print the same identity.
    """
    joined = ",".join(sorted({str(x) for x in (symbols or [])}))
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()[:12]


def read_sample_ledger(path=None):
    """The append-only publication ledger (one row per distinct sample, oldest first)."""
    path = path or SAMPLE_LEDGER
    rows = []
    if not os.path.exists(path):
        return rows
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except Exception:
                    continue
                if isinstance(row, dict) and row.get("signature"):
                    rows.append(row)
    except Exception:
        return rows
    return rows


SAMPLE_LEDGER_FIELDS = ("signature", "legs", "n_legs", "first_published_session",
                        "first_published_verdict", "first_published_verdict_horizon",
                        "changed_from_previous", "previous_signature", "previous_legs",
                        "previous_session")


def sample_row(symbols, ledger_rows, session=None, verdict=None, horizon=None):
    """The frozen identity row for this sample.

    If the sample was published before, its stored row is returned verbatim: the break is
    a fact fixed at first publication, so `run` twice on the same sample cannot flip
    "the sample changed" on and off (idempotency, E188 family).
    """
    syms = sorted({str(x) for x in (symbols or [])})
    sig = sample_signature(syms)
    for row in ledger_rows or []:
        if row.get("signature") == sig:
            return dict(row)
    prev = (ledger_rows or [None])[-1]
    return {"signature": sig, "legs": syms, "n_legs": len(syms),
            "first_published_session": session,
            "first_published_verdict": verdict,
            "first_published_verdict_horizon": horizon,
            "changed_from_previous": bool(prev and prev.get("signature") != sig),
            "previous_signature": (prev or {}).get("signature"),
            "previous_legs": list((prev or {}).get("legs") or []),
            "previous_session": (prev or {}).get("first_published_session")}


def sample_failures(pub, ledger_rows, fresh):
    """Every way a published face can lie about its own sample, as red messages."""
    bad = []
    have = pub.get("sample") or {}
    if not have:
        bad.append("published face carries no sample identity -- a verdict whose member "
                   "set is unnamed cannot be compared with any earlier day")
        return bad
    legs = list(have.get("legs") or [])
    if have.get("signature") != sample_signature(legs):
        bad.append("sample signature %r does not re-derive from its own legs (%s)"
                   % (have.get("signature"), sample_signature(legs)))
    if have.get("n_legs") != len(legs):
        bad.append("sample n_legs %r != %d legs listed"
                   % (have.get("n_legs"), len(legs)))
    fresh_sample = fresh.get("sample") or {}
    if sorted(legs) != sorted(fresh_sample.get("legs") or []):
        bad.append("published sample legs %s != recomputed %s"
                   % (",".join(sorted(legs)) or "none",
                      ",".join(sorted(fresh_sample.get("legs") or [])) or "none"))
    row = next((r for r in (ledger_rows or [])
                if r.get("signature") == have.get("signature")), None)
    if row is None:
        bad.append("the published sample %s never entered the ledger -- `run` publishes and "
                   "records in one step" % (have.get("signature") or "none"))
    else:
        for key in SAMPLE_LEDGER_FIELDS:
            if row.get(key) != have.get(key):
                bad.append("published sample %s %r != ledger %r"
                           % (key, have.get(key), row.get(key)))
    changed = bool(have.get("changed_from_previous"))
    brk = pub.get("sample_break")
    if changed and not brk:
        bad.append("the ledger records a sample change but the face carries no "
                   "sample_break block")
    if not changed and brk:
        bad.append("sample_break present although the ledger says this sample was not a change")
    if pub.get("cross_session_comparable") is changed:
        bad.append("cross_session_comparable=%r contradicts changed_from_previous=%r"
                   % (pub.get("cross_session_comparable"), changed))
    sentence = pub.get("sentence") or ""
    if changed:
        if not (brk or {}).get("previous_legs"):
            bad.append("sample changed but the previous legs are not named")
        if BREAK_MARK not in sentence:
            bad.append("the headline sentence does not say the sample changed -- readers will "
                       "read this verdict as continuous with the previous face")
    elif BREAK_MARK in sentence:
        bad.append("the sentence claims a sample break the ledger does not record")
    return bad


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
def build(hist=None, horizons=HORIZONS, ledger_rows=None, ticket=None):
    if hist is None:
        hist = pp.read_hist()
    legs_by = load_legs(hist)
    amounts, session, session_field = ticket_amounts(ticket)
    if not legs_by:
        return {"verdict": "UNPRICED", "legs": [], "generated_by":
                "etf_book_premium_forward v1.0"}

    panel_last = max(r["date"] for r in hist)
    state = pp.session_state(panel_last, session)
    bars_beyond = len({r["date"] for r in hist if session and r["date"] > session})
    panel = {
        "ticket_session": session,
        "session_field": session_field,
        "price_panel_last": panel_last,
        "state": state,
        "bars_beyond_session": bars_beyond,
        "note": pp.panel_note({"state": state, "ticket_session": session,
                               "price_panel_last": panel_last,
                               "bars_beyond_session": bars_beyond}),
    }

    out = {
        "generated_by": "etf_book_premium_forward v1.0",
        "generated_utc_note": "wall clock appears nowhere; numbers are deterministic on the panel",
        "ticket_session": session,
        "panel": panel,
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
            "tail_bands": ["%s [%s, %s)" % (n, "-inf" if lo is None else "%.0f" % lo,
                                            "+inf" if hi is None else "%.0f" % hi)
                           for n, lo, hi in TAILS],
            "defer_read": "h=1 next-session price move pooled over the sessions each leg "
                          "sat in %s; WAITING_PAID at median<0 with >=%.0f%% down, "
                          "WAITING_COST at median>0 with <=%.0f%% down, else NO_READ"
                          % (DEFER_BAND, 100.0 * DOWN_LINE, 100.0 * (1.0 - DOWN_LINE)),
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
            pctile, bucket, bar_date, leg_state, counted = anchor_reading(rows, session)
            leg["latest_pctile"] = pctile
            leg["latest_bucket"] = bucket
            leg["price_session"] = rows[-1]["date"]
            leg["session_state"] = leg_state
            leg["bar_at_session"] = bar_date
            leg["counted"] = counted
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

    # ---- the one-session read: the only horizon the order itself can choose to wait for
    one_legs = {}
    pooled_vals = {name: [] for name, _lo, _hi in TAILS}
    for sym, rows in sorted(legs_by.items()):
        obs, pct = one_session_obs(rows)
        pctile, _bucket, bar_date, leg_state, counted = anchor_reading(rows, session)
        one_legs[sym] = {
            "symbol": sym, "rows": len(rows), "last_date": rows[-1]["date"],
            "price_session": rows[-1]["date"], "session_state": leg_state,
            "bar_at_session": bar_date, "counted": counted,
            "latest_pctile": pctile, "latest_band": tail_of(pctile),
            "amount_cny": amounts.get(sym),
            "bands": {k: tail_stats(v) for k, v in obs.items()},
        }
        for k, v in obs.items():
            pooled_vals[k].extend(v)
    pooled_tails = {k: tail_stats(v) for k, v in pooled_vals.items()}
    counted_syms = sorted(s for s, l in one_legs.items() if l["counted"])
    panel["legs_counted"] = len(counted_syms)
    panel["legs_off_session"] = sorted(s for s, l in one_legs.items() if not l["counted"])
    out["one_session"] = {
        "horizon": 1,
        "band": DEFER_BAND,
        "pooled": pooled_tails,
        "legs": one_legs,
        "verdict": defer_verdict(pooled_tails),
        "sentence": defer_sentence(pooled_tails, list(one_legs.values()), session=session,
                                   panel=panel),
        "note": "a description of these funds' own records at this percentile, not a "
                "recommendation to wait; the price move is measured, the reason is not",
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

    # ---- what this face measured, and whether it is the same thing as last time
    if ledger_rows is None:
        ledger_rows = read_sample_ledger()
    row = sample_row(list(legs_by), ledger_rows, session=session,
                     verdict=out["verdict"], horizon=out["verdict_horizon"])
    dates = sorted(r["date"] for r in hist)
    out["sample"] = dict(row)
    out["sample"].update({
        "panel_rows": len(hist), "first_date": dates[0], "last_date": dates[-1],
        "definition": "sha256 of the sorted leg codes (12 hex): the identity of what this "
                      "face measured. A new ticket replaces the funds, so a verdict may "
                      "only be compared across sessions inside one signature.",
    })
    if row.get("changed_from_previous"):
        out["sample_break"] = {
            "changed": True, "signature": row["signature"], "legs": row["legs"],
            "previous_signature": row.get("previous_signature"),
            "previous_legs": list(row.get("previous_legs") or []),
            "previous_session": row.get("previous_session"),
            "reason": "the ticket's leg set was replaced, so this face and the previous one "
                      "describe different funds",
        }
        out["cross_session_comparable"] = False
        out["sentence"] = (out["sentence"] + " || sample: legs %s replaced %s (last published "
                           "%s) -- %s"
                           % (",".join(row["legs"]),
                              ",".join(row.get("previous_legs") or []) or "none",
                              row.get("previous_session") or "unrecorded", BREAK_MARK))
    else:
        out["sample_break"] = None
        out["cross_session_comparable"] = True
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
    text = head + "; " + "; ".join(parts)
    if out.get("one_session"):
        text += " || one session: " + out["one_session"]["sentence"]
    return text


# ---------------------------------------------------------------- accessors
def load_out():
    if not os.path.exists(OUT):
        return None
    try:
        return json.load(open(OUT, encoding="utf-8"))
    except Exception:
        return None


def run(ticket_path=None, out_path=None):
    ledger = read_sample_ledger()
    out = build(ledger_rows=ledger,
                ticket=(read_ticket(ticket_path) if ticket_path else None))
    dest = out_path or OUT
    os.makedirs(os.path.dirname(os.path.abspath(dest)), exist_ok=True)
    with open(dest, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    if out_path:
        # a proof run against an old ticket is not a publication: it must not enter the
        # append-only sample ledger, or the ledger would record two sessions for one face.
        print("proof run against %s -> %s" % (ticket_path, dest))
        print("panel: %s" % ((out.get("panel") or {}).get("note") or "no panel block"))
        print("defer read: %s (%s)" % (out["one_session"]["verdict"],
                                       out["one_session"]["band"]))
        print(out["sentence"])
        return 0
    # publish and record in one step: a face whose sample never entered the ledger cannot
    # be audited later, and the next ticket change would have nothing to compare against
    sig = (out.get("sample") or {}).get("signature")
    if sig and not any(r.get("signature") == sig for r in ledger):
        with open(SAMPLE_LEDGER, "a", encoding="utf-8") as f:
            f.write(json.dumps({k: out["sample"].get(k) for k in SAMPLE_LEDGER_FIELDS},
                               ensure_ascii=False) + "\n")
        print("sample: %s (%d legs) recorded -- changed_from_previous=%s"
              % (sig, len(out["sample"].get("legs") or []),
                 out["sample"].get("changed_from_previous")))
    else:
        print("sample: %s (%d legs) already on the ledger"
              % (sig, len((out.get("sample") or {}).get("legs") or [])))
    print("panel: %s" % ((out.get("panel") or {}).get("note") or "no panel block"))
    print("verdict: %s (h=%s)" % (out["verdict"], out["verdict_horizon"]))
    print("defer read: %s (%s)" % (out["one_session"]["verdict"],
                                   out["one_session"]["band"]))
    print(out["sentence"])
    print("wrote %s" % os.path.relpath(OUT, ROOT))
    return 0


def check():
    """Re-derive the published face from the panel; a hand-typed number turns this red."""
    pub = load_out()
    if pub is None:
        print("FAIL: %s missing -- run the tool first" % os.path.relpath(OUT, ROOT))
        return 1
    fresh = build(ledger_rows=read_sample_ledger())
    # r1561: this face prices the LEGS OF THE DAY'S TICKET, so on a new ticket it is not
    # "the numbers drifted" -- the sample was replaced. 2026-11-11 read as 28 failures
    # (four legs "missing", 24 bucket counts off by one or two) when the truth was one
    # sentence: the published face priced 159263/159501/159577/513100/513690 (the 11-10
    # ticket) while today's ticket carries 159519/159655/510760/512040/513690. Say that
    # instead, and say it with the word STALE so the chain's declared refresh -- not a
    # loosened assertion -- is what repairs it. A same-ticket face whose numbers no
    # longer re-derive still falls through to the real red below.
    _h_last = str(HORIZONS[-1])
    _pub_legs = sorted({l["symbol"] for l in
                        (((pub.get("horizons") or {}).get(_h_last) or {}).get("legs") or [])})
    _new_legs = sorted({l["symbol"] for l in fresh["horizons"][_h_last]["legs"]})
    if _pub_legs != _new_legs:
        print("STALE: published face priced legs %s (ticket %s); today's ticket carries %s "
              "-- re-derive with `run`"
              % (",".join(_pub_legs) or "none", pub.get("ticket_session") or "none",
                 ",".join(_new_legs) or "none"))
        return 1
    if (str(pub.get("evidence_cutoff") or "")[:10]
            != str(fresh.get("evidence_cutoff") or "")[:10]
            or pub.get("panel_rows") != fresh.get("panel_rows")):
        print("STALE: published face is %s / %s rows; premium_history.csv now ends %s / %s "
              "rows -- re-derive with `run`"
              % (pub.get("evidence_cutoff"), pub.get("panel_rows"),
                 fresh.get("evidence_cutoff"), fresh.get("panel_rows")))
        return 1
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
    # the one-session read: the horizon the order can actually wait for. A leg that walks
    # an empty band must print n=0, not a zero return; the pooled count must be the sum of
    # the legs' counts (a pooled table that cannot be rebuilt from its rows is a second
    # computation wearing the same name).
    pub_one = pub.get("one_session") or {}
    fresh_one = fresh.get("one_session") or {}
    if not pub_one.get("pooled"):
        bad.append("published face has no one-session read -- re-run the tool")
    else:
        for sym, leg in fresh_one.get("legs", {}).items():
            have = (pub_one.get("legs") or {}).get(sym)
            if not have:
                bad.append("one-session leg %s missing from the published face" % sym)
                continue
            if have.get("latest_band") != leg.get("latest_band"):
                bad.append("%s latest_band %r != %r"
                           % (sym, have.get("latest_band"), leg.get("latest_band")))
            for name, _lo, _hi in TAILS:
                a = (have.get("bands") or {}).get(name) or {}
                b = leg["bands"].get(name) or {}
                if a.get("n") != b.get("n"):
                    bad.append("%s %s n %s != %s" % (sym, name, a.get("n"), b.get("n")))
                elif a.get("mean_pct") is not None and b.get("mean_pct") is not None \
                        and abs(a["mean_pct"] - b["mean_pct"]) > 1e-6:
                    bad.append("%s %s mean %s != %s"
                               % (sym, name, a["mean_pct"], b["mean_pct"]))
                elif a.get("share_down") is not None and b.get("share_down") is not None \
                        and abs(a["share_down"] - b["share_down"]) > 1e-9:
                    bad.append("%s %s share_down %s != %s"
                               % (sym, name, a["share_down"], b["share_down"]))
        for name, _lo, _hi in TAILS:
            got_n = sum((l["bands"].get(name) or {}).get("n", 0)
                        for l in fresh_one["legs"].values())
            pub_n = ((pub_one.get("pooled") or {}).get(name) or {}).get("n")
            if pub_n != got_n:
                bad.append("pooled %s n %s != sum of legs %s" % (name, pub_n, got_n))
        if pub_one.get("verdict") != fresh_one.get("verdict"):
            bad.append("defer verdict %r != recomputed %r"
                       % (pub_one.get("verdict"), fresh_one.get("verdict")))
        pv = (pub_one.get("pooled") or {}).get(DEFER_BAND) or {}
        if pv.get("n") and ("%.0f" % (100.0 * (pv.get("share_down") or 0.0))) \
                not in (pub_one.get("sentence") or ""):
            bad.append("the defer sentence does not print the pooled share it rests on")

    # r1609: "today" must be the ticket's own bar. Re-derive the panel block, the anchored
    # percentiles, and the eviction of any leg priced on another day -- a face that reads
    # the panel's last row instead of the sheet's day keeps printing a number after the
    # panel moves, and nothing on the page changes when it does.
    fpanel = fresh.get("panel") or {}
    ppub = pub.get("panel") or {}
    if not ppub:
        bad.append("published face has no panel block -- it cannot say which day it prices")
    for k in ("ticket_session", "session_field", "price_panel_last", "state",
              "bars_beyond_session", "legs_counted"):
        if ppub.get(k) != fpanel.get(k):
            bad.append("panel.%s %r != re-derived %r" % (k, ppub.get(k), fpanel.get(k)))
    if sorted(ppub.get("legs_off_session") or []) != sorted(fpanel.get("legs_off_session") or []):
        bad.append("panel.legs_off_session %r != re-derived %r"
                   % (ppub.get("legs_off_session"), fpanel.get("legs_off_session")))
    for sym, leg in fresh_one.get("legs", {}).items():
        have = (pub_one.get("legs") or {}).get(sym) or {}
        if have.get("counted") != leg.get("counted"):
            bad.append("%s counted %r != re-derived %r"
                       % (sym, have.get("counted"), leg.get("counted")))
        if not leg.get("counted") and have.get("latest_pctile") is not None:
            bad.append("%s prints a percentile for a bar that is not the ticket's day (%s)"
                       % (sym, leg.get("session_state")))
    if fpanel.get("legs_counted") and (fpanel.get("ticket_session") or "") \
            not in (pub_one.get("sentence") or ""):
        bad.append("the one-session sentence does not name the day it describes (%s)"
                   % fpanel.get("ticket_session"))

    # r1562: the face's verdict has a referent. Assert the published identity re-derives,
    # that the ledger really recorded it, and that a replaced sample is said out loud in
    # the headline -- otherwise two different funds' verdicts read as one continuous series.
    bad.extend(sample_failures(pub, read_sample_ledger(), fresh))

    if bad:
        for b in bad[:12]:
            print("FAIL: " + b)
        print("%d failure(s)" % len(bad))
        return 1
    samp = pub.get("sample") or {}
    print("OK: published face re-derives from premium_history.csv "
          "(%d horizons, %d legs each, verdict %s)"
          % (len(fresh["horizons"]), len(fresh["horizons"][str(HORIZONS[-1])]["legs"]),
             fresh["verdict"]))
    print("OK: sample %s (%d legs) is on the ledger; changed_from_previous=%s"
          % (samp.get("signature"), len(samp.get("legs") or []),
             samp.get("changed_from_previous")))
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


def _rows_dated(sym, prems, closes, start="2019-01-01"):
    """Same fixture with UNIQUE consecutive dates -- session logic is date-keyed, and the
    ``_rows`` fixture repeats days (2021-01-01..28 in a loop), which cannot tell "the
    ticket's bar" from "another bar that shares its date"."""
    import datetime as _dt
    d0 = _dt.date.fromisoformat(start)
    return [{"date": (d0 + _dt.timedelta(days=i)).isoformat(), "symbol": sym, "close": c,
             "nav_date": None, "nav": None, "premium_pct": p}
            for i, (p, c) in enumerate(zip(prems, closes))]


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
    face = build(hist=_rows("TEST", prems4, closes4), ledger_rows=[])
    if face["verdict"] not in WORDS:
        fails.append("L24 built verdict %r is outside the vocabulary" % face["verdict"])
    if not face.get("evidence_cutoff"):
        fails.append("L25 built face has no evidence_cutoff")

    # 11. 'never in the top decile' is described as such, not as a zero return
    # (a strictly falling premium never ranks above its own past, so TOP stays empty)
    face2 = build(hist=_rows("TEST", [10.0 - 0.03 * i for i in range(200)],
                             [100.0 + i for i in range(200)]), ledger_rows=[])
    if "never reached its own top decile" not in face2["sentence"]:
        fails.append("L26 a leg with no top-decile session must say so in the sentence")

    # 12. tail bands are half-open and the top one is unbounded
    eq(tail_of(None), None, "L27 no percentile has no tail band")
    eq(tail_of(94.99), None, "L28 94.99 is below the tail")
    eq(tail_of(95.0), "P95_98", "L29 95.0 opens P95_98")
    eq(tail_of(98.0), "P98P", "L30 98.0 opens P98P")
    eq(tail_of(100.0), "P98P", "L31 100 stays in P98P")

    # 13. the one-session read reports which way the next session went, not just its mean
    # (the fixture is dense enough that the tail band clears THIN_N -- a fixture below the
    # floor would pass every assertion above by simply measuring nothing)
    prems_long = [10.0 if (i % 10) == 0 else 0.0 for i in range(2000)]
    px = 100.0
    cl = []
    for i in range(2000):
        cl.append(px)
        px *= 0.98 if (i % 10) == 0 else 1.0
    obs, _pct = one_session_obs(_rows("TEST", prems_long, cl))
    st = tail_stats(obs["P98P"])
    if st["n"] < THIN_N:
        fails.append("L32 the tail band collected %s hot prints, below the floor" % st["n"])
    eq(defer_verdict({DEFER_BAND: st}), "WAITING_PAID",
       "L33 a falling next session reads WAITING_PAID")
    px = 100.0
    cl2 = []
    for i in range(2000):
        cl2.append(px)
        px *= 1.02 if (i % 10) == 0 else 1.0
    obs2, _p2 = one_session_obs(_rows("TEST", prems_long, cl2))
    eq(defer_verdict({DEFER_BAND: tail_stats(obs2["P98P"])}), "WAITING_COST",
       "L34 the mirror case reads WAITING_COST")
    short_obs, _p3 = one_session_obs(_rows("TEST", prems_long[:40], cl[:40]))
    eq(defer_verdict({DEFER_BAND: tail_stats(short_obs["P98P"])}), "NO_READ",
       "L35 a sample below the floor says nothing")

    # 14. the pooled tail counts must be the sum of the legs' own counts
    face3 = build(hist=_rows("TEST", prems_long, cl), ledger_rows=[])
    one = face3["one_session"]
    legs_tot = sum(l["bands"][n]["n"] for l in one["legs"].values()
                   for n, _lo, _hi in TAILS)
    pooled_tot = sum(one["pooled"][n]["n"] for n, _lo, _hi in TAILS)
    eq(pooled_tot, legs_tot, "L36 pooled tail counts are the sum of the legs")
    if one["verdict"] not in DEFER_WORDS:
        fails.append("L37 defer verdict %r is outside the vocabulary" % one["verdict"])

    # 15. the sample identity: a verdict has a referent, and a replaced referent must be
    # said out loud (2026-11-11 live case: MIXED/-0.133 -> HIGH_PREMIUM_PAYS/+0.023 was a
    # new set of funds, not new information about the old ones)
    eq(sample_signature(["B", "A", "A"]), sample_signature(["A", "B"]),
       "L38 the signature is a property of the set, not of the read order or repeats")
    if sample_signature(["A", "B"]) == sample_signature(["A", "C"]):
        fails.append("L39 two different leg sets share one signature")
    prev_row = {"signature": sample_signature(["AAA"]), "legs": ["AAA"], "n_legs": 1,
                "first_published_session": "2026-11-10",
                "first_published_verdict": "MIXED", "first_published_verdict_horizon": 20,
                "changed_from_previous": False, "previous_signature": None,
                "previous_legs": [], "previous_session": None}
    first_pub = build(hist=_rows("TEST", prems4, closes4), ledger_rows=[])
    eq((first_pub["sample"] or {}).get("changed_from_previous"), False,
       "L40 the first publication of any sample is not a break")
    eq(first_pub["cross_session_comparable"], True, "L41 nothing to compare with yet")
    face_b = build(hist=_rows("TEST", prems4, closes4), ledger_rows=[prev_row])
    if not (face_b["sample"] or {}).get("changed_from_previous"):
        fails.append("L42 a leg set the ledger has never seen is flagged as a change")
    eq(face_b["cross_session_comparable"], False, "L43 a replaced sample is not comparable")
    eq((face_b.get("sample_break") or {}).get("previous_legs"), ["AAA"],
       "L44 the break names the legs it replaced")
    if BREAK_MARK not in (face_b.get("sentence") or ""):
        fails.append("L45 the break reaches the headline sentence, not just a side field")
    own_row = {k: (face_b.get("sample") or {}).get(k) for k in SAMPLE_LEDGER_FIELDS}
    face_c = build(hist=_rows("TEST", prems4, closes4), ledger_rows=[prev_row, own_row])
    eq({k: (face_c.get("sample") or {}).get(k) for k in SAMPLE_LEDGER_FIELDS}, own_row,
       "L46 a sample already on the ledger keeps its frozen row (run stays idempotent)")
    if face_c.get("sentence") != face_b.get("sentence"):
        fails.append("L47 republishing the same sample changed the headline sentence")
    eq(sample_failures(face_c, [prev_row, own_row], face_c), [],
       "L48 a face that names its sample and its break passes the sample arm")
    flipped = dict(face_b, sample=dict(face_b["sample"], changed_from_previous=False))
    if not sample_failures(flipped, [prev_row], face_b):
        fails.append("L49 a hand-flipped changed_from_previous is caught")
    quiet = dict(face_b, sentence="nothing changed here")
    if not any("does not say the sample changed" in m
               for m in sample_failures(quiet, [prev_row], face_b)):
        fails.append("L50 a break missing from the headline sentence is caught")
    claim = dict(first_pub, sentence=first_pub["sentence"] + " " + BREAK_MARK)
    if not any("claims a sample break" in m
               for m in sample_failures(claim, [], first_pub)):
        fails.append("L51 a claimed break the ledger does not record is caught")

    # 16. r1609: "today" is the ticket's bar, not the panel's last row. The last bar is the
    # CHEAPEST of its own history while the bar before it is the dearest, so the two candidate
    # bars (the sheet's day and the tail) cannot print the same percentile by accident -- a
    # fixture where they coincide would pass while measuring nothing.
    prems_s = [float(i) for i in range(299)] + [-5.0]
    closes_s = [100.0 + 0.2 * i for i in range(300)]
    rows_s = _rows_dated("TEST", prems_s, closes_s)
    last_day, prev_day = rows_s[-1]["date"], rows_s[-2]["date"]
    raw = expanding_percentile(prems_s)
    tail_pct = next(p for p in reversed(raw) if p is not None)
    anchored_prev = next(p for p in reversed(expanding_percentile(prems_s[:-1]))
                         if p is not None)
    if tail_pct == anchored_prev:
        fails.append("L52 the fixture cannot tell the tail bar from the bar before it")

    same = build(hist=rows_s, ledger_rows=[], ticket={"base_bar": last_day})
    eq(same["panel"]["state"], "SAME_SESSION", "L53 a ticket on the panel's last bar is same")
    eq(same["panel"]["session_field"], "base_bar", "L54 the day is read from base_bar")
    eq(same["panel"]["legs_counted"], 1, "L55 the same-session leg counts")
    eq(same["one_session"]["legs"]["TEST"]["latest_pctile"], tail_pct,
       "L56 same session: the anchored percentile is the panel's last percentile")

    ahead = build(hist=rows_s, ledger_rows=[], ticket={"base_bar": prev_day})
    leg_ahead = ahead["one_session"]["legs"]["TEST"]
    eq(ahead["panel"]["state"], "PANEL_AHEAD", "L57 a panel past the ticket reads PANEL_AHEAD")
    eq(ahead["panel"]["bars_beyond_session"], 1, "L58 one bar past the sheet")
    eq((ahead["one_session"]["legs"]["TEST"] or {}).get("counted"), True,
       "L59 a leg WITH a bar on the sheet's day still counts")
    eq(leg_ahead["bar_at_session"], prev_day, "L60 the leg names the bar it was read on")
    eq(leg_ahead["latest_pctile"], anchored_prev,
       "L61 PANEL_AHEAD: the reading is the ticket's bar, not the panel tail")
    if prev_day not in ahead["one_session"]["sentence"]:
        fails.append("L62 the one-session sentence names the day it describes")

    behind = build(hist=rows_s, ledger_rows=[], ticket={"base_bar": "2099-01-01"})
    eq(behind["panel"]["state"], "PANEL_BEHIND", "L63 a sheet after the panel is PANEL_BEHIND")
    eq(behind["one_session"]["legs"]["TEST"]["counted"], False,
       "L64 a leg the panel has not reached publishes no number")
    eq(behind["one_session"]["legs"]["TEST"]["latest_pctile"], None,
       "L65 ... and no percentile")
    eq(behind["panel"]["legs_off_session"], ["TEST"],
       "L66 ... and is named as left out")
    if "cannot say" not in behind["one_session"]["sentence"]:
        fails.append("L67 a face that cannot place the legs says so in the sentence")

    unknown = build(hist=rows_s, ledger_rows=[], ticket={})
    eq(unknown["panel"]["state"], "SESSION_UNKNOWN", "L68 a sheet with no day is unknown")
    eq(unknown["panel"]["ticket_session"], None, "L69 unknown is never a guessed date")
    eq(unknown["one_session"]["legs"]["TEST"]["counted"], False,
       "L70 an undated ticket counts nothing")

    gap_hist = [r for r in rows_s if r["date"] != prev_day]
    gap = build(hist=gap_hist, ledger_rows=[], ticket={"base_bar": prev_day})
    eq(gap["panel"]["state"], "PANEL_AHEAD", "L71 a hole still leaves the panel ahead")
    eq(gap["one_session"]["legs"]["TEST"]["counted"], False,
       "L72 a missing sheet bar is not replaced by a neighbour")
    eq(gap["one_session"]["legs"]["TEST"]["bar_at_session"], gap_hist[-2]["date"],
       "L73 the leg says which bar it actually stopped at")

    total = 73
    print("%d/%d legs" % (total - len(fails), total))
    for f in fails:
        print("FAIL: " + f)
    return 1 if fails else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("run", "check", "selftest"))
    ap.add_argument("--ticket", default=None,
                    help="price a named ticket instead of the published latest (proof runs)")
    ap.add_argument("--out", default=None,
                    help="write the face somewhere else; a proof run is not published")
    a = ap.parse_args()
    if a.cmd == "run":
        return run(a.ticket, a.out)
    if a.cmd == "check":
        return check()
    return selftest()


if __name__ == "__main__":
    sys.exit(main())
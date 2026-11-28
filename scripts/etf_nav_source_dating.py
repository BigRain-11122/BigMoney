"""Which day is a NAV number from? Ask the instrument's own price, not its date field.

r2213. r2212 concluded that the premium book's board file (`snap/<session>.navok.json`)
cannot be called "that session's NAV" because it carries one batch-level session stamp
and no per-row date, and that only the sina `fu_` quote -- which prints its own date in
field 7 -- may be used as a denominator. This module tests that premise instead of
inheriting it.

The test needs no third NAV source. An ETF trades at roughly its NAV, so on a day the
price moved by 1% or more, a NAV sitting on yesterday's close is not today's number,
whatever its date field says. Where the price barely moved (|move| < 1%) the two days are
indistinguishable from price alone, and this module refuses to judge those rows.

Two groups are reported separately, because they answer different questions:
  * `all`      -- every ticker that has both a price and a board value: which source is
                  current by default?
  * `r2212_gap`-- only the tickers r2212 flagged as differing by >= 0.10%. That set was
                  selected *by the gap*, so it is biased toward whichever source lags;
                  the price says which one that is instead of assuming it.

Measured 2026-11-27: on the 600 tickers that have both a price and a board value, 512
moved far enough to date. The board sits on today's path on 489 of them and on yesterday's
close on exactly 1; dated sina sits on today's path on 398 and on yesterday's close on 34
-- so a date field is a claim, not evidence, and r2212's proposal ("take the denominator
only from the dated source") would import 34 stale denominators rather than remove any.

22 board rows sit *beyond* the day's move, and this module keeps them in three separate
buckets because one word was hiding three situations (r2213): most are band days where the
two sources agree to within 0.01-0.5% and the price simply could not travel as far as the
NAV; the rest are rows where the two sources disagree with each other and no date can be
assigned from price at all. Neither bucket may be added to "on today's path" -- the old
verdict did exactly that, and printed 511/512 while its own table said 489.

Output: results/etf_nav/source_dating.json + SOURCE-DATING.md (self-contained).

Usage:
    python scripts/etf_nav_source_dating.py run [--sample 200]
    python scripts/etf_nav_source_dating.py check
    python scripts/etf_nav_source_dating.py selftest
"""
import argparse
import glob
import json
import os
import sys
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SNAP_DIR = os.path.join(ROOT, "data", "etf_premium", "snap")
OUT_DIR = os.path.join(ROOT, "results", "etf_nav")
FACE = os.path.join(OUT_DIR, "source_dating.json")
DOC = os.path.join(OUT_DIR, "SOURCE-DATING.md")
PEER_FACE = os.path.join(OUT_DIR, "two_source_audit.json")

HEAD = {"Referer": "https://finance.sina.com.cn/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
BATCH = 80
THROTTLE = 0.4

# Below this intraday move the two sessions cannot be told apart by price: a NAV within
# 1% of both closes is compatible with either day. Such rows are UNDECIDABLE, never
# agreement.
MIN_MOVE = 0.01
SAME_LINE = 0.65
PREV_LINE = 0.35
OVERSHOOT_LINE = 1.35

# A move this large has hit the +/-10% band: the price cannot travel further, so a NAV
# that rose by more than the price is capped by construction, not stale.
LIMIT_MOVE = 0.095
# Two sources "agree" when they are within this of each other; beyond it one of them is
# not the number the other one is.
CROSS_TOL = 0.01
# A row whose position `t` sits this close to a decision line is printed with its own
# number: the label is a cut, and near the cut the cut is what decided the answer.
MARGIN = 0.05

LABELS = ("SAME_SESSION", "PREV_SESSION", "BETWEEN", "OVERSHOOT", "UNDECIDABLE", "NO_DATA")
# Board rows labelled OVERSHOOT are split by whether the two sources agree with each
# other. Both-agree rows are evidence about the price, not about the date; rows where the
# sources disagree with each other are the only ones that leave a dating question open.
BEYOND = ("CAPPED_BY_LIMIT", "AGREED_BEYOND", "SOURCES_DISAGREE")


def position(nav, prev, last, min_move=MIN_MOVE):
    """Where does `nav` sit on the day's price path? 0 = yesterday's close, 1 = today's."""
    try:
        nav, prev, last = float(nav), float(prev), float(last)
    except (TypeError, ValueError):
        return "NO_DATA"
    if nav <= 0 or prev <= 0 or last <= 0:
        return "NO_DATA"
    move = last / prev - 1.0
    if abs(move) < min_move:
        return "UNDECIDABLE"
    t = (nav / prev - 1.0) / move
    if t < PREV_LINE:
        return "PREV_SESSION"
    if t > OVERSHOOT_LINE:
        return "OVERSHOOT"
    if t > SAME_LINE:
        return "SAME_SESSION"
    return "BETWEEN"


def path_t(nav, prev, last, min_move=MIN_MOVE):
    """Where `nav` sits on the day's price path, as a fraction: 1 = today, 0 = yesterday.

    Pure. None when the row cannot be placed at all -- the same refusals as `position`.
    """
    try:
        nav, prev, last = float(nav), float(prev), float(last)
    except (TypeError, ValueError):
        return None
    if nav <= 0 or prev <= 0 or last <= 0:
        return None
    move = last / prev - 1.0
    if abs(move) < min_move:
        return None
    return (nav / prev - 1.0) / move


def margin_of(t):
    """Distance to the nearest decision line, in `t` units.

    A label is a hard cut on a continuous quantity: t = 0.33 reads "yesterday's close" by
    0.02, which is not the same statement as t = 0.05. Rows inside MARGIN are printed with
    their own number, so the reader can see the cut is doing the work rather than the data.
    """
    if t is None:
        return None
    return min(abs(t - PREV_LINE), abs(t - SAME_LINE), abs(t - OVERSHOOT_LINE))


def latest_navok():
    best = None
    for p in sorted(glob.glob(os.path.join(SNAP_DIR, "*.navok.json"))):
        try:
            d = json.load(open(p, encoding="utf-8"))
        except Exception:
            continue
        if d.get("nav"):
            best = (p, d)
    return best


def gap_set_from_peer():
    """Codes r2212 flagged as differing by >= its 0.10% line (worst + over-line lists)."""
    try:
        d = json.load(open(PEER_FACE, encoding="utf-8"))
    except Exception:
        return set(), None
    codes = {r["code"] for r in (d.get("worst") or [])}
    codes |= {r["code"] for r in (d.get("gap_over_line") or [])}
    return codes, d.get("board_session")


def _num(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def parse_fu(sym, raw):
    """sina `fu_` payload -> {code, nav, nav_date, cum_nav}. Pure."""
    if "=" not in raw:
        return None
    body = raw.split("=", 1)[1].strip().strip(";").strip('"')
    f = body.split(",")
    if len(f) < 8:
        return None
    nav = _num(f[2])
    cum = _num(f[3]) if len(f) > 3 else None
    date = f[7].strip()
    if nav is None or nav <= 0 or not date or "-" not in date:
        return None
    return {"code": sym.replace("fu_", ""), "nav": nav, "nav_date": date, "cum_nav": cum}


def parse_quote(sym, raw):
    """sina `hq` payload -> {code, prev_close, last, date}. Pure."""
    if "=" not in raw:
        return None
    body = raw.split("=", 1)[1].strip().strip(";").strip('"')
    f = body.split(",")
    if len(f) < 32:
        return None
    prev, last = _num(f[2]), _num(f[3])
    if not prev or not last or prev <= 0 or last <= 0:
        return None
    return {"code": sym[-6:], "prev_close": prev, "last": last, "date": f[30]}


def _fetch(url):
    req = urllib.request.Request(url, headers=HEAD)
    return urllib.request.urlopen(req, timeout=25).read().decode("gbk", "replace")


def _sweep(codes, prefix, parser, tag):
    out, failed = {}, 0
    for i in range(0, len(codes), BATCH):
        chunk = codes[i:i + BATCH]
        try:
            raw = _fetch("http://hq.sinajs.cn/list=" + ",".join(prefix(c) for c in chunk))
        except Exception:
            failed += 1
            time.sleep(THROTTLE)
            continue
        for line in raw.split(";"):
            line = line.strip()
            if '="' not in line or tag not in line:
                continue
            sym = line.split('="')[0].split("hq_str_")[-1]
            r = parser(sym, line)
            if r:
                out[r["code"]] = r
        time.sleep(THROTTLE)
    return out, failed


def fetch_nav(codes):
    return _sweep(codes, lambda c: "fu_" + c, parse_fu, "fu_")


def fetch_price(codes):
    return _sweep(codes, lambda c: ("sz" if c[0] == "1" else "sh") + c, parse_quote, "hq_str_")


def beyond_kind(nav, other_nav, prev, last, min_move=MIN_MOVE, cross_tol=CROSS_TOL):
    """Split a board row that sits beyond the day's move by whether the sources agree.

    Pure. Returns None for anything that is not an overshoot, else one of BEYOND.
    """
    if position(nav, prev, last, min_move) != "OVERSHOOT":
        return None
    try:
        nav, other = float(nav), float(other_nav)
    except (TypeError, ValueError):
        return "SOURCES_DISAGREE"
    if nav <= 0 or other <= 0:
        return "SOURCES_DISAGREE"
    if abs(nav / other - 1.0) > cross_tol:
        return "SOURCES_DISAGREE"
    move = float(last) / float(prev) - 1.0
    if abs(move) >= LIMIT_MOVE:
        return "CAPPED_BY_LIMIT"
    return "AGREED_BEYOND"


TICKET_GLOB = os.path.join(ROOT, "results", "etf_book_order", "TICKET-*.json")


def load_ticket(session=None):
    """The ticket this face must answer for. Pure read; never guessed.

    Returns `{"status": ...}` on failure instead of raising, so a face built without a
    ticket says so rather than printing an empty table that reads like "no legs".
    """
    paths = sorted(glob.glob(TICKET_GLOB))
    if not paths:
        return {"status": "missing", "why": "no ticket file on disk", "legs": []}
    path = paths[-1]
    if session:
        match = [p for p in paths if session in os.path.basename(p)]
        if match:
            path = match[-1]
        else:
            return {"status": "no_ticket_for_session", "ticket": os.path.basename(path),
                    "why": "the newest ticket is for another session than the board",
                    "legs": []}
    try:
        d = json.load(open(path, encoding="utf-8"))
    except Exception as exc:
        return {"status": "unreadable", "ticket": os.path.basename(path),
                "why": str(exc)[:120], "legs": []}
    order = ((d.get("ticket") or {}).get("order")) or []
    legs = [{"symbol": str(o.get("symbol")), "class": o.get("class"),
             "weight": o.get("weight"), "amount_cny": o.get("amount")} for o in order]
    return {"status": "ok" if legs else "empty", "ticket": os.path.basename(path),
            "generated": d.get("generated"), "session": d.get("evidence_cutoff"),
            "legs": legs}


def ticket_legs(ticket, rows_by_code):
    """Every leg on the ticket, with the dating verdict for its own denominator. Pure.

    The ticket is the only consumer that spends money, so it is the one place where "I
    could not date this NAV" has to be printed next to the leg instead of left in a table
    the reader has to join by hand.
    """
    out = []
    for leg in (ticket.get("legs") or []):
        code = leg["symbol"]
        r = rows_by_code.get(code)
        if r is None:
            out.append({"symbol": code, "class": leg.get("class"), "amount_cny": leg.get("amount_cny"),
                        "status": "NO_PRICE",
                        "why": "no price row for this ticker -> nothing to date"})
            continue
        dated = [lab for lab in (r.get("board_position"), r.get("sina_position"))
                 if lab in ("SAME_SESSION", "PREV_SESSION")]
        status = "DATED" if dated else "UNDECIDABLE"
        out.append({
            "symbol": code, "class": leg.get("class"), "amount_cny": leg.get("amount_cny"),
            "status": status,
            "board_position": r.get("board_position"),
            "sina_position": r.get("sina_position"),
            "sina_nav_date": r.get("sina_nav_date"),
            "board_missing": r.get("board_missing"),
            "board_nav": r.get("board_nav"), "sina_nav": r.get("sina_nav"),
            "board_t": r.get("board_t"), "sina_t": r.get("sina_t"),
            "move_pct": r.get("move_pct"),
        })
    return out


def ticket_verdict(legs):
    """One sentence about the ticket's own denominators. Pure."""
    if not legs:
        return "TICKET: CANNOT_VERIFY -- no legs to date (ticket missing or empty)"
    n = len(legs)
    no_price = [l["symbol"] for l in legs if l["status"] == "NO_PRICE"]
    undec = [l["symbol"] for l in legs if l["status"] == "UNDECIDABLE"]
    dated = [l for l in legs if l["status"] == "DATED"]
    same = [l["symbol"] for l in dated
            if l.get("board_position") == "SAME_SESSION" or l.get("sina_position") == "SAME_SESSION"]
    prev = [l["symbol"] for l in dated
            if l.get("board_position") != "SAME_SESSION" and l.get("sina_position") != "SAME_SESSION"]
    parts = ["%d/%d dated" % (len(dated), n)]
    if same:
        parts.append("%d on today's path" % len(same))
    if prev:
        parts.append("%d on yesterday's close (%s)" % (len(prev), ", ".join(prev)))
    if undec:
        parts.append("%d undecidable (price barely moved: %s)" % (len(undec), ", ".join(undec)))
    if no_price:
        parts.append("%d without a price (%s)" % (len(no_price), ", ".join(no_price)))
    bad = bool(prev or no_price)
    return "TICKET: %s -- %s" % ("ONE_OR_MORE_LEGS_UNPROVEN" if bad else "EVERY_LEG_DATED",
                                  "; ".join(parts))


def build(board_session, board_nav, sina_nav, prices, gap_codes=None):
    """Pure. One row per ticker that has a price and at least one NAV source.

    r2214: the row set is the UNION of both sources, not the board alone. A ticker the
    board never answered for (cross-border funds priced off sina's own NAV) used to fall
    out of this face entirely -- and those are exactly the legs whose denominator the
    ticket leans on. Such a row carries `board_missing: true`, so a missing board value
    is never read as a board value that agrees.
    """
    gap_codes = gap_codes or set()
    rows = []
    for code in sorted((set(board_nav) | set(sina_nav)) & set(prices)):
        px = prices[code]
        b = board_nav.get(code)
        s = (sina_nav.get(code) or {}).get("nav")
        rows.append({
            "code": code,
            "board_nav": b,
            "board_missing": b is None,
            "sina_nav": s,
            "sina_nav_date": (sina_nav.get(code) or {}).get("nav_date"),
            "prev_close": px["prev_close"],
            "last_close": px["last"],
            "move_pct": round((px["last"] / px["prev_close"] - 1.0) * 100.0, 4),
            "board_position": position(b, px["prev_close"], px["last"]),
            "sina_position": position(s, px["prev_close"], px["last"]),
            "board_t": path_t(b, px["prev_close"], px["last"]),
            "sina_t": path_t(s, px["prev_close"], px["last"]),
            "board_beyond": beyond_kind(b, s, px["prev_close"], px["last"]),
            "in_r2212_gap_set": code in gap_codes,
        })
    # A source date that is LATER than the board session is not a future NAV: it is the
    # feed stamping a non-session day onto a number it did not recompute (159655 prints
    # 2026-11-28, a Saturday, on the 4th). The date field is a claim about the feed, so
    # the face counts those rows instead of trusting the field to be a session at all.
    after = [r["code"] for r in rows
             if r.get("sina_nav_date") and board_session and r["sina_nav_date"] > board_session]
    return {
        "board_session": board_session,
        "min_move_pct": MIN_MOVE * 100.0,
        "n_rows": len(rows),
        "all": summarize(rows),
        "r2212_gap": summarize([r for r in rows if r["in_r2212_gap_set"]]),
        "sina_date_after_board": {"n": len(after), "codes": after[:12]},
        "rows": rows,
    }


def summarize(rows):
    # A row that only one source answered for is NO_DATA on the other side, and a NO_DATA
    # row cannot date anything: keeping it in the denominator would inflate every share
    # in the table (r2214: the union row set makes this reachable, so it is excluded here
    # rather than assumed away).
    dec = [r for r in rows if r["board_position"] not in ("UNDECIDABLE", "NO_DATA")]
    n_board_missing = sum(1 for r in rows if r.get("board_missing"))

    def near(key):
        n = 0
        for r in dec:
            m = margin_of(r.get(key))
            if m is not None and m <= MARGIN:
                n += 1
        return n

    return {
        "n_rows": len(rows),
        "n_decidable": len(dec),
        "n_board_missing": n_board_missing,
        "board": {k: sum(1 for r in dec if r["board_position"] == k) for k in LABELS},
        "board_beyond": {k: sum(1 for r in dec if r.get("board_beyond") == k) for k in BEYOND},
        "board_marginal": near("board_t"),
        "sina": {k: sum(1 for r in dec if r["sina_position"] == k) for k in LABELS},
        "sina_marginal": near("sina_t"),
        "sina_missing": sum(1 for r in rows if r["sina_nav"] is None),
    }


def _beyond_text(g):
    """"+N beyond it (M price-capped, K unexplained)" -- the part the old verdict hid."""
    bb = g.get("board_beyond") or {}
    over = g["board"]["OVERSHOOT"]
    if not over:
        return ""
    return ("; %d board rows sit beyond the day's move (%d with the price at the band and "
            "both sources agreeing, %d with the sources disagreeing)"
            % (over, bb.get("CAPPED_BY_LIMIT", 0) + bb.get("AGREED_BEYOND", 0),
               bb.get("SOURCES_DISAGREE", 0)))


def _verdict_one(g, label):
    d = g["n_decidable"]
    if d < 5:
        return "%s: CANNOT_VERIFY -- only %d rows moved >= %s%%" % (
            label, d, MIN_MOVE * 100.0)
    b, s = g["board"], g["sina"]
    if b["SAME_SESSION"] > d / 2 and s["PREV_SESSION"] > d / 2:
        return ("%s: BOARD_IS_TODAY_SINA_IS_YESTERDAY -- board %d/%d on today's path, "
                "dated sina %d/%d on yesterday's close%s" % (
                    label, b["SAME_SESSION"], d, s["PREV_SESSION"], d, _beyond_text(g)))
    if s["SAME_SESSION"] > d / 2 and b["PREV_SESSION"] > d / 2:
        return ("%s: SINA_IS_TODAY_BOARD_IS_YESTERDAY -- dated sina %d/%d on today's path, "
                "board %d/%d on yesterday's close%s" % (
                    label, s["SAME_SESSION"], d, b["PREV_SESSION"], d, _beyond_text(g)))
    both = b["SAME_SESSION"] > d / 2 and s["SAME_SESSION"] > d / 2
    if both:
        if s["PREV_SESSION"]:
            return ("%s: BOTH_CURRENT_BUT_SINA_LAGS_ON_%d -- board %d/%d on today's path, "
                    "dated sina %d/%d on it and %d/%d on yesterday's close even though it "
                    "prints today%s" % (
                        label, s["PREV_SESSION"], b["SAME_SESSION"], d,
                        s["SAME_SESSION"], d, s["PREV_SESSION"], d, _beyond_text(g)))
        return ("%s: BOTH_CURRENT -- %d/%d on today's path in both sources%s" % (
            label, b["SAME_SESSION"], d, _beyond_text(g)))
    return ("%s: MIXED -- board same/prev=%d/%d, sina same/prev=%d/%d over %d movers%s" % (
        label, b["SAME_SESSION"], b["PREV_SESSION"], s["SAME_SESSION"], s["PREV_SESSION"], d,
        _beyond_text(g)))


def verdict_of(face):
    out = [_verdict_one(face["all"], "ALL")]
    if face["r2212_gap"]["n_rows"]:
        out.append(_verdict_one(face["r2212_gap"], "R2212_GAP_SET"))
    return " || ".join(out)


def render(face, verdict):
    L = ["# Which day is this NAV from?", "",
         "board session: %s · rows with a price: %d · minimum move that can date a row: %s%%"
         % (face["board_session"], face["n_rows"], face["min_move_pct"]), "",
         "## Verdict", ""]
    for part in verdict.split(" || "):
        L.append("- " + part)
    tk = face.get("ticket") or {}
    legs = face.get("ticket_legs") or []
    L += ["", "## The legs on the ticket (%s)" % (tk.get("ticket") or "no ticket file"), ""]
    if not legs:
        L += ["No leg could be read: %s. An empty table here is not 'no denominators to",
              "date' -- it means the ticket itself was unreadable." % (tk.get("why") or "unknown"), ""]
    else:
        L += ["| leg | class | amount CNY | board | sina | source date | board t | sina t | move% | status |",
              "|---|---|---|---|---|---|---|---|---|---|"]

        def _f(v):
            return "%.3f" % v if v is not None else "n/a"

        for l in legs:
            L.append("| %s | %s | %s | %s%s | %s | %s | %s | %s | %.2f | %s |" % (
                l["symbol"], l.get("class") or "", l.get("amount_cny") if l.get("amount_cny") is not None else "",
                l.get("board_position") or "n/a",
                " (board has no row)" if l.get("board_missing") else "",
                l.get("sina_position") or "n/a", l.get("sina_nav_date") or "n/a",
                _f(l.get("board_t")), _f(l.get("sina_t")),
                l.get("move_pct") if l.get("move_pct") is not None else float("nan"),
                l.get("status")))
        L += ["", "A leg marked `UNDECIDABLE` is one whose price barely moved: its NAV cannot be",
              "placed on either day from price alone, which is a refusal, not a clean bill.",
              "A leg marked `NO_PRICE` has no quote row at all. Either one means the ticket's",
              "denominator for that leg is unproven on this face.", ""]
    da = face.get("sina_date_after_board") or {}
    if da.get("n"):
        L += ["**The `source date` column is not a session.** %d row(s) print a date LATER than"
              % da["n"],
              "the board session (%s) -- e.g. a Saturday -- on a number the feed did not"
              % face.get("board_session"),
              "recompute: %s." % ", ".join(da.get("codes") or []), ""]
    L += ["", "## Counts by group (price-decidable rows only)", "",
          "| group | rows | decidable | board SAME | board PREV | board beyond: capped | beyond: agreed | beyond: sources disagree | sina SAME | sina PREV | sina missing |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for key, name in (("all", "all tickers"), ("r2212_gap", "r2212 gap set")):
        g = face[key]
        bb = g.get("board_beyond") or {}
        L.append("| %s | %d | %d | %d | %d | %d | %d | %d | %d | %d | %d |" % (
            name, g["n_rows"], g["n_decidable"], g["board"]["SAME_SESSION"],
            g["board"]["PREV_SESSION"],
            bb.get("CAPPED_BY_LIMIT", 0), bb.get("AGREED_BEYOND", 0),
            bb.get("SOURCES_DISAGREE", 0),
            g["sina"]["SAME_SESSION"], g["sina"]["PREV_SESSION"], g["sina_missing"]))
    L += ["", "Legend: SAME_SESSION = the number sits on today's close path; PREV_SESSION = it",
          "sits on yesterday's close; UNDECIDABLE = the price barely moved, so price alone",
          "cannot tell the two days apart (not agreement). A row BEYOND the day's move is",
          "split three ways because the three cases mean different things:",
          "",
          "- `capped` -- the move is >= 9.5% (the band) and both sources agree within 1%: the",
          "  price could not travel to the NAV, so this row is a statement about the band, not",
          "  about a stale number.",
          "- `agreed beyond` -- both sources agree within 1% but the price did not hit a band:",
          "  the NAV moved more than the traded price that day. Not datable from price alone.",
          "- `sources disagree` -- the two sources differ by more than 1% (or one is missing):",
          "  the only case that leaves a real dating question open.", ""]
    marg = [r for r in face["rows"]
            if any((margin_of(r.get(k)) is not None and margin_of(r.get(k)) <= MARGIN)
                   for k in ("board_t", "sina_t"))]
    if marg:
        g = face["all"]
        L += ["## Rows within %s of a decision line (the cut decided these, not the data)"
              % MARGIN, "",
              "board %d and sina %d of %d decidable rows sit this close to a line."
              % (g.get("board_marginal", 0), g.get("sina_marginal", 0), g["n_decidable"]), "",
              "| code | board | sina | board t | sina t | board label | sina label | move% |",
              "|---|---|---|---|---|---|---|---|"]
        for r in marg[:25]:
            def _f(v):
                return "%.3f" % v if v is not None else "n/a"
            L.append("| %s | %s | %s | %s | %s | %s | %s | %.2f |" % (
                r["code"], r["board_nav"], r.get("sina_nav"), _f(r.get("board_t")),
                _f(r.get("sina_t")), r["board_position"], r["sina_position"],
                r["move_pct"]))
        if len(marg) > 25:
            L.append("| ... | | | | | | | %d more |" % (len(marg) - 25))
        L.append("")
    stale = [r for r in face["rows"] if r["sina_position"] == "PREV_SESSION"]
    if stale:
        L += ["## Dated rows that sit on yesterday's close (the ones to re-date)", "",
              "| code | board | sina | sina date | prev | last | move% | board t |",
              "|---|---|---|---|---|---|---|---|"]
        for r in stale[:25]:
            L.append("| %s | %s | %s | %s | %.4f | %.4f | %.2f | %s |" % (
                r["code"], r["board_nav"], r["sina_nav"], r["sina_nav_date"],
                r["prev_close"], r["last_close"], r["move_pct"],
                "%.3f" % r["sina_t"] if r.get("sina_t") is not None else "n/a"))
        if len(stale) > 25:
            L.append("| ... | | | | | | %d more |" % (len(stale) - 25))
        L.append("")
    over = [r for r in face["rows"] if r["board_position"] == "OVERSHOOT"]
    if over:
        agree = [r for r in over if r.get("board_beyond") in ("CAPPED_BY_LIMIT", "AGREED_BEYOND")]
        disag = [r for r in over if r.get("board_beyond") == "SOURCES_DISAGREE"]
        if agree:
            capped = sum(1 for r in agree if r.get("board_beyond") == "CAPPED_BY_LIMIT")
            L += ["## Board numbers beyond the day's move, with both sources agreeing", "",
                  "%d of %d rows: %d at the price band, %d beyond it without a band. Both"
                  % (len(agree), len(over), capped, len(agree) - capped),
                  "sources say the same number here, so the date question does not arise -- the",
                  "NAV simply moved further than the traded price could.", "",
                  "| code | board | sina | board/sina-1 % | prev | last | move% |",
                  "|---|---|---|---|---|---|---|"]
            for r in agree[:25]:
                gap = (abs(float(r["board_nav"]) / float(r["sina_nav"]) - 1.0) * 100.0
                       if r.get("sina_nav") else float("nan"))
                L.append("| %s | %s | %s | %.3f | %.4f | %.4f | %.2f |" % (
                    r["code"], r["board_nav"], r["sina_nav"], gap,
                    r["prev_close"], r["last_close"], r["move_pct"]))
            if len(agree) > 25:
                L.append("| ... | | | | | | %d more |" % (len(agree) - 25))
            L.append("")
        if disag:
            L += ["## Board numbers beyond the day's move, sources disagreeing", "",
                  "These are the rows where no date can be assigned from price: the two sources",
                  "differ by more than %s%% of each other." % (CROSS_TOL * 100.0), "",
                  "| code | board | sina | board/sina-1 % | prev | last | move% |",
                  "|---|---|---|---|---|---|---|"]
            for r in disag[:25]:
                gap = (abs(float(r["board_nav"]) / float(r["sina_nav"]) - 1.0) * 100.0
                       if r.get("sina_nav") else float("nan"))
                L.append("| %s | %s | %s | %.3f | %.4f | %.4f | %.2f |" % (
                    r["code"], r["board_nav"], r.get("sina_nav"), gap,
                    r["prev_close"], r["last_close"], r["move_pct"]))
            L.append("")
    L += ["- A row absent from this table was not compared, not \"agreed\".",
          "- The judgement rests on the instrument's own traded price, not on either source's label.",
          ""]
    return "\n".join(L) + "\n"


def cmd_run(sample):
    got = latest_navok()
    if not got:
        print("no navok snapshot carrying values -> nothing to date", file=sys.stderr)
        return 2
    path, d = got
    board_session, board_nav = d.get("session"), d.get("nav") or {}
    ticket = load_ticket(board_session)
    leg_syms = [l["symbol"] for l in (ticket.get("legs") or [])]
    board_codes = sorted(board_nav)[:sample] if sample else sorted(board_nav)
    # The ticket's own legs are always fetched, whatever the sample cut says: the face
    # exists to answer for the legs that spend money.
    codes = sorted(set(board_codes) | set(leg_syms))
    gap_codes, gap_session = gap_set_from_peer()
    if gap_session and board_session and gap_session != board_session:
        print("note: r2212 gap set is for %s, board is %s -- group comparison is cross-session"
              % (gap_session, board_session))
    print("board: %s (%d values) sample=%d  ticket legs=%d  sweep=%d  gap-set codes=%d" % (
        os.path.basename(path), len(board_nav), len(board_codes), len(leg_syms),
        len(codes), len(gap_codes)))
    sina, f1 = fetch_nav(codes)
    prices, f2 = fetch_price(codes)
    print("sina nav: %d   prices: %d   failed batches: %d" % (len(sina), len(prices), f1 + f2))
    face = build(board_session, {c: board_nav[c] for c in codes if c in board_nav},
                 sina, prices, gap_codes)
    rows_by_code = {r["code"]: r for r in face["rows"]}
    face["ticket"] = ticket
    face["ticket_legs"] = ticket_legs(ticket, rows_by_code)
    face["generated"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    face["failed_batches"] = f1 + f2
    face["sample"] = sample
    face["verdict"] = verdict_of(face) + " || " + ticket_verdict(face["ticket_legs"])
    os.makedirs(OUT_DIR, exist_ok=True)
    json.dump(face, open(FACE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    open(DOC, "w", encoding="utf-8").write(render(face, face["verdict"]))
    print("VERDICT: " + face["verdict"])
    print("-> %s" % FACE)
    return 0


def verify():
    """Re-derive every printed number from the rows. Returns (rc, text).

    Split out of `cmd_check` so a smoke leg can ask the same question in-process without
    spawning a console (零窗律) and without parsing stdout.
    """
    if not os.path.exists(FACE):
        return 3, "STALE: face missing (%s) -> run first" % FACE
    face = json.load(open(FACE, encoding="utf-8"))
    problems = []
    got = latest_navok()
    if got and (got[1].get("session") or "") > (face.get("board_session") or ""):
        return 3, "STALE: board session moved %s -> %s" % (
            face.get("board_session"), got[1].get("session"))
    rows = face.get("rows") or []
    if len(rows) != face.get("n_rows"):
        problems.append("n_rows=%s but %d rows printed" % (face.get("n_rows"), len(rows)))
    for r in rows:
        for key, src in (("board_position", "board_nav"), ("sina_position", "sina_nav")):
            want = position(r.get(src), r.get("prev_close"), r.get("last_close"))
            if want != r.get(key):
                problems.append("%s %s printed %s but re-derives %s"
                                % (r["code"], key, r.get(key), want))
                break
        want_beyond = beyond_kind(r.get("board_nav"), r.get("sina_nav"),
                                  r.get("prev_close"), r.get("last_close"))
        if want_beyond != r.get("board_beyond"):
            problems.append("%s board_beyond printed %s but re-derives %s"
                            % (r["code"], r.get("board_beyond"), want_beyond))
        for key, src in (("board_t", "board_nav"), ("sina_t", "sina_nav")):
            want_t = path_t(r.get(src), r.get("prev_close"), r.get("last_close"))
            got_t = r.get(key)
            if (want_t is None) != (got_t is None):
                problems.append("%s %s printed %s but re-derives %s"
                                % (r["code"], key, got_t, want_t))
            elif want_t is not None and abs(want_t - got_t) > 1e-9:
                problems.append("%s %s printed %.9f but re-derives %.9f"
                                % (r["code"], key, got_t, want_t))
    for key, name in (("all", "all"), ("r2212_gap", "gap")):
        want = summarize([r for r in rows if key == "all" or r.get("in_r2212_gap_set")])
        if want != (face.get(key) or {}):
            problems.append("%s block does not recount from its own rows" % name)
    legs = face.get("ticket_legs") or []
    tk = face.get("ticket") or {}
    if tk.get("status") == "ok" and not legs:
        problems.append("ticket read as ok but no leg is dated")
    if len(legs) != len(tk.get("legs") or []):
        problems.append("ticket has %d legs but %d are dated"
                        % (len(tk.get("legs") or []), len(legs)))
    want_legs = ticket_legs(tk, {r["code"]: r for r in rows})
    if want_legs != legs:
        problems.append("ticket legs do not re-derive from the rows")
    want_verdict = verdict_of(face) + " || " + ticket_verdict(legs)
    if (face.get("verdict") or "") != want_verdict:
        problems.append("verdict does not follow from its own counts")
    after = [r["code"] for r in rows
             if r.get("sina_nav_date") and face.get("board_session")
             and r["sina_nav_date"] > face["board_session"]]
    want_after = {"n": len(after), "codes": after[:12]}
    if want_after != (face.get("sina_date_after_board") or {"n": 0, "codes": []}):
        problems.append("sina_date_after_board does not recount from its own rows")
    if problems:
        return 3, "CHECK FAILED: " + " | ".join(problems[:4])
    return 0, ("CHECK_OK rows=%d decidable=%d board_same=%d board_prev=%d sina_prev=%d "
               "gap_set_rows=%d ticket_legs=%d ticket_dated=%d"
               % (len(rows), face["all"]["n_decidable"], face["all"]["board"]["SAME_SESSION"],
                  face["all"]["board"]["PREV_SESSION"], face["all"]["sina"]["PREV_SESSION"],
                  face["r2212_gap"]["n_rows"], len(legs),
                  sum(1 for l in legs if l.get("status") == "DATED")))


def cmd_check():
    rc, text = verify()
    print(text)
    return rc


def cmd_selftest():
    legs = []

    def chk(name, cond):
        legs.append((name, bool(cond)))

    # A day where price rose 10%: prev 1.000 -> last 1.100
    chk("L1 yesterday's number reads PREV_SESSION", position(1.001, 1.000, 1.100) == "PREV_SESSION")
    chk("L2 today's number reads SAME_SESSION", position(1.098, 1.000, 1.100) == "SAME_SESSION")
    chk("L3 a flat day cannot date anything", position(1.050, 1.000, 1.002) == "UNDECIDABLE")
    chk("L4 a number beyond the move reads OVERSHOOT", position(1.200, 1.000, 1.100) == "OVERSHOOT")
    chk("L5 halfway reads BETWEEN", position(1.050, 1.000, 1.100) == "BETWEEN")
    chk("L6 missing value is NO_DATA, not a label", position(None, 1.0, 1.1) == "NO_DATA")
    chk("L7 zero/negative nav refused", position(0, 1.0, 1.1) == "NO_DATA")
    chk("L8 minimal decidable move works",
        position(1.0005, 1.000, 1.011) in ("PREV_SESSION", "BETWEEN"))

    # The verdict is a function of the counts: flip the counts, the word flips.
    def counts(same=0, prev=0, between=0, over=0):
        return {"SAME_SESSION": same, "PREV_SESSION": prev, "BETWEEN": between,
                "OVERSHOOT": over, "UNDECIDABLE": 0, "NO_DATA": 0}

    g = {"n_rows": 6, "n_decidable": 6, "board": counts(6), "sina": counts(prev=6)}
    v1 = _verdict_one(g, "X")
    g2 = {"n_rows": 6, "n_decidable": 6, "board": counts(prev=6), "sina": counts(6)}
    v2 = _verdict_one(g2, "X")
    g3 = {"n_rows": 6, "n_decidable": 6, "board": counts(6), "sina": counts(5, prev=1)}
    v3 = _verdict_one(g3, "X")
    chk("L9 verdict follows the counts (three directions)",
        v1.startswith("X: BOARD_IS_TODAY") and v2.startswith("X: SINA_IS_TODAY")
        and "BOTH_CURRENT_BUT_SINA_LAGS_ON_1" in v3)

    small = {"n_rows": 2, "n_decidable": 2, "board": counts(2), "sina": counts(2)}
    chk("L10 too few movers is CANNOT_VERIFY", "CANNOT_VERIFY" in _verdict_one(small, "X"))

    f = build("2026-11-27", {"C": 0.6088}, {"C": {"nav": 0.532, "nav_date": "2026-11-27"}},
              {"C": {"prev_close": 0.531, "last": 0.584}})
    r = f["rows"][0]
    chk("L11 live 159546 shape: board overshoots, dated sina sits on yesterday",
        r["board_position"] == "OVERSHOOT" and r["sina_position"] == "PREV_SESSION")

    # The gap set must be attributed per row and counted separately, not folded into `all`.
    f = build("2026-11-27", {"A": 1.99, "B": 1.01},
              {"A": {"nav": 1.0}, "B": {"nav": 1.0}},
              {"A": {"prev_close": 1.0, "last": 1.1}, "B": {"prev_close": 1.0, "last": 1.1}},
              gap_codes={"A"})
    chk("L12 gap set is a separate group with its own count",
        f["r2212_gap"]["n_rows"] == 1 and f["all"]["n_rows"] == 2
        and f["r2212_gap"]["board"]["OVERSHOOT"] == 1)

    # A ticker with no sina nav is counted as missing, never as agreeing.
    f = build("2026-11-27", {"D": 1.05}, {}, {"D": {"prev_close": 1.0, "last": 1.1}})
    chk("L13 absent sina row is missing, not agreement",
        f["all"]["sina_missing"] == 1 and f["all"]["sina"]["SAME_SESSION"] == 0)

    # --- the beyond split: three cases that used to be one word ------------------------
    # A +10% band day where both sources print +17%: the price is capped, the NAV is not
    # stale. This must not be counted as "on today's path", and must not be called a lag.
    chk("L14 a band day with both sources agreeing is CAPPED_BY_LIMIT",
        beyond_kind(1.17, 1.1699, 1.0, 1.10) == "CAPPED_BY_LIMIT")
    chk("L15 same sources on a day with no band are AGREED_BEYOND",
        beyond_kind(1.0180, 1.0179, 1.0, 1.01) == "AGREED_BEYOND")
    chk("L16 sources that differ beyond the day's move are SOURCES_DISAGREE",
        beyond_kind(1.20, 1.10, 1.0, 1.10) == "SOURCES_DISAGREE"
        and beyond_kind(1.20, None, 1.0, 1.10) == "SOURCES_DISAGREE")
    chk("L17 a row that is not beyond has no beyond kind",
        beyond_kind(1.098, 1.097, 1.0, 1.10) is None
        and beyond_kind(1.001, 1.0, 1.0, 1.10) is None)

    # The verdict must print the beyond count and must not add it to "on today's path":
    # board has 6 same + 2 capped + 1 disagree over 9 movers.
    gb = {"n_rows": 9, "n_decidable": 9, "board": counts(6, over=3), "sina": counts(5, prev=2),
          "board_beyond": {"CAPPED_BY_LIMIT": 2, "AGREED_BEYOND": 0, "SOURCES_DISAGREE": 1}}
    vb = _verdict_one(gb, "X")
    chk("L18 verdict names the beyond rows and keeps them out of 'on today's path'",
        "6/9 on today's path" in vb and "3 board rows sit beyond" in vb
        and "2 with the price at the band" in vb and "1 with the sources disagreeing" in vb
        and "9/9" not in vb)
    gb2 = {"n_rows": 9, "n_decidable": 9, "board": counts(6, over=3), "sina": counts(6),
           "board_beyond": {"CAPPED_BY_LIMIT": 2, "AGREED_BEYOND": 1, "SOURCES_DISAGREE": 0}}
    chk("L19 flipping one beyond row changes the printed split",
        "3 with the price at the band" in _verdict_one(gb2, "X")
        and "0 with the sources disagreeing" in _verdict_one(gb2, "X"))

    # End to end on the live shape: capped rows are counted apart from same-session rows.
    f = build("2026-11-27",
              {"E": 0.8448, "F": 0.6105},
              {"E": {"nav": 0.8447, "nav_date": "2026-11-27"},
               "F": {"nav": 0.532, "nav_date": "2026-11-27"}},
              {"E": {"prev_close": 0.72, "last": 0.792},
               "F": {"prev_close": 0.531, "last": 0.584}})
    chk("L20 two live shapes land in different beyond buckets",
        f["rows"][0]["board_beyond"] == "CAPPED_BY_LIMIT"
        and f["rows"][1]["board_beyond"] == "SOURCES_DISAGREE"
        and f["all"]["board"]["SAME_SESSION"] == 0
        and f["all"]["board_beyond"]["CAPPED_BY_LIMIT"] == 1)

    # --- a label near a line is a cut, not a finding ----------------------------------
    # 513630 on 2026-11-27: prev 1.565, last 1.545 (-1.28%), board 1.5584 -> t = 0.33,
    # which reads "yesterday's close" by 0.02. The number must be printable.
    t = path_t(1.5584, 1.565, 1.545)
    chk("L21 a row 0.02 inside a line is flagged marginal and keeps its number",
        position(1.5584, 1.565, 1.545) == "PREV_SESSION"
        and abs(t - 0.3298) < 0.001 and margin_of(t) < MARGIN)
    chk("L22 a row far from every line is not marginal",
        margin_of(path_t(1.098, 1.0, 1.10)) > MARGIN and margin_of(None) is None)
    chk("L23 path_t refuses what position refuses",
        path_t(None, 1.0, 1.1) is None and path_t(1.05, 1.0, 1.001) is None
        and path_t(-1.0, 1.0, 1.1) is None)

    # --- a ticker only one source answered for is still a row, never a silent skip -----
    # r2214: 159655 (cross-border, priced off sina's own NAV) fell out of the face
    # entirely because the board never answered for it -- while the ticket spent 8.7%
    # on it. The union row set brings it back, and the missing board value is `NO_DATA`,
    # never a board value that agrees.
    f = build("2026-11-27", {"G": 1.05},
              {"G": {"nav": 1.0}, "H": {"nav": 1.001, "nav_date": "2026-11-26"}},
              {"G": {"prev_close": 1.0, "last": 1.1},
               "H": {"prev_close": 1.0, "last": 1.1}})
    rh = [r for r in f["rows"] if r["code"] == "H"][0]
    chk("L24 a ticker with no board row is still a row, flagged board_missing",
        len(f["rows"]) == 2 and rh["board_missing"] is True
        and rh["board_position"] == "NO_DATA" and rh["sina_position"] == "PREV_SESSION")
    chk("L25 a NO_DATA row does not inflate the denominator",
        f["all"]["n_decidable"] == 1 and f["all"]["n_board_missing"] == 1)

    tk = {"status": "ok", "ticket": "TICKET-X.json",
          "legs": [{"symbol": "G", "class": "equity", "amount_cny": 1.0},
                   {"symbol": "H", "class": "crossborder", "amount_cny": 2.0},
                   {"symbol": "Z", "class": "equity", "amount_cny": 3.0}]}
    tlegs = ticket_legs(tk, {r["code"]: r for r in f["rows"]})
    by = {l["symbol"]: l for l in tlegs}
    chk("L26 every ticket leg gets a dating status (dated / undecidable / no price)",
        by["G"]["status"] == "DATED" and by["H"]["status"] == "DATED"
        and by["Z"]["status"] == "NO_PRICE")
    v = ticket_verdict(tlegs)
    chk("L27 the ticket sentence names the legs it could not prove",
        v.startswith("TICKET: ONE_OR_MORE_LEGS_UNPROVEN") and "Z" in v
        and ticket_verdict([]).startswith("TICKET: CANNOT_VERIFY"))

    # A date field can name a day that is not a session at all (159655 prints a Saturday).
    f = build("2026-11-27", {"K": 1.05},
              {"K": {"nav": 1.0, "nav_date": "2026-11-28"},
               "L": {"nav": 1.0, "nav_date": "2026-11-27"}},
              {"K": {"prev_close": 1.0, "last": 1.1}, "L": {"prev_close": 1.0, "last": 1.1}})
    chk("L28 a source date after the board session is counted, not trusted",
        f["sina_date_after_board"] == {"n": 1, "codes": ["K"]})

    for n, ok in legs:
        print(("PASS " if ok else "FAIL ") + n)
    bad = [n for n, ok in legs if not ok]
    print("selftest %d/%d" % (len(legs) - len(bad), len(legs)))
    return 0 if not bad else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "check", "selftest"])
    ap.add_argument("--sample", type=int, default=200)
    a = ap.parse_args()
    if a.cmd == "run":
        return cmd_run(a.sample)
    if a.cmd == "check":
        return cmd_check()
    return cmd_selftest()


if __name__ == "__main__":
    sys.exit(main())

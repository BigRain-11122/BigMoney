"""ETF book -- after the swap, when do I have to look again?

r1465 priced today's re-tickering: the same NDX100 basket is sold at +23.64% / +21.26% above
IOPV under 159501 / 513100 and at +14.97% under 159513, so moving the book to the cheap
ticker buys CNY 9,762 more basket -- of which only CNY 1,540 repeats at the pair's historical
average gap and CNY 8,222 is today's episode.

That is a number on a page. The desk is holding the sheet, and the sheet does not say what
to do with the number afterwards:

    I swapped. When does this decision have to be looked at again -- and what number
    makes me look?

Two clocks answer that, and they are not the same clock:

  * decision clock -- the book re-ranks every REBAL sessions anyway; on that bar the swap is
    re-decided from scratch, so no special watch is needed there;
  * gap clock -- between two decision bars the only thing that can move is the pair's gap.
    A swap that has already been executed is a permanent fix at the average gap; it has to
    be undone only if the ticker we moved INTO stops being the cheap one, and "stops being
    cheap" is priceable: acting again costs one exchange, so the gap has to clear that toll
    before another swap is worth doing.

So the trigger is not a percentile and not a mean -- it is the cost of the exchange it would
have to make, and that cost travels with its scope (r1529/r1531):

    one exchange   = 2 sides x COST_BP  (8bp/side -> 0.16 pp)  <- the threshold, incremental
    the manoeuvre  = 4 sides x COST_BP  (8bp/side -> 0.32 pp)  <- in-and-out, cumulative

The two are published side by side and never used as each other: calling 0.16 "the round trip"
makes a desk wait for twice the gap it needs, and calling 0.32 "what this swap cost" prices
the discount at half. `--check` refuses a face that mixes the two words up.

and the perishability of today's episode is measured, not asserted: take every session whose
gap was at least half as wide as today's excess over its own mean, count the sessions until
the gap is back at the mean, and publish the median. A censored episode (still wide at the
end of the panel) is reported as censored -- never scored as zero sessions (r1230 f0).

Usage:
    python scripts/etf_book_swap_trigger.py run
    python scripts/etf_book_swap_trigger.py --check
    python scripts/etf_book_swap_trigger.py --selftest
"""

from __future__ import annotations

import argparse
import json
import os
import statistics
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import etf_book_sibling_gap as gap_face  # noqa: E402  (one implementation of the reconstruction)
import etf_book_swap_toll as swap_toll  # noqa: E402  (r1522's side counts, never retyped)

GAP_JSON = os.path.join(ROOT, "results", "etf_book_sibling_gap.json")
OUT_JSON = os.path.join(ROOT, "results", "etf_book_swap_trigger.json")
OUT_MD = os.path.join(ROOT, "results", "etf_book_swap_trigger.md")

# ---- frozen criteria (echoed into the payload; --check refuses a face that disagrees) ----
EPISODE_SHARE = 0.5     # a "comparable" session carries at least half of today's excess
TAIL_PERCENTILE = 90.0  # today counts as a tail only above this
FAST_EXPIRY = 20        # sessions; at or under one REBAL grid, an episode does not wait for it
STRUCTURAL_SHARE = 0.80  # a toll above this share of sessions is a standing condition


def cost_bp():
    """The per-side cost this book is priced at -- read from the ticket, never retyped."""
    try:
        from scripts.etf_book_order import COST_BP
        return float(COST_BP)
    except Exception:                                            # noqa: BLE001
        import etf_book_order
        return float(etf_book_order.COST_BP)


def toll_pp(bp=None):
    """Cost of ONE exchange in pp of notional: what a second swap has to clear to be worth
    doing. The side count is the r1522 constant, not a literal -- a manoeuvre is 4 sides and
    that number is published next to this one, never in its place (r1531)."""
    return round(float(swap_toll.ENTRY_SIDES) * (cost_bp() if bp is None else float(bp))
                 / 100.0, 4)


def toll_scope(bp=None):
    """r1531: the price and its scope on the same object.

    r1529 published three scopes for this one cost figure (entry 2 sides / exit 2 sides /
    trip 4 sides). The trigger only ever uses the incremental one -- the exchange it would
    have to make today -- and this face used to print that number as "the round-trip toll",
    which is the 4-side figure. A reader who takes the threshold from this section alone
    would wait for a gap twice as wide as the toll it actually pays.
    """
    cost = cost_bp() if bp is None else float(bp)
    sides = int(swap_toll.ENTRY_SIDES)
    trip_sides = sides + int(swap_toll.EXIT_SIDES)
    pp = toll_pp(cost)
    return {
        "name": "one_exchange",
        "sides": sides,
        "pp": pp,
        "question": "换这一次要付多少",
        "decision_use": "INCREMENTAL: the only cost a 'act again?' decision moves",
        "trip_sides": trip_sides,
        "trip_pp": round(trip_sides * cost / 100.0, 4),
        "trip_question": "一来一回总共多少",
        "trip_is_not_the_threshold": True,
        "why": "the exchange this desk already made is paid whether it acts again or not; an "
               "unwind pays the same exchange once more, and that total is a different number",
    }


def episodes_until_mean(rec, mean, wide):
    """Run lengths from every 'wide' session back to the mean, censoring the unhealed tail."""
    runs = []
    n = len(rec)
    i = 0
    while i < n:
        if rec[i] >= wide:
            j = i + 1
            while j < n and rec[j] > mean:
                j += 1
            runs.append({"start_date": None, "sessions": j - i, "censored": j >= n})
            i = j
        else:
            i += 1
    completed = [r["sessions"] for r in runs if not r["censored"]]
    return runs, completed


def summarize_runs(runs, completed):
    out = {"n_episodes": len(runs), "n_completed": len(completed),
           "n_censored": len(runs) - len(completed), "median_sessions": None,
           "p25_sessions": None, "p75_sessions": None, "max_sessions": None}
    if not completed:
        return out
    s = sorted(completed)
    out["median_sessions"] = float(statistics.median(s))
    out["p25_sessions"] = float(s[int(round(0.25 * (len(s) - 1)))])
    out["p75_sessions"] = float(s[int(round(0.75 * (len(s) - 1)))])
    out["max_sessions"] = float(s[-1])
    return out


def classify(today_gap, mean, window_share, expiry, percentile, source_verdict=None):
    """Five words, each one an action. Nothing here is a percentile for its own sake.

    `expiry is None` means the comparable episodes were all censored (none healed inside the
    panel). That is an unmeasured perishability, and it must not be read as "it can wait" --
    the missing-measurement disease of r1230 -- so it resolves toward acting on this bar.
    """
    toll = toll_pp()
    if today_gap is None or mean is None:
        return "CANNOT_VERIFY"
    if source_verdict is not None and source_verdict != "SWAP_SAVES":
        # the upstream face already refused this pair on its own materiality line; a gap under
        # that line is a real CNY figure but not an action (r1465's immaterial bucket)
        return "NOT_ACTIONABLE"
    if today_gap <= toll:
        return "NOT_ACTIONABLE"
    if window_share is not None and window_share >= STRUCTURAL_SHARE:
        return "WINDOW_ALWAYS_OPEN"
    if percentile is not None and percentile >= TAIL_PERCENTILE and \
            (expiry is None or expiry <= FAST_EXPIRY):
        return "ACT_ON_THIS_BAR"
    return "ACT_ON_ANY_BAR"


VERDICTS = ("ACT_ON_THIS_BAR", "ACT_ON_ANY_BAR", "WINDOW_ALWAYS_OPEN", "NOT_ACTIONABLE",
            "CANNOT_VERIFY")


def advice(word, scope=None):
    """One sentence per verdict, spelled in the scope the threshold actually has (r1531).

    The toll phrase is built from the published scope instead of being typed into a static
    string: a literal "round-trip toll" is exactly how 0.16 came to be read as 0.32.
    """
    sc = scope or toll_scope()
    pp = float(sc.get("pp") or 0.0)
    sides = int(sc.get("sides") or 0)
    trip = float(sc.get("trip_pp") or 0.0)
    one = "the toll of making the exchange (%.2f pp, %d sides)" % (pp, sides)
    whole = ("the whole manoeuvre is %.2f pp (%d sides -- the unwind pays the exchange again)"
             % (trip, int(sc.get("trip_sides") or 0)))
    return {
        "ACT_ON_THIS_BAR":
            "this episode is a tail of the pair's own history and either heals inside one "
            "rebalancing grid or was never healed inside the panel -- the one-off part does not "
            "wait for the next decision bar",
        "ACT_ON_ANY_BAR":
            "the gap clears %s but is not a perishable tail -- any bar inside the next grid "
            "may be used without paying for the delay (%s)" % (one, whole),
        "WINDOW_ALWAYS_OPEN":
            "the pair trades wider than %s on almost every session: this is a standing "
            "condition, so the swap is a permanent re-tickering and there is nothing to watch "
            "between decision bars (%s)" % (one, whole),
        "NOT_ACTIONABLE":
            "the gap does not clear %s: swapping would pay more to move than it saves, so the "
            "trigger is the gap itself (re-read on the next decision bar; %s)" % (one, whole),
        "CANNOT_VERIFY":
            "no history was readable for this pair: the trigger cannot be priced, and an absent "
            "answer is not a small gap",
    }[word]


def assess(pair):
    row = {
        "leg_symbol": pair.get("leg_symbol"),
        "sibling_symbol": pair.get("sibling_symbol"),
        "sibling_name": pair.get("sibling_name"),
        "index": pair.get("index"),
        "source_verdict": pair.get("source_verdict"),
        "today_gap_pp": pair.get("gap_today_pp"),
        "mean_gap_pp": None,
        "toll_pp": toll_pp(),
        "today_excess_pp": None,
        "window_share": None,
        "percentile": None,
        "expiry": None,
        "repeatable_gain_cny": pair.get("repeatable_gain_cny"),
        "one_off_gain_cny": pair.get("one_off_gain_cny"),
        "verdict": "CANNOT_VERIFY",
        "toll_scope": toll_scope(),
        "advice": advice("CANNOT_VERIFY"),
        "why": "",
    }
    stats = pair.get("stats") or {}
    mean = stats.get("mean_pp")
    row["mean_gap_pp"] = mean
    row["percentile"] = stats.get("today_percentile")
    files = pair.get("daily_files") or []
    if len(files) != 2 or not all(files):
        row["why"] = "the pair carries no local daily panel"
        return row
    try:
        a = gap_face.load_close(os.path.join(ROOT, files[0]))
        b = gap_face.load_close(os.path.join(ROOT, files[1]))
    except OSError as exc:
        row["why"] = "panel unreadable: %r" % (exc,)
        return row
    dates, ca, cb = gap_face.common_series(a, b)
    if len(dates) < gap_face.MIN_DAYS:
        row["why"] = "fewer than %d common sessions" % gap_face.MIN_DAYS
        return row
    g = gap_face.gap_series(ca, cb)
    rec, _offset = gap_face.reconstruct(g, pair.get("gap_today_pp"))
    if not rec:
        row["why"] = "the reconstruction is empty"
        return row
    rec_mean = statistics.fmean(rec)
    row["mean_gap_pp"] = round(rec_mean, 4)
    today = rec[-1]
    row["today_gap_pp"] = round(today, 4)
    row["today_excess_pp"] = round(today - rec_mean, 4)
    toll = row["toll_pp"]
    row["window_share"] = round(sum(1 for v in rec if v > toll) / len(rec), 4)
    row["percentile"] = gap_face.percentile_rank(rec, today)
    wide = rec_mean + max(EPISODE_SHARE * (today - rec_mean), 0.0)
    runs, completed = episodes_until_mean(rec, rec_mean, wide)
    row["expiry"] = summarize_runs(runs, completed)
    row["verdict"] = classify(today, rec_mean, row["window_share"],
                              (row["expiry"] or {}).get("median_sessions"), row["percentile"],
                              pair.get("source_verdict"))
    row["advice"] = advice(row["verdict"], row["toll_scope"])
    return row


def build():
    if not os.path.exists(GAP_JSON):
        raise SystemExit("no published gap face at %s -- run etf_book_sibling_gap.py run first"
                         % GAP_JSON)
    with open(GAP_JSON, encoding="utf-8") as fh:
        found = json.load(fh)
    rows = [assess(p) for p in (found.get("pairs") or [])]
    counts = {}
    for r in rows:
        counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1
    face = {
        "artifact": "etf_book_swap_trigger",
        "session": found.get("session"),
        "ticket": found.get("ticket"),
        "source_face": os.path.relpath(GAP_JSON, ROOT).replace(os.sep, "/"),
        "criteria": {"episode_share": EPISODE_SHARE, "tail_percentile": TAIL_PERCENTILE,
                     "fast_expiry_sessions": FAST_EXPIRY,
                     "structural_share": STRUCTURAL_SHARE,
                     "cost_bp_per_side": cost_bp(), "toll_pp": toll_pp()},
        "toll_scope": toll_scope(),
        "pairs": rows,
        "verdict_counts": counts,
        "repeatable_gain_cny": found.get("repeatable_gain_cny"),
        "one_off_gain_cny": found.get("one_off_gain_cny"),
        "recheck_rule": recheck_rule(rows, found),
        "caveats": [
            "the trigger is priced in pp of notional and compared against the toll of ONE "
            "exchange (%.2f pp, %d sides) only; the whole manoeuvre (%.2f pp, %d sides) is "
            "published next to it and is never the threshold. It does not price tracking "
            "difference, fee, size or FX-hedge policy between the two tickers"
            % (toll_pp(), int(swap_toll.ENTRY_SIDES),
               round((int(swap_toll.ENTRY_SIDES) + int(swap_toll.EXIT_SIDES)) * cost_bp()
                     / 100.0, 4),
               int(swap_toll.ENTRY_SIDES) + int(swap_toll.EXIT_SIDES)),
            "episode lengths are measured on the reconstructed gap, which inherits the single "
            "IOPV anchor of the gap face; censored episodes are reported, never scored as zero",
            "a 'window always open' reading means the pair is structurally wide, not that the "
            "swap has to be repeated: the book only has to hold it once",
        ],
    }
    return face


def recheck_rule(rows, found):
    fast = [r for r in rows if r["verdict"] == "ACT_ON_THIS_BAR"]
    if fast:
        meds = [(r["expiry"] or {}).get("median_sessions") for r in fast]
        measured = [m for m in meds if m is not None]
        one_off = format(found.get("one_off_gain_cny") or 0.0, ",.0f")
        if measured:
            head = ("act on this bar: the one-off part of %s CNY has historically healed within "
                    "a median of %.0f sessions" % (one_off, min(measured)))
        else:
            head = ("act on this bar: the one-off part of %s CNY is unmeasured -- no comparable "
                    "episode in the panel ever healed, so nothing here says the window waits"
                    % one_off)
    elif any(r["verdict"] in ("ACT_ON_ANY_BAR", "WINDOW_ALWAYS_OPEN") for r in rows):
        head = ("any bar inside the grid works: the gap is not a perishable tail"
                " (one-off part %s CNY)" % format(found.get("one_off_gain_cny") or 0.0, ",.0f"))
    else:
        head = "nothing to act on: no pair clears the toll of the exchange"
    sc = toll_scope()
    return (head + ". After execution the only number that can bring the decision back is the "
            "toll of the exchange it would have to make: re-read this face on the next decision "
            "bar, and act again only if a pair's gap exceeds %.2f pp (%d sides x %.0f bp). "
            "Getting the book back where it came from pays that same exchange once more, so the "
            "whole manoeuvre is %.2f pp (%d sides) -- that number answers 'did the discount pay "
            "for the trip', never 'may I act'."
            % (sc["pp"], sc["sides"], cost_bp(), sc["trip_pp"], sc["trip_sides"]))


def render_md(face):
    L = ["# ETF book -- after the swap, when do I have to look again?", ""]
    c = face["criteria"]
    L += ["session `%s` | ticket `%s` | source `%s`" % (face["session"], face["ticket"],
                                                       face["source_face"]), "",
          "**%s**" % face["recheck_rule"], "",
          "触发价 = **换这一次**要付的过路费 %.2f pp（%d 边 × %.0f bp/边）。这不是分位数，"
          "是「今天再动一次要付多少」。整趟一来一回是 %.2f pp（%d 边）——换回来还要再付一次，"
          "那个数只回答「这趟折扣够不够补回全部成本」，不当门槛（r1529/r1531）。"
          % (c["toll_pp"], int((face.get("toll_scope") or {}).get("sides")
                               or swap_toll.ENTRY_SIDES), c["cost_bp_per_side"],
             float((face.get("toll_scope") or {}).get("trip_pp") or 0.0),
             int((face.get("toll_scope") or {}).get("trip_sides")
                 or (swap_toll.ENTRY_SIDES + swap_toll.EXIT_SIDES))), "",
          "| 腿（书里持有） | 换到 | 今日价差 | 历史均值 | 一次性部分 | 可重复部分 | 超过触发价占比 | 这次尾部多久回均值 | 判词 |",
          "|---|---|---|---|---|---|---|---|---|"]
    for r in face["pairs"]:
        exp = r.get("expiry") or {}
        med = exp.get("median_sessions")
        exp_s = ("—" if med is None else "中位 %.0f 次（%d 例，%d 未愈合）"
                 % (med, exp.get("n_completed") or 0, exp.get("n_censored") or 0))
        L.append("| %s | %s %s | %s pp | %s pp | %s | %s | %s | %s | **%s** |"
                 % (r["leg_symbol"], r["sibling_symbol"], r.get("sibling_name") or "",
                    ("%+.2f" % r["today_gap_pp"]) if r.get("today_gap_pp") is not None else "?",
                    ("%+.2f" % r["mean_gap_pp"]) if r.get("mean_gap_pp") is not None else "?",
                    ("¥%s" % format(r["one_off_gain_cny"], ",.0f")) if r.get("one_off_gain_cny") else "—",
                    ("¥%s" % format(r["repeatable_gain_cny"], ",.0f")) if r.get("repeatable_gain_cny") else "—",
                    ("%.0f%%" % (100.0 * r["window_share"])) if r.get("window_share") is not None else "?",
                    exp_s, r["verdict"]))
    L.append("")
    for r in face["pairs"]:
        L.append("- %s → %s：%s" % (r["leg_symbol"], r["sibling_symbol"], r["advice"]))
    L += ["", "## 读法", "",
          "- 决策时钟和价差时钟是两块表。书每 20 个交易日重排一次，那一天换票会被重新决定；"
          "两次决策之间，唯一能动的是价差，所以真正的「再看一次」不是日历而是价格。",
          "- 已经换过去的票不需要天天看：每一对的均值（%s）就是「这只票历来更便宜多少」，"
          "只有它自己变成了贵的那一只、且价差越过来回成本，才需要再动。"
          % "、".join("%s→%s %+.2f pp" % (r["leg_symbol"], r["sibling_symbol"], r["mean_gap_pp"])
                     for r in face["pairs"] if r.get("mean_gap_pp") is not None),
          "- 「尾部多久回均值」是实测：拿每一次跟今天同等宽的价差，数它回到自己均值用了几个交易日；"
          "还没愈合的算作 censored 单独列出，不当 0 次。",
          "- 出处：`scripts/etf_book_swap_trigger.py`；上游 `%s`（同一份重建，不另算一遍）。"
          % face["source_face"], ""]
    L += ["## 不能从这张面读出来的", ""]
    for cav in face["caveats"]:
        L.append("- %s" % cav)
    L.append("")
    return "\n".join(L)


CROSS_WORDS = ("round-trip", "round trip", "roundtrip", "来回成本", "往返")


def label_violations(face):
    """r1531: the scope word next to the number has to agree with the number.

    r1529 published the three scopes and named this exact defect in a separate face
    (`VALUE_IS_ONE_EXCHANGE_LABEL_SAYS_ROUND_TRIP`); the trigger kept printing the old word in
    its own sentences, so a reader who only opened this section still took 0.16 for 0.32.
    Measured, not asserted: --check and the selftest both call this, and the selftest feeds it
    a tampered copy so a guard that stopped firing is caught.
    """
    bad = []
    sc = face.get("toll_scope") or {}
    if not sc:
        return ["toll_scope missing: the threshold carries no scope"]
    try:
        pp = float(sc.get("pp"))
        trip = float(sc.get("trip_pp"))
        sides = int(sc.get("sides"))
        trip_sides = int(sc.get("trip_sides"))
    except (TypeError, ValueError):
        return ["toll_scope is not numeric: %r" % (sc,)]
    if abs(pp - toll_pp()) > 1e-9:
        bad.append("scope.pp %.4f != price of one exchange %.4f" % (pp, toll_pp()))
    if abs(trip - 2.0 * pp) > 1e-9:
        bad.append("trip_pp %.4f is not twice the exchange %.4f" % (trip, pp))
    if sides <= 0 or trip_sides != 2 * sides:
        bad.append("side counts disagree: %d and %d" % (sides, trip_sides))
    if sc.get("trip_is_not_the_threshold") is not True:
        bad.append("trip_is_not_the_threshold must be true explicitly")
    if abs(pp - trip) > 1e-9:
        strings = [face.get("recheck_rule") or ""] + list(face.get("caveats") or [])
        for r in face.get("pairs") or []:
            strings.append(r.get("advice") or "")
        for s in strings:
            low = s.lower()
            hit = [w for w in CROSS_WORDS if w in low]
            if hit:
                bad.append("a sentence calls the %.2f pp exchange a %r: %r"
                           % (pp, hit[0], s[:80]))
                break
    return bad


def write_out(face):
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(face, fh, ensure_ascii=False, indent=1)
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write(render_md(face))
    return OUT_JSON


def run():
    face = build()
    write_out(face)
    print("verdict_counts=%s" % face["verdict_counts"])
    print("recheck: %s" % face["recheck_rule"])
    print("wrote %s" % os.path.relpath(OUT_JSON, ROOT).replace(os.sep, "/"))
    return 0


def check():
    """Re-derive the whole face from the panels and refuse a payload that disagrees."""
    if not os.path.exists(OUT_JSON):
        print("CHECK_FAIL: no face at %s" % OUT_JSON)
        return 1
    with open(OUT_JSON, encoding="utf-8") as fh:
        published = json.load(fh)
    fresh = build()
    bad = []
    if published.get("criteria") != fresh.get("criteria"):
        bad.append("criteria")
    if published.get("recheck_rule") != fresh.get("recheck_rule"):
        bad.append("recheck_rule")
    if published.get("toll_scope") != fresh.get("toll_scope"):
        bad.append("toll_scope")
    bad += label_violations(published)
    pr = {p["leg_symbol"]: p for p in published.get("pairs") or []}
    fr = {p["leg_symbol"]: p for p in fresh.get("pairs") or []}
    if set(pr) != set(fr):
        bad.append("pair set")
    for k in sorted(set(pr) & set(fr)):
        for field in ("verdict", "toll_pp", "today_gap_pp", "mean_gap_pp", "window_share"):
            if pr[k].get(field) != fr[k].get(field):
                bad.append("%s.%s" % (k, field))
        pe = (pr[k].get("expiry") or {})
        fe = (fr[k].get("expiry") or {})
        if pe.get("median_sessions") != fe.get("median_sessions"):
            bad.append("%s.expiry" % k)
    if bad:
        print("CHECK_FAIL: %s" % ", ".join(bad))
        return 1
    print("CHECK_OK: %d pair(s), threshold %.2f pp = one exchange (%d sides); manoeuvre "
          "%.2f pp (%d sides) is published, not the threshold"
          % (len(fr), toll_pp(), int(swap_toll.ENTRY_SIDES),
             float(fresh["toll_scope"]["trip_pp"]), int(fresh["toll_scope"]["trip_sides"])))
    return 0


def selftest():
    chk = []

    def ok(name, cond, detail=""):
        chk.append((name, bool(cond), detail))

    # the toll is derived from the ticket's own cost, not retyped
    ok("toll is twice the per-side cost", abs(toll_pp(8.0) - 0.16) < 1e-9, toll_pp(8.0))
    ok("toll scales with the cost input", abs(toll_pp(20.0) - 0.40) < 1e-9, toll_pp(20.0))

    # run lengths: heal, censor, and never score a censored episode as zero
    rec = [0.0, 2.0, 2.0, 0.0, 0.0, 2.0, 2.0]
    runs, completed = episodes_until_mean(rec, 0.0, 1.0)
    s = summarize_runs(runs, completed)
    ok("two wide episodes found", s["n_episodes"] == 2, s)
    ok("the healed one is 2 sessions", completed and completed[0] == 2, completed)
    ok("the unhealed tail is censored, not zero",
       s["n_censored"] == 1 and completed == [2], s)
    ok("median is over completed only", s["median_sessions"] == 2.0, s)

    runs2, comp2 = episodes_until_mean([1.5, 1.5], 0.0, 1.0)
    s2 = summarize_runs(runs2, comp2)
    ok("all-censored reads as no median, not as fast", s2["median_sessions"] is None, s2)

    # the four words are actions
    ok("under the toll is not actionable", classify(0.10, 0.83, 0.99, 3.0, 100.0) == "NOT_ACTIONABLE")
    ok("a standing wide pair is not urgent",
       classify(8.67, 0.83, 0.95, 3.0, 100.0) == "WINDOW_ALWAYS_OPEN",
       classify(8.67, 0.83, 0.95, 3.0, 100.0))
    ok("a tail that heals inside the grid acts on this bar",
       classify(8.67, 0.83, 0.40, 5.0, 99.0) == "ACT_ON_THIS_BAR",
       classify(8.67, 0.83, 0.40, 5.0, 99.0))
    ok("a slow episode is not urgent even at the tail",
       classify(8.67, 0.83, 0.40, 80.0, 99.0) == "ACT_ON_ANY_BAR",
       classify(8.67, 0.83, 0.40, 80.0, 99.0))
    ok("an absent reading never becomes NOT_ACTIONABLE",
       classify(None, None, None, None, None) == "CANNOT_VERIFY")
    ok("a pair the upstream face called immaterial is not an action",
       classify(0.19, -0.08, 0.40, 3.0, 64.0, "GAP_IMMATERIAL") == "NOT_ACTIONABLE",
       classify(0.19, -0.08, 0.40, 3.0, 64.0, "GAP_IMMATERIAL"))
    ok("unmeasured perishability resolves toward acting, never toward waiting",
       classify(8.67, 0.83, 0.40, None, 100.0) == "ACT_ON_THIS_BAR",
       classify(8.67, 0.83, 0.40, None, 100.0))

    # every verdict carries an advice line (no word without an action), and that line is
    # spelled in the scope the threshold actually has (r1531)
    sc = toll_scope()
    for w in VERDICTS:
        ok("advice present for %s" % w, bool(advice(w, sc)))

    # the two prices are different quantities, and the side counts come from r1522
    ok("the threshold is one exchange, not the manoeuvre",
       abs(sc["pp"] - toll_pp()) < 1e-9 and abs(sc["trip_pp"] - 2 * sc["pp"]) < 1e-9, sc)
    ok("the manoeuvre is four sides",
       sc["trip_sides"] == swap_toll.ENTRY_SIDES + swap_toll.EXIT_SIDES, sc)
    ok("the scope block says the manoeuvre is never the threshold",
       sc["trip_is_not_the_threshold"] is True, sc)

    # the label guard fires on a face that calls one exchange a round trip, and stays quiet on
    # the face this script builds -- a guard that never fires is not a guard
    good = {"toll_scope": dict(sc),
            "recheck_rule": "act again only if a pair's gap exceeds %.2f pp (%d sides)"
                            % (sc["pp"], sc["sides"]),
            "caveats": [], "pairs": [{"advice": advice("ACT_ON_ANY_BAR", sc)}]}
    ok("the guard passes the face this script builds", label_violations(good) == [],
       label_violations(good))
    tampered = {"toll_scope": dict(sc),
                "recheck_rule": "act again only if the gap clears the round-trip toll",
                "caveats": [], "pairs": [{"advice": advice("ACT_ON_ANY_BAR", sc)}]}
    ok("the guard catches 'round-trip' on a %.2f pp threshold" % sc["pp"],
       bool(label_violations(tampered)), label_violations(tampered))
    tampered2 = {"toll_scope": dict(sc), "recheck_rule": "ok", "caveats": [],
                 "pairs": [{"advice": "the gap does not clear the round trip"}]}
    ok("the guard catches the same words in a pair's advice", bool(label_violations(tampered2)),
       label_violations(tampered2))
    tripped = dict(sc)
    tripped["trip_pp"] = sc["pp"]          # the manoeuvre printed as one exchange
    tampered3 = {"toll_scope": tripped, "recheck_rule": "ok", "caveats": [], "pairs": []}
    ok("the guard catches a manoeuvre priced as one exchange", bool(label_violations(tampered3)),
       label_violations(tampered3))

    # the published face, if present, must reproduce
    if os.path.exists(OUT_JSON):
        rc = check()
        ok("published face re-derives", rc == 0, "check rc=%d" % rc)

    bad = [(n, d) for n, c, d in chk if not c]
    for n, c, d in chk:
        print(("PASS " if c else "FAIL ") + n + ("" if c else " :: %r" % (d,)))
    print("%d/%d" % (len(chk) - len(bad), len(chk)))
    return 0 if not bad else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("run")
    sub.add_parser("check")
    sub.add_parser("selftest")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest or args.cmd == "selftest":
        return selftest()
    if args.check or args.cmd == "check":
        raise SystemExit(check())
    return run()


if __name__ == "__main__":
    raise SystemExit(main())
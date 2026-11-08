# -*- coding: utf-8 -*-
"""E585 -- is the cash leg on a published ticket priced on the bar that ticket names?

r1612 (E583) showed the *share* legs on the published tickets were priced on the 2026-10-14
decision bar while the files were named 10-23..10-28.  Every one of those tickets also carries a
``cash_leg`` block, and it looks like a price:

    {"source": "data/repo_daily/GC001.csv", "mean_accrual_ann_pct": 2.09, "missing_bar_steps": 0}

This study asks the same question of that block.  ``etf_book_order.run`` computes it as
``BW.repo_daily_cash(idx, rates).mean() * 252 * 100`` where ``idx`` is the whole live window, so
what the block publishes is an **expanding-window mean of GC001 since 2020-01-01**, not the rate
quoted on the bar the ticket is named after, and not the accrual a follower would earn on that
bar.

Per ticket it publishes:

  named_bar                        the bar the file name carries
  published_mean_accrual_ann_pct    what the ticket prints
  rederived_window_mean_ann_pct     the same number rebuilt from the repo panel over the
                                    window 2020-01-01..that ticket's own cutoff
  repo_number_on_named_bar          the GC001 close quoted ON the bar the file names
  repo_number_on_decision_bar       the GC001 close quoted on the decision bar
  published_agrees_with_window_end  whether the printed number is the window mean at all
  class                             the_number_is_the_bar_it_names /
                                    the_number_is_the_whole_window_mean /
                                    no_cash_leg_block / named_bar_not_on_the_repo_panel /
                                    the_number_matches_neither_the_bar_nor_the_window

and two money columns, because the two readings imply different income:

  accrual_one_bar_cny_at_bar_rate        cash_amount * rate_on_named_bar / 100 / 252
  accrual_one_bar_cny_at_published_rate  cash_amount * published_mean / 100 / 252

Plus the silent gap: ``repo_daily_cash`` accrues **nothing** on a step with no quote and counts it
in ``missing_bar_steps``.  The newest ticket carries 7 such steps because the repo panel (a bm-a
lane) stops a week behind the ETF panel.  Each is published with its upper-bound CNY cost at the
last quoted rate -- a bound, not a measurement of what would have accrued.

  python scripts/e585_cash_leg_pricing.py build
  python scripts/e585_cash_leg_pricing.py check
  python scripts/e585_cash_leg_pricing.py verify
  python scripts/e585_cash_leg_pricing.py selftest

Output: results/state_tilt/CASHLEGPRICE-<panel cutoff>.json + cashlegprice_latest.json
Read-only over the ticket files and the repo panel.  No ticket is rewritten; no ledger row is
booked; this says nothing about the returns of the book.
"""
from __future__ import annotations

import glob
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
TICKET_DIR = os.path.join(ROOT, "results", "etf_book_order")
REPO_PATH = os.path.join(ROOT, "data", "repo_daily", "GC001.csv")

# the window the producer actually feeds into the mean (etf_book_order.run: idx starts on the
# engine grid, which starts 2020-01-01)
WINDOW_START = "2020-01-01"
TOL_PP = 0.02          # 0.02 pp -- published values are rounded to 3 dp
DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")

C_OWN_BAR = "the_number_is_the_bar_it_names"
C_WINDOW = "the_number_is_the_whole_window_mean"
C_NO_BLOCK = "no_cash_leg_block"
C_NO_PANEL = "named_bar_not_on_the_repo_panel"
C_NEITHER = "the_number_matches_neither_the_bar_nor_the_window"
CLASSES = (C_OWN_BAR, C_WINDOW, C_NO_BLOCK, C_NO_PANEL, C_NEITHER)


def _read_json(path):
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def tx_date(x):
    import pandas as pd
    return pd.Timestamp(x)


def load_rates(path=REPO_PATH):
    import pandas as pd
    df = pd.read_csv(path)
    d = pd.to_datetime(df["date"])
    s = pd.Series(df["close"].astype(float).to_numpy(), index=d)
    return s[~s.index.duplicated(keep="last")].sort_index()


def window_index(close):
    import pandas as pd
    return close.index[close.index >= pd.Timestamp(WINDOW_START)]


def window_mean(idx, rates):
    """Mean annualised accrual over ``idx`` using the repo leg's own accounting."""
    from scripts import etf_phase_beta_window as BW
    if idx is None or len(idx) == 0:
        return None, None
    rf, missing = BW.repo_daily_cash(idx, rates)
    return round(float(rf.mean() * 252.0) * 100.0, 4), int(missing)


def _isnan(v):
    try:
        return v != v
    except Exception:
        return False


def rate_on(rates, bar):
    import pandas as pd
    if bar is None:
        return None
    try:
        ts = pd.Timestamp(bar)
    except Exception:
        return None
    if ts not in rates.index:
        return None
    v = rates.get(ts)
    if v is None or _isnan(v):
        return None
    return round(float(v), 4)


def last_rate_at_or_before(rates, bar):
    import pandas as pd
    ts = pd.Timestamp(bar)
    sub = rates[rates.index <= ts]
    if not len(sub):
        return None
    return round(float(sub.iloc[-1]), 4)


# --------------------------------------------------------------------------- #
# per ticket
# --------------------------------------------------------------------------- #

def named_bar_of(path):
    m = DATE_RE.search(os.path.basename(path))
    return m.group(1) if m else None


def analyse(path, close_index, rates, mean_cache):
    d = _read_json(path)
    tk = d.get("ticket") or {}
    named = named_bar_of(path)
    cutoff = d.get("evidence_cutoff")
    block = d.get("cash_leg") if isinstance(d.get("cash_leg"), dict) else None
    nav = tk.get("nav")
    cash_amount = tk.get("cash_amount")
    cash_weight = tk.get("cash_weight")
    row = {
        "file": os.path.basename(path),
        "named_bar": named,
        "decision_bar": d.get("book_decided_at"),
        "ticket_cutoff": cutoff,
        "published_mean_accrual_ann_pct": None,
        "published_missing_bar_steps": None,
        "window_start": WINDOW_START,
        "window_bars": None,
        "rederived_window_mean_ann_pct": None,
        "rederived_missing_bar_steps": None,
        "published_agrees_with_window_end": False,
        "repo_number_on_named_bar": rate_on(rates, named),
        "repo_number_on_decision_bar": rate_on(rates, d.get("book_decided_at")),
        "published_over_bar_rate": None,
        "nav": nav,
        "cash_weight": cash_weight,
        "cash_amount": cash_amount,
        "accrual_one_bar_cny_at_bar_rate": None,
        "accrual_one_bar_cny_at_published_rate": None,
        "unaccrued_steps_upper_bound": None,
        "unaccrued_cny_upper_bound": None,
        "class": None,
    }
    if block is not None:
        row["published_mean_accrual_ann_pct"] = block.get("mean_accrual_ann_pct")
        row["published_missing_bar_steps"] = block.get("missing_bar_steps")
    if cutoff:
        if cutoff not in mean_cache:
            import pandas as pd
            sub = close_index[close_index <= pd.Timestamp(cutoff)]
            mean_cache[cutoff] = (len(sub),) + window_mean(sub, rates)
        bars, m, miss = mean_cache[cutoff]
        row["window_bars"] = bars
        row["rederived_window_mean_ann_pct"] = m
        row["rederived_missing_bar_steps"] = miss
    pub = row["published_mean_accrual_ann_pct"]
    if pub is not None and row["rederived_window_mean_ann_pct"] is not None:
        row["published_agrees_with_window_end"] = abs(
            float(pub) - row["rederived_window_mean_ann_pct"]) <= TOL_PP

    bar_rate = row["repo_number_on_named_bar"]
    if pub is not None and bar_rate:
        row["published_over_bar_rate"] = round(float(pub) / float(bar_rate), 3)
    if cash_amount:
        if bar_rate:
            row["accrual_one_bar_cny_at_bar_rate"] = round(
                float(cash_amount) * float(bar_rate) / 100.0 / 252.0, 2)
        if pub is not None:
            row["accrual_one_bar_cny_at_published_rate"] = round(
                float(cash_amount) * float(pub) / 100.0 / 252.0, 2)
    miss = row["rederived_missing_bar_steps"]
    if cash_amount and miss and cutoff:
        last = last_rate_at_or_before(rates, cutoff)
        if last:
            row["unaccrued_steps_upper_bound"] = int(miss)
            row["unaccrued_cny_upper_bound"] = round(
                float(cash_amount) * float(last) / 100.0 / 252.0 * int(miss), 2)

    if block is None:
        row["class"] = C_NO_BLOCK
    elif bar_rate is None:
        row["class"] = C_NO_PANEL
    elif abs(float(pub) - float(bar_rate)) <= TOL_PP:
        row["class"] = C_OWN_BAR
    elif row["published_agrees_with_window_end"]:
        row["class"] = C_WINDOW
    else:
        row["class"] = C_NEITHER
    return row


# --------------------------------------------------------------------------- #
# summary / verdict
# --------------------------------------------------------------------------- #

def summarise(rows, repo_last_bar=None):
    published = [r["published_mean_accrual_ann_pct"] for r in rows
                 if r.get("published_mean_accrual_ann_pct") is not None]
    windowed = [r["rederived_window_mean_ann_pct"] for r in rows
                if r.get("rederived_window_mean_ann_pct") is not None]
    barrates = [r["repo_number_on_named_bar"] for r in rows
                if r.get("repo_number_on_named_bar") is not None]
    ratios = [r["published_over_bar_rate"] for r in rows
              if r.get("published_over_bar_rate") is not None]
    with_block = [r for r in rows if r.get("published_mean_accrual_ann_pct") is not None]
    gaps = [r for r in rows if (r.get("unaccrued_cny_upper_bound") or 0) > 0]
    newest = None
    if rows:
        dated = [r for r in rows if r.get("ticket_cutoff")]
        if dated:
            newest = max(dated, key=lambda r: r["ticket_cutoff"])
    return {
        "tickets_total": len(rows),
        "tickets_with_a_cash_leg_block": len(with_block),
        "tickets_whose_number_is_the_bar_rate": sum(1 for r in rows if r["class"] == C_OWN_BAR),
        "tickets_whose_number_is_the_window_mean": sum(1 for r in rows if r["class"] == C_WINDOW),
        "tickets_with_no_cash_leg_block": sum(1 for r in rows if r["class"] == C_NO_BLOCK),
        "tickets_whose_bar_is_not_on_the_repo_panel": sum(
            1 for r in rows if r["class"] == C_NO_PANEL),
        "tickets_matching_neither": sum(1 for r in rows if r["class"] == C_NEITHER),
        "published_mean_min": min(published) if published else None,
        "published_mean_max": max(published) if published else None,
        "published_mean_spread_bp": (round(100.0 * (max(published) - min(published)), 2)
                                     if published else None),
        "window_mean_min": min(windowed) if windowed else None,
        "window_mean_max": max(windowed) if windowed else None,
        "window_mean_spread_bp": (round(100.0 * (max(windowed) - min(windowed)), 2)
                                  if windowed else None),
        "repo_number_on_named_bar_min": min(barrates) if barrates else None,
        "repo_number_on_named_bar_max": max(barrates) if barrates else None,
        "bar_rate_spread_bp": (round(100.0 * (max(barrates) - min(barrates)), 2)
                               if barrates else None),
        "worst_published_over_bar_rate": max(ratios) if ratios else None,
        "tickets_with_unaccrued_steps": len(gaps),
        "newest_ticket": newest.get("file") if newest else None,
        "newest_ticket_missing_steps": (newest.get("unaccrued_steps_upper_bound")
                                        if newest else None),
        "newest_ticket_unaccrued_cny_upper_bound": (newest.get("unaccrued_cny_upper_bound")
                                                    if newest else None),
        "repo_panel_last_bar": repo_last_bar,
    }


def _verdict(s):
    if not s["tickets_total"]:
        return "no_published_ticket_to_measure"
    if s["tickets_with_a_cash_leg_block"] == 0:
        return "no_ticket_carries_a_cash_leg_block"
    if s["tickets_whose_number_is_the_bar_rate"] == s["tickets_with_a_cash_leg_block"]:
        return "the_cash_leg_is_priced_on_the_bar_each_ticket_names"
    return "the_cash_leg_number_is_a_window_mean_not_a_priced_leg"


def _verdict_line(s):
    if not s["tickets_total"]:
        return "no published ticket on disk, so this study has no population"
    if not s["tickets_with_a_cash_leg_block"]:
        return "none of the %d tickets on disk carries a cash_leg block" % s["tickets_total"]
    missing = (s["newest_ticket_missing_steps"] or 0)
    return ("%d of %d tickets print a cash-leg accrual of %.3f%%..%.3f%%/yr, and that number is "
            "the mean of GC001 over the whole %s..cutoff window -- it moves only %.1fbp when "
            "later tickets append bars, while the rate quoted on the bars those tickets name "
            "runs %.3f%%..%.3f%% (%.1fbp apart) wherever the repo panel reaches that bar (%d of "
            "the %d with a block names a bar past the panel's last quote, %s); the printed value "
            "is up to %.2fx the rate on the bar it sits beside, and the newest ticket (%s) "
            "accrues exactly nothing over %d steps, an unaccrued upper bound of %.2f CNY"
            % (s["tickets_with_a_cash_leg_block"], s["tickets_total"],
               s["published_mean_min"] or 0.0, s["published_mean_max"] or 0.0, WINDOW_START,
               s["window_mean_spread_bp"] or 0.0,
               s["repo_number_on_named_bar_min"] or 0.0,
               s["repo_number_on_named_bar_max"] or 0.0, s["bar_rate_spread_bp"] or 0.0,
               s["tickets_whose_bar_is_not_on_the_repo_panel"],
               s["tickets_with_a_cash_leg_block"], s["repo_panel_last_bar"],
               s["worst_published_over_bar_rate"] or 0.0, s["newest_ticket"],
               missing, s["newest_ticket_unaccrued_cny_upper_bound"] or 0.0))


# --------------------------------------------------------------------------- #
# build / check / verify
# --------------------------------------------------------------------------- #

def build(write=True):
    from scripts import etf_composite_pf as F
    close, _openp, _amt, _feats = F.build_panel()
    cutoff = str(close.index[-1].date())
    rates = load_rates()
    widx = window_index(close)
    cache = {}
    paths = sorted(glob.glob(os.path.join(TICKET_DIR, "TICKET-*.json")))
    rows = [analyse(p, widx, rates, cache) for p in paths]
    s = summarise(rows, str(rates.index[-1].date()) if len(rates) else None)
    face = {
        "study": "E585_cash_leg_pricing",
        "generated_by": "scripts/e585_cash_leg_pricing.py",
        "machine": "bm-b",
        "dept": "research+engineering",
        "evidence_cutoff": cutoff,
        "rule": ("the named bar is the date in the ticket file name; the window is "
                 "2020-01-01..the ticket's own evidence_cutoff, which is what "
                 "etf_book_order.run feeds to BW.repo_daily_cash; a published accrual is "
                 "called a price only if it equals the GC001 quote on that bar"),
        "rows": rows,
        "summary": s,
        "verdict": _verdict(s),
        "verdict_line": _verdict_line(s),
    }
    if write:
        os.makedirs(OUTDIR, exist_ok=True)
        body = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True) + "\n"
        with io.open(os.path.join(OUTDIR, "CASHLEGPRICE-%s.json" % cutoff), "w",
                     encoding="utf-8", newline="\n") as fh:
            fh.write(body)
        with io.open(os.path.join(OUTDIR, "cashlegprice_latest.json"), "w",
                     encoding="utf-8", newline="\n") as fh:
            fh.write(body)
    return face


def face_problems(face):
    p = []
    rows = face.get("rows")
    if not isinstance(rows, list) or not rows:
        return ["the face carries no ticket rows"]
    s = face.get("summary") or {}
    for r in rows:
        if r.get("class") not in CLASSES:
            p.append("%s: unknown class %r" % (r.get("file"), r.get("class")))
        pub = r.get("published_mean_accrual_ann_pct")
        rd = r.get("rederived_window_mean_ann_pct")
        bar = r.get("repo_number_on_named_bar")
        if r.get("class") == C_WINDOW:
            if pub is None or rd is None or abs(float(pub) - float(rd)) > TOL_PP:
                p.append("%s: called a window mean while the printed number is not it"
                         % r.get("file"))
            if bar is not None and abs(float(pub) - float(bar)) <= TOL_PP:
                p.append("%s: called a window mean while it equals the bar's own rate"
                         % r.get("file"))
        if r.get("class") == C_OWN_BAR:
            if pub is None or bar is None or abs(float(pub) - float(bar)) > TOL_PP:
                p.append("%s: called the bar's own rate while the numbers disagree"
                         % r.get("file"))
        if r.get("class") == C_NO_BLOCK and pub is not None:
            p.append("%s: called no-block while it publishes an accrual" % r.get("file"))
        ratio = r.get("published_over_bar_rate")
        if ratio is not None and pub is not None and bar:
            want = round(float(pub) / float(bar), 3)
            if abs(want - ratio) > 1e-6:
                p.append("%s: the published-over-bar ratio does not re-derive" % r.get("file"))
        a_bar = r.get("accrual_one_bar_cny_at_bar_rate")
        a_pub = r.get("accrual_one_bar_cny_at_published_rate")
        ca = r.get("cash_amount")
        if ca and bar and a_bar is not None:
            want = round(float(ca) * float(bar) / 100.0 / 252.0, 2)
            if abs(want - a_bar) > 1e-6:
                p.append("%s: the one-bar accrual at the bar rate does not re-derive"
                         % r.get("file"))
        if ca and pub is not None and a_pub is not None:
            want = round(float(ca) * float(pub) / 100.0 / 252.0, 2)
            if abs(want - a_pub) > 1e-6:
                p.append("%s: the one-bar accrual at the published rate does not re-derive"
                         % r.get("file"))
        miss = r.get("unaccrued_steps_upper_bound")
        if miss is not None and r.get("rederived_missing_bar_steps") is not None:
            if int(miss) != int(r["rederived_missing_bar_steps"]):
                p.append("%s: the unaccrued step count is not the window's missing count"
                         % r.get("file"))
    if s.get("tickets_total") != len(rows):
        p.append("the summary ticket count does not match the published rows")
    covered = (s.get("tickets_whose_number_is_the_bar_rate", 0)
               + s.get("tickets_whose_number_is_the_window_mean", 0)
               + s.get("tickets_with_no_cash_leg_block", 0)
               + s.get("tickets_whose_bar_is_not_on_the_repo_panel", 0)
               + s.get("tickets_matching_neither", 0))
    if covered != len(rows):
        p.append("the classes do not cover every ticket")
    if (s.get("tickets_with_a_cash_leg_block", 0)
            != s.get("tickets_whose_number_is_the_bar_rate", 0)
            + s.get("tickets_whose_number_is_the_window_mean", 0)
            + s.get("tickets_matching_neither", 0)
            + s.get("tickets_whose_bar_is_not_on_the_repo_panel", 0)):
        p.append("the with-block count does not re-derive from the classes")
    return p


def check():
    face = _read_json(os.path.join(OUTDIR, "cashlegprice_latest.json"))
    problems = face_problems(face)
    for x in problems:
        print("CHECK FAIL %s" % x)
    if not problems:
        print("CHECK PASS %s" % face.get("verdict_line"))
    return 0 if not problems else 1


def verify():
    published = _read_json(os.path.join(OUTDIR, "cashlegprice_latest.json"))
    fresh = build(write=False)
    problems = face_problems(published)
    for key in ("verdict", "verdict_line", "evidence_cutoff"):
        if fresh.get(key) != published.get(key):
            problems.append("%s drifted between the published face and a live rebuild" % key)
    if (fresh.get("summary") or {}) != (published.get("summary") or {}):
        problems.append("the summary drifted between the published face and a live rebuild")
    for a, b in zip(fresh.get("rows") or [], published.get("rows") or []):
        if (a.get("file"), a.get("class"), a.get("published_mean_accrual_ann_pct"),
                a.get("repo_number_on_named_bar")) != (
                b.get("file"), b.get("class"), b.get("published_mean_accrual_ann_pct"),
                b.get("repo_number_on_named_bar")):
            problems.append("%s: the class or the two numbers changed on a live rebuild"
                            % a.get("file"))
    for x in problems:
        print("VERIFY FAIL %s" % x)
    if not problems:
        print("VERIFY PASS %d tickets re-derived against the repo panel"
              % len(published.get("rows") or []))
    return 0 if not problems else 1


# --------------------------------------------------------------------------- #
# selftest -- closed form, no panel, no disk
# --------------------------------------------------------------------------- #
def selftest():
    import pandas as pd

    ok = []

    def eq(name, got, want):
        ok.append((name, got == want, "%r != %r" % (got, want)))

    def near(name, got, want, tol=1e-6):
        ok.append((name, got is not None and abs(got - want) <= tol,
                   "%r != %r" % (got, want)))

    # a window of five bars, no weekend gaps larger than the fixture says
    idx = pd.to_datetime(["2020-01-02", "2020-01-03", "2020-01-06", "2020-01-07", "2020-01-08"])
    rates = pd.Series([2.0, 2.0, 2.0, 1.0], index=idx[1:])  # no quote on the first bar

    m, miss = window_mean(idx, rates)
    # steps: 01-02->01-03 (rate 2.0), 01-03->01-06 (3 calendar days, 2.0), 01-06->01-07 (1.0),
    #        01-07->01-08 (1.0); first bar accrues 0
    from scripts import etf_phase_beta_window as BW
    rf, m2 = BW.repo_daily_cash(idx, rates)
    near("the window mean uses the repo leg's own accounting",
         m, round(float(rf.mean() * 252.0) * 100.0, 4), 1e-9)
    eq("the window's missing count comes from the repo leg", miss, m2)

    # rate lookups
    eq("a bar that is on the repo panel returns its quote", rate_on(rates, "2020-01-03"), 2.0)
    eq("a bar that the repo panel does not carry returns None",
       rate_on(rates, "2020-01-02"), None)
    eq("an unparsable bar returns None", rate_on(rates, "not-a-date"), None)
    eq("the last quote at or before a bar is found", last_rate_at_or_before(rates, "2020-01-08"),
       1.0)
    eq("a bar that carries its own quote returns that quote, not the previous one",
       last_rate_at_or_before(rates, "2020-01-07"), 2.0)

    # a ticket whose printed number equals the bar's own quote -- the clean class
    row_own = {"file": "TICKET-2020-01-03.json", "named_bar": "2020-01-03",
               "ticket_cutoff": "2020-01-03", "published_mean_accrual_ann_pct": 2.0,
               "rederived_window_mean_ann_pct": 1.5, "repo_number_on_named_bar": 2.0,
               "repo_number_on_decision_bar": None, "cash_amount": 100000.0, "nav": 1000000.0,
               "class": C_OWN_BAR}
    s = summarise([row_own])
    eq("a printed number equal to the bar's quote is classed as the bar's",
       s["tickets_whose_number_is_the_bar_rate"], 1)

    # the same fixture with the number equal to the window mean instead
    row_win = dict(row_own, published_mean_accrual_ann_pct=1.5,
                   rederived_window_mean_ann_pct=1.5, repo_number_on_named_bar=1.0)
    row_win["class"] = C_WINDOW
    s2 = summarise([row_win])
    eq("a printed number equal to the window mean is classed as the window mean",
       s2["tickets_whose_number_is_the_window_mean"], 1)
    eq("the mixed population verdict names the window mean",
       _verdict(summarise([row_own, row_win])),
       "the_cash_leg_number_is_a_window_mean_not_a_priced_leg")
    eq("an all-bar-rate population flips the verdict",
       _verdict(summarise([row_own])), "the_cash_leg_is_priced_on_the_bar_each_ticket_names")
    eq("an empty population has its own verdict", _verdict(summarise([])),
       "no_published_ticket_to_measure")

    # a fixture population through the one real code path
    import tempfile
    tmpdir = tempfile.mkdtemp(prefix="e585_selftest_")
    paths = []
    bodies = [
        {"ticket": {"nav": 1000000.0, "cash_amount": 100000.0, "cash_weight": 0.1},
         "book_decided_at": "2020-01-03", "evidence_cutoff": "2020-01-03",
         "cash_leg": {"source": "x", "mean_accrual_ann_pct": 2.0, "missing_bar_steps": 0}},
        {"ticket": {"nav": 1000000.0, "cash_amount": 100000.0, "cash_weight": 0.1},
         "book_decided_at": "2020-01-03", "evidence_cutoff": "2020-01-08",
         "cash_leg": {"source": "x", "mean_accrual_ann_pct": 1.5, "missing_bar_steps": 0}},
        {"ticket": {}, "book_decided_at": "2020-01-03", "evidence_cutoff": "2020-01-08",
         "cash_leg": "a plain label, not a block"},
    ]
    for i, b in enumerate(bodies):
        nm = ["TICKET-2020-01-03.json", "TICKET-2020-01-08.json",
              "TICKET-2020-01-09-card.json"][i]
        p = os.path.join(tmpdir, nm)
        with io.open(p, "w", encoding="utf-8") as fh:
            fh.write(json.dumps(b))
        paths.append(p)
    cache = {}
    rows = [analyse(p, idx, rates, cache) for p in paths]
    eq("a payload whose cash_leg is a string is published as no block", rows[2]["class"],
       C_NO_BLOCK)
    eq("a ticket with a block on a bar the panel carries is not no-panel",
       rows[0]["class"] != C_NO_PANEL, True)
    near("the one-bar accrual at the bar rate re-derives from cash_amount",
         rows[0]["accrual_one_bar_cny_at_bar_rate"],
         round(100000.0 * 2.0 / 100.0 / 252.0, 2))
    eq("a window with no quote on its first bar still counts that step as unaccrued",
       rows[0]["unaccrued_steps_upper_bound"], 1)
    near("the unaccrued bound prices that step at the last quote at or before the cutoff",
         rows[0]["unaccrued_cny_upper_bound"], round(100000.0 * 2.0 / 100.0 / 252.0, 2))
    full = rates.reindex(idx).fillna(2.0)
    _mf, _missf = window_mean(idx, full)
    eq("a window whose quotes cover every step reports no missing steps", _missf, 0)
    eq("the fixture rows carry the window's own missing count",
       rows[1]["unaccrued_steps_upper_bound"], rows[1]["rederived_missing_bar_steps"])
    s3 = summarise(rows)
    eq("the fixture summary counts three tickets", s3["tickets_total"], 3)
    eq("one fixture ticket carries no block", s3["tickets_with_no_cash_leg_block"], 1)

    face = {"rows": rows, "summary": s3}
    eq("the guard passes a face it built itself", face_problems(face), [])

    doctored = json.loads(json.dumps(face))
    doctored["rows"][0]["class"] = C_WINDOW
    ok.append(("the guard refuses a window-mean class whose numbers are the bar's",
               bool(face_problems(doctored)), "no problem reported"))

    doctored = json.loads(json.dumps(face))
    doctored["rows"][2]["published_mean_accrual_ann_pct"] = 1.0
    ok.append(("the guard refuses a no-block ticket that publishes an accrual",
               bool(face_problems(doctored)), "no problem reported"))

    doctored = json.loads(json.dumps(face))
    doctored["summary"]["tickets_total"] = 99
    ok.append(("the guard refuses a summary count that does not match the rows",
               bool(face_problems(doctored)), "no problem reported"))

    doctored = json.loads(json.dumps(face))
    doctored["rows"][0]["class"] = "a_class_this_study_does_not_define"
    ok.append(("the guard refuses a class the study does not define",
               bool(face_problems(doctored)), "no problem reported"))

    doctored = json.loads(json.dumps(face))
    doctored["rows"][0]["accrual_one_bar_cny_at_bar_rate"] = 999.0
    ok.append(("the guard refuses an accrual that does not re-derive",
               bool(face_problems(doctored)), "no problem reported"))

    doctored = json.loads(json.dumps(face))
    doctored["summary"]["tickets_with_a_cash_leg_block"] = 99
    ok.append(("the guard refuses a with-block count that does not re-derive",
               bool(face_problems(doctored)), "no problem reported"))

    bad = [n for n, good, msg in ok if not good]
    print("%s selftest %d/%d" % ("PASS" if not bad else "FAIL", len(ok) - len(bad), len(ok)))
    for n, good, msg in ok:
        if not good:
            print("  FAIL %s: %s" % (n, msg))
    return 0 if not bad else 1


def main(argv=None):
    argv = argv or sys.argv[1:]
    cmd = argv[0] if argv else "build"
    if cmd == "selftest":
        return selftest()
    if cmd in ("build", "run"):
        face = build(write=True)
        print("BUILT %s | %s" % (face["verdict"], face["verdict_line"]))
        return 0
    if cmd == "check":
        return check()
    if cmd == "verify":
        return verify()
    print("unknown command %r" % cmd)
    return 2


if __name__ == "__main__":
    sys.exit(main())
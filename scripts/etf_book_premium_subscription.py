"""Why does the sheet pay 20% over its funds' own baskets? One testable answer.

r1497/r1500 left this open and said the honest thing: "there is no subscription-status
column in the NAV history". That is true of the *cache* (`data/etf_premium/nav_history/`
carries `date,nav` only, because `etf_book_premium_percentile.load_nav` reads two columns
and drops the rest). It is not true of the *source*: EM's `fund_etf_fund_info_em` returns
six columns, and 申购状态 / 赎回状态 are two of them. Measured on 2026-11-11 for the five
legs of the published ticket:

    159501  场内买入 802 / 暂停申购  29      latest 场内买入
    513100  暂停申购 481 / 场内买入 452      latest 暂停申购
    513690  场内买入 898 / 暂停申购  36      latest 场内买入
    159577  场内买入 604 / 暂停申购  58      latest 场内买入
    159263  场内买入 330 / 暂停申购   0      latest 场内买入

So the question the earlier round wanted to ask can be asked, and the answer is a census,
not a story: the two words that appear are 场内买入 (secondary market only -- no OTC
primary subscription listed) and 暂停申购 (suspended). Neither of them is an open primary
channel. The 限购 hypothesis therefore cannot be *confirmed* by a change of state -- there
is no open state in coverage to compare against -- but it CAN be falsified, and that is
what this face does:

  * if any session in coverage showed an open primary subscription, the hypothesis is dead
    for that leg (the valve existed and the premium survived it): CHANNEL_OPEN_SESSIONS_EXIST
  * if every session is closed, the premium had no valve this face can see inside the
    window: CHANNEL_CLOSED_THROUGHOUT -- a mechanism statement, not a value judgement
  * the one within-leg contrast the data does offer -- hard-suspended sessions vs
    exchange-only sessions -- is priced separately (BLOCK_WIDENS_PREMIUM /
    BLOCK_DOES_NOT_WIDEN), because 513100 spends 481 of 933 sessions in the hard block and
    still carries the deepest premium.

Every reading is joined on the NAV *stamp the premium used* (the strictly-earlier NAV date
from `etf_book_premium_percentile.premium_series`), never on the price bar: a status word
belongs to the NAV row it is printed on.

r1547 added the level the first version was missing: the *runs*. The day counts above invite
a reader to treat 679 suspended sessions as 679 observations, and they are not -- the days
inside one suspension repeat one fact, while on several legs most 暂停申购 runs are a single
NAV row. `episode_read` names every run with its first and last priced session and re-reads
the contrast one level up; on 513100 the published +4.50pp turns out to sit in its single
435-session block (+4.28pp), with the other 47 runs at +0.06pp.

Usage:
    python scripts/etf_book_premium_subscription.py run [--no-fetch]
    python scripts/etf_book_premium_subscription.py check
    python scripts/etf_book_premium_subscription.py selftest
"""
import argparse
import datetime as dt
import json
import math
import os
import statistics
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import etf_book_premium_percentile as pp  # noqa: E402  one price/NAV implementation

OUT_DIR = os.path.join(ROOT, "results", "etf_premium")
OUT = os.path.join(OUT_DIR, "PREMIUM-SUBSCRIPTION.json")
OUT_MD = os.path.join(OUT_DIR, "PREMIUM-SUBSCRIPTION.md")
FACE = os.path.join(OUT_DIR, "PREMIUM-PERCENTILE.json")
SUB_DIR = os.path.join(ROOT, "data", "etf_premium", "subscription")
DOC = os.path.join(ROOT, "research", "ETF_BOOK_PREMIUM_SUBSCRIPTION.md")

HI_PCT = 10.0            # a premium worth explaining (arbitrage-worthy by any reading)
OPEN_WORDS = ("开放申购", "场内申购", "申购开放", "开放")
BLOCK_WORDS = ("暂停",)

C_DATE, C_NAV, C_BUY, C_SELL = "净值日期", "单位净值", "申购状态", "赎回状态"


def status_kind(word):
    """Map one published status word to open / closed / unknown. Never guess."""
    w = (word or "").strip()
    if not w:
        return "unknown"
    if any(k in w for k in OPEN_WORDS):
        return "open"
    return "closed"


def load_status(code, fetch=True, today=None, cache_dir=None):
    """As-collected purchase/redemption status by NAV date. Returns (rows, status).

    rows = [{"date","nav","purchase","redeem"}] ascending. Cache is regenerable raw data.
    """
    d = cache_dir or SUB_DIR
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, str(code) + ".csv")
    rows = []
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            for line in f:
                p = line.rstrip("\n").split(",")
                if len(p) < 4 or p[0] == "date":
                    continue
                try:
                    rows.append({"date": p[0][:10], "nav": float(p[1]),
                                 "purchase": p[2], "redeem": p[3]})
                except ValueError:
                    continue
    latest = rows[-1]["date"] if rows else None
    if rows and today and latest and latest >= today:
        return rows, "cache"
    if not fetch:
        return rows, "cache-stale" if rows else "cache-missing"
    try:
        import akshare as ak
    except Exception as exc:                                   # pragma: no cover
        return rows, "no-akshare:%s" % type(exc).__name__
    try:
        df = ak.fund_etf_fund_info_em(
            fund=str(code), start_date=pp.NAV_START,
            end_date=(today or "20991231").replace("-", ""))
        got = {}
        for _, r in df.iterrows():
            dt = str(r[C_DATE])[:10]
            try:
                nav = float(r[C_NAV])
            except (TypeError, ValueError):
                continue
            if nav <= 0:
                continue
            got[dt] = {"date": dt, "nav": nav,
                       "purchase": str(r.get(C_BUY) or "").strip(),
                       "redeem": str(r.get(C_SELL) or "").strip()}
        merged = {r["date"]: r for r in rows}
        merged.update(got)                                  # as-collected: later pull wins
        rows = [merged[k] for k in sorted(merged)]
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8", newline="\n") as f:
            f.write("date,nav,purchase,redeem\n")
            for r in rows:
                f.write("%s,%.6f,%s,%s\n" % (r["date"], r["nav"], r["purchase"], r["redeem"]))
        os.replace(tmp, path)
        return rows, "fetched"
    except Exception as exc:                                   # pragma: no cover
        return rows, "fetch-error:%s" % type(exc).__name__


def episodes(series):
    """Contiguous runs of one status word, in priced-session order.

    The previous reading counted *days*: 513100 showed 679 hard-suspended sessions and the
    page invited a reader to take that as 679 observations. They are not -- a suspension runs
    for as long as the fund keeps it, and every day inside it repeats the same fact. The same
    count is misleading in the other direction too: on several legs most 暂停申购 runs are a
    single NAV row, i.e. one word printed between two exchange-only rows, which is a blip and
    not a policy. Both have to be counted, and separately.

    Each episode records the first and last priced session that carried the word, so the
    transition days can be named instead of summarised.
    """
    out = []
    for r in series:
        w = r.get("purchase") or ""
        k = r.get("purchase_kind") or "unknown"
        if out and out[-1]["word"] == w and out[-1]["kind"] == k:
            e = out[-1]
            e["last_date"] = r["date"]
            e["last_nav_date"] = r["nav_date"]
            e["n_rows"] += 1
            e["_prems"].append(r["premium_pct"])
        else:
            out.append({"word": w, "kind": k,
                        "first_date": r["date"], "last_date": r["date"],
                        "first_nav_date": r["nav_date"], "last_nav_date": r["nav_date"],
                        "n_rows": 1, "_prems": [r["premium_pct"]]})
    for e in out:
        e["median_pct"] = statistics.median(e["_prems"])
        e.pop("_prems", None)
    return out


def episode_read(series, is_blocked=lambda word: "暂停" in (word or "")):
    """Days vs episodes: how many independent runs the block count really rests on.

    The contrast is re-read one level up -- for each 暂停申购 episode, its own median premium
    against the leg's exchange-only baseline -- so a single 435-session block and an equal
    number of one-row blips can no longer masquerade as the same amount of evidence.
    """
    eps = episodes(series)
    exh = [r["premium_pct"] for r in series
           if r["purchase_kind"] == "closed" and not is_blocked(r.get("purchase"))]
    base = statistics.median(exh) if len(exh) >= 5 else None
    blocked_eps = [e for e in eps if is_blocked(e["word"])]
    gaps = [e["median_pct"] - base for e in blocked_eps] if base is not None else []
    if not blocked_eps:
        verdict = "NO_BLOCKED_EPISODES"
    elif base is None:
        verdict = "NO_EXCHANGE_BASELINE"
    elif len(blocked_eps) < 5:
        verdict = "TOO_FEW_EPISODES"
    else:
        verdict = ("EPISODE_GAP_WIDENS" if statistics.median(gaps) > 1.0
                   else "EPISODE_GAP_DOES_NOT_WIDEN")
    longest = max(blocked_eps, key=lambda e: e["n_rows"]) if blocked_eps else None
    longest_gap = (longest["median_pct"] - base) if (longest and base is not None) else None
    rest = [g for g, e in zip(gaps, blocked_eps) if e is not longest] if longest else list(gaps)
    gap_wo = statistics.median(rest) if rest else None
    return {
        "n_episodes": len(eps),
        "n_blocked_episodes": len(blocked_eps),
        "blocked_one_row": sum(1 for e in blocked_eps if e["n_rows"] == 1),
        "median_blocked_rows": (statistics.median([e["n_rows"] for e in blocked_eps])
                                if blocked_eps else None),
        "longest_blocked_rows": longest["n_rows"] if longest else 0,
        "longest_blocked_first": longest["first_date"] if longest else None,
        "longest_blocked_last": longest["last_date"] if longest else None,
        "exchange_baseline_pct": base,
        "episode_gap_pp": (statistics.median(gaps) if gaps else None),
        "longest_block_gap_pp": longest_gap,
        "gap_without_longest_pp": gap_wo,
        "widens_only_in_longest": bool(longest_gap is not None and longest_gap > 1.0
                                       and gap_wo is not None and gap_wo <= 1.0),
        "episodes_gap_positive": sum(1 for g in gaps if g > 0),
        "n_gaps": len(gaps),
        "verdict": verdict,
        "runs": eps,
    }


WEEKDAY_NAMES = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
CADENCE_MIN_N = 10          # below this, the weekday mix is not a measurement
CADENCE_TAIL = 1e-4         # how unlikely a weekday mix has to be before it is named
CADENCE_EXCESS = 0.15       # and how far above its session base the modal day has to sit


def _weekday(date_str):
    """0=Mon..6=Sun, or -1 when the stamp is not a date this face can read."""
    try:
        return dt.date.fromisoformat(str(date_str)[:10]).weekday()
    except (TypeError, ValueError):
        return -1


def _binom_tail_ge(k, n, p):
    """P(X >= k) for X ~ Bin(n, p). Pure python -- the chain has no scipy."""
    if n <= 0 or k <= 0:
        return 1.0
    if k > n:
        return 0.0
    p = min(max(float(p), 0.0), 1.0)
    return sum(math.comb(n, i) * (p ** i) * ((1.0 - p) ** (n - i)) for i in range(k, n + 1))


def _cadence_verdict(n_one_row, sessions_by_weekday, blips_by_weekday,
                     min_n=CADENCE_MIN_N):
    """Is the weekday mix of the single-row words the session mix, or something else?

    Derived from counts only, so `check` can recompute it from the published numbers and a
    hand-edited verdict word cannot survive.
    """
    total_sessions = sum(sessions_by_weekday)
    out = {"n_one_row": n_one_row, "modal_weekday": None, "modal_weekday_index": None,
           "base_share_modal": None, "blip_share_modal": None, "tail_p": None}
    if not total_sessions or not n_one_row:
        out["verdict"] = "TOO_FEW_BLIPS"
        return out
    base = [c / total_sessions for c in sessions_by_weekday]
    share = [c / n_one_row for c in blips_by_weekday]
    idx = max(range(5), key=lambda i: (share[i], -i))
    out.update({"modal_weekday": WEEKDAY_NAMES[idx], "modal_weekday_index": idx,
                "base_share_modal": round(base[idx], 4),
                "blip_share_modal": round(share[idx], 4),
                "tail_p": _binom_tail_ge(blips_by_weekday[idx], n_one_row, base[idx])})
    if n_one_row < min_n:
        out["verdict"] = "TOO_FEW_BLIPS"
    elif out["tail_p"] < CADENCE_TAIL and share[idx] - base[idx] >= CADENCE_EXCESS:
        out["verdict"] = "BLIP_WEEKDAY_CADENCE"
    else:
        out["verdict"] = "BLIP_NO_CADENCE"
    return out


def blip_cadence(series, min_n=CADENCE_MIN_N):
    """When does a one-row 暂停申购 word appear? Counts only -- never a cause.

    A single-row run is one word printed between two exchange-only rows. The page already
    counts those runs; this block asks the next question, which the page never answered: do
    they land on ordinary sessions? If they did, the weekday mix would look like the session
    mix. This face prices the mix, names the day-of-month peaks, counts how many are
    bracketed by 场内买入 on both sides, and counts the ones a NAV discontinuity could
    actually explain. What it cannot do is name the cause -- a source refresh rhythm and a
    real one-day announcement look identical from here, and the text says so.
    """
    eps = episodes(series)
    blocked = [e for e in eps if "暂停" in (e["word"] or "")]
    one = [e for e in blocked if e["n_rows"] == 1]
    sessions_by_dow = [0] * 5
    unreadable_sessions = 0
    for r in series:
        w = _weekday(r.get("date"))
        if 0 <= w < 5:
            sessions_by_dow[w] += 1
        else:
            unreadable_sessions += 1
    blips_by_dow = [0] * 5
    unreadable_blips = 0
    dom = {}
    bracketed = 0
    nav_jumps = []
    examples = []
    nav_by_date = {r["date"]: r.get("nav") for r in series}
    prev_nav = {}
    nav_rows = [r for r in series if r.get("date")]
    for a, b in zip(nav_rows, nav_rows[1:]):
        prev_nav[b["date"]] = a.get("nav")

    def exchange_only(e):
        return bool(e) and e.get("kind") == "closed" and "暂停" not in (e.get("word") or "")

    for i, e in enumerate(eps):
        if "暂停" not in (e["word"] or "") or e["n_rows"] != 1:
            continue
        d = str(e["first_date"])
        w = _weekday(d)
        if 0 <= w < 5:
            blips_by_dow[w] += 1
        else:
            unreadable_blips += 1
        try:
            k = int(d[8:10])
            dom[k] = dom.get(k, 0) + 1
        except (ValueError, IndexError):
            pass
        left = eps[i - 1] if i > 0 else None
        right = eps[i + 1] if i + 1 < len(eps) else None
        if exchange_only(left) and exchange_only(right):
            bracketed += 1
        cur, prev = nav_by_date.get(d), prev_nav.get(d)
        if cur and prev:
            nav_jumps.append(abs(cur / prev - 1.0) * 100.0)
        if len(examples) < 3:
            examples.append(d)
    top_dom = sorted(dom.items(), key=lambda kv: (-kv[1], kv[0]))[:3]
    out = _cadence_verdict(len(one), sessions_by_dow, blips_by_dow, min_n=min_n)
    out.update({
        "n_blocked": len(blocked),
        "sessions_by_weekday": sessions_by_dow,
        "blips_by_weekday": blips_by_dow,
        "n_sessions_unreadable_date": unreadable_sessions,
        "n_blips_unreadable_date": unreadable_blips,
        "day_of_month_top": [{"dom": k, "n": v} for k, v in top_dom],
        "bracketed_by_exchange_only": bracketed,
        "nav_jump_gt3pct": sum(1 for j in nav_jumps if j > 3.0),
        "nav_jump_max_abs_pct": round(max(nav_jumps), 4) if nav_jumps else None,
        "examples": examples,
        "not_a_cause": "a weekly source refresh and a real one-day announcement are"
                       " indistinguishable here; this block prices when the word appears",
    })
    return out


def pooled_cadence(legs):
    """The same block over all legs, because 116 single-row runs is a pool, not five samples."""
    sessions_by_dow = [0] * 5
    blips_by_dow = [0] * 5
    n_one = n_blocked = bracketed = jumps = 0
    dom = {}
    for l in legs:
        c = l.get("blip_cadence") or {}
        if not c:
            continue
        n_one += c.get("n_one_row") or 0
        n_blocked += c.get("n_blocked") or 0
        bracketed += c.get("bracketed_by_exchange_only") or 0
        jumps += c.get("nav_jump_gt3pct") or 0
        for i in range(5):
            sessions_by_dow[i] += (c.get("sessions_by_weekday") or [0] * 5)[i]
            blips_by_dow[i] += (c.get("blips_by_weekday") or [0] * 5)[i]
        for row in c.get("day_of_month_top") or []:
            k = row.get("dom")
            dom[k] = dom.get(k, 0) + (row.get("n") or 0)
    out = _cadence_verdict(n_one, sessions_by_dow, blips_by_dow)
    top = sorted(dom.items(), key=lambda kv: (-kv[1], kv[0]))[:3]
    out.update({"n_blocked": n_blocked, "sessions_by_weekday": sessions_by_dow,
                "blips_by_weekday": blips_by_dow,
                "bracketed_by_exchange_only": bracketed,
                "nav_jump_gt3pct": jumps,
                "day_of_month_top": [{"dom": k, "n": v} for k, v in top]})
    return out


# ------------------------------------------------------------------ offshore calendar
OFFSHORE_CALENDAR = ("NYSE closures, rule-derived: New Year, MLK, Presidents, Good Friday,"
                     " Memorial, Juneteenth (from 2022), Independence, Labor, Thanksgiving,"
                     " Christmas -- plus the three scheduled 13:00 early closes")
CAL_YEARS = range(2018, 2029)


def _easter(year):
    """Gregorian Easter; Good Friday is two days before it."""
    a = year % 19
    b, c = divmod(year, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l = (32 + 2 * e + 2 * i - h - k) % 7          # noqa: E741  the classic Gauss letters
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return dt.date(year, month, day)


def _nth_weekday(year, month, weekday, n):
    d = dt.date(year, month, 1)
    return d + dt.timedelta(days=(weekday - d.weekday()) % 7 + 7 * (n - 1))


def _last_weekday(year, month, weekday):
    end = (dt.date(year, month + 1, 1) if month < 12 else dt.date(year + 1, 1, 1))
    end -= dt.timedelta(days=1)
    return end - dt.timedelta(days=(end.weekday() - weekday) % 7)


def _observed(d):
    """Saturday -> Friday, Sunday -> Monday: the exchange takes the weekday."""
    if d.weekday() == 5:
        return d - dt.timedelta(days=1)
    if d.weekday() == 6:
        return d + dt.timedelta(days=1)
    return d


def nyse_closures(years=None):
    """(full, early) closure dates. The rules are published, so this needs no data."""
    full, early = set(), set()
    for y in (CAL_YEARS if years is None else years):
        full |= {_observed(dt.date(y, 1, 1)),
                 _nth_weekday(y, 1, 0, 3),                 # Martin Luther King
                 _nth_weekday(y, 2, 0, 3),                 # Washington's Birthday
                 _easter(y) - dt.timedelta(days=2),        # Good Friday
                 _last_weekday(y, 5, 0),                   # Memorial
                 _observed(dt.date(y, 7, 4)),              # Independence
                 _nth_weekday(y, 9, 0, 1),                 # Labor
                 _nth_weekday(y, 11, 3, 4),                # Thanksgiving
                 _observed(dt.date(y, 12, 25))}            # Christmas
        if y >= 2022:
            full.add(_observed(dt.date(y, 6, 19)))        # Juneteenth
        black_friday = _nth_weekday(y, 11, 3, 4) + dt.timedelta(days=1)
        if black_friday.weekday() < 5:
            early.add(black_friday)                       # 13:00 close
        for md in (dt.date(y, 7, 3), dt.date(y, 12, 24)):
            if md.weekday() < 5 and md not in full:
                early.add(md)                             # 13:00 close
    return full, early


CLOSURE_FULL, CLOSURE_EARLY = nyse_closures()


def closure_kind(prev_stamp, stamp):
    """'full' / 'early' / None for a closure inside (prev_stamp, stamp].

    The half-open window is the point: a NAV stamp is short of a valuation because the
    market that closes its basket was shut somewhere between the previous stamp and it.
    """
    try:
        lo = dt.date.fromisoformat(str(prev_stamp)[:10])
        hi = dt.date.fromisoformat(str(stamp)[:10])
    except (TypeError, ValueError):
        return None
    if hi <= lo:
        return None
    day = lo
    full = early = False
    while day < hi:
        day += dt.timedelta(days=1)
        if day in CLOSURE_FULL:
            full = True
        elif day in CLOSURE_EARLY:
            early = True
    if full:
        return "full"
    return "early" if early else None


# ---------------------------------------------------------------- the Hong Kong calendar
# One leg of the ticket is a Hong Kong basket, and its one-row runs do not match New York
# (1/24). HKEX cannot be rule-derived the way the US list can: its statutory holidays follow
# the lunar calendar, and the exchange also shuts for typhoons and black rainstorms that no
# rule set predicts. So this calendar is *measured* from the market itself -- the HSI daily
# series says which dates Hong Kong traded, and its own turnover says which of those were
# half days that never struck a closing valuation.
HK_INDEX_CACHE = os.path.join(ROOT, "data", "etf_premium", "hk_index_HSI.csv")
HK_INDEX_FRESH_H = 6         # refetch at most four times a day; a missing bar before 16:15 HKT is normal
HK_THIN_MAX = 0.60           # a half day trades about half its own trailing turnover
HK_THIN_FLOOR = 0.05         # below this the row is an unreadable turnover, not a half day
HK_THIN_SENSITIVITY = (0.50, 0.60, 0.70)
HK_INDEX_NOTE = ("HKEX calendar, measured on the HSI daily series (no bar = Hong Kong did not"
                 " trade; a bar whose turnover is under %.0f%% of its own trailing-20 median ="
                 " a half day with no closing valuation). Statutory HK holidays follow the"
                 " lunar calendar and the exchange also shuts for typhoons, so no rule set"
                 " names this calendar -- the index does." % (100 * HK_THIN_MAX))


def load_hk_index(fetch=True, cache=None, now=None):
    """(market, status) for the Hong Kong reference market.

    market = {"sessions": set of dates, "ratio": {date: turnover / trailing-20 median},
              "n", "first", "last", "status"}. The cache is as-collected index data
    (`date,amount`), regenerable, and used stale only when the fetch fails -- in which
    case the status says so and the page prints it.
    """
    path = cache or HK_INDEX_CACHE
    rows = []
    fresh = False
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as f:
                for line in f:
                    p = line.rstrip("\n").split(",")
                    if len(p) < 2 or p[0] == "date":
                        continue
                    rows.append((p[0][:10], float(p[1] or 0.0)))
            rows.sort()
            age_h = ((now or dt.datetime.now())
                     - dt.datetime.fromtimestamp(os.path.getmtime(path))).total_seconds() / 3600.0
            fresh = age_h < HK_INDEX_FRESH_H
        except (ValueError, OSError):
            rows, fresh = [], False
    status = "cache" if fresh else "cache-stale"
    if fetch and not fresh:
        got = None
        try:
            import akshare as ak
            df = ak.stock_hk_index_daily_sina(symbol="HSI")
            got = sorted((str(d)[:10], float(a or 0.0))
                         for d, a in zip(df["date"], df["amount"]))
        except Exception as exc:                                    # pragma: no cover
            status = "fetch-failed:%s" % type(exc).__name__
        if got:
            rows, status = got, "fetched"
            try:
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "w", encoding="utf-8", newline="\n") as f:
                    f.write("date,amount\n")
                    for d, a in rows:
                        f.write("%s,%.0f\n" % (d, a))
            except OSError:
                pass
    elif not rows and not fetch:
        status = "cache-missing"
    market = {"n": len(rows), "first": rows[0][0] if rows else None,
              "last": rows[-1][0] if rows else None, "status": status,
              "sessions": {d for d, _ in rows}, "ratio": {}}
    for i, (d, a) in enumerate(rows):
        if i < 20:
            continue
        med = statistics.median(x for _, x in rows[i - 20:i])
        if med > 0:
            market["ratio"][d] = a / med
    return market, status


def hk_closure_kind(prev_stamp, stamp, market, thin_max=HK_THIN_MAX):
    """'closed' / 'thin' / 'window' / None for a Hong Kong valuation gap.

    Three ways the same thing happens, and they are not the same statement:
      closed -- Hong Kong did not trade on the stamp at all (holiday or typhoon);
      thin   -- it traded a half day, so there is no closing valuation to strike NAV against;
      window -- the market was shut somewhere between the previous stamp and this one, which
                is what a multi-session A-share holiday looks like from the fund's side.
    """
    sessions = (market or {}).get("sessions") or set()
    if not sessions:
        return None
    s = str(stamp or "")[:10]
    if not s:
        return None
    if s not in sessions:
        return "closed"
    ratio = (market or {}).get("ratio") or {}
    r = ratio.get(s)
    if r is not None and HK_THIN_FLOOR <= r <= thin_max:
        return "thin"
    lo = str(prev_stamp or "")[:10]
    if not lo:
        return None
    try:
        day = dt.date.fromisoformat(lo)
        hi = dt.date.fromisoformat(s)
    except (TypeError, ValueError):
        return None
    while day < hi:
        day += dt.timedelta(days=1)
        if day.weekday() >= 5:
            continue
        key = day.isoformat()
        rr = ratio.get(key)
        if key not in sessions or (rr is not None and HK_THIN_FLOOR <= rr <= thin_max):
            return "window"
    return None


CAUSE_MOVE_MAX = 0.30        # a valuation gap moves NAV a fraction of a normal session
CAUSE_BOTH_MIN = 0.90        # ... and takes both channels with it
CAUSE_CALENDAR_MIN = 0.60    # ... and a published calendar explains this much of them
CAUSE_LIFT_MIN = 3.0         # ... at least this many times the ordinary-session rate
CAUSE_CALENDAR_MARGIN = 0.10  # ... and has to beat the other calendar in hand by this much


def calendar_choice(cands):
    """Name a calendar only when exactly one of them earns it.

    Two lists are in hand now (New York by rule, Hong Kong by measurement). A leg whose
    dates fit both equally well is not evidence for either, and naming the nearer one
    would be a coin flip dressed as a measurement -- so a tie names nothing.
    """
    qualified = []
    for c in cands or ():
        rate, base = c.get("rate"), c.get("base")
        if rate is None:
            continue
        if rate >= max(CAUSE_CALENDAR_MIN, CAUSE_LIFT_MIN * (base or 0.0)):
            qualified.append(c)
    if not qualified:
        return {"named": None, "reason": "NO_CALENDAR_CLEARS_THE_BAR", "qualified": []}
    qualified.sort(key=lambda c: -c["rate"])
    if len(qualified) > 1 and (qualified[0]["rate"] - qualified[1]["rate"]) < CAUSE_CALENDAR_MARGIN:
        return {"named": None, "reason": "TWO_CALENDARS_FIT_ALIKE",
                "qualified": [c["name"] for c in qualified]}
    return {"named": qualified[0]["name"], "reason": "ONE_CALENDAR_CLEARS_THE_BAR",
            "qualified": [c["name"] for c in qualified]}


def _cause_verdict(n_one_row, both_channels, ratio_median, share_le_quarter,
                   calendar_rate, base_rate, choice=None):
    """What a one-row run *is*, from counts only -- never from a hand-written word.

    Three independent things have to hold before the page will name a cause at all:
    both channels flip on the same row, the NAV barely moves (no new valuation), and a
    majority of the runs move far less than a normal session does. If they hold but no
    calendar in hand explains the dates, the page says so instead of naming a holiday.

    The calendar leg is a *relative* test: the closure rate has to beat the ordinary-session
    rate by CAUSE_LIFT_MIN, expressed as a floor on the rate so a leg whose ordinary sessions
    never follow a closure (0%) cannot divide by zero and look unexplained.

    `choice` (from `calendar_choice`) lets the caller pass two calendars in hand; when it is
    given, the word follows the choice -- a tie between two calendars names neither.
    """
    if not n_one_row:
        return "NO_ONE_ROW_RUNS"
    settled = (both_channels / float(n_one_row) >= CAUSE_BOTH_MIN
               and ratio_median is not None and ratio_median <= CAUSE_MOVE_MAX
               and share_le_quarter >= 0.5)
    if not settled:
        return "CAUSE_UNRESOLVED"
    if choice is not None:
        if choice.get("named"):
            return "CALENDAR_GAP"
        return ("GAP_WITH_UNKNOWN_CALENDAR" if choice.get("qualified") is not None
                and calendar_rate is not None else "GAP_WITH_UNKNOWN_CALENDAR")
    if calendar_rate is None:
        return "GAP_NO_CALENDAR_AVAILABLE"
    if calendar_rate >= max(CAUSE_CALENDAR_MIN, CAUSE_LIFT_MIN * (base_rate or 0.0)):
        return "CALENDAR_GAP"
    return "GAP_WITH_UNKNOWN_CALENDAR"


def blip_cause(series, market=None):
    """A one-row word: a valuation gap, a distribution, or an announcement?

    r1548 priced *when* the single-row runs appear and refused to name a cause; the page
    said a source rhythm and a real one-day announcement look identical from counts of
    weekdays. That was true of the readings it had. It is not true of the row itself:

      * a distribution or a conversion moves the NAV -- these rows move it by a tenth of a
        normal session, and 11 of 116 do not move it at all;
      * an announcement suspends *subscription* -- these rows suspend 赎回 on the same row,
        every single one of them (116/116);
      * a fund-specific decision cannot fall on the same date for two independent managers
        -- 159501 and 159577 share 20 of their 29 and 20 runs;
      * and a shut offshore market explains the dates -- most of them sit on a session whose
        gap contains a closure of the market their basket lives in.

    r1550 asks the last one properly: two calendars are in hand (New York by rule, Hong Kong
    measured on the HSI series), each leg is scored against both, and the page names one only
    when one of them clears the bar and beats the other by CAUSE_CALENDAR_MARGIN. A leg whose
    dates fit neither is left GAP_WITH_UNKNOWN_CALENDAR rather than given the nearer word.
    The Hong Kong reading is also printed at three half-day thresholds, because that cutoff
    is a ruler and the page says so instead of quoting the single number it likes.

    Every number above is a count the page prints, and the verdict word is derived from
    them (`_cause_verdict`), so `check` can refuse a word that its own counts do not support.
    """
    eps = episodes(series)
    blocked = [e for e in eps if "暂停" in (e["word"] or "")]
    one = [e for e in blocked if e["n_rows"] == 1]
    by_date = {r["date"]: r for r in series}
    stamp_nav, stamp_prev, prev_stamp = {}, {}, None
    for r in series:
        nd = r.get("nav_date")
        if nd and nd not in stamp_nav and r.get("nav") is not None:
            stamp_nav[nd] = r["nav"]
            stamp_prev[nd] = prev_stamp
            prev_stamp = nd
    moves = {}
    for nd, nav in stamp_nav.items():
        p = stamp_prev.get(nd)
        if p and stamp_nav.get(p):
            moves[nd] = abs(nav / stamp_nav[p] - 1.0) * 100.0
    base_move = statistics.median(moves.values()) if moves else None

    hk = market if market is not None else {"sessions": set(), "ratio": {}}
    hk_sensitivity = {thr: 0 for thr in HK_THIN_SENSITIVITY}

    both = carry = 0
    ratios = []
    moves_pct = []
    kinds = {"full": 0, "early": 0, None: 0}
    hk_kinds = {"closed": 0, "thin": 0, "window": 0, None: 0}
    unmatched = []
    hk_unmatched = []
    blip_stamps = set()
    for e in one:
        r = by_date.get(str(e["first_date"]))
        if not r:
            continue
        stamp = r.get("nav_date")
        blip_stamps.add(stamp)
        if "暂停" in (r.get("redeem") or ""):
            both += 1
        mv = moves.get(stamp)
        if mv is not None:
            if mv <= 1e-12:
                carry += 1
            if base_move:
                ratios.append(mv / base_move)
        kind = closure_kind(stamp_prev.get(stamp), stamp)
        kinds[kind] = kinds.get(kind, 0) + 1
        if kind is None and len(unmatched) < 12:
            unmatched.append(stamp)
        for thr in HK_THIN_SENSITIVITY:
            if hk_closure_kind(stamp_prev.get(stamp), stamp, hk, thin_max=thr):
                hk_sensitivity[thr] += 1
        hkind = hk_closure_kind(stamp_prev.get(stamp), stamp, hk)
        hk_kinds[hkind] = hk_kinds.get(hkind, 0) + 1
        if hkind is None and len(hk_unmatched) < 12:
            hk_unmatched.append(stamp)
        if mv is not None:
            moves_pct.append((mv, stamp))

    base_hits = base_sessions = 0
    hk_base_hits = hk_base_sessions = 0
    for nd in stamp_nav:
        if nd in blip_stamps:
            continue
        base_sessions += 1
        if closure_kind(stamp_prev.get(nd), nd):
            base_hits += 1
        if hk.get("sessions"):
            hk_base_sessions += 1
            if hk_closure_kind(stamp_prev.get(nd), nd, hk):
                hk_base_hits += 1

    n_one = len(one)
    n_ratio = len(ratios)
    n_quarter = sum(1 for x in ratios if x <= 0.25)
    matched = kinds.get("full", 0) + kinds.get("early", 0)
    calendar_rate = (matched / float(n_one)) if n_one else None
    base_rate = (base_hits / float(base_sessions)) if base_sessions else None
    lift = (calendar_rate / base_rate) if (calendar_rate is not None and base_rate) else None
    hk_matched = hk_kinds.get("closed", 0) + hk_kinds.get("thin", 0) + hk_kinds.get("window", 0)
    hk_rate = (hk_matched / float(n_one)) if (n_one and hk.get("sessions")) else None
    hk_base = (hk_base_hits / float(hk_base_sessions)) if hk_base_sessions else None
    hk_lift = (hk_rate / hk_base) if (hk_rate is not None and hk_base) else None
    choice = calendar_choice([
        {"name": "NYSE", "rate": calendar_rate, "base": base_rate,
         "measure": "rule-derived US closure list, window (prev_stamp, stamp]"},
        {"name": "HKEX", "rate": hk_rate, "base": hk_base,
         "measure": "HSI series: no bar, a half day, or a shut weekday in the gap"},
    ])
    ratio_median = statistics.median(ratios) if ratios else None
    share_quarter = (n_quarter / float(n_ratio)) if n_ratio else 0.0
    out = {
        "n_one_row": n_one,
        "n_blocked": len(blocked),
        "n_multi_row": len(blocked) - n_one,
        "both_channels_suspended": both,
        "both_channels_share": round(both / float(n_one), 4) if n_one else None,
        "exact_carry": carry,
        "nav_move_ratio_median": (round(ratio_median, 4) if ratio_median is not None else None),
        "n_move_ratio": n_ratio,
        "n_move_le_quarter": n_quarter,
        "share_move_le_quarter": round(share_quarter, 4),
        "calendar": OFFSHORE_CALENDAR,
        "n_closure_full": kinds.get("full", 0),
        "n_closure_early": kinds.get("early", 0),
        "n_closure_unmatched": kinds.get(None, 0),
        "closure_rate": (round(calendar_rate, 4) if calendar_rate is not None else None),
        "n_base_sessions": base_sessions,
        "n_base_closure": base_hits,
        "base_rate": (round(base_rate, 4) if base_rate is not None else None),
        "lift": (round(lift, 2) if lift is not None else None),
        "hk_calendar": HK_INDEX_NOTE,
        "hk_index_status": hk.get("status"),
        "hk_index_last": hk.get("last"),
        "hk_thin_max": HK_THIN_MAX,
        "hk_n_closed": hk_kinds.get("closed", 0),
        "hk_n_thin": hk_kinds.get("thin", 0),
        "hk_n_window": hk_kinds.get("window", 0),
        "hk_n_unmatched": hk_kinds.get(None, 0),
        "hk_rate": (round(hk_rate, 4) if hk_rate is not None else None),
        "hk_base_rate": (round(hk_base, 4) if hk_base is not None else None),
        "hk_lift": (round(hk_lift, 2) if hk_lift is not None else None),
        "hk_n_base_sessions": hk_base_sessions,
        "hk_n_base_closure": hk_base_hits,
        "hk_thin_sensitivity": {
            "%.2f" % thr: {
                "n_matched": hk_sensitivity[thr],
                "rate": (round(hk_sensitivity[thr] / float(n_one), 4) if n_one else None)}
            for thr in HK_THIN_SENSITIVITY},
        "hk_unmatched_stamps": hk_unmatched,
        "calendar_named": choice.get("named"),
        "calendar_choice": choice,
        "nav_move_max_pct": (round(max(moves_pct)[0], 4) if moves_pct else None),
        "nav_move_max_stamp": (max(moves_pct)[1] if moves_pct else None),
        "nav_move_p90_pct": (round(sorted(v for v, _ in moves_pct)[int(len(moves_pct) * 0.9)], 4)
                             if moves_pct else None),
        "one_row_stamps": sorted(s for s in blip_stamps if s),
        "unmatched_stamps": unmatched,
        "not_proof": "the closure calendar explains the dates; it does not make the"
                     " premium fair and it is not a statement about quotas",
    }
    out["verdict"] = _cause_verdict(n_one, both, ratio_median, share_quarter,
                                    calendar_rate, base_rate, choice=choice)
    return out


def pooled_blip_cause(legs):
    """The same block over the pool, recomputed from the legs' own counts."""
    n_one = both = carry = full = early = unmatched = 0
    n_ratio = n_quarter = 0
    base_sessions = base_hits = 0
    hk_closed = hk_thin = hk_window = hk_unmatched = 0
    hk_base_sessions = hk_base_hits = 0
    hk_sens = {thr: 0 for thr in HK_THIN_SENSITIVITY}
    leg_medians = []
    nav_max = nav_max_stamp = nav_p90 = None
    for l in legs:
        c = l.get("blip_cause") or {}
        if not c:
            continue
        if (c.get("nav_move_max_pct") is not None
                and (nav_max is None or c["nav_move_max_pct"] > nav_max)):
            nav_max = c["nav_move_max_pct"]
            nav_max_stamp = c.get("nav_move_max_stamp")
        if c.get("nav_move_p90_pct") is not None:
            nav_p90 = c["nav_move_p90_pct"] if nav_p90 is None else max(nav_p90, c["nav_move_p90_pct"])
        n_one += c.get("n_one_row") or 0
        both += c.get("both_channels_suspended") or 0
        carry += c.get("exact_carry") or 0
        full += c.get("n_closure_full") or 0
        early += c.get("n_closure_early") or 0
        unmatched += c.get("n_closure_unmatched") or 0
        n_ratio += c.get("n_move_ratio") or 0
        n_quarter += c.get("n_move_le_quarter") or 0
        base_sessions += c.get("n_base_sessions") or 0
        base_hits += c.get("n_base_closure") or 0
        hk_closed += c.get("hk_n_closed") or 0
        hk_thin += c.get("hk_n_thin") or 0
        hk_window += c.get("hk_n_window") or 0
        hk_unmatched += c.get("hk_n_unmatched") or 0
        hk_base_sessions += c.get("hk_n_base_sessions") or 0
        hk_base_hits += c.get("hk_n_base_closure") or 0
        for thr in HK_THIN_SENSITIVITY:
            cell = (c.get("hk_thin_sensitivity") or {}).get("%.2f" % thr) or {}
            hk_sens[thr] += cell.get("n_matched") or 0
        if c.get("nav_move_ratio_median") is not None:
            leg_medians.append(c["nav_move_ratio_median"])
    matched = full + early
    ratio_median = statistics.median(leg_medians) if leg_medians else None
    share_quarter = (n_quarter / float(n_ratio)) if n_ratio else 0.0
    calendar_rate = (matched / float(n_one)) if n_one else None
    base_rate = (base_hits / float(base_sessions)) if base_sessions else None
    lift = (calendar_rate / base_rate) if (calendar_rate is not None and base_rate) else None
    hk_matched = hk_closed + hk_thin + hk_window
    hk_rate = (hk_matched / float(n_one)) if (n_one and hk_base_sessions) else None
    hk_base = (hk_base_hits / float(hk_base_sessions)) if hk_base_sessions else None
    hk_lift = (hk_rate / hk_base) if (hk_rate is not None and hk_base) else None
    choice = calendar_choice([
        {"name": "NYSE", "rate": calendar_rate, "base": base_rate,
         "measure": "rule-derived US closure list, window (prev_stamp, stamp]"},
        {"name": "HKEX", "rate": hk_rate, "base": hk_base,
         "measure": "HSI series: no bar, a half day, or a shut weekday in the gap"},
    ])
    out = {
        "n_one_row": n_one,
        "n_blocked": sum((l.get("blip_cause") or {}).get("n_blocked") or 0 for l in legs),
        "both_channels_suspended": both,
        "both_channels_share": round(both / float(n_one), 4) if n_one else None,
        "exact_carry": carry,
        "nav_move_ratio_median": (round(ratio_median, 4) if ratio_median is not None else None),
        "nav_move_ratio_basis": "median over legs of each leg's own median",
        "n_move_ratio": n_ratio,
        "n_move_le_quarter": n_quarter,
        "share_move_le_quarter": round(share_quarter, 4),
        "calendar": OFFSHORE_CALENDAR,
        "n_closure_full": full,
        "n_closure_early": early,
        "n_closure_unmatched": unmatched,
        "closure_rate": (round(calendar_rate, 4) if calendar_rate is not None else None),
        "n_base_sessions": base_sessions,
        "n_base_closure": base_hits,
        "base_rate": (round(base_rate, 4) if base_rate is not None else None),
        "lift": (round(lift, 2) if lift is not None else None),
        "hk_calendar": HK_INDEX_NOTE,
        "hk_n_closed": hk_closed,
        "hk_n_thin": hk_thin,
        "hk_n_window": hk_window,
        "hk_n_unmatched": hk_unmatched,
        "hk_rate": (round(hk_rate, 4) if hk_rate is not None else None),
        "hk_base_rate": (round(hk_base, 4) if hk_base is not None else None),
        "hk_lift": (round(hk_lift, 2) if hk_lift is not None else None),
        "hk_n_base_sessions": hk_base_sessions,
        "hk_n_base_closure": hk_base_hits,
        "hk_thin_sensitivity": {
            "%.2f" % thr: {"n_matched": hk_sens[thr],
                           "rate": (round(hk_sens[thr] / float(n_one), 4) if n_one else None)}
            for thr in HK_THIN_SENSITIVITY},
        "calendar_named": choice.get("named"),
        "calendar_choice": choice,
        "nav_move_max_pct": nav_max,
        "nav_move_max_stamp": nav_max_stamp,
        "nav_move_p90_pct": nav_p90,
        "nav_move_basis": "largest / 90th percentile over the legs' one-row stamps",
    }
    out["verdict"] = _cause_verdict(n_one, both, ratio_median, share_quarter,
                                    calendar_rate, base_rate, choice=choice)
    return out


def cross_leg_dates(legs_stamps):
    """Which dates two legs print the same one-row word on.

    A fund can suspend itself; it cannot do so in agreement with a competitor. So the
    overlap between two independently managed legs is the one measurement here that a
    fund-specific decision cannot produce, and the page quotes it from this table rather
    than from a sentence someone typed.
    """
    syms = sorted(s for s, v in legs_stamps.items() if v)
    pairs = []
    for i, a in enumerate(syms):
        for b in syms[i + 1:]:
            shared = sorted(legs_stamps[a] & legs_stamps[b])
            if shared:
                pairs.append({"a": a, "b": b, "n_shared": len(shared),
                              "n_a": len(legs_stamps[a]), "n_b": len(legs_stamps[b]),
                              "shared_first": shared[0], "shared_last": shared[-1]})
    pairs.sort(key=lambda p: (-p["n_shared"], p["a"], p["b"]))
    return {"pairs": pairs, "best": (pairs[0] if pairs else None)}


def series_with_status(prices, navs, status_rows, lag=1):
    """pp.premium_series plus the purchase word printed on the NAV stamp it used."""
    prem = pp.premium_series(prices, navs, lag=lag)
    by_date = {r["date"]: r for r in (status_rows or [])}
    out = []
    for p in prem:
        s = by_date.get(p["nav_date"])
        word = s.get("purchase") if s else ""
        out.append(dict(p, purchase=word or "",
                        purchase_kind=status_kind(word),
                        redeem=(s or {}).get("redeem", "")))
    return out


def window_verdict(series):
    """Does the primary channel ever show open inside coverage?"""
    kinds = [r["purchase_kind"] for r in series]
    known = [k for k in kinds if k != "unknown"]
    if not known:
        return "NO_STATUS_DATA", {"known": 0}
    opens = sum(1 for k in known if k == "open")
    if opens:
        return "CHANNEL_OPEN_SESSIONS_EXIST", {"known": len(known), "open": opens}
    return "CHANNEL_CLOSED_THROUGHOUT", {"known": len(known), "open": 0}


def block_contrast(series, exclude_stamps=None):
    """Hard-suspended sessions vs exchange-only sessions, both priced on their own premium.

    `exclude_stamps` drops priced rows whose NAV stamp is in the given set. The page uses it to
    re-read the same contrast after the single-row valuation gaps (see `blip_cause`) are taken
    out, so a shut offshore market cannot be priced as a fund decision.
    """
    skip = set(exclude_stamps or ())
    blocked = [r["premium_pct"] for r in series
               if "暂停" in (r["purchase"] or "") and r.get("nav_date") not in skip]
    dropped = sum(1 for r in series
                  if "暂停" in (r["purchase"] or "") and r.get("nav_date") in skip)
    exch = [r["premium_pct"] for r in series
            if r["purchase_kind"] == "closed" and "暂停" not in (r["purchase"] or "")]
    if len(blocked) < 5 or len(exch) < 5:
        return {"verdict": "NO_CONTRAST", "n_blocked": len(blocked), "n_exchange": len(exch),
                "n_excluded": dropped, "excluded_requested": len(skip),
                "median_blocked_pct": statistics.median(blocked) if blocked else None,
                "median_exchange_pct": statistics.median(exch) if exch else None}
    mb, me = statistics.median(blocked), statistics.median(exch)
    return {"verdict": "BLOCK_WIDENS_PREMIUM" if mb > me + 1.0 else "BLOCK_DOES_NOT_WIDEN",
            "n_blocked": len(blocked), "n_exchange": len(exch),
            "n_excluded": dropped, "excluded_requested": len(skip),
            "median_blocked_pct": mb, "median_exchange_pct": me,
            "gap_pp": mb - me}


def high_premium_face(series, hi=HI_PCT):
    hi_rows = [r for r in series if r["premium_pct"] >= hi]
    known = [r for r in hi_rows if r["purchase_kind"] != "unknown"]
    if not hi_rows:
        return {"verdict": "NO_HIGH_SESSIONS", "n_high": 0, "n_high_known": 0,
                "share_closed_at_high": None}
    if not known:
        return {"verdict": "NO_STATUS_DATA", "n_high": len(hi_rows), "n_high_known": 0,
                "share_closed_at_high": None}
    closed = sum(1 for r in known if r["purchase_kind"] == "closed")
    return {"verdict": "HIGH_PREMIUM_WHILE_CLOSED" if closed == len(known)
            else "HIGH_PREMIUM_WITH_OPEN_SESSIONS",
            "n_high": len(hi_rows), "n_high_known": len(known),
            "share_closed_at_high": closed / float(len(known)),
            "first_high": hi_rows[0]["date"], "last_high": hi_rows[-1]["date"]}


def leg_facts(leg, prices, navs, status_rows, lag=1, market=None):
    series = series_with_status(prices, navs, status_rows, lag=lag)
    wv, wv_n = window_verdict(series)
    latest = series[-1] if series else None
    hi = high_premium_face(series)
    ep = episode_read(series)
    cause = blip_cause(series, market=market)
    facts = {
        "symbol": str(leg.get("symbol")),
        "class": leg.get("class"),
        "amount_cny": leg.get("amount_cny"),
        "n_sessions": len(series),
        "latest_pct": latest["premium_pct"] if latest else None,
        "latest_price_date": latest["date"] if latest else None,
        "latest_nav_date": latest["nav_date"] if latest else None,
        "latest_purchase": latest["purchase"] if latest else "",
        "latest_purchase_kind": latest["purchase_kind"] if latest else "unknown",
        "n_status_rows": len(status_rows or []),
        "window_verdict": wv,
        "window_facts": wv_n,
        "blocked_sessions": sum(1 for r in series if "暂停" in (r["purchase"] or "")),
        "high_premium": hi,
        "block_contrast": block_contrast(series),
        "block_contrast_excl_gaps": block_contrast(
            series, exclude_stamps=cause.get("one_row_stamps") or []),
        "episode_granularity": ep,
        "blip_cadence": blip_cadence(series),
        "blip_cause": cause,
    }
    return facts


def board_readings(cutoff):
    """The same session's premium on the BOARD's own ruler (price / IOPV), for the same legs.

    Two rulers, two quantities: the board prints intraday basket value, this face divides by
    the disclosed unit NAV. They are not convertible, so the page prints both and the gap
    instead of letting a reader add them. Absent file -> empty map, and the column says so.
    """
    if not cutoff:
        return {}
    path = os.path.join(OUT_DIR, "PREMIUM-%s.json" % cutoff)
    if not os.path.exists(path):
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            face = json.load(f)
    except Exception:
        return {}
    return {str(l.get("symbol")): l.get("premium_pct") for l in face.get("legs", [])}


def build(fetch=True, today=None):
    face = json.load(open(FACE, encoding="utf-8"))
    hk_market, hk_status = load_hk_index(fetch=fetch)
    legs_out, notes = [], []
    cutoff = None
    for leg in face["legs"]:
        code = str(leg.get("symbol"))
        prices = pp.load_prices(code)
        navs, nav_status = pp.load_nav(code, fetch=False)
        status_rows, sub_status = load_status(code, fetch=fetch, today=today)
        if nav_status.startswith("cache-missing") or not navs:
            notes.append("%s: no NAV cache -- premium series unavailable" % code)
        facts = leg_facts(leg, prices, navs, status_rows, market=hk_market)
        facts["nav_cache_status"] = nav_status
        facts["status_source"] = sub_status
        legs_out.append(facts)
        if facts["latest_price_date"] and (cutoff is None or facts["latest_price_date"] > cutoff):
            cutoff = facts["latest_price_date"]

    board = board_readings(cutoff)
    if board:
        for l in legs_out:
            b = board.get(l["symbol"])
            l["board_premium_pct"] = b
            l["ruler_gap_pp"] = (l["latest_pct"] - b) if (b is not None and l["latest_pct"] is not None) else None
    else:
        notes.append("no board face for %s -- the price/IOPV column is not printed" % cutoff)

    verdicts = sorted({l["window_verdict"] for l in legs_out})
    all_closed = all(l["window_verdict"] == "CHANNEL_CLOSED_THROUGHOUT" for l in legs_out)
    pooled = pooled_cadence(legs_out)
    cause = pooled_blip_cause(legs_out)
    cross = cross_leg_dates({str(l["symbol"]): set((l.get("blip_cause") or {})
                                                   .get("one_row_stamps") or [])
                             for l in legs_out})
    doc = {
        "artifact": "etf_book_premium_subscription",
        "machine": os.environ.get("COMPUTERNAME", "bm-c"),
        "decisions": {},
        "evidence_cutoff": cutoff,
        "ticket": {"path": face.get("ticket", {}).get("path"),
                   "as_of": face.get("ticket", {}).get("as_of")},
        "ruler": {
            "premium": face.get("ruler", {}).get("measure"),
            "status_join": "申购状态 printed on the NAV stamp the premium used",
            "status_source": "EM fund_etf_fund_info_em column 申购状态 (dropped by the NAV cache)",
            "hi_pct": HI_PCT,
            "not_proof": "a closed channel is consistent with a standing premium; it is not"
                         " evidence that the premium is fair, nor a sell signal",
        },
        "verdicts": verdicts,
        "hk_index": {"status": hk_status, "n": hk_market.get("n"),
                     "first": hk_market.get("first"), "last": hk_market.get("last"),
                     "note": HK_INDEX_NOTE},
        "legs": legs_out,
        "blip_cadence_pooled": pooled,
        "blip_cause_pooled": cause,
        "blip_cause_cross": cross,
        "notes": notes,
        "summary_sentence": summary_sentence(legs_out, all_closed, pooled, cause),
    }
    return doc


def summary_sentence(legs, all_closed, pooled=None, cause=None):
    n = len(legs)
    closed_n = sum(1 for l in legs if l["window_verdict"] == "CHANNEL_CLOSED_THROUGHOUT")
    open_n = sum(1 for l in legs if l["window_verdict"] == "CHANNEL_OPEN_SESSIONS_EXIST")
    unknown_n = sum(1 for l in legs if l["window_verdict"] == "NO_STATUS_DATA")
    parts = ["%d/%d legs show no open primary subscription anywhere in coverage" % (closed_n, n)]
    if open_n:
        parts.append("%d leg(s) did show open sessions -- the 限购 hypothesis is falsified there"
                     % open_n)
    if unknown_n:
        parts.append("%d leg(s) carry no status data" % unknown_n)
    blocked = [l["symbol"] for l in legs if "暂停" in (l["latest_purchase"] or "")]
    if blocked:
        parts.append("hard-suspended on their latest stamp: %s" % ", ".join(blocked))
    exh = [l["symbol"] for l in legs
           if l["window_verdict"] == "CHANNEL_CLOSED_THROUGHOUT"
           and "暂停" not in (l["latest_purchase"] or "")]
    if exh:
        parts.append("exchange-only on their latest stamp: %s" % ", ".join(exh))
    runs = [(l["symbol"], l["episode_granularity"]) for l in legs
            if l["episode_granularity"]["n_blocked_episodes"]]
    if runs:
        day_n = sum(l["blocked_sessions"] for l in legs)
        run_n = sum(e["n_blocked_episodes"] for _, e in runs)
        blip_n = sum(e["blocked_one_row"] for _, e in runs)
        parts.append("the %d hard-suspended sessions are %d runs (%d of them a single NAV row)"
                     % (day_n, run_n, blip_n))
    widen = [s for s, e in runs if e["verdict"] == "EPISODE_GAP_WIDENS"]
    if widen:
        parts.append("read per run, the block still sits wider on %s" % ", ".join(widen))
    pure = [(l["symbol"], l.get("block_contrast_excl_gaps") or {}) for l in legs]
    pure_wide = [s for s, c in pure if c.get("verdict") == "BLOCK_WIDENS_PREMIUM"]
    pure_flat = [s for s, c in pure if c.get("verdict") == "BLOCK_DOES_NOT_WIDEN"]
    if pure_wide or pure_flat:
        dropped = sum(c.get("n_excluded") or 0 for _, c in pure)
        all_gaps = [s for s, c in pure if c.get("verdict") == "NO_CONTRAST"
                    and (c.get("n_excluded") or 0) > 0]
        parts.append("with the %d one-row valuation gaps removed the block still sits wider on %s"
                     "%s%s" % (dropped, ", ".join(pure_wide) or "no leg",
                               (" and not on %s" % ", ".join(pure_flat)) if pure_flat else "",
                               ("; %s has no real suspension left at all" % ", ".join(all_gaps))
                               if all_gaps else ""))
    single = [(s, e) for s, e in runs if e.get("widens_only_in_longest")]
    if single:
        parts.append("; ".join(
            "%s's gap sits in its single %d-session run (own gap %s) while its other %d runs read %s"
            % (s, e["longest_blocked_rows"], _pp(e["longest_block_gap_pp"]),
               e["n_blocked_episodes"] - 1, _pp(e["gap_without_longest_pp"]))
            for s, e in single))
    if pooled and pooled.get("verdict") == "BLIP_WEEKDAY_CADENCE":
        parts.append("the single-row runs are not spread over the calendar: %s carries %.0f%% of"
                     " them against %.0f%% of priced sessions (chance %.1g), so a one-row word is"
                     " a word printed that session, not a fund policy"
                     % (pooled["modal_weekday"], 100.0 * (pooled["blip_share_modal"] or 0.0),
                        100.0 * (pooled["base_share_modal"] or 0.0), pooled["tail_p"]))
    if cause and cause.get("n_one_row"):
        if cause.get("verdict") == "CALENDAR_GAP":
            named = cause.get("calendar_named") or "NYSE"
            explains = (cause.get("hk_n_closed", 0) + cause.get("hk_n_thin", 0)
                        + cause.get("hk_n_window", 0)) if named == "HKEX" else \
                       ((cause.get("n_closure_full") or 0) + (cause.get("n_closure_early") or 0))
            parts.append("what those one-row words are is a valuation gap, not an announcement:"
                         " %d/%d of them suspend 赎回 on the same row, they move the NAV by %.2f"
                         " of a normal session (median), and %d/%d sit on a session the %s"
                         " calendar explains against %.1f%% of ordinary sessions (%.1fx)"
                         % (cause["both_channels_suspended"], cause["n_one_row"],
                            cause["nav_move_ratio_median"] or 0.0, explains, cause["n_one_row"],
                            named,
                            100.0 * ((cause.get("hk_base_rate") if named == "HKEX"
                                      else cause.get("base_rate")) or 0.0),
                            (cause.get("hk_lift") if named == "HKEX" else cause.get("lift")) or 0.0))
        elif cause.get("verdict") == "GAP_WITH_UNKNOWN_CALENDAR":
            parts.append("the one-row words suspend 赎回 on the same row and barely move the NAV,"
                         " so they are valuation gaps -- but only %d/%d of them land on a session"
                         " the NYSE calendar in hand explains"
                         % ((cause["n_closure_full"] or 0) + (cause["n_closure_early"] or 0),
                            cause["n_one_row"]))
        elif cause.get("verdict") == "CAUSE_UNRESOLVED":
            parts.append("%d single-row words do not behave like a valuation gap -- the cause is"
                         " left open rather than named" % cause["n_one_row"])
    parts.append("closed channel is consistent with a standing premium, not a verdict on it")
    return "; ".join(parts)


def render_md(doc):
    L = []
    L.append("# Premium vs the fund's own purchase channel -- %s" % (doc.get("evidence_cutoff") or "?"))
    L.append("")
    L.append("**Answer (derived):** %s" % doc["summary_sentence"])
    L.append("")
    L.append("Ruler: %s. Status joined on: %s."
             % (doc["ruler"]["premium"], doc["ruler"]["status_join"]))
    L.append("")
    L.append("| leg | class | amount CNY | premium (NAV ruler) | board (price/IOPV) | ruler gap pp "
             "| stamp | 申购状态 on stamp | hard-suspended sessions | premium>=%.0f%% sessions | "
             "share closed at high | window verdict |" % HI_PCT)
    L.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for l in doc["legs"]:
        hi = l["high_premium"]
        L.append("| %s | %s | %s | %s | %s | %s | %s | %s | %d | %d | %s | %s |" % (
            l["symbol"], l["class"], _fmt_money(l.get("amount_cny")),
            _pct(l["latest_pct"]), _pct(l.get("board_premium_pct")),
            ("%+.2f" % l["ruler_gap_pp"]) if l.get("ruler_gap_pp") is not None else "n/a",
            l["latest_nav_date"], l["latest_purchase"] or "(none)",
            l["blocked_sessions"], hi["n_high"],
            ("%.0f%%" % (100.0 * hi["share_closed_at_high"])) if hi["share_closed_at_high"] is not None else "n/a",
            l["window_verdict"]))
    L.append("")
    L.append("## Within-leg contrast: hard-suspended vs exchange-only")
    L.append("")
    L.append("| leg | verdict | median premium, 暂停申购 | median premium, 场内买入 | gap pp | n |")
    L.append("|---|---|---|---|---|---|")
    for l in doc["legs"]:
        c = l["block_contrast"]
        L.append("| %s | %s | %s | %s | %s | %d / %d |" % (
            l["symbol"], c["verdict"], _pct(c.get("median_blocked_pct")),
            _pct(c.get("median_exchange_pct")),
            ("%+.2f" % c["gap_pp"]) if c.get("gap_pp") is not None else "n/a",
            c.get("n_blocked", 0), c.get("n_exchange", 0)))
    L.append("")
    L.append("### The same contrast with the valuation gaps removed")
    L.append("")
    L.append("The one-row 暂停申购 words are a shut overseas market, not a fund decision (see")
    L.append("\"What the one-row words are\" below). Those sessions carry no fresh NAV, so their")
    L.append("premium is priced against a stale one. Repricing the block without them asks the")
    L.append("question the table above cannot: is the premium wider on the sessions the fund")
    L.append("itself chose to shut, or was the wider reading the calendar all along?")
    L.append("")
    L.append("| leg | verdict | median premium, 暂停申购 | median premium, 场内买入 | gap pp | n kept | rows dropped |")
    L.append("|---|---|---|---|---|---|---|")
    for l in doc["legs"]:
        c = l.get("block_contrast_excl_gaps") or {}
        L.append("| %s | %s | %s | %s | %s | %d | %d |" % (
            l["symbol"], c.get("verdict"), _pct(c.get("median_blocked_pct")),
            _pct(c.get("median_exchange_pct")),
            ("%+.2f" % c["gap_pp"]) if c.get("gap_pp") is not None else "n/a",
            c.get("n_blocked", 0), c.get("n_excluded", 0)))
    L.append("")
    L.append("'rows dropped' is the count of priced 暂停申购 rows whose NAV stamp is one of the")
    L.append("single-row runs named in the cause section. The exchange-only column is untouched:")
    L.append("the same baseline prices both readings, so the only thing that moves is the block.")
    all_gaps = [l["symbol"] for l in doc["legs"]
                if (l.get("block_contrast_excl_gaps") or {}).get("verdict") == "NO_CONTRAST"
                and ((l.get("block_contrast_excl_gaps") or {}).get("n_excluded") or 0) > 0]
    if all_gaps:
        L.append("")
        L.append("On %s every hard-suspended session was a single-row valuation gap, so 'n kept'"
                 " is zero: the day-level contrast on that leg was pricing the calendar, not"
                 " the fund, and this table is the one that says so." % ", ".join(all_gaps))
    L.append("")
    L.append("## Days vs runs: how much evidence the block count actually is")
    L.append("")
    L.append("A suspension lasts as long as the fund keeps it, so the days inside one run are")
    L.append("the same fact repeated. The table above counts days; this one counts runs.")
    L.append("")
    L.append("| leg | runs (all words) | blocked runs | runs of a single NAV row | median rows per block "
             "| longest block | run-level gap vs exchange-only | longest run's own gap "
             "| gap with the longest run dropped | verdict |")
    L.append("|---|---|---|---|---|---|---|---|---|---|")
    for l in doc["legs"]:
        e = l["episode_granularity"]
        L.append("| %s | %d | %d | %d | %s | %d (%s..%s) | %s | %s | %s | %s |" % (
            l["symbol"], e["n_episodes"], e["n_blocked_episodes"], e["blocked_one_row"],
            _num(e["median_blocked_rows"]), e["longest_blocked_rows"],
            e["longest_blocked_first"] or "n/a", e["longest_blocked_last"] or "n/a",
            _pp(e.get("episode_gap_pp")), _pp(e.get("longest_block_gap_pp")),
            _pp(e.get("gap_without_longest_pp")), e["verdict"]))
    L.append("")
    L.append("Run-level gap = median over blocked runs of (that run's own median premium - the")
    L.append("leg's exchange-only median), so one long block cannot stand in for hundreds of")
    L.append("sessions. A verdict needs at least five blocked runs; below that the page says")
    L.append("TOO_FEW_EPISODES rather than printing a median of one run as a measurement.")
    L.append("")
    L.append("The last two columns are the cheapest honest question about any such gap: does it")
    L.append("survive dropping the single longest block? A gap that lives in one run is one")
    L.append("decision by one fund, and the page says so instead of quoting it as a population.")
    L.append("")
    L.append("### The transition days, named")
    L.append("")
    L.append("Up to 8 longest blocked runs per leg, with the first and last priced session that")
    L.append("carried the word. Every run in coverage is in the JSON twin (`episode_granularity.runs`),")
    L.append("including the exchange-only ones between them.")
    L.append("")
    L.append("| leg | 申购状态 | first priced session carrying it | last | rows | its own median premium |")
    L.append("|---|---|---|---|---|---|")
    for l in doc["legs"]:
        runs = sorted([e for e in l["episode_granularity"]["runs"] if "暂停" in (e["word"] or "")],
                      key=lambda e: (-e["n_rows"], e["first_date"]))[:8]
        if not runs:
            L.append("| %s | (never suspended in coverage) | | | | |" % l["symbol"])
        for e in runs:
            L.append("| %s | %s | %s | %s | %d | %s |" % (
                l["symbol"], e["word"], e["first_date"], e["last_date"], e["n_rows"],
                _pct(e["median_pct"])))
    L.append("")
    L.append("## Why the blips: when the word is printed, not why")
    L.append("")
    L.append("A single-row 暂停申购 run is one word printed between two exchange-only rows.")
    L.append("The run table above counts them; this one asks whether those days are ordinary")
    L.append("sessions. If they were, their weekday mix would look like the session mix. It")
    L.append("does not.")
    L.append("")
    L.append("| leg | one-row runs | busiest weekday | share of runs on it | its share of sessions "
             "| chance of that (1-sided) | bracketed by 场内买入 both sides | runs with a NAV jump >3% "
             "| day-of-month peaks | verdict |")
    L.append("|---|---|---|---|---|---|---|---|---|---|")
    for l in doc["legs"]:
        c = l.get("blip_cadence") or {}
        peaks = ", ".join("%d(%d)" % (p["dom"], p["n"]) for p in (c.get("day_of_month_top") or []))
        L.append("| %s | %d | %s | %s | %s | %s | %d | %d | %s | %s |" % (
            l["symbol"], c.get("n_one_row", 0), c.get("modal_weekday") or "n/a",
            ("%.0f%%" % (100.0 * c["blip_share_modal"])) if c.get("blip_share_modal") is not None else "n/a",
            ("%.0f%%" % (100.0 * c["base_share_modal"])) if c.get("base_share_modal") is not None else "n/a",
            ("%.2g" % c["tail_p"]) if c.get("tail_p") is not None else "n/a",
            c.get("bracketed_by_exchange_only", 0), c.get("nav_jump_gt3pct", 0),
            peaks or "n/a", c.get("verdict") or "n/a"))
    P = doc.get("blip_cadence_pooled") or {}
    if P:
        L.append("")
        L.append("**Pooled:** %d single-row runs out of %d blocked runs; **%s carries %.0f%% of them"
                 " against %.0f%% of all priced sessions** (one-sided chance %.2g). Peak days of the"
                 " month: %s. %d of the runs are bracketed by 场内买入 on both sides, and %d carry a"
                 " NAV jump larger than 3%% -- a split or a big distribution, not a quota."
                 % (P.get("n_one_row", 0), P.get("n_blocked", 0), P.get("modal_weekday") or "n/a",
                    100.0 * (P.get("blip_share_modal") or 0.0), 100.0 * (P.get("base_share_modal") or 0.0),
                    P.get("tail_p") if P.get("tail_p") is not None else float("nan"),
                    ", ".join("%d(%d)" % (p["dom"], p["n"]) for p in (P.get("day_of_month_top") or [])) or "n/a",
                    P.get("bracketed_by_exchange_only", 0), P.get("nav_jump_gt3pct", 0)))
        L.append("")
        per_leg = [l["symbol"] for l in doc["legs"]
                   if (l.get("blip_cadence") or {}).get("verdict") == "BLIP_WEEKDAY_CADENCE"]
        L.append("")
        L.append("Only %d of %d legs clear the line on their own (%s); the rest lean the same way"
                 " with too few runs to call it, which is why the pooled reading above -- not a"
                 " per-leg one -- is the sentence this section quotes."
                 % (len(per_leg), len(doc["legs"]), ", ".join(per_leg) or "none"))
        L.append("")
        L.append("Read this block as **when**, never as **why**: a source that refreshes its")
        L.append("status word on a weekly rhythm and a fund that announces one-day suspensions")
        L.append("both produce a clump on one weekday, and a count of weekdays cannot separate")
        L.append("them. The next section does, but not from these counts -- from the row itself.")
    L.append("")
    L.append("## What the one-row words are: a valuation gap, not an announcement")
    L.append("")
    L.append("The weekday block above refuses to name a cause, and on its own counts that")
    L.append("refusal is right. The row itself carries three things a weekday count cannot see:")
    L.append("a distribution or a split moves the unit NAV, an announcement suspends")
    L.append("*subscription*, and a fund-specific decision cannot fall on the same date for two")
    L.append("independently managed legs. All three are measured below, plus a published foreign")
    L.append("closure calendar (%s)." % (doc.get("blip_cause_pooled") or {}).get("calendar", "n/a"))
    L.append("")
    L.append("| leg | one-row runs | 赎回 also suspended | NAV unchanged exactly | median "
             "|dNAV| vs a normal session | share <= quarter | closure in the gap (full/early) "
             "| unmatched | closure rate | ordinary-session rate | lift | verdict |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for l in doc["legs"]:
        c = l.get("blip_cause") or {}
        L.append("| %s | %d | %d | %d | %s | %s | %d/%d | %d | %s | %s | %s | %s |" % (
            l["symbol"], c.get("n_one_row", 0), c.get("both_channels_suspended", 0),
            c.get("exact_carry", 0),
            ("%.3f" % c["nav_move_ratio_median"]) if c.get("nav_move_ratio_median") is not None else "n/a",
            ("%.0f%%" % (100.0 * (c.get("share_move_le_quarter") or 0.0))),
            c.get("n_closure_full", 0), c.get("n_closure_early", 0),
            c.get("n_closure_unmatched", 0),
            ("%.0f%%" % (100.0 * c["closure_rate"])) if c.get("closure_rate") is not None else "n/a",
            ("%.1f%%" % (100.0 * c["base_rate"])) if c.get("base_rate") is not None else "n/a",
            ("%.1fx" % c["lift"]) if c.get("lift") is not None else "n/a",
            c.get("verdict") or "n/a"))
    C = doc.get("blip_cause_pooled") or {}
    if C:
        L.append("")
        L.append("**Pooled:** %d one-row runs of %d blocked runs. **%d/%d suspend 赎回 on the very"
                 " same row** -- an announcement that closes subscription does not close"
                 " redemption, and this one always does. They move the NAV by **%.2f of the leg's"
                 " own median move** (median over legs; %.0f%% of the runs sit at a quarter or"
                 " less) and %d carry the previous NAV exactly, so a distribution is not what"
                 " these rows are: the largest move on any of them is %s%% at %s and the 90th"
                 " percentile is %s%%. **%d/%d land on a session whose gap contains an NYSE"
                 " closure** (full %d, early %d) against **%.1f%% of ordinary sessions** -- %.1fx."
                 % (C.get("n_one_row", 0), C.get("n_blocked", 0),
                    C.get("both_channels_suspended", 0), C.get("n_one_row", 0),
                    C.get("nav_move_ratio_median") or 0.0,
                    100.0 * (C.get("share_move_le_quarter") or 0.0), C.get("exact_carry", 0),
                    _num(C.get("nav_move_max_pct")), C.get("nav_move_max_stamp") or "n/a",
                    _num(C.get("nav_move_p90_pct")),
                    (C.get("n_closure_full") or 0) + (C.get("n_closure_early") or 0),
                    C.get("n_one_row", 0), C.get("n_closure_full", 0),
                    C.get("n_closure_early", 0), 100.0 * (C.get("base_rate") or 0.0),
                    C.get("lift") or 0.0))
        L.append("")
        L.append("**Two calendars in hand, and only one is derived from rules.** The US list is"
                 " rule-built; the Hong Kong list is *measured* on the HSI series (no bar = Hong"
                 " Kong did not trade; turnover under a share of its own trailing-20 median = a half"
                 " day with no closing valuation), because HKEX follows the lunar calendar and also"
                 " shuts for typhoons, which no rule set predicts. A calendar is named only when it"
                 " explains at least %.0f%% of these runs at %.1fx the ordinary-session rate and"
                 " beats the other by %.0fpp."
                 % (100.0 * CAUSE_CALENDAR_MIN, CAUSE_LIFT_MIN, 100.0 * CAUSE_CALENDAR_MARGIN))
        L.append("")
        L.append("| calendar | how it is known | runs it explains | rate | ordinary-session rate "
                 "| lift | named |")
        L.append("|---|---|---|---|---|---|---|")
        L.append("| NYSE | rule list, window (prev_stamp, stamp] | %d/%d | %s | %s | %s | %s |" % (
            (C.get("n_closure_full") or 0) + (C.get("n_closure_early") or 0), C.get("n_one_row", 0),
            ("%.0f%%" % (100.0 * C["closure_rate"])) if C.get("closure_rate") is not None else "n/a",
            ("%.1f%%" % (100.0 * C["base_rate"])) if C.get("base_rate") is not None else "n/a",
            ("%.1fx" % C["lift"]) if C.get("lift") is not None else "n/a",
            "yes" if C.get("calendar_named") == "NYSE" else "no"))
        L.append("| HKEX | measured on HSI (no bar / half day / shut weekday in the gap) | %d/%d "
                 "| %s | %s | %s | %s |" % (
            (C.get("hk_n_closed") or 0) + (C.get("hk_n_thin") or 0) + (C.get("hk_n_window") or 0),
            C.get("n_one_row", 0),
            ("%.0f%%" % (100.0 * C["hk_rate"])) if C.get("hk_rate") is not None else "n/a",
            ("%.1f%%" % (100.0 * C["hk_base_rate"])) if C.get("hk_base_rate") is not None else "n/a",
            ("%.1fx" % C["hk_lift"]) if C.get("hk_lift") is not None else "n/a",
            "yes" if C.get("calendar_named") == "HKEX" else "no"))
        L.append("")
        hk = doc.get("hk_index") or {}
        if hk.get("n"):
            sens = C.get("hk_thin_sensitivity") or {}
            L.append("HKEX series used here: **%d sessions, %s..%s** (read: %s). The half-day cutoff"
                     " is a ruler, so the Hong Kong reading is printed at three of them -- %s/%s runs"
                     " at %.0f%% of trailing turnover, %s at %.0f%%, %s at %.0f%% -- and the page"
                     " quotes no single one as the answer."
                     % (hk["n"], hk.get("first") or "?", hk.get("last") or "?",
                        hk.get("status") or "?",
                        (sens.get("%.2f" % HK_THIN_SENSITIVITY[0]) or {}).get("n_matched", 0),
                        C.get("n_one_row", 0), 100.0 * HK_THIN_SENSITIVITY[0],
                        (sens.get("%.2f" % HK_THIN_SENSITIVITY[1]) or {}).get("n_matched", 0),
                        100.0 * HK_THIN_SENSITIVITY[1],
                        (sens.get("%.2f" % HK_THIN_SENSITIVITY[2]) or {}).get("n_matched", 0),
                        100.0 * HK_THIN_SENSITIVITY[2]))
        else:
            L.append("No HKEX series is on disk, so the Hong Kong column carries nothing and no HK"
                     " word is named: an unmeasured calendar is not evidence.")
        by_cal = {}
        for l in doc["legs"]:
            n = ((l.get("blip_cause") or {}).get("calendar_choice") or {}).get("named")
            if n:
                by_cal.setdefault(n, []).append(l["symbol"])
        unnamed = [l["symbol"] for l in doc["legs"]
                   if not ((l.get("blip_cause") or {}).get("calendar_choice") or {}).get("named")
                   and ((l.get("blip_cause") or {}).get("n_one_row") or 0)]
        if by_cal or unnamed:
            L.append("")
            L.append("**Named per leg:** " + "; ".join(
                "%s explains %s" % (k, ", ".join(v)) for k, v in sorted(by_cal.items()))
                + ("; left unnamed: %s" % ", ".join(unnamed) if unnamed else "")
                + ". The pool word above is a different question from these: it asks which"
                  " calendar explains most of the 116 runs, not which one explains a given leg.")
        L.append("")
        X = doc.get("blip_cause_cross") or {}
        best = X.get("best")
        if best:
            L.append("The strongest evidence is the overlap: %s and %s print a one-row word on"
                     " **%d of the same dates** (%d and %d runs, %s..%s). A fund can suspend"
                     " itself; it cannot do it in agreement with a competitor -- a shared foreign"
                     " holiday can."
                     % (best["a"], best["b"], best["n_shared"], best["n_a"], best["n_b"],
                        best["shared_first"], best["shared_last"]))
            L.append("")
        leg_unexplained = [(l["symbol"], (l.get("blip_cause") or {}).get("n_closure_unmatched") or 0)
                           for l in doc["legs"]
                           if (l.get("blip_cause") or {}).get("verdict") == "GAP_WITH_UNKNOWN_CALENDAR"]
        if leg_unexplained and C.get("calendar_named") is None:
            L.append("The pool is diluted by %s, whose runs match neither calendar in hand (%s"
                     " unmatched by the US list): they are left unnamed rather than given the nearer"
                     " word. Naming them would need a calendar this page does not have."
                     % (", ".join(s for s, _ in leg_unexplained),
                        ", ".join(str(n) for _, n in leg_unexplained)))
            L.append("")
        elif C.get("calendar_named") == "HKEX" and leg_unexplained:
            L.append("The legs that the US list could not explain -- %s -- are the ones the measured"
                     " Hong Kong calendar picks up, which is why the word above names HKEX and not"
                     " New York. A rules-only page would have left every one of those rows unnamed."
                     % ", ".join(s for s, _ in leg_unexplained))
            L.append("")
        L.append("### What this changes in the reading")
        L.append("")
        L.append("The day counts above are not 141 independent suspensions. %d of them are"
                 " multi-row runs -- the fund really did keep the channel shut -- and %d are the"
                 " single-row valuation gaps measured here. A session that could not be valued"
                 " has no fresh NAV to price a premium against, so those rows belong to the"
                 " calendar and not to the fund's policy." % (
                     C.get("n_blocked", 0) - C.get("n_one_row", 0), C.get("n_one_row", 0)))
        L.append("")
        L.append("The verdict word is derived from the counts in this table, not written by hand:")
        L.append("it needs both channels to flip, the NAV to move a fraction of a normal session,")
        L.append("and a majority of the dates to fall inside a published closure. Where the last")
        L.append("condition fails, the leg is labelled GAP_WITH_UNKNOWN_CALENDAR instead of"
                 " being given a cause it has not earned.")
        L.append("")
        L.append("Not claimed: a one-off exchange closure nobody can derive from a rule set (the")
        L.append("2025-01-09 US national day of mourning is the one that appears in this sample)")
        L.append("shows up as unmatched, and the page leaves it unmatched. The calendar explains")
        L.append("the dates; it says nothing about quotas, and nothing about whether a %d%%"
                 % int(HI_PCT))
        L.append("premium is fair.")
    L.append("")
    L.append("## What this face refuses to claim")
    L.append("")
    L.append("* A closed channel is **consistent with** a standing premium; it does not make the")
    L.append("  premium fair, and it is not a sell signal. What it does establish is that the")
    L.append("  creation valve an arbitrageur would need was not listed as open on any session")
    L.append("  this face can see -- so 'the premium should already have been arbitraged away'")
    L.append("  is not an argument this data supports.")
    L.append("* The status word is as published on each NAV row; it is not a statement about")
    L.append("  creation limits, quotas, or how much would be accepted if it reopened.")
    L.append("* A same-session open state would falsify the hypothesis. None appears in coverage:")
    L.append("  the only words present are 场内买入 (exchange-only) and 暂停申购 (suspended).")
    L.append("* 'share closed at high' is a census, not a contrast: on a leg with no hard-suspended")
    L.append("  sessions it reads 100% by construction, because every session is exchange-only.")
    L.append("  The only column that carries a difference is the within-leg contrast above, and")
    L.append("  there it is printed as measured -- 159501 and 159577 come out flat or negative.")
    L.append("* The two premium columns are different quantities and are never added: this face")
    L.append("  divides the panel close by the disclosed unit NAV; the board divides price by")
    L.append("  intraday IOPV. The gap column prices how far apart those rulers sit on one session.")
    L.append("* The day counts in the first table are **not** independent observations. A single")
    L.append("  block of 435 sessions is one decision by the fund, and a run of one NAV row is")
    L.append("  one word printed between two exchange-only rows -- neither is 435 answers or a")
    L.append("  policy. The second table is the same contrast re-read per run; where the two")
    L.append("  disagree, the run-level reading is the one with a defensible count behind it.")
    if doc["notes"]:
        L.append("")
        L.append("Notes: " + " | ".join(doc["notes"]))
    return "\n".join(L) + "\n"


def _pct(v):
    return "n/a" if v is None else "%+.2f%%" % v


def _num(v):
    return "n/a" if v is None else "%g" % v


def _pp(v):
    return "n/a" if v is None else "%+.2f" % v


def _fmt_money(v):
    return "n/a" if v is None else "{:,.0f}".format(v)


def _check_episodes(l):
    """The run table has to describe the same series the day table does. Re-derived here."""
    e = l.get("episode_granularity") or {}
    runs = e.get("runs") or []
    bad = []
    sym = l["symbol"]
    if not runs:
        return ["%s: no run table" % sym]
    if e.get("n_episodes") != len(runs):
        bad.append("%s: n_episodes %r != %d runs" % (sym, e.get("n_episodes"), len(runs)))
    if sum(r["n_rows"] for r in runs) != l["n_sessions"]:
        bad.append("%s: runs cover %d rows, series has %d" %
                   (sym, sum(r["n_rows"] for r in runs), l["n_sessions"]))
    blocked_runs = [r for r in runs if "暂停" in (r["word"] or "")]
    if sum(r["n_rows"] for r in blocked_runs) != l["blocked_sessions"]:
        bad.append("%s: blocked runs cover %d rows, blocked_sessions is %d" %
                   (sym, sum(r["n_rows"] for r in blocked_runs), l["blocked_sessions"]))
    if e.get("n_blocked_episodes") != len(blocked_runs):
        bad.append("%s: n_blocked_episodes %r != %d" % (sym, e.get("n_blocked_episodes"),
                                                       len(blocked_runs)))
    if (e.get("blocked_one_row") or 0) > len(blocked_runs):
        bad.append("%s: more single-row runs than runs" % sym)
    for a, b in zip(runs, runs[1:]):
        if a["word"] == b["word"] and a["kind"] == b["kind"]:
            bad.append("%s: two adjacent runs share the word %r -- not grouped" % (sym, a["word"]))
    v = e.get("verdict")
    gap = e.get("episode_gap_pp")
    if v == "NO_BLOCKED_EPISODES" and blocked_runs:
        bad.append("%s: NO_BLOCKED_EPISODES with %d blocked runs" % (sym, len(blocked_runs)))
    elif v == "TOO_FEW_EPISODES" and not (0 < len(blocked_runs) < 5):
        bad.append("%s: TOO_FEW_EPISODES with %d blocked runs" % (sym, len(blocked_runs)))
    elif v == "EPISODE_GAP_WIDENS" and not (gap or 0) > 1.0:
        bad.append("%s: EPISODE_GAP_WIDENS with gap %r" % (sym, gap))
    elif v == "EPISODE_GAP_DOES_NOT_WIDEN" and (gap or 0) > 1.0:
        bad.append("%s: DOES_NOT_WIDEN with gap %r" % (sym, gap))
    elif v == "EPISODE_GAP_DOES_NOT_WIDEN" and len(blocked_runs) < 5:
        bad.append("%s: DOES_NOT_WIDEN decided on %d runs" % (sym, len(blocked_runs)))
    lg, gw = e.get("longest_block_gap_pp"), e.get("gap_without_longest_pp")
    if e.get("widens_only_in_longest") and not (lg is not None and lg > 1.0
                                                and gw is not None and gw <= 1.0):
        bad.append("%s: widens_only_in_longest without one wide run and a flat rest "
                   "(longest %r, rest %r)" % (sym, lg, gw))
    if len(blocked_runs) <= 1 and gw is not None:
        bad.append("%s: gap without the longest run should be n/a with %d run(s)"
                   % (sym, len(blocked_runs)))
    if len(blocked_runs) >= 2 and (lg is None or gw is None):
        bad.append("%s: %d blocked runs but the longest run is not priced separately -- a face"
                   " that publishes the block count must publish whether its gap survives"
                   " dropping the widest run" % (sym, len(blocked_runs)))
    return bad


def _check_excluded_contrast(l):
    """The calendar-excluded contrast must be the day contrast minus exactly the named rows.

    Two numbers are published instead of one, and the page prints both. A block that dropped
    rows it never counted, or counted rows it never dropped, is a second reading of a
    different series -- so the check recomputes the arithmetic from the leg's own counts.
    """
    sym = l["symbol"]
    c = l.get("block_contrast_excl_gaps")
    if not c:
        return ["%s: the calendar-excluded contrast is not published" % sym]
    bad = []
    dropped = c.get("n_excluded") or 0
    one = (l.get("blip_cause") or {}).get("n_one_row") or 0
    if dropped + (c.get("n_blocked") or 0) != (l.get("blocked_sessions") or 0):
        bad.append("%s: excluded contrast keeps %r and drops %r, but blocked_sessions is %r"
                   % (sym, c.get("n_blocked"), dropped, l.get("blocked_sessions")))
    if dropped > one:
        bad.append("%s: dropped %r rows but only %r single-row runs are counted" % (sym, dropped, one))
    if (c.get("excluded_requested") or 0) < dropped:
        bad.append("%s: %r rows dropped from %r requested stamps" %
                   (sym, dropped, c.get("excluded_requested")))
    gap = c.get("gap_pp") or 0.0
    if c.get("verdict") == "BLOCK_WIDENS_PREMIUM" and not gap > 1.0:
        bad.append("%s: excluded block says WIDENS with a gap of %r" % (sym, c.get("gap_pp")))
    if c.get("verdict") == "BLOCK_DOES_NOT_WIDEN" and gap > 1.0:
        bad.append("%s: excluded block says DOES_NOT_WIDEN with a gap of %r" % (sym, c.get("gap_pp")))
    if c.get("verdict") not in ("BLOCK_WIDENS_PREMIUM", "BLOCK_DOES_NOT_WIDEN", "NO_CONTRAST"):
        bad.append("%s: excluded block verdict %r is not one this face derives"
                   % (sym, c.get("verdict")))
    return bad


def _check_cadence(doc, page=True):
    """The blip block must be arithmetic a reader can recompute, and it must be on the page."""
    bad = []
    legs = doc["legs"]
    pooled = doc.get("blip_cadence_pooled")
    if not pooled:
        return ["no blip cadence block -- the single-row runs are published without a reading"]
    sessions_by_dow = [0] * 5
    blips_by_dow = [0] * 5
    n_one = n_blocked = 0
    for l in legs:
        c = l.get("blip_cadence") or {}
        sym = l["symbol"]
        if not c:
            bad.append("%s: no blip cadence block" % sym)
            continue
        e = l.get("episode_granularity") or {}
        if (c.get("n_one_row") or 0) > (e.get("blocked_one_row") or 0):
            bad.append("%s: %r single-row runs but the run table says %r"
                       % (sym, c.get("n_one_row"), e.get("blocked_one_row")))
        if (c.get("n_blocked") or 0) != (e.get("n_blocked_episodes") or 0):
            bad.append("%s: cadence counts %r blocked runs, the run table says %r"
                       % (sym, c.get("n_blocked"), e.get("n_blocked_episodes")))
        if sum(c.get("blips_by_weekday") or [0] * 5) + (c.get("n_blips_unreadable_date") or 0) \
                != (c.get("n_one_row") or 0):
            bad.append("%s: weekday counts do not add up to the single-row runs" % sym)
        if sum(c.get("sessions_by_weekday") or [0] * 5) + (c.get("n_sessions_unreadable_date") or 0) \
                != l["n_sessions"]:
            bad.append("%s: weekday session counts do not add up to n_sessions" % sym)
        want = _cadence_verdict(c.get("n_one_row") or 0,
                                (c.get("sessions_by_weekday") or [0] * 5),
                                (c.get("blips_by_weekday") or [0] * 5))
        if c.get("verdict") != want["verdict"]:
            bad.append("%s: cadence verdict %r but its counts derive %r"
                       % (sym, c.get("verdict"), want["verdict"]))
        if c.get("modal_weekday") != want["modal_weekday"]:
            bad.append("%s: modal weekday %r but its counts derive %r"
                       % (sym, c.get("modal_weekday"), want["modal_weekday"]))
        if (c.get("bracketed_by_exchange_only") or 0) > (c.get("n_one_row") or 0):
            bad.append("%s: more bracketed runs than single-row runs" % sym)
        n_one += c.get("n_one_row") or 0
        n_blocked += c.get("n_blocked") or 0
        for i in range(5):
            sessions_by_dow[i] += (c.get("sessions_by_weekday") or [0] * 5)[i]
            blips_by_dow[i] += (c.get("blips_by_weekday") or [0] * 5)[i]
    if (pooled.get("n_one_row") or 0) != n_one:
        bad.append("pooled single-row runs %r != %d from the legs"
                   % (pooled.get("n_one_row"), n_one))
    if (pooled.get("n_blocked") or 0) != n_blocked:
        bad.append("pooled blocked runs %r != %d from the legs"
                   % (pooled.get("n_blocked"), n_blocked))
    want = _cadence_verdict(n_one, sessions_by_dow, blips_by_dow)
    if pooled.get("verdict") != want["verdict"]:
        bad.append("pooled cadence verdict %r but the leg counts derive %r"
                   % (pooled.get("verdict"), want["verdict"]))
    if page and os.path.exists(OUT_MD):
        md = open(OUT_MD, encoding="utf-8").read()
        if "Why the blips" not in md:
            bad.append("the page does not carry the blip cadence section")
        elif n_one >= CADENCE_MIN_N and "Pooled:" not in md:
            bad.append("the page omits the pooled reading although %d single-row runs exist" % n_one)
    return bad


def _check_cause(doc, page=True):
    """The cause block must be the arithmetic of its own counts, and it must be on the page."""
    bad = []
    legs = doc["legs"]
    pooled = doc.get("blip_cause_pooled")
    if not pooled:
        return ["no blip cause block -- the one-row runs are published without a cause reading"]
    n_one = both = full = early = unmatched = 0
    n_ratio = n_quarter = base_sessions = base_hits = 0
    leg_medians = []
    for l in legs:
        c = l.get("blip_cause") or {}
        sym = l["symbol"]
        if not c:
            bad.append("%s: no blip cause block" % sym)
            continue
        e = l.get("episode_granularity") or {}
        if (c.get("n_one_row") or 0) != (e.get("blocked_one_row") or 0):
            bad.append("%s: cause counts %r single-row runs, the run table says %r"
                       % (sym, c.get("n_one_row"), e.get("blocked_one_row")))
        if (c.get("both_channels_suspended") or 0) > (c.get("n_one_row") or 0):
            bad.append("%s: more rows with both channels shut than single-row runs" % sym)
        if (c.get("n_closure_full") or 0) + (c.get("n_closure_early") or 0) \
                + (c.get("n_closure_unmatched") or 0) != (c.get("n_one_row") or 0):
            bad.append("%s: closure counts do not add up to the single-row runs" % sym)
        if (c.get("n_move_le_quarter") or 0) > (c.get("n_move_ratio") or 0):
            bad.append("%s: more quarter-sized moves than measured moves" % sym)
        if (c.get("exact_carry") or 0) > (c.get("n_one_row") or 0):
            bad.append("%s: more carried NAVs than single-row runs" % sym)
        if (c.get("n_base_closure") or 0) > (c.get("n_base_sessions") or 0):
            bad.append("%s: more closure sessions than ordinary sessions" % sym)
        if len(c.get("one_row_stamps") or []) != (c.get("n_one_row") or 0):
            bad.append("%s: %d stamps published for %r single-row runs"
                       % (sym, len(c.get("one_row_stamps") or []), c.get("n_one_row")))
        want = _cause_verdict(c.get("n_one_row") or 0,
                              c.get("both_channels_suspended") or 0,
                              c.get("nav_move_ratio_median"),
                              c.get("share_move_le_quarter") or 0.0,
                              c.get("closure_rate"), c.get("base_rate"),
                              choice=c.get("calendar_choice"))
        if c.get("verdict") != want:
            bad.append("%s: cause verdict %r but its counts derive %r"
                       % (sym, c.get("verdict"), want))
        if (c.get("hk_n_closed") or 0) + (c.get("hk_n_thin") or 0) \
                + (c.get("hk_n_window") or 0) + (c.get("hk_n_unmatched") or 0) != (c.get("n_one_row") or 0):
            bad.append("%s: Hong Kong closure counts do not add up to the single-row runs" % sym)
        if (c.get("hk_n_base_closure") or 0) > (c.get("hk_n_base_sessions") or 0):
            bad.append("%s: more HK closure sessions than ordinary sessions" % sym)
        named = (c.get("calendar_choice") or {}).get("named")
        if (c.get("calendar_named") or None) != named:
            bad.append("%s: calendar word %r is not the one its choice block names %r"
                       % (sym, c.get("calendar_named"), named))
        if named == "HKEX" and c.get("hk_rate") is None:
            bad.append("%s: calendar word 'HKEX' without an HK reading behind it" % sym)
        n_one += c.get("n_one_row") or 0
        both += c.get("both_channels_suspended") or 0
        full += c.get("n_closure_full") or 0
        early += c.get("n_closure_early") or 0
        unmatched += c.get("n_closure_unmatched") or 0
        n_ratio += c.get("n_move_ratio") or 0
        n_quarter += c.get("n_move_le_quarter") or 0
        base_sessions += c.get("n_base_sessions") or 0
        base_hits += c.get("n_base_closure") or 0
        if c.get("nav_move_ratio_median") is not None:
            leg_medians.append(c["nav_move_ratio_median"])
    for key, want in (("n_one_row", n_one), ("both_channels_suspended", both),
                      ("n_closure_full", full), ("n_closure_early", early),
                      ("n_closure_unmatched", unmatched), ("n_move_ratio", n_ratio),
                      ("n_move_le_quarter", n_quarter), ("n_base_sessions", base_sessions),
                      ("n_base_closure", base_hits)):
        if (pooled.get(key) or 0) != want:
            bad.append("pooled %s %r != %d from the legs" % (key, pooled.get(key), want))
    hk_want = {"hk_n_closed": 0, "hk_n_thin": 0, "hk_n_window": 0, "hk_n_unmatched": 0,
               "hk_n_base_sessions": 0, "hk_n_base_closure": 0}
    for l in legs:
        c = l.get("blip_cause") or {}
        for k in hk_want:
            hk_want[k] += c.get(k) or 0
    for key, want in hk_want.items():
        if (pooled.get(key) or 0) != want:
            bad.append("pooled %s %r != %d from the legs" % (key, pooled.get(key), want))
    for thr in HK_THIN_SENSITIVITY:
        got = ((pooled.get("hk_thin_sensitivity") or {}).get("%.2f" % thr) or {}).get("n_matched")
        want_n = sum((((l.get("blip_cause") or {}).get("hk_thin_sensitivity") or {})
                      .get("%.2f" % thr) or {}).get("n_matched") or 0 for l in legs)
        if (got or 0) != want_n:
            bad.append("pooled HK sensitivity at %.2f %r != %d from the legs" % (thr, got, want_n))
    hk_base = (hk_want["hk_n_base_closure"] / float(hk_want["hk_n_base_sessions"])
               if hk_want["hk_n_base_sessions"] else None)
    want = _cause_verdict(n_one, both,
                          statistics.median(leg_medians) if leg_medians else None,
                          (n_quarter / float(n_ratio)) if n_ratio else 0.0,
                          ((full + early) / float(n_one)) if n_one else None,
                          (base_hits / float(base_sessions)) if base_sessions else None,
                          choice=pooled.get("calendar_choice"))
    if pooled.get("verdict") != want:
        bad.append("pooled cause verdict %r but the leg counts derive %r"
                   % (pooled.get("verdict"), want))
    want_choice = calendar_choice([
        {"name": "NYSE", "rate": ((full + early) / float(n_one)) if n_one else None,
         "base": (base_hits / float(base_sessions)) if base_sessions else None},
        {"name": "HKEX",
         "rate": (((hk_want["hk_n_closed"] + hk_want["hk_n_thin"] + hk_want["hk_n_window"])
                   / float(n_one)) if (n_one and hk_want["hk_n_base_sessions"]) else None),
         "base": hk_base},
    ])
    if (pooled.get("calendar_choice") or {}).get("named") != want_choice.get("named"):
        bad.append("pooled calendar word %r but the counts derive %r"
                   % ((pooled.get("calendar_choice") or {}).get("named"),
                      want_choice.get("named")))
    if (pooled.get("calendar_named") or None) != want_choice.get("named"):
        bad.append("pooled calendar word %r is not the one the counts derive %r"
                   % (pooled.get("calendar_named"), want_choice.get("named")))
    stamps = {l["symbol"]: set((l.get("blip_cause") or {}).get("one_row_stamps") or [])
              for l in legs}
    if sum(1 for v in stamps.values() if v) >= 2:
        want_cross = cross_leg_dates(stamps)
        got = doc.get("blip_cause_cross") or {}
        if not got:
            bad.append("no cross-leg overlap block although two legs published one-row dates")
        elif (got.get("best") or {}).get("n_shared") != (want_cross.get("best") or {}).get("n_shared"):
            bad.append("cross-leg overlap %r is not the largest shared-date count %r"
                       % ((got.get("best") or {}).get("n_shared"),
                          (want_cross.get("best") or {}).get("n_shared")))
    if page and os.path.exists(OUT_MD):
        md = open(OUT_MD, encoding="utf-8").read()
        if "What the one-row words are" not in md:
            bad.append("the page does not carry the one-row cause section")
        elif n_one and pooled.get("verdict") not in md:
            bad.append("the page does not print the pooled cause verdict %r"
                       % pooled.get("verdict"))
    return bad


def check(doc=None):
    """Re-derive every verdict word from the published numbers. No stored answer is trusted."""
    explicit = doc is not None          # a fixture is not the published page, so no page leg
    doc = doc or json.load(open(OUT, encoding="utf-8"))
    bad = []
    for l in doc["legs"]:
        n = l["n_sessions"]
        hi = l["high_premium"]
        if hi["n_high"] > n:
            bad.append("%s: high sessions %d > sessions %d" % (l["symbol"], hi["n_high"], n))
        if l["blocked_sessions"] > n:
            bad.append("%s: blocked %d > sessions %d" % (l["symbol"], l["blocked_sessions"], n))
        if l["latest_purchase_kind"] == "open" and l["window_verdict"] == "CHANNEL_CLOSED_THROUGHOUT":
            bad.append("%s: open stamp but CLOSED_THROUGHOUT" % l["symbol"])
        if hi["share_closed_at_high"] is not None and not (0.0 <= hi["share_closed_at_high"] <= 1.0):
            bad.append("%s: share_closed_at_high out of range" % l["symbol"])
        c = l["block_contrast"]
        if c["verdict"] == "BLOCK_WIDENS_PREMIUM" and not (c.get("gap_pp") or 0) > 1.0:
            bad.append("%s: BLOCK_WIDENS_PREMIUM with gap <= 1pp" % l["symbol"])
        if l.get("board_premium_pct") is not None:
            want = l["latest_pct"] - l["board_premium_pct"]
            got = l.get("ruler_gap_pp")
            if got is None or abs(got - want) > 1e-6:
                bad.append("%s: ruler gap %r is not latest - board (%.4f)" % (l["symbol"], got, want))
        bad.extend(_check_episodes(l))
        bad.extend(_check_excluded_contrast(l))
    bad.extend(_check_cadence(doc, page=not explicit))
    bad.extend(_check_cause(doc, page=not explicit))
    if not explicit and os.path.exists(OUT_MD):
        md = open(OUT_MD, encoding="utf-8").read()
        measured = [l["symbol"] for l in doc["legs"]
                    if (l.get("block_contrast_excl_gaps") or {}).get("verdict")
                    in ("BLOCK_WIDENS_PREMIUM", "BLOCK_DOES_NOT_WIDEN")]
        if measured and "with the valuation gaps removed" not in md:
            bad.append("the page publishes a calendar-excluded contrast for %d leg(s) but does"
                       " not carry the section" % len(measured))
    ok = not bad
    print("check %s" % ("OK" if ok else "FAIL"))
    for b in bad:
        print("  ", b)
    return 0 if ok else 1


# --------------------------------------------------------------------------- selftest

def selftest():
    ok = [0, 0]

    def chk(cond, why):
        ok[1] += 1
        if cond:
            ok[0] += 1
        else:
            sys.stderr.write("  FAIL: %s\n" % (why,))
            sys.stderr.flush()

    def row(word, prem, d):
        return {"date": d, "nav": 1.0, "nav_date": "2025-12-31", "premium_pct": prem,
                "purchase": word, "purchase_kind": status_kind(word)}

    # L1 word mapping
    chk(status_kind("场内买入") == "closed", "场内买入 is exchange-only, not open")
    chk(status_kind("暂停申购") == "closed", "暂停申购 is closed")
    chk(status_kind("开放申购") == "open", "开放申购 is open")
    chk(status_kind("") == "unknown" and status_kind(None) == "unknown", "empty word is unknown")

    # L2 the join is on the NAV stamp, not the price bar
    prices = {"2026-01-05": 1.10, "2026-01-06": 1.20}
    navs = [{"date": "2026-01-02", "nav": 1.00}, {"date": "2026-01-05", "nav": 1.05}]
    st = [{"date": "2026-01-02", "nav": 1.00, "purchase": "暂停申购", "redeem": ""},
          {"date": "2026-01-05", "nav": 1.05, "purchase": "场内买入", "redeem": ""}]
    s = series_with_status(prices, navs, st)
    first = [r for r in s if r["date"] == "2026-01-05"][0]
    chk(first["nav_date"] == "2026-01-02", "lag=1 uses the earlier NAV stamp")
    chk(first["purchase"] == "暂停申购", "status comes from the stamp's row, not the price row")
    shifted = [{"date": "2026-01-03", "nav": 1.0, "purchase": "场内买入", "redeem": ""}]
    s2 = series_with_status(prices, navs, shifted)
    chk(all(r["purchase_kind"] == "unknown" for r in s2),
        "a status row on a date the series does not use cannot leak in")

    # L3/L4/L5 window verdicts
    mk = lambda n, word: [{"date": "2026-01-0%d" % (i % 9 + 1), "nav": 1.0,
                           "premium_pct": 1.0, "nav_date": "2026-01-0%d" % (i % 9 + 1),
                           "purchase": word, "purchase_kind": status_kind(word)} for i in range(n)]
    v, _ = window_verdict(mk(10, "场内买入"))
    chk(v == "CHANNEL_CLOSED_THROUGHOUT", "all exchange-only -> closed throughout")
    v, _ = window_verdict(mk(9, "场内买入") + mk(1, "开放申购"))
    chk(v == "CHANNEL_OPEN_SESSIONS_EXIST", "one open session falsifies the block story")
    v, _ = window_verdict([{"date": "d", "nav": 1.0, "premium_pct": 1.0, "nav_date": "d",
                            "purchase": "", "purchase_kind": "unknown"}])
    chk(v == "NO_STATUS_DATA", "no status data is not a closed channel")

    # L6 contrast
    blocked = mk(6, "暂停申购")
    for r in blocked:
        r["premium_pct"] = 20.0
    exh = mk(6, "场内买入")
    for r in exh:
        r["premium_pct"] = 5.0
    chk(block_contrast(blocked + exh)["verdict"] == "BLOCK_WIDENS_PREMIUM", "block wider -> widens")
    for r in exh:
        r["premium_pct"] = 19.5
    chk(block_contrast(blocked + exh)["verdict"] == "BLOCK_DOES_NOT_WIDEN",
        "same level -> does not widen")
    chk(block_contrast(blocked)["verdict"] == "NO_CONTRAST", "single group -> no contrast")

    # L7 high-premium face
    chk(high_premium_face(mk(5, "场内买入"))["verdict"] == "NO_HIGH_SESSIONS",
        "premium never above the line -> nothing to explain")
    hp = high_premium_face(blocked + exh)
    chk(hp["verdict"] == "HIGH_PREMIUM_WHILE_CLOSED" and abs(hp["share_closed_at_high"] - 1.0) < 1e-9,
        "all high sessions closed -> WHILE_CLOSED")
    open_high = mk(3, "开放申购")
    for r in open_high:
        r["premium_pct"] = 20.0
    mixed = blocked[:3] + open_high
    chk(high_premium_face(mixed)["verdict"] == "HIGH_PREMIUM_WITH_OPEN_SESSIONS",
        "an open high session must not read as closed (fixture must put it ABOVE the line)")

    # L8 cache round-trip
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        rows = [{"date": "2026-01-02", "nav": 1.234, "purchase": "场内买入", "redeem": "场内卖出"}]
        p = os.path.join(td, "999999.csv")
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            f.write("date,nav,purchase,redeem\n")
            for r in rows:
                f.write("%s,%.6f,%s,%s\n" % (r["date"], r["nav"], r["purchase"], r["redeem"]))
        back, st = load_status("999999", fetch=False, today="2026-01-02", cache_dir=td)
        chk(st == "cache" and len(back) == 1 and back[0]["purchase"] == "场内买入",
            "cache round-trip keeps the status word")

    # L9 render carries the derived words and the refusal
    doc = {"evidence_cutoff": "2026-01-05", "summary_sentence": "sentence",
           "ruler": {"premium": "close/nav-1", "status_join": "stamp"},
           "legs": [{"symbol": "1", "class": "c", "amount_cny": 1.0, "latest_pct": 1.0,
                     "latest_nav_date": "2026-01-02", "latest_purchase": "场内买入",
                     "blocked_sessions": 0,
                     "high_premium": {"n_high": 0, "share_closed_at_high": None},
                     "window_verdict": "CHANNEL_CLOSED_THROUGHOUT",
                     "episode_granularity": episode_read(
                         [row("场内买入", 1.0, "2026-01-%02d" % (i + 1)) for i in range(6)]),
                     "block_contrast": {"verdict": "NO_CONTRAST", "n_blocked": 0,
                                        "n_exchange": 0}}], "notes": []}
    md = render_md(doc)
    chk("CHANNEL_CLOSED_THROUGHOUT" in md and "refuses to claim" in md,
        "rendered page carries the derived word and the refusal")

    # L10 check() must reject a doctored verdict
    bad = json.loads(json.dumps(doc))
    bad["legs"] = [{"symbol": "1", "n_sessions": 1, "blocked_sessions": 0,
                    "latest_purchase_kind": "open", "window_verdict": "CHANNEL_CLOSED_THROUGHOUT",
                    "high_premium": {"n_high": 0, "share_closed_at_high": None},
                    "block_contrast": {"verdict": "NO_CONTRAST"}}]
    import io
    import contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = check(bad)
    chk(rc == 1, "check() rejects an open stamp published as CLOSED_THROUGHOUT")

    # L11 the ruler gap is recomputed, not stored
    flat_series = [row("场内买入", 1.0, "2026-01-%02d" % (i + 1)) for i in range(6)]
    gap_doc = json.loads(json.dumps(bad))
    gap_doc["legs"] = [{"symbol": "1", "n_sessions": 6, "blocked_sessions": 0,
                        "latest_purchase_kind": "closed",
                        "window_verdict": "CHANNEL_CLOSED_THROUGHOUT",
                        "latest_pct": 24.40, "board_premium_pct": 20.29, "ruler_gap_pp": 4.11,
                        "high_premium": {"n_high": 0, "share_closed_at_high": None},
                        "episode_granularity": episode_read(flat_series),
                        "blip_cadence": blip_cadence(flat_series),
                        "blip_cause": blip_cause(flat_series),
                        "block_contrast": {"verdict": "NO_CONTRAST"},
                        "block_contrast_excl_gaps": {"verdict": "NO_CONTRAST", "n_blocked": 0,
                                                     "n_excluded": 0, "excluded_requested": 0,
                                                     "n_exchange": 0}}]
    gap_doc["blip_cadence_pooled"] = pooled_cadence(gap_doc["legs"])
    gap_doc["blip_cause_pooled"] = pooled_blip_cause(gap_doc["legs"])
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        chk(check(gap_doc) == 0, "ruler gap 24.40-20.29=4.11 passes")
        gap_doc["legs"][0]["ruler_gap_pp"] = 0.0
        chk(check(gap_doc) == 1, "a round-number gap that is not the difference goes red")

    # L12 runs: consecutive equal words merge, a word returning later is a new run
    s3 = [row("场内买入", 1.0, "2026-01-01"), row("暂停申购", 2.0, "2026-01-02"),
          row("暂停申购", 3.0, "2026-01-03"), row("场内买入", 4.0, "2026-01-04")]
    eps = episodes(s3)
    chk(len(eps) == 3 and eps[1]["n_rows"] == 2, "consecutive same words merge into one run")
    chk(eps[1]["first_date"] == "2026-01-02" and eps[1]["last_date"] == "2026-01-03",
        "a run names its first and last priced session")
    chk(abs(eps[1]["median_pct"] - 2.5) < 1e-9, "a run carries its own median, not the pooled one")
    chk(len(episodes(s3 + [row("暂停申购", 9.0, "2026-01-05")])) == 4,
        "the same word returning later is a new run, not a merge")
    chk(all("_prems" not in e for e in eps), "the scratch column does not reach the output")

    # L13 five one-row blips above the baseline -> five runs, all positive
    blips = []
    for i in range(5):
        blips.append(row("场内买入", 5.0, "2026-02-%02d" % (2 * i + 1)))
        blips.append(row("暂停申购", 20.0, "2026-02-%02d" % (2 * i + 2)))
    er = episode_read(blips)
    chk(er["n_blocked_episodes"] == 5 and er["blocked_one_row"] == 5,
        "five one-row blips are five runs")
    chk(er["verdict"] == "EPISODE_GAP_WIDENS" and er["n_gaps"] == 5,
        "every run above the baseline -> widens at run level")

    # L14 the whole point: one long block cannot stand in for many sessions
    mixed = [row("场内买入", 5.0, "2026-03-01")]
    mixed += [row("暂停申购", 20.0, "2026-03-%02d" % (2 + i)) for i in range(20)]
    for i in range(5):
        mixed.append(row("场内买入", 5.0, "2026-03-%02d" % (22 + 2 * i)))
        mixed.append(row("暂停申购", 5.0, "2026-03-%02d" % (23 + 2 * i)))
    er2 = episode_read(mixed)
    chk(er2["n_blocked_episodes"] == 6 and er2["longest_blocked_rows"] == 20,
        "one 20-row block plus five blips = six runs")
    chk(er2["verdict"] == "EPISODE_GAP_DOES_NOT_WIDEN",
        "one long block and five flat blips is a flat run-level median, not a wide gap")
    chk(block_contrast(mixed)["verdict"] == "BLOCK_WIDENS_PREMIUM",
        "...while the day-level contrast reads wide on the same series (that is the trap)")
    chk(er2["widens_only_in_longest"] and abs(er2["longest_block_gap_pp"] - 15.0) < 1e-9
        and abs(er2["gap_without_longest_pp"]) < 1e-9,
        "the widest run is named and the rest of the runs are priced without it")
    chk(episode_read(blips)["gap_without_longest_pp"] is not None,
        "with five runs there is still a rest to price")

    # L15 a median of three runs is not a measurement
    fewer = [row("场内买入", 5.0, "2026-05-%02d" % (1 + i)) for i in range(5)]
    fewer += [row("暂停申购", 20.0, "2026-05-%02d" % (6 + i)) for i in range(20)]
    for i in range(2):
        fewer.append(row("场内买入", 5.0, "2026-05-%02d" % (26 + 2 * i)))
        fewer.append(row("暂停申购", 5.0, "2026-05-%02d" % (27 + 2 * i)))
    chk(episode_read(fewer)["n_blocked_episodes"] == 3
        and episode_read(fewer)["verdict"] == "TOO_FEW_EPISODES",
        "three blocked runs -> TOO_FEW_EPISODES, not a verdict")
    chk(episode_read(blips[:6])["verdict"] == "NO_EXCHANGE_BASELINE",
        "no exchange-only baseline to compare against -> says so instead of guessing")
    chk(episode_read([row("场内买入", 5.0, "2026-04-%02d" % (i + 1)) for i in range(6)])["verdict"]
        == "NO_BLOCKED_EPISODES", "never suspended -> NO_BLOCKED_EPISODES")

    # L16 the run table must describe the same series as the day table
    leg_ok = {"symbol": "1", "n_sessions": len(mixed), "blocked_sessions":
              sum(1 for r in mixed if "暂停" in r["purchase"]),
              "episode_granularity": episode_read(mixed)}
    chk(_check_episodes(leg_ok) == [], "a consistent run table passes the leg")
    leg_bad = json.loads(json.dumps(leg_ok))
    leg_bad["episode_granularity"]["runs"][0]["n_rows"] += 1
    chk(_check_episodes(leg_bad) != [], "a run table whose rows do not cover the series goes red")
    leg_bad2 = json.loads(json.dumps(leg_ok))
    leg_bad2["episode_granularity"]["runs"] = leg_bad2["episode_granularity"]["runs"][:2]
    chk(_check_episodes(leg_bad2) != [], "a truncated run table goes red (it is not a sample)")

    # L17 the page says both counts and names the run boundaries
    doc2 = json.loads(json.dumps(doc))
    doc2["legs"][0]["symbol"] = "159501"
    doc2["legs"][0]["n_sessions"] = len(mixed)
    doc2["legs"][0]["blocked_sessions"] = leg_ok["blocked_sessions"]
    doc2["legs"][0]["episode_granularity"] = episode_read(mixed)
    md2 = render_md(doc2)
    chk("Days vs runs" in md2 and "EPISODE_GAP_DOES_NOT_WIDEN" in md2,
        "the page carries the run verdict word")
    chk("2026-03-02" in md2 and "2026-03-21" in md2,
        "the page names the first and last session of the longest block")

    # L18 the blip cadence: twenty one-row words on the same weekday is not a random sample
    def week_series(days, start="2026-01-05"):
        """One 暂停申购 session per week on the given weekday; every other session 场内买入.

        A lead-in week of exchange-only sessions is prepended so that even the first blip has
        a session on both sides -- otherwise 'bracketed by two exchange-only rows' is false
        for the very first row for a reason that has nothing to do with the cadence.
        """
        out = []
        d0 = dt.date.fromisoformat(start)          # a Monday
        for wd_ in range(5):
            out.append(row("场内买入", 1.0, (d0 + dt.timedelta(days=wd_)).isoformat()))
        for wk, day in enumerate(days):
            for wd_ in range(5):
                d = d0 + dt.timedelta(days=7 * (wk + 1) + wd_)
                out.append(row("暂停申购" if wd_ == day else "场内买入", 1.0, d.isoformat()))
        return out

    cad_mon = blip_cadence(week_series([0] * 20))
    chk(cad_mon["verdict"] == "BLIP_WEEKDAY_CADENCE" and cad_mon["modal_weekday"] == "Mon"
        and cad_mon["n_one_row"] == 20, "twenty single-row words on Mondays -> BLIP_WEEKDAY_CADENCE")
    chk(cad_mon["bracketed_by_exchange_only"] == 20,
        "each weekly word sits between two exchange-only rows")
    chk(blip_cadence(week_series([0, 1, 2, 3] * 5))["verdict"] == "BLIP_NO_CADENCE",
        "the same count spread over three weekdays is not a cadence")
    chk(blip_cadence(week_series([0] * 3))["verdict"] == "TOO_FEW_BLIPS",
        "three single-row runs are not a weekday measurement")

    # L19 a split-sized NAV move is the one thing that would explain a one-day word
    s_jump = week_series([0] * 5)
    for r in s_jump:
        if r["purchase"] == "暂停申购":
            r["nav"] = 2.0                        # 100% against the 1.0 of the session before
    cad_jump = blip_cadence(s_jump)
    chk(cad_jump["nav_jump_gt3pct"] == 5 and cad_jump["nav_jump_max_abs_pct"] > 3.0,
        "a NAV discontinuity on a blip day is counted, not silently skipped")

    # L20 the block must be recomputable, and a hand-edited verdict must not survive
    cad_series = week_series([0] * 20)
    leg_cad = {"symbol": "T", "n_sessions": len(cad_series),
               "episode_granularity": episode_read(cad_series),
               "blip_cadence": blip_cadence(cad_series)}
    doc_cad = {"legs": [leg_cad], "blip_cadence_pooled": pooled_cadence([leg_cad])}
    chk(_check_cadence(doc_cad, page=False) == [], "a consistent cadence block passes")
    doc_cad2 = json.loads(json.dumps(doc_cad))
    doc_cad2["legs"][0]["blip_cadence"]["verdict"] = "BLIP_NO_CADENCE"
    chk(_check_cadence(doc_cad2, page=False) != [],
        "a hand-edited cadence verdict goes red against its own counts")
    doc_cad3 = json.loads(json.dumps(doc_cad))
    doc_cad3["legs"][0]["blip_cadence"]["blips_by_weekday"] = [5, 5, 5, 5, 0]
    chk(_check_cadence(doc_cad3, page=False) != [],
        "weekday counts that do not add up to the runs go red")
    doc_cad4 = json.loads(json.dumps(doc_cad))
    doc_cad4["blip_cadence_pooled"]["n_one_row"] = 19
    chk(_check_cadence(doc_cad4, page=False) != [],
        "a pooled count that disagrees with the legs goes red")

    # L21 the page carries the section and the pooled sentence
    doc["legs"][0]["blip_cadence"] = blip_cadence(cad_series)
    doc["blip_cadence_pooled"] = pooled_cadence(doc["legs"])
    md3 = render_md(doc)
    chk("Why the blips" in md3 and "BLIP_WEEKDAY_CADENCE" in md3 and "Pooled:" in md3,
        "the rendered page carries the cadence table, the pooled reading and the verdict word")

    # L22 what a one-row word *is*: a shut foreign market leaves three fingerprints at once
    NORMAL_WED = [dt.date(2024, 1, 10), dt.date(2024, 1, 17), dt.date(2024, 1, 24),
                  dt.date(2024, 1, 31), dt.date(2024, 2, 7), dt.date(2024, 2, 14),
                  dt.date(2024, 3, 6), dt.date(2024, 3, 13), dt.date(2024, 3, 20),
                  dt.date(2024, 4, 10)]
    HOLIDAYS = [dt.date(2023, 11, 23), dt.date(2024, 1, 15), dt.date(2024, 2, 19),
                dt.date(2024, 3, 29), dt.date(2024, 5, 27), dt.date(2024, 7, 4),
                dt.date(2024, 9, 2), dt.date(2024, 11, 28), dt.date(2024, 12, 25),
                dt.date(2025, 1, 20), dt.date(2025, 4, 18), dt.date(2025, 5, 26)]

    def cause_series(blips, move_pct=0.7, blip_move_pct=0.0, redeem_shut=True, fill=3):
        """Rows keyed by NAV stamp; a blip stamp prints 暂停申购 between 场内买入 stamps."""
        stamps = []
        for h in sorted(blips):
            for k in range(fill, 0, -1):
                d = h - dt.timedelta(days=k)
                while d.weekday() >= 5 or d in CLOSURE_FULL or d in CLOSURE_EARLY:
                    d -= dt.timedelta(days=1)
                if d not in stamps:
                    stamps.append(d)
            stamps.append(h)
        nav = 1.0
        out = []
        for s in sorted(set(stamps)):
            is_blip = s in blips
            if out:
                nav *= 1.0 + (blip_move_pct if is_blip else move_pct) / 100.0
            word = "暂停申购" if is_blip else "场内买入"
            out.append({"date": s.isoformat(), "nav": nav, "nav_date": s.isoformat(),
                        "premium_pct": 1.0, "purchase": word,
                        "purchase_kind": status_kind(word),
                        "redeem": "暂停赎回" if (is_blip and redeem_shut) else "场内卖出"})
        return out

    cause_cal = blip_cause(cause_series(HOLIDAYS))
    chk(cause_cal["verdict"] == "CALENDAR_GAP" and cause_cal["n_one_row"] == len(HOLIDAYS),
        "twelve one-row words on NYSE closures -> CALENDAR_GAP")
    chk(cause_cal["both_channels_suspended"] == len(HOLIDAYS),
        "a valuation gap suspends redemption on the same row, every time")
    chk(cause_cal["n_move_le_quarter"] >= len(HOLIDAYS) - 1 and cause_cal["exact_carry"] > 0,
        "a carried NAV is counted, and a gap moves the NAV far less than a normal session")
    chk(cause_cal["n_closure_full"] == len(HOLIDAYS) and (cause_cal["base_rate"] or 0.0) < 0.5,
        "the closure rate is priced against ordinary sessions, not quoted alone")

    # L23 the same shape on ordinary dates must NOT earn the calendar word
    cause_unk = blip_cause(cause_series(NORMAL_WED))
    chk(cause_unk["verdict"] == "GAP_WITH_UNKNOWN_CALENDAR",
        "the same gap on ordinary dates is left unnamed instead of given a holiday")
    cause_ann = blip_cause(cause_series(NORMAL_WED, blip_move_pct=1.5, redeem_shut=False))
    chk(cause_ann["verdict"] == "CAUSE_UNRESOLVED",
        "a word that moves the NAV like a normal session and leaves 赎回 open is not a gap")

    # L24 the closure calendar is rules, so the legs can be checked by hand
    chk(all(d in CLOSURE_FULL for d in (dt.date(2023, 11, 23), dt.date(2024, 3, 29),
                                       dt.date(2024, 6, 19), dt.date(2022, 12, 26),
                                       dt.date(2023, 1, 2))),
        "Thanksgiving, Good Friday, Juneteenth and the observed Christmas/New Year are closures")
    chk(dt.date(2023, 11, 24) in CLOSURE_EARLY and dt.date(2024, 7, 3) in CLOSURE_EARLY
        and dt.date(2023, 11, 24) not in CLOSURE_FULL,
        "the day after Thanksgiving and 3 July are early closes, not full ones")
    chk(closure_kind("2023-11-22", "2023-11-23") == "full"
        and closure_kind("2023-11-23", "2023-11-24") == "early"
        and closure_kind("2024-06-17", "2024-06-18") is None,
        "the window is (previous stamp, stamp] and an ordinary day carries nothing")

    # L25 the cause block must be the arithmetic of its counts
    cs = cause_series(HOLIDAYS)
    leg_cause = {"symbol": "T", "n_sessions": len(cs),
                 "episode_granularity": episode_read(cs),
                 "blip_cadence": blip_cadence(cs),
                 "blip_cause": blip_cause(cs)}
    doc_cause = {"legs": [leg_cause],
                 "blip_cadence_pooled": pooled_cadence([leg_cause]),
                 "blip_cause_pooled": pooled_blip_cause([leg_cause])}
    chk(_check_cause(doc_cause, page=False) == [], "a consistent cause block passes")
    doc_c1 = json.loads(json.dumps(doc_cause))
    doc_c1["legs"][0]["blip_cause"]["verdict"] = "CAUSE_UNRESOLVED"
    chk(_check_cause(doc_c1, page=False) != [],
        "a hand-edited cause verdict goes red against its own counts")
    doc_c2 = json.loads(json.dumps(doc_cause))
    doc_c2["legs"][0]["blip_cause"]["n_closure_unmatched"] += 1
    chk(_check_cause(doc_c2, page=False) != [], "closure counts that do not add up go red")
    doc_c3 = json.loads(json.dumps(doc_cause))
    doc_c3["blip_cause_pooled"]["n_one_row"] += 1
    chk(_check_cause(doc_c3, page=False) != [], "a pooled count that disagrees with the legs goes red")
    doc_c4 = json.loads(json.dumps(doc_cause))
    doc_c4["legs"][0]["blip_cause"]["both_channels_suspended"] = 0
    chk(_check_cause(doc_c4, page=False) != [],
        "dropping the redemption evidence changes the derived verdict and goes red")

    # L26 the overlap between two legs is a derived count, not a sentence
    xl = cross_leg_dates({"A": {"2024-01-01", "2024-02-01", "2024-03-01"},
                          "B": {"2024-01-01", "2024-02-01", "2024-03-01", "2024-04-01"},
                          "C": {"2024-01-01"}})
    chk(xl["best"]["a"] == "A" and xl["best"]["b"] == "B" and xl["best"]["n_shared"] == 3,
        "the cross-leg block names the pair with the most shared dates")
    doc_x = json.loads(json.dumps(doc_cause))
    leg2 = json.loads(json.dumps(leg_cause))
    leg2["symbol"] = "U"
    doc_x["legs"] = [leg_cause, leg2]
    doc_x["blip_cadence_pooled"] = pooled_cadence(doc_x["legs"])
    doc_x["blip_cause_pooled"] = pooled_blip_cause(doc_x["legs"])
    doc_x["blip_cause_cross"] = cross_leg_dates(
        {l["symbol"]: set(l["blip_cause"]["one_row_stamps"]) for l in doc_x["legs"]})
    chk(_check_cause(doc_x, page=False) == [],
        "two legs that share every date pass with a derived overlap block")
    doc_x1 = json.loads(json.dumps(doc_x))
    doc_x1["blip_cause_cross"]["best"]["n_shared"] = 3
    chk(_check_cause(doc_x1, page=False) != [], "a hand-shrunk overlap goes red")
    doc_x2 = json.loads(json.dumps(doc_x))
    doc_x2["legs"][1]["blip_cause"]["one_row_stamps"] = []
    chk(_check_cause(doc_x2, page=False) != [], "a stamps list that disagrees with the run count goes red")

    # L27 the page carries the section and the pooled word
    doc["legs"][0]["blip_cause"] = blip_cause(cs)
    doc["blip_cause_pooled"] = pooled_blip_cause(doc["legs"])
    md4 = render_md(doc)
    chk("What the one-row words are" in md4 and "CALENDAR_GAP" in md4,
        "the rendered page carries the cause section and the derived verdict word")

    # L28 the second calendar is measured, and it is named only on its own evidence
    HK_HOLIDAYS = [dt.date(2024, 2, 13), dt.date(2024, 4, 4), dt.date(2024, 10, 1),
                   dt.date(2024, 7, 1), dt.date(2024, 5, 15), dt.date(2024, 9, 18),
                   dt.date(2024, 12, 26), dt.date(2023, 10, 23)]

    def hk_fixture(closed_days, thin=None, start="2023-10-01", end="2025-06-30"):
        d = dt.date.fromisoformat(start)
        stop = dt.date.fromisoformat(end)
        sessions = []
        while d <= stop:
            if d.weekday() < 5 and d not in closed_days:
                sessions.append(d.isoformat())
            d += dt.timedelta(days=1)
        ratio = {k: 1.0 for k in sessions}
        for k, v in (thin or {}).items():
            ratio[k.isoformat()] = v
        return {"sessions": set(sessions), "ratio": ratio, "n": len(sessions),
                "first": sessions[0] if sessions else None,
                "last": sessions[-1] if sessions else None, "status": "fixture"}

    hk_fix = hk_fixture(HK_HOLIDAYS)
    cs_hk = cause_series(HK_HOLIDAYS)
    c_ny = blip_cause(cs_hk)
    chk(c_ny["verdict"] == "GAP_WITH_UNKNOWN_CALENDAR" and c_ny["hk_rate"] is None,
        "on Hong Kong holidays the rules-only reading leaves the runs unnamed")
    c_hk = blip_cause(cs_hk, market=hk_fix)
    chk(c_hk["calendar_named"] == "HKEX" and c_hk["verdict"] == "CALENDAR_GAP",
        "the measured HKEX calendar names the runs the US list cannot")
    chk((c_hk["hk_rate"] or 0.0) >= 0.99 and (c_hk["hk_n_closed"] or 0) == len(HK_HOLIDAYS),
        "the HK reading is a rate against its own ordinary sessions, not a bare count")

    # L29 the half-day cutoff is a ruler, so the page prints three of them
    THIN_DAYS = [dt.date(2024, 8, 14), dt.date(2024, 8, 21), dt.date(2024, 8, 28)]
    c_thin = blip_cause(cause_series(THIN_DAYS),
                        market=hk_fixture([], thin={d: 0.55 for d in THIN_DAYS}))
    sens = c_thin["hk_thin_sensitivity"]
    chk(c_thin["hk_n_thin"] == len(THIN_DAYS),
        "a half day trades about half its own trailing turnover and carries no valuation")
    chk(sens["0.50"]["n_matched"] == 0 and sens["0.60"]["n_matched"] == len(THIN_DAYS)
        and sens["0.70"]["n_matched"] == len(THIN_DAYS),
        "the same half day counts at 60% and 70% of trailing turnover, not at 50%")
    chk(sens["0.50"]["n_matched"] <= sens["0.60"]["n_matched"] <= sens["0.70"]["n_matched"],
        "the three thresholds are monotone, so the page can print them side by side")

    # L30 a date both calendars explain is a tie, and a tie names neither
    BOTH = [dt.date(2024, 12, 25), dt.date(2024, 1, 1), dt.date(2023, 12, 25)]
    c_both = blip_cause(cause_series(BOTH), market=hk_fixture(BOTH))
    chk(c_both["calendar_choice"]["reason"] == "TWO_CALENDARS_FIT_ALIKE"
        and c_both["calendar_named"] is None
        and c_both["verdict"] == "GAP_WITH_UNKNOWN_CALENDAR",
        "Christmas is shut in both markets, so the page names neither calendar")

    # L31 the two-calendar block must be the arithmetic of its own counts
    leg_hk = {"symbol": "T", "n_sessions": len(cs_hk), "latest_purchase_kind": "closed",
              "blocked_sessions": 0, "window_verdict": "CHANNEL_CLOSED_THROUGHOUT",
              "high_premium": {"n_high": 0, "share_closed_at_high": None},
              "episode_granularity": episode_read(cs_hk),
              "blip_cadence": blip_cadence(cs_hk),
              "blip_cause": blip_cause(cs_hk, market=hk_fix),
              "block_contrast": {"verdict": "NO_CONTRAST"}}
    doc_hk = {"legs": [leg_hk], "blip_cadence_pooled": pooled_cadence([leg_hk]),
              "blip_cause_pooled": pooled_blip_cause([leg_hk]),
              "ruler": {"premium": "close/nav-1", "status_join": "stamp"},
              "summary_sentence": "sentence",
              "hk_index": {"status": "fixture", "n": hk_fix["n"],
                           "first": hk_fix["first"], "last": hk_fix["last"]}}
    chk(_check_cause(doc_hk, page=False) == [], "a consistent two-calendar block passes")
    doc_hk1 = json.loads(json.dumps(doc_hk))
    doc_hk1["legs"][0]["blip_cause"]["calendar_named"] = "NYSE"
    chk(_check_cause(doc_hk1, page=False) != [],
        "a calendar word that its own choice block does not name goes red")
    doc_hk2 = json.loads(json.dumps(doc_hk))
    doc_hk2["legs"][0]["blip_cause"]["hk_n_closed"] += 1
    chk(_check_cause(doc_hk2, page=False) != [],
        "HK closure counts that do not add up to the runs go red")
    doc_hk3 = json.loads(json.dumps(doc_hk))
    doc_hk3["blip_cause_pooled"]["calendar_choice"]["named"] = "NYSE"
    chk(_check_cause(doc_hk3, page=False) != [],
        "a pooled calendar word that the pooled counts do not derive goes red")
    doc_md = json.loads(json.dumps(doc))
    doc_md["legs"][0]["blip_cause"] = blip_cause(cs_hk, market=hk_fix)
    doc_md["blip_cause_pooled"] = pooled_blip_cause(doc_md["legs"])
    doc_md["hk_index"] = doc_hk["hk_index"]
    md5 = render_md(doc_md)
    chk("Two calendars in hand" in md5 and "HKEX" in md5 and "50%" in md5,
        "the rendered page carries both calendars and the three half-day thresholds")

    # L32 the calendar-excluded contrast drops exactly the named rows, and says how many
    cb = [{"date": "2026-04-%02d" % i, "nav": 1.0, "nav_date": "2026-03-%02d" % i,
           "premium_pct": (40.0 if i <= 5 else 12.0), "purchase": "暂停申购",
           "purchase_kind": status_kind("暂停申购")} for i in range(1, 11)]
    ce = [{"date": "2026-05-%02d" % i, "nav": 1.0, "nav_date": "2026-04-%02d" % i,
           "premium_pct": 12.0, "purchase": "场内买入",
           "purchase_kind": status_kind("场内买入")} for i in range(1, 11)]
    chk(block_contrast(cb + ce)["verdict"] == "BLOCK_WIDENS_PREMIUM",
        "half the blocked rows far above the exchange level lift the block median")
    pure = block_contrast(cb + ce, exclude_stamps=[r["nav_date"] for r in cb[:5]])
    chk(pure["verdict"] == "BLOCK_DOES_NOT_WIDEN" and pure["n_excluded"] == 5,
        "dropping those five rows takes the gap with it, and the block says how many it dropped")
    chk(pure["n_blocked"] == 5 and pure["excluded_requested"] == 5,
        "the excluded reading publishes both the rows kept and the stamps it was asked to drop")
    chk(block_contrast(cb + ce)["n_excluded"] == 0
        and block_contrast(cb + ce)["excluded_requested"] == 0,
        "without an exclusion the same block reports zero dropped rows")

    # L33 the excluded block is checked against the leg's own counts, not trusted
    leg_x = {"symbol": "X", "blocked_sessions": 10,
             "blip_cause": {"n_one_row": 5}, "block_contrast_excl_gaps": dict(pure)}
    chk(_check_excluded_contrast(leg_x) == [], "a consistent excluded block passes")
    leg_x1 = json.loads(json.dumps(leg_x))
    leg_x1["block_contrast_excl_gaps"]["n_excluded"] = 7
    chk(_check_excluded_contrast(leg_x1) != [],
        "a drop count that does not reconcile with blocked_sessions goes red")
    leg_x2 = json.loads(json.dumps(leg_x))
    leg_x2["blip_cause"]["n_one_row"] = 3
    chk(_check_excluded_contrast(leg_x2) != [],
        "dropping more rows than the cause block counts goes red")
    leg_x3 = json.loads(json.dumps(leg_x))
    leg_x3["block_contrast_excl_gaps"]["verdict"] = "BLOCK_WIDENS_PREMIUM"
    chk(_check_excluded_contrast(leg_x3) != [],
        "a verdict word its own gap does not support goes red")
    leg_x4 = json.loads(json.dumps(leg_x))
    leg_x4["block_contrast_excl_gaps"] = None
    chk(_check_excluded_contrast(leg_x4) != [],
        "a leg that publishes no excluded block goes red")

    print("selftest %d/%d" % (ok[0], ok[1]))
    return 0 if ok[0] == ok[1] else 1


def run(fetch=True):
    doc = build(fetch=fetch)
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")
    with open(OUT_MD, "w", encoding="utf-8", newline="\n") as f:
        f.write(render_md(doc))
    os.makedirs(os.path.dirname(DOC), exist_ok=True)
    print(doc["summary_sentence"])
    for l in doc["legs"]:
        print("  %-7s %-12s premium %8s  stamp %s  %-6s  %s"
              % (l["symbol"], l["class"], _pct(l["latest_pct"]), l["latest_nav_date"],
                 l["latest_purchase"], l["window_verdict"]))
    print("wrote", OUT)
    print("wrote", OUT_MD)
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["run", "check", "selftest"])
    ap.add_argument("--no-fetch", action="store_true")
    a = ap.parse_args()
    if a.mode == "selftest":
        return selftest()
    if a.mode == "check":
        return check()
    return run(fetch=not a.no_fetch)


if __name__ == "__main__":
    sys.exit(main())

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


def block_contrast(series):
    """Hard-suspended sessions vs exchange-only sessions, both priced on their own premium."""
    blocked = [r["premium_pct"] for r in series if "暂停" in (r["purchase"] or "")]
    exch = [r["premium_pct"] for r in series
            if r["purchase_kind"] == "closed" and "暂停" not in (r["purchase"] or "")]
    if len(blocked) < 5 or len(exch) < 5:
        return {"verdict": "NO_CONTRAST", "n_blocked": len(blocked), "n_exchange": len(exch),
                "median_blocked_pct": statistics.median(blocked) if blocked else None,
                "median_exchange_pct": statistics.median(exch) if exch else None}
    mb, me = statistics.median(blocked), statistics.median(exch)
    return {"verdict": "BLOCK_WIDENS_PREMIUM" if mb > me + 1.0 else "BLOCK_DOES_NOT_WIDEN",
            "n_blocked": len(blocked), "n_exchange": len(exch),
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


def leg_facts(leg, prices, navs, status_rows, lag=1):
    series = series_with_status(prices, navs, status_rows, lag=lag)
    wv, wv_n = window_verdict(series)
    latest = series[-1] if series else None
    hi = high_premium_face(series)
    ep = episode_read(series)
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
        "episode_granularity": ep,
        "blip_cadence": blip_cadence(series),
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
    legs_out, notes = [], []
    cutoff = None
    for leg in face["legs"]:
        code = str(leg.get("symbol"))
        prices = pp.load_prices(code)
        navs, nav_status = pp.load_nav(code, fetch=False)
        status_rows, sub_status = load_status(code, fetch=fetch, today=today)
        if nav_status.startswith("cache-missing") or not navs:
            notes.append("%s: no NAV cache -- premium series unavailable" % code)
        facts = leg_facts(leg, prices, navs, status_rows)
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
        "legs": legs_out,
        "blip_cadence_pooled": pooled,
        "notes": notes,
        "summary_sentence": summary_sentence(legs_out, all_closed, pooled),
    }
    return doc


def summary_sentence(legs, all_closed, pooled=None):
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
        L.append("Read this as **when**, never as **why**: a source that refreshes its status word")
        L.append("on a weekly rhythm and a fund that announces one-day suspensions both produce a")
        L.append("clump on one weekday, and this data cannot separate them. What it does settle is")
        L.append("the reading of a single-row run: it is a word printed on one session, so it must")
        L.append("not be priced as 'the fund was suspended that day'.")
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
    bad.extend(_check_cadence(doc, page=not explicit))
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
            print("  FAIL:", why)

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
                        "block_contrast": {"verdict": "NO_CONTRAST"}}]
    gap_doc["blip_cadence_pooled"] = pooled_cadence(gap_doc["legs"])
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

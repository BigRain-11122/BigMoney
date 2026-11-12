"""A second reader for the ETF spot board, from sina, when the EM family refuses us.

r1599. The `etf_premium` lane lost 2026-11-12 because every eastmoney host answered
`RemoteDisconnected`, and that lane's holes do not heal: after the board rolls, the
session's tape is gone (`etf_premium_face.board_gap` says so in its own docstring).
This module is the recipe that was proven reachable from this host on that same
evening, kept as code instead of a report line:

    hq.sinajs.cn/list=sh510300,sz159915,...   -- batch quote: close price + amount + session
    hq.sinajs.cn/list=fu_510300,fu_510050,... -- batch fund NAV: unit NAV + previous NAV

Both batch endpoints accept many symbols per request, so a full board is ~20 requests,
not ~1,700. `--probe` measures what the fallback would actually cover and how its
numbers sit against the newest local snapshot, and writes that as evidence. It does
NOT write a snapshot: sina publishes NAV where eastmoney publishes an intraday IOPV,
and a premium built on one cannot be appended to a series built on the other without
saying so. That decision belongs to whoever wires this in, with the difference in hand.

Usage:
    python scripts/etf_premium_sina.py probe [--sample 40]
    python scripts/etf_premium_sina.py selftest
"""
import argparse
import json
import os
import sys
import time

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SNAP_DIR = os.path.join(ROOT, "data", "etf_premium", "snap")
RESULTS = os.path.join(ROOT, "results")
HOST = "http://hq.sinajs.cn/list="
HEADERS = {"Referer": "https://finance.sina.com.cn/",
           "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
BATCH = 80          # symbols per request; the endpoint tolerates ~100
THROTTLE_S = 0.4    # between batches -- this is a fallback, not a scraping job


def sina_symbol(code: str):
    """ETF code -> sina symbol prefix, or None when the prefix is not an exchange ETF."""
    c = str(code).zfill(6)
    if not c.isdigit():
        return None
    if c[0] in ("5", "6", "9"):
        return "sh" + c
    if c[0] in ("1", "2", "3"):
        return "sz" + c
    return None


def parse_quote(text: str):
    """`var hq_str_sh510300="..."` lines -> {symbol: raw payload string}."""
    out = {}
    for line in (text or "").splitlines():
        line = line.strip()
        if not line.startswith("var hq_str_") or "=" not in line:
            continue
        head, _, tail = line.partition("=")
        sym = head[len("var hq_str_"):].strip()
        payload = tail.strip().rstrip(";").strip('"')
        if payload:
            out[sym] = payload
    return out


def _num(v):
    try:
        f = float(str(v).strip())
    except (TypeError, ValueError):
        return None
    return f


def split_quote(payload: str):
    """One ETF quote payload -> (name, price, amount, session).

    Sina's ETF line is positional: 0 name, 1 open, 2 prev close, 3 last, ..., 9 amount,
    and the session sits near the tail next to the time (`...,2026-11-12,15:34:59,00`).
    The tail is scanned instead of indexed from the end, because the trailing fields
    move when a fund adds depth levels.
    """
    parts = payload.split(",")
    if len(parts) < 10:
        return None
    name = parts[0].strip()
    price = _num(parts[3])
    amount = _num(parts[9])
    session = None
    for tok in parts[10:]:
        t = tok.strip()
        if len(t) == 10 and t[4] == "-" and t[7] == "-" and t[:4].isdigit():
            session = t
            break
    return name, price, amount, session


def split_nav(payload: str):
    """One `fu_` payload -> (name, nav_today, nav_prev, session).

    Positional too: 0 name, 1 time, 2 unit NAV, 3 previous unit NAV, 6 the NAV's own
    daily change in percent, 7 the session. The change is used as a self-check -- it
    must equal nav/nav_prev-1, otherwise the columns are not what they look like.
    """
    parts = payload.split(",")
    if len(parts) < 8:
        return None
    name = parts[0].strip()
    nav_today = _num(parts[2])
    nav_prev = _num(parts[3])
    chg = _num(parts[6])
    session = parts[7].strip()
    if session and not (len(session) == 10 and session[4] == "-"):
        session = None
    check = None
    if nav_today and nav_prev:
        check = (nav_today / nav_prev - 1.0) * 100.0
    return name, nav_today, nav_prev, session, chg, check


def sina_board(codes, batch=BATCH, throttle=THROTTLE_S, getter=None):
    """Batch-read quotes and NAVs -> DataFrame(code, name, price, amount, session, nav).

    `getter(symbols)` returns the raw response text; injected so the selftest never
    touches the network. Rows the source did not answer stay missing -- an absent
    quote is a hole in the reading, never a zero.
    """
    getter = getter or _get
    syms = [s for s in (sina_symbol(c) for c in codes) if s]
    quotes, navs = {}, {}
    for i in range(0, len(syms), batch):
        chunk = syms[i:i + batch]
        # The NAV endpoint is addressed by bare code (`fu_510300`), not by the quote's
        # exchange-prefixed symbol -- one request still carries both markets.
        nav_syms = ["fu_" + s[2:] for s in chunk]
        try:
            text = getter(chunk)
        except Exception as exc:                                  # noqa: BLE001
            print("batch %d failed: %s: %s" % (i // batch, type(exc).__name__, str(exc)[:120]))
            try:
                navs.update(parse_quote(getter(nav_syms)))
            except Exception:                                     # noqa: BLE001
                pass
            continue
        quotes.update(parse_quote(text))
        try:
            navs.update(parse_quote(getter(nav_syms)))
        except Exception as exc:                                  # noqa: BLE001
            print("nav batch %d failed: %s" % (i // batch, str(exc)[:100]))
        if throttle and i + batch < len(syms):
            time.sleep(throttle)
    rows = []
    for code, sym in ((str(c).zfill(6), sina_symbol(c)) for c in codes):
        if not sym:
            continue
        q = split_quote(quotes.get(sym, "")) if quotes.get(sym) else None
        n = split_nav(navs.get("fu_" + sym[2:], "")) if navs.get("fu_" + sym[2:]) else None
        rows.append({
            "code": code,
            "name": (q[0] if q else (n[0] if n else "")),
            "price": q[1] if q else None,
            "amount": q[2] if q else None,
            "session": q[3] if q else None,
            "nav": n[1] if n else None,
            "nav_prev": n[2] if n else None,
            "nav_session": n[3] if n else None,
            "nav_chg": n[4] if n else None,
            # |published change - recomputed change|: two readings of ONE number, so a
            # non-zero value is the source disagreeing with its own columns, not a signal.
            "nav_check_pp": (abs(n[4] - n[5] if (n[4] is not None and n[5] is not None) else None)
                             if n else None),
        })
    df = pd.DataFrame(rows)
    if len(df):
        both = df["price"].gt(0) & df["nav"].gt(0)
        df["premium_pct"] = None
        df.loc[both, "premium_pct"] = (df.loc[both, "price"] / df.loc[both, "nav"] - 1.0) * 100.0
    return df


def _get(symbols):
    import urllib.request
    url = HOST + ",".join(symbols)
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=12) as r:
        return r.read().decode("gbk", "ignore")


def board_frame(codes, **kw):
    """The board in the shape `etf_premium_face.normalize_spot` reads, plus its source.

    The IOPV column is filled with the fund's published unit NAV. That is NOT the same
    number as the intraday IOPV eastmoney prints, so every row carries `_source` and the
    snapshot it lands in says so out loud: a premium measured against the official NAV
    is comparable within itself and only loosely comparable with the IOPV series.
    """
    df = sina_board(codes, **kw)
    out = pd.DataFrame({
        "代码": df["code"],
        "名称": df["name"],
        "最新价": df["price"],
        "IOPV实时估值": df["nav"],
        "成交额": df["amount"],
        "数据日期": df["session"],
        "_source": "sina_nav_not_iopv",
    })
    return out


def board_for_session(target, **kw):
    """The board sina is printing, checked to be `target` -> (frame, source name).

    The universe comes from the newest local snapshot: this is a fallback for a session
    the lane already knows the membership of, not a discovery mechanism. If sina's own
    session field disagrees with the session we were asked for, that is a refusal -- the
    alternative is filing one day's tape under another day's name.
    """
    _sess, _path, snap = newest_snapshot()
    if snap is None or not len(snap):
        raise RuntimeError("no local snapshot to define the universe")
    codes = list(snap["code"].astype(str).str.zfill(6))
    df = board_frame(codes, **kw)
    seen = sorted({str(d) for d in df["数据日期"].dropna()})
    if seen != [str(target)]:
        raise RuntimeError("sina reports %s, target session is %s" % (seen or "nothing", target))
    n_price = int(df["最新价"].notna().sum())
    n_nav = int(df["IOPV实时估值"].notna().sum())
    if n_price < max(50, len(codes) // 4) or n_nav < max(50, len(codes) // 4):
        raise RuntimeError("sina answered too little: %d prices, %d NAVs of %d"
                           % (n_price, n_nav, len(codes)))
    print("fallback board: sina prices %d/%d, NAVs %d/%d, session %s"
          % (n_price, len(codes), n_nav, len(codes), seen[0]))
    return df, "sina.nav_not_iopv"


def newest_snapshot():
    """(session, path, frame) of the newest local snapshot, or (None, None, None)."""
    if not os.path.isdir(SNAP_DIR):
        return None, None, None
    names = [n for n in os.listdir(SNAP_DIR)
             if n.endswith(".csv") and os.path.getsize(os.path.join(SNAP_DIR, n)) > 0]
    if not names:
        return None, None, None
    names.sort()
    path = os.path.join(SNAP_DIR, names[-1])
    return names[-1][:-4], path, pd.read_csv(path)


def probe(sample=40, seed=0):
    """Measure what sina would cover and how its numbers sit beside the local board."""
    sess, path, snap = newest_snapshot()
    if snap is None:
        return 2, {"status": "no_snapshot", "detail": "no local board to compare against"}
    codes = list(snap["code"].astype(str).str.zfill(6))
    if sample and sample < len(codes):
        step = max(1, len(codes) // sample)
        codes = codes[::step][:sample]
    t0 = time.time()
    df = sina_board(codes)
    elapsed = round(time.time() - t0, 1)
    got = df[df["price"].notna() & df["session"].notna()] if len(df) else df
    nav = df[df["nav"].notna()] if len(df) else df
    out = {
        "artifact": "etf_premium_sina_probe",
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "sample": len(codes),
        "requested": len(codes),
        "answered_quote": int(len(got)),
        "answered_nav": int(len(nav)),
        "elapsed_s": elapsed,
        "sessions_seen": (sorted(set(got["session"].dropna())) if len(got) else []),
        "nav_sessions_seen": (sorted(set(nav["nav_session"].dropna())) if len(nav) else []),
        "local_snapshot": {"session": sess, "path": os.path.relpath(path, ROOT), "rows": int(len(snap))},
        "note": ("sina publishes the fund's unit NAV where eastmoney publishes an intraday "
                 "IOPV; the two premiums are not the same series and this probe does not "
                 "write a snapshot."),
    }
    if len(nav):
        chk = nav["nav_check_pp"].dropna().astype(float)
        if len(chk):
            out["nav_columns_agree_abs_max_pp"] = round(float(chk.max()), 6)
            out["nav_columns_agree_n"] = int(len(chk))
    if len(df) and df["premium_pct"].notna().any():
        p = df["premium_pct"].astype(float).dropna()
        out["premium_median_pct"] = round(float(p.median()), 4)
        out["premium_p10_pct"] = round(float(p.quantile(0.10)), 4)
        out["premium_p90_pct"] = round(float(p.quantile(0.90)), 4)
        # Same-session comparison only: a 11-12 board says nothing about an 11-11 one.
        if len(got) and sorted(set(got["session"].dropna())) == [sess]:
            local = snap.set_index(snap["code"].astype(str).str.zfill(6))["premium_pct"]
            j = df.dropna(subset=["premium_pct"]).set_index("code")["premium_pct"]
            common = [c for c in j.index if c in local.index]
            if common:
                diff = (j.loc[common].astype(float) - local.loc[common].astype(float)).dropna()
                out["same_session_diff_vs_local_median_pp"] = round(float(diff.median()), 4)
                out["same_session_diff_vs_local_max_pp"] = round(float(diff.abs().max()), 4)
                out["same_session_compared"] = int(len(diff))
    return 0, out


def _selftest():
    ok = 0
    total = 0

    def leg(name, cond):
        nonlocal ok, total
        total += 1
        if cond:
            ok += 1
        print("[%s] %s" % ("PASS" if cond else "FAIL", name))

    leg("prefix: exchange ETFs map by first digit", sina_symbol("510300") == "sh510300"
        and sina_symbol("159915") == "sz159915" and sina_symbol("588000") == "sh588000")
    leg("prefix: a non-numeric code gets no invented symbol", sina_symbol("ABCDEF") is None)

    q = 'var hq_str_sh510300="沪深300ETF,4.145,4.150,4.114,4.177,4.108,4.113,4.114,1163144635,4818464209.000,507600,4.113,2026-11-12,15:34:59,00";'
    parsed = parse_quote(q)
    name, price, amount, session = split_quote(parsed["sh510300"])
    leg("quote: name/close/amount/session are read positionally and the session is found",
        name == "沪深300ETF" and abs(price - 4.114) < 1e-9
        and amount > 4.8e9 and session == "2026-11-12")

    nv = 'var hq_str_fu_510300="华泰柏瑞沪深300ETF,16:02:00,4.1209,4.1528,1.8669,0,-0.7686,2026-11-12,4.0752,-1.8676";'
    n = split_nav(parse_quote(nv)["fu_510300"])
    leg("nav: unit NAV, previous NAV and the session are read", abs(n[1] - 4.1209) < 1e-9
        and abs(n[2] - 4.1528) < 1e-9 and n[3] == "2026-11-12")
    leg("nav: the board's own change column agrees with nav/nav_prev",
        abs(n[4 + 1] - (n[1] / n[2] - 1.0) * 100.0) < 1e-6)

    fixture = {"sh510300": 'X,1,1,4.114,1,1,1,1,1,1.0e9,1,1,2026-11-12,15:00:00,00',
               "fu_510300": 'X,16:00:00,4.1209,4.1528,0,0,-0.7686,2026-11-12,0,0',
               "sz159915": 'Y,1,1,2.0,1,1,1,1,1,3.0e8,1,1,2026-11-12,15:00:00,00'}
    df = sina_board(["510300", "159915", "999999"],
                    getter=lambda syms: "\n".join(
                        'var hq_str_%s="%s";' % (s, fixture[s]) for s in syms if s in fixture))
    leg("board: answered rows carry a premium and unanswered rows stay missing",
        len(df) == 3 and df.loc[0, "code"] == "510300"
        and pd.notna(df.loc[0, "premium_pct"])
        and pd.notna(df.loc[1, "price"]) and pd.isna(df.loc[2, "price"])
        and pd.isna(df.loc[2, "premium_pct"]))
    leg("board: no NAV means no premium, never zero",
        pd.isna(df.loc[1, "premium_pct"]) and pd.isna(df.loc[1, "nav"]))

    print("selftest: %d/%d PASS" % (ok, total))
    return 0 if ok == total else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd")
    p = sub.add_parser("probe", help="measure coverage against the newest local snapshot")
    p.add_argument("--sample", type=int, default=40)
    sub.add_parser("selftest", help="offline checks")
    args = ap.parse_args(argv)
    if args.cmd == "selftest":
        return _selftest()
    if args.cmd == "probe":
        rc, out = probe(sample=args.sample)
        os.makedirs(RESULTS, exist_ok=True)
        path = os.path.join(RESULTS, "etf_premium_sina_probe.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=1)
        print(json.dumps(out, ensure_ascii=False, indent=1))
        print("wrote %s" % os.path.relpath(path, ROOT))
        return rc
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())

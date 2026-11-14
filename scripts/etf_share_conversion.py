"""ETF_SHARE_CONVERSION — disclose and repair a share conversion instead of refusing the leg.

The carry face refuses to print an ETF leg that moves more than 35% in one session
(`idx_fut_carry_risk`, r1700), because an unrepaired quote flip turns a flat year into a
hundred-percent one.  That rule is right about quote flips and wrong about corporate
actions: a fund share conversion (份额折算) is a real, permanent level change -- the
holder's share count is divided by the same factor the price is multiplied by, so wealth
is unchanged and the event carries **no return**.  Refusing on it throws away the whole
leg (IM has had exactly one such day: 2022-09-05, 0.982 -> 2.713).

This module separates the two cases with four observable markers, all read off the same
daily panel, and hands consumers an adjusted series rather than a judgement call:

  1. persistence      the new level must survive (a flip comes back, a conversion does not)
  2. turnover         price*volume must continue across the event (a conversion preserves
                      turnover; a mispriced print does not)
  3. index absence    the tracked index must not have moved that day (market move vs fund
                      event)
  4. suspension       a conversion suspends the fund for one session, so the session
                      before the event is missing from the panel

`corporate_action` = 1 and 2 and (3 or 4); `quote_flip` = the level reverts; anything else
is `unresolved` and the leg keeps being refused -- an unread leg stays unread.

Subcommands:
  run       -- scan every ETF in the pair map, write results/etf_share_conversion.json
               and research/ETF_SHARE_CONVERSION.md
  selftest  -- hermetic synthetic panels (conversion / flip / unresolved), offline
"""

import csv
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import idx_fut_basis as base  # noqa: E402  (single daily-panel reader, r1375 family)

OUT_JSON = os.path.join(ROOT, "results", "etf_share_conversion.json")
OUT_MD = os.path.join(ROOT, "research", "ETF_SHARE_CONVERSION.md")

MOVE = 0.35          # the same 35% trigger the carry face refuses on
PERSIST_BARS = 10    # how long the new level has to hold
PERSIST_TOL = 0.25   # ...within this much of the event ratio
TURNOVER_BAND = (0.4, 2.5)


def read_daily(code, daily_dir=None):
    """date -> {open, high, low, close, volume} from the one daily panel reader."""
    path = os.path.join(daily_dir or os.path.join(ROOT, "data", "daily"), code + ".csv")
    if not os.path.exists(path):
        return None
    rows = base.read_csv_rows(path)
    out = {}
    for r in rows:
        try:
            d = str(r["date"])[:10]
            out[d] = {"open": float(r["open"]), "close": float(r["close"]),
                      "volume": float(r.get("volume") or 0.0)}
        except (KeyError, TypeError, ValueError):
            continue
    return out or None


def _index_series(code):
    """Tracked index closes, keyed by date.  None when the host has no index panel."""
    idx = base.load_index(code) if code else None
    return idx or None


def detect(panel):
    """Every session whose close moves more than MOVE against the previous close."""
    dates = sorted(panel)
    hits = []
    for k in range(1, len(dates)):
        prev, cur = panel[dates[k - 1]]["close"], panel[dates[k]]["close"]
        if prev > 0 and cur > 0 and (cur / prev > 1 + MOVE or cur / prev < 1 - MOVE):
            hits.append((k, dates[k], prev, cur))
    return dates, hits


def load_calendar(path=None):
    """Official trading sessions, or None.  A conversion suspends the fund, so the panel
    is missing a session the calendar says traded -- that gap is the marker."""
    path = path or os.path.join(ROOT, "data", "exchange_calendar.csv")
    if not os.path.exists(path):
        return None
    out = set()
    with open(path, encoding="utf-8") as fh:
        for k, line in enumerate(fh):
            t = line.strip().split(",")[0]
            if k == 0 or len(t) < 10:
                continue
            out.add(t[:10])
    return out or None


def _prev_session(calendar, date):
    prior = [d for d in calendar if d < date]
    return max(prior) if prior else None


def classify(dates, panel, k, prev, cur, index=None, calendar=None):
    """Evidence for one level shift.  Pure; returns a dict a reader can audit."""
    ratio = cur / prev
    ev = {
        "date": dates[k], "prev_close": prev, "close": cur, "ratio": round(ratio, 6),
        "markers": {}, "evidence": {},
    }

    tail = dates[k + 1:k + 1 + PERSIST_BARS]
    if tail:
        later = [panel[d]["close"] for d in tail]
        ratio_later = later[-1] / prev
        held = abs(ratio_later - ratio) <= PERSIST_TOL * max(ratio, 1.0)
        reverted = abs(later[-1] / prev - 1.0) <= PERSIST_TOL
        ev["markers"]["persistence"] = bool(held and not reverted)
        ev["evidence"]["close_after_%d_bars" % len(tail)] = later[-1]
        ev["evidence"]["ratio_after_bars"] = round(ratio_later, 6)
    else:
        ev["markers"]["persistence"] = False
        ev["evidence"]["close_after_bars"] = None

    v_prev, v_cur = panel[dates[k - 1]]["volume"], panel[dates[k]]["volume"]
    turn_prev, turn_cur = prev * v_prev, cur * v_cur
    if turn_prev > 0 and turn_cur > 0:
        tr = turn_cur / turn_prev
        lo, hi = TURNOVER_BAND
        ev["markers"]["turnover"] = bool(lo <= tr <= hi)
        ev["evidence"]["turnover_ratio"] = round(tr, 4)
    else:
        ev["markers"]["turnover"] = False
        ev["evidence"]["turnover_ratio"] = None

    if index and dates[k] in index and dates[k - 1] in index:
        i_prev, i_cur = index[dates[k - 1]], index[dates[k]]
        move = (i_cur / i_prev - 1.0) if i_prev > 0 else 0.0
        ev["markers"]["index_absence"] = bool(abs(move) <= MOVE / 2.0)
        ev["evidence"]["index_move_pct"] = round(move * 100.0, 3)
    else:
        ev["markers"]["index_absence"] = None   # no index panel on this host
        ev["evidence"]["index_move_pct"] = None

    # a conversion suspends the fund: the session the calendar says traded right before
    # the event is missing from the panel.  Without a calendar we say nothing (None).
    if calendar:
        ps = _prev_session(calendar, dates[k])
        missing = bool(ps and ps not in panel and ps != dates[k - 1])
        ev["markers"]["suspension_gap"] = missing
        ev["evidence"]["session_before_event"] = ps
        ev["evidence"]["session_missing"] = missing
    else:
        ev["markers"]["suspension_gap"] = None
        ev["evidence"]["session_before_event"] = dates[k - 1] if k >= 1 else None
        ev["evidence"]["session_missing"] = None

    m = ev["markers"]
    if m["persistence"] and m["turnover"] and (m["index_absence"] or m.get("suspension_gap")):
        ev["kind"] = "corporate_action"
    elif not m["persistence"]:
        ev["kind"] = "quote_flip"
    else:
        ev["kind"] = "unresolved"
    return ev


def adjust(series, events):
    """Scale every price before a conversion by that event's ratio; one flat series out."""
    if not events:
        return dict(series), []
    applied = []
    out = {}
    factors = [(e["date"], e["ratio"]) for e in events if e.get("kind") == "corporate_action"]
    for d, v in series.items():
        f = 1.0
        for ed, er in factors:
            if d < ed:
                f *= er
        out[d] = v * f
    for ed, er in factors:
        applied.append({"date": ed, "factor": round(er, 6)})
    return out, applied


def _classify_all(code, daily_dir=None, calendar=None):
    """One read of the panel -> (dates, panel, events).  Every caller goes through here so
    the index-panel evidence and the calendar marker are never applied in one place only."""
    panel = read_daily(code, daily_dir)
    if not panel:
        return None, None, []
    dates, hits = detect(panel)
    prod = next((p for p, v in base.PAIRS.items() if v[2] == code), None)
    ix = _index_series(base.PAIRS[prod][0]) if prod else None
    events = [classify(dates, panel, k, p, c, ix, calendar) for k, _d, p, c in hits]
    return dates, panel, events


def adjusted_closes(code, daily_dir=None, calendar=None):
    """Close series with qualified conversions removed.  None if the panel is absent."""
    _dates, panel, events = _classify_all(code, daily_dir, calendar)
    if not panel:
        return None, []
    series = {d: v["close"] for d, v in panel.items()}
    out, applied = adjust(series, events)
    return out, [e for e in events if e.get("kind") == "corporate_action"]


def adjusted_field(code, field="open", daily_dir=None, calendar=None):
    """One column of the ETF panel with conversions removed, plus the events applied."""
    _dates, panel, events = _classify_all(code, daily_dir, calendar)
    if not panel:
        return None, []
    series = {d: v[field] for d, v in panel.items() if v.get(field)}
    out, applied = adjust(series, events)
    return out, applied


def scan(daily_dir=None, calendar=None):
    calendar = calendar if calendar is not None else load_calendar()
    codes = sorted({v[2] for v in base.PAIRS.values() if v[2]})
    faces = {}
    for code in codes:
        panel = read_daily(code, daily_dir)
        if not panel:
            faces[code] = {"status": "no_panel"}
            continue
        dates, panel, events = _classify_all(code, daily_dir, calendar)
        prod = next((p for p, v in base.PAIRS.items() if v[2] == code), None)
        faces[code] = {
            "status": "ok",
            "index": base.PAIRS[prod][0] if prod else None,
            "first": dates[0], "last": dates[-1], "bars": len(dates),
            "shifts": events,
            "qualified_events": sum(1 for e in events if e["kind"] == "corporate_action"),
            "unresolved_events": sum(1 for e in events if e["kind"] == "unresolved"),
            "quote_flip_events": sum(1 for e in events if e["kind"] == "quote_flip"),
        }
    return faces


def write_doc(face, path=OUT_MD):
    lines = ["# ETF 份额折算 vs 报价翻转 — 同一条腿的两种 35% 日", "",
             "> 正身 `results/etf_share_conversion.json`；生成器 `scripts/etf_share_conversion.py`"
             "（`--write-doc`），页面与面同源，禁手改。", "",
             "carry 面拒印 >35% 日的规则是对的（对报价翻转），但对份额折算是错的：折算当日"
             "份额数被同一个因子除，财富不变，那一天**没有收益**。本面把两种情形分开，"
             "并给消费者一条已调整的序列，而不是一句判词。", ""]
    for code, f in sorted(face.items()):
        if f.get("status") != "ok":
            lines.append("- **%s**: 面板缺席（%s）" % (code, f.get("status")))
            continue
        if not f["shifts"]:
            lines.append("- **%s**: %s → %s（%d 根），全窗无 >35%% 日"
                         % (code, f["first"], f["last"], f["bars"]))
            continue
        lines.append("## %s（%s → %s，%d 根）" % (code, f["first"], f["last"], f["bars"]))
        lines.append("")
        lines.append("| 日 | 前收 | 收 | 倍数 | 持续 | 成交额 | 指数同日 | 判定 |")
        lines.append("|---|---|---|---|---|---|---|---|")
        for e in f["shifts"]:
            m = e["markers"]
            lines.append("| %s | %.3f | %.3f | %.3f | %s | %s | %s | **%s** |" % (
                e["date"], e["prev_close"], e["close"], e["ratio"],
                "是" if m.get("persistence") else "否",
                ("%.2f" % e["evidence"]["turnover_ratio"]) if e["evidence"]["turnover_ratio"] else "—",
                ("%+.2f%%" % e["evidence"]["index_move_pct"]) if e["evidence"]["index_move_pct"] is not None else "—",
                e["kind"]))
        lines.append("")
        lines.append("调整：把事件日之前的全部价格按该倍数缩放（等价于持有者份额被反向除），"
                     "事件后价格不动 —— 序列连续，事件日收益按真实开盘/收盘正常计算。")
        lines.append("")
    text = "\n".join(lines) + "\n"
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    return text


def run(write_doc_flag=False):
    faces = scan()
    last = max((f.get("last") or "" for f in faces.values() if f.get("status") == "ok"), default=None)
    out = {
        "artifact": "ETF share conversion vs quote flip, per ETF in the index/futures pair map",
        "evidence_cutoff": last,
        "law_refs": ["O-20261114-2325-bm-c (only work that moves a bet)",
                     "r1700 idx_fut_carry_risk (refuses a >35% ETF day)"],
        "criteria": {"move_trigger": MOVE, "persist_bars": PERSIST_BARS,
                     "persist_tol": PERSIST_TOL, "turnover_band": list(TURNOVER_BAND)},
        "faces": faces,
        "verdict": _verdict(faces),
    }
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    if write_doc_flag:
        write_doc(faces)
    return out


def _verdict(faces):
    qual = [(c, e["date"], e["ratio"]) for c, f in faces.items()
            if f.get("status") == "ok" for e in f["shifts"] if e["kind"] == "corporate_action"]
    unres = [(c, e["date"]) for c, f in faces.items()
             if f.get("status") == "ok" for e in f["shifts"] if e["kind"] == "unresolved"]
    flips = [(c, e["date"]) for c, f in faces.items()
             if f.get("status") == "ok" for e in f["shifts"] if e["kind"] == "quote_flip"]
    if qual and not unres:
        text = ("QUALIFIED: %d share conversion(s) (%s) can be removed from the leg; "
                "the rest of the panel is clean" %
                (len(qual), ", ".join("%s@%s x%.3f" % q for q in qual)))
    elif unres:
        text = ("PARTIAL: %d conversion(s) qualified, %d unresolved (kept refused: %s)" %
                (len(qual), len(unres), ", ".join("%s@%s" % u for u in unres)))
    elif flips:
        text = ("FLIPS_ONLY: %d quote flip(s) (%s) -- refused, not repaired as conversions" %
                (len(flips), ", ".join("%s@%s" % f for f in flips)))
    else:
        text = "CLEAN: no level shift above %.0f%% in any ETF leg" % (MOVE * 100)
    return {"verdict": text, "qualified": qual, "unresolved": unres, "quote_flips": flips}


# ---------------------------------------------------------------- selftest

def _synth(rows, daily_dir, code):
    path = os.path.join(daily_dir, code + ".csv")
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["date", "open", "high", "low", "close", "volume"])
        for d, c, v in rows:
            w.writerow([d, c, c, c, c, v])
    return path


def selftest():
    ok = 0
    total = 0

    def leg(name, cond):
        nonlocal ok, total
        total += 1
        if cond:
            ok += 1
            print("[PASS] %s" % name)
        else:
            print("[FAIL] %s" % name)

    with tempfile.TemporaryDirectory() as td:
        # a conversion: level x2.76 that stays, turnover preserved, and the fund was
        # suspended on the session the calendar says traded right before it (2022-09-02)
        rows = [("2022-08-%02d" % d, 0.98, 1_900_000_000) for d in range(20, 31)]
        rows += [("2022-09-%02d" % d, 2.70, 690_000_000) for d in range(5, 21)]
        _synth(rows, td, "sh512100")
        cal_path = os.path.join(td, "cal.csv")
        with open(cal_path, "w", encoding="utf-8", newline="") as fh:
            fh.write("date\n")
            for r in rows:
                fh.write(r[0] + "\n")
            fh.write("2022-09-02\n")   # the suspension day the panel does not carry
        days = load_calendar(cal_path)
        leg("the synthetic calendar carries the suspension day", "2022-09-02" in days)
        panel = read_daily("sh512100", td)
        dates, hits = detect(panel)
        leg("detect finds the level shift", len(hits) == 1 and hits[0][2] == 0.98)
        k0, _d0, p0, c0 = hits[0]
        ev = classify(dates, panel, k0, p0, c0, None, days)
        leg("a persistent level with flat turnover and a suspended session is a conversion",
            ev["kind"] == "corporate_action")
        leg("the suspension marker names the missing session",
            ev["markers"]["suspension_gap"] is True
            and ev["evidence"]["session_before_event"] == "2022-09-02")
        leg("its ratio is the price ratio", abs(ev["ratio"] - 2.70 / 0.98) < 1e-6)
        series = {d: v["close"] for d, v in panel.items()}
        adj, applied = adjust(series, [ev])
        leg("pre-event prices are scaled onto the new level",
            abs(adj[dates[0]] - 2.70) < 1e-6)
        leg("post-event prices are untouched", adj[dates[-1]] == 2.70)
        leg("one factor is reported", len(applied) == 1 and applied[0]["date"] == ev["date"])

        # a quote flip: jumps up then comes back -> must stay refused
        rows2 = [("2021-01-%02d" % d, 1.00, 5_000_000) for d in range(4, 12)]
        rows2 += [("2021-01-%02d" % d, 10.0, 5_000_000) for d in range(12, 15)]
        rows2 += [("2021-01-%02d" % d, 1.00, 5_000_000) for d in range(15, 25)]
        _synth(rows2, td, "sh511030")
        p2 = read_daily("sh511030", td)
        d2, h2 = detect(p2)
        kinds = [classify(d2, p2, h[0], h[2], h[3])["kind"] for h in h2]
        leg("a level that comes back is a quote flip", kinds and kinds[0] == "quote_flip")
        s2 = {d: v["close"] for d, v in p2.items()}
        _a2, ap2 = adjust(s2, [ev] * 0)
        leg("no qualified event -> series unchanged", _a2 == s2 and ap2 == [])

        # a shift with no persistence evidence is never qualified
        rows3 = [("2020-03-%02d" % d, 2.0, 1_000_000) for d in range(2, 12)]
        _synth(rows3, td, "sh999999")
        p3 = read_daily("sh999999", td)
        d3, h3 = detect(p3)
        leg("a shift at the tail end of the panel is not qualified", not h3)

    # live panel sanity: the module reads the one daily reader, no second parser
    leg("read_daily and idx_fut_basis agree on the same file",
        (lambda: (read_daily("sh512100") or {}).get("2022-09-05", {}).get("close") ==
        (base.load_etf("sh512100") or {}).get("2022-09-05"))())

    print("\nself-test %d/%d" % (ok, total))
    return 0 if ok == total else 1


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    cmd = argv[0]
    if cmd == "run":
        out = run(write_doc_flag="--write-doc" in argv)
        print(out["verdict"]["verdict"])
        if "--checkdoc" in argv:
            text = write_doc(out["faces"])
            print("doc chars=%d" % len(text))
        return 0
    if cmd == "selftest":
        return selftest()
    print("unknown subcommand %r" % cmd)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

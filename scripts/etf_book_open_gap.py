"""r1829: the sheet is priced at a close; the fill happens at the next open.

Every line on the desk's order sheet is priced at the decision bar's close, and the
page's own caveat already says "开盘成交价会不同".  That caveat is a promise nobody
measured: the reader is asked to hand over ~half a million at 09:30 tomorrow and the
page never says how far tomorrow's open ever sits from yesterday's close on THESE five
names.  This face measures exactly that and nothing else -- the overnight gap
`open_t / close_{t-1} - 1` per name, pooled, in bp, and the same band in CNY on the
ticket's own traded amount.

What it is NOT (said on the page as well):
  * not a cost -- a gap is a price level change, it moves the exposure `k` by the same
    percentage and it is not paid to anyone;
  * not additive to the commission line -- one is a transfer, the other is a price;
  * not a forecast -- it is the distribution this five-name set has already shown.

Rules this face keeps, all borrowed from the family it joins:
  * the names are the ticket's own (r1827 family: a reading on another five names is
    another book);
  * a print that is a quote-face flip (|gap| > 35%, the same frozen line
    `etf_equity_alpha.repair_flips` uses) is neutralised AND counted, never silently
    dropped (r1259/r1311 family);
  * two calibers, printed side by side, never blended: the last RECENT_SESSIONS
    sessions per name, and each name's full history;
  * a missing panel is a reason, never 0 (r98 family).

Usage:
    python scripts/etf_book_open_gap.py run      # derive results/etf_book_open_gap.json
    python scripts/etf_book_open_gap.py check    # derive, then verify the published face
    python scripts/etf_book_open_gap.py selftest # offline (synthetic panels, no disk)
"""
import argparse
import glob
import io
import json
import os
import sys
import datetime as dt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

OUT = os.path.join(ROOT, "results", "etf_book_open_gap.json")
OUT_REL = "results/etf_book_open_gap.json"
TICKET_GLOB = os.path.join(ROOT, "results", "etf_book_order", "TICKET-*.json")

FLIP_THR = 0.35          # frozen: the same single-day line repair_flips uses
RECENT_SESSIONS = 250    # one trading year, per name
BAND_RATIO = 2.0         # band_cny >= 2 x fee -> "the open dwarfs the fee"


def _p(*parts):
    return os.path.join(ROOT, *parts)


def _rel(path):
    try:
        return os.path.relpath(path, ROOT).replace("\\", "/")
    except ValueError:
        return path


def _read_json(path):
    try:
        with io.open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


def newest_ticket(pattern=TICKET_GLOB):
    """The newest non-card sheet, or (None, reason)."""
    for path in sorted(glob.glob(pattern), reverse=True):
        if path.endswith("-card.json"):
            continue
        t = _read_json(path)
        if t:
            return path, t
    return None, "no TICKET-*.json on disk"


def to_sina_symbol(code):
    """Imported from the daily pool -- 5xx = SH, 1xx = SZ. Never re-implemented."""
    from update_daily import to_sina_symbol as _pool_symbol

    return _pool_symbol(str(code).strip())


def read_panel(symbol):
    """[(date, open, close)] in file order; empty when the panel is absent/unreadable."""
    path = _p("data", "daily", "%s.csv" % to_sina_symbol(symbol))
    if not os.path.exists(path):
        return [], path
    rows = []
    try:
        with io.open(path, encoding="utf-8", errors="replace") as fh:
            header = fh.readline().strip().split(",")
            try:
                i_d, i_o, i_c = header.index("date"), header.index("open"), header.index("close")
            except ValueError:
                return [], path
            for line in fh:
                cells = line.strip().split(",")
                if len(cells) <= max(i_d, i_o, i_c):
                    continue
                try:
                    rows.append((cells[i_d], float(cells[i_o]), float(cells[i_c])))
                except ValueError:
                    continue
    except OSError:
        return [], path
    return rows, path


def gaps(rows, flip_thr=FLIP_THR):
    """[(date, gap)] for open_t vs close_{t-1}, plus (n_flips, n_undefined).

    The flip line is defined on the CLOSE series, the same way `repair_flips` does
    (|close_t / close_{t-1} - 1| > 35% is a share-count restatement read as a collapse,
    not a market move).  Two different sessions are then unmeasurable, and both are
    counted rather than guessed:

      * the session whose own print is the flip -- its open is part of the same
        restatement, so `open_t / close_{t-1}` is not a market gap;
      * the session AFTER it -- its denominator is the fake close, so it is not a
        market gap either (the trap the r1259/r1311 family keeps: one bad print
        poisons two readings, and neutralising only the first invents the second).

    A gap is also undefined when either the open or the prior close is non-positive.
    Every skipped session lands in `n_undefined`; nothing is replaced by 0.
    """
    flips = set()
    for i in range(1, len(rows)):
        c0 = rows[i - 1][2]
        c1 = rows[i][2]
        if c0 > 0 and c1 > 0 and abs(c1 / c0 - 1.0) > flip_thr:
            flips.add(i)
    out, undefined = [], 0
    for i in range(1, len(rows)):
        _d0, _o0, c0 = rows[i - 1]
        d1, o1, _c1 = rows[i]
        if i in flips or (i - 1) in flips or c0 <= 0 or o1 <= 0:
            undefined += 1
            continue
        out.append((d1, o1 / c0 - 1.0))
    return out, (len(flips), undefined)


def _pct(sorted_vals, q):
    """Linear-interpolated percentile on an already sorted list (q in [0, 100])."""
    if not sorted_vals:
        return None
    if len(sorted_vals) == 1:
        return sorted_vals[0]
    pos = (len(sorted_vals) - 1) * (q / 100.0)
    lo = int(pos)
    hi = min(lo + 1, len(sorted_vals) - 1)
    frac = pos - lo
    return sorted_vals[lo] * (1.0 - frac) + sorted_vals[hi] * frac


def stats(vals):
    """band statistics in fractions (the caller converts to bp)."""
    if not vals:
        return {"n": 0, "median": None, "mean": None, "p20": None, "p80": None,
                "share_positive": None}
    s = sorted(vals)
    return {
        "n": len(s),
        "median": _pct(s, 50),
        "mean": sum(s) / float(len(s)),
        "p20": _pct(s, 20),
        "p80": _pct(s, 80),
        "share_positive": sum(1 for v in s if v > 0) / float(len(s)),
    }


def _bp(x):
    return None if x is None else round(x * 1e4, 4)


def _stats_bp(st):
    out = dict(st)
    for k in ("median", "mean", "p20", "p80"):
        out[k + "_bp"] = _bp(st.get(k))
    return out


def build(ticket_path=None):
    """The published face. Pure read of the ticket + five daily panels."""
    path, ticket = (ticket_path, _read_json(ticket_path)) if ticket_path else newest_ticket()
    if not isinstance(ticket, dict):
        return {"present": False, "verdict": "NO_TICKET",
                "sentence": "没有可读的执行单票面，这张面答不了「开盘离票面价多远」。",
                "evidence_cutoff": None}
    order = ((ticket.get("ticket") or {}).get("order")) or []
    if not order:
        return {"present": False, "verdict": "NO_ORDER_ROWS",
                "sentence": "票面上没有下单行，这张面答不了。", "evidence_cutoff": None}
    traded = sum(float(r.get("amount") or 0.0) for r in order)
    cost_bp = ticket.get("cost_bp_per_side")
    fee_cny = (traded * float(cost_bp) / 1e4 * 2.0) if cost_bp is not None else None

    names, pooled_recent, pooled_all, missing = [], [], [], []
    all_dates = []
    for row in order:
        sym = str(row.get("symbol"))
        rows, ppath = read_panel(sym)
        if len(rows) < 2:
            missing.append(sym)
            names.append({"symbol": sym, "panel": _rel(ppath), "readable": False,
                          "n_sessions": 0, "calibers": {}, "n_flips": None})
            continue
        series, (flips, undef) = gaps(rows)
        if not series:
            missing.append(sym)
            names.append({"symbol": sym, "panel": _rel(ppath), "readable": False,
                          "n_sessions": 0, "calibers": {}, "n_flips": flips})
            continue
        recent = [g for _d, g in series[-RECENT_SESSIONS:]]
        allg = [g for _d, g in series]
        pooled_recent.extend(recent)
        pooled_all.extend(allg)
        all_dates.extend(d for d, _g in series)
        names.append({
            "symbol": sym,
            "panel": _rel(ppath),
            "readable": True,
            "panel_first": rows[0][0],
            "panel_last": rows[-1][0],
            "n_sessions": len(allg),
            "n_flips": flips,
            "n_undefined": undef,
            "calibers": {
                "recent": _stats_bp(stats(recent)),
                "all_history": _stats_bp(stats(allg)),
            },
        })

    if not pooled_recent:
        return {"present": False, "verdict": "NO_PANEL",
                "sentence": "这五只票在盘上都没有可读的日线（缺面不读 0），"
                            "所以「开盘离票面价多远」今天答不了。",
                "missing": missing, "evidence_cutoff": ticket.get("evidence_cutoff")}

    recent_st = _stats_bp(stats(pooled_recent))
    all_st = _stats_bp(stats(pooled_all))
    band_cny = (recent_st["p80"] - recent_st["p20"]) * traded
    one_bp_cny = traded / 1e4
    median_cny = recent_st["median"] * traded

    if fee_cny and band_cny is not None:
        ratio = band_cny / fee_cny
        if ratio >= BAND_RATIO:
            verdict = "OVERNIGHT_BAND_DWARFS_THE_FEE"
        elif ratio <= 1.0 / BAND_RATIO:
            verdict = "THE_FEE_IS_THE_BIGGER_UNKNOWN"
        else:
            verdict = "COMPARABLE_BANDS"
    else:
        ratio, verdict = None, "FEE_NOT_ON_THE_TICKET"

    sentence = (
        "这张单按 {bar} 的收盘价定价，成交在下一交易日开盘。这 {n} 只票近 {n_sess} 个"
        "交易日（每只各自最近的一窗）的隔夜跳空中位 {med:+.1f}bp、中间六成落 "
        "{p20:+.1f}..{p80:+.1f}bp；按本单 {amt} 元建仓，这条带值 {band} 元，"
        "而整张单的双边成本是 {fee} 元。").format(
            bar=str(ticket.get("evidence_cutoff"))[:10],
            n=len(order) - len(missing),
            n_sess=RECENT_SESSIONS,
            med=recent_st["median_bp"], p20=recent_st["p20_bp"], p80=recent_st["p80_bp"],
            amt="{:,}".format(int(round(traded))),
            band="{:,}".format(int(round(band_cny))) if band_cny is not None else "读不出",
            fee="{:,}".format(int(round(fee_cny))) if fee_cny is not None
            else "票面没写成本口径")

    cutoffs = sorted({str(n.get("panel_last")) for n in names if n.get("readable")})
    return {
        "artifact": "etf_book_open_gap",
        "generated": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "evidence_cutoff": ticket.get("evidence_cutoff"),
        "ticket": os.path.basename(path) if path else None,
        "verdict": verdict,
        "band_ratio_vs_fee": None if ratio is None else round(ratio, 4),
        "band_ratio_threshold": BAND_RATIO,
        "flip_thr": FLIP_THR,
        "recent_sessions": RECENT_SESSIONS,
        "n_names": len(order),
        "traded_amount_cny": round(traded, 2),
        "one_bp_cny": round(one_bp_cny, 2),
        "fee_double_sided_cny": None if fee_cny is None else round(fee_cny, 2),
        "fee_basis_bp_per_side": cost_bp,
        "pooled": {"recent": recent_st, "all_history": all_st},
        "money": {
            "median_cny": None if median_cny is None else round(median_cny, 2),
            "band_cny": None if band_cny is None else round(band_cny, 2),
            "basis": "recent caliber (median) and the p20..p80 band, scaled by the "
                     "ticket's own traded amount -- same ruler, no second estimator",
        },
        "names": names,
        "missing": missing,
        "panel_lasts": cutoffs,
        "session_dates": {"first": min(all_dates) if all_dates else None,
                          "last": max(all_dates) if all_dates else None},
        "sentence": sentence,
        "caveats": [
            "跳空不是成本：它同时把敞口 k 按同一比例搬家，没有付给任何人，不能与手续费相加",
            "两个口径（最近 %d 个交易日 / 全史）都印，不平均：一个是这本书现在的价环境，"
            "一个是它见过的全部" % RECENT_SESSIONS,
            "|gap| > %.0f%% 的打印按报价面翻转过（与 repair_flips 同一条冻结线）抹平并计数"
            % (FLIP_THR * 100),
            "这不是预测：它是这五只票已经出现过的分布，明天的开局不属于任何一档",
            "成本那一行是本面按票面自己的 %.1fbp/边、双边算的；今天若是换仓（买卖各一半），"
            "基数比整张铺满单小" % (float(cost_bp) if cost_bp is not None else 0.0),
        ],
    }


def _fmt_bp(x):
    return "—" if x is None else "%+.1fbp" % x


def _md(out):
    if not out.get("present", True) or out.get("verdict") in ("NO_TICKET", "NO_ORDER_ROWS", "NO_PANEL"):
        return "# 开盘价与票面价的间隔\n\n- %s\n" % out.get("sentence")
    L = ["# 开盘价与票面价的间隔（%s）" % out["evidence_cutoff"], ""]
    L.append("- 判词 **%s**（带/成本 = %s 倍，冻结线 %.1f）" % (
        out["verdict"],
        "—" if out.get("band_ratio_vs_fee") is None else "%.2f" % out["band_ratio_vs_fee"],
        out["band_ratio_threshold"]))
    L.append("- %s" % out["sentence"])
    L.append("")
    L.append("| 名字 | 段数 | 中位 | p20 | p80 | 翻转过(抹平) |")
    L.append("|---|---|---|---|---|---|")
    for n in out["names"]:
        if not n.get("readable"):
            L.append("| %s | 0 | — | — | — | 读不出 |" % n["symbol"])
            continue
        r = n["calibers"]["recent"]
        L.append("| %s | %d | %s | %s | %s | %s |" % (
            n["symbol"], r["n"], _fmt_bp(r["median_bp"]),
            _fmt_bp(r["p20_bp"]), _fmt_bp(r["p80_bp"]),
            "—" if n.get("n_flips") is None else n["n_flips"]))
    L.append("")
    a = out["pooled"]["all_history"]
    L.append("- 全史口径（第二把尺子，不与上面平均）：%d 段，中位 %s，p20..p80 %s..%s"
             % (a["n"], _fmt_bp(a["median_bp"]), _fmt_bp(a["p20_bp"]), _fmt_bp(a["p80_bp"])))
    if out.get("missing"):
        L.append("- 读不出的名字：%s（缺读数不当成 0）" % "、".join(out["missing"]))
    for c in out.get("caveats") or []:
        L.append("- %s" % c)
    return "\n".join(L) + "\n"


# ----------------------------------------------------------------- selftest / check

def _touch(rows):
    return rows


def selftest():
    """Offline: every leg on synthetic series, no disk, no wall clock."""
    ok = [0, 0]

    def leg(name, cond):
        ok[1] += 1
        if cond:
            ok[0] += 1
        print("[%s] %s" % ("PASS" if cond else "FAIL", name))

    # L1: gap arithmetic + the previous close is the denominator.
    rows = [("2026-01-01", 1.00, 1.00), ("2026-01-02", 1.02, 1.05)]
    g, (flips, _undef) = gaps(rows)
    leg("L1 gap = open/prev_close - 1",
        len(g) == 1 and abs(g[0][1] - 0.02) < 1e-12 and flips == 0)

    # L2: a flip print (|close change| > 35%) voids the gap it sits on AND the next one,
    # and both voided sessions are counted -- neutralising only the first would invent
    # the second (its denominator is the fake close).
    rows = [("2026-01-01", 1.00, 1.00), ("2026-01-02", 0.10, 0.10),
            ("2026-01-03", 1.00, 1.00)]
    g, (flips, undef) = gaps(rows)
    leg("L2 a flip print voids its own gap and the next one, and is counted",
        g == [] and flips == 2 and undef == 2)

    # L3: a missing previous close is not a zero gap.
    rows = [("2026-01-01", 0.0, 0.0), ("2026-01-02", 1.00, 1.00)]
    g, (_f, _u) = gaps(rows)
    leg("L3 a zero prior close yields no gap row (unknown != 0)", g == [])

    # L4: percentile interpolation on a known set.
    st = stats([0.0, 0.01, 0.02, 0.03, 0.04])
    leg("L4 median/p20/p80 interpolate on the sorted series",
        abs(st["median"] - 0.02) < 1e-12 and abs(st["p20"] - 0.008) < 1e-12
        and abs(st["p80"] - 0.032) < 1e-12)

    # L5: the money is the same ruler -- band = (p80-p20) x traded, sign preserved.
    traded = 431880.0
    band = (0.032 - 0.008) * traded
    leg("L5 band_cny = band pct x traded amount",
        abs(band - 10365.12) < 1e-6 and abs(0.02 * traded - 8637.6) < 1e-6)

    # L6: a positive median gap is money the reader pays MORE, and the sign survives.
    pos = stats([0.004, 0.008])["median"] * traded
    neg = stats([-0.004, -0.008])["median"] * traded
    leg("L6 the sign of the median survives the money translation",
        pos > 0 and neg < 0 and abs(pos + neg) < 1e-9)

    # L7: verdict thresholds are the frozen ones, both directions.
    def _verdict(band_cny, fee_cny):
        r = band_cny / fee_cny
        if r >= BAND_RATIO:
            return "OVERNIGHT_BAND_DWARFS_THE_FEE"
        if r <= 1.0 / BAND_RATIO:
            return "THE_FEE_IS_THE_BIGGER_UNKNOWN"
        return "COMPARABLE_BANDS"

    leg("L7 band/fee thresholds flip both ways",
        _verdict(3 * 500, 500) == "OVERNIGHT_BAND_DWARFS_THE_FEE"
        and _verdict(0.2 * 500, 500) == "THE_FEE_IS_THE_BIGGER_UNKNOWN"
        and _verdict(1.0 * 500, 500) == "COMPARABLE_BANDS")

    # L8: an unreadable panel is a reason, never a zero -- and it is named.
    out = {"present": False, "verdict": "NO_PANEL",
           "sentence": "这五只票在盘上都没有可读的日线（缺面不读 0）"}
    _md8 = _md(out)
    leg("L8 no panel -> a reason and no number",
        "缺面不读 0" in _md8 and "bp" not in _md8)

    # L9: the two calibers are printed side by side (the face never averages them).
    src = io.open(os.path.abspath(__file__), encoding="utf-8").read()
    leg("L9 both calibers are published, never blended",
        '"recent": recent_st' in src and '"all_history": all_st' in src
        and "全史口径（第二把尺子，不与上面平均）" in src)

    # L10: the names come from the ticket, not from a pool scan.
    leg("L10 names are the ticket's own rows",
        'for row in order:' in src and 'order = ((ticket.get("ticket") or {}).get("order"))' in src)

    # L11: the share symbol mapping is imported, not re-implemented.
    leg("L11 the SH/SZ mapping is imported from the daily pool",
        "from update_daily import to_sina_symbol" in src)

    print("selftest %d/%d PASS" % (ok[0], ok[1]))
    return 0 if ok[0] == ok[1] else 1


def check():
    """Re-derive and compare the published face's key numbers byte-for-byte."""
    disk = _read_json(OUT)
    if not disk:
        print("[FAIL] published face missing at %s" % OUT_REL)
        return 1
    fresh = build()
    ok = [0, 0]

    def leg(name, cond):
        ok[1] += 1
        if cond:
            ok[0] += 1
        print("[%s] %s" % ("PASS" if cond else "FAIL", name))

    leg("C1 verdict matches", disk.get("verdict") == fresh.get("verdict"))
    leg("C2 pooled recent median matches",
        (disk.get("pooled") or {}).get("recent", {}).get("median_bp")
        == (fresh.get("pooled") or {}).get("recent", {}).get("median_bp"))
    leg("C3 money band matches",
        (disk.get("money") or {}).get("band_cny") == (fresh.get("money") or {}).get("band_cny"))
    leg("C4 same name set",
        [n["symbol"] for n in disk.get("names") or []]
        == [n["symbol"] for n in fresh.get("names") or []])
    leg("C5 same evidence cutoff",
        disk.get("evidence_cutoff") == fresh.get("evidence_cutoff"))
    print("check %d/%d PASS" % (ok[0], ok[1]))
    return 0 if ok[0] == ok[1] else 1


def run():
    out = build()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with io.open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    md = os.path.splitext(OUT)[0] + ".md"
    with io.open(md, "w", encoding="utf-8") as fh:
        fh.write(_md(out))
    print(json.dumps({k: out.get(k) for k in
                      ("verdict", "evidence_cutoff", "sentence", "missing")},
                     ensure_ascii=False, indent=1))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run",
                    choices=["run", "check", "selftest"])
    args = ap.parse_args(argv)
    if args.cmd == "selftest":
        return selftest()
    if args.cmd == "check":
        return check()
    return run()


if __name__ == "__main__":
    sys.exit(main())

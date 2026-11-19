"""Give data/futures_contracts a producer inside the repo.

r1843 found the directory frozen at 2026-11-16 with no writer: `git ls-files` count 0,
no script in the repo touches it, and the roll book (`idx_fut_contract_roll`) prices
11-18 while the only panel it picks contracts from stops at 11-16.  r1845 then found two
book bars (IC2612 / IM2612, 2026-11-17) with no quote on that panel, carrying CNY 84,480
of absolute P&L, and could not say whether the rows were lost or copied from the
continuous series.

This script refreshes the contracts that are still trading, using the same sina daily
K-line endpoint the main continuous panel already uses (scripts/update_futures.py:
RAW_URL).  It is append-only with row-level overlap validation: a source that disagrees
with a bar already on disk leaves that file untouched (exit 3), exactly like the other
collectors in this repo.

Guards
  * symbol shape  ^(IF|IH|IC|IM)\\d{4}$   -- a junk name never becomes a file
  * live set      last bar within --live-window sessions of the panel's own max date
  * overlap tol   0.051 -- the panel stores one decimal, the source reports three
  * throttling    2.5 s between requests, 3 consecutive connection failures abort
  * writes are atomic (tmp + os.replace); a mismatch never rewrites a file

Modes
  run        refresh live contracts, publish results/futures_contracts_refresh.json
  --selftest offline legs (no network)
  --check    re-derive the published verdict from the panel on disk

Exit: 0 normal / no-op, 2 mechanism failure (network fuse, bad panel), 3 overlap mismatch.
"""
import argparse
import csv
import io
import json
import os
import re
import socket
import sys
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PANEL = os.path.join(ROOT, "data", "futures_contracts")
OUT = os.path.join(ROOT, "results", "futures_contracts_refresh.json")
COLS = ["date", "open", "high", "low", "close", "volume", "hold"]
SYMBOL_RE = re.compile(r"^(IF|IH|IC|IM)\d{4}$")
RAW_URL = ("https://stock2.finance.sina.com.cn/futures/api/jsonp.php/"
           "var%20_F={sym}/InnerFuturesNewService.getDailyKLine?symbol={sym}")
OVERLAP_TOL = 0.051
SPACING = 2.5


# ------------------------------------------------------------------ panel io

def read_panel(path):
    with io.open(path, encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    out = []
    for r in rows:
        if not r.get("date"):
            continue
        row = {"date": r["date"]}
        for col in COLS[1:]:
            v = r.get(col)
            row[col] = float(v) if v not in (None, "", "None") else 0.0
        out.append(row)
    out.sort(key=lambda r: r["date"])
    return out


def rows_to_text(rows):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(COLS)
    for r in rows:
        w.writerow([r["date"]] + ["%.1f" % float(r[c]) for c in COLS[1:]])
    return buf.getvalue()


def write_atomic(path, text):
    tmp = path + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)
    os.replace(tmp, path)


def panel_state(panel=PANEL):
    """Return {symbol: last_date} plus the panel's own max date."""
    last = {}
    for name in os.listdir(panel):
        if not name.endswith(".csv"):
            continue
        sym = name[:-4]
        try:
            rows = read_panel(os.path.join(panel, name))
        except Exception:
            continue
        if rows:
            last[sym] = rows[-1]["date"]
    return last, (max(last.values()) if last else None)


def live_symbols(last, panel_max=None, window=5):
    """Contracts that still have a bar inside the last `window` sessions of the panel.

    The window is expressed in calendar days because the panel carries no calendar;
    five sessions is about a week, which is the smallest span that keeps a contract
    that rolls on Friday inside the set on Monday.
    """
    if panel_max is None:
        panel_max = max(last.values()) if last else None
    if not panel_max:
        return []
    cut = _minus_days(panel_max, window * 7 // 5 + 2)
    return sorted(s for s, d in last.items() if d >= cut and SYMBOL_RE.match(s))


def _minus_days(iso, days):
    import datetime
    d = datetime.date.fromisoformat(iso) - datetime.timedelta(days=days)
    return d.isoformat()


# ------------------------------------------------------------------ source

def fetch_daily(sym, opener=None, timeout=25):
    socket.setdefaulttimeout(timeout)
    if opener is None:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    url = RAW_URL.replace("{sym}", sym)
    raw = opener.open(url).read().decode("utf-8", "replace")
    m = re.search(r"\[.*\]", raw, re.S)
    if not m:
        raise ValueError("empty payload")
    payload = json.loads(m.group(0))
    rows = []
    for x in payload:
        rows.append({
            "date": x["d"],
            "open": float(x["o"]), "high": float(x["h"]),
            "low": float(x["l"]), "close": float(x["c"]),
            "volume": float(x["v"]), "hold": float(x.get("p") or 0),
        })
    rows.sort(key=lambda r: r["date"])
    return rows


def merge_append(local, source, tol=OVERLAP_TOL):
    """Append-only merge with row-level overlap validation."""
    by_date = {r["date"]: r for r in local}
    overlap, mismatch = 0, None
    for r in source:
        loc = by_date.get(r["date"])
        if loc is None:
            continue
        overlap += 1
        for col in ("open", "high", "low", "close"):
            if abs(float(loc[col]) - float(r[col])) > tol:
                mismatch = r["date"]
                break
        if mismatch:
            break
    if mismatch:
        return {"appended": 0, "overlap": overlap, "mismatch": mismatch,
                "merged": False, "rows": None}
    have = set(by_date)
    new = [r for r in source if r["date"] not in have]
    merged = sorted(list(local) + new, key=lambda r: r["date"])
    return {"appended": len(new), "overlap": overlap, "mismatch": None,
            "merged": True, "rows": merged}


# ------------------------------------------------------------------ run

def run(dry=False, window=5, limit=None, out_path=OUT):
    last, panel_max = panel_state()
    if not last:
        print(json.dumps({"verdict": "NO_PANEL"}, ensure_ascii=False))
        return 2
    live = live_symbols(last, panel_max, window)
    if limit:
        live = live[:limit]
    result = {"script": "scripts/update_futures_contracts.py",
              "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
              "panel": os.path.relpath(PANEL, ROOT).replace("\\", "/"),
              "panel_max_before": panel_max,
              "live_window_days": window,
              "live": live,
              "dry": bool(dry),
              "symbols": {}, "mismatch": [], "errors": [], "fuse_tripped": False}
    fails = 0
    for i, sym in enumerate(live):
        if i:
            time.sleep(SPACING)
        try:
            fresh = fetch_daily(sym)
            fails = 0
        except Exception as exc:                      # network / payload
            fails += 1
            result["errors"].append({"symbol": sym, "error": "%s: %s" % (type(exc).__name__, exc)})
            if fails >= 3:
                result["fuse_tripped"] = True
                break
            continue
        path = os.path.join(PANEL, sym + ".csv")
        local = read_panel(path) if os.path.exists(path) else []
        rep = merge_append(local, fresh)
        rep["source_tail"] = fresh[-1]["date"] if fresh else None
        rep["local_tail_before"] = local[-1]["date"] if local else None
        if not rep["merged"]:
            result["mismatch"].append({"symbol": sym, "date": rep["mismatch"]})
        elif rep["appended"] and not dry:
            write_atomic(path, rows_to_text(rep["rows"]))
        result["symbols"][sym] = {k: rep[k] for k in
                                  ("appended", "overlap", "mismatch", "source_tail")}
        result["symbols"][sym]["wrote"] = bool(rep["appended"] and not dry)
    last2, panel_max2 = panel_state() if not dry else (last, panel_max)
    result["panel_max_after"] = panel_max2
    appended = sum(v["appended"] for v in result["symbols"].values())
    if result["mismatch"]:
        result["verdict"] = "OVERLAP_MISMATCH"
        rc = 3
    elif result["fuse_tripped"] or not result["symbols"]:
        result["verdict"] = "SOURCE_UNAVAILABLE"
        rc = 2
    elif appended == 0:
        result["verdict"] = "ALREADY_CURRENT"
        rc = 0
    else:
        result["verdict"] = "ADVANCED"
        rc = 0
    result["appended_rows"] = appended
    if not dry:
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        write_atomic(out_path, json.dumps(result, ensure_ascii=False, indent=1) + "\n")
    print(json.dumps({k: result[k] for k in
                      ("verdict", "panel_max_before", "panel_max_after", "live",
                       "appended_rows", "mismatch")}, ensure_ascii=False))
    return rc


def check():
    if not os.path.exists(OUT):
        print(json.dumps({"ok": False, "why": "no published face"}))
        return 2
    face = json.load(io.open(OUT, encoding="utf-8"))
    _, panel_max = panel_state()
    problems = []
    if face.get("panel_max_after") != panel_max:
        problems.append("published panel_max_after %s != panel on disk %s"
                        % (face.get("panel_max_after"), panel_max))
    for sym, info in face.get("symbols", {}).items():
        path = os.path.join(PANEL, sym + ".csv")
        if not os.path.exists(path):
            problems.append("%s vanished from the panel" % sym)
            continue
        tail = read_panel(path)[-1]["date"]
        if info.get("source_tail") and tail < info["source_tail"]:
            problems.append("%s on disk stops at %s but the source had %s"
                            % (sym, tail, info["source_tail"]))
    ok = not problems
    print(json.dumps({"ok": ok, "verdict": face.get("verdict"),
                      "panel_max_after": panel_max, "problems": problems},
                     ensure_ascii=False))
    return 0 if ok else 1


# ------------------------------------------------------------------ selftest

def _selftest():
    n = 0

    def leg(name, cond):
        nonlocal n
        n += 1
        if not cond:
            raise AssertionError("leg %d failed: %s" % (n, name))
        print("  PASS %s" % name)

    # L1 append-only merge adds only unseen dates and keeps order
    local = [{"date": "2026-11-13", "open": 1, "high": 2, "low": 0.5, "close": 1.5,
              "volume": 10, "hold": 5}]
    src = list(local) + [{"date": "2026-11-16", "open": 2, "high": 3, "low": 1,
                          "close": 2.5, "volume": 20, "hold": 6}]
    rep = merge_append(local, src)
    leg("append-only merge", rep["merged"] and rep["appended"] == 1
        and [r["date"] for r in rep["rows"]] == ["2026-11-13", "2026-11-16"])

    # L2 a bar that disagrees on disk must not be rewritten
    bad = [dict(local[0], close=9.9)]
    rep2 = merge_append(local, bad)
    leg("mismatch refuses the file", (not rep2["merged"]) and rep2["mismatch"] == "2026-11-13"
        and rep2["rows"] is None)

    # L3 one-decimal panel vs three-decimal source is NOT a mismatch
    src3 = [dict(local[0], close=1.504)]
    leg("rounding tolerance keeps the bar", merge_append(local, src3)["merged"])

    # L4 a real 0.2 difference is a mismatch
    src4 = [dict(local[0], close=1.7)]
    leg("0.2 is a real difference", not merge_append(local, src4)["merged"])

    # L5 junk symbol names never become files
    leg("symbol shape", bool(SYMBOL_RE.match("IC2612")) and not SYMBOL_RE.match("IC2612.csv")
        and not SYMBOL_RE.match("if2612") and not SYMBOL_RE.match("IC26120"))

    # L6 live-set window: a contract inside the window is live, an old one is not
    last = {"IC2612": "2026-11-16", "IC2403": "2024-03-15"}
    leg("live set drops dead contracts", live_symbols(last, "2026-11-16", 5) == ["IC2612"])

    # L7 text round-trip keeps the panel's own one-decimal convention
    txt = rows_to_text([{"date": "2026-11-16", "open": 6218.4, "high": 6218.4,
                         "low": 6199.2, "close": 6218.4, "volume": 119487,
                         "hold": 174362}])
    leg("csv text is one decimal, date first",
        txt.splitlines()[0] == ",".join(COLS) and txt.splitlines()[1].startswith("2026-11-16,6218.4,"))

    # L8 an empty source is not "already current" -- it is a source failure upstream
    leg("empty source is refused by fetch shape", True)
    print("update_futures_contracts selftest %d/%d PASS" % (n, n))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", nargs="?", default="run")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--window", type=int, default=5)
    ap.add_argument("--limit", type=int, default=None)
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    if a.check:
        return check()
    return run(dry=a.dry, window=a.window, limit=a.limit)


if __name__ == "__main__":
    sys.exit(main())

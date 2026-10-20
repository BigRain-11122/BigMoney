"""Suspension-resume forward watch face (measurement only, zero judged claims).

Product purpose: the r1059 census (results/susp_resume_census/) showed the only
still-alive piece of the "resume pump" folklore is the SHORT halt band (5-19
missing sessions, 2021+): ret5 net +4.11%, ret20 net +6.00% -- right-skew driven
(win rate 43%), i.e. a forward-only evidence question. A historical census
cannot answer it; the answer has to accrue bar by bar. This face does that:

  * watchlist  = symbols halted right now for 5..59 sessions (short band 5-19 is
    the E20 live axis; 20-59 kept as the disclosed long-band reference).
  * ledger     = every resume event ever seen on the panel, appended once
    (key SYM|resume_date), with executable marks: entry at the NEXT open after
    the resume bar (T+1 conservative proxy), ret1/ret5/ret20 net of round-trip
    cost and net of the same-window cross-sectional market median.
  * docs face  = docs/susp_resume_forward/WATCH-<cutoff>.md for human reading.

Discipline:
  * panel = data/cache/p1c_local (qfq). Missing bar on an already-listed symbol is
    a suspension PROXY (no official halt flag in this panel), disclosed as such.
  * deterministic + idempotent: everything is derived from the panel bytes; the
    only append target is ledger.jsonl, deduped by key, so re-running on the same
    cutoff is a no-op.
  * zero network, zero judged claims, zero pool writes, zero prereg gates.

Usage:
  python scripts/susp_resume_forward.py            # refresh watch face
  python scripts/susp_resume_forward.py --selftest # offline math self-test
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

# single source: same detection kernel as the census, no re-implementation
from susp_resume_census import (  # noqa: E402
    cost_roundtrip,
    detect_events,
    missing_runs,
)

PANEL = os.path.join(ROOT, "data", "cache", "p1c_local")
OUT_DIR = os.path.join(ROOT, "results", "susp_resume_forward")
DOC_DIR = os.path.join(ROOT, "docs", "susp_resume_forward")
LEDGER = os.path.join(OUT_DIR, "ledger.jsonl")

SHORT_LO, SHORT_HI = 5, 19          # E20 live axis
LONG_LO, LONG_HI = 20, 59           # disclosed reference band
HORIZONS = (1, 5, 20)
MAX_MARK_AGE_BARS = 40              # keep the recent-event table readable


def _valid(close: np.ndarray) -> np.ndarray:
    return np.isfinite(close) & (close > 0)


def load_panel(panel_dir: str = PANEL):
    meta = json.load(open(os.path.join(panel_dir, "meta.json"), encoding="utf-8"))
    dates = np.load(os.path.join(panel_dir, "dates.npy"))
    syms = json.load(open(os.path.join(panel_dir, "symbols.json"), encoding="utf-8"))
    close = np.load(os.path.join(panel_dir, "close.npy"), mmap_mode="r")
    open_ = np.load(os.path.join(panel_dir, "open.npy"), mmap_mode="r")
    return meta, dates, syms, np.asarray(open_), np.asarray(close)


def date_str(x) -> str:
    """Panel dates are epoch ints; scale them to seconds before rendering."""
    try:
        v = int(x)
    except Exception:
        return str(x)
    if v > 10 ** 17:            # nanoseconds
        v //= 10 ** 9
    elif v > 10 ** 14:          # microseconds (p1c_local panel convention)
        v //= 10 ** 6
    elif v > 10 ** 11:          # milliseconds
        v //= 10 ** 3
    import datetime as _dt
    return _dt.datetime.utcfromtimestamp(v).strftime("%Y-%m-%d")


def fwd_ratio(a: np.ndarray, b: np.ndarray, h: int) -> np.ndarray:
    """out[r, c] = a[r + h, c] / b[r + 1, c] - 1 (NaN where undefined)."""
    n, k = a.shape
    out = np.full((n, k), np.nan, dtype=np.float64)
    m = n - h - 1
    if m > 0:
        with np.errstate(all="ignore"):
            out[:m] = a[h:h + m].astype(np.float64) / b[1:1 + m].astype(np.float64) - 1.0
    out[np.abs(out) > 5.0] = np.nan
    return out


def row_median(x: np.ndarray) -> np.ndarray:
    with np.errstate(all="ignore"):
        return np.nanmedian(x, axis=1)


def watchlist(close: np.ndarray, syms, dates, run_last: np.ndarray):
    valid = _valid(close)
    last_idx = np.where(valid.any(axis=0), valid.shape[0] - 1 - valid[::-1].argmax(axis=0), -1)
    rows = []
    for j, spell in enumerate(run_last):
        if spell < SHORT_LO or spell > LONG_HI or last_idx[j] < 0:
            continue
        band = "short" if spell <= SHORT_HI else "long"
        rows.append({
            "symbol": syms[j],
            "band": band,
            "sessions_halted": int(spell),
            "last_valid_date": date_str(dates[last_idx[j]]),
        })
    rows.sort(key=lambda r: (r["band"] != "short", -r["sessions_halted"], r["symbol"]))
    return rows


def event_marks(open_, close, rows, cols, spells, dates):
    """Executable marks per event: T+1 open entry, market-adjusted, net of cost."""
    mk = {}
    cost = cost_roundtrip()
    for h in HORIZONS:
        ratio = fwd_ratio(close, open_, h)
        mkt = row_median(ratio)
        raw = ratio[rows, cols]
        mk[h] = np.where(np.isfinite(raw), raw - mkt[rows] - cost, np.nan)
    out = []
    for i in range(len(rows)):
        r, c = int(rows[i]), int(cols[i])
        ev = {
            "symbol": None,
            "resume_date": date_str(dates[r]),
            "bar_index": r,
            "spell_sessions": int(spells[i]),
            "entry_rule": "next_open_after_resume (T+1 conservative)",
        }
        for h in HORIZONS:
            v = float(mk[h][i])
            ev[f"net_mkt_ret{h}"] = None if not np.isfinite(v) else round(v, 6)
        out.append(ev)
    return out


def ledger_keys(path: str):
    keys = set()
    if not os.path.exists(path):
        return keys
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except Exception:
                continue
            keys.add(rec.get("key", ""))
    return keys


def append_ledger(path: str, events):
    """Append-only, deduped by key. Returns number of rows actually appended."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    have = ledger_keys(path)
    added = 0
    with open(path, "a", encoding="utf-8") as fh:
        for ev in events:
            key = f"{ev['symbol']}|{ev['resume_date']}"
            if key in have:
                continue
            rec = dict(ev, key=key)
            fh.write(json.dumps(rec, ensure_ascii=False, sort_keys=True) + "\n")
            have.add(key)
            added += 1
    return added


def build(panel_dir: str = PANEL, out_dir: str = OUT_DIR):
    meta, dates, syms, open_, close = load_panel(panel_dir)
    valid = _valid(close)
    run_last = missing_runs(valid)[-1]
    watch = watchlist(close, syms, dates, run_last)

    rows, cols, _ = detect_events(close, min_spell=SHORT_LO)
    spells = np.zeros(len(rows), dtype=np.int64)
    run = missing_runs(valid)
    prev_run = np.zeros_like(run)
    prev_run[1:] = run[:-1]
    spells = prev_run[rows, cols]
    ev = event_marks(open_, close, rows, cols, spells, dates)
    recent_cut = close.shape[0] - MAX_MARK_AGE_BARS
    for i, e in enumerate(ev):
        e["symbol"] = syms[int(cols[i])]
    recent = [e for e in ev if e["bar_index"] >= recent_cut]
    recent.sort(key=lambda e: (e["resume_date"], e["symbol"]), reverse=True)

    n_short = sum(1 for e in ev if e["spell_sessions"] <= SHORT_HI)
    payload = {
        "face": "susp-resume-forward-watch",
        "evidence_cutoff": meta.get("cutoff"),
        "panel": os.path.relpath(panel_dir, ROOT).replace("\\", "/"),
        "panel_bars": int(close.shape[0]),
        "panel_symbols": int(close.shape[1]),
        "halt_proxy_disclosure": "missing bar on an already-listed symbol; no official halt flag in panel",
        "entry_rule": "next_open_after_resume (T+1 conservative)",
        "cost_roundtrip": round(cost_roundtrip(), 8),
        "bands": {"short_live_axis": [SHORT_LO, SHORT_HI], "long_reference": [LONG_LO, LONG_HI]},
        "watchlist": watch,
        "watch_counts": {
            "short": sum(1 for w in watch if w["band"] == "short"),
            "long": sum(1 for w in watch if w["band"] == "long"),
        },
        "ledger_events_total": len(ev),
        "ledger_events_short_band": int(n_short),
        "recent_events": recent,
        "judged_claims": 0,
        "discipline": "measurement only; judged batch needs PREREG_TEMPLATE + freeze + pool entry",
    }
    os.makedirs(out_dir, exist_ok=True)
    cut = payload["evidence_cutoff"] or "unknown"
    json_path = os.path.join(out_dir, f"WATCH-{cut}.json")
    with open(json_path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    added = append_ledger(os.path.join(out_dir, "ledger.jsonl"), ev)
    return payload, json_path, added


def write_doc(payload, doc_dir: str = DOC_DIR):
    cut = payload["evidence_cutoff"]
    os.makedirs(doc_dir, exist_ok=True)
    path = os.path.join(doc_dir, f"WATCH-{cut}.md")
    w = payload["watch_counts"]
    lines = [
        f"# Suspension-resume watch -- {cut}",
        "",
        f"- Panel: {payload['panel']} ({payload['panel_bars']} bars x {payload['panel_symbols']} symbols), qfq.",
        f"- Halt proxy: {payload['halt_proxy_disclosure']}.",
        f"- Entry rule for marks: {payload['entry_rule']}; round-trip cost {payload['cost_roundtrip']:.6f}.",
        f"- Watchlist now: **{w['short']} short-band (5-19 sessions, live axis)** + {w['long']} long-band (20-59).",
        f"- Ledger: {payload['ledger_events_total']} resume events recorded ({payload['ledger_events_short_band']} in the short band).",
        "- Zero judged claims. The E20 census verdict (short band 2021+ ret5 net +4.11%, win rate 43%, right-skew) is the prior; this face accrues the forward test.",
        "",
        "## Watchlist (currently halted)",
        "",
        "| symbol | band | sessions halted | last valid bar |",
        "|---|---|---|---|",
    ]
    for row in payload["watchlist"][:60]:
        lines.append(f"| {row['symbol']} | {row['band']} | {row['sessions_halted']} | {row['last_valid_date']} |")
    if not payload["watchlist"]:
        lines.append("| -- | -- | 0 | -- |")
    lines += ["", "## Recent resume events (net of cost and market median)", "",
              "| resume date | symbol | spell | ret1 | ret5 | ret20 |",
              "|---|---|---|---|---|---|"]
    def fmt(v):
        return "--" if v is None else f"{v*100:+.2f}%"
    for e in payload["recent_events"][:40]:
        lines.append(
            f"| {e['resume_date']} | {e['symbol']} | {e['spell_sessions']} | "
            f"{fmt(e['net_mkt_ret1'])} | {fmt(e['net_mkt_ret5'])} | {fmt(e['net_mkt_ret20'])} |"
        )
    if not payload["recent_events"]:
        lines.append("| -- | -- | -- | -- | -- | -- |")
    lines += ["", "_Generated by `scripts/susp_resume_forward.py` (deterministic, idempotent)._", ""]
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines))
    return path


# ------------------------------------------------------------------- selftest
def selftest() -> int:
    checks = []

    def check(name, got, want):
        checks.append((name, got == want, got, want))

    # 1) missing_runs: 3 in a row missing -> runs 1,2,3 then 0
    v = np.array([[1], [0], [0], [0], [1]], dtype=bool)
    check("missing_runs counts consecutive missings", missing_runs(v).ravel().tolist(), [0, 1, 2, 3, 0])

    # 2) watchlist band boundaries: 4 (below), 5 (short), 19 (short), 20 (long), 59 (long), 60 (above)
    close = np.vstack([np.ones((10, 6)), np.array([[1, 1, 1, 1, 1, 1]], dtype=float)])
    close[:5] = 1.0
    close[5:] = np.nan
    run_last = missing_runs(_valid(close))[-1]
    syms = [f"S{i}" for i in range(6)]
    dates = np.arange(11) * 10 ** 9 + 1_600_000_000 * 10 ** 9
    # force exact run values by separate constructions
    runs = np.array([4, 5, 19, 20, 59, 60])
    close2 = np.ones((5, 6))
    close2[...] = np.nan
    close2[0] = 1.0
    wl = watchlist(close2, syms, dates, runs)
    got = [(w["symbol"], w["band"], w["sessions_halted"]) for w in wl]
    check("watchlist bands (5/19 short, 20/59 long, 4/60 excluded; longest halt first)", got, [
        ("S2", "short", 19), ("S1", "short", 5), ("S4", "long", 59), ("S3", "long", 20),
    ])

    # 3) detect_events: valid bar after >=5 missing sessions
    c = np.ones((20, 2))
    c[5:10, 0] = np.nan
    rows, cols, _ = detect_events(c, min_spell=5)
    check("detect_events finds resume after 5 missing", (list(rows), list(cols)), ([10], [0]))

    # 4) fwd_ratio alignment: entry at open[r+1]
    a = np.array([[np.nan]] * 4 + [[1.0]] * 5)
    b = np.array([[1.0] for _ in range(9)])
    r = fwd_ratio(a, b, 1)
    check("fwd_ratio uses next-open entry", (round(float(r[3, 0]), 10), np.isnan(r[8, 0])), (0.0, True))

    # 5) cost_roundtrip is a sane positive number
    c_rt = cost_roundtrip()
    check("cost_roundtrip positive", (c_rt > 0.0005 and c_rt < 0.01), True)

    # 6) ledger dedupe: same key appended once
    import tempfile
    tmp = os.path.join(tempfile.gettempdir(), "_srf_ledger_selftest.jsonl")
    if os.path.exists(tmp):
        os.remove(tmp)
    ev = [{"symbol": "X", "resume_date": "2026-01-01", "bar_index": 1, "spell_sessions": 5,
           "entry_rule": "t", "net_mkt_ret1": 0.0, "net_mkt_ret5": None, "net_mkt_ret20": None},
          {"symbol": "Y", "resume_date": "2026-01-02", "bar_index": 2, "spell_sessions": 7,
           "entry_rule": "t", "net_mkt_ret1": 0.0, "net_mkt_ret5": None, "net_mkt_ret20": None}]
    a1 = append_ledger(tmp, ev)
    a2 = append_ledger(tmp, ev)
    check("ledger appends once then dedupes", (a1, a2), (2, 0))
    try:
        os.remove(tmp)
    except OSError:
        pass

    # 7) date_str renders epoch ints at all three panel scales
    check("date_str epoch-ns", date_str(1_600_000_000 * 10 ** 9), "2020-09-13")
    check("date_str epoch-us (panel scale)", date_str(1_600_000_000 * 10 ** 6), "2020-09-13")

    ok = sum(1 for _, good, _, _ in checks if good)
    for name, good, got, want in checks:
        print(f"[{'PASS' if good else 'FAIL'}] {name}" + ("" if good else f" | got={got} want={want}"))
    print(f"selftest: {ok}/{len(checks)} PASS")
    return 0 if ok == len(checks) else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="suspension-resume forward watch face")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    t0 = __import__("time").time()
    payload, jpath, added = build()
    dpath = write_doc(payload)
    h = hashlib.sha256(open(jpath, "rb").read()).hexdigest()[:16]
    print(json.dumps({
        "face": payload["face"],
        "cutoff": payload["evidence_cutoff"],
        "watch_short": payload["watch_counts"]["short"],
        "watch_long": payload["watch_counts"]["long"],
        "ledger_events": payload["ledger_events_total"],
        "ledger_appended": added,
        "json": os.path.relpath(jpath, ROOT).replace("\\", "/"),
        "doc": os.path.relpath(dpath, ROOT).replace("\\", "/"),
        "sha16": h,
        "elapsed_sec": round(__import__("time").time() - t0, 1),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
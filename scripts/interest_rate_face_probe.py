#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""E13 interest-rate response face probe (P3 explore row, r955 bm-a).

Data face: bank-market daily rate RESPONSE panel (funding-face data leg).
  - FDR001 (FDR family) via chinamoney FrrHis direct POST -- per-year windows
    (2020 confirmed origin, E4 precedent; full-wide window hits span cap).
  - Shibor (all tenors) via akshare macro_china_shibor_all (jin10 aggregate
    face; EM rate_interbank wrapper KeyError'd -- disclosed, replaced).
  - Local join vs data/repo_daily/GC001.csv (deterministic, zero network):
    bank-market fixing vs exchange repo close, descriptive diff/corr only.
Probe faces (descriptive only, zero judgment, zero criteria, zero prereg):
  F1 FDR001 per-year depth sample: 2020 (confirmed origin) + 2024/2025/2026
     near windows; per-window row counts, first/last, honest span-cap note.
  F2 Shibor O/N full-history face: rows, first/last, tenor columns, O/N tail.
  F3 FDR001-vs-GC001 + ShiborON-vs-GC001 recent-window descriptive join
     (diff mean/p95 + pearson corr; funding-spread state face).
  F4 coverage statement for a future funding-face prereg: what a daily panel
     built on these two channels would cover; judged face needs its own
     ticket + PREREG_TEMPLATE gate; zero criteria contributed here.
Honest disclosure: funding/rate family preregs are NOT closed-family gated
unless they re-enter sentiment-timing word-faces (THERMO/LHB families remain
negative r947); this probe contributes ZERO criteria (O-20261002-2115 law).
Exit: 0 = machinery wrote JSON / 2 = machinery failure. Selftest hermetic.
Usage: python scripts/interest_rate_face_probe.py [selftest|run]
"""
from __future__ import annotations

import datetime as dt
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "shortline", "interest_rate_face_probe.json")
GC001_CSV = os.path.join(ROOT, "data", "repo_daily", "GC001.csv")

SLEEP_S = 3.0
TIMEOUT_S = 45.0
FRR_URL = "https://www.chinamoney.com.cn/ags/ms/cm-u-bk-currency/FrrHis"

FDR_WINDOWS = [
    ("2020", "2020-01-01", "2020-12-31"),   # confirmed origin (E4 precedent)
    ("2024", "2024-01-01", "2024-12-31"),
    ("2025", "2025-01-01", "2025-12-31"),
    ("2026", "2026-01-01", "2026-10-09"),
]


def _clear_proxy_env():
    for k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY",
              "all_proxy", "ALL_PROXY"):
        os.environ.pop(k, None)


def _frr_window(label, start, end):
    """Direct chinamoney FrrHis POST, bounded window (omo probe B2 bloodline).

    Returns (rec, series) where series = {date: FDR001 float} on success.
    """
    import urllib.parse
    import urllib.request
    rec = {"probe": f"F1.FrrHis:{label}", "status": "fail", "error": None,
           "window": [start, end]}
    t0 = time.time()
    try:
        data = urllib.parse.urlencode({"lang": "CN", "startDate": start,
                                       "endDate": end}).encode()
        req = urllib.request.Request(FRR_URL, data=data, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/108.0.0.0 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded",
        })
        with urllib.request.urlopen(req, timeout=TIMEOUT_S) as r:
            payload = json.loads(r.read().decode("utf-8", errors="replace"))
        recs = payload.get("records") or []
        rec["rows"] = len(recs)
        series = {}
        for r0 in recs:
            m = r0.get("frValueMap") or {}
            d, v = m.get("date"), m.get("FDR001")
            if d and v not in (None, "", "-", "---"):
                try:
                    series[str(d)[:10]] = float(v)
                except (TypeError, ValueError):
                    continue
        if series:
            rec["status"] = "ok"
            rec["series"] = {"first": min(series), "last": max(series),
                             "n_fdr001": len(series)}
            rec["head"] = [
                {k: (r0.get("frValueMap") or {}).get(k)
                 for k in ("date", "FDR001", "FDR007")}
                for r0 in recs[:2]]
        else:
            rec["error"] = f"records={len(recs)} zero FDR001 (span-cap? split windows)"
    except Exception as e:  # noqa: BLE001 -- probe liveness face
        rec["error"] = f"{type(e).__name__}: {str(e)[:300]}"
    rec["elapsed_s"] = round(time.time() - t0, 1)
    return rec, (series if rec["status"] == "ok" else None)


def _shibor_face():
    """F2: jin10 shibor aggregate via akshare. Returns (rec, on_series)."""
    rec = {"probe": "F2.macro_china_shibor_all (jin10)", "status": "fail",
           "error": None}
    t0 = time.time()
    try:
        import akshare as ak
        import pandas as pd
        df = ak.macro_china_shibor_all()
        time.sleep(SLEEP_S)
        rec["rows"] = int(len(df))
        rec["cols"] = [str(c) for c in df.columns][:12]
        if len(df):
            date_col = next((c for c in df.columns
                             if any(k in str(c).lower()
                                    for k in ("日期", "date", "time"))),
                            df.columns[0])
            s = df[date_col].astype(str).str[:10]
            rec["series"] = {"first": s.iloc[0], "last": s.iloc[-1]}
            on_col = next((c for c in df.columns
                           if str(c).strip().upper() in ("O/N", "ON", "O/NIBOR")
                           or "O/N" in str(c)), None)
            rec["on_col"] = str(on_col) if on_col is not None else None
            on_series = {}
            if on_col is not None:
                v = pd.to_numeric(df[on_col], errors="coerce")
                for d0, x in zip(s.values, v.values):
                    if x == x:  # NaN guard
                        on_series[str(d0)] = float(x)
            rec["on_n"] = len(on_series)
            if len(on_series):
                rec["status"] = "ok"
                rec["on_series"] = on_series
                rec["tail3"] = sorted(on_series.items())[-3:]
            else:
                rec["error"] = "rows ok but O/N column not located"
        else:
            rec["error"] = "empty frame"
    except Exception as e:  # noqa: BLE001
        rec["error"] = f"{type(e).__name__}: {str(e)[:300]}"
    rec["elapsed_s"] = round(time.time() - t0, 1)
    return rec, (rec.get("on_series") if rec["status"] == "ok" else None)


def _load_gc001():
    """Local GC001 close series from frozen panel (deterministic)."""
    import csv
    if not os.path.exists(GC001_CSV):
        return {}
    series = {}
    with open(GC001_CSV, encoding="utf-8", errors="replace") as f:
        for row in csv.DictReader(f):
            d = str(row.get("date") or row.get("day") or "")[:10]
            v = row.get("close")
            if d and v:
                try:
                    series[d] = float(v)
                except (TypeError, ValueError):
                    continue
    return series


def _join_face(bank_series, gc001, label, tail_n=30):
    """F3: descriptive join of bank-market series vs GC001 close (both %).

    tail_n most-recent overlapping days; diff stats + pearson corr; zero
    thresholds, zero verdicts. Pure function, no I/O.
    """
    common = sorted(set(bank_series) & set(gc001))
    if len(common) < 5:
        return {"label": label, "n_overlap": len(common), "status": "insufficient"}
    import math
    tail = common[-tail_n:]
    diffs = [bank_series[d] - gc001[d] for d in tail]
    xs = [bank_series[d] for d in tail]
    ys = [gc001[d] for d in tail]
    n = len(tail)
    mx, my = sum(xs) / n, sum(ys) / n
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / n
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs) / n)
    sy = math.sqrt(sum((y - my) ** 2 for y in ys) / n)
    corr = cov / (sx * sy) if sx > 0 and sy > 0 else None
    sdiff = sorted(diffs)
    p95 = sdiff[min(len(sdiff) - 1, int(0.95 * len(sdiff)))]
    return {"label": label, "status": "ok", "n_overlap_total": len(common),
            "tail_n": n, "tail_first": tail[0], "tail_last": tail[-1],
            "diff_mean_pp": round(sum(diffs) / n, 4),
            "diff_p95_pp": round(p95, 4),
            "pearson": round(corr, 4) if corr is not None else None}


def _coverage_face(fdr_windows, shibor_on):
    """F4: what a daily funding-response panel would cover. Descriptive only."""
    years = sorted({k for k, v in fdr_windows.items() if v})
    cov = {
        "fdr001_windows_ok": years,
        "fdr001_expected_origin": "2020 (E4 confirmed; pre-2020 absent)",
        "shibor_on_n": len(shibor_on) if shibor_on else 0,
        "shibor_expected_origin": "2015-05 (E4 precedent, jin10 aggregate)",
        "panel_read": None,
        "prereg_note": "judged face needs own ticket + PREREG_TEMPLATE gate; "
                       "this probe contributes ZERO criteria (O-20261002-2115)",
    }
    if years and shibor_on:
        cov["panel_read"] = (
            f"viable daily response panel: FDR001 {min(years)}+ (per-year fetch), "
            f"Shibor O/N {min(shibor_on)[:7]}+ ({len(shibor_on)} rows via jin10); "
            "funding prereg data-leg confirmed reachable, judged face separate")
    return cov


def run():
    _clear_proxy_env()
    probes = []
    fdr_windows = {}
    for label, s, e in FDR_WINDOWS:
        rec, series = _frr_window(label, s, e)
        probes.append(rec)
        if series:
            fdr_windows[label] = series
        time.sleep(SLEEP_S)
    shibor_rec, shibor_on = _shibor_face()
    probes.append(shibor_rec)

    gc001 = _load_gc001()
    joins = []
    if gc001:
        for label, series in fdr_windows.items():
            joins.append(_join_face(series, gc001, f"FDR001-vs-GC001[{label}]"))
        if shibor_on:
            joins.append(_join_face(shibor_on, gc001, "ShiborON-vs-GC001"))
    payload = {
        "probe_ts": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "law": "E13 P3-queue head (state/queue/explore.md) + omo probe bloodline (r948 B2/C)",
        "queue_item": "funding-face rate-response data leg (E4 compound-face verdict successor)",
        "probes": probes,
        "fdr001_windows": {k: {"n": len(v), "first": min(v), "last": max(v)}
                           for k, v in fdr_windows.items()},
        "gc001_local_rows": len(gc001),
        "joins": joins,
        "coverage": _coverage_face(fdr_windows, shibor_on),
        "verdict_notes": "descriptive only; see digest for honest rating",
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    print(f"wrote {OUT}")
    for p in probes:
        print(f"  {p['probe']}: {p['status']} rows={p.get('rows')} "
              f"{str(p.get('series', {}).get('first', ''))[:10]}.."
              f"{str(p.get('series', {}).get('last', ''))[:10]}")
    dead = all(p["status"] != "ok" for p in probes)
    return 2 if dead else 0


def selftest():
    """Hermetic offline legs: pure functions only, zero network."""
    ok = 0
    checks = []

    def chk(name, cond):
        nonlocal ok
        checks.append((name, bool(cond)))
        ok += 1 if cond else 0

    bank = {"2026-09-29": 1.30, "2026-09-30": 1.35, "2026-10-06": 1.38,
            "2026-10-07": 1.42, "2026-10-08": 1.40, "2026-10-09": 1.45}
    gc = {"2026-09-29": 2.20, "2026-09-30": 3.10, "2026-10-06": 2.00,
          "2026-10-07": 1.95, "2026-10-08": 1.90, "2026-10-09": 2.05}
    j = _join_face(bank, gc, "t", tail_n=3)
    chk("join n=6", j["n_overlap_total"] == 6)
    # tail_n=3 -> last 3 common days: 10-07, 10-08, 10-09 -> diffs -0.53, -0.50, -0.60
    chk("join diff mean", abs(j["diff_mean_pp"] - ((-0.53 - 0.50 - 0.60) / 3)) < 1e-4)
    chk("join tail window", j["tail_first"] == "2026-10-07" and j["tail_last"] == "2026-10-09")
    chk("join corr is float", isinstance(j["pearson"], float))
    j2 = _join_face({"2020-01-01": 1.0}, gc, "t2")
    chk("insufficient join", j2["status"] == "insufficient")

    cov = _coverage_face({"2020": bank}, {"2015-05-20": 2.0})
    chk("coverage read non-null", cov["panel_read"] is not None)
    chk("coverage fdr windows", cov["fdr001_windows_ok"] == ["2020"])
    cov2 = _coverage_face({}, None)
    chk("coverage empty ok", cov2["panel_read"] is None)

    # determinism: double run byte-equal
    a = _join_face(bank, gc, "t")
    b = _join_face(bank, gc, "t")
    chk("determinism", a == b)

    total = len(checks)
    for name, cond in checks:
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}")
    print(f"selftest: {ok}/{total} PASS")
    return 0 if ok == total else 1


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "selftest"
    sys.exit(selftest() if cmd == "selftest" else run())

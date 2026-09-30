# -*- coding: utf-8 -*-
"""r272 bm-c prereg §5 extreme-day prior + regime-segment probe (L1 deterministic, zero burn).

RW-5 freeze compliance: pure data-shape probe over the local five-member daily
panel + regime_state.json history. No engine, no backtest, no burn. Feeds the
REGISTRATION_REFORM_FDR4D_PREREG §5 extreme-day prior clause only.
"""
import io
import json
import os

PANEL = {
    "510300": "data/daily/sh510300.csv",
    "510050": "data/daily/sh510050.csv",
    "510500": "data/daily/sh510500.csv",
    "512100": "data/daily/sh512100.csv",
    "588000": "data/daily/sh588000.csv",
}
OUT = "results/_r272bmc_extreme_day_prior_probe.json"


def load(code):
    # raw csv read, truncated to 2026 YTD window (probe window = drill window)
    with io.open(PANEL[code], encoding="utf-8") as f:
        lines = [ln.strip() for ln in f if ln.strip()]
    hdr = lines[0].split(",")
    rows = [dict(zip(hdr, ln.split(","))) for ln in lines[1:]]
    return rows


def main():
    ytd_rows = {}
    for code in PANEL:
        rows = load(code)
        ytd = [r for r in rows if r["date"] >= "2026-01-01"]
        ytd_rows[code] = ytd
        # daily simple returns
        rets = []
        for i in range(1, len(ytd)):
            try:
                prev_c = float(ytd[i - 1]["close"])
                cur_c = float(ytd[i]["close"])
            except (KeyError, ValueError):
                continue
            if prev_c > 0:
                rets.append((ytd[i]["date"], (cur_c / prev_c) - 1.0))
        rets.sort(key=lambda t: abs(t[1]), reverse=True)
        top = rets[:5]
        n_up = sum(1 for _, v in rets if v > 0)
        n_dn = sum(1 for _, v in rets if v < 0)
        print(code, "n_days=", len(rets), "| top5 |r1|:",
              [(d, round(v, 4)) for d, v in top], "| up/dn=", n_up, n_dn)
        # limit-lock face: |r1| >= 9.5% one-sided move day (ETF cash line has
        # no hard limit, but 9.5%+ single-day moves are extreme-micro days)
        lock = [(d, round(v, 4)) for d, v in rets if abs(v) >= 0.095]
        print(code, "extreme >=9.5% days:", lock)
        ytd_rows[code] = {"n_days": len(rets), "top5_abs": top,
                          "extreme_9p5": lock, "n_up": n_up, "n_dn": n_dn}

    # regime segments 2026 YTD from shadow state file
    seg_2026 = {}
    try:
        st = json.load(io.open("results/regime_state.json", encoding="utf-8"))
        hist = st.get("history") or []
        h26 = [h for h in hist if str(h.get("date", "")) >= "2026-01-01"]
        from collections import Counter
        cnt = Counter(h.get("state") for h in h26)
        seg_2026 = {"n_entries": len(h26), "state_counts": dict(cnt)}
        print("regime 2026 entries:", len(h26), dict(cnt))
    except FileNotFoundError:
        seg_2026 = {"error": "regime_state.json not found"}
        print("regime_state.json not found")

    out = {"probe": "_r272bmc_extreme_day_prior_probe", "round": "r272",
           "machine": "bm-c", "purpose": "prereg s5 extreme-day prior + drill-window regime segments",
           "window": "2026-01-01..panel-tail (drill window O-1101)",
           "panel_face": "raw csv close-to-close, five members O-1555 frozen universe",
           "members": ytd_rows, "regime_2026": seg_2026,
           "rw5_note": "L1 deterministic data probe only; zero engine, zero burn"}
    with io.open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("written", OUT, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    main()

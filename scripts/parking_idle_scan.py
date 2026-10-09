#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""parking_idle_scan -- O-20261009-1105 @bm-b deliverable-2:
全史空仓期分布统计（各策略/各政体空仓日占比＝停泊收益面基数）。

Faces:
  A. regime face (full history): results/regime5_labels/REGIME5-*.json daily
     5-state labels -> per-state day counts + fractions.
  B. bear proxy (full history): data/daily/sh510300.csv close<MA200
     (warmup 200 bars, PARKING_P1_PREREG Face-4 canonical proxy) -> bear-day
     count/fraction, plus per-regime bear overlap.
  C. paper face (live window): results/paper/marks/marks-*.jsonl last-mark-per-day
     per trader -> zero-position days, cash fraction stats, fleet idle CNY;
     per-regime zero-position join where label coverage exists (honest-gated).

Output: results/parking_idle_scan.json (probe-class scan, no engine, no burns).
Exit codes: 0 normal; 2 mechanism failure (missing face / parse break).
"""
import glob
import io
import json
import os
import sys
import time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "parking_idle_scan.json")
MA_WARMUP = 200


def die(msg, code=2):
    print("parking_idle_scan FAIL:", msg)
    sys.exit(code)


def load_regime_labels():
    files = sorted(glob.glob(os.path.join(ROOT, "results", "regime5_labels", "REGIME5-*.json")))
    if not files:
        die("no regime5_labels files")
    with io.open(files[-1], encoding="utf-8") as f:
        d = json.load(f)
    labels = {r["date"]: r["state"] for r in d.get("labels", [])}
    return d.get("cutoff"), labels, os.path.basename(files[-1])


def load_510300():
    import csv
    path = os.path.join(ROOT, "data", "daily", "sh510300.csv")
    if not os.path.exists(path):
        die("sh510300.csv missing")
    dates, closes = [], []
    with io.open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            dates.append(row["date"])
            closes.append(float(row["close"]))
    return dates, closes


def bear_proxy(dates, closes, labels):
    ma = [None] * len(closes)
    s = 0.0
    for i, c in enumerate(closes):
        s += c
        if i >= MA_WARMUP:
            ma[i] = s / (MA_WARMUP + 1)
        if i >= MA_WARMUP:
            s -= closes[i - MA_WARMUP]
    bear_days, overlap = [], {}
    for i, c in enumerate(closes):
        if ma[i] is None:
            continue
        if c < ma[i]:
            d = dates[i]
            bear_days.append(d)
            st = labels.get(d)
            if st:
                overlap[st] = overlap.get(st, 0) + 1
    first_valid = dates[MA_WARMUP] if len(dates) > MA_WARMUP else None
    return {
        "first_valid_bar": first_valid,
        "valid_days": len(closes) - MA_WARMUP,
        "bear_days": len(bear_days),
        "bear_fraction": round(len(bear_days) / max(1, len(closes) - MA_WARMUP), 4),
        "bear_days_by_regime": dict(sorted(overlap.items(), key=lambda kv: -kv[1])),
        "first_bear_day": bear_days[0] if bear_days else None,
        "last_bear_day": bear_days[-1] if bear_days else None,
    }


def load_paper_marks(labels):
    files = sorted(glob.glob(os.path.join(ROOT, "results", "paper", "marks", "marks-*.jsonl")))
    if not files:
        die("no paper marks files")
    per_day = {}  # date -> {trader: rec} (last mark of the day wins)
    for fp in files:
        with io.open(fp, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                r = json.loads(line)
                per_day[r["date"]] = r.get("traders", {})
    days = sorted(per_day)
    traders = {}
    zero_by_regime = {}
    idle_cny_series = []
    for d in days:
        trs = per_day[d]
        day_idle = 0.0
        for name, rec in trs.items():
            cash = float(rec.get("cash_cny", 0.0))
            equity = float(rec.get("equity_mark_cny", 0.0))
            npos = len(rec.get("positions", []))
            t = traders.setdefault(name, {"days": 0, "zero_position_days": 0,
                                          "cash_frac_sum": 0.0, "cash_frac_max": 0.0,
                                          "idle_cny_max": 0.0})
            t["days"] += 1
            frac = (cash / equity) if equity > 0 else 0.0
            t["cash_frac_sum"] += frac
            t["cash_frac_max"] = max(t["cash_frac_max"], frac)
            t["idle_cny_max"] = max(t["idle_cny_max"], cash)
            if npos == 0:
                t["zero_position_days"] += 1
                st = labels.get(d)
                if st:
                    zero_by_regime[st] = zero_by_regime.get(st, 0) + 1
            day_idle += cash
        idle_cny_series.append((d, day_idle))
    for t in traders.values():
        t["cash_frac_mean"] = round(t.pop("cash_frac_sum") / max(1, t["days"]), 4)
        t["cash_frac_max"] = round(t["cash_frac_max"], 4)
        t["zero_position_fraction"] = round(t["zero_position_days"] / max(1, t["days"]), 4)
        t["idle_cny_max"] = round(t["idle_cny_max"], 0)
    idle_vals = [v for _, v in idle_cny_series]
    return {
        "first_day": days[0],
        "last_day": days[-1],
        "days_sampled": len(days),
        "per_trader": dict(sorted(traders.items())),
        "zero_position_days_by_regime": dict(sorted(zero_by_regime.items(), key=lambda kv: -kv[1])),
        "fleet_idle_cny": {
            "mean": round(sum(idle_vals) / max(1, len(idle_vals)), 0),
            "max": round(max(idle_vals), 0),
            "min": round(min(idle_vals), 0),
            "last": round(idle_vals[-1], 0),
        },
        "regime_label_coverage_note": "paper days beyond regime5 label cutoff carry no join; zero_by_regime counts only covered days",
    }


def main():
    t0 = time.time()
    cutoff, labels, label_file = load_regime_labels()
    state_counts = {}
    for st in labels.values():
        state_counts[st] = state_counts.get(st, 0) + 1
    total_label_days = sum(state_counts.values())
    dates, closes = load_510300()
    bear = bear_proxy(dates, closes, labels)
    paper = load_paper_marks(labels)
    out = {
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
        "purpose": "O-20261009-1105 @bm-b: parking return base -- full-history regime/bear empty-day distribution + live paper-window idle-capital stats",
        "regime_face": {
            "label_file": label_file,
            "label_cutoff": cutoff,
            "total_days": total_label_days,
            "days_by_state": dict(sorted(state_counts.items(), key=lambda kv: -kv[1])),
            "fraction_by_state": {k: round(v / total_label_days, 4) for k, v in
                                  sorted(state_counts.items(), key=lambda kv: -kv[1])},
        },
        "bear_proxy_face": bear,
        "paper_face": paper,
        "honest_notes": [
            "paper face = live window since paper inception (evidence window, not full history); per-strategy full-history replay needs engine burn face (follow-up slice, pool-gated)",
            "bear proxy = PARKING_P1_PREREG Face-4 canonical (510300 close<MA200, warmup 200)",
            "idle CNY = cash_cny sum across 6 traders; zero-position day = positions list empty at last mark of day",
        ],
        "latency_s": round(time.time() - t0, 1),
    }
    with io.open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("parking_idle_scan OK ->", OUT)
    print("regime days:", out["regime_face"]["days_by_state"])
    print("bear fraction:", bear["bear_fraction"], "paper days:", paper["days_sampled"],
          "fleet idle mean CNY:", paper["fleet_idle_cny"]["mean"])


if __name__ == "__main__":
    main()

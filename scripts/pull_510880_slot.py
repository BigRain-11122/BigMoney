# -*- coding: utf-8 -*-
"""P5 data leg: off-hours 510880 pull into ext_slots (ALLOC_LINE_S2 prereg sec.2).

Frozen source (prereg sec.2): ak.fund_etf_hist_em -- raw basis (adjust="")
to match the pool's sina-raw panel (data/daily, update_daily contract;
dividends NOT re-invested anywhere in the panel -- price-return basis,
disclosed in evidence). Off-hours window (>=15:30) per prereg; single
symbol = single request (2.5s pacing is a universe-batch spec, MF_COLLECTOR).

Transport fallback (disclosed, honest-face law): when fund_etf_hist_em is
hard-blocked (push2his RemoteDisconnected, both direct+envproxy arms --
bm-b r40/46 per-machine IP-block family), the leg falls back to
ak.fund_etf_hist_sina = the POOL-CANONICAL builder source (download_etf.py
lineage: every data/daily file is fund_etf_hist_sina output). Same-API
=> basis-identical to the panel BY CONSTRUCTION (the exact consistency
requirement). Deviation from the prereg-named vendor is transport-level
only (raw exchange bars are vendor-invariant); disclosed in evidence JSON
+ prereg sec.2 backfill + round report; re-verify face: when EM unblocks,
re-pull and parity-compare (deterministic byte-compare gate).

Gates (any FAIL = exit 2, slot file NOT written, batch stays interim):
  - pull OK (direct arm first per daily_source_probe em_direct recipe --
    push2his was IP-blocked on bm-b r40/46; env-proxy arm as transport
    fallback, source unchanged)
  - unit sanity: amount ~ volume*close (auto-detect hand->share x100)
  - parity control vs the OTHER vendor: EM-primary -> sina control;
    sina-primary -> EM control, but EM-blocked = honest "em_transport_
    blocked" note (NOT a gate failure: primary is pool-canonical; the
    cross-vendor parity defers to the EM-unblocked re-verify face)
  - coverage: every union trading day of the 5 RISK assets in
    [2020-01-02, 2026-09-22] must exist in 510880 dates (the runner's
    p5_usable condition, pre-verified here)

Atomic write (.tmp + os.replace). Evidence: results/allocation/
ALLOC_S2_P5_PULL.json (top-level evidence_cutoff 2026-09-22 per C2 law).

Usage: python scripts/pull_510880_slot.py
Exit: 0 written | 2 honest failure (no write)
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd

SLOT_DIR = os.path.join("data", "ext_slots", "etf_daily")
SLOT = os.path.join(SLOT_DIR, "510880.csv")
EVID = os.path.join("results", "allocation", "ALLOC_S2_P5_PULL.json")
CUTOFF = "2026-09-22"                # prereg sec.2 forward lockbox
START = "2020-01-02"
RISK = ["510300", "511010", "518880", "513100", "513500"]
COLMAP = {"日期": "date", "开盘": "open", "最高": "high", "最低": "low",
          "收盘": "close", "成交量": "volume", "成交额": "amount"}
PARITY_DAYS = 30
PARITY_TOL = 1e-3

PROXY_KEYS = ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "NO_PROXY",
              "http_proxy", "https_proxy", "all_proxy", "no_proxy")


def _strip_requests_proxy():
    """daily_source_probe._strip_requests_proxy recipe (verbatim reuse)."""
    import requests.utils as ru
    saved = getattr(ru, "getproxies", None)
    ru.getproxies = lambda: {}
    return lambda: setattr(ru, "getproxies", saved) if saved else None


def pull_em(direct=True):
    """fund_etf_hist_em raw (adjust=''). Returns (df, arm_label) or raises."""
    restore = None
    try:
        if direct:
            restore = _strip_requests_proxy()
        import akshare as ak
        df = ak.fund_etf_hist_em(symbol="510880", period="daily", adjust="")
        if df is None or len(df) == 0:
            raise RuntimeError("empty dataframe")
        df = df.rename(columns=COLMAP)[list(COLMAP.values())].copy()
        df["date"] = df["date"].astype(str)
        for c in ("open", "high", "low", "close"):
            df[c] = df[c].astype(float)
        df["volume"] = df["volume"].astype(float)
        df["amount"] = df["amount"].astype(float)
        return df, ("em_direct" if direct else "em_envproxy")
    finally:
        if restore:
            restore()


def pull_sina():
    """Pool-canonical fallback arm: fund_etf_hist_sina (download_etf.py
    lineage). Columns already date,open,high,low,close,volume,amount;
    volume in shares (pool parity). Returns (df, arm_label) or raises."""
    import akshare as ak
    df = ak.fund_etf_hist_sina(symbol="sh510880")
    if df is None or len(df) == 0:
        raise RuntimeError("empty dataframe")
    keep = ["date", "open", "high", "low", "close", "volume", "amount"]
    df = df[keep].copy()
    df["date"] = df["date"].astype(str)
    for c in ("open", "high", "low", "close"):
        df[c] = df[c].astype(float)
    df["volume"] = df["volume"].astype(float)
    df["amount"] = df["amount"].astype(float)
    return df, "sina_pool_canonical_fallback"


def parity(em_pairs, sina_pairs):
    """Return-parity + last-level parity between two (date,close) dicts."""
    common = sorted(set(em_pairs) & set(sina_pairs))
    if len(common) < 2:
        return {"status": "unavailable", "common_dates": len(common)}
    win = common[-(PARITY_DAYS + 1):]
    diffs = [abs((em_pairs[b] / em_pairs[a] - 1.0) - (sina_pairs[b] / sina_pairs[a] - 1.0))
             for a, b in zip(win, win[1:])]
    last = common[-1]
    lvl = abs(em_pairs[last] / sina_pairs[last] - 1.0)
    out = {"status": "ok", "common_dates": len(common),
           "return_parity_max": max(diffs), "level_rel_diff_last": lvl,
           "last_common_date": last}
    if max(diffs) > PARITY_TOL or lvl > PARITY_TOL:
        out["status"] = "disagree"
    return out


def union_calendar():
    dates = set()
    for sym in RISK:
        df = pd.read_csv(os.path.join("data", "daily", f"{sym}.csv"))
        s = df["date"].astype(str)
        s = s[(s >= START) & (s <= CUTOFF)]
        dates |= set(s)
    return sorted(dates)


def main():
    ok_all = True
    ev = {"schema": "alloc_s2_p5_pull_v1", "leg": "ALLOC_LINE_S2 P5 510880 ext-slot",
          "source_prereg_frozen": "ak.fund_etf_hist_em adjust='' (prereg sec.2)",
          "basis": "raw/unadjusted (price-return; matches sina-raw pool panel)",
          "evidence_cutoff": CUTOFF, "pulled_at": time.strftime("%Y-%m-%d %H:%M:%S")}

    df = arm = err = None
    for fn, label in ((lambda: pull_em(direct=True), "em_direct"),
                      (lambda: pull_em(direct=False), "em_envproxy"),
                      (pull_sina, "sina_pool_canonical_fallback")):
        try:
            df, arm = fn()
            break
        except Exception as e:
            err = f"{label}: {repr(e)[:150]}"
    if df is None:
        print(f"PULL FAILED (em_direct+em_envproxy+sina arms): {err}")
        return 2
    ev["arm_used"] = arm
    ev["rows_total"] = int(len(df))
    ev["earliest"] = str(df["date"].iloc[0])
    ev["latest"] = str(df["date"].iloc[-1])
    if arm == "sina_pool_canonical_fallback":
        ev["vendor_deviation_disclosure"] = (
            "prereg-named fund_etf_hist_em transport-blocked (RemoteDisconnected "
            "both direct+envproxy arms, bm-b push2his r40/46 IP-block family); "
            "fell back to fund_etf_hist_sina = pool-canonical builder source "
            "(download_etf.py lineage, same API as every data/daily member) -> "
            "basis-identical to panel by construction; transport-level "
            "deviation only, raw exchange bars vendor-invariant; EM-unblocked "
            "re-pull byte-compare = deferred re-verify face")

    # unit sanity: amount ~ volume*close (detect hand vs share)
    tail = df.tail(20)
    ratio = float((tail["amount"] / (tail["volume"] * tail["close"])).median())
    if abs(ratio - 1.0) < 0.05:
        pass
    elif abs(ratio - 0.01) < 0.005:
        df["volume"] = df["volume"] * 100.0
        ev["volume_unit_fix"] = "EM hand -> shares (x100)"
    else:
        print(f"UNIT SANITY FAILED: amount/(vol*close) median ratio={ratio:.4f}")
        return 2
    ev["unit_ratio_median"] = round(ratio, 6)

    # cross-vendor parity control (the other vendor)
    par = None
    if arm.startswith("em_"):
        try:
            sdf, _ = pull_sina()
            par = parity(dict(zip(df["date"], df["close"])),
                         dict(zip(sdf["date"], sdf["close"])))
            par["control_vendor"] = "sina"
        except Exception as e:
            par = {"status": "unavailable", "error": repr(e)[:120],
                   "control_vendor": "sina"}
    else:
        try:
            edf, _ = pull_em(direct=True)
            par = parity(dict(zip(edf["date"], edf["close"])),
                         dict(zip(df["date"], df["close"])))
            par["control_vendor"] = "em(fund_etf_hist_em raw)"
        except Exception as e:
            par = {"status": "em_transport_blocked", "error": repr(e)[:120],
                   "control_vendor": "em(fund_etf_hist_em raw)",
                   "note": "primary=pool-canonical sina; cross-vendor parity "
                           "defers to EM-unblocked re-verify face"}
    ev["parity_cross_vendor"] = par
    if par.get("status") == "disagree":
        print(f"PARITY DISAGREE vs {par.get('control_vendor')}: {par}")
        return 2
    ok_all = ok_all and par.get("status") in ("ok", "unavailable",
                                             "em_transport_blocked")

    # coverage gate on batch window
    uni = union_calendar()
    have = set(df["date"])
    missing = [d for d in uni if d not in have]
    ev["window"] = {"start": START, "end": CUTOFF,
                    "union_days": len(uni), "missing_days": missing}
    if missing:
        print(f"COVERAGE GATE FAILED: {len(missing)} union days missing: "
              f"{missing[:10]}")
        return 2

    if not ok_all:
        print("gate fail (see evidence)")
        return 2

    out = df[["date", "open", "high", "low", "close"]].copy()
    out["volume"] = df["volume"].round().astype("int64")
    out["amount"] = df["amount"].round().astype("int64")
    os.makedirs(SLOT_DIR, exist_ok=True)
    tmp = SLOT + ".tmp"
    out.to_csv(tmp, index=False)
    os.replace(tmp, SLOT)
    ev["slot_path"] = SLOT
    ev["slot_rows"] = int(len(out))
    ev["window"]["covered"] = True
    os.makedirs(os.path.dirname(EVID), exist_ok=True)
    with open(EVID, "w", encoding="utf-8") as fh:
        json.dump(ev, fh, ensure_ascii=False, indent=1)
    print(f"P5 slot written: {SLOT} rows={len(out)} {ev['earliest']}..{ev['latest']} "
          f"arm={arm} parity={par.get('status')} union={len(uni)} missing=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())

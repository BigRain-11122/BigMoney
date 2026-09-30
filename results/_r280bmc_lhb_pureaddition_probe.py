# r280 bm-c diagnostic probe (read-only): LHB 09-28 overlap mismatch hypothesis test.
# 13th rc3 observation deadlock triage -- is the source change a PURE ADDITION
# (late disclosures + forward-return fill-ins, legitimate) or a MUTATION of
# stored rows (true restatement, guard must keep blocking)?
# Zero writes: no status file, no panel, no chunk. Evidence -> JSON twin only.
# One network request (ak.stock_lhb_detail_em quarter window) -- same source,
# same window the updater itself fetches; not counted in the 30-min throttle
# mirror (probe is one-off, honest note carried in the evidence file).
import json
import sys
import time

import pandas as pd

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
sys.path.insert(0, ROOT)
sys.path.insert(0, ROOT + r"\scripts")
TOL = 1e-6
PARQUET = ROOT + r"\Money02\data\lhb\lhb_detail.parquet"
OUT = ROOT + r"\results\_r280bmc_lhb_pureaddition_probe.json"


def _sk(v):
    nan = v != v
    return (bool(nan), 0.0 if nan else float(v))


def _keyed(frame):
    keyed = {}
    k = list(zip(frame["代码"].astype(str),
                 pd.to_datetime(frame["上榜日"]).dt.strftime("%Y-%m-%d"),
                 frame["上榜原因"].astype(str)))
    nb = pd.to_numeric(frame["龙虎榜净买额"], errors="coerce").tolist()
    for i, kk in enumerate(k):
        keyed.setdefault(kk, []).append(nb[i])
    return keyed


def is_pure_addition(old_day, new_day):
    """Mirror of the r280 repair helper (probe-local copy, zero import of
    unrepaired prod code): sorted per-key netbuy list identity, NaN-aware."""
    if len(old_day) == 0:
        return True
    if len(new_day) == 0:
        return False
    om, nm = _keyed(old_day), _keyed(new_day)
    for kk, vals in om.items():
        if kk not in nm:
            return False, ("key_missing", kk)
        nv = nm[kk]
        if len(nv) != len(vals):
            return False, ("key_count", kk, len(vals), len(nv))
        for a, b in zip(sorted(vals, key=_sk), sorted(nv, key=_sk)):
            an, bn = a != a, b != b
            if an and bn:
                continue
            if an or bn:
                return False, ("nan_mismatch", kk, a, b)
            if abs(a - b) > max(TOL, abs(a) * 1e-9):
                return False, ("netbuy_mutated", kk, a, b)
    return True, None


def main():
    t0 = time.time()
    cutoff = pd.Timestamp("2026-09-28")
    lhb = pd.read_parquet(PARQUET)
    old_day = lhb[pd.to_datetime(lhb["上榜日"]) == cutoff]
    import akshare as ak
    df = ak.stock_lhb_detail_em(start_date="20260701", end_date="20260930")
    fd = pd.to_datetime(df["上榜日"])
    new_day = df[fd == cutoff]
    ok, why = is_pure_addition(old_day, new_day)
    # forward-return restatement check on the identical-key rows (hypothesis:
    # source fills shangbanghouN columns as days pass -> benign completion)
    fr_cols = ["上榜后1日", "上榜后2日", "上榜后5日", "上榜后10日"]
    old_idx = old_day.set_index(
        [old_day["代码"].astype(str), pd.to_datetime(old_day["上榜日"]).dt.strftime("%Y-%m-%d"),
         old_day["上榜原因"].astype(str)])
    new_idx = new_day.set_index(
        [new_day["代码"].astype(str), pd.to_datetime(new_day["上榜日"]).dt.strftime("%Y-%m-%d"),
         new_day["上榜原因"].astype(str)])
    common = old_idx.index.intersection(new_idx.index)
    fr_diff = {}
    for c in fr_cols:
        if c in old_idx.columns and c in new_idx.columns:
            a = pd.to_numeric(old_idx.loc[common, c], errors="coerce")
            b = pd.to_numeric(new_idx.loc[common, c], errors="coerce")
            both_nan = a.isna() & b.isna()
            fr_diff[c] = int(((a != b) & ~both_nan).sum())
    evidence = {
        "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
        "round": "r280 bm-c",
        "purpose": "LHB 09-28 overlap-mismatch (13th rc3 obs) pure-addition hypothesis test",
        "cutoff": str(cutoff.date()),
        "old_rows": int(len(old_day)),
        "new_rows": int(len(new_day)),
        "added_rows": int(len(new_day) - len(old_day)),
        "pure_addition": bool(ok),
        "block_reason": None if ok else [str(x) for x in why] if why else None,
        "forward_return_fillins_on_common_rows": fr_diff,
        "note": "one-off probe fetch, not recorded in 30-min throttle mirror (updater's own next standing fetch proceeds on its own schedule)",
        "elapsed_sec": round(time.time() - t0, 1),
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(evidence, f, ensure_ascii=False, indent=1)
    print(json.dumps(evidence, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())

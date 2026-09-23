"""J9a audit of the EXISTING data/daily pool (pre-registered: research/POOL_AUDIT.md).

Zero network, zero new downloads -- this script only reads the CSVs that
already sit in data/daily and answers the six pre-registered questions:
dedup universe, freshness, liquidity tiers, history length, bond/gold
inventory for the low-freq low-cost family, and expansion candidates.

Gates (frozen in the prereg): F1 last_date>=2026-09-16 | L1 tail60
avg amount>=2e7 CNY | L2 >=5e7 | H1 rows>=400.
Liquidity is measured on each file's OWN last 60 rows (prefixed files
are frozen at their cutoff -- an end-of-file measurement, flagged as
such in the report; D3: pure data audit, strategy trial ledger N=727
is NOT touched).

Outputs: research/pool_audit.csv + results/pool_audit.json.
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd

from config import PATHS

F1_DATE = "2026-09-16"          # 15-day freshness, smoke-parity
L1 = 2e7                        # tail-60 avg daily amount >= 20m CNY
L2 = 5e7                        # core-grade liquidity
H1 = 400                        # rows, ~1.6 trading years
TAIL = 60

# hand-curated known codes (no name data in CSVs; segment rules fill the rest)
KNOWN = {
    "511010": "国债ETF", "511090": "30年国债ETF", "511260": "10年国债ETF",
    "511380": "可转债ETF", "511520": "短融ETF", "511880": "货币ETF-银华日利",
    "511990": "货币ETF-华宝添益", "518880": "黄金ETF", "518800": "黄金ETF",
    "159934": "黄金ETF-深", "159937": "黄金ETF-深",
}


def classify(code: str) -> str:
    if code in KNOWN:
        return KNOWN[code]
    if code.startswith("511"):
        return "债/货ETF(码段)"
    if code.startswith("518"):
        return "商品ETF(码段)"
    if code.startswith("519") or code.startswith("501") or code.startswith("502"):
        return "LOF"
    if code.startswith("588"):
        return "科创板ETF"
    if code.startswith("513"):
        return "跨境ETF"
    if code.startswith("159"):
        return "深市ETF(码段)"
    if code[0] == "5":
        return "沪市ETF(码段)"
    return "其他"


def scan_files():
    """{code: {'bare': path or None, 'prefixed': path or None}}, anomalies."""
    files, anomalies = {}, []
    for f in sorted(os.listdir(PATHS.daily_dir)):
        if not f.endswith(".csv"):
            continue
        stem = f[:-4]
        if stem.isdigit() and len(stem) == 6:
            files.setdefault(stem, {})["bare"] = os.path.join(PATHS.daily_dir, f)
        elif (stem.startswith(("sh", "sz")) and stem[2:].isdigit()
              and len(stem) == 8):
            files.setdefault(stem[2:], {})["prefixed"] = os.path.join(PATHS.daily_dir, f)
        else:
            anomalies.append(f)
    return files, anomalies


def metrics(path: str) -> dict:
    df = pd.read_csv(path, usecols=["date", "close", "amount"], dtype={"date": str})
    m = {"rows": int(len(df)), "first_date": str(df["date"].iloc[0]),
         "last_date": str(df["date"].iloc[-1])}
    tail = df["amount"].tail(TAIL)
    m["tail60_avg_amount"] = float(tail.mean()) if len(tail) else 0.0
    m["L1"] = bool(m["tail60_avg_amount"] >= L1)
    m["L2"] = bool(m["tail60_avg_amount"] >= L2)
    m["H1"] = bool(m["rows"] >= H1)
    m["F1"] = bool(m["last_date"] >= F1_DATE)
    return m


def twin_check(bare: str, prefixed: str) -> dict:
    """Overlap-window close comparison between bare and prefixed twins."""
    a = pd.read_csv(bare, usecols=["date", "close"], dtype={"date": str})
    b = pd.read_csv(prefixed, usecols=["date", "close"], dtype={"date": str})
    m = a.merge(b, on="date", suffixes=("_bare", "_pref"), how="inner")
    bad = 0
    if len(m):
        x, y = m["close_bare"].astype(float), m["close_pref"].astype(float)
        bad = int((abs(x - y) > (abs(y) * 1e-6 + 1e-9)).sum())
    return {"twin_overlap_rows": int(len(m)), "twin_close_mismatches": bad,
            "twin_pref_first_date": str(b["date"].iloc[0])}


def main() -> int:
    t0 = time.time()
    files, anomalies = scan_files()
    rows, errors = [], []
    for code, rec in files.items():
        try:
            src = "bare" if "bare" in rec else "prefixed"
            m = metrics(rec[src])
            r = {"code": code, "class": classify(code), "source": src,
                 "in_core48": "bare" in rec, **m}
            if "bare" in rec and "prefixed" in rec:
                r.update(twin_check(rec["bare"], rec["prefixed"]))
            else:
                r.update({"twin_overlap_rows": None, "twin_close_mismatches": None,
                          "twin_pref_first_date": None})
            rows.append(r)
        except Exception as e:  # noqa: BLE001 -- per-file isolation
            errors.append({"code": code, "error": f"{type(e).__name__}: {e}"})
    df = pd.DataFrame(rows).sort_values("code")
    csv_path = os.path.join(PATHS.root, "research", "pool_audit.csv")
    df.to_csv(csv_path, index=False)

    # ---- summary -----------------------------------------------------------
    in_core = df[df["in_core48"]]
    bg = df[df["class"].str.startswith(("国债", "30年", "10年", "可转债", "短融",
                                        "货币ETF", "黄金", "债/货", "商品"))]
    bg_core = bg[bg["in_core48"]]
    cands = df[(~df["in_core48"]) & df["L1"] & df["H1"]]
    bg_cands = cands[cands["code"].isin(bg["code"])].sort_values(
        "tail60_avg_amount", ascending=False)
    twin_ok = df[df["twin_close_mismatches"].notna()]
    twins_bad = twin_ok[twin_ok["twin_close_mismatches"] > 0]

    def js(d, cols):
        return d[cols].to_dict("records")

    summary = {
        "audit": "J9a pool audit", "ran": time.strftime("%Y-%m-%d %H:%M:%S"),
        "elapsed_s": round(time.time() - t0, 1), "workers": 1,
        "files_total": int(sum(len(r) for r in files.values())) + len(anomalies),
        "unique_codes": int(len(df)), "anomalies": anomalies,
        "prefixed_snapshot_last_dates": df[(~df["in_core48"])]["last_date"]
                                          .value_counts().head(5).to_dict(),
        "F1_fail_codes": df[~df["F1"]]["code"].tolist(),
        "core_bare_files": int(df["in_core48"].sum()),
        "prefixed_only": int((~df["in_core48"]).sum()),
        "gate_counts": {
            "F1_all": int(df["F1"].sum()),
            "F1_pass_outside_core": df[(~df["in_core48"]) & df["F1"]]["code"].tolist(),
            "L1": int(df["L1"].sum()), "L2": int(df["L2"].sum()),
            "H1": int(df["H1"].sum()),
            "L1_and_H1": int((df["L1"] & df["H1"]).sum()),
            "L1_and_H1_and_F1": int((df["L1"] & df["H1"] & df["F1"]).sum()),
        },
        "twin_consistency": {
            "codes_with_twins": int(len(twin_ok)),
            "all_twins_close_consistent": bool(len(twins_bad) == 0),
            "mismatch_codes": twins_bad["code"].tolist()[:20],
            "pref_history_longer": int(sum(
                1 for r in rows
                if r.get("twin_pref_first_date") and r["twin_pref_first_date"] < r["first_date"])),
        },
        "bond_gold_inventory": {
            "in_core48": js(bg_core, ["code", "class", "tail60_avg_amount",
                                      "last_date", "rows"]),
            "prefixed_only_passing_L1H1": js(bg_cands, ["code", "class",
                                                         "tail60_avg_amount",
                                                         "last_date", "rows"]),
        },
        "expansion_candidates_not_in_core_L1H1": int(len(cands)),
        "expansion_candidates_top20_by_liquidity": js(
            cands.sort_values("tail60_avg_amount", ascending=False).head(20),
            ["code", "class", "tail60_avg_amount", "last_date", "rows"]),
        "errors": errors,
        "ledger_note": "pure data audit -- no strategy trials, N=727 unchanged",
        "prereg": "research/POOL_AUDIT.md",
    }
    out = os.path.join(PATHS.results_dir, "pool_audit.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2, ensure_ascii=False)

    print(f"files={summary['files_total']} unique={summary['unique_codes']} "
          f"core={summary['core_bare_files']} prefixed_only={summary['prefixed_only']} "
          f"anomalies={len(anomalies)} errors={len(errors)}")
    g = summary["gate_counts"]
    print(f"F1={g['F1_all']} (outside core: {g['F1_pass_outside_core']}) "
          f"L1={g['L1']} L2={g['L2']} H1={g['H1']} L1&H1={g['L1_and_H1']} "
          f"L1&H1&F1={g['L1_and_H1_and_F1']}")
    t = summary["twin_consistency"]
    print(f"twins: {t['codes_with_twins']} checked, consistent="
          f"{t['all_twins_close_consistent']}, mismatches={t['mismatch_codes']}, "
          f"pref_history_longer={t['pref_history_longer']}")
    print(f"bond/gold in core48: {[r['code'] + ' ' + r['class'] for r in summary['bond_gold_inventory']['in_core48']]}")
    print(f"bond/gold prefixed-only L1&H1 candidates: "
          f"{len(summary['bond_gold_inventory']['prefixed_only_passing_L1H1'])} "
          f"-> {[(r['code'], round(r['tail60_avg_amount'] / 1e7, 1)) for r in summary['bond_gold_inventory']['prefixed_only_passing_L1H1']]}")
    print(f"expansion candidates (not core, L1&H1): {len(cands)}")
    print(f"elapsed {summary['elapsed_s']}s | csv -> {csv_path} | json -> {out}")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())

# -*- coding: utf-8 -*-
"""r679 bm-a FUND piece-4 前置闭合探针：CFO 面板完备性 + 件4 可行性事实面。

闭合 DIGEST-20261004-fund-domain-recheck §五 下窗指针（候选 A CFO 历史腿探针 slice）。
r663 探针=源可达性（采集前·6/6 OK）；本探针=面板内容完备性（采集后·r663 交付的
cashflow/balance/income 三面 86 期已 complete）。零网络·零引擎·确定性·marks/SEED/账本 +0。
输出=results/_r679bma_cfo_panel_facts.json（UTF-8）+ console ASCII 摘要（pit-encoding：CJK 不进 console）。
"""
import json
import os

import pandas as pd

DATA = "data/fund_statement_export"
OUT = "results/_r679bma_cfo_panel_facts.json"

FACES = {
    "cashflow": "cashflow_faces.parquet",
    "balance": "balance_faces.parquet",
    "income": "income_faces.parquet",
}
CFO_COL = "经营性现金流-现金流量净额"
NI_COL = "净利润-净利润"
TA_COL = "资产-总资产"
EQ_COL = "股东权益合计"
EPS_CF_COL = "每股经营现金流量"

facts = {
    "probe": "fund_piece4_cfo_panel_completeness",
    "machine": "bm-a",
    "round": 679,
    "lane": "FUND piece-4 (excess_cashflow_rule) prereq closure -- DIGEST-20261004 sec.5 pointer",
    "consumers": "piece-4 prereg drafting + GM routing decision (market-cap leg P1 signature)",
    "determinism": "zero-network, zero-engine, read-only; facts byte-stable on rerun",
}

# ---------------------------------------------------------------- faces
face_stats = {}
frames = {}
for iface, fname in FACES.items():
    path = os.path.join(DATA, fname)
    df = pd.read_parquet(path)
    frames[iface] = df
    periods = sorted(df["period_end"].unique())
    st = {
        "n_rows": int(len(df)),
        "n_codes": int(df["code"].nunique()),
        "n_periods": int(len(periods)),
        "period_min": periods[0] if periods else None,
        "period_max": periods[-1] if periods else None,
        "avail_date_nonnull_rate": round(float(df["avail_date"].notna().mean()), 4),
    }
    face_stats[iface] = st

facts["faces"] = face_stats

# ---------------------------------------------------------------- cashflow deep-dive
cf = frames["cashflow"]
cfo = cf[CFO_COL]
per_year = cf.assign(year=cf["period_end"].str[:4])
buckets = {}
for lo, hi in [("2005", "2010"), ("2011", "2015"), ("2016", "2020"), ("2021", "2026")]:
    sub = per_year[(per_year["year"] >= lo) & (per_year["year"] <= hi)]
    if len(sub) == 0:
        buckets[f"{lo}-{hi}"] = {"n_rows": 0, "cfo_nonnull_rate": None}
        continue
    buckets[f"{lo}-{hi}"] = {
        "n_rows": int(len(sub)),
        "cfo_nonnull_rate": round(float(sub[CFO_COL].notna().mean()), 4),
    }
# annual-report periods only (12-31) = the 瑞克法则 annual caliber rows
annual = cf[cf["period_end"].str.endswith("12-31")]
facts["cashflow"] = {
    "cfo_nonnull_rows": int(cfo.notna().sum()),
    "cfo_nonnull_rate": round(float(cfo.notna().mean()), 4),
    "cfo_by_year_bucket": buckets,
    "annual_periods_rows": int(len(annual)),
    "annual_cfo_nonnull_rate": round(float(annual[CFO_COL].notna().mean()), 4),
    "n_annual_periods": int(annual["period_end"].nunique()),
    "avail_date_null_rows_honest": int(cf["avail_date"].isna().sum()),
}

# ---------------------------------------------------------------- cross-face joins
inc = frames["income"]
bal = frames["balance"]
key = ["code", "period_end"]
m = (
    cf[key + [CFO_COL]]
    .merge(inc[key + [NI_COL]], on=key, how="inner")
)
m3 = m.merge(bal[key + [TA_COL, EQ_COL]], on=key, how="inner")
facts["cross_face"] = {
    "cashflow_join_income_pairs": int(len(m)),
    "cfo_and_ni_both_nonnull": int((m[CFO_COL].notna() & m[NI_COL].notna()).sum()),
    "triple_join_pairs": int(len(m3)),
    "cfo_ni_ta_all_nonnull": int(
        (m3[CFO_COL].notna() & m3[NI_COL].notna() & m3[TA_COL].notna()).sum()
    ),
    "cfo_ni_eq_all_nonnull": int(
        (m3[CFO_COL].notna() & m3[NI_COL].notna() & m3[EQ_COL].notna()).sum()
    ),
}
# accrual wedge sanity: CFO and NI same-sign disagreement rates (no claim, shape only)
both = m3[m3[CFO_COL].notna() & m3[NI_COL].notna()]
wedge = both[CFO_COL] - both[NI_COL]
facts["cross_face"]["accrual_wedge_stats"] = {
    "wedge_positive_rate_cfo_gt_ni": round(float((wedge > 0).mean()), 4),
    "n_wedge_rows": int(len(both)),
}

# ---------------------------------------------------------------- income/balance nonnull
facts["income"] = {
    "ni_nonnull_rate": round(float(inc[NI_COL].notna().mean()), 4),
    "eps_cf_col_present_nonnull_rate": round(float(inc[EPS_CF_COL].notna().mean()), 4)
    if EPS_CF_COL in inc.columns
    else "COL_ABSENT",
}
facts["balance"] = {
    "ta_nonnull_rate": round(float(bal[TA_COL].notna().mean()), 4),
    "equity_nonnull_rate": round(float(bal[EQ_COL].notna().mean()), 4),
}

# ---------------------------------------------------------------- market cap gap recheck
elig_path = "data/fundamental/eligibility.csv"
elig_cols = list(pd.read_csv(elig_path, nrows=0).columns)
mk_cap_like = [c for c in elig_cols if any(t in c.lower() for t in
               ("mkt", "market_cap", "marketcap", "市值", "total_mv", "circ_mv"))]
facts["market_cap_leg"] = {
    "eligibility_columns": elig_cols,
    "market_cap_like_columns": mk_cap_like,
    "verdict": "GAP_CONFIRMED" if not mk_cap_like else "RECHECK_NEEDED",
    "note": "piece-4 needs CFO/mktcap (or CFO/invested-capital variant); invested-capital "
            "variant (CFO/total-assets, CFO/equity) IS buildable from balance face today; "
            "mktcap caliber needs P1 signed collector leg (unsigned ticket domain)",
}

# ---------------------------------------------------------------- verdict
cf_ok = facts["cashflow"]["cfo_nonnull_rate"] >= 0.85 and face_stats["cashflow"]["n_periods"] >= 80
facts["verdict"] = {
    "cfo_leg": "PASS" if cf_ok else "FAIL",
    "invested_capital_variant_buildable": facts["cross_face"]["cfo_ni_ta_all_nonnull"] > 0,
    "mktcap_variant": "BLOCKED_P1_SIGNATURE" if not mk_cap_like else "RECHECK",
    "d6_corr_vs_value_family": "PENDING_TRIO_FINALIZE (ETA 10-05..09 bm-b)",
    "prereg_draftable_now": False,
    "next_action": "wait trio finalize -> D6 corr measured -> piece-4 prereg (excess CFO "
                   "invested-capital caliber first draft candidate); mktcap leg = GM P1 "
                   "signature decision with this facts file as evidence",
}

os.makedirs("results", exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(facts, f, ensure_ascii=False, indent=1)

# ASCII-only console summary (pit-encoding law)
print("face rows:", {k: v["n_rows"] for k, v in face_stats.items()})
print("cashflow periods:", face_stats["cashflow"]["n_periods"],
      face_stats["cashflow"]["period_min"], "->", face_stats["cashflow"]["period_max"])
print("cfo_nonnull_rate:", facts["cashflow"]["cfo_nonnull_rate"],
      "annual:", facts["cashflow"]["annual_cfo_nonnull_rate"])
print("cfo+ni+ta nonnull:", facts["cross_face"]["cfo_ni_ta_all_nonnull"])
print("mktcap cols:", mk_cap_like, "->", facts["market_cap_leg"]["verdict"])
print("VERDICT:", json.dumps(facts["verdict"], ensure_ascii=False))
print("facts ->", OUT)

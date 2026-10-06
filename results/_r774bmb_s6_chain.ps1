# r774 bm-b S6 chain runner (lineage r773 verbatim, zero intentional adds; legs 25-28
#  golden-week no-new-bar block -> honest skip, cutoff 2026-09-30 unchanged, reopen 10-08)
# Log: results\_r774bmb_s6_chain.log
$ErrorActionPreference = "Continue"
$env:PYTHONIOENCODING = "utf-8"
$rcs = @()

function Leg($name) {
    "== LEG $name RC=$LASTEXITCODE =="
    $script:rcs += "$name=$LASTEXITCODE"
}

"== S6 chain start r774 bm-b $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') =="
python scripts\pool_dualrun_reconcile.py run; Leg "01_dualrun"
python scripts\compute_audit.py; Leg "02_compute_audit"
python scripts\py_watermark.py probe; Leg "03_py_watermark"
python scripts\update_daily.py; Leg "04_update_daily"
python scripts\market_regime.py; Leg "05_market_regime"
python scripts\strategy_scorecard.py; Leg "06_scorecard"
python scripts\market_clock_call.py run; Leg "07_clock_call"
python scripts\update_lhb.py; Leg "08_lhb"
python scripts\update_heat.py; Leg "09_heat"
python scripts\update_futures.py; Leg "10_futures"
python scripts\update_repo.py; Leg "11_repo"
python scripts\update_options.py; Leg "12_options"
python scripts\update_moneyflow.py; Leg "13_moneyflow"
python scripts\update_sina_mf.py; Leg "14_sina_mf"
python scripts\update_astock_daily.py; Leg "15_astock_daily"
python scripts\update_etf_daily.py; Leg "16_etf_daily"
python scripts\rev_osc_signal_export.py run; Leg "17_rev_osc"
python scripts\update_minute_feed.py; Leg "18_minute_feed"
python scripts\update_ths_panel.py; Leg "19_ths_panel"
python scripts\ah_panel_puller.py; Leg "20_ah_panel"
python scripts\update_fund_premium.py snapshot; Leg "21_fund_premium"
python scripts\update_fundamental.py; Leg "22_fundamental"
python -m firm.risk.b_layer_filter; Leg "23_b_layer"
python scripts\update_fund_statements.py; Leg "24_fund_statements"
# legs 25-28 (live.paper/t35_open_fill/t24 pair): golden-week no-new-bar block -> honest skip (cutoff 2026-09-30 unchanged)
python scripts\aggressive_lab.py paper; Leg "29_aggr_paper"
python scripts\alloc_paper.py run; Leg "30_alloc_paper"
python scripts\grid_paper.py run; Leg "31_grid_paper"
python scripts\system_v1_paper.py run; Leg "32_system_v1"
python scripts\t35_paper_export.py run; Leg "33_t35_export"
python scripts\daily_scorecard.py; Leg "34_daily_scorecard"
python scripts\daily_report.py run; Leg "35_daily_report"
python scripts\ceo_live_usage.py; Leg "36_ceo_live"
python -m monitor.build_status; Leg "37_build_status"
python scripts\token_meter.py; Leg "38_token_meter"
python scripts\finalize_trio_readiness.py; Leg "39_trio_readiness"

"== S6 SUMMARY =="
$rcs -join " "
"== S6 chain end $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') =="

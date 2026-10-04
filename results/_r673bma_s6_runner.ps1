# r673 bm-a S6 maintenance chain driver (37 legs, literal commands, log-to-file)
$ErrorActionPreference = 'Continue'
$log = 'results\_r673bma_s6_log.txt'
"=== S6 chain r673 bm-a start $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ===" | Out-File $log -Encoding utf8

function Leg($name, $cmd) {
  "=== LEG $name ===" | Out-File $log -Append -Encoding utf8
  $rc = 0
  try { Invoke-Expression $cmd 2>&1 | Out-File $log -Append -Encoding utf8; $rc = $LASTEXITCODE } catch { "EXCEPTION: $_" | Out-File $log -Append -Encoding utf8; $rc = -1 }
  "=== RC $name rc=$rc ===" | Out-File $log -Append -Encoding utf8
}

Leg 'dualrun'      'python scripts\pool_dualrun_reconcile.py run'
Leg 'compute_audit' 'python scripts\compute_audit.py'
Leg 'py_watermark'  'python scripts\py_watermark.py probe'
Leg 'update_daily'  'python scripts\update_daily.py'
Leg 'regime'        'python scripts\market_regime.py'
Leg 'scorecard'     'python scripts\strategy_scorecard.py'
Leg 'clock_call'    'python scripts\market_clock_call.py run'
Leg 'lhb'           'python scripts\update_lhb.py'
Leg 'heat'          'python scripts\update_heat.py'
Leg 'futures'       'python scripts\update_futures.py'
Leg 'repo'          'python scripts\update_repo.py'
Leg 'options'       'python scripts\update_options.py'
Leg 'moneyflow'     'python scripts\update_moneyflow.py'
Leg 'sina_mf'       'python scripts\update_sina_mf.py'
Leg 'astock_daily'  'python scripts\update_astock_daily.py'
Leg 'etf_daily'     'python scripts\update_etf_daily.py'
Leg 'rev_osc'       'python scripts\rev_osc_signal_export.py run'
Leg 'minute_feed'   'python scripts\update_minute_feed.py'
Leg 'ths_panel'     'python scripts\update_ths_panel.py'
Leg 'ah_panel'      'python scripts\ah_panel_puller.py'
Leg 'fund_premium'  'python scripts\update_fund_premium.py snapshot'
Leg 'fundamental'   'python scripts\update_fundamental.py'
Leg 'b_layer'       'python -m firm.risk.b_layer_filter'
Leg 'fund_stmt'     'python scripts\update_fund_statements.py'
Leg 't35_verify'    'python scripts\t35_open_fill_verify.py'
Leg 't24_prospect'  'python scripts\t24_prospect_paper.py run'
Leg 't24_promo'     'python scripts\t24_prospect_promotion.py run'
Leg 'aggr_paper'    'python scripts\aggressive_lab.py paper'
Leg 'alloc_paper'   'python scripts\alloc_paper.py run'
Leg 'grid_paper'    'python scripts\grid_paper.py run'
Leg 'sysv1_paper'   'python scripts\system_v1_paper.py run'
Leg 't35_export'    'python scripts\t35_paper_export.py run'
Leg 'daily_sc'      'python scripts\daily_scorecard.py'
Leg 'daily_report'  'python scripts\daily_report.py run'
Leg 'ceo_usage'     'python scripts\ceo_live_usage.py'
Leg 'build_status'  'python -m monitor.build_status'
Leg 'token_meter'   'python scripts\token_meter.py'
"=== S6 chain end $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ===" | Out-File $log -Append -Encoding utf8

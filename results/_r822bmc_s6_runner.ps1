# S6 chain runner r822 bm-c (in-process, zero-window)
# Each step: exit code + last output line captured. Honest reporting per protocol.
$ErrorActionPreference = 'Continue'
$steps = @(
  @{n='pool_dualrun_reconcile'; c='python scripts\pool_dualrun_reconcile.py run'},
  @{n='compute_audit';           c='python scripts\compute_audit.py'},
  @{n='py_watermark_probe';      c='python scripts\py_watermark.py probe'},
  @{n='update_daily';            c='python scripts\update_daily.py'},
  @{n='market_regime';          c='python scripts\market_regime.py'},
  @{n='strategy_scorecard';     c='python scripts\strategy_scorecard.py'},
  @{n='market_clock_call';      c='python scripts\market_clock_call.py run'},
  @{n='update_lhb';             c='python scripts\update_lhb.py'},
  @{n='update_zt_pool';         c='python scripts\update_zt_pool.py'},
  @{n='update_heat';            c='python scripts\update_heat.py'},
  @{n='update_futures';         c='python scripts\update_futures.py'},
  @{n='update_repo';            c='python scripts\update_repo.py'},
  @{n='update_options';         c='python scripts\update_options.py'},
  @{n='update_moneyflow';       c='python scripts\update_moneyflow.py'},
  @{n='update_sina_mf';         c='python scripts\update_sina_mf.py'},
  @{n='update_astock_daily';    c='python scripts\update_astock_daily.py'},
  @{n='update_etf_daily';       c='python scripts\update_etf_daily.py'},
  @{n='rev_osc_export';         c='python scripts\rev_osc_signal_export.py run'},
  @{n='update_minute_feed';     c='python scripts\update_minute_feed.py'},
  @{n='update_ths_panel';       c='python scripts\update_ths_panel.py'},
  @{n='ah_panel_puller';        c='python scripts\ah_panel_puller.py'},
  @{n='update_fund_premium';    c='python scripts\update_fund_premium.py snapshot'},
  @{n='update_fundamental';     c='python scripts\update_fundamental.py'},
  @{n='b_layer_filter';        c='python -m firm.risk.b_layer_filter'},
  @{n='update_fund_statements'; c='python scripts\update_fund_statements.py'},
  @{n='aggressive_lab_paper';  c='python scripts\aggressive_lab.py paper'},
  @{n='alloc_paper';           c='python scripts\alloc_paper.py run'},
  @{n='grid_paper';            c='python scripts\grid_paper.py run'},
  @{n='system_v1_paper';       c='python scripts\system_v1_paper.py run'},
  @{n='t35_paper_export';      c='python scripts\t35_paper_export.py run'},
  @{n='daily_scorecard';       c='python scripts\daily_scorecard.py'},
  @{n='daily_report';          c='python scripts\daily_report.py run'},
  @{n='ceo_live_usage';        c='python scripts\ceo_live_usage.py'},
  @{n='build_status';          c='python -m monitor.build_status'},
  @{n='token_meter';           c='python scripts\token_meter.py'}
)
foreach ($s in $steps) {
  $out = cmd /c "$($s.c) 2>&1" | Out-String
  $code = $LASTEXITCODE
  $last = ($out -split "`r?`n" | Where-Object { $_ -match '\S' } | Select-Object -Last 1)
  if ($null -eq $last) { $last = '(no output)' }
  if ($last.Length -gt 160) { $last = $last.Substring(0,160) }
  Write-Output ("S6|{0}|exit={1}|{2}" -f $s.n, $code, $last)
}
Write-Output "S6_CHAIN_DONE"

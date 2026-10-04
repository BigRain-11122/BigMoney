# r660 bm-b S6 chain runner (38 legs, r659 template; ASCII-only comments per C-migration law)
$ErrorActionPreference = 'Continue'
$env:PYTHONIOENCODING = 'utf-8'
$log = 'results\_r660bmb_s6_log.txt'
if (Test-Path $log) { Remove-Item $log -Force }
Add-Content -Path $log -Encoding UTF8 -Value "S6 chain r660 bm-b start $(Get-Date -Format o)"
$bad = @()
$legs = @(
  @{ n = 'pool_dualrun_reconcile'; c = 'scripts\pool_dualrun_reconcile.py run' },
  @{ n = 'compute_audit';          c = 'scripts\compute_audit.py' },
  @{ n = 'py_watermark';           c = 'scripts\py_watermark.py probe' },
  @{ n = 'update_daily';           c = 'scripts\update_daily.py' },
  @{ n = 'market_regime';          c = 'scripts\market_regime.py' },
  @{ n = 'strategy_scorecard';     c = 'scripts\strategy_scorecard.py' },
  @{ n = 'market_clock_call';      c = 'scripts\market_clock_call.py run' },
  @{ n = 'update_lhb';             c = 'scripts\update_lhb.py' },
  @{ n = 'update_heat';            c = 'scripts\update_heat.py' },
  @{ n = 'update_futures';         c = 'scripts\update_futures.py' },
  @{ n = 'update_repo';            c = 'scripts\update_repo.py' },
  @{ n = 'update_options';         c = 'scripts\update_options.py' },
  @{ n = 'update_moneyflow';       c = 'scripts\update_moneyflow.py' },
  @{ n = 'update_sina_mf';         c = 'scripts\update_sina_mf.py' },
  @{ n = 'update_astock_daily';    c = 'scripts\update_astock_daily.py' },
  @{ n = 'update_etf_daily';       c = 'scripts\update_etf_daily.py' },
  @{ n = 'rev_osc_signal_export';  c = 'scripts\rev_osc_signal_export.py run' },
  @{ n = 'update_minute_feed';     c = 'scripts\update_minute_feed.py' },
  @{ n = 'update_ths_panel';       c = 'scripts\update_ths_panel.py' },
  @{ n = 'ah_panel_puller';        c = 'scripts\ah_panel_puller.py' },
  @{ n = 'update_fund_premium';    c = 'scripts\update_fund_premium.py snapshot' },
  @{ n = 'update_fundamental';     c = 'scripts\update_fundamental.py' },
  @{ n = 'b_layer_filter';         c = '-m firm.risk.b_layer_filter' },
  @{ n = 'update_fund_statements'; c = 'scripts\update_fund_statements.py' }
)
foreach ($l in $legs) {
  $sw = [System.Diagnostics.Stopwatch]::StartNew()
  cmd /c "python $($l.c) >> `"$log`" 2>&1"
  $rc = $LASTEXITCODE
  $sw.Stop()
  Add-Content -Path $log -Encoding UTF8 -Value ""
  Add-Content -Path $log -Encoding UTF8 -Value "=== $($l.n) rc=$rc $([math]::Round($sw.Elapsed.TotalSeconds,1))s"
  if ($rc -ne 0) { $bad += "$($l.n) rc=$rc" }
}
# bar-triggered legs (idempotent / lane-guarded during golden week)
$env:BIGMONEY_REGIME_GUARD = 'enforce'
$legs2 = @(
  @{ n = 'live_paper';             c = '-m live.paper' },
  @{ n = 't35_open_fill_verify';   c = 'scripts\t35_open_fill_verify.py' },
  @{ n = 't24_prospect_paper';     c = 'scripts\t24_prospect_paper.py run' },
  @{ n = 't24_prospect_promotion'; c = 'scripts\t24_prospect_promotion.py run' },
  @{ n = 'aggressive_lab';         c = 'scripts\aggressive_lab.py paper' },
  @{ n = 'alloc_paper';            c = 'scripts\alloc_paper.py run' },
  @{ n = 'grid_paper';             c = 'scripts\grid_paper.py run' },
  @{ n = 'system_v1_paper';       c = 'scripts\system_v1_paper.py run' },
  @{ n = 't35_paper_export';       c = 'scripts\t35_paper_export.py run' }
)
foreach ($l in $legs2) {
  $sw = [System.Diagnostics.Stopwatch]::StartNew()
  cmd /c "python $($l.c) >> `"$log`" 2>&1"
  $rc = $LASTEXITCODE
  $sw.Stop()
  Add-Content -Path $log -Encoding UTF8 -Value ""
  Add-Content -Path $log -Encoding UTF8 -Value "=== $($l.n) rc=$rc $([math]::Round($sw.Elapsed.TotalSeconds,1))s"
  if ($rc -ne 0) { $bad += "$($l.n) rc=$rc" }
}
$legs3 = @(
  @{ n = 'daily_scorecard';  c = 'scripts\daily_scorecard.py' },
  @{ n = 'daily_report';     c = 'scripts\daily_report.py run' },
  @{ n = 'ceo_live_usage';   c = 'scripts\ceo_live_usage.py' },
  @{ n = 'build_status';     c = '-m monitor.build_status' },
  @{ n = 'token_meter';      c = 'scripts\token_meter.py' }
)
foreach ($l in $legs3) {
  $sw = [System.Diagnostics.Stopwatch]::StartNew()
  cmd /c "python $($l.c) >> `"$log`" 2>&1"
  $rc = $LASTEXITCODE
  $sw.Stop()
  Add-Content -Path $log -Encoding UTF8 -Value ""
  Add-Content -Path $log -Encoding UTF8 -Value "=== $($l.n) rc=$rc $([math]::Round($sw.Elapsed.TotalSeconds,1))s"
  if ($rc -ne 0) { $bad += "$($l.n) rc=$rc" }
}
Add-Content -Path $log -Encoding UTF8 -Value ""
Add-Content -Path $log -Encoding UTF8 -Value "S6 chain end $(Get-Date -Format o) bad=[$($bad -join '; ')]"
Write-Output "S6 DONE bad=[$($bad -join '; ')]"

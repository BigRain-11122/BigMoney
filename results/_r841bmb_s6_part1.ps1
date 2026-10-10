$env:PYTHONIOENCODING = 'utf-8'
$legs = @(
  @('pool_dualrun_reconcile', 'python scripts\pool_dualrun_reconcile.py run'),
  @('compute_audit', 'python scripts\compute_audit.py'),
  @('py_watermark', 'python scripts\py_watermark.py probe'),
  @('update_daily', 'python scripts\update_daily.py'),
  @('market_regime', 'python scripts\market_regime.py'),
  @('strategy_scorecard', 'python scripts\strategy_scorecard.py'),
  @('market_clock_call', 'python scripts\market_clock_call.py run'),
  @('update_lhb', 'python scripts\update_lhb.py'),
  @('update_zt_pool', 'python scripts\update_zt_pool.py'),
  @('update_heat', 'python scripts\update_heat.py'),
  @('update_futures', 'python scripts\update_futures.py'),
  @('update_repo', 'python scripts\update_repo.py'),
  @('update_options', 'python scripts\update_options.py'),
  @('update_moneyflow', 'python scripts\update_moneyflow.py'),
  @('update_sina_mf', 'python scripts\update_sina_mf.py'),
  @('update_etf_daily', 'python scripts\update_etf_daily.py'),
  @('regime_thermo_build', 'python scripts\regime_thermo_build.py'),
  @('regime_gate_dualarm', 'python scripts\regime_gate_dualarm.py run'),
  @('rev_osc_signal_export', 'python scripts\rev_osc_signal_export.py run'),
  @('update_minute_feed', 'python scripts\update_minute_feed.py')
)
foreach ($leg in $legs) {
  $out = Invoke-Expression $leg[1] 2>&1 | Out-String
  $first = ($out -split "`r?`n" | Where-Object { $_.Trim() } | Select-Object -First 1)
  $extra = ($out -split "`r?`n" | Where-Object { $_.Trim() } | Select-Object -First 4) -join ' ~ '
  Write-Output ("LEG {0} | exit={1} | {2}" -f $leg[0], $LASTEXITCODE, $extra)
}

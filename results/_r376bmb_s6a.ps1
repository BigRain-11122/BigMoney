$ErrorActionPreference = 'Continue'
$legs = @(
  @('compute_audit', 'scripts\compute_audit.py'),
  @('py_watermark', 'scripts\py_watermark.py probe'),
  @('update_daily', 'scripts\update_daily.py'),
  @('market_regime', 'scripts\market_regime.py'),
  @('strategy_scorecard', 'scripts\strategy_scorecard.py'),
  @('market_clock_call', 'scripts\market_clock_call.py run'),
  @('update_lhb', 'scripts\update_lhb.py'),
  @('update_heat', 'scripts\update_heat.py'),
  @('update_futures', 'scripts\update_futures.py'),
  @('update_repo', 'scripts\update_repo.py'),
  @('update_options', 'scripts\update_options.py'),
  @('update_moneyflow', 'scripts\update_moneyflow.py'),
  @('update_sina_mf', 'scripts\update_sina_mf.py'),
  @('astock_daily', 'scripts\update_astock_daily.py'),
  @('rev_osc_export', 'scripts\rev_osc_signal_export.py run'),
  @('update_ths_panel', 'scripts\update_ths_panel.py'),
  @('ah_panel_puller', 'scripts\ah_panel_puller.py'),
  @('fund_premium', 'scripts\update_fund_premium.py snapshot'),
  @('fundamental', 'scripts\update_fundamental.py'),
  @('b_layer_filter', '-m firm.risk.b_layer_filter')
)
foreach ($leg in $legs) {
  $name = $leg[0]; $args_ = $leg[1]
  $out = & python $args_ 2>&1
  $rc = $LASTEXITCODE
  $last = ($out | Where-Object { $_ -and "$_".Trim() } | Select-Object -Last 1)
  if ("$last".Length -gt 130) { $last = "$last".Substring(0,130) }
  Write-Output ("LEG {0} rc={1} :: {2}" -f $name, $rc, "$last")
}

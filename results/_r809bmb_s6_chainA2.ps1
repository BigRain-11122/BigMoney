$ErrorActionPreference = 'Continue'
$legs = @(
  @('update_etf_daily',         'python scripts\update_etf_daily.py'),
  @('rev_osc_export',           'python scripts\rev_osc_signal_export.py run'),
  @('update_minute_feed',       'python scripts\update_minute_feed.py'),
  @('update_ths_panel',         'python scripts\update_ths_panel.py'),
  @('ah_panel_puller',          'python scripts\ah_panel_puller.py'),
  @('update_fund_premium',      'python scripts\update_fund_premium.py snapshot'),
  @('update_fundamental',       'python scripts\update_fundamental.py'),
  @('b_layer_filter',           'python -m firm.risk.b_layer_filter'),
  @('update_fund_statements',   'python scripts\update_fund_statements.py')
)
foreach ($leg in $legs) {
  $name = $leg[0]; $cmd = $leg[1]
  $out = cmd /c "$cmd 2>&1"
  $rc = $LASTEXITCODE
  $last = ($out | Select-Object -Last 1)
  Write-Output ("LEG {0} rc={1} last={2}" -f $name, $rc, ($last -replace "`r|`n",''))
  if ($rc -ne 0) { Write-Output ("  DETAIL: {0}" -f (($out | Select-Object -First 6) -join ' | ')) }
}

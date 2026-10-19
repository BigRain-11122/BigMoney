$ErrorActionPreference = 'Continue'
Set-Location 'K:\Fluxgroup\FluxGroup\quant\bigmoney'
$runs = @(
  @('dualrun', 'scripts\pool_dualrun_reconcile.py', 'run'),
  @('audit', 'scripts\compute_audit.py'),
  @('watermark', 'scripts\py_watermark.py', 'probe'),
  @('update_daily', 'scripts\update_daily.py'),
  @('regime', 'scripts\market_regime.py'),
  @('clock', 'scripts\market_clock_call.py', 'run'),
  @('fund_premium', 'scripts\update_fund_premium.py', 'snapshot'),
  @('b_layer', 'firm\risk\b_layer_filter.py'),
  @('daily_report', 'scripts\daily_report.py', 'run'),
  @('token', 'scripts\token_meter.py')
)
foreach ($r in $runs) {
  $name = $r[0]
  $p = $r[1]
  $extra = @()
  if ($r.Count -gt 2) { $extra = $r[2..($r.Count-1)] }
  if ($p -like '*.py') { $out = & python $p @extra 2>&1; $rc = $LASTEXITCODE }
  else { $out = & python -m $p.Replace('\','.').Replace('.py','') 2>&1; $rc = $LASTEXITCODE }
  $tail = ($out | Select-Object -Last 1)
  Write-Output ("{0} rc={1} :: {2}" -f $name, $rc, $tail)
}
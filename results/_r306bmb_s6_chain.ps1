# r306 bm-b S6 maintenance chain (sequential, per-leg rc capture; r293 driver pattern, bm-b path; lineage r305 copy round-face-only)
$ErrorActionPreference = 'Continue'
Set-Location 'C:\Users\Administrator\Desktop\Bigmoney'
$legs = @(
  @{n='compute_audit';       c={python scripts\compute_audit.py}},
  @{n='py_watermark';        c={python scripts\py_watermark.py probe}},
  @{n='update_daily';        c={python scripts\update_daily.py}},
  @{n='market_regime';       c={python scripts\market_regime.py}},
  @{n='strategy_scorecard';  c={python scripts\strategy_scorecard.py}},
  @{n='market_clock_call';   c={python scripts\market_clock_call.py run}},
  @{n='update_lhb';          c={python scripts\update_lhb.py}},
  @{n='update_heat';         c={python scripts\update_heat.py}},
  @{n='update_futures';      c={python scripts\update_futures.py}},
  @{n='update_options';      c={python scripts\update_options.py}},
  @{n='update_moneyflow';    c={python scripts\update_moneyflow.py}},
  @{n='update_sina_mf';      c={python scripts\update_sina_mf.py}},
  @{n='update_astock_daily'; c={python scripts\update_astock_daily.py}},
  @{n='update_ths_panel';    c={python scripts\update_ths_panel.py}},
  @{n='ah_panel_puller';     c={python scripts\ah_panel_puller.py}},
  @{n='update_fund_premium'; c={python scripts\update_fund_premium.py snapshot}},
  @{n='update_fundamental';  c={python scripts\update_fundamental.py}},
  @{n='b_layer_filter';     c={python -m firm.risk.b_layer_filter}},
  @{n='live_paper';          c={python -m live.paper}},
  @{n='t35_open_fill_verify'; c={python scripts\t35_open_fill_verify.py}},
  @{n='t24_prospect_paper';  c={python scripts\t24_prospect_paper.py run}},
  @{n='t24_prospect_promotion'; c={python scripts\t24_prospect_promotion.py run}},
  @{n='aggressive_lab_paper'; c={python scripts\aggressive_lab.py paper}},
  @{n='alloc_paper';         c={python scripts\alloc_paper.py run}},
  @{n='grid_paper';         c={python scripts\grid_paper.py run}},
  @{n='t35_paper_export';    c={python scripts\t35_paper_export.py run}},
  @{n='daily_scorecard';     c={python scripts\daily_scorecard.py}},
  @{n='daily_report';        c={python scripts\daily_report.py run}},
  @{n='build_status';        c={python -m monitor.build_status}},
  @{n='token_meter';         c={python scripts\token_meter.py}}
)
$results = @()
foreach ($leg in $legs) {
  $out = & $leg.c 2>&1
  $rc = $LASTEXITCODE
  $lastLine = ($out | Where-Object {$_ -is [string] -and $_.Trim()} | Select-Object -Last 1)
  if ($null -eq $lastLine) { $lastLine = '' }
  $results += [PSCustomObject]@{leg=$leg.n; rc=$rc; tail=("$lastLine".Substring(0,[Math]::Min(110,"$lastLine".Length)))}
  Write-Output ("{0,-24} rc={1}  {2}" -f $leg.n, $rc, ("$lastLine".Substring(0,[Math]::Min(100,"$lastLine".Length))))
}
$bad = $results | Where-Object { $_.rc -notin @(0) }
Write-Output ("=== S6 chain done: {0}/{1} legs rc=0; NON-ZERO: {2}" -f ($results.Count - $bad.Count), $results.Count, (($bad | ForEach-Object {$_.leg+':'+$_.rc}) -join ', '))

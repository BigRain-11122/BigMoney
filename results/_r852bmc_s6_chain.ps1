# r852 bm-c S6 chain driver (r851 verbatim clone) -- canonical 43-leg table (r838-lineage, post-r842 gate-param fixes included)
$ErrorActionPreference = 'Continue'
$py  = 'C:\Users\Dasheng\AppData\Local\Programs\Python\Python313\python.exe'
$log = 'K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r852bmc_s6_log.txt'
$legs = @(
  @('pool_dualrun_reconcile',   "$py scripts/pool_dualrun_reconcile.py run"),
  @('compute_audit',             "$py scripts/compute_audit.py"),
  @('py_watermark',              "$py scripts/py_watermark.py probe"),
  @('update_daily',              "$py scripts/update_daily.py"),
  @('market_regime',             "$py scripts/market_regime.py"),
  @('strategy_scorecard',        "$py scripts/strategy_scorecard.py"),
  @('market_clock_call',         "$py scripts/market_clock_call.py run"),
  @('update_lhb',                "$py scripts/update_lhb.py"),
  @('update_zt_pool',            "$py scripts/update_zt_pool.py"),
  @('zt_pool_crosscheck',        "$py scripts/zt_pool_crosscheck.py"),
  @('update_heat',               "$py scripts/update_heat.py"),
  @('update_futures',            "$py scripts/update_futures.py"),
  @('update_repo',               "$py scripts/update_repo.py"),
  @('update_options',            "$py scripts/update_options.py"),
  @('update_moneyflow',          "$py scripts/update_moneyflow.py"),
  @('update_sina_mf',            "$py scripts/update_sina_mf.py"),
  @('update_astock_daily',       "$py scripts/update_astock_daily.py"),
  @('update_etf_daily',          "$py scripts/update_etf_daily.py"),
  @('regime_thermo_build',       "$py scripts/regime_thermo_build.py"),
  @('regime_gate_evidence',      "$py scripts/regime_gate_evidence.py run"),
  @('rev_osc_signal_export',     "$py scripts/rev_osc_signal_export.py run"),
  @('update_minute_feed',        "$py scripts/update_minute_feed.py"),
  @('update_ths_panel',          "$py scripts/update_ths_panel.py"),
  @('ah_panel_puller',           "$py scripts/ah_panel_puller.py"),
  @('update_fund_premium',       "$py scripts/update_fund_premium.py snapshot"),
  @('update_fundamental',        "$py scripts/update_fundamental.py"),
  @('b_layer_filter',            "$py -m firm.risk.b_layer_filter"),
  @('update_fund_statements',    "$py scripts/update_fund_statements.py"),
  @('live_paper',                "$py -m live.paper"),
  @('t35_open_fill_verify',      "$py scripts/t35_open_fill_verify.py"),
  @('t24_prospect_paper',        "$py scripts/t24_prospect_paper.py run"),
  @('t24_prospect_promotion',    "$py scripts/t24_prospect_promotion.py run"),
  @('aggressive_lab',            "$py scripts/aggressive_lab.py paper"),
  @('alloc_paper',               "$py scripts/alloc_paper.py run"),
  @('grid_paper',                "$py scripts/grid_paper.py run"),
  @('cta_p1_paper',              "$py scripts/cta_p1_paper.py run"),
  @('system_v1_paper',           "$py scripts/system_v1_paper.py run"),
  @('t35_paper_export',          "$py scripts/t35_paper_export.py run"),
  @('daily_scorecard',           "$py scripts/daily_scorecard.py"),
  @('daily_report',              "$py scripts/daily_report.py run"),
  @('ceo_live_usage',            "$py scripts/ceo_live_usage.py"),
  @('build_status',              "$py -m monitor.build_status"),
  @('token_meter',               "$py scripts/token_meter.py")
)
$start = Get-Date -Format 'yyyy-MM-ddTHH:mm:sszzz'
"r852 bm-c S6 chain run $start legs=$($legs.Count)" | Out-File $log -Encoding utf8
$bad = 0
foreach ($leg in $legs) {
  $name = $leg[0]; $cmd = $leg[1]
  Add-Content $log "`n===== $name ====="
  Add-Content $log "`$ $cmd"
  $out = Invoke-Expression $cmd 2>&1 | Out-String
  $rc = $LASTEXITCODE
  if ($out) { Add-Content $log $out }
  Add-Content $log "`n[rc=$rc]"
  Write-Host "$name rc=$rc"
  if ($rc -ne 0) { $bad++ }
}
$done = Get-Date -Format 'yyyy-MM-ddTHH:mm:sszzz'
Add-Content $log "`nDONE $done bad=$bad"
Write-Host "DONE $done bad=$bad legs=$($legs.Count)"

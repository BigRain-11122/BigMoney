# _r540bmc_s6_chain.ps1 -- S6 data/panel maintenance chain, r540 bm-c.
# Lineage: r539 log face (results\_r539bmc_s6_log.txt 38 legs) mirrored leg-for-leg;
# r531 law: every leg carries scripts\ or -m prefix (zero bare names).
# r521 law: PYTHONIOENCODING=utf-8 set for CJK output through wrapper.
# Output: results\_r540bmc_s6_log.txt ; bad list = any rc != 0 (honest report).
$root = 'K:\Fluxgroup\FluxGroup\quant\bigmoney'
$env:PYTHONIOENCODING = 'utf-8'
$log = Join-Path $root 'results\_r540bmc_s6_log.txt'
$py = (Get-Command python.exe -ErrorAction SilentlyContinue).Source
if (-not $py) { $py = 'C:\Users\Dasheng\AppData\Local\Programs\Python\Python313\python.exe' }
$wrap = Join-Path $root 'Tools\Invoke-SilentExe.ps1'
$legs = @(
  @('pool_dualrun_reconcile', 'scripts\pool_dualrun_reconcile.py run'),
  @('compute_audit',           'scripts\compute_audit.py'),
  @('py_watermark',            'scripts\py_watermark.py probe'),
  @('update_daily',            'scripts\update_daily.py'),
  @('market_regime',           'scripts\market_regime.py'),
  @('strategy_scorecard',      'scripts\strategy_scorecard.py'),
  @('market_clock_call',       'scripts\market_clock_call.py run'),
  @('update_lhb',              'scripts\update_lhb.py'),
  @('update_heat',             'scripts\update_heat.py'),
  @('update_futures',          'scripts\update_futures.py'),
  @('update_repo',             'scripts\update_repo.py'),
  @('update_options',          'scripts\update_options.py'),
  @('update_moneyflow',        'scripts\update_moneyflow.py'),
  @('update_sina_mf',          'scripts\update_sina_mf.py'),
  @('update_astock_daily',     'scripts\update_astock_daily.py'),
  @('update_etf_daily',        'scripts\update_etf_daily.py'),
  @('rev_osc_signal_export',   'scripts\rev_osc_signal_export.py run'),
  @('update_minute_feed',      'scripts\update_minute_feed.py'),
  @('update_ths_panel',        'scripts\update_ths_panel.py'),
  @('ah_panel_puller',         'scripts\ah_panel_puller.py'),
  @('update_fund_premium',     'scripts\update_fund_premium.py snapshot'),
  @('update_fundamental',      'scripts\update_fundamental.py'),
  @('b_layer_filter',           '-m firm.risk.b_layer_filter'),
  @('update_fund_statements',   'scripts\update_fund_statements.py'),
  @('live_paper',              '-m live.paper'),
  @('t35_open_fill_verify',    'scripts\t35_open_fill_verify.py'),
  @('t24_prospect_paper',      'scripts\t24_prospect_paper.py run'),
  @('t24_prospect_promotion',   'scripts\t24_prospect_promotion.py run'),
  @('aggressive_lab',          'scripts\aggressive_lab.py paper'),
  @('alloc_paper',             'scripts\alloc_paper.py run'),
  @('grid_paper',              'scripts\grid_paper.py run'),
  @('system_v1_paper',         'scripts\system_v1_paper.py run'),
  @('t35_paper_export',        'scripts\t35_paper_export.py run'),
  @('daily_scorecard',         'scripts\daily_scorecard.py'),
  @('daily_report',            'scripts\daily_report.py run'),
  @('ceo_live_usage',          'scripts\ceo_live_usage.py'),
  @('build_status',            '-m monitor.build_status'),
  @('token_meter',             'scripts\token_meter.py')
)
$start = Get-Date
"s6chain: start $start legs=$($legs.Count)" | Set-Content -Path $log -Encoding utf8
$bad = @()
foreach ($leg in $legs) {
  $name = $leg[0]; $args_ = $leg[1]
  $t0 = Get-Date
  $out = & $wrap -Exe $py -ArgString $args_ -Cwd $root
  $rc = $LASTEXITCODE
  $dur = [math]::Round(((Get-Date) - $t0).TotalSeconds, 1)
  $hdr = "=== $name rc=$rc ${dur}s"
  Add-Content -Path $log -Value $hdr -Encoding utf8
  if ($out) { Add-Content -Path $log -Value $out -Encoding utf8 }
  Add-Content -Path $log -Value '' -Encoding utf8
  if ($rc -ne 0) { $bad += "$name(rc=$rc)" }
}
$end = Get-Date
$badstr = if ($bad.Count) { $bad -join ',' } else { '[]' }
Add-Content -Path $log -Value "S6 chain end $end bad=[$badstr]" -Encoding utf8
Write-Output "S6_DONE legs=$($legs.Count) bad=[$badstr] elapsed=$([math]::Round(((Get-Date)-$start).TotalSeconds,1))s"

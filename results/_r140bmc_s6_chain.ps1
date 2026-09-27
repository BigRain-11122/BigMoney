# r140 bm-c S6 maintenance chain (r380 lineage; live-family legs gated on new-bar presence per trigger law)
$legs = @(
  @("compute_audit", "python scripts\compute_audit.py"),
  @("wm_probe", "python scripts\py_watermark.py probe"),
  @("update_daily", "python scripts\update_daily.py"),
  @("market_regime", "python scripts\market_regime.py"),
  @("scorecard", "python scripts\strategy_scorecard.py"),
  @("clock_call", "python scripts\market_clock_call.py run"),
  @("update_lhb", "python scripts\update_lhb.py"),
  @("update_heat", "python scripts\update_heat.py"),
  @("update_futures", "python scripts\update_futures.py"),
  @("update_repo", "python scripts\update_repo.py"),
  @("update_options", "python scripts\update_options.py"),
  @("update_moneyflow", "python scripts\update_moneyflow.py"),
  @("update_sina_mf", "python scripts\update_sina_mf.py"),
  @("astock_daily", "python scripts\update_astock_daily.py"),
  @("rev_osc_export", "python scripts\rev_osc_signal_export.py run"),
  @("ths_panel", "python scripts\update_ths_panel.py"),
  @("ah_panel", "python scripts\ah_panel_puller.py"),
  @("fund_premium", "python scripts\update_fund_premium.py snapshot"),
  @("fundamental", "python scripts\update_fundamental.py"),
  @("b_layer", "python -m firm.risk.b_layer_filter")
)
foreach ($leg in $legs) {
  $out = & cmd /c "$($leg[1]) 2>&1" | Out-String
  $rc = $LASTEXITCODE
  $last = ($out -split "`n" | Where-Object { $_.Trim() } | Select-Object -Last 1)
  if ($last -and $last.Length -gt 150) { $last = $last.Substring(0,150) }
  Write-Output ("LEG {0} rc={1} :: {2}" -f $leg[0], $rc, $last)
}
# new-bar gate: live.paper family runs only on rounds with a fresh bar (cutoff == today, post 15:30 publish)
$cutoff = & cmd /c "python -c `"import json;print(json.load(open('results/update_status.json',encoding='utf-8')).get('data_cutoff',''))`" 2>&1" | Out-String
$cutoff = $cutoff.Trim()
$today = (Get-Date -Format 'yyyy-MM-dd')
$newbar = ($cutoff -eq $today)
Write-Output ("NEWBAR_GATE cutoff={0} today={1} newbar={2}" -f $cutoff, $today, $newbar)
if ($newbar) { $env:BIGMONEY_REGIME_GUARD = 'enforce' }
$liveFamily = @(
  @("live_paper", "python -m live.paper"),
  @("t35_verify", "python scripts\t35_open_fill_verify.py"),
  @("t24_paper", "python scripts\t24_prospect_paper.py run"),
  @("t24_promo", "python scripts\t24_prospect_promotion.py run")
)
if ($newbar) {
  foreach ($leg in $liveFamily) {
    $out = & cmd /c "$($leg[1]) 2>&1" | Out-String
    $rc = $LASTEXITCODE
    $last = ($out -split "`n" | Where-Object { $_.Trim() } | Select-Object -Last 1)
    if ($last -and $last.Length -gt 150) { $last = $last.Substring(0,150) }
    Write-Output ("LEG {0} rc={1} :: {2}" -f $leg[0], $rc, $last)
  }
} else {
  foreach ($leg in $liveFamily) {
    Write-Output ("LEG {0} SKIP :: no-new-bar trigger law (cutoff {1})" -f $leg[0], $cutoff)
  }
}
$legs2 = @(
  @("aggr_paper", "python scripts\aggressive_lab.py paper"),
  @("alloc_paper", "python scripts\alloc_paper.py run"),
  @("grid_paper", "python scripts\grid_paper.py run"),
  @("sysv1_paper", "python scripts\system_v1_paper.py run"),
  @("t35_export", "python scripts\t35_paper_export.py run"),
  @("daily_scorecard", "python scripts\daily_scorecard.py"),
  @("daily_report", "python scripts\daily_report.py run"),
  @("build_status", "python -m monitor.build_status"),
  @("token_meter", "python scripts\token_meter.py")
)
foreach ($leg in $legs2) {
  $out = & cmd /c "$($leg[1]) 2>&1" | Out-String
  $rc = $LASTEXITCODE
  $last = ($out -split "`n" | Where-Object { $_.Trim() } | Select-Object -Last 1)
  if ($last -and $last.Length -gt 150) { $last = $last.Substring(0,150) }
  Write-Output ("LEG {0} rc={1} :: {2}" -f $leg[0], $rc, $last)
}

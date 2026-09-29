# _r445bmb_s6_sweep.ps1 -- S6 maintenance chain, bm-b r445
# r444 law: explicit per-leg args arrays (no Split parsing -> no phantom
# first-arg on zero-arg legs). Native python.exe -> $LASTEXITCODE valid.
$env:BIGMONEY_REGIME_GUARD = 'enforce'   # v3 date gate closed on 09-30 -> honest shadow, zero behavior change
$legs = @(
  @('pool_dualrun_reconcile', @('scripts\pool_dualrun_reconcile.py','run')),
  @('compute_audit',          @('scripts\compute_audit.py')),
  @('py_watermark',           @('scripts\py_watermark.py','probe')),
  @('update_daily',           @('scripts\update_daily.py')),
  @('market_regime',          @('scripts\market_regime.py')),
  @('strategy_scorecard',     @('scripts\strategy_scorecard.py')),
  @('market_clock_call',      @('scripts\market_clock_call.py','run')),
  @('update_lhb',             @('scripts\update_lhb.py')),
  @('update_heat',            @('scripts\update_heat.py')),
  @('update_futures',         @('scripts\update_futures.py')),
  @('update_repo',            @('scripts\update_repo.py')),
  @('update_options',         @('scripts\update_options.py')),
  @('update_moneyflow',       @('scripts\update_moneyflow.py')),
  @('update_sina_mf',         @('scripts\update_sina_mf.py')),
  @('update_astock_daily',    @('scripts\update_astock_daily.py')),
  @('update_etf_daily',       @('scripts\update_etf_daily.py')),
  @('rev_osc_signal_export',  @('scripts\rev_osc_signal_export.py','run')),
  @('update_minute_feed',     @('scripts\update_minute_feed.py')),
  @('update_ths_panel',       @('scripts\update_ths_panel.py')),
  @('ah_panel_puller',        @('scripts\ah_panel_puller.py')),
  @('update_fund_premium',    @('scripts\update_fund_premium.py','snapshot')),
  @('update_fundamental',     @('scripts\update_fundamental.py')),
  @('b_layer_filter',         @('-m','firm.risk.b_layer_filter')),
  @('live_paper',             @('-m','live.paper')),
  @('t35_open_fill_verify',   @('scripts\t35_open_fill_verify.py')),
  @('t24_prospect_paper',     @('scripts\t24_prospect_paper.py','run')),
  @('t24_prospect_promotion', @('scripts\t24_prospect_promotion.py','run')),
  @('aggressive_lab',         @('scripts\aggressive_lab.py','paper')),
  @('alloc_paper',            @('scripts\alloc_paper.py','run')),
  @('grid_paper',             @('scripts\grid_paper.py','run')),
  @('system_v1_paper',        @('scripts\system_v1_paper.py','run')),
  @('t35_paper_export',       @('scripts\t35_paper_export.py','run')),
  @('daily_scorecard',        @('scripts\daily_scorecard.py')),
  @('daily_report',           @('scripts\daily_report.py','run')),
  @('ceo_live_usage',         @('scripts\ceo_live_usage.py')),
  @('build_status',           @('-m','monitor.build_status')),
  @('token_meter',            @('scripts\token_meter.py'))
)
$red = @()
foreach ($leg in $legs) {
  $name = $leg[0]
  $out = & python @($leg[1]) 2>&1
  $rc = $LASTEXITCODE
  $tail = ($out | Select-Object -Last 2) -join ' | '
  Write-Output ("LEG {0} rc={1} :: {2}" -f $name, $rc, $tail)
  if ($rc -ne 0) { $red += ("{0} rc={1}" -f $name, $rc) }
}
Write-Output ("=== S6 SWEEP DONE: {0}/{1} green; RED: {2}" -f
  ($legs.Count - $red.Count), $legs.Count, ($red -join '; '))

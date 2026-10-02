# r570 bm-b S6 chain runner (holiday window 2026-10-02, cutoff 2026-09-30)
# r318/r559 laws: per-leg rc capture, log append per leg, array-ized args.
$ErrorActionPreference = 'Continue'
$log = 'results\_r570bmb_s6_chain.log'
Set-Content $log "S6 chain r570 start $(Get-Date -Format 'HH:mm:ss')"
$legs = @(
  @('dualrun',      @('scripts\pool_dualrun_reconcile.py','run')),
  @('audit',        @('scripts\compute_audit.py')),
  @('wm',           @('scripts\py_watermark.py','probe')),
  @('daily',        @('scripts\update_daily.py')),
  @('regime',       @('scripts\market_regime.py')),
  @('scorecard',    @('scripts\strategy_scorecard.py')),
  @('clock',        @('scripts\market_clock_call.py','run')),
  @('lhb',          @('scripts\update_lhb.py')),
  @('heat',         @('scripts\update_heat.py')),
  @('futures',      @('scripts\update_futures.py')),
  @('repo',         @('scripts\update_repo.py')),
  @('options',      @('scripts\update_options.py')),
  @('moneyflow',    @('scripts\update_moneyflow.py')),
  @('sina_mf',      @('scripts\update_sina_mf.py')),
  @('astock',       @('scripts\update_astock_daily.py')),
  @('etf',          @('scripts\update_etf_daily.py')),
  @('rev_osc',      @('scripts\rev_osc_signal_export.py','run')),
  @('minute',       @('scripts\update_minute_feed.py')),
  @('ths',          @('scripts\update_ths_panel.py')),
  @('ah',           @('scripts\ah_panel_puller.py')),
  @('fund_prem',    @('scripts\update_fund_premium.py','snapshot')),
  @('fundamental',  @('scripts\update_fundamental.py')),
  @('b_layer',      @('-m','firm.risk.b_layer_filter')),
  @('t24_promo',    @('scripts\t24_prospect_promotion.py','run')),
  @('aggr',         @('scripts\aggressive_lab.py','paper')),
  @('alloc',        @('scripts\alloc_paper.py','run')),
  @('grid',         @('scripts\grid_paper.py','run')),
  @('sysv1',        @('scripts\system_v1_paper.py','run')),
  @('t35_export',   @('scripts\t35_paper_export.py','run')),
  @('dscore',       @('scripts\daily_scorecard.py')),
  @('dreport',      @('scripts\daily_report.py','run')),
  @('live_usage',   @('scripts\ceo_live_usage.py')),
  @('build_status', @('-m','monitor.build_status')),
  @('token',        @('scripts\token_meter.py'))
)
$fail = 0
foreach ($leg in $legs) {
  $name = $leg[0]
  $out = & python @($leg[1]) 2>&1
  $rc = $LASTEXITCODE
  $tail = ($out | Select-Object -Last 1)
  Add-Content $log "[$name] rc=$rc :: $tail"
  Write-Host "[$name] rc=$rc :: $tail"
  if ($rc -ne 0) { $fail++ }
}
Write-Host "S6_CHAIN_DONE fails=$fail"

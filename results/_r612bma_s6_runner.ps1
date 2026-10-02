$legs = @(
    @('update_daily',        @('scripts\update_daily.py')),
    @('market_regime',       @('scripts\market_regime.py')),
    @('scorecard',           @('scripts\strategy_scorecard.py')),
    @('market_clock',        @('scripts\market_clock_call.py', 'run')),
    @('update_lhb',          @('scripts\update_lhb.py')),
    @('update_heat',         @('scripts\update_heat.py')),
    @('update_futures',      @('scripts\update_futures.py')),
    @('update_repo',         @('scripts\update_repo.py')),
    @('update_options',      @('scripts\update_options.py')),
    @('update_moneyflow',    @('scripts\update_moneyflow.py')),
    @('update_sina_mf',      @('scripts\update_sina_mf.py')),
    @('astock_daily',        @('scripts\update_astock_daily.py')),
    @('etf_daily',           @('scripts\update_etf_daily.py')),
    @('rev_osc_export',      @('scripts\rev_osc_signal_export.py', 'run')),
    @('minute_feed',         @('scripts\update_minute_feed.py')),
    @('ths_panel',           @('scripts\update_ths_panel.py')),
    @('ah_panel',            @('scripts\ah_panel_puller.py')),
    @('fund_premium',        @('scripts\update_fund_premium.py', 'snapshot')),
    @('update_fundamental',  @('scripts\update_fundamental.py')),
    @('b_layer_filter',      @('-m', 'firm.risk.b_layer_filter')),
    @('aggr_paper',          @('scripts\aggressive_lab.py', 'paper')),
    @('alloc_paper',         @('scripts\alloc_paper.py', 'run')),
    @('grid_paper',          @('scripts\grid_paper.py', 'run')),
    @('system_v1_paper',     @('scripts\system_v1_paper.py', 'run')),
    @('t35_export',          @('scripts\t35_paper_export.py', 'run')),
    @('daily_scorecard',     @('scripts\daily_scorecard.py')),
    @('daily_report',        @('scripts\daily_report.py', 'run')),
    @('ceo_live_usage',      @('scripts\ceo_live_usage.py')),
    @('build_status',        @('-m', 'monitor.build_status')),
    @('token_meter',         @('scripts\token_meter.py'))
)
$fails = @()
foreach ($leg in $legs) {
    $name = $leg[0]
    $a = [string[]]@($leg[1])
    & python @a *> $null
    $rc = $LASTEXITCODE
    if ($rc -ne 0) { $fails += ("{0}={1}" -f $name, $rc) }
    Write-Host ("LEG {0} rc={1}" -f $name, $rc)
}
if ($fails.Count -gt 0) { Write-Output ("FAILS: " + ($fails -join ' ')) } else { Write-Output 'ALL-LEGS-RC0' }

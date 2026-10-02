$ErrorActionPreference = "Continue"
$log = "results\_r605bma_s6_log.txt"
"=== r604 bm-a S6 chain $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ===" | Out-File $log -Append -Encoding utf8
function Leg($name, $argv) {
    $t0 = Get-Date
    & python @argv >> $log 2>&1
    $rc = $LASTEXITCODE
    $dt = [int]((Get-Date) - $t0).TotalSeconds
    $line = "[LEG] $name rc=$rc ${dt}s"
    Write-Host $line
    $line | Out-File $log -Append -Encoding utf8
    return $rc
}
Leg "pool_dualrun_reconcile" @("scripts\pool_dualrun_reconcile.py", "run") | Out-Null
Leg "compute_audit"           @("scripts\compute_audit.py") | Out-Null
Leg "py_watermark"            @("scripts\py_watermark.py", "probe") | Out-Null
Leg "update_daily"            @("scripts\update_daily.py") | Out-Null
Leg "market_regime"           @("scripts\market_regime.py") | Out-Null
Leg "strategy_scorecard"      @("scripts\strategy_scorecard.py") | Out-Null
Leg "market_clock_call"       @("scripts\market_clock_call.py", "run") | Out-Null
Leg "update_lhb"              @("scripts\update_lhb.py") | Out-Null
Leg "update_heat"             @("scripts\update_heat.py") | Out-Null
Leg "update_futures"          @("scripts\update_futures.py") | Out-Null
Leg "update_repo"             @("scripts\update_repo.py") | Out-Null
Leg "update_options"          @("scripts\update_options.py") | Out-Null
Leg "update_moneyflow"        @("scripts\update_moneyflow.py") | Out-Null
Leg "update_sina_mf"          @("scripts\update_sina_mf.py") | Out-Null
Leg "update_astock_daily"     @("scripts\update_astock_daily.py") | Out-Null
Leg "update_etf_daily"        @("scripts\update_etf_daily.py") | Out-Null
Leg "rev_osc_signal_export"   @("scripts\rev_osc_signal_export.py", "run") | Out-Null
Leg "update_minute_feed"      @("scripts\update_minute_feed.py") | Out-Null
Leg "update_ths_panel"       @("scripts\update_ths_panel.py") | Out-Null
Leg "ah_panel_puller"         @("scripts\ah_panel_puller.py") | Out-Null
Leg "update_fund_premium"     @("scripts\update_fund_premium.py", "snapshot") | Out-Null
Leg "update_fundamental"      @("scripts\update_fundamental.py") | Out-Null
Leg "b_layer_filter"          @("-m", "firm.risk.b_layer_filter") | Out-Null
Leg "aggressive_lab"          @("scripts\aggressive_lab.py", "paper") | Out-Null
Leg "alloc_paper"             @("scripts\alloc_paper.py", "run") | Out-Null
Leg "grid_paper"              @("scripts\grid_paper.py", "run") | Out-Null
Leg "system_v1_paper"         @("scripts\system_v1_paper.py", "run") | Out-Null
Leg "t35_paper_export"        @("scripts\t35_paper_export.py", "run") | Out-Null
Leg "daily_scorecard"         @("scripts\daily_scorecard.py") | Out-Null
Leg "daily_report"            @("scripts\daily_report.py", "run") | Out-Null
Leg "ceo_live_usage"          @("scripts\ceo_live_usage.py") | Out-Null
Leg "build_status"            @("-m", "monitor.build_status") | Out-Null
Leg "token_meter"             @("scripts\token_meter.py") | Out-Null
Write-Host "=== S6 chain done, log: $log ==="


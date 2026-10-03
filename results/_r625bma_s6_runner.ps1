$ErrorActionPreference = "Continue"
$log = "C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney\results\_r625bma_s6.log"
"=== r625 bm-a S6 chain start $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ===" | Add-Content $log

function Leg {
    param([string]$Name, [string[]]$ArgList)
    $t0 = Get-Date
    & python @ArgList 2>&1 | ForEach-Object { "$Name | $_" | Add-Content $log }
    $rc = $LASTEXITCODE
    $dt = [math]::Round(((Get-Date) - $t0).TotalSeconds, 1)
    "[$Name] rc=$rc ${dt}s" | Add-Content $log
    Write-Host "[$Name] rc=$rc ${dt}s"
}

Leg "dualrun"      @("scripts\pool_dualrun_reconcile.py", "run")
Leg "audit"         @("scripts\compute_audit.py")
Leg "daily"         @("scripts\update_daily.py")
Leg "regime"        @("scripts\market_regime.py")
Leg "scorecard"     @("scripts\strategy_scorecard.py")
Leg "clock-call"    @("scripts\market_clock_call.py", "run")
Leg "lhb"           @("scripts\update_lhb.py")
Leg "heat"          @("scripts\update_heat.py")
Leg "futures"       @("scripts\update_futures.py")
Leg "repo"          @("scripts\update_repo.py")
Leg "options"       @("scripts\update_options.py")
Leg "moneyflow"     @("scripts\update_moneyflow.py")
Leg "sina-mf"       @("scripts\update_sina_mf.py")
Leg "astock-daily"  @("scripts\update_astock_daily.py")
Leg "etf-daily"     @("scripts\update_etf_daily.py")
Leg "rev-osc-exp"   @("scripts\rev_osc_signal_export.py", "run")
Leg "minute-feed"   @("scripts\update_minute_feed.py")
Leg "ths-panel"     @("scripts\update_ths_panel.py")
Leg "ah-panel"      @("scripts\ah_panel_puller.py")
Leg "fund-prem"     @("scripts\update_fund_premium.py", "snapshot")
Leg "fundamental"   @("scripts\update_fundamental.py")
Leg "b-layer"       @("-m", "firm.risk.b_layer_filter")
$env:BIGMONEY_REGIME_GUARD = 'enforce'
Leg "live-paper"    @("-m", "live.paper")
Remove-Item Env:BIGMONEY_REGIME_GUARD -ErrorAction SilentlyContinue
Leg "t35-openfill"  @("scripts\t35_open_fill_verify.py")
Leg "prospect"      @("scripts\t24_prospect_paper.py", "run")
Leg "prospect-prom" @("scripts\t24_prospect_promotion.py", "run")
Leg "aggr-paper"    @("scripts\aggressive_lab.py", "paper")
Leg "alloc-paper"   @("scripts\alloc_paper.py", "run")
Leg "grid-paper"    @("scripts\grid_paper.py", "run")
Leg "sysv1-paper"   @("scripts\system_v1_paper.py", "run")
Leg "t35-export"    @("scripts\t35_paper_export.py", "run")
Leg "daily-score"   @("scripts\daily_scorecard.py")
Leg "daily-report"  @("scripts\daily_report.py", "run")
Leg "live-usage"    @("scripts\ceo_live_usage.py")
Leg "build-status"   @("-m", "monitor.build_status")
Leg "token-meter"   @("scripts\token_meter.py")
"=== r625 bm-a S6 chain end $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ===" | Add-Content $log


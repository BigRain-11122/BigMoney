$ErrorActionPreference = 'Continue'
$log = 'results\_r487bmb_s6_log.txt'
"=== r487 bm-b S6 chain start $(Get-Date -Format 'HH:mm:ss') ===" | Out-File $log -Encoding utf8

function Run-Leg {
    param($name, $cmd, $timeoutSec = 300)
    $t = Get-Date
    try {
        $p = Start-Process -FilePath 'python' -ArgumentList $cmd -NoNewWindow -PassThru -RedirectStandardOutput "$env:TEMP\s6_out.txt" -RedirectStandardError "$env:TEMP\s6_err.txt"
        if (-not $p.WaitForExit($timeoutSec * 1000)) { $p.Kill(); "$name rc=TIMEOUT(${timeoutSec}s)" | Out-File $log -Append -Encoding utf8; return }
        $out = (Get-Content "$env:TEMP\s6_out.txt" -Tail 1 -ErrorAction SilentlyContinue)
        "$name rc=$($p.ExitCode) | $out" | Out-File $log -Append -Encoding utf8
    } catch { "$name rc=EXC $($_.Exception.Message)" | Out-File $log -Append -Encoding utf8 }
}

# 1 dualrun reconcile FIRST (evidence before settle)
Run-Leg 'dualrun' @('scripts\pool_dualrun_reconcile.py', 'run') 120
Run-Leg 'compute_audit' @('scripts\compute_audit.py') 180
Run-Leg 'py_watermark' @('scripts\py_watermark.py', 'probe') 120
Run-Leg 'update_daily' @('scripts\update_daily.py') 300
Run-Leg 'market_regime' @('scripts\market_regime.py') 120
Run-Leg 'strategy_scorecard' @('scripts\strategy_scorecard.py') 180
Run-Leg 'market_clock_call' @('scripts\market_clock_call.py', 'run') 120
Run-Leg 'update_lhb' @('scripts\update_lhb.py') 180
Run-Leg 'update_heat' @('scripts\update_heat.py') 120
Run-Leg 'update_futures' @('scripts\update_futures.py') 120
Run-Leg 'update_repo' @('scripts\update_repo.py') 120
Run-Leg 'update_options' @('scripts\update_options.py') 120
Run-Leg 'update_moneyflow' @('scripts\update_moneyflow.py') 120
Run-Leg 'update_sina_mf' @('scripts\update_sina_mf.py') 120
Run-Leg 'update_astock_daily' @('scripts\update_astock_daily.py') 120
Run-Leg 'update_etf_daily' @('scripts\update_etf_daily.py') 180
Run-Leg 'rev_osc_signal_export' @('scripts\rev_osc_signal_export.py', 'run') 120
Run-Leg 'update_minute_feed' @('scripts\update_minute_feed.py') 120
Run-Leg 'update_ths_panel' @('scripts\update_ths_panel.py') 120
Run-Leg 'ah_panel_puller' @('scripts\ah_panel_puller.py') 120
Run-Leg 'update_fund_premium' @('scripts\update_fund_premium.py', 'snapshot') 120
Run-Leg 'update_fundamental' @('scripts\update_fundamental.py') 180
Run-Leg 'b_layer_filter' @('-m', 'firm.risk.b_layer_filter') 120

# paper lane legs: REGIME_GUARD v3 enforce env (date gate open 2026-10-01, approval file in place)
$env:BIGMONEY_REGIME_GUARD = 'enforce'
Run-Leg 'live.paper' @('-m', 'live.paper') 600
Run-Leg 't35_open_fill_verify' @('scripts\t35_open_fill_verify.py') 120
Run-Leg 't24_prospect_paper' @('scripts\t24_prospect_paper.py', 'run') 300
Run-Leg 't24_prospect_promotion' @('scripts\t24_prospect_promotion.py', 'run') 180
Run-Leg 'aggressive_lab' @('scripts\aggressive_lab.py', 'paper') 300
Run-Leg 'alloc_paper' @('scripts\alloc_paper.py', 'run') 300
Run-Leg 'grid_paper' @('scripts\grid_paper.py', 'run') 300
Run-Leg 'system_v1_paper' @('scripts\system_v1_paper.py', 'run') 300
Run-Leg 't35_paper_export' @('scripts\t35_paper_export.py', 'run') 180
Remove-Item Env:BIGMONEY_REGIME_GUARD -ErrorAction SilentlyContinue

Run-Leg 'daily_scorecard' @('scripts\daily_scorecard.py') 180
Run-Leg 'daily_report' @('scripts\daily_report.py', 'run') 180
Run-Leg 'ceo_live_usage' @('scripts\ceo_live_usage.py') 180
Run-Leg 'monitor_build_status' @('-m', 'monitor.build_status') 180
Run-Leg 'token_meter' @('scripts\token_meter.py') 120

"=== S6 chain end $(Get-Date -Format 'HH:mm:ss') ===" | Out-File $log -Append -Encoding utf8
Write-Output "--- log tail ---"
Get-Content $log | Where-Object { $_ -notmatch 'rc=0 \| *$' } | Select-Object -First 45

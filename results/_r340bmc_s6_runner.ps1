# r336 bm-c S6 chain runner (34 legs, batched single shell invocation; r495 pattern).
# All native exes via Invoke-SilentExe wrapper (zero desktop flash law).
$w = "K:\Fluxgroup\FluxGroup\quant\bigmoney\Tools\Invoke-SilentExe.ps1"
$py = "C:\Users\Dasheng\AppData\Local\Programs\Python\Python313\python.exe"
Set-Location "K:\Fluxgroup\FluxGroup\quant\bigmoney"
$legs = @(
    @{n='dualrun_reconcile'; a='scripts\pool_dualrun_reconcile.py run'},
    @{n='compute_audit';    a='scripts\compute_audit.py'},
    @{n='py_watermark';     a='scripts\py_watermark.py probe'},
    @{n='update_daily';      a='scripts\update_daily.py'},
    @{n='market_regime';     a='scripts\market_regime.py'},
    @{n='strategy_scorecard';a='scripts\strategy_scorecard.py'},
    @{n='market_clock_call';a='scripts\market_clock_call.py run'},
    @{n='update_lhb';        a='scripts\update_lhb.py'},
    @{n='update_heat';       a='scripts\update_heat.py'},
    @{n='update_futures';    a='scripts\update_futures.py'},
    @{n='update_repo';       a='scripts\update_repo.py'},
    @{n='update_options';    a='scripts\update_options.py'},
    @{n='update_moneyflow';  a='scripts\update_moneyflow.py'},
    @{n='update_sina_mf';    a='scripts\update_sina_mf.py'},
    @{n='update_astock_daily';a='scripts\update_astock_daily.py'},
    @{n='update_etf_daily';  a='scripts\update_etf_daily.py'},
    @{n='rev_osc_export';    a='scripts\rev_osc_signal_export.py run'},
    @{n='update_minute_feed';a='scripts\update_minute_feed.py'},
    @{n='update_ths_panel';  a='scripts\update_ths_panel.py'},
    @{n='ah_panel_puller';   a='scripts\ah_panel_puller.py'},
    @{n='fund_premium';      a='scripts\update_fund_premium.py snapshot'},
    @{n='update_fundamental';a='scripts\update_fundamental.py'},
    @{n='b_layer_filter';    a='-m firm.risk.b_layer_filter'},
    @{n='aggressive_lab';    a='scripts\aggressive_lab.py paper'},
    @{n='alloc_paper';      a='scripts\alloc_paper.py run'},
    @{n='grid_paper';       a='scripts\grid_paper.py run'},
    @{n='system_v1_paper';  a='scripts\system_v1_paper.py run'},
    @{n='t35_paper_export';  a='scripts\t35_paper_export.py run'},
    @{n='daily_scorecard';   a='scripts\daily_scorecard.py'},
    @{n='daily_report';      a='scripts\daily_report.py run'},
    @{n='ceo_live_usage';    a='scripts\ceo_live_usage.py'},
    @{n='build_status';      a='-m monitor.build_status'},
    @{n='token_meter';       a='scripts\token_meter.py'},
    @{n='attrition_guard';   a='scripts\attrition_ledger_guard.py scan'}
)
$nonzero = @()
foreach ($leg in $legs) {
    $out = & $w -Exe $py -ArgString $leg.a -Cwd "K:\Fluxgroup\FluxGroup\quant\bigmoney"
    $rc = $LASTEXITCODE
    $lines = @($out -split '\r?\n' | Where-Object { $_.Trim() -ne '' })
    $tail = if ($lines.Count -gt 0) { $lines[-1] } else { '' }
    if ($tail.Length -gt 130) { $tail = $tail.Substring(0, 130) }
    Write-Output ("LEG|" + $leg.n + "|RC=" + $rc + "|" + $tail)
    if ($rc -ne 0) {
        $nonzero += $leg.n
        $lines | Select-Object -Last 4 | ForEach-Object { Write-Output ("  NZ|" + $leg.n + "|" + $_) }
    }
}
Write-Output ("CHAIN_DONE non_zero_legs=" + $nonzero.Count + " [" + ($nonzero -join ',') + "]")

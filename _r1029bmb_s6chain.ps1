# r1029 bm-b S6 chain driver (ASCII only per iteration_loop.ps1 encoding law).
# 17:0x evening-pre window: 10-19 bar NOT landed (sh510300 tail=2026-10-16) ->
# live.paper family honestly skipped 4th round (sina daily evening-lag window
# ~20:4x-21:xx per r286/r941/r1035/r1026 precedents); conditional retry wired.
# smoke_test + orphan_probe already run pre-chain this round (49/49 PASS,
# 0/7 orphans) - not re-run. idle_worked step intentionally OMITTED: no
# claimable product work this round (board/pool/queues all empty, night
# stations not in window) -> honest starvation face per O-20261007-2315
# semantics; --worked would mask the real supply-line signal.
$ErrorActionPreference = 'Continue'
Set-Location C:\Fluxgroup\FluxGroup\quant\bigmoney
$log = 'results\_r1029bmb_s6_log.txt'
$start = Get-Date
"chain start $(Get-Date -Format HH:mm:ss) (r1029)" | Add-Content $log -Encoding UTF8
function Step([string]$name, [string[]]$argv) {
    $el = ((Get-Date) - $start).TotalMinutes
    if ($el -gt 18.0) {
        $l = "BUDGET-CUT-SKIP $name at $([math]::Round($el,1))min"
        Add-Content $log $l -Encoding UTF8
        Write-Output $l
        return
    }
    $out = & python @argv 2>&1
    $rc = $LASTEXITCODE
    $oline = ''
    foreach ($o in $out) { $s = "$o"; if ($s.Trim()) { $oline = $s.Trim(); break } }
    $line = "rc=$rc $name :: $oline"
    Add-Content $log $line -Encoding UTF8
    Write-Output $line
    return $rc
}
Write-Output "chain start $(Get-Date -Format HH:mm:ss)"
$satRc = Step 'sat_engine_status' @('scripts\saturation_engine.py','status')
if ($satRc -eq 1) {
    Write-Output 'SAT_ENGINE_DEAD -> reregister + tick (S3 P0 repair)'
    & Tools\register_satengine_task.ps1
    Step 'sat_engine_tick_after_repair' @('scripts\saturation_engine.py','tick')
}
Step 'pool_dualrun'        @('scripts\pool_dualrun_reconcile.py','run')
Step 'compute_audit'      @('scripts\compute_audit.py')
Step 'py_watermark'        @('scripts\py_watermark.py','probe')
Step 'd19_probe'          @('results\_r686bmb_d19_check.py')
Step 'd19_advance'         @('scripts\d19_watermark.py','update','--advance')
Step 'update_daily'        @('scripts\update_daily.py')
Step 'market_regime'       @('scripts\market_regime.py')
Step 'strategy_scorecard'  @('scripts\strategy_scorecard.py')
Step 'market_clock_call'   @('scripts\market_clock_call.py','run')
Step 'update_lhb'           @('scripts\update_lhb.py')
Step 'update_zt_pool'       @('scripts\update_zt_pool.py')
Step 'update_heat'          @('scripts\update_heat.py')
Step 'update_futures'       @('scripts\update_futures.py')
Step 'update_repo_panel'    @('scripts\update_repo.py')
Step 'update_options'       @('scripts\update_options.py')
Step 'update_moneyflow'     @('scripts\update_moneyflow.py')
Step 'update_sina_mf'      @('scripts\update_sina_mf.py')
Step 'update_astock_daily'  @('scripts\update_astock_daily.py')
Step 'update_etf_daily'     @('scripts\update_etf_daily.py')
Step 'regime_thermo'        @('scripts\regime_thermo_build.py')
Step 'regime_gate_dualarm'  @('scripts\regime_gate_dualarm.py','run')
Step 'rev_osc_signal'       @('scripts\rev_osc_signal_export.py','run')
Step 'update_minute_feed'   @('scripts\update_minute_feed.py')
Step 'update_ths_panel'     @('scripts\update_ths_panel.py')
Step 'ah_panel_puller'      @('scripts\ah_panel_puller.py')
Step 'update_fund_premium'  @('scripts\update_fund_premium.py','snapshot')
Step 'update_fundamental'   @('scripts\update_fundamental.py')
Step 'b_layer_filter'       @('-m','firm.risk.b_layer_filter')
Step 'update_fund_statements' @('scripts\update_fund_statements.py')
"SKIP live.paper (r1029 17:0x: 10-19 bar not landed, cutoff 10-16, evening window ~20:4x)" | Add-Content $log -Encoding UTF8
"SKIP t35_open_fill_verify (no new bar)" | Add-Content $log -Encoding UTF8
"SKIP t24_prospect_paper (no new bar)" | Add-Content $log -Encoding UTF8
"SKIP t24_prospect_promotion (no new bar)" | Add-Content $log -Encoding UTF8
Write-Output 'SKIP x4 live.paper family (10-19 bar not landed - honest skip r1026 precedent)'
Step 'aggressive_lab'      @('scripts\aggressive_lab.py','paper')
Step 'alloc_paper'         @('scripts\alloc_paper.py','run')
Step 'grid_paper'          @('scripts\grid_paper.py','run')
Step 'system_v1_paper'     @('scripts\system_v1_paper.py','run')
Step 't35_paper_export'    @('scripts\t35_paper_export.py','run')
Step 'daily_scorecard'     @('scripts\daily_scorecard.py')
Step 'daily_report'        @('scripts\daily_report.py','run')
Step 'ceo_live_usage'      @('scripts\ceo_live_usage.py')
Step 'build_status'        @('-m','monitor.build_status')
Step 'token_meter'         @('scripts\token_meter.py')
Step 'attrition_scan'      @('scripts\attrition_ledger_guard.py','scan')
Write-Output "chain end $(Get-Date -Format HH:mm:ss) elapsed=$([math]::Round(((Get-Date) - $start).TotalMinutes,1))min"
"chain end $(Get-Date -Format HH:mm:ss) elapsed=$([math]::Round(((Get-Date) - $start).TotalMinutes,1))min" | Add-Content $log -Encoding UTF8

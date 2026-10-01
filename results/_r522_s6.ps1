# r522 S6 chain -- bm-a lane (protocol order: dualrun BEFORE compute_audit).
# Each leg: combined output -> logs\s6_r522\<leg>.log; print leg + rc; on
# unexpected rc print tail. Expected rc sets per protocol exit contracts.
$ErrorActionPreference = 'Continue'
$logdir = 'logs\s6_r522'
New-Item -ItemType Directory -Force -Path $logdir | Out-Null

$legs = @(
    @{n='dualrun';      c='python scripts\pool_dualrun_reconcile.py run'; ok=@(0,2)},
    @{n='compute_audit';c='python scripts\compute_audit.py'; ok=@(0)},
    @{n='watermark';    c='python scripts\py_watermark.py probe'; ok=@(0,2)},
    @{n='update_daily'; c='python scripts\update_daily.py'; ok=@(0,1)},
    @{n='regime';      c='python scripts\market_regime.py'; ok=@(0,2)},
    @{n='strat_scorecard'; c='python scripts\strategy_scorecard.py'; ok=@(0)},
    @{n='market_clock'; c='python scripts\market_clock_call.py run'; ok=@(0,2)},
    @{n='lhb';         c='python scripts\update_lhb.py'; ok=@(0,2,3)},
    @{n='heat';        c='python scripts\update_heat.py'; ok=@(0,2)},
    @{n='futures';     c='python scripts\update_futures.py'; ok=@(0,2,3)},
    @{n='repo';        c='python scripts\update_repo.py'; ok=@(0,2,3)},
    @{n='options';     c='python scripts\update_options.py'; ok=@(0,2)},
    @{n='moneyflow';   c='python scripts\update_moneyflow.py'; ok=@(0,2)},
    @{n='sina_mf';     c='python scripts\update_sina_mf.py'; ok=@(0,2)},
    @{n='astock';      c='python scripts\update_astock_daily.py'; ok=@(0,2)},
    @{n='etf_daily';   c='python scripts\update_etf_daily.py'; ok=@(0,2,3)},
    @{n='rev_osc_exp'; c='python scripts\rev_osc_signal_export.py run'; ok=@(0,2)},
    @{n='minute_feed'; c='python scripts\update_minute_feed.py'; ok=@(0,2,3)},
    @{n='ths_panel';   c='python scripts\update_ths_panel.py'; ok=@(0,2,3)},
    @{n='ah_panel';    c='python scripts\ah_panel_puller.py'; ok=@(0,2)},
    @{n='fund_prem';   c='python scripts\update_fund_premium.py snapshot'; ok=@(0,2)},
    @{n='fundamental'; c='python scripts\update_fundamental.py'; ok=@(0,2)},
    @{n='b_layer';     c='python -m firm.risk.b_layer_filter'; ok=@(0)},
    @{n='live_paper';  c="`$env:BIGMONEY_REGIME_GUARD='enforce'; python -m live.paper"; ok=@(0)},
    @{n='t35_verify';  c='python scripts\t35_open_fill_verify.py'; ok=@(0,1,2)},
    @{n='prospect_paper'; c='python scripts\t24_prospect_paper.py run'; ok=@(0,2)},
    @{n='prospect_promo'; c='python scripts\t24_prospect_promotion.py run'; ok=@(0,2)},
    @{n='aggr_paper';  c='python scripts\aggressive_lab.py paper'; ok=@(0,2)},
    @{n='alloc_paper'; c='python scripts\alloc_paper.py run'; ok=@(0,2)},
    @{n='grid_paper'; c='python scripts\grid_paper.py run'; ok=@(0,2)},
    @{n='sysv1_paper'; c='python scripts\system_v1_paper.py run'; ok=@(0,2)},
    @{n='t35_export'; c='python scripts\t35_paper_export.py run'; ok=@(0,2)},
    @{n='daily_score'; c='python scripts\daily_scorecard.py'; ok=@(0)},
    @{n='daily_report'; c='python scripts\daily_report.py run'; ok=@(0,2)},
    @{n='ceo_usage';  c='python scripts\ceo_live_usage.py'; ok=@(0,2)},
    @{n='build_status'; c='python -m monitor.build_status'; ok=@(0)},
    @{n='token_meter'; c='python scripts\token_meter.py'; ok=@(0)}
)

$fail = @()
foreach ($leg in $legs) {
    $log = Join-Path $logdir ($leg.n + '.log')
    cmd /c $leg.c *> $log
    $rc = $LASTEXITCODE
    $mark = if ($leg.ok -contains $rc) { 'OK' } else { 'UNEXPECTED'; $fail += $leg.n }
    Write-Host ("{0,-16} rc={1} {2}" -f $leg.n, $rc, $mark)
    if ($mark -eq 'UNEXPECTED') { Get-Content $log -Tail 6 | Write-Host }
}
Write-Host "=== S6 chain done: $($legs.Count) legs, $($fail.Count) unexpected ==="
if ($fail.Count) { Write-Host ("FAIL LEGS: " + ($fail -join ', ')) }

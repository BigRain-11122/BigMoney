# r290 bm-c S6 chain runner (in-process, zero new console)
$legs = @(
    @{n='dualrun';    c={python scripts\pool_dualrun_reconcile.py run}},
    @{n='compute_audit'; c={python scripts\compute_audit.py}},
    @{n='py_watermark'; c={python scripts\py_watermark.py probe}},
    @{n='update_daily'; c={python scripts\update_daily.py}},
    @{n='market_regime'; c={python scripts\market_regime.py}},
    @{n='scorecard';   c={python scripts\strategy_scorecard.py}},
    @{n='clock_call';  c={python scripts\market_clock_call.py run}},
    @{n='update_lhb';  c={python scripts\update_lhb.py}},
    @{n='update_heat'; c={python scripts\update_heat.py}},
    @{n='futures';     c={python scripts\update_futures.py}},
    @{n='repo';        c={python scripts\update_repo.py}},
    @{n='options';     c={python scripts\update_options.py}},
    @{n='moneyflow';   c={python scripts\update_moneyflow.py}},
    @{n='sina_mf';     c={python scripts\update_sina_mf.py}},
    @{n='astock';      c={python scripts\update_astock_daily.py}},
    @{n='etf_daily';   c={python scripts\update_etf_daily.py}},
    @{n='rev_osc';     c={python scripts\rev_osc_signal_export.py run}},
    @{n='minute_feed'; c={python scripts\update_minute_feed.py}},
    @{n='ths_panel';   c={python scripts\update_ths_panel.py}},
    @{n='ah_panel';   c={python scripts\ah_panel_puller.py}},
    @{n='fund_prem';   c={python scripts\update_fund_premium.py snapshot}},
    @{n='fundamental'; c={python scripts\update_fundamental.py}},
    @{n='b_layer';     c={python -m firm.risk.b_layer_filter}},
    @{n='live_paper';  c={if ($env:BIGMONEY_REGIME_GUARD -eq 'enforce') { python -m live.paper } else { Write-Host 'live_paper: no new bar trigger -> skip per chain condition' } }},
    @{n='t35_verify';  c={python scripts\t35_open_fill_verify.py}},
    @{n='t24_paper';   c={python scripts\t24_prospect_paper.py run}},
    @{n='t24_promo';   c={python scripts\t24_prospect_promotion.py run}},
    @{n='aggr_paper';  c={python scripts\aggressive_lab.py paper}},
    @{n='alloc_paper'; c={python scripts\alloc_paper.py run}},
    @{n='grid_paper';  c={python scripts\grid_paper.py run}},
    @{n='sysv1_paper'; c={python scripts\system_v1_paper.py run}},
    @{n='t35_export';  c={python scripts\t35_paper_export.py run}},
    @{n='daily_score'; c={python scripts\daily_scorecard.py}},
    @{n='daily_report';c={python scripts\daily_report.py run}},
    @{n='ceo_live';   c={python scripts\ceo_live_usage.py}},
    @{n='build_status';c={python -m monitor.build_status}},
    @{n='token_meter'; c={python scripts\token_meter.py}}
)
$bad = @()
foreach ($leg in $legs) {
    $out = & $leg.c 2>&1
    $rc = $LASTEXITCODE
    if ($null -eq $rc) { $rc = 0 }
    $tail = ($out | Select-Object -Last 1)
    if ($tail -and $tail.ToString().Length -gt 130) { $tail = $tail.ToString().Substring(0,130) }
    Write-Host ("LEG {0,-13} rc={1}  {2}" -f $leg.n, $rc, $tail)
    if ($rc -ne 0) { $bad += "$($leg.n)=$rc" }
}
Write-Host "=== S6 SUMMARY: legs=$($legs.Count) nonzero=$($bad.Count) $($bad -join ' ')"

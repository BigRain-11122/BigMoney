# r369 bm-b S6 maintenance chain runner (33 legs, rc capture, one-line tails)
$legs = @(
    @{n='01 compute_audit';        c='python scripts\compute_audit.py'},
    @{n='02 py_watermark';         c='python scripts\py_watermark.py probe'},
    @{n='03 update_daily';         c='python scripts\update_daily.py'},
    @{n='04 market_regime';        c='python scripts\market_regime.py'},
    @{n='05 strategy_scorecard';   c='python scripts\strategy_scorecard.py'},
    @{n='06 market_clock_call';    c='python scripts\market_clock_call.py run'},
    @{n='07 update_lhb';           c='python scripts\update_lhb.py'},
    @{n='08 update_heat';          c='python scripts\update_heat.py'},
    @{n='09 update_futures';       c='python scripts\update_futures.py'},
    @{n='10 update_repo';          c='python scripts\update_repo.py'},
    @{n='11 update_options';       c='python scripts\update_options.py'},
    @{n='12 update_moneyflow';     c='python scripts\update_moneyflow.py'},
    @{n='13 update_sina_mf';       c='python scripts\update_sina_mf.py'},
    @{n='14 update_astock_daily';  c='python scripts\update_astock_daily.py'},
    @{n='15 rev_osc_signal_export';c='python scripts\rev_osc_signal_export.py run'},
    @{n='16 update_ths_panel';     c='python scripts\update_ths_panel.py'},
    @{n='17 ah_panel_puller';      c='python scripts\ah_panel_puller.py'},
    @{n='18 update_fund_premium';  c='python scripts\update_fund_premium.py snapshot'},
    @{n='19 update_fundamental';   c='python scripts\update_fundamental.py'},
    @{n='20 b_layer_filter';       c='python -m firm.risk.b_layer_filter'},
    @{n='21 live_paper';           c='python -m live.paper'},
    @{n='22 t35_open_fill_verify'; c='python scripts\t35_open_fill_verify.py'},
    @{n='23 t24_prospect_paper';   c='python scripts\t24_prospect_paper.py run'},
    @{n='24 t24_prospect_promo';   c='python scripts\t24_prospect_promotion.py run'},
    @{n='25 aggressive_lab';       c='python scripts\aggressive_lab.py paper'},
    @{n='26 alloc_paper';         c='python scripts\alloc_paper.py run'},
    @{n='27 grid_paper';          c='python scripts\grid_paper.py run'},
    @{n='28 system_v1_paper';      c='python scripts\system_v1_paper.py run'},
    @{n='29 t35_paper_export';     c='python scripts\t35_paper_export.py run'},
    @{n='30 daily_scorecard';     c='python scripts\daily_scorecard.py'},
    @{n='31 daily_report';         c='python scripts\daily_report.py run'},
    @{n='32 build_status';         c='python -m monitor.build_status'},
    @{n='33 token_meter';          c='python scripts\token_meter.py'}
)
$nonzero = @()
foreach ($leg in $legs) {
    $out = & cmd /c "$($leg.c) 2>&1" | Out-String
    $rc = $LASTEXITCODE
    $tail = ($out -split "`r?`n" | Where-Object { $_.Trim() } | Select-Object -Last 1)
    if ($tail -and $tail.Length -gt 130) { $tail = $tail.Substring(0,130) }
    Write-Output ("rc={0} {1} | {2}" -f $rc, $leg.n, $tail)
    if ($rc -ne 0) { $nonzero += ("{0} rc={1}" -f $leg.n, $rc) }
}
Write-Output ("NONZERO: " + ($(if ($nonzero.Count) { $nonzero -join '; ' } else { 'NONE' })))

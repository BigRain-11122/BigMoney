# r495 bm-b S6 chain runner (explicit arrays; PS string-splat char-explode pit avoided)
# Sentinel law r494: caller reads S6RUNNER_DONE line + fails count from this log, NOT $LASTEXITCODE of the ps1.
$legs = @(
  @{n='strategy_scorecard';    m='scripts\strategy_scorecard.py';    a=@()},
  @{n='market_clock_call';     m='scripts\market_clock_call.py';     a=@('run')},
  @{n='update_lhb';            m='scripts\update_lhb.py';            a=@()},
  @{n='update_heat';           m='scripts\update_heat.py';           a=@()},
  @{n='update_futures';        m='scripts\update_futures.py';        a=@()},
  @{n='update_repo';           m='scripts\update_repo.py';           a=@()},
  @{n='update_options';        m='scripts\update_options.py';       a=@()},
  @{n='update_moneyflow';      m='scripts\update_moneyflow.py';      a=@()},
  @{n='update_sina_mf';        m='scripts\update_sina_mf.py';       a=@()},
  @{n='update_astock_daily';   m='scripts\update_astock_daily.py';   a=@()},
  @{n='update_etf_daily';      m='scripts\update_etf_daily.py';      a=@()},
  @{n='rev_osc_signal_export'; m='scripts\rev_osc_signal_export.py'; a=@('run')},
  @{n='update_minute_feed';    m='scripts\update_minute_feed.py';    a=@()},
  @{n='update_ths_panel';      m='scripts\update_ths_panel.py';      a=@()},
  @{n='ah_panel_puller';       m='scripts\ah_panel_puller.py';       a=@()},
  @{n='update_fund_premium';   m='scripts\update_fund_premium.py';   a=@('snapshot')},
  @{n='update_fundamental';    m='scripts\update_fundamental.py';    a=@()},
  @{n='b_layer_filter';        m='firm.risk.b_layer_filter';         a=@(); mod=$true},
  @{n='live.paper';            m='live.paper';                       a=@(); mod=$true; env_regime=$true},
  @{n='t35_open_fill_verify';  m='scripts\t35_open_fill_verify.py';  a=@()},
  @{n='t24_prospect_paper';    m='scripts\t24_prospect_paper.py';    a=@('run')},
  @{n='t24_prospect_promotion';m='scripts\t24_prospect_promotion.py';a=@('run')},
  @{n='aggressive_lab';        m='scripts\aggressive_lab.py';        a=@('paper')},
  @{n='alloc_paper';           m='scripts\alloc_paper.py';           a=@('run')},
  @{n='grid_paper';            m='scripts\grid_paper.py';            a=@('run')},
  @{n='system_v1_paper';       m='scripts\system_v1_paper.py';      a=@('run')},
  @{n='t35_paper_export';      m='scripts\t35_paper_export.py';      a=@('run')},
  @{n='daily_scorecard';       m='scripts\daily_scorecard.py';       a=@()},
  @{n='daily_report';          m='scripts\daily_report.py';          a=@('run')},
  @{n='ceo_live_usage';        m='scripts\ceo_live_usage.py';        a=@()},
  @{n='monitor.build_status';  m='monitor.build_status';             a=@(); mod=$true},
  @{n='token_meter';           m='scripts\token_meter.py';           a=@()}
)
$fails = @()
foreach ($l in $legs) {
  if ($l.env_regime) { $env:BIGMONEY_REGIME_GUARD = 'enforce' }
  $out = if ($l.mod) { & python -m $l.m @($l.a) 2>&1 } else { & python $l.m @($l.a) 2>&1 }
  $rc = $LASTEXITCODE
  $tail = ($out | Select-Object -Last 2) -join ' | '
  $line = "LEG {0} rc={1} :: {2}" -f $l.n, $rc, $tail
  $line | Out-File -Append -Encoding utf8 results\_r495bmb_s6_log.txt
  if ($rc -ne 0) { $fails += ("{0}(rc={1})" -f $l.n, $rc) }
  if ($l.env_regime) { Remove-Item env:BIGMONEY_REGIME_GUARD -ErrorAction SilentlyContinue }
}
"S6RUNNER_DONE fails={0} {1}" -f $fails.Count, ($fails -join ',') | Out-File -Append -Encoding utf8 results\_r495bmb_s6_log.txt
Write-Output ("S6RUNNER_DONE fails={0} {1}" -f $fails.Count, ($fails -join ','))

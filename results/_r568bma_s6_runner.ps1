# r568 S6 chain runner: ordered legs, rc + tail line evidence per leg (r318/r559 laws: explicit arrays, per-leg evidence)
$legs = @(
  @{n='dualrun';    c=@('python','scripts\pool_dualrun_reconcile.py','run')},
  @{n='audit';      c=@('python','scripts\compute_audit.py')},
  @{n='wm_probe';   c=@('python','scripts\py_watermark.py','probe')},
  @{n='daily';      c=@('python','scripts\update_daily.py')},
  @{n='regime';     c=@('python','scripts\market_regime.py')},
  @{n='scorecard';  c=@('python','scripts\strategy_scorecard.py')},
  @{n='clock';      c=@('python','scripts\market_clock_call.py','run')},
  @{n='lhb';        c=@('python','scripts\update_lhb.py')},
  @{n='heat';       c=@('python','scripts\update_heat.py')},
  @{n='futures';    c=@('python','scripts\update_futures.py')},
  @{n='repo';       c=@('python','scripts\update_repo.py')},
  @{n='options';    c=@('python','scripts\update_options.py')},
  @{n='moneyflow';  c=@('python','scripts\update_moneyflow.py')},
  @{n='sina_mf';    c=@('python','scripts\update_sina_mf.py')},
  @{n='astock';     c=@('python','scripts\update_astock_daily.py')},
  @{n='etf_daily';  c=@('python','scripts\update_etf_daily.py')},
  @{n='rev_osc';    c=@('python','scripts\rev_osc_signal_export.py','run')},
  @{n='minute';     c=@('python','scripts\update_minute_feed.py')},
  @{n='ths';        c=@('python','scripts\update_ths_panel.py')},
  @{n='ah_panel';   c=@('python','scripts\ah_panel_puller.py')},
  @{n='fund_prem';  c=@('python','scripts\update_fund_premium.py','snapshot')},
  @{n='fundament';  c=@('python','scripts\update_fundamental.py')},
  @{n='b_layer';    c=@('python','-m','firm.risk.b_layer_filter')}
)
$fail=@()
foreach ($l in $legs) {
  $out = & $l.c[0] $l.c[1..($l.c.Count-1)] 2>&1
  $rc = $LASTEXITCODE
  $tail = ($out | Select-Object -Last 1)
  Write-Output ("LEG {0} rc={1} :: {2}" -f $l.n, $rc, ($tail -replace '\s+',' '))
  if ($rc -ne 0) { $fail += ("{0} rc={1}" -f $l.n, $rc) }
}
Write-Output ("S6-PART1 DONE fails=" + ($fail -join ','))

# r937 bm-b S6 chain batch 2
$ErrorActionPreference = 'Continue'
$chain = @(
  @{n='astock_daily';  c='python scripts\update_astock_daily.py'},
  @{n='etf_daily';     c='python scripts\update_etf_daily.py'},
  @{n='thermo';        c='python scripts\regime_thermo_build.py'},
  @{n='dualarm';       c='python scripts\regime_gate_dualarm.py run'},
  @{n='rev_osc';       c='python scripts\rev_osc_signal_export.py run'},
  @{n='minute_feed';   c='python scripts\update_minute_feed.py'},
  @{n='ths_panel';     c='python scripts\update_ths_panel.py'},
  @{n='ah_panel';     c='python scripts\ah_panel_puller.py'},
  @{n='fund_premium';  c='python scripts\update_fund_premium.py snapshot'},
  @{n='fundamental';   c='python scripts\update_fundamental.py'},
  @{n='b_layer';       c='python -m firm.risk.b_layer_filter'},
  @{n='fund_states';   c='python scripts\update_fund_statements.py'}
)
foreach ($s in $chain) {
  $out = & cmd /c $s.c 2>&1
  $rc = $LASTEXITCODE
  Write-Output ("### {0} rc={1}" -f $s.n, $rc)
  if ($rc -ne 0) { $out | Select-Object -Last 4 | Write-Output }
}

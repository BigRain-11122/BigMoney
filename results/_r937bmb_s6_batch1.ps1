# r937 bm-b S6 chain batch runner (compact rc logging, nonzero prints tail)
$ErrorActionPreference = 'Continue'
$chain = @(
  @{n='dualrun';        c='python scripts\pool_dualrun_reconcile.py run'},
  @{n='compute_audit';  c='python scripts\compute_audit.py'},
  @{n='py_watermark';    c='python scripts\py_watermark.py probe'},
  @{n='update_daily';   c='python scripts\update_daily.py'},
  @{n='market_regime';  c='python scripts\market_regime.py'},
  @{n='scorecard';      c='python scripts\strategy_scorecard.py'},
  @{n='market_clock';   c='python scripts\market_clock_call.py run'},
  @{n='update_lhb';     c='python scripts\update_lhb.py'},
  @{n='update_zt_pool'; c='python scripts\update_zt_pool.py'},
  @{n='update_heat';    c='python scripts\update_heat.py'},
  @{n='update_futures'; c='python scripts\update_futures.py'},
  @{n='update_repo';    c='python scripts\update_repo.py'},
  @{n='update_options'; c='python scripts\update_options.py'},
  @{n='moneyflow';      c='python scripts\update_moneyflow.py'},
  @{n='sina_mf';        c='python scripts\update_sina_mf.py'}
)
foreach ($s in $chain) {
  $out = & cmd /c $s.c 2>&1
  $rc = $LASTEXITCODE
  Write-Output ("### {0} rc={1}" -f $s.n, $rc)
  if ($rc -ne 0) { $out | Select-Object -Last 4 | Write-Output }
}

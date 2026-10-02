# r582 bm-a S6 chain runner (PS lessons: r571 explicit arrays, r318 Write-Host for diagnostics)
$ErrorActionPreference = "Continue"
$legs = @(
  @("dualrun",   @("python","scripts\pool_dualrun_reconcile.py","run")),
  @("audit",     @("python","scripts\compute_audit.py")),
  @("watermark", @("python","scripts\py_watermark.py","probe")),
  @("daily",     @("python","scripts\update_daily.py")),
  @("regime",    @("python","scripts\market_regime.py")),
  @("scorecard", @("python","scripts\strategy_scorecard.py")),
  @("clock",     @("python","scripts\market_clock_call.py","run")),
  @("lhb",       @("python","scripts\update_lhb.py")),
  @("heat",      @("python","scripts\update_heat.py")),
  @("futures",   @("python","scripts\update_futures.py")),
  @("repo",      @("python","scripts\update_repo.py")),
  @("options",   @("python","scripts\update_options.py")),
  @("moneyflow", @("python","scripts\update_moneyflow.py")),
  @("sinamf",    @("python","scripts\update_sina_mf.py")),
  @("ths",       @("python","scripts\update_ths_panel.py")),
  @("ahpanel",   @("python","scripts\ah_panel_puller.py")),
  @("fundament", @("python","scripts\update_fundamental.py")),
  @("blayer",    @("python","-m","firm.risk.b_layer_filter"))
)
$results = @()
foreach ($leg in $legs) {
  $name = $leg[0]
  $arr = @($leg[1])
  $out = & $arr[0] $arr[1..($arr.Count-1)] 2>&1
  $rc = $LASTEXITCODE
  $tail = ($out | Select-Object -Last 1)
  Write-Host "LEG $name rc=$rc :: $tail"
  $results += "$name rc=$rc"
}
Write-Host ("S6-A SUMMARY: " + ($results -join " | "))

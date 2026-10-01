# r326 bm-c S6 chain batch B -- paper/derive/report legs (14), rc per leg, log to file.
# v2: arg-array legs (v1 tuple misalignment bug fixed; r495 splat law: arrays only).
$Project = "K:\Fluxgroup\FluxGroup\quant\bigmoney"
Set-Location $Project
$log = Join-Path $Project "results\_r326bmc_s6.log"
"=== r326 S6 chain batch B v2 start $(Get-Date -Format 'HH:mm:ss') ===" | Add-Content $log
$legs = @(
  @("livepaper",  @("-m", "live.paper")),
  @("t35ofv",     @("scripts\t35_open_fill_verify.py")),
  @("prospect",   @("scripts\t24_prospect_paper.py", "run")),
  @("promotion",  @("scripts\t24_prospect_promotion.py", "run")),
  @("aggr",       @("scripts\aggressive_lab.py", "paper")),
  @("alloc",      @("scripts\alloc_paper.py", "run")),
  @("grid",       @("scripts\grid_paper.py", "run")),
  @("sysv1",      @("scripts\system_v1_paper.py", "run")),
  @("export",     @("scripts\t35_paper_export.py", "run")),
  @("dscore",     @("scripts\daily_scorecard.py")),
  @("dreport",    @("scripts\daily_report.py", "run")),
  @("ceolive",    @("scripts\ceo_live_usage.py")),
  @("buildstatus",@("-m", "monitor.build_status")),
  @("tokenmeter", @("scripts\token_meter.py"))
)
$fail = 0
foreach ($leg in $legs) {
  $name = $leg[0]
  $argv = $leg[1]
  $t0 = Get-Date
  $out = & python @argv 2>&1
  $rc = $LASTEXITCODE
  $el = [int]((Get-Date) - $t0).TotalSeconds
  if ($rc -ne 0) { $fail++ }
  $tail = ($out | Select-Object -Last 2) -join " | "
  $line = "LEG $name rc=$rc ${el}s :: $tail"
  Write-Host $line
  Add-Content $log $line
  Add-Content $log ($out -join "`n")
}
Write-Host "=== batch B v2 done $(Get-Date -Format 'HH:mm:ss') fail=$fail ==="
Add-Content $log "=== batch B v2 done $(Get-Date -Format 'HH:mm:ss') fail=$fail ==="
exit $fail

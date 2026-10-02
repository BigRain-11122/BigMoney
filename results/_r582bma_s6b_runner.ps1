# r582 bm-a S6 chain B-segment (paper/report faces; each self-gates on new-bar)
$ErrorActionPreference = "Continue"
$legs = @(
  @("prospect",  @("python","scripts\t24_prospect_paper.py","run")),
  @("promotion", @("python","scripts\t24_prospect_promotion.py","run")),
  @("aggr",      @("python","scripts\aggressive_lab.py","paper")),
  @("alloc",     @("python","scripts\alloc_paper.py","run")),
  @("grid",      @("python","scripts\grid_paper.py","run")),
  @("sysv1",     @("python","scripts\system_v1_paper.py","run")),
  @("export",    @("python","scripts\t35_paper_export.py","run")),
  @("dscore",    @("python","scripts\daily_scorecard.py")),
  @("dreport",   @("python","scripts\daily_report.py","run")),
  @("ceolive",   @("python","scripts\ceo_live_usage.py")),
  @("status",    @("python","-m","monitor.build_status")),
  @("token",     @("python","scripts\token_meter.py"))
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
Write-Host ("S6-B SUMMARY: " + ($results -join " | "))

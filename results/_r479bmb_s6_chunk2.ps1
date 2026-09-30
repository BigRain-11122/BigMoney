# r479 bm-b S6 chain chunk 2 (new-bar legs 24-37)
$ErrorActionPreference = 'Continue'
$log = 'results\_r479bmb_s6_log.txt'
"=== r479 bm-b S6 chunk2 start $(Get-Date -Format 'HH:mm:ss') ===" | Out-File $log -Append -Encoding utf8
$env:BIGMONEY_REGIME_GUARD = 'enforce'
$legs = @(
    @('live_paper', 'python -m live.paper'),
    @('t35_open_fill_verify', 'python scripts\t35_open_fill_verify.py'),
    @('t24_prospect_paper', 'python scripts\t24_prospect_paper.py run'),
    @('t24_prospect_promotion', 'python scripts\t24_prospect_promotion.py run'),
    @('aggressive_lab_paper', 'python scripts\aggressive_lab.py paper'),
    @('alloc_paper', 'python scripts\alloc_paper.py run'),
    @('grid_paper', 'python scripts\grid_paper.py run'),
    @('system_v1_paper', 'python scripts\system_v1_paper.py run'),
    @('t35_paper_export', 'python scripts\t35_paper_export.py run'),
    @('daily_scorecard', 'python scripts\daily_scorecard.py'),
    @('daily_report', 'python scripts\daily_report.py run'),
    @('ceo_live_usage', 'python scripts\ceo_live_usage.py'),
    @('build_status', 'python -m monitor.build_status'),
    @('token_meter', 'python scripts\token_meter.py')
)
foreach ($leg in $legs) {
    $name = $leg[0]
    $t0 = Get-Date
    Invoke-Expression $leg[1] *>&1 | Out-File $log -Append -Encoding utf8
    $rc = $LASTEXITCODE
    $dt = [math]::Round(((Get-Date) - $t0).TotalSeconds, 1)
    $line = "LEG $name rc=$rc ${dt}s"
    $line | Out-File $log -Append -Encoding utf8
    Write-Output $line
}
"=== chunk2 end $(Get-Date -Format 'HH:mm:ss') ===" | Out-File $log -Append -Encoding utf8
